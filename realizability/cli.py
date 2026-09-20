"""Command-line entry point for NumPy-only B0 preflight diagnostics."""

from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import resource
import subprocess
from typing import Any

import numpy as np

from .boundary_modes import azimuthal_design_matrix, canonical_modes, gram_matrix, net_flux
from .config import PilotConfig, load_config
from .reference import core_radius, strain_rate


def build_preflight(config: PilotConfig) -> dict[str, Any]:
    """Build a compact, solver-free report of the B0 benchmark assumptions."""

    geometry = config.geometry
    fluid = config.fluid
    reference = config.reference
    modes = canonical_modes(config.mode_order)
    gram = gram_matrix(modes, geometry)
    eigenvalues = np.linalg.eigvalsh(gram)
    sensitivity = []
    for duration in (30.0, reference.duration, 300.0):
        target = replace(reference, duration=duration)
        for fraction, label in ((0.0, "start"), (0.5, "midpoint"), (1.0, "end")):
            time = fraction * duration
            sensitivity.append(
                {
                    "duration_s": duration,
                    "time_label": label,
                    "time_s": time,
                    "core_radius_mm": 1000.0 * core_radius(time, target),
                    "strain_rate_per_s": strain_rate(time, fluid, target),
                }
            )
    ring_aliasing = []
    for samples in (8, 12, 16):
        matrix = azimuthal_design_matrix(samples, 6)
        theta = 2.0 * np.pi * np.arange(samples) / samples
        m4_rank = int(np.linalg.matrix_rank(np.column_stack((np.cos(4.0 * theta), np.sin(4.0 * theta)))))
        ring_aliasing.append(
            {"samples": samples, "rank_through_m6": int(np.linalg.matrix_rank(matrix)), "m4_quadrature_rank": m4_rank}
        )
    viscous_lengths = [
        {"frequency_hz": frequency, "penetration_depth_mm": 1000.0 * np.sqrt(fluid.kinematic_viscosity / (np.pi * frequency))}
        for frequency in config.frequencies_hz
    ]
    return {
        "schema_version": config.schema_version,
        "assumption": "NumPy-only B0 preflight; no CFD, response gains, or hardware feasibility result.",
        "tank_volume_litres": 1000.0 * np.pi * geometry.radius**2 * (2.0 * geometry.half_height),
        "probe_reynolds_number": config.probe_velocity * geometry.radius / fluid.kinematic_viscosity,
        "wall_to_initial_core_distance_mm": 1000.0 * (geometry.radius - reference.initial_core_radius),
        "wall_to_initial_core_diffusion_time_s": (geometry.radius - reference.initial_core_radius) ** 2 / fluid.kinematic_viscosity,
        "viscous_penetration_lengths": viscous_lengths,
        "boundary_modes": [
            {
                "name": mode.name,
                "kind": mode.kind,
                "peak_raw_amplitude": mode.peak_raw_amplitude,
                "net_flux_m3_per_s_at_unit_speed": net_flux(mode, geometry),
            }
            for mode in modes
        ],
        "gram_eigenvalues": eigenvalues.tolist(),
        "gram_condition_number": float(eigenvalues[-1] / eigenvalues[0]),
        "reference_sensitivity": sensitivity,
        "ideal_ring_aliasing": ring_aliasing,
    }


def format_preflight(report: dict[str, Any]) -> str:
    """Render a compact human-readable report alongside the machine-readable JSON."""

    lines = [
        "# B0 boundary-control preflight",
        "",
        report["assumption"],
        "",
        f"Tank volume: {report['tank_volume_litres']:.3f} L",
        f"Probe Reynolds number: {report['probe_reynolds_number']:.3g}",
        f"Wall-to-initial-core diffusion estimate: {report['wall_to_initial_core_diffusion_time_s']:.0f} s",
        "",
        "| Frequency (Hz) | Planar viscous penetration (mm) |",
        "|---:|---:|",
    ]
    lines.extend(
        f"| {row['frequency_hz']:g} | {row['penetration_depth_mm']:.3f} |"
        for row in report["viscous_penetration_lengths"]
    )
    lines.extend(["", "| Ring samples | Rank through m=6 | m=4 quadrature rank |", "|---:|---:|---:|"])
    lines.extend(
        f"| {row['samples']} | {row['rank_through_m6']} | {row['m4_quadrature_rank']} |"
        for row in report["ideal_ring_aliasing"]
    )
    lines.extend(["", f"Boundary Gram condition number: {report['gram_condition_number']:.6g}", "", "## Reference strain sensitivity", "", "| Duration (s) | Time | Core radius (mm) | Strain (1/s) |", "|---:|---|---:|---:|"])
    lines.extend(
        f"| {row['duration_s']:g} | {row['time_label']} | {row['core_radius_mm']:.3f} | {row['strain_rate_per_s']:.6f} |"
        for row in report["reference_sensitivity"]
    )
    lines.extend(["", "All boundary modes are peak-normalized; normal-mode flux values should be near quadrature roundoff."])
    return "\n".join(lines) + "\n"


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="B0 physical-realizability diagnostics")
    subcommands = parser.add_subparsers(dest="command", required=True)
    preflight = subcommands.add_parser("preflight", help="write the NumPy-only benchmark preflight")
    preflight.add_argument("--config", type=Path, required=True, help="versioned B0 JSON configuration")
    preflight.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/realizability"),
        help="generated output directory; ignored by Git",
    )
    verify = subcommands.add_parser("verify", help="run the optional DOLFINx B1 verification suite")
    verify.add_argument("--config", type=Path, required=True, help="versioned benchmark JSON configuration")
    verify.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/realizability/b1"),
        help="generated output directory; ignored by Git",
    )
    verify.add_argument(
        "--pilot-mesh-size",
        type=float,
        default=0.05,
        help="uniform cylinder pilot mesh size in metres (coarse smoke default)",
    )
    b2_gate = subcommands.add_parser(
        "b2-gate", help="run the B2 two-pilot numerical gate without launching the campaign"
    )
    b2_gate.add_argument("--config", type=Path, required=True, help="versioned benchmark JSON configuration")
    b2_gate.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/realizability/b2"),
        help="generated output directory; ignored by Git",
    )
    b2_gate.add_argument(
        "--mesh-sizes",
        type=float,
        nargs="+",
        default=(0.04, 0.03, 0.025),
        help="coarse-to-fine uniform pilot mesh sizes in metres",
    )
    return parser.parse_args()


