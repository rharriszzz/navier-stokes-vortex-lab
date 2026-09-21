"""R097 integrity/documentation checks only; no archived imports or fixtures."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = 'dc73ec008460e2200a6b475bb36d846ca018cb7a'
START = '57b90a1'
ALLOWED = {'REQUEST_LOG.md', 'WORK_SESSIONS.md', 'SESSION_HANDOFF.md', 'STATUS.md',
           'PROJECT_TRACKS.md', 'docs/realizability/B2_NEXT_STEPS.md'}


def git(*args, input=None):
    return subprocess.check_output(['git', *args], cwd=ROOT, input=input)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    def invalid(value):
        raise ValueError(value)
    return json.loads(path.read_text(), parse_constant=invalid)


def headings(path):
    slugs = set()
    for line in path.read_text().splitlines():
        if re.match(r'^#{1,6} ', line):
            value = re.sub(r'^#+\s+', '', line).strip().lower()
            value = re.sub(r'[^\w\-\s]', '', value)
            slugs.add(re.sub(r'\s', '-', value))
    return slugs


def main():
    baseline = {}
    for row in git('ls-tree', '-r', BASE).decode().splitlines():
        fields, name = row.split('\t', 1)
        if name not in ALLOWED:
            baseline[name] = fields.split()[2]
    actual = git('hash-object', '--stdin-paths',
                 input=('\n'.join(baseline) + '\n').encode()).decode().splitlines()
    assert actual == list(baseline.values()), 'baseline file changed outside scoped docs'
    for name in ('REQUEST_LOG.md', 'WORK_SESSIONS.md'):
        for commit in (BASE, START):
            assert (ROOT / name).read_bytes().startswith(git('show', f'{commit}:{name}'))
    requests = re.findall(r'^## R(\d+)\b', (ROOT / 'REQUEST_LOG.md').read_text(), re.M)
    assert len(requests) == len(set(requests)) == 97 and max(map(int, requests)) == 97
    session = (ROOT / 'WORK_SESSIONS.md').read_text().split('## R097 —', 1)[1]
    assert len(re.findall(r'^STARTED \|', session, re.M)) == 1
    assert len(re.findall(r'^COMPLETED \|', session, re.M)) == 1
    handoff = (ROOT / 'SESSION_HANDOFF.md').read_text()
    assert 'acceptance review' in handoff and 'GPT-6 Astra/high' in handoff
    words = sum(len((ROOT / n).read_text().split()) for n in ('AGENTS.md', 'SESSION_HANDOFF.md'))
    assert words < 2800
    paths = [ROOT / n for n in sorted(ALLOWED) if n.endswith('.md')]
    paths += [HERE / 'contract.md', HERE / 'README.md']
    links = fragments = 0
    for path in paths:
        for raw in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            if re.match(r'^[a-zA-Z]+:', raw):
                continue
            target, _, fragment = unquote(raw).partition('#')
            dest = (path.parent / target).resolve() if target else path
            # This output is created only after every check succeeds below.
            assert dest == HERE / 'documentation_validation.json' or dest.exists(), (path, raw)
            links += 1
            if fragment:
                assert fragment in headings(dest), (path, raw, 'missing heading')
                fragments += 1
    receipt = read(HERE / 'attempt_01/receipt.json')
    inventory = read(HERE / 'attempt_01/snapshot/inventory.json')
    for name, value in inventory['files'].items():
        assert sha(HERE / 'attempt_01/snapshot' / name) == value
        if name not in ('handoff.md',):
            assert sha(ROOT / inventory['origins'][name]) == value
    for name, value in receipt['output_sha256'].items():
        assert sha(HERE / 'attempt_01' / name) == value
    bound=read(HERE/'attempt_01/bound.json')
    assert bound['inventory_sha256']==sha(HERE/'attempt_01/snapshot/inventory.json')
    assert bound['started_sha256']==sha(HERE/'attempt_01/started.json')
    fixtures=read(HERE/'attempt_01/output/fixtures.json')
    progress=read(HERE/'attempt_01/output/progress.json')
    tree=ast.parse((HERE/'source/validate.py').read_text())
    names={n.name for n in tree.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
    registered=progress['registered']
    assert len(names)==len(registered)==len(set(registered))==9 and names==set(registered)
    assert fixtures['checks']==progress['checks']
    assert [c['name'] for c in progress['checks']]==registered
    assert all(c['status']=='passed' for c in progress['checks'])
    assert progress['state']=='COMPLETED' and progress['status']=='passed'
    ledger=read(HERE/'ledger.json')
    assert len(ledger['attempts'])==1 and ledger['attempts'][0]['receipt_sha256']==sha(HERE/'attempt_01/receipt.json')
    assert ledger['total_charged_seconds']==receipt['charged_seconds']==receipt['observed_guard_seconds']+5
    assert ledger['attempts'][0]['charged_seconds']==receipt['charged_seconds']<120
    assert receipt['status']=='passed' and receipt['whole_recorder_certified'] is False
    assert receipt['child_lifetime_peak_rss_bytes']<=256<<20
    assert receipt['returncode']==0 and not receipt['timed_out']
    py_files = list(HERE.rglob('*.py'))
    for path in py_files:
        ast.parse(path.read_text())
    json_files = [p for p in HERE.rglob('*.json') if p.name != 'documentation_validation.json']
    for path in json_files:
        read(path)
    git('diff', '--check')
    result = dict(status='passed', baseline_commit=BASE,
        preserved_baseline_files=len(baseline),
        preserved_historical_evidence_files=sum('/evidence/' in n for n in baseline),
        log_prefixes_preserved=True, unique_request_ids=97, lifecycle_pairs=1,
        local_links=links, fragments=fragments, root_and_handoff_words=words,
        fixture_source_input_bindings=len(inventory['files']),
        fixture_output_bindings=len(receipt['output_sha256']), fixture_groups=9,
        python_syntax_files=len(py_files), finite_json_files=len(json_files),
        checker_sha256=sha(Path(__file__)), archived_mains_executed=False)
    (HERE / 'documentation_validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
