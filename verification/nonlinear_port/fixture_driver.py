"""One unexecuted n=2 Poiseuille verification step; FEM modules are injected.

This module imports only the standard library and local source. A future
supervised worker must inject pinned FEM modules after a separate admission.
The return value is numerical evidence, never a process/run acceptance record.
"""
from math import fsum, isfinite, sqrt
import time

from . import fixtures
from .cube_adapter import (Assembler, RETURNS, boundary_values, create_cube,
                           exact_data, interpolate_state, sparse_solve, step_forms)
from .diagnostics import (assemble_scalars, compatibility_report, field_forms,
                          field_report, quadrature_comparison, step_checks,
                          poiseuille_endpoint_budgets)
from .manifest import validate as validate_manifest
from .polynomial import face
from .prototype import Refusal, newton
from .sparse import constraint_condition, row_scales, scale_system


def nonexact_guess(exact_state, velocity_dofs, fixed, amount=.05):
    """Perturb one free velocity DOF while retaining the exact lateral lift."""
    if not isfinite(amount) or amount == 0:
        raise Refusal('nonzero finite free-velocity perturbation required')
    free = sorted(set(map(int, velocity_dofs))-set(fixed))
    if not free or any(i < 0 or i >= len(exact_state) for i in free):
        raise Refusal('no identifiable free velocity DOF')
    result = list(exact_state)
    result[free[0]] += amount
    if not all(isfinite(v) for v in result) or any(result[i] != v for i, v in fixed.items()):
        raise Refusal('initial guess lost prescribed trace')
    return result, free[0]


def return_quadrature_samples(np, meshlib, basix, domain, tags, velocity, degree):
    """Evaluate outward velocity on every cap facet at triangle quadrature points.

    This is a pointwise backflow screen. It does not replace signed integrated
    flux forms or a check that the numerical quadrature itself integrates them.
    """
    if degree not in (24, 26) or domain.topology.dim != 3:
        raise Refusal('frozen tetrahedral return sampling only')
    points, weights = basix.make_quadrature(basix.CellType.triangle, degree)
    if (len(points) == 0 or len(points) != len(weights)
            or any(not isfinite(float(v)) or v <= 0 for v in weights)
            or abs(fsum(float(v) for v in weights)-.5) > 1e-12
            or any(s < 0 or t < 0 or s+t > 1 for s, t in points)):
        raise Refusal('invalid return quadrature rule')
    fdim = 2
    domain.topology.create_connectivity(fdim, 3)
    attached = domain.topology.connectivity(fdim, 3)
    values = []
    counts = []
    for side, tag in enumerate(RETURNS):
        facets = tags.find(tag)
        if len(facets) == 0:
            raise Refusal('missing tagged return facets')
        geometry = meshlib.entities_to_geometry(domain, fdim, facets)
        if len(geometry) != len(facets) or any(len(g) != 3 for g in geometry):
            raise Refusal('return facet is not affine triangular geometry')
        physical, cells = [], []
        for facet, nodes in zip(facets, geometry):
            cell_ids = attached.links(int(facet))
            if len(cell_ids) != 1:
                raise Refusal('return facet is not exterior')
            vertices = domain.geometry.x[nodes]
            if any(abs(float(vertex[2])-side) > 1e-12 for vertex in vertices):
                raise Refusal('return facet is not on its tagged cap')
            for s, t in points:
                physical.append((1-s-t)*vertices[0]+s*vertices[1]+t*vertices[2])
                cells.append(int(cell_ids[0]))
        sampled = velocity.eval(np.asarray(physical), np.asarray(cells, dtype=np.int32))
        if len(sampled) != len(physical) or any(len(value) != 3 for value in sampled):
            raise Refusal('missing velocity samples at return quadrature points')
        normal_sign = 2*side-1
        side_values = [normal_sign*float(value[2]) for value in sampled]
        if not all(isfinite(v) for v in side_values):
            raise Refusal('nonfinite return normal sample')
        values.extend(side_values)
        counts.append(len(side_values))
    return values, counts


