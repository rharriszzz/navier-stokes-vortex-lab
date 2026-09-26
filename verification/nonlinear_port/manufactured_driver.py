"""Injected n=2 manufactured BE driver and strict saved envelope checks."""
import hashlib
import json
from math import fsum, isfinite, sqrt
from pathlib import Path
import time

from .cube_adapter import (Assembler, RETURNS, SUPERLU_OPTIONS, SUPERLU_PREFIX, boundary_values, create_cube,
                           interpolate_state, sparse_solve, step_forms)
from .diagnostics import field_forms
from .fixture_driver import nonexact_guess, return_quadrature_samples
from .manufactured_manifest import canonical, contract_digest, validate as validate_manifest
from .manufactured_report import build_report, validate_report
from .package_identity import validate_versions
from .prototype import Refusal, newton
from .rotation_driver import (_duplicate_pairs, _nonfinite_constant,
                              geometry_receipt, read_limited, strict_json_bytes,
                              write_limited_new)
from .source_binding import expected_binding
from .sparse import CSR, constraint_condition, row_scales, scale_system


PHASES = {'mesh_and_lift', 'primary_form_setup_jit',
          'compatibility_rank_newton', 'diagnostic_form_jit_assembly_sampling'}
INTERVALS = {'import_seconds', 'fixture_setup_jit_and_solve_seconds'}
ENVELOPE_KEYS = {'worker_schema', 'fixture', 'kind', 'mode', 'manifest_sha256',
    'contract_sha256', 'source_binding', 'geometry', 'subdivisions', 'step',
    'time', 'dt', 'history_semantics', 'load_semantics', 'mixed_dofs',
    'global_dofs', 'fixed_velocity_dofs', 'fixed_inventory',
    'perturbed_velocity_dof', 'perturbation', 'multipliers', 'eta',
    'constraint_condition',
    'compatibility', 'measured_targets', 'lateral_absolute_flux',
    'frozen_row_scales',
    'nonlinear_history', 'linear_corrections', 'raw_by_degree',
    'assembly_receipts', 'backflow_sampling_degree',
    'return_quadrature_sample_counts',
    'minimum_return_normal_velocity', 'report', 'phase_seconds',
    'worker_intervals', 'actual_versions', 'ffcx_artifact'}
GEOMETRY = dict(subdivisions=2, cell_type='tetrahedron',
    topological_dimension=3, geometric_dimension=3, cells=48, vertices=27,
    exterior_facets=48, facet_counts={str(tag): 8 for tag in range(1, 7)},
    mixed_space_dofs=402, mixed_space_ghosts=0,
    space_used_for_field_representation=True)


def _scalar(value):
    from numbers import Real
    if isinstance(value, bool) or not isinstance(value, Real) or not isfinite(value):
        raise Refusal('nonfinite or non-real manufactured scalar')
    return float(value)


def measured_geometry(modules, domain, space, tags):
    receipt = geometry_receipt(modules, domain, space, tags)
    receipt['space_used_for_field_representation'] = True
    if type(receipt) is not dict or set(receipt) != set(GEOMETRY):
        raise Refusal('incomplete manufactured geometry')
    for key, value in GEOMETRY.items():
        if type(receipt[key]) is not type(value) or receipt[key] != value:
            raise Refusal('wrong manufactured geometry: ' + key)
    return receipt


def _form_receipt(U, form, domain, tags, key):
    if not isinstance(form, U.Form) or form.arguments():
        raise Refusal('manufactured diagnostic requires ordinary rank-zero UFL form')
    integrals = form.integrals()
    if not integrals or tuple(form.ufl_domains()) != (domain.ufl_domain(),):
        raise Refusal('manufactured form lost its domain or integrals')
    boundary = (key.startswith(('area_', 'flux_')) or key in {
        'lateral_flux', 'boundary_absolute_flux', 'traction_L2_returns_squared',
        'angular.advective', 'angular.traction', 'energy.advective', 'energy.traction'})
    expected_type = 'exterior_facet' if boundary else 'cell'
    if any(item.integral_type() != expected_type for item in integrals):
        raise Refusal('manufactured diagnostic has wrong measure: ' + key)
    tagged = {'lateral_flux': {1, 2, 3, 4},
              'traction_L2_returns_squared': {5, 6}}
    if key.startswith(('area_', 'flux_')):
        tagged[key] = {RETURNS[int(key[-1])]}
    if key in tagged:
        if ({item.subdomain_id() for item in integrals} != tagged[key]
                or any(item.subdomain_data() is not tags for item in integrals)):
            raise Refusal('manufactured diagnostic lost return/face tags')
    return len(integrals)


