# Current session handoff

Last updated: 2026-09-20. Latest request:
[R019](REQUEST_LOG.md#r019--2026-09-20--short-continuation-request), complete
after the toy portability contract passed. No physical child was launched.
R019 starts from `0e8e421`; `continue` authorizes its scoped commit/push.
The scoped checkpoint `76cfa81` was pushed to `origin/main`; this delivery
confirmation is in the follow-up continuity commit and Git history.

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

## Latest result: toy portability prerequisites pass (R019)

Read the [R019 result](docs/realizability/B2_TOY_PORTABILITY_RESULT.md),
[evidence index](docs/realizability/B2_TOY_PORTABILITY_EVIDENCE.md), and
[validation](docs/realizability/evidence/r019/validation.json). All 19 pinned
production identities matched. In a shallow disposable directory, the wrapper
uses the repository-root working directory, checks source identities before
DOLFINx/MPI imports, and saves a finite early refusal from a wrong root.

The wrong-root report has finite stage/error/count fields and zero physical
counts. The watchdog, 24-permutation/load/kernel fixtures, wrapper grouping and
compatibility fixtures, full block-RHS oracle, and disk fixtures all passed.
The complete parent-monitored sequence took 5.3787 seconds, with 140.5117 MiB
peak observed child-tree RSS and a 0.056605-second maximum sample gap. Including
four earlier failed disposable attempts, recorded parent-monitored time was
6.4805 seconds. Those attempts exposed an output-directory collision and
sandbox MPI/UCX startup failures; their reports and error logs are archived.

A synthetic failed-prerequisite report also verified the parent's refusal path:
it recorded finite zero counts and `child_launched=false`, with no physical
launch record. No mesh, PDE solve, factorization or matrix solve ran. The R016
P-only result and failed physical comparison are unchanged; no A compatibility
or matched-trace response was measured. The physical B2 gate remains failed
and `campaign_ready=false`.

## Preserved physical and toy results

The [R012 audit](docs/realizability/B2_PHYSICAL_RESPONSE_AUDIT.md) remains the
last complete physical response audit. The
[R016 attempt](docs/realizability/B2_MATCHED_TRACE_LIFTING_RESULT.md) completed
P's solve, one same-factor correction and output checks, then failed at A_32
lifting. Its cell-integrated P gain is
`-1.6734724052233703 - 1.0983702805959774 i 1/m`, about 28,963.5 times the
reference magnitude with 74.1175 degrees phase error. It took 59.1795 s and
755.8633 MiB; one mesh, one primary solve, one correction and one factorization
were recorded. No A solve or coefficient vector was saved. Do not rerun old
physical cases to reconstruct missing evidence.

The [R017 repair](docs/realizability/B2_BLOCK_RHS_TOY_REPAIR_RESULT.md)
reproduced block metadata loss on copy/duplicate and passed the factory-created
RHS oracle, layout checks, complete lifting/scatter/assignment, coupling,
compatibility and refusal fixtures on toys. Its cumulative 8.5013 s and
183.2071 MiB were within limits. R018's path failure does not invalidate those
recorded arithmetic checks or validate any physical A result.

The paired accuracy comparison, continuum geometry/spatial-error allocation
and total FEM error floor remain unknown. Alpha=48 remains inconclusive;
certificates are not integrated into schema-3 gate reports. The physical B2
gate remains failed and `campaign_ready=false`. Force/power, pressure demand,
preparation, sensing and validated movie flow remain unassessed or unresolved.

## Next task

**GPT-6 Astra, high reasoning:** review the unchanged R013 physical runner and
the R019 prerequisite evidence against the original contract. Before any launch,
check Git status/history and read the required research documents, R013 contract,
R016–R019 results/evidence and exact physical runner. Reverify all 19 pinned
production identities and the preserved P evidence. Confirm the five toy
phases, wrong-root handling, parent refusal, output limits and unchanged
180 s/1.5 GiB physical caps. If all prerequisites hold and no method,
interpretation or acceptance decision is unresolved, run at most one separate
physical attempt. Stop on the first failure, resource cap or unexplained result;
do not retry, change trace/tolerance/solver, integrate a gate, or begin campaign,
B3, rendering or encoding. If the review finds an unresolved scientific or
numerical choice, record it and stop before launch.

At completion, archive and audit complete or finite partial evidence, update the
log and handoff, commit/push the scoped changes under the next **Continue**, and
stop. Recommend Luna/medium for the following task only if it is an understood
mechanical repair; retain Astra/high if physical interpretation, numerical
method or acceptance thresholds remain. GPT-6 Astra is listed in the current
session catalog, and its official model page supports high reasoning for complex
research and coding ([OpenAI Docs](https://developers.openai.com/api/docs/models/gpt-6-astra)).
No model switch, delegated session or automation was launched.

**Next prompt: Continue.**
