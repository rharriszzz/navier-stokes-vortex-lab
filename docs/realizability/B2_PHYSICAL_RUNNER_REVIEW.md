# R067 observer, physical runner and compiler review

Recorded 2026-09-20 against source commit
`73416243fb9857c834d6663cca2235a116253537`. This completes the PC review selected
by R065/R066 and requested by [R067](../../REQUEST_LOG.md#r067--2026-09-20--short-continuation-request).
It uses the [R021 contract](B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md),
[R013 thresholds](B2_MATCHED_TRACE_REVIEW.md),
[R020 physical stop](B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md), and
[R033 prerequisite evidence](B2_COMPATIBLE_TRACE_PREFLIGHT_FOLLOWUP.md).

## Decision

The fixed q=64/q=96 matched-trace comparison remains scientifically useful,
but **the archived parent is not ready for physical launch**. Preserve the
validated compatibility observer. Repair the launch policy and failure/count
reporting in a new disposable copy, with saved-data and synthetic checks only.
Do not rerun R033 as a new assignment or launch the physical experiment yet.
The next task is specified [below](#next-task-launch-and-report-repair).

A passing matched-trace result would show agreement for one output on the
existing discretization; a failed result would help identify approximation
limitations. Neither outcome alone separates continuum geometry error from
spatial/trace error or proves hardware feasibility. The alternative shared
potential moments, a new axisymmetric solver, refinement, and pressure/return
flow repair remain deferred. No change to the production Stokes method,
actuation, sensing, reduced state or scientific thresholds is selected here.

The physical B2 gate stays failed and `campaign_ready=false`. R020 remains the
last physical attempt. The fixed q=64/q=96 physical attempt has not been used;
R067 launches none. A future benchmark must never replay it on both machines.

## What the observer evidence supports

The [saved-data audit](evidence/r067/review.json) verifies 19 pinned production
identities, all 796 previously committed evidence files, R033's final and
per-attempt runner hashes, four observer cases, nine full block-oracle
comparisons and 16 high-order facet checks. Historical evidence is unchanged.

| Contract item | Finding |
|---|---|
| P then A_64 then A_96 before KSP | The unique pinned `nullspace.remove(vector)` line triggers the observer once. Required locals exist; solver/preconditioner/solution locals must not exist. The final sentinel case prepares all three RHSs with zero factor/solve events. |
| Full block lifting | A replacement vector comes from `create_vector`; all four blocks, complete bilinear lifting, reverse scatter and BC assignment are used. The independent unconstrained UFL matrix/load oracle includes pressure and real/imaginary coupling. |
| Compatibility and raw preservation | Pressure vectors have disjoint pressure-only support and coefficient normalization `1/sqrt(nq)`. Right and transpose nullspace tests pass. Removal is measured on a copy against `256*eps*||b_raw||`; rejected raw vectors remain unchanged. P is checked without applying removal; accepted A vectors are retained after arithmetic-sized removal. |
| Refusal order | Injected P, first-A and second-A failures stop with 1, 2 and 3 completed RHS assemblies respectively, zero attempted primary solves, and no factorization. Later RHSs are unmeasured. |
| Layout/operator invariants | Owned/ghost offsets, sizes, ownership, constraints, matrix digest/state and zero PETSc events are checked at the barrier. Accepted A hashes and operator identity are checked again before their solves. |
| Scope of the oracle | All nine comparisons use an actual assembled 68-by-68 reference-tetrahedron block operator and independent UFL loads. Dense arithmetic is confined to the toy. This does not test the physical 22,900-unknown matrix or the 128-term physical boundary integrals. |

Sources: [observer](evidence/r033/source/presolve.py),
[physical helpers](evidence/r033/source/physical.py),
[actual observer toys](evidence/r033/source/advanced_toys.py), and
[block RHS toys](evidence/r033/source/block_rhs_toys.py).
The q=64/q=96 polynomial projection tests and the q=4 observer oracle cover
different obligations; the observer tests do not secretly evaluate the physical
trace. Saved R020 q64 flux remains motivation, not assembled compatibility.

## Physical path: retained checks and required repairs

The [physical runner](evidence/r033/source/physical.py) retains the exact
482-cell mesh hash, V/Q DOFs 9522/1928, alpha=96, local 500-cell certificate
cap, `C_upper=58.12657123078638` within relative `1e-10`, and positive guarded
beta. It uses the existing direct helper and serial layout, with no dense
global audit. Its manual loads preserve the full complex normal projection,
zero caps, q=64/q=96, 128 terms and batches at most 256 points. Both boundary
load arrays are computed before entering P's helper; the complete lifted RHS
compatibility checks still occur P/A_64/A_96 before any factorization.

The source preserves one shared factorization, one correction per primary,
exact primary essential values, zero constrained correction RHS, residual and
correction consistency `<1e-9`, own-target A divergence `<1e-3`, and essential
residual `<1e-14`. Disk clipping retains exact circular arcs, rejects ambiguous
interior facets and duplicate regions, checks moments/reconstruction and uses
`256*eps*A_out`. Both polar rules, P reproduction within
`2.4719806123e-13 1/m`, all six features, uncorrected/corrected comparisons,
E/D identities, `E5/100` output/correction and `E5/10` load-step screens remain.
Strict magnitude `<5%` and phase `<5 degrees` remain unchanged. Failed accuracy
or component screens are reportable outcomes; failed arithmetic/PDE checks stop
interpretation. A `complete` run status would not mean an accuracy pass.

These checks exist in source; R033 did not execute the physical path. Review
identified the following launch/reporting gaps, not new numerical failures:

| Finding | Evidence and required behavior |
|---|---|
| Stale prerequisite limits | `run_contract.physical` still requires `<60 s` and `<512 MiB`; `toys` and R033's actual policy use 600 s/1536 MiB. Pure predicate evaluation accepts the final 56.251 s/171.24 MiB pass by coincidence, but refuses otherwise valid 61 s or 600 MiB examples. Validate against the declared, reviewed policy and all consumed attempts. Do not edit historical reports to make them fit. |
| Incomplete report binding | The parent checks phase names, top-level status and watch fields, but not each child report/hash or the observer assertions. `verify()` binds current source files to a preflight file, not the submitted success report to those exact sources/environment. Require a versioned evidence manifest, archived source hashes, child report hashes and substantive pass/zero-event assertions. Missing or malformed fields must give a finite refusal before launch. |
| Once-only protection is directory-local | `mkdir(exist_ok=False)` prevents reuse of one output directory, but moving/copying the harness can reset that protection. Keep an explicit consumed-attempt record with the scientific contract ID and source/evidence manifest. Review that record before launch and transfer it between machines. This is coordination, not a distributed lock. |
| Early failures lose report structure | `verify()`, output creation and report parsing precede the parent's refusal boundary. A child killed before its first checkpoint gets only `partial_no_child_report`; a later kill leaves last-checkpoint counts. Initialize the parent report first, preserve the exception and watch, distinguish known zero prelaunch counts from unknown postlaunch counts, and label the last observed stage/counts. Never invent final zero counts after a child started. |
| A primary convergence reason is overwritten | After `ksp.solve(rhs,solution)` the code immediately calls the correction helper; only its later reason is tested. Save and require each primary reason before correction so an unsuccessful A primary cannot be obscured by a successful correction. Preserve the actual returned count even when its reason is nonpositive. |
| Event counts are checked too late | Exact 1 symbolic/1 numeric/6 solve events are asserted at final completion. Add stage-local assertions after each returned primary/correction and checkpoint before later diagnostics. Preserve a pre-solve baseline of 0; after P expect (1,1,1), then solve counts 2,3,4,5,6 with unchanged factor counts/handle/state. Stop immediately on discrepancy. |
| Launch environment/host checks are external | The parent has no current Windows/WSL headroom gate, Windows pressure sampling, or effective-cache check. Its Linux `/proc` monitor is not a Mac monitor. Require the resource/provenance prerequisites below before a later FEM launch; they were not exercised here. |

Sources: [parent](evidence/r033/source/run_contract.py),
[Linux monitor](evidence/r033/source/toy_runner.py), and
[pure predicate evidence](evidence/r067/review.json).
The old standalone physical entry point also contains legacy 60 s/512 MiB
logic. The new copy should have one supported guarded launch path; retain the
archive as history. None of these findings invalidates R033's saved toy pass or
justifies changing a scientific tolerance.

## FFCx form and cache audit

The [upstream v0.10.1 release](https://github.com/FEniCS/ffcx/releases/tag/v0.10.1)
identifies the fix for multiple integrals sharing a quadrature rule. R056 and
R058 already identify the same `0.10.1 pyhbc3ee6d_1` Conda artifact on PC and
Mac. This review additionally hashes the installed PC `representation.py`,
`naming.py`, JIT source and UFCx header against the Conda per-file metadata.
All four match; the IR code accumulates each integrand in the rule's list and
sums the list. The unchanged module string `0.10.0` is not a package downgrade.

[Symbolic inspection](evidence/r067/inspect_forms.py) extracts the pinned SIP
and mode functions and reconstructs the P boundary expression with an abstract
UFL domain and coefficient. It runs compiler **analysis only**: no geometrical
mesh, quadrature-point generation, IR/code generation, C/JIT, assembly or solve.
[Results](evidence/r067/forms.json):

| Inspected form | Raw integrals | After symbolic grouping |
|---|---:|---|
| SIP velocity block | 7 | One integrand each for cell, exterior facet and interior facet; default degrees 2/4/4. |
| P T_00c boundary load | 2 | One exterior-facet integrand, default degree 11. |
| Physical polynomial load check | 1 | One exterior-facet integrand, default degree 4. |
| Reaction verification velocity block | 8 | One integrand per cell/exterior/interior group, default degree 4. |

Thus repeated `ds`/`dS` terms in these forms do not themselves demonstrate the
bug's trigger: they are combined before rule aggregation within an integral
group. Pressure and mass coupling blocks each have one cell integral. Custom
q64/q96 matched loads use NumPy/Basix kernels, not FFCx quadrature selection.
This targeted check does not reproduce every historical UFL object or prove
all possible metadata combinations safe. Keep the patched package.

FFCx's cache key includes the UFL signature, module version, UFCx header,
compiler options and compilation/ABI inputs; it does **not** hash the entire
compiler source or the Conda artifact. Therefore the key alone cannot rule out
reuse across compiler builds sharing those inputs. Installed DOLFINx options
also allow user/current-directory settings to override the cache default;
setting `XDG_CACHE_HOME` alone is not proof of the effective cache location.
These conclusions come from the installed, hash-checked source, not a JIT run.

Both surviving R033 isolated cache inventories (112 files each) still match
their archived hashes. Attempt 4 reused attempt 3's cache, whose creation was
included in R033's consumed budget. The global cache's earliest current mtime
is 2026-09-20 02:33:33 UTC, after the recorded FFCx installation at about
02:00 UTC. That timing supports the installation chronology but cannot prove
which binary every historical solve loaded; exact loaded-module inventories
were not saved. There is no evidence here of an unpatched result, and no
historical physical rerun is warranted. No global cache was modified.

For any later reference/physical task: create a fresh task-local cache, verify
the **effective** DOLFINx options before first form compilation, preserve the
existing compiler options and record package build/artifact hash separately
from module version. Record generated/loaded module filenames and hashes,
compiler/ABI/thread settings and cold/warm status. Fail before compilation if
an override points outside the declared cache. Never transfer compiled caches
between macOS and Linux. An unavailable old cache is not permission to repeat
a once-only experiment; the committed evidence is sufficient for this review.

## Workload and host decision

The intended physical matrix remains 22,900 real unknowns on 482 cells; the
sparsity/factorization method is unchanged. q64/q96 uses 13,312 boundary points
per facet versus 5,120 for q32/q64, a factor of 2.6 in point count. This is not
a runtime multiplier. At q96 the retained BDM2 basis and gradient chunks alone
occupy about 25.31 MiB per facet (`9216*30*(3+9)*8` bytes), plus values, trace
basis, work arrays and compiler/LU memory. Facets are processed sequentially;
reference batches of 256 do not bound the total retained chunk memory.

R020's 59.97 s/757.00 MiB physical stop and R033's 571.42 MiB compilation peak
are useful scale evidence, not a peak forecast for the full q64/q96 path.
Retain 180 s/1536 MiB as the **provisional physical stop limits**, subject to
Astra's launch review and live capacity; no increase or launch is authorized
by this review. The PC's recorded WSL capacity (7.61 GiB) and Windows capacity
(15.72 GiB) are overlapping views. The Mac has 24 GiB installed and verified
native packages/imports/MPI, but no validated FEM process-tree monitor or
matched numerical timing. Remain on PC for repair; there is no performance
basis to move the physical experiment yet.

Before later PC FEM execution, require WSL available RAM at least 4096 MiB
and Windows available physical RAM at least the selected child-tree cap plus
1024 MiB, sampled within 30 s of launch. Do not add host and guest readings
or count swap. During execution keep tree RSS sampling at nominal 0.05 s,
report maximum sample gaps, and sample host pressure at least once per second;
stop if Windows availability falls below 1024 MiB, a required reading fails,
or tree/time limits are crossed. These are prospective resource guard choices,
not physical acceptance thresholds. They need synthetic validation. Mac
execution needs its own validated available-memory definition and process-tree
accounting; this PC review cannot certify it remotely.

## Repeatable reference decision

A limited **assembly/observer reference** is warranted after launch/report
repair and synthetic monitor validation. Use a frozen copy of R033
`advanced_toys.py` and its support modules: four trace/order cases, 16 facet
checks, nine full-block oracle comparisons, compatible P/A/A and three
refusals, with the pre-KSP sentinel and exactly zero factor/solve events.
It uses reference tetrahedra and polynomial data only, no physical cylinder,
Bessel trace, 50 mm problem or q64/q96 physical-attempt allowance. This is a
reference for compiler/assembly portability, not a solver-speed benchmark.

Freeze source and report schema before measurements. Use Python 3.12.13, the
unchanged package pins, one MPI rank, one numerical-library thread, the same
form options and no imported binary cache on either host. Expected outcomes
are the same case/assembly/refusal counts, finite values, correct support and
layouts, right/transpose nullspace passes and zero factor/solve events.
Each host must pass the existing `256*eps` absolute-contribution oracle screens
and `1e-8` flux screen independently. Also preserve numerical oracle operands,
projection/load entries and their absolute-contribution scales. Cross-host
entry differences must be at most `256*eps*(S_PC+S_Mac)` using the corresponding
recorded scales; near-zero values use this absolute screen, never relative
error against a cancelled value. Exact agreement is required for discrete
case/count/constraint inventories. Raw byte/matrix hashes are provenance only,
not cross-architecture accuracy tests. No tolerance may be tuned afterward.

Follow the existing [benchmark protocol](MAC_INSTALL_AND_BENCHMARK_PLAN.md#agent-protocol-for-mac-versus-pc-benchmarks)
for one cold run and three warm repetitions on each host, unique run IDs and
all-attempt cumulative accounting. Provisionally allow 600 s cumulative and
1536 MiB active child-tree RSS per host, with the PC headroom rule above and a
separately validated Mac rule. Stop on any numerical/resource failure; an
extra warm repeat or fresh cache is not an automatic retry. Compare cold JIT
and warm assembly/observer timing separately. No host winner for LU/physical
solves can be inferred from this fixture. A matched solve benchmark and its
cross-host output contract remain a later scientific decision.

The fixture is specified, not implemented or executed here. Archive any new
scalar/vector evidence before transfer; its polynomial inputs regenerate from
frozen source, so no irreplaceable `/tmp` input is required. A later host switch
must follow repository ownership/release rules and does not reset attempts.

## Next task: launch and report repair

Use **GPT-5.6 Luna with medium reasoning on this PC** for one bounded mechanical
repair. The session catalog lists Luna and Astra; the supported efforts were
rechecked with OpenAI Docs ([Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna),
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)). No model
switch, sub-agent or automation was launched.

1. Copy the archived R033 harness into a new disposable task directory and pin
   its source/evidence manifest. Keep old evidence and the 19 production files
   byte-identical. Use Python 3.12.13. Preserve R033's four consumed prerequisite
   attempts/56.25128577899886 s as history and the unused physical allowance;
   a new repair-validation budget does not erase either record.
2. Implement the first six launch/report repairs in the table: one declared
   prerequisite policy, evidence/source binding, consumed-attempt record,
   complete early-refusal/unknown-count reporting, immediate primary convergence
   checks and stage-local factor/solve checks. Keep numerical forms, kernels,
   observer anchor, BCs, q orders and tolerances unchanged. Disable the legacy
   alternate launch path in the new copy. Keep physical execution disabled by
   default pending a later reviewed launch contract.
3. Validate with saved R033 reports and synthetic dictionaries/fake solver
   events: final valid evidence, 61 s and 600 MiB valid-policy cases, true budget
   excess, missing/modified child/source hashes, failed observer flags, nonfinite
   data, wrong root, already-consumed attempt, prelaunch exception, no child
   report, interrupted checkpoint, unsuccessful A primary and unexpected
   factor/solve counts. A successful fake launch must return a labelled sentinel
   before subprocess/FEM execution. Ensure refusal never invokes the real child.
   Fake solver tests supplement the archived actual observer tests; they do not
   claim to revalidate the physical solver. Record which repaired source paths
   remain unexercised by FEM; the later launch review must decide their required
   scoped validation before enabling physical execution.
4. Use a maximum 120 s cumulative/256 MiB for this standard-library validation,
   recording all attempts. No DOLFINx/MPI import, JIT, new mesh, numerical toy,
   physical reference or PDE solve belongs to this repair. If the required fix
   touches numerical semantics or exposes unexplained scientific behavior, stop
   with evidence and recommend Astra/high.
5. Completion is the new guarded source, reproducible focused checks, evidence
   audit, updated continuity, scoped commit/push and stop. Then recommend
   Luna/medium for the separately bounded portable synthetic monitor work if
   only mechanical tasks remain; recommend Astra/high before selecting a FEM
   launch, solving, changing tolerances or interpreting numerical discrepancies.

R067 stops at this review. No repair implementation or benchmark is included.
**Next prompt on the PC: Continue.**
