"""Map EOS-recovered startup pressure on both 32-cell/core meshes at 12 ns."""

import argparse
from pathlib import Path

import numpy as np


def extract(root, dest):
    from physics_first.disk_pilot import flash
    from physics_first.su2_acoustic import FIELDS, read_restart

    fields = {}
    for case in ("rk32", "wide32"):
        p = []
        for step in (0, 4):
            data = read_restart(root/case/f"state_{step:05d}.dat")
            mask = np.maximum(abs(data["x"]), abs(data["y"])) <= .03001
            q = np.column_stack([data[k][mask] for k in FIELDS[2:]])
            p.append(flash(q)[0])
        fields[case] = np.column_stack((1000*data["x"][mask], 1000*data["y"][mask], p[1]-p[0]))
    np.savez(dest, **fields)


def plot(source, dest):
    import matplotlib.pyplot as plt
    from matplotlib.colors import SymLogNorm
    from matplotlib.patches import Rectangle

    fig, axes = plt.subplots(1, 2, figsize=(8.4, 4.35), layout="constrained", sharey=True)
    norm = SymLogNorm(linthresh=.02, vmin=-1.3, vmax=1.3)
    with np.load(source) as data:
        for ax, case, title in zip(axes, ("rk32", "wide32"),
                                   ("10 mm Cartesian half-width", "35 mm Cartesian half-width")):
            x, y, dp = data[case].T
            points = ax.scatter(x, y, c=dp, cmap="RdBu_r", norm=norm, s=2.1, linewidths=0)
            if case == "rk32":
                ax.add_patch(Rectangle((-10,-10),20,20,fill=False,linestyle=":",color="0.3",lw=.75))
            ax.set(xlim=(-30,30), ylim=(-30,30), aspect="equal", title=title, xlabel="x (mm)")
    axes[0].set_ylabel("y (mm)")
    bar = fig.colorbar(points, ax=axes, location="bottom", shrink=.77, aspect=42,
                       ticks=[-1,-.1,-.02,0,.02,.1,1])
    bar.set_ticklabels(["−1","−0.1","−0.02","0","0.02","0.1","1"])
    bar.set_label("Change in pressure from release (Pa)")
    fig.suptitle("Pressure after 12 ns at matched core spacing", fontsize=15)
    fig.savefig(dest, dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("extract","plot"))
    parser.add_argument("source", type=Path)
    parser.add_argument("dest", type=Path)
    args = parser.parse_args()
    (extract if args.mode=="extract" else plot)(args.source, args.dest)
