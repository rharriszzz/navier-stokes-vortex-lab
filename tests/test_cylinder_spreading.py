"""Independent mode and finite-domain checks for the optional SciPy benchmark."""

import importlib.util
import unittest

import numpy as np


@unittest.skipUnless(importlib.util.find_spec("scipy"), "cylinder reference requires SciPy")
class CylinderModesTest(unittest.TestCase):
    def test_rigid_rotation_survives_projection(self):
        from physics_first.cylinder_spreading import Expansion, WALL, radial_rule

        r, w = radial_rule(512)
        rotation = Expansion.project(32, r, w, lambda x: 3 * x)
        u = rotation.velocity(r, rotation.at_time(5))
        np.testing.assert_allclose(u, 3 * r, atol=1e-12)
        np.testing.assert_allclose(rotation.vorticity(r, rotation.at_time(5)), 6, atol=1e-10)
        self.assertAlmostEqual(w @ (r**2 * u), 3 * WALL**4 / 4, places=15)

    def test_first_decaying_mode_at_axis_and_wall(self):
        from scipy.special import j1
        from physics_first.cylinder_spreading import Expansion, VISCOSITY, WALL, radial_rule

        # Independently tabulated first positive J2 root.
        k = 5.135622301840683 / WALL
        r, w = radial_rule(512)
        mode = Expansion.project(32, r, w, lambda x: j1(k * x))
        amplitudes = mode.at_time(5)
        decay = np.exp(-5 * VISCOSITY * k**2)
        np.testing.assert_allclose(mode.velocity(r, amplitudes), j1(k * r) * decay, atol=1e-12)
        self.assertAlmostEqual(mode.vorticity(0, amplitudes).item(), k * decay, places=9)
        h = 1e-6
        left, wall, right = mode.velocity(np.array([WALL-h, WALL, WALL+h]), amplitudes)
        self.assertAlmostEqual((right-left)/(2*h) - wall/WALL, 0, places=7)

    def test_sampled_initial_condition(self):
        from physics_first.cylinder_spreading import initial_swirl, oseen

        r = np.array([0, 0.010, 0.060, 0.070, 0.080, 0.100])
        expected = oseen(r, 0)[0] * np.array([1, 1, 1, 0.5, 0, 0])
        np.testing.assert_allclose(initial_swirl(r), expected, atol=1e-15)
        self.assertAlmostEqual(expected[1], 0.100)
