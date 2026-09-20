"""Dependency-free regressions for B2 gate acceptance and reporting."""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from realizability.backends.b2_gate import (
    _add_reference_diagnostics, _comparison, _complex_records, _reference_comparison,
    format_b2_gate, run_b2_gate,
)
from realizability.backends.b2_stability import _backward_euler_decision


class B2GateReportTests(unittest.TestCase):
    def test_early_stability_rejection_formats_unrun_stages(self) -> None:
        audit = {
            "all_requested_cases_stable": False,
            "audit_mesh_sizes_m": [0.1, 0.07],
            "penalty_factors": [6.0, 48.0],
        }
        with patch("realizability.backends.b2_gate.run_cylinder_stability_audit", return_value=audit), \
            patch("realizability.backends.b2_gate.harmonic_response") as harmonic:
            with patch("realizability.backends.b2_gate.disk_rotation_gain") as reference:
                report = run_b2_gate(object(), mesh_sizes=(0.04, 0.03))
                markdown = format_b2_gate(report)
        harmonic.assert_not_called()
        reference.assert_not_called()
        self.assertFalse(report["all_numerical_gates_passed"])
        self.assertIn("not run", markdown)
        self.assertIn("0.1 m, 0.07 m", markdown)
        self.assertIn("6, 48", markdown)
        self.assertFalse(report["campaign_ready"])
        self.assertTrue(report["campaign_blockers"])
        self.assertEqual(report["actual_response_mesh_stability"]["status"], "not_assessed")

    def test_success_formatter_includes_scope_limitations(self) -> None:
        report = {
            "claim": "synthetic report only",
            "all_numerical_gates_passed": True,
            "campaign_launched": False,
            "cylinder_stability_gate_passed": True,
            "affine_verification_passed": True,
            "pilot_divergence_and_residual_gates_passed": True,
            "primary_mesh_convergence_passed": True,
            "penalty_sensitivity_passed": True,
            "quadrature_convergence_passed": True,
            "primary_feature_mesh_comparisons": {},
            "limitations": ["fixture-only synthetic limitation"],
        }
        markdown = format_b2_gate(report)
        self.assertIn("fixture-only synthetic limitation", markdown)
        self.assertIn("two-pilot numerical checks pass", markdown)
        self.assertIn("Campaign ready: **False**", markdown)

    def test_zero_and_nonfinite_comparisons_are_strict_json_and_fail(self) -> None:
        for left, right in ((0j, 0j), (0j, 1 + 0j), (1 + 0j, 0j),
                            (complex(float("nan"), 0), 1 + 0j),
                            (complex(1e308, 1e308), complex(-1e308, -1e308))):
            result = _comparison(left, right)
            self.assertFalse(result["passed_5_percent_5_degree"])
            json.dumps(result, allow_nan=False)
        equal = _comparison(2 + 3j, 2 + 3j)
        self.assertTrue(equal["passed_5_percent_5_degree"])
        self.assertEqual(equal["complex_absolute_change"], 0.0)

    def test_complex_feature_records_mark_invalid_and_undefined_phase(self) -> None:
        import numpy as np

        records = _complex_records(np.array([0j, complex(float("inf"), 1), 1 + 1j, 1 + 1j, 1 + 1j, 1 + 1j]))
        self.assertTrue(records[0]["valid"])
        self.assertFalse(records[0]["phase_valid"])
        self.assertIsNone(records[0]["phase_degrees"])
        self.assertFalse(records[1]["valid"])
        json.dumps(records, allow_nan=False)

    def test_reference_comparison_and_synthetic_completed_report_remain_blocked(self) -> None:
        reference = 1.0 + 2.0j
        identical = _reference_comparison(reference, reference)
        self.assertEqual(identical["complex_absolute_error_per_m"], 0.0)
        known_error = _reference_comparison(4 + 6j, 1 + 2j)
        self.assertAlmostEqual(known_error["complex_absolute_error_per_m"], 5.0)
        self.assertAlmostEqual(known_error["relative_complex_error"], 5.0 / (5**0.5))
        self.assertEqual(_reference_comparison(0j, 0j)["wrapped_phase_difference_degrees"], None)

        def feature(value):
            return {"real": value.real, "imaginary": value.imag, "valid": True}

        report = {
            "campaign_ready": False,
            "actual_response_mesh_stability": {"status": "not_assessed", "mesh_sizes_m": [0.04],
                                               "penalty_factors": [48, 96]},
            "pilot_records": {"T_00c": [{"mesh_size_m": 0.04, "feature_gains": [None, feature(10 + 20j)]}]},
            "primary_feature_penalty_checks": {"T_00c": {"comparison_penalty_factor": 96,
                                                              "comparison_feature_gains": [None, feature(10 + 20j)]}},
        }
        _add_reference_diagnostics(report, reference)
        self.assertTrue(report["physical_reference_comparisons"]["pilot_T_00c"][0]["relative_complex_error"] > 1)
        # An exact synthetic match adds no actual response-mesh stability evidence.
        report["pilot_records"]["T_00c"][0]["feature_gains"][1] = feature(reference)
        _add_reference_diagnostics(report, reference)
        self.assertEqual(report["physical_reference_comparisons"]["pilot_T_00c"][0]["complex_absolute_error_per_m"], 0.0)
        self.assertFalse(report["campaign_ready"])
        self.assertEqual(report["actual_response_mesh_stability"]["status"], "not_assessed")
        json.dumps(report, allow_nan=False)

    def test_gate_api_and_cli_penalty_defaults_match(self) -> None:
        from realizability.cli import _arguments

        with patch("sys.argv", ["realizability", "b2-gate", "--config", "pilot.json"]):
            args = _arguments()
        self.assertEqual(
            (args.penalty_factor, args.comparison_penalty_factor),
            (run_b2_gate.__defaults__[1], run_b2_gate.__defaults__[2]),
        )
        self.assertEqual((args.penalty_factor, args.comparison_penalty_factor), (48.0, 96.0))


