"""R256 source inventory and unchanged historical-contract audit; no FEM import."""
import hashlib
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from verification.nonlinear_port.linear_evidence import MAX_DOFS
from verification.nonlinear_port.manufactured_manifest import validate

MODIFIED = {
    'verification/nonlinear_port/linear_evidence.py',
    'verification/nonlinear_port/supervision.py',
    'verification/nonlinear_port/systemd_backend.py',
}
ADDED = {
    'verification/nonlinear_port/future_manufactured.json',
    'verification/nonlinear_port/manufactured_driver.py',
    'verification/nonlinear_port/manufactured_manifest.py',
    'verification/nonlinear_port/manufactured_policy.py',
    'verification/nonlinear_port/manufactured_report.py',
    'verification/nonlinear_port/manufactured_worker.py',
    'verification/nonlinear_port/test_manufactured_integration.py',
}


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run():
    old = json.loads((ROOT/'docs/realizability/evidence/r251/source_inventory.json').read_text())['source_sha256']
    changed = {name for name, sha in old.items() if digest(ROOT/name) != sha}
    assert len(old) == 36 and changed == MODIFIED
    proposal_path = ROOT/'docs/realizability/evidence/r255/proposal.json'
    manifest_path = ROOT/'verification/nonlinear_port/future_manufactured.json'
    assert manifest_path.read_bytes() == proposal_path.read_bytes()
    proposal = json.loads(manifest_path.read_text())
    validate(proposal)
    reference = runpy.run_path(str(ROOT/'docs/realizability/evidence/r255/audit.py'))['manufactured_reference']()
    assert reference == proposal['exact_reference']
    assert proposal['latest_system_dofs_max'] == MAX_DOFS == 512
    assert proposal['execution_admitted'] is False and proposal['attempts_granted'] == 0
    tests = json.loads((HERE/'tests.json').read_text())
    assert tests['failures'] == tests['errors'] == 0
    assert tests['saved_r246_validator'] == tests['saved_r253_validator'] == 'PASS'
    assert not tests['numerical_modules_loaded']
    forbidden = {'numpy','dolfinx','basix','ufl','ffcx','petsc4py','mpi4py','scipy'}
    loaded = sorted(name for name in forbidden if name in sys.modules)
    assert not loaded
    inventory = {name: digest(ROOT/name) for name in sorted(MODIFIED | ADDED)}
    return dict(status='SOURCE_IMPLEMENTED_NO_ADMISSION',
        previous_bound_source_files=len(old), previous_files_unchanged=len(old)-len(changed),
        intentionally_modified_prior_files=sorted(changed),
        added_fixture_files=sorted(ADDED), source_sha256=inventory,
        proposal_sha256=digest(proposal_path), copied_manifest_sha256=digest(manifest_path),
        exact_reference_rederived=True, tests=tests['tests'],
        saved_r246_validator='PASS', saved_r253_validator='PASS',
        attempts_granted=0, new_numerical_work=False,
        numerical_modules_loaded=loaded, manager_connection=False)


if __name__ == '__main__':
    result = run()
    (HERE/'audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({key:result[key] for key in ('status','tests',
        'previous_files_unchanged','attempts_granted','numerical_modules_loaded')},
        sort_keys=True))
