"""Isolated P2/P1 nonlinear verification kernel; no admitted launch driver.

Imports only the standard library. UFL/FEM objects are injected into builders
by the unexecuted cube adapter. No production backend is imported.
"""
from dataclasses import dataclass
from math import isfinite, sqrt
from sys import float_info
from .sparse import CSR


class Refusal(ValueError):
    pass


def require_fixture(name):
    if name not in ('manufactured', 'affine_time', 'poiseuille', 'rotation'):
        raise Refusal('verification fixtures only; tank and B2 are excluded')


def compatible_fluxes(dirichlet_flux, returns, absolute_term_sum, condition=1.0):
    values = [dirichlet_flux, *returns, absolute_term_sum, condition]
    if len(returns) != 2 or not all(isfinite(v) for v in values):
        raise Refusal('two finite return fluxes required')
    if condition < 1 or condition > 1e6 or absolute_term_sum <= 0:
        raise Refusal('invalid or ill-conditioned compatibility scale')
    if absolute_term_sum < abs(dirichlet_flux) + sum(abs(v) for v in returns):
        raise Refusal('underreported compatibility term sum')
    limit = 128*float_info.epsilon*condition*absolute_term_sum
    defect = dirichlet_flux + sum(returns)
    if abs(defect) > limit:
        raise Refusal('incompatible prescribed total flux; no projection allowed')
    return defect, limit


def time_coefficients(step, dt):
    if type(step) is not int or step < 1 or not isfinite(dt) or dt <= 0:
        raise Refusal('positive step and fixed dt required')
    return (1/dt, -1/dt, 0) if step == 1 else (1.5/dt, -2/dt, .5/dt)


def make_space(fem, basix_ufl, mesh, fixture):
    """Future adapter only. Full pressure + gauge scalar = mean-zero pressure."""
    require_fixture(fixture)
    if mesh.geometry.dim != 3:
        raise Refusal('three-dimensional verification mesh required')
    cell = mesh.basix_cell()
    velocity = basix_ufl.element('Lagrange', cell, 2, shape=(3,))
    pressure = basix_ufl.element('Lagrange', cell, 1)
    return fem.functionspace(mesh, basix_ufl.mixed_element([velocity, pressure]))


def build_forms(U, w, previous, older, test, increment, normal, dx, ds,
                return_tags, pressures, eta, force, offsets, targets, volume,
                step, dt, fixture, rho=1.0, mu=.1, exact_history=None):
    """Unassembled residual/Jacobian blocks for (w=(u,p), P-, P+, eta).

    eta augments continuity, paired with the integral(p)=0 row. With exactly
    compatible boundary totals it is zero; a nonzero value must refuse a run.
    Every Dirichlet value is installed in w before evaluating ALL residual rows.
    Newton increments vanish there; eliminate their columns only afterwards.
    Scalar forms are globally assembled by the future adapter, never per-rank.
    """
    require_fixture(fixture)
    if len(return_tags) != 2 or len(set(return_tags)) != 2:
        raise Refusal('two distinct tagged returns required')
    if len(pressures) != 2 or len(offsets) != 2 or len(targets) != 2:
        raise Refusal('two return data groups required')
    if not all(isfinite(v) and v > 0 for v in (rho, mu, volume)):
        raise Refusal('positive finite density, viscosity and volume required')
    u, p = U.split(w)
    old_u, _ = U.split(previous)
    older_u, _ = U.split(older)
    if exact_history is not None:
        if fixture != 'manufactured' or step != 1 or len(exact_history) != 2:
            raise Refusal('exact history override only for spatial BE fixture')
        old_u, older_u = exact_history
    v, q = U.split(test)
    du, dp = U.split(increment)
    a0, a1, a2 = time_coefficients(step, dt)
    dtu = a0*u+a1*old_u+a2*older_u
    residual = (rho*U.inner(dtu, v)-rho*U.inner(U.outer(u, u), U.grad(v))
                + 2*mu*U.inner(U.sym(U.grad(u)), U.sym(U.grad(v)))
                - p*U.div(v)+q*U.div(u)+eta*q-U.inner(force, v))*dx
    pressure_columns, flux_rows, flux_residuals = [], [], []
    for tag, pressure, offset, target in zip(return_tags, pressures, offsets, targets):
        residual += (rho*U.dot(u, normal)*U.dot(u, v)
                     + pressure*U.dot(v, normal)-U.dot(offset, v))*ds(tag)
        pressure_columns.append(U.dot(v, normal)*ds(tag))
        flux_rows.append(U.dot(du, normal)*ds(tag))
        flux_residuals.append(U.dot(u, normal)*ds(tag)-(target/volume)*dx)
    return {
        'momentum_continuity': residual,
        'jacobian': U.derivative(residual, w, increment),
        'pressure_columns': pressure_columns,
        'eta_column': q*dx,
        'flux_rows': flux_rows,
        'flux_residuals': flux_residuals,
        'gauge_row': dp*dx,
        'gauge_residual': p*dx,
        'divergence_energy_defect': rho/2*U.inner(u, u)*U.div(u)*dx,
    }


