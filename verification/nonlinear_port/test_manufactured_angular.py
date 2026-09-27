"""Import-free angular sidecar controls and worker persistence checks."""
from copy import deepcopy
from math import fsum
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from . import manufactured_angular as audit
from . import manufactured_worker as worker
from .manufactured_driver import GEOMETRY
from .manufactured_manifest import expected
from .prototype import Refusal


BINDING = dict(source_commit='a'*40, executable_sha256='b'*64)


def sample():
    pressure = list(range(0, 54, 2))
    velocity = [i for i in range(402) if i not in set(pressure)]
    coordinates = [[(j % 17)/16, (j % 13)/12, (j % 11)/10]
                   for j in range(125)]
    phi = [0.]*402
    for j, (x, y, _z) in enumerate(coordinates):
        for c, value in enumerate((-y, x, 0.)):
            phi[velocity[3*j+c]] = value
    fixed = sorted(velocity[:240])
    state = [0.]*402 + [.23, -.37, .19]
    for i in fixed:
        state[i] = 1.+i/1000
    result = dict(schema=1, fixture='manufactured',
        stage='final_accepted_state_after_newton', source_binding=BINDING,
        geometry=deepcopy(GEOMETRY), step=1, time=.125, dt=.125,
        state=state, fixed_indices=fixed,
        fixed_values=[state[i] for i in fixed],
        phi=dict(coefficients=phi, velocity_parent_map=velocity,
                 pressure_parent_map=pressure,
                 velocity_node_coordinates=coordinates, velocity_block_size=3),
        degrees={})
    for degree in audit.DEGREES:
        residual = [(i+1)/137 for i in range(402)]
        if degree == '26':
            residual = [v+.02 for v in residual]
        scalar = dict(A_D=.43, A_R=.59, C_D=-.8, C_R=.666,
                      G_R=-1/11, residual_action=fsum(
                          phi[i]*residual[i] for i in range(402)))
        original = dict(storage=1.5, advective=scalar['A_D']+scalar['A_R'],
                        traction=scalar['C_D']+scalar['C_R'])
        original['body'] = scalar['residual_action']-original['storage']-scalar['A_R']-scalar['G_R']
        original['physical_defect'] = fsum(original.values())
        reductions, comparisons = audit._reductions(phi, residual, fixed, scalar, original)
        result['degrees'][degree] = dict(raw_residual=residual,
            raw_receipt=dict(method='fem_petsc.assemble_vector+ghost_reverse',
                compiled_rank=1, integrals=[list(p) for p in audit.EXPECTED_INTEGRALS['raw_residual']]),
            scalar=scalar, scalar_receipts={key:dict(method='fem.form+assemble_scalar',
                compiled_rank=0, integrals=[list(p) for p in audit.EXPECTED_INTEGRALS[key]])
                for key in audit.SCALARS}, original=original,
            multipliers=state[402:], reductions=reductions,
            comparisons=comparisons)
    return result


