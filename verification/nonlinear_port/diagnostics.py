"""Unassembled field diagnostics and finite, missing-data-refusing reductions."""
from math import fsum, isfinite, log2, sqrt
from .prototype import Refusal, time_coefficients, compatible_fluxes


ANGULAR_TERMS = ('storage', 'advective', 'traction', 'body')
ENERGY_TERMS = ('storage', 'advective', 'traction', 'body', 'dissipation',
                'conservative_divergence', 'pressure_divergence')


def finite(values):
    if not all(type(v) in (float, int) and isfinite(v) for v in values):
        raise Refusal('missing or nonfinite diagnostic')


def signed_budget(terms, kind, relative=.01, floor=1e-10):
    """Values carry residual signs: traction/body are negative, storage positive."""
    required = ANGULAR_TERMS if kind == 'angular' else ENERGY_TERMS if kind == 'energy' else None
    if required is None or set(terms) != set(required):
        raise Refusal('incomplete signed budget terms')
    finite([*terms.values(), relative, floor])
    if relative <= 0 or floor <= 0:
        raise Refusal('invalid budget tolerance')
    defect = fsum(terms.values())
    total = fsum(abs(v) for v in terms.values())
    limit = max(floor, relative*total)
    return dict(terms=terms, signed_defect=defect, absolute_term_sum=total,
                limit=limit, accepted=abs(defect) <= limit)


def refinement(errors, rate, floor=1e-10):
    finite([*errors, rate, floor])
    if len(errors) != 3 or any(e < 0 for e in errors) or rate <= 0 or floor <= 0:
        raise Refusal('three nonnegative errors and positive gates required')
    pairs = []
    for coarse, fine in zip(errors, errors[1:]):
        if coarse <= floor and fine <= floor:
            pairs.append(dict(status='floor_limited', rate=None, accepted=True))
        elif fine <= floor:
            lower_bound = log2(coarse/floor)
            pairs.append(dict(status='rate_lower_bound', rate=lower_bound,
                              accepted=lower_bound >= rate))
        else:
            measured = log2(coarse/fine) if coarse > 0 else None
            pairs.append(dict(status='measured', rate=measured,
                              accepted=measured is not None and measured >= rate))
    return dict(pairs=pairs, accepted=all(p['accepted'] for p in pairs))


def quadrature_comparison(base, check, relative=1e-8, floor=1e-10):
    if not base or base.keys() != check.keys():
        raise Refusal('quadrature diagnostic inventories differ')
    finite([*base.values(), *check.values(), relative, floor])
    if relative <= 0 or floor <= 0:
        raise Refusal('invalid quadrature tolerance')
    return {k: dict(difference=check[k]-v, limit=relative*max(floor, abs(v)),
                    accepted=abs(check[k]-v) <= relative*max(floor, abs(v)))
            for k, v in base.items()}


def assemble_scalars(fem, forms):
    """Caller must enforce serial communicator; no hidden local/global confusion."""
    result = {k: float(fem.assemble_scalar(fem.form(v))) for k, v in forms.items()}
    finite(result.values())
    return result