@dataclass(frozen=True)
class NewtonOptions:
    iterations: int = 12
    backtracks: int = 8
    relative: float = 1e-10
    absolute: float = 1e-12


def newton(initial, evaluate, linear_solve, options=NewtonOptions()):
    """Solve an already scaled/lifted algebraic residual with exact Jacobian.

    evaluate returns (residual, Jacobian); linear_solve(J, rhs) is supplied by
    the adapter. The same fixed row/column scales apply throughout. Returns
    only after residual convergence, never on small-step size alone. This
    kernel is not an execution supervisor or a FEM acceptance decision.
    """
    if (type(options.iterations) is not int or not 1 <= options.iterations <= 12
            or type(options.backtracks) is not int or not 0 <= options.backtracks <= 8
            or not all(isfinite(v) and v > 0 for v in (options.relative, options.absolute))):
        raise Refusal('invalid nonlinear iteration limits')
    x = list(initial)
    if not x or not all(isfinite(v) for v in x):
        raise Refusal('nonfinite or empty initial state')
    history = []

    def checked(state):
        r, j = evaluate(state)
        if isinstance(j, CSR):
            try:
                j.validate(len(x))
            except ValueError as exc:
                raise Refusal(str(exc)) from exc
            valid_matrix = True
        else:
            valid_matrix = (len(j) == len(x)
                and all(len(row) == len(x) for row in j)
                and all(isfinite(v) for row in j for v in row))
        if (len(r) != len(x) or not valid_matrix
                or not all(isfinite(v) for v in r)):
            raise Refusal('invalid residual or Jacobian')
        norm = sqrt(sum(v*v for v in r))
        if not isfinite(norm):
            raise Refusal('residual norm overflow')
        return r, j, norm

    r, j, initial_norm = checked(x)
    target = max(options.absolute, options.relative*initial_norm)
    for iteration in range(options.iterations+1):
        norm = sqrt(sum(v*v for v in r))
        history.append(norm)
        if norm <= target:
            return x, history
        if iteration == options.iterations:
            break
        delta = linear_solve(j, [-v for v in r])
        if len(delta) != len(x) or not all(isfinite(v) for v in delta):
            raise Refusal('invalid linear correction')
        # Check the supplied linear solve, rather than trusting its status.
        action = (j.matvec(delta) if isinstance(j, CSR) else
                  [sum(a*b for a, b in zip(row, delta)) for row in j])
        linear_defect = sqrt(sum((v+ri)**2 for v, ri in zip(action, r)))
        if linear_defect > max(options.absolute*.1, norm*1e-8):
            raise Refusal('linear correction residual failed')
        for k in range(options.backtracks+1):
            damping = 2.0**(-k)
            trial = [v+damping*d for v, d in zip(x, delta)]
            if not all(isfinite(v) for v in trial):
                raise Refusal('nonfinite trial state')
            nr, nj, nn = checked(trial)
            if nn <= (1-1e-4*damping)*norm or nn <= target:
                x, r, j = trial, nr, nj
                break
        else:
            raise Refusal('Newton line search exhausted')
    raise Refusal('Newton iteration cap reached')


def enforce_lifting(residual, jacobian, state, fixed_values):
    """Keep every free/coupled residual row; require installed current lift."""
    n = len(state)
    if len(residual) != n or len(jacobian) != n or any(len(r) != n for r in jacobian):
        raise Refusal('inconsistent algebraic sizes')
    if any(type(i) is not int or i < 0 or i >= n for i in fixed_values):
        raise Refusal('invalid Dirichlet index')
    if any(state[i] != value for i, value in fixed_values.items()):
        raise Refusal('install time-dependent lift before residual evaluation')
    r = list(residual)
    j = [list(row) for row in jacobian]
    for i in fixed_values:
        for row in j:
            row[i] = 0.0
        j[i] = [0.0]*n
        j[i][i] = 1.0
        r[i] = 0.0
    return r, j


def launch(*args, **kwargs):
    raise Refusal('FEM execution unadmitted: no supervised driver or tank launch')


def advance(initial, dt, steps, step_problem, linear_solve):
    """Fixed-step BE/BDF2 loop for a future assembly adapter.

    step_problem(step, time, previous, older) returns (guess, evaluate, accept).
    It installs the new lift, uses both full historical velocities, checks the
    assembled flux compatibility before Newton, and fixes scales. accept(state)
    MUST reject nonzero eta, failed gauge/fluxes or diagnostics; it returns the
    step report. Exceptions stop without advancing history. No retry or dt change.
    """
    time_coefficients(1, dt)
    if type(steps) is not int or not 1 <= steps <= 32:
        raise Refusal('future fixture step count must be between 1 and 32')
    previous, older = list(initial), list(initial)
    reports = []
    for step in range(1, steps+1):
        guess, evaluate, accept = step_problem(step, step*dt, previous[:], older[:])
        state, history = newton(guess, evaluate, linear_solve)
        report = accept(state)
        if not isinstance(report, dict) or report.get('accepted') is not True:
            raise Refusal('step diagnostics did not explicitly accept')
        reports.append(dict(report, step=step, time=step*dt, residual_history=history))
        older, previous = previous, list(state)
    return previous, reports
