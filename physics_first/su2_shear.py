"""Generate the three R284 doubly periodic viscous-water inputs."""

import argparse
from pathlib import Path

import numpy as np

from physics_first.acoustic_initial_state import background
from physics_first.su2_acoustic import write_configuration, write_strip

LENGTH = 10e-6
HEIGHT = LENGTH / 8
NY = 4
AMPLITUDE = 0.01
CASES = ((32, 2048), (64, 2048), (64, 4096))


def make_case(directory, cells, steps, *, shift_cells=0):
    if (cells, steps) not in (*CASES, (128, 2048), (128, 4096)):
        raise ValueError("unsupported shear grid or step count")
    base = background()
    density = base["rho_kg_m3"]
    speed = base["sound_speed_m_s"]
    dt = 8 * LENGTH / (speed * steps)
    x = np.arange(cells + 1) * LENGTH / cells
    y = np.arange(NY + 1) * HEIGHT / NY
    angles = 2 * np.pi * ((np.arange(cells + 1) - shift_cells) % cells) / cells
    velocity = AMPLITUDE * np.sin(angles)
    energy = density * (base["internal_energy_J_kg"] + 0.5 * velocity**2)
    row = np.column_stack((x, np.zeros_like(x), np.full_like(x, density),
                           np.zeros_like(x), density * velocity, energy))
    nodes = np.tile(row, (NY + 1, 1))
    nodes[:, 1] = np.repeat(y, len(x))
    directory.mkdir(parents=True, exist_ok=False)
    write_strip(directory, cells, NY, nodes)
    write_configuration(directory, base, dt, steps, AMPLITUDE / speed, LENGTH,
                        restart_frequency=steps // 4, periodic_height=HEIGHT)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    for cells, steps in CASES:
        make_case(args.root / f"n{cells}-t{steps}", cells, steps)
