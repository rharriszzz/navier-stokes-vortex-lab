# R020 matched-trace attempt: pressure compatibility stop

Recorded 2026-09-20 for [R020](../../REQUEST_LOG.md#r020--2026-09-20--short-continuation-request)
from `847b205`, under the unchanged
[R013 contract](B2_MATCHED_TRACE_REVIEW.md#one-executable-next-task-contract).
The [evidence index](B2_MATCHED_TRACE_COMPATIBILITY_EVIDENCE.md) links exact
sources, prerequisite reports, the physical partial report and saved-data audit.

## Outcome

**The paired diagnostic remains incomplete.** The repaired wrapper completed
A_32 RHS allocation, layout validation, loading, lifting, reverse scatter and
boundary assignment, then stopped at `A_32_primary_rhs_compatibility` before
its solve. The required pressure-constant removal was **11.0906 times** the
unchanged `256*eps*||b||` limit. This is a measured numerical compatibility
failure, rather than the previous wrapper/API failures.

One physical child ran for **59.9722 seconds**, with **756.9961 MiB** peak
observed child-tree RSS, within 180 s/1.5 GiB. It created one 482-cell mesh,
returned one P primary solve and performed one same-factor correction: one
symbolic factorization, one numeric factorization and two matrix solves.
Neither A solve ran. No retry, new quadrature order, tolerance adjustment,
return-flow repair or changed trace followed the stop. The physical B2 gate
remains failed and `campaign_ready=false`.

## Compatibility evidence

Both facet rules assembled all 282 exterior facets before P's solve. Their
projected normal fluxes passed the existing relative `1e-8` screen, but that
screen does not imply arithmetic compatibility of the lifted block RHS.

| Quantity | A_32 real | A_32 imaginary |
|---|---:|---:|
| Signed projected flux (m³/s) | 2.571353564e-19 | 2.336108895e-22 |
| Absolute projected flux (m³/s) | 8.459460469e-10 | 1.417029064e-10 |
| Closed-flux ratio | 3.039618866e-10 | 1.648596316e-12 |
| Pressure-constant product before removal | 5.856082051e-14 | 5.322894013e-17 |

The RHS Euclidean norm was `0.09289054512910896`. The recorded removal norm
was `5.856084855505123e-14`, exceeding the fixed tolerance
`5.2802161649827306e-15`; removal/RHS was `6.304285164185145e-13`.
These are algebraic quantities in the normalized system, not SI pressure
measurements. The helper saved the products and removal norm, then refused
the candidate RHS. No solve used the incompatible or projected candidate.

The replacement RHS exactly matched P's MPI vector type, 22,900 owned/global
entries, ownership range, owned offsets `[0,9522,11450,20972,22900]`, ghost
offsets and array size. Pressure rows participated in lifting. The constraint
sets matched P, with 1,692 prescribed exterior DOFs in each velocity block and
none in pressure. The R017 metadata repair reached its intended operation.

The pinned [direct helper](../../realizability/backends/fenicsx_stokes.py)
normalizes a pressure coefficient vector of ones. For 1,928 DG1 pressure
DOFs its norm is `sqrt(1928)`. The pressure row has sign `-div(u)`; after
lifting, its constant product is predicted by the signed boundary flux as

```text
pressure product = signed_flux_si / (U * sqrt(1928)),  U = 1e-7 m/s.
```

Saved-data arithmetic predicts real/imaginary products
`5.8560972724e-14` and `5.3203422193e-17`. Their discrepancies from the
measured products are `1.5221116456e-19` and `2.5517937565e-20`, below
`256*eps` times the corresponding absolute-flux scales. This agreement,
together with A_64's much smaller saved net flux, supports finite-order trace
integration as the cause. It is an inference from stored fluxes and the
unchanged assembly, not a new integration or proof of a total error bound.

A_64's saved real/imaginary closed-flux ratios are `1.357980991e-16` and
`1.935054430e-16`. **A_64 lifting and pressure compatibility were not reached.**
Its small flux does not establish a compatible assembled RHS, a successful
solve or an accurate response. The prescribed comparison of two loads cannot
be replaced after seeing the A_32 failure.

## Completed checks and preserved P result

The review verified all 19 production identities and 358 historical evidence
files. R016–R019 saved-data auditors passed with their writes redirected into
the new work directory, preserving the old archives. The exact seven R019
runner/support sources were copied to `/tmp/navier-b2-matched-r020/`.

The fresh prerequisite sequence passed the wrong-root refusal, synthetic
wall/RSS watchdog, 24-permutation load/kernel fixtures, wrapper grouping and
compatibility checks, full block RHS oracle, and extra disk fixtures. It took
**5.6300 seconds**, with **144.6055 MiB** peak observed RSS and maximum sample
gap **0.057955 s**, below 60 s/512 MiB. The unchanged parent's finite refusal
path was checked through R019's preserved evidence and source review. The
approved MPI environment was used; no sandbox MPI failure occurred.

The physical mesh hash, 9,522/1,928 V/Q DOFs, 22,900 block unknowns and local
certificate reproduce R016. `C_upper=58.12657123078638`, with positive guarded
beta at alpha=96. Physical polynomial loads agree with UFL. All 482 cells
were visited for the disk partition, with 11 positive-area regions, correct
moments and no ambiguous coincident interior facet. Both facet files, the
local bound and the disk regions reproduce R016 as parsed data, apart from
the local bound's elapsed time.

P's complete saved output object equals R016 exactly, including the primary,
correction and corrected cell integrals, both original six-feature rules,
reconstruction/arc checks, residuals, matrix digest and factor-state checks.
Its cell-integrated gain remains
`-1.6734724052233703 - 1.0983702805959774 i 1/m`, amplitude ratio **28,963.4968**
and phase error **74.1175 degrees** against the reference. The strict
5%/5-degree comparison fails. No A gain, paired error identity, boundary
sensitivity or continuum geometry allocation can be inferred.

The physical watchdog collected 1,096 samples with maximum gap **0.059125 s**;
process high-water RSS was also **756.9961 MiB**. Sampling does not provide an
instantaneous memory bound. Exact timers, versions, hashes, limits, projection
moments and sampled boundary speed/displacement/acceleration are archived.
Force/power, pressure demand, physical preparation, sensing and validated movie
flow remain unassessed or unresolved.

## Continuity correction and validation

The first historical audit exposed an unrelated documentation error in R019:
commit `76cfa81` replaced R005's original status line with R019's toy outcome.
R020 restored that exact line from `0e8e421` and appended a dated correction.
R005's completion notes remain intact. No numerical prerequisite had run when
this was corrected. The subsequent static review and all four historical
auditors passed. The initial failure is explicitly preserved in the
[correction record](evidence/r020/continuity_correction.json).

The [R020 audit](evidence/r020/audit.py) checks exact sources, historical
preservation, all finite JSON, resource records, stop inventory, unchanged
P outputs, failed A_32 compatibility and the saved flux prediction. It also
checks Python syntax and local documentation links. Its
[validation record](evidence/r020/validation.json) distinguishes a successful
evidence audit from the failed physical diagnostic.

Skipped after refusal: both A solves/corrections, their PDE/trace/output
checks, A_64 RHS compatibility, paired comparisons and load-output sensitivity.
No coefficient vector was saved for later field recovery. Full application,
dense/calibration/refinement suites, production changes, gate integration,
campaign, B3, rendering and encoding were outside scope.

## Next bounded task: review compatibility and specify a revised fixture

Recommend **GPT-6 Astra, high reasoning** for one method review, using saved
data and pinned source only. This is a scientific integration/compatibility
decision, not an understood mechanical repair.

1. Recheck identities, R013's trace and normalization, R020's actual lifting
   path, and the relation between constant pressure products and projected
   flux. Audit saved A_32/A_64 moments and cancellation scales without rebuilding
   the mesh, reevaluating the reference or assembling another physical RHS.
2. Explain why the relative flux screen and the arithmetic RHS screen give
   different outcomes. Preserve both thresholds. Review alternatives for a
   future compatible trace-integration comparison, including higher fixed
   quadrature and a construction that preserves the divergence-free trace's
   flux moments. Identify each alternative's error, implementation and resource
   implications; smaller saved A_64 flux alone is not acceptance evidence.
3. Select and state one justified future experiment contract or record the
   specific unresolved decision. Keep the finite 128-term continuum trace,
   physical parameters, strict accuracy thresholds and failed gate explicit.
   Any changed integration prescription must be reviewed as a new contract;
   do not hide incompatibility with pressure projection, return flow, relaxed
   tolerances, changed boundary data or a post-result choice of outputs.
4. Specify toy coverage, pre-solve compatibility checks, finite failure reports,
   output screens, solve/factor inventory and resource caps before proposing
   a subsequent run. Consider checking both candidate RHS compatibilities
   before any primary solve, so another known refusal does not repeat P.
   Do not implement the method or launch numerical fixtures in this review.
5. Archive saved-data calculations and the derivation, update continuity,
   commit/push under Continue, and stop at the method-review boundary. No
   physical retry, new mesh, reference sweep, gate integration, campaign, B3
   or movie work is included.

Retain Astra/high for interpretation, integration choices and physical runs.
Recommend Luna/medium only when that review leaves a fully specified mechanical
implementation with explicit checks and a stop before physical interpretation.
Both are listed in the current session catalog; their supported efforts were
rechecked using OpenAI Docs ([Astra](https://developers.openai.com/api/docs/models/gpt-6-astra),
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)). No model switch,
delegated session or automation was launched. **Next prompt: Continue.**
