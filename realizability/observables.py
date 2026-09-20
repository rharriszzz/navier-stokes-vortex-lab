"""Fixed-coordinate diagnostic observables for B0 fixtures and later fields."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CoreMeasurement:
    valid: bool
    radius: float | None
    peak_swirl: float | None
    reason: str | None


def axial_strain(z: np.ndarray, u_z: np.ndarray, weights: np.ndarray) -> float:
    """Return a_z from a vertically sampled plane with physical weights."""

    denominator = 2.0 * np.sum(weights * z * z)
    if denominator <= 0.0:
        raise ValueError("Axial strain weights must cover nonzero z.")
    return float(np.sum(weights * z * u_z) / denominator)


def radial_strain(x: np.ndarray, y: np.ndarray, u_x: np.ndarray, u_y: np.ndarray, weights: np.ndarray) -> float:
    denominator = np.sum(weights * (x * x + y * y))
    if denominator <= 0.0:
        raise ValueError("Radial strain weights must cover nonzero radius.")
    return float(-np.sum(weights * (x * u_x + y * u_y)) / denominator)


def fitted_rotation(x: np.ndarray, y: np.ndarray, u_x: np.ndarray, u_y: np.ndarray, weights: np.ndarray) -> float:
    denominator = np.sum(weights * (x * x + y * y))
    if denominator <= 0.0:
        raise ValueError("Rotation weights must cover nonzero radius.")
    return float(np.sum(weights * (x * u_y - y * u_x)) / denominator)


def cylindrical_components(theta: np.ndarray, u_x: np.ndarray, u_y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    u_r = u_x * np.cos(theta) + u_y * np.sin(theta)
    u_theta = -u_x * np.sin(theta) + u_y * np.cos(theta)
    return u_r, u_theta


def fourier_coefficients(values: np.ndarray, theta: np.ndarray, weights: np.ndarray, m: int) -> tuple[float, float]:
    """Return signed cosine/sine coefficients using physical area weights."""

    area = np.sum(weights)
    if area <= 0.0:
        raise ValueError("Fourier weights must have positive area.")
    cosine = 2.0 * np.sum(weights * values * np.cos(m * theta)) / area
    sine = 2.0 * np.sum(weights * values * np.sin(m * theta)) / area
    return float(cosine), float(sine)


def linear_features(
    vertical_z: np.ndarray,
    vertical_u_z: np.ndarray,
    vertical_weights: np.ndarray,
    disk_x: np.ndarray,
    disk_y: np.ndarray,
    disk_u_x: np.ndarray,
    disk_u_y: np.ndarray,
    disk_weights: np.ndarray,
    annulus_theta: np.ndarray,
    annulus_u_r: np.ndarray,
    annulus_u_theta: np.ndarray,
    annulus_weights: np.ndarray,
) -> np.ndarray:
    """Return [a_z, Omega, C_r4, S_r4, C_theta4, S_theta4]."""

    c_r, s_r = fourier_coefficients(annulus_u_r, annulus_theta, annulus_weights, 4)
    c_theta, s_theta = fourier_coefficients(annulus_u_theta, annulus_theta, annulus_weights, 4)
    return np.array(
        [
            axial_strain(vertical_z, vertical_u_z, vertical_weights),
            fitted_rotation(disk_x, disk_y, disk_u_x, disk_u_y, disk_weights),
            c_r,
            s_r,
            c_theta,
            s_theta,
        ],
        dtype=float,
    )


def measure_core(radius: np.ndarray, swirl: np.ndarray, threshold: float = 1.0e-12) -> CoreMeasurement:
    """Measure a unique resolved interior peak without assigning a rest radius."""

    radius = np.asarray(radius, dtype=float)
    swirl = np.asarray(swirl, dtype=float)
    if radius.ndim != 1 or swirl.ndim != 1 or radius.size != swirl.size or radius.size < 3:
        raise ValueError("radius and swirl must be same-length one-dimensional arrays of length >= 3.")
    if np.any(np.diff(radius) <= 0.0):
        raise ValueError("radius samples must be strictly increasing.")
    magnitude = np.abs(swirl)
    maximum = float(np.max(magnitude))
    if maximum <= threshold:
        return CoreMeasurement(False, None, None, "below_threshold")
    if np.argmax(magnitude) in (0, radius.size - 1):
        return CoreMeasurement(False, None, None, "peak_at_edge")
    local_maxima = np.flatnonzero(
        (magnitude[1:-1] > magnitude[:-2]) & (magnitude[1:-1] > magnitude[2:])
    ) + 1
    if local_maxima.size != 1:
        return CoreMeasurement(False, None, None, "multiple_maxima")
    index = int(local_maxima[0])
    return CoreMeasurement(True, float(radius[index]), float(swirl[index]), None)


def reynolds_stress(
    u_r: np.ndarray,
    u_theta: np.ndarray,
    theta: np.ndarray,
    radial_weights: np.ndarray,
) -> float:
    """Area-weighted azimuthal covariance on an r-by-theta annulus grid."""

    u_r = np.asarray(u_r, dtype=float)
    u_theta = np.asarray(u_theta, dtype=float)
    theta = np.asarray(theta, dtype=float)
    radial_weights = np.asarray(radial_weights, dtype=float)
    if u_r.shape != u_theta.shape or u_r.ndim != 2 or u_r.shape[1] != theta.size or u_r.shape[0] != radial_weights.size:
        raise ValueError("Use r-by-theta velocity arrays and one radial weight per row.")
    mean_r = np.mean(u_r, axis=1, keepdims=True)
    mean_theta = np.mean(u_theta, axis=1, keepdims=True)
    covariance_by_radius = np.mean((u_r - mean_r) * (u_theta - mean_theta), axis=1)
    return float(np.sum(radial_weights * covariance_by_radius) / np.sum(radial_weights))


def single_mode_spatial_correlation(c_r: float, s_r: float, c_theta: float, s_theta: float) -> float:
    """Angular mean of one radial-constant Fourier-mode product.

    A common sinusoidal time factor contributes an additional factor of one
    half when this spatial correlation is subsequently time averaged.
    """

    return 0.5 * (c_r * c_theta + s_r * s_theta)