def assemble_diagnostics(modules, domain, tags, w, context, degree):
    U, fem = modules['ufl'], modules['fem']
    dx = U.Measure('dx', domain=domain, metadata={'quadrature_degree': degree})
    ds = U.Measure('ds', domain=domain, subdomain_data=tags,
                   metadata={'quadrature_degree': degree})
    if context.get('history') is None or context.get('force') is None:
        raise Refusal('exact polynomial history and corrected BE load required')
    forms = field_forms(U, domain, w, *context['history'], context['exact'],
                        context['force'], dx, ds, 1, .125)
    if set(forms) != set(context['raw_keys']):
        raise Refusal('manufactured diagnostic form inventory changed')
    raw, receipts = {}, {}
    for key in sorted(forms):
        print(f'manufactured degree={degree} key={key} stage=form', flush=True)
        count = _form_receipt(U, forms[key], domain, tags, key)
        compiled = fem.form(forms[key])
        if type(compiled.rank) is not int or compiled.rank != 0:
            raise Refusal('compiled manufactured diagnostic has wrong rank')
        print(f'manufactured degree={degree} key={key} stage=assemble', flush=True)
        raw[key] = _scalar(fem.assemble_scalar(compiled))
        receipts[key] = dict(method='fem.form+assemble_scalar',
                             ufl_integrals=count, compiled_rank=0)
    return raw, receipts


