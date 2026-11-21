"""Independent staggered indexing, constitutive laws and pressure response."""
import importlib.util
import json
from pathlib import Path
import unittest

import numpy as np


@unittest.skipUnless(importlib.util.find_spec("CoolProp"), "requires HEOS Water")
class StaggeredWaterTest(unittest.TestCase):
    def setUp(self):
        from physics_first.liquid_imex import Liquid
        self.w = Liquid()

    def test_uniform_translation(self):
        from physics_first.liquid_imex_2d import step
        U = np.broadcast_to(np.array([1.e-6, .4, -.7, .003])[:, None, None], (4, 5, 11))
        V, p, _, (res, corrections, _, _) = step(self.w, U, 1e-10, 2e-7, 3e-7)
        np.testing.assert_array_equal(V, U)
        self.assertEqual(p.max(), p.min())
        self.assertEqual((res, corrections), (0, 0))

    def test_dual_fluxes_work_and_conduction(self):
        from physics_first.liquid_imex_2d import slow, fluxes, step
        from physics_first.liquid_imex import P0
        rng = np.random.default_rng(294)
        dx, dy = 2e-6, 3e-6
        ny, nx = 5, 7
        r, mx, my, H = rng.normal(size=(4, ny, nx))*np.array([1e-5, .5, 1., .1])[:, None, None]
        w = self.w
        U = np.array([r, mx, my, H])
        s = slow(w, U, dx, dy)
        fx, fy = fluxes(s, s.pressure, mx, my)
        # Hand-index the neighbors of a single interior volume and its corner.
        j, i = 2, 3

        def u(b, a):
            return mx[b,a]/(w.rho+(r[b,a]+r[b,a+1])/2)

        def v(b, a):
            return my[b,a]/(w.rho+(r[b,a]+r[b+1,a])/2)

        def cell(b, a):
            ux = (u(b,a)-u(b,a-1))/dx
            vy = (v(b,a)-v(b-1,a))/dy
            xx = w.mu*(4*ux-2*vy)/3
            yy = w.mu*(4*vy-2*ux)/3
            K = (mx[b,a]*u(b,a)+mx[b,a-1]*u(b,a-1)
                 + my[b,a]*v(b,a)+my[b-1,a]*v(b-1,a))/(4*(w.rho+r[b,a]))
            e = H[b,a]/(w.rho+r[b,a])-K
            p, T = w.thermo(np.array([r[b,a]]), np.array([e]))
            return xx, yy, p[0], T[0], e+(P0+p[0])/(w.rho+r[b,a])+K

        def corner(b, a):
            return w.mu*((u(b+1,a)-u(b,a))/dy+(v(b,a+1)-v(b,a))/dx)

        c, east, north = cell(j,i), cell(j,i+1), cell(j+1,i)
        stress = corner(j,i)
        self.assertAlmostEqual(fx[1,j,i], (mx[j,i]+mx[j,i+1])*(u(j,i)+u(j,i+1))/4-east[0]+east[2])
        self.assertAlmostEqual(fy[2,j,i], (my[j,i]+my[j+1,i])*(v(j,i)+v(j+1,i))/4-north[1]+north[2])
        self.assertAlmostEqual(fx[2,j,i], (mx[j,i]+mx[j+1,i])*(v(j,i)+v(j,i+1))/4-stress)
        self.assertAlmostEqual(fy[1,j,i], (my[j,i]+my[j,i+1])*(u(j,i)+u(j+1,i))/4-stress)
        ex = (mx[j,i]*(c[4]+east[4])/2-u(j,i)*(c[0]+east[0])/2
              - (stress*(v(j,i)+v(j,i+1))+corner(j-1,i)*(v(j-1,i)+v(j-1,i+1)))/4
              - w.k*(east[3]-c[3])/dx)
        ey = (my[j,i]*(c[4]+north[4])/2-v(j,i)*(c[1]+north[1])/2
              - (stress*(u(j,i)+u(j+1,i))+corner(j,i-1)*(u(j,i-1)+u(j+1,i-1)))/4
              - w.k*(north[3]-c[3])/dy)
        np.testing.assert_allclose([fx[3,j,i], fy[3,j,i]], [ex, ey], rtol=3e-15)

        # Advance this genuinely 2D state. Assemble each shared flux by
        # depositing equal and opposite amounts into its two volumes.
        dt = 1e-10
        V, trial, (fx, fy), _ = step(w, U, dt, dx, dy)
        balance = U.astype(np.longdouble)
        for b, a in np.ndindex(ny, nx):
            for neighbor, spacing, field in [((b, (a+1)%nx), dx, fx),
                                              (((b+1)%ny, a), dy, fy)]:
                transport = np.longdouble(dt)*field[:,b,a].astype(np.longdouble)/spacing
                balance[:,b,a] -= transport
                balance[:,neighbor[0],neighbor[1]] += transport
        np.testing.assert_allclose(V, balance, rtol=3e-15, atol=1e-20)
        np.testing.assert_allclose([fx[0],fy[0]], (U[1:3]+V[1:3])/2, rtol=3e-15)
        self.assertGreater(np.ptp(trial, axis=0).max(), 1.)

    def test_zero_viscosity_shear_fixed_point(self):
        from physics_first.liquid_imex_2d import step
        from physics_first.liquid_shear import initial, LENGTH, HEIGHT
        self.w.mu = 0.  # Conductivity stays physical.
        for shifted in (False, True):
            U = initial(self.w, 128, 4, shifted)
            V, p, _, (_, _, stress_power, _) = step(
                self.w, U, 8*LENGTH/(2048*self.w.c), LENGTH/128, HEIGHT/4)
            np.testing.assert_array_equal(V, U)
            np.testing.assert_array_equal(p, 0.)
            self.assertEqual(stress_power, 0.)

    def test_pressure_adjoint_and_nyquist_acoustics(self):
        from physics_first.liquid_imex_2d import divergence, gradient
        from physics_first.liquid_shear import checkerboard
        rng = np.random.default_rng(94)
        p, mx, my = rng.normal(size=(3, 5, 8))
        a = np.sum(p*divergence(mx, my, .4, .7))
        b = np.sum(mx*gradient(p, -1, .4)+my*gradient(p, -2, .7))
        self.assertAlmostEqual(a, -b, places=12)
        results = checkerboard(self.w)
        for row in results:
            self.assertTrue(row["pass"], row)

    def test_checkpoint_fields_against_discrete_shear_mode(self):
        from physics_first.su2_shear import LENGTH, HEIGHT
        archive = Path(__file__).resolve().parents[1]/"docs/physics-first/r294"
        for prefix in ("pilot", "matrix"):
            results = json.loads((archive/(prefix+".json")).read_text())
            self.assertTrue(results["pass"])
            self.assertEqual(len(results["cases"]), 1 if prefix == "pilot" else 17)
            with np.load(archive/(prefix+".npz")) as fields:
                self.assertEqual(set(results["cases"]), set(fields.files))
                for key, run in results["cases"].items():
                    q = fields[key]
                    nx, ny = run["nx"], run["ny"]
                    self.assertEqual(q.shape, (5, 6, ny, nx))
                    scale = 2*np.sin(np.pi/nx)*nx/LENGTH
                    z = -(self.w.mu/self.w.rho)*run["dt_s"]*scale**2
                    # Transfer function of explicit midpoint applied to the
                    # transverse diffusion eigenvector. Includes time error.
                    steps = np.arange(5)*(run["steps"]//4)
                    ratio = np.exp(steps*np.log1p(z+z*z/2))
                    v = q[:,2]/(self.w.rho+(q[:,0]+np.roll(q[:,0],-1,axis=1))/2)
                    modes = np.fft.rfft(v, axis=2)[:,:,1].mean(axis=1)
                    np.testing.assert_allclose(modes/modes[0], ratio, rtol=1e-13)
                    # Independently gather each unique transverse column.
                    for n, snap in enumerate(run["checkpoints"]):
                        ranges = [max(col)-min(col) for col in q[n,5].T]
                        np.testing.assert_array_equal(ranges, snap["strip_range_by_x_Pa"])
                        delta = (q[n,:4].astype(np.longdouble)-q[0,:4]).mean(axis=(1,2))
                        drift = delta*(LENGTH*HEIGHT)
                        np.testing.assert_allclose(drift, snap["inventory_drift"], rtol=1e-15)
                        self.assertTrue(np.all(np.abs(drift) <= snap["roundoff_bound"]))
                    if run["shifted"]:
                        ref = fields[f"{nx}x{ny}_{run['steps']}_0_{run['tol_Pa']:g}"]
                        shift_error = np.roll(q[:,4:], -(nx//4), axis=-1)-ref[:,4:]
                        np.testing.assert_array_equal(np.max(abs(shift_error), axis=(1,2,3)),
                                                      results["aligned_max_Pa"][key])
