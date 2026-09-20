# Current session handoff

Last updated: 2026-09-20. Latest request:
[R016](REQUEST_LOG.md#r016--2026-09-20--short-continuation-request), completed
at the required internal-error stop. One physical child reached P's solve,
correction and output checks, then failed in A_32 RHS lifting. No matched-trace
solve or physical retry occurred. R016 starts from `349c9a3`; scoped commit/push
is authorized by `continue`. Actual delivery is recorded in Git history and
the final response. Prior R014/R015 evidence remains unchanged.

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

## Latest result: RHS lifting failure (R016)

Read the [R016 result](docs/realizability/B2_MATCHED_TRACE_LIFTING_RESULT.md),
[evidence index](docs/realizability/B2_MATCHED_TRACE_LIFTING_EVIDENCE.md), and
[stored-data validation](docs/realizability/evidence/r016/stored_validation.json).
The child code exactly matches the R015 archive. All 19 production identities,
mesh/certificate/load/geometry prerequisites and toy checks passed. One sandbox
MPI import failure preceded approved execution; the total toy time including
that attempt was 5.3733 s, with peak 140.9961 MiB, below 60 s/512 MiB.

The single physical child ran 59.1795 s with 755.8633 MiB observed/process peak
RSS, below 180 s/1.5 GiB. It recorded one mesh, one returned P primary solve,
one residual correction, one symbolic/numeric factorization and two matrix
solves. Matrix digest/state and factor handle/state remained unchanged through
P's correction. All original P diagnostics reproduce R012 except timing.

P's cell-integrated gain is `-1.6734724052233703 - 1.0983702805959774 i 1/m`.
Reconstruction, independent arc evaluation, arithmetic/component screens and
linearity passed for P, its correction and corrected field. Both original polar
rules reproduce R012. The cell-integrated magnitude remains about 28,963.5 times
the reference, with 74.1175 degrees phase error. This is a completed P diagnostic
inside an incomplete paired experiment, not validated physical response data.

The traceback identifies `physical.py:465`, A_32 `apply_lifting`, raising
`AttributeError: 'list' object has no attribute '_cpp_object'`. The saved
`stage=P_outputs` is the last checkpoint. The copied RHS entered DOLFINx's
non-block lifting branch; loss of `_blocks` metadata at `rhs=b.copy()` is the
source/traceback-based diagnosis, still to be reproduced on a toy. R015 checked
BC grouping and NumPy-slice assignment, not this complete PETSc operation.
Neither A pressure compatibility nor any A solve/output was reached. No
coefficient vectors were saved. Do not rerun this physical case to reconstruct
missing evidence.

The standard-library audit passed for 48 archived artifacts, 79 prior R014/R015
files, four earlier appendices, 19 production identities, 564 facet projection
records, disk moments, P measurements and stop counts. Changed files are the
request log, this handoff, status/track summaries, relevant B2 navigation,
the new R016 result/index and `docs/realizability/evidence/r016/`. Full application,
dense/calibration/refinement suites, rendering and encoding were skipped.
The staged whitespace check has four byte-preservation exceptions:
`evidence/r016/toy_runner.py:213` (blank line at EOF) and
`evidence/r016/toys/kernels.stderr:3`, `:4`, `:5` (raw MPI error trailing spaces).
All other staged files pass; the whole-archive whitespace check does not pass.
Documentation validation passed for 13 Markdown files, 137 local links/anchors,
20 fenced blocks and nine Python sources; earlier request history is preserved.

## Scientific limits retained

The [R012 audit](docs/realizability/B2_PHYSICAL_RESPONSE_AUDIT.md) remains the
last complete physical response audit. R016 adds a checked P disk integral but
no matched-trace accuracy comparison or continuum geometry/spatial-error
allocation. The finest polar gain still differs from the cell integral by
19.8128 times the 5% reference scale. A tiny correction does not establish
spatial convergence. Alpha=48 remains inconclusive; certificates are not
integrated into schema-3 gate reports. The physical B2 gate remains failed and
`campaign_ready=false`. Force/power, pressure demand, preparation, sensing and
validated movie flow remain unassessed or unresolved.

## Next task

**GPT-5.6 Luna, medium reasoning:** complete the
[R016 toy-only block RHS repair contract](docs/realizability/B2_MATCHED_TRACE_LIFTING_RESULT.md#next-bounded-task-exercise-and-repair-block-rhs-lifting-on-toys).
Before acting read `STATUS.md`, `PROJECT_TRACKS.md`, `EXPERIMENT.md`,
`PHYSICAL_REALIZABILITY_PLAN.md`, `CONTROL_RESEARCH_ROADMAP.md`, the R013 contract,
and R014–R016 result/evidence records. Inspect Git status and history first;
the initial R015 log entry lacks its outcome, but its completed result and
commits (`5f48dba`, `349c9a3`) establish that the earlier grouping task is done.

- Work on a new disposable copy. Reproduce copy/duplicate metadata behavior on
  one reference tetrahedron; create the replacement block RHS through the
  DOLFINx vector factory and validate all owned/ghost offsets before lifting.
- Exercise the actual loading/lifting/scatter/assignment helper on zero and
  nonzero complex targets, with pressure and real/imaginary cross-block coupling.
  Compare against independent toy operator arithmetic, preserving the original
  forms, trace, constraints and all tolerances in the physical runner.
- Add accurate pre-operation stages and layout/failure records; check compatible
  and incompatible pressure fixtures and the R015 grouping/refusal fixtures.
- All toy execution, including failures, stays within 60 s/512 MiB total,
  serial and single-threaded, using approved access needed by MPI. No physical
  cylinder, factorization, PDE solve, physical retry or cap increase.
- Completion: exact repaired copy and finite passing toy report, unchanged
  production/prior-evidence identities, updated continuity and scoped commit/push.
  Stop on a resource limit, unexplained inconsistency, scientific decision or
  completion. No campaign, B3, gate integration, rendering or movie export.

After the mechanical checks pass, recommend **GPT-6 Astra, high reasoning**
for review of the remaining A path and one separately scoped R013 attempt with
its original prerequisites/caps/stops. Retain Luna/medium only for a fully
understood mechanical defect; refer scientific assumptions or threshold changes
to Astra/high. A toy pass alone never authorizes physical interpretation.

Both recommendations were rechecked against the session catalog and fetched
[OpenAI Docs: Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
and [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) pages.
This is a recommendation only, not a model switch or scheduled continuation.

**Next prompt: Continue.**
