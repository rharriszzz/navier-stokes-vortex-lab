# Current session handoff

Last updated: 2026-09-20. Latest request:
[R020](REQUEST_LOG.md#r020--2026-09-20--short-continuation-request), complete
at the physical A_32 pressure-compatibility stop. R020 starts from `847b205`;
`continue` authorizes its scoped commit/push. Actual delivery is recorded in
Git history and the final response.

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

## Latest result: A_32 pressure compatibility fails (R020)

Read the [R020 result and next-task contract](docs/realizability/B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md),
[evidence index](docs/realizability/B2_MATCHED_TRACE_COMPATIBILITY_EVIDENCE.md),
[physical partial report](docs/realizability/evidence/r020/physical/report.json),
[post-stop arithmetic](docs/realizability/evidence/r020/poststop_review.json), and
[validation](docs/realizability/evidence/r020/validation.json).

All 19 pinned production identities and 358 historical files matched. Saved-data
R016–R019 audits passed. The fresh five-phase toy sequence plus wrong-root
probe passed in 5.6300 s, with 144.6055 MiB peak observed child-tree RSS.
R019's parent-refusal evidence was reaudited. The seven runner/support sources
were copied exactly from R019; no numerical code or threshold changed.

One physical attempt took 59.9722 s and 756.9961 MiB. P's primary solve,
one same-factor correction and complete outputs reproduce R016. A_32 then
completed block RHS allocation, loading, lifting, scatter and assignment, but
failed its pressure-compatibility screen before solving. Removal norm
`5.856084855505123e-14` exceeded `5.2802161649827306e-15` by 11.0906 times.
One mesh, one symbolic/numeric factorization pair and two matrix solves ran.
No A solve, A_64 lifting/compatibility, paired comparison or retry followed.

The A_32 real/imaginary flux ratios pass `1e-8`, yet fail the tighter RHS
arithmetic requirement. Saved signed flux divided by `U*sqrt(1928)` predicts
the pressure-constant products within the recorded absolute-flux arithmetic
scale, supporting finite-order trace integration as the cause. A_64's much
smaller saved flux does not demonstrate assembled RHS compatibility or accuracy.
This is a numerical-method review boundary, not a mechanical wrapper repair.

R020 also restored R005's original status line after Git showed R019 had
accidentally overwritten it with its toy outcome. The correction and initial
historical-auditor failure are recorded, and R005's completion notes remain.
Old evidence was not changed; audit-generated writes were redirected to R020.

## Preserved physical limits

The [R012 audit](docs/realizability/B2_PHYSICAL_RESPONSE_AUDIT.md) remains the
last complete physical response audit. R020's P cell-integrated gain remains
`-1.6734724052233703 - 1.0983702805959774 i 1/m`, amplitude ratio 28,963.4968
and phase error 74.1175 degrees. Its arithmetic and output screens pass but
reference accuracy fails. No coefficient vector was saved for later recovery.

The paired accuracy comparison, continuum geometry/spatial-error allocation
and total FEM error floor remain unknown. Alpha=48 remains inconclusive;
certificates are not integrated into schema-3 gate reports. The physical B2
gate remains failed and `campaign_ready=false`. Force/power, pressure demand,
preparation, sensing and validated movie flow remain unassessed or unresolved.

## Next task

**GPT-6 Astra, high reasoning:** perform the
[R020 bounded compatibility method review](docs/realizability/B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md#next-bounded-task-review-compatibility-and-specify-a-revised-fixture).
Read Git status/history, required research documents, the R013 contract,
R016–R020 results and exact sources. Recheck identities and audit saved flux,
normal-projection moments, pressure-nullspace normalization and lifting.
Explain the two compatibility screens and review a future integration strategy
that keeps the same finite reference trace and acceptance thresholds. Compare
higher fixed quadrature with a construction that preserves divergence-free
flux moments; select one justified future contract or record the unresolved
choice. Specify toy coverage, both RHS compatibility checks before primary
solves where practical, output screens, solve/factor counts and resource caps.

This review uses saved data and derivation only: no new physical mesh, FEM
assembly/solve, reference evaluation, quadrature sweep, method implementation,
pressure/return-flow repair, relaxed tolerance, gate integration, campaign,
B3, rendering or encoding. Completion is one review and an explicit subsequent
experiment contract, or the precise unresolved decision. Archive/audit the
saved-data work, update continuity, commit/push, then stop at that boundary.

Retain Astra/high for integration choices, physical attempts and interpretation.
Recommend Luna/medium only if the remaining task is a fully specified mechanical
implementation with prescribed checks and a stop before scientific interpretation.
Both are in the current session catalog; supported efforts were rechecked using
OpenAI Docs ([Astra](https://developers.openai.com/api/docs/models/gpt-6-astra),
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)). No model switch,
delegated session or automation was launched.

**Next prompt: Continue.**
