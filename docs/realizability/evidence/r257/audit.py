"""R257 admission review: read bytes and saved data; never connect or import FEM."""
import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def run():
    from verification.nonlinear_port.manufactured_manifest import contract_digest, validate
    from verification.nonlinear_port.linear_evidence import MAX_DOFS, MAX_BYTES, MAX_NNZ
    from verification.nonlinear_port.supervision import validate_worker_result
    from verification.nonlinear_port.rotation_driver import validate_worker_payload

    allocation = read(HERE/'allocation.json')
    sources = read(HERE/'source_inventory.json')['source_sha256']
    assert len(sources) == 44
    for name, sha in sources.items():
        assert digest(ROOT/name) == sha, name
    prior = read(ROOT/'docs/realizability/evidence/r256/audit.json')['source_sha256']
    changes = sorted(name for name, sha in prior.items() if digest(ROOT/name) != sha)
    assert changes == ['verification/nonlinear_port/manufactured_driver.py',
                       'verification/nonlinear_port/manufactured_report.py',
                       'verification/nonlinear_port/test_manufactured_integration.py']
    manifest_path = ROOT/'verification/nonlinear_port/future_manufactured.json'
    manifest = read(manifest_path)
    validate(manifest)
    assert manifest_path.read_bytes() == (ROOT/'docs/realizability/evidence/r255/proposal.json').read_bytes()
    reference = runpy.run_path(str(ROOT/'docs/realizability/evidence/r255/audit.py'))['manufactured_reference']()
    assert manifest['exact_reference'] == reference
    assert allocation['contract'] == manifest
    assert allocation['contract_sha256'] == contract_digest(manifest)
    assert (MAX_DOFS, MAX_BYTES, MAX_NNZ) == (512, 4194304, 65536)
    for key, path in [('caller_sha256', HERE/'run_once.py'),
                      ('source_inventory_sha256', HERE/'source_inventory.json'),
                      ('artifact_inventory_sha256', HERE/'artifacts.json'),
                      ('manifest_sha256', manifest_path)]:
        assert allocation[key] == digest(path), key
    artifacts = read(HERE/'artifacts.json')
    assert (HERE/'artifacts.json').read_bytes() == (ROOT/'docs/realizability/evidence/r251/artifacts.json').read_bytes()
    for name, sha in artifacts['runtime_files_sha256'].items():
        assert digest(name) == sha, name
    for name, resolved in artifacts['library_resolutions'].items():
        assert str(Path(name).resolve(strict=True)) == resolved
    assert digest(artifacts['cached_archive']) == artifacts['package']['sha256']
    executable = Path(allocation['interpreter']).resolve(strict=True)
    assert digest(executable) == allocation['executable_sha256']
    raw_count = 0
    prior_runs = []
    for req in ('r232', 'r235', 'r238', 'r242', 'r246', 'r253'):
        evidence = ROOT/'docs/realizability/evidence'/req
        inventory = read(evidence/'run_hashes.json')
        original = Path(inventory['source_directory'])
        for name, item in inventory['files'].items():
            blob = (evidence/'run'/name).read_bytes()
            assert len(blob) == item['bytes'] and hashlib.sha256(blob).hexdigest() == item['sha256']
            assert blob == (original/name).read_bytes()
            raw_count += 1
        held = read(original/'held.json')
        assert (original/'reservation.json').is_file()
        assert not Path('/proc', str(held['pid'])).exists()
        assert not Path('/sys/fs/cgroup', held['cgroup'].lstrip('/')).exists()
        prior_runs.append(dict(request=req, spent=1, reservation_present=True,
                               recorded_pid_absent=True, recorded_cgroup_absent=True))
    assert raw_count == 74
    old = read(ROOT/'verification/nonlinear_port/future_fem.json')
    validate_worker_result(read(ROOT/'docs/realizability/evidence/r246/run/numerical.json'),
                           old['versions'], old['gates'], policy=old['poiseuille_diagnostic_policy'])
    rotation = read(ROOT/'verification/nonlinear_port/future_rotation.json')
    directory = ROOT/'docs/realizability/evidence/r253/run'
    validate_worker_payload(read(directory/'numerical.json'), rotation,
                            read(directory/'reservation.json'), read(directory/'admission.json'))
    installed = Path('/tmp/navier-fenicsx-r229/lib/python3.12/site-packages/dolfinx/fem/forms.py')
    tree = ast.parse(installed.read_text())
    zero = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == '_zero_form')
    checks = [ast.unparse(n.test) for n in ast.walk(zero) if isinstance(n, ast.Assert)]
    assert 'len(V) > 0' in checks
    target = Path(allocation['run_directory'])
    assert not target.exists() and not target.is_symlink()
    available = next(int(line.split()[1]) for line in Path('/proc/meminfo').read_text().splitlines()
                     if line.startswith('MemAvailable:'))
    controllers = Path('/sys/fs/cgroup/cgroup.controllers').read_text().split()
    assert available >= 1536*1024 and {'memory', 'pids'} <= set(controllers)
    tests, caller = read(HERE/'tests.json'), read(HERE/'caller_tests.json')
    assert tests['tests'] == 104 and caller['count'] == 6
    assert tests['errors'] == tests['failures'] == caller['errors'] == caller['failures'] == 0
    assert not tests['numerical_modules_loaded'] and not caller['numerical_modules_loaded']
    forbidden = {'numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py', 'scipy'}
    loaded = sorted(name for name in sys.modules if name.split('.')[0] in forbidden)
    assert not loaded
    return dict(status='ADMITTED_FOR_LATER_EXECUTION', attempts_granted=1, attempts_spent=0,
        run_directory=str(target), run_directory_absent=True, source_files=44,
        source_sha256=sources, r256_files_repaired=changes, exact_reference_rederived=True,
        raw_originals_verified=raw_count, prior_runs=prior_runs,
        saved_r246_validator='PASS', saved_r253_validator='PASS', r242_status='INCOMPLETE',
        tests=104, caller_tests=6, runtime_artifacts_verified=len(artifacts['runtime_files_sha256']),
        library_resolutions_verified=len(artifacts['library_resolutions']),
        archive_and_interpreter_verified=True, interpreter=str(executable),
        installed_zero_form_assertion=checks, host_available_kib=available, controllers=controllers,
        manager_version_source='R251 reviewed 249.11-0ubuntu3.22; live refresh required by caller',
        manager_connection=False, numerical_modules_loaded=loaded, new_numerical_work=False,
        actual_api_jit_solver_budget_resource_behavior='unmeasured; one bounded measurement admitted')


if __name__ == '__main__':
    result = run()
    (HERE/'audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256', 'prior_runs')}, sort_keys=True))
