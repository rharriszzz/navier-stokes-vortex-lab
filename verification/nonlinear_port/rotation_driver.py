"""Injected rotation assembly and strict saved-result checks; no FEM imports."""
import hashlib
import json
import math
import os
from pathlib import Path
import time

from .cube_adapter import create_cube
from .package_identity import validate_versions
from .prototype import Refusal
from .rotation_manifest import canonical, contract_digest, validate as validate_manifest
from .rotation_oracle import build_report, rotation_forms, validate_report
from .source_binding import expected_binding


REPORT_LIMIT = 2_000_000
GEOMETRY = dict(subdivisions=2, cell_type='tetrahedron',
                topological_dimension=3, geometric_dimension=3, cells=48,
                vertices=27, exterior_facets=48,
                facet_counts={str(tag): 8 for tag in range(1, 7)},
                mixed_space_dofs=402, mixed_space_ghosts=0,
                space_used_for_field_representation=False)
ENVELOPE_KEYS = frozenset({'worker_schema', 'kind', 'fixture', 'mode',
                           'manifest_sha256', 'contract_sha256', 'source_binding',
                           'geometry', 'oracle', 'assembly_receipts', 'phase_seconds',
                           'worker_intervals', 'actual_versions', 'ffcx_artifact'})
PHASES = frozenset({'mesh_and_tags', 'degree24_form_jit_assembly',
                    'degree26_form_jit_assembly', 'report_reduction'})
INTERVALS = frozenset({'import_seconds', 'fixture_setup_jit_and_assembly_seconds'})


def _duplicate_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Refusal('duplicate rotation JSON key')
        result[key] = value
    return result


def _nonfinite_constant(value):
    raise Refusal('nonfinite rotation JSON constant: ' + value)


def strict_json_bytes(data):
    if type(data) is not bytes or len(data) > REPORT_LIMIT:
        raise Refusal('missing or oversized rotation JSON')
    try:
        return json.loads(data.decode('utf-8'), object_pairs_hook=_duplicate_pairs,
                          parse_constant=_nonfinite_constant)
    except (UnicodeError, ValueError, TypeError, RecursionError) as exc:
        raise Refusal('malformed rotation JSON') from exc


