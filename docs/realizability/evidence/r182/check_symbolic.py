"""Exact identities for benchmark Section 7.8; requires optional SymPy.

Run with the temporary R183 environment or another Python with SymPy installed.
No reference sampling, quadrature, PDE solve, or floating-point evaluation.
Prints JSON to stdout; does not modify repository files.
"""

import json
import platform

import sympy as s


checks = []


def zero(name, expression):
    assert s.simplify(expression) == 0, name
    checks.append(name)


r, z, t = s.symbols("r z t", real=True)
nu, c = s.symbols("nu c", positive=True)
B = s.Function("B")(t)
f, g = s.Function("f")(r), s.Function("g")(z)
a = (4 * nu - s.diff(B, t)) / (2 * B)
E = s.exp(-r**2 / B)
h = 1 - E
hr = s.diff(h, r)
fp, gp = s.diff(f, r), s.diff(g, z)
L = c * f * g * h
Ur = -a * r * f * (g + z * gp)
Uz = a * z * (2 * f + r * fp) * g

zero("meridional incompressibility", s.diff(r * Ur, r) / r + s.diff(Uz, z))
zero("raw swirl time derivative", s.diff(h, t) + r**2 * E * s.diff(B, t) / B**2)
zero("raw swirl radial diffusion", s.diff(h, r, 2) - hr / r + 4 * r**2 * E / B**2)
zero("unwindowed swirl balance", s.diff(h, t) - a * r * hr - nu * (s.diff(h, r, 2) - hr / r))

# Independently differentiate the target in the mean angular-momentum equation.
D = s.diff(L, t) + Ur * s.diff(L, r) + Uz * s.diff(L, z) - nu * (
    s.diff(L, r, 2) - s.diff(L, r) / r + s.diff(L, z, 2)
)
compact = c * (
    a * r * f * g * (1 - f * (g + z * gp)) * hr
    + a * f * g * (2 * z * f * gp - r * fp * g) * h
    - nu * (2 * fp * g * hr + g * (s.diff(f, r, 2) - fp / r) * h + f * s.diff(g, z, 2) * h)
)
zero("all-cutoff deficit formula", D - compact)
zero("central plateau deficit", D.subs({f: 1, g: 1}).doit())
radial = c * (a * r * f * (1 - f) * hr - a * r * f * fp * h - nu * (2 * fp * hr + (s.diff(f, r, 2) - fp / r) * h))
axial = c * (a * r * g * (1 - g - z * gp) * hr + 2 * a * z * g * gp * h - nu * s.diff(g, z, 2) * h)
zero("radial transition formula", D.subs(g, 1).doit() - radial)
zero("axial transition formula", D.subs(f, 1).doit() - axial)

v = s.symbols("v", real=True)
W = 1 - 10 * v**3 + 15 * v**4 - 6 * v**5
zero("cutoff derivative factorization", s.diff(W, v) + 30 * v**2 * (1 - v)**2)
for endpoint, value in [(0, 1), (1, 0)]:
    zero(f"cutoff value at {endpoint}", W.subs(v, endpoint) - value)
    for order in [1, 2]:
        zero(f"cutoff derivative {order} at {endpoint}", s.diff(W, v, order).subs(v, endpoint))
zero("exact cutoff integral", s.integrate(W, (v, 0, 1)) - s.Rational(1, 2))

# Whole-support cancellation uses these total derivatives and zero face terms.
zero("axial advection integration by parts", g**2 + 2 * z * g * gp - s.diff(z * g**2, z))
zero("radial advection integration by parts", r**2 * f * (fp * h + f * hr) + r * f * (2 * f + r * fp) * h - s.diff(r**2 * f**2 * h, r))
F = f * h
zero("radial viscous integral is face torque", r * (s.diff(F, r, 2) - s.diff(F, r) / r) - s.diff(r * s.diff(F, r) - 2 * F, r))
zero("angular momentum storage integrand", s.diff(r * f * h, t) + s.diff(B, t) / B**2 * r**3 * f * E)

# Sign follows after the documented assumptions: Gamma,G,I3,rho,B,-Bdot > 0.
rho, Gamma, G, I3, beta, Bpositive = s.symbols("rho Gamma G I3 beta Bpositive", positive=True)
assert (rho * Gamma * G * beta * I3 / Bpositive**2).is_positive
checks.append("positive required torque under stated assumptions")

print(json.dumps({
    "status": "passed",
    "python": platform.python_version(),
    "sympy": s.__version__,
    "checks": checks,
    "reference_numerical_evaluation": False,
    "scope": "symbolic identities only; no stress realizability or boundary reachability claim",
}, indent=2))
