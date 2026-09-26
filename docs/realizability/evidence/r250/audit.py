"""R250 saved-data, source and pure contract audit; no numerical modules."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from verification.nonlinear_port.supervision import validate_worker_result
from verification.nonlinear_port.rotation_manifest import validate as validate_rotation_manifest
from verification.nonlinear_port.rotation_oracle import contract_record


def run():
    previous=json.loads((ROOT/'docs/realizability/evidence/r249/audit.json').read_text())
    old=previous['source_sha256']
    changed={'verification/nonlinear_port/supervision.py',
             'verification/nonlinear_port/systemd_backend.py'}
    assert set(old)&changed==changed
    for path,digest in old.items():
        if path not in changed:
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    r246=json.loads((ROOT/'docs/realizability/evidence/r246/run/numerical.json').read_text())
    oldmanifest=json.loads((ROOT/'verification/nonlinear_port/future_fem.json').read_text())
    validate_worker_result(r246,oldmanifest['versions'],oldmanifest['gates'],
                           policy=oldmanifest['poiseuille_diagnostic_policy'])
    proposal=json.loads((ROOT/'verification/nonlinear_port/future_rotation.json').read_text())
    validate_rotation_manifest(proposal)
    assert proposal['contract']==contract_record()
    source=dict(old)
    for path in changed|{
        'verification/nonlinear_port/rotation_manifest.py',
        'verification/nonlinear_port/rotation_driver.py',
        'verification/nonlinear_port/rotation_worker.py',
        'verification/nonlinear_port/test_rotation_integration.py',
        'verification/nonlinear_port/future_rotation.json'}:
        source[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    raw_count=0; prior=[]
    evidence=ROOT/'docs/realizability/evidence'
    for req in ('r232','r235','r238','r242','r246'):
        inventory=json.loads((evidence/req/'run_hashes.json').read_text())
        original=Path(inventory['source_directory'])
        for name,item in inventory['files'].items():
            data=(evidence/req/'run'/name).read_bytes()
            assert len(data)==item['bytes']
            assert hashlib.sha256(data).hexdigest()==item['sha256']
            assert data==(original/name).read_bytes()
            raw_count+=1
        held=json.loads((original/'held.json').read_text())
        assert (original/'reservation.json').is_file()
        assert not Path('/proc',str(held['pid'])).exists()
        assert not Path('/sys/fs/cgroup',held['cgroup'].lstrip('/')).exists()
        prior.append(dict(request=req,reservation_present=True,
                          recorded_pid_absent=True,recorded_cgroup_absent=True,
                          spent=1))
    assert raw_count==60 and len(source)==36
    tests=json.loads((evidence/'r250/tests.json').read_text())
    assert tests['count']==93 and tests['failures']==tests['errors']==0
    assert not tests['numerical_modules_loaded']
    loaded=[m for m in ('numpy','dolfinx','basix','ufl','ffcx','petsc4py','mpi4py','scipy')
            if m in sys.modules]
    assert not loaded
    return dict(status='SOURCE_INTEGRATED_NO_EXECUTION',attempts_granted=0,
                r246_saved_controller_replay='PASS',r242_status='INCOMPLETE',
                raw_originals_verified=raw_count,prior_runs=prior,
                previous_source_files_unchanged=len(old)-len(changed),
                previous_source_files_intentionally_changed=sorted(changed),
                source_sha256=source,source_files=len(source),
                strict_rotation_proposal=True,tests=tests,
                numerical_modules_loaded=loaded,no_manager_connection=True,
                no_fem_import_jit_assembly=True)

if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True,allow_nan=False))
