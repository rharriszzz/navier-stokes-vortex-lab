"""R251 source/artifact/saved-result review; standard library, no manager/FEM."""
import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
HERE=Path(__file__).resolve().parent

def digest(path):
    with path.open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()

def run():
    prior=runpy.run_path(str(ROOT/'docs/realizability/evidence/r250/audit.py'))['run']()
    old=json.loads((ROOT/'docs/realizability/evidence/r250/audit.json').read_text())
    assert prior==old
    allocation=json.loads((HERE/'allocation.json').read_text())
    inventory=json.loads((HERE/'source_inventory.json').read_text())['source_sha256']
    assert inventory==prior['source_sha256'] and len(inventory)==36
    for name,sha in inventory.items(): assert digest(ROOT/name)==sha,name
    for key,path in [('caller_sha256',HERE/'run_once.py'),
                     ('source_inventory_sha256',HERE/'source_inventory.json'),
                     ('artifact_inventory_sha256',HERE/'artifacts.json'),
                     ('manifest_sha256',ROOT/'verification/nonlinear_port/future_rotation.json')]:
        assert digest(path)==allocation[key],key
    artifacts=json.loads((HERE/'artifacts.json').read_text())
    for name,sha in artifacts['runtime_files_sha256'].items(): assert digest(Path(name))==sha,name
    for name,resolved in artifacts['library_resolutions'].items(): assert str(Path(name).resolve(strict=True))==resolved
    assert digest(Path(artifacts['cached_archive']))==artifacts['package']['sha256']
    executable=Path(allocation['interpreter']).resolve(strict=True)
    assert digest(executable)==allocation['executable_sha256']
    from verification.nonlinear_port.rotation_manifest import contract_digest,validate
    manifest=json.loads((ROOT/'verification/nonlinear_port/future_rotation.json').read_text())
    validate(manifest)
    assert allocation['contract']==manifest['contract']
    assert contract_digest(manifest['contract'])==allocation['contract_sha256']
    assert allocation['contract']['raw_targets_rational']==json.loads(
        (ROOT/'docs/realizability/evidence/r247/audit.json').read_text())['rotation_exact_targets']
    run_dir=Path(allocation['run_directory'])
    assert not run_dir.exists() and not run_dir.is_symlink()
    installed=Path('/tmp/navier-fenicsx-r229/lib/python3.12/site-packages/dolfinx/fem/forms.py')
    tree=ast.parse(installed.read_text())
    zero=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='_zero_form')
    checks=[ast.unparse(n.test) for n in ast.walk(zero) if isinstance(n,ast.Assert)]
    assert 'len(V) > 0' in checks
    assert digest(installed)==json.loads((ROOT/'docs/realizability/evidence/r249/audit.json').read_text())['installed_source_review']['sha256']
    tests=json.loads((HERE/'tests.json').read_text())
    assert tests['count']==6 and tests['failures']==tests['errors']==0
    assert not tests['numerical_modules_loaded']
    loaded=[n for n in sys.modules if n.split('.')[0] in
            {'numpy','dolfinx','basix','ufl','ffcx','petsc4py','mpi4py','scipy'}]
    assert not loaded
    return dict(status='ADMITTED_FOR_LATER_EXECUTION',attempts_granted=1,
        attempts_spent=0,run_directory=str(run_dir),run_directory_absent=True,
        source_files_unchanged=36,source_sha256=inventory,
        r250_audit_reproduced=True,r246_saved_controller_replay='PASS',r242_status='INCOMPLETE',
        raw_originals_verified=60,prior_runs=prior['prior_runs'],
        prior_93_tests='R250 results reused with all 36 source hashes unchanged; not rerun',
        caller_tests=tests,runtime_artifacts_verified=len(artifacts['runtime_files_sha256']),
        library_resolutions_verified=len(artifacts['library_resolutions']),
        cached_archive_verified=True,interpreter=str(executable),
        installed_zero_form_assertion=checks,installed_forms_unchanged_since_r249=True,
        manifest_sha256=allocation['manifest_sha256'],contract_sha256=allocation['contract_sha256'],
        numerical_modules_loaded=loaded,manager_connection=False,
        real_ufl_jit_assembly=False,real_api_behavior='unmeasured; explicit bounded risk')

if __name__=='__main__':
    result=run()
    (HERE/'audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','prior_runs')},sort_keys=True))