def run_manufactured(modules, manifest, *, clock=time.monotonic,
                     linear_evidence):
    """Only fixed n=2/step1. Caller owns admission, held scope and imports."""
    validate_manifest(manifest)
    if (set(modules) != {'np', 'mesh', 'fem', 'fem_petsc', 'basix_ufl', 'basix',
                         'ufl', 'PETSc', 'comm'} or modules['comm'].size != 1
            or linear_evidence is None):
        raise Refusal('complete injected modules and linear recorder required')
    np, meshlib, fem, fp = (modules[key] for key in ('np', 'mesh', 'fem', 'fem_petsc'))
    U, PETSc, comm = (modules[key] for key in ('ufl', 'PETSc', 'comm'))
    started = clock()
    domain, space, tags, lateral = create_cube(np, meshlib, fem,
        modules['basix_ufl'], comm, 2, 'manufactured')
    geometry = measured_geometry(modules, domain, space, tags)
    previous = interpolate_state(np, fem, space, 'manufactured', 0.)
    trace = interpolate_state(np, fem, space, 'manufactured', .125)
    fixed = boundary_values(fem, space, lateral, trace)
    _velocity_space, velocity_map = space.sub(0).collapse()
    if not fixed or not len(velocity_map):
        raise Refusal('missing lateral lift or velocity inventory')
    guess, perturbed = nonexact_guess(trace.x.array.tolist(), velocity_map, fixed)
    if len(guess) != 402:
        raise Refusal('wrong n=2 mixed state length')
    w = fem.Function(space)
    w.x.array[:] = guess
    w.x.scatter_forward()
    guess += [0., 0., 0.]
    t_mesh = clock()
    forms, constants, context = step_forms(U, fem, domain, space, tags, w,
        previous, previous, .125, .125, 1, 'manufactured', degree=24)
    if context.get('history') is None or context.get('force') is None:
        raise Refusal('manufactured residual lost exact history or corrected load')
    assembler = Assembler(fem, fp, PETSc, w, forms, constants, fixed)
    t_forms = clock()
    rows = [assembler.vector(form) for form in assembler.rows]
    condition = constraint_condition(rows, fixed)
    ds, exact = context['ds'], context['exact']
    u, _ = U.split(w)
    normal = U.FacetNormal(domain)
    lateral_flux = _scalar(fem.assemble_scalar(fem.form(
        sum(U.dot(u, normal)*ds(tag) for tag in (1, 2, 3, 4)))))
    lateral_absolute = _scalar(fem.assemble_scalar(fem.form(
        sum(abs(U.dot(u, normal))*ds(tag) for tag in (1, 2, 3, 4)))))
    targets = [_scalar(fem.assemble_scalar(fem.form(exact['targets'][i]*ds(tag))))
               for i, tag in enumerate(RETURNS)]
    # Compatibility is evaluated from quadrature, while reporting uses the
    # independently fixed rational targets in the proposal.
    from .diagnostics import compatibility_report
    compatibility = compatibility_report(lateral_flux, targets,
        lateral_absolute+fsum(abs(value) for value in targets), condition['condition_bound'])
    if any(abs(targets[i]-value) > 1e-12 for i, value in enumerate((.625, 417/256))) or abs(lateral_flux+577/256) > 1e-12:
        raise Refusal('manufactured measured targets differ from rational reference')
    _residual, matrix = assembler(guess)
    scales = row_scales(matrix)
    evaluated_state = None
    def evaluate(state):
        nonlocal evaluated_state
        evaluated_state = list(state)
        return scale_system(*assembler(state), scales)
    corrections = []
    def linear_solve(matrix, rhs):
        receipt = linear_evidence(matrix, rhs, state=evaluated_state,
            scales=scales, fixed=fixed, step=1, correction=len(corrections)+1)
        answer = sparse_solve(np, PETSc, comm, matrix, rhs)
        defect = sqrt(fsum((value-target)**2 for value, target in zip(matrix.matvec(answer), rhs)))
        norm = sqrt(fsum(value*value for value in rhs))
        corrections.append(dict(true_residual=defect, rhs_norm=norm,
                                linear_system=receipt))
        return answer
    state, history = newton(guess, evaluate, linear_solve)
    t_solve = clock()
    if not corrections or len(state) != 405:
        raise Refusal('manufactured pilot needs checked corrections and 405 DOFs')
    assembler(state)  # install the accepted mixed state and border before diagnostics
    raw, receipts = {}, {}
    for degree in (24, 26):
        if degree == 24:
            degree_context = context
        else:
            _forms, _constants, degree_context = step_forms(U, fem, domain, space,
                tags, w, previous, previous, .125, .125, 1, 'manufactured', degree=26)
        degree_context['raw_keys'] = manifest['diagnostic_policy']['raw_keys']
        raw[str(degree)], receipts[str(degree)] = assemble_diagnostics(
            modules, domain, tags, w, degree_context, degree)
    velocity = w.sub(0).collapse()
    samples, counts = return_quadrature_samples(np, meshlib, modules['basix'],
        domain, tags, velocity, 24)
    report = build_report(raw, state[-3:-1], state[-1], history, corrections,
        min(samples), counts, condition, compatibility, targets,
        lateral_absolute, manifest)
    t_diagnostics = clock()
    return dict(geometry=geometry, subdivisions=2, step=1, time=.125, dt=.125,
        history_semantics=manifest['history'], load_semantics=manifest['load'],
        mixed_dofs=402, global_dofs=len(state), fixed_velocity_dofs=len(fixed),
        fixed_inventory={str(key): fixed[key] for key in sorted(fixed)},
        perturbed_velocity_dof=perturbed, perturbation=.05,
        multipliers=state[-3:-1], eta=state[-1],
        constraint_condition=condition, compatibility=compatibility,
        measured_targets=targets, lateral_absolute_flux=lateral_absolute,
        frozen_row_scales=dict(minimum=min(scales), maximum=max(scales)),
        nonlinear_history=history, linear_corrections=corrections,
        raw_by_degree=raw, assembly_receipts=receipts,
        backflow_sampling_degree=24,
        return_quadrature_sample_counts=counts,
        minimum_return_normal_velocity=min(samples), report=report,
        phase_seconds=dict(mesh_and_lift=t_mesh-started,
            primary_form_setup_jit=t_forms-t_mesh,
            compatibility_rank_newton=t_solve-t_forms,
            diagnostic_form_jit_assembly_sampling=t_diagnostics-t_solve))


