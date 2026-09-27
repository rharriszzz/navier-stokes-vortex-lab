"""Source-only depth, algebra and routing checks for symbolic polynomials."""
import ast
from fractions import Fraction
import hashlib
import inspect
from math import ceil, isclose, log2
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from docs.realizability.evidence.r263 import probe
from . import fixtures
from . import cube_adapter
from .polynomial import Poly


LEGACY_EVALUATE_AST_SHA256 = '3d20e2f9136dd2d06190edccadc28bad6add843ec2fb533c73f2e857832d07c4'


def exact(poly, values):
    total = Fraction(0)
    for powers, coefficient in poly.terms.items():
        monomial = coefficient
        for coordinate, exponent in zip(values, powers):
            monomial *= coordinate**exponent
        total += monomial
    return total


def symbolic_value(value, points):
    node = probe.cast(value)
    if not node.ufl_operands:
        if isinstance(node.value, str):
            return points[node.value]
        return Fraction(node.value)
    values = [symbolic_value(child, points) for child in node.ufl_operands]
    if isinstance(node, probe.Sum):
        return values[0] + values[1]
    if isinstance(node, probe.Product):
        return values[0] * values[1]
    if isinstance(node, probe.Power):
        return values[0] ** values[1]
    raise AssertionError(type(node))


class Vector(tuple):
    def __add__(self, other):
        return Vector(a+b for a, b in zip(self, other))

    def __sub__(self, other):
        return Vector(a+(-1)*b for a, b in zip(self, other))

    def __truediv__(self, other):
        return Vector(a*(1/other) for a in self)


class SymbolicU:
    def SpatialCoordinate(self, domain):
        return [probe.Expr(value=name) for name in ('x', 'y', 'z')]

    def as_vector(self, items):
        return Vector(items)

    def Measure(self, name, **kwargs):
        return name, kwargs

    def TestFunction(self, space):
        return object()

    def TrialFunction(self, space):
        return object()

    def FacetNormal(self, domain):
        return object()

    def replace(self, row, mapping):
        return row


