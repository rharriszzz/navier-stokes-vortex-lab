"""R266 static publication checks; no numerical imports or worker."""
import ast
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = 'd5b42eb0433c81c663810ab2858b67f6b4c8c789'
PAGES = ('SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md', 'EXPERIMENT.md',
         'PHYSICAL_REALIZABILITY_PLAN.md', 'CONTROL_RESEARCH_ROADMAP.md',
         'docs/realizability/B1_SETUP.md', 'verification/nonlinear_port/README.md',
         'docs/realizability/MANUFACTURED_RESULT_R266.md')


def run():
    sources = sorted(HERE.glob('*.py'))
    records = sorted(HERE.glob('*.json')) + sorted((HERE / 'run').glob('*.json'))
    for path in sources:
        ast.parse(path.read_text(), filename=str(path))
    for path in records:
        json.loads(path.read_text())
    audit = json.loads((HERE / 'audit.json').read_text())
    assert audit['status'] == 'INCOMPLETE'
    assert audit['attempts_spent'] == 1 and audit['old_allocations_spent'] == 8
    assert audit['run_files'] == 15 and audit['caller_files'] == 4
    assert audit['original_bytes_verified'] is True and audit['cleanup_empty'] is True
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
        assert (ROOT / name).read_bytes().startswith(old), name
    ids = [int(x) for x in re.findall(r'^## R(\d+)\b',
                                    (ROOT / 'REQUEST_LOG.md').read_text(), re.M)]
    assert len(ids) == len(set(ids)) == 266 and set(ids) == set(range(1, 267))
    sessions = (ROOT / 'WORK_SESSIONS.md').read_text()
    for event in ('STARTED', 'COMPLETED'):
        assert len(re.findall(r'^' + event + r' \| [^\n]+ \| R266 \|', sessions, re.M)) == 1
    handoff = (ROOT / 'SESSION_HANDOFF.md').read_text()
    assert handoff.count('## Next task\n') == 1
    next_task = handoff.split('## Next task\n', 1)[1].split('### Historical', 1)[0]
    assert 'R266' in next_task and 'Astra / high' in next_task
    assert 'R266\'s single R265 manufactured pilot is INCOMPLETE' in handoff.split('### Previous', 1)[0]
    changed = subprocess.check_output(['git', 'diff', '--name-only', BASE],
                                      cwd=ROOT, text=True).splitlines()
    allowed = set(PAGES) | {'REQUEST_LOG.md', 'WORK_SESSIONS.md'}
    assert all(name in allowed or name.startswith('docs/realizability/evidence/r266/')
               for name in changed), changed
    indexed = subprocess.check_output(['git', 'ls-files', 'docs/realizability/evidence/r266'],
                                      cwd=ROOT, text=True).splitlines()
    expected = sorted(str(p.relative_to(ROOT)) for p in HERE.rglob('*')
                      if p.is_file())
    assert indexed == expected, (indexed, expected)
    for name in expected:
        if name.endswith('/checks.json'):
            continue
        assert subprocess.check_output(['git', 'show', ':' + name], cwd=ROOT) == (ROOT / name).read_bytes(), name
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, check=True)
    return dict(status='INCOMPLETE', ast_files=len(sources), json_files=len(records),
                local_link_targets_checked=links, unique_contiguous_request_ids=266,
                append_only_logs=True, r266_started_once=True, r266_completed_once=True,
                runtime_source_changes=0, evidence_files_in_git_index=len(expected),
                raw_run_files_in_git_index=15, caller_files_in_git_index=4,
                original_files_and_git_coverage=19, whitespace='PASS')


if __name__ == '__main__':
    result = run()
    (HERE / 'checks.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, sort_keys=True))
