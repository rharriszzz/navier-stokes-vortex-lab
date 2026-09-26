"""R253 saved rotation execution and source-only integrity audit; no numerical imports."""
import hashlib
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from verification.nonlinear_port.rotation_driver import (
    read_limited, validate_reservation, validate_worker_payload)
from verification.nonlinear_port.rotation_manifest import validate as validate_manifest
from verification.nonlinear_port.source_binding import expected_binding
from verification.nonlinear_port.supervision import CAPS, validate_worker_result


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run():
    inventory = json.loads((HERE/'run_hashes.json').read_text())
    source_dir = Path(inventory['source_directory'])
    assert source_dir == Path('/tmp/navier-rotation-r251-once')
    assert inventory['count'] == 14 and len(inventory['files']) == 14
    assert set(inventory['files']) == {p.name for p in source_dir.iterdir() if p.is_file()}
    for name, entry in inventory['files'].items():
        preserved = (HERE/'run'/name).read_bytes()
        assert len(preserved) == entry['bytes']
        assert hashlib.sha256(preserved).hexdigest() == entry['sha256']
        assert preserved == (source_dir/name).read_bytes()
    def record(name): return read_limited(HERE/'run'/name)
    allocation = read_limited(ROOT/'docs/realizability/evidence/r251/allocation.json')
    manifest_path = ROOT/'verification/nonlinear_port/future_rotation.json'
    manifest_bytes = manifest_path.read_bytes()
    manifest = read_limited(manifest_path)
    validate_manifest(manifest)
    reservation = record('reservation.json')
    admission = record('admission.json')
    assert admission['source_commit'] == reservation['source_commit'] == '2e60a7bdc635587b09e3da5f6a03eed2ef3c85c3'
    assert admission['run_directory'] == str(source_dir)
    assert admission['attempts_granted'] == 1 and reservation['attempt'] == 1
    validate_reservation(reservation, admission, manifest_bytes, manifest,
                         source_dir, allocation['interpreter'], reservation['owner'])
    source = expected_binding(ROOT, reservation, allocation['interpreter'])
    assert record('held.json')['source_binding'] == source
    assert record('numerical.json')['source_binding'] == source
    assert reservation['caps'] == CAPS
    numerical = record('numerical.json')
    validate_worker_payload(numerical, manifest, reservation, admission)
    raw = numerical['oracle']['raw_by_degree']
    assert numerical['oracle']['numerical_accepted'] is True
    assert set(raw) == {'24','26'} and all(len(raw[d]) == 38 for d in raw)
    assert all(len(numerical['assembly_receipts'][d]) == 38 for d in raw)
    assert all(x['accepted'] is True for x in numerical['oracle']['degree_checks'].values())
    assert len(numerical['oracle']['pair_checks']) == 38
    assert all(x['accepted'] is True for x in numerical['oracle']['pair_checks'].values())
    worker_log = (HERE/'run/worker.log').read_text()
    assert worker_log.count(' stage=form\n') == worker_log.count(' stage=assemble\n') == 76
    geometry = numerical['geometry']
    assert (geometry['cells'], geometry['vertices'], geometry['exterior_facets'],
            geometry['mixed_space_dofs']) == (48,27,48,402)
    result = record('result.json')
    completion = record('completion.json')
    caller = record('caller.json')
    caller_completion = record('caller_completion.json')
    assert result['status'] == 'PROVISIONAL_PASS'
    assert completion['status'] == caller['status'] == caller_completion['status'] == 'PASS'
    assert caller['inner_status'] == 'PASS' and caller['reason'] is None
    assert record('exit.json') == record('finished.json')
    assert result['exit']['exit_code'] == 0 and result['exit']['manager_result'] == 'success'
    assert result['held_scope']['source_binding'] == source
    assert result['held_scope']['memory_max_bytes'] == 1536*1024**2
    assert result['held_scope']['swap_max_bytes'] == 0
    assert result['held_scope']['pids_max'] == 32
    assert result['held_scope']['independent_expiry_seconds'] == 150.0
    assert result['held_scope']['threads'] == result['held_scope']['mpi_ranks'] == 1
    cleanup = result['cleanup']
    assert cleanup['empty'] is True and cleanup['unknown_children'] is False
    assert cleanup['resource_snapshot_complete'] is True
    snapshot = record('resource_snapshot.json')
    assert cleanup['memory_peak_bytes'] == snapshot['memory_peak_bytes']
    assert cleanup['pids_peak'] == snapshot['pids_peak']
    assert 0 <= snapshot['memory_peak_bytes'] <= 1536*1024**2
    assert 0 <= snapshot['pids_peak'] <= 32
    for key in ('max','oom','oom_kill'):
        assert snapshot['memory_events'][key] == 0
    assert snapshot['pids_events']['max'] == 0
    assert caller_completion['elapsed_after_caller_save'] <= 180
    assert completion['observed_elapsed_after_result_and_log'] <= 180
    assert not (HERE/'run/late.json').exists() and not (source_dir/'late.json').exists()
    held = record('held.json')
    assert not Path('/proc',str(held['pid'])).exists()
    assert not (Path('/sys/fs/cgroup')/held['cgroup'].lstrip('/')).exists()
    assert result['cleanup']['manager_final']['MainPID'] == '0'
    assert result['cleanup']['manager_final']['ControlGroup'] == ''
    old = runpy.run_path(str(ROOT/'docs/realizability/evidence/r250/audit.py'))['run']()
    assert old == json.loads((ROOT/'docs/realizability/evidence/r250/audit.json').read_text())
    # The R246 policy remains a saved, independent fixture status.
    r246 = json.loads((ROOT/'docs/realizability/evidence/r246/run/numerical.json').read_text())
    old_manifest = json.loads((ROOT/'verification/nonlinear_port/future_fem.json').read_text())
    validate_worker_result(r246,old_manifest['versions'],old_manifest['gates'],
                           policy=old_manifest['poiseuille_diagnostic_policy'])
    prior = json.loads((ROOT/'docs/realizability/evidence/r251/source_inventory.json').read_text())['source_sha256']
    assert len(prior) == 36
    for name, expected in prior.items(): assert digest(ROOT/name) == expected, name
    modules = [name for name in sys.modules if name.split('.')[0] in
               {'numpy','dolfinx','basix','ufl','ffcx','petsc4py','mpi4py','scipy'}]
    assert not modules
    max_ratio = {degree:max(abs(v['difference'])/v['limit']
                            for v in numerical['oracle']['degree_checks'][degree]['target_checks'].values())
                 for degree in ('24','26')}
    return dict(status='PASS',attempts_granted=1,attempts_spent=1,
                launch_commit=admission['source_commit'],worker_exit=0,caller_exit=0,
                raw_originals_preserved=len(inventory['files']),raw_original_bytes=sum(v['bytes'] for v in inventory['files'].values()),
                old_raw_originals_verified=old['raw_originals_verified'],old_allocations_spent=5,
                r246_saved_controller_replay='PASS',r242_status='INCOMPLETE',
                numerical_accepted=True,raw_keys_per_degree=38,assembly_calls=76,
                pair_checks_passed=38,maximum_degree_target_ratio=max_ratio,
                geometry=geometry,phase_seconds=numerical['phase_seconds'],
                worker_intervals=numerical['worker_intervals'],
                controller_setup_seconds=result['setup_seconds'],controller_work_seconds=result['work_seconds'],
                controller_finish_seconds=completion['observed_finish_seconds'],
                caller_elapsed_after_save_seconds=caller_completion['elapsed_after_caller_save'],
                memory_peak_bytes=snapshot['memory_peak_bytes'],pids_peak=snapshot['pids_peak'],
                memory_events=snapshot['memory_events'],pids_events=snapshot['pids_events'],
                empty_cleanup=True,recorded_pid_absent=True,recorded_cgroup_absent=True,
                no_late_marker=True,report_bytes=inventory['files']['numerical.json']['bytes'],
                source_files_unchanged=36,prior_audit_reproduced=True,
                final_save_tail_observed=False,independent_parent_wall_observed=False,
                numerical_modules_loaded_by_audit=modules)

if __name__ == '__main__':
    answer=run()
    (HERE/'audit.json').write_text(json.dumps(answer,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps(answer,sort_keys=True,allow_nan=False))
