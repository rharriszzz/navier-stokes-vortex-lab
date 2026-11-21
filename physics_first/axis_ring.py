"""Meridional no-swirl ring solver, SI units. The streamfunction is r² times phi."""
from math import factorial

import numpy as np
from scipy import sparse
from scipy.integrate import simpson
from scipy.interpolate import RectBivariateSpline
from scipy.sparse.linalg import splu
from scipy.special import eval_gegenbauer, i1e

from .ring_strain import CORE, RADIUS

GAMMA = 0.0036
NU = 1.003395e-6
RHO = 998.2


def half_grid(uniform_end, length, h):
    """Uniform core, then a C² sinh extension with endpoint exactly at length."""
    scale = 0.004
    span = scale * np.arcsinh((length - uniform_end) / scale)
    outer = np.linspace(0, span, round(span / h) + 1)[1:]
    return np.r_[np.linspace(0, uniform_end, round(uniform_end / h) + 1),
                 uniform_end + scale * np.sinh(outer / scale)]


def derivative(x, order, even=False):
    """Polynomial-exact five-node weights; fold negative radial nodes for even data."""
    n = len(x)
    op = sparse.lil_matrix((n, n))
    for i in range(n):
        start = np.clip(i - 2, -2 if even else 0, n - 5)
        ids = np.arange(start, start + 5)
        distance = np.where(ids < 0, -x[abs(ids)], x[abs(ids)]) - x[i]
        scale = max(abs(distance))
        target = np.eye(5)[order] * factorial(order) / scale**order
        weights = np.linalg.solve(np.vander(distance / scale, 5, increasing=True).T, target)
        for j, weight in zip(abs(ids), weights):
            op[i, j] += weight
    return op.tocsr()


def release(r, z, width=CORE):
    """Analytic angular integral of the archived Gaussian-convolved line tangent."""
    q = 2 * r * RADIUS / width**2
    scale = 2 * GAMMA * RADIUS / (np.sqrt(np.pi) * width**3)
    factor = np.divide(i1e(q), r, out=np.full_like(r, RADIUS / width**2), where=r > 0)
    return scale * factor * np.exp(-((r - RADIUS)**2 + z**2) / width**2)


def rk3(state, dt, rhs):
    """Third-order SSP Runge–Kutta, also used on jointly carried material markers."""
    def stage(a, b, weight):
        return tuple((1 - weight)*x + weight*(y + dt*k)
                     for x, y, k in zip(a, b, rhs(*b), strict=True))
    first = stage(state, state, 1)
    second = stage(state, first, 0.25)
    return stage(state, second, 2/3)


class Grid:
    def __init__(self, per_core, length=0.08):
        self.h = CORE / per_core
        self.r = half_grid(0.022, length, self.h)
        positive = half_grid(0.008, length, self.h)
        self.z = np.r_[-positive[:0:-1], positive]
        self.R, self.Z = self.r[:, None], self.z[None, :]
        self.shape = (len(self.r), len(self.z))
        self.dr = derivative(self.r, 1, even=True)
        self.dz = derivative(self.z, 1)
        rr = derivative(self.r, 2, even=True)
        self.zz = derivative(self.z, 2)
        inv_r = np.divide(1., self.r, out=np.zeros_like(self.r), where=self.r > 0)
        self.radial = sparse.diags(np.r_[4., np.ones(len(self.r)-1)]) @ rr
        self.radial += sparse.diags(3 * inv_r) @ self.dr
        op = sparse.kronsum(self.zz, self.radial, format='csr')
        boundary = np.zeros(self.shape, bool)
        boundary[-1, :] = boundary[:, 0] = boundary[:, -1] = True
        self.edge = boundary.ravel()
        self.inside = ~self.edge
        self.lu = splu(op[self.inside][:, self.inside].tocsc(), permc_spec='MMD_AT_PLUS_A')
        self.rim = op[self.inside][:, self.edge]
        wr, wz = (simpson(np.eye(len(x)), x=x) for x in (self.r, self.z))
        self.weights = np.outer(wr, wz)
        # 5D Newton kernel, averaged over the four-dimensional radial directions.
        radius = np.hypot(self.R, self.Z) / length
        cosine = np.divide(self.Z, radius * length, out=np.zeros(self.shape), where=radius > 0)
        self.moments, self.exterior = [], []
        for n in range(7):
            cn = eval_gegenbauer(n, 1.5, cosine)
            self.moments.append((cn * radius**n * self.weights * self.R**3 /
                                 (4 * eval_gegenbauer(n, 1.5, 1))).ravel())
            self.exterior.append((cn.ravel()[self.edge] / radius.ravel()[self.edge]**(3+n)
                                  / length**3))
        self.moments = np.array(self.moments)
        self.exterior = np.array(self.exterior)

    def invert(self, eta, boundary=None):
        phi = np.empty(self.shape)
        flat = phi.ravel()
        flat[self.edge] = ((self.moments @ eta.ravel()) @ self.exterior
                           if boundary is None else boundary.ravel()[self.edge])
        flat[self.inside] = self.lu.solve(-eta.ravel()[self.inside] - self.rim @ flat[self.edge])
        return phi

    def axial(self, field):
        return (self.dz @ field.T).T

    def velocity(self, phi):
        # Use a common discrete curl for both mass flux components.
        psi = self.R**2 * phi
        ur = -self.R * self.axial(phi)
        uz = self.dr @ psi
        uz[1:] /= self.R[1:]
        uz[0] = 2 * phi[0]
        return ur, uz

    def diffusion(self, eta):
        return self.radial @ eta + (self.zz @ eta.T).T

    def tendency(self, eta, ur, uz, nu):
        rhs = nu * self.diffusion(eta) - ur * (self.dr @ eta) - uz * self.axial(eta)
        rhs.ravel()[self.edge] = 0
        return rhs

    def interpolate(self, field, degree=3):
        return RectBivariateSpline(self.r, self.z, field, kx=degree, ky=degree).ev

    def step(self, eta, markers, dt, nu=NU):
        def rhs(current, points):
            ur, uz = self.velocity(self.invert(current))
            # All markers lie in the uniform core patch. Local cubic Lagrange
            # interpolation avoids fitting a domain-wide spline at each stage.
            velocity = np.stack([self.probe(v, points) for v in (ur, uz)], axis=-1)
            return self.tendency(current, ur, uz, nu), velocity
        return rk3((eta, markers), dt, rhs)

    def probe(self, field, points):
        indices, weights = [], []
        for dim, nodes in enumerate((self.r, self.z)):
            q = points[:, dim]
            idx = (np.searchsorted(nodes, q) - 2).clip(0, len(nodes)-4)[:, None] + np.arange(4)
            x = nodes[idx]
            basis = np.ones_like(x)
            for j in range(4):
                for k in range(4):
                    if k != j:
                        basis[:, j] *= (q - x[:, k]) / (x[:, j] - x[:, k])
            indices.append(idx)
            weights.append(basis)
        block = field[indices[0][:, :, None], indices[1][:, None, :]]
        return np.einsum('nij,ni,nj->n', block, *weights)
