"""Geometry and calibration checks for the sufficient B2 local certificate."""

from __future__ import annotations

import importlib.util
import itertools
import json
import unittest

import numpy as np

from realizability.backends.b2_coercivity import (
    calculate_local_bound,
    face_trace_matrix,
    p1_mass_matrix,
)


class LocalFormulaTests(unittest.TestCase):
    def test_analytic_p1_mass_and_face_integrals(self) -> None:
        # Independent degree-two simplex quadrature on a unit tetrahedron.
        volume = 1.0 / 6.0
        a, b = 0.5854101966249685, 0.1381966011250105
        barycentric = np.asarray([(a if i == j else b) for j in range(4) for i in range(4)]).reshape(4, 4)
        quadrature_mass = np.zeros((4, 4))
        for point in barycentric:
            quadrature_mass += (volume / 4.0) * np.outer(point, point)
        # The analytic formula is V/20*(1 + delta_ij).
        mass = p1_mass_matrix(volume)
        np.testing.assert_allclose(mass, quadrature_mass, rtol=1e-14, atol=1e-16)

        face_area = 1.0
        face_points = np.asarray(((2/3, 1/6, 1/6), (1/6, 2/3, 1/6), (1/6, 1/6, 2/3)))
        quadrature_face = np.zeros((3, 3))
        for point in face_points:
            quadrature_face += (face_area / 3.0) * np.outer(point, point)
        trace = face_trace_matrix(face_area, (0, 2, 3))
        np.testing.assert_allclose(trace[np.ix_((0, 2, 3), (0, 2, 3))], quadrature_face,
                                   rtol=1e-14, atol=1e-16)
        self.assertEqual(trace[1, 1], 0.0)

    def test_degenerate_tetrahedron_fails_geometry_guard(self) -> None:
        from realizability.backends.b2_coercivity import _cell_geometry
        flat = np.asarray(((0., 0., 0.), (1., 0., 0.), (0., 1., 0.), (1., 1., 0.)))
        volume, diameter = _cell_geometry(flat)
        self.assertEqual(volume, 0.0)
        self.assertLessEqual(volume / diameter**3, 1.0e-12)

    def test_nonfinite_guarded_margin_is_invalid_and_json_safe(self) -> None:
        from realizability.backends.b2_coercivity import _classify
        result = _classify(1.0e308, 1.0e-308)
        self.assertEqual(result["status"], "invalid")
        self.assertIsNone(result["beta"])
        json.dumps(result, allow_nan=False)

    def test_cell_bound_is_scale_and_vertex_permutation_invariant(self) -> None:
        vertices = np.asarray(((0., 0., 0.), (1., 0., 0.), (0., 1., 0.), (0., 0., 1.)))

        def value(points: np.ndarray) -> float:
            from realizability.backends.b2_coercivity import _cell_geometry
            volume, diameter = _cell_geometry(points)
            trace = np.zeros((4, 4))
            for face in itertools.combinations(range(4), 3):
                triangle = points[list(face)]
                area = np.linalg.norm(np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])) / 2
                trace += diameter * face_trace_matrix(float(area), face)
            p = np.eye(4) - (1 - 1 / np.sqrt(5)) * np.ones((4, 4)) / 4
            white = (20 / volume) * p @ trace @ p
            return float(np.max(np.sum(np.abs(white), axis=1)))

        base = value(vertices)
        self.assertAlmostEqual(value(7.3 * vertices), base, places=12)
        for order in itertools.permutations(range(4)):
            self.assertAlmostEqual(value(vertices[list(order)]), base, places=12)

    def test_resource_refusal_precedes_cell_coordinate_arrays(self) -> None:
        class Geometry:
            dofmap = np.zeros((3, 4), dtype=int)
            cmap = type("CMap", (), {"degree": 1})()
            @property
            def x(self):
                raise AssertionError("coordinates must not be copied before the cell cap check")

        domain = type("Domain", (), {
            "comm": type("Comm", (), {"size": 1})(),
            "topology": type("Topology", (), {"dim": 3, "index_map": lambda self, _: type("Index", (), {"size_global": 3})()})(),
            "geometry": Geometry(),
        })()
        with self.assertRaises(OverflowError):
            calculate_local_bound(domain, max_cells=2)


@unittest.skipUnless(importlib.util.find_spec("dolfinx"), "optional DOLFINx environment is not active")
class DOLFINxCoercivityCalibrationTests(unittest.TestCase):
    def test_each_local_trace_constant_matches_ufl_assembly(self) -> None:
        import scipy.linalg as la
        from dolfinx import fem
        from dolfinx.fem import petsc as fem_petsc
        import ufl

        from realizability.backends.fenicsx_stokes import create_cylinder
        from realizability.config import PilotConfig

        for size in (0.10, 0.07):
            domain, _, _ = create_cylinder(PilotConfig(), size)
            result = calculate_local_bound(domain)
            Q = fem.functionspace(domain, ("DG", 1))
            p, q = ufl.TrialFunction(Q), ufl.TestFunction(Q)
            h = ufl.CellDiameter(domain)
            mass = fem_petsc.assemble_matrix(fem.form(p * q * ufl.dx)); mass.assemble()
            trace = fem_petsc.assemble_matrix(fem.form(ufl.avg(h) / 2 * (p("+") * q("+") + p("-") * q("-")) * ufl.dS + h * p * q * ufl.ds)); trace.assemble()
            mi, mj, mv = mass.getValuesCSR(); ti, tj, tv = trace.getValuesCSR()
            from scipy.sparse import csr_matrix
            M = csr_matrix((mv, mj, mi), shape=mass.getSize())
            T = csr_matrix((tv, tj, ti), shape=trace.getSize())
            for cell in range(result["cell_count"]):
                dofs = Q.dofmap.cell_dofs(cell)
                actual = la.eigvalsh(T[dofs][:, dofs].toarray(), M[dofs][:, dofs].toarray())[-1]
                expected = result["cell_trace_eigenvalues"][cell]
                self.assertLessEqual(abs(actual - expected) / abs(expected), 1.0e-12)
            mass.destroy(); trace.destroy()
