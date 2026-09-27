"""Static publication checks for the R263 source-only review."""
import ast
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = 'fa5f56f4a4ff1c2d3bfff9d713e20794d3bf364f'
PAGES = ('SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md', 'EXPERIMENT.md',
         'PHYSICAL_REALIZABILITY_PLAN.md', 'CONTROL_RESEARCH_ROADMAP.md',
         'docs/realizability/B1_SETUP.md', 'verification/nonlinear_port/README.md',
         'docs/realizability/MANUFACTURED_DEPTH_REVIEW_R263.md')


def run():
    sources, records = sorted(HERE.glob('*.py')), sorted(HERE.glob('*.json'))
    for path in sources:
        ast.parse(path.read_text(), filename=str(path))
    for path in records:
        json.loads(path.read_text())
    audit = json.loads((HERE/'audit.json').read_text())
    probe = json.loads((HERE/'probe.json').read_text())
    assert audit['status'] == 'REPAIR_CONTRACT_NO_ADMISSION'
    assert audit['source_files'] == 46 and audit['spent_reservations'] == 8
    assert audit['raw_original_files_verified'] == audit['git_index_raw_files_verified'] == 97
    assert len(audit['base_omitted_logs']) == 4 and audit['omitted_log_bytes'] == 781
    assert audit['new_attempts_admitted'] == 0
    assert probe['case_count'] == 28 and probe['focused_edge_cases'] == 5
    assert len(probe['negative_controls']) == 4 and not probe['numerical_modules_loaded']
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
    assert len(ids) == len(set(ids)) == 263 and set(ids) == set(range(1, 264))
    sessions = (ROOT/'WORK_SESSIONS.md').read_text()
    for event in ('STARTED', 'COMPLETED'):
        assert len(re.findall(r'^'+event+r' \| [^\n]+ \| R263 \|', sessions, re.M)) == 1
    handoff = (ROOT/'SESSION_HANDOFF.md').read_text()
    assert handoff.count('## Next task\n') == 1
    next_task = handoff.split('## Next task\n', 1)[1].split('### Historical', 1)[0]
    assert 'Sol / high' in next_task and 'Poly.evaluate_balanced' in next_task
    assert 'R263 fixes a balanced symbolic' in handoff.split('### Previous', 1)[0]
    changed = subprocess.check_output(['git', 'diff', '--name-only', BASE], cwd=ROOT, text=True).splitlines()
    assert not any(name.startswith('verification/nonlinear_port/') and name != 'verification/nonlinear_port/README.md'
                   for name in changed)
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, check=True)
    return dict(status='REPAIR_CONTRACT_NO_ADMISSION', ast_files=len(sources),
                json_files=len(records), local_link_targets_checked=links,
                unique_contiguous_request_ids=263, append_only_logs=True,
                r263_started_once=True, r263_completed_once=True,
                runtime_source_unchanged=True, original_files_and_git_coverage=97,
                new_attempts_admitted=0, whitespace='PASS')


if __name__ == '__main__':
    result = run()
    (HERE/'checks.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
