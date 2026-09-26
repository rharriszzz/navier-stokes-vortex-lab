"""Import-free integration/algebra tests; deliberately not FEM mocks-as-proof."""
from fractions import Fraction as F
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from .sparse import CSR, border_and_lift, row_scales, scale_system, constraint_condition
from .prototype import Refusal, newton, enforce_lifting
from .cube_adapter import merge_tags, fields, sparse_solve
from .diagnostics import (signed_budget, refinement, quadrature_comparison,
                          ANGULAR_TERMS, ENERGY_TERMS, field_report,
                          integrate_budgets, step_checks, physical_interval_budget)
from .fixtures import forcing, stress
from .polynomial import x, y, z, volume, face, dot
from .test_algebra import toy_matrix, rank


def dense(matrix):
    return [[row.get(j, 0.) for j in range(matrix.n)] for row in matrix.rows()]


def scripted_solver(answer, reason=4, pc_reason=0, solve_error=None):
    """Script status/answer only; never emulate or execute a factorization."""
    events = []

    class Array(list):
        def tolist(self):
            return list(self)

    class Vec:
        def __init__(self, name):
            self.name, self.array = name, Array([0., 0.])

        def getArray(self, readonly=False):
            return self.array

        def destroy(self):
            events.append(('destroy', self.name))

    class Mat:
        def createAIJ(self, **kwargs):
            self.vectors = 0
            return self

        def assemble(self):
            pass

        def createVecRight(self):
            self.vectors += 1
            return Vec('b' if self.vectors == 1 else 'x')

        def destroy(self):
            events.append(('destroy', 'a'))

    class PC:
        def setType(self, value):
            events.append(('pc', value))

        def setFactorSolverType(self, value):
            events.append(('backend', value))

        def getFailedReason(self):
            events.append(('pc_reason',))
            if isinstance(pc_reason, Exception):
                raise pc_reason
            return pc_reason

    class KSP:
        def create(self, comm):
            return self

        def setOperators(self, matrix):
            pass

        def setType(self, value):
            events.append(('ksp', value))

        def getPC(self):
            return PC()

        def solve(self, b, x):
            events.append(('solve', tuple(b.array)))
            if solve_error is not None:
                raise solve_error
            x.array[:] = answer

        def getConvergedReason(self):
            return reason

        def destroy(self):
            events.append(('destroy', 'ksp'))

    np = SimpleNamespace(asarray=lambda values, dtype: tuple(dtype(v) for v in values))
    petsc = SimpleNamespace(Mat=Mat, KSP=KSP, IntType=int, ScalarType=float)
    return np, petsc, SimpleNamespace(size=1), events


