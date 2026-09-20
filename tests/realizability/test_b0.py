"""Independent B0 checks specified in BOUNDARY_CONTROL_HANDOFF.md."""

from __future__ import annotations

from dataclasses import replace
import math
import unittest

import numpy as np

from realizability.boundary_modes import (
    axial_shape,
    azimuthal_design_matrix,
    canonical_modes,
    gram_matrix,
    mode_scalar,
    net_flux,
    parse_mode,
    side_quadrature,
)
from realizability.config import FluidConfig, GeometryConfig, PilotConfig, ReferenceConfig
from realizability.observables import (
    axial_strain,
    fitted_rotation,
    fourier_coefficients,
    measure_core,
    radial_strain,
    reynolds_stress,
    single_mode_spatial_correlation,
)
from realizability.reference import (
    circulation,
    core_radius,
    finite_difference_divergence,
    raw_swirl,
    strain_rate,
    velocity,
)
from realizability.response import assess_identifiability, scaled_gain, singular_value_report


class BoundaryModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.geometry = GeometryConfig()

    def test_axial_integrals_flux_and_gram(self) -> None:
        points, weights = np.polynomial.legendre.leggauss(32)
        self.assertAlmostEqual(float(np.dot(weights, axial_shape(points, 0))), 16.0 / 15.0, places=13)
        self.assertAlmostEqual(float(np.dot(weights, axial_shape(points, 1))), 0.0, places=13)
        self.assertAlmostEqual(float(np.dot(weights, axial_shape(points, 2))), 0.0, places=13)
        with self.assertRaisesRegex(ValueError, "nonzero net flux"):
            parse_mode("N_00c")
        modes = canonical_modes(PilotConfig().mode_order)
        for mode in modes:
            theta = np.linspace(0.0, 2.0 * np.pi, 720, endpoint=False)
            s = np.linspace(-1.0, 1.0, 1001)
            theta_grid, s_grid = np.meshgrid(theta, s, indexing="ij")
            self.assertAlmostEqual(float(np.max(np.abs(mode_scalar(mode, theta_grid, s_grid)))), 1.0, places=10)
            self.assertAlmostEqual(net_flux(mode, self.geometry), 0.0, places=13)
        gram = gram_matrix(modes, self.geometry)
        self.assertTrue(np.all(np.linalg.eigvalsh(gram) > 0.0))

    def test_ideal_ring_ranks_and_m4_aliasing(self) -> None:
        expected_ranks = {8: 8, 12: 12, 16: 13}
        for samples, expected in expected_ranks.items():
            self.assertEqual(np.linalg.matrix_rank(azimuthal_design_matrix(samples, 6)), expected)
        theta = 2.0 * np.pi * np.arange(8) / 8
        self.assertEqual(np.linalg.matrix_rank(np.column_stack((np.cos(4 * theta), np.sin(4 * theta)))), 1)


class ReferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fluid = FluidConfig()
        self.config = ReferenceConfig()

    def test_reference_divergence_boundary_and_axis(self) -> None:
        rng = np.random.default_rng(20260919)
        points = rng.uniform([-0.079, -0.079, -0.119], [0.079, 0.079, 0.119], size=(2000, 3))
        rms = []
        for spacing in (1.0e-4, 5.0e-5, 2.5e-5):
            rms.append(float(np.sqrt(np.mean(finite_difference_divergence(points, spacing, 50.0, self.fluid, self.config) ** 2))))
        self.assertLess(rms[1], rms[0] / 3.5)
        self.assertLess(rms[2], rms[1] / 3.5)
        theta = np.linspace(0.0, 2.0 * np.pi, 20, endpoint=False)
        boundary = np.vstack(
            (
                np.column_stack((0.1 * np.cos(theta), 0.1 * np.sin(theta), np.zeros_like(theta))),
                np.column_stack((0.05 * np.cos(theta), 0.05 * np.sin(theta), np.full_like(theta, 0.15))),
                np.column_stack((0.05 * np.cos(theta), 0.05 * np.sin(theta), np.full_like(theta, -0.15))),
            )
        )
        self.assertLess(float(np.max(np.abs(velocity(boundary, 50.0, self.fluid, self.config)))), 1.0e-15)
        axis = velocity(np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.01]]), 50.0, self.fluid, self.config)
        self.assertTrue(np.isfinite(axis).all())
        epsilon = 1.0e-9
        near_axis = velocity(np.array([[epsilon, 0.0, 0.0]]), 50.0, self.fluid, self.config)[0]
        expected_angular = circulation(self.config) / (2.0 * math.pi * (core_radius(50.0, self.config) ** 2 / 1.2564312086261697))
        self.assertAlmostEqual(near_axis[1] / epsilon, expected_angular, places=6)

    def test_raw_swirl_peaks_and_invalid_core_cases(self) -> None:
        expected = {0.0: (0.010, 0.010), 50.0: (0.007382411530116699, 0.01354570922957193), 100.0: (0.003, 1.0 / 30.0)}
        for time, (expected_radius, expected_speed) in expected.items():
            radius = np.linspace(0.0, 0.025, 250_001)
            swirl = raw_swirl(radius, time, self.config)
            measured = measure_core(radius, swirl)
            self.assertTrue(measured.valid)
            self.assertAlmostEqual(measured.radius, expected_radius, delta=2.0e-7)
            self.assertAlmostEqual(measured.peak_swirl, expected_speed, places=7)
        radius = np.linspace(0.0, 0.025, 51)
        self.assertEqual(measure_core(radius, np.zeros_like(radius)).reason, "below_threshold")
        multiple = np.zeros_like(radius)
        multiple[20] = multiple[30] = 1.0
        self.assertEqual(measure_core(radius, multiple).reason, "multiple_maxima")
        edge = np.exp(-radius)
        self.assertEqual(measure_core(radius, edge).reason, "peak_at_edge")

    def test_reference_time_sensitivity(self) -> None:
        start_rates = []
        for duration in (30.0, 100.0, 300.0):
            target = replace(self.config, duration=duration)
            start_rates.append(strain_rate(0.0, self.fluid, target))
        self.assertGreater(start_rates[0], start_rates[1])
        self.assertGreater(start_rates[1], start_rates[2])


