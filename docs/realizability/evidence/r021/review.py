"""R021: audit saved identities and facet arithmetic; no numerical imports."""
from contextlib import redirect_stdout
import hashlib
import io
import json
import math
from pathlib import Path
import runpy
import subprocess
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = HERE.parent / 'r020'
BASE = 'e96f81b'
EPS = math.ulp(1.0)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def quadratic(matrix, values):
    """Saved facet Gram quadratic form; no new projection or assembly."""
    return math.fsum(values[i] * matrix[i][j] * values[j]
                     for i in range(6) for j in range(6))


def calculate():
    report = read(OLD / 'physical/report.json')
    data = {q: read(OLD / f'physical/A_{q}_facets.json') for q in (32, 64)}
    rows = {}
    for q, facets in data.items():
        worst_residual = worst_symmetry = worst_normal = 0.0
        assert len(facets) == len({f['facet'] for f in facets}) == 282
        assert {tag: sum(f['tag'] == tag for f in facets) for tag in (2, 3)} == {2: 200, 3: 82}
        for facet in facets:
            matrix = facet['mass']
            matrix_scale = math.fsum(abs(x) for row in matrix for x in row)
            symmetry = max(abs(matrix[i][j] - matrix[j][i]) for i in range(6) for j in range(6))
            worst_symmetry = max(worst_symmetry, symmetry / (256 * EPS * matrix_scale))
            assert symmetry <= 256 * EPS * matrix_scale
            # Positive pivots of the symmetrized SAVED Gram matrix only.
            lower = [[0.0] * 6 for _ in range(6)]
            for i in range(6):
                for j in range(i + 1):
                    value = (matrix[i][j] + matrix[j][i]) / 2
                    value -= math.fsum(lower[i][k] * lower[j][k] for k in range(j))
                    if i == j:
                        assert value > 0
                        lower[i][j] = math.sqrt(value)
                    else:
                        lower[i][j] = value / lower[j][j]
            error = abs(math.fsum(x*x for x in facet['normal']) - 1)
            worst_normal = max(worst_normal, error)
            assert error <= 256 * EPS
            for component in (0, 1):
                coefficients = [v[component] for v in facet['coefficients']]
                moments = [v[component] for v in facet['projection_moments']]
                for i in range(6):
                    terms = [matrix[i][j] * coefficients[j] for j in range(6)]
                    error = abs(math.fsum(terms) - moments[i])
                    tolerance = 256 * EPS * (math.fsum(abs(t) for t in terms) + abs(moments[i]))
                    assert error <= tolerance
                    worst_residual = max(worst_residual, error / tolerance if tolerance else 0)
            if facet['tag'] == 3:
                assert all(x == 0 for key in ('coefficients', 'projection_moments') for v in facet[key] for x in v)
                assert facet['signed_flux_si'] == facet['absolute_flux_si'] == [0, 0]
        totals = [math.fsum(f['signed_flux_si'][i] for f in facets) for i in (0, 1)]
        absolute = [math.fsum(f['absolute_flux_si'][i] for f in facets) for i in (0, 1)]
        facet_absolute = [math.fsum(abs(f['signed_flux_si'][i]) for f in facets) for i in (0, 1)]
        saved = report['loads'][f'A_{q}']
        errors = [abs(a-b) for a, b in zip(totals, saved['signed_flux_si'])]
        assert all(e <= 256 * EPS * s for e, s in zip(errors, facet_absolute))
        assert all(abs(a-b) <= 256 * EPS * b for a, b in zip(absolute, saved['absolute_flux_si']))
        rows[str(q)] = dict(facets=282, side=200, caps=82,
            maximum_Mc_minus_m_over_arithmetic_tolerance=worst_residual,
            maximum_mass_asymmetry_over_arithmetic_tolerance=worst_symmetry,
            maximum_unit_normal_squared_error=worst_normal,
            saved_mass_positive_pivots=True, caps_exactly_zero=True,
            recomputed_signed_flux_si=totals, saved_signed_flux_si=saved['signed_flux_si'],
            sum_absolute_facet_signed_flux_si=facet_absolute,
            integrated_absolute_flux_si=absolute, report_sum_discrepancy_si=errors,
            saved_flux_ratios=saved['flux_ratios'])
    differences = []
    delta_energy = [[], []]
    target_energy = [[], []]
    mass_step = 0.0
    for a, b in zip(data[32], data[64]):
        for key in ('facet', 'cell', 'local_facet', 'tag', 'normal'):
            assert a[key] == b[key]
        scale = math.fsum(abs(x) for row in a['mass'] + b['mass'] for x in row)
        difference = max(abs(a['mass'][i][j]-b['mass'][i][j]) for i in range(6) for j in range(6))
        assert difference <= 256 * EPS * scale
        mass_step = max(mass_step, difference / (256 * EPS * scale))
        for component in (0, 1):
            delta = [x[component]-y[component] for x, y in zip(a['coefficients'], b['coefficients'])]
            target = [x[component] for x in b['coefficients']]
            delta_energy[component].append(quadratic(b['mass'], delta))
            target_energy[component].append(quadratic(b['mass'], target))
        differences.append(dict(facet=a['facet'], cell=a['cell'],
            signed_flux_step_si=[x-y for x, y in zip(a['signed_flux_si'], b['signed_flux_si'])]))
    norm_step = [math.sqrt(math.fsum(e)) for e in delta_energy]
    norm64 = [math.sqrt(math.fsum(e)) for e in target_energy]
    compatibility = report['loads']['A_32']['pressure_compatibility']
    speed = report['physical_parameters']['U_m_per_s']
    pressure_norm = math.sqrt(report['mesh']['pressure_dofs'])
    flux_budget = speed * pressure_norm * compatibility['tolerance']
    predictions = {str(q): [x / speed / pressure_norm for x in report['loads'][f'A_{q}']['signed_flux_si']]
                   for q in (32, 64)}
    products = compatibility['pressure_constant_products_before']
    discrepancies = [abs(a-b) for a, b in zip(predictions['32'], products)]
    prediction_scales = [256 * EPS * x / speed / pressure_norm
                         for x in report['loads']['A_32']['absolute_flux_si']]
    assert all(a <= b for a, b in zip(discrepancies, prediction_scales))
    return dict(status='passed_saved_data_audit', base_commit=BASE,
        new_physical_meshes=0, new_FEM_assemblies=0, new_PDE_solves=0,
        new_reference_evaluations=0, new_quadrature_evaluations=0,
        facet_audit=rows, mass_step_over_arithmetic_tolerance=mass_step,
        normal_projection_step=dict(norm='L2(surface), normalized velocity; units m',
            real_imaginary_step=norm_step, real_imaginary_q64_norm=norm64,
            relative_step=[a/b for a, b in zip(norm_step, norm64)],
            interpretation='Saved q64 facet Gram matrices weight coefficient differences; no new field evaluation. Not an error bound or output sensitivity.'),
        largest_facet_flux_steps=sorted(differences, key=lambda d: math.hypot(*d['signed_flux_step_si']), reverse=True)[:5],
        compatibility=dict(pressure_constant_norm=pressure_norm, measured=compatibility,
            predicted_products=predictions, prediction_discrepancies=discrepancies,
            prediction_arithmetic_scales=prediction_scales,
            removal_over_tolerance=compatibility['removed_norm']/compatibility['tolerance'],
            equivalent_combined_flux_budget_si_at_A32_rhs_norm=flux_budget,
            equivalent_individual_flux_ratio_ceilings=[flux_budget/x for x in report['loads']['A_32']['absolute_flux_si']],
            A64_assembled_compatibility='unmeasured; flux prediction only'),
        quadrature_cost=dict(old_points_per_facet=32**2+64**2,
            proposed_points_per_facet=64**2+96**2, point_count_ratio=(64**2+96**2)/(32**2+64**2),
            interpretation='Boundary loading point count only; not a runtime or peak-memory prediction.'),
        limitations=['No saved facet basis integrals to reconstruct signed flux independently from moments.',
            'No saved full A RHS/coefficient solution, so no new lifting or compatibility audit for A64.',
            'Moment equations test projection arithmetic, not integration accuracy.',
            'No new method implemented or numerical fixture executed.'],
        physical_gate_passed=False, campaign_ready=False)


