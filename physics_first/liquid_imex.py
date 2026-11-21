"""Periodic 1D pressure-based midpoint finite volumes. Quantities are SI.

U = (rho-rho0, rho*u, rho*(e-e0+u**2/2)); one right face per cell.
See docs/physics-first/LIQUID_IMEX.md for the split and EOS quadrature.
"""
import numpy as np
import CoolProp.CoolProp as CP

from .acoustic_initial_state import P0, T0, LENGTH


class Liquid:
    """Reference-relative HEOS water, for small excursions about ambient water."""

    def __init__(self):
        self.state = CP.AbstractState("HEOS", "Water")
        self.state.update(CP.PT_INPUTS, P0, T0)
        s = self.state
        self.rho, self.e, self.s = s.rhomass(), s.umass(), s.smass()
        self.c, self.mu, self.k = s.speed_sound(), s.viscosity(), s.conductivity()
        self.cv = s.cvmass()
        self.er = s.first_partial_deriv(CP.iUmass, CP.iDmass, CP.iT)

    def thermo(self, dr, de):
        """Integrate dp and dT along a straight segment in (rho,e).

        Evaluate physical Helmholtz derivatives near the segment midpoint.
        The tangent estimate for T_mid changes the integral at cubic order.
        No absolute-energy/pressure subtraction enters either result.
        """
        mid_temp = T0 + (de - self.er * dr) / (2 * self.cv)
        mid_rho = self.rho + 0.5 * dr
        dp, dtemp = np.empty_like(dr), np.empty_like(dr)
        s = self.state
        for i in range(len(dr)):
            s.update(CP.DmassT_INPUTS, mid_rho[i], mid_temp[i])
            er = s.first_partial_deriv(CP.iUmass, CP.iDmass, CP.iT)
            dtemp[i] = (de[i] - er * dr[i]) / s.cvmass()
            dp[i] = (s.first_partial_deriv(CP.iP, CP.iDmass, CP.iT) * dr[i]
                     + s.first_partial_deriv(CP.iP, CP.iT, CP.iDmass) * dtemp[i])
        return dp, dtemp

    def primitive(self, U):
        dr, m, energy = U
        rho = self.rho + dr
        u = m / rho
        de = energy / rho - 0.5 * u**2
        p, temp = self.thermo(dr, de)
        return u, de, p, temp

    def initialize(self, cells, amplitude, direction):
        """Isentropic midpoint quadrature in pressure, sampled at FV centers."""
        x = (np.arange(cells) + 0.5) / cells
        p = amplitude * np.sin(2 * np.pi * x)
        dr, de = np.empty_like(p), np.empty_like(p)
        s = self.state
        for i, delta in enumerate(p):
            pm = P0 + delta / 2
            s.update(CP.PSmass_INPUTS, pm, self.s)
            dr[i] = delta / s.speed_sound()**2
            de[i] = dr[i] * pm / s.rhomass()**2
        rho = self.rho + dr
        u = direction * p / (self.rho * self.c)
        return np.array([dr, rho*u, rho*(de + 0.5*u**2)])


def face(v):
    return 0.5 * (v + np.roll(v, -1))


def diff(f):
    """Undivided right-minus-left flux."""
    return f - np.roll(f, 1)


def slow_flux(water, U, dx):
    """Non-pressure momentum flux, non-enthalpy energy flux, shifted h."""
    u, de, p, temp = water.primitive(U)
    rho = water.rho + U[0]
    stress = (4 * water.mu / (3 * dx)) * (np.roll(u, -1) - u)
    heat = (-water.k / dx) * (np.roll(temp, -1) - temp)
    adv = face(U[1] * u) - stress
    work = face(0.5 * U[1] * u**2) - stress * face(u) + heat
    return adv, work, face(de + (P0 + p) / rho), p


def step(water, U, dt, dx, tol=2e-11):
    """Return updated conserved averages, endpoint p', fluxes and Pa residuals."""
    lam = dt / dx
    adv, work, h, p = slow_flux(water, U, dx)
    mass = face(U[1])
    old_flux = (mass, adv + face(p), work + h * mass)
    pred = U - 0.5 * lam * np.array([diff(f) for f in old_flux])
    adv, work, h, _ = slow_flux(water, pred, dx)
    # Chord Jacobian at rest. D is the centered divergence of a face mean.
    freq = 2 * np.pi * np.fft.rfftfreq(len(p))
    symbol = 1 + (0.5 * lam * water.c * np.sin(freq))**2
    trial = p.copy()
    max_linear = 0.
    for iteration in range(9):
        force = adv + face(0.5 * (p + trial))
        m_new = U[1] - lam * diff(force)
        mass = face(0.5 * (U[1] + m_new))
        energy = work + h * mass
        updated = np.array([U[0] - lam * diff(mass), m_new,
                            U[2] - lam * diff(energy)])
        residual = water.primitive(updated)[2] - trial
        err = np.max(np.abs(residual))
        if err <= tol:
            return updated, trial, np.array([mass, force, energy]), (err, max_linear, iteration)
        correction = np.fft.irfft(np.fft.rfft(residual) / symbol, n=len(p))
        d2 = diff(face(diff(face(correction))))
        linear = correction - (0.5 * lam * water.c)**2 * d2 - residual
        max_linear = max(max_linear, np.max(np.abs(linear)))
        trial += correction
    raise ArithmeticError(f"pressure iteration failed with {err:g} Pa residual")
