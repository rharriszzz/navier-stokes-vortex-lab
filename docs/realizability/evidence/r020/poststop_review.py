"""R020 saved-data arithmetic and stop accounting; no FEM imports or reruns."""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path.cwd()


def read(path):
    return json.loads(path.read_text())


def main():
    report = read(HERE / 'physical/report.json')
    watch = read(HERE / 'physical/watch.json')
    toys = read(HERE / 'toys/report.json')
    previous = read(ROOT / 'docs/realizability/evidence/r016/physical/report.json')
    assert report['stage'] == 'A_32_primary_rhs_compatibility'
    assert report['status'] == 'partial_failed'
    assert set(report['outputs']) == {'P'}
    assert report['outputs']['P'] == previous['outputs']['P']
    assert 'pressure_compatibility' not in report['loads']['A_64']
    compatibility = report['loads']['A_32']['pressure_compatibility']
    nq = report['mesh']['pressure_dofs']
    speed = report['physical_parameters']['U_m_per_s']
    # The pinned helper normalizes an all-ones DG1 pressure coefficient vector.
    # Its Euclidean norm is sqrt(nq). With pressure row -div(u), lifting gives
    # the signed projected flux / (U*sqrt(nq)) for the pressure-constant product.
    predicted = [flux / speed / math.sqrt(nq)
                 for flux in report['loads']['A_32']['signed_flux_si']]
    products = compatibility['pressure_constant_products_before']
    discrepancies = [abs(a-b) for a, b in zip(predicted, products)]
    flux_scales = [256 * math.ulp(1.0) * flux / speed / math.sqrt(nq)
                   for flux in report['loads']['A_32']['absolute_flux_si']]
    assert all(error <= scale for error, scale in zip(discrepancies, flux_scales))
    predicted64 = [flux / speed / math.sqrt(nq)
                   for flux in report['loads']['A_64']['signed_flux_si']]
    result = dict(
        status='stopped_at_pressure_compatibility',
        physical_attempts=1, physical_meshes=1, returned_primary_solves=1,
        correction_rhs=1, matrix_solves=2, symbolic_factorizations=1,
        numeric_factorizations=1, matched_trace_solves=0,
        physical_seconds=watch['elapsed_seconds'],
        physical_peak_observed_rss_mib=watch['parent_observed_peak_rss_mib'],
        process_high_water_rss_mib=report['process_peak_rss_mib'],
        physical_maximum_sample_gap_seconds=watch['maximum_sample_gap_seconds'],
        toy_total_seconds=toys['elapsed_seconds'],
        toy_peak_observed_rss_mib=max(w['parent_observed_peak_rss_mib']
                                    for w in toys['watches'].values()),
        P_outputs_equal_R016=True,
        A32_compatibility=compatibility,
        removed_norm_over_tolerance=compatibility['removed_norm']/compatibility['tolerance'],
        removed_norm_over_rhs_norm=compatibility['removed_norm']/compatibility['rhs_norm'],
        pressure_nullspace_normalization=math.sqrt(nq),
        flux_prediction=dict(formula='signed_flux_si / (U * sqrt(nq))',
            A32_predicted_products=predicted, A32_measured_products=products,
            A32_absolute_discrepancies=discrepancies,
            A32_absolute_flux_arithmetic_scales=flux_scales,
            A64_flux_only_predicted_products=predicted64,
            A64_assembled_rhs_compatibility='not measured'),
        interpretation='The saved A32 flux predicts the measured pressure incompatibility within an absolute-flux arithmetic scale. This supports finite-order trace integration as the cause, but no new quadrature or trace calculation was performed. A64 compatibility and all matched-trace gains remain unmeasured.',
        skipped=['A32 primary solve/correction/PDE/output checks',
                 'A64 lifting/compatibility/solve/correction/PDE/output checks',
                 'paired errors and output load sensitivity',
                 'new meshes, quadrature orders, tolerance or trace changes',
                 'production changes, gate integration, campaign, B3, movie'],
        retry_after_stop=False, physical_gate_passed=False, campaign_ready=False,
        next_task='Astra/high: saved-data and method review of pressure compatibility and a future trace-integration contract; no physical retry during review.')
    (HERE / 'poststop_review.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
