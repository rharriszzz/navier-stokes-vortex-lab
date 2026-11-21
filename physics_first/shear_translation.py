"""Prepare and compare the single R285 translation against the archived R284 case."""

import argparse
import json
from pathlib import Path

import CoolProp.CoolProp as CP
import numpy as np

from physics_first.measure_shear import check_history, measure, thermodynamics
from physics_first.su2_acoustic import FIELDS, read_restart
from physics_first.su2_shear import AMPLITUDE, HEIGHT, LENGTH, NY, background, make_case

NX, STEPS, SHIFT = 64, 2048, 16
CONSERVED = FIELDS[2:]


def unique_grid(record, fields):
    shape = NY + 1, -1
    grid = np.stack([record[k].reshape(shape) for k in fields], axis=-1)
    np.testing.assert_array_equal(grid[:, 0], grid[:, -1])
    np.testing.assert_array_equal(grid[0], grid[-1])
    return grid[:-1, :-1]


def audit_mesh(path, coordinates, cells=NX):
    """Check actual quads, oriented boundary edges, unique donors and dual areas."""
    lines = iter(path.read_text().splitlines())

    def header(key):
        name, value = next(lines).split("=")
        if name != key:
            raise ValueError(f"expected {key}, found {name}")
        return value.strip()

    if header("NDIME") != "2" or int(header("NELEM")) != cells * NY:
        raise ValueError("unexpected strip topology")
    quads = np.array([next(lines).split() for _ in range(cells * NY)], dtype=int)
    np.testing.assert_array_equal(quads[:, 0], 9)
    a = np.arange(cells * NY).reshape(NY, cells) + np.arange(NY)[:, None]
    expected = np.stack((a, a+1, a+cells+2, a+cells+1), axis=-1)
    np.testing.assert_array_equal(quads[:, 1:], expected.reshape(-1, 4))
    count = int(header("NPOIN"))
    nodes = np.array([next(lines).split() for _ in range(count)], dtype=float)
    np.testing.assert_array_equal(nodes[:, 2], np.arange(count))
    xy = nodes[:, :2]
    np.testing.assert_array_equal(xy, coordinates)
    markers = {}
    for _ in range(int(header("NMARK"))):
        name = header("MARKER_TAG")
        edges = np.array([next(lines).split() for _ in range(int(header("MARKER_ELEMS")))], dtype=int)
        np.testing.assert_array_equal(edges[:, 0], 3)
        markers[name] = edges[:, 1:]
    if set(markers) != {"left", "right", "bottom", "top"}:
        raise ValueError("expected two pairs of periodic markers")
    shape = NY + 1, cells + 1
    ids = np.arange(count).reshape(shape)
    for source, target, offset, ordered in [
        ("left", "right", [LENGTH, 0], ids[:, 0][::-1]),
        ("bottom", "top", [0, HEIGHT], ids[0]),
    ]:
        # Opposite marker edges have opposite orientations. The source edge
        # list need not be sorted in traversal order.
        left = markers[source]
        expected_edges = set(zip(ordered[:-1], ordered[1:]))
        if set(map(tuple, left)) != expected_edges or len(left) != len(expected_edges):
            raise ValueError(f"incorrect edges on {source}")
        right = markers[target]
        donor_ids = np.unique(right)
        matches = np.all((xy[ordered] + offset)[:, None] == xy[donor_ids], axis=-1)
        np.testing.assert_array_equal(matches.sum(axis=0), 1)
        np.testing.assert_array_equal(matches.sum(axis=1), 1)
        donor = donor_ids[matches.argmax(axis=1)]
        if set(map(tuple, right)) != set(zip(donor[1:], donor[:-1])) or len(right) != len(left):
            raise ValueError(f"incorrect donor orientation on {target}")
    # Four rectangle quarters contribute to every identified torus vertex.
    corners = quads[:, 1:]
    widths = xy[corners[:, 1], 0] - xy[corners[:, 0], 0]
    heights = xy[corners[:, 3], 1] - xy[corners[:, 0], 1]
    dual = np.zeros(count)
    np.add.at(dual, corners, (widths * heights / 4)[:, None])
    dual = dual.reshape(shape)
    merged = np.zeros((NY, cells))
    j, i = np.indices(shape)
    np.add.at(merged, (j % NY, i % cells), dual)
    ideal = LENGTH * HEIGHT / (cells * NY)
    np.testing.assert_allclose(merged, ideal, rtol=1e-14, atol=0)
    return dict(axial_donor_pairs=NY+1, transverse_donor_pairs=cells+1,
                unique_nodes=merged.size, corner_ids=ids[np.ix_([0, -1], [0, -1])].ravel().tolist(),
                geometric_corner_dual_areas_m2=dual[np.ix_([0, -1], [0, -1])].ravel().tolist(),
                merged_dual_area_range_m2=[merged.min(), merged.max()])


