"""Periodic Cartesian staggered finite volumes for near-ambient viscous water.

Arrays use (y,x). r and H live at centers, mx and my on their positive faces.
Each momentum component has its own half-cell-shifted dual control volume.
"""
from typing import NamedTuple

import numpy as np

from .liquid_imex import P0


def next_cell(a, axis):
    return np.roll(a, -1, axis=axis)


def prev_cell(a, axis):
    return np.roll(a, 1, axis=axis)


def forward_mean(a, axis):
    return 0.5 * (a + next_cell(a, axis))


def back_mean(a, axis):
    return 0.5 * (a + prev_cell(a, axis))


def gradient(a, axis, spacing):
    return (next_cell(a, axis) - a) / spacing


def divergence(fx, fy, dx, dy):
    return (fx - prev_cell(fx, -1)) / dx + (fy - prev_cell(fy, -2)) / dy


def kinetic(water, U):
    r, mx, my, _ = U
    u = mx / (water.rho + forward_mean(r, -1))
    v = my / (water.rho + forward_mean(r, -2))
    ke = 0.5 * (back_mean(mx*u, -1) + back_mean(my*v, -2))
    return u, v, ke


def primitive(water, U):
    u, v, ke = kinetic(water, U)
    de = (U[3] - ke) / (water.rho + U[0])
    # Batch identical thermodynamic inputs only. No averaging or symmetry
    # constraint is applied to the fields, fluxes, FFT or pressure unknowns.
    pairs = np.stack((U[0].ravel(), de.ravel()))
    unique, indices = np.unique(pairs, axis=1, return_inverse=True)
    p, t = water.thermo(*unique)
    return u, v, ke, de, p[indices].reshape(de.shape), t[indices].reshape(de.shape)


class SlowFlux(NamedTuple):
    xx: np.ndarray
    xy: np.ndarray  # x momentum across a y face
    yx: np.ndarray
    yy: np.ndarray
    work_x: np.ndarray
    work_y: np.ndarray
    enthalpy_x: np.ndarray
    enthalpy_y: np.ndarray
    pressure: np.ndarray
    viscous_power: float
    pressure_dilatation: float


def slow(water, U, dx, dy):
    r, mx, my, _ = U
    u, v, ke, de, p, t = primitive(water, U)
    ux = (u - prev_cell(u, -1)) / dx
    vy = (v - prev_cell(v, -2)) / dy
    dil = (ux + vy) / 3
    xx, yy = 2*water.mu*(ux-dil), 2*water.mu*(vy-dil)
    shear_rate = gradient(u, -2, dy) + gradient(v, -1, dx)
    xy = water.mu * shear_rate  # at upper-right corners
    # Dual mass flux = conservative interpolation of primal mass flux.
    # Normal entries below are indexed at the positive face of the dual cell.
    axx = forward_mean(mx, -1)*forward_mean(u, -1) - next_cell(xx, -1)
    ayy = forward_mean(my, -2)*forward_mean(v, -2) - next_cell(yy, -2)
    axy = forward_mean(my, -1)*forward_mean(u, -2) - xy
    ayx = forward_mean(mx, -2)*forward_mean(v, -1) - xy
    h = de + (P0+p)/(water.rho+r)
    specific_ke = ke / (water.rho+r)
    wx = (mx*forward_mean(specific_ke, -1) - forward_mean(xx, -1)*u
          - back_mean(xy*forward_mean(v, -1), -2) - water.k*gradient(t, -1, dx))
    wy = (my*forward_mean(specific_ke, -2) - forward_mean(yy, -2)*v
          - back_mean(xy*forward_mean(u, -2), -1) - water.k*gradient(t, -2, dy))
    # Integral of discrete tau:grad(u), evaluated at the stress locations.
    power = np.mean(xx*ux + yy*vy + xy*shear_rate)
    return SlowFlux(axx, axy, ayx, ayy, wx, wy, forward_mean(h, -1),
                    forward_mean(h, -2), p, power, np.mean(p*(ux+vy)))


def fluxes(s, pressure, mx, my):
    return (np.array([mx, s.xx+next_cell(pressure, -1), s.yx, s.work_x+s.enthalpy_x*mx]),
            np.array([my, s.xy, s.yy+next_cell(pressure, -2), s.work_y+s.enthalpy_y*my]))


def step(water, U, dt, dx, dy, tol=2e-11):
    """Return conservative update, endpoint pressure, oriented fluxes and budgets."""
    old = slow(water, U, dx, dy)
    p = old.pressure
    pred = U - (dt/2)*divergence(*fluxes(old, p, U[1], U[2]), dx, dy)
    mid = slow(water, pred, dx, dy)
    adv_x = divergence(mid.xx, mid.xy, dx, dy)
    adv_y = divergence(mid.yx, mid.yy, dx, dy)
    ny, nx = p.shape
    kx = np.sin(np.pi*np.fft.rfftfreq(nx))/dx
    ky = np.sin(np.pi*np.fft.fftfreq(ny))/dy
    symbol = 1 + (water.c*dt)**2 * (kx**2 + ky[:, None]**2)
    trial = p.copy()
    for iteration in range(9):
        pm = (p + trial)/2
        mass_x = U[1] - (dt/2)*(adv_x + gradient(pm, -1, dx))
        mass_y = U[2] - (dt/2)*(adv_y + gradient(pm, -2, dy))
        fx, fy = fluxes(mid, pm, mass_x, mass_y)
        V = U - dt * divergence(fx, fy, dx, dy)
        residual = primitive(water, V)[4] - trial
        error = np.max(np.abs(residual))
        if error <= tol:
            return V, trial, (fx, fy), (float(error), iteration, mid.viscous_power, mid.pressure_dilatation)
        trial += np.fft.irfft2(np.fft.rfft2(residual)/symbol, s=p.shape, axes=(-2, -1))
    raise ArithmeticError(f"endpoint EOS residual {error:g} Pa after 9 evaluations")
