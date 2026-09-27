"""R265 scalar arithmetic and symbolic-time review; no numerical libraries.

Point samples describe Python binary64 arithmetic, not generated UFL/C code,
assembled errors or a guaranteed margin against diagnostic acceptance gates.
"""
from fractions import Fraction as F
from itertools import product
import json
from math import ceil, log2
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from docs.realizability.evidence.r263 import probe


def exact(poly, points):
    return sum((coefficient * product_value(points, powers)
                for powers, coefficient in poly.terms.items()), F(0))


def product_value(points, powers):
    value = F(1)
    for point, power in zip(points, powers):
        value *= point**power
    return value


def expected_tree(terms):
    # Independent recursive oracle: split at the largest power of two < n.
    if not terms:
        return 0
    if len(terms) == 1:
        return terms[0]
    split = 1 << ((len(terms)-1).bit_length()-1)
    return expected_tree(terms[:split]) + expected_tree(terms[split:])


def run():
    guard = probe.Guard()
    sys.meta_path.insert(0, guard)
    limit = sys.getrecursionlimit()
    try:
        from verification.nonlinear_port import fixtures, cube_adapter
        from verification.nonlinear_port.polynomial import Poly
        from verification.nonlinear_port.test_balanced_polynomial import SymbolicU, symbolic_value
        coords = [probe.Expr(value=name) for name in ('x', 'y', 'z', 't')]
        for count in range(34):
            poly = Poly({(i, 0, 0, 0): F((-1)**i, i+1) for i in range(count)})
            terms = [float(v) * coords[0]**k[0] if k[0] else float(v)
                     for k, v in poly.terms.items()]
            actual = poly.evaluate_balanced(coords)
            assert probe.fingerprint(probe.cast(actual)) == probe.fingerprint(probe.cast(expected_tree(terms)))
        cancellation = Poly({(i, 0, 0, 0): (-1)**i for i in range(32)})
        assert cancellation.evaluate_balanced([1., 0., 0., 0.]) == 0.
        cases, symbolic_cases = [], 0
        points = list(product((0., .5, 1.), repeat=3)) + [
            (.1, .2, .3), (1/3, 2/3, 1/7), (.01, .99, .51),
            (.999, .001, .123), (.25, .5, .75)]
        samples = [(*point, time) for point in points for time in (0., .125)]
        for fixture in ('manufactured', 'poiseuille', 'rotation', 'affine_time'):
            u, p = getattr(fixtures, fixture)()
            polys = [*u, p, *fixtures.forcing(u, p)]
            for index, poly in enumerate(polys):
                old, new = poly.evaluate(coords), poly.evaluate_balanced(coords)
                assert probe.signature(old) == probe.signature(new)
                bound = max(map(probe.depth, probe.summands(new))) + ceil(log2(max(1, len(poly.terms))))
                assert probe.depth(new) <= bound
                symbolic_cases += 1
                maxima = dict(old_error=0., balanced_error=0., reassociation_delta=0.,
                              balanced_addition_error=0., balanced_addition_bound=0.)
                for point in samples:
                    rational = [F(v) for v in point]
                    reference = exact(poly, rational)
                    before, after = poly.evaluate(point), poly.evaluate_balanced(point)
                    terms = []
                    for powers, coefficient in poly.terms.items():
                        term = float(coefficient)
                        for coordinate, exponent in zip(point, powers):
                            if exponent:
                                term *= coordinate**exponent
                        terms.append(F(term))
                    # With normal arithmetic and no under/overflow, each term
                    # crosses at most h rounded additions. This bound covers
                    # addition only, using exact rational sums of float terms.
                    h = ceil(log2(max(1, len(terms))))
                    unit = F(1, 2**53)
                    bound = h*unit/(1-h*unit)*sum(map(abs, terms), F(0))
                    error = abs(F(after)-sum(terms, F(0)))
                    assert error <= bound
                    observations = dict(old_error=float(abs(F(before)-reference)),
                        balanced_error=float(abs(F(after)-reference)),
                        reassociation_delta=abs(after-before),
                        balanced_addition_error=float(error), balanced_addition_bound=float(bound))
                    for key, value in observations.items():
                        maxima[key] = max(maxima[key], value)
                cases.append(dict(fixture=fixture, component=index, terms=len(poly.terms), **maxima))
            # Time remains a symbolic operand here, exercising Constant-like
            # graph construction omitted by the fixed-time R264 fake test.
            data = cube_adapter.exact_data(SymbolicU(), object(), fixture, coords[3])
            for time in (F(0), F(1, 8)):
                values = dict(x=F(1, 4), y=F(1, 2), z=F(3, 4), t=time)
                for graph, poly in zip([*data['u'], data['p'], *data['force']], polys):
                    rounded = Poly({k: F(float(v)) for k, v in poly.terms.items()})
                    assert symbolic_value(graph, values) == exact(rounded, list(values.values()))
        assert sys.getrecursionlimit() == limit
        loaded = sorted(n for n in sys.modules if n.split('.')[0] in probe.FORBIDDEN)
        assert not loaded
        return dict(status='PASS', deterministic_tree_sizes=34,
                    cancellation_control=True, all_symbolic_fixture_cases=symbolic_cases,
                    symbolic_time_exact_data_values=56, samples_per_polynomial=len(samples),
                    scalar_evaluations=len(cases)*len(samples), cases=cases,
                    maximum_reassociation_delta=max(c['reassociation_delta'] for c in cases),
                    maximum_balanced_error=max(c['balanced_error'] for c in cases),
                    maximum_old_error=max(c['old_error'] for c in cases),
                    numerical_modules_loaded=loaded, recursion_limit_changed=False,
                    real_compiler_or_assembled_error_claim=False)
    finally:
        sys.meta_path.remove(guard)


if __name__ == '__main__':
    result = run()
    (HERE/'reassociation.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'cases'}, sort_keys=True))
