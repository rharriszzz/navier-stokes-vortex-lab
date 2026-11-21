"""Draw the centerlines at release from the dimensional R286 design."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot(destination):
    fig, (tubes, rings) = plt.subplots(1, 2, figsize=(9.4, 3.7),
                                      constrained_layout=True, width_ratios=[1.25, 1])
    colors = ("#277483", "#9a5022")
    z = np.linspace(-64, 64, 401)
    theta = np.linspace(0, 2*np.pi, 401)
    angle = np.pi/6
    for sign, color in zip((-1, 1), colors):
        x = sign*(8 - 2*np.cos(2*np.pi*z/128))
        tubes.plot(z, x, color=color, linewidth=2.5)
        start = 200 - 22*sign
        end = 200 + 22*sign
        tubes.annotate("", xy=(z[end], x[end]), xytext=(z[start], x[start]),
                       arrowprops=dict(arrowstyle="->", color=color, lw=2.5))
        # Top view along z. The ellipse is the projection of a tilted circle.
        rings.plot(sign*19 + 15*np.cos(angle)*np.cos(theta), 15*np.sin(theta),
                   color=color, linewidth=2.5)
        rings.annotate("", xy=(sign*12, 0), xytext=(sign*19, 0),
                       arrowprops=dict(arrowstyle="->", color=color, lw=2))
    tubes.set(title="Bowed tubes · side view", xlabel="Axial position z (mm)",
              ylabel="Lateral position x (mm)", xlim=(-68, 68), ylim=(-25, 25))
    tubes.set_aspect("equal")
    tubes.text(0, -19, "Arrows show circulation direction", ha="center", fontsize=9)
    rings.set(title="Converging rings · view along z", xlabel="Lateral position x (mm)",
              ylabel="y (mm)", xlim=(-36, 36), ylim=(-24, 24))
    rings.set_aspect("equal")
    rings.annotate("", xy=(6, 0), xytext=(-6, 0), arrowprops=dict(arrowstyle="<->", lw=1))
    rings.text(0, 2, "12 mm", ha="center", fontsize=8)
    rings.text(0, -21, "Arrows show lateral propagation", ha="center", fontsize=9)
    for ax in (tubes, rings):
        ax.spines[["right", "top"]].set_visible(False)
    fig.savefig(destination, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    plot(parser.parse_args().destination)
