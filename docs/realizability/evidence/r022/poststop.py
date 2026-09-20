"""Derive the R022 refusal summary from saved reports only; standard library."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text())


def calculate():
    first = read('attempts/attempt-01/toys/report.json')
    final = read('toys/report.json')
    advanced = read('toys/advanced/advanced-report.json')
    rows = advanced['high_order']
    facets = [facet for row in rows for facet in row['facets']]
    result = dict(status='refused_at_toy_resource_cap', physical_child_launched=False,
        physical_meshes=0, physical_primary_solves_attempted=0,
        physical_primary_solves_returned=0, physical_corrections=0,
        symbolic_factorizations=0, numeric_factorizations=0, matrix_solves=0,
        orders=[64, 96], toy_attempts=2,
        initial_failure=dict(phase=first['failed_phase'],
            error=read('attempts/attempt-01/toys/wrapper/toy-repair-report.json')['error'],
            repair='Convert the accepted NumPy Boolean to built-in bool; initial sources and reports preserved.'),
        first_attempt_seconds=first['elapsed_seconds'],
        second_attempt_seconds=final['current_attempt_seconds'],
        cumulative_toy_seconds=final['elapsed_seconds'],
        observed_peak_child_tree_rss_mib=max(w['parent_observed_peak_rss_mib']
            for report in (first, final) for w in report['watches'].values()),
        maximum_sample_gap_seconds=max(w['maximum_sample_gap_seconds']
            for report in (first, final) for w in report['watches'].values()),
        advanced_watch=final['watches']['advanced'],
        last_advanced_checkpoint=advanced['stage'],
        last_checkpoint_child_high_water_mib=advanced['process_peak_rss_mib'],
        final_process_high_water='unavailable after SIGKILL; last checkpoint is not final peak',
        high_order_cases=len(rows), high_order_facets=len(facets),
        maximum_projection_error_over_tolerance=max(r['projection_error']/r['projection_tolerance'] for r in facets),
        maximum_weak_load_error_over_tolerance=max(r['weak_load_error']/r['weak_load_tolerance'] for r in facets),
        maximum_ufl_error_over_tolerance=max(r['ufl_error']/r['ufl_tolerance'] for r in rows),
        maximum_target_batch=max(r['maximum_target_batch'] for r in rows),
        original_five_prerequisites_passed=True, wrong_root_refusal_passed=True,
        parent_refusal_passed=True, actual_observer_cases_completed=len(advanced['observer_cases']),
        actual_observer_validation='not reached; runner remains unvalidated for physical execution',
        stop_localization='After all high-order polynomial results were checkpointed, before first observer case. Source next constructs reference tetrahedron and unconstrained harmonic UFL oracle. No intervening stage checkpoint or per-process RSS was saved.',
        memory_cause='Compiler contribution is plausible from a four-process tree and newly generated C without recorded completion; not established by a process-level trace.',
        no_retry_after_resource_stop=True, physical_gate_passed=False, campaign_ready=False,
        skipped=['actual harmonic observer accept/refuse cases', 'physical child',
            'physical RHS compatibility', 'P/A solves and output comparison',
            'production changes', 'gate integration', 'campaign', 'B3', 'rendering', 'encoding'],
        next_task='Toy-only process isolation and stage/RSS reporting, preserving the exact tests/forms/thresholds and cumulative 60 s/512 MiB caps; stop before any physical run.')
    assert result['cumulative_toy_seconds'] == result['first_attempt_seconds'] + result['second_attempt_seconds']
    assert len(rows) == 4 and len(facets) == 16 and not advanced['observer_cases']
    return result


if __name__ == '__main__':
    result = calculate()
    (HERE / 'result.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps(result, indent=2))
