"""Plot the finest R277 series. Pass a PNG output path on the command line."""

import argparse

import numpy as np
from matplotlib import pyplot as plt

from physics_first.cylinder_spreading import Expansion, TIMES, radial_rule


def plot(destination):
    model = Expansion.project(128, *radial_rule(2048))
    r = np.linspace(0, 0.03, 601)
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.5), layout="constrained")
    for t, color, pattern in zip(TIMES, ("#303942", "#9a571b", "#146e90"), ("--", ":", "-")):
        amplitudes = model.at_time(t)
        speed = model.velocity(r, amplitudes)
        axes[0].plot(r*1000, speed*1000, pattern, color=color, label=f"{t:g} s")
        peak = np.argmax(speed)
        axes[0].plot(r[peak]*1000, speed[peak]*1000, "o", color=color, ms=4)
        axes[1].plot(r*1000, model.vorticity(r, amplitudes), pattern, color=color)
    for ax, label in zip(axes, ("Swirl speed (mm/s)", "Axial vorticity (1/s)")):
        ax.set(xlabel="Radius from axis (mm)", ylabel=label, xlim=(0, 30), ylim=(0, None))
        ax.grid(axis="y", alpha=0.2)
        ax.spines[["right", "top"]].set_visible(False)
    axes[0].legend(frameon=False, loc="lower right")
    fig.savefig(destination, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination")
    plot(parser.parse_args().destination)