def expected_admission(admission, manifest_bytes, manifest, run_dir,
                       source_commit, interpreter, owner):
    """Require a separately published one-use admission before reservation."""
    validate_manifest(manifest)
    if (type(admission) is not dict or type(source_commit) is not str
            or len(source_commit) != 40
            or any(ch not in '0123456789abcdef' for ch in source_commit)
            or type(interpreter) is not str or not Path(interpreter).is_absolute()
            or type(owner) is not str or not owner
            or not Path(run_dir).is_absolute()):
        raise Refusal('missing manufactured admission/source identity')
    binary = Path(interpreter).resolve(strict=True)
    template = dict(approved=True, fixture='manufactured',
        kind='manufactured_spatial_pilot', mode='single_be_spatial_pilot',
        worker_schema=1, attempts_granted=1,
        run_directory=str(Path(run_dir).resolve()), source_commit=source_commit,
        manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
        contract_sha256=contract_digest(manifest), interpreter=interpreter,
        executable=str(binary),
        executable_sha256=hashlib.sha256(binary.read_bytes()).hexdigest())
    if (set(admission) != set(template) | {'artifact_inventory_sha256'}
            or any(type(admission[key]) is not type(value)
                   or admission[key] != value for key, value in template.items())
            or type(admission['artifact_inventory_sha256']) is not str
            or len(admission['artifact_inventory_sha256']) != 64
            or any(ch not in '0123456789abcdef'
                   for ch in admission['artifact_inventory_sha256'])):
        raise Refusal('no matching explicit manufactured admission')
    return template


def validate_reservation(reservation, admission, manifest_bytes, manifest,
                         directory, interpreter, owner):
    required = {'status', 'fixture', 'attempt', 'source_commit', 'interpreter',
        'owner', 'release_nonce', 'wall_start_utc', 'monotonic_start', 'caps',
        'kind', 'mode', 'worker_schema', 'manifest_sha256', 'contract_sha256',
        'executable', 'executable_sha256', 'artifact_inventory_sha256'}
    if (type(reservation) is not dict or set(reservation) != required
            or reservation.get('status') != 'RESERVED'
            or type(reservation.get('attempt')) is not int or reservation['attempt'] != 1
            or reservation.get('fixture') != 'manufactured'
            or reservation.get('owner') != owner
            or reservation.get('interpreter') != interpreter
            or canonical(reservation.get('caps')) != canonical(manifest['proposed_caps'])
            or type(reservation.get('release_nonce')) is not str
            or len(reservation['release_nonce']) != 32
            or any(ch not in '0123456789abcdef' for ch in reservation['release_nonce'])
            or type(reservation.get('wall_start_utc')) is not str
            or type(reservation.get('monotonic_start')) not in (int, float)
            or not isfinite(reservation['monotonic_start'])):
        raise Refusal('manufactured reservation changed')
    template = expected_admission(admission, manifest_bytes, manifest, directory,
                                  reservation.get('source_commit'), interpreter, owner)
    for key in ('fixture', 'kind', 'mode', 'worker_schema', 'source_commit',
                'manifest_sha256', 'contract_sha256', 'interpreter', 'executable',
                'executable_sha256', 'artifact_inventory_sha256'):
        if (type(reservation.get(key)) is not type(admission.get(key))
                or reservation.get(key) != admission.get(key)):
            raise Refusal('manufactured reservation/admission mismatch: ' + key)
    if reservation['manifest_sha256'] != template['manifest_sha256']:
        raise Refusal('manufactured manifest bytes changed')
    return reservation


def _times(values, keys):
    if (type(values) is not dict or set(values) != keys
            or any(type(value) not in (int, float) or not isfinite(value)
                   or value < 0 for value in values.values())):
        raise Refusal('missing manufactured timing inventory')


