"""Static R259 completion checks. Does not rerun workers or numerical code."""
import ast
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = '56ecd3f7bdf9ed6fdaaf24b0209fde1b8d0f8ada'
PAGES = ['SESSION_HANDOFF.md','STATUS.md','PROJECT_TRACKS.md','EXPERIMENT.md',
         'PHYSICAL_REALIZABILITY_PLAN.md','CONTROL_RESEARCH_ROADMAP.md',
         'docs/realizability/B1_SETUP.md','verification/nonlinear_port/README.md',
         'docs/realizability/MANUFACTURED_FAILURE_REVIEW_R259.md']


def run():
    sources = sorted(HERE.glob('*.py'))
    for path in sources:
        ast.parse(path.read_text(), filename=str(path))
    records = [p for p in HERE.glob('*.json') if p.name != 'checks.json']
    for path in records:
        json.loads(path.read_text())
    audit = json.loads((HERE/'audit.json').read_text())
    probe = json.loads((HERE/'probe.json').read_text())
    assert audit['source_files_unchanged'] == 44 and audit['raw_originals_verified'] == 84
    assert audit['spent_reservations'] == 7 and audit['new_attempts_admitted'] == 0
    assert probe['checks'] == 4 and probe['three_distinct_sites_match_saved_log'] is True
    assert not audit['numerical_modules_loaded'] and not probe['numerical_modules_loaded']
    links = 0
    for name in PAGES:
        path = ROOT/name
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            target = target.split('#',1)[0]
            if not target or '://' in target or target.startswith('mailto:'):
                continue
            assert (path.parent/target).exists(), (name,target)
            links += 1
    for name in ('REQUEST_LOG.md','WORK_SESSIONS.md'):
        old = subprocess.check_output(['git','show',BASE+':'+name], cwd=ROOT)
        assert (ROOT/name).read_bytes().startswith(old), name
    ids = [int(x) for x in re.findall(r'^## R(\d+)\b',(ROOT/'REQUEST_LOG.md').read_text(),re.M)]
    assert len(ids) == len(set(ids)) == 259 and set(ids) == set(range(1,260))
    sessions = (ROOT/'WORK_SESSIONS.md').read_text()
    for event in ('STARTED','COMPLETED'):
        assert len(re.findall(r'^'+event+r' \| [^\n]+ \| R259 \|',sessions,re.M)) == 1
    handoff = (ROOT/'SESSION_HANDOFF.md').read_text()
    assert handoff.count('## Next task\n') == 1
    next_task = handoff.split('## Next task\n',1)[1].split('### Historical',1)[0]
    assert '**Continue in this chat with GPT-6 Sol / high' in next_task
    assert 'R259' in handoff.split('### Previous',1)[0]
    changed = subprocess.check_output(['git','diff','--name-only',BASE],cwd=ROOT,text=True).splitlines()
    allowed = set(PAGES) | {'REQUEST_LOG.md','WORK_SESSIONS.md'}
    assert all(name in allowed or name.startswith('docs/realizability/evidence/r259/') for name in changed), changed
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    return dict(status='SOURCE_ONLY_DIAGNOSTIC_REPAIR_REQUIRED', ast_files=len(sources),
        json_files=len(records), local_link_targets_checked=links,
        unique_contiguous_request_ids=259, prior_logs_preserved=True,
        r259_started_once=True,r259_completed_once=True,
        historical_evidence_and_runtime_sources_unchanged=True,
        new_attempts_admitted=0, whitespace='PASS',
        next_task='Sol/high implements fixed bounded failure record/stages/tests; stop before admission',
        session_recommendation='Continue in this chat: directly connected implementation contract')


if __name__ == '__main__':
    result = run()
    (HERE/'checks.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
