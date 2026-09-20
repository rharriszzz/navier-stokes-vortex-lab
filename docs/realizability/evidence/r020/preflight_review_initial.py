"""R020 read-only archive review and disposable source preparation; no FEM imports."""
import ast
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import runpy
import shutil
import subprocess
from unittest.mock import patch

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
OLD = ROOT / 'docs/realizability/evidence'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    historical = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', base,
        'docs/realizability/evidence/r014', 'docs/realizability/evidence/r015',
        'docs/realizability/evidence/r016', 'docs/realizability/evidence/r017',
        'docs/realizability/evidence/r018', 'docs/realizability/evidence/r019'], text=True).splitlines()
    hashes = {}
    for name in historical:
        content = (ROOT / name).read_bytes()
        assert content == subprocess.check_output(['git', 'show', base + ':' + name]), name
        hashes[name] = sha(ROOT / name)
    # Historical auditors write their validation records. Capture those writes in
    # this new work directory; never change the prior evidence or its manifests.
    write_text = Path.write_text
    redirected = []
    def capture_write(path, data, *args, **kwargs):
        if path.is_relative_to(OLD):
            dest = HERE / ('reaudit-' + path.parent.name + '-' + path.name)
            redirected.append(str(path.relative_to(ROOT)))
            return write_text(dest, data, *args, **kwargs)
        raise AssertionError('Unexpected historical audit write: ' + str(path))
    for request in ('r016', 'r017', 'r018', 'r019'):
        buffer = io.StringIO()
        with patch.object(Path, 'write_text', capture_write), redirect_stdout(buffer):
            audit = runpy.run_path(str(OLD / request / 'audit.py'))
            if 'main' in audit:
                audit['main']()
        (HERE / ('reaudit-' + request + '.stdout')).write_text(buffer.getvalue())
    for name, digest in hashes.items():
        assert sha(ROOT / name) == digest
    sources = json.loads((OLD / 'r016/preflight.json').read_text())['source_sha256']
    assert len(sources) == 19
    for name, digest in sources.items():
        assert sha(ROOT / name) == digest
    runners = {}
    for name in ('physical.py', 'toy_runner.py', 'kernels.py', 'disk.py',
                 'wrapper_toys.py', 'block_rhs_toys.py', 'run_contract.py'):
        shutil.copyfile(OLD / 'r019' / name, HERE / name)
        ast.parse((HERE / name).read_text())
        runners[name] = sha(HERE / name)
    runners['run_contract.py'] = sha(HERE / 'run_contract.py')
    review = dict(
        constraint_grouping='Same trial/test spaces in the serial square system; nonempty velocity, empty pressure groups, exact exterior sets and disjoint offsets checked before P and A.',
        rhs_layout='R017 factory validates PETSc type/sizes/ownership, owned and ghost offsets, and array size against captured P RHS before loading/lifting; complete operation covered by independent toy oracle.',
        pressure_compatibility='A pressure rows are included in lifting. Both products and removed norm persist before refusal above 256*eps*norm(b). Physical compatibility is unmeasured until this attempt; flux-ratio pass does not imply it.',
        essential_correction='Primary constrained coefficients set to RHS values; constrained residual required exactly zero; one same-factor correction, no loop.',
        inventory='One mesh, common matrix/factors; success requires three primary RHSs, three corrections and six matrix solves. Digest includes CSR/values, offsets and essential sets; matrix/factor states checked.',
        own_targets='A diagnostics use its complex projected normal data and full tangential trace; original PDE ceilings retained.',
        outputs='Exact-circle cell polynomial integral, reconstruction and independent arcs; original two six-feature rules and fixed P reproduction tolerance; strict reference and component screens unchanged.',
        stops='First exception, incompatibility or resource stop ends physical attempt; no second child, changed trace, tolerance, solver or cap. Failed accuracy is a reportable outcome.',
        prior_P='R016 stored-data audit re-executed without rewriting old evidence: cell gain, polar reproduction, correction, operator and PDE checks preserved.',
        portability='R019 root validation precedes FEM imports; finite wrong-root report and parent refusal archived. Exact R019 sources copied; fresh five-phase sequence required.',
        scientific_choices='No new method, tolerance, boundary condition or interpretation selected. R013 contract retained.')
    report = dict(status='passed', base_commit=base, source_sha256=sources,
        runner_sha256=runners, historical_file_sha256=hashes,
        historical_audit_writes_redirected=redirected, static_review=review,
        physical_execution_prerequisite='All five fresh toy/watchdog phases must pass before the single physical child.',
        physical_attempt_limit=1, toy_limits=dict(wall_seconds=60, rss_mib=512),
        physical_limits=dict(wall_seconds=180, rss_mib=1536, poll_seconds=.05))
    (HERE / 'preflight.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(status=report['status'], historical_files=len(hashes),
        source_identities=len(sources), copied_children=len(runners)-1), indent=2))


if __name__ == '__main__':
    main()
