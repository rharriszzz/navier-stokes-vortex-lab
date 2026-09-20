"""Dependency-free regressions for B2 gate acceptance and reporting."""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from realizability.backends.b2_gate import format_b2_gate, run_b2_gate
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
            report = run_b2_gate(object(), mesh_sizes=(0.04, 0.03))
            markdown = format_b2_gate(report)
        harmonic.assert_not_called()
        self.assertFalse(report["all_numerical_gates_passed"])
        self.assertIn("not run", markdown)
        self.assertIn("0.1 m, 0.07 m", markdown)
        self.assertIn("6, 48", markdown)

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
