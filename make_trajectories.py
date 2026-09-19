#!/usr/bin/env python3
"""
Generate passive-tracer trajectories for POV-Ray.

The model is intentionally kinematic. It is designed to provide a clear,
deterministic finite-scale visualization, not to solve the full Navier-Stokes
equations.

Output:
    positions/frame0001.inc
    positions/frame0002.inc
    ...
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import math

import numpy as np


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = ROOT / "positions"


@dataclass(frozen=True)
class Config:
    n_frames: int = 240
    fps: float = 30.0
    n_beads: int = 500
    substeps_per_frame: int = 8
    seed: int = 20260919
    max_radius: float = 0.92
    max_abs_z: float = 0.98


def smoothstep(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3.0 - 2.0 * x)


def progress(t: float, duration: float) -> float:
    margin = 0.08 * duration
    usable = duration - 2.0 * margin
    return smoothstep((t - margin) / usable)


def state_parameters(t: float, duration: float) -> tuple[float, float, float, float, float, float]:
    """
    Return:
        s, strain_rate, swirl_strength, perturbation_amplitude,
        perturbation_radius, perturbation_width
    """
    s = progress(t, duration)

    strain_rate = 0.12 + 0.38 * s
    swirl_strength = 1.30 + 2.20 * s
    perturbation_amplitude = 0.020 + 0.085 * s

    perturbation_radius = 0.68 - 0.22 * s
    perturbation_width = 0.15 - 0.03 * s

    return (
        s,
        strain_rate,
        swirl_strength,
        perturbation_amplitude,
        perturbation_radius,
        perturbation_width,
    )


def velocity_field(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    t: float,
    duration: float,
    max_radius: float,
    max_abs_z: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simplified illustrative velocity field.

    The untapered mean meridional core flow

        u_r = -a r
        u_z =  2 a z

    is divergence-free.

    The current wall taper and oscillatory perturbation are visualization
    devices and are not guaranteed to preserve exact incompressibility.
    """
    s, a, omega, eps, pulse_r, pulse_w = state_parameters(t, duration)

    r = np.sqrt(x * x + y * y) + 1.0e-12
    theta = np.arctan2(y, x)

    radial_gate = np.clip(1.0 - (r / max_radius) ** 8, 0.0, 1.0)
    axial_gate = np.clip(1.0 - (np.abs(z) / max_abs_z) ** 6, 0.0, 1.0)
    wall_gate = radial_gate * axial_gate

    # Mean meridional flow.
    u_r = (-a * r) * wall_gate
    u_z = (2.0 * a * z) * wall_gate

    # Swirl concentrated toward the core/intermediate radii.
    u_theta = (omega * r * np.exp(-(r / 0.56) ** 2)) * wall_gate

    # Localized m=4 perturbation.
    annulus = (
        np.exp(-((r - pulse_r) / pulse_w) ** 2)
        * np.exp(-(z / 0.55) ** 2)
    )
    phase = 4.0 * theta - 2.0 * math.pi * (0.55 * t + 0.07 * t * t)

    u_r = u_r + eps * annulus * np.cos(phase)
    u_theta = u_theta + 0.75 * eps * annulus * np.cos(phase + 0.5)
    u_z = u_z + 1.10 * eps * annulus * np.sin(phase)

    # Cylindrical -> Cartesian.
    u_x = u_r * np.cos(theta) - u_theta * np.sin(theta)
    u_y = u_r * np.sin(theta) + u_theta * np.cos(theta)

    return u_x, u_y, u_z