def field_forms(U, domain, w, previous_u, older_u, exact, force, dx, ds, step, dt):
    """All six faces, physical stress, both signed divergence contributions.

    The field pressure is compared after removal of its mean, but the raw mean
    remains a separate gate. Unit cube volume is one and must be verified.
    Physical storage and BE/BDF2 energy identity terms are separately reported.
    """
    u, p = U.split(w)
    v, old = previous_u, older_u
    a, b, c = time_coefficients(step, dt)
    dtu = a*u+b*v+c*old
    x, n = U.SpatialCoordinate(domain), U.FacetNormal(domain)
    D = U.sym(U.grad(u))
    sigma = -p*U.Identity(3)+.2*D
    exact_sigma = -exact['p']*U.Identity(3)+.2*U.sym(U.grad(exact['u']))
    traction = U.dot(sigma, n)
    angular = lambda vector: x[0]*vector[1]-x[1]*vector[0]
    forms = {
        'volume': 1*dx,
        'u_L2_squared': U.inner(u-exact['u'], u-exact['u'])*dx,
        'u_H1_seminorm_squared': U.inner(U.grad(u-exact['u']), U.grad(u-exact['u']))*dx,
        'p_error_integral': (p-exact['p'])*dx,
        'p_error_squared': (p-exact['p'])**2*dx,
        'pressure_mean': p*dx,
        'kinetic_energy': .5*U.inner(u, u)*dx,
        'angular_momentum': angular(u)*dx,
        'div_u_L2_squared': U.div(u)**2*dx,
        'angular.storage': angular(dtu)*dx,
        'angular.advective': angular(u)*U.dot(u, n)*ds,
        'angular.traction': -angular(traction)*ds,
        'angular.body': -angular(force)*dx,
        'energy.storage': U.inner(dtu, u)*dx,
        'energy.advective': .5*U.inner(u, u)*U.dot(u, n)*ds,
        'energy.traction': -U.dot(traction, u)*ds,
        'energy.body': -U.dot(force, u)*dx,
        'energy.dissipation': .2*U.inner(D, D)*dx,
        'energy.conservative_divergence': .5*U.inner(u, u)*U.div(u)*dx,
        'energy.pressure_divergence': -p*U.div(u)*dx,
        'kinetic_discrete_derivative': .5*(a*U.inner(u, u)+b*U.inner(v, v)+c*U.inner(old, old))*dx,
        'lateral_flux': sum(U.dot(u, n)*ds(tag) for tag in (1, 2, 3, 4)),
        'boundary_absolute_flux': abs(U.dot(u, n))*ds,
    }
    error = U.dot(sigma-exact_sigma, n)
    forms['traction_L2_returns_squared'] = sum(U.inner(error, error)*ds(tag) for tag in (5, 6))
    for side, tag in enumerate((5, 6)):
        forms[f'flux_{side}'] = U.dot(u, n)*ds(tag)
        forms[f'area_{side}'] = 1*ds(tag)
    if step == 1:
        forms['energy_identity_storage'] = .5*(U.inner(u, u)-U.inner(v, v))/dt*dx
        forms['energy_identity_dissipation'] = .5*U.inner(u-v, u-v)/dt*dx
    else:
        forms['energy_identity_storage'] = (
            U.inner(u, u)+U.inner(2*u-v, 2*u-v)-U.inner(v, v)-U.inner(2*v-old, 2*v-old))/(4*dt)*dx
        forms['energy_identity_dissipation'] = U.inner(u-2*v+old, u-2*v+old)/(4*dt)*dx
    return forms


def field_report(values, multipliers, expected_multipliers, targets, eta):
    """Diagnostic report only: never sets overall accepted or authorizes history."""
    norms = ('u_L2', 'u_H1_seminorm', 'div_u_L2', 'traction_L2_returns')
    required = {*(n+'_squared' for n in norms), 'volume', 'pressure_mean',
                'p_error_integral', 'p_error_squared', 'flux_0', 'flux_1',
                'area_0', 'area_1', 'lateral_flux', 'boundary_absolute_flux',
                'energy_identity_storage', 'energy_identity_dissipation',
                'kinetic_discrete_derivative',
                *('angular.'+n for n in ANGULAR_TERMS),
                *('energy.'+n for n in ENERGY_TERMS)}
    if not required <= values.keys() or any(len(v) != 2 for v in (multipliers, expected_multipliers, targets)):
        raise Refusal('incomplete field diagnostic inventory')
    finite([*values.values(), *multipliers, *expected_multipliers, *targets, eta])
    if any(abs(values[k]-1) > 1e-12 for k in ('volume', 'area_0', 'area_1')):
        raise Refusal('unit cube volume/cap area failed')
    if any(values[n+'_squared'] < 0 for n in norms) or values['p_error_squared'] < 0:
        raise Refusal('negative squared norm')
    report = {n: sqrt(values[n+'_squared']) for n in norms}
    variance = values['p_error_squared']-values['p_error_integral']**2/values['volume']
    if variance < -1e-14*max(1, values['p_error_squared']):
        raise Refusal('negative mean-zero pressure variance')
    report['p_L2_mean_zero'] = sqrt(max(0, variance))
    report['both_flux_errors'] = [values[f'flux_{i}']-targets[i] for i in range(2)]
    report['multiplier_errors'] = [a-b for a, b in zip(multipliers, expected_multipliers)]
    report['pressure_mean'], report['eta'] = values['pressure_mean'], eta
    report['energy_identity_defect'] = (values['energy.storage']
        - values['energy_identity_storage']-values['energy_identity_dissipation'])
    report['raw'] = values
    for kind, terms in [('angular', ANGULAR_TERMS), ('energy', ENERGY_TERMS)]:
        report[kind+'_budget'] = signed_budget({n: values[kind+'.'+n] for n in terms}, kind)
    return report


