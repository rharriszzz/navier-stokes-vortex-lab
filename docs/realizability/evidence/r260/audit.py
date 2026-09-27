"""R260 source/evidence audit; read-only except its own audit.json output."""
import hashlib
import json
from pathlib import Path
import runpy
import sys

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def run():
    original=read(ROOT/'docs/realizability/evidence/r257/source_inventory.json')['source_sha256']
    expected_changes={
        'verification/nonlinear_port/manufactured_driver.py',
        'verification/nonlinear_port/manufactured_worker.py',
        'verification/nonlinear_port/test_manufactured_integration.py',
    }
    differences={name for name,sha in original.items() if digest(ROOT/name)!=sha}
    assert len(original)==44 and differences==expected_changes
    added={
        'verification/nonlinear_port/manufactured_failure.py',
        'verification/nonlinear_port/test_manufactured_failure.py',
    }
    sources={name:digest(ROOT/name) for name in sorted(set(original)|added)}
    allocation=read(ROOT/'docs/realizability/evidence/r257/allocation.json')
    assert digest(ROOT/'verification/nonlinear_port/future_manufactured.json')==allocation['manifest_sha256']
    artifacts=read(ROOT/'docs/realizability/evidence/r257/artifacts.json')
    for name,sha in artifacts['runtime_files_sha256'].items():
        assert digest(name)==sha,name
    for name,resolved in artifacts['library_resolutions'].items():
        assert str(Path(name).resolve(strict=True))==resolved,name
    assert digest(artifacts['cached_archive'])==artifacts['package']['sha256']
    assert digest(Path(allocation['interpreter']).resolve(strict=True))==allocation['executable_sha256']
    raw=0
    for request in ('r232','r235','r238','r242','r246','r253','r258'):
        evidence=ROOT/'docs/realizability/evidence'/request
        inventory=read(evidence/'run_hashes.json')
        source=Path(inventory['source_directory'])
        for name,item in inventory['files'].items():
            blob=(evidence/'run'/name).read_bytes()
            assert len(blob)==item['bytes'] and hashlib.sha256(blob).hexdigest()==item['sha256']
            assert blob==(source/name).read_bytes()
            raw+=1
        held=read(source/'held.json')
        assert (source/'reservation.json').is_file()
        assert not Path('/proc',str(held['pid'])).exists()
        assert not (Path('/sys/fs/cgroup')/held['cgroup'].lstrip('/')).exists()
    assert raw==84
    r258=runpy.run_path(str(ROOT/'docs/realizability/evidence/r258/audit.py'))['run']()
    tests=read(HERE/'tests.json')
    assert tests['tests']==113 and tests['errors']==tests['failures']==0
    assert not tests['numerical_modules_loaded']
    assert tests['saved_r246_validator']==tests['saved_r253_validator']=='PASS'
    assert r258['status']=='INCOMPLETE' and r258['attempts_spent']==1
    forbidden={'numpy','dolfinx','basix','ufl','ffcx','petsc4py','mpi4py','scipy'}
    loaded=sorted(n for n in sys.modules if n.split('.')[0] in forbidden)
    assert not loaded
    return dict(status='SOURCE_INTEGRATED_NO_ADMISSION',source_files=len(sources),
        source_sha256=sources,changed_prior_source_files=sorted(differences),
        unchanged_prior_source_files=len(original)-len(differences),
        added_source_test_files=sorted(added),
        manifest_unchanged=True,runtime_artifacts_verified=len(artifacts['runtime_files_sha256']),
        library_resolutions_verified=len(artifacts['library_resolutions']),
        archive_and_interpreter_verified=True,raw_originals_verified=raw,
        spent_reservations=7,recorded_pids_cgroups_absent=True,
        saved_r258_status='INCOMPLETE',saved_r246_validator='PASS',saved_r253_validator='PASS',
        r242_status='INCOMPLETE',tests=113,numerical_modules_loaded=loaded,
        new_manager_worker_or_reservation=False,new_attempts_admitted=0)


if __name__=='__main__':
    result=run()
    (HERE/'audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},sort_keys=True))
