"""Static R261 publication checks; no numerical imports or workload launch."""
import ast
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = '71a82e1ff9a49a8d26de654f7f45a9014d5bd740'
PAGES = [
    'SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md', 'EXPERIMENT.md',
    'PHYSICAL_REALIZABILITY_PLAN.md', 'CONTROL_RESEARCH_ROADMAP.md',
    'docs/realizability/B1_SETUP.md', 'verification/nonlinear_port/README.md',
    'docs/realizability/MANUFACTURED_ADMISSION_R261.md',
]


def run():
    sources = sorted(HERE.glob('*.py')) + [ROOT/name for name in (
        'verification/nonlinear_port/manufactured_driver.py',
        'verification/nonlinear_port/manufactured_failure.py',
        'verification/nonlinear_port/test_manufactured_failure.py')]
    for path in sources:
        ast.parse(path.read_text(), filename=str(path))
    records = sorted(HERE.glob('*.json'))
    for path in records:
        json.loads(path.read_text())
    audit = json.loads((HERE/'audit.json').read_text())
    tests = json.loads((HERE/'tests.json').read_text())
    caller = json.loads((HERE/'caller_tests.json').read_text())
    assert audit['status'] == 'ADMITTED_FOR_LATER_EXECUTION'
    assert audit['source_files'] == 46 and audit['raw_originals_verified'] == 84
    assert audit['historical_reservations_spent'] == 7 and audit['new_attempts_spent'] == 0
    assert tests['tests'] == 114 and tests['errors'] == tests['failures'] == 0
    assert caller['count'] == 6 and caller['errors'] == caller['failures'] == 0
    assert not tests['numerical_modules_loaded'] and not caller['numerical_modules_loaded']
    links = 0
    for name in PAGES:
        path = ROOT/name
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            target = target.split('#', 1)[0]
            if not target or '://' in target or target.startswith('mailto:'):
                continue
            if path.parent/target == HERE/'checks.json':
                links += 1
                continue
            assert (path.parent/target).exists(), (name, target)
            links += 1
    for name in ('REQUEST_LOG.md', 'WORK_SESSIONS.md'):
        old = subprocess.check_output(['git', 'show', BASE+':'+name], cwd=ROOT)
        assert (ROOT/name).read_bytes().startswith(old), name
    ids = [int(x) for x in re.findall(r'^## R(\d+)\b',
                                     (ROOT/'REQUEST_LOG.md').read_text(), re.M)]
    assert len(ids) == len(set(ids)) == 261 and set(ids) == set(range(1, 262))
    sessions = (ROOT/'WORK_SESSIONS.md').read_text()
    for event in ('STARTED', 'COMPLETED'):
        assert len(re.findall(r'^'+event+r' \| [^\n]+ \| R261 \|', sessions, re.M)) == 1
    handoff = (ROOT/'SESSION_HANDOFF.md').read_text()
    assert handoff.count('## Next task\n') == 1
    next_task = handoff.split('## Next task\n', 1)[1].split('### Historical', 1)[0]
    assert 'R261' in next_task and 'Stop for Astra/high' in next_task
    assert 'R261 admits one NEW' in handoff.split('### Previous', 1)[0]
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    return dict(status='ADMITTED_FOR_LATER_EXECUTION', ast_files=len(sources),
                json_files=len(records), local_link_targets_checked=links,
                unique_contiguous_request_ids=261, prior_logs_preserved=True,
                r261_started_once=True, r261_completed_once=True,
                source_tests=114, fake_caller_tests=6, new_attempts_spent=0,
                whitespace='PASS', next_task='execute fixed R261 caller once after later Continue')


if __name__ == '__main__':
    result = run()
    (HERE/'checks.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
