"""Source-only expression-depth probe; fake operands, no UFL/FEM import.

Executes selected installed traversal AST with injected scalar graph objects.
This demonstrates a depth mechanism, not an actual compiler reproduction.
"""
import ast
from collections import Counter
from fractions import Fraction
from functools import singledispatchmethod, wraps
import hashlib
import json
from math import ceil, log2
from pathlib import Path
import sys
from typing import overload

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LIB = Path('/tmp/navier-fenicsx-r229/lib/python3.12/site-packages/ufl')
sys.path.insert(0, str(ROOT))
FORBIDDEN = {'numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py', 'scipy'}


class Guard:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in FORBIDDEN:
            raise AssertionError('numerical import prohibited: '+fullname)


class Expr:
    # Identity hashes deliberately avoid emulating UFL hashing/equality.
    def __init__(self, *operands, value=None):
        self.ufl_operands = tuple(cast(x) for x in operands)
        self.value = value

    def __add__(self, other):
        return self if isinstance(other, (int, float)) and other == 0 else Sum(self, other)

    __radd__ = __add__

    def __mul__(self, other):
        if isinstance(other, (int, float)) and other in (0, 1):
            return 0 if other == 0 else self
        return Product(self, other)

    __rmul__ = __mul__

    def __pow__(self, exponent):
        if exponent == 0:
            return 1
        return self if exponent == 1 else Power(self, exponent)


class Sum(Expr):
    pass


class Product(Expr):
    pass


class Power(Expr):
    pass


def cast(value):
    return value if isinstance(value, Expr) else Expr(value=value)


def balanced(poly, coords):
    # Prospective evidence-only reducer: same terms, adjacent pairs, odd carry.
    terms = []
    for powers, coefficient in poly.terms.items():
        term = float(coefficient)
        for coord, exponent in zip(coords, powers):
            if exponent:
                term *= coord**exponent
        terms.append(term)
    if not terms:
        return 0
    while len(terms) > 1:
        terms = [terms[i]+terms[i+1] if i+1 < len(terms) else terms[i]
                 for i in range(0, len(terms), 2)]
    return terms[0]


def depth(node):
    # Iterative, so the measurement does not impose the traversal's limit.
    stack, maximum = [(cast(node), 0)], 0
    while stack:
        item, level = stack.pop()
        maximum = max(maximum, level)
        stack.extend((child, level+1) for child in item.ufl_operands)
    return maximum


def summands(node):
    stack, result = [cast(node)], []
    while stack:
        item = stack.pop()
        if isinstance(item, Sum):
            stack.extend(reversed(item.ufl_operands))
        else:
            result.append(item)
    return result


def fingerprint(node):
    # Only bounded individual monomials enter here, never long sum trees.
    return (type(node).__name__, node.value,
            tuple(fingerprint(x) for x in node.ufl_operands))


def signature(node):
    # At fixed time, adjacent pure constants may fold before a symbolic sum.
    # Compare their exact binary-float values as rationals and retain every
    # nonconstant monomial/factor, including multiplicity.
    terms, constant = [], Fraction(0)
    for item in summands(node):
        if not item.ufl_operands and isinstance(item.value, (int, float)):
            constant += Fraction(item.value)
        else:
            terms.append(fingerprint(item))
    return Counter(terms), constant


def load_walker():
    dag_path, derivative_path = LIB/'corealg/dag_traverser.py', LIB/'algorithms/apply_derivatives.py'
    dag_tree = ast.parse(dag_path.read_text())
    derivative_tree = ast.parse(derivative_path.read_text())
    namespace = dict(Expr=Expr, BaseForm=Expr, Sum=Sum,
                     singledispatchmethod=singledispatchmethod, wraps=wraps, overload=overload)
    dag = next(x for x in dag_tree.body if isinstance(x, ast.ClassDef) and x.name == 'DAGTraverser')
    exec(compile(ast.Module(body=[dag], type_ignores=[]), str(dag_path), 'exec'), namespace)
    for name in ('GenericDerivativeRuleset', 'GateauxDerivativeRuleset'):
        cls = next(x for x in derivative_tree.body if isinstance(x, ast.ClassDef) and x.name == name)
        kept = []
        for method in cls.body:
            if not isinstance(method, ast.FunctionDef):
                continue
            decorators = [ast.unparse(x) for x in method.decorator_list]
            if (method.name == 'process'
                    or name == 'GenericDerivativeRuleset' and
                    (method.name == '__init__' or 'process.register(Sum)' in decorators)):
                kept.append(method)
        cls.body = kept
        exec(compile(ast.Module(body=[cls], type_ignores=[]), str(derivative_path), 'exec'), namespace)
    generic, gateaux = namespace['GenericDerivativeRuleset'], namespace['GateauxDerivativeRuleset']
    # Fake leaf/product/power handling only: all coordinate/load terms are
    # independent of the mixed unknown. Traverse operands, then return zero.
    def independent(self, node, *children):
        return 0
    generic.process.register(Expr)(namespace['DAGTraverser'].postorder(independent))
    return gateaux, {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in (dag_path, derivative_path, LIB/'algebra.py')}


