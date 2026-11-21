"""Optional tests for the SU2 acoustic case and its endpoint measurements."""

import importlib.util
import math
from pathlib import Path
import tempfile
import unittest


@unittest.skipUnless(importlib.util.find_spec("CoolProp"), "requires the water EOS")
class WaterAcousticsTest(unittest.TestCase):
    def test_sound_speed_against_isentropic_density_secant(self):
        import CoolProp.CoolProp as cp
        from physics_first.acoustic_initial_state import background, isentropic_conserved

        base = background()
        state = cp.AbstractState("HEOS", "Water")
        low = isentropic_conserved(state, base, -10)[0]
        high = isentropic_conserved(state, base, 10)[0]
        speed = math.sqrt(20 / (high - low))
        self.assertLess(abs(speed / base["sound_speed_m_s"] - 1), 1e-4)

    def test_periodic_restart_and_endpoint_units(self):
        import CoolProp.CoolProp as cp
        import numpy as np
        from physics_first.acoustic_initial_state import background
        from physics_first.measure_acoustic import wave
        from physics_first.su2_acoustic import make_case, read_restart, FIELDS

        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "case"
            make_case(directory, 32, 256)
            data = read_restart(directory / "state_00000.dat")
        nodes = np.column_stack([data[name] for name in FIELDS[2:]]).reshape(3, 33, 4)
        np.testing.assert_array_equal(nodes[:, 0], nodes[:, -1])
        np.testing.assert_array_equal(nodes[0], nodes[-1])
        base = background()
        angles = 2 * np.pi * (np.arange(32) + 0.5) / 32
        result = wave(nodes[0, :32], np.full(32, 0.1/32), angles, base, cp.AbstractState("HEOS", "Water"))
        self.assertAlmostEqual(result["amplitude_pa"], 10, delta=0.001)
        self.assertAlmostEqual(result["phase_rad"], -math.pi/2, places=4)
        expected = 0.1 * 100 / (2 * base["rho_kg_m3"] * base["sound_speed_m_s"]**2)
        self.assertLess(abs(result["wave_energy_J_per_m2"]/expected - 1), 1e-4)

    def test_100_pa_normalization(self):
        import CoolProp.CoolProp as cp
        import numpy as np
        from physics_first.acoustic_initial_state import LENGTH, background
        from physics_first.measure_acoustic import measure, wave
        from physics_first.su2_acoustic import FIELDS, make_case, read_restart

        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "control"
            make_case(directory, 32, 256, amplitude_pa=100)
            with self.assertRaisesRegex(ValueError, "amplitude does not match"):
                measure(directory, 32, 256)
            data = read_restart(directory / "state_00000.dat")
        base = background()
        nodes = np.column_stack([data[k][:32] for k in FIELDS[2:]])
        angles = 2 * np.pi * (np.arange(32) + 0.5) / 32
        result = wave(nodes, np.full(32, LENGTH/32), angles, base, cp.AbstractState("HEOS", "Water"))
        expected = LENGTH * 100**2 / (2 * base["rho_kg_m3"] * base["sound_speed_m_s"]**2)
        self.assertAlmostEqual(result["amplitude_pa"], 100, delta=0.001)
        self.assertLess(abs(result["wave_energy_J_per_m2"] / expected - 1), 1e-4)
