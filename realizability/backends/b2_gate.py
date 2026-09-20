"""B2 numerical acceptance gate; this module never launches the six-mode sweep."""

from __future__ import annotations

import gc
import math
from typing import Any

import numpy as np

from ..config import PilotConfig
from .fem_observables import extract_complex_linear_features
from .hdiv_stokes import affine_reaction_verification, harmonic_response


FEATURE_NAMES = ("a_z", "Omega", "C_r4", "S_r4", "C_theta4", "S_theta4")
FEATURE_UNITS = (
    "1/m",
    "1/m",
    "dimensionless",
    "dimensionless",
    "dimensionless",
    "dimensionless",
)
PRIMARY_FEATURE = {"N_02c": 0, "T_00c": 1}


def _complex_records(values: np.ndarray) -> list[dict[str, float | str]]:
    return [
        {
            "name": name,
            "unit": unit,
            "real": float(value.real),
            "imaginary": float(value.imag),
            "magnitude": float(abs(value)),
            "phase_degrees": float(np.angle(value, deg=True)),
        }
        for name, unit, value in zip(FEATURE_NAMES, FEATURE_UNITS, values)
    ]


def _phase_difference_degrees(left: complex, right: complex) -> float:
    if abs(left) <= np.finfo(float).tiny or abs(right) <= np.finfo(float).tiny:
        return math.inf
    return abs(math.degrees(math.atan2((left / right).imag, (left / right).real)))


def _comparison(coarse: complex, fine: complex) -> dict[str, float | bool]:
    magnitude_relative_change = abs(abs(fine) - abs(coarse)) / max(abs(fine), np.finfo(float).tiny)
    phase_change = _phase_difference_degrees(fine, coarse)
    return {
        "magnitude_relative_change": float(magnitude_relative_change),
        "phase_change_degrees": float(phase_change),
        "passed_5_percent_5_degree": bool(magnitude_relative_change < 0.05 and phase_change < 5.0),
    }


def run_b2_gate(
    config: PilotConfig,
    mesh_sizes: tuple[float, ...] = (0.04, 0.03, 0.025),
    penalty_factor: float = 6.0,
    comparison_penalty_factor: float = 12.0,
) -> dict[str, Any]:
    """Run only the normal/tangential pilot gates required before a campaign."""

    if len(mesh_sizes) < 2 or any(size <= 0.0 for size in mesh_sizes):
        raise ValueError("Use at least two positive mesh sizes.")
    if any(finer >= coarser for coarser, finer in zip(mesh_sizes, mesh_sizes[1:])):
        raise ValueError("mesh_sizes must be listed from coarse to fine.")

    affine = affine_reaction_verification(resolution=3, penalty_factor=penalty_factor)
    records: dict[str, list[dict[str, Any]]] = {mode: [] for mode in PRIMARY_FEATURE}
    primary_values: dict[str, list[complex]] = {mode: [] for mode in PRIMARY_FEATURE}
    quadrature_checks: dict[str, dict[str, Any]] = {}
    all_pde_diagnostics_pass = True

    for mode in PRIMARY_FEATURE:
        for mesh_size in mesh_sizes:
            result, fields = harmonic_response(
                config,
                mode,
                0.01,
                mesh_size,
                penalty_factor=penalty_factor,
                _return_fields=True,
            )
            gains = extract_complex_linear_features(fields) / config.probe_velocity
            index = PRIMARY_FEATURE[mode]
            primary_values[mode].append(complex(gains[index]))
            diagnostics_passed = (
                result.real.divergence_ratio < 1.0e-3
                and result.imaginary.divergence_ratio < 1.0e-3
                and result.corrected_flux_ratio < 1.0e-8
                and result.real.algebraic_residual < 1.0e-9
                and result.real.boundary_dof_residual < 1.0e-14
                and result.imaginary.boundary_dof_residual < 1.0e-14
            )
            all_pde_diagnostics_pass = all_pde_diagnostics_pass and diagnostics_passed
            records[mode].append(
                {
                    "solver": result.as_dict(),
                    "feature_gains": _complex_records(gains),
                    "pde_diagnostics_passed": diagnostics_passed,
                }
            )
            if mesh_size == mesh_sizes[-1]:
                low = extract_complex_linear_features(
                    fields, plane_order=12, radial_order=12, angular_order=64
                ) / config.probe_velocity
                high = extract_complex_linear_features(
                    fields, plane_order=24, radial_order=24, angular_order=128
                ) / config.probe_velocity
                quadrature_checks[mode] = {
                    "low_to_default_primary": _comparison(low[index], gains[index]),
                    "default_to_high_primary": _comparison(gains[index], high[index]),
                }
            del fields
            gc.collect()

    mesh_comparisons = {
        mode: [
            {
                "coarse_mesh_size": coarse,
                "fine_mesh_size": fine,
                **_comparison(coarse_value, fine_value),
            }
            for coarse, fine, coarse_value, fine_value in zip(
                mesh_sizes,
                mesh_sizes[1:],
                values,
                values[1:],
            )
        ]
        for mode, values in primary_values.items()
    }

    penalty_checks: dict[str, dict[str, Any]] = {}
    for mode, index in PRIMARY_FEATURE.items():
        result, fields = harmonic_response(
            config,
            mode,
            0.01,
            mesh_sizes[-1],
            penalty_factor=comparison_penalty_factor,
            _return_fields=True,
        )
        gains = extract_complex_linear_features(fields) / config.probe_velocity
        penalty_checks[mode] = {
            "base_penalty_factor": penalty_factor,
            "comparison_penalty_factor": comparison_penalty_factor,
            **_comparison(primary_values[mode][-1], gains[index]),
            "comparison_solver": result.as_dict(),
            "comparison_feature_gains": _complex_records(gains),
        }
        del fields
        gc.collect()

    affine_passed = (
        affine["velocity_l2_error"] < 1.0e-9
        and affine["pressure_l2"] < 1.0e-9
        and affine["divergence_l2"] < 1.0e-9
        and affine["algebraic_residual"] < 1.0e-9
    )
    mesh_passed = all(rows[-1]["passed_5_percent_5_degree"] for rows in mesh_comparisons.values())
    penalty_passed = all(row["passed_5_percent_5_degree"] for row in penalty_checks.values())
    quadrature_passed = all(
        row["default_to_high_primary"]["passed_5_percent_5_degree"]
        for row in quadrature_checks.values()
    )
    all_passed = bool(
        affine_passed
        and all_pde_diagnostics_pass
        and mesh_passed
        and penalty_passed
        and quadrature_passed
    )
    return {
        "schema_version": 1,
        "claim": "B2 pre-campaign numerical gate only; no six-mode response campaign or control result.",
        "formulation": {
            "velocity_pressure": "BDM2/DG1 divergence-conforming symmetric interior-penalty Stokes",
            "operating_point": "rest",
            "frequency_hz": 0.01,
            "penalty_factor": penalty_factor,
            "comparison_penalty_factor": comparison_penalty_factor,
            "manufactured_volume_forcing": "affine reaction verification fixture only",
            "production_volume_forcing": "none",
        },
        "mesh_sizes": list(mesh_sizes),
        "affine_reaction_verification": affine,
        "affine_verification_passed": affine_passed,
        "pilot_divergence_and_residual_gates_passed": all_pde_diagnostics_pass,
        "pilot_records": records,
        "primary_feature_mesh_comparisons": mesh_comparisons,
        "primary_feature_penalty_checks": penalty_checks,
        "quadrature_checks": quadrature_checks,
        "primary_mesh_convergence_passed": mesh_passed,
        "penalty_sensitivity_passed": penalty_passed,
        "quadrature_convergence_passed": quadrature_passed,
        "all_numerical_gates_passed": all_passed,
        "campaign_launched": False,
        "campaign_blocked_reason": None
        if all_passed
        else "The two-pilot mesh/penalty/quadrature acceptance gates are not all satisfied.",
    }


