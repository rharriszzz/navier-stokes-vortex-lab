"""Plot measured shear amplitude and the finest-grid thermal signature."""
import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot(directory, path):
    result = json.loads((directory/"matrix.json").read_text())
    key = "128x4_2048_0_2e-11"
    points = result["cases"][key]["checkpoints"]
    nu = result["physical_nu_m2_s"]
    k = 2*np.pi/1e-5
    end = points[-1]["time_s"]
    t = np.linspace(0, end, 250)
    fig, (decay, thermal) = plt.subplots(1, 2, figsize=(9, 3.6), layout="constrained")
    decay.plot(8*t/end, 100*(-np.expm1(-nu*k*k*t)), c="#263850", label="Continuum")
    for nx, mark, color in [(32, "s", "#bf6900"), (128, "o", "#008374")]:
        rows = result["cases"][f"{nx}x4_2048_0_2e-11"]["checkpoints"]
        losses = [100*(1-s["amplitude_m_s"]/rows[0]["amplitude_m_s"]) for s in rows]
        decay.plot(range(0, 9, 2), losses, mark, color=color, markerfacecolor="none",
                   markersize=7 if nx == 32 else 4, label=f"{nx} axial cells")
    decay.set(xlabel="Acoustic crossings", ylabel="Amplitude loss (%)", title="Eight crossings of viscous shear")
    decay.legend(frameon=False)
    with np.load(directory/"matrix.npz") as archive:
        # Each pressure profile has four independent transverse rows.
        p = archive[key][-1,5,0]
        shifted = archive["128x4_2048_1_2e-11"][-1,5,0]
    x = 10*np.arange(len(p))/len(p)
    for values, name, style, color in [(p, "Original", "-", "#008374"),
                                        (shifted, "Shifted by 2.5 µm", "--", "#bf6900")]:
        thermal.plot(x, 1e9*(values-values.mean()), style, color=color, label=name)
    thermal.set(xlabel="Axial position (µm)", ylabel="Pressure minus box mean (nPa)",
                title="Axial pressure at eight crossings")
    thermal.legend(frameon=False)
    for ax in (decay, thermal):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=.2)
    fig.savefig(path, dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    plot(args.directory, args.output)
