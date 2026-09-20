# Current session handoff

Last updated: 2026-09-20. Latest request:
[R021](REQUEST_LOG.md#r021--2026-09-20--short-continuation-request), complete
at the compatibility method-review boundary. R021 starts from `e96f81b`;
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

## Latest result: revised compatibility contract (R021)

Read the [R021 review and subsequent experiment contract](docs/realizability/B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md),
[evidence index](docs/realizability/B2_COMPATIBLE_TRACE_INTEGRATION_EVIDENCE.md),
[saved-data arithmetic](docs/realizability/evidence/r021/review.json), and
[validation](docs/realizability/evidence/r021/validation.json).
Then read the [R020 physical stop](docs/realizability/B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md),
[exact runner](docs/realizability/evidence/r020/physical.py),
[R013 original contract](docs/realizability/B2_MATCHED_TRACE_REVIEW.md), and
R016–R019 results linked from those records. Required research documents remain
`PROJECT_TRACKS.md`, `EXPERIMENT.md`, `PHYSICAL_REALIZABILITY_PLAN.md` and
`CONTROL_RESEARCH_ROADMAP.md`.

R021 verified all 19 production identities, 433 historical evidence files and
564 saved facet records. R020's auditor passed with writes redirected to R021.
Projection mass equations pass the fixed arithmetic scale; saved q32/q64
normal-projection relative L2 steps are 1.3433e-8 real and 1.6209e-10 imaginary.
These are integration sensitivities, not output errors. At A_32's RHS norm,
the pressure arithmetic limit corresponds to a combined flux norm of
2.31849e-20 m³/s. Its saved real flux exceeds this by about eleven times even
though it passes the separate 1e-8 relative flux screen. No new numerical
fixture, method implementation, reference evaluation or physical solve ran.

The selected future experiment uses **fixed Duffy orders 64 and 96**, preserving
the finite 128-term trace, projection/load method, physical parameters and all
thresholds. Check P and both A RHS compatibilities before any primary solve or
factorization. A shared vector-potential/edge-moment alternative was derived
and deferred; do not implement it or select another order after a failure.
Q=64's saved flux remains motivation only: its assembled compatibility is
unmeasured. The new pair is proposed, not validated or implemented.

## Preserved physical limits

R020 remains the latest physical attempt: one mesh, P solve/correction and
checked outputs, then A_32 compatibility refusal before its solve. It took
59.9722 s and 756.9961 MiB; one symbolic/numeric factorization pair and two
matrix solves ran. Its removal norm 5.8560848555e-14 was 11.0906 times the
5.2802161650e-15 limit. No retry followed.

The [R012 audit](docs/realizability/B2_PHYSICAL_RESPONSE_AUDIT.md) remains the
last complete physical response audit. R020's P cell gain reproduces R016:
`-1.6734724052233703 - 1.0983702805959774 i 1/m`, amplitude ratio 28,963.4968
and phase error 74.1175 degrees. Its arithmetic/output screens pass but
reference accuracy fails. No solution coefficient vector was saved.

The paired comparison, continuum geometry/spatial-error allocation and total
FEM error floor remain unknown. Alpha=48 remains inconclusive; certificates
are not integrated into schema-3 gate reports. The physical B2 gate remains
failed and `campaign_ready=false`. Force/power, pressure demand, preparation,
sensing and validated movie flow remain unassessed or unresolved.

## Next task

**GPT-6 Astra, high reasoning:** carry out the
[R021 subsequent experiment contract](docs/realizability/B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md#one-subsequent-experiment-contract).
Implement only a new disposable copy of R020, preserving production and old
evidence. Use q=64/q=96 and the actual repaired lifting helper in a once-only
pre-solve observer at the pinned direct helper's first nullspace removal.
Validate raw P and both A candidates before allowing KSP/factors/solves; retain
accepted A vectors rather than assembling them again after P. Record each raw
candidate and refusal without modifying it to force compatibility.

Under the cumulative 60 s/512 MiB toy cap, retain the five prerequisite phases,
wrong-root/parent refusal and watchdog checks. Add the prescribed high-order
polynomial checks and exercise the actual pre-solve observer on tetrahedral
harmonic blocks, including incompatible P/first-A/second-A paths. Even the
successful toy preparation stops before factorization/solve via a sentinel.
If every prerequisite passes and no scientific choice remains, launch at most
one physical child under 180 s/1536 MiB, serial and single-threaded. Success
inventory is three primaries plus three same-factor corrections, one symbolic
and numeric factorization and six matrix solves. Retain all R013 disk, PDE,
original-feature, reference, component and operator checks as restated in R021.

Completion is the complete comparison or a finite, audited refusal report,
updated continuity, scoped commit/push and stop. Stop at first unexplained
numerical failure, cap or scientific decision. No physical retry, cap increase,
third order, trace/tolerance change, pressure/return-flow repair, new mesh,
gate integration, campaign, B3, rendering or encoding. A failed accuracy result
is useful and does not authorize another case. Any new physical-mesh work
belongs inside the one physical child's cap.

Retain Astra/high for numerical implementation, physical attempts and
interpretation. Recommend Luna/medium only for an understood, fully specified
mechanical follow-up with focused checks and a stop before physical
interpretation. Recheck availability then. Both are in the current session
catalog; OpenAI Docs confirmed supported efforts on the fetched official
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) pages.
No model switch, delegated session or automation was launched.

**Next prompt: Continue.**
