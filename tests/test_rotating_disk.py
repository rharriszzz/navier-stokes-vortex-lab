"""Verification of the rotating-water analytical and discrete controls."""

import unittest

import numpy as np
from scipy.special import j1

from physics_first.cylinder_spreading import WALL, radial_rule
from physics_first.no_slip_disk import evaluate, project


class NoSlipTest(unittest.TestCase):
    def test_first_dirichlet_mode(self):
        r, w = radial_rule(512)
        k = 3.8317059702075125 / WALL
        series = project(16, r, w, lambda x: j1(x*k))
        np.testing.assert_allclose(series.amplitudes, [1, *([0]*15)], atol=1e-12)
        self.assertLess(abs(series.velocity(WALL, series.amplitudes).item()), 1e-14)

    def test_torque_and_dissipation(self):
        rows = evaluate(128, 2048)["snapshots"]
        for row in rows:
            self.assertLess(abs(row["angular_rate_N"] - row["wall_torque_per_length_N"]), 1e-16)
        loss = rows[0]["energy_J_m"] - rows[1]["energy_J_m"]
        trap = .0005 * (rows[0]["dissipation_W_m"] + rows[1]["dissipation_W_m"])
        self.assertAlmostEqual(loss/trap, 1., places=7)
