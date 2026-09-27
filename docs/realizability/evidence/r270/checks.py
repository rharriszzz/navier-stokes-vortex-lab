"""R270 saved-evidence and publication checks, without numerical imports."""
import ast
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = '950c2a72fe04fadc2d5a262539f0748d24924646'
PAGES = ('SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md',
         'EXPERIMENT.md', 'PHYSICAL_REALIZABILITY_PLAN.md',
         'CONTROL_RESEARCH_ROADMAP.md', 'docs/realizability/B1_SETUP.md',
         'verification/nonlinear_port/README.md',
         'docs/realizability/MANUFACTURED_RESULT_R270.md')


def run():
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    for path in HERE.glob('*.json'):
        json.loads(path.read_text())
    for path in (HERE / 'run').glob('*.json'):
        json.loads(path.read_text())
    verified = json.loads((HERE / 'verification.json').read_text())
    assert verified['status'] == 'INCOMPLETE' and verified['allocation_spent'] == '1/1'
    assert len(verified['copied_run_files']) == 16
    assert verified['new_worker_pid_cgroup_absent']
    for degree in ('24', '26'):
        assert verified['degrees'][degree]['comparisons_passed'] == 5
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
        old = subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=ROOT)
        assert (ROOT / name).read_bytes().startswith(old)
    ids = [int(v) for v in re.findall(r'^## R(\d+)\b',
            (ROOT / 'REQUEST_LOG.md').read_text(), re.M)]
    assert len(ids) == len(set(ids)) == 270 and set(ids) == set(range(1, 271))
    sessions = (ROOT / 'WORK_SESSIONS.md').read_text()
    assert len(re.findall(r'^STARTED \| [^\n]+ \| R270 \|', sessions, re.M)) == 1
    assert len(re.findall(r'^COMPLETED \| [^\n]+ \| R270 \|', sessions, re.M)) == 1
    handoff = (ROOT / 'SESSION_HANDOFF.md').read_text()
    assert handoff.count('## Next task\n') == 1
    task = handoff.split('## Next task\n', 1)[1].split('### Historical', 1)[0]
    assert 'R270' in task and 'Astra / high' in task and 'source-only' in task
    allowed = set(PAGES) | {'REQUEST_LOG.md', 'WORK_SESSIONS.md'}
    changed = subprocess.check_output(['git', 'diff', '--name-only', BASE], cwd=ROOT,
                                      text=True).splitlines()
    untracked = subprocess.check_output(['git', 'ls-files', '--others',
                                         '--exclude-standard'], cwd=ROOT,
                                        text=True).splitlines()
    assert all(name in allowed or name.startswith('docs/realizability/evidence/r270/')
               for name in changed + untracked), changed + untracked
    for command in (['git', 'diff', '--check'], ['git', 'diff', '--cached', '--check']):
        subprocess.run(command, cwd=ROOT, check=True)
    return dict(status='PASS', evidence_json_files=len(list(HERE.glob('*.json'))) +
                len(list((HERE / 'run').glob('*.json'))),
                local_links_checked=links, contiguous_request_ids=270,
                append_only_logs=True, lifecycle_started_completed_once=True,
                scoped_files=True, whitespace='PASS')


if __name__ == '__main__':
    result = run()
    (HERE / 'checks.json').write_text(json.dumps(result, indent=2,
                                                sort_keys=True) + '\n')
    print(json.dumps(result, sort_keys=True))
