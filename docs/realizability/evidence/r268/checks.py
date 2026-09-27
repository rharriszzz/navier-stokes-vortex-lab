"""R268 source, links, lifecycle and scoped publication checks."""
import ast
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = 'ef32bb2aae8fa393038b59d101dd7c9b0c7fc92d'
PAGES = ('SESSION_HANDOFF.md','STATUS.md','PROJECT_TRACKS.md','EXPERIMENT.md',
         'PHYSICAL_REALIZABILITY_PLAN.md','CONTROL_RESEARCH_ROADMAP.md',
         'docs/realizability/B1_SETUP.md','verification/nonlinear_port/README.md',
         'docs/realizability/MANUFACTURED_ANGULAR_SIDECAR_R268.md')
SOURCE = ('manufactured_angular.py','manufactured_driver.py',
          'manufactured_failure.py','manufactured_worker.py',
          'test_manufactured_angular.py','test_manufactured_failure.py',
          'test_manufactured_integration.py')


def run():
    for name in SOURCE:
        path = ROOT/'verification/nonlinear_port'/name
        ast.parse(path.read_text(), filename=str(path))
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    for path in HERE.glob('*.json'):
        json.loads(path.read_text())
    tests = json.loads((HERE/'tests.json').read_text())
    audit = json.loads((HERE/'audit.json').read_text())
    assert tests['tests'] == 123 and tests['failures'] == tests['errors'] == 0
    assert tests['saved_r266_validator'] == 'INCOMPLETE' and not tests['numerical_modules_loaded']
    assert audit['status'] == 'PASS' and audit['spent_allocations'] == 9
    assert audit['original_and_index_files_unchanged'] == 116
    assert len(audit['source_sha256']) == 49
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
        old = subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
        assert (ROOT/name).read_bytes().startswith(old)
    ids = [int(v) for v in re.findall(r'^## R(\d+)\b',
            (ROOT/'REQUEST_LOG.md').read_text(),re.M)]
    assert len(ids) == len(set(ids)) == 268 and set(ids) == set(range(1,269))
    sessions = (ROOT/'WORK_SESSIONS.md').read_text()
    assert len(re.findall(r'^STARTED \| [^\n]+ \| R268 \|',sessions,re.M)) == 1
    assert len(re.findall(r'^COMPLETED \| [^\n]+ \| R268 \|',sessions,re.M)) == 1
    handoff = (ROOT/'SESSION_HANDOFF.md').read_text()
    assert handoff.count('## Next task\n') == 1
    task = handoff.split('## Next task\n',1)[1].split('### Historical',1)[0]
    assert 'R268' in task and 'Astra / high' in task and 'stop before launch' in task
    allowed = set(PAGES)|{'REQUEST_LOG.md','WORK_SESSIONS.md'}|{
        'verification/nonlinear_port/'+name for name in SOURCE}
    changed = subprocess.check_output(['git','diff','--name-only',BASE],cwd=ROOT,text=True).splitlines()
    untracked = subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
    assert all(name in allowed or name.startswith('docs/realizability/evidence/r268/')
               for name in changed+untracked)
    for command in (['git','diff','--check'],['git','diff','--cached','--check']):
        subprocess.run(command,cwd=ROOT,check=True)
    return dict(status='PASS', ast_files=len(SOURCE)+len(list(HERE.glob('*.py'))),
                evidence_json_files=len(list(HERE.glob('*.json'))),
                local_links_checked=links, contiguous_request_ids=268,
                append_only_logs=True, lifecycle_started_completed_once=True,
                scoped_files=True, whitespace='PASS')


if __name__ == '__main__':
    result = run()
    (HERE/'checks.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
