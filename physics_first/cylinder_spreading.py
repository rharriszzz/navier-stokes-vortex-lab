"""R277 radial mode sum for the stationary, shear-free water cylinder (SI)."""

import json
from dataclasses import dataclass
from math import pi

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import j0, j1, jn_zeros, jv

from physics_first.water_scales import DENSITY, VISCOSITY, scales
from realizability.reference import smooth_cutoff

WALL = 0.100
INNER = 0.030
INITIAL = scales(0.010, 0.100)
TIMES = (0.0, 1.0, 5.0)


def oseen(radius, time):
    """Infinite-column velocity and axial vorticity, including the axis limit."""
    radius = np.asarray(radius, dtype=float)
    width2 = INITIAL.gaussian_width_m**2 + 4 * VISCOSITY * time
    gamma = INITIAL.circulation_m2_s
    fraction = -np.expm1(-radius**2 / width2)
    speed = gamma / (2 * pi) * np.divide(fraction, radius, out=np.zeros_like(radius),
                                          where=radius != 0)
    return speed, gamma / (pi * width2) * np.exp(-radius**2 / width2)


def initial_swirl(radius):
    window, _ = smooth_cutoff(radius, 0.060, 0.080)
    return window * oseen(radius, 0)[0]


def radial_rule(points, end=WALL):
    """Eight-point Gauss integration on equal panels spanning [0, end]."""
    if points <= 0 or points % 8:
        raise ValueError("use a positive multiple of eight quadrature points")
    nodes, weights = np.polynomial.legendre.leggauss(8)
    panels = points // 8
    half = end / (2 * panels)
    centers = (2 * np.arange(panels) + 1) * half
    return (centers[:, None] + nodes * half).ravel(), np.tile(weights * half, panels)


@dataclass
class Expansion:
    wavenumbers: np.ndarray
    amplitudes: np.ndarray
    rigid_rate: float
    viscosity: float = VISCOSITY

    @classmethod
    def project(cls, modes, radius, weights, profile=initial_swirl):
        roots = jn_zeros(2, modes)
        k = roots / WALL
        weighted = weights * radius * profile(radius)
        norms = 0.5 * (WALL * j1(roots))**2
        amplitudes = (weighted @ j1(np.outer(radius, k))) / norms
        return cls(k, amplitudes, (weighted @ radius) / (WALL**4 / 4))

    def at_time(self, time):
        return self.amplitudes * np.exp(-self.viscosity * time * self.wavenumbers**2)

    def velocity(self, radius, amplitudes):
        return self.rigid_rate * radius + j1(np.outer(radius, self.wavenumbers)) @ amplitudes

    def vorticity(self, radius, amplitudes):
        return 2 * self.rigid_rate + j0(np.outer(radius, self.wavenumbers)) @ (
            self.wavenumbers * amplitudes)


def snapshot(series, time, points):
    amplitudes = series.at_time(time)
    scan = np.linspace(0, WALL, points + 1)
    u = series.velocity(scan, amplitudes)
    index = int(np.argmax(u))
    if not 0 < index < points:
        raise ValueError("peak at domain endpoint")

    def slope(r):
        kr = r * series.wavenumbers
        return series.rigid_rate + 0.5 * ((j0(kr) - jv(2, kr)) @
                                          (series.wavenumbers * amplitudes))

    peak = brentq(slope, scan[index - 1], scan[index + 1], xtol=1e-15)
    inner = np.linspace(0, INNER, 301)
    ref_u, ref_omega = oseen(inner, time)
    probes = []
    for end in (0.010, 0.020, INNER):
        r, w = radial_rule(points, end)
        u_probe = series.velocity(end, amplitudes).item()
        dp = DENSITY * (w @ (series.velocity(r, amplitudes)**2 / r))
        ref_dp = quad(lambda x: DENSITY * oseen(x, time)[0]**2 / x, 0, end)[0]
        probes.append(dict(radius_m=end, circulation_m2_s=2 * pi * end * u_probe,
                           pressure_above_axis_pa=dp, oseen_pressure_above_axis_pa=ref_dp))
    return dict(time_s=time, peak_radius_m=peak, peak_speed_m_s=series.velocity(peak, amplitudes).item(),
                axis_vorticity_s_inv=series.vorticity(0.0, amplitudes).item(), probes=probes,
                max_inner_speed_error_m_s=max(abs(series.velocity(inner, amplitudes) - ref_u)),
                max_inner_vorticity_error_s_inv=max(abs(series.vorticity(inner, amplitudes) - ref_omega)))


