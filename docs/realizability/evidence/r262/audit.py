"""Replay R262's saved one-use result without a numerical import or worker."""
import hashlib
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))


def read(path):
    return json.loads(Path(path).read_text())


def run():
    inventory = read(HERE/'run_hashes.json')
    original = Path(inventory['source_directory'])
    saved = HERE/'run'
    assert inventory['run_count'] == 11
    assert set(inventory['run_files']) == {p.name for p in saved.iterdir()}
    assert set(inventory['run_files']) == {p.name for p in original.iterdir()}
    total = 0
    for name, record in inventory['run_files'].items():
        data = (saved/name).read_bytes()
        assert data == (original/name).read_bytes(), name
        assert len(data) == record['bytes'] and hashlib.sha256(data).hexdigest() == record['sha256'], name
        total += len(data)
    for name, record in inventory['caller_files'].items():
        data = (HERE/name).read_bytes()
        assert data == (Path(inventory['caller_source_directory'])/name).read_bytes(), name
        assert len(data) == record['bytes'] and hashlib.sha256(data).hexdigest() == record['sha256'], name
        total += len(data)
    assert total == inventory['total_bytes'] == 13250
    allocation = read(ROOT/'docs/realizability/evidence/r261/allocation.json')
    reservation = read(saved/'reservation.json')
    admission = read(saved/'admission.json')
    held = read(saved/'held.json')
    release = read(saved/'release.json')
    result = read(saved/'result.json')
    completion = read(saved/'completion.json')
    caller = read(saved/'caller.json')
    caller_completion = read(saved/'caller_completion.json')
    failure = read(saved/'failure.json')
    launch = '8de6ffd1d9c089eead43a804fe59cb65ea789774'
    assert allocation['attempts_granted'] == 1 and allocation['run_directory'] == str(original)
    assert reservation['status'] == 'RESERVED' and reservation['attempt'] == 1
    assert reservation['source_commit'] == admission['source_commit'] == caller['preflight']['source_commit'] == launch
    assert held['source_binding']['source_commit'] == failure['source_binding']['source_commit'] == launch
    assert held['nonce'] == release['nonce'] == reservation['release_nonce']
    assert held['cgroup'] == release['cgroup'] == result['held_scope']['cgroup_path']
    assert result['held_scope']['worker_held'] is True and result['held_scope']['all_task_processes_in_scope'] is True
    assert all(record['status'] == 'INCOMPLETE' for record in (result, completion, caller, caller_completion))
    assert caller['inner_status'] == 'INCOMPLETE' and caller['reason'] is None
    assert caller['preflight']['manager_version'] == allocation['reviewed_manager_version']
    assert caller['preflight']['source_files'] == 46 and caller['preflight']['runtime_artifacts_verified'] == 11
    assert result['reason'] == 'missing, exceeded or unknown cleanup/resource evidence'
    assert result['cleanup']['empty'] is True and result['cleanup']['unknown_children'] is False
    assert result['cleanup']['resource_snapshot_complete'] is False
    assert result['cleanup']['manager_final']['ExecMainStatus'] == '1'
    assert result['cleanup']['manager_final']['MainPID'] == '0'
    assert result['cleanup']['manager_final']['ControlGroup'] == ''
    assert failure['diagnostic_only'] is True and failure['exception_type'] == 'RecursionError'
    assert failure['last_completed_stage'] == 'primary_forms'
    assert failure['last_begun_stage'] == 'primary_compilation'
    assert failure['frames_truncated'] is True
    assert any(frame['file'].endswith('/cube_adapter.py') and frame['line'] == 195
               for frame in failure['traceback'])
    assert any(frame['file'].endswith('/ufl/algorithms/apply_derivatives.py')
               for frame in failure['traceback'])
    assert len((saved/'failure.json').read_bytes()) <= 32768
    assert 'RecursionError: maximum recursion depth exceeded' in (saved/'worker.log').read_text()
    assert 'worker failed before completion: exit-code' in (saved/'run.log').read_text()
    stdout = read(HERE/'navier-r262-caller-stdout.txt')
    assert stdout['status'] == 'INCOMPLETE' and stdout['inner_status'] == 'INCOMPLETE'
    assert not (HERE/'navier-r262-caller-stderr.txt').read_bytes()
    assert not Path('/proc', str(held['pid'])).exists()
    assert not (Path('/sys/fs/cgroup')/held['cgroup'].lstrip('/')).exists()
    assert not any((saved/name).exists() for name in
                   ('numerical.json', 'resource_snapshot.json', 'exit.json', 'finished.json', 'late.json'))
    prior = runpy.run_path(str(ROOT/'docs/realizability/evidence/r260/audit.py'))['run']()
    assert prior['raw_originals_verified'] == 84 and prior['spent_reservations'] == 7
    assert prior['recorded_pids_cgroups_absent']
    assert prior['saved_r246_validator'] == prior['saved_r253_validator'] == 'PASS'
    assert prior['saved_r258_status'] == 'INCOMPLETE'
    forbidden = {'numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py', 'scipy'}
    loaded = sorted(name for name in sys.modules if name.split('.')[0] in forbidden)
    assert not loaded
    return dict(status='INCOMPLETE', launch_commit=launch, attempts_granted=1,
                attempts_spent=1, prior_allocations_spent=7, raw_run_files=11,
                caller_files=2, raw_bytes=total, original_bytes_verified=True,
                reserved_held_released=True, worker_exit_status=1,
                failure_stage='primary_compilation', failure_type='RecursionError',
                numerical_report_present=False, resource_snapshot_present=False,
                cleanup_empty=True, recorded_pid_absent=True, recorded_cgroup_absent=True,
                saved_r246_validator='PASS', saved_r253_validator='PASS',
                saved_r258_status='INCOMPLETE', numerical_modules_loaded=loaded)


if __name__ == '__main__':
    result = run()
    (HERE/'audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
