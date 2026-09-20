"""Validate R016 documentation and immutable request history; no FEM work."""
import ast
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
FILES = [
    'REQUEST_LOG.md', 'SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md',
    *['docs/realizability/' + name + '.md' for name in (
        'B2_GATE', 'B2_MATCHED_TRACE_RESULT', 'B2_MATCHED_TRACE_REVIEW',
        'B2_MATCHED_TRACE_RUN_EVIDENCE', 'B2_MATCHED_TRACE_WRAPPER_REPAIR',
        'B2_NEXT_STEPS', 'B2_PHYSICAL_RESPONSE_AUDIT',
        'B2_MATCHED_TRACE_LIFTING_RESULT', 'B2_MATCHED_TRACE_LIFTING_EVIDENCE')],
]


def main():
    errors, links, fences = [], 0, 0
    report_path = EVIDENCE / 'documentation_validation.json'
    for name in FILES:
        source = ROOT / name
        body = source.read_text()
        count = sum(line.lstrip().startswith('```') for line in body.splitlines())
        assert count % 2 == 0, name
        fences += count // 2
        for destination in re.findall(r'\[[^\]]*\]\(([^)]+)\)', body):
            if destination.startswith(('http://', 'https://', 'mailto:')):
                continue
            links += 1
            path, separator, anchor = destination.partition('#')
            target = (source.parent / path).resolve() if path else source
            # This check produces its linked report after successful validation.
            if target == report_path and not separator:
                continue
            if not target.exists():
                errors.append(f'{name}: missing target {destination}')
                continue
            if separator:
                headings = [re.sub(r'\s', '-', re.sub(r'[^a-z0-9 _-]', '',
                    line.lstrip('#').strip().lower())).strip('-')
                    for line in target.read_text().splitlines() if line.startswith('#')]
                if anchor not in headings:
                    errors.append(f'{name}: missing anchor {destination}')
    assert not errors, '\n'.join(errors)
    preflight = json.loads((EVIDENCE / 'preflight.json').read_text())
    old_log = subprocess.check_output(
        ['git', 'show', preflight['base_commit'] + ':REQUEST_LOG.md'], cwd=ROOT)
    assert (ROOT / 'REQUEST_LOG.md').read_bytes().startswith(old_log)
    assert (ROOT / 'REQUEST_LOG.md').read_text().count('## R016 —') == 1
    python_files = list(EVIDENCE.rglob('*.py'))
    for path in python_files:
        ast.parse(path.read_text())
    result = dict(status='passed', markdown_files=len(FILES), local_links_and_anchors=links,
                  fenced_blocks=fences, python_sources_parsed=len(python_files),
                  prior_request_history_preserved=True, R016_recorded_once=True)
    report_path.write_text(json.dumps(result, indent=2)+'\n')
    assert report_path.is_file()
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
