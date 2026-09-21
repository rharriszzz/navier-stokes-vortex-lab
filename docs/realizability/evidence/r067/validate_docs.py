"""Validate the R067/R068/R069 documentation and small review artifacts."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE = '73416243fb9857c834d6663cca2235a116253537'
PAGES = ['AGENTS.md', 'README.md', 'PROJECT_TRACKS.md', 'REQUEST_LOG.md',
         'SESSION_HANDOFF.md', 'STATUS.md', 'docs/realizability/B1_SETUP.md',
         'docs/realizability/B2_NEXT_STEPS.md',
         'docs/realizability/B2_PHYSICAL_RUNNER_REVIEW.md',
         'docs/realizability/MAC_INSTALL_AND_BENCHMARK_PLAN.md']


def headings(page):
    return {re.sub(r'\s', '-', re.sub(r'[^a-z0-9 _-]', '',
            line.lstrip('#').strip().lower())).strip('-')
            for line in page.read_text().splitlines() if line.startswith('#')}


links = anchors = shell_blocks = 0
for name in PAGES:
    page = REPO / name
    body = page.read_text()
    assert sum(line.lstrip().startswith('```') for line in body.splitlines()) % 2 == 0, name
    for destination in re.findall(r'\[[^\]]*\]\(([^)]+)\)', body):
        if destination.startswith(('https://', 'http://', 'mailto:')):
            continue
        local, separator, anchor = destination.partition('#')
        target = (page.parent / local).resolve() if local else page
        assert target.exists(), (name, destination)
        links += 1
        if separator:
            assert anchor in headings(target), (name, destination)
            anchors += 1
    for block in re.findall(r'^```bash\n(.*?)^```', body, re.M | re.S):
        subprocess.run(['bash', '-n'], input=block, text=True, check=True, cwd=REPO)
        shell_blocks += 1
for path in HERE.glob('*.py'):
    ast.parse(path.read_text(), filename=str(path))
for name in ('review.json', 'forms.json'):
    json.loads((HERE / name).read_text(), parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
old_log = subprocess.check_output(['git', 'show', f'{BASE}:REQUEST_LOG.md'], cwd=REPO)
log = (REPO / 'REQUEST_LOG.md').read_bytes()
assert log.startswith(old_log)
old_ids = [int(s) for s in re.findall(rb'^## R(\d+) ', old_log, re.M)]
new_ids = [int(s) for s in re.findall(rb'^## R(\d+) ', log[len(old_log):], re.M)]
assert new_ids == [max(old_ids)+i for i in (1,2,3)]
assert len(set(old_ids + new_ids)) == len(old_ids + new_ids)
for name in ('environment-b1.yml', 'make_trajectories.py', 'render.sh', 'render.ps1'):
    old = subprocess.check_output(['git', 'show', f'{BASE}:{name}'], cwd=REPO)
    assert (REPO/name).read_bytes() == old, name
handoff = (REPO/'SESSION_HANDOFF.md').read_text()
assert handoff.count('## Next task\n') == 1
next_task = handoff.split('## Next task\n')[1].split('## Deferred Mac setup check')[0]
assert 'Luna' in next_task and '3.12.13' in next_task and '120 s' in next_task
assert 'No DOLFINx/MPI import' in next_task
forms = json.loads((HERE/'forms.json').read_text())
assert len(forms['forms']) == 4
assert all(group['integrands_after_analysis'] == 1
           for form in forms['forms'].values() for group in form['groups'])
subprocess.run(['git', 'diff', '--check'], cwd=REPO, check=True)
result = dict(status='passed', markdown_files=len(PAGES), local_links=links,
              heading_fragments=anchors, bash_blocks_syntax_only=shell_blocks,
              new_request_ids=new_ids, request_history_prefix_preserved=True,
              unchanged_runtime_pins_and_trajectory_render_sources=True,
              symbolic_forms=4, physical_execution=False,
              checks='Links/headings, Bash syntax without execution, Python AST, JSON, request continuity, source preservation and whitespace',
              artifacts={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in sorted(HERE.iterdir()) if p.is_file()
                         and p.name != 'documentation_validation.json'})
(HERE/'documentation_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
