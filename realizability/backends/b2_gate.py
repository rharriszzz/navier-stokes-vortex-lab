"""B2 numerical acceptance gate; this module never launches the six-mode sweep."""

from __future__ import annotations

import gc
import math
from typing import Any

import numpy as np

from ..config import PilotConfig
from .b2_stability import run_cylinder_stability_audit
from .fem_observables import extract_complex_linear_features
from .hdiv_stokes import affine_reaction_verification, harmonic_response
from ..swirl_reference import disk_rotation_gain


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


def _gate_status(value: bool | None) -> str:
    return "not run" if value is None else str(value)


def _display(value: Any, *, precision: int = 3) -> str:
    if value is None or not math.isfinite(float(value)):
        return "undefined"
    return f"{float(value):.{precision}f}"


def _finite_or_none(value: float) -> float | None:
    return float(value) if math.isfinite(float(value)) else None


def _complex_records(values: np.ndarray) -> list[dict[str, Any]]:
    records = []
    for name, unit, value in zip(FEATURE_NAMES, FEATURE_UNITS, values):
        value = complex(value)
        finite = math.isfinite(value.real) and math.isfinite(value.imag)
        magnitude = abs(value) if finite else math.nan
        valid = finite and math.isfinite(magnitude)
        phase_valid = valid and magnitude > 0.0
        records.append({
            "name": name,
            "unit": unit,
            "real": _finite_or_none(value.real),
            "imaginary": _finite_or_none(value.imag),
            "magnitude": _finite_or_none(magnitude),
            "phase_degrees": _finite_or_none(float(np.angle(value, deg=True))) if phase_valid else None,
            "valid": valid,
            "phase_valid": phase_valid,
            "invalid_reason": None if valid else "complex feature is nonfinite or magnitude overflowed",
            "phase_invalid_reason": None if phase_valid else ("zero response has undefined phase" if valid else "complex feature is nonfinite or magnitude overflowed"),
        })
    return records


def _phase_difference_degrees(left: complex, right: complex) -> float | None:
    if not (math.isfinite(left.real) and math.isfinite(left.imag) and math.isfinite(right.real) and math.isfinite(right.imag)):
        return None
    if abs(left) == 0.0 or abs(right) == 0.0:
        return None
    difference = math.atan2(left.imag, left.real) - math.atan2(right.imag, right.real)
    return abs(math.degrees(math.atan2(math.sin(difference), math.cos(difference))))


def _comparison(coarse: complex, fine: complex) -> dict[str, Any]:
    finite = all(math.isfinite(v) for v in (coarse.real, coarse.imag, fine.real, fine.imag))
    magnitude_relative_change = abs(abs(fine) - abs(coarse)) / abs(fine) if finite and abs(fine) else None
    phase_change = _phase_difference_degrees(fine, coarse)
    absolute_error = abs(fine - coarse) if finite else math.nan
    derived_finite = (
        (magnitude_relative_change is None or math.isfinite(magnitude_relative_change))
        and (phase_change is None or math.isfinite(phase_change))
        and math.isfinite(absolute_error)
    )
    valid = finite and derived_finite and magnitude_relative_change is not None and phase_change is not None
    return {
        "complex_absolute_change": _finite_or_none(absolute_error),
        "magnitude_relative_change": _finite_or_none(magnitude_relative_change) if magnitude_relative_change is not None else None,
        "phase_change_degrees": _finite_or_none(phase_change) if phase_change is not None else None,
        "comparison_valid": valid,
        "invalid_reason": None if valid else ("nonfinite complex input or arithmetic overflow" if not finite or not derived_finite else "phase or relative magnitude change undefined for zero response"),
        "passed_5_percent_5_degree": bool(valid and magnitude_relative_change < 0.05 and phase_change < 5.0),
    }


def _reference_comparison(value: complex, reference: complex) -> dict[str, Any]:
    finite = all(math.isfinite(v) for v in (value.real, value.imag, reference.real, reference.imag))
    absolute_error = abs(value - reference) if finite else math.nan
    reference_magnitude = abs(reference) if finite else math.nan
    relative_complex_error = absolute_error / reference_magnitude if finite and reference_magnitude else None
    relative_magnitude_error = abs(abs(value) - reference_magnitude) / reference_magnitude if finite and reference_magnitude else None
    phase = _phase_difference_degrees(value, reference)
    arithmetic_valid = finite and all(
        item is not None and math.isfinite(item)
        for item in (absolute_error, relative_complex_error, relative_magnitude_error)
    )
    return {
        "complex_absolute_error_per_m": _finite_or_none(absolute_error),
        "relative_complex_error": _finite_or_none(relative_complex_error) if relative_complex_error is not None else None,
        "relative_magnitude_error": _finite_or_none(relative_magnitude_error) if relative_magnitude_error is not None else None,
        "wrapped_phase_difference_degrees": _finite_or_none(phase) if phase is not None else None,
        "valid": arithmetic_valid,
        "phase_valid": phase is not None,
        "invalid_reason": None if arithmetic_valid else ("nonfinite complex input or arithmetic overflow"),
        "phase_invalid_reason": None if phase is not None else ("zero response has undefined phase" if finite else "complex input is nonfinite"),
    }


