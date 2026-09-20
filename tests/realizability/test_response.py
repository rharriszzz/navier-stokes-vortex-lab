"""Phase-sensitive checks for real and harmonic response diagnostics."""

from __future__ import annotations

import unittest

import numpy as np

from realizability.response import (
    assess_identifiability,
    inverse_square_root,
    numerical_nullspace,
    scaled_gain,
    singular_value_report,
)


class ComplexResponseTests(unittest.TestCase):
    def test_hermitian_gram_whitening(self) -> None:
        # Eigenvalues are 1 and 4; the positive inverse root is known exactly.
        gram = np.array([[2.5, 1.5j], [-1.5j, 2.5]])
        expected = np.array([[0.75, -0.25j], [0.25j, 0.75]])
        root = inverse_square_root(gram)
        np.testing.assert_allclose(root, expected, atol=1.0e-14)
        np.testing.assert_allclose(root, root.conj().T, atol=1.0e-14)
        np.testing.assert_allclose(root.conj().T @ gram @ root, np.eye(2), atol=1.0e-14)

    def test_scaled_harmonic_gain_preserves_phase_and_units(self) -> None:
        gain = np.array([[2.0 + 4.0j, 6.0 - 3.0j], [-4.0j, 12.0 + 6.0j]])
        gram = np.diag([4.0, 9.0])
        scales = np.array([2.0, 4.0])
        scaled = scaled_gain(gain, gram, scales, 0.5)
        expected = np.array([[0.25 + 0.5j, 0.5 - 0.25j], [-0.25j, 0.5 + 0.25j]])
        np.testing.assert_allclose(scaled, expected, atol=1.0e-14)
        # Independent changes of input and output units cancel in normalization.
        input_unit = 1000.0
        output_units = np.array([1.0, 1000.0])
        rescaled = scaled_gain(
            gain * output_units[:, None] / input_unit,
            gram,
            scales * output_units,
            0.5 * input_unit,
        )
        np.testing.assert_allclose(rescaled, scaled, atol=1.0e-14)

    def test_singular_values_include_quadrature_response(self) -> None:
        # Columns are orthogonal with norm sqrt(2); dropping phase loses one.
        gain = np.array([[1.0, 1.0j], [1.0, -1.0j], [0.0, 0.0]])
        report = singular_value_report(gain)
        np.testing.assert_allclose(report.singular_values, [np.sqrt(2.0)] * 2)
        self.assertEqual(report.numerical_rank, 2)
        self.assertEqual(report.missing_output_directions, 1)
        self.assertAlmostEqual(report.condition_number, 1.0)
        phase_shifted = singular_value_report(1.0j * gain)
        np.testing.assert_allclose(phase_shifted.singular_values, report.singular_values)

    def test_complex_right_nullspace_is_orthonormal_and_annihilated(self) -> None:
        cases = (
            (np.array([[1.0, 1.0j, 0.0]]), 2),
            (np.array([[1.0, 1.0j], [2.0, 2.0j], [0.0, 0.0]]), 1),
            (np.diag([1.0j, 2.0j]), 0),
            (np.zeros((2, 3), dtype=complex), 3),
        )
        for matrix, nullity in cases:
            with self.subTest(shape=matrix.shape, nullity=nullity):
                basis = numerical_nullspace(matrix)
                self.assertEqual(basis.shape, (matrix.shape[1], nullity))
                np.testing.assert_allclose(matrix @ basis, 0.0, atol=1.0e-14)
                np.testing.assert_allclose(basis.conj().T @ basis, np.eye(nullity), atol=1.0e-14)

    def test_identifiability_preserves_measurement_and_feature_phase(self) -> None:
        measurement = np.array([[1.0, 1.0j, 0.0]])
        passing = assess_identifiability(measurement, (2.0 - 3.0j) * measurement)
        self.assertTrue(passing.identifiable)
        self.assertEqual(passing.nullity, 2)
        self.assertLess(passing.q_on_measurement_nullspace_norm, 1.0e-14)

        # The same real part does not imply the same observable combination.
        opposite_phase = assess_identifiability(measurement, measurement.conj())
        self.assertFalse(opposite_phase.identifiable)
        self.assertAlmostEqual(opposite_phase.q_on_measurement_nullspace_norm, np.sqrt(2.0))

        # A wholly imaginary feature on an unmeasured state must remain visible.
        unmeasured = assess_identifiability(measurement, np.array([[0.0, 0.0, 2.0j]]))
        self.assertFalse(unmeasured.identifiable)
        self.assertAlmostEqual(unmeasured.q_on_measurement_nullspace_norm, 2.0)


if __name__ == "__main__":
    unittest.main()
