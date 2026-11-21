"""Isolate the linear viscous momentum contribution in two identical SU2 releases."""

import argparse
import json
from pathlib import Path
from shutil import copyfile

import numpy as np

from physics_first.acoustic_initial_state import background
from physics_first.cylinder_spreading import INITIAL, INNER
from physics_first.rotating_disk import mesh, dual_geometry
from physics_first.su2_acoustic import read_restart


def prepare(source, case):
    case.mkdir()
    for file in ("line.su2", "state_00000.dat", "initial.json"):
        copyfile(source / file, case / file)
    lines = (source / "wave.cfg").read_text().splitlines()
    for i, line in enumerate(lines):
        if line.startswith("MU_CONSTANT="):
            lines[i] = f"MU_CONSTANT= {float(line.split('=')[1])/2:.17g}"
    (case / "wave.cfg").write_text("\n".join(lines)+"\n")


def measure(source, case):
    xy, quads, wall = mesh(32)
    vol, _ = dual_geometry(xy, quads, wall)
    r = np.linalg.norm(xy, axis=1)
    core = (r>0) & (r<=INNER+1e-15)
    er = xy/np.where(r>0, r, 1)[:, None]
    et = np.column_stack((-er[:, 1], er[:, 0]))
    a, b = [read_restart(path/"state_00001.dat") for path in (source, case)]
    for key in ("x", "y", "Residual_Density"):
        np.testing.assert_array_equal(a[key], b[key])
    init = read_restart(source/"state_00000.dat")
    rho = init["Density"]
    m = np.column_stack((init["Momentum_x"], init["Momentum_y"]))
    diff = np.column_stack([a[k]-b[k] for k in ("Residual_Momentum_x","Residual_Momentum_y")])
    visc = -2*diff/(vol*rho)[:, None]
    props = background()
    nu = props["mu_Pa_s"]/props["rho_kg_m3"]
    w = INITIAL.gaussian_width_m
    exact = -2*nu*INITIAL.circulation_m2_s*r*np.exp(-(r/w)**2)/(np.pi*w**4)
    def rms(v):
        return np.sqrt(np.average(v[core]**2, weights=vol[core]))
    return dict(core_rms_viscous_radial_m_s2=rms((visc*er).sum(axis=1)),
                core_rms_viscous_tangential_m_s2=rms((visc*et).sum(axis=1)),
                core_rms_viscous_tangential_error_m_s2=rms((visc*et).sum(axis=1)-exact),
                kinetic_viscous_power_W_m=vol @ (visc*m).sum(axis=1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare","measure"))
    parser.add_argument("source", type=Path)
    parser.add_argument("case", type=Path)
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare(args.source, args.case)
    else:
        print(json.dumps(measure(args.source, args.case), indent=2, allow_nan=False))
