"""Static R260 publication checks; never imports numerical or worker code."""
import ast
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = '01097367a7f971ba34d4a7a5463d34bddab8260c'
PAGES = [
    'SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md', 'EXPERIMENT.md',
    'PHYSICAL_REALIZABILITY_PLAN.md', 'CONTROL_RESEARCH_ROADMAP.md',
    'docs/realizability/B1_SETUP.md', 'verification/nonlinear_port/README.md',
    'docs/realizability/MANUFACTURED_DIAGNOSTICS_R260.md',
]
CHANGED_RUNTIME = {
    'verification/nonlinear_port/manufactured_driver.py',
    'verification/nonlinear_port/manufactured_worker.py',
    'verification/nonlinear_port/test_manufactured_integration.py',
}
ADDED_RUNTIME = {
    'verification/nonlinear_port/manufactured_failure.py',
    'verification/nonlinear_port/test_manufactured_failure.py',
}


def run():
    for name in CHANGED_RUNTIME | ADDED_RUNTIME:
        path = ROOT/name
        ast.parse(path.read_text(), filename=str(path))
    sources = sorted(HERE.glob('*.py'))
    for path in sources:
        ast.parse(path.read_text(), filename=str(path))
    records = [p for p in HERE.glob('*.json') if p.name != 'checks.json']
    for path in records:
        json.loads(path.read_text())
    audit = json.loads((HERE/'audit.json').read_text())
    tests = json.loads((HERE/'tests.json').read_text())
    assert audit['status'] == 'SOURCE_INTEGRATED_NO_ADMISSION'
    assert audit['source_files'] == 46 and audit['raw_originals_verified'] == 84
    assert audit['spent_reservations'] == 7 and audit['new_attempts_admitted'] == 0
    assert set(audit['changed_prior_source_files']) == CHANGED_RUNTIME
    assert set(audit['added_source_test_files']) == ADDED_RUNTIME
    assert tests['tests'] == 113 and tests['errors'] == tests['failures'] == 0
    assert tests['saved_r246_validator'] == tests['saved_r253_validator'] == 'PASS'
    assert tests['saved_r258_status'] == 'INCOMPLETE'
    assert not tests['numerical_modules_loaded'] and not audit['numerical_modules_loaded']
    links = 0
    for name in PAGES:
        path = ROOT/name
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            target = target.split('#', 1)[0]
            if not target or '://' in target or target.startswith('mailto:'):
                continue
            if path.parent/target == HERE/'checks.json':
                links += 1  # This output is created after the check succeeds.
                continue
            assert (path.parent/target).exists(), (name, target)
            links += 1
    for name in ('REQUEST_LOG.md', 'WORK_SESSIONS.md'):
        old = subprocess.check_output(['git', 'show', BASE+':'+name], cwd=ROOT)
        assert (ROOT/name).read_bytes().startswith(old), name
    ids = [int(x) for x in re.findall(r'^## R(\d+)\b',
                                     (ROOT/'REQUEST_LOG.md').read_text(), re.M)]
    assert len(ids) == len(set(ids)) == 260 and set(ids) == set(range(1, 261))
    sessions = (ROOT/'WORK_SESSIONS.md').read_text()
    for event in ('STARTED', 'COMPLETED'):
        assert len(re.findall(r'^'+event+r' \| [^\n]+ \| R260 \|',
                              sessions, re.M)) == 1
    handoff = (ROOT/'SESSION_HANDOFF.md').read_text()
    assert handoff.count('## Next task\n') == 1
    next_task = handoff.split('## Next task\n', 1)[1].split('### Historical', 1)[0]
    assert '**Use `/new`, select GPT-6 Astra / high' in next_task
    assert 'R260' in handoff.split('### Previous', 1)[0]
    changed = set(subprocess.check_output(['git', 'diff', '--name-only', BASE],
                                          cwd=ROOT, text=True).splitlines())
    evidence = {'docs/realizability/evidence/r260/'+name for name in (
        'audit.py', 'audit.json', 'checks.py', 'checks.json',
        'test_runner.py', 'tests.txt', 'tests.json')}
    allowed = set(PAGES) | CHANGED_RUNTIME | ADDED_RUNTIME | evidence | {
        'REQUEST_LOG.md', 'WORK_SESSIONS.md'}
    assert changed == allowed, (sorted(changed-allowed), sorted(allowed-changed))
    assert all((ROOT/name).exists() for name in ADDED_RUNTIME)
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    return dict(status='SOURCE_INTEGRATED_NO_ADMISSION',
                ast_files=len(sources)+len(CHANGED_RUNTIME | ADDED_RUNTIME),
                json_files=len(records), local_link_targets_checked=links,
                unique_contiguous_request_ids=260, prior_logs_preserved=True,
                r260_started_once=True, r260_completed_once=True,
                intended_runtime_changes_only=True,
                tests=113, new_attempts_admitted=0, whitespace='PASS',
                next_task='Astra/high source review; new one-use admission/caller or precise blocker; stop before launch',
                session_recommendation='/new at published source boundary')


if __name__ == '__main__':
    result = run()
    (HERE/'checks.json').write_text(json.dumps(result, indent=2,
                                               sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
