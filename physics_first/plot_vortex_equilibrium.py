"""Plot the saved finest R283 state and its inner pressure-gradient mismatch."""

import argparse

import matplotlib.pyplot as plt
import numpy as np


def plot(csv_path, output):
    s = np.genfromtxt(csv_path, delimiter=",", names=True)
    r = s["r_m"]
    fig, axes = plt.subplots(2, 1, figsize=(6.8, 5.0), layout="constrained")
    axes[0].plot(1000*r, s["p_Pa"] - s["p_Pa"][-1], color="#175a88")
    axes[0].axvspan(60, 80, color="0.90", label="Swirl taper")
    axes[0].set(xlabel="Radius (mm)", ylabel="Pressure relative to wall (Pa)", xlim=(0, 100))
    axes[0].legend(frameon=False)

    inner = r <= 0.030
    rotation = np.divide(s["rho_kg_m3"] * s["u_theta_m_s"]**2, r,
                         out=np.zeros_like(r), where=r > 0)
    for column, label, color in (("recovered_p_Pa", "Recovered pressure", "#bd591c"),
                                 ("p_Pa", "Integrated pressure", "#175a88")):
        gradient = np.gradient(s[column], r[1])
        gradient[0] = 0  # even axis extension
        axes[1].plot(1000*r[inner], (gradient - rotation)[inner], label=label, color=color)
    axes[1].set(xlabel="Radius (mm)", ylabel="Radial force imbalance (Pa/m)", xlim=(0, 30))
    axes[1].legend(frameon=False, ncols=2)
    fig.savefig(output, dpi=145)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path")
    parser.add_argument("output")
    args = parser.parse_args()
    plot(args.csv_path, args.output)
