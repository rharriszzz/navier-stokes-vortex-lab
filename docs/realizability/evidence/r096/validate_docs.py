"""R096 integrity/documentation checks only; no archived imports or fixtures."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = 'aeb7de5b48f142b387cf212b39f31d23204dfacf'
START = 'a10d4a5'
ALLOWED = {'REQUEST_LOG.md', 'WORK_SESSIONS.md', 'SESSION_HANDOFF.md', 'STATUS.md',
           'PROJECT_TRACKS.md', 'docs/realizability/B2_NEXT_STEPS.md',
           'docs/realizability/B2_MONITOR_ADAPTER_REVIEW.md',
           'docs/realizability/B2_MONITOR_LIVE_VALIDATION_CONTRACT.md'}


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
    assert len(requests) == len(set(requests)) == 96 and max(map(int, requests)) == 96
    session = (ROOT / 'WORK_SESSIONS.md').read_text().split('## R096 —', 1)[1]
    assert len(re.findall(r'^STARTED \|', session, re.M)) == 1
    assert len(re.findall(r'^COMPLETED \|', session, re.M)) == 1
    handoff = (ROOT / 'SESSION_HANDOFF.md').read_text()
    assert 'J01–J04 completion-certificate repair' in handoff and 'GPT-6 Astra/high' in handoff
    words = sum(len((ROOT / n).read_text().split()) for n in ('AGENTS.md', 'SESSION_HANDOFF.md'))
    assert words < 2800
    paths = [ROOT / n for n in sorted(ALLOWED) if n.endswith('.md')]
    paths += [ROOT / 'docs/realizability/B2_MONITOR_R088_REVIEW.md', HERE / 'README.md']
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
    started = read(HERE / 'attempt_01/started.json')
    receipt = read(HERE / 'attempt_01/receipt.json')
    for name, value in started['source_input_sha256'].items():
        assert sha(HERE.parent / name) == value
    for name, value in receipt['output_sha256'].items():
        assert sha(HERE / 'attempt_01' / name) == value
    review = read(HERE / 'attempt_01/review.json')
    assert len(review['checks']) == 9 and receipt['status'] == 'passed'
    assert receipt['charged_seconds'] < 20 and receipt['whole_recorder_certified'] is False
    py_files = list(HERE.glob('*.py'))
    for path in py_files:
        ast.parse(path.read_text())
    json_files = [p for p in HERE.rglob('*.json') if p.name != 'documentation_validation.json']
    for path in json_files:
        read(path)
    git('diff', '--check')
    result = dict(status='passed', baseline_commit=BASE,
        preserved_baseline_files=len(baseline),
        preserved_historical_evidence_files=sum('/evidence/' in n for n in baseline),
        log_prefixes_preserved=True, unique_request_ids=96, lifecycle_pairs=1,
        local_links=links, fragments=fragments, root_and_handoff_words=words,
        audit_source_input_bindings=len(started['source_input_sha256']),
        audit_output_bindings=len(receipt['output_sha256']), audit_observations=9,
        python_syntax_files=len(py_files), finite_json_files=len(json_files),
        checker_sha256=sha(Path(__file__)), archived_mains_executed=False)
    (HERE / 'documentation_validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
