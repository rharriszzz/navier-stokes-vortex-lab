# Current session handoff

Last updated: 2026-09-20. Latest request:
[R015](REQUEST_LOG.md#r015--2026-09-20--short-continuation-request), completed
at the toy-only stopping point. The repaired runner is archived; no physical
matched-trace attempt was run. R014 remains a partial diagnostic after its
post-P-solve instrumentation error. R013 was committed and pushed as `d5a2711`;
R015 was committed and pushed as `5f48dba` on `origin/main`, with a clean tree.

## User goals

Read [STATUS.md](STATUS.md). The user wants to learn whether exterior sensors
and actuators can provide an adequate initial setup for some orders of magnitude
of the process, and provide data for a separate, clear, approximately realistic
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
such as “Continue without pushing” override that default. It does not switch the
selected model or schedule another session. No scheduler is installed.

## Latest task: toy-only wrapper repair (R015)

Read the [R015 result](docs/realizability/B2_MATCHED_TRACE_WRAPPER_REPAIR.md)
and [validation record](docs/realizability/evidence/r015/validation.json).
The disposable R014 runner now groups constraints with `fem.bcs_by_block`,
validates groups/offsets/exterior DOFs before the original helper, and uses the
resulting groups for essential sets, RHS lifting and assignment, set comparison
and residuals. It checkpoints returned solve counts and factor counters
immediately, and persists pre-removal compatibility diagnostics before
refusing an RHS.

The final tetrahedron check passed for separate real/imaginary BDM2/DG1 spaces:
24 exterior and six free interior velocity DOFs per velocity block, no pressure
constraints, correct offsets and disjoint sets. Exact assignment passed for
zero and nonzero complex targets. Missing/wrong-space groups refused, and
synthetic compatibility/bookkeeping errors preserved finite partial reports.
Eight monitored attempts totaled 3.7696 seconds, maximum observed child-tree
RSS 180.5742 MiB, and maximum sample gap 0.056968 seconds, under 60 s/512 MiB.
The final run passed. All 19 pinned production identities match; the read-only
R014 audit passed for 27 archived artifacts. No physical mesh, factorization,
PDE solve, or retry ran. Exact code and all attempt evidence are under
`docs/realizability/evidence/r015/`.

The staged whitespace check has one documented exception: the exact copied
support file `evidence/r015/toy_runner.py` has a trailing blank line at EOF
(line 213), preserved for byte fidelity. All other staged files pass.

The R014 [result](docs/realizability/B2_MATCHED_TRACE_RESULT.md) remains
partial: its one 50 mm physical child ran 54.1700 s and peaked at 734.7539 MiB,
then its wrapper failed while collecting constraints after the original P
solve. It recorded one returned P solve, zero corrections and zero matched-trace
solves. No A compatibility, matched-trace solve, corrected output or new gain
was reached. Do not rerun that physical case to recreate archived evidence.

## Last complete physical accuracy result (R012; unchanged)

Read the [R012 audit](docs/realizability/B2_PHYSICAL_RESPONSE_AUDIT.md) and
[evidence](docs/realizability/B2_PHYSICAL_RESPONSE_EVIDENCE.md). The finest
polar gain was `-1.6734039795256472 - 1.0983726070219908 i 1/m`, with amplitude
28962.6876 times the reference and 74.1164 degrees phase error. Physical
accuracy failed at all five rules. The correction was tiny, while polar
integration remained unresolved at the reference scale. R014 supplies no
replacement accuracy result or geometry/spatial-error allocation. Alpha=48
remains inconclusive; certificates are not integrated into schema-3 gate
reports. Force/power, pressure demand, preparation, sensing and validated movie
flow remain unassessed or unresolved.

## Next task

**GPT-6 Astra, high reasoning:** review the repaired disposable runner and
conduct the single R013 matched-trace attempt specified by the
[R013 review](docs/realizability/B2_MATCHED_TRACE_REVIEW.md#one-executable-next-task-contract),
under that contract's original prerequisites, caps, checks and stops. Before
acting, read `STATUS.md`, `PROJECT_TRACKS.md`, `EXPERIMENT.md`,
`PHYSICAL_REALIZABILITY_PLAN.md`, `CONTROL_RESEARCH_ROADMAP.md`, the R013 review,
the R014 result/evidence index, and the R015 result/archive. Check Git status and
the existing request/history outcomes first.

- Validate the repaired runner and unchanged production identities. Preserve
  the exact repaired copy and R014 evidence.
- Toy execution remains capped at 60 s/512 MiB total. The single physical child
  remains capped at 180 s/1.5 GiB. No retry, cap increase or second mesh.
- Keep the fixed 50 mm mesh, forms, penalty, thresholds, boundary trace,
  correction count and interpretation rules from the R013 contract. A toy pass
  does not establish physical correctness.
- Stop on any prerequisite/integrity inconsistency, compatibility or PDE check
  failure, resource limit, or completion. Preserve partial evidence. Do not
  start a refinement, campaign, B3, gate integration, rendering or movie export.

The review specifies a finite task; do not choose new physics, solver,
actuator, sensing or acceptance assumptions. A scientific assumption or
threshold decision requires stopping for review. At completion, record evidence,
changed files, checks/skips and the next bounded task, then commit/push scoped
work under `Continue`.

The current official OpenAI model page lists GPT-6 Astra and supports `high`
reasoning for complex reasoning and coding; account access can differ. This is
a recommendation only. No model switch, physical attempt or automation has
occurred. See [OpenAI Docs: GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra).

**Next prompt: Continue.**