def format_b2_gate(report: dict[str, Any]) -> str:
    """Render a concise B2 gate report."""

    lines = [
        "# B2 pre-campaign numerical gate",
        "",
        report["claim"],
        "",
        f"All numerical gates passed: **{report['all_numerical_gates_passed']}**",
        f"Six-mode campaign launched: **{report['campaign_launched']}**",
        "",
        "| Gate | Passed |",
        "|---|:---:|",
        f"| affine reaction verification | {report['affine_verification_passed']} |",
        f"| flux, algebraic residual, and strong divergence | {report['pilot_divergence_and_residual_gates_passed']} |",
        f"| primary gain/phase mesh convergence | {report['primary_mesh_convergence_passed']} |",
        f"| SIP penalty sensitivity | {report['penalty_sensitivity_passed']} |",
        f"| feature quadrature convergence | {report['quadrature_convergence_passed']} |",
        "",
        "## Primary-feature mesh comparisons",
        "",
        "| Mode → feature | Meshes (m) | Gain change | Phase change | Passed |",
        "|---|---:|---:|---:|:---:|",
    ]
    for mode, rows in report["primary_feature_mesh_comparisons"].items():
        feature = FEATURE_NAMES[PRIMARY_FEATURE[mode]]
        for row in rows:
            lines.append(
                f"| {mode} → {feature} | {row['coarse_mesh_size']:g} → {row['fine_mesh_size']:g} | "
                f"{100.0 * row['magnitude_relative_change']:.3f}% | {row['phase_change_degrees']:.3f}° | "
                f"{row['passed_5_percent_5_degree']} |"
            )
    lines.extend(["", "## Disposition", ""])
    if report["all_numerical_gates_passed"]:
        lines.append("The documented pilot gates pass; a separate command may launch the six-mode campaign.")
    else:
        lines.append(
            "The campaign remains blocked. Passing strong divergence alone is insufficient while the reported "
            "gain/phase or formulation-sensitivity checks remain unresolved."
        )
    return "\n".join(lines) + "\n"
