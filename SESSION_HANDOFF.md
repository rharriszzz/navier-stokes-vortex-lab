# Current session handoff

Last updated: 2026-09-20. Latest request:
[R022](REQUEST_LOG.md#r022--2026-09-20--continue-with-overall-progress-in-statusmd),
complete at the toy resource-refusal boundary. R022 starts from `eebc69d`;
the qualified Continue request authorizes its scoped commit/push and requires
the overall progress/remaining-work update in `STATUS.md` before committing.
That update is complete. Actual delivery is recorded in Git history and the
final response.

## User goals

Read [STATUS.md](STATUS.md), including its new overall milestone table. The
user wants to learn whether exterior sensors and actuators can provide an
adequate initial setup for some orders of magnitude of the process, and provide
data for a separate, clear, approximately realistic 3D movie. Initial
preparation and continued driving are distinct. The quantity/range meant by
“orders of magnitude,” preparation tolerances, permitted continued actuation
and adequate sensing remain open. The illustrative movie pipeline is usable;
no physical preparation, attained contraction range or validated movie flow
history is established. We are still verifying numerical boundary responses.

## Reusable continuation request

In a session opened in this repository, say:

> Continue

The [short continuation request in AGENTS.md](AGENTS.md#short-continuation-request)
defines the workflow: log the request, complete the bounded task and checks,
update continuity, commit/push scoped work, and stop. Explicit qualifications
such as “Continue without pushing” override that default. It does not switch
the selected model or schedule another session. No scheduler is installed.

## Latest result: R022 toy memory stop

Read the [R022 result and next contract](docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_RESULT.md),
[evidence index](docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_EVIDENCE.md),
[derived result](docs/realizability/evidence/r022/result.json),
[validation](docs/realizability/evidence/r022/validation.json), and exact
[advanced toy source](docs/realizability/evidence/r022/advanced_toys.py),
[observer](docs/realizability/evidence/r022/presolve.py),
[physical runner](docs/realizability/evidence/r022/physical.py) and
[parent](docs/realizability/evidence/r022/run_contract.py).
Then read the [R021 contract](docs/realizability/B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md),
[R020 physical stop](docs/realizability/B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md),
[R013 original contract](docs/realizability/B2_MATCHED_TRACE_REVIEW.md) and
R016–R019 results linked there. Required research documents remain
`PROJECT_TRACKS.md`, `EXPERIMENT.md`, `PHYSICAL_REALIZABILITY_PLAN.md` and
`CONTROL_RESEARCH_ROADMAP.md`.

R022 preserved all 19 production identities and 440 historical files and
reaudited R021 with writes redirected. The disposable runner implements fixed
q=64/q=96 and a once-only pre-solve observer, checking P and both A candidates
on copies before allowing factorization. Accepted A vectors are retained.
The actual observer path remains unvalidated: its toy cases were not reached.

The first toy attempt exposed a NumPy-Boolean JSON-reporting defect, fixed by
converting `accepted` to built-in bool. Its exact code/reports and 5.239195592 s
are preserved. The second attempt passed wrong-root refusal, all five original
phases, actual parent refusal and 16 high-order polynomial facet checks.
It then hit the 512 MiB child-tree cap at 513.60546875 MiB, before the first
observer case. Cumulative toy time was 16.405468375 s; maximum sample gap was
0.058599793 s. There was no numerical retry after this resource stop.

The final advanced child record is a partial last checkpoint, with all four
trace/order cases and no observer cases. Its 180.66015625 MiB process high-water
value is not the final peak. The parent saw up to four processes. Source order
and a generated C cache artifact suggest compilation contributed, but no
per-process RSS or intervening stage checkpoint identifies the exact cause.
No physical child, factorization, PDE solve or physical trace evaluation ran.

## Preserved physical limits

R020 remains the latest physical attempt: one mesh, P solve/correction and
checked outputs, then A_32 compatibility refusal before its solve. Its required
removal was 11.0906 times the unchanged arithmetic limit. The saved q64 flux
is motivation, not acceptance of an assembled candidate. R012 remains the
last complete physical response audit. R020's P gain is
`-1.6734724052233703 - 1.0983702805959774 i 1/m`, amplitude ratio 28,963.4968
and phase error 74.1175 degrees. Its arithmetic/output checks pass; reference
accuracy fails. No physical solution coefficient vector was saved.

Paired comparison, continuum geometry/spatial-error allocation and total FEM
error floor remain unknown. Alpha=48 remains inconclusive; certificates are
not integrated into schema-3 gate reports. The physical B2 gate stays failed
and `campaign_ready=false`. Force/power, pressure demand, hardware feasibility,
preparation, sensing and validated movie flow remain unassessed or unresolved.

## Next task

**GPT-5.6 Luna, medium reasoning:** carry out only the
[R022 toy-process isolation contract](docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_RESULT.md#next-bounded-task-isolate-toy-processes-and-finish-observer-coverage).
Use a new disposable copy, preserving all prior evidence and production pins.
Split high-order polynomial and harmonic observer fixtures into separate,
sequential children so the former process exits before the latter starts.
Preserve exact mathematics, q64/q96, full lifting oracle and all thresholds;
no compiler-option change or reduced coverage. Add checkpoints around mesh,
form compilation, oracle assembly and observer cases, plus per-process RSS
and executable names at peak/stop in the parent. Keep final parent totals
separate from partial child checkpoints.

Under one cumulative 60 s/512 MiB budget, retain all five original phases,
wrong-root/parent refusals and synthetic watchdogs, both complex polynomial
traces on all four faces at q64/q96, and actual pinned harmonic observer
P/A/A acceptance with a pre-KSP sentinel plus incompatible P/first-A/second-A
cases. Require full block-oracle agreement, once-only observation, expected
layout/nullspace/matrix invariants, unchanged refused raw vectors and zero
factor/solve events. Retain metadata, offset and synthetic lifting refusals.
Count imports, compilation and all attempts; record cache reuse and do not
prewarm outside the cap or edit a global cache to hide the prior failure.
Use the approved serial MPI environment and single-thread libraries.

Completion is a full audited prerequisite pass or finite refusal, updated
continuity, scoped commit/push and stop **before physical execution**. Stop at
the first resource cap, unexplained numerical result or scientific choice;
no retry after a cap, physical child, new order, trace/tolerance/method change,
pressure/return-flow repair, gate integration, campaign, B3, rendering or encoding.
Process isolation may reduce peak memory; it is not a guarantee of success.

After a pass recommend **GPT-6 Astra/high** to review exercised coverage and
the remaining physical path before a separately scoped R021 attempt. If a
cap recurs or a numerical/method issue appears, recommend Astra/high for one
bounded diagnosis from the improved evidence; do not choose new numerical
settings automatically. Retain Luna/medium only for understood mechanical
work. Both models are in the current session catalog; OpenAI Docs fetched the
supported efforts on official [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
and [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) pages.
No model switch, delegated session or automation was launched.

**Next prompt: Continue.**
