"""R022 disposable once-only compatibility barrier at the pinned helper anchor."""
import hashlib
import inspect
import sys

import numpy as np

import toy_runner as support

EPS = np.finfo(float).eps
ORDERS = (64, 96)


class ToyPreparedStop(RuntimeError):
    """Successful toy preparation stops before any KSP exists."""


def vector_sha(vector):
    return hashlib.sha256(vector.array_r.tobytes()).hexdigest()


def matrix_digest(matrix, offsets, constrained):
    digest = hashlib.sha256()
    for array in matrix.getValuesCSR():
        digest.update(array.tobytes())
    digest.update(np.asarray(offsets).tobytes())
    digest.update(constrained.tobytes())
    return digest.hexdigest()


def factor_counts():
    from petsc4py import PETSc
    return {name: int(PETSc.Log.Event(name).getPerfInfo()['count'])
            for name in ('MatLUFactorSym', 'MatLUFactorNum', 'MatSolve')}


def prepare_all(local, expected, candidate_factory, prepared, record, checkpoint,
                toy_probe=None):
    """Validate raw P, then build/check/retain both A RHSs with the actual lift."""
    from dolfinx import fem
    from dolfinx.fem.petsc import create_vector, apply_lifting, set_bc
    from petsc4py import PETSc
    import physical

    required = ('matrix', 'vector', 'spaces', 'offsets', 'a', 'bcs',
                'null_vectors', 'nullspace', 'pressure_indices')
    if any(key not in local for key in required) or any(
            key in local for key in ('solver', 'preconditioner', 'solution_vector')):
        raise RuntimeError('Pre-solve helper capture differs from pinned layout')
    matrix, raw, spaces, offsets = (local[key] for key in required[:4])
    nulls, nullspace = local['null_vectors'], local['nullspace']
    assert tuple(local['pressure_indices']) == (1, 3)
    sizes = [s.dofmap.index_map.size_local * s.dofmap.index_map_bs for s in spaces]
    assert len(spaces) == 4 and sizes[0] == sizes[2] and sizes[1] == sizes[3]
    assert np.array_equal(offsets, np.cumsum([0, *sizes]))
    layout = physical.vector_layout(raw)
    assert layout['owned_offsets'] == offsets.tolist()
    assert layout['ghost_offsets'] == [int(offsets[-1])] * 5
    assert layout['local_size'] == layout['global_size'] == layout['array_size'] == offsets[-1]
    assert layout['ownership_range'] == [0, int(offsets[-1])]
    grouping = fem.extract_function_spaces(local['a'], 1)
    _, sets, _ = physical.collect_constraints(fem, spaces, local['bcs'], offsets, expected, grouping)
    constrained = np.concatenate([sets[i] for i in (0, 2)])
    before_digest = matrix_digest(matrix, offsets, constrained)
    before_state = matrix.stateGet()
    record['pre_solve_operator'] = dict(digest=before_digest, state=before_state,
        offsets=offsets.tolist(), constrained_count=len(constrained),
        layout=layout, factor_counts=factor_counts())
    assert all(count == 0 for count in factor_counts().values())
    checkpoint('pre_solve_nullspace_validation')
    assert len(nulls) == 2
    gram = np.array([[x.dot(y) for y in nulls] for x in nulls])
    assert np.max(abs(gram - np.eye(2))) <= 256 * EPS
    normalization = []
    for null, block in zip(nulls, (1, 3)):
        start, end = offsets[block:block + 2]
        wanted = 1.0 / np.sqrt(end - start)
        null_values = null.array_r
        outside = np.r_[null_values[:start], null_values[end:]]
        error = float(np.max(abs(null_values[start:end] - wanted)))
        assert np.count_nonzero(outside) == 0 and error <= 256 * EPS * wanted
        right, left = raw.duplicate(), raw.duplicate()
        matrix.mult(null, right)
        matrix.multTranspose(null, left)
        normalization.append(dict(pressure_block=block, pressure_dofs=int(end - start),
            expected_coefficient=float(wanted), maximum_coefficient_error=error,
            outside_support_nonzeros=0, right_residual_norm=float(right.norm()),
            left_residual_norm=float(left.norm())))
        right.destroy()
        left.destroy()
    transpose = PETSc.Mat().createTranspose(matrix)
    try:
        right_test, left_test = bool(nullspace.test(matrix)), bool(nullspace.test(transpose))
    finally:
        transpose.destroy()
    record['pre_solve_nullspace'] = dict(gram=gram.tolist(), normalization=normalization,
        right_test_passed=right_test, transpose_test_passed=left_test)
    checkpoint('pre_solve_nullspace_validation')
    assert right_test and left_test

    def unchanged():
        assert matrix.stateGet() == before_state
        assert matrix_digest(matrix, offsets, constrained) == before_digest
        assert all(count == 0 for count in factor_counts().values())

    def check(name, vector, row, apply):
        row['candidate_layout'] = physical.vector_layout(vector)
        assert row['candidate_layout'] == layout
        if toy_probe is not None:
            # Only toy callers may compare an independent oracle or inject into
            # a copy. The physical caller supplies no probe.
            vector = toy_probe(name, vector, local)
        physical.record_compatibility(vector, nulls, row, checkpoint,
            'pressure_compatibility', name + '_primary_rhs_compatibility',
            apply=apply, nullspace=nullspace)
        unchanged()
        row['same_matrix_digest_and_state'] = True
        return vector

    record['completed_rhs_assemblies'] = 1
    record['candidates'] = {'P': {}}
    check('P', raw, record['candidates']['P'], False)
    record['P_pressure_compatibility'] = record['candidates']['P']['pressure_compatibility']
    for order in ORDERS:
        name = 'A_' + str(order)
        row = record['candidates'][name] = {}
        checkpoint(name + '_constraint_collection')
        candidate = candidate_factory(name, local)
        groups, new_sets, _ = physical.collect_constraints(
            fem, spaces, candidate['bcs'], offsets, expected, grouping)
        assert all(np.array_equal(x, y) for x, y in zip(sets, new_sets))
        row['constrained_dofs_per_block'] = [len(item) for item in new_sets]
        row['flux_ratios'] = candidate['flux_ratios']
        checkpoint(name + '_flux_checked')
        if any(value is None or value >= 1e-8 for value in candidate['flux_ratios']):
            raise RuntimeError(name + ' prescribed normal closed-flux check failed')
        rhs = physical.make_lifted_rhs(create_vector, apply_lifting, set_bc, PETSc,
            spaces, local['a'], raw, candidate['block_loads'], groups, row,
            lambda stage: checkpoint(name + '_' + stage))
        record['completed_rhs_assemblies'] += 1
        candidate['rhs'] = check(name, rhs, row, True)
        candidate['grouped_bcs'] = groups
        prepared[name] = candidate
        checkpoint(name + '_rhs_prepared')
    unchanged()
    record['all_candidates_prepared'] = True
    checkpoint('all_rhs_prepared_before_KSP')