def read_limited(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > REPORT_LIMIT:
        raise Refusal('missing or oversized rotation JSON')
    return strict_json_bytes(path.read_bytes())


def write_limited_new(path, value):
    try:
        data = (json.dumps(value, indent=2, sort_keys=True,
                           allow_nan=False) + '\n').encode('utf-8')
    except (TypeError, ValueError) as exc:
        raise Refusal('non-JSON rotation result') from exc
    if len(data) > REPORT_LIMIT:
        raise Refusal('oversized serialized rotation result')
    with Path(path).open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def expected_admission(admission, manifest_bytes, manifest, run_dir,
                       source_commit, interpreter, owner):
    """Check all external bindings before a one-use reservation is created."""
    validate_manifest(manifest)
    if (type(admission) is not dict or type(source_commit) is not str
            or len(source_commit) != 40 or any(ch not in '0123456789abcdef' for ch in source_commit)
            or type(interpreter) is not str or not Path(interpreter).is_absolute()
            or type(owner) is not str or not owner or not Path(run_dir).is_absolute()):
        raise Refusal('missing rotation admission/source identity')
    directory = Path(run_dir).resolve()
    resolved = Path(interpreter).resolve(strict=True)
    template = dict(approved=True, fixture='rotation', mode='exact_field_assembly',
                    kind='rotation_assembly', worker_schema=1, attempts_granted=1,
                    run_directory=str(directory), source_commit=source_commit,
                    manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
                    contract_sha256=contract_digest(manifest['contract']),
                    interpreter=interpreter, executable=str(resolved),
                    executable_sha256=hashlib.sha256(resolved.read_bytes()).hexdigest())
    if (set(admission) != set(template) | {'artifact_inventory_sha256'}
            or any(type(admission[key]) is not type(value) or admission[key] != value
                   for key, value in template.items())
            or type(admission['artifact_inventory_sha256']) is not str
            or len(admission['artifact_inventory_sha256']) != 64
            or any(ch not in '0123456789abcdef' for ch in admission['artifact_inventory_sha256'])):
        raise Refusal('no matching explicit rotation admission')
    return template


def validate_reservation(reservation, admission, manifest_bytes, manifest,
                         directory, interpreter, owner):
    """Worker independently checks the saved allocation before held release."""
    required = {'status', 'fixture', 'attempt', 'source_commit', 'interpreter',
                'owner', 'release_nonce', 'wall_start_utc', 'monotonic_start',
                'caps', 'kind', 'mode', 'worker_schema', 'manifest_sha256',
                'contract_sha256', 'executable', 'executable_sha256',
                'artifact_inventory_sha256'}
    if (type(reservation) is not dict or set(reservation) != required
            or reservation.get('status') != 'RESERVED'
            or type(reservation.get('attempt')) is not int or reservation['attempt'] != 1
            or reservation.get('fixture') != 'rotation'
            or reservation.get('mode') != 'exact_field_assembly'
            or reservation.get('kind') != 'rotation_assembly'
            or type(reservation.get('worker_schema')) is not int
            or reservation['worker_schema'] != 1
            or reservation.get('owner') != owner
            or reservation.get('interpreter') != interpreter
            or canonical(reservation.get('caps')) != canonical(manifest['proposed_caps'])
            or type(reservation.get('release_nonce')) is not str
            or len(reservation['release_nonce']) != 32
            or any(ch not in '0123456789abcdef' for ch in reservation['release_nonce'])
            or type(reservation.get('wall_start_utc')) is not str
            or type(reservation.get('monotonic_start')) not in (int, float)
            or not math.isfinite(reservation['monotonic_start'])):
        raise Refusal('rotation reservation changed')
    template = expected_admission(admission, manifest_bytes, manifest, directory,
                                  reservation.get('source_commit'), interpreter, owner)
    for key in ('fixture', 'mode', 'kind', 'worker_schema', 'source_commit',
                'manifest_sha256', 'contract_sha256', 'interpreter', 'executable',
                'executable_sha256', 'artifact_inventory_sha256'):
        if reservation.get(key) != admission.get(key):
            raise Refusal('rotation reservation/admission mismatch: ' + key)
    if reservation['manifest_sha256'] != template['manifest_sha256']:
        raise Refusal('rotation manifest bytes changed')
    return reservation


def geometry_receipt(modules, domain, space, tags):
    topology = domain.topology
    fdim = topology.dim - 1
    exterior = modules['mesh'].exterior_facet_indices(topology)
    values = tags.values
    indices = tags.indices
    counts = {str(tag): sum(int(value) == tag for value in values)
              for tag in range(1, 7)}
    if (len(indices) != len(exterior) or set(map(int, indices)) != set(map(int, exterior))
            or sum(counts.values()) != len(values)):
        raise Refusal('rotation facet inventory does not cover exterior')
    return dict(subdivisions=2, cell_type=topology.cell_name(),
                topological_dimension=topology.dim, geometric_dimension=domain.geometry.dim,
                cells=topology.index_map(3).size_global,
                vertices=topology.index_map(0).size_global,
                exterior_facets=len(exterior), facet_counts=counts,
                mixed_space_dofs=space.dofmap.index_map.size_global*space.dofmap.index_map_bs,
                mixed_space_ghosts=space.dofmap.index_map.num_ghosts,
                space_used_for_field_representation=False)


def validate_geometry(receipt):
    if type(receipt) is not dict or set(receipt) != set(GEOMETRY):
        raise Refusal('missing rotation geometry receipt')
    for key, value in GEOMETRY.items():
        if type(receipt[key]) is not type(value):
            raise Refusal('wrong rotation geometry type: ' + key)
        if key == 'facet_counts':
            if (set(receipt[key]) != set(value)
                    or any(type(receipt[key][tag]) is not int
                           or receipt[key][tag] != count for tag, count in value.items())):
                raise Refusal('wrong rotation face counts')
        elif receipt[key] != value:
            raise Refusal('wrong rotation geometry: ' + key)
    return receipt


def _scalar(value):
    # numpy.float64 is accepted via numbers.Real; complex, arrays and bool are not.
    from numbers import Real
    if isinstance(value, bool) or not isinstance(value, Real):
        raise Refusal('non-real assembled rotation scalar')
    result = float(value)
    if not math.isfinite(result):
        raise Refusal('nonfinite assembled rotation scalar')
    return result


def _form_receipt(U, form, domain, tags, key):
    if not isinstance(form, U.Form) or form.arguments():
        raise Refusal('rotation needs ordinary rank-zero UFL Form')
    integrals = form.integrals()
    if not integrals or tuple(form.ufl_domains()) != (domain.ufl_domain(),):
        raise Refusal('rotation form lost its mesh domain or integrals')
    boundary = (key.startswith(('area_', 'normal_'))
                or key.endswith('_traction_boundary_l2_squared'))
    expected_type = 'exterior_facet' if boundary else 'cell'
    if any(integral.integral_type() != expected_type for integral in integrals):
        raise Refusal('rotation form has wrong measure type')
    if boundary:
        ids = {integral.subdomain_id() for integral in integrals}
        wanted = (set(range(1, 7)) if key.endswith('_traction_boundary_l2_squared')
                  else {int(key.split('_')[1])})
        if ids != wanted or any(integral.subdomain_data() is not tags for integral in integrals):
            raise Refusal('rotation face tags missing or changed')
    return len(integrals)


def assemble_rotation(modules, manifest, *, monotonic=time.monotonic):
    """One serial n=2 exact-field assembly. Caller owns held release and imports."""
    validate_manifest(manifest)
    if modules['comm'].size != 1:
        raise Refusal('rotation needs one MPI rank')
    np, fem, U = modules['np'], modules['fem'], modules['ufl']
    begin = monotonic()
    domain, space, tags, _ = create_cube(np, modules['mesh'], fem,
                                         modules['basix_ufl'], modules['comm'], 2, 'rotation')
    geometry = validate_geometry(geometry_receipt(modules, domain, space, tags))
    phases = {'mesh_and_tags': monotonic()-begin}
    raw, receipts = {}, {}
    for degree in (24, 26):
        started = monotonic()
        forms = rotation_forms(U, domain, tags, degree)
        if set(forms) != set(manifest['contract']['raw_targets_rational']):
            raise Refusal('rotation form inventory changed')
        values, evidence = {}, {}
        for key in sorted(forms):
            print(f'rotation degree={degree} key={key} stage=form', flush=True)
            try:
                count = _form_receipt(U, forms[key], domain, tags, key)
                compiled = fem.form(forms[key])
                if type(compiled.rank) is not int or compiled.rank != 0:
                    raise Refusal('compiled rotation form has wrong rank')
                print(f'rotation degree={degree} key={key} stage=assemble', flush=True)
                values[key] = _scalar(fem.assemble_scalar(compiled))
            except Exception as exc:
                raise Refusal(f'rotation degree={degree} key={key}: {type(exc).__name__}: {exc}') from exc
            evidence[key] = dict(method='fem.form+assemble_scalar',
                                 ufl_integrals=count, compiled_rank=0)
        raw[str(degree)], receipts[str(degree)] = values, evidence
        phases[f'degree{degree}_form_jit_assembly'] = monotonic()-started
    started = monotonic()
    report = build_report(raw, manifest['contract'])
    phases['report_reduction'] = monotonic()-started
    return geometry, report, receipts, phases


def _nonnegative_times(times, keys):
    if type(times) is not dict or set(times) != keys:
        raise Refusal('missing rotation timing inventory')
    for value in times.values():
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise Refusal('invalid rotation timing')


def validate_worker_payload(payload, manifest, reservation, admission):
    validate_manifest(manifest)
    if type(payload) is not dict or set(payload) != ENVELOPE_KEYS:
        raise Refusal('incomplete rotation worker envelope')
    fixed = dict(worker_schema=1, kind='rotation_assembly', fixture='rotation',
                 mode='exact_field_assembly',
                 manifest_sha256=reservation['manifest_sha256'],
                 contract_sha256=contract_digest(manifest['contract']))
    if any(type(payload[key]) is not type(value) or payload[key] != value
           for key, value in fixed.items()):
        raise Refusal('rotation envelope context changed')
    if (any(reservation.get(key) != admission.get(key) for key in
            ('source_commit', 'manifest_sha256', 'contract_sha256', 'interpreter',
             'executable', 'executable_sha256', 'artifact_inventory_sha256'))
            or canonical(payload['source_binding']) != canonical(expected_binding(
                Path(__file__).resolve().parents[2], reservation, reservation['interpreter']))):
        raise Refusal('rotation worker source/interpreter binding changed')
    validate_geometry(payload['geometry'])
    validate_report(payload['oracle'], manifest['contract'])
    receipts = payload['assembly_receipts']
    keys = set(manifest['contract']['raw_targets_rational'])
    if type(receipts) is not dict or set(receipts) != {'24', '26'}:
        raise Refusal('missing rotation assembly receipts')
    for degree in ('24', '26'):
        if type(receipts[degree]) is not dict or set(receipts[degree]) != keys:
            raise Refusal('incomplete rotation assembly receipts')
        for key, item in receipts[degree].items():
            expected_count = (6 if key.endswith('_traction_boundary_l2_squared') else 1)
            if (type(item) is not dict or set(item) !=
                    {'method', 'ufl_integrals', 'compiled_rank'}
                    or item['method'] != 'fem.form+assemble_scalar'
                    or type(item['ufl_integrals']) is not int
                    or item['ufl_integrals'] != expected_count
                    or type(item['compiled_rank']) is not int or item['compiled_rank'] != 0):
                raise Refusal('invalid rotation assembly receipt')
    _nonnegative_times(payload['phase_seconds'], PHASES)
    _nonnegative_times(payload['worker_intervals'], INTERVALS)
    validate_versions(payload['actual_versions'], manifest['versions'], payload['ffcx_artifact'])
    return payload
