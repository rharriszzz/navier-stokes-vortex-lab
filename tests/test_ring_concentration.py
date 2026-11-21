import unittest

import numpy as np
from scipy.integrate import simpson

from physics_first.axis_ring import CORE, GAMMA
from physics_first.ring_concentration import moments, radii


class ConcentrationTest(unittest.TestCase):
    def test_translated_gaussian_has_known_width_area_and_fraction_radii(self):
        x=np.linspace(-8*CORE,8*CORE,161)
        center=np.array([.6*CORE,-.3*CORE])
        def gaussian(r,z):
            return GAMMA/(np.pi*CORE**2)*np.exp(-((r-center[0])**2+(z-center[1])**2)/CORE**2)
        r,z=x[:,None],x[None,:]
        axis_weights=simpson(np.eye(len(x)),x=x)
        c,m=moments(r,z,gaussian(r,z),np.outer(axis_weights,axis_weights))
        np.testing.assert_allclose(c,center,rtol=1e-12)
        np.testing.assert_allclose([m['minor_m'],m['major_m']],CORE,rtol=1e-12)
        self.assertAlmostEqual(m['aeff_m2']/(2*np.pi*CORE**2),1)
        for f,radius in zip((.25,.5,.75),radii(gaussian,center).values(),strict=True):
            self.assertAlmostEqual(radius/CORE,np.sqrt(-np.log1p(-f)),places=10)

    def test_pair_assignment_at_facing_midplane(self):
        from physics_first.ring_assignment import study
        table = {(r['gap_mm'],r['radius_mm'],r['order']): r for r in study()}
        facing = table[8.,4.,32]
        # Independent archived 512-line source and contour integral.
        self.assertAlmostEqual(facing['flux_over_gamma'],.9800286457206975,places=12)
        self.assertLess(facing['r75_inside_midplane_mm'],4)
        self.assertIsNone(table[4.,2.,32]['r75_inside_midplane_mm'])
        self.assertIsNone(table[2.,1.,32]['r25_inside_midplane_mm'])
