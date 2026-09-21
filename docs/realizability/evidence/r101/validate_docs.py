"""R101 documentation integrity only. No archived imports or behavioral runs."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = 'c2d700d68705f6ad65c5b87f71f5cf550e4b41bb'
START = '4b6c4db'
ALLOWED = {'REQUEST_LOG.md', 'WORK_SESSIONS.md', 'SESSION_HANDOFF.md', 'STATUS.md',
           'PROJECT_TRACKS.md', 'docs/realizability/B2_NEXT_STEPS.md'}
CONTRACT = ROOT / 'docs/realizability/B2_MONITOR_MANAGER_CAPABILITY_DECISION.md'


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
    assert len(requests) == len(set(requests)) == 101 and set(map(int, requests)) == set(range(1, 102))
    session = (ROOT / 'WORK_SESSIONS.md').read_text().split('## R101 —', 1)[1]
    assert len(re.findall(r'^STARTED \|', session, re.M)) == 1
    assert len(re.findall(r'^COMPLETED \|', session, re.M)) == 1
    handoff = (ROOT / 'SESSION_HANDOFF.md').read_text()
    assert 'GPT-6 Astra/high' in handoff and 'documentation-only' in handoff
    assert 'user policy selection' in handoff and 'No new execution allowance' in handoff
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
    for term in ('Unsupported under the unchanged R099 contract', 'E0', 'E1', 'E8',
                 '5.34962656602147/120', 'No policy change is selected', 'CLOCK_MONOTONIC',
                 'CLONE_PIDFD', 'journalctl --sync', 'outside-unit', 'policy selection A/B/C'):
        assert term.lower() in text.lower(), term
    sources = json.loads((HERE / 'sources.json').read_text())
    assert len(sources['sources']) == 16
    assert len({v['id'] for v in sources['sources']}) == 16
    for source in sources['sources']:
        assert source['url'] in text, source['id']
    entry = (ROOT / 'REQUEST_LOG.md').read_text().split('## R101 —', 1)[1]
    assert '@gmail.com' not in entry and '[REDACTED account email]' in entry
    for token in ('01a0c5ed-8489-76b3-8e06-eec8713e8261',
                  '01a0c5f7-badb-7ef1-bbd1-85d1e0a2ee35', '187,363', '172,592',
                  '1,322,368', '14,771', '1,019', '7m 46s', '5:52 PM',
                  '98%', '17:37 on 28 Sep', '283 credits', '100%', '17:55 on 28 Sep'):
        assert token in entry, token
    for name in ('STATUS.md', 'PROJECT_TRACKS.md', 'docs/realizability/B2_NEXT_STEPS.md'):
        current = (ROOT / name).read_text()
        assert 'B2_MONITOR_MANAGER_CAPABILITY_DECISION.md' in current
        assert 'policy selection A/B/C' in current and 'SESSION_HANDOFF.md#next-task' in current
    ast.parse(Path(__file__).read_text())
    git('diff', '--check')
    inputs = ['AGENTS.md', 'docs/workflow/SESSION_PROTOCOL.md', 'docs/workflow/TRACK_RULES.md',
              'EXPERIMENT.md', 'PHYSICAL_REALIZABILITY_PLAN.md', 'CONTROL_RESEARCH_ROADMAP.md',
              'docs/realizability/B2_MONITOR_R097_REVIEW.md',
              'docs/realizability/B2_MONITOR_TRUSTED_ADAPTER_CONTRACT.md',
              'docs/realizability/B2_MONITOR_R082_REVIEW.md',
              'docs/realizability/B2_MONITOR_LIVE_VALIDATION_CONTRACT.md',
              'docs/realizability/evidence/r097/contract.md']
    inputs += ['docs/realizability/evidence/r097/source/' + n
               for n in ('certificate.py', 'integration.py', 'primitives.py')]
    result = dict(status='passed', baseline_commit=BASE,
        preserved_baseline_files=len(baseline),
        preserved_historical_evidence_files=sum('/evidence/' in n for n in baseline),
        log_prefixes_preserved=True, unique_request_ids=101, lifecycle_pairs=1,
        local_links=links, fragments=fragments, root_and_handoff_words=words,
        official_sources=16, input_sha256={n: sha(ROOT / n) for n in inputs},
        decision_sha256=sha(CONTRACT), sources_index_sha256=sha(HERE / 'sources.json'), checker_sha256=sha(Path(__file__)),
        archived_code_executed=False, fixture_attempts=0,
        limitation='Structural/integrity checks; no proof of authority or OS capability.')
    (HERE / 'documentation_validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
