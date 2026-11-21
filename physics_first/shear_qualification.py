"""Generate corrected JST pairs or remeasure their saved SU2 restarts."""

import argparse
import json
from pathlib import Path

import numpy as np

from physics_first.shear_translation import CONSERVED, audit_inputs, compare, discrepancy, unique_grid
from physics_first.su2_acoustic import read_restart
from physics_first.su2_shear import make_case

COEFFICIENT = "JST_SENSOR_COEFF= (0.5, 0.0)"
SCREEN = (64, 2048)
REFINEMENT = ((32, 2048), (128, 2048), (64, 4096))
PHASES = ("original", "translated")


def directories(root, cells, steps):
    stem = f"n{cells}-t{steps}"
    return root / stem, root / (stem + "-shift")


def prepare(root, cells, steps):
    paths = directories(root, cells, steps)
    for path, shift in zip(paths, (0, cells // 4)):
        make_case(path, cells, steps, shift_cells=shift)
        with (path / "wave.cfg").open("a") as config:
            config.write(COEFFICIENT + "\n")
    audit_inputs(*paths, cells)


def alternating_components(field):
    """Largest absolute Nyquist projection of any complete row or column."""
    ny, nx = field.shape
    return [float(abs((field * (-1.)**np.arange(nx)).mean(axis=1)).max()),
            float(abs((field * (-1.)**np.arange(ny)[:, None]).mean(axis=0)).max())]


def qualify_pair(root, cells, steps):
    paths = directories(root, cells, steps)
    for path in paths:
        settings = (path / "wave.cfg").read_text().splitlines()
        if [s for s in settings if s.startswith("JST_SENSOR_COEFF")] != [COEFFICIENT]:
            raise ValueError(f"incorrect JST sensor setting in {path}")
        if "JST viscous coefficients (2nd & 4th): 0.5, 0." not in (path / "solver.log").read_text():
            raise ValueError(f"solver did not report the corrected coefficients in {path}")
    resumed_shift = 3072 if (paths[1] / "resumed").is_dir() else None
    result = compare(*paths, cells, steps, resumed_shift_step=resumed_shift)
    if resumed_shift is not None:
        result["translated_resumed_from_step"] = resumed_shift
    for ep in result["matched_endpoints"]:
        solver_pressure = []
        for path, name in zip(paths, PHASES):
            r = read_restart(path / f"state_{ep['step']:05d}.dat")
            q = unique_grid(r, CONSERVED)
            modes = {key: alternating_components(q[:, :, i] / q[:, :, 0])
                     for i, key in ((1, "u_m_s"), (2, "v_m_s"))}
            if ep["step"]:
                p = unique_grid(r, ["Pressure"])[:, :, 0]
                solver_pressure.append(p)
                ep[name]["solver_pressure_max_y_range_Pa"] = float(np.ptp(p, axis=0).max())
                modes["solver_pressure_Pa"] = alternating_components(p - p.mean())
                # Remove the y-invariant physical signal and measure the axial
                # spectrum of the symmetry error, retaining all transverse rows.
                leakage = p - p.mean(axis=0)
                spectrum = np.mean(abs(np.fft.rfft(leakage, axis=1) / cells)**2, axis=0)
                spectrum[1:-1] *= 2
                mode = int(spectrum.argmax())
                ep[name]["symmetry_error_axial_spectrum"] = dict(
                    strongest_mode=mode, rms_Pa=float(np.sqrt(spectrum[mode])),
                    total_rms_Pa=float(np.sqrt(spectrum.sum())))
            ep[name]["max_line_nyquist_xy"] = modes
            del ep[name]["column_y_range_Pa"]
        if solver_pressure:
            ep["aligned_solver_pressure_Pa"] = discrepancy(*solver_pressure)
    endpoints = result["matched_endpoints"][1:]
    result["checks"] = {
        "cross_strip_pressure": all(e[name]["max_y_range_Pa"] <= 0.001 for e in endpoints for name in PHASES),
        "aligned_pressure": all(e["aligned_pressure_Pa"]["max_abs"] <= 0.001 for e in endpoints),
        "viscosity": all(abs(result[name]["excess_pct"]) <= 10 for name in PHASES),
        "intervals": all(result[name]["interval_spread_over_nu"] < 0.05 for name in PHASES),
        "phase_sensitivity": bool(abs(result["phase_change_over_physical_nu"]) < 0.05),
    }
    return result


def analyze(root, refine):
    settings = [SCREEN, *REFINEMENT, (128, 4096)] if refine else [SCREEN]
    results = {f"{n}/{s}": qualify_pair(root, n, s) for n, s in settings}
    passed = all(all(r["checks"].values()) for r in results.values())
    summary = dict(pairs=results)
    if refine:
        nu = results["64/2048"]["physical_nu_m2_s"]
        changes = {}
        for name in PHASES:
            fits = {key: pair[name]["nu_fit_m2_s"] for key, pair in results.items()}
            coarse, fine, finer = (fits[f"{n}/2048"] for n in (32, 64, 128))
            half, finer_half = fits["64/4096"], fits["128/4096"]
            changes[name] = dict(grid_32_64=abs(coarse-fine)/nu, grid_64_128=abs(fine-finer)/nu,
                                 step_64=abs(fine-half)/nu, step_128=abs(finer-finer_half)/nu,
                                 grid_64_128_half_step=abs(half-finer_half)/nu)
        summary["changes_over_physical_nu"] = changes
        passed &= all(x < 0.05 for change in changes.values() for x in change.values())
    summary["quantitative_gates_pass"] = bool(passed)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare-screen", "prepare-refinement", "prepare-step-control", "screen", "qualify"])
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    if args.command.startswith("prepare-"):
        groups = {"prepare-screen": [SCREEN], "prepare-refinement": REFINEMENT,
                  "prepare-step-control": [(128, 4096)]}
        for grid in groups[args.command]:
            prepare(args.root, *grid)
    else:
        summary = analyze(args.root, args.command == "qualify")
        print(json.dumps(summary, indent=2, allow_nan=False))
        raise SystemExit(0 if summary["quantitative_gates_pass"] else 1)