def main():
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE,
        *[f'docs/realizability/evidence/r{n:03}' for n in range(14, 21)]], cwd=ROOT, text=True).splitlines()
    historical = {}
    for name in names:
        path = ROOT / name
        assert path.read_bytes() == subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=ROOT)
        historical[name] = sha(path)
    sources = read(OLD / 'preflight.json')['source_sha256']
    assert len(sources) == 19
    for name, digest in sources.items():
        assert sha(ROOT / name) == digest
    original_write = Path.write_text
    def capture_write(path, value, *args, **kwargs):
        assert path == OLD / 'validation.json', path
        return original_write(HERE / 'reaudit-r020-validation.json', value, *args, **kwargs)
    buffer = io.StringIO()
    with patch.object(Path, 'write_text', capture_write), redirect_stdout(buffer):
        runpy.run_path(str(OLD / 'audit.py'))['main']()
    (HERE / 'reaudit-r020.stdout').write_text(buffer.getvalue())
    assert all(sha(ROOT / name) == digest for name, digest in historical.items())
    write('identities.json', dict(base_commit=BASE, production_sha256=sources,
        historical_sha256=historical, historical_files=len(historical),
        R020_reaudit='passed; validation write redirected to R021'))
    result = calculate()
    write('review.json', result)
    print(json.dumps(dict(status=result['status'], production_identities=len(sources),
        historical_files=len(historical), facets=564,
        projection_step=result['normal_projection_step'], compatibility=result['compatibility']), indent=2))


if __name__ == '__main__':
    main()
