"""Measure R284 shear damping and thermodynamic leakage from sparse SU2 restarts."""

import argparse
import csv
import json
from pathlib import Path

import CoolProp.CoolProp as CP
import numpy as np

from physics_first.acoustic_initial_state import background
from physics_first.su2_acoustic import FIELDS, read_restart
from physics_first.su2_shear import AMPLITUDE, CASES, HEIGHT, LENGTH, NY

K = 2 * np.pi / LENGTH


def fit_decay(times, amplitudes):
    log_ratio = np.log(np.asarray(amplitudes) / amplitudes[0])
    # Scaling the abscissa also makes the intercept well-conditioned.
    slope, _ = np.polyfit(times / times[-1], log_ratio, 1)
    return -slope / (times[-1] * K**2), -np.diff(log_ratio) / (np.diff(times) * K**2)


def thermodynamics(q, base, state):
    temperatures = []
    pressures = []
    for density, mx, my, energy in q:
        internal = energy / density - 0.5 * ((mx / density)**2 + (my / density)**2)
        state.update(CP.DmassUmass_INPUTS, density, internal)
        if state.phase() != CP.iphase_liquid:
            raise ValueError("non-liquid conservative state")
        pressures.append(state.p() - base["pressure_pa"])
        temperatures.append(state.T() - base["temperature_K"])
    return np.array(pressures), np.array(temperatures)


