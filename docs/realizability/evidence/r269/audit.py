"""Read-only R269 preservation and scoped source inventory audit."""
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = '2c25fc60076a48ac1610ed3c1dc956b482bbd963'
CHANGED = {'verification/nonlinear_port/manufactured_angular.py'}
NEW = {'verification/nonlinear_port/test_manufactured_angular_assembly.py'}


def run():
    old = json.loads((HERE.parent/'r266/audit.json').read_text())
    assert old['status'] == 'INCOMPLETE' and old['attempts_spent'] == 1
    old_count = 0
    for request in ('r232','r235','r238','r242','r246','r253','r258','r262','r266'):
        folder = HERE.parent/request
        inventory = json.loads((folder/'run_hashes.json').read_text())
        files = inventory.get('files', inventory.get('run_files', {}))
        entries = [(folder/'run'/name, Path(inventory['source_directory'])/name, record)
                   for name, record in files.items()]
        if 'caller_files' in inventory:
            for name, record in inventory['caller_files'].items():
                original = record.get('original')
                if original is None:
                    original = str(Path(inventory['caller_source_directory'])/name)
                entries.append((folder/name, Path(original), record))
        for saved, original, record in entries:
            blob = saved.read_bytes()
            assert blob == original.read_bytes(), saved
            assert len(blob) == record['bytes'] and hashlib.sha256(blob).hexdigest() == record['sha256']
            assert subprocess.check_output(['git','show',':'+str(saved.relative_to(ROOT))],cwd=ROOT) == blob
            old_count += 1
        held = json.loads((folder/'run/held.json').read_text())
        assert json.loads((folder/'run/reservation.json').read_text())['attempt'] == 1
        assert not Path('/proc', str(held['pid'])).exists()
        assert not (Path('/sys/fs/cgroup')/held['cgroup'].lstrip('/')).exists()
    assert old_count == 116
    source = json.loads((HERE.parent/'r268/audit.json').read_text())['source_sha256']
    assert len(source) == 49 and CHANGED <= source.keys() and not NEW & source.keys()
    unchanged = {name: digest for name, digest in source.items() if name not in CHANGED}
    for name, digest in unchanged.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    for name in CHANGED | NEW:
        assert (ROOT/name).is_file(), name
    baseline_evidence = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE,
        'docs/realizability/evidence'], cwd=ROOT, text=True).splitlines()
    subprocess.run(['git', 'diff', '--exit-code', BASE, '--', *baseline_evidence],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    artifacts = json.loads((HERE/'artifacts.json').read_text())
    for name, digest in artifacts['runtime_files_sha256'].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest
    for name, resolved in artifacts['library_resolutions'].items():
        assert str(Path(name).resolve(strict=True)) == resolved
    assert hashlib.sha256(Path(artifacts['cached_archive']).read_bytes()).hexdigest() == artifacts['package']['sha256']
    allocation = json.loads((HERE.parent/'r265/allocation.json').read_text())
    assert hashlib.sha256(Path(allocation['interpreter']).resolve(strict=True).read_bytes()).hexdigest() == allocation['executable_sha256']
    inventory = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                 for name in sorted(source.keys() | NEW)}
    allocation = json.loads((HERE/'allocation.json').read_text())
    prior = json.loads((HERE.parent/'r265/allocation.json').read_text())
    for key in ('contract', 'contract_sha256', 'manifest_sha256', 'limits', 'interpreter',
                'executable_sha256', 'reviewed_manager_version', 'measurement_limits',
                'pre_reservation_recovery', 'consumption_rule'):
        assert allocation[key] == prior[key], key
    assert allocation['request'] == 'R269' and allocation['attempts_granted'] == 1
    assert allocation['attempts_spent_at_review'] == 0
    assert len(allocation['prior_allocations']) == 9
    assert all(v['spent'] == v['granted'] == 1 for v in allocation['prior_allocations'])
    for key, name in (('caller_sha256', 'run_once.py'),
                      ('source_inventory_sha256', 'source_inventory.json'),
                      ('artifact_inventory_sha256', 'artifacts.json')):
        assert allocation[key] == hashlib.sha256((HERE/name).read_bytes()).hexdigest()
    assert json.loads((HERE/'source_inventory.json').read_text())['source_sha256'] == inventory
    old_artifacts = json.loads((HERE.parent/'r265/artifacts.json').read_text())
    assert all(artifacts['runtime_files_sha256'][k] == v for k,v in old_artifacts['runtime_files_sha256'].items())
    assert len(artifacts['runtime_files_sha256']) == 15
    directory = Path(allocation['run_directory'])
    assert directory == Path('/tmp/navier-manufactured-r269-once')
    assert not directory.exists() and not directory.is_symlink()
    tests = json.loads((HERE/'tests.json').read_text())
    caller = json.loads((HERE/'caller_tests.json').read_text())
    assert tests['tests'] == 127 and tests['failures'] == tests['errors'] == 0
    assert caller['count'] == 8 and caller['failures'] == caller['errors'] == 0
    assert not tests['numerical_modules_loaded'] and not caller['numerical_modules_loaded']
    assert tests['saved_r246_validator'] == tests['saved_r253_validator'] == 'PASS'
    assert tests['saved_r266_validator'] == 'INCOMPLETE'
    assert tests['r267_decomposition_controls'] == 4
    loaded = sorted(name for name in sys.modules if name.split('.')[0] in
                    {'numpy','dolfinx','basix','ufl','ffcx','petsc4py','mpi4py','scipy'})
    assert not loaded
    return dict(status='ADMITTED_FOR_LATER_EXECUTION', old_source_files=len(source),
        new_attempts_admitted=1, new_attempts_spent=0, fresh_directory_absent=True,
        physical_and_resource_gates_unchanged=True,
        source_tests_passed=127, fake_caller_checks_passed=8,
        unchanged_old_source=len(unchanged), changed_old_source=sorted(CHANGED),
        new_source=sorted(NEW), source_sha256=inventory,
        historical_evidence_files_unchanged=len(baseline_evidence),
        original_and_index_files_unchanged=old_count,
        spent_allocations=9,
        runtime_artifacts_verified=15, resource_snapshot_preserved=True,
        recorded_pid_cgroup_absent=True, numerical_modules_loaded=loaded,
        numerical_or_manager_work=False)


if __name__ == '__main__':
    result = run()
    (HERE/'audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'source_sha256'}, sort_keys=True))
