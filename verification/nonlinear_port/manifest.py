"""Validate the proposed, non-executable FEM fixture manifest without FEM imports."""
from .prototype import Refusal, require_fixture


def validate(data):
    require_fixture(data.get('fixture'))
    if data.get('schema') != 1 or data.get('execution_admitted') is not False or data.get('attempts_granted') != 0:
        raise Refusal('manifest cannot admit execution')
    if data.get('proposed_attempts') != 1:
        raise Refusal('only one future proposed attempt')
    if data.get('spatial', {}).get('subdivisions') != [2, 4, 8]:
        raise Refusal('three frozen spatial levels required')
    if data.get('temporal', {}).get('dt') != [.125, .0625, .03125]:
        raise Refusal('three frozen time levels required')
    caps = data.get('proposed_caps', {})
    expected = dict(elapsed_seconds=180, whole_task_memory_mib=1536, swap_mib=0,
                    mpi_ranks=1, threads=1, pids=32, velocity_pressure_dofs=20000)
    if caps != expected:
        raise Refusal('proposed resource caps changed')
    required = {'u_L2', 'p_L2_mean_zero', 'both_flux_errors', 'eta', 'signed_angular_budget',
                'signed_energy_budget', 'nonlinear_history', 'exit_cleanup'}
    if not required <= set(data.get('outputs', [])):
        raise Refusal('missing required output')
    if not data.get('versions') or not data.get('gates') or not data.get('refusal'):
        raise Refusal('missing verification contract')
    # Refuse absent/nonfinite numerical gates instead of treating them as passes.
    from math import isfinite
    gates = data['gates']
    numeric = {'temporal_u_L2_rate', 'flux_gauge_eta_absolute', 'finest_u_L2',
               'finest_p_L2', 'finest_div_u_L2', 'budget_relative_absolute_sum',
               'budget_absolute_floor', 'quadrature_relative_change', 'error_floor', 'finest_multiplier_error'}
    rates = {'u_L2', 'u_H1_seminorm', 'p_L2_mean_zero', 'div_u_L2', 'traction_L2_returns'}
    if set(gates) != numeric | {'spatial_rates'} or set(gates['spatial_rates']) != rates:
        raise Refusal('incomplete error gates')
    for v in [*(gates[k] for k in numeric), *gates['spatial_rates'].values()]:
        if type(v) not in (float, int) or not isfinite(v) or v <= 0:
            raise Refusal('invalid error gate')
    versions = {'python': '3.12.13', 'dolfinx': '0.10.0', 'basix': '0.10.0',
                'ufl': '2025.2.1', 'ffcx': '0.10.1', 'petsc': '3.25.5',
                'petsc4py': '3.25.5', 'mpi4py': '4.1.2', 'mpich': '5.0.1'}
    if data['versions'] != versions:
        raise Refusal('manifest must retain existing FEM pins')
    if data.get('quadrature_degree') != 24 or data.get('quadrature_check_degree') != 26:
        raise Refusal('frozen quadrature rules required')
