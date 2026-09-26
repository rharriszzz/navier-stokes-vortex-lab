"""R244 explicit accuracy policy for one frozen Poiseuille oracle.

The signed floor is an accuracy budget, not a bound on floating-point error.
The legacy general comparator remains unchanged. No execution is admitted here.
"""
import json

from .diagnostics import ANGULAR_TERMS, ENERGY_TERMS, finite, quadrature_comparison
from .prototype import Refusal


SIGNED_KEYS = frozenset(
    {'angular.'+key for key in ANGULAR_TERMS}
    | {'energy.'+key for key in ENERGY_TERMS if key != 'dissipation'}
    | {'energy_identity_storage', 'kinetic_discrete_derivative', 'lateral_flux',
       'flux_0', 'flux_1', 'pressure_mean', 'p_error_integral'})
OTHER_KEYS = frozenset({
    'u_L2_squared', 'u_H1_seminorm_squared', 'p_error_squared',
    'div_u_L2_squared', 'traction_L2_returns_squared', 'energy_identity_dissipation',
    'energy.dissipation', 'kinetic_energy', 'angular_momentum',
    'volume', 'area_0', 'area_1', 'boundary_absolute_flux'})
RAW_KEYS = SIGNED_KEYS | OTHER_KEYS
NONNEGATIVE_KEYS = OTHER_KEYS - {'angular_momentum'}
DOMAIN = 'affine unit cube; lateral Dirichlet; z=0 and z=1 independent flux returns'


def policy_record():
    """Fresh JSON record; callers cannot mutate module policy through it."""
    return dict(schema=1, name='poiseuille_signed_accuracy_v1',
                fixture='poiseuille', subdivisions=2, step=1, dt=.125,
                rho=1., mu=.1, domain=DOMAIN, nondimensional=True,
                degrees=[24, 26], backflow_sampling_degree=24,
                relative=1e-8, scale_floor=1e-10, signed_absolute_floor=1e-14,
                signed_keys=sorted(SIGNED_KEYS), raw_keys=sorted(RAW_KEYS))


def validate_policy(record):
    # Canonical JSON also distinguishes true/1 and 1.0/1 in version fields.
    try:
        actual = json.dumps(record, sort_keys=True, allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise Refusal('invalid Poiseuille diagnostic policy') from exc
    if actual != json.dumps(policy_record(), sort_keys=True):
        raise Refusal('missing or changed Poiseuille diagnostic policy')


def validate_manifest_policy(manifest):
    validate_policy(manifest.get('poiseuille_diagnostic_policy'))
    if (type(manifest.get('rho')) not in (float, int) or manifest['rho'] != 1.
            or type(manifest.get('mu')) not in (float, int) or manifest['mu'] != .1
            or manifest.get('domain') != DOMAIN
            or manifest.get('spatial', {}).get('dt') != .125
            or manifest.get('spatial', {}).get('steps_per_mesh') != 1
            or manifest.get('oracles', {}).get('poiseuille', {}).get('subdivisions') != 2
            or manifest.get('gates', {}).get('quadrature_relative_change') != 1e-8):
        raise Refusal('Poiseuille diagnostic policy fixture binding changed')


def compare(base, check, policy):
    validate_policy(policy)
    for values in (base, check):
        if not isinstance(values, dict) or set(values) != RAW_KEYS:
            raise Refusal('incomplete or unknown Poiseuille diagnostic inventory')
        finite(values.values())
        if any(values[key] < 0 for key in NONNEGATIVE_KEYS):
            raise Refusal('negative Poiseuille nonnegative diagnostic')
    result = quadrature_comparison(base, check, relative=1e-8, floor=1e-10)
    for key in SIGNED_KEYS:
        item = result[key]
        item['limit'] = max(item['limit'], 1e-14)
        item['accepted'] = abs(item['difference']) <= item['limit']
    return result
