"""Measure the acoustic mode and signed finite-volume budgets from SU2 restarts."""

import argparse
import json
from math import pi
from pathlib import Path

import CoolProp.CoolProp as CP
import numpy as np

from physics_first.acoustic_initial_state import AMPLITUDE, LENGTH, P0, background
from physics_first.su2_acoustic import FIELDS, HEIGHT, NY, read_restart

CONSERVED = FIELDS[2:]


def wave(q, weights, angles, base, state):
    # Reconstruct endpoint pressure from the saved conservative variables.
    pressure, temperature = [], []
    for rho, mx, my, energy in q:
        kinetic = 0.5 * ((mx / rho)**2 + (my / rho)**2)
        state.update(CP.DmassUmass_INPUTS, rho, energy / rho - kinetic)
        if state.phase() != CP.iphase_liquid:
            raise ValueError("endpoint is outside single-phase liquid")
        pressure.append(state.p() - P0)
        temperature.append(state.T())
    dp = np.asarray(pressure)
    rho0, c = base["rho_kg_m3"], base["sound_speed_m_s"]
    mean = np.dot(weights, dp) / LENGTH
    mode = 2 * np.dot(weights, (dp - mean) * np.exp(-1j * angles)) / LENGTH
    velocity2 = (q[:, 1]**2 + q[:, 2]**2) / q[:, 0]**2
    energy = np.dot(weights, dp**2 / (2 * rho0 * c**2) + rho0 * velocity2 / 2)
    inventory = np.sum(weights[:, None] * q.astype(np.longdouble), axis=0)
    return dict(mass_kg_per_m2=float(inventory[0]), momentum_per_area=inventory[1:3].astype(float).tolist(),
                total_energy_J_per_m2=float(inventory[3]), amplitude_pa=abs(mode), phase_rad=np.angle(mode), mean_dp_pa=mean,
                wave_energy_J_per_m2=energy, pressure_range_pa=[min(dp)+P0, max(dp)+P0],
                density_range_kg_m3=[min(q[:, 0]), max(q[:, 0])],
                temperature_range_K=[min(temperature), max(temperature)])


def shifted(integral, e0):
    mass, mx, my, energy = integral
    return np.array([mass, mx, my, energy - e0 * mass], dtype=np.longdouble)


def measure(directory, cells, steps):
    base = background()
    state = CP.AbstractState("HEOS", "Water")
    first = read_restart(directory / "state_00000.dat")
    x, y = first["x"], first["y"]
    dx = LENGTH / cells
    dt = LENGTH / (base["sound_speed_m_s"] * steps)
    # Duplicated periodic end vertices share their combined dual volume.
    seam_weight = np.where((x == 0) | (x == LENGTH), 0.5, 1.0)
    transverse = np.where((y == 0) | (y == HEIGHT), 0.5, 1.0)
    weights = dx * transverse * seam_weight / NY
    np.testing.assert_allclose(weights.sum(), LENGTH, rtol=1e-14)
    angles = 2*pi * (x / LENGTH + 0.5 / cells)
    start = np.column_stack([first[k] for k in CONSERVED])
    snapshots = [dict(step=0, time_s=0.0, **wave(start, weights, angles, base, state))]
    interval_start = start
    e0 = base["internal_energy_J_kg"]
    net_out = np.zeros(4, dtype=np.longdouble)
    previous = start
    max_update_error = np.zeros(4)
    intervals = []
    for step in range(1, steps + 1):
        record = read_restart(directory / f"state_{step:05d}.dat")
        if not (np.array_equal(x, record["x"]) and np.array_equal(y, record["y"])):
            raise ValueError("mesh/output ordering mismatch")
        q = np.column_stack([record[k] for k in CONSERVED])
        residual = np.column_stack([record["Residual_" + k] for k in CONSERVED])
        # With the (1/2, 1) midpoint RK update, the last assembled residual
        # is the flux rate used for the entire physical step (no body source).
        effective_volume = (dx * HEIGHT / NY) * transverse
        prediction = -dt * residual / effective_volume[:, None]
        max_update_error = np.maximum(max_update_error, np.max(abs((q - previous) - prediction), axis=0))
        summed = np.sum(seam_weight[:, None] * residual.astype(np.longdouble), axis=0)
        net_out += shifted(summed, e0) * (dt / HEIGHT)
        previous = q
        if step % (steps // 4) == 0:
            delta = np.sum(weights[:, None] * (q - interval_start).astype(np.longdouble), axis=0)
            storage = shifted(delta, e0)
            intervals.append(dict(end_step=step, storage_change=storage.astype(float).tolist(),
                                  net_outward_impulse=net_out.astype(float).tolist(),
                                  defect=(storage + net_out).astype(float).tolist()))
            interval_start = q
            net_out.fill(0)
            snapshots.append(dict(step=step, time_s=step * dt, **wave(q, weights, angles, base, state)))
    phase = np.unwrap([s["phase_rad"] for s in snapshots])
    speed_ratio = (phase[0] - phase[-1]) / (2*pi)
    last, initial = snapshots[-1], snapshots[0]
    defects = np.abs([i["defect"] for i in intervals])
    wave_energy = initial["wave_energy_J_per_m2"]
    mass = base["rho_kg_m3"] * LENGTH
    speed = AMPLITUDE / (base["rho_kg_m3"] * base["sound_speed_m_s"])
    return dict(cells=cells, steps=steps, dt_s=dt, acoustic_cfl=cells/steps,
                measured_phase_speed_m_s=speed_ratio * base["sound_speed_m_s"],
                speed_error_pct=100 * (speed_ratio - 1),
                amplitude_error_pct=100 * (last["amplitude_pa"] / AMPLITUDE - 1),
                amplitude_change_pct=100 * (last["amplitude_pa"] / initial["amplitude_pa"] - 1),
                relative_mass_defect_max=defects[:, 0].max() / mass,
                relative_momentum_defect_max=np.linalg.norm(defects[:, 1:3], axis=1).max() / (mass*speed),
                shifted_energy_defect_over_wave_energy_max=defects[:, 3].max() / wave_energy,
                max_local_update_discrepancy=max_update_error.tolist(),
                snapshots=snapshots, budget_intervals=intervals)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("cells", type=int)
    parser.add_argument("steps", type=int)
    args = parser.parse_args()
    print(json.dumps(measure(args.directory, args.cells, args.steps), indent=2, allow_nan=False))