def evaluate(modes, points, dt):
    r, weights = radial_rule(points)
    series = Expansion.project(modes, r, weights)
    # Integrate shear squared in physical space, independently of kinetic-energy loss.
    k = series.wavenumbers
    kr = np.outer(r, k)
    times = np.linspace(0, 5, round(5 / dt) + 1)
    amplitudes = series.at_time(times[:, None]).T
    velocity = series.rigid_rate * r[:, None] + j1(kr) @ amplitudes
    shear = (-jv(2, kr) * k) @ amplitudes
    kinetic = pi * DENSITY * ((weights * r) @ velocity**2)
    angular = 2 * pi * DENSITY * ((weights * r**2) @ velocity)
    power = 2 * pi * DENSITY * VISCOSITY * ((weights * r) @ shear**2)
    energy_loss = kinetic[0] - kinetic[-1]
    dissipated = np.trapezoid(power, times)
    scan = np.linspace(0, WALL, 4097)
    init_error = series.velocity(scan, series.amplitudes) - initial_swirl(scan)
    records = []
    for t in TIMES:
        idx = int(round(t / dt))
        row = snapshot(series, t, points)
        row.update(kinetic_J_per_m=kinetic[idx], angular_kg_m_per_s=angular[idx],
                   dissipation_W_per_m=power[idx],
                   cumulative_dissipation_J_per_m=np.trapezoid(power[:idx + 1], times[:idx + 1]))
        records.append(row)
    return dict(modes=modes, radial_points=points, time_spacing_s=dt, snapshots=records,
                max_initial_speed_error_m_s=max(abs(init_error)), rigid_rate_s_inv=series.rigid_rate,
                kinetic_loss_J_per_m=energy_loss, dissipation_J_per_m=dissipated,
                residual_J_per_m=dissipated - energy_loss,
                max_relative_angular_drift=max(abs(angular - angular[0])) / abs(angular[0]))


def compare_fine_pair(coarser, fine):
    pairs = list(zip(coarser["snapshots"], fine["snapshots"], strict=True))
    loss = fine["kinetic_loss_J_per_m"]
    if loss <= 0:
        raise ValueError("a dissipating benchmark requires a positive kinetic-energy loss")
    return dict(
        max_peak_change_m=max(abs(a["peak_radius_m"] - b["peak_radius_m"]) for a, b in pairs),
        max_pressure_change_pa=max(abs(a["probes"][-1]["pressure_above_axis_pa"] -
                                       b["probes"][-1]["pressure_above_axis_pa"]) for a, b in pairs),
        integrated_dissipation_change_fraction=abs(coarser["dissipation_J_per_m"] -
                                                   fine["dissipation_J_per_m"]) / loss,
        balance_change_fraction=abs(coarser["residual_J_per_m"] - fine["residual_J_per_m"]) / loss,
    )


def experiment():
    # Three one-factor studies sharing the finest run.
    runs = [evaluate(n, 2048, 0.025) for n in (32, 64)]
    runs += [evaluate(128, p, 0.025) for p in (512, 1024)]
    runs += [evaluate(128, 2048, dt) for dt in (0.1, 0.05, 0.025)]
    fine = runs[-1]
    comparisons = {name: compare_fine_pair(run, fine) for name, run in
                   zip(("modes", "radius", "time"), (runs[1], runs[3], runs[5]), strict=True)}
    limits = dict(max_peak_change_m=0.000020, max_pressure_change_pa=0.05,
                  integrated_dissipation_change_fraction=0.005, balance_change_fraction=0.005)
    checks = {name: all(measured[key] <= limit for key, limit in limits.items())
              for name, measured in comparisons.items()}
    checks.update(energy=abs(fine["residual_J_per_m"]) / fine["kinetic_loss_J_per_m"] < 0.005,
                  angular=fine["max_relative_angular_drift"] < 1e-6,
                  final_radius=abs(fine["snapshots"][-1]["peak_radius_m"] - 0.01119) <= 0.00005)
    inputs = dict(cylinder_radius_m=WALL, axial_period_m=0.10, rho_kg_m3=DENSITY,
                  nu_m2_s=VISCOSITY, reference_temperature_K=293.15, initial_wall_pressure_Pa=101325,
                  initial_peak_radius_m=INITIAL.peak_radius_m, initial_peak_speed_m_s=INITIAL.peak_speed_m_s)
    return dict(inputs=inputs, runs=runs, fine_pair_changes=comparisons, checks=checks,
                passed=all(checks.values()))


if __name__ == "__main__":
    report = experiment()
    print(json.dumps(report, indent=2, allow_nan=False, default=lambda value: value.item()))
    raise SystemExit(0 if report["passed"] else 1)
