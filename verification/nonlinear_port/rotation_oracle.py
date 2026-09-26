"""Prospective exact-field rotation assembly oracle; no FEM imports or launch path.

The injected form builder supplies expressions only. A later, separately
admitted worker must assemble them and own all resource and exit decisions.
"""
import json
from fractions import Fraction
from math import isfinite, sqrt

from .cube_adapter import exact_data
from .prototype import Refusal


_BASE_TARGETS = {
    'volume': '1',
    'velocity_l2_squared': '1/6',
    'gradient_l2_squared': '2',
    'pressure_mean': '0',
    'pressure_l2_squared': '1/360',
    'convection_l2_squared': '1/6',
    'pressure_gradient_l2_squared': '1/6',
    'strain_l2_squared': '0',
    'divergence_l2_squared': '0',
    'momentum_residual_l2_squared': '0',
    'viscous_stress_l2_squared': '0',
    'viscous_traction_boundary_l2_squared': '0',
    'total_traction_boundary_l2_squared': '7/180',
    'viscous_dissipation': '0',
}
_TARGETS = dict(_BASE_TARGETS)
for _axis in range(3):
    for _side in (0, 1):
        _tag = 1 + 2*_axis + _side
        _TARGETS[f'area_{_tag}'] = '1'
        for _component in range(3):
            _TARGETS[f'normal_{_tag}_{_component}'] = (
                str(2*_side-1) if _component == _axis else '0')
assert len(_TARGETS) == 38

_ZERO_NORM_ORDER = (
    'strain_l2_squared', 'divergence_l2_squared',
    'momentum_residual_l2_squared', 'viscous_stress_l2_squared',
    'viscous_traction_boundary_l2_squared',
)
_ZERO_NORMS = frozenset(_ZERO_NORM_ORDER)
_GEOMETRY_ORDER = ('volume',
                   *(f'area_{tag}' for tag in range(1, 7)),
                   *(f'normal_{tag}_{component}'
                     for tag in range(1, 7) for component in range(3)))
_GEOMETRY = frozenset(_GEOMETRY_ORDER)
_NONNEGATIVE = frozenset({key for key in _TARGETS
                          if key.endswith('_squared') or key.startswith('area_')
                          or key in ('volume', 'viscous_dissipation')})


def contract_record():
    """Complete JSON-native numerical context; independent of the proposal file."""
    return dict(schema=1, name='rotation_assembly_v1', fixture='rotation',
                mode='exact_field_assembly', domain='affine unit cube',
                subdivisions=2, rho=1.0, mu=0.1, degrees=[24, 26],
                field_representation='exact coordinate expressions; no P1 pressure interpolation or PDE solve',
                raw_targets_rational=dict(_TARGETS),
                geometry_keys=list(_GEOMETRY_ORDER),
                nonnegative_keys=sorted(_NONNEGATIVE),
                zero_norm_squared_keys=list(_ZERO_NORM_ORDER),
                geometry_absolute_tolerance=1e-12,
                scalar_absolute_tolerance=1e-10,
                zero_norm_tolerance=1e-10,
                zero_norm_squared_tolerance=1e-20,
                pair_absolute_tolerance=1e-10)


def _json(value):
    def require_json_native(item):
        if type(item) is dict:
            if any(type(key) is not str for key in item):
                raise Refusal('rotation record needs string keys')
            for member in item.values():
                require_json_native(member)
        elif type(item) is list:
            for member in item:
                require_json_native(member)
        elif type(item) not in (str, int, float, bool, type(None)):
            raise Refusal('rotation record needs JSON-native values')
    require_json_native(value)
    try:
        # Canonical JSON distinguishes bool/int and int/float in nested records.
        return json.dumps(value, sort_keys=True, allow_nan=False,
                          separators=(',', ':'))
    except (TypeError, ValueError) as exc:
        raise Refusal('rotation contract/report is not finite JSON') from exc


def validate_contract(value):
    if type(value) is not dict or _json(value) != _json(contract_record()):
        raise Refusal('missing or changed rotation contract')
    return value


