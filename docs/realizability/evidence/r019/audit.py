"""Standard-library audit of the R019 toy-only portability evidence."""
import hashlib
import json
import math
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
ROOT = Path.cwd().resolve()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    def reject(value):
        raise ValueError(f'Nonfinite JSON constant {value} in {path}')
    return json.loads(Path(path).read_text(), parse_constant=reject)


def finite(value):
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite(key) and finite(item) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return all(finite(item) for item in value)
    return True


preflight = read_json(HERE / 'preflight.json')
assert preflight['status'] == 'passed'
assert preflight['base_commit'] == 'bd4945bf68facaf1e016d4a1b64c389fdfa441d4'
production = {name: sha(ROOT / name) for name in preflight['source_sha256']}
assert production == preflight['source_sha256']
for name, expected in preflight['runner_sha256'].items():
    assert sha(HERE / name) == expected, name

report_path = HERE / 'toys/report.json'
report = read_json(report_path)
assert report['status'] == 'passed'
assert report['physical_meshes'] == report['matrix_solves'] == 0
assert report['elapsed_seconds'] < 60.0
assert set(report['watches']) == {'wrong_root', 'watchdog', 'kernels', 'wrapper', 'block-rhs', 'disk'}
normal = {name: watch for name, watch in report['watches'].items() if name != 'wrong_root'}
assert len(normal) == 5
assert all(w['returncode'] == 0 and w['stop_reason'] is None
           and w['parent_observed_peak_rss_mib'] < 512.0 for w in normal.values())
assert max(w['parent_observed_peak_rss_mib'] for w in report['watches'].values()) < 512.0
assert max(w['maximum_sample_gap_seconds'] for w in report['watches'].values()) < 0.1
wrong_watch = report['watches']['wrong_root']
assert wrong_watch['returncode'] != 0 and wrong_watch['stop_reason'] is None
wrong = read_json(HERE / 'toys/wrong-root/toy-repair-report.json')
assert wrong['status'] == 'partial_failed' and wrong['stage'] == 'imports'
assert all(wrong[key] == 0 for key in ('physical_meshes', 'pde_solves',
    'matrix_factorizations', 'primary_rhs', 'returned_primary_solves',
    'correction_rhs', 'matrix_solves'))
assert 'repository_root' in wrong and wrong['error']['type'] == 'FileNotFoundError'
for name, child_name in (('kernels', 'toy-report.json'),
                         ('wrapper', 'toy-repair-report.json'),
                         ('block-rhs', 'block-rhs-report.json'),
                         ('disk', 'extra-toys.json')):
    assert read_json(HERE / 'toys' / name / child_name)['status'] == 'passed'
watchdog = read_json(HERE / 'toys/watchdog/self-check.json')
assert watchdog['timeout']['stop_reason'] == 'wall_time_limit'
assert watchdog['memory']['stop_reason'] == 'rss_limit'
assert watchdog['memory']['largest_observed_process_tree'] >= 2

refusal = read_json(HERE / 'parent-refusal/report.json')
assert refusal['status'] == 'prerequisite_refused'
assert refusal['stage'] == 'toy_prerequisites' and refusal['child_launched'] is False
assert all(refusal[key] == 0 for key in ('physical_meshes', 'primary_rhs',
    'returned_primary_solves', 'correction_rhs', 'matrix_factorizations', 'matrix_solves'))
assert not (HERE / 'parent-refusal/launch.json').exists()

json_files = sorted(HERE.rglob('*.json'))
for path in json_files:
    assert finite(read_json(path)), path

