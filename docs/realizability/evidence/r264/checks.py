"""Static publication checks for the R264 balanced-source integration."""
import ast
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = '4323cf1a2b23d8fb009afca5083678d6dc0e27b3'
PAGES = ('SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md', 'EXPERIMENT.md',
         'PHYSICAL_REALIZABILITY_PLAN.md', 'CONTROL_RESEARCH_ROADMAP.md',
         'docs/realizability/B1_SETUP.md', 'verification/nonlinear_port/README.md',
         'docs/realizability/MANUFACTURED_BALANCED_INTEGRATION_R264.md')


def run():
    sources, records = sorted(HERE.glob('*.py')), sorted(HERE.glob('*.json'))
    for path in sources:
        ast.parse(path.read_text(), filename=str(path))
    for path in records:
        json.loads(path.read_text())
    audit = json.loads((HERE/'audit.json').read_text())
    probe = json.loads((HERE.parent/'r263/probe.json').read_text())
    tests = json.loads((HERE/'tests.json').read_text())
    inventory = json.loads((HERE/'source_inventory.json').read_text())
    assert audit['status'] == 'BALANCED_SOURCE_IMPLEMENTED_NO_ADMISSION'
    assert audit['source_files'] == len(inventory['source_sha256']) == 47
    assert audit['prior_source_unchanged'] == 44 and audit['spent_reservations'] == 8
    assert tests['tests'] == 118 and tests['failures'] == tests['errors'] == 0
    assert audit['raw_original_files_verified'] == audit['git_index_raw_files_verified'] == 97
    assert not audit['base_omitted_logs'] and audit['omitted_log_bytes'] == 0
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
    assert len(ids) == len(set(ids)) == 264 and set(ids) == set(range(1, 265))
    sessions = (ROOT/'WORK_SESSIONS.md').read_text()
    for event in ('STARTED', 'COMPLETED'):
        assert len(re.findall(r'^'+event+r' \| [^\n]+ \| R264 \|', sessions, re.M)) == 1
    handoff = (ROOT/'SESSION_HANDOFF.md').read_text()
    assert handoff.count('## Next task\n') == 1
    next_task = handoff.split('## Next task\n', 1)[1].split('### Historical', 1)[0]
    assert 'Astra / high' in next_task and 'Poly.evaluate_balanced' in next_task
    assert 'R264 implements the R263 balanced' in handoff.split('### Previous', 1)[0]
    changed = subprocess.check_output(['git', 'diff', '--name-only', BASE], cwd=ROOT, text=True).splitlines()
    expected_runtime = {'verification/nonlinear_port/cube_adapter.py',
                        'verification/nonlinear_port/polynomial.py',
                        'verification/nonlinear_port/test_balanced_polynomial.py'}
    assert {name for name in changed if name.startswith('verification/nonlinear_port/')
            and name != 'verification/nonlinear_port/README.md'} == expected_runtime
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, check=True)
    return dict(status='BALANCED_SOURCE_IMPLEMENTED_NO_ADMISSION', ast_files=len(sources),
                json_files=len(records), local_link_targets_checked=links,
                unique_contiguous_request_ids=264, append_only_logs=True,
                r264_started_once=True, r264_completed_once=True,
                changed_runtime_source_files=2, new_source_test_files=1,
                original_files_and_git_coverage=97,
                new_attempts_admitted=0, whitespace='PASS')


if __name__ == '__main__':
    result = run()
    (HERE/'checks.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