class BackwardEulerDecisionTests(unittest.TestCase):
    def evaluate(self, measured: float, predicted: float, residual: float = 1.0e-12, decay: float = 0.1):
        return _backward_euler_decision(decay, {
            "time_step_s": 1.0,
            "measured_energy_ratio": measured,
            "predicted_energy_ratio": predicted,
            "step_algebraic_residual": residual,
        })

    def test_correct_stable_decay_passes(self) -> None:
        result = self.evaluate(1.0 / 1.1**2, 1.0 / 1.1**2)
        self.assertTrue(result["passed"])

    def test_stable_case_energy_growth_fails(self) -> None:
        self.assertFalse(self.evaluate(1.01, 1.01)["passed"])

    def test_wrong_prediction_fails(self) -> None:
        self.assertFalse(self.evaluate(0.8, 0.9)["passed"])

    def test_excessive_residual_fails(self) -> None:
        self.assertFalse(self.evaluate(0.8, 0.8, residual=1.0e-4)["passed"])

    def test_nonfinite_diagnostics_fail_and_are_json_safe(self) -> None:
        result = self.evaluate(float("nan"), 0.8)
        self.assertFalse(result["passed"])
        self.assertIsNone(result["measured_energy_ratio"])
        json.dumps(result, allow_nan=False)

    def test_missing_or_null_diagnostics_fail_and_are_json_safe(self) -> None:
        result = _backward_euler_decision(0.1, {
            "time_step_s": 1.0,
            "measured_energy_ratio": None,
            "predicted_energy_ratio": 0.8,
            "step_algebraic_residual": 1.0e-12,
        })
        self.assertFalse(result["passed"])
        self.assertIsNone(result["measured_energy_ratio"])
        json.dumps(result, allow_nan=False)

    def test_skipped_step_is_unexecuted_not_passed(self) -> None:
        result = _backward_euler_decision(0.1, None)
        self.assertEqual(result["status"], "not_run")
        self.assertIsNone(result["passed"])

    def test_known_unstable_spectral_case_can_match_growing_step(self) -> None:
        decay = -0.03417723621999698
        predicted = 1.0 / (1.0 + decay) ** 2
        result = self.evaluate(predicted, predicted, decay=decay)
        self.assertTrue(result["passed"])
        self.assertFalse(result["checks"]["non_growth_applicable"])


if __name__ == "__main__":
    unittest.main()
