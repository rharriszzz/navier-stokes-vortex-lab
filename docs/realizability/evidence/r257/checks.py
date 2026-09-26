"""Static R257 completion checks, including append-only history."""
import ast
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = 'a00049a724f98e0094ce693d9b547a9fbc9564c5'
MARKDOWN = ['AGENTS.md', 'docs/workflow/SESSION_PROTOCOL.md', 'SESSION_HANDOFF.md',
    'STATUS.md', 'PROJECT_TRACKS.md', 'EXPERIMENT.md', 'PHYSICAL_REALIZABILITY_PLAN.md',
    'CONTROL_RESEARCH_ROADMAP.md', 'docs/realizability/B1_SETUP.md',
    'verification/nonlinear_port/README.md', 'docs/realizability/MANUFACTURED_ADMISSION_R257.md']


def run():
    inventory = json.loads((HERE/'source_inventory.json').read_text())['source_sha256']
    python = [ROOT/name for name in inventory if name.endswith('.py')]+list(HERE.glob('*.py'))
    for path in python:
        ast.parse(path.read_text(), filename=str(path))
    records = [p for p in HERE.glob('*.json') if p.name != 'checks.json']
    for path in records:
        json.loads(path.read_text())
    links = 0
    for name in MARKDOWN:
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
    assert len(ids) == len(set(ids)) == 257 and set(ids) == set(range(1, 258))
    sessions = (ROOT/'WORK_SESSIONS.md').read_text()
    for event in ('STARTED', 'COMPLETED'):
        assert len(re.findall(r'^'+event+r' \| [^\n]+ \| R257 \|', sessions, re.M)) == 1
    handoff = (ROOT/'SESSION_HANDOFF.md').read_text()
    assert handoff.count('## Next task\n') == 1
    assert '**Use `/new`, select GPT-6 Sol / high' in handoff
    # Verify historical tracked evidence and old fixture runtime sources unchanged.
    changed = subprocess.check_output(['git', 'diff', '--name-only', BASE], cwd=ROOT, text=True).splitlines()
    allowed = {'verification/nonlinear_port/manufactured_driver.py',
               'verification/nonlinear_port/manufactured_report.py',
               'verification/nonlinear_port/test_manufactured_integration.py',
               'verification/nonlinear_port/README.md'}
    assert all(not n.startswith('verification/nonlinear_port/') or n in allowed for n in changed)
    assert not any(n.startswith('docs/realizability/evidence/')
                   and not n.startswith('docs/realizability/evidence/r257/') for n in changed)
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    return dict(status='ADMITTED_FOR_LATER_EXECUTION', ast_files=len(python), json_files=len(records),
        local_link_targets_checked=links, unique_contiguous_request_ids=257,
        prior_logs_preserved=True, r257_started_once=True, r257_completed_once=True,
        historical_evidence_unchanged=True, old_fixture_sources_unchanged=True,
        whitespace='PASS', session_recommendation='Use /new after publication; Sol/high then Continue',
        next_task='Execute fixed R257 pilot once, preserve evidence, publish and stop for Astra/high interpretation')


if __name__ == '__main__':
    record = run()
    (HERE/'checks.json').write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
    print(json.dumps(record, sort_keys=True))