def _source_provenance(config_path: Path, extra_sources: tuple[Path, ...] = ()) -> dict[str, Any]:
    tracked_sources = [
        Path("realizability/backends/fenicsx_stokes.py"),
        Path("realizability/backends/b1_verification.py"),
        config_path,
        *extra_sources,
    ]
    hashes = {
        str(path): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in tracked_sources
        if path.is_file()
    }
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"], check=True, capture_output=True, text=True
            ).stdout.strip()
        )
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    return {"repository_commit": commit, "repository_dirty": dirty, "source_sha256": hashes}


def format_verification(report: dict[str, Any]) -> str:
    lines = [
        "# B1 verified-solver report",
        "",
        report["claim"],
        "",
        f"All acceptance checks passed: **{report['all_acceptance_checks_passed']}**",
        "",
        "| Check | Passed | Criterion |",
        "|---|:---:|---|",
    ]
    lines.extend(
        f"| {case['name']} | {case['passed']} | {case['criterion']} |" for case in report["cases"]
    )
    lines.extend(["", "## Pilot discrepancies", ""])
    for pilot in report["pilots"]:
        inputs = pilot["input_diagnostics"]
        lines.append(
            f"- {pilot['mode']}: real/imaginary divergence ratios "
            f"{pilot['real']['divergence_ratio']:.6g} / {pilot['imaginary']['divergence_ratio']:.6g}; "
            f"flux correction {pilot['flux_correction_coefficient']:.6g}; actual peak/RMS speed "
            f"{inputs['actual_peak_speed']:.6g} / {inputs['side_rms_speed']:.6g} m/s; actual faceted-trace "
            f"inward normal flow {inputs['inward_volume_flow_amplitude']:.6g} m^3/s."
        )
    lines.extend(["", "## Deferred to B2", ""])
    lines.extend(f"- {item}" for item in report["not_yet_checked"])
    return "\n".join(lines) + "\n"


def _json_default(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def main() -> None:
    args = _arguments()
    config = load_config(args.config)
    if args.command == "verify":
        from .backends.b1_verification import run_verification

        report = run_verification(config, args.pilot_mesh_size)
        report["provenance"] = _source_provenance(args.config)
        report["process_peak_rss_mib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        output_dir = args.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "verification.json").write_text(
            json.dumps(report, indent=2, sort_keys=True, default=_json_default) + "\n", encoding="utf-8"
        )
        markdown = format_verification(report)
        (output_dir / "verification.md").write_text(markdown, encoding="utf-8")
        print(markdown, end="")
        print(f"Wrote {output_dir / 'verification.json'} and {output_dir / 'verification.md'}")
        return
    if args.command == "b2-gate":
        from .backends.b2_gate import format_b2_gate, run_b2_gate

        report = run_b2_gate(config, tuple(args.mesh_sizes))
        report["provenance"] = _source_provenance(
            args.config,
            (
                Path("realizability/backends/hdiv_stokes.py"),
                Path("realizability/backends/fem_observables.py"),
                Path("realizability/backends/b2_gate.py"),
            ),
        )
        report["process_peak_rss_mib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        output_dir = args.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "gate.json").write_text(
            json.dumps(report, indent=2, sort_keys=True, default=_json_default) + "\n",
            encoding="utf-8",
        )
        markdown = format_b2_gate(report)
        (output_dir / "gate.md").write_text(markdown, encoding="utf-8")
        print(markdown, end="")
        print(f"Wrote {output_dir / 'gate.json'} and {output_dir / 'gate.md'}")
        return
    report = build_preflight(config)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "preflight.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "preflight.md").write_text(format_preflight(report), encoding="utf-8")
    print(format_preflight(report), end="")
    print(f"Wrote {output_dir / 'preflight.json'} and {output_dir / 'preflight.md'}")


if __name__ == "__main__":
    main()