def rotation_forms(U, domain, tags, degree):
    """Build 38 scalar forms from exact coordinate fields, using injected UFL.

    ``tags`` is the reviewed six-face MeshTags object. This function does not
    create a mesh, compile a form or set an execution/admission result.
    """
    if domain is None or tags is None or type(degree) is not int or degree not in (24, 26):
        raise Refusal('rotation requires domain, six-face tags and degree 24/26')
    dx = U.Measure('dx', domain=domain, metadata={'quadrature_degree': degree})
    ds = U.Measure('ds', domain=domain, subdomain_data=tags,
                   metadata={'quadrature_degree': degree})
    exact = exact_data(U, domain, 'rotation', 0.0)
    u, p = exact['u'], exact['p']
    normal = U.FacetNormal(domain)
    gradient = U.grad(u)
    strain = U.sym(gradient)
    viscous_stress = 0.2*strain       # 2*mu*D, mu=0.1
    stress = viscous_stress + U.Identity(3)*(-p)
    convection = U.div(U.outer(u, u))
    pressure_gradient = U.grad(p)
    momentum_residual = convection + pressure_gradient-U.div(viscous_stress)
    viscous_traction = U.dot(viscous_stress, normal)
    traction = U.dot(stress, normal)
    forms = {
        'volume': 1*dx,
        'velocity_l2_squared': U.inner(u, u)*dx,
        'gradient_l2_squared': U.inner(gradient, gradient)*dx,
        'pressure_mean': p*dx,
        'pressure_l2_squared': p*p*dx,
        'convection_l2_squared': U.inner(convection, convection)*dx,
        'pressure_gradient_l2_squared': U.inner(pressure_gradient, pressure_gradient)*dx,
        'strain_l2_squared': U.inner(strain, strain)*dx,
        'divergence_l2_squared': U.div(u)**2*dx,
        'momentum_residual_l2_squared': U.inner(momentum_residual, momentum_residual)*dx,
        'viscous_stress_l2_squared': U.inner(viscous_stress, viscous_stress)*dx,
        'viscous_traction_boundary_l2_squared': sum(
            U.inner(viscous_traction, viscous_traction)*ds(tag) for tag in range(1, 7)),
        'total_traction_boundary_l2_squared': sum(
            U.inner(traction, traction)*ds(tag) for tag in range(1, 7)),
        'viscous_dissipation': 0.2*U.inner(strain, strain)*dx,
    }
    for tag in range(1, 7):
        forms[f'area_{tag}'] = 1*ds(tag)
        for component in range(3):
            forms[f'normal_{tag}_{component}'] = normal[component]*ds(tag)
    if set(forms) != set(_TARGETS):
        raise Refusal('rotation form inventory differs from contract')
    return forms


def _check_raw(raw):
    if type(raw) is not dict or set(raw) != set(_TARGETS):
        raise Refusal('incomplete rotation scalar inventory')
    for key, value in raw.items():
        if type(value) not in (int, float) or not isfinite(value):
            raise Refusal('nonfinite or non-native rotation scalar')
        if key in _NONNEGATIVE and value < 0:
            raise Refusal('negative rotation norm, geometry or dissipation')


def build_report(raw_by_degree, contract):
    """Compute numerical decisions only; never claims supervised execution PASS."""
    validate_contract(contract)
    if type(raw_by_degree) is not dict or set(raw_by_degree) != {'24', '26'}:
        raise Refusal('rotation needs degree 24 and 26 raw records')
    for raw in raw_by_degree.values():
        _check_raw(raw)
    targets = {key: float(Fraction(value)) for key, value in _TARGETS.items()}
    degree_checks = {}
    for degree in ('24', '26'):
        raw = raw_by_degree[degree]
        checks = {}
        for key, expected in targets.items():
            limit = (1e-12 if key in _GEOMETRY else
                     1e-20 if key in _ZERO_NORMS else 1e-10)
            difference = raw[key]-expected
            checks[key] = dict(expected=expected, difference=difference,
                               limit=limit, accepted=abs(difference) <= limit)
        degree_checks[degree] = dict(target_checks=checks,
                                     derived_zero_norms={key: sqrt(raw[key])
                                                         for key in sorted(_ZERO_NORMS)},
                                     accepted=all(item['accepted'] for item in checks.values()))
    pair_checks = {key: dict(difference=raw_by_degree['26'][key]-raw_by_degree['24'][key],
                             limit=1e-10,
                             accepted=abs(raw_by_degree['26'][key]-raw_by_degree['24'][key]) <= 1e-10)
                   for key in _TARGETS}
    accepted = all(entry['accepted'] for entry in degree_checks.values()) and all(
        entry['accepted'] for entry in pair_checks.values())
    report = dict(schema=1, contract=contract_record(), raw_by_degree=raw_by_degree,
                  degree_checks=degree_checks, pair_checks=pair_checks,
                  numerical_accepted=accepted)
    if len(_json(report).encode()) > 2_000_000:
        raise Refusal('oversized rotation report')
    return report


def validate_report(report, contract):
    """Recompute every cached decision from raw scalars and exact contract."""
    validate_contract(contract)
    if type(report) is not dict or set(report) != {
            'schema', 'contract', 'raw_by_degree', 'degree_checks',
            'pair_checks', 'numerical_accepted'}:
        raise Refusal('incomplete rotation report')
    expected = build_report(report['raw_by_degree'], contract)
    if (_json(report) != _json(expected)
            or report['numerical_accepted'] is not True
            or expected['numerical_accepted'] is not True):
        raise Refusal('failed or inconsistent rotation evidence')
    return report
