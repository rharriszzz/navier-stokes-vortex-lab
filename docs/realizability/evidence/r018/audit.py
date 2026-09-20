"""Audit saved R018 refusal, source identities and documentation; no FEM work."""
import ast
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite(value):
    if isinstance(value, float):
        assert math.isfinite(value)
    elif isinstance(value, dict):
        for item in value.values():
            finite(item)
    elif isinstance(value, list):
        for item in value:
            finite(item)


def read(path):
    def reject(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    result = json.loads(path.read_text(), parse_constant=reject)
    finite(result)
    return result


def main():
    manifest = read(HERE / 'archive_manifest.json')
    assert len(manifest) == 29
    for name, item in manifest.items():
        assert sha(HERE / name) == item['archived_sha256'], name
        assert item['archived_sha256'] == item['original_sha256'], name
        original = Path(item['original_path'])
        if original.exists():
            assert sha(original) == item['original_sha256'], name
    preflight = read(HERE / 'preflight.json')
    assert preflight['status'] == 'passed'
    assert len(preflight['source_sha256']) == 19
    for name, digest in preflight['source_sha256'].items():
        assert sha(ROOT / name) == digest, name
    assert len(preflight['historical_file_sha256']) == 266
    for name, digest in preflight['historical_file_sha256'].items():
        assert sha(ROOT / name) == digest, name
    for name, digest in preflight['runner_sha256'].items():
        assert sha(HERE / name) == digest, name
        if name != 'run_contract.py':
            assert (HERE / name).read_bytes() == (HERE.parent / 'r017' / name).read_bytes()
    for name in ('reaudit-r016-stored_validation.json', 'reaudit-r017-validation.json'):
        assert read(HERE / name)['status'] == 'passed'
    old = read(HERE.parent / 'r016/physical/report.json')
    assert old['outputs']['P']['primary']['gain'] == [-1.6734724052233703, -1.0983702805959774]
    assert old['P_polar_reproduction_passed']
    assert old['outputs']['P']['comparison']['magnitude_passed'] is False
    assert old['outputs']['P']['comparison']['phase_passed'] is False

    toy = read(HERE / 'toys/report.json')
    assert toy['status'] == 'prerequisite_refused' and toy['failed_phase'] == 'wrapper'
    assert list(toy['watches']) == ['watchdog', 'kernels', 'wrapper']
    watches = list(toy['watches'].values())
    assert [w['returncode'] for w in watches] == [0, 0, 1]
    assert all(w['stop_reason'] is None for w in watches)
    assert math.fsum(w['elapsed_seconds'] for w in watches) <= toy['elapsed_seconds'] < 60
    peak = max(w['parent_observed_peak_rss_mib'] for w in watches)
    assert peak < 512
    assert toy['physical_meshes'] == toy['matrix_solves'] == 0
    watchdog = read(HERE / 'toys/watchdog/self-check.json')
    assert watchdog['timeout']['stop_reason'] == 'wall_time_limit'
    assert watchdog['memory']['stop_reason'] == 'rss_limit'
    assert watchdog['memory']['largest_observed_process_tree'] >= 2
    assert all(watchdog[key]['maximum_sample_gap_seconds'] <= .1 for key in ('timeout', 'memory'))
    kernel = read(HERE / 'toys/kernels/toy-report.json')
    assert kernel['status'] == 'passed'
    assert kernel['source_sha256'] == preflight['source_sha256']
    assert kernel['runner_sha256'] == sha(HERE / 'toy_runner.py')
    assert kernel['kernels_sha256'] == sha(HERE / 'kernels.py')
    assert {tuple(row['permutation']) for row in kernel['load_toys']} == set(itertools.permutations(range(4)))
    for row in kernel['load_toys']:
        assert row['load_error'] <= 256 * math.ulp(1.0) * row['load_absolute_scale']
    for row in kernel['disk_toys']:
        if 'tolerance' in row:
            assert row['error'] <= row['tolerance']
            assert row['independent_difference'] <= row['tolerance']
    assert kernel['physical_meshes'] == kernel['matrix_solves'] == 0
    error = (HERE / 'toys/wrapper.stderr').read_text()
    assert 'wrapper_toys.py", line 22' in error
    assert 'parents[4]' in error and error.endswith('IndexError: 4\n')
    assert not (HERE / 'toys/wrapper/toy-repair-report.json').exists()
    assert not (HERE / 'physical').exists()
    assert not (HERE / 'toys/block-rhs').exists()
    assert not (HERE / 'toys/disk').exists()
    stopped = read(HERE / 'poststop_review.json')
    assert stopped['status'] == 'stopped_before_physical_execution'
    assert stopped['toy_total_seconds'] == toy['elapsed_seconds']
    assert stopped['toy_peak_child_tree_rss_mib'] == peak
    for key in ('physical_attempts', 'physical_meshes', 'pde_solves', 'primary_rhs',
                'correction_rhs', 'matrix_solves', 'factorizations'):
        assert stopped[key] == 0
    assert stopped['child_report_present'] is stopped['retry_after_stop'] is False
    assert stopped['campaign_ready'] is stopped['physical_gate_passed'] is False
    original_root = Path(manifest['physical.py']['original_path']).parent
    if original_root.exists():
        assert not (original_root / 'physical').exists()

    # Check the reported failure location and report boundary without executing toys.
    wrapper = (HERE / 'wrapper_toys.py').read_text()
    assert 'parents[4]' in wrapper.splitlines()[21]
    assert wrapper.index('parents[4]') < wrapper.index("record = dict(status='partial'")
    parent = (HERE / 'run_contract.py').read_text()
    physical_node = next(node for node in ast.parse(parent).body
                         if isinstance(node, ast.FunctionDef) and node.name == 'physical')
    physical_source = ast.get_source_segment(parent, physical_node)
    assert physical_source.index("toy['status'] == 'passed'") < physical_source.index('output.mkdir')
    assert physical_source.index('output.mkdir(exist_ok=False)') < physical_source.index('support.monitor')
    syntax_count = 0
    for path in HERE.rglob('*.py'):
        ast.parse(path.read_text())
        syntax_count += 1
    json_count = 0
    for path in HERE.rglob('*.json'):
        if path.name != 'validation.json':
            read(path)
            json_count += 1

    old_log = subprocess.check_output(['git', 'show', preflight['base_commit'] + ':REQUEST_LOG.md'], cwd=ROOT)
    assert (ROOT / 'REQUEST_LOG.md').read_bytes().startswith(old_log)
    assert (ROOT / 'REQUEST_LOG.md').read_text().count('## R018 —') == 1
    markdown = ['REQUEST_LOG.md', 'SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md',
        'docs/realizability/B2_NEXT_STEPS.md', 'docs/realizability/B2_MATCHED_TRACE_REVIEW.md',
        'docs/realizability/B2_BLOCK_RHS_TOY_REPAIR_RESULT.md',
        'docs/realizability/B2_MATCHED_TRACE_PREFLIGHT_RESULT.md',
        'docs/realizability/B2_MATCHED_TRACE_PREFLIGHT_EVIDENCE.md']
    links = fences = 0
    for name in markdown:
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
            # This report is generated only after all checks pass.
            if target == HERE / 'validation.json' and not target.exists():
                continue
            assert target.exists(), (name, destination)
            if separator:
                headings = [re.sub(r'\s', '-', re.sub(r'[^a-z0-9 _-]', '',
                    line.lstrip('#').strip().lower())).strip('-')
                    for line in target.read_text().splitlines() if line.startswith('#')]
                assert anchor in headings, (name, destination)
    result = dict(status='passed', scope='stored data, source and documentation only; no FEM imports',
        archived_artifacts=len(manifest), production_identities=19, historical_files_preserved=266,
        unchanged_R017_child_sources=6, historical_audits_reexecuted=2,
        toy_status=toy['status'], toy_total_seconds=toy['elapsed_seconds'],
        toy_peak_child_tree_rss_mib=peak, kernel_permutations=24,
        wrapper_child_report_absence_checked=True, physical_launches=0,
        physical_meshes=0, pde_solves=0, matrix_solves=0,
        parent_launch_guard_reviewed=True, syntax_checks=syntax_count,
        finite_json_files=json_count, markdown_files=len(markdown),
        local_links_and_anchors=links, fenced_blocks=fences, earlier_request_history_preserved=True,
        audit_sha256=sha(Path(__file__)))
    (HERE / 'validation.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
