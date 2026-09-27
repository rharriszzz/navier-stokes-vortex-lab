"""Final-state angular evidence, assembled with injected FEM modules only.

The sidecar explains a failed physical budget; it never changes that decision.
No numerical package is imported by this module.
"""
import json
from math import fsum, isfinite
import os
from pathlib import Path
import re
from sys import float_info

from .prototype import Refusal


MAX_BYTES = 262144
DEGREES = ('24', '26')
LATERAL = (1, 2, 3, 4)
RETURNS = (5, 6)
SCALARS = ('A_D', 'A_R', 'C_D', 'C_R', 'G_R', 'residual_action')
EXPECTED_INTEGRALS = {
    'A_D': [('exterior_facet', tag) for tag in LATERAL],
    'A_R': [('exterior_facet', tag) for tag in RETURNS],
    'C_D': [('exterior_facet', tag) for tag in LATERAL],
    'C_R': [('exterior_facet', tag) for tag in RETURNS],
    'G_R': [('exterior_facet', tag) for tag in RETURNS],
    'residual_action': [('cell', 'everywhere'),
                        *[('exterior_facet', tag) for tag in RETURNS]],
    'raw_residual': [('cell', 'everywhere'),
                     *[('exterior_facet', tag) for tag in RETURNS]],
}


def _number(value, name):
    if type(value) not in (int, float):
        raise Refusal('invalid angular evidence number: ' + name)
    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise Refusal('invalid angular evidence number: ' + name) from exc
    if not isfinite(number):
        raise Refusal('invalid angular evidence number: ' + name)
    return number


def _vector(values, count, name):
    if type(values) is not list or len(values) != count:
        raise Refusal('invalid angular evidence vector: ' + name)
    return [_number(value, name) for value in values]


def _keys(value, names, name):
    if type(value) is not dict or set(value) != set(names):
        raise Refusal('invalid angular evidence keys: ' + name)


def _same_typed(value, expected):
    if type(value) is not type(expected):
        return False
    if type(value) is dict:
        return value.keys() == expected.keys() and all(
            _same_typed(value[key], expected[key]) for key in expected)
    if type(value) is list:
        return len(value) == len(expected) and all(
            _same_typed(a, b) for a, b in zip(value, expected))
    return value == expected


def _receipt(form, U, domain, tags, name, rank):
    if not isinstance(form, U.Form) or len(form.arguments()) != rank:
        raise Refusal('angular evidence form rank: ' + name)
    if tuple(form.ufl_domains()) != (domain.ufl_domain(),):
        raise Refusal('angular evidence form domain: ' + name)
    integrals = []
    for item in form.integrals():
        kind, tag = item.integral_type(), item.subdomain_id()
        if kind == 'exterior_facet' and item.subdomain_data() is not tags:
            raise Refusal('angular evidence lost face tags: ' + name)
        integrals.append((kind, tag))
    if sorted(integrals, key=str) != sorted(EXPECTED_INTEGRALS[name], key=str):
        raise Refusal('angular evidence form inventory: ' + name)
    return dict(method='fem.form+assemble_scalar' if rank == 0 else
                'fem_petsc.assemble_vector+ghost_reverse',
                compiled_rank=rank, integrals=[list(pair) for pair in integrals])


def _check_receipt(receipt, name, rank):
    _keys(receipt, ('method', 'compiled_rank', 'integrals'), name + '.receipt')
    method = 'fem.form+assemble_scalar' if rank == 0 else 'fem_petsc.assemble_vector+ghost_reverse'
    integrals = receipt['integrals']
    if (type(integrals) is not list or any(type(pair) is not list or len(pair) != 2 or
            type(pair[0]) is not str or type(pair[1]) not in (str, int)
            for pair in integrals)):
        raise Refusal('invalid angular evidence receipt: ' + name)
    if (receipt['method'] != method or type(receipt['compiled_rank']) is not int
            or receipt['compiled_rank'] != rank or
            sorted(integrals, key=str) !=
            sorted([list(pair) for pair in EXPECTED_INTEGRALS[name]], key=str)):
        raise Refusal('altered angular evidence receipt: ' + name)


def _identity(terms):
    terms = [_number(value, 'identity term') for value in terms]
    defect = fsum(terms)
    limit = max(1e-12, 128 * float_info.epsilon * fsum(abs(value) for value in terms))
    return dict(terms=terms, defect=defect, limit=limit,
                accepted=abs(defect) <= limit)


