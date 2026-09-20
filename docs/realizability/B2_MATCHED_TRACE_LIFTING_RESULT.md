# R016 matched-trace attempt: RHS lifting failure

Recorded 2026-09-20 for [R016](../../REQUEST_LOG.md#r016--2026-09-20--short-continuation-request)
against `349c9a3`, under the unchanged [R013 contract](B2_MATCHED_TRACE_REVIEW.md#one-executable-next-task-contract).
The [evidence index](B2_MATCHED_TRACE_LIFTING_EVIDENCE.md) contains the exact
R015 child code, reports, traceback, parent watchdog and stored-data audit.

## Outcome and stop

**The paired diagnostic remains incomplete.** One physical child completed the
original-command P solve, its one residual correction and its output checks,
then failed while lifting the first matched-trace RHS. Neither A_32 nor A_64
was solved. The child took **59.1795 seconds**, with **755.8633 MiB** observed
peak RSS, below the unchanged 180 s/1.5 GiB caps. No physical retry followed.

The traceback points to `physical.py:465`,
`apply_lifting(rhs,captured['a'],bcs=new_grouped)`, and ends with
`AttributeError: 'list' object has no attribute '_cpp_object'`.
The saved `stage=P_outputs` is the last checkpoint, not the failed operation.
The A_32 constraint grouping/set comparison completed before the lifting call;
the A_32 boundary assignment, pressure-compatibility check and solve were not
reached. A_64 lifting was not attempted. This is a wrapper/API failure, not an
A accuracy or compatibility failure.

The recorded inventory is one 482-cell physical mesh, one returned primary
solve, one correction and two matrix solves. PETSc records one symbolic and
one numeric factorization. Matrix digest, state and factor handle/state match
through the P correction. The full three-primary/six-solve inventory was not
reached. The physical B2 gate stays failed and `campaign_ready=false`.

## Failure diagnosis and coverage limitation

The installed DOLFINx 0.10.0 implementation chooses blocked lifting using the
vector's `_blocks` attribute. The traceback entered its non-block branch,
which expects a single row of forms; the wrapper supplied the full block array.
Immediately beforehand the wrapper constructs `rhs=b.copy()`. From this source
and traceback, loss of Python block metadata at that copy is the inferred
cause. No new toy execution was performed after the physical stop to reproduce
the copy behavior. The [official implementation](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/_modules/dolfinx/fem/petsc.html#apply_lifting)
documents the dispatch; [create_vector](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/generated/dolfinx.fem.petsc.html#dolfinx.fem.petsc.create_vector)
provides construction with the block layout.

The R015 repair correctly fixed boundary-space grouping. Its toy tested
`bc.set` on slices of a NumPy array; it did **not** call the full PETSc
`apply_lifting`/`set_bc` sequence on a copied block vector. R016 repeated those
prescribed checks successfully, but they did not cover this newly reached
operation. The original R014/R015 artifacts remain unchanged. This result
does not retroactively claim that their tests covered block lifting.

## Completed prerequisites and P measurements

All 19 production source/configuration identities matched, as did the exact
482-cell mesh with 9,522/1,928 V/Q DOFs and 22,900 real block unknowns.
The 500-cell local diagnostic reproduced `C_upper=58.12657123078638` and
positive alpha=96 guarded beta `0.22187075813338908`. The 3,000-free-DOF
dense guard was unchanged; no dense global audit ran.

The 24 vertex-permutation checks, 30 spanning polynomial vector traces per
permutation, oriented normal projection, weak loads, disk/arc/jump/tangency
checks, quadratic restriction and wrapper checks passed. The watchdog's
synthetic wall-time and two-process RSS tests passed. An initial sandbox child
aborted during MPI initialization before these numerical checks. Its evidence
is retained; after approved escalation the checks passed, with **5.3733 seconds
total**, including the initial 0.4232 s, and **140.9961 MiB** maximum observed
child-tree RSS. The shared toy limits remained 60 s/512 MiB.

On the physical mesh, both polynomial weak loads agreed with UFL at the fixed
arithmetic tolerance. All 482 cells were checked for the disk partition: 11
positive-area regions, correct moments through degree three, and no ambiguous
positive-area coincident interior facet. Both full-trace loads completed on
282 exterior facets. Their real/imaginary closed-flux ratios reproduce R014
and pass `1e-8`; **neither A pressure-compatibility screen was reached**.
Normals, moments, projection coefficients and fluxes are archived for both
orders. Sampled speed, displacement and acceleration scales are preserved as
verification data; force/power, pressure demand and hardware remain unassessed.

The P boundary groups contain 1,692 constrained velocity DOFs each and no
pressure constraints, with disjoint global sets and correct offsets. P's
pre-removal pressure products and removed norm are zero. All original P
diagnostics reproduce R012 exactly except timing, including divergence ratios
`1.61723e-14` and `2.21477e-14` and zero essential residuals.

| Completed P check | Recorded value |
|---|---:|
| Primary relative residual | 8.5034294457e-15 |
| Correction relative residual | 3.3885767741e-13 |
| Corrected relative residual | 1.1617023439e-15 |
| Constrained residual maximum | 0 |
| Cell-integrated primary gain (1/m) | -1.6734724052233703 - 1.0983702805959774 i |
| Cell-integrated corrected gain (1/m) | -1.6734724052233734 - 1.0983702805959560 i |
| Correction gain magnitude (1/m) | 2.2504571344e-14 |
| Primary output arithmetic scale (1/m) | 4.8954273499e-12 |
| Primary independent arc-evaluation difference (1/m) | 1.5543122345e-15 |
| Output linearity discrepancy (1/m) | 2.8976737488e-15 |

Local polynomial reconstruction passed on all 11 regions for P, its correction
and corrected field. All three output arithmetic/component screens passed
against the prescribed `E5/100=3.4556100991e-8 1/m`; output linearity passed
its `9.7908546997e-12 1/m` arithmetic tolerance. These are completed diagnostic
checks, not rigorous total-error bounds or a completed matched-trace experiment.

Both unchanged polar rules reproduce R012 within `2.4719806123e-13 1/m`, and
the report retains all six signed features at each rule. The finest polar
disk gain differs from the cell-integrated value by `6.8465234732e-5 1/m`,
19.8128 times E5. P's cell-integrated amplitude is 28963.4968 times the
reference with 74.1175 degrees phase error; its strict 5%/5-degree comparison
fails. This corroborates the already failed P comparison. It supplies no
matched-trace error, boundary-sensitivity difference or continuum geometry
allocation. No conclusion about physical preparation or sensing follows.

## Evidence and skipped work

The physical watchdog took 1,090 samples with maximum gap 0.060371 s; process
high-water RSS and observed peak were both 755.8633 MiB. Sampling is not an
instantaneous memory bound. The read-only standard-library audit passed for
48 archived artifacts, 19 production identities, 79 historical R014/R015
files, four earlier appendices, 564 facet records, disk moments, P outputs,
operator records and stop counts. It performs no FEM import, mesh, assembly,
solve, reference evaluation or reintegration of a field.

Skipped after the stop: completed A lifting/assignment, A pressure compatibility,
both A solves and corrections, their PDE/trace/feature/output checks, the
paired error identities and load sensitivity. Full application, optional
dense/calibration/refinement suites, production changes, gate integration,
campaign, B3, rendering and encoding were outside this task. No solution
coefficient vectors were saved for later field recovery. There was no physical
retry, threshold change, cap increase or new solver choice.

## Next bounded task: exercise and repair block RHS lifting on toys

Recommend **GPT-5.6 Luna, medium reasoning** for this mechanical package.
Use a new disposable copy of the archived code, preserving all R014–R016
evidence and the 19 pinned production identities.

1. Reproduce the missing-layout path with a PETSc block vector on one reference
   tetrahedron with distinct real/imaginary BDM2/DG1 spaces. Record the original,
   copied and duplicated vectors' type, local/global size, owned/ghost offsets
   and `_blocks` metadata. This is a toy API check, not another physical run.
2. Replace the A RHS allocation with `dolfinx.fem.petsc.create_vector` using the
   captured RHS/test spaces and the original MPI vector kind. Validate its
   layout against the captured original vector and block sizes before writing
   data or lifting. Refuse missing/wrong layout explicitly. Avoid depending on
   unverified attribute propagation through `copy()`/`duplicate()`.
3. Exercise the actual helper used by the repaired physical wrapper through
   manual block loading, column-grouped lifting, reverse scatter and row-grouped
   boundary assignment, with zero and nonzero complex normal targets. Use the
   same trial/test spaces for grouping, retaining the existing constraint
   validation. Include velocity-pressure and real-imaginary off-diagonal toy
   forms so pressure lifting and cross-block offsets are tested. Compare all
   entries against an independently assembled unconstrained toy operator times
   the boundary extension, followed by exact essential assignment. That matrix
   product is a toy lifting oracle only; never use it to manufacture a physical
   verification load. Require unchanged unconstrained entries for zero targets,
   exact constrained values, nontrivial pressure-row lifting and an unchanged
   toy matrix. Use the existing `256*eps` absolute-contribution arithmetic scale.
4. Checkpoint an explicit stage before A constraint collection, RHS allocation,
   lifting, assignment and compatibility. Persist layout metadata and actual
   solve counts on refusal. Test missing-layout/wrong-offset and synthetic
   lifting-error paths, plus compatible/incompatible pressure fixtures. No
   pressure products may be silently removed to force a pass. Re-run the R015
   grouping and failure-report fixtures; retain exact finite partial reports.
5. Keep all toy execution, including imports and any failed attempts, under a
   parent-monitored **60 s/512 MiB total** budget, single-threaded and serial.
   MPI requires the approved execution environment; do not rediscover the
   sandbox failure with another numerical attempt. No physical cylinder,
   factorization or PDE solve. Stop on a resource limit, unexplained numerical
   inconsistency, scientific decision or completion; do not enlarge the budget.
6. Archive the exact repaired copy, fixtures and finite reports; audit original
   evidence and source identities, update continuity, commit/push under the next
   `Continue`, and stop before physical execution.

After these checks pass, recommend **GPT-6 Astra, high reasoning** to review
coverage of the remaining A path and specify or conduct one separately scoped
R013 attempt under its original prerequisites and caps. Retain Luna/medium
only for another fully understood mechanical defect; refer any scientific
assumption, tolerance or method decision to Astra/high. A toy lifting pass
still does not establish physical compatibility or accuracy.

Model availability and effort support were checked in the current session
catalog and the fetched official [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
and [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) pages using
OpenAI Docs. No model switch, delegation or automation occurred in this task.
The next prompt is **Continue**.
