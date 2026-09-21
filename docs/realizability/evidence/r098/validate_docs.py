"""R098 integrity/documentation checks only; no archived imports or fixtures."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = '9ed35fca076d413916e2b0ab9bb4a041a9adcb02'
START = '83b19ba'
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
    assert len(requests) == len(set(requests)) == 98 and max(map(int, requests)) == 98
    session = (ROOT / 'WORK_SESSIONS.md').read_text().split('## R098 —', 1)[1]
    assert len(re.findall(r'^STARTED \|', session, re.M)) == 1
    assert len(re.findall(r'^COMPLETED \|', session, re.M)) == 1
    handoff = (ROOT / 'SESSION_HANDOFF.md').read_text()
    assert 'acceptance review' in handoff and 'GPT-6 Astra/high' in handoff
    words = sum(len((ROOT / n).read_text().split()) for n in ('AGENTS.md', 'SESSION_HANDOFF.md'))
    assert words < 2800
    paths = [ROOT / n for n in sorted(ALLOWED) if n.endswith('.md')]
    paths += [HERE / 'README.md', ROOT / 'docs/realizability/B2_MONITOR_R097_REVIEW.md']
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
    saved = read(HERE / 'saved_validation.json')
    assert saved['checker_sha256'] == sha(HERE / 'check_saved.py')
    for name, expected in saved['input_sha256'].items():
        assert sha(ROOT / name) == expected
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text())
    entry = (ROOT / 'REQUEST_LOG.md').read_text().split('## R098 —', 1)[1]
    assert '@gmail.com' not in entry and '[REDACTED account email]' in entry
    assert '01a0c5cf-3cc5-7bd2-bb4e-8c63df99efc8' in entry
    assert '01a0c5e5-2f01-70f3-bd2b-9ec5f2f475c8' in entry
    assert 'documentation-only' in handoff and 'No new execution allowance' in handoff
    for name in ('STATUS.md', 'PROJECT_TRACKS.md', 'docs/realizability/B2_NEXT_STEPS.md'):
        assert 'B2_MONITOR_R097_REVIEW.md' in (ROOT / name).read_text()
        assert 'SESSION_HANDOFF.md#next-task' in (ROOT / name).read_text()
    git('diff', '--check')
    result = dict(status='passed', baseline_commit=BASE,
        preserved_baseline_files=len(baseline),
        preserved_historical_evidence_files=sum('/evidence/' in n for n in baseline),
        log_prefixes_preserved=True, unique_request_ids=98, lifecycle_pairs=1,
        local_links=links, fragments=fragments, root_and_handoff_words=words,
        saved_review_inputs=len(saved['input_sha256']),
        checker_sha256=sha(Path(__file__)), archived_code_executed=False)
    (HERE / 'documentation_validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