def compatibility_report(lateral, targets, absolute_terms, condition):
    defect, limit = compatible_fluxes(lateral, targets, absolute_terms, condition)
    return dict(defect=defect, limit=limit, condition=condition,
                absolute_term_sum=absolute_terms)


def integrate_budgets(times, samples, kind):
    """Trapezoidal integration of signed instantaneous terms; retain all samples.

    This is a quadrature diagnostic, not the BE/BDF2 algebraic identity and not
    a replacement for physical endpoint storage. Temporal integration error
    remains part of the refinement study.
    """
    finite(times)
    if len(times) < 2 or len(samples) != len(times) or any(b <= a for a, b in zip(times, times[1:])):
        raise Refusal('ordered times and complete budget samples required')
    for sample in samples:
        signed_budget(sample, kind)
    integrated = {key: fsum((times[i+1]-times[i])*(samples[i][key]+samples[i+1][key])/2
                            for i in range(len(times)-1)) for key in samples[0]}
    return dict(rule='trapezoidal signed terms', times=times, samples=samples,
                budget=signed_budget(integrated, kind))


def physical_interval_budget(times, samples, kind, initial_inventory, final_inventory):
    """Endpoint physical storage plus integrated signed transport/work terms."""
    finite([initial_inventory, final_inventory])
    integral = integrate_budgets(times, samples, kind)
    terms = dict(integral['budget']['terms'], storage=final_inventory-initial_inventory)
    return dict(physical=signed_budget(terms, kind), discrete_term_integral=integral,
                storage_difference=terms['storage']-integral['budget']['terms']['storage'])


def step_checks(report, normal_samples, nonlinear_history, linear_residual, gates,
                linear_rhs_norm=0.):
    """Necessary numerical gates only. Does not certify a suite or process exits."""
    finite([*normal_samples, *nonlinear_history, linear_residual, linear_rhs_norm])
    if not normal_samples or not nonlinear_history or len(nonlinear_history) > 13:
        raise Refusal('missing return quadrature samples or nonlinear history')
    if any(v < 0 for v in nonlinear_history) or min(linear_residual, linear_rhs_norm) < 0:
        raise Refusal('negative residual norm')
    constraint_limit = gates['flux_gauge_eta_absolute']
    constraints = [*report['both_flux_errors'], report['pressure_mean'], report['eta']]
    finite(constraints)
    identity_scale = fsum(abs(report['raw'][k]) for k in
                         ('energy.storage', 'energy_identity_storage', 'energy_identity_dissipation'))
    checks = dict(
        constraints=all(abs(v) <= constraint_limit for v in constraints),
        backflow=min(normal_samples) >= -1e-8,
        nonlinear=nonlinear_history[-1] <= max(1e-12, 1e-10*nonlinear_history[0]),
        linear=linear_residual <= max(1e-13, 1e-8*linear_rhs_norm),
        energy_identity=abs(report['energy_identity_defect']) <= max(1e-12, 128*2.220446049250313e-16*identity_scale),
        angular_budget=report['angular_budget']['accepted'],
        energy_budget=report['energy_budget']['accepted'])
    return dict(checks=checks, numerical_step_accepted=all(checks.values()),
                minimum_return_normal_velocity=min(normal_samples))
