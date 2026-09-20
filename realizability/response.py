"""Unit-aware real/complex response and finite-family identifiability diagnostics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SingularValueReport:
    singular_values: np.ndarray
    numerical_rank: int
    missing_output_directions: int
    condition_number: float | None


@dataclass(frozen=True)
class IdentifiabilityReport:
    identifiable: bool
    nullity: int
    q_on_measurement_nullspace_norm: float


def inverse_square_root(matrix: np.ndarray, tolerance: float = 1.0e-12) -> np.ndarray:
    """Hermitian inverse square root of a positive-definite boundary Gram matrix."""

    eigenvalues, eigenvectors = np.linalg.eigh(np.asarray(matrix))
    if np.min(eigenvalues) <= tolerance:
        raise ValueError("Boundary Gram matrix is not positive definite.")
    return (eigenvectors / np.sqrt(eigenvalues)) @ eigenvectors.conj().T


def scaled_gain(gain: np.ndarray, gram: np.ndarray, output_scales: np.ndarray, probe_velocity: float) -> np.ndarray:
    """Apply output and equal-boundary-RMS normalization, retaining harmonic phase."""

    gain = np.asarray(gain)
    output_scales = np.asarray(output_scales, dtype=float)
    if gain.shape[0] != output_scales.size or gain.shape[1] != gram.shape[0]:
        raise ValueError("Gain, Gram matrix, and output scales have incompatible shapes.")
    if np.any(output_scales <= 0.0) or probe_velocity <= 0.0:
        raise ValueError("Output scales and probe velocity must be positive.")
    return (gain * probe_velocity / output_scales[:, np.newaxis]) @ inverse_square_root(gram)


def singular_value_report(matrix: np.ndarray, relative_tolerance: float = 1.0e-10) -> SingularValueReport:
    """Report rank and missing feature directions over the map's real/complex field."""

    matrix = np.asarray(matrix)
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    cutoff = relative_tolerance * singular_values[0] if singular_values.size and singular_values[0] else 0.0
    rank = int(np.count_nonzero(singular_values > cutoff))
    condition = float(singular_values[0] / singular_values[rank - 1]) if rank else None
    return SingularValueReport(singular_values, rank, matrix.shape[0] - rank, condition)


def numerical_nullspace(matrix: np.ndarray, relative_tolerance: float = 1.0e-10) -> np.ndarray:
    """Orthonormal columns spanning the right numerical nullspace of matrix."""

    matrix = np.asarray(matrix)
    _, singular_values, right_vectors_h = np.linalg.svd(matrix, full_matrices=True)
    cutoff = relative_tolerance * singular_values[0] if singular_values.size and singular_values[0] else 0.0
    rank = int(np.count_nonzero(singular_values > cutoff))
    # SVD returns V^H, so conjugation is required to recover right vectors.
    return right_vectors_h[rank:].conj().T.copy()


def assess_identifiability(measurement_map: np.ndarray, feature_map: np.ndarray, tolerance: float = 1.0e-10) -> IdentifiabilityReport:
    """Test ker(P) subset ker(Q) for one declared real or complex state family.

    Complex maps act on complex coefficients (e.g. harmonic amplitudes); these
    diagnostics alone do not establish dynamical observability.
    """

    nullspace = numerical_nullspace(measurement_map, tolerance)
    if nullspace.size == 0:
        return IdentifiabilityReport(True, 0, 0.0)
    q_on_nullspace = np.asarray(feature_map) @ nullspace
    norm = float(np.linalg.norm(q_on_nullspace, ord=2))
    scale = max(1.0, float(np.linalg.norm(feature_map, ord=2)))
    return IdentifiabilityReport(norm <= tolerance * scale, nullspace.shape[1], norm)
