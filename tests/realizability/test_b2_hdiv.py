"""Optional DOLFINx checks for the B2 pre-campaign discretization."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np


HAS_DOLFINX = importlib.util.find_spec("dolfinx") is not None


@unittest.skipUnless(HAS_DOLFINX, "optional B1/B2 DOLFINx environment is not active")
class HdivB2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from realizability import load_config

        cls.config = load_config(Path("configs/realizability/pilot.json"))

    def test_affine_reaction_fixture(self) -> None:
        from realizability.backends.hdiv_stokes import affine_reaction_verification

        metrics = affine_reaction_verification(resolution=3)
        for value in metrics.values():
            self.assertLess(value, 1.0e-9)

    def test_pilots_are_strongly_divergence_free(self) -> None:
        from realizability.backends.hdiv_stokes import harmonic_response

        for mode in ("N_02c", "T_00c"):
            result = harmonic_response(self.config, mode, 0.01, 0.07)
            self.assertLess(result.real.divergence_ratio, 1.0e-3)
            self.assertLess(result.imaginary.divergence_ratio, 1.0e-3)
            self.assertLess(result.corrected_flux_ratio, 1.0e-8)
            self.assertLess(result.real.algebraic_residual, 1.0e-9)
        tangential = harmonic_response(self.config, "T_00c", 0.01, 0.07)
        self.assertEqual(tangential.flux_correction_coefficient, 0.0)

    def test_feature_extraction_is_finite(self) -> None:
        import numpy as np

        from realizability.backends.fem_observables import extract_complex_linear_features
        from realizability.backends.hdiv_stokes import harmonic_response

        _, fields = harmonic_response(
            self.config, "N_02c", 0.01, 0.07, _return_fields=True
        )
        features = extract_complex_linear_features(fields)
        self.assertEqual(features.shape, (6,))
        self.assertTrue(np.isfinite(features).all())

    def test_small_mesh_sip_stability_audit(self) -> None:
        from realizability.backends.hdiv_stokes import sip_stability_diagnostics

        for penalty in (6.0, 12.0, 24.0, 48.0):
            metrics = sip_stability_diagnostics(resolution=2, penalty_factor=penalty)
            self.assertLess(metrics["symmetry_relative_error"], 1.0e-12)
            self.assertGreater(metrics["free_velocity_dofs"], 0)
            self.assertGreater(metrics["discrete_divergence_free_dofs"], 0)
            self.assertTrue(np.isfinite(metrics["minimum_free_velocity_eigenvalue"]))
            self.assertTrue(np.isfinite(metrics["minimum_divergence_free_eigenvalue"]))
            if penalty == 6.0:
                self.assertLess(metrics["minimum_divergence_free_eigenvalue"], 0.0)
            else:
                self.assertGreater(metrics["minimum_divergence_free_eigenvalue"], 0.0)


if __name__ == "__main__":
    unittest.main()
