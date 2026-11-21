"""Plot measured and translation-predicted pressure asymmetry at eight crossings."""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot(report, output):
    endpoint = report["matched_endpoints"][-1]
    original = np.asarray(endpoint["original"]["column_y_range_Pa"])
    shifted = np.asarray(endpoint["translated"]["column_y_range_Pa"])
    offset = report["shift_cells"]
    # Display a full period with the seam and the predicted peak both inside.
    index = np.arange(-offset, len(original) - offset + 1)
    fig, ax = plt.subplots(figsize=(8, 3.6), layout="constrained")
    for series, style, color, label in [
        (original, ".-", "#304b69", "Original wave"),
        (np.roll(original, offset), "--", "#7d7d7d", "Expected after a 16-cell shift"),
        (shifted, "o-", "#b24721", "Measured after shift"),
    ]:
        ax.plot(index, series[index % len(original)], style, color=color, label=label,
                linewidth=1.4, markersize=3)
    ax.axvline(0, color="#777777", linewidth=0.7, zorder=0)
    ax.set(xlim=(index[0], index[-1]), ylim=(-0.6, 23),
           xticks=np.arange(-16, 49, 8), xlabel="Axial cell index relative to the periodic seam",
           ylabel="Cross-strip pressure range (Pa)", title="The pressure disturbance stays at the seam")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9)
    fig.savefig(output, dpi=165)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    plot(json.loads(args.json.read_text()), args.output)
