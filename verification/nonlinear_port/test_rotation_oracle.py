"""Source-only rotation contract and injected form wiring; no FEM imports."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import unittest

from .prototype import Refusal
from .rotation_oracle import (build_report, contract_record, rotation_forms,
                              validate_contract, validate_report)


ROOT = Path(__file__).resolve().parents[2]
PROPOSAL = json.loads((ROOT/'docs/realizability/evidence/r247/rotation_proposal.json').read_text())


def raw():
    return {key: float(Fraction(value)) for key, value in
            PROPOSAL['raw_targets_rational'].items()}


def pair():
    return {'24': raw(), '26': raw()}


class Expr:
    def __init__(self, value):
        self.value = str(value)

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def binary(self, operation, other):
        return Expr(f'({self}{operation}{other})')

    def __add__(self, other): return self.binary('+', other)
    def __radd__(self, other): return Expr(other).binary('+', self)
    def __sub__(self, other): return self.binary('-', other)
    def __rsub__(self, other): return Expr(other).binary('-', self)
    def __mul__(self, other): return self.binary('*', other)
    def __rmul__(self, other): return Expr(other).binary('*', self)
    def __pow__(self, other): return self.binary('**', other)
    def __neg__(self): return Expr(f'(-{self})')
    def __getitem__(self, index): return Expr(f'{self}[{index}]')
    def __call__(self, tag): return Expr(f'{self}({tag})')


class FakeU:
    @staticmethod
    def SpatialCoordinate(domain):
        assert domain == 'cube'
        return [Expr(name) for name in ('x', 'y', 'z')]

    @staticmethod
    def as_vector(components):
        return Expr('vector('+','.join(map(str, components))+')')

    @staticmethod
    def FacetNormal(domain):
        assert domain == 'cube'
        return Expr('normal')

    @staticmethod
    def Measure(kind, *, domain, subdomain_data=None, metadata):
        assert domain == 'cube' and metadata['quadrature_degree'] in (24, 26)
        assert (kind == 'dx' and subdomain_data is None
                or kind == 'ds' and subdomain_data == 'six-face-tags')
        return Expr(kind+str(metadata['quadrature_degree']))

    @staticmethod
    def Identity(size):
        assert size == 3
        return Expr('I')

    @staticmethod
    def grad(value): return Expr(f'grad({value})')
    @staticmethod
    def sym(value): return Expr(f'sym({value})')
    @staticmethod
    def div(value): return Expr(f'div({value})')
    @staticmethod
    def outer(left, right): return Expr(f'outer({left},{right})')
    @staticmethod
    def inner(left, right): return Expr(f'inner({left},{right})')
    @staticmethod
    def dot(left, right): return Expr(f'dot({left},{right})')


class RotationOracleTests(unittest.TestCase):
    def setUp(self):
        self.contract = contract_record()

    def assertRefuses(self, f):
        with self.assertRaises(Refusal):
            f()

    def test_contract_matches_independent_proposal(self):
        for key, value in self.contract.items():
            self.assertEqual(value, PROPOSAL[key], key)
        self.assertEqual(len(self.contract['raw_targets_rational']), 38)
        self.assertEqual(validate_contract(self.contract), self.contract)

    def test_exact_targets_pass_at_both_degrees(self):
        report = build_report(pair(), self.contract)
        self.assertTrue(report['numerical_accepted'])
        self.assertIs(validate_report(report, self.contract), report)
        self.assertEqual(len(report['pair_checks']), 38)
        self.assertEqual(set(report), set(PROPOSAL['required_report_fields']))
        self.assertTrue(all(value == 0 for degree in report['degree_checks'].values()
                            for value in degree['derived_zero_norms'].values()))

    def test_common_mode_wrong_values_refuse(self):
        for key, value in [('pressure_l2_squared', 0.0),
                           ('convection_l2_squared', 0.0),
                           ('gradient_l2_squared', 0.0),
                           ('total_traction_boundary_l2_squared', 0.0),
                           ('momentum_residual_l2_squared', 1/6),
                           ('viscous_stress_l2_squared', 1/50),
                           ('viscous_traction_boundary_l2_squared', 1/25),
                           ('viscous_dissipation', 1/5)]:
            with self.subTest(key=key):
                values = pair()
                values['24'][key] = values['26'][key] = value
                report = build_report(values, self.contract)
                self.assertFalse(report['numerical_accepted'])
                self.assertTrue(report['pair_checks'][key]['accepted'])
                self.assertRefuses(lambda: validate_report(report, self.contract))

    def test_one_degree_failure_and_pair_gate(self):
        values = pair()
        values['26']['pressure_gradient_l2_squared'] += 2e-10
        report = build_report(values, self.contract)
        self.assertTrue(report['degree_checks']['24']['accepted'])
        self.assertFalse(report['degree_checks']['26']['accepted'])
        self.assertFalse(report['pair_checks']['pressure_gradient_l2_squared']['accepted'])
        self.assertRefuses(lambda: validate_report(report, self.contract))
        values = pair()
        values['24']['pressure_mean'] = -0.75e-10
        values['26']['pressure_mean'] = 0.75e-10
        report = build_report(values, self.contract)
        self.assertTrue(all(x['accepted'] for x in report['degree_checks'].values()))
        self.assertFalse(report['pair_checks']['pressure_mean']['accepted'])

    def test_geometry_tags_and_side_faces(self):
        for key in ('area_1', 'normal_2_0', 'normal_4_1', 'normal_6_2'):
            with self.subTest(key=key):
                values = pair()
                values['24'][key] += 2e-12
                self.assertFalse(build_report(values, self.contract)['numerical_accepted'])

    def test_missing_extra_nonfinite_bool_and_negative_raw_refuse(self):
        values = pair()
        del values['24']['volume']
        self.assertRefuses(lambda: build_report(values, self.contract))
        values = pair()
        values['26']['unknown'] = 0.0
        self.assertRefuses(lambda: build_report(values, self.contract))
        for bad in (float('nan'), float('inf'), True, None, '0'):
            with self.subTest(bad=bad):
                values = pair()
                values['24']['pressure_mean'] = bad
                self.assertRefuses(lambda: build_report(values, self.contract))
        values = pair()
        values['24']['strain_l2_squared'] = -1e-30
        self.assertRefuses(lambda: build_report(values, self.contract))
        values = pair()
        values['24']['volume'] = -1
        self.assertRefuses(lambda: build_report(values, self.contract))
        for degrees in ({24: raw(), 26: raw()}, {'24': raw()}):
            self.assertRefuses(lambda: build_report(degrees, self.contract))

    def test_contract_drift_and_cached_decisions_refuse(self):
        for field, altered in [('schema', True), ('degrees', [24]),
                               ('fixture', 'poiseuille'), ('rho', 1),
                               ('raw_targets_rational', {}), ('degrees', (24, 26))]:
            with self.subTest(field=field):
                bad = copy.deepcopy(self.contract)
                bad[field] = altered
                self.assertRefuses(lambda: validate_contract(bad))
                self.assertRefuses(lambda: build_report(pair(), bad))
        report = build_report(pair(), self.contract)
        mutations = []
        bad = copy.deepcopy(report); bad['schema'] = True; mutations.append(bad)
        bad = copy.deepcopy(report); bad['numerical_accepted'] = 1; mutations.append(bad)
        bad = copy.deepcopy(report); bad['contract']['fixture'] = 'poiseuille'; mutations.append(bad)
        bad = copy.deepcopy(report); bad['degree_checks']['26']['target_checks']['volume']['accepted'] = False; mutations.append(bad)
        bad = copy.deepcopy(report); bad['degree_checks']['24']['derived_zero_norms']['strain_l2_squared'] = 1e-8; mutations.append(bad)
        bad = copy.deepcopy(report); del bad['pair_checks']['area_1']; mutations.append(bad)
        bad = copy.deepcopy(report); del bad['raw_by_degree']['26']; mutations.append(bad)
        bad = copy.deepcopy(report); bad['extra'] = 0; mutations.append(bad)
        for bad in mutations:
            self.assertRefuses(lambda bad=bad: validate_report(bad, self.contract))

    def test_form_builder_has_actual_derivatives_and_all_faces(self):
        forms = rotation_forms(FakeU, 'cube', 'six-face-tags', 24)
        self.assertEqual(set(forms), set(self.contract['raw_targets_rational']))
        residual = str(forms['momentum_residual_l2_squared'])
        self.assertIn('div(outer(', residual)
        self.assertIn(')+grad(', residual)
        self.assertIn('div((0.2*sym(grad(', residual)
        self.assertIn('**2', str(forms['divergence_l2_squared']))
        self.assertIn('sym(grad(', str(forms['viscous_dissipation']))
        self.assertIn('I*(-', str(forms['total_traction_boundary_l2_squared']))
        for key in ('viscous_traction_boundary_l2_squared',
                    'total_traction_boundary_l2_squared'):
            self.assertIn('normal', str(forms[key]))
            for tag in range(1, 7):
                self.assertIn(f'ds24({tag})', str(forms[key]))
        self.assertIn('normal[0]', str(forms['normal_1_0']))
        self.assertIn('ds24(1)', str(forms['normal_1_0']))
        forms26 = rotation_forms(FakeU, 'cube', 'six-face-tags', 26)
        self.assertIn('ds26(6)', str(forms26['total_traction_boundary_l2_squared']))
        for degree in (True, 23):
            self.assertRefuses(lambda: rotation_forms(FakeU, 'cube', 'six-face-tags', degree))
        self.assertRefuses(lambda: rotation_forms(FakeU, None, 'six-face-tags', 24))


if __name__ == '__main__':
    unittest.main()
