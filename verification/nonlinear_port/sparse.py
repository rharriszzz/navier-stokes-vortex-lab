"""Small serial CSR bridge. No dense FEM matrices or optional imports."""
from dataclasses import dataclass
from math import isfinite, fsum


@dataclass(frozen=True)
class CSR:
    n: int
    indptr: tuple
    indices: tuple
    values: tuple

    def validate(self, n):
        if (type(self.n) is not int or self.n != n or n < 1
                or len(self.indptr) != n+1 or self.indptr[0] != 0
                or self.indptr[-1] != len(self.values)
                or len(self.indices) != len(self.values)
                or any(type(i) is not int for i in self.indptr + self.indices)
                or any(a > b for a, b in zip(self.indptr, self.indptr[1:]))
                or any(i < 0 or i >= n for i in self.indices)
                or not all(isfinite(v) for v in self.values)):
            raise ValueError('invalid finite square CSR')
        for i in range(n):
            cols = self.indices[self.indptr[i]:self.indptr[i+1]]
            if any(a >= b for a, b in zip(cols, cols[1:])):
                raise ValueError('CSR columns must be sorted and unique')

    def matvec(self, vector):
        if len(vector) != self.n:
            raise ValueError('CSR vector size mismatch')
        return [fsum(self.values[k]*vector[self.indices[k]]
                     for k in range(self.indptr[i], self.indptr[i+1]))
                for i in range(self.n)]

    @classmethod
    def from_rows(cls, rows):
        """Store every diagonal slot, including zero pressure/scalar entries.

        PETSc's serial AIJ symbolic LU requires structural diagonals. Adding
        a zero slot leaves the operator unchanged; off-diagonal zeros may drop.
        """
        ptr, cols, vals = [0], [], []
        for i, row in enumerate(rows):
            row = dict(row)
            row.setdefault(i, 0.0)
            for j, v in sorted(row.items()):
                if v or j == i:
                    cols.append(int(j))
                    vals.append(float(v))
            ptr.append(len(cols))
        result = cls(len(rows), tuple(ptr), tuple(cols), tuple(vals))
        result.validate(len(rows))
        return result

    def rows(self):
        return [dict(zip(self.indices[self.indptr[i]:self.indptr[i+1]],
                         self.values[self.indptr[i]:self.indptr[i+1]]))
                for i in range(self.n)]


def border_and_lift(core, columns, rows, residual, scalar_residual, state, fixed):
    """Unknown order: mixed velocity/pressure, P-, P+, eta. Keep all rows.

    Current Dirichlet data are already in state and ALL assembled residuals.
    Consequently only the increment is zero; do not subtract the lift twice.
    """
    from .prototype import Refusal
    n = core.n
    core.validate(n)
    if (len(columns) != 3 or len(rows) != 3 or len(scalar_residual) != 3
            or any(len(v) != n for v in [*columns, *rows])
            or len(residual) != n or len(state) != n+3):
        raise Refusal('invalid bordered block dimensions')
    if any(type(i) is not int or not 0 <= i < n or state[i] != v
           for i, v in fixed.items()):
        raise Refusal('current lift must be installed before ALL assembly')
    matrix = core.rows()
    for i in range(n):
        matrix[i].update({n+k: columns[k][i] for k in range(3)})
    matrix.extend(dict(enumerate(row)) for row in rows)
    r = list(residual) + list(scalar_residual)
    matrix = [{j: value for j, value in row.items() if j not in fixed}
              for row in matrix]
    for i in fixed:
        matrix[i] = {i: 1.0}
        r[i] = 0.0
    if not all(isfinite(v) for v in r):
        raise Refusal('nonfinite residual')
    return r, CSR.from_rows(matrix)


def row_scales(matrix):
    """Freeze once per step; dimensionless unknown column scales are all one."""
    return tuple(1/max(1.0, fsum(abs(v) for v in row.values()))
                 for row in matrix.rows())


def scale_system(residual, matrix, scales):
    if len(scales) != matrix.n or not all(isfinite(s) and s > 0 for s in scales):
        raise ValueError('invalid fixed row scales')
    return ([s*r for s, r in zip(scales, residual)],
            CSR.from_rows([{j: scales[i]*v for j, v in row.items()}
                           for i, row in enumerate(matrix.rows())]))


def constraint_condition(rows, fixed):
    """Three-row Gram rank/condition bound; NOT the mixed operator inf-sup.

    For C with the fixed velocity columns removed, cond2(C) is bounded by
    sqrt(||CC^T||inf ||(CC^T)^-1||inf). Tiny pivots or bound > 1e6 refuse.
    """
    from .prototype import Refusal
    if len(rows) != 3 or not rows[0] or any(len(r) != len(rows[0]) for r in rows):
        raise Refusal('three equally sized scalar rows required')
    if not all(isfinite(v) for r in rows for v in r):
        raise Refusal('nonfinite constraint rows')
    if any(type(i) is not int or not 0 <= i < len(rows[0]) for i in fixed):
        raise Refusal('invalid fixed constraint column')
    gram = [[fsum(a*b for k, (a, b) in enumerate(zip(ri, rj)) if k not in fixed)
             for rj in rows] for ri in rows]
    return condition_from_gram(gram)


def condition_from_gram(gram):
    """Recompute the saved three-row condition bound without trusting its flag."""
    from math import sqrt
    from .prototype import Refusal
    if (len(gram) != 3 or any(len(row) != 3 for row in gram)
            or any(type(v) not in (float, int) or not isfinite(v) for row in gram for v in row)
            or any(gram[i][i] <= 0 for i in range(3))
            or any(gram[i][j] != gram[j][i] for i in range(3) for j in range(3))):
        raise Refusal('invalid constraint Gram matrix')
    norm = max(fsum(abs(v) for v in r) for r in gram)
    if not isfinite(norm) or norm == 0:
        raise Refusal('zero or overflowing constraint Gram matrix')
    a, b, c = gram[0]
    _, d, e = gram[1]
    f = gram[2][2]
    if a*d-b*b <= 0 or a*(d*f-e*e)-b*(b*f-c*e)+c*(b*e-c*d) <= 0:
        raise Refusal('constraint Gram matrix is not positive definite')
    aug = [r[:] + [float(i == j) for j in range(3)] for i, r in enumerate(gram)]
    for j in range(3):
        pivot = max(range(j, 3), key=lambda i: abs(aug[i][j]))
        aug[j], aug[pivot] = aug[pivot], aug[j]
        if abs(aug[j][j]) <= 1e-14*norm:
            raise Refusal('unresolved constraint row rank')
        scale = aug[j][j]
        aug[j] = [v/scale for v in aug[j]]
        for i in range(3):
            if i != j:
                scale = aug[i][j]
                aug[i] = [a-scale*b for a, b in zip(aug[i], aug[j])]
    bound = max(1., sqrt(norm*max(fsum(abs(v) for v in r[3:]) for r in aug)))
    if not isfinite(bound) or bound > 1e6:
        raise Refusal('ill-conditioned constraint rows')
    return dict(method='sqrt infinity-norm condition of three-row Gram',
                condition_bound=bound, gram=gram)
