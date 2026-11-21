"""Constant-property viscous swirl in a stationary no-slip circular cylinder (SI)."""

import json

import numpy as np
from scipy.optimize import brentq
from scipy.special import j0, j1, jn_zeros, jv

from physics_first.acoustic_initial_state import background
from physics_first.cylinder_spreading import (
    Expansion, INITIAL, INNER, WALL, initial_swirl, radial_rule,
)


def project(modes, r, weights, profile=initial_swirl):
    roots = jn_zeros(1, modes)
    k = roots / WALL
    norm = (WALL * j0(roots))**2 / 2
    amplitudes = ((weights * r * profile(r)) @ j1(np.outer(r, k))) / norm
    props = background()
    return Expansion(k, amplitudes, 0.0, props["mu_Pa_s"] / props["rho_kg_m3"])


def evaluate(modes, points):
    props = background()
    rho = props["rho_kg_m3"]
    nu = props["mu_Pa_s"] / rho
    r, w = radial_rule(points)
    series = project(modes, r, w)
    k = series.wavenumbers
    kr = np.outer(r, k)
    inner, wi = radial_rule(points, INNER)
    rows = []
    for time in (0, .001, .020):
        a = series.at_time(time)
        u = series.velocity(r, a)
        shear = -jv(2, kr) @ (k * a)
        peak = brentq(lambda x: (j0(k*x) - jv(2, k*x)) @ (k*a), .009, .012)
        width2 = INITIAL.gaussian_width_m**2 + 4*nu*time
        gamma = INITIAL.circulation_m2_s
        ui = series.velocity(inner, a)
        acceleration = series.velocity(inner, -nu * k**2 * a)
        rows.append(dict(time_s=time, peak_m=peak, speed_m_s=series.velocity(peak, a).item(),
                         axis_omega_s=series.vorticity(0, a).item(),
                         rise_Pa=rho * (wi @ (ui**2 / inner)),
                         energy_J_m=np.pi*rho * (w @ (r*u**2)),
                         dissipation_W_m=2*np.pi*rho*nu * (w @ (r*shear**2)),
                         wall_speed_m_s=series.velocity(WALL, a).item(),
                         wall_torque_per_length_N=-2*np.pi*rho*nu*WALL**2 * (jv(2, WALL*k) @ (k*a)),
                         angular_rate_N=2*np.pi*rho*(w @ (r**2 * series.velocity(r, -nu*k**2*a))),
                         max_inner_oseen_speed_error_m_s=float(max(abs(
                             ui + gamma*np.expm1(-inner**2/width2)/(2*np.pi*inner)))),
                         max_inner_oseen_omega_error_s=float(max(abs(series.vorticity(inner, a)
                             - gamma*np.exp(-inner**2/width2)/(np.pi*width2)))),
                         max_inner_oseen_viscous_acc_error_m_s2=float(max(abs(acceleration
                             + 2*nu*gamma*inner*np.exp(-inner**2/width2)/(np.pi*width2**2)))) ))
    return dict(modes=modes, points=points, nu_m2_s=nu, snapshots=rows)


if __name__ == "__main__":
    print(json.dumps([evaluate(n, p) for n, p in ((128, 2048), (256, 2048), (256, 4096))],
                     indent=2, allow_nan=False))
