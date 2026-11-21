"""Regression checks for a transverse shear state and its measured decay."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


@unittest.skipUnless(importlib.util.find_spec("CoolProp"), "requires the water EOS")
class WaterShearTest(unittest.TestCase):
    def test_mesh_state_and_conservative_energy(self):
        import CoolProp.CoolProp as cp
        import numpy as np
        from physics_first.measure_shear import thermodynamics
        from physics_first.su2_acoustic import FIELDS, read_restart
        from physics_first.su2_shear import AMPLITUDE, background, make_case

        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "strip"
            make_case(directory, 32, 2048)
            cfg = (directory / "wave.cfg").read_text()
            self.assertIn("bottom, top,", cfg)
            self.assertNotIn("MARKER_SYM=", cfg)
            self.assertIn("OUTPUT_WRT_FREQ= 512\n", cfg)
            r = read_restart(directory / "state_00000.dat")
        q = np.column_stack([r[name] for name in FIELDS[2:]])
        grid = q.reshape(5, 33, 4)
        np.testing.assert_array_equal(grid[0], grid[-1])
        np.testing.assert_array_equal(grid[:, 0], grid[:, -1])
        np.testing.assert_array_equal(q[:, 1], 0)
        energy_span = 0.5 * background()["rho_kg_m3"] * AMPLITUDE**2
        self.assertAlmostEqual(np.ptp(q[:, 3]), energy_span, delta=2e-8)
        dp, dT = thermodynamics(q, background(), cp.AbstractState("HEOS", "Water"))
        self.assertLess(abs(dp).max(), 0.0003)
        self.assertLess(abs(dT).max(), 1e-9)

    def test_full_snapshot_analysis_against_manufactured_decay(self):
        import numpy as np
        from physics_first.measure_shear import K, measure
        from physics_first.su2_acoustic import read_restart
        from physics_first.su2_shear import LENGTH, background, make_case
        from unittest.mock import patch

        base = background()
        nu = base["mu_Pa_s"] / base["rho_kg_m3"]
        end = 8 * LENGTH / base["sound_speed_m_s"]
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "strip"
            make_case(directory, 32, 2048)
            initial = read_restart(directory / "state_00000.dat")

            def snapshot(path):
                step = int(path.stem.split("_")[1])
                record = dict(initial)
                record["Momentum_y"] = initial["Momentum_y"] * np.exp(-nu * K**2 * end * step/2048)
                volume = LENGTH**2 / (8 * 4 * 32)
                record["Residual_Density"] = np.zeros_like(initial["x"])
                record["Residual_Momentum_y"] = nu * K**2 * volume * record["Momentum_y"]
                record["Pressure"] = np.full_like(initial["x"], base["pressure_pa"])
                record["Temperature"] = np.full_like(initial["x"], base["temperature_K"])
                return record

            with patch("physics_first.measure_shear.read_restart", side_effect=snapshot):
                result = measure(directory, 32, 2048, base)
        for value in (result["nu_fit_m2_s"], result["kinetic_energy_fit_m2_s"], *result["interval_nu_m2_s"]):
            self.assertAlmostEqual(value / nu, 1, places=12)
        self.assertAlmostEqual(result["snapshots"][-1]["residual_modal_nu_m2_s"] / nu, 1, places=12)
        self.assertAlmostEqual(result["snapshots"][0]["amplitude_m_s"], 0.01, places=15)
        self.assertLess(result["snapshots"][-1]["transverse_off_mode_rms_m_s"], 1e-16)

    def test_translation_preflight_and_wrong_phase(self):
        from physics_first.shear_translation import NX, STEPS, SHIFT, audit_inputs, corner_stencil
        from physics_first.su2_shear import make_case

        with tempfile.TemporaryDirectory() as tmp:
            ref, dest = Path(tmp) / "base", Path(tmp) / "shifted"
            make_case(ref, NX, STEPS)
            make_case(dest, NX, STEPS, shift_cells=SHIFT)
            check = audit_inputs(ref, dest)
            self.assertEqual(check["unique_nodes"], 256)
            self.assertEqual(check["initial_p_spread_Pa"], 0)
            self.assertTrue(check["initial_inverse_shift_bit_identical"])
            corner = corner_stencil(ref)
            self.assertLess(abs(corner["four_neighbor_torus"]), 1e-12)
            self.assertGreater(corner["left_corner_local"], 0.97)
            with self.assertRaises(AssertionError):
                audit_inputs(ref, ref)

    def test_alignment_on_unique_periodic_vertices(self):
        import numpy as np
        from physics_first.shear_translation import NX, NY, SHIFT, discrepancy, unique_grid

        field = np.arange(NX * NY).reshape(NY, NX, 1)
        shifted = np.roll(field, SHIFT, axis=1)
        with_seams = np.pad(shifted[:, :, 0], ((0, 1), (0, 1)), mode="wrap")
        recovered = unique_grid({"example": with_seams}, ["example"])
        self.assertEqual(discrepancy(field, recovered)["max_abs"], [0.0])
        recovered = recovered.copy()
        recovered[1, 0, 0] += 8
        self.assertEqual(discrepancy(field, recovered)["rms"], [0.5])
