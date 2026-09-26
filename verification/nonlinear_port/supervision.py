"""Finite one-attempt Poiseuille controller; no admitted whole-task backend.

An admitted Linux backend must create a held whole-task scope, verify effective
limits and independent expiry, then release a pinned worker. This controller
keeps the reservation and result ledger. It deliberately has no default backend:
the restricted agent namespace cannot establish host containment, and the
current manifest grants zero attempts.
"""
import hashlib
import json
from math import isfinite
import os
from pathlib import Path
import secrets
import time

from .manifest import validate as validate_manifest
from .prototype import Refusal
from .sparse import condition_from_gram
from .fixture_driver import numerical_decision
from .diagnostics import (field_report, quadrature_comparison, step_checks,
                          compatibility_report, finite, poiseuille_endpoint_budgets)


CAPS = dict(elapsed_seconds=180, whole_task_memory_mib=1536, swap_mib=0,
            mpi_ranks=1, threads=1, pids=32, velocity_pressure_dofs=20000)
SETUP_SECONDS = 15
WORK_SECONDS = 150
FINISH_SECONDS = 15
MAX_REPORT_BYTES = 2_000_000


def _save_new(path, value):
    """Create each record once; a failed/partial write remains unresolved."""
    with open(path, 'x', encoding='utf-8') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def _load_limited(path):
    if not path.is_file() or path.stat().st_size > MAX_REPORT_BYTES:
        raise Refusal('missing or oversized worker result')
    with path.open('r', encoding='utf-8') as stream:
        result = json.load(stream)
        if stream.read(1):
            raise Refusal('trailing worker result data')
    if not isinstance(result, dict):
        raise Refusal('worker result must be an object')
    return result


def verify_held_scope(facts, scope_id):
    """Check observed effective limits before release, never requested values."""
    required = {'cgroup_path', 'memory_max_bytes', 'swap_max_bytes', 'pids_max',
                'independent_expiry_seconds', 'worker_held',
                'all_task_processes_in_scope', 'mpi_ranks', 'threads'}
    if not isinstance(facts, dict) or not required <= facts.keys():
        raise Refusal('missing held-scope facts')
    if (not isinstance(scope_id, str) or not scope_id.startswith('/')
            or facts['cgroup_path'] != scope_id or scope_id == '/'):
        raise Refusal('unverified task cgroup identity')
    for key in ('memory_max_bytes', 'swap_max_bytes', 'pids_max',
                'independent_expiry_seconds', 'mpi_ranks', 'threads'):
        if type(facts[key]) not in (int, float) or not isfinite(facts[key]):
            raise Refusal('missing effective task limit')
    if (facts['memory_max_bytes'] > 1536*1024**2 or facts['memory_max_bytes'] <= 0
            or facts['swap_max_bytes'] != 0 or not 0 < facts['pids_max'] <= 32
            or not 0 < facts['independent_expiry_seconds'] <= WORK_SECONDS
            or facts['mpi_ranks'] != 1 or facts['threads'] != 1
            or facts['worker_held'] is not True
            or facts['all_task_processes_in_scope'] is not True):
        raise Refusal('held task scope does not enforce frozen caps')
    return dict(facts)


