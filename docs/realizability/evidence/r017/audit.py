"""Audit stored R017 toy evidence with the standard library; no FEM execution."""
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
R016 = ROOT / 'docs/realizability/evidence/r016'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    value = json.loads(path.read_text())
    finite(value)
    return value


def finite(value):
    if isinstance(value, float):
        assert math.isfinite(value)
    elif isinstance(value, dict):
        for item in value.values():
            finite(item)
    elif isinstance(value, list):
        for item in value:
            finite(item)


def main():
    archive_path = EVIDENCE / 'r017_archive_manifest.json'
    if archive_path.exists():
        archived = read(archive_path)
        for name, digest in archived.items():
            assert sha(EVIDENCE / name) == digest, name
    preflight = read(EVIDENCE / 'preflight.json')
    assert preflight['base_commit'] == 'a22fc32f86c957a32e187d090bcd2eb6117db4ad'
    r016_preflight = read(R016 / 'preflight.json')
    assert preflight['source_sha256_from_r016_preflight'] is True
    source_hashes = r016_preflight['source_sha256']
    for name, digest in source_hashes.items():
        assert sha(ROOT / name) == digest, name
    for name, digest in preflight['runner_sha256'].items():
        assert sha(EVIDENCE / name) == digest, name
    assert sha(EVIDENCE / 'physical.py') != sha(R016 / 'physical.py')
    assert sha(EVIDENCE / 'wrapper_toys.py') != sha(R016 / 'wrapper_toys.py')

    # Keep only the three unmodified support sources needed by the R017 copy.
    copied = 0
    for name in ('disk.py', 'kernels.py', 'toy_runner.py'):
        assert (EVIDENCE / name).read_bytes() == (R016 / name).read_bytes(), name
        copied += 1
    r016_validation = read(R016 / 'stored_validation.json')
    assert r016_validation['status'] == 'passed'
    old_log = subprocess.check_output(['git', 'show', preflight['base_commit'] + ':REQUEST_LOG.md'],
                                     cwd=ROOT)
    request_log = ROOT / 'REQUEST_LOG.md'
    assert request_log.read_bytes().startswith(old_log)
    assert request_log.read_text().count('## R017 —') == 1

    markdown_files = [ROOT / name for name in (
        'REQUEST_LOG.md', 'SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md',
        'docs/realizability/B2_NEXT_STEPS.md',
        'docs/realizability/B2_MATCHED_TRACE_LIFTING_RESULT.md',
        'docs/realizability/B2_MATCHED_TRACE_LIFTING_EVIDENCE.md',
        'docs/realizability/B2_BLOCK_RHS_TOY_REPAIR_RESULT.md',
        'docs/realizability/B2_BLOCK_RHS_TOY_REPAIR_EVIDENCE.md')]
    link_count = fence_count = 0
    for source in markdown_files:
        body = source.read_text()
        fences = sum(line.lstrip().startswith('```') for line in body.splitlines())
        assert fences % 2 == 0, source
        fence_count += fences // 2
        for destination in re.findall(r'\[[^\]]*\]\(([^)]+)\)', body):
            if destination.startswith(('http://', 'https://', 'mailto:')):
                continue
            link_count += 1
            path, separator, anchor = destination.partition('#')
            target = (source.parent / path).resolve() if path else source
            if target == archive_path and not target.exists():
                continue
            assert target.exists(), (source, destination)
            if separator:
                headings = [re.sub(r'\s', '-', re.sub(r'[^a-z0-9 _-]', '',
                    line.lstrip('#').strip().lower())).strip('-')
                    for line in target.read_text().splitlines() if line.startswith('#')]
                assert anchor in headings, (source, destination)

    cumulative = []
    peaks = []
    attempt_reports = []
    for number in range(1, 8):
        attempt = EVIDENCE / 'toy-runs' / f'attempt-{number:02d}'
        report_path = (attempt / 'execution/report.json' if number <= 4 else attempt / 'report.json')
        report = read(report_path)
        elapsed = float(report['elapsed_seconds'])
        cumulative.append(elapsed)
        assert elapsed < preflight['toy_budget']['cumulative_wall_seconds']
        for phase in report['phases']:
            watch = phase['watch']
            peaks.append(float(watch['parent_observed_peak_rss_mib']))
        attempt_reports.append(report)
    final = attempt_reports[-1]
    assert final['status'] == 'passed'
    assert final['elapsed_seconds'] < 60.0
    assert cumulative == sorted(cumulative)
    assert max(peaks) < preflight['toy_budget']['process_tree_peak_rss_mib']
    assert max(report['physical_meshes'] for report in attempt_reports) == 0
    assert max(report['pde_solves'] for report in attempt_reports) == 0
    assert max(report['matrix_factorizations'] for report in attempt_reports) == 0
    assert max(report['matrix_solves'] for report in attempt_reports) == 0

    wrapper = read(EVIDENCE / 'toy-runs/attempt-07/wrapper/toy-repair-report.json')
    assert wrapper['status'] == 'passed'
    assert wrapper['tetrahedron']['constrained_dofs_per_block'] == [24, 0, 24, 0]
    assert wrapper['pressure_compatibility_fixtures'] == dict(
        compatible_accepted=True, incompatible_refused=True,
        compatible_removed_norm=0.0, incompatible_removed_norm=1.0)
    assert all(wrapper['failure_reporting'].values())

    toy = read(EVIDENCE / 'toy-runs/attempt-07/block-rhs/block-rhs-report.json')
    assert toy['status'] == 'passed'
    metadata = toy['vector_metadata']
    assert metadata['observed_metadata_loss'] is True
    assert metadata['reference']['blocks'] is not None
    assert metadata['copied']['blocks'] is metadata['duplicated']['blocks'] is None
    operator = toy['operator']
    assert operator['unchanged'] is True and operator['state_before'] == operator['state_after']
    assert all(value > 0 for value in operator['required_coupling_frobenius_norms'].values())
    zero, nonzero = toy['cases']
    assert zero['target'] == [0.0, 0.0] and zero['zero_target_free_entries_unchanged']
    assert nonzero['target'] == [0.125, -0.375]
    assert nonzero['max_oracle_error'] <= nonzero['arithmetic_tolerance']
    assert nonzero['exact_essential_values'] and nonzero['pressure_row_lifting_nontrivial']
    for name in ('wrong_offset_refusal', 'missing_layout_refusal', 'synthetic_lifting_failure'):
        refusal = toy[name]
        assert refusal['refused'] and refusal['matrix_solves'] == 0
        assert refusal['stage'] in ('rhs_layout_validation', 'rhs_lifting')
        assert refusal['rhs_layout'] if name != 'synthetic_lifting_failure' else refusal['layout_present']

    archived_files = sum(1 for path in EVIDENCE.rglob('*')
                         if path.is_file() and path.name not in ('r017_archive_manifest.json', 'validation.json')) + 1
    for path in EVIDENCE.rglob('*.py'):
        compile(path.read_text(), str(path), 'exec')
    result = dict(status='passed', archive_files=archived_files,
        r016_copy_file_count=copied,
        markdown_files=len(markdown_files), local_links_and_anchors=link_count,
        fenced_blocks=fence_count,
        production_source_identities=len(source_hashes), attempt_wall_cumulative_seconds=cumulative,
        total_toy_seconds=final['elapsed_seconds'], peak_child_tree_rss_mib=max(peaks),
        metadata_loss_reproduced=True, rhs_cases=2, matrix_unchanged=True,
        required_couplings=len(operator['required_coupling_frobenius_norms']),
        pressure_compatibility_fixtures=2, physical_meshes=0, pde_solves=0,
        matrix_factorizations=0, matrix_solves=0)
    validation_path = EVIDENCE / 'validation.json'
    validation_path.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    manifest = {path.relative_to(EVIDENCE).as_posix(): sha(path)
                for path in sorted(EVIDENCE.rglob('*'))
                if path.is_file() and path != archive_path}
    archive_path.write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