markdown = [
    'REQUEST_LOG.md', 'SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md',
    'docs/realizability/B2_NEXT_STEPS.md',
    'docs/realizability/B2_MATCHED_TRACE_PREFLIGHT_RESULT.md',
    'docs/realizability/B2_MATCHED_TRACE_PREFLIGHT_EVIDENCE.md',
    'docs/realizability/B2_TOY_PORTABILITY_RESULT.md',
    'docs/realizability/B2_TOY_PORTABILITY_EVIDENCE.md',
]
local_links = fenced_blocks = 0
for name in markdown:
    source = ROOT / name
    body = source.read_text()
    fence_count = sum(line.lstrip().startswith('```') for line in body.splitlines())
    assert fence_count % 2 == 0, name
    fenced_blocks += fence_count // 2
    for destination in re.findall(r'\[[^\]]*\]\(([^)]+)\)', body):
        if destination.startswith(('http://', 'https://', 'mailto:')):
            continue
        local_links += 1
        path, separator, anchor = destination.partition('#')
        target = (source.parent / path).resolve() if path else source
        assert target.exists(), (name, destination)
        if separator:
            headings = [re.sub(r'[^a-z0-9 _-]', '', line.lstrip('#').strip().lower())
                        .replace(' ', '-') for line in target.read_text().splitlines()
                        if line.startswith('#')]
            assert anchor in headings, (name, destination)

attempt_elapsed = []
for path in sorted((HERE / 'attempts').glob('*/parent-report.json')):
    attempt_elapsed.append(read_json(path)['elapsed_seconds'])
total_all_attempts = math.fsum([report['elapsed_seconds'], *attempt_elapsed])
assert total_all_attempts < 60.0, total_all_attempts

archive_files = {str(path.relative_to(HERE)): sha(path)
                 for path in sorted(HERE.rglob('*')) if path.is_file()
                 and path.name not in ('archive_manifest.json', 'validation.json')}
archive_manifest = dict(status='passed', base_commit=preflight['base_commit'],
                        files_sha256=archive_files)
(HERE / 'archive_manifest.json').write_text(json.dumps(archive_manifest,
    indent=2, allow_nan=False) + '\n')
for name, digest in archive_files.items():
    assert sha(HERE / name) == digest, name
json_files = sorted(HERE.rglob('*.json'))
for path in json_files:
    assert finite(read_json(path)), path

validation = dict(
    status='passed', scope='R019 toy portability and refusal reporting; no physical child',
    base_commit=preflight['base_commit'], production_sources_verified=len(production),
    archived_runner_sources_verified=len(preflight['runner_sha256']),
    five_prerequisite_phases='passed', wrong_root='finite early refusal with zero physical counts',
    parent_refusal='passed; no physical child launch record',
    complete_parent_monitored_seconds=report['elapsed_seconds'],
    all_attempts_parent_monitored_seconds=total_all_attempts,
    peak_observed_child_tree_rss_mib=max(
        [w['parent_observed_peak_rss_mib'] for w in report['watches'].values()]),
    maximum_sample_gap_seconds=max(
        [w['maximum_sample_gap_seconds'] for w in report['watches'].values()]),
    physical_meshes=0, pde_solves=0, matrix_factorizations=0, matrix_solves=0,
    archived_json_files=len(json_files), finite_json_files=len(json_files),
    markdown_files=len(markdown), local_links_and_anchors=local_links,
    fenced_blocks=fenced_blocks,
    production_sha256=production,
    runner_sha256={name: sha(HERE / name) for name in preflight['runner_sha256']},
    evidence_sha256={str(path.relative_to(HERE)): sha(path)
                     for path in sorted(HERE.rglob('*')) if path.is_file()
                     and path.name != 'validation.json'},
)
(HERE / 'validation.json').write_text(json.dumps(validation, indent=2,
    allow_nan=False) + '\n')
print(json.dumps({key: validation[key] for key in (
    'status', 'production_sources_verified', 'five_prerequisite_phases',
    'complete_parent_monitored_seconds', 'all_attempts_parent_monitored_seconds',
    'peak_observed_child_tree_rss_mib', 'maximum_sample_gap_seconds',
    'physical_meshes', 'matrix_solves', 'archived_json_files',
    'local_links_and_anchors')}, indent=2))