def _reductions(phi, residual, fixed, scalar, original):
    fixed_set = set(fixed)
    rd = fsum(phi[i] * residual[i] for i in sorted(fixed_set))
    rf = fsum(phi[i] * residual[i] for i in range(402) if i not in fixed_set)
    ad, ar, cd, cr, gr, action = (scalar[key] for key in SCALARS)
    reaction = fsum((rd, ad))
    lateral = fsum((reaction, cd))
    returned = fsum((cr, -gr))
    reconstructed = fsum((lateral, returned, rf))
    reduced = dict(R_D=rd, R_F=rf, reaction_torque_D=reaction,
                   lateral_mismatch=lateral, return_mismatch=returned,
                   reconstructed_defect=reconstructed)
    comparisons = dict(
        advection=_identity((ad, ar, -original['advective'])),
        traction=_identity((cd, cr, -original['traction'])),
        residual_vector_action=_identity((rd, rf, -action)),
        residual_scalar_action=_identity((action, -original['storage'],
                                          -original['body'], -ar, -gr)),
        physical_defect=_identity((reconstructed, -original['physical_defect'])))
    return reduced, comparisons


def install_final_constants(constants, state):
    """Install accepted P-/P+/eta in each degree's newly created Constants."""
    if len(constants) != 3 or len(state) != 405:
        raise Refusal('angular evidence final multiplier inventory')
    values = _vector(list(state[402:]), 3, 'final multipliers')
    for constant, value in zip(constants, values):
        constant.value = value


def validate_record(record, binding):
    """Reject malformed or altered cached evidence; retain measured mismatches."""
    _keys(record, ('schema', 'fixture', 'stage', 'source_binding', 'geometry',
                   'step', 'time', 'dt', 'state', 'fixed_indices', 'fixed_values',
                   'phi', 'degrees'), 'record')
    from .manufactured_driver import GEOMETRY
    if (type(record['schema']) is not int or record['schema'] != 1 or
            record['fixture'] != 'manufactured' or record['stage'] != 'final_accepted_state_after_newton' or
            not _same_typed(record['source_binding'], binding) or
            not _same_typed(record['geometry'], GEOMETRY) or
            type(record['step']) is not int or record['step'] != 1 or
            _number(record['time'], 'time') != .125 or _number(record['dt'], 'dt') != .125):
        raise Refusal('angular evidence identity/state mismatch')
    state = _vector(record['state'], 405, 'state')
    fixed = record['fixed_indices']
    if (type(fixed) is not list or len(fixed) != 240 or
            any(type(i) is not int or not 0 <= i < 402 for i in fixed) or
            fixed != sorted(set(fixed))):
        raise Refusal('angular evidence fixed indices')
    values = _vector(record['fixed_values'], len(fixed), 'fixed values')
    if any(state[i] != value for i, value in zip(fixed, values)):
        raise Refusal('angular evidence fixed trace alias')
    phi = record['phi']
    _keys(phi, ('coefficients', 'velocity_parent_map', 'pressure_parent_map',
                'velocity_node_coordinates', 'velocity_block_size'), 'phi')
    coefficients = _vector(phi['coefficients'], 402, 'phi')
    vm, pm = phi['velocity_parent_map'], phi['pressure_parent_map']
    if (type(vm) is not list or type(pm) is not list or
            len(vm) != 375 or len(pm) != 27 or
            any(type(i) is not int for i in vm + pm) or
            sorted(vm + pm) != list(range(402)) or
            type(phi['velocity_block_size']) is not int or phi['velocity_block_size'] != 3 or
            type(phi['velocity_node_coordinates']) is not list or
            len(phi['velocity_node_coordinates']) != 125):
        raise Refusal('angular evidence parent maps')
    coordinates = phi['velocity_node_coordinates']
    for j, coordinate in enumerate(coordinates):
        x, y, z = _vector(coordinate, 3, 'coordinate')
        for component, expected in enumerate((-y, x, 0.)):
            if abs(coefficients[vm[3*j+component]]-expected) > 1e-12:
                raise Refusal('angular evidence phi interpolation')
    if any(coefficients[i] != 0. for i in pm) or not set(fixed) <= set(vm):
        raise Refusal('angular evidence pressure/fixed map')
    _keys(record['degrees'], DEGREES, 'degrees')
    for degree in DEGREES:
        entry = record['degrees'][degree]
        _keys(entry, ('raw_residual', 'raw_receipt', 'scalar', 'scalar_receipts',
                      'original', 'multipliers', 'reductions', 'comparisons'), degree)
        residual = _vector(entry['raw_residual'], 402, degree + '.raw')
        _check_receipt(entry['raw_receipt'], 'raw_residual', 1)
        _keys(entry['scalar'], SCALARS, degree + '.scalar')
        scalar = {key: _number(value, key) for key, value in entry['scalar'].items()}
        _keys(entry['scalar_receipts'], SCALARS, degree + '.receipts')
        for key, receipt in entry['scalar_receipts'].items():
            _check_receipt(receipt, key, 0)
        _keys(entry['original'], ('storage', 'advective', 'traction', 'body',
                                  'physical_defect'), degree + '.original')
        original = {key: _number(value, key) for key, value in entry['original'].items()}
        if original['physical_defect'] != fsum(original[key] for key in
                                              ('storage', 'advective', 'traction', 'body')):
            raise Refusal('angular evidence original defect altered')
        if _vector(entry['multipliers'], 3, 'multipliers') != state[402:]:
            raise Refusal('angular evidence multiplier alias')
        reductions, comparisons = _reductions(coefficients, residual, fixed, scalar, original)
        if (not _same_typed(entry['reductions'], reductions) or
                not _same_typed(entry['comparisons'], comparisons)):
            raise Refusal('angular evidence cached reduction altered')
    return record