class ObservableTests(unittest.TestCase):
    def test_strain_rotation_fourier_and_stress(self) -> None:
        a = 0.37
        omega = -0.22
        x = np.linspace(-0.025, 0.025, 71)
        z = np.linspace(-0.025, 0.025, 73)
        x_grid, z_grid = np.meshgrid(x, z, indexing="ij")
        weights_vertical = np.full_like(x_grid, (x[1] - x[0]) * (z[1] - z[0]))
        self.assertAlmostEqual(axial_strain(z_grid, 2.0 * a * z_grid, weights_vertical), a, places=12)
        radius = np.linspace(0.001, 0.025, 37)
        theta = np.linspace(0.0, 2.0 * np.pi, 128, endpoint=False)
        r_grid, theta_grid = np.meshgrid(radius, theta, indexing="ij")
        x_disk = r_grid * np.cos(theta_grid)
        y_disk = r_grid * np.sin(theta_grid)
        weights_disk = r_grid * (radius[1] - radius[0]) * (theta[1] - theta[0])
        u_x = -a * x_disk - omega * y_disk
        u_y = -a * y_disk + omega * x_disk
        self.assertAlmostEqual(radial_strain(x_disk, y_disk, u_x, u_y, weights_disk), a, places=12)
        self.assertAlmostEqual(fitted_rotation(x_disk, y_disk, u_x, u_y, weights_disk), omega, places=12)
        values = 0.04 * np.cos(4.0 * theta_grid) - 0.07 * np.sin(4.0 * theta_grid)
        c, s = fourier_coefficients(values, theta_grid, weights_disk, 4)
        self.assertAlmostEqual(c, 0.04, places=12)
        self.assertAlmostEqual(s, -0.07, places=12)
        u_r = np.broadcast_to(0.04 * np.cos(4.0 * theta)[np.newaxis, :], r_grid.shape)
        u_theta = np.broadcast_to(0.08 * np.cos(4.0 * theta)[np.newaxis, :], r_grid.shape)
        radial_weights = radius * (radius[1] - radius[0])
        self.assertAlmostEqual(reynolds_stress(u_r, u_theta, theta, radial_weights), 0.04 * 0.08 / 2.0, places=12)
        spatial = single_mode_spatial_correlation(0.04, 0.0, 0.08, 0.0)
        time = np.linspace(0.0, 2.0 * np.pi, 1000, endpoint=False)
        self.assertAlmostEqual(np.mean(spatial * np.cos(time) ** 2), spatial / 2.0, places=12)


class ResponseTests(unittest.TestCase):
    def test_scaled_gain_is_unit_invariant_and_rank_is_honest(self) -> None:
        gain = np.array(
            [
                [2.0, -1.0],
                [3.0, 1.0],
                [4.0, 2.0],
                [1.0, 5.0],
                [-2.0, 3.0],
                [6.0, -4.0],
            ]
        )
        gram = np.diag([0.5, 2.0])
        output_scales = np.array([1.0, 2.0, 0.1, 0.2, 0.3, 0.4])
        scaled = scaled_gain(gain, gram, output_scales, 1.0e-7)
        unit_scale = 1000.0  # SI metres/metres-per-second -> millimetres/millimetres-per-second
        gain_in_millimetres = gain.copy()
        gain_in_millimetres[:2] /= unit_scale  # strain outputs stay in 1/s; input speed number changes.
        output_scales_in_millimetres = output_scales.copy()
        output_scales_in_millimetres[2:] *= unit_scale
        self.assertTrue(
            np.allclose(
                scaled,
                scaled_gain(
                    gain_in_millimetres,
                    gram,
                    output_scales_in_millimetres,
                    1.0e-7 * unit_scale,
                ),
            )
        )
        report = singular_value_report(np.array([[1.0, 0.0], [0.0, 0.0], [0.0, 0.0]]))
        self.assertEqual(report.numerical_rank, 1)
        self.assertEqual(report.missing_output_directions, 2)
        self.assertIsNotNone(report.condition_number)

    def test_identifiability_nullspace_examples(self) -> None:
        failing = assess_identifiability(np.array([[1.0, 0.0]]), np.array([[0.0, 1.0]]))
        self.assertFalse(failing.identifiable)
        self.assertGreater(failing.q_on_measurement_nullspace_norm, 0.9)
        passing = assess_identifiability(np.array([[1.0, 0.0]]), np.array([[1.0, 0.0]]))
        self.assertTrue(passing.identifiable)


if __name__ == "__main__":
    unittest.main()