def _validate_latest(saved, payload, latest):
    """Validate the recorder's full sparse record and its envelope aliases."""
    from .linear_evidence import MAX_BYTES, MAX_DOFS, MAX_NNZ, finite_vector
    context = dict(schema=1, fixture='manufactured', subdivisions=2, step=1,
        dt=.125, correction=latest['correction'], stage='before_factorization',
        source_binding=payload['source_binding'], shape=[405, 405], mixed_dofs=402,
        unknown_order='mixed u/p, P_minus, P_plus, eta',
        operator='already lifted and row scaled; rhs is negative scaled residual',
        solver=dict(ksp='preonly', pc='lu', backend='superlu', shift='none',
                    options_prefix=SUPERLU_PREFIX, options=dict(SUPERLU_OPTIONS)),
        factor_permutation=None, pivot_coordinate=None,
        caps=dict(dofs=MAX_DOFS, nnz=MAX_NNZ, bytes=MAX_BYTES))
    variable = {'csr', 'rhs', 'state', 'row_scales', 'fixed_indices', 'fixed_values'}
    if (type(saved) is not dict or set(saved) != set(context) | variable
            or any(canonical(saved[key]) != canonical(value) for key, value in context.items())):
        raise Refusal('latest manufactured linear-system context/inventory changed')
    csr = saved['csr']
    if (type(csr) is not dict or set(csr) != {'indptr', 'indices', 'values'}
            or any(type(value) is not list for value in csr.values())
            or len(csr['values']) > MAX_NNZ):
        raise Refusal('invalid latest manufactured CSR inventory')
    finite_vector(csr['values'], len(csr['values']), 'CSR values')
    matrix = CSR(405, tuple(csr['indptr']), tuple(csr['indices']), tuple(csr['values']))
    try:
        matrix.validate(405)
    except (ValueError, TypeError, OverflowError) as exc:
        raise Refusal('invalid latest manufactured CSR') from exc
    for key in ('rhs', 'state', 'row_scales'):
        if type(saved[key]) is not list:
            raise Refusal('invalid latest manufactured vector: ' + key)
        finite_vector(saved[key], 405, key)
    scales = saved['row_scales']
    fixed = payload['fixed_inventory']
    indices = sorted(map(int, fixed))
    if (canonical(saved['fixed_indices']) != canonical(indices)
            or canonical(saved['fixed_values']) != canonical([fixed[str(i)] for i in indices])
            or any(saved['state'][i] != fixed[str(i)] for i in indices)
            or min(scales) <= 0
            or canonical(dict(minimum=min(scales), maximum=max(scales)))
               != canonical(payload['frozen_row_scales'])):
        raise Refusal('latest manufactured lift/scales alias changed')
    rhs_norm = sqrt(fsum(v*v for v in saved['rhs']))
    if rhs_norm != payload['linear_corrections'][-1]['rhs_norm']:
        raise Refusal('latest manufactured RHS norm changed')


