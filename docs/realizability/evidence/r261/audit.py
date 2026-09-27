"""R261 read-only source, artifact and saved-evidence audit."""
import hashlib
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run():
    prior = read(ROOT/'docs/realizability/evidence/r260/audit.json')['source_sha256']
    current = read(HERE/'source_inventory.json')['source_sha256']
    assert len(prior) == len(current) == 46 and set(prior) == set(current)
    changed = {name for name in prior if prior[name] != current[name]}
    assert changed == {
        'verification/nonlinear_port/manufactured_driver.py',
        'verification/nonlinear_port/manufactured_failure.py',
        'verification/nonlinear_port/test_manufactured_failure.py',
    }
    for name, sha in current.items():
        assert digest(ROOT/name) == sha, name
    allocation = read(HERE/'allocation.json')
    artifacts = read(HERE/'artifacts.json')
    assert allocation['request'] == 'R261'
    assert allocation['attempts_granted'] == 1 and allocation['attempts_spent_at_review'] == 0
    assert allocation['run_directory'] == '/tmp/navier-manufactured-r261-once'
    assert not Path(allocation['run_directory']).exists()
    assert not Path(allocation['run_directory']).is_symlink()
    for key, file in (('source_inventory_sha256', 'source_inventory.json'),
                      ('artifact_inventory_sha256', 'artifacts.json'),
                      ('caller_sha256', 'run_once.py')):
        assert allocation[key] == digest(HERE/file), key
    assert allocation['manifest_sha256'] == digest(ROOT/'verification/nonlinear_port/future_manufactured.json')
    for name, sha in artifacts['runtime_files_sha256'].items():
        assert digest(name) == sha, name
    for name, resolved in artifacts['library_resolutions'].items():
        assert str(Path(name).resolve(strict=True)) == resolved, name
    assert digest(artifacts['cached_archive']) == artifacts['package']['sha256']
    assert digest(Path(allocation['interpreter']).resolve(strict=True)) == allocation['executable_sha256']
    old = runpy.run_path(str(ROOT/'docs/realizability/evidence/r260/audit.py'))['run']()
    assert old['raw_originals_verified'] == 84 and old['spent_reservations'] == 7
    assert old['recorded_pids_cgroups_absent']
    assert old['saved_r246_validator'] == old['saved_r253_validator'] == 'PASS'
    assert old['saved_r258_status'] == 'INCOMPLETE'
    tests = read(HERE/'tests.json')
    caller = read(HERE/'caller_tests.json')
    assert tests['tests'] == 114 and not tests['errors'] and not tests['failures']
    assert caller['count'] == 6 and not caller['errors'] and not caller['failures']
    assert not tests['numerical_modules_loaded'] and not caller['numerical_modules_loaded']
    forbidden = {'numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py', 'scipy'}
    loaded = sorted(name for name in sys.modules if name.split('.')[0] in forbidden)
    assert not loaded
    return dict(status='ADMITTED_FOR_LATER_EXECUTION', source_files=len(current),
                changed_from_r260=sorted(changed), runtime_artifacts_verified=11,
                library_resolutions_verified=4, archive_and_interpreter_verified=True,
                raw_originals_verified=84, historical_reservations_spent=7,
                recorded_pids_cgroups_absent=True, saved_r246_validator='PASS',
                saved_r253_validator='PASS', saved_r258_status='INCOMPLETE',
                source_tests=114, fake_caller_tests=6, numerical_modules_loaded=loaded,
                new_directory_absent=True, new_attempts_spent=0,
                manager_worker_reservation_or_numerical_import=False)


if __name__ == '__main__':
    result = run()
    (HERE/'audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
