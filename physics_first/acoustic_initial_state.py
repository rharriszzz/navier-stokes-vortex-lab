"""SI reference properties and isentropic initial states for a periodic water wave."""

import CoolProp.CoolProp as CP

P0 = 101325.0  # Pa absolute
T0 = 293.15  # K
AMPLITUDE = 10.0  # Pa
LENGTH = 0.10  # m


def background():
    state = CP.AbstractState("HEOS", "Water")
    state.update(CP.PT_INPUTS, P0, T0)
    return dict(pressure_pa=P0, temperature_K=T0, rho_kg_m3=state.rhomass(),
                sound_speed_m_s=state.speed_sound(), entropy_J_kg_K=state.smass(),
                internal_energy_J_kg=state.umass(), mu_Pa_s=state.viscosity(),
                conductivity_W_m_K=state.conductivity())


def isentropic_conserved(state, base, dp):
    """Return density, axial momentum density and total-energy density."""
    state.update(CP.PSmass_INPUTS, P0 + dp, base["entropy_J_kg_K"])
    # Refine the entropy target at fixed pressure using (ds/dT)_p = cp/T.
    temperature = state.T() - (state.smass() - base["entropy_J_kg_K"]) * state.T() / state.cpmass()
    state.update(CP.PT_INPUTS, P0 + dp, temperature)
    if state.phase() != CP.iphase_liquid:
        raise ValueError("expected liquid state")
    rho = state.rhomass()
    u = dp / (base["rho_kg_m3"] * base["sound_speed_m_s"])
    return rho, rho * u, rho * (state.umass() + u * u / 2)
