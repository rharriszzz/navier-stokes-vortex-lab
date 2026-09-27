"""Read-only R271 preservation audit; no numerical imports or manager access."""
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = '790210217dc717be7a1ed67b1f295a0e1ade1ad8'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    old_count = 0
    for request in ('r232', 'r235', 'r238', 'r242', 'r246', 'r253', 'r258', 'r262', 'r266'):
        folder = HERE.parent/request
        inventory = json.loads((folder/'run_hashes.json').read_text())
        files = inventory.get('files', inventory.get('run_files', {}))
        entries = [(folder/'run'/name, Path(inventory['source_directory'])/name, record)
                   for name, record in files.items()]
        for name, record in inventory.get('caller_files', {}).items():
            original = record.get('original')
            if original is None:
                original = str(Path(inventory['caller_source_directory'])/name)
            entries.append((folder/name, Path(original), record))
        for saved, original, record in entries:
            blob = saved.read_bytes()
            assert blob == original.read_bytes(), saved
            assert len(blob) == record['bytes'] and digest(saved) == record['sha256']
            assert subprocess.check_output(['git', 'show', ':'+str(saved.relative_to(ROOT))], cwd=ROOT) == blob
            old_count += 1
        held = json.loads((folder/'run/held.json').read_text())
        assert json.loads((folder/'run/reservation.json').read_text())['attempt'] == 1
        assert not Path('/proc', str(held['pid'])).exists()
        assert not (Path('/sys/fs/cgroup')/held['cgroup'].lstrip('/')).exists()
    assert old_count == 116
    verified = runpy.run_path(str(HERE.parent/'r270/verify_saved.py'))['run']()
    for name in verified['copied_run_files']:
        saved = HERE.parent/'r270/run'/name
        assert subprocess.check_output(['git', 'show', ':'+str(saved.relative_to(ROOT))], cwd=ROOT) == saved.read_bytes()
    allocation = json.loads((HERE.parent/'r269/allocation.json').read_text())
    for key, name in (('caller_sha256', 'run_once.py'),
                      ('source_inventory_sha256', 'source_inventory.json'),
                      ('artifact_inventory_sha256', 'artifacts.json')):
        assert allocation[key] == digest(HERE.parent/'r269'/name)
    source = json.loads((HERE.parent/'r269/source_inventory.json').read_text())['source_sha256']
    for name, sha in source.items():
        assert digest(ROOT/name) == sha, name
    artifacts = json.loads((HERE.parent/'r269/artifacts.json').read_text())
    for name, sha in artifacts['runtime_files_sha256'].items():
        assert digest(Path(name)) == sha, name
    for name, resolved in artifacts['library_resolutions'].items():
        assert str(Path(name).resolve(strict=True)) == resolved
    assert digest(Path(artifacts['cached_archive'])) == artifacts['package']['sha256']
    assert digest(Path(allocation['interpreter']).resolve(strict=True)) == allocation['executable_sha256']
    historical = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE,
        'docs/realizability/evidence'], cwd=ROOT, text=True).splitlines()
    subprocess.run(['git', 'diff', '--exit-code', BASE, '--', *historical],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    forbidden = {'numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py', 'scipy'}
    loaded = sorted(name for name in sys.modules if name.split('.')[0] in forbidden)
    assert not loaded
    return dict(status='PASS', old_original_and_index_files=old_count,
        r270_original_and_index_files=len(verified['copied_run_files']),
        historical_evidence_files_unchanged=len(historical), source_bindings_unchanged=len(source),
        runtime_artifacts=len(artifacts['runtime_files_sha256']),
        library_resolutions=len(artifacts['library_resolutions']), archive_interpreter_verified=True,
        spent_allocations=10, recorded_pids_cgroups_absent=True,
        r269_allocation_bindings_unchanged=True, numerical_modules_loaded=loaded,
        numerical_or_manager_work=False)


if __name__ == '__main__':
    result = run()
    (HERE/'audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
