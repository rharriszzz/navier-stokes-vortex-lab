# Current session handoff

Last updated: 2026-09-20. Latest request:
[R018](REQUEST_LOG.md#r018--2026-09-20--short-continuation-request), complete at
the prescribed prerequisite stop. No physical child was launched. R018 starts
from `bd4945b`; `continue` authorizes its scoped commit/push. Actual delivery
is recorded in Git history and the final response. R014–R017 evidence is unchanged.

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

## Latest result: prerequisite path failure (R018)

Read [the R018 result](docs/realizability/B2_MATCHED_TRACE_PREFLIGHT_RESULT.md),
[evidence index](docs/realizability/B2_MATCHED_TRACE_PREFLIGHT_EVIDENCE.md), and
[validation](docs/realizability/evidence/r018/validation.json).
All 19 production identities and 266 prior evidence files match. The R016 and
R017 stored-data audits passed with writes redirected into the new directory.
Static review covered the repaired remaining A path; physical compatibility
remained an execution prerequisite, not an assumed pass.

The exact R017 sources were copied to `/tmp/navier-b2-matched-r018/`. Fresh
watchdog and kernel checks passed. The wrapper toy then raised `IndexError: 4`
at `wrapper_toys.py:22`, where `Path(__file__).resolve().parents[4]` assumes
archive depth. The temporary copy has only three parents. R018 preparation
missed that launch-layout dependency. The failure precedes record construction,
the first checkpoint and the exception handler, so no wrapper child JSON exists.
The parent retained its finite refusal record, traceback and resource data.

Three monitored child phases used 4.8031 s total, including the failed wrapper,
with peak observed child-tree RSS 141.5703 MiB and maximum gap 0.057983 s,
below 60 s/512 MiB. Block RHS and extra disk phases were not launched after
the refusal. No physical mesh, factorization, PDE solve or matrix solve ran.
No repair or retry followed the required stop. Full application, refinement,
rendering and encoding were skipped. The default staged whitespace check has
one preserved-source exception at `evidence/r018/toy_runner.py:213`.

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

**GPT-5.6 Luna, medium reasoning:** complete the
[R018 toy portability repair contract](docs/realizability/B2_MATCHED_TRACE_PREFLIGHT_RESULT.md#next-bounded-task-make-toy-prerequisites-portable).
Before acting, check Git status/history and read this handoff, `STATUS.md`,
`PROJECT_TRACKS.md`, `EXPERIMENT.md`, `PHYSICAL_REALIZABILITY_PLAN.md`,
`CONTROL_RESEARCH_ROADMAP.md`, the R013 contract, R016–R018 result/evidence
records and exact R018 sources. Preserve historical evidence and all 19
production identities.

Use a new disposable copy. Replace the wrapper toy's fixed ancestor index
with the documented repository-root working directory, validated against the
pinned identities. Move root validation inside its report/exception boundary.
Inspect all parent/child launch, output-directory and sibling-import assumptions.
Under one cumulative 60 s/512 MiB budget in the approved MPI environment, run
the complete five-phase prerequisite sequence from the repository root with
scripts in a shallow temporary directory, and verify an intentional wrong-root
refusal leaves finite stage/error/count JSON. Keep every original numerical
fixture and threshold. Verify the parent's refusal path without a physical child.

Completion means correct disposable invocation and early refusal reporting
pass, or a precise unresolved failure is recorded; archive and audit evidence,
update continuity, commit/push scoped work and stop. Stop on resource limits,
unexplained numerical inconsistency or a scientific decision. No physical
cylinder, PDE solve, factorization, changed scientific tolerance, gate
integration, campaign/B3, rendering or encoding in this repair task.

On passing, recommend GPT-6 Astra/high for review and at most one separately
continued R013 physical attempt under its original prerequisites and
180 s/1.5 GiB caps. Keep Luna/medium only for understood mechanical defects;
use Astra/high for scientific, method or acceptance-threshold decisions.
Both are available in the current session catalog; OpenAI Docs confirms the
supported efforts ([Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna),
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)). No model
switch, delegated session or automation was launched.

**Next prompt: Continue.**