class AdapterChecks(unittest.TestCase):
    def test_sparse_refusal_preserves_both_status_and_nonfinite_count(self):
        matrix = CSR.from_rows([{0: 1.}, {1: 1.}])
        for reason, answer, count in ((-11, [1., 2.], 0), (0, [1., 2.], 0),
                                       (4, [float('nan'), 2.], 1),
                                       (-11, [float('inf'), -float('inf')], 2)):
            with self.subTest(reason=reason, count=count):
                np, petsc, comm, events = scripted_solver(answer, reason, 2)
                with self.assertRaises(Refusal) as caught:
                    sparse_solve(np, petsc, comm, matrix, [1., 2.])
                message = str(caught.exception)
                self.assertIn(f'ksp_reason={reason};', message)
                self.assertIn(f'nonfinite_answer_entries={count};', message)
                self.assertIn('pc_failed_reason=2', message)
                self.assertEqual(events[-4:], [('destroy', n) for n in ('ksp', 'x', 'b', 'a')])

    def test_optional_pc_diagnostic_failure_keeps_primary_refusal(self):
        np, petsc, comm, events = scripted_solver([1., 2.], -11, RuntimeError('probe'))
        with self.assertRaisesRegex(Refusal, 'ksp_reason=-11;.*pc_failed_reason=unavailable:RuntimeError'):
            sparse_solve(np, petsc, comm, CSR.from_rows([{0: 1.}, {1: 1.}]), [1., 2.])
        self.assertEqual(events[-4:], [('destroy', n) for n in ('ksp', 'x', 'b', 'a')])

    def test_sparse_diagnostic_preserves_success_true_residual_and_solver_exception(self):
        matrix = CSR.from_rows([{0: 1.}, {1: 1.}])
        for answer, error in (([1., 2.], None), ([0., 0.], None),
                              ([1., 2.], RuntimeError('scripted solve exception'))):
            with self.subTest(answer=answer, error=error):
                np, petsc, comm, events = scripted_solver(answer, solve_error=error)
                if error is not None:
                    with self.assertRaises(RuntimeError) as caught:
                        sparse_solve(np, petsc, comm, matrix, [1., 2.])
                    self.assertIs(caught.exception, error)
                elif answer == [0., 0.]:
                    with self.assertRaisesRegex(Refusal, '^sparse linear true residual failed$'):
                        sparse_solve(np, petsc, comm, matrix, [1., 2.])
                else:
                    self.assertEqual(sparse_solve(np, petsc, comm, matrix, [1., 2.]), answer)
                self.assertEqual(events[:4], [('ksp', 'preonly'), ('pc', 'lu'),
                                              ('backend', 'petsc'), ('solve', (1., 2.))])
                self.assertNotIn(('pc_reason',), events)
                self.assertEqual(events[-4:], [('destroy', n) for n in ('ksp', 'x', 'b', 'a')])

    def test_csr_keeps_zero_diagonal_without_changing_operator(self):
        rows = [{2: 4., 0: 0., 1: 0.}, {}, {0: -2., 2: 3.}]
        original = [dict(row) for row in rows]
        matrix = CSR.from_rows(rows)
        self.assertEqual(rows, original)
        self.assertEqual(matrix.indptr, (0, 2, 3, 5))
        self.assertEqual(matrix.indices, (0, 2, 1, 0, 2))
        self.assertEqual(matrix.values, (0., 4., 0., -2., 3.))
        self.assertEqual(matrix.matvec([2., 5., 7.]), [28., 0., 17.])
        # Empty rows remain numerically zero: structural completion is no shift.
        zero = CSR.from_rows([{}, {}, {}])
        self.assertEqual(zero.indices, (0, 1, 2))
        self.assertEqual(zero.values, (0., 0., 0.))
        self.assertEqual(rank(dense(zero)), 0)

    def test_border_lift_and_scaling_keep_pressure_and_scalar_diagonals(self):
        full = toy_matrix()
        core = CSR.from_rows([{j: full[i][j] for j in range(5)} for i in range(5)])
        columns = [[float(full[i][j]) for i in range(5)] for j in range(5, 8)]
        rows = [[float(v) for v in full[i][:5]] for i in range(5, 8)]
        state, residual = [2.] + [0.]*7, [float(i-3) for i in range(8)]
        for fixed in ({}, {0: 2.}):
            with self.subTest(fixed=fixed):
                r, matrix = border_and_lift(core, columns, rows, residual[:5],
                                            residual[5:], state, fixed)
                expected_r, expected = enforce_lifting(residual, full, state, fixed)
                self.assertEqual(r, expected_r)
                self.assertEqual(dense(matrix), expected)
                scales = row_scales(matrix)
                sr, scaled = scale_system(r, matrix, scales)
                self.assertEqual(sr, [s*v for s, v in zip(scales, expected_r)])
                self.assertEqual(dense(scaled), [[scales[i]*v for v in row]
                                                for i, row in enumerate(expected)])
                for candidate in (matrix, scaled):
                    self.assertTrue(all(i in row for i, row in enumerate(candidate.rows())))
                    for i in range(3, 8):  # two pressure rows, P-, P+, eta
                        self.assertEqual(candidate.rows()[i][i], 0.)
                if fixed:
                    self.assertEqual(matrix.rows()[0], {0: 1.})
                    self.assertTrue(all(0 not in row for row in matrix.rows()[1:]))
                else:
                    self.assertEqual(rank(dense(matrix)), 8)

    def test_zero_diagonals_reach_petsc_csr_boundary(self):
        # Exercise the real bridge up to createAIJ, without importing PETSc/NumPy
        # or pretending to factor a matrix. The saddle matrix is invertible.
        _, matrix = scale_system([1., 2.], CSR.from_rows([{1: 1.}, {0: 1.}]), (2., 3.))
        captured = {}
        class BoundaryReached(Exception):
            pass
        class Mat:
            def createAIJ(self, **kwargs):
                captured.update(kwargs)
                raise BoundaryReached
        np = SimpleNamespace(asarray=lambda values, dtype: tuple(dtype(v) for v in values))
        petsc = SimpleNamespace(Mat=Mat, IntType=int, ScalarType=float)
        comm = SimpleNamespace(size=1)
        with self.assertRaises(BoundaryReached):
            sparse_solve(np, petsc, comm, matrix, [2., 6.])
        self.assertEqual(captured['size'], (2, 2))
        self.assertIs(captured['comm'], comm)
        self.assertEqual(captured['csr'], ((0, 2, 4), (0, 1, 0, 1), (0., 2., 3., 0.)))

    def test_constraint_condition_and_rank_refusal(self):
        report = constraint_condition([[1., 0., 0., 9.], [0., 2., 0., 9.], [0., 0., 3., 9.]], {3})
        self.assertEqual(report['condition_bound'], 3.)
        for rows in ([[1., 0., 0.]]*3, [[1., 0., 0.], [0., 1., 0.], [0., 0., 1e-8]]):
            with self.assertRaises(Refusal):
                constraint_condition(rows, {})

    def test_border_rank_and_dense_lifting_equivalence(self):
        full = toy_matrix()
        core = CSR.from_rows([{j: full[i][j] for j in range(5)} for i in range(5)])
        columns = [[float(full[i][j]) for i in range(5)] for j in range(5, 8)]
        rows = [[float(v) for v in full[i][:5]] for i in range(5, 8)]
        state, r = [2., 0., 0., 0., 0., 0., 0., 0.], [float(i-3) for i in range(8)]
        _, raw = border_and_lift(core, columns, rows, r[:5], r[5:], state, {})
        self.assertEqual(dense(raw), full)
        self.assertEqual(rank(dense(raw)), 8)
        br, bj = border_and_lift(core, columns, rows, r[:5], r[5:], state, {0: 2.})
        dr, dj = enforce_lifting(r, full, state, {0: 2.})
        self.assertEqual(br, dr)
        self.assertEqual(dense(bj), dj)
        self.assertEqual(br[5:], r[5:])
        with self.assertRaises(Refusal):
            border_and_lift(core, columns, rows, r[:5], r[5:], state, {0: 0.})

    def test_sparse_newton_and_fixed_scaling(self):
        def evaluate(x):
            j = CSR.from_rows([{0: 2*x[0]}])
            return scale_system([x[0]**2-2], j, (.1,))
        root, _ = newton([.1], evaluate, lambda j, b: [b[0]/j.values[0]])
        self.assertAlmostEqual(root[0]**2, 2, places=10)
        j = CSR.from_rows([{0: 2., 1: -4.}, {1: 8.}])
        self.assertEqual(row_scales(j), (1/6, 1/8))
        self.assertEqual(j.matvec([3., 2.]), [-2., 16.])
        with self.assertRaises(Refusal):
            newton([.1], evaluate, lambda j, b: [0.])

    def test_bad_csr_refused_without_densification(self):
        for j in (CSR(1, (0, 1), (1,), (1.,)), CSR(1, (0, 1), (0,), (float('nan'),)),
                  CSR(1, (0, 2), (0, 0), (1., 2.)), CSR(2, (0, 2, 1), (0,), (1.,))):
            with self.assertRaises(ValueError):
                j.validate(j.n)
        n = 20003
        diagonal = CSR(n, tuple(range(n+1)), tuple(range(n)), (1.,)*n)
        diagonal.validate(n)
        self.assertEqual(diagonal.matvec([1.]*n), [1.]*n)
        # Deliberately no iteration/indexing protocol that could allocate n*n.
        self.assertFalse(hasattr(diagonal, '__iter__'))

    def test_boundary_partition_refusals(self):
        groups = {i: [10+i] for i in range(1, 7)}
        self.assertEqual(merge_tags(groups, range(11, 17)), (list(range(11, 17)), list(range(1, 7))))
        for bad, exterior in ((dict(groups, **{}), range(11, 18)),
                              ({**groups, 6: [11]}, range(11, 17)),
                              ({**groups, 6: []}, range(11, 17))):
            with self.assertRaises(Refusal):
                merge_tags(bad, exterior)
        with self.assertRaises(Refusal):
            fields('tank')

    def test_pressure_divergence_sign_independent_polynomial_balance(self):
        # Deliberately non-solenoidal field: both divergence terms are nonzero.
        u, p = [x, 2*y, 3*z], x+y+z
        f, sigma = forcing(u, p), stress(u, p)
        div = sum(u[i].d(i) for i in range(3))
        conv_div = volume(F(1, 2)*dot(u, u)*div)
        pressure_div = -volume(p*div)
        adv, work = 0, 0
        for axis in range(3):
            for side in (0, 1):
                sign = 2*side-1
                adv += face(F(1, 2)*dot(u, u)*u[axis]*sign, axis, side)
                work -= face(sum(u[i]*sigma[i][axis]*sign for i in range(3)), axis, side)
        diss = volume(sum(F(1, 20)*(u[i].d(j)+u[j].d(i))**2 for i in range(3) for j in range(3)))
        body = -volume(dot(u, f))
        self.assertEqual(adv+work+diss+body+conv_div+pressure_div, 0)
        self.assertNotEqual(conv_div, 0)
        self.assertNotEqual(pressure_div, 0)

    def test_budget_refusal_sign_and_integration(self):
        terms = dict(zip(ANGULAR_TERMS, [2., 3., -4., -1.]))
        self.assertTrue(signed_budget(terms, 'angular')['accepted'])
        self.assertFalse(signed_budget(dict(terms, body=1.), 'angular')['accepted'])
        for bad in ({'storage': 0}, dict(terms, body=float('nan'))):
            with self.assertRaises(Refusal):
                signed_budget(bad, 'angular')
        report = integrate_budgets([0., .5, 1.], [terms]*3, 'angular')
        self.assertEqual(report['budget']['terms'], terms)
        physical = physical_interval_budget([0., 1.], [terms]*2, 'angular', 0., 3.)
        self.assertTrue(physical['discrete_term_integral']['budget']['accepted'])
        self.assertFalse(physical['physical']['accepted'])
        with self.assertRaises(Refusal):
            integrate_budgets([0., 0.], [terms]*2, 'angular')

    def test_rates_floors_and_quadrature(self):
        self.assertTrue(refinement([1., .125, .015625], 2.5)['accepted'])
        self.assertFalse(refinement([1., 1., .5], 1.7)['accepted'])
        floor = refinement([1e-12]*3, 2.5)
        self.assertIsNone(floor['pairs'][0]['rate'])
        self.assertFalse(refinement([1.1e-10, 1e-12, 1e-12], 2.5)['accepted'])
        self.assertFalse(refinement([1e-12, 1e-5, 1e-6], 2.5)['accepted'])
        self.assertTrue(quadrature_comparison({'x': 2.}, {'x': 2.+1e-9})['x']['accepted'])
        self.assertFalse(quadrature_comparison({'x': 0.}, {'x': 1e-15})['x']['accepted'])
        with self.assertRaises(Refusal):
            quadrature_comparison({'x': 2.}, {})

    def test_field_report_missing_terms_and_eta_gate(self):
        values = dict(volume=1., pressure_mean=0., p_error_integral=0., p_error_squared=0.,
                      flux_0=.5, flux_1=1.5, area_0=1., area_1=1., lateral_flux=-2.,
                      boundary_absolute_flux=4., energy_identity_storage=0.,
                      energy_identity_dissipation=0., kinetic_discrete_derivative=0.)
        values.update({n+'_squared': 0. for n in ('u_L2', 'u_H1_seminorm', 'div_u_L2', 'traction_L2_returns')})
        values.update({'angular.'+n: 0. for n in ANGULAR_TERMS})
        values.update({'energy.'+n: 0. for n in ENERGY_TERMS})
        report = field_report(values, [0., 0.], [0., 0.], [.5, 1.5], .001)
        self.assertNotIn('accepted', report)
        gates = json.loads(Path(__file__).with_name('future_fem.json').read_text())['gates']
        checked = step_checks(report, [0.], [0.], 0., gates)
        self.assertFalse(checked['numerical_step_accepted'])
        self.assertFalse(checked['checks']['constraints'])
        bad = dict(values)
        del bad['energy.pressure_divergence']
        with self.assertRaises(Refusal):
            field_report(bad, [0., 0.], [0., 0.], [.5, 1.5], 0.)


if __name__ == '__main__':
    unittest.main()