def validate_numerical_aliases(record, numerical, binding):
    """Cross-check a new sidecar without accepting/replacing the physical report.

    Historical numerical envelopes intentionally have no sidecar requirement.
    A separate diagnostic caller invokes this check even on physical refusal.
    """
    validate_record(record, binding)
    if not _same_typed(numerical['source_binding'], binding):
        raise Refusal('angular evidence numerical source alias')
    for key in ('geometry', 'step', 'time', 'dt'):
        if not _same_typed(record[key], numerical[key]):
            raise Refusal('angular evidence numerical alias: ' + key)
    fixed = {str(i): value for i, value in
             zip(record['fixed_indices'], record['fixed_values'])}
    _keys(numerical['fixed_inventory'], fixed, 'numerical fixed inventory')
    numerical_fixed = {key: _number(value, 'numerical fixed value')
                       for key, value in numerical['fixed_inventory'].items()}
    if (fixed != numerical_fixed or
            type(numerical['fixed_velocity_dofs']) is not int or
            numerical['fixed_velocity_dofs'] != len(fixed) or
            _vector(numerical['multipliers'], 2, 'numerical multipliers') +
            [_number(numerical['eta'], 'numerical eta')] != record['state'][402:]):
        raise Refusal('angular evidence numerical fixed/multiplier alias')
    for degree in DEGREES:
        for key in ('storage', 'advective', 'traction', 'body'):
            if record['degrees'][degree]['original'][key] != _number(
                    numerical['raw_by_degree'][degree]['angular.'+key], key):
                raise Refusal('angular evidence numerical physical-term alias')
    return record


