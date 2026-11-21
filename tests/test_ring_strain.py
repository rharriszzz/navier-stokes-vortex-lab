"""Independent radial mass, curved Gaussian diffusion and circulation sign checks."""
import unittest

import numpy as np
from scipy.integrate import quad
from scipy.special import ive

from physics_first import ring_strain as rings


class RingStrainTest(unittest.TestCase):
    def test_radial_kernel_including_coincidence(self):
        # Integrate the two Gaussian radial moments directly, without gammainc.
        q = np.array([0., 1e-6, .1, 1., 4., 12.])
        for order, coefficient in enumerate((4., -8.)):
            expected = [coefficient / np.sqrt(np.pi) * quad(
                lambda v: v**(2+2*order) * np.exp(-(x*v)**2), 0., 1.,
                epsabs=1e-17)[0] for x in q]
            np.testing.assert_allclose(rings.radial_factor(q*q, order), expected, rtol=1e-13)

    def test_isolated_gaussian_and_its_laplacian(self):
        # On a circular centerline |r|²/a² = k(1-cos(phi)).
        # The oriented line element contributes cos(phi) on the local tangent.
        k = 2*(rings.RADIUS/rings.CORE)**2
        b0, b1, b2 = ive([0, 1, 2], k)
        magnitude = (2*np.pi*rings.GAMMA*rings.RADIUS*b1 /
                     (np.pi**1.5 * rings.CORE**3))
        visc = (rings.NU / rings.CORE**2 *
                (4*k*(1 - (b0+b2)/(2*b1)) - 6))
        for side in (-1, 1):
            pos, tangent = rings.ring(side, 128)
            dl = (2*np.pi*rings.RADIUS/len(pos)) * tangent
            _, _, omega, lap = rings.field(pos, pos, dl)
            np.testing.assert_allclose(omega, magnitude*tangent, atol=2e-12)
            np.testing.assert_allclose(rings.NU*lap/magnitude, visc*tangent, atol=2e-13)

    def test_circulation_sign_and_velocity_scale(self):
        # Every element lies at radius R from the center and contributes along n.
        for side in (-1, 1):
            pos, tangent = rings.ring(side, 128)
            center = (side*rings.HALF_SPACING*rings.AXES[0])[None, :]
            dl = (2*np.pi*rings.RADIUS/len(pos)) * tangent
            u = rings.field(center, pos, dl, velocity_only=True)
            normal = np.array([-side*.5, 0, np.sqrt(3)/2])
            # R/a = 7.5, missing Gaussian mass < 1e-22.
            np.testing.assert_allclose(u[0], rings.GAMMA/(2*rings.RADIUS)*normal, atol=1e-15)
