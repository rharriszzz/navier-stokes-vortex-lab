"""Verification of the rotating-water analytical and discrete controls."""

import importlib.util
import unittest

import numpy as np

requires_water = unittest.skipUnless(
    all(importlib.util.find_spec(k) for k in ("CoolProp", "scipy")), "water disk requires SciPy and CoolProp"
)


@requires_water
class NoSlipTest(unittest.TestCase):
    def test_first_dirichlet_mode(self):
        from scipy.special import j1
        from physics_first.cylinder_spreading import WALL, radial_rule
        from physics_first.no_slip_disk import project

        r, w = radial_rule(512)
        k = 3.8317059702075125 / WALL
        series = project(16, r, w, lambda x: j1(x*k))
        np.testing.assert_allclose(series.amplitudes, [1, *([0]*15)], atol=1e-12)
        self.assertLess(abs(series.velocity(WALL, series.amplitudes).item()), 1e-14)

    def test_torque_and_dissipation(self):
        from physics_first.no_slip_disk import evaluate

        rows = evaluate(128, 2048)["snapshots"]
        for row in rows:
            self.assertLess(abs(row["angular_rate_N"] - row["wall_torque_per_length_N"]), 1e-16)
        loss = rows[0]["energy_J_m"] - rows[1]["energy_J_m"]
        trap = .0005 * (rows[0]["dissipation_W_m"] + rows[1]["dissipation_W_m"])
        self.assertAlmostEqual(loss/trap, 1., places=7)


@requires_water
class DiskGeometryTest(unittest.TestCase):
    def test_dual_area_and_rotation(self):
        from physics_first.cylinder_spreading import WALL
        from physics_first.rotating_disk import mesh, dual_geometry
        xy, quads, wall = mesh(16)
        area, perimeter = dual_geometry(xy, quads, wall)
        boundary = xy[wall]
        polygon = .5*np.sum(boundary[:, 0]*np.roll(boundary[:, 1], -1)
                            - boundary[:, 1]*np.roll(boundary[:, 0], -1))
        self.assertAlmostEqual(area.sum(), polygon, places=14)
        self.assertTrue(np.all(perimeter>0))
        self.assertEqual(len(np.unique(quads)), len(xy))
        np.testing.assert_allclose(np.linalg.norm(boundary, axis=1), WALL, atol=1e-15)

    def test_quadratic_peak(self):
        from physics_first.disk_pilot import peak_fit
        r = np.arange(7)*.003
        u = 0.1 - 9*(r-.01)**2
        np.testing.assert_allclose(peak_fit(r, u, r>0), [.01, .1], atol=1e-12)
