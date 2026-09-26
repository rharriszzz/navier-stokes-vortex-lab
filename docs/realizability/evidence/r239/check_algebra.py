"""Bounded exact toy evidence; no FEM assembly, numerical imports or backend solve.

Run from any directory with project Python; JSON goes to stdout. All matrices
have at most nine rows. This is not a reproduction of PETSc's actual ordering.
"""
from fractions import Fraction as F
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from verification.nonlinear_port.test_algebra import rank, toy_matrix
from verification.nonlinear_port.sparse import (
    CSR, border_and_lift, constraint_condition, row_scales, scale_system,
)


def eliminate(rows, pivoting):
    """Exact Gaussian elimination with optional largest-column row pivot."""
    assert 1 <= len(rows) <= 9
    a = [[F(v) for v in row] for row in rows]
    swaps, pivots = [], []
    for j in range(len(a)):
        p = max(range(j, len(a)), key=lambda i: abs(a[i][j])) if pivoting else j
        if p != j:
            swaps.append([j, p])
            a[j], a[p] = a[p], a[j]
        pivot = a[j][j]
        pivots.append(str(pivot))
        if not pivot:
            return dict(completed=False, zero_pivot_index=j, pivots=pivots,
                        row_swaps=swaps, determinant=None)
        for i in range(j + 1, len(a)):
            factor = a[i][j] / pivot
            a[i] = [x - factor*y for x, y in zip(a[i], a[j])]
    determinant = F((-1)**len(swaps))
    for pivot in pivots:
        determinant *= F(pivot)
    return dict(completed=True, zero_pivot_index=None, pivots=pivots,
                row_swaps=swaps, determinant=str(determinant))


def describe(a):
    return dict(size=len(a), exact_rank=rank(a),
                natural=eliminate(a, False), row_pivoted=eliminate(a, True))


def main():
    ungauged, gauged = toy_matrix(False), toy_matrix()
    null = [0, 0, 0, 1, 0, 1, 1]
    assert all(sum(x*y for x, y in zip(row, null)) == 0 for row in ungauged)
    result = dict(ungauged=describe(ungauged), gauged=describe(gauged))
    assert result['ungauged']['exact_rank'] == 6
    assert result['gauged']['exact_rank'] == 8
    assert result['gauged']['natural']['zero_pivot_index'] == 6
    assert result['gauged']['row_pivoted']['determinant'] == '-1'
    assert result['gauged']['row_pivoted']['row_swaps'] == [[5, 7]]

    # Deliberately remove zero-mean pressure coupling: Gram alone misses this.
    singular = [row[:] for row in gauged]
    singular[2][4] = singular[4][2] = 0
    constraints = [[float(v) for v in row[:5]] for row in gauged[5:]]
    gram = constraint_condition(constraints, {})
    assert gram['condition_bound'] == 1.0
    assert rank(singular) == 7
    assert not eliminate(singular, True)['completed']
    result['singular_control'] = dict(**describe(singular), constraint_check=gram)

    # Real CSR/border/lift/scaling functions on a toy only. Add an independent
    # fixed coordinate in front, then border the five-unknown toy core.
    core_rows = [{0: 3.0}] + [
        {j+1: float(gauged[i][j]) for j in range(5)} for i in range(5)]
    columns = [[0.] + [float(gauged[i][k]) for i in range(5)] for k in range(5, 8)]
    rows = [[0.] + [float(v) for v in gauged[k][:5]] for k in range(5, 8)]
    residual, matrix = border_and_lift(
        CSR.from_rows(core_rows), columns, rows, [9.] + [0.]*5,
        [0.]*3, [2.] + [0.]*8, {0: 2.})
    assert residual == [0.]*9
    dense = [[row.get(j, 0.) for j in range(9)] for row in matrix.rows()]
    assert [row[1:] for row in dense[1:]] == gauged
    assert dense[0] == [1.] + [0.]*8
    scales = row_scales(matrix)
    _, scaled = scale_system(residual, matrix, scales)
    scaled_dense = [[row.get(j, 0.) for j in range(9)] for row in scaled.rows()]
    assert rank(dense) == rank(scaled_dense) == 9
    assert eliminate(dense, False)['zero_pivot_index'] == 7
    assert eliminate(scaled_dense, True)['completed']
    assert all(i in row for i, row in enumerate(scaled.rows()))
    result['border_lift_scale'] = dict(
        unscaled=describe(dense), scaled=describe(scaled_dense),
        positive_row_scales=list(scales), every_diagonal_stored=True,
        note='Exact fractions of stored binary floats; toy only, at most 9 rows.')
    forbidden = {'numpy', 'sympy', 'dolfinx', 'ufl', 'ffcx', 'basix', 'petsc4py', 'mpi4py'}
    loaded = sorted(forbidden & {name.split('.')[0] for name in sys.modules})
    assert not loaded
    result.update(request='R239', python=sys.version, executable=sys.executable,
                  numerical_modules_loaded=loaded, fem_attempts=0,
                  interpretation='Toy counterexamples only; actual FEM rank and ordering unknown.')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
