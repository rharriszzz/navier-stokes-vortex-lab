"""Bounded R289 time-method comparisons on the two release-qualified disks."""

import argparse
from pathlib import Path
from shutil import copyfile

CASES = {
    "wide32": (32, "rk", 3e-9, 4, 1),
    "rk32": (32, "rk", 3e-9, 4, 1),
    "half32": (32, "rk", 1.5e-9, 8, 1),
    "rk64": (64, "rk", 3e-9, 4, 1),
    "dual32": (32, "dual", 12e-9, 1, 8),
    "slow32": (32, "dual", 25e-6, 1, 12),
}


def prepare(root, name):
    n, method, dt, steps, inner = CASES[name]
    source = root / ("r289-wide32" if name == "wide32" else f"r289-disk{n}")
    directory = root / name
    directory.mkdir(exist_ok=False)
    for filename in ("line.su2", "state_00000.dat", "initial.json"):
        copyfile(source / filename, directory / filename)
    settings = dict(line.split("= ", 1) for line in (source / "wave.cfg").read_text().splitlines())
    settings.update(TIME_STEP=f"{dt:.17g}", TIME_ITER=str(steps+1), INNER_ITER=str(inner),
                    OUTPUT_WRT_FREQ=str(max(steps//2, 1)), WRT_PERFORMANCE="YES")
    if method == "dual":
        settings.update(TIME_MARCHING="DUAL_TIME_STEPPING-1ST_ORDER", TIME_DISCRE_FLOW="EULER_IMPLICIT",
                        CFL_NUMBER="10", LINEAR_SOLVER_ERROR="1e-8", LINEAR_SOLVER_ITER="50",
                        SCREEN_OUTPUT="(TIME_ITER, INNER_ITER, RMS_DENSITY, RMS_MOMENTUM-X, RMS_ENERGY, LINSOL_ITER)")
    else:
        settings.update(TIME_DISCRE_FLOW="RUNGE-KUTTA_EXPLICIT")
    (directory / "wave.cfg").write_text("".join(f"{key}= {value}\n" for key, value in settings.items()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("case", choices=CASES)
    args = parser.parse_args()
    prepare(args.root, args.case)
