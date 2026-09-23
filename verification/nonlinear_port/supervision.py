"""Finite one-attempt Poiseuille controller source, with no live backend.

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
from .fixture_driver import numerical_decision
from .diagnostics import ANGULAR_TERMS, ENERGY_TERMS


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


def validate_worker_result(payload, versions=None, gates=None):
    """A field report alone can never accept an attempt."""
    required = {'fixture', 'subdivisions', 'numerical_accepted', 'checks',
                'compatibility', 'constraint_condition', 'nonlinear_history',
                'linear_corrections', 'return_quadrature_sample_counts',
                'minimum_return_normal_velocity', 'diagnostics_degree24',
                'diagnostics_degree26', 'quadrature_comparison', 'step_checks',
                'phase_seconds', 'worker_intervals', 'actual_versions'}
    if not required <= payload.keys() or payload['fixture'] != 'poiseuille' or payload['subdivisions'] != 2:
        raise Refusal('incomplete one-fixture worker result')
    if (payload['numerical_accepted'] is not True or not payload['checks']
            or any(v is not True for v in payload['checks'].values())
            or payload['step_checks'].get('numerical_step_accepted') is not True
            or len(payload['linear_corrections']) < 1
            or any(not item.get('accepted') for item in payload['quadrature_comparison'].values())):
        raise Refusal('failed numerical gate or missing verified correction')
    compatibility = payload['compatibility']
    condition = payload['constraint_condition']
    if (not isinstance(compatibility, dict) or not isinstance(condition, dict)
            or any(type(compatibility.get(k)) not in (int, float) or not isfinite(compatibility[k])
                   for k in ('defect', 'limit'))
            or abs(compatibility['defect']) > compatibility['limit']
            or type(condition.get('condition_bound')) not in (int, float)
            or not isfinite(condition['condition_bound'])
            or not 1 <= condition['condition_bound'] <= 1e6):
        raise Refusal('missing or failed compatibility/rank evidence')
    if (payload['return_quadrature_sample_counts'] is None
            or len(payload['return_quadrature_sample_counts']) != 2
            or any(type(n) is not int or n < 1 for n in payload['return_quadrature_sample_counts'])
            or len(payload['nonlinear_history']) < 2):
        raise Refusal('missing return samples or correction history')
    report = payload['diagnostics_degree24']
    raw = report.get('raw') if isinstance(report, dict) else None
    raw_required = {'volume', 'pressure_mean', 'p_error_integral', 'p_error_squared',
                    'flux_0', 'flux_1', 'area_0', 'area_1', 'lateral_flux',
                    'boundary_absolute_flux', 'energy_identity_storage',
                    'energy_identity_dissipation', 'kinetic_discrete_derivative',
                    *('angular.'+k for k in ANGULAR_TERMS),
                    *('energy.'+k for k in ENERGY_TERMS),
                    *(k+'_squared' for k in ('u_L2', 'u_H1_seminorm',
                                            'div_u_L2', 'traction_L2_returns'))}
    if (not isinstance(raw, dict) or not raw_required <= raw.keys()
            or set(payload['diagnostics_degree26']) != set(raw)
            or set(payload['quadrature_comparison']) != set(raw)
            or report.get('angular_budget', {}).get('accepted') is not True
            or report.get('energy_budget', {}).get('accepted') is not True):
        raise Refusal('incomplete raw diagnostic or budget inventory')
    if gates is not None:
        decision = numerical_decision(report, payload['step_checks'],
                                       payload['quadrature_comparison'],
                                       len(payload['linear_corrections']), gates)
        if decision['numerical_accepted'] is not True or decision['checks'] != payload['checks']:
            raise Refusal('worker numerical decision does not match recorded terms')
    if versions is not None and any(payload['actual_versions'].get(k) != v
                                    for k, v in versions.items()):
        raise Refusal('worker reported different pinned versions')
    phases = payload['phase_seconds']
    if (not isinstance(phases, dict) or set(phases) != {
            'mesh_and_lift', 'primary_form_setup_jit',
            'compatibility_rank_newton', 'diagnostic_form_jit_assembly_sampling'}
            or not isinstance(payload['worker_intervals'], dict)
            or not all(type(v) in (int, float) and isfinite(v) and v >= 0
                       for v in [*phases.values(), *payload['worker_intervals'].values()])):
        raise Refusal('missing or nonfinite worker timing inventory')
    minimum = payload['minimum_return_normal_velocity']
    if type(minimum) not in (float, int) or not isfinite(minimum) or minimum < -1e-8:
        raise Refusal('unresolved return backflow')
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
            or admission.get('manifest_sha256') != digest):
        raise Refusal('no matching explicit one-fixture execution admission')
    if not isinstance(source_commit, str) or len(source_commit) != 40:
        raise Refusal('missing bound source commit')
    if not isinstance(interpreter, str) or not interpreter or not isinstance(owner, str) or not owner:
        raise Refusal('missing interpreter or task owner')
    if backend is None:
        raise Refusal('host containment backend unavailable')

    start = monotonic()
    directory = Path(run_dir)
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
                        or cleanup['memory_events'].get('oom', 1) != 0
                        or cleanup['memory_events'].get('oom_kill', 1) != 0
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
        if monotonic()-start > CAPS['elapsed_seconds']:
            # The completion record itself finished late. Preserve both records;
            # a late marker overrides a formerly provisional/PASS observation.
            _save_new(directory/'late.json', dict(status='INCOMPLETE', reason='completion saved late'))
            completed = False
        result['status'] = 'PASS' if completed else 'INCOMPLETE'
        result['completion'] = completion
    return result
