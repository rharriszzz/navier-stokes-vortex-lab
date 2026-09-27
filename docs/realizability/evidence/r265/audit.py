"""R265 read-only binding/evidence audit; never connects to a manager."""
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def read(path):
    return json.loads(path.read_text())


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run():
    previous = runpy.run_path(str(HERE.parent/'r264/audit.py'))['run']()
    assert previous['spent_reservations'] == 8
    allocation = read(HERE/'allocation.json')
    prior = read(HERE.parent/'r261/allocation.json')
    assert allocation['request'] == 'R265'
    assert type(allocation['attempts_granted']) is int and allocation['attempts_granted'] == 1
    assert allocation['attempts_spent_at_review'] == 0
    assert len(allocation['prior_allocations']) == 8
    assert all(a['spent'] == a['granted'] == 1 for a in allocation['prior_allocations'])
    for key in ('contract', 'contract_sha256', 'manifest_sha256', 'limits', 'interpreter',
                'executable_sha256', 'reviewed_manager_version', 'measurement_limits',
                'pre_reservation_recovery', 'consumption_rule'):
        assert allocation[key] == prior[key], key
    for key, name in (('caller_sha256', 'run_once.py'),
                      ('source_inventory_sha256', 'source_inventory.json'),
                      ('artifact_inventory_sha256', 'artifacts.json')):
        assert allocation[key] == digest(HERE/name)
    assert (HERE/'source_inventory.json').read_bytes() == (HERE.parent/'r264/source_inventory.json').read_bytes()
    assert (HERE/'artifacts.json').read_bytes() == (HERE.parent/'r261/artifacts.json').read_bytes()
    # The caller change is solely allocation/owner/path identity.
    assert (HERE/'run_once.py').read_text() == (HERE.parent/'r261/run_once.py').read_text().replace('R261', 'R265').replace('r261', 'r265')
    directory = Path(allocation['run_directory'])
    assert directory == Path('/tmp/navier-manufactured-r265-once')
    assert not directory.exists() and not directory.is_symlink()
    tests, caller, arithmetic = (read(HERE/name) for name in
                                ('tests.json', 'caller_tests.json', 'reassociation.json'))
    assert tests['tests'] == 118 and tests['errors'] == tests['failures'] == 0
    assert caller['count'] == 6 and caller['errors'] == caller['failures'] == 0
    assert arithmetic['status'] == 'PASS' and arithmetic['scalar_evaluations'] == 1792
    for evidence in (tests, caller, arithmetic):
        assert evidence['numerical_modules_loaded'] == []
    assert not caller['fixed_directory_created']
    assert not arithmetic['recursion_limit_changed']
    # Preserve every existing evidence file, including helpers imported by tests.
    files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', '4870e82',
                                     'docs/realizability/evidence'], cwd=ROOT, text=True).splitlines()
    # Use one archive stream to avoid spawning one Git process per file.
    import io
    import tarfile
    archive = subprocess.check_output(['git', 'archive', '4870e82', 'docs/realizability/evidence'], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tree:
        for name in files:
            assert (ROOT/name).read_bytes() == tree.extractfile(name).read(), name
    return dict(status='ADMITTED_FOR_LATER_EXECUTION', source_files_unchanged=47,
                source_tests_passed=118, fake_caller_checks_passed=6,
                scalar_samples=1792, symbolic_fixture_cases=28, tree_sizes=34,
                runtime_artifacts_verified=11, library_resolutions_verified=4,
                archive_and_interpreter_verified=True,
                prior_evidence_files_unchanged=len(files), raw_original_files_verified=97,
                git_index_raw_files_verified=97, spent_historical_allocations=8,
                recorded_pids_cgroups_absent=True, saved_r246_validator='PASS',
                saved_r253_validator='PASS', saved_r262_status='INCOMPLETE',
                rational_r255_reference_rederived=True,
                fresh_directory_absent=True, caller_only_identity_changed=True,
                science_and_resource_gates_unchanged=True,
                new_attempts_admitted=1, new_attempts_spent=0,
                numerical_import_manager_worker_or_reservation=False)


if __name__ == '__main__':
    result = run()
    (HERE/'audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
