# R017 block RHS lifting repair: evidence index

Recorded 2026-09-20 for [R017](../../REQUEST_LOG.md#r017--2026-09-20--short-continuation-request).
Read the [result](B2_BLOCK_RHS_TOY_REPAIR_RESULT.md) and the original
[R016 failure and repair contract](B2_MATCHED_TRACE_LIFTING_RESULT.md).

## Repaired disposable source

- [Physical wrapper with layout-checked RHS helper](evidence/r017/physical.py)
- [One-tetrahedron block RHS/lifting oracle](evidence/r017/block_rhs_toys.py)
- [R015 grouping, compatibility and failure-report fixtures](evidence/r017/wrapper_toys.py)
- [Cumulative parent watchdog](evidence/r017/run_toys.py) and copied
  [toy support](evidence/r017/toy_runner.py)
- [Preflight identities and limits](evidence/r017/preflight.json)
- [Standard-library evidence audit](evidence/r017/audit.py),
  [validation result](evidence/r017/validation.json) and
  [archive hashes](evidence/r017/r017_archive_manifest.json)

The source copy includes R016's captured kernels and disk integration code.
The three unchanged support sources are byte-compared with R016; its historical
run payload remains in its original directory and is not duplicated here.

## Execution evidence

The [final passing attempt](evidence/r017/toy-runs/attempt-07/report.json)
contains the R015 fixture report and the
[block RHS report](evidence/r017/toy-runs/attempt-07/block-rhs/block-rhs-report.json),
including vector layouts, operator digest/state, coupling norms, oracle
errors, refusal layouts and solve counts. Its
[compatible-pressure record](evidence/r017/toy-runs/attempt-07/wrapper/synthetic-compatible-pressure.json)
and incompatible-pressure record are retained beside it.

All seven parent attempts are preserved under
[`evidence/r017/toy-runs/`](evidence/r017/toy-runs/). The first six include
their finite reports and captured errors; every attempt is included in the
cumulative 8.5013 second total. The largest recorded process-tree peak across
them is 183.2071 MiB. No run used a physical mesh, PDE solve, factorization or
matrix solve.

Run `python3 docs/realizability/evidence/r017/audit.py` from the repository
root to verify finite reports, source identities, R016 archive preservation,
the cumulative resource envelope and the final toy assertions. It performs no
FEM import or numerical recalculation.