def rk4_step(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    t: float,
    dt: float,
    duration: float,
    cfg: Config,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    def f(xx: np.ndarray, yy: np.ndarray, zz: np.ndarray, tt: float):
        return velocity_field(
            xx, yy, zz, tt, duration, cfg.max_radius, cfg.max_abs_z
        )

    k1x, k1y, k1z = f(x, y, z, t)
    k2x, k2y, k2z = f(
        x + 0.5 * dt * k1x,
        y + 0.5 * dt * k1y,
        z + 0.5 * dt * k1z,
        t + 0.5 * dt,
    )
    k3x, k3y, k3z = f(
        x + 0.5 * dt * k2x,
        y + 0.5 * dt * k2y,
        z + 0.5 * dt * k2z,
        t + 0.5 * dt,
    )
    k4x, k4y, k4z = f(
        x + dt * k3x,
        y + dt * k3y,
        z + dt * k3z,
        t + dt,
    )

    x_new = x + (dt / 6.0) * (k1x + 2.0 * k2x + 2.0 * k3x + k4x)
    y_new = y + (dt / 6.0) * (k1y + 2.0 * k2y + 2.0 * k3y + k4y)
    z_new = z + (dt / 6.0) * (k1z + 2.0 * k2z + 2.0 * k3z + k4z)

    # Numerical confinement. The wall taper should already suppress most
    # outward motion; this prevents numerical excursions outside the scene.
    radius = np.sqrt(x_new * x_new + y_new * y_new)
    outside = radius > cfg.max_radius
    if np.any(outside):
        scale = 0.995 * cfg.max_radius / (radius[outside] + 1.0e-12)
        x_new[outside] *= scale
        y_new[outside] *= scale

    z_new = np.clip(z_new, -cfg.max_abs_z, cfg.max_abs_z)

    return x_new, y_new, z_new


def core_radius_from_progress(s: float) -> float:
    tau_ratio = 10.0 ** (-2.0 * s)
    return 0.32 * tau_ratio ** 0.30 + 0.02


def core_half_height_from_progress(s: float) -> float:
    return 0.55 * (1.0 + 0.30 * s)


def actuator_phase(t: float) -> float:
    """Radians."""
    return 2.0 * math.pi * (0.55 * t + 0.07 * t * t)


def write_include(
    path: Path,
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    sim_time: float,
    duration: float,
) -> None:
    s, *_ = state_parameters(sim_time, duration)
    tau_ratio = 10.0 ** (-2.0 * s)
    core_radius = core_radius_from_progress(s)
    core_half_height = core_half_height_from_progress(s)
    phase = actuator_phase(sim_time)

    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("// Generated by make_trajectories.py -- do not edit.\n")
        f.write(f"#declare SimTime = {sim_time:.10g};\n")
        f.write(f"#declare TauRatio = {tau_ratio:.10g};\n")
        f.write(f"#declare CoreRadius = {core_radius:.10g};\n")
        f.write(f"#declare CoreHalfHeight = {core_half_height:.10g};\n")
        f.write(f"#declare ActuatorPhase = {phase:.10g};\n")
        f.write(f"#declare NBeads = {len(x)};\n")
        f.write("#declare BeadPos = array[NBeads] {\n")

        for i, (xx, yy, zz) in enumerate(zip(x, y, z)):
            comma = "," if i + 1 < len(x) else ""
            f.write(f"  <{xx:.10g}, {yy:.10g}, {zz:.10g}>{comma}\n")

        f.write("};\n")


def generate(cfg: Config, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # Remove stale generated frame includes, but preserve .gitkeep.
    for path in output_dir.glob("frame*.inc"):
        path.unlink()

    rng = np.random.default_rng(cfg.seed)

    theta = rng.uniform(0.0, 2.0 * math.pi, cfg.n_beads)
    radius = np.sqrt(rng.uniform(0.02, 0.90, cfg.n_beads)) * 0.78
    z = rng.uniform(-0.78, 0.78, cfg.n_beads)

    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    duration = cfg.n_frames / cfg.fps
    frame_dt = 1.0 / cfg.fps
    dt = frame_dt / cfg.substeps_per_frame

    t = 0.0

    for frame_index in range(1, cfg.n_frames + 1):
        write_include(
            output_dir / f"frame{frame_index:04d}.inc",
            x,
            y,
            z,
            t,
            duration,
        )

        for _ in range(cfg.substeps_per_frame):
            x, y, z = rk4_step(x, y, z, t, dt, duration, cfg)
            t += dt

    r_final = np.sqrt(x * x + y * y)

    print(f"Wrote {cfg.n_frames} frames to {output_dir}")
    print(f"Beads: {cfg.n_beads}")
    print(f"Duration: {duration:.3f} s at {cfg.fps:g} fps")
    print(f"Final radius range: {r_final.min():.6f} .. {r_final.max():.6f}")
    print(f"Final z range: {z.min():.6f} .. {z.max():.6f}")

    all_finite = np.isfinite(x).all() and np.isfinite(y).all() and np.isfinite(z).all()
    if not all_finite:
        raise RuntimeError("Non-finite tracer coordinate detected.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=240)
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument("--beads", type=int, default=500)
    parser.add_argument("--substeps", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260919)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    cfg = Config(
        n_frames=args.frames,
        fps=args.fps,
        n_beads=args.beads,
        substeps_per_frame=args.substeps,
        seed=args.seed,
    )

    if cfg.n_frames < 1:
        raise SystemExit("--frames must be >= 1")
    if cfg.fps <= 0:
        raise SystemExit("--fps must be > 0")
    if cfg.n_beads < 1:
        raise SystemExit("--beads must be >= 1")
    if cfg.substeps_per_frame < 1:
        raise SystemExit("--substeps must be >= 1")

    generate(cfg, args.output_dir)


if __name__ == "__main__":
    main()
