"""Audit stored R016 evidence using only the standard library; no FEM work."""
import ast
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
EPS = math.ulp(1.0)


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
    value = json.loads(path.read_text())
    finite(value)
    return value


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = read(EVIDENCE / 'archive_manifest.json')
    for name, item in manifest.items():
        assert sha(EVIDENCE / name) == item['archived_sha256'], name
        original = Path(item['original_path'])
        if original.exists():
            assert sha(original) == item['original_sha256'], name
            if original.suffix == '.json':
                assert read(original) == read(EVIDENCE / name), name
    preflight = read(EVIDENCE / 'preflight.json')
    for name, digest in preflight['source_sha256'].items():
        assert sha(ROOT / name) == digest, name
    for name, digest in preflight['runner_sha256'].items():
        assert sha(EVIDENCE / name) == digest
        assert sha(ROOT / 'docs/realizability/evidence/r015' / name) == digest
    historical = subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', preflight['base_commit'],
         'docs/realizability/evidence/r014', 'docs/realizability/evidence/r015'],
        cwd=ROOT, text=True).splitlines()
    appendices = ['B2_MATCHED_TRACE_EVIDENCE.md', 'B2_PHYSICAL_RESPONSE_EVIDENCE.md',
                  'B2_ACCURACY_EVIDENCE.md', 'B2_RESPONSE_COERCIVITY_EVIDENCE.md']
    for name in historical + ['docs/realizability/' + name for name in appendices]:
        assert (ROOT / name).read_bytes() == subprocess.check_output(
            ['git', 'show', preflight['base_commit'] + ':' + name], cwd=ROOT), name

    toys = read(EVIDENCE / 'toys-approved/report.json')
    sandbox = read(EVIDENCE / 'toys/report.json')
    assert sandbox['failed_phase'] == 'kernels'
    assert sandbox['watches']['kernels']['returncode'] == 143
    assert read(EVIDENCE / 'toys/kernels/toy-report.json')['stage'] == 'imports'
    assert 'MPI_Init_thread' in (EVIDENCE / 'toys/kernels.stderr').read_text()
    assert toys['status'] == 'passed' and toys['elapsed_seconds'] < 60
    assert toys['prior_sandbox_seconds'] == sandbox['elapsed_seconds']
    watches = list(sandbox['watches'].values()) + list(toys['watches'].values())
    assert math.fsum(w['elapsed_seconds'] for w in watches) <= toys['elapsed_seconds']
    assert max(w['parent_observed_peak_rss_mib'] for w in watches) < 512
    assert all(w['stop_reason'] is None for w in watches)
    assert all(w['returncode'] == 0 for w in toys['watches'].values())
    watchdog = read(EVIDENCE / 'toys-approved/watchdog/self-check.json')
    assert watchdog['timeout']['stop_reason'] == 'wall_time_limit'
    assert watchdog['memory']['stop_reason'] == 'rss_limit'
    assert watchdog['memory']['largest_observed_process_tree'] >= 2
    kernel = read(EVIDENCE / 'toys-approved/kernels/toy-report.json')
    assert kernel['status'] == 'passed'
    assert len(kernel['load_toys']) == 24
    assert {tuple(row['permutation']) for row in kernel['load_toys']} == set(itertools.permutations(range(4)))
    wrapper = read(EVIDENCE / 'toys-approved/wrapper/toy-repair-report.json')
    assert wrapper['status'] == 'passed'
    assert wrapper['tetrahedron']['constrained_dofs_per_block'] == [24, 0, 24, 0]
    assert wrapper['tetrahedron']['velocity_free_interior_dofs'] == [6, 6]
    assert all(wrapper['failure_reporting'].values())
    assert read(EVIDENCE / 'toys-approved/disk/extra-toys.json')['status'] == 'passed'

    r = read(EVIDENCE / 'physical/report.json')
    watch = read(EVIDENCE / 'physical/watch.json')
    assert r['status'] == 'partial_failed' and r['stage'] == 'P_outputs'
    assert r['error'] == dict(type='AttributeError', message="'list' object has no attribute '_cpp_object'")
    assert 'apply_lifting(rhs,captured' in (EVIDENCE / 'physical/physical.stderr').read_text()
    assert (r['physical_meshes'], r['primary_rhs'], r['returned_primary_solves'],
            r['correction_rhs'], r['matrix_solves']) == (1, 1, 1, 1, 2)
    assert r['campaign_ready'] is r['physical_gate_passed'] is False
    assert watch['returncode'] == 1 and watch['stop_reason'] is None
    assert watch['elapsed_seconds'] < 180 and watch['parent_observed_peak_rss_mib'] < 1536
    assert r['source_sha256'] == preflight['source_sha256']
    for name, digest in r['runner_sha256'].items():
        assert sha(EVIDENCE / name) == digest
    assert r['mesh'] == dict(cells=482, velocity_dofs=9522, pressure_dofs=1928,
        mesh_sha256='423ab057c5738ae3e2dcef6e82c238ee7e61bc1d0af7f1e212d04b8a2cd6bfb4')
    bound = read(EVIDENCE / 'physical/local_bound.json')
    assert len(bound['cell_trace_eigenvalues']) == 482
    assert bound['C_upper'] == 58.12657123078638
    assert r['certificate']['classification']['status'] == 'certified_positive'
    assert not r['coincident_interior_facets']
    regions = read(EVIDENCE / 'physical/disk_regions.json')
    assert len(regions) == len({row['cell'] for row in regions}) == 11
    for i, (expected, tolerance) in enumerate(zip(r['disk_partition']['expected_moments'],
                                                 r['disk_partition']['arithmetic_tolerances'])):
        total = math.fsum(row['moments']['moments'][i] for row in regions)
        assert total == r['disk_partition']['dimensionless_moments'][i]
        assert abs(total - expected) <= tolerance
    for name in ('A_32', 'A_64'):
        facets = read(EVIDENCE / ('physical/' + name + '_facets.json'))
        assert len(facets) == len({row['facet'] for row in facets}) == 282
        assert 'pressure_compatibility' not in r['loads'][name]
        for row in facets:
            assert abs(math.fsum(v*v for v in row['normal']) - 1) < 256*EPS
            coefficients = [complex(*c) for c in row['coefficients']]
            targets = [complex(*c) for c in row['projection_moments']]
            for i in range(6):
                terms = [row['mass'][i][j]*coefficients[j] for j in range(6)]
                assert abs(sum(terms)-targets[i]) <= 256*EPS*(sum(map(abs, terms))+abs(targets[i]))
        for i in range(2):
            absolute = math.fsum(row['absolute_flux_si'][i] for row in facets)
            signed = math.fsum(row['signed_flux_si'][i] for row in facets)
            assert abs(absolute-r['loads'][name]['absolute_flux_si'][i]) <= 256*EPS*absolute
            assert abs(signed-r['loads'][name]['signed_flux_si'][i]) <= 256*EPS*absolute
            assert r['loads'][name]['flux_ratios'][i] < 1e-8
    for row in r['physical_UFL_validation']:
        assert row['maximum_coefficient_difference'] <= row['tolerance']
    old_text = (ROOT / 'docs/realizability/B2_PHYSICAL_RESPONSE_EVIDENCE.md').read_text()
    old = json.loads(re.search(r'^## Complete calculation report\n\n```json\n(.*?)^```',
                               old_text, re.M | re.S).group(1))
    current, previous = dict(r['P_diagnostics']), dict(old['solver'])
    current.pop('elapsed_seconds')
    previous.pop('elapsed_seconds')
    assert current == previous
    assert r['P_constraint_dofs_per_block'] == [1692, 0, 1692, 0]
    blocks = r['constrained_dofs_by_block']
    assert not blocks[1] and not blocks[3]
    assert len(set(blocks[0] + blocks[2])) == 3384
    offsets = r['operator']['offsets']
    assert offsets == [0, 9522, 11450, 20972, 22900]
    assert all(offsets[i] <= dof < offsets[i+1] for i in (0, 2) for dof in blocks[i])
    assert r['P_pressure_compatibility']['removed_norm'] == 0
    assert set(r['outputs']) == {'P'}
    p = r['outputs']['P']
    a = p['algebraic']
    assert a['factor_counts'] == dict(MatLUFactorSym=1, MatLUFactorNum=1, MatSolve=2)
    assert a['matrix_digest'] == r['operator']['digest']
    assert all(a[k] for k in ('same_matrix_state', 'same_factor_handle', 'same_factor_state'))
    assert max(a[k] for k in ('primary_relative_residual', 'correction_relative_residual',
                              'corrected_relative_residual')) < 1e-9
    assert a['enforced_essential_change'] == a['constrained_residual_maximum'] == 0
    gains = []
    for key in ('primary', 'correction', 'corrected'):
        row = p[key]
        gain = complex(*row['gain'])
        gains.append(gain)
        assert gain == complex(*row['numerator']) / row['denominator_m4']
        assert row['denominator_m4'] == math.pi*.025**4/2
        assert row['arithmetic_tolerance_per_m'] == 256*EPS*row['absolute_contribution_gain']
        assert row['independent_difference_per_m'] <= row['arithmetic_tolerance_per_m']
        assert max(row['arithmetic_tolerance_per_m'], row['independent_difference_per_m']) <= r['tolerances']['output_component_per_m']
        assert row['arithmetic_passed'] and row['component_screen_passed']
        assert len(row['reconstruction']) == 11
        assert all(x['error'] <= x['tolerance'] for x in row['reconstruction'])
    assert abs(gains[2]-gains[0]-gains[1]) == p['linearity_error_per_m']
    assert p['linearity_error_per_m'] <= p['linearity_tolerance_per_m']
    assert abs(gains[1]) <= r['tolerances']['output_component_per_m']
    for row, prior in zip(p['polar'], (old['quadrature'][1], old['quadrature'][-1])):
        assert len(row['gains']) == 6
        assert abs(complex(*row['gains'][1])-complex(*prior['features_gain'][1])) <= 2.4719806123e-13
    assert r['P_polar_reproduction_passed']
    reference = complex(*r['reference']['gain_per_m'])
    assert abs(gains[0]-reference) == p['comparison']['absolute_complex_error_per_m']
    assert p['comparison']['magnitude_passed'] is p['comparison']['phase_passed'] is False
    json_paths = list(EVIDENCE.rglob('*.json'))
    for path in json_paths:
        read(path)
    for path in EVIDENCE.rglob('*.py'):
        ast.parse(path.read_text())
    result = dict(status='passed', archived_artifacts=len(manifest), pinned_source_identities=19,
        historical_files_preserved=len(historical), prior_appendices_preserved=len(appendices),
        toy_total_seconds=toys['elapsed_seconds'],
        toy_peak_rss_mib=max(w['parent_observed_peak_rss_mib'] for w in watches),
        physical_seconds=watch['elapsed_seconds'], physical_peak_rss_mib=watch['parent_observed_peak_rss_mib'],
        physical_meshes=1, returned_primary_solves=1, correction_solves=1, matched_trace_solves=0,
        projection_records=564, disk_regions=11, P_cell_output_screens_passed=True,
        P_polar_reproduction_passed=True, physical_accuracy_passed=False,
        source_and_traceback_diagnosis_only=True, new_FEM_execution_by_audit=False)
    (EVIDENCE / 'stored_validation.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
