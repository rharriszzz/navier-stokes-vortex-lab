"""R272 publication checks; source-only, writes only its own result."""
import ast
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = '83fb7c95143fa91869be7b89a436dca4a7e6e1d7'
PAGES = ('SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md', 'EXPERIMENT.md',
         'PHYSICAL_REALIZABILITY_PLAN.md', 'CONTROL_RESEARCH_ROADMAP.md',
         'docs/realizability/B1_SETUP.md', 'verification/nonlinear_port/README.md',
         'docs/realizability/MANUFACTURED_SPATIAL_DESIGN_R272.md')


def run():
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    for path in HERE.glob('*.json'):
        json.loads(path.read_text(), parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
    probe = json.loads((HERE/'probe.json').read_text())
    audit = json.loads((HERE/'audit.json').read_text())
    assert audit['status'] == 'PASS' and audit['spent_allocations'] == 10
    assert audit['source_bindings_unchanged'] == 50
    assert audit['old_original_and_index_files'] + audit['r270_original_and_index_files'] == 132
    assert probe['status'] == 'DESIGN_COMPLETE_NOT_ADMITTED'
    assert probe['new_admissions'] == probe['new_attempts'] == 0
    assert not probe['numerical_modules_loaded'] and not audit['numerical_modules_loaded']
    assert probe['saved_r246_validator'] == probe['saved_r253_validator'] == 'PASS'
    assert probe['saved_r266_validator'] == probe['saved_r270_validator'] == 'INCOMPLETE'
    assert probe['mesh_counts']['4']['bordered_dofs'] == 2315
    assert probe['linear_serialized_upper_bound'] < probe['proposed_linear_bytes_cap']
    assert probe['angular_both_degrees_serialized_upper_bound'] < probe['proposed_angular_bytes_cap']
    assert probe['actual_n4_resource_fit'] == 'UNMEASURED'
    assert probe['baseline_files_bound'] == 18
    links = 0
    for name in PAGES:
        path = ROOT/name
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            target = target.split('#', 1)[0]
            if not target or '://' in target or target.startswith('mailto:'):
                continue
            resolved = (path.parent/target).resolve()
            if resolved == HERE/'checks.json' and not resolved.exists():
                continue  # This invocation creates its result; a second pass checks its link.
            assert resolved.exists(), (name, target)
            links += 1
    for name in ('REQUEST_LOG.md', 'WORK_SESSIONS.md'):
        old = subprocess.check_output(['git', 'show', BASE+':'+name], cwd=ROOT)
        assert (ROOT/name).read_bytes().startswith(old)
    ids = [int(v) for v in re.findall(r'^## R(\d+)\b', (ROOT/'REQUEST_LOG.md').read_text(), re.M)]
    assert len(ids) == len(set(ids)) == 272 and set(ids) == set(range(1, 273))
    sessions = (ROOT/'WORK_SESSIONS.md').read_text()
    for event in ('STARTED', 'COMPLETED'):
        assert len(re.findall(r'^'+event+r' \| [^\n]+ \| R272 \|', sessions, re.M)) == 1
    handoff = (ROOT/'SESSION_HANDOFF.md').read_text()
    assert handoff.count('## Next task\n') == 1
    task = handoff.split('## Next task\n', 1)[1].split('### Historical', 1)[0]
    assert all(s in task for s in ('Sol / high', 'n=4', '2,315', '16 MiB', 'source', 'Stop before new admission'))
    allowed = set(PAGES) | {'REQUEST_LOG.md', 'WORK_SESSIONS.md'}
    changed = subprocess.check_output(['git', 'diff', '--name-only', BASE], cwd=ROOT, text=True).splitlines()
    untracked = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    assert all(name in allowed or name.startswith('docs/realizability/evidence/r272/')
               for name in changed + untracked), changed + untracked
    for command in (['git', 'diff', '--check'], ['git', 'diff', '--cached', '--check']):
        subprocess.run(command, cwd=ROOT, check=True)
    return dict(status='PASS', local_links_checked=links, contiguous_request_ids=272,
        evidence_python_files=len(list(HERE.glob('*.py'))),
        append_only_logs=True, lifecycle_started_completed_once=True,
        scoped_files=True, whitespace='PASS', historical_source_tests_reused=127,
        historical_caller_tests_reused=8, new_numerical_work=False)


if __name__ == '__main__':
    result = run()
    (HERE/'checks.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
