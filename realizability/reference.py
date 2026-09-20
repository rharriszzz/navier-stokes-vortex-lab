"""Finite divergence-free reference fixture for diagnostics, separate from Track A."""

from __future__ import annotations

import math

import numpy as np

from .config import FluidConfig, ReferenceConfig


SIMILARITY_Q = 1.2564312086261697


def smooth_cutoff(distance: np.ndarray, plateau: float, cutoff: float) -> tuple[np.ndarray, np.ndarray]:
    """C2 cutoff and derivative with respect to nonnegative distance."""

    distance = np.asarray(distance, dtype=float)
    value = np.ones_like(distance)
    derivative = np.zeros_like(distance)
    transition = (distance > plateau) & (distance < cutoff)
    v = (distance[transition] - plateau) / (cutoff - plateau)
    value[distance >= cutoff] = 0.0
    value[transition] = 1.0 - (10.0 * v**3 - 15.0 * v**4 + 6.0 * v**5)
    derivative[transition] = -(30.0 * v**2 - 60.0 * v**3 + 30.0 * v**4) / (cutoff - plateau)
    return value, derivative


def core_radius(time: float, config: ReferenceConfig) -> float:
    """Target raw-swirl peak radius in metres."""

    if not 0.0 <= time <= config.duration:
        raise ValueError("Reference time must lie within [0, duration].")
    radius_squared = config.initial_core_radius**2 + (
        config.final_core_radius**2 - config.initial_core_radius**2
    ) * time / config.duration
    return math.sqrt(radius_squared)


def width_squared(time: float, config: ReferenceConfig) -> float:
    return core_radius(time, config) ** 2 / SIMILARITY_Q


def strain_rate(time: float, fluid: FluidConfig, config: ReferenceConfig) -> float:
    """Strain rate that combines prescribed contraction with viscous spreading."""

    width_rate = (
        config.final_core_radius**2 - config.initial_core_radius**2
    ) / (config.duration * SIMILARITY_Q)
    return (4.0 * fluid.kinematic_viscosity - width_rate) / (2.0 * width_squared(time, config))


def circulation(config: ReferenceConfig) -> float:
    """Constant circulation selected from the initial peak swirl speed."""

    return (
        2.0
        * math.pi
        * config.initial_core_radius
        * config.initial_peak_swirl
        / (-math.expm1(-SIMILARITY_Q))
    )


def raw_swirl(radius: np.ndarray, time: float, config: ReferenceConfig) -> np.ndarray:
    """Gaussian-vorticity swirl with a regular Cartesian-axis limit."""

    radius = np.asarray(radius, dtype=float)
    b_squared = width_squared(time, config)
    coefficient = np.full_like(radius, circulation(config) / (2.0 * math.pi * b_squared))
    non_axis = radius != 0.0
    coefficient[non_axis] = (
        circulation(config)
        / (2.0 * math.pi)
        * (-np.expm1(-(radius[non_axis] ** 2) / b_squared))
        / (radius[non_axis] ** 2)
    )
    return coefficient * radius


def velocity(xyz: np.ndarray, time: float, fluid: FluidConfig, config: ReferenceConfig) -> np.ndarray:
    """Evaluate the windowed divergence-free reference in Cartesian coordinates."""

    points = np.asarray(xyz, dtype=float)
    if points.shape[-1] != 3:
        raise ValueError("xyz must have final dimension 3.")
    x, y, z = np.moveaxis(points, -1, 0)
    r = np.hypot(x, y)
    f, f_r = smooth_cutoff(r, config.radial_plateau, config.radial_cutoff)
    g, g_absolute = smooth_cutoff(np.abs(z), config.axial_plateau, config.axial_cutoff)
    g_z = g_absolute * np.sign(z)
    a = strain_rate(time, fluid, config)

    radial_coefficient = -a * f * (g + z * g_z)
    b_squared = width_squared(time, config)
    angular_coefficient = np.full_like(r, circulation(config) / (2.0 * math.pi * b_squared))
    non_axis = r != 0.0
    angular_coefficient[non_axis] = (
        circulation(config)
        / (2.0 * math.pi)
        * (-np.expm1(-(r[non_axis] ** 2) / b_squared))
        / (r[non_axis] ** 2)
    )
    angular_coefficient *= f * g
    u_x = radial_coefficient * x - angular_coefficient * y
    u_y = radial_coefficient * y + angular_coefficient * x
    u_z = a * z * (2.0 * f + r * f_r) * g
    return np.stack((u_x, u_y, u_z), axis=-1)


def finite_difference_divergence(
    xyz: np.ndarray,
    spacing: float,
    time: float,
    fluid: FluidConfig,
    config: ReferenceConfig,
) -> np.ndarray:
    """Centered finite-difference diagnostic; not a substitute for analytic divergence."""

    if spacing <= 0.0:
        raise ValueError("spacing must be positive.")
    points = np.asarray(xyz, dtype=float)
    divergence = np.zeros(points.shape[:-1], dtype=float)
    for axis in range(3):
        offset = np.zeros(3)
        offset[axis] = spacing
        divergence += (velocity(points + offset, time, fluid, config)[..., axis] - velocity(points - offset, time, fluid, config)[..., axis]) / (2.0 * spacing)
    return divergence
