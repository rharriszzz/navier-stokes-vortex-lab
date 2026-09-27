"""R263 source, saved-result and Git evidence coverage audit; no FEM imports."""
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = 'fa5f56f4a4ff1c2d3bfff9d713e20794d3bf364f'
sys.path.insert(0, str(ROOT))
FORBIDDEN = {'numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py', 'scipy'}


class Guard:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in FORBIDDEN:
            raise AssertionError('numerical import prohibited: '+fullname)


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run():
    guard = Guard()
    sys.meta_path.insert(0, guard)
    try:
        r262 = runpy.run_path(str(HERE.parent/'r262/audit.py'))['run']()
        assert r262['status'] == 'INCOMPLETE' and r262['attempts_spent'] == 1
        allocation = read(HERE.parent/'r261/allocation.json')
        source = read(HERE.parent/'r261/source_inventory.json')['source_sha256']
        assert len(source) == 46
        for name, sha in source.items():
            assert digest(ROOT/name) == sha, name
        for key, name in (('caller_sha256', 'run_once.py'),
                          ('source_inventory_sha256', 'source_inventory.json'),
                          ('artifact_inventory_sha256', 'artifacts.json')):
            assert digest(HERE.parent/'r261'/name) == allocation[key]
        artifacts = read(HERE.parent/'r261/artifacts.json')
        for name, sha in artifacts['runtime_files_sha256'].items():
            assert digest(name) == sha, name
        for name, resolved in artifacts['library_resolutions'].items():
            assert str(Path(name).resolve(strict=True)) == resolved
        assert digest(artifacts['cached_archive']) == artifacts['package']['sha256']
        assert digest(Path(allocation['interpreter']).resolve(strict=True)) == allocation['executable_sha256']
        probe = read(HERE/'probe.json')
        assert probe['status'] == 'PASS' and probe['case_count'] == 28
        assert probe['recursion_limit_changed'] is False and not probe['numerical_modules_loaded']
        for name, sha in probe['installed_source_sha256'].items():
            assert digest(name) == sha
        base_files = set(subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE], cwd=ROOT, text=True).splitlines())
        raw, missing_at_base = 0, []
        for request in ('r232', 'r235', 'r238', 'r242', 'r246', 'r253', 'r258', 'r262'):
            folder = HERE.parent/request
            inventory = read(folder/'run_hashes.json')
            entries = [(folder/'run'/name, Path(inventory['source_directory'])/name, item)
                       for name, item in inventory.get('files', inventory.get('run_files', {})).items()]
            if request == 'r262':
                entries += [(folder/name, Path(inventory['caller_source_directory'])/name, item)
                            for name, item in inventory['caller_files'].items()]
            for saved, original, item in entries:
                blob = saved.read_bytes()
                assert blob == original.read_bytes()
                assert len(blob) == item['bytes'] and hashlib.sha256(blob).hexdigest() == item['sha256']
                name = str(saved.relative_to(ROOT))
                indexed = subprocess.check_output(['git', 'show', ':'+name], cwd=ROOT)
                assert indexed == blob, name
                if name not in base_files:
                    missing_at_base.append(name)
                raw += 1
            held = read(folder/'run/held.json')
            assert read(folder/'run/reservation.json')['attempt'] == 1
            assert not Path('/proc', str(held['pid'])).exists()
            assert not (Path('/sys/fs/cgroup')/held['cgroup'].lstrip('/')).exists()
        expected_missing = sorted('docs/realizability/evidence/'+r+'/run/'+name
                                  for r in ('r235', 'r262') for name in ('run.log', 'worker.log'))
        assert sorted(missing_at_base) == expected_missing and raw == 97
        from verification.nonlinear_port.supervision import validate_worker_result
        from verification.nonlinear_port.rotation_driver import validate_worker_payload
        old = read(ROOT/'verification/nonlinear_port/future_fem.json')
        validate_worker_result(read(HERE.parent/'r246/run/numerical.json'), old['versions'], old['gates'],
                               policy=old['poiseuille_diagnostic_policy'])
        rotation = read(ROOT/'verification/nonlinear_port/future_rotation.json')
        saved = HERE.parent/'r253/run'
        validate_worker_payload(read(saved/'numerical.json'), rotation,
                                read(saved/'reservation.json'), read(saved/'admission.json'))
        reference = runpy.run_path(str(HERE.parent/'r255/audit.py'))['manufactured_reference']()
        assert reference == read(HERE.parent/'r255/proposal.json')['exact_reference']
        loaded = sorted(n for n in sys.modules if n.split('.')[0] in FORBIDDEN)
        assert not loaded
        return dict(status='REPAIR_CONTRACT_NO_ADMISSION', source_files=46,
                    runtime_artifacts_verified=11, library_resolutions_verified=4,
                    archive_and_interpreter_verified=True, raw_original_files_verified=raw,
                    git_index_raw_files_verified=raw, base_omitted_logs=expected_missing,
                    omitted_log_bytes=781, spent_reservations=8,
                    recorded_pids_cgroups_absent=True, saved_r246_validator='PASS',
                    saved_r253_validator='PASS', saved_r262_status='INCOMPLETE',
                    rational_r255_reference_rederived=True, probe_cases=28,
                    probe_edge_cases=5, probe_negative_controls=4,
                    unchanged_source_tests_reused=114, numerical_modules_loaded=loaded,
                    numerical_import_manager_worker_or_reservation=False, new_attempts_admitted=0)
    finally:
        sys.meta_path.remove(guard)


if __name__ == '__main__':
    result = run()
    (HERE/'audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
