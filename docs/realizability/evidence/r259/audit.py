"""Read-only R259 source/artifact/raw audit; no numerical import or manager."""
import hashlib
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run():
    from verification.nonlinear_port.supervision import validate_worker_result
    from verification.nonlinear_port.rotation_driver import validate_worker_payload
    sources = read(ROOT/'docs/realizability/evidence/r257/source_inventory.json')['source_sha256']
    assert len(sources) == 44
    for name, sha in sources.items():
        assert digest(ROOT/name) == sha, name
    artifacts = read(ROOT/'docs/realizability/evidence/r257/artifacts.json')
    for name, sha in artifacts['runtime_files_sha256'].items():
        assert digest(name) == sha, name
    for name, target in artifacts['library_resolutions'].items():
        assert str(Path(name).resolve(strict=True)) == target
    assert digest(artifacts['cached_archive']) == artifacts['package']['sha256']
    allocation = read(ROOT/'docs/realizability/evidence/r257/allocation.json')
    assert digest(Path(allocation['interpreter']).resolve(strict=True)) == allocation['executable_sha256']
    raw_count = 0
    for request in ('r232','r235','r238','r242','r246','r253','r258'):
        evidence = ROOT/'docs/realizability/evidence'/request
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
        assert not (Path('/sys/fs/cgroup')/held['cgroup'].lstrip('/')).exists()
    assert raw_count == 84
    r258 = runpy.run_path(str(ROOT/'docs/realizability/evidence/r258/audit.py'))['run']()
    old = read(ROOT/'verification/nonlinear_port/future_fem.json')
    validate_worker_result(read(ROOT/'docs/realizability/evidence/r246/run/numerical.json'),
        old['versions'], old['gates'], policy=old['poiseuille_diagnostic_policy'])
    rotation = read(ROOT/'verification/nonlinear_port/future_rotation.json')
    directory = ROOT/'docs/realizability/evidence/r253/run'
    validate_worker_payload(read(directory/'numerical.json'), rotation,
        read(directory/'reservation.json'), read(directory/'admission.json'))
    probe = read(HERE/'probe.json')
    assert probe['checks'] == 4 and probe['status'] == 'PASS'
    from verification.nonlinear_port import fixtures
    u, p = fixtures.manufactured()
    force = fixtures.forcing(u, p)
    # Complexity is source context only, never identification of the crash.
    terms = dict(velocity=[len(v.terms) for v in u], pressure=len(p.terms),
                 force=[len(v.terms) for v in force])
    forbidden = {'numpy','dolfinx','basix','ufl','ffcx','petsc4py','mpi4py','scipy'}
    loaded = sorted(n for n in sys.modules if n.split('.')[0] in forbidden)
    assert not loaded
    return dict(status='SOURCE_ONLY_DIAGNOSTIC_REPAIR_REQUIRED',
        source_files_unchanged=len(sources), source_sha256=sources,
        raw_originals_verified=raw_count, spent_reservations=7,
        all_recorded_pids_and_cgroups_absent=True, saved_r258=r258,
        saved_r246_validator='PASS', saved_r253_validator='PASS', r242_status='INCOMPLETE',
        runtime_artifacts_verified=len(artifacts['runtime_files_sha256']),
        library_resolutions_verified=len(artifacts['library_resolutions']),
        archive_and_interpreter_verified=True, ambiguity_probe_checks=4,
        polynomial_terms=terms, actual_failure_site='undetermined',
        numerical_modules_loaded=loaded, new_attempts_admitted=0,
        new_worker_or_manager=False)


if __name__ == '__main__':
    result = run()
    (HERE/'audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'source_sha256'}, sort_keys=True))