def measure(directory, cells, steps, base):
    state = CP.AbstractState("HEOS", "Water")
    start = read_restart(directory / "state_00000.dat")
    x, y = start["x"], start["y"]
    shape = NY + 1, cells + 1
    np.testing.assert_allclose(x.reshape(shape), np.tile(np.linspace(0, LENGTH, cells + 1),
                               (NY + 1, 1)), rtol=2e-15, atol=0)
    np.testing.assert_allclose(y, np.repeat(np.linspace(0, HEIGHT, NY + 1), cells + 1),
                               rtol=2e-15, atol=0)
    # Fractions of the box volume at vertices, including both periodic cuts.
    weights = np.where((x == 0) | (x == LENGTH), 0.5, 1.0)
    weights *= np.where((y == 0) | (y == HEIGHT), 0.5, 1.0) / (NY * cells)
    np.testing.assert_allclose(weights.sum(), 1.0)
    phase = np.exp(-1j * K * x)
    q0 = np.column_stack([start[name] for name in FIELDS[2:]])
    rho0 = base["rho_kg_m3"]
    np.testing.assert_array_equal(q0[:, 0], rho0)
    np.testing.assert_array_equal(q0[:, 1], 0)
    np.testing.assert_allclose(q0[:, 2] / rho0, AMPLITUDE * np.sin(K * x), atol=2e-17)
    np.testing.assert_allclose(q0[:, 3], rho0 * (base["internal_energy_J_kg"]
                               + 0.5 * (q0[:, 2] / rho0)**2), rtol=2e-16)
    dt = 8 * LENGTH / (base["sound_speed_m_s"] * steps)
    snapshots = []
    for step in range(0, steps + 1, steps // 4):
        record = read_restart(directory / f"state_{step:05d}.dat")
        np.testing.assert_array_equal(record["x"], x)
        np.testing.assert_array_equal(record["y"], y)
        q = np.column_stack([record[name] for name in FIELDS[2:]])
        # Both copies of each seam must carry the same conservative state.
        grid = q.reshape(*shape, 4)
        np.testing.assert_array_equal(grid[0], grid[-1])
        np.testing.assert_array_equal(grid[:, 0], grid[:, -1])
        rho, mx, my, energy = q.T
        u, v = mx / rho, my / rho
        mode = 2 * np.dot(weights, v * phase)
        other = v - np.real(mode * phase.conj())
        dp, dT = thermodynamics(q, base, state)
        change = q.astype(np.longdouble) - q0
        drift = np.sum(weights[:, None] * change, axis=0)
        ke = weights @ (0.5 * (mx*u + my*v))
        snapshot = dict(step=step, time_s=step*dt, amplitude_m_s=abs(mode),
                        phase_rad=np.angle(mode), transverse_off_mode_rms_m_s=np.sqrt(weights @ other**2),
                        max_y_variation_v_m_s=np.ptp(v.reshape(shape), axis=0).max(),
                        longitudinal_max_m_s=abs(u).max(), longitudinal_rms_m_s=np.sqrt(weights @ u**2),
                        pressure_change_min_mean_max_Pa=[dp.min(), weights @ dp, dp.max()],
                        pressure_rms_about_mean_Pa=np.sqrt(weights @ (dp - weights @ dp)**2),
                        pressure_max_y_range_Pa=np.ptp(dp.reshape(shape), axis=0).max(),
                        T_change_min_mean_max_K=[dT.min(), weights @ dT, dT.max()],
                        max_density_change_kg_m3=abs(rho-rho0).max(),
                        kinetic_J_m3=ke, mean_conserved_change_from_start=drift.astype(float).tolist(),
                        shifted_energy_change_J_m3=float(drift[3] - base["internal_energy_J_kg"] * drift[0]))
        if step:
            # SU2 sums periodic copies for the last RK stage. Each assembled
            # update therefore uses a full dx*dy dual volume, including seams.
            full_volume = LENGTH * HEIGHT / (NY * cells)
            dvdt = -(record["Residual_Momentum_y"] - v * record["Residual_Density"]) / (rho * full_volume)
            mode_rate = 2 * np.dot(weights, dvdt * phase)
            snapshot["residual_modal_nu_m2_s"] = -(mode_rate / mode).real / K**2
            peak = int(np.argmax(abs(dp)))
            snapshot["max_abs_dp_location_xy_m"] = [x[peak], y[peak]]
            snapshot["su2_primitive_max_pressure_difference_Pa"] = abs(
                record["Pressure"] - base["pressure_pa"] - dp).max()
            snapshot["su2_primitive_max_temperature_difference_K"] = abs(
                record["Temperature"] - base["temperature_K"] - dT).max()
        snapshots.append(snapshot)
    times = np.array([s["time_s"] for s in snapshots])
    amplitudes = np.array([s["amplitude_m_s"] for s in snapshots])
    energies = np.array([s["kinetic_J_m3"] for s in snapshots])
    fitted, intervals = fit_decay(times, amplitudes)
    energy_fit, _ = fit_decay(times, np.sqrt(energies))
    nu = base["mu_Pa_s"] / rho0
    return dict(cells=cells, steps=steps, dt_s=dt, axial_acoustic_CFL=base["sound_speed_m_s"]*dt*cells/LENGTH,
                nu_fit_m2_s=fitted, nu_excess_m2_s=fitted-nu, excess_pct=100*(fitted/nu-1),
                equivalent_mu_Pa_s=fitted*rho0, interval_nu_m2_s=intervals.tolist(),
                interval_spread_over_nu=np.ptp(intervals)/nu, kinetic_energy_fit_m2_s=energy_fit,
                snapshots=snapshots)


def check_history(directory, steps, dt):
    with (directory / "history_00001.csv").open() as history:
        reader = csv.reader(history, skipinitialspace=True)
        fields = [column.strip() for column in next(reader)]
        records = list(reader)
    indices = [int(row[fields.index("Time_Iter")]) for row in records]
    times = [float(row[fields.index("Cur_Time")]) for row in records]
    np.testing.assert_array_equal(indices, np.arange(1, steps + 1))
    np.testing.assert_allclose(times, dt * np.arange(1, steps + 1), atol=0, rtol=1e-9)
    if "Exit Success (SU2_CFD)" not in (directory / "solver.log").read_text():
        raise ValueError(f"missing successful solver exit in {directory}")


def summarize(root):
    base = background()
    rho = base["rho_kg_m3"]
    nu = base["mu_Pa_s"] / rho
    end_time = 8 * LENGTH / base["sound_speed_m_s"]
    predicted_ratio = np.exp(-nu * K**2 * end_time)
    state = CP.AbstractState("HEOS", "Water")
    state.update(CP.PT_INPUTS, base["pressure_pa"], base["temperature_K"])
    # Leading box-average heating in a closed, fixed volume.
    heating = AMPLITUDE**2 / 4 * (1 - predicted_ratio**2) / state.cvmass()
    dp_dT = state.first_partial_deriv(CP.iP, CP.iT, CP.iDmass)
    runs = [measure(root / f"n{n}-t{s}", n, s, base) for n, s in CASES]
    fine_final = read_restart(root / "n64-t4096" / "state_04096.dat")
    q = np.column_stack([fine_final[k] for k in FIELDS[2:]])
    dp, _ = thermodynamics(q, base, state)
    profile = dict(x_m=fine_final["x"].reshape(NY + 1, -1)[0].tolist(),
                   lower_quarter_dp_Pa=dp.reshape(NY + 1, -1)[1].tolist(),
                   upper_quarter_dp_Pa=dp.reshape(NY + 1, -1)[3].tolist())
    for run in runs:
        check_history(root / f"n{run['cells']}-t{run['steps']}", run["steps"], run["dt_s"])
    coarse, fine, half = (r["nu_fit_m2_s"] for r in runs)
    checks = dict(fine_half_accuracy=abs(half / nu - 1) <= 0.10,
                  grid_change=abs(coarse-fine) / nu < 0.05,
                  timestep_change=abs(fine-half) / nu < 0.05,
                  interval_spread=max(r["interval_spread_over_nu"] for r in runs) < 0.05)
    return dict(base=base, physical_nu_m2_s=nu, wavenumber_rad_m=K, end_time_s=end_time,
                predicted_final_ratio=predicted_ratio, expected_mean_heat_K=heating,
                expected_mean_thermal_pressure_Pa=heating*dp_dT, isochoric_dp_dT_Pa_K=dp_dT,
                energy_density_ulp_J_m3=np.spacing(rho * base["internal_energy_J_kg"]),
                grid_change_over_nu=abs(coarse-fine)/nu, timestep_change_over_nu=abs(fine-half)/nu,
                conserved_change_columns=["density [kg/m3]", "x momentum density [kg/(m2 s)]",
                                          "y momentum density [kg/(m2 s)]", "total energy density [J/m3]"],
                fine_final_pressure_profile=profile, runs=runs, checks={name: bool(passed) for name, passed in checks.items()})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    result = summarize(args.root)
    print(json.dumps(result, indent=2, allow_nan=False))
    raise SystemExit(0 if all(result["checks"].values()) else 1)
