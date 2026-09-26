"""Run the real driver/Newton path with fake FEM boundaries, not a FEM proof."""
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from . import fixture_driver as driver
from .sparse import CSR
from .test_driver_supervision import CONTRACT, payload


class Array(list):
    def tolist(self):
        return list(self)


class DriverWiring(unittest.TestCase):
    def test_complete_driver_keeps_mixed_and_scalar_dimensions_separate(self):
        """R222 failed at the first assembly: its state omitted all three scalars."""
        target = [2., 3., 4., 5., 0., 0., 0.]
        space = MagicMock()
        space.sub.return_value.collapse.return_value = (None, [0, 1, 2])
        def function(_):
            return SimpleNamespace(x=SimpleNamespace(array=Array(target[:4]),
                                                      scatter_forward=lambda: None),
                                   sub=lambda _: SimpleNamespace(collapse=lambda: None))
        fem = SimpleNamespace(Function=function, form=lambda x: x,
                              assemble_scalar=MagicMock(side_effect=[0., 1., 0., 0.]))
        U = MagicMock()
        U.split.return_value = (MagicMock(), MagicMock())
        U.Measure.return_value = MagicMock()
        observed = []
        class Assembler:
            rows = (0, 1, 2)
            def __init__(self, *args):
                pass
            def vector(self, i):
                return [[0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]][i]
            def __call__(self, state):
                # This assertion reproduces the real adapter's n+3 contract.
                if len(state) != 7:
                    raise ValueError('mixed state missing scalar border')
                observed.append(list(state))
                return [v-t for v, t in zip(state, target)], CSR.from_rows(
                    [{i: 1.} for i in range(7)])
        data = {'targets': [0., 0.], 'force': MagicMock()}
        modules = dict.fromkeys(['np', 'mesh', 'fem_petsc', 'basix_ufl',
                                 'basix', 'PETSc', 'comm'])
        modules.update(fem=fem, ufl=U)
        raw = payload()['diagnostics_degree24']['raw']
        with (patch.object(driver, 'create_cube', return_value=(None, space, None, None)),
              patch.object(driver, 'interpolate_state', side_effect=lambda *a: function(space)),
              patch.object(driver, 'boundary_values', return_value={0: 2.}),
              patch.object(driver, 'step_forms', return_value=({}, [], {'exact': data, 'ds': MagicMock()})),
              patch.object(driver, 'Assembler', Assembler),
              patch.object(driver, 'sparse_solve', side_effect=lambda np, p, c, mat, rhs: rhs),
              patch.object(driver, 'exact_data', return_value=data),
              patch.object(driver, 'field_forms', return_value={}),
              patch.object(driver, 'assemble_scalars', return_value=raw),
              patch.object(driver, 'return_quadrature_samples', return_value=([0., 0.], [1, 1]))):
            report = driver.run_poiseuille(modules, CONTRACT)
        self.assertTrue(report['numerical_accepted'])
        self.assertEqual((report['mixed_dofs'], report['global_dofs']), (4, 7))
        self.assertEqual(observed[0], [2., 3.05, 4., 5., 0., 0., 0.])
        self.assertEqual(observed[-1], target)
        self.assertEqual(len(report['linear_corrections']), 1)
        self.assertEqual(report['multipliers'], [0., 0.])
        self.assertEqual(report['eta'], 0.)


if __name__ == '__main__':
    unittest.main()
