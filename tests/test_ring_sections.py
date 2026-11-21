"""Geometry, cancellation and local frames that the original centerline tests do not exercise."""
import unittest

import numpy as np

from physics_first import ring_strain as rs
from scipy.integrate import quad
from scipy.special import erf

from physics_first.ring_preparation import energy_term, RHO
from physics_first.ring_sections import frame, samples
from physics_first.ring_thresholds import placement


class SectionGeometryTest(unittest.TestCase):
    def test_gap_and_orientation_are_independent(self):
        for tilt in np.deg2rad([25.,30.,35.]):
            opts = placement(.008,tilt)
            x,t = rs.ring(-1,128,**opts)
            y,_ = rs.ring(1,128,**opts)
            self.assertAlmostEqual(np.min(np.linalg.norm(x[:,None]-y,axis=2)),.008)
            center,tangent,basis = frame(11.25,.008,tilt)
            np.testing.assert_array_equal(center,x[4])
            np.testing.assert_array_equal(tangent,t[4])
            np.testing.assert_allclose(np.cross(*basis),tangent,atol=1e-14)

    def test_midpoint_has_no_fractional_rate(self):
        points,checks = samples(0,.008,.002,.0036,np.pi/6,128,())
        null, = (r for r in points if r['symmetry_null'])
        self.assertAlmostEqual(null['r_a'],2)
        self.assertIsNone(null['net'])
        self.assertEqual(null['net_abs'],0.)
        self.assertLess(checks['null_raw_omega'],1e-12)
        near, = (r for r in points if r['r_a']==.5 and r['phi_deg']==0)
        self.assertGreater(near['net'],0.)
        self.assertLess(near['iso_net'],0.)

    def test_single_ring_energy_against_angular_integral(self):
        # Rotational invariance reduces the double line integral to a chord integral.
        x,t = rs.ring(-1,256)
        dl = t*(2*np.pi*rs.RADIUS/len(x))
        def integrand(angle):
            chord = 2*rs.RADIUS*np.sin(angle/2)
            return np.cos(angle)*erf(chord/(np.sqrt(2)*rs.CORE))/chord
        expected = RHO*rs.GAMMA**2*rs.RADIUS**2/4 * quad(integrand,0,2*np.pi)[0]
        self.assertAlmostEqual(energy_term((x,dl),(x,dl),rs.CORE,rs.GAMMA),expected,places=14)