def _physical_reference(config: PilotConfig) -> dict[str, Any]:
    parameters = dict(cylinder_radius=config.geometry.radius, half_height=config.geometry.half_height,
                      disk_radius=0.025, viscosity=config.fluid.kinematic_viscosity, frequency_hz=0.01)
    gain64 = disk_rotation_gain(**parameters, terms=64)
    gain128 = disk_rotation_gain(**parameters, terms=128)
    return {
        "mode": "T_00c", "feature": "Omega", "gain_unit": "1/m",
        "harmonic_convention": "complex amplitude with exp(i*2*pi*f*t); gain maps peak wall velocity to peak angular velocity",
        "parameters": {"cylinder_radius_m": parameters["cylinder_radius"],
                       "half_height_m": parameters["half_height"], "disk_radius_m": parameters["disk_radius"],
                       "viscosity_m2_per_s": parameters["viscosity"], "frequency_hz": parameters["frequency_hz"]},
        "series_terms": {"reference": 128, "comparison": 64},
        "64_to_128_term_complex_difference_per_m": float(abs(gain128 - gain64)),
        "complex_gain_per_m": {"real": gain128.real, "imaginary": gain128.imag},
        "_gain": gain128,
    }


def _add_reference_diagnostics(report: dict[str, Any], reference_gain: complex) -> None:
    """Attach reference discrepancies to already-computed T_00c pilot records."""
    comparisons = []
    for row in report["pilot_records"]["T_00c"]:
        gain = row["feature_gains"][PRIMARY_FEATURE["T_00c"]]
        value = complex(gain["real"], gain["imaginary"]) if gain["valid"] else complex(math.nan, math.nan)
        comparison = {"mesh_size_m": row.get("mesh_size_m"), **_reference_comparison(value, reference_gain)}
        row["physical_reference_comparison"] = comparison
        comparisons.append(comparison)
    penalty = report["primary_feature_penalty_checks"]["T_00c"]
    gain = penalty["comparison_feature_gains"][PRIMARY_FEATURE["T_00c"]]
    value = complex(gain["real"], gain["imaginary"]) if gain["valid"] else complex(math.nan, math.nan)
    penalty_comparison = {"penalty_factor": penalty["comparison_penalty_factor"],
                          **_reference_comparison(value, reference_gain)}
    penalty["physical_reference_comparison"] = penalty_comparison
    report["physical_reference_comparisons"] = {
        "pilot_T_00c": comparisons,
        "penalty_comparison_T_00c": penalty_comparison,
    }


def _pde_diagnostics_passed(result) -> bool:
    """Apply the same algebraic and physical checks to every pilot solve."""

    return bool(
        result.real.divergence_ratio < 1.0e-3
        and result.imaginary.divergence_ratio < 1.0e-3
        and result.corrected_flux_ratio < 1.0e-8
        and result.real.algebraic_residual < 1.0e-9
        and result.real.boundary_dof_residual < 1.0e-14
        and result.imaginary.boundary_dof_residual < 1.0e-14
    )


