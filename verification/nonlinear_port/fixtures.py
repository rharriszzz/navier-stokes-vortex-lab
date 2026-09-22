"""Dimensionless exact verification data. Never physical tank actuation."""
from fractions import Fraction as F
from .polynomial import Poly, x, y, z, t, dot

RHO = F(1)
MU = F(1, 10)


def manufactured():
    a = 1 + t + t**3
    c = F(1, 2) + t
    e = 1 + t**2 + t**3
    psi = e * x**2 * (1-x)**2 * y**2 * (1-y)**2
    u = [-a*x + psi.d(1), -a*y - psi.d(0), 2*a*z-c]
    p = (1+t) * (x*x+y*y+z*z-1)
    return u, p


def stress(u, p, rho=RHO, mu=MU):
    return [[mu*(u[i].d(j)+u[j].d(i)) - (p if i == j else 0)
             for j in range(3)] for i in range(3)]


def forcing(u, p, rho=RHO, mu=MU):
    """Conservative momentum load rho*(u_t+div(u tensor u))-div(sigma)."""
    sigma = stress(u, p, rho, mu)
    return [rho*(u[i].d(3)+sum((u[i]*u[j]).d(j) for j in range(3)))
            - sum(sigma[i][j].d(j) for j in range(3)) for i in range(3)]


def return_data(side):
    if side not in (0, 1):
        raise ValueError('return side must be 0 or 1')
    u, p = manufactured()
    a, c = 1+t+t**3, F(1, 2)+t
    normal = [0, 0, 2*side-1]
    pressure = (1+t)*(side-F(1, 3))-4*MU*a
    sigma = stress(u, p)
    offset = [dot(row, normal).at(2, side)+pressure*normal[i]
              for i, row in enumerate(sigma)]
    flux = c if side == 0 else 2*a-c
    return flux, pressure, offset


def poiseuille():
    # Plane channel, exact moving trace on z faces. x=1 needs shear traction.
    return [4*y*(1-y), Poly(), Poly()], 8*MU*(F(1, 2)-x)


def rotation():
    # Unit angular speed about (1/2,1/2), with centrifugal pressure.
    return [F(1, 2)-y, x-F(1, 2), Poly()], (
        RHO*F(1, 2)*((x-F(1, 2))**2+(y-F(1, 2))**2-F(1, 6)))


def affine_time():
    """Exactly P2/P1-representable spatial companion; nonzero BDF2 time error."""
    a, c = 1+t+t**3, F(1, 2)+t
    return [-a*x, -a*y, 2*a*z-c], (1+t)*(x+y+z-F(3, 2))
