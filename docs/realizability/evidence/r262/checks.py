"""R262 saved-result and publication checks; no numerical imports or worker."""
import ast
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = '8de6ffd1d9c089eead43a804fe59cb65ea789774'
PAGES = ('SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md', 'EXPERIMENT.md',
         'PHYSICAL_REALIZABILITY_PLAN.md', 'CONTROL_RESEARCH_ROADMAP.md',
         'docs/realizability/B1_SETUP.md', 'verification/nonlinear_port/README.md',
         'docs/realizability/MANUFACTURED_RESULT_R262.md')


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run():
    saved = runpy.run_path(str(HERE/'audit.py'))['run']()
    assert saved['status'] == 'INCOMPLETE' and saved['attempts_spent'] == 1
    inventory = json.loads((ROOT/'docs/realizability/evidence/r261/source_inventory.json').read_text())['source_sha256']
    assert len(inventory) == 46
    assert all(digest(ROOT/name) == sha for name, sha in inventory.items())
    allocation = json.loads((ROOT/'docs/realizability/evidence/r261/allocation.json').read_text())
    for key, name in (('caller_sha256', 'run_once.py'),
                      ('source_inventory_sha256', 'source_inventory.json'),
                      ('artifact_inventory_sha256', 'artifacts.json')):
        assert digest(ROOT/'docs/realizability/evidence/r261'/name) == allocation[key]
    artifacts = json.loads((ROOT/'docs/realizability/evidence/r261/artifacts.json').read_text())
    assert all(digest(name) == sha for name, sha in artifacts['runtime_files_sha256'].items())
    assert all(str(Path(name).resolve(strict=True)) == resolved
               for name, resolved in artifacts['library_resolutions'].items())
    assert digest(artifacts['cached_archive']) == artifacts['package']['sha256']
    assert digest(Path(allocation['interpreter']).resolve(strict=True)) == allocation['executable_sha256']
    assert digest(ROOT/'verification/nonlinear_port/future_manufactured.json') == allocation['manifest_sha256']
    sources = (HERE/'audit.py', HERE/'checks.py')
    for path in sources:
        ast.parse(path.read_text(), filename=str(path))
    records = list(HERE.glob('*.json')) + list((HERE/'run').glob('*.json'))
    for path in records:
        json.loads(path.read_text())
    links = 0
    for name in PAGES:
        path = ROOT/name
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            target = target.split('#', 1)[0]
            if not target or '://' in target or target.startswith('mailto:'):
                continue
            assert (path.parent/target).exists(), (name, target)
            links += 1
    for name in ('REQUEST_LOG.md', 'WORK_SESSIONS.md'):
        old = subprocess.check_output(['git', 'show', BASE+':'+name], cwd=ROOT)
        assert (ROOT/name).read_bytes().startswith(old), name
    ids = [int(x) for x in re.findall(r'^## R(\d+)\b', (ROOT/'REQUEST_LOG.md').read_text(), re.M)]
    assert len(ids) == len(set(ids)) == 262 and set(ids) == set(range(1, 263))
    sessions = (ROOT/'WORK_SESSIONS.md').read_text()
    assert all(len(re.findall(r'^'+event+r' \| [^\n]+ \| R262 \|', sessions, re.M)) == 1
               for event in ('STARTED', 'COMPLETED'))
    handoff = (ROOT/'SESSION_HANDOFF.md').read_text()
    assert handoff.count('## Next task\n') == 1
    next_task = handoff.split('## Next task\n', 1)[1].split('### Historical', 1)[0]
    assert 'Astra / high' in next_task and 'source-only repair contract' in next_task
    assert 'R262' in handoff.split('### Previous', 1)[0]
    changed = subprocess.check_output(['git', 'diff', '--name-only', BASE], cwd=ROOT, text=True).splitlines()
    assert not any(name.startswith('verification/nonlinear_port/') and name != 'verification/nonlinear_port/README.md'
                   for name in changed)
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    forbidden = {'numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py', 'scipy'}
    loaded = sorted(name for name in sys.modules if name.split('.')[0] in forbidden)
    assert not loaded
    return dict(status='INCOMPLETE', raw_audit='PASS', source_bindings=46,
                caller_inventory_artifact_bindings=3, runtime_artifacts=11,
                library_resolutions=4, ast_files=len(sources), json_files=len(records),
                local_link_targets_checked=links, unique_contiguous_request_ids=262,
                append_only_logs=True, r262_started_once=True, r262_completed_once=True,
                numerical_source_unchanged=True, numerical_modules_loaded=loaded,
                whitespace='PASS')


if __name__ == '__main__':
    result = run()
    (HERE/'checks.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
