"""Read-only R266 saved-result audit; never starts a manager or numerical worker."""
import hashlib
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUN = HERE / 'run'
LAUNCH = 'd5b42eb0433c81c663810ab2858b67f6b4c8c789'
FORBIDDEN = {'numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py', 'scipy'}


def read(path):
    return json.loads(path.read_text())


def run():
    inventory = read(HERE / 'run_hashes.json')
    original = Path(inventory['source_directory'])
    assert original == Path('/tmp/navier-manufactured-r265-once')
    assert inventory['run_count'] == 15
    assert set(inventory['run_files']) == {p.name for p in RUN.iterdir()}
    assert set(inventory['run_files']) == {p.name for p in original.iterdir()}
    total = 0
    for name, record in inventory['run_files'].items():
        saved = (RUN / name).read_bytes()
        assert saved == (original / name).read_bytes(), name
        assert len(saved) == record['bytes']
        assert hashlib.sha256(saved).hexdigest() == record['sha256'], name
        total += len(saved)
    assert inventory['caller_count'] == 4
    for name, record in inventory['caller_files'].items():
        saved = (HERE / name).read_bytes()
        assert saved == Path(record['original']).read_bytes(), name
        assert len(saved) == record['bytes']
        assert hashlib.sha256(saved).hexdigest() == record['sha256'], name
        total += len(saved)
    assert total == inventory['total_bytes']

    preflight = read(HERE / 'preflight.json')
    refused = read(HERE / 'sandbox-caller-stdout.txt')
    assert preflight['first_exit_code'] == 1
    assert refused['status'] == 'INCOMPLETE' and refused['inner_status'] is None
    assert refused['reason'] == 'Refusal: sd-bus operation failed: errno 1'
    assert not (HERE / 'sandbox-caller-stderr.txt').read_bytes()
    assert preflight['fixed_directory_after_refusal'] == 'absent'
    assert preflight['reservation_after_refusal'] == 'absent'
    assert preflight['new_worker_after_refusal'] == 'absent'
    assert preflight['source_change'] is False
    assert preflight['allocation_spent_by_first_command'] is False

    allocation = read(ROOT / 'docs/realizability/evidence/r265/allocation.json')
    assert allocation['attempts_granted'] == 1
    assert allocation['run_directory'] == str(original)
    reservation = read(RUN / 'reservation.json')
    admission = read(RUN / 'admission.json')
    held = read(RUN / 'held.json')
    release = read(RUN / 'release.json')
    finished = read(RUN / 'finished.json')
    exit_record = read(RUN / 'exit.json')
    result = read(RUN / 'result.json')
    completion = read(RUN / 'completion.json')
    caller = read(RUN / 'caller.json')
    caller_completion = read(RUN / 'caller_completion.json')
    host_stdout = read(HERE / 'host-caller-stdout.txt')
    numerical = read(RUN / 'numerical.json')
    snapshot = read(RUN / 'resource_snapshot.json')
    assert not (HERE / 'host-caller-stderr.txt').read_bytes()
    assert reservation['status'] == 'RESERVED' and reservation['attempt'] == 1
    assert (reservation['source_commit'] == admission['source_commit']
            == caller['preflight']['source_commit'] == LAUNCH)
    assert held['source_binding']['source_commit'] == numerical['source_binding']['source_commit'] == LAUNCH
    assert held['nonce'] == release['nonce'] == finished['nonce'] == exit_record['nonce'] == reservation['release_nonce']
    assert held['cgroup'] == release['cgroup'] == result['held_scope']['cgroup_path']
    assert result['held_scope']['worker_held'] is True
    assert result['held_scope']['all_task_processes_in_scope'] is True
    assert result['exit']['exit_code'] == 0 and result['exit']['manager_result'] == 'success'
    assert all(item['status'] == 'INCOMPLETE' for item in (result, completion, caller, caller_completion, host_stdout))
    assert caller['inner_status'] == host_stdout['inner_status'] == 'INCOMPLETE'
    assert caller['reason'] is host_stdout['reason'] is None
    assert result['reason'] == 'Refusal: failed or inconsistent manufactured evidence'
    assert caller['preflight']['source_files'] == 47
    assert caller['preflight']['runtime_artifacts_verified'] == 11
    assert caller['preflight']['manager_version'] == allocation['reviewed_manager_version']

    report = numerical['report']
    assert report['numerical_accepted'] is False
    assert {key for key, value in report['checks'].items() if not value} == {'degree24', 'degree26'}
    for degree in ('24', '26'):
        validation = report['degree_validation'][degree]
        assert validation['accepted'] is False
        assert {key for key, value in validation['checks'].items() if not value} == {'angular_budget', 'angular_interval'}
        budget = validation['field_report']['angular_budget']
        interval = validation['interval_budgets']['angular']
        assert abs(budget['signed_defect']) > budget['limit']
        assert abs(interval['defect']) > interval['limit']
    assert (RUN / 'linear_system.json').is_file()
    assert snapshot['memory_peak_bytes'] == result['cleanup']['memory_peak_bytes']
    assert snapshot['pids_peak'] == result['cleanup']['pids_peak']
    assert snapshot['memory_events']['max'] == snapshot['memory_events']['oom'] == snapshot['memory_events']['oom_kill'] == 0
    assert snapshot['pids_events']['max'] == 0
    assert snapshot['memory_peak_bytes'] < 1536 * 1024 * 1024
    assert snapshot['pids_peak'] <= 32
    assert result['cleanup']['empty'] is True and result['cleanup']['unknown_children'] is False
    assert result['cleanup']['resource_snapshot_complete'] is True
    assert result['cleanup']['manager_final']['MainPID'] == '0'
    assert result['cleanup']['manager_final']['ControlGroup'] == ''
    assert not Path('/proc', str(held['pid'])).exists()
    assert not (Path('/sys/fs/cgroup') / held['cgroup'].lstrip('/')).exists()
    assert not (RUN / 'failure.json').exists()

    old = runpy.run_path(str(HERE.parent / 'r264/audit.py'))['run']()
    assert old['raw_original_files_verified'] == 97
    assert old['git_index_raw_files_verified'] == 97
    assert old['spent_reservations'] == 8
    assert old['recorded_pids_cgroups_absent'] is True
    assert old['saved_r246_validator'] == old['saved_r253_validator'] == 'PASS'
    loaded = sorted(name for name in sys.modules if name.split('.')[0] in FORBIDDEN)
    assert not loaded
    return dict(status='INCOMPLETE', launch_commit=LAUNCH, attempts_granted=1,
                attempts_spent=1, prior_allocations_spent=8,
                recoverable_preflight_refusals=1, run_files=15, caller_files=4,
                raw_bytes=total, original_bytes_verified=True,
                reserved_held_released=True, worker_exit_status=0,
                numerical_report_present=True, linear_system_present=True,
                numerical_accepted=False, failed_degree_checks=['angular_budget', 'angular_interval'],
                resource_snapshot_present=True,
                memory_peak_bytes=snapshot['memory_peak_bytes'],
                pids_peak=snapshot['pids_peak'], resource_events_zero=True,
                cleanup_empty=True, recorded_pid_absent=True,
                recorded_cgroup_absent=True, old_raw_files_verified=97,
                old_allocations_spent=8, saved_r246_validator='PASS',
                saved_r253_validator='PASS', numerical_modules_loaded=loaded)


if __name__ == '__main__':
    result = run()
    (HERE / 'audit.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, sort_keys=True))
