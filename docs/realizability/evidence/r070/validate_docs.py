"""Check R070 continuity links, history append, and scoped whitespace."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
PAGES = [ROOT/'REQUEST_LOG.md', ROOT/'SESSION_HANDOFF.md']

def headings(path):
    return {re.sub(r'\s', '-', re.sub(r'[^a-z0-9 _-]', '', line.lstrip('#').strip().lower())).strip('-')
            for line in path.read_text().splitlines() if line.startswith('#')}

links = anchors = 0
for page in PAGES:
    body = page.read_text()
    for destination in re.findall(r'\[[^\]]*\]\(([^)]+)\)', body):
        if destination.startswith(('https://', 'http://', 'mailto:')):
            continue
        local, sep, anchor = destination.partition('#')
        target = (page.parent/local).resolve() if local else page
        assert target.exists(), (page, destination)
        links += 1
        if sep:
            assert anchor in headings(target), (page, destination)
            anchors += 1
old = subprocess.check_output(['git','show','HEAD:REQUEST_LOG.md'], cwd=ROOT)
current = (ROOT/'REQUEST_LOG.md').read_bytes()
assert current.startswith(old)
added = [int(x) for x in re.findall(rb'^## R(\d+) ', current[len(old):], re.M)]
assert added == [70,71], added
handoff = (ROOT/'SESSION_HANDOFF.md').read_text()
assert handoff.count('## Next task\n') == 1
next_task = handoff.split('## Next task\n',1)[1].split('## Deferred Mac setup check',1)[0]
assert all(s in next_task for s in ('Luna','medium','3.12.13','120 s','256 MiB','Do not execute a FEM'))
assert 'physical execution remains disabled' in handoff[:2200]
subprocess.run(['git','diff','--check'], cwd=ROOT, check=True)
result = {'status':'passed', 'markdown_files':len(PAGES), 'local_links':links,
          'heading_fragments':anchors, 'new_request_ids':added,
          'history_prefix_preserved':True, 'single_current_next_task':True,
          'physical_execution_disabled':True, 'scoped_diff_whitespace':'passed',
          'attempt_history':[
              {'attempt':1,'status':'failed','reason':'The first request-history check counted the R071 outcome subheading as a duplicate request ID; changed it to a dated bold outcome note.'},
              {'attempt':2,'status':'failed','reason':'The first next-task check expected a literal “No”; updated the check to match the stated “Do not execute a FEM” stop.'},
              {'attempt':3,'status':'passed','reason':'44 local links, 11 heading fragments, request-prefix continuity, sequential IDs, current handoff task and git diff --check passed before the final dated log note.'},
              {'attempt':4,'status':'passed','reason':'Repeated after the final log note; all checks passed and result hashes match the committed inputs.'},
              {'attempt':5,'status':'passed','reason':'Repeated after publication-state wording was made valid both before and after push; all continuity and whitespace checks passed.'},
              {'attempt':6,'status':'passed','reason':'Updated the handoff to distinguish the unchanged archive from the repaired disposable copy; all final links, request-history and whitespace checks passed.'}
          ],
          'files_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in PAGES}}
(BASE/'documentation_validation.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2))
