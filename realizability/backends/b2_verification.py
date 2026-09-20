"""Small B2 verification fixtures that remain separate from response gates."""

from __future__ import annotations

from dataclasses import replace
import math
from typing import Any

import numpy as np

from ..config import PilotConfig
from ..swirl_reference import disk_rotation_gain
from .fem_observables import extract_complex_linear_features
from .hdiv_stokes import harmonic_response, non_affine_manufactured_convergence


def _comparison(value: complex, reference: complex) -> dict[str, float | None]:
    phase_error = None
    if abs(value) > np.finfo(float).tiny and abs(reference) > np.finfo(float).tiny:
        phase_error = float(
            abs(math.degrees(math.atan2((value / reference).imag, (value / reference).real)))
        )
    return {
        "complex_absolute_error_per_m": float(abs(value - reference)),
        "relative_gain_error": float(abs(abs(value) - abs(reference)) / max(abs(reference), np.finfo(float).tiny)),
        "phase_error_degrees": phase_error,
    }


def run_b2_verification_fixture(
    config: PilotConfig,
    mesh_sizes: tuple[float, float] = (0.07, 0.05),
    *,
    penalty_factor: float = 48.0,
    comparison_penalty_factor: float = 96.0,
) -> dict[str, Any]:
    """Compare a low-frequency/high-viscosity swirl solve to its smooth oracle.

    The viscosity and frequency are deliberately changed from the physical B2
    pilot to make a modest mesh meaningful as a verification fixture.  This
    function neither selects a production mesh nor changes an acceptance
    threshold for the physical 0.01 Hz response.
    """

    if len(mesh_sizes) != 2 or mesh_sizes[1] >= mesh_sizes[0]:
        raise ValueError("Use exactly two decreasing positive mesh sizes.")
    if penalty_factor <= 0.0 or comparison_penalty_factor <= 0.0:
        raise ValueError("penalty factors must be positive.")
    fixture = replace(
        config,
        fluid=replace(config.fluid, kinematic_viscosity=1.0e-4),
    )
    frequency_hz = 0.001
    reference = disk_rotation_gain(
        cylinder_radius=fixture.geometry.radius,
        half_height=fixture.geometry.half_height,
        disk_radius=0.025,
        viscosity=fixture.fluid.kinematic_viscosity,
        frequency_hz=frequency_hz,
        terms=128,
    )
    records: list[dict[str, Any]] = []
    base_values: list[complex] = []
    for mesh_size in mesh_sizes:
        result, fields = harmonic_response(
            fixture, "T_00c", frequency_hz, mesh_size,
            penalty_factor=penalty_factor, _return_fields=True,
        )
        feature = complex(extract_complex_linear_features(fields)[1] / fixture.probe_velocity)
        low = complex(
            extract_complex_linear_features(fields, plane_order=12, radial_order=12, angular_order=64)[1]
            / fixture.probe_velocity
        )
        high = complex(
            extract_complex_linear_features(fields, plane_order=24, radial_order=24, angular_order=128)[1]
            / fixture.probe_velocity
        )
        base_values.append(feature)
        records.append(
            {
                "mesh_size_m": mesh_size,
                "solver": result.as_dict(),
                "omega_gain_per_m": {"real": feature.real, "imaginary": feature.imag},
                "reference_comparison": _comparison(feature, reference),
                "quadrature": {
                    "low_to_default_complex_absolute_error_per_m": float(abs(low - feature)),
                    "default_to_high_complex_absolute_error_per_m": float(abs(feature - high)),
                },
            }
        )
    comparison_result, comparison_fields = harmonic_response(
        fixture, "T_00c", frequency_hz, mesh_sizes[-1],
        penalty_factor=comparison_penalty_factor, _return_fields=True,
    )
    comparison_value = complex(
        extract_complex_linear_features(comparison_fields)[1] / fixture.probe_velocity
    )
    return {
        "schema_version": 1,
        "claim": "B2 numerical verification fixture only; no physical 0.01 Hz response validation or production-mesh selection.",
        "fixture": {
            "mode": "T_00c",
            "kinematic_viscosity_m2_per_s": fixture.fluid.kinematic_viscosity,
            "frequency_hz": frequency_hz,
            "cylinder_and_disk": "unchanged from the B2 benchmark",
            "base_penalty_factor": penalty_factor,
            "comparison_penalty_factor": comparison_penalty_factor,
        },
        "smooth_cylinder_reference_omega_gain_per_m": {"real": reference.real, "imaginary": reference.imag},
        "non_affine_manufactured_convergence": non_affine_manufactured_convergence(
            penalty_factor=penalty_factor
        ),
        "swirl_records": records,
        "mesh_refinement_complex_change_per_m": float(abs(base_values[-1] - base_values[0])),
        "fine_mesh_penalty_comparison": {
            "solver": comparison_result.as_dict(),
            "omega_gain_per_m": {"real": comparison_value.real, "imaginary": comparison_value.imag},
            "base_to_comparison": _comparison(comparison_value, base_values[-1]),
            "comparison_to_reference": _comparison(comparison_value, reference),
        },
    }


def format_b2_verification_fixture(report: dict[str, Any]) -> str:
    """Render the fixture's mesh/reference evidence without a pass claim."""

    lines = [
        "# B2 verification fixture",
        "",
        report["claim"],
        "",
        "| Mesh (m) | Complex error (1/m) | Relative gain error | Phase error |",
        "|---:|---:|---:|---:|",
    ]
    for row in report["swirl_records"]:
        comparison = row["reference_comparison"]
        lines.append(
            f"| {row['mesh_size_m']:g} | {comparison['complex_absolute_error_per_m']:.6g} | "
            f"{100.0 * comparison['relative_gain_error']:.3f}% | "
            f"{comparison['phase_error_degrees'] if comparison['phase_error_degrees'] is not None else 'undefined'} |"
        )
    return "\n".join(lines) + "\n"
