"""Optional analytic reference for the axisymmetric ``T_00c`` swirl pilot.

This is a smooth-cylinder Stokes reference, not a replacement for the
faceted three-dimensional BDM2/DG1 calculation.  SciPy is imported only when
one of these diagnostics is evaluated, so the NumPy-only B0 package remains
usable without it.
"""

from __future__ import annotations

import math

import numpy as np


def _ive(order: int, values: np.ndarray | complex):
    try:
        from scipy.special import ive
    except ImportError as error:  # pragma: no cover - depends on optional environment
        raise RuntimeError(
            "The independent swirl reference requires SciPy; install it only in the "
            "optional B2 verification environment."
        ) from error
    return ive(order, values)


def sidewall_coefficients(count: int) -> np.ndarray:
    """Return the first ``count`` cosine coefficients of ``(1-s**2)**2``."""

    if count < 1:
        raise ValueError("count must be positive.")
    n = np.arange(count, dtype=float)
    a = (n + 0.5) * math.pi
    return 16.0 * (-1.0) ** n * (3.0 - a * a) / a**5


def _eigenvalues(count: int, half_height: float, viscosity: float, frequency_hz: float):
    if half_height <= 0.0 or viscosity <= 0.0 or frequency_hz <= 0.0:
        raise ValueError("half_height, viscosity, and frequency_hz must be positive.")
    n = np.arange(count, dtype=float)
    a = (n + 0.5) * math.pi
    return a, np.sqrt((a / half_height) ** 2 + 2j * math.pi * frequency_hz / viscosity)


def normalized_swirl(
    radius: np.ndarray | float,
    z: np.ndarray | float,
    *,
    cylinder_radius: float,
    half_height: float,
    viscosity: float,
    frequency_hz: float,
    terms: int = 64,
) -> np.ndarray:
    """Return ``v(r,z)/U`` for the regular periodic smooth-cylinder solution."""

    if cylinder_radius <= 0.0:
        raise ValueError("cylinder_radius must be positive.")
    radius_values, z_values = np.broadcast_arrays(
        np.asarray(radius, dtype=float), np.asarray(z, dtype=float)
    )
    if np.any(radius_values < 0.0) or np.any(radius_values > cylinder_radius):
        raise ValueError("radius must lie in [0, cylinder_radius].")
    if np.any(np.abs(z_values) > half_height):
        raise ValueError("z must lie between the cylinder caps.")
    a, lam = _eigenvalues(terms, half_height, viscosity, frequency_hz)
    coefficients = sidewall_coefficients(terms)
    radial = np.asarray(radius_values, dtype=float).reshape(-1)
    axial = np.asarray(z_values, dtype=float).reshape(-1)
    ratio = (
        _ive(1, lam[:, None] * radial)
        / _ive(1, lam[:, None] * cylinder_radius)
        * np.exp(lam.real[:, None] * (radial - cylinder_radius))
    )
    values = np.sum(
        coefficients[:, None] * ratio * np.cos(a[:, None] * axial / half_height), axis=0
    )
    # The regular order-one Bessel solution is exactly zero on the axis.
    values[radial == 0.0] = 0.0
    return values.reshape(radius_values.shape)


def disk_rotation_gain(
    *,
    cylinder_radius: float,
    half_height: float,
    disk_radius: float,
    viscosity: float,
    frequency_hz: float,
    terms: int = 64,
) -> complex:
    """Return the analytic ``T_00c -> Omega`` gain in reciprocal metres."""

    if not 0.0 < disk_radius <= cylinder_radius:
        raise ValueError("disk_radius must lie in (0, cylinder_radius].")
    _, lam = _eigenvalues(terms, half_height, viscosity, frequency_hz)
    coefficients = sidewall_coefficients(terms)
    ratio = (
        _ive(2, lam * disk_radius)
        / _ive(1, lam * cylinder_radius)
        * np.exp(lam.real * (disk_radius - cylinder_radius))
    )
    return complex((4.0 / disk_radius**2) * np.sum(coefficients * ratio / lam))
