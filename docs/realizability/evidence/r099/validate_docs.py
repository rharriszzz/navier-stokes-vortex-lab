"""R099 documentation integrity only. No archived imports or behavioral runs."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = 'd26b1adbef44d49582a88f058a5cfbcd222bfd32'
START = 'fe67f6a'
ALLOWED = {'REQUEST_LOG.md', 'WORK_SESSIONS.md', 'SESSION_HANDOFF.md', 'STATUS.md',
           'PROJECT_TRACKS.md', 'docs/realizability/B2_NEXT_STEPS.md'}
CONTRACT = ROOT / 'docs/realizability/B2_MONITOR_TRUSTED_ADAPTER_CONTRACT.md'


def git(*args, input=None):
    return subprocess.check_output(['git', *args], cwd=ROOT, input=input)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def headings(path):
    return {re.sub(r'\s', '-', re.sub(r'[^\w\-\s]', '',
            re.sub(r'^#+\s+', '', line).strip().lower()))
            for line in path.read_text().splitlines() if re.match(r'^#{1,6} ', line)}


def main():
    baseline = {}
    for row in git('ls-tree', '-r', BASE).decode().splitlines():
        fields, name = row.split('\t', 1)
        if name not in ALLOWED:
            baseline[name] = fields.split()[2]
    actual = git('hash-object', '--stdin-paths',
                 input=('\n'.join(baseline) + '\n').encode()).decode().splitlines()
    assert actual == list(baseline.values()), 'unexpected baseline modification'
    for name in ('REQUEST_LOG.md', 'WORK_SESSIONS.md'):
        for commit in (BASE, START):
            assert (ROOT / name).read_bytes().startswith(git('show', f'{commit}:{name}'))
    requests = re.findall(r'^## R(\d+)\b', (ROOT / 'REQUEST_LOG.md').read_text(), re.M)
    assert len(requests) == len(set(requests)) == 99 and max(map(int, requests)) == 99
    session = (ROOT / 'WORK_SESSIONS.md').read_text().split('## R099 —', 1)[1]
    assert len(re.findall(r'^STARTED \|', session, re.M)) == 1
    assert len(re.findall(r'^COMPLETED \|', session, re.M)) == 1
    handoff = (ROOT / 'SESSION_HANDOFF.md').read_text()
    assert 'GPT-6 Astra/high' in handoff and 'documentation-only' in handoff
    assert 'capability decision' in handoff and 'No new execution allowance' in handoff
    words = sum(len((ROOT / n).read_text().split()) for n in ('AGENTS.md', 'SESSION_HANDOFF.md'))
    assert words < 2800
    paths = [ROOT / n for n in sorted(ALLOWED)] + [HERE / 'README.md', CONTRACT]
    links = fragments = 0
    for path in paths:
        for raw in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            if re.match(r'^[a-zA-Z]+:', raw):
                continue
            target, _, fragment = unquote(raw).partition('#')
            dest = (path.parent / target).resolve() if target else path
            assert dest == HERE / 'documentation_validation.json' or dest.exists(), (path, raw)
            links += 1
            if fragment:
                assert fragment in headings(dest), (path, raw, 'missing heading')
                fragments += 1
    text = CONTRACT.read_text()
    field_map = {}
    for filename, classes in [('certificate.py', ('Admission', 'TerminalWitness')),
                              ('primitives.py', ('Policy',))]:
        tree = ast.parse((ROOT / 'docs/realizability/evidence/r097/source' / filename).read_text())
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef) and n.name in classes):
            fields = [n.target.id for n in cls.body if isinstance(n, ast.AnnAssign)]
            field_map[cls.name] = fields
            for field in fields:
                assert f'`{field}`' in text or f'`{field}=' in text, (cls.name, field)
    assert {k: len(v) for k, v in field_map.items()} == {'Admission': 9, 'TerminalWitness': 12, 'Policy': 7}
    assert len(re.findall(r'^\| E[0-9] ', text, re.M)) == 10
    for term in ('implementation admission refused', 'reserved', 'R081', 'R083', 'R097',
                 'M death/restart', 'persistence', '5.34962656602147/120'):
        assert term in text, term
    entry = (ROOT / 'REQUEST_LOG.md').read_text().split('## R099 —', 1)[1]
    assert '@gmail.com' not in entry and '[REDACTED account email]' in entry
    for identity in ('01a0c5e5-2f01-70f3-bd2b-9ec5f2f475c8', '01a0c5ed-8489-76b3-8e06-eec8713e8261'):
        assert identity in entry
    for name in ('STATUS.md', 'PROJECT_TRACKS.md', 'docs/realizability/B2_NEXT_STEPS.md'):
        current = (ROOT / name).read_text()
        assert 'B2_MONITOR_TRUSTED_ADAPTER_CONTRACT.md' in current
        assert 'capability decision' in current and 'SESSION_HANDOFF.md#next-task' in current
    ast.parse(Path(__file__).read_text())
    git('diff', '--check')
    inputs = ['AGENTS.md', 'docs/workflow/SESSION_PROTOCOL.md', 'docs/workflow/TRACK_RULES.md',
              'EXPERIMENT.md', 'PHYSICAL_REALIZABILITY_PLAN.md', 'CONTROL_RESEARCH_ROADMAP.md',
              'docs/realizability/B2_MONITOR_R097_REVIEW.md',
              'docs/realizability/B2_MONITOR_R082_REVIEW.md',
              'docs/realizability/B2_MONITOR_LIVE_VALIDATION_CONTRACT.md',
              'docs/realizability/evidence/r097/contract.md']
    inputs += ['docs/realizability/evidence/r097/source/' + n
               for n in ('certificate.py', 'integration.py', 'primitives.py')]
    result = dict(status='passed', baseline_commit=BASE,
        preserved_baseline_files=len(baseline),
        preserved_historical_evidence_files=sum('/evidence/' in n for n in baseline),
        log_prefixes_preserved=True, unique_request_ids=99, lifecycle_pairs=1,
        local_links=links, fragments=fragments, root_and_handoff_words=words,
        field_map=field_map, event_rows=10, input_sha256={n: sha(ROOT / n) for n in inputs},
        contract_sha256=sha(CONTRACT), checker_sha256=sha(Path(__file__)),
        archived_code_executed=False, fixture_attempts=0,
        limitation='Structural/integrity checks; no proof of authority or OS capability.')
    (HERE / 'documentation_validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