def traverse(walker, graph):
    try:
        answer = walker(())(cast(graph))
    except RecursionError:
        return 'RecursionError'
    assert answer == 0
    return 'zero derivative'


def run():
    guard = Guard()
    sys.meta_path.insert(0, guard)
    limit = sys.getrecursionlimit()
    try:
        from verification.nonlinear_port import fixtures
        from verification.nonlinear_port.polynomial import Poly
        walker, hashes = load_walker()
        coords = [Expr(value=name) for name in ('x', 'y', 'z')] + [.125]
        cases = []
        for fixture in ('manufactured', 'poiseuille', 'rotation', 'affine_time'):
            u, p = getattr(fixtures, fixture)()
            groups = {'u': u, 'p': [p], 'force': fixtures.forcing(u, p)}
            for group, polys in groups.items():
                for index, poly in enumerate(polys):
                    old, candidate = poly.evaluate(coords), balanced(poly, coords)
                    # Zero and pure-constant cases retain their value; all
                    # nonconstant terms retain multiplicity and factor ordering.
                    assert signature(old) == signature(candidate), (fixture, group, index)
                    before, after = traverse(walker, old), traverse(walker, candidate)
                    assert after == 'zero derivative'
                    monomial_depth = max(map(depth, summands(candidate)))
                    assert depth(candidate) <= monomial_depth+ceil(log2(max(1, len(poly.terms))))
                    cases.append(dict(fixture=fixture, group=group, component=index,
                                      terms=len(poly.terms), old_depth=depth(old),
                                      balanced_depth=depth(candidate), old_walk=before,
                                      balanced_walk=after, identical_summands=True))
        force = [c for c in cases if c['fixture'] == 'manufactured' and c['group'] == 'force']
        assert [c['terms'] for c in force] == [221, 222, 11]
        assert [c['old_walk'] for c in force[:2]] == ['RecursionError']*2
        # Empty, singleton, odd-length and cancellation-preserving checks.
        assert balanced(Poly(), coords) == 0
        for count in (1, 3, 5, 17):
            poly = Poly({(i, 0, 0, 0): Fraction((-1)**i, i+1) for i in range(count)})
            assert Counter(map(fingerprint, summands(poly.evaluate(coords)))) == Counter(
                map(fingerprint, summands(balanced(poly, coords))))
        omitted = dict(poly.terms)
        omitted.pop(next(reversed(omitted)))
        flipped = dict(poly.terms)
        first = next(iter(flipped))
        flipped[first] = -flipped[first]
        assert signature(balanced(poly, coords)) != signature(balanced(Poly(omitted), coords))
        assert signature(balanced(poly, coords)) != signature(balanced(Poly(flipped), coords))
        loaded = sorted(n for n in sys.modules if n.split('.')[0] in FORBIDDEN)
        assert not loaded and sys.getrecursionlimit() == limit
        return dict(status='PASS', cases=cases, case_count=len(cases),
                    focused_edge_cases=5, recursion_limit=limit, recursion_limit_changed=False,
                    negative_controls=['original left-fold force 0 recurses',
                                       'original left-fold force 1 recurses',
                                       'omitted odd tail changes signature',
                                       'flipped coefficient changes signature'],
                    installed_source_sha256=hashes, numerical_modules_loaded=loaded,
                    actual_compiler_reproduction=False,
                    conclusion='Long polynomial sums are a sufficient fake traversal failure mechanism; balanced summation removes it.',
                    limitation='Fake scalar operands and identity hashing; no UFL graph, compiler, FEM, residual or solve ran. Actual failing expression remains unobserved.')
    finally:
        sys.meta_path.remove(guard)


if __name__ == '__main__':
    result = run()
    (HERE/'probe.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
