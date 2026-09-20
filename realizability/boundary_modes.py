"""Analytic, flux-compatible side-wall modes for the cylindrical benchmark."""

from __future__ import annotations

from dataclasses import dataclass
import re

import numpy as np

from .config import GeometryConfig


_MODE_PATTERN = re.compile(r"^(?P<kind>[NT])_(?P<m>[0-9])(?P<k>[0-2])(?P<phase>[cs])$")


@dataclass(frozen=True)
class BoundaryMode:
    """One peak-normalized normal or tangential side-wall velocity basis field."""

    kind: str
    m: int
    k: int
    phase: str
    peak_raw_amplitude: float

    @property
    def name(self) -> str:
        return f"{self.kind}_{self.m}{self.k}{self.phase}"

    @property
    def is_normal(self) -> bool:
        return self.kind == "N"


def parse_mode(name: str) -> BoundaryMode:
    """Parse a canonical mode name and reject physically incompatible N_00c."""

    match = _MODE_PATTERN.fullmatch(name)
    if match is None:
        raise ValueError(f"Invalid boundary mode {name!r}.")
    kind = match.group("kind")
    m = int(match.group("m"))
    k = int(match.group("k"))
    phase = match.group("phase")
    if m == 0 and phase == "s":
        raise ValueError("Sine modes at m = 0 are identically zero and omitted.")
    if kind == "N" and m == 0 and k == 0:
        raise ValueError("N_00c has nonzero net flux and is incompatible with the closed tank.")
    return BoundaryMode(kind, m, k, phase, axial_peak(k))


def axial_shape(s: np.ndarray, k: int) -> np.ndarray:
    """Return the unnormalized axial polynomial Z_k(s), |s| <= 1."""

    s = np.asarray(s, dtype=float)
    w = (1.0 - s * s) ** 2
    if k == 0:
        return w
    if k == 1:
        return s * w
    if k == 2:
        return (s * s - 1.0 / 7.0) * w
    raise ValueError(f"Unsupported axial basis index {k}.")


def axial_peak(k: int) -> float:
    """Return the maximum absolute axial shape value using its smooth extrema."""

    # The roots include all extrema for the degree-six axial shapes; endpoints
    # are included because they make the no-slip rim condition explicit.
    if k == 0:
        candidates = np.array([-1.0, 0.0, 1.0])
    elif k == 1:
        candidates = np.array([-1.0, -1.0 / np.sqrt(5.0), 0.0, 1.0 / np.sqrt(5.0), 1.0])
    elif k == 2:
        candidates = np.array([-1.0, 0.0, 1.0])
        # Numerical roots of d/ds [(s^2 - 1/7)(1-s^2)^2].
        polynomial = np.polynomial.Polynomial([-1.0 / 7.0, 0.0, 9.0 / 7.0, 0.0, -15.0 / 7.0, 0.0, 1.0])
        roots = polynomial.deriv().roots()
        real_roots = roots[np.abs(roots.imag) < 1.0e-12].real
        candidates = np.concatenate((candidates, real_roots[(real_roots >= -1.0) & (real_roots <= 1.0)]))
    else:
        raise ValueError(f"Unsupported axial basis index {k}.")
    return float(np.max(np.abs(axial_shape(candidates, k))))


def angular_shape(theta: np.ndarray, m: int, phase: str) -> np.ndarray:
    theta = np.asarray(theta, dtype=float)
    if phase == "c":
        return np.cos(m * theta)
    if phase == "s":
        return np.sin(m * theta)
    raise ValueError(f"Unsupported phase {phase!r}.")


def mode_scalar(mode: BoundaryMode, theta: np.ndarray, s: np.ndarray) -> np.ndarray:
    """Return the unit-peak signed scalar coefficient of a boundary mode."""

    return axial_shape(s, mode.k) * angular_shape(theta, mode.m, mode.phase) / mode.peak_raw_amplitude


def mode_velocity(mode: BoundaryMode, theta: np.ndarray, s: np.ndarray) -> np.ndarray:
    """Return Cartesian unit-peak velocity vectors on the cylindrical side wall."""

    scalar = mode_scalar(mode, theta, s)
    radial = np.stack((np.cos(theta), np.sin(theta), np.zeros_like(theta)), axis=-1)
    tangential = np.stack((-np.sin(theta), np.cos(theta), np.zeros_like(theta)), axis=-1)
    return scalar[..., np.newaxis] * (radial if mode.is_normal else tangential)


def side_quadrature(geometry: GeometryConfig, n_theta: int = 128, n_z: int = 32) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Tensor-product side-wall quadrature returning theta, s, and area weights."""

    if n_theta < 4 or n_z < 2:
        raise ValueError("Use at least four angular and two axial quadrature points.")
    theta_values = 2.0 * np.pi * np.arange(n_theta) / n_theta
    legendre_points, legendre_weights = np.polynomial.legendre.leggauss(n_z)
    theta, s = np.meshgrid(theta_values, legendre_points, indexing="ij")
    weights = geometry.radius * geometry.half_height * (2.0 * np.pi / n_theta) * legendre_weights[np.newaxis, :]
    return theta.ravel(), s.ravel(), np.broadcast_to(weights, theta.shape).ravel()


def net_flux(mode: BoundaryMode, geometry: GeometryConfig) -> float:
    """Integrate the physical normal flux of one peak-normalized mode."""

    theta, s, weights = side_quadrature(geometry)
    if not mode.is_normal:
        return 0.0
    return float(np.sum(mode_scalar(mode, theta, s) * weights))


def gram_matrix(modes: tuple[BoundaryMode, ...], geometry: GeometryConfig) -> np.ndarray:
    """Return M_ij = integral(b_i dot b_j) dS / side_area."""

    theta, s, weights = side_quadrature(geometry)
    velocities = [mode_velocity(mode, theta, s) for mode in modes]
    side_area = 4.0 * np.pi * geometry.radius * geometry.half_height
    matrix = np.empty((len(modes), len(modes)), dtype=float)
    for row, left in enumerate(velocities):
        for column, right in enumerate(velocities):
            matrix[row, column] = np.sum(np.einsum("ij,ij->i", left, right) * weights) / side_area
    return matrix


def canonical_modes(names: tuple[str, ...]) -> tuple[BoundaryMode, ...]:
    return tuple(parse_mode(name) for name in names)


def azimuthal_design_matrix(samples: int, maximum_mode: int) -> np.ndarray:
    """Sample constant/cosine/sine modes around an equally spaced ring."""

    if samples < 1 or maximum_mode < 0:
        raise ValueError("samples must be positive and maximum_mode nonnegative.")
    theta = 2.0 * np.pi * np.arange(samples) / samples
    columns = [np.ones(samples)]
    for m in range(1, maximum_mode + 1):
        columns.extend((np.cos(m * theta), np.sin(m * theta)))
    return np.column_stack(columns)
