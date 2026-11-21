"""Independent flux, thermodynamics, dispersion and refinement checks for R293."""
import importlib.util
import json
import unittest
from pathlib import Path

import numpy as np


@unittest.skipUnless(importlib.util.find_spec("CoolProp"), "requires HEOS Water")
class LiquidIMEXTest(unittest.TestCase):
    def setUp(self):
        from physics_first.liquid_imex import Liquid
        self.w = Liquid()

    def test_uniform_translating_liquid(self):
        from physics_first.liquid_imex import step
        U = np.tile([[2e-5], [.03], [.001]], (1, 19))
        V, p, flux, res = step(self.w, U, 3e-6, .1/19)
        np.testing.assert_array_equal(U, V)
        self.assertTrue(np.all(p == p[0]))
        self.assertTrue(np.all(flux == flux[:, :1]))
        self.assertEqual(res, (0, 0, 0))

    def test_periodic_face_updates_and_reference_change(self):
        from physics_first.liquid_imex import step, P0
        # Off-isentrope, odd mesh, no velocity/pressure phase relation.
        n = 19
        angles = 2*np.pi*np.arange(n)/n
        U = np.array([3e-5*np.sin(angles), .02*np.cos(2*angles), .1*np.sin(3*angles)])
        dx, dt = .1/n, 2e-6
        w = self.w
        V, p, F, _ = step(w, U, dt, dx)
        def faces(Z, impulses, pressures):
            u, e, _, T = w.primitive(Z)
            rho = w.rho + Z[0]
            # Compute physical total-energy flux, including absolute enthalpy.
            out = []
            for i in range(n):
                j = (i+1) % n
                mass = (impulses[i]+impulses[j])/2
                tau = (4*w.mu/3)*(u[j]-u[i])/dx
                ke_flux = (Z[1,i]*u[i]**2 + Z[1,j]*u[j]**2)/4
                thermal = -w.k*(T[j]-T[i])/dx
                h = np.longdouble(w.e) + (e[i]+e[j]+(P0+pressures[i])/rho[i]
                                          +(P0+pressures[j])/rho[j])/2
                energy = h*mass + ke_flux - tau*(u[i]+u[j])/2 + thermal
                momentum = (Z[1,i]*u[i]+Z[1,j]*u[j])/2 - tau
                out.append([mass, momentum, energy])
            return np.array(out).T
        old_p = w.primitive(U)[2]
        old = faces(U, U[1], old_p)
        old[1] += (old_p + np.roll(old_p,-1))/2
        old[2] -= np.longdouble(w.e)*old[0]
        pred = U - np.asarray((dt/(2*dx))*(old-np.roll(old,1,axis=1)),float)
        full = faces(pred, (U[1]+V[1])/2, w.primitive(pred)[2])
        pmid = (old_p+p)/2
        full[1] += (pmid+np.roll(pmid,-1))/2
        shifted = full.copy()
        shifted[2] -= np.longdouble(w.e)*full[0]
        np.testing.assert_allclose(F, shifted, atol=3e-13, rtol=1e-14)
        for i in range(n):
            change = V[:,i].astype(np.longdouble)-U[:,i]
            full_change = change.copy()
            full_change[2] += np.longdouble(w.e)*change[0]
            np.testing.assert_allclose(full_change,-(dt/dx)*(full[:,i]-full[:,i-1]),atol=2e-15)
        np.testing.assert_allclose(np.sum(V.astype(np.longdouble)-U,axis=1),0,atol=5e-16)

    def test_one_step_spectrum_and_solve(self):
        from physics_first.liquid_imex import step, LENGTH
        from physics_first.liquid_imex_benchmark import flash
        n, steps = 35, 12
        w = self.w
        w.mu = w.k = 0.
        theta = 2*np.pi/n
        for direction in (1, -1):
            U = w.initialize(n,.01,direction)
            V, p, _, (nonlinear, linear, _) = step(w,U,LENGTH/(steps*w.c),LENGTH/n)
            raw, recovered, temp, sound = flash(w,V)
            # Exact amplification of the linearized centered FV/trapezoidal pair.
            x = direction*(n/steps)*np.sin(theta)/2
            predicted = (1-1j*x)/(1+1j*x)
            measured = np.fft.fft(recovered)[1]/np.fft.fft(w.primitive(U)[2])[1]
            self.assertLess(abs(measured-predicted),2e-9)
            self.assertLess(max(abs(recovered-p)),5e-11)
            self.assertLess(max(abs(raw-p)),.001)
            self.assertLess(max(abs(temp-293.15)),1e-8)
            self.assertLess(max(abs(sound-w.c)),1e-6)
            self.assertLess(nonlinear,2e-11)
            self.assertLess(linear,1e-12)

    def test_off_isentrope_derivatives(self):
        from physics_first.liquid_imex_benchmark import flash
        w = self.w
        dr = np.array([2e-5,0.,5e-11,0.])
        de = np.array([0.,.025,0.,-2e-7])
        U = np.array([dr,dr*0,(w.rho+dr)*de])
        _, _, p, t = w.primitive(U)
        raw, p_independent, temp, sound = flash(w,U)
        np.testing.assert_allclose(p,p_independent,atol=1e-9,rtol=1e-12)
        np.testing.assert_allclose(p,raw,rtol=0,atol=3e-4)
        np.testing.assert_allclose(t+293.15,temp,rtol=0,atol=2e-10)
        self.assertTrue(np.all(abs(sound-w.c)<.001))

    def test_decimal_helmholtz_inversion(self):
        from physics_first.liquid_helmholtz_check import samples
        result = samples()
        for row in result['samples']:
            self.assertLess(abs(row['difference_Pa']),row['amplitude_Pa']*2e-12)
        self.assertAlmostEqual(float(result['rho0']),self.w.rho,delta=1e-10)
        self.assertAlmostEqual(float(result['e0']),self.w.e,delta=3e-8)

    def test_refinement_from_saved_density_mode(self):
        # Independent of pressure, measurement routine, and archived gate flags.
        directory = Path(__file__).resolve().parents[1]/'docs/physics-first/r293'
        with np.load(directory/'fields.npz') as fields:
            for amp in (10,100):
                for sign in (-1,1):
                    def speed(n, m):
                        dr = fields[f'n{n}_m{m}_A{amp}_s{sign}_tol2e-11'][:,0]
                        phase = np.unwrap(np.angle(np.fft.fft(dr,axis=1)[:,1]))
                        return -(phase[-1]-phase[0])/(2*np.pi*sign)
                    for configs in ([(32,512),(64,512),(128,512)],
                                    [(128,128),(128,256),(128,512)]):
                        a,b,c = [speed(*cfg) for cfg in configs]
                        self.assertLess(abs(a-1),.01)
                        self.assertAlmostEqual((a-b)/(b-c),4,delta=.05)
        result = json.loads((directory/'results.json').read_text())
        self.assertTrue(all(result['checks'].values()))
