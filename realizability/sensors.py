"""Small B0 sensor operators; noise and dynamic observability remain B3 work."""

from __future__ import annotations

import numpy as np


def pressure_differences(pressure: np.ndarray, reference_index: int = 0) -> np.ndarray:
    """Return finite-patch pressure readings relative to one declared patch."""

    pressure = np.asarray(pressure, dtype=float)
    if pressure.ndim != 1 or not 0 <= reference_index < pressure.size:
        raise ValueError("pressure must be a nonempty vector with a valid reference index.")
    return pressure - pressure[reference_index]


def shared_reference_covariance(sensor_variances: np.ndarray, reference_index: int = 0) -> np.ndarray:
    """Covariance of p_i - p_reference for independent absolute pressure noise."""

    variances = np.asarray(sensor_variances, dtype=float)
    if variances.ndim != 1 or np.any(variances < 0.0) or not 0 <= reference_index < variances.size:
        raise ValueError("sensor_variances must be nonnegative with a valid reference index.")
    differences = np.eye(variances.size)
    differences[:, reference_index] -= 1.0
    return (differences * variances[np.newaxis, :]) @ differences.T
