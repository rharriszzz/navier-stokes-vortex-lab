# Current session handoff

Last updated: 2026-09-20. Latest request:
[R014](REQUEST_LOG.md#r014--2026-09-20--short-continuation-request), completed at
the prescribed internal-error stopping point. The numerical experiment is
partial. R013 was committed/pushed as `d5a2711`; R014 began with a clean worktree.

## User goals

Read [STATUS.md](STATUS.md). The user wants to learn whether exterior sensors
and actuators can provide an adequate initial setup for some orders of magnitude
of the process, and to provide data for a separate clear, approximately realistic
3D movie. Distinguish initial preparation from continued driving. The quantity
and range meant by “orders of magnitude,” physical preparation tolerances,
permitted continued actuation and adequate sensing remain open. Rest-Stokes
verification does not demonstrate those goals or a validated movie trajectory.

## Reusable continuation request

In a session opened in this repository, say:

> Continue

The [short continuation request in AGENTS.md](AGENTS.md#short-continuation-request)
defines the workflow: log the request, complete the bounded task and checks,
update continuity, commit/push scoped work, and stop. Explicit qualifications
such as “Continue without pushing” override that default. It does not switch
the selected model or schedule another session. No scheduler is installed.

## Last task: partial matched-trace attempt

Read the [R014 result](docs/realizability/B2_MATCHED_TRACE_RESULT.md) and
[evidence index](docs/realizability/B2_MATCHED_TRACE_RUN_EVIDENCE.md). The single
physical child ran 54.1700 s, with 734.7539 MiB parent/process peak RSS and a
0.060411 s maximum sample gap, below 180 s/1.5 GiB. No retry or cap increase.

All 19 source/config identities and the exact 50 mm mesh matched: 482 cells,
9,522/1,928 V/Q DOFs, 282 exterior facets, hash
`423ab057c5738ae3e2dcef6e82c238ee7e61bc1d0af7f1e212d04b8a2cd6bfb4`.
The 500-cell local certificate reproduced C_upper `58.12657123078638` and
alpha=96 beta `0.22187075813338908`. Both facet orders assembled; their
real/imaginary closed-flux ratios passed the unchanged 1e-8 ceiling.

Completed toy checks include all 24 tetrahedron vertex permutations and 30 P2³
vector traces, exact-circle moments/arcs/jumps/tangencies, and polynomial
reconstruction/restriction fixtures. Their shared measured duration was
4.4804 s, with 141.5508 MiB maximum parent RSS, below 60 s/512 MiB. Physical
polynomial loads agreed with UFL. The disk partition has 11 positive-area
regions and correct moments through degree three; no coincident interior facet
was found. These are geometry/load checks, not solved-field accuracy evidence.

The original P solve returned with the same diagnostics as R012 except timing.
The next wrapper operation used `bc.function_space == spaces[i]`, comparing
C++ and Python space objects; its filter was empty and concatenate raised
`ValueError: need at least one array to concatenate`. This is an instrumentation
bug. Recorded counts: one primary solve, zero corrections, zero matched-trace
solves. The last checkpoint stage still names P assembly; the traceback records
the subsequent failed constraint collection. Matrix/factor hashes and event
counters were not reached. No fields were saved for later gain recovery.

A lifting/pressure compatibility, solved-field reconstruction/integration,
all six features at the two rules, error identities and physical/component
comparisons are unexecuted. The report has no new gain. Do not claim those
checks passed or label the error a failed physical matched-trace comparison.
The exact failed runner is preserved, including its unvalidated later code.

The standard-library stored-data audit checks 27 archived artifacts, 19 source
identities, 482 certificate values, 564 facet projection equations/flux reductions,
11 disk regions, UFL comparisons and P diagnostics. Evidence is durable under
`docs/realizability/evidence/r014/`; original temporary files are in
`/tmp/navier-b2-matched-r014/`. Do not rerun a physical case to recreate them.
The result/evidence index explains hashes and lossless JSON whitespace compaction.
No production package/configuration, solver/form, threshold, default guard or
gate changed. No full application, dense/refinement suite, rendering or encoding
ran. The physical B2 gate remains failed and `campaign_ready=false`.

## Last complete physical accuracy result (R012; unchanged)

Read the [R012 audit](docs/realizability/B2_PHYSICAL_RESPONSE_AUDIT.md) and
[exact evidence](docs/realizability/B2_PHYSICAL_RESPONSE_EVIDENCE.md).
The finest polar gain was `-1.6734039795256472 - 1.0983726070219908 i 1/m`,
with amplitude 28962.6876 times the reference and 74.1164 degrees phase error.
Physical accuracy failed at all five rules. The correction was tiny, while
polar integration remained unresolved at the reference scale. R014 supplies
no replacement accuracy result or geometry/spatial-error allocation. Alpha=48
remains inconclusive; certificates are not integrated into schema-3 gate reports.
Force/power, pressure demand, preparation, sensing and validated movie flow remain
unassessed or unresolved.

## Next task

**GPT-5.6 Luna, medium reasoning:** complete the
[toy-only wrapper repair](docs/realizability/B2_MATCHED_TRACE_RESULT.md#next-bounded-task-repair-wrapper-instrumentation-on-toy-data-only).
Read that full five-step contract and the exact failed runner first. Also read
`STATUS.md`, the R013 review, and the four root research documents required by
`AGENTS.md`. Preserve the archived R014 attempt; make a new disposable copy.

- Replace all three direct C++/Python space comparisons with
  `fem.bcs_by_block`; use the resulting groups for constraints and residuals.
  Check nonempty velocity/empty pressure groups, offsets, disjoint sets and
  equality to independently located exterior DOFs before entering the solve.
- Persist returned-solve counts and factor counters before further bookkeeping;
  set accurate operation stages. Persist pre-removal compatibility numbers
  before rejecting a RHS, including the currently unexecuted A failure path.
- Use one reference tetrahedron, distinct real/imaginary BDM2/DG1 spaces,
  zero/nonzero targets and intentional missing/wrong-space groups. Check 24
  exterior DOFs per velocity block, six free interior velocity DOFs and zero
  pressure constraints. Test exact assignment and unchanged sets. Exercise
  failure reporting with synthetic bookkeeping/compatibility cases.
- Parent-monitor all toy execution at **60 s/512 MiB total**. No physical
  cylinder, global factorization or PDE solve, no physical retry or threshold
  change. Preserve the numerical source identities and archived evidence.

**Completion and stop:** preserve the exact repaired copy, focused finite toy
report and checks; update request history/handoff; commit/push under `Continue`;
stop before a physical attempt or scientific interpretation. On failure preserve
partial evidence; do not silently change the boundary method or screen.

**Following recommendation:** after focused checks pass, recommend **GPT-6 Astra,
high**, to review the repaired runner and conduct a separately authorized R013
experiment under all original caps, checks and stop conditions. No model switch
or run occurs automatically. Retain Luna/medium only for another fully understood
mechanical defect with exact checks; use Astra/high if scientific assumptions,
thresholds or numerical interpretation require a decision. The A pressure screen
and physical output path have not been validated merely by fixing grouping.

**Availability:** rechecked 2026-09-20 in the session model catalog and fetched
[official Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) and
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) pages with
OpenAI Docs. Both model/effort choices are listed; account access can differ.
No switch, delegation or automation was launched. Next prompt: **Continue**.