def numerical_decision(report, checked, comparison, corrections, gates):
    """A complete single-level oracle gate; never a suite or process verdict."""
    if corrections < 1 or type(corrections) is not int:
        raise Refusal('at least one verified linear correction required')
    required = {'u_L2', 'p_L2_mean_zero', 'div_u_L2', 'traction_L2_returns',
                'multiplier_errors', 'both_flux_errors'}
    if not required <= report.keys() or not comparison or not checked:
        raise Refusal('incomplete Poiseuille numerical evidence')
    if any(len(report[k]) != 2 for k in ('multiplier_errors', 'both_flux_errors')):
        raise Refusal('both return errors required')
    values = [report[k] for k in required if k not in ('multiplier_errors', 'both_flux_errors')]
    values += [*report['multiplier_errors'], *report['both_flux_errors']]
    if not all(type(v) in (float, int) and isfinite(v) for v in values):
        raise Refusal('nonfinite Poiseuille oracle evidence')
    if any(report[k] < 0 for k in ('u_L2', 'p_L2_mean_zero', 'div_u_L2', 'traction_L2_returns')):
        raise Refusal('negative Poiseuille norm')
    tol = gates['flux_gauge_eta_absolute']
    checks = {
        'velocity_pressure_exact': report['u_L2'] <= 1e-9 and report['p_L2_mean_zero'] <= 1e-9,
        'divergence': report['div_u_L2'] <= 1e-9,
        'return_traction': report['traction_L2_returns'] <= 1e-9,
        'multipliers': all(abs(v) <= tol for v in report['multiplier_errors']),
        'quadrature_24_26': all(item['accepted'] for item in comparison.values()),
        'step_gates': checked['numerical_step_accepted'],
        'verified_correction': corrections >= 1,
    }
    return {'checks': checks, 'numerical_accepted': all(checks.values())}