def validate_worker_payload(payload, manifest, reservation, admission, directory):
    """Pure saved-data replay plus final latest-system byte binding."""
    validate_manifest(manifest)
    if type(payload) is not dict or set(payload) != ENVELOPE_KEYS:
        raise Refusal('incomplete manufactured worker envelope')
    fixed = dict(worker_schema=1, fixture='manufactured',
        kind='manufactured_spatial_pilot', mode='single_be_spatial_pilot',
        manifest_sha256=reservation['manifest_sha256'],
        contract_sha256=contract_digest(manifest), subdivisions=2, step=1,
        time=.125, dt=.125, history_semantics=manifest['history'],
        load_semantics=manifest['load'], mixed_dofs=402, global_dofs=405,
        perturbation=.05, backflow_sampling_degree=24)
    if any(type(payload[key]) is not type(value) or payload[key] != value
           for key, value in fixed.items()):
        raise Refusal('manufactured envelope context changed')
    if (any(reservation.get(key) != admission.get(key) for key in
            ('source_commit', 'manifest_sha256', 'contract_sha256', 'interpreter',
             'executable', 'executable_sha256', 'artifact_inventory_sha256'))
            or canonical(payload['source_binding']) != canonical(expected_binding(
                Path(__file__).resolve().parents[2], reservation,
                reservation['interpreter']))):
        raise Refusal('manufactured source/interpreter binding changed')
    if canonical(payload['geometry']) != canonical(GEOMETRY):
        raise Refusal('manufactured geometry changed')
    inventory = payload['fixed_inventory']
    if (type(inventory) is not dict or not inventory
            or type(payload['fixed_velocity_dofs']) is not int
            or payload['fixed_velocity_dofs'] != len(inventory)
            or type(payload['perturbed_velocity_dof']) is not int
            or not 0 <= payload['perturbed_velocity_dof'] < 402
            or str(payload['perturbed_velocity_dof']) in inventory):
        raise Refusal('manufactured lift inventory changed')
    for index, value in inventory.items():
        if (type(index) is not str or not index.isdecimal()
                or str(int(index)) != index or not 0 <= int(index) < 402
                or type(value) not in (int, float) or not isfinite(value)):
            raise Refusal('invalid manufactured fixed DOF')
    if (type(payload['frozen_row_scales']) is not dict
            or set(payload['frozen_row_scales']) != {'minimum', 'maximum'}
            or any(type(value) not in (int, float) or not isfinite(value) or value <= 0
                   for value in payload['frozen_row_scales'].values())
            or payload['frozen_row_scales']['minimum'] > payload['frozen_row_scales']['maximum']):
        raise Refusal('invalid manufactured frozen scales')
    receipts = payload['assembly_receipts']
    keys = set(manifest['diagnostic_policy']['raw_keys'])
    if type(receipts) is not dict or set(receipts) != {'24', '26'}:
        raise Refusal('missing manufactured assembly receipts')
    for degree in ('24', '26'):
        if type(receipts[degree]) is not dict or set(receipts[degree]) != keys:
            raise Refusal('incomplete manufactured assembly receipts')
        for key, item in receipts[degree].items():
            count = (4 if key == 'lateral_flux' else
                     2 if key == 'traction_L2_returns_squared' else 1)
            if (type(item) is not dict
                    or set(item) != {'method', 'ufl_integrals', 'compiled_rank'}
                    or item['method'] != 'fem.form+assemble_scalar'
                    or type(item['ufl_integrals']) is not int
                    or item['ufl_integrals'] != count
                    or type(item['compiled_rank']) is not int
                    or item['compiled_rank'] != 0):
                raise Refusal('invalid manufactured assembly receipt')
    if (type(payload['report']) is not dict
            or canonical(payload['report'].get('raw_by_degree'))
               != canonical(payload['raw_by_degree'])):
        raise Refusal('manufactured raw report alias changed')
    validate_report(payload['report'], manifest,
        multipliers=payload['multipliers'], eta=payload['eta'],
        history=payload['nonlinear_history'], corrections=payload['linear_corrections'],
        minimum_normal=payload['minimum_return_normal_velocity'],
        sample_counts=payload['return_quadrature_sample_counts'],
        condition=payload['constraint_condition'], compatibility=payload['compatibility'],
        measured_targets=payload['measured_targets'],
        lateral_absolute_flux=payload['lateral_absolute_flux'])
    _times(payload['phase_seconds'], PHASES)
    _times(payload['worker_intervals'], INTERVALS)
    validate_versions(payload['actual_versions'], manifest['versions'], payload['ffcx_artifact'])
    latest = payload['linear_corrections'][-1]['linear_system']
    with Path(directory, latest['file']).open('rb') as stream:
        data = stream.read(4*1024*1024+1)
    if len(data) != latest['bytes'] or hashlib.sha256(data).hexdigest() != latest['sha256']:
        raise Refusal('latest manufactured linear-system bytes changed')
    if len(data) > 4*1024*1024:
        raise Refusal('oversized manufactured linear-system bytes')
    try:
        saved = json.loads(data.decode('utf-8'), object_pairs_hook=_duplicate_pairs,
                           parse_constant=_nonfinite_constant)
    except (UnicodeError, ValueError, TypeError, RecursionError) as exc:
        raise Refusal('invalid manufactured linear-system JSON') from exc
    _validate_latest(saved, payload, latest)
    return payload
