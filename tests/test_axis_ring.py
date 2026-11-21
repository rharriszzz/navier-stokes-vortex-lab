"""Axis regularity, physical normalization and reproducible release measurements."""
import unittest

import numpy as np

from physics_first.axis_ring import CORE, GAMMA, RADIUS, Grid, derivative, release
from physics_first.axis_ring_measure import shape
from physics_first.axis_ring_verify import probes, reference


class AxisRingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = Grid(8)

    def test_axis_limit_and_mass_flux(self):
        g = self.g
        # Even quartic psi is exactly differentiated even on the stretched grid.
        phi = (1+g.R**2)*(1+g.Z+g.Z**2)
        u,v = g.velocity(phi)
        np.testing.assert_allclose(v, (2+4*g.R**2)*(1+g.Z+g.Z**2), atol=1e-11)
        du = derivative(g.r,1) @ u
        np.testing.assert_allclose(2*du[0]+g.axial(v)[0], 0, atol=1e-9)
        s = g.R**4 + g.Z**2
        np.testing.assert_allclose(g.diffusion(s),np.broadcast_to(24*g.R**2 + 2,g.shape),atol=2e-8)

    def test_oriented_curl_against_archived_line_integral(self):
        g = self.g
        p = probes()
        u,w,_ = reference(p)
        eta = release(g.R,g.Z)
        np.testing.assert_allclose(p[:,0]*release(*p.T),w,rtol=3e-14)
        ur,uz = g.velocity(g.invert(eta))
        np.testing.assert_allclose(g.interpolate(ur)(*p.T),u[:,0],atol=1.2e-5)
        np.testing.assert_allclose(g.interpolate(uz)(*p.T),u[:,1],atol=1.2e-5)

    def test_aperture_normalization_and_eigenvalues(self):
        center = np.array([RADIUS,0])
        radius = 2*CORE
        section = shape(lambda r,z: np.ones_like(r)*GAMMA/(np.pi*radius**2), center, radius)
        self.assertAlmostEqual(section['flux'],GAMMA,14)
        self.assertAlmostEqual(section['major'],radius/np.sqrt(2),14)
        self.assertAlmostEqual(section['minor'],radius/np.sqrt(2),14)

    def test_release_section_against_archive(self):
        g = self.g
        section = shape(g.interpolate(g.R*release(g.R,g.Z)),np.array([RADIUS,0]),2*CORE)
        self.assertAlmostEqual(section['flux'],.003533145880159973,delta=4e-9)
        self.assertAlmostEqual(section['minor'],.001923640719113354,delta=1e-8)
