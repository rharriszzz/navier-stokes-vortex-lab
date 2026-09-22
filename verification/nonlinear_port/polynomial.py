"""Small exact rational polynomial oracle in (x, y, z, t); no FEM dependencies."""
from fractions import Fraction as F


class Poly:
    def __init__(self, value=0):
        terms = value if isinstance(value, dict) else {(0, 0, 0, 0): F(value)}
        self.terms = {k: F(v) for k, v in terms.items() if v}

    @staticmethod
    def cast(value):
        return value if isinstance(value, Poly) else Poly(value)

    def __add__(self, other):
        terms = self.terms.copy()
        for k, v in self.cast(other).terms.items():
            terms[k] = terms.get(k, 0) + v
        return Poly(terms)

    __radd__ = __add__

    def __neg__(self):
        return Poly({k: -v for k, v in self.terms.items()})

    def __sub__(self, other):
        return self + -self.cast(other)

    def __rsub__(self, other):
        return self.cast(other) + -self

    def __mul__(self, other):
        terms = {}
        for a, av in self.terms.items():
            for b, bv in self.cast(other).terms.items():
                k = tuple(i + j for i, j in zip(a, b))
                terms[k] = terms.get(k, 0) + av * bv
        return Poly(terms)

    __rmul__ = __mul__

    def __pow__(self, n):
        if not isinstance(n, int) or n < 0:
            raise ValueError('nonnegative integer power required')
        result = Poly(1)
        for _ in range(n):
            result = result * self
        return result

    def d(self, axis):
        terms = {}
        for k, v in self.terms.items():
            if k[axis]:
                out = list(k)
                out[axis] -= 1
                terms[tuple(out)] = v * k[axis]
        return Poly(terms)

    def at(self, axis, value):
        terms = {}
        for k, v in self.terms.items():
            out = list(k)
            out[axis] = 0
            key = tuple(out)
            terms[key] = terms.get(key, 0) + v * F(value)**k[axis]
        return Poly(terms)

    def integral(self, axis):
        """Definite integral from 0 to 1, leaving other variables symbolic."""
        terms = {}
        for k, v in self.terms.items():
            out = list(k)
            out[axis] = 0
            key = tuple(out)
            terms[key] = terms.get(key, 0) + v / (k[axis] + 1)
        return Poly(terms)

    def evaluate(self, coordinates):
        # Also accepts UFL expressions: coefficients are exact until conversion.
        result = 0
        for k, v in self.terms.items():
            term = float(v)
            for coord, exponent in zip(coordinates, k):
                if exponent:
                    term *= coord**exponent
            result += term
        return result

    def __eq__(self, other):
        return self.terms == self.cast(other).terms


def variable(axis):
    key = [0] * 4
    key[axis] = 1
    return Poly({tuple(key): 1})


x, y, z, t = (variable(i) for i in range(4))


def volume(p):
    return Poly.cast(p).integral(0).integral(1).integral(2)


def face(p, axis, side):
    p = Poly.cast(p).at(axis, side)
    for j in range(3):
        if j != axis:
            p = p.integral(j)
    return p


def dot(a, b):
    return sum(i*j for i, j in zip(a, b))
