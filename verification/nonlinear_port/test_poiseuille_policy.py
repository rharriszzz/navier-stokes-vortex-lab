"""Policy/dual-degree negative controls; stdlib saved-data only, no FEM."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from .diagnostics import quadrature_comparison
from .fixture_driver import evaluate_poiseuille_pair
from .manifest import validate as validate_manifest
from .poiseuille_policy import compare, policy_record, RAW_KEYS, SIGNED_KEYS
from .prototype import Refusal
from .supervision import validate_worker_result, MAX_REPORT_BYTES
from .test_driver_supervision import CONTRACT, payload


def rebuild(p, base, check):
    p.update(evaluate_poiseuille_pair(
        base, check, p['multipliers'], p['eta'], p['nonlinear_history'],
        p['linear_corrections'], [p['minimum_return_normal_velocity']],
        CONTRACT['gates'], CONTRACT['poiseuille_diagnostic_policy'], p['dt']))
    return p


def validate(p):
    return validate_worker_result(p, CONTRACT['versions'], CONTRACT['gates'],
                                  policy=CONTRACT['poiseuille_diagnostic_policy'])


class PoiseuillePolicy(unittest.TestCase):
    def test_legacy_and_quantity_specific_thresholds(self):
        self.assertFalse(quadrature_comparison({'x': 0.}, {'x': 1e-15})['x']['accepted'])
        base = payload()['diagnostics_degree24']['raw']
        self.assertEqual(len(RAW_KEYS), 30)
        self.assertEqual(len(SIGNED_KEYS), 17)
        for key, value, expected in (
                ('pressure_mean', 1e-15, True), ('pressure_mean', 2e-14, False),
                ('u_L2_squared', 1e-16, False), ('energy_identity_dissipation', 1e-16, False),
                ('energy.dissipation', 1e-16, False), ('kinetic_energy', 1., False)):
            with self.subTest(key=key, value=value):
                result = compare(base, dict(base, **{key: value}), policy_record())
                self.assertIs(result[key]['accepted'], expected)

    def test_inventory_nonfinite_negative_and_bool_refuse(self):
        base = payload()['diagnostics_degree24']['raw']
        bads = [dict(base, unknown=0.), {k: v for k, v in base.items() if k != 'flux_1'},
                dict(base, pressure_mean=float('nan')), dict(base, pressure_mean=float('inf')),
                dict(base, pressure_mean=True), dict(base, u_L2_squared=-1e-30),
                dict(base, energy_identity_dissipation=-1e-30)]
        for bad in bads:
            for a, b in ((bad, base), (base, bad)):
                with self.subTest(bad=bad), self.assertRaises(Refusal):
                    compare(a, b, policy_record())

    def test_policy_and_fixture_cannot_default_or_drift(self):
        base = payload()['diagnostics_degree24']['raw']
        for policy in (None, {}, dict(policy_record(), schema=True),
                       dict(policy_record(), signed_absolute_floor=1e-10),
                       dict(policy_record(), fixture='rotation')):
            with self.subTest(policy=policy), self.assertRaises(Refusal):
                compare(base, base, policy)
        validate_manifest(CONTRACT)
        for edit in (lambda p: p.pop('poiseuille_diagnostic_policy'),
                     lambda p: p.__setitem__('rho', 2.),
                     lambda p: p.__setitem__('mu', .2),
                     lambda p: p.__setitem__('domain', 'curved cube'),
                     lambda p: p['spatial'].__setitem__('dt', .25),
                     lambda p: p['spatial'].__setitem__('steps_per_mesh', 2),
                     lambda p: p['oracles']['poiseuille'].__setitem__('subdivisions', 4)):
            manifest = deepcopy(CONTRACT)
            edit(manifest)
            with self.assertRaises(Refusal):
                validate_manifest(manifest)
        with self.assertRaises(Refusal):
            validate_worker_result(payload(), CONTRACT['versions'], CONTRACT['gates'])

    def test_common_mode_wrong_answers_fail_physical_gates(self):
        for key, value in (('pressure_mean', 1e-6), ('u_L2_squared', 1e-16)):
            p = payload()
            raw = dict(p['diagnostics_degree24']['raw'], **{key: value})
            rebuild(p, raw, dict(raw))
            self.assertTrue(p['checks']['quadrature_24_26'])
            self.assertFalse(p['numerical_accepted'])
            with self.assertRaises(Refusal):
                validate(p)

    def test_degree26_physical_failure_even_when_pair_agrees(self):
        p = payload()
        base = dict(p['diagnostics_degree24']['raw'], pressure_mean=1e-10-2e-15)
        check = dict(base, pressure_mean=1e-10+2e-15)
        rebuild(p, base, check)
        self.assertTrue(p['checks']['quadrature_24_26'])
        self.assertTrue(p['degree_validation']['24']['numerical_accepted'])
        self.assertFalse(p['degree_validation']['26']['numerical_accepted'])
        with self.assertRaises(Refusal):
            validate(p)
        # Forged caches cannot override the bad degree-26 raw pressure mean.
        good = payload()
        for key in ('checks', 'numerical_accepted', 'degree_validation'):
            p[key] = good[key]
        with self.assertRaises(Refusal):
            validate(p)

    def test_report_schema_missing_or_corrupted_caches_refuse(self):
        validate(payload())
        changes = [lambda p: p.pop('diagnostic_policy'),
                   lambda p: p.pop('degree_validation'),
                   lambda p: p.__setitem__('numerical_schema', 1),
                   lambda p: p.__setitem__('numerical_schema', True),
                   lambda p: p.__setitem__('backflow_sampling_degree', 26),
                   lambda p: p['degree_validation'].pop('26'),
                   lambda p: p['degree_validation']['26']['field_report'].__setitem__('u_L2', 2.),
                   lambda p: p['degree_validation']['26']['checks'].__setitem__('divergence', False),
                   lambda p: p['degree_validation']['26']['physical_endpoint_budgets']['energy']['physical'].__setitem__('signed_defect', 1.)]
        for change in changes:
            bad = deepcopy(payload())
            change(bad)
            with self.subTest(change=change), self.assertRaises(Refusal):
                validate(bad)

    def test_saved_r242_legacy_refusal_and_explicit_prospective_replay(self):
        path = Path(__file__).resolve().parents[2]/'docs/realizability/evidence/r242/run/numerical.json'
        original = path.read_bytes()
        p = json.loads(original)
        old = quadrature_comparison(p['diagnostics_degree24']['raw'], p['diagnostics_degree26'])
        self.assertEqual(old, p['quadrature_comparison'])
        self.assertEqual(sum(not item['accepted'] for item in old.values()), 12)
        with self.assertRaises(Refusal):
            validate(p)  # absent policy/schema cannot select the new method
        projected = rebuild(deepcopy(p), p['diagnostics_degree24']['raw'], p['diagnostics_degree26'])
        self.assertTrue(projected['numerical_accepted'])
        validate(projected)
        encoded = json.dumps(projected, allow_nan=False).encode()
        self.assertLess(len(encoded), MAX_REPORT_BYTES)
        self.assertEqual(path.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
