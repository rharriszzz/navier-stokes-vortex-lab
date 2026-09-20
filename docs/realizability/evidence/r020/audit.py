"""Audit saved R020 evidence and documentation using only the standard library."""
import ast
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
EPS = math.ulp(1.0)


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
    assert len(manifest) == 72
    for name, item in manifest.items():
        assert sha(HERE / name) == item['archived_sha256'], name
        original = Path(item['original_path'])
        if original.exists():
            assert sha(original) == item['original_sha256'], name
            if original.suffix == '.json':
                assert read(original) == read(HERE / name), name
    preflight = read(HERE / 'preflight.json')
    assert preflight['status'] == 'passed'
    assert len(preflight['source_sha256']) == 19
    for name, digest in preflight['source_sha256'].items():
        assert sha(ROOT / name) == digest, name
    assert len(preflight['historical_file_sha256']) == 358
    for name, digest in preflight['historical_file_sha256'].items():
        assert sha(ROOT / name) == digest, name
    for name, digest in preflight['runner_sha256'].items():
        assert sha(HERE / name) == digest, name
        assert (HERE / name).read_bytes() == (HERE.parent / 'r019' / name).read_bytes(), name
    for name in ('reaudit-r016-stored_validation.json', 'reaudit-r017-validation.json',
                 'reaudit-r018-validation.json', 'reaudit-r019-validation.json'):
        assert read(HERE / name)['status'] == 'passed'

    toys = read(HERE / 'toys/report.json')
    assert toys['status'] == 'passed'
    assert toys['physical_meshes'] == toys['matrix_solves'] == 0
    assert set(toys['watches']) == {'wrong_root', 'watchdog', 'kernels', 'wrapper', 'block-rhs', 'disk'}
    watches = list(toys['watches'].values())
    assert all(w['stop_reason'] is None for w in watches)
    assert math.fsum(w['elapsed_seconds'] for w in watches) <= toys['elapsed_seconds'] < 60
    assert max(w['parent_observed_peak_rss_mib'] for w in watches) < 512
    assert max(w['maximum_sample_gap_seconds'] for w in watches) < .1
    assert all(w['returncode'] == (1 if name == 'wrong_root' else 0)
               for name, w in toys['watches'].items())
    wrong = read(HERE / 'toys/wrong-root/toy-repair-report.json')
    assert wrong['status'] == 'partial_failed' and wrong['stage'] == 'imports'
    assert all(wrong[k] == 0 for k in ('physical_meshes', 'pde_solves', 'matrix_factorizations',
                                      'primary_rhs', 'returned_primary_solves', 'correction_rhs', 'matrix_solves'))
    assert toys['wrong_root_refusal']['report_sha256'] == sha(HERE / 'toys/wrong-root/toy-repair-report.json')
    watchdog = read(HERE / 'toys/watchdog/self-check.json')
    assert watchdog['timeout']['stop_reason'] == 'wall_time_limit'
    assert watchdog['memory']['stop_reason'] == 'rss_limit'
    assert watchdog['memory']['largest_observed_process_tree'] >= 2
    kernel = read(HERE / 'toys/kernels/toy-report.json')
    assert kernel['status'] == 'passed'
    assert {tuple(r['permutation']) for r in kernel['load_toys']} == set(itertools.permutations(range(4)))
    for row in kernel['load_toys']:
        assert row['load_error'] <= 256*EPS*row['load_absolute_scale']
    for row in kernel['disk_toys']:
        if 'tolerance' in row:
            assert max(row['error'], row['independent_difference']) <= row['tolerance']
    wrapper = read(HERE / 'toys/wrapper/toy-repair-report.json')
    assert wrapper['status'] == 'passed' and all(wrapper['failure_reporting'].values())
    block = read(HERE / 'toys/block-rhs/block-rhs-report.json')
    assert block['status'] == 'passed' and block['operator']['unchanged']
    for row in block['cases']:
        assert row['max_oracle_error'] <= row['arithmetic_tolerance']
        assert row['exact_essential_values'] and row['zero_target_free_entries_unchanged']
    assert block['cases'][1]['pressure_row_lifting_nontrivial']
    for key in ('wrong_offset_refusal', 'missing_layout_refusal', 'synthetic_lifting_failure'):
        assert block[key]['refused'] and block[key]['matrix_solves'] == 0
    assert read(HERE / 'toys/disk/extra-toys.json')['status'] == 'passed'

    r = read(HERE / 'physical/report.json')
    watch = read(HERE / 'physical/watch.json')
    launch = read(HERE / 'physical/launch.json')
    assert launch['physical_attempt'] == 1
    assert launch['wall_limit_seconds'] == 180 and launch['rss_limit_mib'] == 1536
    assert launch['runner_sha256'] == sha(HERE / 'physical.py')
    assert launch['parent_sha256'] == sha(HERE / 'run_contract.py')
    assert launch['toy_report_sha256'] == sha(HERE / 'toys/report.json')
    assert r['status'] == 'partial_failed' and r['stage'] == 'A_32_primary_rhs_compatibility'
    assert r['error'] == dict(type='RuntimeError', message='Primal pressure compatibility failed before solve')
    assert 'record_compatibility' in (HERE / 'physical/physical.stderr').read_text()
    assert (r['physical_meshes'], r['primary_rhs'], r['returned_primary_solves'],
            r['correction_rhs'], r['matrix_solves']) == (1, 1, 1, 1, 2)
    assert r['physical_gate_passed'] is r['campaign_ready'] is False
    assert watch['returncode'] == 1 and watch['stop_reason'] is None
    assert watch['elapsed_seconds'] < 180 and watch['parent_observed_peak_rss_mib'] < 1536
    assert r['process_peak_rss_mib'] < 1536
    assert r['source_sha256'] == preflight['source_sha256']
    for name, digest in r['runner_sha256'].items():
        assert sha(HERE / name) == digest
    old = read(HERE.parent / 'r016/physical/report.json')
    # Independently reaudited R016 supplies exact saved comparison values.
    for key in ('mesh', 'disk_partition', 'physical_parameters', 'tolerances',
                'P_constraint_dofs_per_block', 'constrained_dofs_by_block', 'operator',
                'P_pressure_compatibility', 'physical_UFL_validation', 'outputs'):
        assert r[key] == old[key], key
    certificate, old_certificate = dict(r['certificate']), dict(old['certificate'])
    certificate.pop('elapsed_seconds')
    old_certificate.pop('elapsed_seconds')
    assert certificate == old_certificate
    assert r['P_polar_reproduction_passed'] and not r['coincident_interior_facets']
    current_p, old_p = dict(r['P_diagnostics']), dict(old['P_diagnostics'])
    current_p.pop('elapsed_seconds')
    old_p.pop('elapsed_seconds')
    assert current_p == old_p
    for name in ('disk_regions.json', 'A_32_facets.json', 'A_64_facets.json'):
        assert read(HERE / 'physical' / name) == read(HERE.parent / 'r016/physical' / name), name
    bound = read(HERE / 'physical/local_bound.json')
    old_bound = read(HERE.parent / 'r016/physical/local_bound.json')
    bound.pop('elapsed_seconds')
    old_bound.pop('elapsed_seconds')
    assert bound == old_bound
    p = r['outputs']['P']
    assert p['algebraic']['factor_counts'] == dict(MatLUFactorSym=1, MatLUFactorNum=1, MatSolve=2)
    assert p['comparison']['magnitude_passed'] is p['comparison']['phase_passed'] is False
    assert all(p[k]['arithmetic_passed'] and p[k]['component_screen_passed']
               for k in ('primary', 'correction', 'corrected'))
    assert r['rhs_layout']['reference'] == r['rhs_layout']['replacement']
    assert r['rhs_layout']['block_sizes'] == [9522, 1928, 9522, 1928]
    compatibility = r['loads']['A_32']['pressure_compatibility']
    assert compatibility['tolerance'] == 256*EPS*compatibility['rhs_norm']
    assert compatibility['removed_norm'] > compatibility['tolerance']
    assert abs(math.hypot(*compatibility['pressure_constant_products_before']) -
               compatibility['removed_norm']) < 256*EPS*compatibility['rhs_norm']
    assert 'pressure_compatibility' not in r['loads']['A_64']
    for name in ('A_32', 'A_64'):
        assert max(r['loads'][name]['flux_ratios']) < 1e-8
        for key, value in old['loads'][name].items():
            assert r['loads'][name][key] == value
    post = read(HERE / 'poststop_review.json')
    assert post['status'] == 'stopped_at_pressure_compatibility' and post['retry_after_stop'] is False
    assert post['matched_trace_solves'] == 0 and post['physical_attempts'] == 1
    assert post['physical_seconds'] == watch['elapsed_seconds']
    flux = post['flux_prediction']
    for i in range(2):
        predicted = r['loads']['A_32']['signed_flux_si'][i] / 1e-7 / math.sqrt(1928)
        assert predicted == flux['A32_predicted_products'][i]
        error = abs(predicted-compatibility['pressure_constant_products_before'][i])
        assert error == flux['A32_absolute_discrepancies'][i]
        assert error <= flux['A32_absolute_flux_arithmetic_scales'][i]

    correction = read(HERE / 'continuity_correction.json')
    old_log = subprocess.check_output(['git', 'show', preflight['base_commit'] + ':REQUEST_LOG.md'],
                                      cwd=ROOT, text=True)
    assert old_log.count(correction['incorrect_status']) == 1
    restored = old_log.replace(correction['incorrect_status'], correction['restored_status'], 1)
    log = (ROOT / 'REQUEST_LOG.md').read_text()
    assert log.startswith(restored) and log.count('## R020 —') == 1
    syntax = json_count = 0
    for path in HERE.rglob('*.py'):
        ast.parse(path.read_text())
        syntax += 1
    for path in HERE.rglob('*.json'):
        if path.name != 'validation.json':
            read(path)
            json_count += 1
    markdown = ['REQUEST_LOG.md', 'SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md',
        'docs/realizability/B2_NEXT_STEPS.md', 'docs/realizability/B2_MATCHED_TRACE_REVIEW.md',
        'docs/realizability/B2_BLOCK_RHS_TOY_REPAIR_RESULT.md',
        'docs/realizability/B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md',
        'docs/realizability/B2_MATCHED_TRACE_COMPATIBILITY_EVIDENCE.md']
    links = fences = 0
    for name in markdown:
        source = ROOT / name
        body = source.read_text()
        count = sum(line.lstrip().startswith('```') for line in body.splitlines())
        assert count % 2 == 0, name
        fences += count // 2
        for destination in re.findall(r'\[[^\]]*\]\(([^)]+)\)', body):
            if destination.startswith(('https://', 'http://', 'mailto:')):
                continue
            links += 1
            path, separator, anchor = destination.partition('#')
            target = (source.parent / path).resolve() if path else source
            if target == HERE / 'validation.json' and not target.exists():
                continue
            assert target.exists(), (name, destination)
            if separator:
                headings = [re.sub(r'[^a-z0-9 _-]', '', line.lstrip('#').strip().lower())
                            .replace(' ', '-') for line in target.read_text().splitlines()
                            if line.startswith('#')]
                assert anchor in headings, (name, destination)
    result = dict(status='passed', scope='saved data, identities, arithmetic and documentation; no FEM imports',
        archived_artifacts=len(manifest), production_identities=19, historical_files_preserved=358,
        exact_R019_runner_sources=len(preflight['runner_sha256']), historical_audits_reexecuted=4,
        toy_status='passed', toy_total_seconds=toys['elapsed_seconds'],
        toy_peak_rss_mib=max(w['parent_observed_peak_rss_mib'] for w in watches),
        physical_status=r['status'], physical_stage=r['stage'],
        physical_seconds=watch['elapsed_seconds'], physical_peak_rss_mib=watch['parent_observed_peak_rss_mib'],
        physical_meshes=1, primary_solves=1, correction_solves=1, factorizations=1, matrix_solves=2,
        matched_trace_solves=0, P_outputs_exactly_reproduce_R016=True,
        A32_compatibility='failed; preserved, no solve', A64_compatibility='not measured',
        continuity_correction_verified=True, syntax_checks=syntax, finite_json_files=json_count,
        markdown_files=len(markdown), local_links_and_anchors=links, fenced_blocks=fences,
        audit_sha256=sha(Path(__file__)))
    (HERE / 'validation.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
