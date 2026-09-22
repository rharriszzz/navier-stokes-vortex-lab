"""Run with .venv/bin/python -m unittest verification.nonlinear_port.test_algebra."""
import ast
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest

from .polynomial import Poly, x, y, z, t, face, volume, dot
from .fixtures import manufactured, forcing, stress, return_data, poiseuille, rotation, affine_time, MU
from .prototype import (Refusal, compatible_fluxes, time_coefficients, newton,
                        NewtonOptions, enforce_lifting, require_fixture, launch, advance)


def rank(rows):
    a = [[F(v) for v in row] for row in rows]
    pivot = 0
    for col in range(len(a[0])):
        row = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if row is None:
            continue
        a[pivot], a[row] = a[row], a[pivot]
        scale = a[pivot][col]
        a[pivot] = [v/scale for v in a[pivot]]
        for i in range(len(a)):
            if i != pivot:
                c = a[i][col]
                a[i] = [v-c*w for v, w in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def toy_matrix(gauge=True):
    # Unknowns v0,v1,v2,p_const,p_zero_mean,P-,P+[,eta].
    b = [[1, 1, 0], [0, 0, 1]]
    c = [[1, 0, 0], [0, 1, 0]]
    n = 8 if gauge else 7
    a = [[F(0) for _ in range(n)] for _ in range(n)]
    for i in range(3):
        a[i][i] = 2
        for j in range(2):
            a[i][3+j] = -b[j][i]
            a[3+j][i] = b[j][i]
            a[i][5+j] = c[j][i]
            a[5+j][i] = c[j][i]
    if gauge:
        a[3][7] = a[7][3] = 1
    return a


class AlgebraChecks(unittest.TestCase):
    def test_polynomial_primitives(self):
        p = F(3, 7)*x**4*y**2*z*t**3
        self.assertEqual(p.d(0), F(12, 7)*x**3*y**2*z*t**3)
        self.assertEqual(volume(p), t**3*F(1, 70))
        self.assertEqual(face(p, 2, 1), t**3*F(1, 35))

    def test_manufactured_flux_pressure_and_lift(self):
        u, p = manufactured()
        self.assertEqual(sum(u[j].d(j) for j in range(3)), 0)
        self.assertEqual(volume(p), 0)
        a, c = 1+t+t**3, F(1, 2)+t
        lift = [-a*x, -a*y, 2*a*z-c]
        for axis in (0, 1):
            for side in (0, 1):
                for i in range(3):
                    self.assertEqual(u[i].at(axis, side), lift[i].at(axis, side))
        # Affine lift is representable exactly in P2; swirl trace vanishes on sides.
        self.assertEqual(sum(lift[i].d(i) for i in range(3)), 0)
        for side in (0, 1):
            flux, pressure, offset = return_data(side)
            self.assertEqual(face(u[2]*(2*side-1), 2, side), flux)
            self.assertEqual(face(offset[2], 2, side), 0)
            self.assertEqual(offset[0], 0)
            self.assertEqual(offset[1], 0)
            self.assertNotEqual(offset[2], 0)
            self.assertNotEqual(pressure, 0)
        self.assertEqual(return_data(0)[0]+return_data(1)[0], 2*a)
        for time in (0, F(1, 4), 1):
            self.assertGreater(float(return_data(0)[0].at(3, time).evaluate([0]*4)), 0)
            self.assertGreater(float(return_data(1)[0].at(3, time).evaluate([0]*4)), 0)

    def test_force_independent_advective_expression(self):
        u, p = manufactured()
        f = forcing(u, p)
        for i in range(3):
            oracle = u[i].d(3)+sum(u[j]*u[i].d(j) for j in range(3))
            oracle += p.d(i)-MU*sum(u[i].d(j).d(j) for j in range(3))
            self.assertEqual(f[i], oracle)
        self.assertNotEqual(sum(u[j]*u[0].d(j) for j in range(3)), 0)
        # Independent axial formula; u_z=2Az-C, no x/y dependence.
        a, c = 1+t+t**3, F(1, 2)+t
        self.assertEqual(f[2], 2*(1+3*t*t)*z-1+2*a*(2*a*z-c)+2*(1+t)*z)

    def test_closed_angular_budget(self):
        u, p = manufactured()
        sigma, f = stress(u, p), forcing(u, p)
        angular = x*u[1]-y*u[0]
        advective, traction = Poly(), Poly()
        for axis in range(3):
            for side in (0, 1):
                sign = 2*side-1
                advective += face(angular*u[axis]*sign, axis, side)
                traction += face((x*sigma[1][axis]-y*sigma[0][axis])*sign, axis, side)
        self.assertEqual(volume(angular).d(3)+advective-traction-volume(x*f[1]-y*f[0]), 0)
        self.assertNotEqual(traction, 0)

    def test_closed_energy_budget(self):
        u, p = manufactured()
        sigma, f = stress(u, p), forcing(u, p)
        energy = F(1, 2)*dot(u, u)
        dissipation = sum(MU*F(1, 2)*(u[i].d(j)+u[j].d(i))**2
                          for i in range(3) for j in range(3))
        advective, work = Poly(), Poly()
        for axis in range(3):
            for side in (0, 1):
                sign = 2*side-1
                advective += face(energy*u[axis]*sign, axis, side)
                work += face(sum(u[i]*sigma[i][axis]*sign for i in range(3)), axis, side)
        self.assertEqual(volume(energy).d(3)+advective-work+volume(dissipation)-volume(dot(u, f)), 0)
        self.assertNotEqual(volume(dissipation), 0)

    def test_poiseuille_oracle(self):
        u, p = poiseuille()
        self.assertEqual(forcing(u, p), [Poly(), Poly(), Poly()])
        self.assertEqual(volume(u[0]), F(2, 3))
        self.assertEqual(p.at(0, 0)-p.at(0, 1), 8*MU)
        self.assertEqual(stress(u, p)[1][0], 4*MU*(1-2*y))
        self.assertEqual(volume(p), 0)

    def test_rigid_rotation_oracle(self):
        u, p = rotation()
        self.assertEqual(forcing(u, p), [Poly(), Poly(), Poly()])
        self.assertEqual(volume(p), 0)
        for i in range(3):
            for j in range(3):
                self.assertEqual(u[i].d(j)+u[j].d(i), 0)

    def test_constraint_rank_and_joint_null_vector(self):
        a = toy_matrix(False)
        self.assertEqual(rank(a), 6)
        null = [0, 0, 0, 1, 0, 1, 1]
        self.assertEqual([dot(row, null) for row in a], [0]*7)
        self.assertNotEqual([row[3] for row in a], [0]*7)
        self.assertEqual(rank(toy_matrix()), 8)
        # Remove constant pressure and its redundant divergence row:
        keep = [0, 1, 2, 4, 5, 6]
        self.assertEqual(rank([[a[i][j] for j in keep] for i in keep]), 6)
        compatible_fluxes(-2.0, [.5, 1.5], 4.0)
        with self.assertRaises(Refusal):
            compatible_fluxes(-2.0, [.5, 1.5001], 4.0001)
        with self.assertRaises(Refusal):
            compatible_fluxes(-2.0, [.5, 1.5], float('nan'))

    def test_retained_lifting_rows(self):
        # Constraint x0+x1=5 with installed x0=2 must retain residual x1-3.
        r, j = enforce_lifting([7., -3.], [[4., 5.], [1., 1.]], [2., 0.], {0: 2.})
        self.assertEqual(r, [0., -3.])
        self.assertEqual(j, [[1., 0.], [0., 1.]])
        with self.assertRaises(Refusal):
            enforce_lifting([0., 0.], [[1., 0.], [0., 1.]], [0., 0.], {0: 2.})

    def test_backward_euler_bdf2_and_energy_identity(self):
        dt = F(1, 8)
        for step in (1, 2):
            a = time_coefficients(step, dt)
            self.assertAlmostEqual(sum(a), 0)
            self.assertAlmostEqual(sum(c*v for c, v in zip(a, [1, 1-dt, 1-2*dt])), 1)
        a = time_coefficients(2, dt)
        self.assertAlmostEqual(sum(c*v for c, v in zip(a, [1, (1-dt)**2, (1-2*dt)**2])), 2)
        # Scalar identity extends componentwise in any mass inner product.
        u, v, w = F(3, 7), F(-2, 3), F(4, 5)
        lhs = (3*u-4*v+w)*u/2
        rhs = (u*u+(2*u-v)**2-v*v-(2*v-w)**2+(u-2*v+w)**2)/4
        self.assertEqual(lhs, rhs)

    def test_newton_and_failure_paths(self):
        root, history = newton([.1], lambda x: ([x[0]**2-2], [[2*x[0]]]),
                               lambda j, b: [b[0]/j[0][0]])
        self.assertAlmostEqual(root[0]**2, 2, places=10)
        self.assertLess(history[-1], 1e-10)
        self.assertTrue(all(b < a for a, b in zip(history, history[1:])))
        for evaluation, solver, options in (
                (lambda x: ([float('nan')], [[1]]), lambda j, b: b, NewtonOptions()),
                (lambda x: ([1.], [[1.]]), lambda j, b: [0.], NewtonOptions()),
                (lambda x: ([1.], [[1.]]), lambda j, b: b, NewtonOptions()),
                (lambda x: ([x[0]**2-2], [[2*x[0]]]), lambda j, b: [b[0]/j[0][0]], NewtonOptions(iterations=1))):
            with self.assertRaises(Refusal):
                newton([.1], evaluation, solver, options)

    def test_affine_time_companion(self):
        u, p = affine_time()
        self.assertEqual(sum(u[i].d(i) for i in range(3)), 0)
        self.assertEqual(volume(p), 0)
        for field, degree in [(v, 1) for v in u]+[(p, 1)]:
            self.assertLessEqual(max(sum(k[:3]) for k in field.terms), degree)
        self.assertNotEqual(u[0].d(3).d(3).d(3), 0)

    def test_time_loop_history_and_rejection(self):
        # y'=3t^2 with exact y(0)=0; exercises actual BE startup then BDF2.
        errors = []
        for dt in (.125, .0625, .03125):
            def problem(step, time, old, older):
                a, b, c = time_coefficients(step, dt)
                def evaluate(value):
                    return [a*value[0]+b*old[0]+c*older[0]-3*time*time], [[a]]
                return old[:], evaluate, lambda state: {'accepted': True}
            result, reports = advance([0.], dt, round(1/dt), problem,
                                      lambda j, b: [b[0]/j[0][0]])
            self.assertEqual(reports[-1]['time'], 1)
            errors.append(abs(result[0]-1))
        self.assertGreater(errors[0]/errors[1], 3.5)
        self.assertGreater(errors[1]/errors[2], 3.5)
        def bad_problem(step, time, old, older):
            return [0.], lambda x: ([x[0]], [[1.]]), lambda x: {'accepted': False}
        with self.assertRaises(Refusal):
            advance([0.], .125, 1, bad_problem, lambda j, b: b)

    def test_scope_syntax_and_no_fem_imports(self):
        for name in ('tank', 'b2', 'campaign'):
            with self.assertRaises(Refusal):
                require_fixture(name)
        with self.assertRaises(Refusal):
            launch()
        forbidden = {'ufl', 'dolfinx', 'basix', 'petsc4py', 'mpi4py', 'numpy', 'sympy'}
        self.assertFalse(forbidden.intersection(sys.modules))
        for path in Path(__file__).parent.glob('*.py'):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertFalse({a.name.split('.')[0] for a in node.names} & forbidden)
                if isinstance(node, ast.ImportFrom) and node.module:
                    self.assertNotIn(node.module.split('.')[0], forbidden)

    def test_manifest(self):
        from .manifest import validate
        path = Path(__file__).with_name('future_fem.json')
        data = json.loads(path.read_text())
        validate(data)
        for key, value in [('execution_admitted', True), ('attempts_granted', 1), ('fixture', 'tank')]:
            bad = dict(data, **{key: value})
            with self.assertRaises(Refusal):
                validate(bad)


if __name__ == '__main__':
    unittest.main()