def assemble_record(modules, domain, space, tags, w, state, fixed,
                    degree_inputs, raw_by_degree, geometry, binding):
    """Assemble final raw residuals and independent angular scalar actions."""
    U, fem, fp = (modules[key] for key in ('ufl', 'fem', 'fem_petsc'))
    velocity_space, velocity_map = space.sub(0).collapse()
    _pressure_space, pressure_map = space.sub(1).collapse()
    value = fem.Function(velocity_space)
    value.interpolate(lambda x: modules['np'].vstack((-x[1], x[0],
                                                       modules['np'].zeros(x.shape[1]))))
    phi = fem.Function(space)
    phi.x.array[:] = 0.
    phi.x.array[velocity_map] = value.x.array
    phi.x.scatter_forward()
    coords = velocity_space.tabulate_dof_coordinates().tolist()
    phi_record = dict(coefficients=phi.x.array.tolist(),
        velocity_parent_map=[int(i) for i in velocity_map],
        pressure_parent_map=[int(i) for i in pressure_map],
        velocity_node_coordinates=coords,
        velocity_block_size=int(velocity_space.dofmap.index_map_bs))
    result = dict(schema=1, fixture='manufactured',
        stage='final_accepted_state_after_newton', source_binding=dict(binding),
        geometry=geometry, step=1, time=.125, dt=.125,
        state=[float(v) for v in state], fixed_indices=sorted(fixed),
        fixed_values=[float(fixed[i]) for i in sorted(fixed)],
        phi=phi_record, degrees={})
    if _vector(w.x.array.tolist(), 402, 'installed state') != result['state'][:402]:
        raise Refusal('angular evidence state is not installed final field')
    u, p = U.split(w)
    x, n = U.SpatialCoordinate(domain), U.FacetNormal(domain)
    angular = lambda v: x[0]*v[1]-x[1]*v[0]
    stress = -p*U.Identity(3)+.2*U.sym(U.grad(u))
    traction = U.dot(stress, n)
    for degree in (24, 26):
        print(f'manufactured angular degree={degree} stage=begin', flush=True)
        forms, constants, context = degree_inputs[str(degree)]
        if context.get('history') is None or context.get('force') is None:
            raise Refusal('angular evidence requires exact BE history and corrected load')
        install_final_constants(constants, state)
        ds = context['ds']
        scalar_forms = dict(
            A_D=sum(angular(u)*U.dot(u, n)*ds(tag) for tag in LATERAL),
            A_R=sum(angular(u)*U.dot(u, n)*ds(tag) for tag in RETURNS),
            C_D=sum(-angular(traction)*ds(tag) for tag in LATERAL),
            C_R=sum(-angular(traction)*ds(tag) for tag in RETURNS),
            residual_action=U.action(forms['momentum_continuity'], phi))
        v, _q = U.split(phi)
        scalar_forms['G_R'] = sum((constants[tag-5]*U.dot(v, n) -
                                  U.dot(context['exact']['offsets'][tag-5], v))*ds(tag)
                                 for tag in RETURNS)
        scalar = {}
        receipts = {}
        for key in SCALARS:
            form = scalar_forms[key]
            receipts[key] = _receipt(form, U, domain, tags, key, 0)
            print(f'manufactured angular degree={degree} key={key} stage=assemble', flush=True)
            compiled = fem.form(form)
            if type(compiled.rank) is not int or compiled.rank != 0:
                raise Refusal('angular evidence scalar compiled rank')
            scalar[key] = _number(fem.assemble_scalar(compiled), key)
        residual_form = forms['momentum_continuity']
        raw_receipt = _receipt(residual_form, U, domain, tags, 'raw_residual', 1)
        print(f'manufactured angular degree={degree} key=raw_residual stage=assemble', flush=True)
        compiled = fem.form(residual_form)
        if type(compiled.rank) is not int or compiled.rank != 1:
            raise Refusal('angular evidence vector compiled rank')
        vector = fp.assemble_vector(compiled)
        try:
            vector.ghostUpdate(addv=modules['PETSc'].InsertMode.ADD_VALUES,
                               mode=modules['PETSc'].ScatterMode.REVERSE)
            residual = vector.getArray(readonly=True).tolist()
        finally:
            vector.destroy()
        raw = raw_by_degree[str(degree)]
        original = {key: float(raw['angular.'+key]) for key in
                    ('storage', 'advective', 'traction', 'body')}
        original['physical_defect'] = fsum(original.values())
        reductions, comparisons = _reductions(result['phi']['coefficients'],
                                               residual, fixed, scalar, original)
        result['degrees'][str(degree)] = dict(raw_residual=residual,
            raw_receipt=raw_receipt, scalar=scalar, scalar_receipts=receipts,
            original=original, multipliers=[float(v) for v in state[402:]],
            reductions=reductions, comparisons=comparisons)
        print(f'manufactured angular degree={degree} stage=end', flush=True)
    return validate_record(result, binding)


def _no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Refusal('duplicate angular evidence JSON key')
        result[key] = value
    return result


def strict_json(data):
    if len(data) > MAX_BYTES:
        raise Refusal('angular evidence byte cap')
    try:
        return json.loads(data, object_pairs_hook=_no_duplicates,
                          parse_constant=lambda value: (_ for _ in ()).throw(
                              Refusal('nonfinite angular evidence JSON')))
    except (UnicodeError, ValueError, TypeError, RecursionError) as exc:
        raise Refusal('invalid angular evidence JSON') from exc


class AngularAudit:
    """Exclusive finite sidecar writer bound to a reserved run and source."""
    def __init__(self, directory, binding):
        if type(binding) is not dict:
            raise Refusal('angular evidence requires source binding')
        self.directory = Path(directory)
        self.binding = dict(binding)
        commit = binding.get('source_commit')
        executable = binding.get('executable_sha256')
        if (not self.directory.is_dir() or
                type(commit) is not str or not re.fullmatch('[0-9a-f]{40}', commit) or
                type(executable) is not str or not re.fullmatch('[0-9a-f]{64}', executable)):
            raise Refusal('angular evidence requires reserved directory and source binding')

    def __call__(self, **inputs):
        record = assemble_record(binding=self.binding, **inputs)
        data = (json.dumps(record, sort_keys=True, separators=(',', ':'),
                           allow_nan=False)+'\n').encode('utf-8')
        if len(data) > MAX_BYTES:
            raise Refusal('angular evidence byte cap')
        validate_record(strict_json(data), self.binding)
        path = self.directory/'angular_audit.json'
        with path.open('xb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        return dict(file=path.name, bytes=len(data))