class BalancedPolynomialChecks(unittest.TestCase):
    def test_production_depth_and_monomials_for_every_fixture(self):
        walker, _ = probe.load_walker()
        coords = [probe.Expr(value=name) for name in ('x', 'y', 'z')] + [.125]
        cases = 0
        for name in ('manufactured', 'poiseuille', 'rotation', 'affine_time'):
            u, p = getattr(fixtures, name)()
            for group in (u, [p], fixtures.forcing(u, p)):
                for poly in group:
                    original, balanced = poly.evaluate(coords), poly.evaluate_balanced(coords)
                    self.assertEqual(probe.signature(original), probe.signature(balanced))
                    self.assertLessEqual(probe.depth(balanced),
                        max(map(probe.depth, probe.summands(balanced)))
                        + ceil(log2(max(1, len(poly.terms)))))
                    self.assertEqual(probe.traverse(walker, balanced), 'zero derivative')
                    cases += 1
        self.assertEqual(cases, 28)
        u, p = fixtures.manufactured()
        force = fixtures.forcing(u, p)
        for component, expected_terms in ((0, 221), (1, 222)):
            self.assertEqual(len(force[component].terms), expected_terms)
            self.assertEqual(probe.traverse(walker, force[component].evaluate(coords)),
                             'RecursionError')
            self.assertEqual(probe.depth(force[component].evaluate_balanced(coords)), 12)

    def test_algebra_rational_samples_and_sensitive_controls(self):
        coords = [probe.Expr(value=name) for name in ('x', 'y', 'z')] + [.125]
        samples = {'x': Fraction(1, 4), 'y': Fraction(1, 2), 'z': Fraction(3, 4)}
        values = [*samples.values(), Fraction(1, 8)]
        for fixture in ('manufactured', 'poiseuille', 'rotation', 'affine_time'):
            u, p = getattr(fixtures, fixture)()
            for poly in [*u, p, *fixtures.forcing(u, p)]:
                observed = symbolic_value(poly.evaluate_balanced(coords), samples)
                self.assertTrue(isclose(float(observed), float(exact(poly, values)),
                                        rel_tol=1e-12, abs_tol=1e-12))
        poly = Poly({(i, 0, 0, 0): Fraction((-1)**i, i+1) for i in range(17)})
        signature = probe.signature(poly.evaluate_balanced(coords))
        omitted = dict(poly.terms)
        omitted.pop(next(reversed(omitted)))
        flipped = dict(poly.terms)
        first = next(iter(flipped))
        flipped[first] = -flipped[first]
        self.assertNotEqual(signature, probe.signature(Poly(omitted).evaluate_balanced(coords)))
        self.assertNotEqual(signature, probe.signature(Poly(flipped).evaluate_balanced(coords)))
        self.assertEqual(Poly().evaluate_balanced(coords), 0)
        self.assertEqual(Poly(7).evaluate_balanced(coords), 7.0)
        self.assertEqual(Poly({(1, 0, 0, 0): 1, (0, 1, 0, 0): -1}).evaluate_balanced(coords).__class__,
                         probe.Sum)

    def test_legacy_numeric_evaluation_source_and_interpolation(self):
        method = next(node for node in ast.parse(inspect.getsource(Poly)).body[0].body
                      if isinstance(node, ast.FunctionDef) and node.name == 'evaluate')
        current = hashlib.sha256(ast.dump(method, include_attributes=False).encode()).hexdigest()
        self.assertEqual(current, LEGACY_EVALUATE_AST_SHA256)

        class Array(list):
            def __setitem__(self, key, value):
                if isinstance(key, list):
                    for index, item in zip(key, value):
                        list.__setitem__(self, index, item)
                else:
                    list.__setitem__(self, key, value)

        class Space:
            def __init__(self, size=4):
                self.size = size

            def sub(self, component):
                class Sub:
                    def collapse(inner):
                        return Space(3 if component == 0 else 1), (
                            [0, 1, 2] if component == 0 else [3])
                return Sub()

        class Function:
            def __init__(self, space):
                self.x = SimpleNamespace(array=Array([0.]*space.size),
                                         scatter_forward=lambda: None)

            def interpolate(self, callback):
                class Coords:
                    shape = (3, 1)
                    def __iter__(self):
                        return iter((.25, .5, .75))
                values = callback(Coords())
                self.x.array[:] = [value[0] if isinstance(value, list) else value
                                   for value in values]

        np = SimpleNamespace(broadcast_to=lambda value, size: [value]*size,
                             asarray=lambda value: value)
        fem = SimpleNamespace(Function=Function)
        legacy = Poly.evaluate
        called = []
        def count(self, coordinates):
            called.append(self)
            return legacy(self, coordinates)
        with patch.object(Poly, 'evaluate', count), patch.object(
                Poly, 'evaluate_balanced', side_effect=AssertionError('symbolic route in interpolation')):
            state = cube_adapter.interpolate_state(np, fem, Space(), 'manufactured', .125)
        self.assertEqual(len(called), 4)
        u, p = fixtures.manufactured()
        expected = [float(exact(v, [Fraction(1, 4), Fraction(1, 2), Fraction(3, 4),
                                    Fraction(1, 8)])) for v in [*u, p]]
        for actual, wanted in zip(state.x.array, expected):
            self.assertAlmostEqual(actual, wanted, places=12)

    def test_exact_data_and_both_degree_step_routes(self):
        symbolic = SymbolicU()
        balanced = Poly.evaluate_balanced
        calls = []
        def required(self, coordinates):
            calls.append(self)
            return balanced(self, coordinates)
        with (patch.object(Poly, 'evaluate', side_effect=AssertionError('legacy symbolic call')),
              patch.object(Poly, 'evaluate_balanced', required)):
            for fixture in ('manufactured', 'poiseuille', 'rotation', 'affine_time'):
                for time in (0., .125, 1.):
                    data = cube_adapter.exact_data(symbolic, object(), fixture, time)
                    self.assertEqual(len(data['u']), 3)
                    self.assertEqual(len(data['force']), 3)
                    self.assertEqual(len(data['targets']), 2)
                    self.assertEqual(len(data['offsets']), 2)
            captured = []
            def build(*args, **kwargs):
                captured.append((args, kwargs))
                return dict(flux_rows=[], gauge_row=0)
            fem = SimpleNamespace(Constant=lambda domain, value: value)
            with patch.object(cube_adapter, 'build_forms', build):
                for degree in (24, 26):
                    forms, constants, context = cube_adapter.step_forms(
                        symbolic, fem, object(), object(), object(), object(), object(),
                        object(), .125, .125, 1, 'manufactured', degree=degree)
                    self.assertEqual(len(constants), 3)
                    self.assertEqual(forms['scalar_rows'], [0])
                    self.assertIs(context['history'][0], context['history'][1])
                    self.assertEqual(context['dx'][1]['metadata']['quadrature_degree'], degree)
                    self.assertGreater(len(calls), 0)
                    u, _ = fixtures.manufactured()
                    current, old = [v.at(3, Fraction(1, 8)) for v in u], [v.at(3, 0) for v in u]
                    force = fixtures.forcing(u, fixtures.manufactured()[1])
                    sample = {'x': Fraction(1, 4), 'y': Fraction(1, 2), 'z': Fraction(3, 4)}
                    points = [*sample.values(), Fraction(1, 8)]
                    for i in range(3):
                        target = (exact(force[i], points)
                                  + 8*(exact(current[i], points)-exact(old[i], points))
                                  - exact(u[i].d(3).at(3, Fraction(1, 8)), points))
                        actual = symbolic_value(context['force'][i], sample)
                        self.assertTrue(isclose(float(actual), float(target),
                                                 rel_tol=1e-12, abs_tol=1e-12))
                        old_actual = symbolic_value(context['history'][0][i], sample)
                        self.assertTrue(isclose(float(old_actual), float(exact(old[i], points)),
                                                 rel_tol=1e-12, abs_tol=1e-12))
        self.assertGreater(len(calls), 250)


if __name__ == '__main__':
    unittest.main()
