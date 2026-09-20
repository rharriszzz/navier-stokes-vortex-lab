# Current session handoff

Last updated: 2026-09-20. Latest request:
[R012](REQUEST_LOG.md#r012--2026-09-20--short-continuation-request), completed.
The R010 status report was already committed/pushed in R011 (`b84b2c5`, with
publication log `339b3ee`); there were no pending user edits at R012 start.

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

## Last completed task

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
without a new bounded contract. The next task below uses the durable records.

## Next task

**GPT-6 Astra, high reasoning:** complete the
[geometry and boundary-layer accuracy method review](docs/realizability/B2_PHYSICAL_RESPONSE_AUDIT.md#next-bounded-task-design-a-geometry-and-boundary-layer-accuracy-test).
The deliverable is **one selected affordable experiment contract**, not another
physical run. Read the audit/appendix, R009 error decomposition, R005 method
assumptions, R008 certificates, `STATUS.md` and the four root research documents
(`PROJECT_TRACKS.md`, `EXPERIMENT.md`, `PHYSICAL_REALIZABILITY_PLAN.md`,
`CONTROL_RESEARCH_ROADMAP.md`).

Use existing source/reports and elementary scale/cost calculations. Distinguish
the smooth-cylinder reference boundary problem from the faceted/projection
problem. Compare an existing-form 3D boundary-layer mesh, a separate
symmetry-restricted diagnostic, and an output-weighted residual approach. State
assumptions and alternatives before selecting one proposed test; no new method
silently replaces the backend. Specify equations and physical boundary data,
identity/configuration checks, appropriate reference and feature integration,
mesh-specific stability evidence, resource limits and failure interpretation.
The 753 MiB coarse cost and historical 6931 MiB 25 mm cost do not predict a
safe factorization for a new mesh.

**Completion and stop:** publish the reviewed experiment contract, or explicitly
record the missing decision if none is defensible. No new mesh, assembly, PDE
solve, reference sweep, field reintegration, solver/form implementation, adjoint,
boundary-model change, gate integration, campaign or B3 in this review. Preserve
R/H/nu/f/U, fixed disk, signed features, phasor, acceptance thresholds, default
500-cell and 3,000-free-DOF guards, failed physical B2 gate and false readiness.
Update continuity, commit/push under `Continue`, then stop before executing the
proposed experiment. Do not infer preparation, sensing or movie-data feasibility.

**Following recommendation:** use GPT-5.6 Luna, medium, only for a fully specified
mechanical package, with exact edits, focused checks and a stop before scientific
interpretation. Otherwise retain Astra/high for one bounded unresolved numerical
question. Do not start that following task in the same continuation.

**Availability:** rechecked 2026-09-20 in the session model catalog and fetched
[official Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) pages using the
OpenAI Docs skill. Both model/effort choices are listed; account/client access
may differ. No model switch, delegated session or automation was launched.
