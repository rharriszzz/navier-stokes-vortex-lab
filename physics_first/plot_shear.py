"""Plot the shear decay and the independently recovered final pressure field."""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np



def plot(result, output):
    fig, (left, right) = plt.subplots(1, 2, figsize=(10.2, 4.2), layout="constrained")
    crossings = np.linspace(0, 8, 200)
    left.plot(crossings, 100 * (1 - result["predicted_final_ratio"]**(crossings / 8)),
              color="#222222", linestyle="--", label="Physical viscosity")
    styles = [("o", "#b54e21"), ("s", "#186180"), ("x", "#701868")]
    for run, (marker, color) in zip(result["runs"], styles, strict=True):
        amplitudes = np.array([s["amplitude_m_s"] for s in run["snapshots"]])
        times = [8 * s["time_s"] / result["end_time_s"] for s in run["snapshots"]]
        left.plot(times, 100 * (1-amplitudes/amplitudes[0]), color=color, marker=marker,
                  markerfacecolor="white", markersize=7, linewidth=1.4 if marker != "x" else 0,
                  label=f"{run['cells']} cells, {run['steps']} steps")
    left.set(xlabel="Elapsed acoustic crossings", ylabel="Loss of transverse amplitude (%)",
             title="Decay of the 10 µm shear wave", xticks=range(0, 9, 2))
    left.legend(frameon=False, fontsize=9)
    profile = result["fine_final_pressure_profile"]
    x = np.array(profile["x_m"]) * 1e6
    for key, label, color in [("lower_quarter_dp_Pa", "y/H = 0.25", "#186180"),
                              ("upper_quarter_dp_Pa", "y/H = 0.75", "#b54e21")]:
        right.plot(x, profile[key], ".-", color=color, markersize=3, linewidth=1, label=label)
    right.set(xlabel="Axial position x (µm)", ylabel="Pressure relative to 101325 Pa (Pa)",
              title="Fine-grid pressure after eight crossings", xlim=(0, 10))
    right.legend(frameon=False, fontsize=9, loc="upper center")
    for ax in (left, right):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.22)
    fig.savefig(output, dpi=175)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    plot(json.loads(args.json.read_text()), args.output)
