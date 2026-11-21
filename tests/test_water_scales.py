import math
import unittest

from physics_first.water_scales import DENSITY, PEAK_X, scales


class WaterScalesTest(unittest.TestCase):
    def test_baseline_and_peak_definition(self):
        s = scales(0.01, 0.1)
        self.assertAlmostEqual(s.reynolds, 1000)
        self.assertAlmostEqual(s.viscous_time_s, 100)
        self.assertAlmostEqual(s.mach, 1 / 14800)
        self.assertAlmostEqual(s.dynamic_pressure_pa, 4.99)
        self.assertAlmostEqual(s.velocity_gradient_s_inv, 10)
        self.assertAlmostEqual(s.burgers_axial_strain_s_inv, 0.05025725)
        self.assertAlmostEqual(math.expm1(PEAK_X), 2 * PEAK_X)
        fraction = -math.expm1(-(s.peak_radius_m / s.gaussian_width_m)**2)
        self.assertAlmostEqual(s.circulation_m2_s * fraction / (2 * math.pi * 0.01), 0.1)

    def test_pressure_against_radial_force_quadrature(self):
        s = scales(0.01, 0.1)
        # Integrate rho*u_theta^2/r in log(r/b), so dr/r = d(log(r/b)).
        intervals = 4096
        step = 32 / intervals
        terms = []
        for i in range(intervals):
            ratio = math.exp(-16 + (i + 0.5) * step)
            radius = ratio * s.gaussian_width_m
            speed = s.circulation_m2_s * -math.expm1(-ratio**2) / (2 * math.pi * radius)
            terms.append(DENSITY * speed**2 * step)
        self.assertAlmostEqual(math.fsum(terms), s.center_deficit_pa, places=9)

    def test_fixed_circulation_family(self):
        initial = scales(0.01, 0.1)
        for radius in (0.003, 0.001):
            factor = 0.01 / radius
            s = scales(radius, 0.1 * factor)
            self.assertAlmostEqual(s.circulation_m2_s, initial.circulation_m2_s)
            self.assertAlmostEqual(s.reynolds, initial.reynolds)
            self.assertAlmostEqual(s.center_deficit_pa, initial.center_deficit_pa * factor**2)
            self.assertAlmostEqual(s.burgers_axial_strain_s_inv,
                                   initial.burgers_axial_strain_s_inv * factor**2)

    def test_rest_and_invalid_inputs(self):
        self.assertEqual(scales(0.01, 0).center_deficit_pa, 0)
        for radius, speed in ((0, 0.1), (-1, 0.1), (0.01, -1), (math.nan, 1), (1, math.inf)):
            with self.assertRaises(ValueError):
                scales(radius, speed)
