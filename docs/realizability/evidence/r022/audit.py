"""Audit R022 saved evidence and documentation; never launch numerical work."""
import ast
import hashlib
import json
import math
from pathlib import Path
import re
import runpy
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    def reject(value):
        raise ValueError('Nonfinite JSON: ' + value)
    result = json.loads(path.read_text(), parse_constant=reject)
    def finite(value):
        if isinstance(value, float):
            assert math.isfinite(value), path
        elif isinstance(value, dict):
            for item in value.values():
                finite(item)
        elif isinstance(value, list):
            for item in value:
                finite(item)
    finite(result)
    return result


def main():
    ids = read(HERE / 'identities.json')
    assert ids['historical_files'] == len(ids['historical_sha256']) == 440
    assert len(ids['production_sha256']) == 19
    for group in ('production_sha256', 'historical_sha256'):
        for name, digest in ids[group].items():
            assert sha(ROOT / name) == digest, name
    assert read(HERE / 'reaudit-r021-validation.json')['status'] == 'passed'
    manifest = read(HERE / 'archive_manifest.json')['artifacts']
    assert len(manifest) == 86
    assert len({row['archive_path'] for row in manifest.values()}) == 79
    for name, row in manifest.items():
        assert sha(HERE / row['archive_path']) == row['sha256'], name
    for prefix in ('', 'attempts/attempt-01/'):
        preflight = read(HERE / prefix / 'preflight.json')
        assert preflight['source_sha256'] == ids['production_sha256']
        assert preflight['orders'] == [64, 96]
        for name, digest in preflight['runner_sha256'].items():
            assert manifest[prefix + name]['sha256'] == digest
    for name in ('toy_runner.py', 'kernels.py', 'disk.py', 'wrapper_toys.py', 'block_rhs_toys.py'):
        assert sha(HERE / name) == sha(HERE.parent / 'r020' / name)
    first = read(HERE / 'attempts/attempt-01/toys/report.json')
    final = read(HERE / 'toys/report.json')
    assert first['status'] == final['status'] == 'prerequisite_refused'
    assert first['failed_phase'] == 'wrapper' and final['failed_phase'] == 'advanced'
    assert final['prior_elapsed_seconds'] == first['elapsed_seconds']
    assert final['elapsed_seconds'] == first['elapsed_seconds'] + final['current_attempt_seconds'] < 60
    assert set(final['watches']) == {'wrong_root', 'watchdog', 'kernels', 'wrapper',
                                    'block-rhs', 'disk', 'parent-refusal', 'advanced'}
    for name, watch in final['watches'].items():
        assert watch['samples'] > 0 and watch['nominal_poll_seconds'] == .05
        if name == 'advanced':
            assert watch['returncode'] == -9 and watch['stop_reason'] == 'rss_limit'
            assert watch['parent_observed_peak_rss_mib'] > 512
            assert watch['largest_observed_process_tree'] == 4
        elif name == 'wrong_root':
            assert watch['returncode'] != 0 and watch['stop_reason'] is None
        else:
            assert watch['returncode'] == 0 and watch['stop_reason'] is None
            assert watch['parent_observed_peak_rss_mib'] < 512
    for parent in ('toys', 'attempts/attempt-01/toys'):
        wrong = read(HERE / parent / 'wrong-root/toy-repair-report.json')
        assert wrong['status'] == 'partial_failed' and wrong['stage'] == 'imports'
        for key in ('physical_meshes', 'pde_solves', 'matrix_factorizations',
                    'primary_rhs', 'returned_primary_solves', 'correction_rhs', 'matrix_solves'):
            assert wrong[key] == 0
        kernels = read(HERE / parent / 'kernels/toy-report.json')
        assert kernels['status'] == 'passed' and len(kernels['load_toys']) == 24
        assert len({tuple(row['permutation']) for row in kernels['load_toys']}) == 24
        watchdog = read(HERE / parent / 'watchdog/self-check.json')
        assert watchdog['timeout']['stop_reason'] == 'wall_time_limit'
        assert watchdog['memory']['stop_reason'] == 'rss_limit'
        assert watchdog['memory']['largest_observed_process_tree'] >= 2
    for name, filename in (('wrapper', 'toy-repair-report.json'),
                           ('block-rhs', 'block-rhs-report.json'), ('disk', 'extra-toys.json')):
        assert read(HERE / 'toys' / name / filename)['status'] == 'passed'
    wrapper = read(HERE / 'toys/wrapper/toy-repair-report.json')
    assert wrapper['pressure_compatibility_fixtures']['compatible_accepted']
    assert wrapper['pressure_compatibility_fixtures']['incompatible_refused']
    rejected = read(HERE / 'toys/wrapper/synthetic-compatibility-failure.json')['pressure_compatibility']
    assert rejected['raw_unchanged_after_measurement'] and not rejected['accepted']
    assert not rejected['removal_applied'] and rejected['removed_norm'] > rejected['tolerance']
    accepted = read(HERE / 'toys/wrapper/synthetic-compatible-pressure.json')['pressure_compatibility']
    assert accepted['accepted'] and accepted['removal_applied']
    assert accepted['raw_sha256'] == accepted['accepted_sha256']
    parent = read(HERE / 'toys/parent-refusal/refused/report.json')
    assert parent['status'] == 'prerequisite_refused' and not parent['child_launched']
    assert all(parent[key] == 0 for key in ('physical_meshes', 'primary_rhs',
        'returned_primary_solves', 'correction_rhs', 'matrix_factorizations', 'matrix_solves'))
    advanced = read(HERE / 'toys/advanced/advanced-report.json')
    assert advanced['status'] == 'partial' and advanced['stage'] == 'high_order_polynomial'
    assert advanced['observer_cases'] == []
    assert [(row['case'], row['order']) for row in advanced['high_order']] == [
        (0, 64), (0, 96), (1, 64), (1, 96)]
    facets = 0
    for row in advanced['high_order']:
        assert row['ufl_error'] <= row['ufl_tolerance']
        assert row['maximum_target_batch'] <= 256
        assert [item['facet'] for item in row['facets']] == [0, 1, 2, 3]
        for item in row['facets']:
            assert item['projection_error'] <= item['projection_tolerance']
            assert item['weak_load_error'] <= item['weak_load_tolerance']
            assert item['nonzero_complex_normal']
            facets += 1
    assert not (HERE / 'physical').exists()
    assert not list(HERE.rglob('launch.json'))
    derived = read(HERE / 'result.json')
    assert derived == runpy.run_path(str(HERE / 'poststop.py'))['calculate']()
    assert not derived['physical_child_launched'] and not derived['campaign_ready']
    assert derived['actual_observer_cases_completed'] == 0
    cache = read(HERE / 'cache_metadata.json')
    assert cache['newest_generated_source_siblings'] == [cache['recent_files'][0]['name']]

    base_log = subprocess.check_output(['git', 'show', ids['base_commit'] + ':REQUEST_LOG.md'],
                                       cwd=ROOT, text=True)
    log = (ROOT / 'REQUEST_LOG.md').read_text()
    assert log.startswith(base_log) and log.count('## R022 —') == 1
    syntax = json_count = 0
    for path in HERE.rglob('*.py'):
        ast.parse(path.read_text())
        syntax += 1
    for path in HERE.rglob('*.json'):
        if path != HERE / 'validation.json':
            read(path)
            json_count += 1
    markdown = ['REQUEST_LOG.md', 'SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md',
        'docs/realizability/B2_NEXT_STEPS.md', 'docs/realizability/B2_MATCHED_TRACE_REVIEW.md',
        'docs/realizability/B2_BLOCK_RHS_TOY_REPAIR_RESULT.md',
        'docs/realizability/B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md',
        'docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_RESULT.md',
        'docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_EVIDENCE.md']
    links = fences = 0
    for name in markdown:
        path = ROOT / name
        body = path.read_text()
        count = sum(line.lstrip().startswith('```') for line in body.splitlines())
        assert count % 2 == 0, name
        fences += count // 2
        for destination in re.findall(r'\[[^\]]*\]\(([^)]+)\)', body):
            if destination.startswith(('https://', 'http://', 'mailto:')):
                continue
            links += 1
            local, separator, anchor = destination.partition('#')
            target = (path.parent / local).resolve() if local else path
            if target == HERE / 'validation.json' and not target.exists():
                continue
            assert target.exists(), (name, destination)
            if separator:
                headings = [re.sub(r'[^a-z0-9 _-]', '', line.lstrip('#').strip().lower()).replace(' ', '-')
                            for line in target.read_text().splitlines() if line.startswith('#')]
                assert anchor in headings, (name, destination)
    result = dict(status='passed', scope='saved evidence, source identity and documentation; no numerical execution',
        base_commit=ids['base_commit'], production_identities=19, historical_files_preserved=440,
        historical_audits_reexecuted_before_toys=1, execution_artifacts=86,
        unique_execution_files=79, toy_attempts=2, high_order_facet_checks=facets,
        actual_observer_cases_completed=0, physical_child_launched=False,
        derived_result_reproduced=True, request_history_preserved=True,
        python_syntax_checks=syntax, finite_json_inputs=json_count,
        markdown_files=len(markdown), local_links_and_anchors=links, fenced_blocks=fences,
        numerical_result='prerequisite resource refusal; no physical result',
        physical_gate_passed=False, campaign_ready=False,
        artifact_sha256={str(p.relative_to(HERE)): sha(p) for p in sorted(HERE.rglob('*'))
                        if p.is_file() and p != HERE / 'validation.json' and '__pycache__' not in p.parts})
    (HERE / 'validation.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'artifact_sha256'}, indent=2))


if __name__ == '__main__':
    main()