def call_with_barrier(original, captured, args, kwargs, expected, candidate_factory,
                      prepared, record, checkpoint, toy_stop=False, toy_probe=None):
    """Trace the actual direct helper once, preserving its source and P solve."""
    support.verify_sources()
    if sys.gettrace() is not None:
        raise RuntimeError('An existing tracer would be overwritten')
    lines, first = inspect.getsourcelines(original)
    anchors = [first + index for index, line in enumerate(lines)
               if line.strip() == 'nullspace.remove(vector)']
    solves = [first + index for index, line in enumerate(lines)
              if line.strip() == 'solver.solve(vector, solution_vector)']
    assert len(anchors) == len(solves) == 1 and anchors[0] < solves[0]
    record['pre_solve_observer'] = dict(anchor_line=anchors[0], solve_line=solves[0],
        calls=0, toy_stop=toy_stop, factor_counts=factor_counts())
    def trace(frame, event, arg):
        if frame.f_code is original.__code__ and event == 'line':
            if frame.f_lineno == anchors[0]:
                record['pre_solve_observer']['calls'] += 1
                assert record['pre_solve_observer']['calls'] == 1
                prepare_all(frame.f_locals, expected, candidate_factory, prepared,
                            record, checkpoint, toy_probe)
                if toy_stop:
                    raise ToyPreparedStop('toy prepared all candidates before KSP')
            elif frame.f_lineno == solves[0]:
                assert record.get('all_candidates_prepared')
                record['primary_rhs'] += 1
                record['attempted_primary_solves'] += 1
                checkpoint('P_primary_solve')
        return trace
    sys.settrace(trace)
    try:
        result = support.capture_return(original, captured, *args, **kwargs)
    finally:
        sys.settrace(None)
        record['pre_solve_observer']['factor_counts'] = factor_counts()
        checkpoint(record['stage'])
    assert record['pre_solve_observer']['calls'] == 1
    return result