def run_b2_gate(
    config: PilotConfig,
    mesh_sizes: tuple[float, ...] = (0.04, 0.03, 0.025),
    penalty_factor: float = 48.0,
    comparison_penalty_factor: float = 96.0,
) -> dict[str, Any]:
    """Run only the normal/tangential pilot gates required before a campaign."""

    if len(mesh_sizes) < 2 or any(size <= 0.0 for size in mesh_sizes):
        raise ValueError("Use at least two positive mesh sizes.")
    if any(finer >= coarser for coarser, finer in zip(mesh_sizes, mesh_sizes[1:])):
        raise ValueError("mesh_sizes must be listed from coarse to fine.")

    stability_audit = run_cylinder_stability_audit(
        config, penalty_factors=(penalty_factor, comparison_penalty_factor)
    )
    stability_passed = bool(stability_audit["all_requested_cases_stable"])
    if not stability_passed:
        return {
            "schema_version": 3,
            "claim": "B2 pre-campaign numerical gate only; no six-mode response campaign or control result.",
            "formulation": {
                "velocity_pressure": "BDM2/DG1 divergence-conforming symmetric interior-penalty Stokes",
                "operating_point": "rest",
                "frequency_hz": 0.01,
                "penalty_factor": penalty_factor,
                "comparison_penalty_factor": comparison_penalty_factor,
                "production_volume_forcing": "none",
            },
            "mesh_sizes": list(mesh_sizes),
            "cylinder_stability_audit": stability_audit,
            "cylinder_stability_gate_passed": False,
            "affine_verification_passed": None,
            "pilot_divergence_and_residual_gates_passed": None,
            "primary_feature_mesh_comparisons": {},
            "primary_mesh_convergence_passed": None,
            "penalty_sensitivity_passed": None,
            "quadrature_convergence_passed": None,
            "all_numerical_gates_passed": False,
            "campaign_launched": False,
            "campaign_ready": False,
            "campaign_blockers": [
                "requested-penalty stability audit rejected; harmonic pilot solves were not run",
                "stability on actual response meshes is not assessed",
                "physical-reference accuracy and the response error floor remain unassessed",
            ],
            "actual_response_mesh_stability": {"status": "not_assessed", "mesh_sizes_m": list(mesh_sizes),
                                               "penalty_factors": [penalty_factor, comparison_penalty_factor]},
            "campaign_blocked_reason": "One or more requested penalties failed the bounded cylinder stability audit; harmonic pilot solves were not launched.",
            "legacy_aggregate_definition": "all_numerical_gates_passed aggregates only the bounded fixture stability, affine, pilot PDE diagnostics, mesh, penalty, and quadrature checks that ran in this gate.",
        }

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
            diagnostics_passed = _pde_diagnostics_passed(result)
            all_pde_diagnostics_pass = all_pde_diagnostics_pass and diagnostics_passed
            records[mode].append(
                {
                    "mesh_size_m": mesh_size,
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
        diagnostics_passed = _pde_diagnostics_passed(result)
        penalty_checks[mode] = {
            "base_penalty_factor": penalty_factor,
            "comparison_penalty_factor": comparison_penalty_factor,
            **_comparison(primary_values[mode][-1], gains[index]),
            "comparison_solver": result.as_dict(),
            "comparison_feature_gains": _complex_records(gains),
            "comparison_pde_diagnostics_passed": diagnostics_passed,
        }
        del fields
        gc.collect()

    reference = _physical_reference(config)
    reference_gain = reference.pop("_gain")

    affine_passed = (
        affine["velocity_l2_error"] < 1.0e-9
        and affine["pressure_l2"] < 1.0e-9
        and affine["divergence_l2"] < 1.0e-9
        and affine["algebraic_residual"] < 1.0e-9
    )
    mesh_passed = all(rows[-1]["passed_5_percent_5_degree"] for rows in mesh_comparisons.values())
    penalty_passed = all(
        row["passed_5_percent_5_degree"] and row["comparison_pde_diagnostics_passed"]
        for row in penalty_checks.values()
    )
    quadrature_passed = all(
        row["default_to_high_primary"]["passed_5_percent_5_degree"]
        for row in quadrature_checks.values()
    )
    all_passed = bool(
        stability_passed
        and affine_passed
        and all_pde_diagnostics_pass
        and mesh_passed
        and penalty_passed
        and quadrature_passed
    )
    report = {
        "schema_version": 3,
        "claim": "B2 pre-campaign numerical gate only; no six-mode response campaign or control result.",
        "limitations": [
            "Cylinder stability is audited only on fixed 100/70 mm fixtures, not the requested response meshes.",
            "Passing these numerical gates does not establish physical response accuracy or campaign readiness.",
            "The independent smooth-cylinder reference does not certify the faceted production response or resolve its error floor.",
        ],
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
        "cylinder_stability_audit": stability_audit,
        "cylinder_stability_gate_passed": stability_passed,
        "affine_reaction_verification": affine,
        "affine_verification_passed": affine_passed,
        "pilot_divergence_and_residual_gates_passed": all_pde_diagnostics_pass,
        "pilot_records": records,
        "independent_physical_reference": reference,
        "physical_reference_comparisons": {},
        "primary_feature_mesh_comparisons": mesh_comparisons,
        "primary_feature_penalty_checks": penalty_checks,
        "quadrature_checks": quadrature_checks,
        "primary_mesh_convergence_passed": mesh_passed,
        "penalty_sensitivity_passed": penalty_passed,
        "quadrature_convergence_passed": quadrature_passed,
        "all_numerical_gates_passed": all_passed,
        "campaign_launched": False,
        "campaign_ready": False,
        "campaign_blockers": [
            *( [] if all_passed else ["one or more legacy two-pilot numerical acceptance gates failed"]),
            "stability on actual response meshes is not assessed",
            "physical-reference accuracy and the response error floor require review",
        ],
        "actual_response_mesh_stability": {"status": "not_assessed", "mesh_sizes_m": list(mesh_sizes),
                                           "penalty_factors": [penalty_factor, comparison_penalty_factor]},
        "legacy_aggregate_definition": "all_numerical_gates_passed aggregates bounded fixture stability, affine verification, pilot PDE diagnostics, two-pilot mesh convergence, penalty sensitivity, and quadrature convergence; it excludes actual response-mesh stability and physical-reference accuracy.",
        "campaign_blocked_reason": "Campaign readiness is false: actual response-mesh stability and physical-reference accuracy/error floor remain unresolved.",
    }
    _add_reference_diagnostics(report, reference_gain)
    return report


def format_b2_gate(report: dict[str, Any]) -> str:
    """Render a concise B2 gate report."""

    lines = [
        "# B2 pre-campaign numerical gate",
        "",
        report["claim"],
        "",
        f"All numerical gates passed: **{report['all_numerical_gates_passed']}**",
        f"Six-mode campaign launched: **{report['campaign_launched']}**",
        f"Campaign ready: **{report.get('campaign_ready', False)}**",
        "",
        "| Gate | Passed |",
        "|---|:---:|",
        f"| bounded cylinder energy stability | {report['cylinder_stability_gate_passed']} |",
        f"| affine reaction verification | {_gate_status(report.get('affine_verification_passed'))} |",
        f"| flux, algebraic residual, and strong divergence | {_gate_status(report.get('pilot_divergence_and_residual_gates_passed'))} |",
        f"| primary gain/phase mesh convergence | {_gate_status(report.get('primary_mesh_convergence_passed'))} |",
        f"| SIP penalty sensitivity | {_gate_status(report.get('penalty_sensitivity_passed'))} |",
        f"| feature quadrature convergence | {_gate_status(report.get('quadrature_convergence_passed'))} |",
        f"| actual response-mesh stability | {report.get('actual_response_mesh_stability', {}).get('status', 'not assessed')} |",
        "",
        "## Primary-feature mesh comparisons",
        "",
        "| Mode → feature | Meshes (m) | Gain change | Absolute complex change (1/m) | Phase change | Passed |",
        "|---|---:|---:|---:|:---:|",
    ]
    if not report["cylinder_stability_gate_passed"]:
        lines.extend(["", "## Disposition", "", report["campaign_blocked_reason"], "",
                      f"Audited fixture meshes: {', '.join(f'{size:g} m' for size in report['cylinder_stability_audit']['audit_mesh_sizes_m'])}.",
                      f"Audited penalties: {', '.join(f'{value:g}' for value in report['cylinder_stability_audit']['penalty_factors'])}.",
                      "Later gate stages are **not run** because the cylinder stability gate rejected the requested penalties.",
                      "", "Campaign blockers:", *[f"- {item}" for item in report.get("campaign_blockers", [])]])
        return "\n".join(lines) + "\n"
    for mode, rows in report["primary_feature_mesh_comparisons"].items():
        feature = FEATURE_NAMES[PRIMARY_FEATURE[mode]]
        for row in rows:
            lines.append(
                f"| {mode} → {feature} | {row['coarse_mesh_size']:g} → {row['fine_mesh_size']:g} | "
                f"{_display(100.0 * row['magnitude_relative_change'] if row['magnitude_relative_change'] is not None else None)}% | "
                f"{_display(row['complex_absolute_change'], precision=6)} | "
                f"{_display(row['phase_change_degrees'])}° | "
                f"{row['passed_5_percent_5_degree']} |"
            )
    lines.extend(["", "## Disposition", ""])
    if report["all_numerical_gates_passed"]:
        lines.append("The documented two-pilot numerical checks pass on the stated fixtures; campaign readiness remains false.")
        lines.extend(["", "## Scope limitations", ""])
        lines.extend(f"- {limitation}" for limitation in report.get("limitations", []))
    else:
        lines.append(
            "The campaign remains blocked. Passing strong divergence alone is insufficient while the reported "
            "gain/phase or formulation-sensitivity checks remain unresolved."
        )
    lines.extend(["", "Campaign blockers:"])
    lines.extend(f"- {item}" for item in report.get("campaign_blockers", []))
    reference = report.get("physical_reference_comparisons")
    if reference:
        lines.extend(["", "## Independent physical-reference comparison", "",
                      "Smooth-cylinder `T_00c → Omega` at 0.01 Hz; errors are observations, not acceptance certificates.",
                      "", "| Mesh (m) | Complex error (1/m) | Relative complex error | Relative magnitude error | Wrapped phase difference |",
                      "|---:|---:|---:|---:|---:|"])
        for row in reference["pilot_T_00c"]:
            lines.append(f"| {row['mesh_size_m']:g} | {_display(row['complex_absolute_error_per_m'], precision=6)} | "
                         f"{_display(row['relative_complex_error'])} | {_display(row['relative_magnitude_error'])} | "
                         f"{_display(row['wrapped_phase_difference_degrees'])}° |")
    return "\n".join(lines) + "\n"
