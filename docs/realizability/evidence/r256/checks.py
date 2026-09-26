"""Static completion checks for R256 documentation and source records."""
import ast
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from docs.realizability.evidence.r256.audit import ADDED, MODIFIED

MARKDOWN = [
    'SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md', 'EXPERIMENT.md',
    'PHYSICAL_REALIZABILITY_PLAN.md', 'CONTROL_RESEARCH_ROADMAP.md',
    'docs/realizability/B1_SETUP.md',
    'docs/realizability/MANUFACTURED_INTEGRATION_R256.md',
    'verification/nonlinear_port/README.md',
]


def run():
    sources = sorted(name for name in MODIFIED | ADDED if name.endswith('.py'))
    sources += [str(path.relative_to(ROOT)) for path in
                (HERE/'test_runner.py', HERE/'audit.py', HERE/'checks.py')]
    for name in sources:
        ast.parse((ROOT/name).read_text(encoding='utf-8'), filename=name)
    json_files = [ROOT/'verification/nonlinear_port/future_manufactured.json',
                  HERE/'tests.json', HERE/'audit.json']
    for path in json_files:
        json.loads(path.read_text(encoding='utf-8'))
    links = 0
    for name in MARKDOWN:
        path = ROOT/name
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            target = target.split('#', 1)[0]
            if not target or '://' in target or target.startswith('mailto:'):
                continue
            assert (path.parent/target).exists(), (name, target)
            links += 1
    log = (ROOT/'REQUEST_LOG.md').read_text(encoding='utf-8')
    ids = [int(value) for value in re.findall(r'^## R(\d+)\b', log, re.M)]
    assert len(ids) == len(set(ids)) == 256 and set(ids) == set(range(1, 257))
    sessions = (ROOT/'WORK_SESSIONS.md').read_text(encoding='utf-8')
    assert sessions.count('STARTED | 2026-09-26T23:18:41Z | R256') == 1
    assert sessions.count('COMPLETED |') >= 1
    assert (ROOT/'SESSION_HANDOFF.md').read_text().count('## Next task\n') == 1
    assert (HERE/'tests.json').is_file() and (HERE/'audit.json').is_file()
    return dict(status='SOURCE_IMPLEMENTED_NO_ADMISSION',
        ast_files=len(sources), json_files=len(json_files),
        local_link_targets_checked=links, unique_contiguous_request_ids=len(ids),
        r256_started_once=True,
        r256_completed_once=sessions.count(' | R256 | PC/WSL daisy | released: no') == 2,
        numerical_modules_loaded=sorted(name for name in
            ('numpy','dolfinx','basix','ufl','ffcx','petsc4py','mpi4py','scipy')
            if name in sys.modules),
        next_task='Astra/high reviews R256 source and publishes separate admission/caller or blocker; stop before launch.')


if __name__ == '__main__':
    result = run()
    (HERE/'checks.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
