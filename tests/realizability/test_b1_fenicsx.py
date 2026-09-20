"""B1 tests that run only inside the optional DOLFINx environment."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


HAS_DOLFINX = importlib.util.find_spec("dolfinx") is not None


@unittest.skipUnless(HAS_DOLFINX, "optional B1 DOLFINx environment is not active")
class FenicsxB1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from realizability import load_config

        cls.config = load_config(Path("configs/realizability/pilot.json"))

    def test_independent_steady_fixtures(self) -> None:
        from realizability.backends.b1_verification import _harmonic_sign_fixture, _steady_affine

        zero = _steady_affine(2, 0.0, 0.0)
        self.assertLess(zero["velocity_l2"], 1.0e-13)
        self.assertLess(zero["pressure_l2"], 1.0e-13)

        affine = _steady_affine(3, 0.07, -0.11)
        self.assertLess(affine["velocity_l2_error"], 1.0e-11)
        self.assertLess(affine["pressure_gauge_l2_error"], 1.0e-11)
        self.assertLess(affine["divergence_l2"], 1.0e-11)
        self.assertAlmostEqual(
            affine["shifted_pressure_mean"] - affine["pressure_mean"], -3.25, places=11
        )
        self.assertLess(max(_harmonic_sign_fixture().values()), 1.0e-11)

    def test_actual_trace_flux_and_boundary_values(self) -> None:
        from realizability.backends.fenicsx_stokes import harmonic_pilot

        for mode in ("N_02c", "T_00c"):
            result = harmonic_pilot(self.config, mode, 0.01, 0.07)
            self.assertLess(result.real.flux_ratio, 1.0e-8)
            self.assertLess(result.real.boundary_residual, 1.0e-14)
            self.assertLess(result.imaginary.boundary_residual, 1.0e-14)
            self.assertLess(abs(result.flux_correction_coefficient), 1.0e-2)
            self.assertLess(result.real.algebraic_residual, 1.0e-9)

    def test_manufactured_convergence_and_decay(self) -> None:
        from realizability.backends.b1_verification import _mms_transient, _zero_input_decay

        spatial = [
            _mms_transient(n, 0.002, 0.004, self.config.fluid.kinematic_viscosity)
            for n in (2, 3, 4)
        ]
        errors = [row["velocity_l2_error"] for row in spatial]
        self.assertGreater(errors[0], errors[1])
        self.assertGreater(errors[1], errors[2])

        energies = _zero_input_decay(3, 0.02, 4, self.config.fluid.kinematic_viscosity)
        for before, after in zip(energies, energies[1:]):
            self.assertLessEqual(after, before * (1.0 + 1.0e-12))

    def test_pilot_divergence_failure_is_reported(self) -> None:
        """The deliberately coarse pilot must not be mislabeled accepted."""

        from realizability.backends.fenicsx_stokes import harmonic_pilot

        result = harmonic_pilot(self.config, "N_02c", 0.01, 0.07)
        self.assertGreater(
            max(result.real.divergence_ratio, result.imaginary.divergence_ratio), 1.0e-3
        )

    def test_boundary_only_transient_driver(self) -> None:
        from realizability.backends.fenicsx_stokes import transient_pulse

        result = transient_pulse(self.config, "T_00c", 0.1, (0.0, 1.0, 0.0), 0.07)
        self.assertEqual(result.forcing_status, "none (boundary Dirichlet actuation only)")
        self.assertEqual(result.steps[0].velocity_l2, 0.0)
        self.assertGreater(result.steps[1].velocity_l2, 0.0)
        self.assertLess(result.steps[2].velocity_l2, result.steps[1].velocity_l2)
        self.assertLess(abs(result.steps[1].net_flux), 1.0e-20)


if __name__ == "__main__":
    unittest.main()
