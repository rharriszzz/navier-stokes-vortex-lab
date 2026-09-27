"""Static R267 publication checks; no numerical work."""
import ast
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = '7266486772651903f45187465752aea708b150ac'
PAGES = ('SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md', 'EXPERIMENT.md',
         'PHYSICAL_REALIZABILITY_PLAN.md', 'CONTROL_RESEARCH_ROADMAP.md',
         'docs/realizability/B1_SETUP.md', 'verification/nonlinear_port/README.md',
         'docs/realizability/MANUFACTURED_ANGULAR_REVIEW_R267.md')


def run():
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    for path in HERE.glob('*.json'):
        json.loads(path.read_text())
    audit = json.loads((HERE / 'audit.json').read_text())
    probe = json.loads((HERE / 'probe.json').read_text())
    assert audit['status'] == 'PASS' and audit['spent_allocations'] == 9
    assert audit['source_bindings_unchanged'] == 47
    assert probe['saved_validator_refuses'] and probe['decomposition_negative_controls'] == 4
    assert not probe['numerical_modules_loaded'] and probe['runtime_source_changes'] == 0
    links = 0
    for name in PAGES:
        path = ROOT / name
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            target = target.split('#', 1)[0]
            if not target or '://' in target or target.startswith('mailto:'):
                continue
            assert (path.parent / target).exists(), (name, target)
            links += 1
    for name in ('REQUEST_LOG.md', 'WORK_SESSIONS.md'):
        old = subprocess.check_output(['git', 'show', BASE+':'+name], cwd=ROOT)
        assert (ROOT / name).read_bytes().startswith(old)
    ids = [int(x) for x in re.findall(r'^## R(\d+)\b', (ROOT/'REQUEST_LOG.md').read_text(), re.M)]
    assert len(ids) == len(set(ids)) == 267 and set(ids) == set(range(1, 268))
    sessions = (ROOT / 'WORK_SESSIONS.md').read_text()
    for event in ('STARTED', 'COMPLETED'):
        assert len(re.findall(r'^'+event+r' \| [^\n]+ \| R267 \|', sessions, re.M)) == 1
    handoff = (ROOT / 'SESSION_HANDOFF.md').read_text()
    assert handoff.count('## Next task\n') == 1
    task = handoff.split('## Next task\n', 1)[1].split('### Historical', 1)[0]
    assert 'R267' in task and 'Sol / high' in task and '118' in task
    assert 'all nine allocations remain spent' in handoff.split('### Previous', 1)[0]
    allowed = set(PAGES) | {'REQUEST_LOG.md', 'WORK_SESSIONS.md'}
    changed = subprocess.check_output(['git', 'diff', '--name-only', BASE], cwd=ROOT, text=True).splitlines()
    assert all(n in allowed or n.startswith('docs/realizability/evidence/r267/') for n in changed)
    indexed = subprocess.check_output(['git', 'ls-files', 'docs/realizability/evidence/r267'],
                                      cwd=ROOT, text=True).splitlines()
    expected = sorted(str(p.relative_to(ROOT)) for p in HERE.iterdir() if p.is_file())
    assert indexed == expected and len(expected) == 6
    for name in expected:
        if name.endswith('/checks.json'):
            continue
        assert subprocess.check_output(['git', 'show', ':'+name], cwd=ROOT) == (ROOT/name).read_bytes()
    for command in (['git', 'diff', '--check'], ['git', 'diff', '--cached', '--check']):
        subprocess.run(command, cwd=ROOT, check=True)
    return dict(status='PASS', ast_files=3, evidence_files=6,
        local_links_checked=links, contiguous_request_ids=267,
        append_only_logs=True, lifecycle_started_completed_once=True,
        runtime_source_changes=0, evidence_index_matches=True, whitespace='PASS')


if __name__ == '__main__':
    result = run()
    (HERE/'checks.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
