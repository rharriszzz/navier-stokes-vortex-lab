# Current session handoff

Last updated: 2026-09-20. Latest request:
[R017](REQUEST_LOG.md#r017--2026-09-20--short-continuation-request), complete.
The toy-only block RHS repair passed under its cumulative limits. No physical
retry occurred. R017 starts from `a22fc32`; scoped commit/push is authorized by
`continue`. Actual delivery is recorded in Git history and the final response.
R014–R016 evidence remains unchanged.

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

## Previous result: RHS lifting failure (R016)

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

## Latest result: block RHS toy repair (R017)

Read [the R017 result](docs/realizability/B2_BLOCK_RHS_TOY_REPAIR_RESULT.md),
[evidence index](docs/realizability/B2_BLOCK_RHS_TOY_REPAIR_EVIDENCE.md), and
[stored-data validation](docs/realizability/evidence/r017/validation.json).
The single-tetrahedron test reproduced loss of `_blocks` on PETSc copy and
duplicate. The repaired helper creates a replacement from captured spaces,
checks PETSc and owned/ghost layout before loading, and then performs the actual
block lift, reverse scatter and grouped assignment. Zero and nonzero complex
targets matched the independent toy operator oracle; pressure and
real/imaginary cross-blocks were nonzero, the operator remained unchanged, and
exact boundary assignment and refusal/report stages passed. Compatible and
incompatible pressure fixtures and the R015 grouping/reporting fixtures passed.

Seven cumulative toy attempts, including all failed attempts, took 8.5013 s;
the largest observed child-tree RSS was 183.2071 MiB, below 60 s/512 MiB. All
19 production identities match. The R017 audit byte-compared its three
unchanged support sources with R016 and separately verified the stored R016
audit. No physical mesh, factorization,
PDE solve or matrix solve ran. Full application and rendering/movie checks were
skipped. R016's last complete physical evidence remains the P-only result, which
fails its reference comparison; this toy result supplies no physical accuracy
or feasibility evidence.

## Next task

**GPT-6 Astra, high reasoning:** review the repaired disposable R017 wrapper's
remaining A path against the original R013 contract. Before acting, inspect Git
status/history and read `STATUS.md`, `PROJECT_TRACKS.md`, `EXPERIMENT.md`,
`PHYSICAL_REALIZABILITY_PLAN.md`, `CONTROL_RESEARCH_ROADMAP.md`, R013–R017 result
and evidence records, and the exact R017 archive. Recheck all source identities,
preserved P evidence, A constraint grouping, layout validation, pressure
compatibility, primary/correction counts, output checks and stop behavior.

- If original R013 prerequisites, thresholds and resource caps hold without a
  scientific decision, execute at most one separate physical attempt using the
  repaired disposable runner under 180 s/1.5 GiB. Preserve all finite partial
  output and stop on the first failure, resource limit or unexplained result.
- If any prerequisite fails, or a method/tolerance/physical interpretation
  choice is needed, do not launch the physical child. Record the exact issue and
  alternatives for scientific review.
- Do not retry, increase caps, change tolerances, modify production solver
  choices, integrate the gate, start a campaign/B3 study, render or encode.

Completion means the original contract is either completed once or explicitly
stopped before physical execution with the unresolved decision documented,
evidence audited, continuity updated and scoped changes committed/pushed. A
successful paired numerical experiment still does not establish preparation,
sensing sufficiency or a validated movie trajectory. Retain GPT-5.6 Luna,
medium for understood mechanical defects; use Astra/high for any scientific or
acceptance-threshold decision. The current session catalog lists both models;
OpenAI Docs describes Astra for complex reasoning/research and Luna for
cost-sensitive workloads ([Astra](https://developers.openai.com/api/docs/models/gpt-6-astra),
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)). This is a
recommendation only, not a model switch or scheduled continuation.

**Next prompt: Continue.**