def run_poiseuille(modules, manifest, clock=time.monotonic):
    """Build and solve only the frozen n=2 BE Poiseuille oracle.

    The trusted outer controller owns admission, containment, timing, attempt
    reservation, child exit and cleanup. This function must run inside that
    already verified scope. Its output cannot by itself accept an attempt.
    """
    validate_manifest(manifest)
    if set(modules) != {'np', 'mesh', 'fem', 'fem_petsc', 'basix_ufl', 'basix',
                        'ufl', 'PETSc', 'comm'}:
        raise Refusal('incomplete pinned FEM module injection')
    np, meshlib, fem, fp = (modules[k] for k in ('np', 'mesh', 'fem', 'fem_petsc'))
    U, PETSc, comm = (modules[k] for k in ('ufl', 'PETSc', 'comm'))
    dt = manifest['spatial']['dt']
    t0 = clock()
    domain, space, tags, lateral = create_cube(
        np, meshlib, fem, modules['basix_ufl'], comm, 2, 'poiseuille')
    previous = interpolate_state(np, fem, space, 'poiseuille', 0.)
    trace = interpolate_state(np, fem, space, 'poiseuille', dt)
    fixed = boundary_values(fem, space, lateral, trace)
    _velocity_space, velocity_map = space.sub(0).collapse()
    if not len(fixed) or not len(velocity_map):
        raise Refusal('missing lateral lift or velocity inventory')
    guess, perturbed_dof = nonexact_guess(trace.x.array.tolist(), velocity_map, fixed)
    mixed_dofs = len(guess)
    w = fem.Function(space)
    w.x.array[:] = guess
    w.x.scatter_forward()
    # The adapter's global state is (mixed u/p, P_minus, P_plus, eta).
    # Keep the mixed Function assignment above separate from its scalar border.
    guess += [0., 0., 0.]
    t_mesh = clock()
    forms, constants, context = step_forms(U, fem, domain, space, tags, w,
                                           previous, previous, dt, dt, 1,
                                           'poiseuille', degree=24)
    assembler = Assembler(fem, fp, PETSc, w, forms, constants, fixed)
    t_forms = clock()
    rows = [assembler.vector(form) for form in assembler.rows]
    condition = constraint_condition(rows, fixed)
    exact = context['exact']
    ds = context['ds']
    u, _ = U.split(w)
    normal = U.FacetNormal(domain)
    lateral_flux = float(fem.assemble_scalar(fem.form(
        sum(U.dot(u, normal)*ds(tag) for tag in (1, 2, 3, 4)))))
    lateral_absolute = float(fem.assemble_scalar(fem.form(
        sum(abs(U.dot(u, normal))*ds(tag) for tag in (1, 2, 3, 4)))))
    targets = [float(fem.assemble_scalar(fem.form(exact['targets'][i]*ds(tag))))
               for i, tag in enumerate(RETURNS)]
    compatibility = compatibility_report(lateral_flux, targets,
                                          lateral_absolute+fsum(abs(v) for v in targets),
                                          condition['condition_bound'])
    _raw_residual, raw_matrix = assembler(guess)
    scales = row_scales(raw_matrix)

    def evaluate(state):
        return scale_system(*assembler(state), scales)

    corrections = []
    def linear_solve(matrix, rhs):
        answer = sparse_solve(np, PETSc, comm, matrix, rhs)
        defect = sqrt(fsum((v-b)**2 for v, b in zip(matrix.matvec(answer), rhs)))
        rhs_norm = sqrt(fsum(v*v for v in rhs))
        corrections.append({'true_residual': defect, 'rhs_norm': rhs_norm})
        return answer

    state, history = newton(guess, evaluate, linear_solve)
    t_solve = clock()
    if not corrections:
        raise Refusal('non-exact oracle solved without a checked correction')
    # Newton's final evaluation installed the accepted state before diagnostics.
    assembler(state)
    for degree in (24, 26):
        measure_dx = U.Measure('dx', domain=domain, metadata={'quadrature_degree': degree})
        measure_ds = U.Measure('ds', domain=domain, subdomain_data=tags,
                               metadata={'quadrature_degree': degree})
        exact_degree = exact_data(U, domain, 'poiseuille', dt)
        forms_degree = field_forms(U, domain, w, U.split(previous)[0],
                                   U.split(previous)[0], exact_degree,
                                   exact_degree['force'], measure_dx, measure_ds,
                                   1, dt)
        values = assemble_scalars(fem, forms_degree)
        if degree == 24:
            base_values = values
        else:
            check_values = values
    comparison = quadrature_comparison(
        base_values, check_values, manifest['gates']['quadrature_relative_change'])
    u_poly, p_poly = fixtures.poiseuille()
    sigma = fixtures.stress(u_poly, p_poly)
    expected = [-float(face(sigma[2][2], 2, side).evaluate([0, 0, 0, dt]))
                for side in (0, 1)]
    report = field_report(base_values, state[-3:-1], expected, targets, state[-1])
    velocity = w.sub(0).collapse()
    samples, sample_counts = return_quadrature_samples(
        np, meshlib, modules['basix'], domain, tags, velocity, 24)
    latest = corrections[-1]
    checked = step_checks(report, samples, history, latest['true_residual'],
                          manifest['gates'], latest['rhs_norm'])
    decision = numerical_decision(report, checked, comparison,
                                   len(corrections), manifest['gates'])
    endpoints = poiseuille_endpoint_budgets(base_values, dt)
    decision['checks']['physical_endpoint_budgets'] = all(
        entry['physical']['accepted'] for entry in endpoints.values())
    decision['numerical_accepted'] = all(decision['checks'].values())
    t_diagnostics = clock()
    return {
        'fixture': 'poiseuille', 'subdivisions': 2, 'dt': dt,
        'mixed_dofs': mixed_dofs, 'global_dofs': len(guess),
        'fixed_velocity_dofs': len(fixed), 'perturbed_velocity_dof': perturbed_dof,
        'constraint_condition': condition, 'compatibility': compatibility,
        'frozen_row_scales': {'minimum': min(scales), 'maximum': max(scales)},
        'nonlinear_history': history, 'linear_corrections': corrections,
        'return_quadrature_sample_counts': sample_counts,
        'minimum_return_normal_velocity': min(samples),
        'phase_seconds': {'mesh_and_lift': t_mesh-t0,
                          'primary_form_setup_jit': t_forms-t_mesh,
                          'compatibility_rank_newton': t_solve-t_forms,
                          'diagnostic_form_jit_assembly_sampling': t_diagnostics-t_solve},
        'diagnostics_degree24': report, 'diagnostics_degree26': check_values,
        'multipliers': state[-3:-1], 'eta': state[-1],
        'physical_endpoint_budgets': endpoints,
        'quadrature_comparison': comparison, 'step_checks': checked,
        **decision,
    }
