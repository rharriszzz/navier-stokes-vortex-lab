"""Replay the saved R258 incomplete outcome without importing numerical modules."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def read(path):
    return json.loads(Path(path).read_text())


def run():
    inventory = read(HERE/'run_hashes.json')
    original = Path(inventory['source_directory'])
    saved = HERE/'run'
    assert inventory['count'] == 10
    assert set(inventory['files']) == {p.name for p in saved.iterdir()}
    assert set(inventory['files']) == {p.name for p in original.iterdir()}
    total = 0
    for name, record in inventory['files'].items():
        blob = (saved/name).read_bytes()
        assert blob == (original/name).read_bytes(), name
        assert len(blob) == record['bytes'], name
        assert hashlib.sha256(blob).hexdigest() == record['sha256'], name
        total += len(blob)
    assert total == inventory['total_bytes']
    reservation = read(saved/'reservation.json')
    admission = read(saved/'admission.json')
    held = read(saved/'held.json')
    release = read(saved/'release.json')
    result = read(saved/'result.json')
    completion = read(saved/'completion.json')
    caller = read(saved/'caller.json')
    caller_completion = read(saved/'caller_completion.json')
    assert reservation['status'] == 'RESERVED' and reservation['attempt'] == 1
    assert reservation['fixture'] == admission['fixture'] == 'manufactured'
    assert admission['approved'] is True and admission['attempts_granted'] == 1
    source = reservation['source_commit']
    assert source == admission['source_commit'] == held['source_binding']['source_commit']
    assert source == 'c34ecabe5cb9a89687bf4eaa782bd5b76022c1b5'
    assert held['nonce'] == release['nonce'] == reservation['release_nonce']
    assert held['cgroup'] == release['cgroup'] == result['held_scope']['cgroup_path']
    assert result['held_scope']['worker_held'] is True
    assert result['status'] == completion['status'] == caller['status'] == caller_completion['status'] == 'INCOMPLETE'
    assert caller['inner_status'] == 'INCOMPLETE' and caller['reason'] is None
    assert result['reason'] == 'missing, exceeded or unknown cleanup/resource evidence'
    assert result['cleanup']['empty'] is True and result['cleanup']['unknown_children'] is False
    assert result['cleanup']['resource_snapshot_complete'] is False
    assert result['cleanup']['manager_final']['ExecMainStatus'] == '1'
    assert result['cleanup']['manager_final']['MainPID'] == '0'
    assert result['cleanup']['manager_final']['ControlGroup'] == ''
    assert 'RecursionError: maximum recursion depth exceeded' in (saved/'worker.log').read_text()
    assert 'worker failed before completion: exit-code' in (saved/'run.log').read_text()
    assert not Path('/proc', str(held['pid'])).exists()
    assert not (Path('/sys/fs/cgroup')/held['cgroup'].lstrip('/')).exists()
    assert not any((saved/name).exists() for name in
        ('numerical.json', 'resource_snapshot.json', 'exit.json', 'finished.json', 'late.json'))
    preflight = read(HERE/'preflight_refusal.json')
    assert preflight['attempt_spent'] is False and preflight['run_directory_absent_after_refusal'] is True
    assert read(ROOT/'docs/realizability/evidence/r257/allocation.json')['attempts_granted'] == 1
    return dict(status='INCOMPLETE', attempts_spent=1, attempts_granted=1,
        launch_commit=source, raw_files=len(inventory['files']), raw_bytes=total,
        original_bytes_verified=True, reservation_present=True, held_and_released=True,
        worker_exit_status=1, worker_log='RecursionError: maximum recursion depth exceeded',
        numerical_report_present=False, resource_snapshot_present=False,
        caller_completion='INCOMPLETE', cleanup_empty=True,
        recorded_pid_absent=True, recorded_cgroup_absent=True,
        pre_reservation_sandbox_refusal_recorded=True,
        no_second_numerical_attempt=True)


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
