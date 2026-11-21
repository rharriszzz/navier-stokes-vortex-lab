"""Lightweight checks for the static real-water initial condition."""
import importlib.util
import unittest

import numpy as np


@unittest.skipUnless(all(importlib.util.find_spec(pkg) for pkg in ("CoolProp", "scipy")),
                     "water equilibrium requires CoolProp and SciPy")
class VortexEquilibriumTest(unittest.TestCase):
    def test_core_axis_and_quiescent_outer_ring(self):
        from physics_first.vortex_equilibrium import INITIAL, P0, initial_state

        state = initial_state(16)
        self.assertEqual(state.u[0], 0)
        self.assertAlmostEqual(state.u[16], INITIAL.peak_speed_m_s)
        np.testing.assert_array_equal(state.p[128:], P0)
        np.testing.assert_array_equal(state.conserved[:, [1, 3]], 0)
        np.testing.assert_array_equal(state.u[128:], 0)
        self.assertTrue(np.all(np.diff(state.p) >= 0))
        self.assertAlmostEqual(state.p[48] - state.p[0], 15.9053, delta=0.05)

    def test_recovery_uses_total_energy_and_all_momenta(self):
        from physics_first.acoustic_initial_state import P0, T0, background
        from physics_first.vortex_equilibrium import recover

        base = background()
        rho, e = base["rho_kg_m3"], base["internal_energy_J_kg"]
        v = np.array([0.3, 0.1, -0.2])
        q = np.array([[rho, *(rho * v), rho * (e + v @ v / 2)]])
        p, temperature = recover(q)
        self.assertAlmostEqual(p[0], P0, delta=0.01)
        self.assertAlmostEqual(temperature[0], T0, delta=1e-8)

    def test_radial_stencil_on_rigid_rotation_and_pressure_perturbation(self):
        from physics_first.vortex_equilibrium import Profile, radial_balance

        r = np.linspace(0, 0.040, 41)
        rho, omega, end = 1000.0, 10.0, 30
        u = omega * r
        q = np.zeros((len(r), 5))
        q[:, 0], q[:, 2] = rho, rho * u
        p = 101325 + 0.5 * rho * u**2
        s = Profile(r, p, u, np.zeros_like(r), q, p, np.full_like(r, 293.15))
        self.assertLess(radial_balance(s, end, p)["force_Pa_m"]["peak_abs"], 1e-7)
        # A +1000*r² Pa perturbation gives F=+2000*r and inward a=-2*r.
        bad = radial_balance(s, end, p + 1000 * r**2)
        self.assertAlmostEqual(bad["force_Pa_m"]["peak_abs"], 60, places=6)
        self.assertAlmostEqual(bad["acceleration_m_s2"]["signed_at_peak"], -0.06)
        self.assertAlmostEqual(bad["force_Pa_m"]["radius_m"], r[end])

    def test_integrals_use_independent_domains(self):
        from physics_first.vortex_equilibrium import INNER, integral_check

        # Flat pressure should expose the entire known physical head as a defect.
        result = integral_check(101325, 101325, INNER)
        self.assertEqual(result["dp_over_rho_m2_s2"], 0)
        self.assertAlmostEqual(result["defect_m2_s2"], -15.9020157 / 998, places=10)
