# Current session handoff

Last updated: 2026-09-20. Workflow: [R003](REQUEST_LOG.md#r003--2026-09-20--short-continuation-request).
Last completed B2 task: [R005](REQUEST_LOG.md#r005--2026-09-20--short-continuation-request).

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

**GPT-5.6 Luna, medium reasoning:** implement the separate `b2-coercivity`
diagnostic specified in
[B2_SCALABLE_STABILITY_REVIEW.md](docs/realizability/B2_SCALABLE_STABILITY_REVIEW.md#bounded-follow-on-implementation).
Read that review, its calibration appendix, the previous stability/report
reviews, and the four required research documents before coding. The formula,
numerical guards, report states, validation cases, and resource caps are fixed
in the review. This is a sufficient local energy certificate: an inconclusive
bound does not prove instability or authorize changing the penalty.

**Completion:** implement the optional command and strict JSON/Markdown reports;
validate geometry formulas and small-cylinder agreement with independent UFL
assembly and the dense fixtures; run ordinary realizability and optional B2
discovery, CLI help, and only the 100/70/50 mm local diagnostic. Enforce the
500-cell, 120 s, 1 GiB limits for that diagnostic's verification run. Keep the
separate dense regression below 3,000 free DOFs (180 s/1.5 GiB budget). Record
checks/skips, evidence, and source/mesh hashes; update documentation, commit,
and push under the new `Continue` request. Keep `b2-gate` integration for a later
review: its actual response-mesh stability remains `not_assessed`, the physical
B2 gate remains failed, and `campaign_ready` remains false.

**Stop:** stop after this diagnostic and its checks, even if the 50 mm result
is inconclusive. No harmonic pilot, sparse production factorization, larger
mesh run, physical-parameter change, or threshold relaxation belongs here.
Stop earlier with evidence if calibration contradicts the bound, assumptions
fail, or a resource cap is exceeded. Recommend **GPT-6 Astra, high reasoning**
next to interpret the result and select a bounded actual-mesh stability or
physical-accuracy task. Recommend Luna/medium again only for an understood
mechanical defect, specifying its exact fix, validation, and stop condition.

**Availability:** the [official model guide](https://learn.chatgpt.com/docs/models)
was opened on 2026-09-20 and lists Luna and Astra for Codex. Client/account
availability can vary; recheck at the next handoff. No model switch or new
session was launched by this written recommendation.

## Last completed work

R005 completed the stability-method review at source `21676b9`. The sufficient
local bound certifies alpha=96 at 100 mm and alpha=48/96 at 70 mm. It is
inconclusive for some stable cases, including alpha=48 at 100 mm. The sparse
alternative counted all 67 negative constrained modes for alpha=6 on 100 mm
and none for alpha=48; it is not the next implementation package.

Validation: ten dense cases, five targeted time steps, 253 independent local
trace-form comparisons, and six sparse inertia comparisons agreed with their
reference results. The full calibration took 46.86 s / 796.06 MiB peak RSS;
the separate warm local calculation took 0.117 s / 196.74 MiB. Evidence is in
`/tmp/navier-b2-stability-method-r005/{dense,local,local_cost,provenance}.json`;
the versioned calibration appendix preserves reproduction code and provenance.
Local Markdown links/anchors, fenced-block syntax, strict JSON/evidence
consistency, and `git diff --check` passed. Application suites and visualization
checks were skipped because numerical/application source did not change.

Earlier R004 reporting checks remain recorded in `REQUEST_LOG.md` and
`B2_CONTINUATION_REVIEW.md`; do not replay that completed implementation.
