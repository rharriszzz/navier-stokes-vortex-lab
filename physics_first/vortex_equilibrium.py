"""Time-zero centrifugal balance of the R277 finite-cylinder swirl (SI)."""

import argparse
from dataclasses import dataclass
import json
from pathlib import Path

import CoolProp
import CoolProp.CoolProp as CP
import numpy as np
from scipy.integrate import quad

from physics_first.acoustic_initial_state import P0, T0
from physics_first.cylinder_spreading import INITIAL, INNER, WALL, initial_swirl

EVIDENCE = Path(__file__).resolve().parents[1] / "docs" / "physics-first"
LEVELS = (16, 32, 64)


def centrifugal(radius, speed):
    """u_theta²/r; a smooth odd swirl gives zero acceleration at the axis."""
    return np.divide(speed**2, radius, out=np.zeros_like(radius, dtype=float), where=radius != 0)


def liquid_at_pt(eos, pressure):
    eos.update(CP.PT_INPUTS, pressure, T0)
    if eos.phase() != CP.iphase_liquid:
        raise ValueError(f"nonliquid PT state at {pressure} Pa")


@dataclass
class Profile:
    r: np.ndarray
    p: np.ndarray
    u: np.ndarray
    e: np.ndarray
    # Columns are density, radial/azimuthal/axial momentum densities and rho*E.
    conserved: np.ndarray
    recovered_p: np.ndarray
    recovered_T: np.ndarray


def recover(conserved):
    """Flash only the stored mass, three momenta and total energy."""
    eos = CP.AbstractState("HEOS", "Water")
    pressure, temperature = np.empty((2, len(conserved)))
    for i, row in enumerate(conserved):
        rho = row[0]
        velocity = row[1:4] / rho
        e = row[4] / rho - 0.5 * (velocity @ velocity)
        eos.update(CP.DmassUmass_INPUTS, rho, e)
        if eos.phase() != CP.iphase_liquid:
            raise ValueError(f"nonliquid recovered state at node {i}")
        pressure[i], temperature[i] = eos.p(), eos.T()
    return pressure, temperature


def initial_state(cells_per_core):
    """Inward explicit midpoint integration in radius on a uniform nodal grid."""
    if not isinstance(cells_per_core, int) or cells_per_core < 1:
        raise ValueError("cells per core must be a positive integer")
    r = np.linspace(0, WALL, round(WALL / INITIAL.peak_radius_m) * cells_per_core + 1)
    h = r[1]
    mid = (r[1:] + r[:-1]) / 2
    u = initial_swirl(r)
    accel = centrifugal(r, u)
    accel_mid = centrifugal(mid, initial_swirl(mid))
    eos = CP.AbstractState("HEOS", "Water")
    p, rho, e = np.empty((3, len(r)))
    p[-1] = P0
    for i in reversed(range(len(r))):
        liquid_at_pt(eos, p[i])
        rho[i], e[i] = eos.rhomass(), eos.umass()
        if i > 0:
            liquid_at_pt(eos, p[i] - 0.5 * h * rho[i] * accel[i])
            p[i-1] = p[i] - h * eos.rhomass() * accel_mid[i-1]

    q = np.zeros((len(r), 5))
    q[:, 0], q[:, 2], q[:, 4] = rho, rho * u, rho * (e + 0.5 * u**2)
    recovered_p, recovered_T = recover(q)
    for values in (r, u, p, e, q, recovered_p, recovered_T):
        if not np.isfinite(values).all():
            raise ValueError("nonfinite initial state")
    return Profile(r, p, u, e, q, recovered_p, recovered_T)


def integral_check(p_axis, p_outer, outer_radius):
    """Integrate in thermodynamic pressure and in geometric radius independently."""
    eos = CP.AbstractState("HEOS", "Water")

    def specific_volume(p):
        liquid_at_pt(eos, p)
        return 1.0 / eos.rhomass()

    lhs = quad(specific_volume, p_axis, p_outer, epsabs=1e-14)[0]
    breaks = [x for x in (0.060, 0.080) if x < outer_radius]
    rhs = quad(lambda r: initial_swirl(r)**2 / r, 0, outer_radius,
               points=breaks, epsabs=1e-14, epsrel=1e-12)[0]
    return dict(dp_over_rho_m2_s2=lhs, swirl_integral_m2_s2=rhs, defect_m2_s2=lhs-rhs)


def even_gradient(pressure, end, spacing):
    """Centered on nodes 0..end. Mirror at zero and use the real neighbor past end."""
    gradient = np.zeros(end + 1)
    gradient[1:] = (pressure[2:end+2] - pressure[:end]) / (2 * spacing)
    return gradient


