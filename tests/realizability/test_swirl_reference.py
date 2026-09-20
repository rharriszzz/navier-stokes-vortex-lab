"""Focused checks for the optional smooth-cylinder T_00c reference."""

from __future__ import annotations

import importlib.util
import math
import unittest

import numpy as np


HAS_SCIPY = importlib.util.find_spec("scipy") is not None


@unittest.skipUnless(HAS_SCIPY, "optional SciPy reference environment is not active")
class SwirlReferenceTests(unittest.TestCase):
    parameters = dict(
        cylinder_radius=0.10,
        half_height=0.15,
        disk_radius=0.025,
        viscosity=1.0e-6,
        frequency_hz=0.01,
    )

    def test_coefficients_match_independent_quadrature(self) -> None:
        from realizability.swirl_reference import sidewall_coefficients

        count = 32
        points, weights = np.polynomial.legendre.leggauss(512)
        a = (np.arange(count) + 0.5) * math.pi
        quadrature = np.cos(a[:, None] * points) @ (weights * (1.0 - points * points) ** 2)
        self.assertLess(np.max(np.abs(sidewall_coefficients(count) - quadrature)), 4.0e-15)

    def test_axis_and_caps_obey_regular_boundary_conditions(self) -> None:
        from realizability.swirl_reference import normalized_swirl

        kwargs = {key: value for key, value in self.parameters.items() if key != "disk_radius"}
        axis = normalized_swirl(np.zeros(9), np.linspace(-0.15, 0.15, 9), terms=64, **kwargs)
        caps = normalized_swirl(np.linspace(0.0, 0.10, 31), 0.15, terms=64, **kwargs)
        near_axis_radius = np.array([1.0e-7, 2.0e-7, 4.0e-7])
        near_axis = normalized_swirl(near_axis_radius, 0.0, terms=64, **kwargs)
        self.assertLess(np.max(np.abs(axis)), 1.0e-14)
        self.assertLess(np.max(np.abs(caps)), 1.0e-13)
        self.assertTrue(np.isfinite(near_axis / near_axis_radius).all())

    def test_truncated_sidewall_series_reconstructs_target(self) -> None:
        from realizability.swirl_reference import normalized_swirl

        kwargs = {key: value for key, value in self.parameters.items() if key != "disk_radius"}
        z = np.linspace(-0.15, 0.15, 301)
        target = (1.0 - (z / 0.15) ** 2) ** 2
        value_64 = normalized_swirl(0.10, z, terms=64, **kwargs)
        value_128 = normalized_swirl(0.10, z, terms=128, **kwargs)
        error_64 = np.max(np.abs(value_64 - target))
        error_128 = np.max(np.abs(value_128 - target))
        self.assertLess(error_128, 3.5e-6)
        self.assertLess(error_128, error_64)

    def test_disk_gain_refines_and_agrees_with_radial_quadrature(self) -> None:
        from realizability.swirl_reference import disk_rotation_gain, normalized_swirl

        gains = [disk_rotation_gain(terms=count, **self.parameters) for count in (16, 32, 64, 128)]
        self.assertLess(abs(gains[-1] - gains[-2]), 1.0e-15)
        radius_nodes, weights = np.polynomial.legendre.leggauss(512)
        radius = self.parameters["disk_radius"] * (radius_nodes + 1.0) / 2.0
        radial_weights = self.parameters["disk_radius"] * weights / 2.0
        profile = normalized_swirl(
            radius, 0.0, terms=128,
            **{key: value for key, value in self.parameters.items() if key != "disk_radius"},
        )
        quadrature = 4.0 / self.parameters["disk_radius"] ** 4 * np.sum(
            radial_weights * radius**2 * profile
        )
        self.assertLess(abs(gains[-1] - quadrature), 2.0e-18)
        self.assertAlmostEqual(gains[-1].real, 2.066285885722e-5, places=15)
        self.assertAlmostEqual(gains[-1].imag, -6.595106312048e-5, places=15)

    def test_resolved_verification_fixture_refines(self) -> None:
        from realizability.swirl_reference import disk_rotation_gain

        fixture = dict(self.parameters, viscosity=1.0e-4, frequency_hz=0.001)
        coarse = disk_rotation_gain(terms=16, **fixture)
        fine = disk_rotation_gain(terms=64, **fixture)
        self.assertLess(abs(coarse - fine), 1.0e-13)
