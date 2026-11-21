"""Create a one-wavelength periodic SU2 liquid-water case (no solver implementation)."""

import argparse
import struct
from pathlib import Path

import CoolProp.CoolProp as CP
import numpy as np

from physics_first.acoustic_initial_state import AMPLITUDE, LENGTH, P0, background, isentropic_conserved

HEIGHT = 0.01
NY = 2
FIELDS = ("x", "y", "Density", "Momentum_x", "Momentum_y", "Energy")
MAGIC = 535532


def read_restart(path):
    with path.open("rb") as f:
        magic, count, rows, width, _ = struct.unpack("<5i", f.read(20))
        if magic != MAGIC or width != 8:
            raise ValueError(f"expected SU2 double restart in {path}")
        names = [f.read(33).split(b"\0", 1)[0].decode() for _ in range(count)]
        data = np.fromfile(f, dtype="<f8").reshape(rows, count)
    if not np.isfinite(data).all():
        raise ValueError(f"nonfinite restart data in {path}")
    return {name: data[:, i] for i, name in enumerate(names)}


def make_case(directory, cells, steps, amplitude_pa=AMPLITUDE):
    if not 0 < amplitude_pa < P0:
        raise ValueError("expected a positive amplitude below the background pressure")
    if cells not in (32, 64, 128) or steps % 4 or steps < 2 * cells:
        raise ValueError("use a saved grid and a multiple of four time steps at acoustic CFL <= 0.5")
    directory.mkdir(parents=True, exist_ok=False)
    base = background()
    c = base["sound_speed_m_s"]
    rho0 = base["rho_kg_m3"]
    dt = LENGTH / (steps * c)
    angles = 2 * np.pi * ((np.arange(cells + 1) % cells) + 0.5) / cells
    state = CP.AbstractState("HEOS", "Water")
    rows = []
    for i, a in enumerate(angles):
        dp = amplitude_pa * np.sin(a)
        rho, momentum, energy = isentropic_conserved(state, base, dp)
        rows.append([LENGTH * i / cells, 0, rho, momentum, 0, energy])
    data = np.tile(np.asarray(rows), (NY + 1, 1))
    data[:, 1] = np.repeat(np.linspace(0, HEIGHT, NY + 1), cells + 1)
    write_strip(directory, cells, NY, data)
    write_configuration(directory, base, dt, steps, amplitude_pa / (rho0*c*c), LENGTH,
                        restart_frequency=1)


def write_strip(directory, cells, ny, data):
    """Write a structured quadrilateral strip and its conservative nodal state."""
    with (directory / "state_00000.dat").open("wb") as f:
        f.write(struct.pack("<5i", MAGIC, len(FIELDS), len(data), 8, 0))
        for name in FIELDS:
            f.write(name.encode().ljust(33, b"\0"))
        f.write(data.astype("<f8").tobytes())

    stride = cells + 1
    lines = ["NDIME= 2", f"NELEM= {cells * ny}"]
    for j in range(ny):
        for i in range(cells):
            a = j * stride + i
            lines.append(f"9 {a} {a+1} {a+stride+1} {a+stride}")
    lines += [f"NPOIN= {len(data)}"] + [f"{x:.17g} {y:.17g} {i}" for i, (x, y) in enumerate(data[:, :2])]
    boundaries = {
        "bottom": [(i, i + 1) for i in range(cells)],
        "right": [(j*stride + cells, (j+1)*stride + cells) for j in range(ny)],
        "top": [(ny*stride + i + 1, ny*stride + i) for i in range(cells)],
        "left": [((j+1)*stride, j*stride) for j in range(ny)],
    }
    lines.append("NMARK= 4")
    for marker, edges in boundaries.items():
        lines += [f"MARKER_TAG= {marker}", f"MARKER_ELEMS= {len(edges)}"]
        lines.extend(f"3 {a} {b}" for a, b in edges)
    (directory / "line.su2").write_text("\n".join(lines) + "\n")


def write_configuration(directory, base, dt, steps, mach, length, restart_frequency,
                        periodic_height=None):
    pairs = f"left, right, 0, 0, 0, 0, 0, 0, {length}, 0, 0"
    if periodic_height is None:
        boundaries = f"MARKER_PERIODIC= ({pairs})\nMARKER_SYM= (bottom, top)"
    else:
        pairs += f", bottom, top, 0, 0, 0, 0, 0, 0, 0, {periodic_height}, 0"
        boundaries = f"MARKER_PERIODIC= ({pairs})"
    (directory / "wave.cfg").write_text(f"""SOLVER= NAVIER_STOKES
MATH_PROBLEM= DIRECT
SYSTEM_MEASUREMENTS= SI
MESH_FILENAME= line.su2
MESH_FORMAT= SU2
FLUID_MODEL= COOLPROP
FLUID_NAME= Water
REF_DIMENSIONALIZATION= DIMENSIONAL
INIT_OPTION= TD_CONDITIONS
FREESTREAM_OPTION= TEMPERATURE_FS
FREESTREAM_PRESSURE= {P0}
FREESTREAM_TEMPERATURE= {base['temperature_K']}
MACH_NUMBER= {mach:.17g}
VISCOSITY_MODEL= CONSTANT_VISCOSITY
MU_CONSTANT= {base['mu_Pa_s']:.17g}
CONDUCTIVITY_MODEL= CONSTANT_CONDUCTIVITY
THERMAL_CONDUCTIVITY_CONSTANT= {base['conductivity_W_m_K']:.17g}
{boundaries}
TIME_DOMAIN= YES
TIME_MARCHING= TIME_STEPPING
TIME_STEP= {dt:.17g}
UNST_CFL_NUMBER= 0
TIME_ITER= {steps + 1}
INNER_ITER= 1
CONV_NUM_METHOD_FLOW= JST
TIME_DISCRE_FLOW= RUNGE-KUTTA_EXPLICIT
RK_ALPHA_COEFF= (0.5, 1.0)
MGLEVEL= 0
NUM_METHOD_GRAD= GREEN_GAUSS
RESTART_SOL= YES
RESTART_ITER= 1
READ_BINARY_RESTART= YES
SOLUTION_FILENAME= state
RESTART_FILENAME= state
WRT_RESTART_COMPACT= NO
VOLUME_OUTPUT= (COORDINATES, SOLUTION, PRIMITIVE, RESIDUAL)
OUTPUT_FILES= (RESTART)
OUTPUT_WRT_FREQ= {restart_frequency}
SCREEN_OUTPUT= (TIME_ITER, CUR_TIME, RMS_DENSITY)
SCREEN_WRT_FREQ_TIME= {steps//4}
""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("cells", type=int)
    parser.add_argument("steps", type=int)
    parser.add_argument("--amplitude-pa", type=float, default=AMPLITUDE, help="peak pressure perturbation in Pa")
    args = parser.parse_args()
    make_case(args.directory, args.cells, args.steps, args.amplitude_pa)