def radial_balance(profile, end, pressure):
    """Centered pressure difference, even extension at the axis, radial dr norm."""
    r = profile.r[:end+1]
    rho = profile.conserved[:end+1, 0]
    u_theta = profile.conserved[:end+1, 2] / rho
    grad_p = even_gradient(pressure, end, r[1])
    defect = grad_p - rho * centrifugal(r, u_theta)
    acceleration = -defect / rho

    def metrics(values):
        idx = np.argmax(abs(values))
        return dict(peak_abs=max(abs(values)), signed_at_peak=values[idx], radius_m=r[idx],
                    radial_rms=np.sqrt(np.trapezoid(values**2, r) / r[-1]))

    return dict(force_Pa_m=metrics(defect), acceleration_m_s2=metrics(acceleration))


def measure(profile, n, benchmark):
    end = round(INNER / INITIAL.peak_radius_m) * n
    rise = profile.p[end] - profile.p[0]
    delta = profile.recovered_p - profile.p
    r = profile.r[:end+1]
    grad_delta = even_gradient(delta, end, r[1])
    recovery_gradient_rms = np.sqrt(np.trapezoid(grad_delta**2, r) / r[-1])
    return dict(cells_per_core=n, nodes=len(profile.r), dr_m=profile.r[1], axis_pressure_Pa=profile.p[0],
                rise_30mm_Pa=rise, rise_error_Pa=rise-benchmark,
                max_pressure_roundtrip_Pa=max(abs(profile.recovered_p - profile.p)),
                max_temperature_roundtrip_K=max(abs(profile.recovered_T - T0)),
                liquid_nodes_PT=len(profile.r), liquid_nodes_recovered=len(profile.r),
                inner_identity=integral_check(profile.p[0], profile.p[end], INNER),
                cylinder_identity=integral_check(profile.p[0], profile.p[-1], WALL),
                balance=radial_balance(profile, end, profile.recovered_p),
                prescribed_pressure_balance=radial_balance(profile, end, profile.p),
                recovery_gradient_rms_Pa_m=recovery_gradient_rms)


def experiment(csv_path=None):
    baseline = json.loads((EVIDENCE / "spreading_results.json").read_text())
    probe = baseline["runs"][-1]["snapshots"][0]["probes"][-1]
    if probe["radius_m"] != INNER:
        raise ValueError("R277 comparison radius differs from the equilibrium probe")
    ref = probe["pressure_above_axis_pa"]
    eos = CP.AbstractState("HEOS", "Water")
    liquid_at_pt(eos, P0)
    rho_wall = eos.rhomass()
    benchmark = ref * rho_wall / baseline["inputs"]["rho_kg_m3"]
    rows = []
    for n in LEVELS:
        profile = initial_state(n)
        rows.append(measure(profile, n, benchmark))
    if csv_path:
        columns = np.column_stack((profile.r, profile.u, profile.p, profile.e, profile.conserved,
                                   profile.recovered_p, profile.recovered_T))
        np.savetxt(csv_path, columns, delimiter=",", comments="", fmt="%.17g",
                   header="r_m,u_theta_m_s,p_Pa,e_J_kg,rho_kg_m3,mr_kg_m2_s,mtheta_kg_m2_s,"
                          "mz_kg_m2_s,rhoE_J_m3,recovered_p_Pa,recovered_T_K")

    errors = dict(pressure=[row["rise_error_Pa"] for row in rows],
                  inner_identity=[row["inner_identity"]["defect_m2_s2"] for row in rows],
                  cylinder_identity=[row["cylinder_identity"]["defect_m2_s2"] for row in rows],
                  prescribed_force_rms=[row["prescribed_pressure_balance"]["force_Pa_m"]["radial_rms"]
                                        for row in rows],
                  recovered_force_rms=[row["balance"]["force_Pa_m"]["radial_rms"] for row in rows])
    orders = {name: np.log2(np.abs(np.array(vals[:-1]) / vals[1:])).tolist()
              for name, vals in errors.items()}
    checks = dict(pressure_rise=all(abs(x) < 0.05 for x in errors["pressure"]),
                  pressure_recovery=all(row["max_pressure_roundtrip_Pa"] < 0.01 for row in rows),
                  acceleration=all(row["balance"]["acceleration_m_s2"]["radial_rms"] < 0.01
                                   for row in rows),
                  second_order=all(1.8 < order < 2.2 for pair in orders.values() for order in pair))
    return dict(eos="HEOS::Water", coolprop=CoolProp.__version__, wall_pressure_Pa=P0,
                temperature_K=T0, wall_density_kg_m3=rho_wall, R277_rise_Pa=ref,
                adjusted_benchmark_Pa=benchmark, runs=rows, observed_orders=orders,
                checks=checks, passed=all(checks.values()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, help="write the finest radial state in SI units")
    report = experiment(parser.parse_args().csv)
    print(json.dumps(report, indent=2, allow_nan=False))
    raise SystemExit(0 if report["passed"] else 1)
