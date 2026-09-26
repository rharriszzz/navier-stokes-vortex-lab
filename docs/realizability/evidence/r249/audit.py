"""R249 source and saved-data audit; standard library only, no launches."""
import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from verification.nonlinear_port.rotation_oracle import contract_record, validate_contract


def run():
    previous = runpy.run_path(str(ROOT/'docs/realizability/evidence/r247/audit.py'))['run']()
    recorded = json.loads((ROOT/'docs/realizability/evidence/r247/audit.json').read_text())
    assert previous == recorded
    sources = json.loads((ROOT/'docs/realizability/evidence/r248/checks.json').read_text())['source_sha256']
    for name, digest in sources.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    proposal = json.loads((ROOT/'docs/realizability/evidence/r247/rotation_proposal.json').read_text())
    contract = contract_record()
    validate_contract({key: proposal[key] for key in contract})
    assert contract['raw_targets_rational'] == previous['rotation_exact_targets']
    installed = Path('/tmp/navier-fenicsx-r229/lib/python3.12/site-packages/dolfinx/fem/forms.py')
    tree = ast.parse(installed.read_text())
    zero = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == '_zero_form')
    assertion = next(n for n in ast.walk(zero) if isinstance(n, ast.Assert))
    assert ast.unparse(assertion.test) == 'len(V) > 0'
    forbidden = [n for n in sys.modules if n.split('.')[0] in
                 {'numpy','dolfinx','basix','ufl','ffcx','petsc4py','mpi4py','scipy'}]
    assert not forbidden
    return dict(status='INTEGRATION_REVIEW_ONLY', attempts_granted=0,
                source_sha256=sources, source_files_unchanged=len(sources),
                r247_audit_reproduced=True, raw_originals_verified=previous['raw_files_verified'],
                prior_runs=previous['prior_runs'], r246_controller_replay=previous['r246_controller_replay'],
                r242_status='INCOMPLETE', exact_contract_and_38_targets_verified=True,
                contract_sha256=hashlib.sha256(json.dumps(contract, sort_keys=True,
                    separators=(',', ':'), allow_nan=False).encode()).hexdigest(),
                installed_source_review=dict(path=str(installed), sha256=hashlib.sha256(installed.read_bytes()).hexdigest(),
                    zero_form_assertion=ast.unparse(assertion.test), numerical_import=False,
                    runtime_behavior_verified=False),
                prior_85_tests='R248 results reused with all 31 source/test/pin hashes unchanged; not rerun',
                numerical_modules_loaded=forbidden, manager_connection=False, runtime_implementation=False)

if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True, allow_nan=False))