def audit_inputs(original, shifted, cells=NX):
    for name in ("line.su2", "wave.cfg"):
        if (original / name).read_bytes() != (shifted / name).read_bytes():
            raise ValueError(f"archive mismatch for {name}")
    a, b = (read_restart(d / "state_00000.dat") for d in (original, shifted))
    xy = np.column_stack([b["x"], b["y"]])
    np.testing.assert_array_equal(xy, np.column_stack([a["x"], a["y"]]))
    result = audit_mesh(original / "line.su2", xy, cells)
    ref, translated = (unique_grid(r, CONSERVED) for r in (a, b))
    np.testing.assert_array_equal(ref.view(np.uint64), np.roll(translated, -(cells // 4), axis=1).view(np.uint64))
    base = background()
    rho, mx, my, energy = translated.reshape(-1, 4).T
    np.testing.assert_array_equal(rho, base["rho_kg_m3"])
    np.testing.assert_array_equal(mx, 0)
    v = AMPLITUDE * np.sin(2*np.pi*(np.arange(cells)-cells//4)/cells)
    np.testing.assert_allclose((my/rho).reshape(NY, cells), np.tile(v, (NY, 1)), atol=2e-17)
    np.testing.assert_allclose(energy, rho*(base["internal_energy_J_kg"] + 0.5*(my/rho)**2), rtol=2e-16)
    dp, dT = thermodynamics(translated.reshape(-1, 4), base, CP.AbstractState("HEOS", "Water"))
    result.update(initial_max_abs_dp_Pa=abs(dp).max(), initial_max_abs_dT_K=abs(dT).max(),
                  initial_p_spread_Pa=np.ptp(dp), initial_T_spread_K=np.ptp(dT),
                  initial_inverse_shift_bit_identical=True)
    return result


def discrepancy(reference, shifted):
    """Compare only independent torus vertices, with the shift undone."""
    delta = np.roll(shifted, -(reference.shape[1] // 4), axis=1) - reference
    return dict(rms=np.sqrt(np.mean(delta**2, axis=(0, 1))).tolist(),
                max_abs=np.max(abs(delta), axis=(0, 1)).tolist())


def pressure_pattern(q, base, state):
    dp, _ = thermodynamics(q.reshape(-1, 4), base, state)
    cells = q.shape[1]
    dp = dp.reshape(NY, cells)
    transverse = dp - dp.mean(axis=0)
    by_column = np.sum(transverse**2, axis=0)
    spread = np.ptp(dp, axis=0)
    # The windows have equal width. The second is where
    # the original seam feature would arrive if carried with the wave.
    def fraction(center):
        distance = (np.arange(cells) - center + cells//2) % cells - cells//2
        if by_column.sum() == 0:
            return None
        return float(by_column[abs(distance) <= 4].sum() / by_column.sum())

    peak_i = int(spread.argmax())
    return dp, dict(min_mean_max_Pa=[dp.min(), dp.mean(), dp.max()],
                    min_ji=list(map(int, np.unravel_index(dp.argmin(), dp.shape))),
                    max_ji=list(map(int, np.unravel_index(dp.argmax(), dp.shape))),
                    max_y_range_Pa=spread.max(), peak_y_range_i=peak_i,
                    symmetry_rms_Pa=np.sqrt(np.mean(transverse**2)),
                    symmetry_power_near_seam=fraction(0),
                    symmetry_power_near_translated_seam=fraction(cells // 4),
                    column_y_range_Pa=spread.tolist())


def corner_stencil(directory):
    # At a geometrical corner both local neighbours have the periodic flag.
    # No extra undivided-Laplacian contribution passes SU2's send-side filter.
    my = read_restart(directory / "state_00000.dat")["Momentum_y"].reshape(NY + 1, -1)
    left = my[0, 1] + my[1, 0] - 2 * my[0, 0]
    right = my[0, -2] + my[1, -1] - 2 * my[0, -1]
    torus = my[0, 1] + my[0, -2] + my[1, 0] + my[-2, 0] - 4 * my[0, 0]
    return dict(left_corner_local=left, right_corner_local=right, four_neighbor_torus=torus)


def compare(original, shifted, cells=NX, steps=STEPS, *, resumed_shift_step=None):
    shift = cells // 4
    preflight = audit_inputs(original, shifted, cells)
    base = background()
    nu = base["mu_Pa_s"] / base["rho_kg_m3"]
    state = CP.AbstractState("HEOS", "Water")
    runs = []
    for directory, offset in ((original, 0), (shifted, shift)):
        run = measure(directory, cells, steps, base, shift_cells=offset)
        check_history(directory, steps, run["dt_s"], resume_step=resumed_shift_step if offset else None)
        run["initial_corner_undivided_laplacian_my_kg_m2_s"] = corner_stencil(directory)
        runs.append(run)
    endpoints = []
    for step in range(0, steps + 1, steps // 4):
        records = [read_restart(d / f"state_{step:05d}.dat") for d in (original, shifted)]
        q0, q1 = (unique_grid(r, CONSERVED) for r in records)
        p0, s0 = pressure_pattern(q0, base, state)
        p1, s1 = pressure_pattern(q1, base, state)
        endpoint = dict(step=step, time_s=step*runs[0]["dt_s"],
                        aligned_conserved=discrepancy(q0, q1),
                        aligned_pressure_Pa=discrepancy(p0, p1), original=s0, translated=s1)
        if step:
            names = ("Residual_Momentum_x", "Residual_Momentum_y")
            r0, r1 = (unique_grid(r, names) for r in records)
            endpoint["aligned_momentum_residual_N_per_m"] = discrepancy(r0, r1)
            for summary, res in ((s0, r0), (s1, r1)):
                summary["momentum_residual_rms_N_per_m"] = np.sqrt(np.mean(res**2, axis=(0, 1))).tolist()
                summary["momentum_residual_max_abs_N_per_m"] = np.max(abs(res), axis=(0, 1)).tolist()
        endpoints.append(endpoint)
    change = (runs[1]["nu_fit_m2_s"] - runs[0]["nu_fit_m2_s"]) / nu
    return dict(shift_cells=shift, original_index_of_shifted_node=f"(i-{shift}) mod {cells}",
                preflight=preflight, conserved_fields=list(CONSERVED),
                conserved_units=["kg/m3", "kg/(m2 s)", "kg/(m2 s)", "J/m3"],
                physical_nu_m2_s=nu, phase_change_over_physical_nu=change,
                original=runs[0], translated=runs[1], matched_endpoints=endpoints)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "audit", "compare"])
    parser.add_argument("original", type=Path)
    parser.add_argument("shifted", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        make_case(args.shifted, NX, STEPS, shift_cells=SHIFT)
    reader = compare if args.command == "compare" else audit_inputs
    print(json.dumps(reader(args.original, args.shifted), indent=2, allow_nan=False))
