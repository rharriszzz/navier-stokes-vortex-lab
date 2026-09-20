# Current session handoff

Last updated: 2026-09-20. Latest request:
[R013](REQUEST_LOG.md#r013--2026-09-20--short-continuation-request), completed.
R012 was already committed/pushed as `568c68b`; there were no pending user edits
at R013 start. The current checkpoint records a method review, not a new solve.

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

## Last completed task: method review

R013 completed the [matched-trace method review](docs/realizability/B2_MATCHED_TRACE_REVIEW.md)
and its [read-only evidence appendix](docs/realizability/B2_MATCHED_TRACE_EVIDENCE.md).
It distinguishes the smooth cylinder, the current projected command on a
faceted vessel, and a verification problem prescribing the full complex trace
of the finite 128-term known solution on the same polyhedron. That last problem
has a known continuum solution without volume forcing. Its normal trace is
generally nonzero; a tangential-only substitution is not the same fixture.

The selected next experiment pairs the current command with this trace on the
existing 50 mm alpha=96 operator. Two fixed facet rules check load sensitivity;
cell-aware polynomial disk integration addresses the unresolved polar-rule
effect. The error identity separates matched-problem approximation error from
discrete sensitivity to changed boundary data. It does not identify continuum
geometry error or rule out cancellation from one mesh. A boundary-layer 3D
mesh, symmetry-restricted discretization and enriched/adjoint error study were
compared and deferred with reasons.

R013 checked the embedded R012 report/runner, all 19 source/config hashes and
three evidence-appendix identities, and calculated elementary length/output
scales using only the standard library. Documentation links, anchors, fences,
embedded Python/JSON, scalar consistency and request-history preservation were
checked. No mesh, FEM import, assembly, solve, reference evaluation or stored
field integration ran; no proposed load/output kernel was implemented. No
package, configuration, solver/form, guard, threshold or gate changed. The
review and appendix preserve the specification and read-only evidence;
temporary checks are in `/tmp/navier-b2-method-r013/`.

## Last numerical result (R012; unchanged)

R012 completed the single 50 mm alpha=96 physical T_00c response audit under
the [R009 contract](docs/realizability/B2_ACCURACY_REVIEW.md#one-proposed-experiment-and-next-task).
Read the [result](docs/realizability/B2_PHYSICAL_RESPONSE_AUDIT.md) and
[exact evidence](docs/realizability/B2_PHYSICAL_RESPONSE_EVIDENCE.md).

The prescribed mesh hash, 482 cells, 9,522/1,928 V/Q DOFs and 19 source/config
hashes matched. The local certificate reproduced `C_upper=58.12657123078638`
and beta `0.22187075813338908`. Exactly one primal harmonic solve and one
residual-correction solve used the same factors. PETSc recorded one symbolic
and one numerical factorization, with matrix solves increasing from one to two.
The existing PDE and fixed arithmetic checks pass.

**Physical accuracy fails at all five feature rules.** The finest disk gain is
`-1.6734039795256472 - 1.0983726070219908 i 1/m`, amplitude 28962.6876 times
the independent reference, phase discrepancy 74.1164 degrees. Absolute complex
error is `2.0016562003 1/m`. The residual correction is `2.2498932366e-14 1/m`,
while the finest quadrature step is `2.9156584710e-4 1/m`, 84.37 times the
`3.4556100991e-6 1/m` scale. These are measured corrections/sensitivities, not
error bounds. The combined spatial, geometry/loading and integration error
is unresolved; this is not evidence of physical hardware failure.

The complete physical child took 38.7542 s, with parent-observed and process
peak RSS 753.0508 MiB, below 180 s/1.5 GiB. Maximum sample gap was 0.08138 s.
Both final synthetic watchdog checks passed before the single attempt; there
was no retry or cap increase. All point locations succeeded. Stored-evidence
validation checked eight manifest files, 19 source/config identities, 482 local
trace values, eight coefficient arrays, 30 complex original features and three
sets of 49,152 disk samples. Documentation links, embedded runner/report bytes,
syntax, tables and `git diff --check` were checked.

No package/configuration, solver/form, threshold or guard changed. No full
application, dense/UFL calibration, refinement suite, rendering or encoding ran.
The physical B2 gate remains failed and `campaign_ready=false`; the separate
alpha=96 certificates are still not integrated into schema-3 gate reports.
Alpha=48 remains inconclusive. Force/power and pressure demand remain unassessed.

Evidence is in `/tmp/navier-b2-response-r012/`; the versioned result and appendix
preserve the exact runner and compact numerical evidence independently of those
temporary files. Do not rerun the physical case to reconstruct temporary files
without a new bounded contract. The next task below uses the durable records
and has its own paired-run contract.

## Next task

**GPT-6 Astra, high reasoning:** implement a disposable runner and execute the
[one matched-trace experiment](docs/realizability/B2_MATCHED_TRACE_REVIEW.md#one-executable-next-task-contract)
once. This is proposed, **not already executed**. Read the complete R013 review
and appendix, R012 audit/appendix, R009 error decomposition, R005 method
assumptions, R008 certificates, `STATUS.md` and the four root research documents
(`PROJECT_TRACKS.md`, `EXPERIMENT.md`, `PHYSICAL_REALIZABILITY_PLAN.md`,
`CONTROL_RESEARCH_ROADMAP.md`). The full contract governs these summary points:

- Pin the 19 source/config identities and exact existing 50 mm mesh hash;
  reproduce its 482 cells, V/Q dimensions and local alpha=96 certificate.
  Preserve the 500-cell and 3,000-free-DOF guards. No other physical mesh.
- Implement and check oriented facet L2 normal projection and the matching
  weak tangential load for the full 128-term complex trace. Facet Duffy orders
  are 32 and 64, with at most 256 reference points per batch. Check flux and
  pressure compatibility before projection into the algebraic nullspace.
- Implement cell-aware polynomial integration on the exact disk, with the
  prescribed geometry/moment/orientation checks. Refuse ambiguous positive-area
  coincident facets. Keep the existing polar extractors and report them too.
- Toy checks have a separate 60 s/512 MiB total budget. The physical child is
  parent-monitored from imports through output at **180 s/1.5 GiB**, nominal
  0.05 s samples. Validate the watchdog first. No retry or cap increase.
- One unchanged matrix/factorization serves P, A_32 and A_64, each with one
  homogeneous residual correction: exactly three primary RHSs, three correction
  RHSs and six matrix solves on success. Preserve matrix/factor identities,
  lifting, pressure gauges, physical scaling and fixed PDE/arithmetic checks.
- Report complex error identities and unchanged strict 5%/5-degree comparisons.
  The new load/output/correction component screens qualify this diagnostic;
  they do not replace gate thresholds or certify a total error bound. A failure
  stops at the recorded stage, with partial evidence and no method substitution.

**Completion and stop:** preserve the exact runner and finite JSON report,
including refused/partial results if a prerequisite or cap fails. Interpret only
what the completed checks support, update continuity with one next task,
commit/push under `Continue`, and stop after this single experiment. No
persistent backend/form/mesh-generator change, boundary-layer mesh, alternate
penalty, reduced solver, adjoint, gate integration, campaign, B3 or movie export.
Preserve R/H/nu/f/U, disk, signed features, phasor, acceptance thresholds, failed
physical B2 gate and false readiness. No hardware-feasibility claim follows.

**Following recommendation:** use GPT-5.6 Luna, medium, only for a fully specified
mechanical package, with exact edits, focused checks and a stop before scientific
interpretation. Otherwise retain Astra/high for one bounded unresolved numerical
question. Do not start that following task in the same continuation.

**Availability:** rechecked 2026-09-20 in the session model catalog and fetched
[official Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) pages using the
OpenAI Docs skill. Both model/effort choices are listed; account/client access
may differ. No model switch, delegated session or automation was launched.