def validate_worker_result(payload, versions, gates):
    """Recompute decisions from finite saved terms; never trust cached PASS flags."""
    required = {'fixture', 'subdivisions', 'dt', 'mixed_dofs', 'global_dofs',
                'numerical_accepted', 'checks', 'compatibility',
                'constraint_condition', 'nonlinear_history', 'linear_corrections',
                'return_quadrature_sample_counts', 'minimum_return_normal_velocity',
                'diagnostics_degree24', 'diagnostics_degree26',
                'quadrature_comparison', 'step_checks', 'multipliers', 'eta',
                'physical_endpoint_budgets',
                'phase_seconds', 'worker_intervals', 'actual_versions'}
    if not isinstance(payload, dict) or not required <= payload.keys():
        raise Refusal('incomplete one-fixture worker result')
    if (payload['fixture'] != 'poiseuille' or type(payload['subdivisions']) is not int
            or payload['subdivisions'] != 2 or payload['dt'] != .125
            or type(payload['mixed_dofs']) is not int
            or not 0 < payload['mixed_dofs'] <= CAPS['velocity_pressure_dofs']
            or type(payload['global_dofs']) is not int
            or payload['global_dofs'] != payload['mixed_dofs']+3):
        raise Refusal('wrong fixture or dof inventory')
    compatibility = payload['compatibility']
    condition = payload['constraint_condition']
    if (not isinstance(condition, dict)
            or condition.get('method') != 'sqrt infinity-norm condition of three-row Gram'
            or len(condition.get('gram', [])) != 3
            or any(len(row) != 3 for row in condition['gram'])):
        raise Refusal('missing measured constraint rank evidence')
    finite([v for row in condition['gram'] for v in row])
    if condition_from_gram(condition['gram']) != condition:
        raise Refusal('constraint condition differs from saved Gram matrix')
    if not isinstance(compatibility, dict) or compatibility.get('targets') != [0., 0.]:
        raise Refusal('wrong Poiseuille return targets')
    recomputed = compatibility_report(compatibility['lateral_flux'],
                                     compatibility['targets'],
                                     compatibility['absolute_term_sum'],
                                     condition['condition_bound'])
    if recomputed != compatibility:
        raise Refusal('compatibility decision differs from saved terms')
    counts = payload['return_quadrature_sample_counts']
    history, corrections = payload['nonlinear_history'], payload['linear_corrections']
    if (not isinstance(counts, list) or len(counts) != 2
            or any(type(n) is not int or n < 1 for n in counts)
            or not 2 <= len(history) <= 13 or len(corrections) != len(history)-1):
        raise Refusal('missing return samples or complete correction history')
    for item in corrections:
        if not isinstance(item, dict) or set(item) != {'true_residual', 'rhs_norm'}:
            raise Refusal('incomplete linear correction evidence')
        finite(item.values())
        if (min(item.values()) < 0
                or item['true_residual'] > max(1e-13, 1e-8*item['rhs_norm'])):
            raise Refusal('failed linear correction')
    report = payload['diagnostics_degree24']
    if not isinstance(report, dict) or 'raw' not in report:
        raise Refusal('missing raw diagnostics')
    # For this frozen oracle both cap pressure means and flux totals are zero.
    rebuilt = field_report(report['raw'], payload['multipliers'], [0., 0.],
                           [0., 0.], payload['eta'])
    if rebuilt != report:
        raise Refusal('field report differs from raw diagnostics')
    comparison = quadrature_comparison(report['raw'], payload['diagnostics_degree26'],
                                       gates['quadrature_relative_change'])
    latest = corrections[-1]
    checked = step_checks(rebuilt, [payload['minimum_return_normal_velocity']],
                          history, latest['true_residual'], gates, latest['rhs_norm'])
    decision = numerical_decision(rebuilt, checked, comparison, len(corrections), gates)
    endpoints = poiseuille_endpoint_budgets(report['raw'], payload['dt'])
    decision['checks']['physical_endpoint_budgets'] = all(
        entry['physical']['accepted'] for entry in endpoints.values())
    decision['numerical_accepted'] = all(decision['checks'].values())
    if (comparison != payload['quadrature_comparison'] or checked != payload['step_checks']
            or endpoints != payload['physical_endpoint_budgets']
            or decision['checks'] != payload['checks']
            or payload['numerical_accepted'] is not True
            or decision['numerical_accepted'] is not True):
        raise Refusal('failed or inconsistent numerical evidence')
    if any(payload['actual_versions'].get(k) != v for k, v in versions.items()):
        raise Refusal('worker reported different pinned versions')
    phases = payload['phase_seconds']
    intervals = payload['worker_intervals']
    if (not isinstance(phases, dict) or set(phases) != {
            'mesh_and_lift', 'primary_form_setup_jit',
            'compatibility_rank_newton', 'diagnostic_form_jit_assembly_sampling'}
            or not isinstance(intervals, dict) or set(intervals) != {
                'import_seconds', 'fixture_setup_jit_and_solve_seconds'}):
        raise Refusal('missing worker timing inventory')
    finite([*phases.values(), *intervals.values()])
    if any(v < 0 for v in [*phases.values(), *intervals.values()]):
        raise Refusal('negative worker timing')
    return payload


