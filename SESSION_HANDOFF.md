# Current session handoff

Last updated: 2026-09-20. Workflow and last completed B2 task:
[R009](REQUEST_LOG.md#r009--2026-09-20--short-continuation-request).

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

**GPT-6 Astra, high reasoning:** implement, run once, and interpret the single
50 mm alpha=96 physical T_00c response audit in the
[R009 next-task contract](docs/realizability/B2_ACCURACY_REVIEW.md#one-proposed-experiment-and-next-task).
Read that review and its exact-runner evidence, R008, the R005 method assumptions,
and the four root research documents (`PROJECT_TRACKS.md`, `EXPERIMENT.md`,
`PHYSICAL_REALIZABILITY_PLAN.md`, `CONTROL_RESEARCH_ROADMAP.md`).

Use a disposable instrumented runner with the existing backend/form. Pin the
19 source/config hashes and the 50 mm mesh hash; verify 482 cells, 9,522/1,928
V/Q DOFs and the local alpha=96 certificate before assembling that same mesh.
Run exactly one physical harmonic solve, then exactly one residual-correction
RHS using its existing factors. Record original/corrected residuals, nullspace
compatibility, absolute disk correction and a signed-feature quadrature sweep
at the five prescribed rules. Compare original gains against the independent
128-term physical reference without changing acceptance thresholds. The review
specifies the matrix/field scaling and report identities to check.

**Limits:** 180 s total child-tree wall time and 1.5 GiB active child-tree RSS,
parent monitored nominally every 0.05 s from imports through output. Validate
the watchdog before the physical attempt. These are conservative stop limits,
not a measured factorization-cost promise. The historical 25 mm run peaked at
6931.1 MiB and 20 mm failed; geometry-only R008 timing predicts no LU cost.
Keep the default 500-cell and dense 3,000-free-DOF guards. Retain R/H/nu/f/U,
fixed disk, signed features, phasor convention and facet-consistent target.
No new solver/form, persistent backend API, mesh sweep, second penalty,
adjoint, boundary-layer implementation, gate integration, campaign or B3.

**Completion and stop:** preserve a complete or explicitly partial/refused
report, exact runner/provenance, checks/skips, and the numerical interpretation.
Stop on identity mismatch, numerical inconsistency, resource cap, or after the
one case; no automatic retry or cap increase. A failed reference comparison is
a useful result. One mesh cannot establish refinement or penalty robustness;
a small residual correction is not a total error bound. Keep the physical B2
gate failed and `campaign_ready=false`. Alpha=96 remains a verification
candidate only on certified geometries; alpha=48 stays inconclusive. Commit
and push the scoped checkpoint under `Continue`, then stop.

**Following recommendation:** use GPT-5.6 Luna, medium, only for a fully
understood mechanical instrumentation/report fix, specifying exact edits,
focused checks, and a stop before interpretation. Otherwise retain Astra/high
for one bounded unresolved numerical-method or scientific question. Do not
start that following task in the same continuation.

**Availability:** checked 2026-09-20 in the session's model catalog and fetched
official [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) pages using the
OpenAI Docs skill. Both named models/efforts are listed; account/client access
can differ. No model switch, delegated session, or automation was launched.

## Last completed work

R009 reproduced the physical disk gain
`2.0662858857221768e-5 - 6.595106312048072e-5 i 1/m`, or a physical rotation
amplitude of `6.911220198253778e-12 1/s`. The 32/64/128-term results coincide
at returned precision. The largest observed radial quadrature discrepancy is
`1.3736273526914378e-18 1/m`; polar feature checks are similarly small. The
series and radial cancellation ratios are only 1.05233 and 1.17288. These are
reference sensitivities, not a certified total FEM error floor.

The review translates the existing 5%/5-degree criteria into absolute complex
error implications without replacing them: `0.05 |G|=3.4556100991268897e-6 1/m`
is sufficient for both comparisons. It separates unknown algebraic, FEM
quadrature, boundary-load, geometry and spatial errors, and explains why the
unit-command solve avoids interpreting tiny physical amplitude as an inherent
roundoff failure. Historical alpha=6 discrepancies remain historical.

Validation: three series, 128 independent coefficient integrals, 21 radial
integrations, five polar feature comparisons, unscaled/scaled Bessel and
summation checks, three stored historical gains, source/report identities,
strict JSON/manifest and documentation checks. Both final synthetic watchdog
checks passed after fixing a self-check directory-creation defect. The two
reference passes totalled 0.8442 s; maximum parent-observed RSS was 66.9063 MiB,
with final process peak 71.7813 MiB and maximum sample gap 0.05342 s, below
120 s/1 GiB. The second parent deadline deducted the first pass's duration.

No numerical source or configuration changed. No mesh, FEM/PDE/UFL/dense test,
harmonic pilot, full application suite, rendering or encoding ran. Physical
accuracy/error floor and production penalty remain unresolved. No certificate
was integrated into the gate; schema-3 response stability still says
`not_assessed` despite the separate R008 alpha=96 evidence.

Evidence: `/tmp/navier-b2-accuracy-r009/`; the versioned
[review](docs/realizability/B2_ACCURACY_REVIEW.md) and
[appendix](docs/realizability/B2_ACCURACY_EVIDENCE.md) preserve reproducible
calculations, quantitative records, source identities and the proposed task.
