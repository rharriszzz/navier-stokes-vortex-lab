"""Serial, one-tetrahedron DOLFINx block RHS/lifting oracle for R017."""
import hashlib
import json
import resource
import time
from pathlib import Path

import numpy as np

import physical
import toy_runner as support


def layout_or_none(vector):
    blocks = vector.getAttr('_blocks')
    return None if blocks is None else [list(block) for block in blocks]


def json_safe(value):
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def run(output):
    from dolfinx import fem, mesh
    from dolfinx.fem.petsc import apply_lifting, assemble_matrix, create_matrix, create_vector, set_bc
    from mpi4py import MPI
    from petsc4py import PETSc
    import basix.ufl
    import ufl

    started = time.monotonic()
    record = dict(status='partial', stage='imports', campaign_ready=False,
                  physical_meshes=0, pde_solves=0, matrix_factorizations=0,
                  primary_rhs=0, matrix_solves=0, source_sha256=support.EXPECTED_SOURCES)

    def checkpoint(stage):
        record['stage'] = stage
        record['elapsed_seconds'] = time.monotonic() - started
        record['process_peak_rss_mib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        support.write_json(output / 'block-rhs-report.json', json_safe(record))

    checkpoint('imports')
    try:
        support.verify_sources()
        record['runner_sha256'] = support.sha(Path(__file__))
        ref = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
        domain = mesh.create_mesh(MPI.COMM_SELF, np.array([[0, 1, 2, 3]], dtype=np.int64),
            ufl.Mesh(basix.ufl.element('Lagrange', 'tetrahedron', 1, shape=(3,))), ref)
        domain.topology.create_connectivity(2, 3)
        domain.topology.create_connectivity(3, 2)
        element_v = basix.ufl.element('BDM', 'tetrahedron', 2, shape=(3,))
        element_q = basix.ufl.element('Lagrange', 'tetrahedron', 1, discontinuous=True)
        spaces = [fem.functionspace(domain, element_v), fem.functionspace(domain, element_q),
                  fem.functionspace(domain, element_v), fem.functionspace(domain, element_q)]
        V = spaces[0]
        exterior = mesh.exterior_facet_indices(domain.topology)
        sizes = [space.dofmap.index_map.size_local * space.dofmap.index_map_bs for space in spaces]
        offsets = np.cumsum([0, *sizes])
        bcs = []
        expected = [np.empty(0, dtype=np.int32) for _ in spaces]
        expected[0] = fem.locate_dofs_topological(V, 2, exterior)
        expected[2] = fem.locate_dofs_topological(spaces[2], 2, exterior)

        # Every velocity/pressure and real/imaginary coupling has a distinct scale.
        a_ufl = [[None for _ in spaces] for _ in spaces]
        for i, test_space in enumerate(spaces):
            test = ufl.TestFunction(test_space)
            for j, trial_space in enumerate(spaces):
                trial = ufl.TrialFunction(trial_space)
                scale = float(1 + 2 * i + j)
                if i in (0, 2) and j in (0, 2):
                    term = ufl.inner(trial, test)
                elif i in (0, 2):
                    term = trial * ufl.div(test)
                elif j in (0, 2):
                    term = test * ufl.div(trial)
                else:
                    term = trial * test
                a_ufl[i][j] = scale * term * ufl.dx
        forms = fem.form(a_ufl)
        grouping_spaces = fem.extract_function_spaces(forms, 1)
        matrix = create_matrix(forms)
        assemble_matrix(matrix, forms)
        matrix.assemble()
        matrix_state = matrix.stateGet()
        matrix_rows = np.arange(int(matrix.getSize()[0]), dtype=PETSc.IntType)
        dense = matrix.getValues(matrix_rows, matrix_rows)
        coupled_blocks = {}
        for row, column in ((0, 2), (2, 0), (1, 0), (3, 2)):
            block = dense[offsets[row]:offsets[row + 1], offsets[column]:offsets[column + 1]]
            coupled_blocks[f'{row}_{column}'] = float(np.linalg.norm(block))
        if any(value <= 0. for value in coupled_blocks.values()):
            raise AssertionError('A required real/imaginary or velocity/pressure block is zero')
        reference = create_vector(spaces, kind=PETSc.Vec.Type.MPI)
        copied = reference.copy()
        duplicated = reference.duplicate()
        original_layout = layout_or_none(reference)
        copied_layout = layout_or_none(copied)
        duplicated_layout = layout_or_none(duplicated)
        record['vector_metadata'] = dict(type=reference.getType(),
            reference=dict(local_size=reference.getLocalSize(), global_size=reference.getSize(),
                ownership_range=list(reference.getOwnershipRange()), blocks=original_layout,
                array_size=len(reference.array)),
            copied=dict(local_size=copied.getLocalSize(), global_size=copied.getSize(),
                ownership_range=list(copied.getOwnershipRange()), blocks=copied_layout,
                array_size=len(copied.array)),
            duplicated=dict(local_size=duplicated.getLocalSize(), global_size=duplicated.getSize(),
                ownership_range=list(duplicated.getOwnershipRange()), blocks=duplicated_layout,
                array_size=len(duplicated.array)),
            observed_metadata_loss=(copied_layout is None or duplicated_layout is None))
        checkpoint('metadata_reproduced')
        if original_layout is None:
            raise RuntimeError('Factory-created reference vector lacks block metadata')

        def make_bcs(real_value, imag_value):
            result = []
            targets = []
            for space, dofs, value_scalar in ((spaces[0], expected[0], real_value),
                                               (spaces[2], expected[2], imag_value)):
                value = fem.Function(space)
                value.x.array[:] = value_scalar
                targets.append(value)
                result.append(fem.dirichletbc(value, dofs))
            return result, targets

        cases = []
        for target_real, target_imag in ((0., 0.), (.125, -.375)):
            case_bcs, targets = make_bcs(target_real, target_imag)
            groups, global_sets, local_sets = physical.collect_constraints(
                fem, spaces, case_bcs, offsets, expected, grouping_spaces)
            loads = [np.linspace(.1, .8, sizes[0]),
                     np.linspace(-.2, .3, sizes[1]),
                     np.linspace(.9, -.4, sizes[2]),
                     np.linspace(.25, -.15, sizes[3])]
            rhs_record = dict(stage='pre_rhs', matrix_solves=0)

            def rhs_checkpoint(stage):
                rhs_record['stage'] = stage
                rhs_record['matrix_solves'] = 0
                support.write_json(output / f'{len(cases)}-{stage}.json', rhs_record)

            rhs = physical.make_lifted_rhs(create_vector, apply_lifting, set_bc, PETSc,
                spaces, forms, reference, loads, groups, rhs_record, rhs_checkpoint)
            target = np.zeros(int(reference.getSize()))
            for idx, bcs_i in enumerate(groups):
                for bc in bcs_i:
                    start, end = int(offsets[idx]), int(offsets[idx + 1])
                    bc.set(target[start:end])
            load = np.concatenate(loads)
            oracle = load - dense @ target
            constrained = np.concatenate([global_sets[0], global_sets[2]])
            oracle[constrained] = target[constrained]
            actual = np.asarray(rhs.array[:len(oracle)]).copy()
            eps_scale = 256 * np.finfo(float).eps * max(1., float(np.sum(np.abs(dense) * np.outer(np.abs(target), np.ones(len(target))))))
            error = float(np.max(np.abs(actual - oracle)))
            if error > eps_scale:
                raise AssertionError(f'Independent lifting oracle error {error} exceeds {eps_scale}')
            free = np.setdiff1d(np.arange(len(target)), constrained)
            if target_real == 0. and target_imag == 0.:
                if not np.array_equal(actual[free], load[free]):
                    raise AssertionError('Zero target changed unconstrained RHS entries')
            if not np.array_equal(actual[constrained], target[constrained]):
                raise AssertionError('Essential values were not assigned exactly')
            pressure_rows = np.r_[offsets[1]:offsets[2], offsets[3]:offsets[4]].astype(int)
            pressure_lift = float(np.linalg.norm(actual[pressure_rows] - load[pressure_rows]))
            if target_real != 0. and target_imag != 0. and pressure_lift <= eps_scale:
                raise AssertionError('Pressure row did not receive nontrivial velocity lifting')
            cases.append(dict(target=[target_real, target_imag], max_oracle_error=error,
                arithmetic_tolerance=eps_scale, exact_essential_values=True,
                zero_target_free_entries_unchanged=bool(target_real != 0. or target_imag != 0. or
                                                        np.array_equal(actual[free], load[free])),
                pressure_row_lifting_norm=pressure_lift,
                pressure_row_lifting_nontrivial=bool(pressure_lift > eps_scale)))
        if matrix.stateGet() != matrix_state:
            raise AssertionError('Toy operator matrix changed during RHS work')
        record['operator'] = dict(size=list(matrix.getSize()), state_before=matrix_state,
            state_after=matrix.stateGet(), unchanged=True,
            dense_digest=hashlib.sha256(dense.tobytes()).hexdigest(),
            required_coupling_frobenius_norms=coupled_blocks)
        record['cases'] = cases

        # Wrong block offsets and missing metadata must refuse before load/lifting.
        wrong_reference = create_vector([spaces[1], spaces[0], spaces[2], spaces[3]],
                                        kind=PETSc.Vec.Type.MPI)
        refusal = dict(stage='pre_rhs', matrix_solves=0)
        def wrong_checkpoint(stage):
            refusal.update(stage=stage, matrix_solves=0)
            support.write_json(output / 'wrong-offset-refusal.json', json_safe(refusal))
        try:
            physical.make_lifted_rhs(create_vector, apply_lifting, set_bc, PETSc,
                spaces, forms, wrong_reference, [np.zeros(n) for n in sizes],
                fem.bcs_by_block(grouping_spaces, make_bcs(.1, .2)[0]), refusal, wrong_checkpoint)
        except RuntimeError as error:
            record['wrong_offset_refusal'] = dict(refused=True, error=str(error),
                stage=refusal['stage'], matrix_solves=0, rhs_layout=refusal.get('rhs_layout'))
        else:
            raise AssertionError('Wrong block offsets were accepted')
        missing_record = dict(stage='pre_rhs', matrix_solves=0)
        def missing_checkpoint(stage):
            missing_record.update(stage=stage, matrix_solves=0)
            support.write_json(output / 'missing-layout-refusal.json', json_safe(missing_record))
        try:
            physical.make_lifted_rhs(create_vector, apply_lifting, set_bc, PETSc,
                spaces, forms, copied, [np.zeros(n) for n in sizes],
                fem.bcs_by_block(grouping_spaces, make_bcs(.1, .2)[0]), missing_record,
                missing_checkpoint)
        except RuntimeError as error:
            record['missing_layout_refusal'] = dict(refused=True, error=str(error),
                stage=missing_record['stage'], matrix_solves=0,
                rhs_layout=missing_record.get('rhs_layout'))
        else:
            raise AssertionError('Missing block metadata was accepted')

        failure_record = dict(stage='pre_rhs', matrix_solves=0)
        def failure_checkpoint(stage):
            failure_record.update(stage=stage, matrix_solves=0)
            support.write_json(output / 'synthetic-lifting-failure.json',
                               json_safe(failure_record))
        def fail_lifting(*args, **kwargs):
            raise RuntimeError('synthetic lifting failure')
        try:
            physical.make_lifted_rhs(create_vector, fail_lifting, set_bc, PETSc,
                spaces, forms, reference, [np.zeros(n) for n in sizes],
                fem.bcs_by_block(grouping_spaces, make_bcs(.1, .2)[0]), failure_record,
                failure_checkpoint)
        except RuntimeError as error:
            record['synthetic_lifting_failure'] = dict(refused=True, error=str(error),
                stage=failure_record['stage'], layout_present='rhs_layout' in failure_record,
                matrix_solves=0)
        else:
            raise AssertionError('Synthetic lifting error did not propagate')
        if (record['wrong_offset_refusal']['stage'] != 'rhs_layout_validation' or
                record['missing_layout_refusal']['stage'] != 'rhs_layout_validation' or
                record['synthetic_lifting_failure']['stage'] != 'rhs_lifting'):
            raise AssertionError('Failure report stage was not persisted before operation')
        record['status'] = 'passed'
        checkpoint('block_rhs_toys_complete')
    except Exception as error:
        record['status'] = 'partial_failed'
        record['error'] = dict(type=type(error).__name__, message=str(error))
        checkpoint(record['stage'])
        raise


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    run(args.output)
