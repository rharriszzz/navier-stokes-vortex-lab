# Current session handoff

Last updated: 2026-09-20. Workflow: [R003](REQUEST_LOG.md#r003--2026-09-20--short-continuation-request).
Current B2 task: [R004](REQUEST_LOG.md#r004--2026-09-20--short-continuation-request).

## Reusable continuation request

In a session opened in this repository, say:

> Continue

The [short continuation request in AGENTS.md](AGENTS.md#short-continuation-request)
defines the full workflow: log the request, complete the bounded task and its
checks, update Markdown and the next model's handoff, commit, push, and stop.
An explicit qualification overrides the default, such as “Continue without
pushing.” The selected model is unchanged by the prompt; choose the recommended
model/effort when starting the session. No scheduler is installed.

## Next task

**GPT-6 Astra, high reasoning:** review and specify one bounded, scalable
stability check for the actual B2 response operators. Begin with the completed
diagnostic evidence in
[B2_CONTINUATION_REVIEW.md](docs/realizability/B2_CONTINUATION_REVIEW.md#2026-09-20-implementation-result),
the older stability review, and the four required research documents. Calibrate
the proposed method against the existing dense small-cylinder fixtures before
estimating its use on response meshes. Specify which spectrum/energy property
it certifies, residual and convergence evidence, expected peak memory/runtime,
and failure conditions. Compare sparse constrained eigenanalysis with a
sufficient coercivity certificate; do not select a production solver or launch
large response runs.

**Completion:** commit a review document that states the mathematical target,
calibration plan, resource cap, interpretation limits, acceptance evidence,
and a bounded follow-on implementation task. Keep the 3,000-free-DOF dense
audit guard. The physical B2 gate remains failed and `campaign_ready` remains
false.

**Stop:** stop at the method-review boundary. If calibration contradicts the
stored dense fixtures, or a defensible check requires changing the physical
model, boundary data, or thresholds, report the evidence and alternatives for
research review; do not proceed to implementation or a production response
campaign. If work reduces to a clear mechanical correction, recommend GPT-5.6
Luna at medium effort for that narrower fix, with a specific validation and
stop condition.

**Availability:** the official model guide currently lists Astra for Codex and
describes it for complex work; actual access can vary by client/account. Recheck
the [official model guidance](https://learn.chatgpt.com/docs/models) at the next
handoff. The GPT-6 Astra recommendation reflects numerical-method judgment;
choose Luna only for an understood routine correction.

## Last completed work

R001 established request recording and the B2 diagnostic review. R003 defined
the reusable `Continue` workflow including scoped commit/push. R004 implements
the six-step B2 reporting package: strict JSON-safe scalar/feature comparisons,
absolute complex sensitivity fields, independent physical-reference reports,
and explicit campaign blockers. The physical B2 gate remains failed.

Validation for R004: ordinary realizability discovery ran 44 tests (32 passed,
12 optional DOLFINx skips); optional B2 discovery ran 21 tests and passed; CLI
help passed; the bounded alpha=6/48 rejection wrote strict JSON and Markdown,
kept all gates/readiness false, and launched no harmonic pilots or reference
evaluation. `git diff --check` passed. The report evidence is in
`/tmp/navier-b2-next-diagnostic-rejection-r004-final/gate.{json,md}`.

The official model guide was checked on 2026-09-20 and currently lists Astra
and Luna for Codex; account/client rollout can still affect availability.
