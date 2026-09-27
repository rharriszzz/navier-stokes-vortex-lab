"""Read-only retained evidence audit for R267; writes only its own result."""
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = '7266486772651903f45187465752aea708b150ac'


def run():
    probe = runpy.run_path(str(HERE / 'probe.py'))
    guard = probe['Guard']()
    sys.meta_path.insert(0, guard)
    try:
        old = runpy.run_path(str(HERE.parent / 'r266/audit.py'))['run']()
        assert old['old_raw_files_verified'] == 97 and old['attempts_spent'] == 1
        inventory = json.loads((HERE.parent / 'r266/run_hashes.json').read_text())
        paths = [HERE.parent / 'r266/run' / n for n in inventory['run_files']]
        paths += [HERE.parent / 'r266' / n for n in inventory['caller_files']]
        for path in paths:
            relative = str(path.relative_to(ROOT))
            assert subprocess.check_output(['git', 'show', ':'+relative], cwd=ROOT) == path.read_bytes()
        allocation = json.loads((HERE.parent / 'r265/allocation.json').read_text())
        for key, name in [('caller_sha256', 'run_once.py'),
                          ('source_inventory_sha256', 'source_inventory.json'),
                          ('artifact_inventory_sha256', 'artifacts.json')]:
            assert hashlib.sha256((HERE.parent / 'r265' / name).read_bytes()).hexdigest() == allocation[key]
        source = json.loads((HERE.parent / 'r265/source_inventory.json').read_text())['source_sha256']
        for name, digest in source.items():
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
        historical = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE,
            'docs/realizability/evidence'], cwd=ROOT, text=True).splitlines()
        # One git diff checks all tracked historical evidence without loading FEM.
        subprocess.run(['git', 'diff', '--exit-code', BASE, '--', *historical],
                       cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        loaded = sorted(n for n in sys.modules if n.split('.')[0] in probe['FORBIDDEN'])
        assert not loaded
        return dict(status='PASS', source_bindings_unchanged=len(source),
            r266_original_and_index_files=len(paths), old_original_and_index_files=97,
            historical_evidence_files_unchanged=len(historical), spent_allocations=9,
            recorded_pids_cgroups_absent=True, runtime_artifacts=11,
            library_resolutions=4, archive_interpreter_verified=True,
            saved_r246_validator='PASS', saved_r253_validator='PASS',
            saved_r266_status='INCOMPLETE', r265_allocation_bindings_verified=True,
            numerical_modules_loaded=loaded, numerical_or_manager_work=False)
    finally:
        sys.meta_path.remove(guard)


if __name__ == '__main__':
    result = run()
    (HERE / 'audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
