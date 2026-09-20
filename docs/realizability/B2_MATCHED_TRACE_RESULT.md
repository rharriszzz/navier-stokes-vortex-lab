# B2 matched-trace attempt: wrapper failure after the first solve

Recorded 2026-09-20 for [R014](../../REQUEST_LOG.md#r014--2026-09-20--short-continuation-request)
against `d5a2711`, under the [R013 experiment contract](B2_MATCHED_TRACE_REVIEW.md#one-executable-next-task-contract).
The [evidence index](B2_MATCHED_TRACE_RUN_EVIDENCE.md) preserves the exact
disposable code, finite partial report, facet data, watchdogs and read-only audit.

## Result and stopping point

**The diagnostic is incomplete because its disposable wrapper failed after
the original-command solve. No matched-trace response was calculated.** The
physical child ran once, for 54.1700 s with 734.7539 MiB peak RSS, within
180 s/1.5 GiB. There was no resource stop, retry or cap increase.

The original backend returned P successfully and its existing PDE checks passed.
The next wrapper operation attempted to collect constrained DOFs using
`bc.function_space == spaces[i]`. In this installed DOLFINx version, the former
returns a C++ object while the latter is a Python wrapper. The filter produced
no arrays, and `numpy.concatenate` raised
`ValueError: need at least one array to concatenate`. The installed
`bcs_by_block` implementation instead uses `V.contains(bc.function_space)`;
the [DOLFINx API](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/generated/dolfinx.fem.html#dolfinx.fem.bcs_by_block)
documents grouping boundary conditions by space. This is an instrumentation
defect, not a failed Stokes accuracy comparison or evidence about hardware.

The report's `stage=P_assembly_and_primary_solve` is its **last checkpoint**;
the preserved traceback identifies the subsequent failed constraint collection.
Exactly one physical mesh and one returned primary matrix solve are recorded.
There were zero residual-correction solves and zero A solves. The matrix hash,
factor identity and PETSc event-counter checkpoint was after the failing line
and was not reached; those checks must not be claimed passed. No coefficient
vectors were saved, so the unmeasured gains cannot be recovered from this report.

R013 requires stopping on an internal inconsistency without retry. The exact
failed wrapper is preserved unchanged; its later code is **unexecuted and
unvalidated on a physical field**. The physical B2 gate stays failed and
`campaign_ready=false`. No resolution/geometry error allocation, matched-trace
accuracy, preparation, sensing or movie-flow conclusion follows.

## Completed prerequisites

All 19 numerical source/configuration identities matched. The physical mesh
hash was `423ab057c5738ae3e2dcef6e82c238ee7e61bc1d0af7f1e212d04b8a2cd6bfb4`,
with 482 cells, 9,522/1,928 V/Q DOFs and 282 exterior facets. The unchanged
500-cell local diagnostic reproduced `C_upper=58.12657123078638` and
alpha=96 guarded beta `0.22187075813338908`. The 3,000-free-DOF dense guard
was unchanged; no dense global audit ran.

Toy checks covered all 24 reference-tetrahedron vertex permutations, 30
polynomial vector traces spanning P2³, oriented basis evaluation against
DOLFINx, facet-normal L2 projection, and polynomial weak loads. Circle moments
through degree three were checked on a disk, half/quarter disks, a triangle,
an arc segment, tangencies and a two-region polynomial jump. Analytic arc
moments were compared with 16/32-point rules; quadratic stencil/restriction and
plane-cut checks followed in a second toy child. The two toy children together
took 4.4804 s, below the shared 60 s/512 MiB budget; their maximum parent-observed
RSS was 141.5508 MiB. No toy failure or toy retry occurred.

On the physical mesh, the disk intersects 11 positive-area cell regions. The
runner visited all 482 cells and found no positive-area coincident interior
facet on the disk. Summed moments through degree three passed their fixed
arithmetic checks; area was `0.001963495408493621 m²` and denominator
`6.135923151542566e-7 m⁴`. These check the **partition geometry**, not integration
of a solved velocity field. No physical field reconstruction or output-component
screen was reached.

Two representative polynomial boundary loads agreed with ordinary UFL assembly
over all exterior facets. Maximum coefficient differences were `1.31839e-16`
and `9.97466e-18`, below their fixed `256*eps*sum(abs(contributions))` tolerances
`5.87251e-13` and `6.55390e-14`. This is RHS assembly validation, with no extra
PDE solve. The new code uses actual DOF transformations and affine Piola maps;
it does not create a load by applying the global matrix to a prescribed field.

## Boundary fixtures assembled before the stop

Both q=32 and q=64 Duffy rules completed the 128-term full-complex-trace normal
projection and weak load on all 282 facets, with exact zero caps and reference
batches of at most 256 points. Normals, six projection coefficients/moments,
facet mass matrices and signed/absolute fluxes are archived for both rules.

| Quantity | A_32 | A_64 |
|---|---:|---:|
| Signed real flux (m³/s) | 2.571353564e-19 | -1.148951082e-25 |
| Signed imaginary flux (m³/s) | 2.336108895e-22 | 2.742032422e-26 |
| Real closed-flux ratio | 3.039618866e-10 | 1.357980991e-16 |
| Imaginary closed-flux ratio | 1.648596316e-12 | 1.935054430e-16 |
| Sampled speed scale (m/s) | 9.999968377e-8 | 9.999999110e-8 |
| Sampled displacement scale (m) | 1.591544398e-6 | 1.591549289e-6 |
| Sampled acceleration scale (m/s²) | 6.283165438e-9 | 6.283184748e-9 |

All four flux ratios pass the unchanged strict `1e-8` check. The sampled scales
are verification data, not certified global bounds or hardware demands.
Pressure demand and force/power remain unassessed.

**The lifted A pressure-compatibility checks were not reached.** Passing the
closed-flux ratio does not imply passing the separate `256*eps*||b||` arithmetic
compatibility screen. The difference between the flux residuals at the two
rules warrants retaining that screen; no pass or failure of it is inferred.
No return-flow repair, changed trace or threshold was used.

P's pre-removal pressure-constant products and removed norm were zero; its RHS
norm was `0.10374689140977104`. The returned relative residual was
`8.503429445731727e-15`, with real/imaginary divergence ratios
`1.617227848598101e-14` and `2.214765018788265e-14`. Its essential DOF residuals
were zero. All P diagnostics exactly match R012 except timing. This reproduces
the already studied backend solve; there is no new P gain or corrected output.

## Evidence validation and limitations

Synthetic wall-time and two-process RSS watchdog tests passed. The physical
watchdog sampled 1,003 times at nominal 0.05 s, with maximum gap 0.060411 s;
both parent-observed and process high-water RSS were 734.7539 MiB. Imports,
geometry, local checks, loads, assembly, solve and report output were monitored.
Sampled RSS is not an instantaneous bound.

The standard-library [stored-data audit](evidence/r014/audit.py) checks 27
archived file identities, 19 source identities, 482 local certificate values,
564 facet projection equations/flux reductions, 11 disk regions, both UFL
comparisons, all permutation records, P diagnostics and the stop counts.
It performs no new mesh, assembly, solve, reference evaluation or field integral.
The two large facet JSON files are stored one facet per line without changing
any parsed value; the manifest records original and archived byte hashes.

Skipped after the stop: all corrections; A lifting/pressure compatibility and
solves; matrix/factor identity and event counters; physical polynomial
reconstruction; all six original features at both rules; cell-integrated gains;
P output reproduction; error identities and component/reference comparisons.
No full application, dense/calibration/refinement suite, production backend
change, gate integration, campaign, B3, rendering or encoding ran. The numerical
package and all prior evidence appendices are unchanged.

## Next bounded task: repair wrapper instrumentation on toy data only

Recommend **GPT-5.6 Luna, medium reasoning** for this fully specified mechanical
package. Preserve this failed attempt and its archived code. Make a new disposable
working copy; do not edit the evidence to make it appear successful.

1. Replace all three comparisons of `bc.function_space == spaces[index]` in
   `physical.py` with grouping through `fem.bcs_by_block(spaces, bcs)` and its
   corresponding `new_bcs` grouping. Use those groups consistently for global
   constraints, same-set comparison and essential residuals. Require nonempty
   groups for each velocity block, empty pressure groups, disjoint correctly
   offset sets, and equality to independently located exterior normal DOFs.
2. Run this validation before entering the original direct-solve helper, while
   its spaces/BCs are already available. Make invalid/empty/missing groups produce
   an explicit refusal report before a solve. Preserve all physical load/form,
   lift, nullspace, solver, scaling and acceptance behavior.
3. Checkpoint actual returned-solve counts and PETSc factor counters immediately
   after the helper returns, before later bookkeeping can fail. Set an explicit
   next stage before constraint collection and each compatibility check. Persist
   pre-removal pressure products, RHS norm, removed norm and tolerance **before**
   raising on compatibility failure. The current helper raises before returning
   those data to its caller; that path also needs a focused failure-report test.
4. Under a parent-monitored **60 s/512 MiB total toy budget**, test one reference
   tetrahedron with distinct real/imaginary BDM2/DG1 spaces and prescribed normal
   coefficients. Expect 24 exterior DOFs per velocity block, six unconstrained
   cell-interior velocity DOFs, zero pressure constraints and correct block
   offsets. Check zero and nonzero complex targets, exact constrained assignment,
   unchanged constraint sets, and intentional missing/wrong-space refusal. Use
   synthetic bookkeeping/compatibility failures to test durable partial JSON.
   No physical cylinder, matrix factorization or PDE solve is part of this task.
5. Preserve the exact repaired working copy, toy fixtures and finite report,
   audit unchanged production hashes and archived R014 evidence, update the log
   and handoff, commit/push under the next `Continue`, and stop. Do not launch the
   matched-trace experiment in that same continuation.

After passing the focused repair, recommend **GPT-6 Astra, high reasoning** to
review the repaired runner and conduct a separately authorized R013 attempt,
retaining every prerequisite, cap and stop. The unreached A pressure screen and
physical output path remain unvalidated. If another mechanical defect prevents
the toy checks, retain Luna/medium with exact edits and no physical retry; if
resolution requires a scientific assumption or threshold change, stop and
recommend Astra/high for that bounded decision.

Availability was rechecked 2026-09-20 in the session catalog and fetched official
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) and
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) pages using
OpenAI Docs. This is a task/effort recommendation, not a model switch, delegated
session or automation. Account access can differ. The next prompt is **Continue**.