class AngularEvidenceChecks(unittest.TestCase):
    def test_degree26_constants_receive_distinct_final_values(self):
        state = sample()['state']
        degree24 = [NS(value=0.) for _ in range(3)]
        degree26 = [NS(value=7.) for _ in range(3)]
        for constants in (degree24, degree26):
            audit.install_final_constants(constants, state)
            self.assertEqual([c.value for c in constants], [.23, -.37, .19])
        with self.assertRaises(Refusal):
            audit.install_final_constants(degree26[:2], state)

    def test_nontrivial_maps_final_constants_and_independent_actions(self):
        item = sample()
        self.assertIs(audit.validate_record(item, BINDING), item)
        for degree in audit.DEGREES:
            entry = item['degrees'][degree]
            self.assertNotEqual(entry['reductions']['R_D'], 0)
            self.assertNotEqual(entry['reductions']['R_F'], 0)
            self.assertTrue(all(check['accepted'] for check in entry['comparisons'].values()))
        self.assertNotEqual(item['degrees']['24']['raw_residual'],
                            item['degrees']['26']['raw_residual'])
        for key, mutation in (
            ('state', lambda v: v['state'].__setitem__(402, 0.)),
            ('fixed', lambda v: v['fixed_values'].__setitem__(0, 0.)),
            ('phi', lambda v: v['phi']['coefficients'].__setitem__(
                v['phi']['velocity_parent_map'][4], 0.)),
            ('map', lambda v: v['phi']['velocity_parent_map'].__setitem__(0, 0)),
            ('raw', lambda v: v['degrees']['26']['raw_residual'].__setitem__(
                v['phi']['velocity_parent_map'][4], 0.)),
            ('receipt', lambda v: v['degrees']['24']['raw_receipt'].update(
                method='row_scaled')),
            ('geometry_bool', lambda v: v['geometry'].update(space_used_for_field_representation=1)),
            ('cached_bool', lambda v: v['degrees']['24']['comparisons']['advection'].update(accepted=1)),
            ('extra', lambda v: v['degrees']['24'].update(extra=1)),
            ('bool', lambda v: v['degrees']['26']['scalar'].update(A_D=True)),
            ('nonfinite', lambda v: v['degrees']['26']['scalar'].update(A_D=float('nan'))),
        ):
            bad = deepcopy(item); mutation(bad)
            with self.subTest(key=key), self.assertRaises(Refusal):
                audit.validate_record(bad, BINDING)

    def test_measured_mismatch_is_retained_and_wrong_sign_controls_fail(self):
        item = sample()
        for change, comparison in (
            (lambda e: e['scalar'].update(A_D=-e['scalar']['A_D']), 'advection'),
            (lambda e: e['scalar'].update(A_D=0.), 'advection'),
            (lambda e: e['scalar'].update(G_R=-e['scalar']['G_R']), 'residual_scalar_action'),
            (lambda e: e['raw_residual'].__setitem__(
                next(i for i in range(402) if i not in item['fixed_indices'] and
                     item['phi']['coefficients'][i] != 0), 0.), 'residual_vector_action'),
        ):
            bad = deepcopy(item)
            entry = bad['degrees']['24']
            change(entry)
            entry['reductions'], entry['comparisons'] = audit._reductions(
                bad['phi']['coefficients'], entry['raw_residual'], bad['fixed_indices'],
                entry['scalar'], entry['original'])
            self.assertFalse(entry['comparisons'][comparison]['accepted'])
            self.assertIs(audit.validate_record(bad, BINDING), bad)

    def test_json_refusals_and_exclusive_bounded_persistence(self):
        item = sample()
        for data in (b'{"a":1,"a":2}', b'{"x":NaN}', b'{' + b' '*audit.MAX_BYTES + b'}'):
            with self.assertRaises(Refusal): audit.strict_json(data)
        with TemporaryDirectory() as parent, patch.object(audit, 'assemble_record', return_value=item):
            recorder = audit.AngularAudit(parent, BINDING)
            receipt = recorder()
            data = (Path(parent)/'angular_audit.json').read_bytes()
            self.assertEqual(receipt['bytes'], len(data))
            self.assertEqual(audit.strict_json(data), item)
            with self.assertRaises(FileExistsError): recorder()

    def test_worker_writes_sidecar_on_existing_physical_incomplete_path(self):
        item = sample()
        with TemporaryDirectory() as parent:
            directory = Path(parent)
            manifest = directory/'manifest.json'
            manifest.write_text('{}')
            tracker = NS(arm=lambda *a: None, mark=lambda *a: None)
            def fake_run(_modules, _manifest, **kwargs):
                self.assertIsInstance(kwargs['angular_evidence'], audit.AngularAudit)
                with patch.object(audit, 'assemble_record', return_value=item):
                    kwargs['angular_evidence']()
                return dict(report=dict(numerical_accepted=False))
            with (patch.object(worker, 'read_limited', side_effect=[{}, {'owner':'daisy'}]),
                  patch.object(worker, 'strict_json_bytes', return_value=expected()),
                  patch.object(worker, 'validate_manifest'),
                  patch.object(worker, 'validate_reservation'),
                  patch.object(worker, 'verify_source', return_value=BINDING),
                  patch.object(worker, '_cgroup_path', return_value='/test'),
                  patch.object(worker, 'held'), patch.object(worker, 'completed'),
                  patch.object(worker, 'load_pinned_modules', return_value=({}, {}, {})),
                  patch.object(worker, 'run_manufactured', side_effect=fake_run),
                  patch.dict('os.environ', {key:'1' for key in
                    ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')})):
                self.assertEqual(worker.main([str(directory), str(manifest)], tracker=tracker), 0)
            self.assertFalse(json.loads((directory/'numerical.json').read_text())['report']['numerical_accepted'])
            self.assertEqual(audit.strict_json((directory/'angular_audit.json').read_bytes()), item)


if __name__ == '__main__':
    unittest.main()
