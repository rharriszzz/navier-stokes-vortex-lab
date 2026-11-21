"""Independent small-mesh and thermodynamic checks for the release projection."""
import unittest

import CoolProp.CoolProp as CP
import numpy as np

from physics_first.disk_mass_balance import eos_rates, mass_matrix, projection
from physics_first.rotating_disk import dual_geometry
from physics_first.disk_release_screen import loop, shear


class MassBalanceTest(unittest.TestCase):
    def setUp(self):
        x, y = np.meshgrid(np.arange(5.), np.arange(5.))
        self.xy = np.column_stack((x.ravel(), y.ravel())) - 2
        self.cells = np.array([[a, a+1, a+6, a+5] for a in range(20) if a%5<4])
        self.wall = np.flatnonzero(abs(self.xy).max(axis=1)==2)

    def test_polynomial_flux_and_shared_faces(self):
        xy = self.xy
        a = mass_matrix(xy, self.cells, np.ones(len(xy)))
        # A direct four-face sum on a regular interior dual for linear u=(2x,3y).
        u = xy*[2, 3]
        res = a@u.ravel()
        np.testing.assert_allclose(res[np.max(abs(xy), axis=1)<2], 5)
        np.testing.assert_allclose(np.asarray(a.sum(axis=0)), 0, atol=1e-14)
        # Density and velocity average separately on each SU2 face.
        rho = 10+xy[:, 0]
        along_x = xy*[1, 0]
        res = mass_matrix(xy, self.cells, rho)@along_x.ravel()
        np.testing.assert_allclose(res[12:14], [10, 12])

    def test_discrete_pressure_force_in_core(self):
        a = mass_matrix(self.xy, self.cells, np.ones(len(self.xy)))
        pressure = 101325.+2*self.xy[:, 0]-4*self.xy[:, 1]
        force = (a.T@pressure).reshape(-1, 2)
        interior = abs(self.xy).max(axis=1)<2
        # Each interior dual has unit area; pressure force is -grad p.
        np.testing.assert_allclose(force[interior], np.tile([-2., 4.], (interior.sum(), 1)))

    def test_constrained_minimizer_against_dense_svd(self):
        self.xy[12] += [.13, -.07]
        vol, _ = dual_geometry(self.xy, self.cells, self.wall)
        rho = np.linspace(990, 1000, len(vol))
        a = mass_matrix(self.xy, self.cells, rho)
        u = np.random.default_rng(26).normal(size=self.xy.shape)
        u[self.wall] = 0
        b = a@u.ravel()
        change, info = projection(a, vol, rho, self.wall, b)
        free = np.repeat(~np.isin(np.arange(len(vol)), self.wall), 2)
        w = np.repeat(np.sqrt(vol*rho), 2)[free]
        op = a.toarray()[:, free]/w/np.sqrt(vol[:, None])/info['scale']
        lhs = np.vstack((op, np.eye(len(w))*info['damping']))
        rhs = np.r_[-b/np.sqrt(vol)/info['scale'], np.zeros(len(w))]
        direct = np.linalg.lstsq(lhs, rhs, rcond=None)[0]/w
        np.testing.assert_allclose(change.ravel()[free], direct, atol=2e-11)
        np.testing.assert_array_equal(change[self.wall], 0)

    def test_solid_rotation_loop_stress_and_eos(self):
        u = self.xy[:, ::-1]*[-3, 3]
        self.assertEqual(loop(self.xy, u, 1), 24)
        np.testing.assert_allclose(shear(self.xy, self.cells, u, 1), 0, atol=1e-14)
        fluid = CP.AbstractState('HEOS', 'Water')
        fluid.update(CP.PT_INPUTS, 101325., 293.15)
        rho, e = fluid.rhomass(), fluid.umass()
        q = rho*np.array([[1., .1, .05, e+.00625]])
        change = np.array([[1., -.3, .2, e+1234.]])
        prediction, _ = eos_rates(q, change)
        def pressure(q):
            fluid.update(CP.DmassUmass_INPUTS, q[0], q[3]/q[0]-.5*np.sum((q[1:3]/q[0])**2))
            return fluid.p()
        step = 1e-4
        fd = (pressure((q+step*change)[0])-pressure((q-step*change)[0]))/(2*step)
        self.assertAlmostEqual(fd/prediction[0], 1, places=5)