def supervise_once(run_dir, manifest_path, admission, backend, *,
                   source_commit, interpreter, owner, monotonic=time.monotonic):
    """Reserve once, verify held scope, release, collect and refuse incomplete runs.

    ``backend`` is an injected, separately reviewed host capability. Its
    ``start_held`` must include the worker/JIT children and task reporters in
    one Linux scope. There is no implicit retry or fallback backend.
    """
    manifest_bytes = Path(manifest_path).read_bytes()
    manifest = json.loads(manifest_bytes)
    validate_manifest(manifest)
    digest = hashlib.sha256(manifest_bytes).hexdigest()
    if (not isinstance(admission, dict) or admission.get('approved') is not True
            or admission.get('fixture') != 'poiseuille'
            or admission.get('attempts_granted') != 1
            or admission.get('source_commit') != source_commit
            or admission.get('manifest_sha256') != digest
            or admission.get('run_directory') != str(Path(run_dir).resolve())):
        raise Refusal('no matching explicit one-fixture execution admission')
    if not isinstance(source_commit, str) or len(source_commit) != 40:
        raise Refusal('missing bound source commit')
    if not isinstance(interpreter, str) or not interpreter or not isinstance(owner, str) or not owner:
        raise Refusal('missing interpreter or task owner')
    if backend is None:
        raise Refusal('host containment backend unavailable')

    start = monotonic()
    directory = Path(run_dir).resolve()
    directory.mkdir(parents=False, exist_ok=False)
    reservation = dict(status='RESERVED', fixture='poiseuille', attempt=1,
                       source_commit=source_commit, manifest_sha256=digest,
                       interpreter=interpreter, owner=owner,
                       release_nonce=secrets.token_hex(16),
                       wall_start_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                       monotonic_start=start, caps=CAPS)
    _save_new(directory/'reservation.json', reservation)
    _save_new(directory/'admission.json', admission)
    handle = None
    result = dict(status='INCOMPLETE', reservation=reservation)
    log = []
    finish_start = None
    try:
        command = (interpreter, '-m', 'verification.nonlinear_port.worker',
                   str(directory), str(Path(manifest_path).resolve()))
        handle = backend.start_held(command, directory, CAPS)
        facts = verify_held_scope(handle.facts(), handle.scope_id)
        result['held_scope'] = facts
        setup_elapsed = monotonic()-start
        result['setup_seconds'] = setup_elapsed
        if setup_elapsed > SETUP_SECONDS:
            raise Refusal('setup exceeded 15 seconds before release')
        handle.release()
        log.append('Held task released after effective scope verification.')
        observed = handle.wait(WORK_SECONDS)
        result['exit'] = observed
        result['work_seconds'] = monotonic()-start-setup_elapsed
        finish_start = monotonic()
        if (not isinstance(observed, dict) or type(observed.get('exit_code')) is not int
                or observed['exit_code'] != 0 or not 0 <= result['work_seconds'] <= WORK_SECONDS):
            raise Refusal('worker exit or managed time failed')
        payload = validate_worker_result(_load_limited(directory/'numerical.json'),
                                         manifest['versions'], manifest['gates'])
        result['numerical'] = payload
        log.append('Complete numerical payload loaded and checked.')
    except Exception as exc:
        # A partially started service still belongs to this attempt.
        handle = handle or getattr(backend, 'active_handle', None)
        result['reason'] = f'{type(exc).__name__}: {exc}'
        log.append(result['reason'])
    finally:
        cleanup_start = monotonic()
        if handle is not None:
            try:
                handle.stop()
                cleanup = handle.cleanup()
                result['cleanup'] = cleanup
                if (not isinstance(cleanup, dict) or cleanup.get('empty') is not True
                        or cleanup.get('unknown_children') is not False
                        or type(cleanup.get('memory_peak_bytes')) is not int
                        or cleanup['memory_peak_bytes'] > 1536*1024**2
                        or cleanup['memory_peak_bytes'] < 0
                        or cleanup.get('memory_events') is None
                        or not isinstance(cleanup['memory_events'], dict)
                        or cleanup['memory_events'].get('max', 1) != 0
                        or cleanup['memory_events'].get('oom', 1) != 0
                        or cleanup['memory_events'].get('oom_kill', 1) != 0
                        or cleanup.get('pids_events', {}).get('max', 1) != 0
                        or type(cleanup.get('pids_peak')) is not int
                        or not 0 <= cleanup['pids_peak'] <= 32):
                    result['reason'] = 'missing, exceeded or unknown cleanup/resource evidence'
            except Exception as exc:
                result['reason'] = f'cleanup unconfirmed: {type(exc).__name__}: {exc}'
        result['cleanup_seconds'] = monotonic()-cleanup_start
        result['elapsed_seconds_before_save'] = monotonic()-start
        if result['elapsed_seconds_before_save'] > CAPS['elapsed_seconds']:
            result['reason'] = 'end-to-end ceiling exceeded before save'
        if finish_start is not None and monotonic()-finish_start > FINISH_SECONDS:
            result['reason'] = 'cleanup/report interval exceeded 15 seconds before save'
        if 'reason' not in result and 'numerical' in result and 'cleanup' in result:
            result['status'] = 'PROVISIONAL_PASS'
        # A save/late failure must never create a PASS record. The finite caller
        # cannot certify its own final fsync tail; the result discloses that.
        result['final_save_tail_observed'] = False
        save_start = monotonic()
        try:
            _save_new(directory/'result.json', result)
            with open(directory/'run.log', 'x', encoding='utf-8') as stream:
                stream.write('\n'.join(log)+'\n')
                stream.flush()
                os.fsync(stream.fileno())
        except Exception as exc:
            raise Refusal(f'run persistence incomplete: {exc}') from exc
        persisted_elapsed = monotonic()-start
        finish_elapsed = monotonic()-finish_start if finish_start is not None else None
        completed = (result['status'] == 'PROVISIONAL_PASS'
                     and persisted_elapsed <= CAPS['elapsed_seconds']
                     and finish_elapsed is not None and finish_elapsed <= FINISH_SECONDS)
        completion = dict(status='PASS' if completed else 'INCOMPLETE',
                          observed_elapsed_after_result_and_log=persisted_elapsed,
                          observed_finish_seconds=finish_elapsed,
                          result_and_log_save_seconds=monotonic()-save_start,
                          cleanup_seconds=result['cleanup_seconds'],
                          final_completion_save_tail_observed=False)
        try:
            _save_new(directory/'completion.json', completion)
        except Exception as exc:
            raise Refusal(f'completion persistence incomplete: {exc}') from exc
        if (monotonic()-start > CAPS['elapsed_seconds']
                or (finish_start is not None and monotonic()-finish_start > FINISH_SECONDS)):
            # The completion record itself finished late. Preserve both records;
            # a late marker overrides a formerly provisional/PASS observation.
            _save_new(directory/'late.json', dict(status='INCOMPLETE', reason='completion saved late'))
            completed = False
        result['status'] = 'PASS' if completed else 'INCOMPLETE'
        result['completion'] = completion
    return result
