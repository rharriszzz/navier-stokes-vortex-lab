# User request log

This versioned log records requests received while working in this repository.
`AGENTS.md` requires subsequent sessions to maintain it. Recording begins on
2026-09-20; unavailable earlier conversations have not been reconstructed.
Use `SESSION_HANDOFF.md` for the current task and a reusable continuation request.
This is an agent-maintained record, not an automatic transcript collector.

## R001 — 2026-09-20 — Request logging and project continuation

**User request (verbatim):**

> I want you (and subsequent codex sessions) to record each request I make, so I can come up with a request that will be automatically be processed.  Suggest a way, and do it.  Next, read the files, come up with a plan, and do it.  When the work becomes menial, suggest a model and level, let it know when to stop, tell it how to suggest which model / level should be next, update relevant markdown files, then add commit push.  thanks!

**Scope:** Establish persistent request recording, read the project status and
research plans, complete the next bounded review, prepare a routine coding
handoff with model/effort and stopping rules, update documentation, validate,
stage, commit, and push this work. Commit/push is explicitly authorized for
this request. A reusable prompt will make future continuations easy to submit;
no unattended schedule has been requested.

**Starting point:** Clean `main` at `705b89f`, tracking `origin/main`.
The B2 acceptance repair is complete; the physical response gate remains failed.

**Plan:**

1. Add the log, persistent agent instructions, and a current session handoff.
2. Review the repaired B2 gate and existing stability/reference evidence; run
   bounded checks to establish the next task without launching a response campaign.
3. Record findings and an implementable next package with completion/stop rules.
4. Validate documentation, stage the scoped files, commit, and push.

**Outcome, 2026-09-20:** Review and handoff complete at the requested boundary
between research review and routine coding. Persistent recording is implemented
in `AGENTS.md`; the current request is preserved above. `SESSION_HANDOFF.md`
contains a reusable continuation prompt and the next task's completion and
stopping rules. No automation was scheduled or model switched.

The review reproduced the repaired B2 rejection, checked the independent swirl
reference against historical data, inventoried the response meshes without
assembling production matrices, and reproduced strict-JSON failure for zero or
nonfinite gain comparisons. The next implementation is specified in
`docs/realizability/B2_CONTINUATION_REVIEW.md`; it is handed off, not implemented
by this documentation checkpoint. The physical B2 gate remains failed.

**Validation:**

- `python3 -W error -m unittest discover -s tests/realizability -v`:
  41 tests; 29 passed, 12 optional DOLFINx skips.
- Optional interpreter, `python -m unittest discover -s tests/realizability
  -p 'test_b2*.py' -v`: 18 passed.
- Real bounded alpha=6/48 rejection: both JSON/Markdown written; false gate;
  later stages not run. Evidence and full commands are in the new B2 review.
- CLI help, local Markdown links/anchors, code fences, and whitespace checked.

**Changed files:** `AGENTS.md`, `REQUEST_LOG.md`, `SESSION_HANDOFF.md`,
`README.md`, `PROJECT_TRACKS.md`, `docs/realizability/B2_NEXT_STEPS.md`,
`docs/realizability/B2_GATE_REVIEW.md`, and
`docs/realizability/B2_CONTINUATION_REVIEW.md`.

**Next model/task:** GPT-5.6 Luna, medium reasoning, for the specified reporting
and physical-reference diagnostics. Stop after implementation and its checks;
recommend GPT-6 Astra, high reasoning, for a scalable actual-mesh stability
method review, or stop earlier with evidence if scientific changes are needed.

**Git delivery:** This entry belongs to the requested checkpoint with subject
`Record requests and define the next B2 diagnostic task`. Its commit identity
is available in Git history; the session's final response records the commit
hash and push outcome. The authorization applies to this request's changes.

## R002 — 2026-09-20 — Initial prompt for the next model

**User request (verbatim):**

> OK.  what is its initial prompt?

**Scope:** Provide the initial prompt for the recommended GPT-5.6 Luna session
at medium reasoning, using the current bounded B2 implementation handoff.

**Outcome:** Provided a copyable prompt directing the next session to implement
the six specified diagnostic/report steps, run required checks, update the
request log and Markdown, stop at the package boundary, recommend the following
model/effort, and commit/push its scoped changes. The implementation remains
the next session's task. Only this request log was changed for this follow-up;
the prompt was checked against `SESSION_HANDOFF.md` and the B2 review.

## R003 — 2026-09-20 — Short continuation request

**User request (verbatim):**

> In the future, I don't want to say this many words.  Can you update one or more of the markdown files, so that what I have to say will be simpler?  also, please add commit and push

**Scope:** Replace the long continuation prompt with the repository shorthand
`Continue`, preserving its task, validation, logging, model-handoff, and scoped
commit/push instructions. Update the relevant Markdown and commit/push these
changes, including the existing R002 log entry.

**Outcome:** Defined `Continue` in `AGENTS.md` as the complete bounded workflow:
record the request, carry out the task and checks, update documentation and
model/effort handoff, stage scoped changes, commit, push, and stop. Explicit
qualifications override the default. Replaced the long prompt in
`SESSION_HANDOFF.md` and linked the shortcut from `README.md`. The next B2
implementation task and its stopping conditions remain recorded in the handoff.

**Changed files:** `AGENTS.md`, `SESSION_HANDOFF.md`, `README.md`, and
`REQUEST_LOG.md`, including preservation of R002.

**Validation:** Four Markdown files, 14 local links/anchors, code fences, and
`git diff --check` passed. Numerical tests were not rerun for this documentation
change.

**Git delivery:** Explicitly authorized by this request. This entry is included
in the checkpoint `Simplify continuation to a single-word request`; Git history
and the session's final response record its commit and push result.

## R004 — 2026-09-20 — Short continuation request

**User request (verbatim):**

> continue

**Scope:** Apply the `Continue` workflow to the current B2 diagnostic implementation package in `SESSION_HANDOFF.md`: read required research and review documents, implement the bounded reporting/reference diagnostics, run prescribed checks, update evidence and next-task handoff, then commit and push scoped changes.

**Status:** Complete at the toy-only stopping point.

**Outcome, 2026-09-20:** Repaired a new disposable copy of the R014 runner.
All three direct boundary-space comparisons were replaced by space-aware
`fem.bcs_by_block` groups extracted from the block forms. The groups are
validated before the helper call and reused for essential sets, RHS lifting
and assignment, same-set checks, and essential residuals. Returned solve counts
and factor counters now persist immediately after helper return. Both P and A
compatibility paths persist pre-removal products, RHS/removed norms and the
unchanged tolerance before a possible refusal, with explicit operation stages.

The passing tetrahedron fixture used separate real/imaginary BDM2/DG1 spaces:
24 exterior velocity DOFs and six free interior velocity DOFs per velocity
block, zero pressure constraints, valid offsets and disjoint sets. Exact
assignment passed for zero and nonzero complex targets; missing and wrong-space
groups were refused. Synthetic compatibility and post-return bookkeeping
failures preserved the expected finite partial JSON. The eight monitored
attempts totaled 3.769630435 seconds, with maximum observed child-tree RSS
180.57421875 MiB and maximum sample gap 0.05696793 seconds, below 60 s/512 MiB.
No physical mesh, PDE solve, factorization, or retry ran. The 19 pinned
production hashes match. The R014 read-only stored-data audit passed for all
27 archived artifacts.

**Evidence and validation:** `docs/realizability/B2_MATCHED_TRACE_WRAPPER_REPAIR.md`
and `docs/realizability/evidence/r015/` preserve the repaired source, toy
fixture, all eight monitored attempts, final finite report, and audit. The R015
audit confirmed the toy contract, all finite JSON, Python syntax, source
hashes, and R014 archive identities. No physical accuracy or matched-trace
result follows. The A physical compatibility screen and physical output path
remain unvalidated.

The staged whitespace check found one trailing blank at EOF in the exact
preserved R014 support copy `docs/realizability/evidence/r015/toy_runner.py`
(line 213); it is retained for byte fidelity. All other staged files pass.

**Changed files:** This log, `SESSION_HANDOFF.md`, the new bounded result
document, and the new `docs/realizability/evidence/r015/` archive.

**Next task:** GPT-6 Astra, high reasoning, to review the repaired runner and
conduct the separately scoped R013 matched-trace attempt under its original
caps, checks, and stopping conditions. Stop for any scientific assumption or
threshold decision; no automatic model switch or physical run is launched.
Current official OpenAI documentation lists GPT-6 Astra and high reasoning;
account availability can differ. The continuation prompt remains **Continue**.

**Git delivery:** Commit `5f48dbaed841a73923a1523350046957d339992b` was pushed
to `origin/main`. HEAD and upstream match; the worktree was clean after push.

**Outcome, 2026-09-20:** Completed the bounded B2 report package. Schema-3
reports now handle undefined/nonfinite gain comparisons as strict-JSON nulls
with validity flags, record absolute complex sensitivity and independent
physical-reference diagnostics, and keep campaign readiness false with actual
response-mesh stability explicitly unassessed. The early stability rejection
still performs no harmonic pilot or optional reference calculation.

**Validation:** 44 ordinary realizability tests ran (32 passed, 12 optional
DOLFINx skips); 21 optional B2 tests passed; CLI help passed; the real bounded
alpha=6/48 rejection wrote strict JSON/Markdown with a false gate and no pilot
records; `git diff --check` passed. The final rejection evidence is in
`/tmp/navier-b2-next-diagnostic-rejection-r004-final/gate.{json,md}`. An
intermediate new test had an incorrect expected complex difference; its
expectation was corrected and both final suites pass.

**Changed files:** `realizability/backends/b2_gate.py`, `realizability/cli.py`,
`tests/realizability/test_b2_gate.py`, `docs/realizability/B2_GATE.md`,
`docs/realizability/B2_CONTINUATION_REVIEW.md`, `PROJECT_TRACKS.md`,
`SESSION_HANDOFF.md`, and this log. Actual response-mesh stability and
physical-reference accuracy/error floor remain unresolved. No production
response solve or physical threshold change was made.

**Next task/recommendation:** GPT-6 Astra, high reasoning, to review and specify
a scalable actual-response-operator stability method calibrated against dense
small fixtures, with residual/convergence evidence, resource limits, and
failure conditions. Stop at that research-review boundary. If only a known
mechanical correction remains, recommend GPT-5.6 Luna, medium, with narrow
checks and a stop condition. Official model guidance was rechecked on
2026-09-20; Astra is listed for Codex, with client/account availability caveats.

## R005 — 2026-09-20 — Short continuation request

**User request (verbatim):**

> continue

**Scope:** Complete the current bounded method review for stability of actual
B2 response operators. Read the required research and prior evidence, compare
sparse constrained eigenanalysis with a sufficient coercivity certificate,
calibrate against dense small-cylinder fixtures, and document acceptance
evidence, resource limits, and one bounded implementation follow-up. Commit
and push only this request's changes to the configured upstream.

**Status:** In progress.

**Plan and completion criteria:** Review the mathematical operator and stored
fixtures; perform bounded calibration calculations; write a method review with
residual/convergence requirements, runtime/memory estimates, failure conditions,
and interpretation limits; update the handoff and relevant documentation;
validate the documentation; commit and push.

**Stopping conditions:** Stop at the method-review boundary. Preserve the
3,000-free-DOF dense audit guard, failed physical B2 gate, and false campaign
readiness. Do not implement a production method or launch large response runs.
If calibration contradicts stored fixtures or requires changes to the physical
model, boundary data, or thresholds, record evidence and alternatives for
research review.

**Outcome, 2026-09-20:** Completed the bounded stability-method review. Derived
a sufficient local coercivity certificate for the existing affine tetrahedral
BDM2 SIP form and compared it with constrained sparse inertia analysis. The
certificate uses four-by-four cell trace matrices and a conservative row-sum
bound; inconclusive results do not imply instability. It certifies alpha=96
on 100 mm and alpha=48/96 on 70 mm, while remaining inconclusive on some
dense-positive cases. No physical parameter, backend, gate, or threshold was
changed. The physical B2 gate remains failed and campaign readiness false.

**Validation:** Ten dense small-cylinder cases reproduce stored decay rates;
five targeted 70 mm backward-Euler steps meet the existing prediction checks;
253 independent UFL cell trace comparisons agree within `5.24e-15` relative;
six sparse inertia counts match the complete dense 100 mm spectrum, including
67 negative constrained modes at alpha=6 and none at alpha=48. The full run
took 46.86 s and peaked at 796.06 MiB RSS. A separate warm local-only run took
0.117 s inside the script and peaked at 196.74 MiB. Strict JSON, source/script/
mesh hashes, documented values, Python/JSON fences, eight Markdown files and
23 local links/anchors were checked; `git diff --check` passed. Application
test suites, harmonic response pilots, rendering, and encoding checks were
skipped because their source was unchanged and they are outside this review.

**Evidence:** `/tmp/navier-b2-stability-method-r005/` contains `calibrate.py`,
`dense.json`, `local.json`, `local_cost.json`, and `provenance.json`. The
versioned calibration appendix preserves the exact script and provenance for
reproduction without depending on those temporary files. Numerical source
remains at `21676b96ced6c2372fc8ca350c9650a90960fe3a`.

**Changed files:** `REQUEST_LOG.md`, `SESSION_HANDOFF.md`, `PROJECT_TRACKS.md`,
`docs/realizability/B2_GATE.md`, `docs/realizability/B2_NEXT_STEPS.md`,
`docs/realizability/B2_CONTINUATION_REVIEW.md`, and new
`docs/realizability/B2_SCALABLE_STABILITY_REVIEW.md` and
`docs/realizability/B2_SCALABLE_STABILITY_CALIBRATION.md`.

**Next task/recommendation:** GPT-5.6 Luna, medium reasoning, to implement only
the specified separate local coercivity diagnostic and reports. Verify on
100/70/50 mm under the 500-cell, 120 s, 1 GiB limits; keep dense regressions
separate under their 3,000-free-DOF guard. Stop after the package and its checks,
including if 50 mm is inconclusive. Recommend GPT-6 Astra, high reasoning,
then to interpret stability/physical-accuracy evidence; recommend Luna again
only for a known mechanical fix with a narrow validation/stop condition.
Official model availability was rechecked on 2026-09-20; both are listed for
Codex subject to account/client access. No model switch or new session was
launched. Unresolved: actual response-mesh stability, physical accuracy/error
floor, and whether inconclusive cases merit a separate sparse method.

**Git delivery:** This request authorizes the scoped documentation checkpoint
`Review scalable B2 stability certificates`. Its commit identity and upstream
push result are recorded in Git history and the session's final response.
The review stops here before implementing the next diagnostic.

## R006 — 2026-09-20 — Short continuation request

**User request (verbatim):**

> continue

**Scope:** Implement the bounded B2 local coercivity diagnostic defined in the
current handoff and stability review, run only its prescribed checks, update
documentation and handoff, then commit and push the scoped changes to the
configured upstream.

**Status:** Complete.

**Outcome, 2026-09-20:** Implemented the separate optional `b2-coercivity`
diagnostic and strict JSON/Markdown reports. It uses the reviewed four-by-four
cell certificate, validates affine connected tetrahedral geometry and facet
coverage, enforces the 500-cell pre-array guard, and reports positive,
inconclusive, invalid, or resource-limited results. It includes config,
dependency versions, mesh/source hashes, energy-bound units, timings, and peak
RSS. It remains separate from `b2-gate`; no production response operator,
harmonic pilot, physical threshold, or campaign setting changed.

**Validation:** The 100/70/50 mm meshes have 82/171/482 cells, and their
`C_upper` values are 56.0371901177, 36.7200957987, and 58.1265712308. The
alpha=6/12/24/48/96 certificate classifications match the review on 100/70 mm;
on 50 mm alpha=96 is certified and alpha=48 is inconclusive. The 50 mm mesh
hash matches its stored dense-fixture hash. Independent UFL mass/trace
eigenvalues agree on all 253 100/70 mm cells within `1e-12`; quadrature,
scale-invariance, vertex-permutation, degeneracy, and pre-array resource
refusal checks pass. A separate guarded dense run reproduced all ten stored
rates (maximum absolute difference `4.01e-14 /s`), including the negative
alpha=6 control and stable-but-inconclusive cases. The final diagnostic took
0.51 s and 179.56 MiB parent-observed peak RSS; the dense run took 7.26 s and
769.07 MiB. Both stayed below their 120 s/1 GiB and 180 s/1.5 GiB limits.

Ordinary discovery: 50 tests, 37 passed and 13 optional DOLFINx skips.
Optional B2 discovery: 27 passed. Focused optional coercivity suite: six
passed. CLI help, strict JSON/report review, mesh/source hash checks, and
`git diff --check` passed. Render and movie checks were skipped because those
layers did not change. Final report evidence is in
`/tmp/navier-b2-coercivity-r006-final2/`,
`/tmp/navier-b2-coercivity-r006-final2-watch.json`,
`/tmp/navier-b2-stability-dense-r006.json`, and
`/tmp/navier-b2-dense-r006-watch.json`.

**Changed files:** `realizability/backends/b2_coercivity.py`,
`realizability/cli.py`, `tests/realizability/test_b2_coercivity.py`,
`docs/realizability/B2_SCALABLE_STABILITY_REVIEW.md`,
`docs/realizability/B2_GATE.md`, `docs/realizability/B2_NEXT_STEPS.md`,
`PROJECT_TRACKS.md`, `SESSION_HANDOFF.md`, and `REQUEST_LOG.md`.

**Next task/recommendation:** GPT-6 Astra, high reasoning, to interpret whether
this sufficient local result informs actual response-mesh stability and to
select one bounded stability or physical-accuracy/error-floor review. Define
acceptance evidence, resource limits, alternatives, and stop conditions; stop
before large runs or implementation. Recommend GPT-5.6 Luna, medium, only if
that review reduces the next action to a known mechanical fix with a narrow
check. Official OpenAI model documentation was rechecked 2026-09-20 and lists
Astra for complex reasoning/coding and Luna for cost-sensitive work; local
client/account access may vary. No model switch occurred.

**Git delivery:** The scoped implementation commit `ae31af2` was pushed
successfully to the configured `origin/main` upstream. The worktree was clean
after publication. This completion record is committed separately so the
original request and implementation commit remain unchanged.

## R007 — 2026-09-20 — Short continuation request

**User request (verbatim):**

> continue

**Scope:** Review the completed standalone B2 coercivity diagnostic and its
50 mm evidence, determine what it establishes about the actual response
meshes, and select one bounded stability or physical-accuracy/error-floor
follow-up. Update the research record and handoff, then commit and push only
this request's scoped changes to the configured upstream.

**Status:** In progress.

**Plan and completion criteria:** Read the required research documents,
calibration appendix, previous stability/report reviews, and diagnostic
implementation/evidence. Document certified versus inconclusive conclusions,
assumptions, alternatives, acceptance evidence, resource limits, and failure
conditions for one concrete next task. Check the documentation and recorded
evidence, update continuity records, and publish the scoped checkpoint.

**Stopping conditions:** Stop at the research-decision boundary. Preserve the
3,000-free-DOF dense guard, failed B2 gate, and `campaign_ready=false`. Do not
wire the standalone certificate into the gate, change physical parameters or
thresholds, or launch response-mesh factorizations, harmonic pilots, larger
meshes, or campaigns.

**Outcome, 2026-09-20:** Completed the bounded interpretation review in
`docs/realizability/B2_COERCIVITY_INTERPRETATION.md`. The exact 50 mm mesh/form
at alpha=96 has a guarded positive dissipation margin of
`0.22187075813338908`, which also applies under constant positive viscosity
scaling. Alpha=48 remains inconclusive. Its computed local trace maximum is
`48.96418141363834`, so replacing only the row-sum estimate would still not
certify that penalty through the same sufficient inequality. No stability
conclusion transfers to the distinct 40/30/25 mm meshes, and physical accuracy
remains unresolved. No numerical source, physical threshold, or gate changed.

**Validation:** Read-only strict-JSON audit checked 735 stored cell values,
15 classifications, three facet-count identities, six matching config/source
hashes, pilot configuration, four stored dense sign/conservatism controls and
their mesh identities, and false schema-3 gate/readiness status. Documentation
validation passed for seven Markdown files, 26 local links/anchors, 18 fenced
blocks (Python/JSON syntax checked where present), and three numerical table
rows; `git diff --check` passed. Application tests, PDE/UFL/dense checks,
rendering, and encoding were skipped because numerical source is unchanged.
No mesh generation, response-mesh factorization, harmonic pilot, or campaign
was run. These are R007 evidence/consistency checks, not rerun R006 CFD tests.

**Evidence:** `/tmp/navier-b2-interpretation-r007/` contains `audit.py`,
`audit.json`, and `check_docs.py`. The review preserves the decisive values,
source/report identities, interpretation, and next-task contract without
requiring temporary files. The audited R006 report SHA-256 is
`83530949284b50c3cd4e9b22e9cbb88c47c0f0d9667ee752f4065d3ba8e9454f`.

**Changed files:** `REQUEST_LOG.md`, `SESSION_HANDOFF.md`, `PROJECT_TRACKS.md`,
`docs/realizability/B2_GATE.md`, `docs/realizability/B2_NEXT_STEPS.md`,
`docs/realizability/B2_SCALABLE_STABILITY_REVIEW.md`, and new
`docs/realizability/B2_COERCIVITY_INTERPRETATION.md`.

**Next task/recommendation:** GPT-6 Astra, high reasoning, to execute and
interpret the existing local diagnostic on 40/30/25 mm response geometries,
with a 50 mm control, exact mesh-identity checks, and the review's 120 s
total/1 GiB child-tree RSS watchdog. A per-call `max_cells=4000` allowance is
explicitly scoped to the three new geometry cases; preserve the default
500-cell and dense 3,000-free-DOF guards. Stop after reporting classifications
and costs, including inconclusive outcomes, or earlier on a documented
failure condition. No new backend, global operator, harmonic pilot, or gate
integration is selected. Follow with Astra/high for physical accuracy or
unresolved stability interpretation; recommend Luna/medium only for a known
mechanical fix with its exact check and stop. Official model pages and this
session's model catalog were checked on 2026-09-20. No model switch, delegated
session, or automation was launched.

**Status at completion:** Complete; stopped at the research-decision boundary.
Actual response-mesh stability, physical accuracy/error floor, and any later
sparse-method choice remain unresolved. The physical B2 gate remains failed
and `campaign_ready=false`.

**Git delivery:** This request authorizes the scoped documentation checkpoint
`Review B2 coercivity scope and bound response-mesh study` and its push to the
configured upstream. The commit identity and actual push outcome are reported
in Git history and the session's final response; no force-push is authorized.

## R008 — 2026-09-20 — Short continuation request

**User request (verbatim):**

> continue

**Scope:** Execute and interpret the R007 bounded local coercivity study on
the existing 40/30/25 mm response geometries, with the prescribed 50 mm control.
Preserve the exact runner, evidence, provenance, and resource observations;
update the research documents and handoff; commit and push only this scoped
work to the configured upstream.

**Status:** In progress.

**Plan and completion criteria:** Review the acceptance contract and required
research context; check source identities; prepare a disposable runner with
a parent watchdog; evaluate the four cases once each in fresh serial children;
check identity, geometry, arithmetic, and strict report semantics; document
the result and one bounded next task; validate and publish the checkpoint.

**Stopping conditions:** Enforce 120 s total experiment wall time and 1 GiB
active child-tree RSS. Use the default 500-cell cap for the 50 mm control and
the reviewed per-call 4,000-cell allowance only for 40/30/25 mm. Stop on a
control/hash mismatch, unsupported geometry, resource refusal, or contradictory
arithmetic. Inconclusive is a valid result. Preserve the dense 3,000-free-DOF
guard, failed physical B2 gate, and `campaign_ready=false`. No global operator
assembly, factorization, harmonic pilot, additional mesh sweep, gate
integration, physical parameter/penalty/threshold change, campaign, or B3 work.

**Outcome, 2026-09-20:** Completed the bounded four-case study using the existing
local certificate and a disposable parent/child runner. All 50/40/30/25 mm
mesh identities matched the inventory. Alpha=96 was certified positive on all
four; alpha=48 remained inconclusive on all four. Their C_upper values were
58.1265712308, 57.9026155132, 58.4738571184, and 59.3021263562. Every maximum
local trace eigenvalue exceeds 48, so replacing only the row-sum estimate would
still not certify 48 through the same sufficient inequality. No actual
alpha=48 instability, physical response accuracy, or production penalty choice
is inferred.

**Resource evidence:** Four fresh serial children ran once each, with no
retries, refusals, or unexecuted cases. Total experiment time was 2.6918 s;
maximum parent-observed active child-tree RSS was 184.5078 MiB. The largest
observed sample gap was 0.05561 s at a nominal 0.05 s interval. All remained
within the prescribed 120 s/1 GiB budget and 0.1 s monitoring requirement.
The 50 mm control retained its 500-cell cap, and only the three reviewed new
cases used `max_cells=4000`. Backend defaults and the dense guard are unchanged.

**Validation:** The 50 mm control reproduced the exact recorded bound before
subsequent cases ran. Checked four mesh identities, geometry/facet guards,
6,351 finite local values, eight beta/classification calculations, 19 unchanged
package/config hashes, configuration, strict JSON/Markdown, explicit unresolved
stability/physical-accuracy blockers, and false readiness. All 22 manifest
files matched their hashes. Final synthetic wall-time and two-process RSS
watchdog checks passed. Focused ordinary coercivity discovery ran six tests:
five passed and one optional DOLFINx/UFL test skipped. Runner syntax and exact
embedded bytes passed. Documentation checks passed for nine Markdown files,
38 local links/anchors, 23 fenced blocks, four numerical and four resource
table rows; `git diff --check` passed. Full application, optional UFL/dense/PDE,
rendering, and encoding suites were not run because source is unchanged and
they are outside the bounded study. No global matrices or harmonic responses
were computed.

**Evidence:** `/tmp/navier-b2-response-coercivity-r008/` contains `runner.py`,
the per-mesh JSON/Markdown pairs, parent watch records, study/manifest files,
synthetic watchdog checks, and the read-only evidence/document audit. The
versioned `B2_RESPONSE_COERCIVITY_EVIDENCE.md` preserves exact runner text,
compact numerical records, config/versions/source identities, and report
hashes so the result does not depend on temporary files. Runner SHA-256:
`3eed2ee55b1ebce6b7a183b53e8c19e01deb02254d142d63b1aca07bd33686fe`.

**Changed files:** `REQUEST_LOG.md`, `SESSION_HANDOFF.md`, `PROJECT_TRACKS.md`,
`docs/realizability/B2_GATE.md`, `docs/realizability/B2_NEXT_STEPS.md`,
`docs/realizability/B2_SCALABLE_STABILITY_REVIEW.md`,
`docs/realizability/B2_COERCIVITY_INTERPRETATION.md`, and new
`docs/realizability/B2_RESPONSE_COERCIVITY_RESULT.md` and
`docs/realizability/B2_RESPONSE_COERCIVITY_EVIDENCE.md`. Numerical source,
configuration, physical thresholds, and gate behavior are unchanged.

**Next task/recommendation:** GPT-6 Astra, high reasoning, for the result
document's bounded physical-accuracy/error-floor investigation. Use existing
source/reports and bounded reference/quadrature calculations to produce a
quantitative error budget and one proposed affordable experiment. Preserve
physical parameters and acceptance criteria; enforce 120 s/1 GiB for new
reference calculations; stop at the accuracy-review boundary before mesh,
global-operator, or harmonic work. The certified alpha=96 candidate motivates
that task; resolving alpha=48 by sparse analysis is deferred. Recommend
Luna/medium next only for a fully specified mechanical diagnostic/report
package with exact checks and a stop before interpretation; otherwise retain
Astra/high for the bounded scientific question. Official model pages and
the session's model catalog were rechecked on 2026-09-20. No model switch,
delegated session, or automation was launched.

**Status at completion:** Complete; stopped after the bounded study and its
documentation. Physical accuracy/error floor, alpha=48's actual stability,
and production penalty selection remain unresolved. The physical B2 gate
remains failed and `campaign_ready=false`; its `not_assessed` field has not
incorporated the separate alpha=96 certificates.

**Git delivery:** `Continue` authorizes the scoped checkpoint
`Record B2 response-mesh coercivity certificates` and its push to the configured
upstream. The commit identity and actual push outcome are reported in Git
history and the session's final response; no force-push is authorized.

## R009 — 2026-09-20 — Short continuation request

**User request (verbatim):**

> continue

**Scope:** Complete the R008 bounded physical-response accuracy/error-floor
investigation using existing source/reports and bounded reference/feature
quadrature calculations. Preserve quantitative evidence and reproducible
calculation text, propose one affordable next experiment, update continuity
records, and commit/push only the scoped work to the configured upstream.

**Status:** In progress.

**Plan and completion criteria:** Read the handoff's required research and
method records; reproduce the physical complex disk gain and sensitivity;
separate known error contributions from unknowns; compare targeted error or
adjoint diagnostics with boundary-layer or symmetry-restricted alternatives;
specify one proposed experiment with acceptance evidence, identity checks,
resource limits, and failure conditions; validate and publish the review.

**Stopping conditions:** Stop at the accuracy-review boundary, or earlier on
reference inconsistency or resource refusal. New reference calculations are
limited to 32/64/128 terms and at most 512 quadrature points per integrated
coordinate, under a parent-enforced total 120 s/1 GiB RSS budget. No mesh
generation, global assembly/factorization, harmonic pilots, gate integration,
campaigns, or B3. Preserve physical parameters, signed features, phasor and
facet-target conventions, thresholds, default guards, failed physical B2
gate, and `campaign_ready=false`. Alpha=96 remains only a verification
candidate on the recorded geometries; alpha=48 remains inconclusive.

**Outcome, 2026-09-20:** Completed the physical-accuracy/error-floor review in
`docs/realizability/B2_ACCURACY_REVIEW.md`, with exact calculations in
`B2_ACCURACY_EVIDENCE.md`. The physical complex gain reproduced as
`2.0662858857221768e-5 - 6.595106312048072e-5 i 1/m`, giving rotation amplitude
`6.911220198253778e-12 1/s`. The 32/64/128-term results coincide at returned
precision; the largest measured radial quadrature discrepancy is
`1.3736273526914378e-18 1/m`. Series/radial cancellation ratios are 1.05233
and 1.17288. These are observed reference sensitivities, not a rigorous
reference bound or a total FEM error floor.

The review derives how `0.05 |G|=3.4556100991268897e-6 1/m` is sufficient for
both existing magnitude/phase comparisons, without replacing their thresholds.
It separates algebraic/output, boundary load, geometry and spatial uncertainty,
retains the historical alpha=6 discrepancies as historical, and compares
same-operator error/adjoint, boundary-layer, and symmetry-restricted options.
The selected next experiment is one capped 50 mm alpha=96 physical response
audit with feature-quadrature sensitivity and one residual-correction RHS
using the original factors. No repaired harmonic response or total error bound
is claimed; physical accuracy and production penalty selection remain unresolved.

**Resources and validation:** Final reference pass 0.3690 s; both executed
passes together 0.8442 s, with the second parent deadline deducting the first
pass's measured duration. Maximum parent-observed child RSS across both was
66.9063 MiB; final process high-water RSS was 71.7813 MiB; maximum sample gap
0.05342 s. All are within 120 s/1 GiB. The initial synthetic watchdog CLI
self-check encountered a directory-creation defect before launching children;
the corrected final runner passed wall-time and two-process RSS termination
checks. Reference consistency and resource limits never failed.

Checks passed for three series, 128 independently integrated coefficients,
21 radial and five polar comparisons, scaled/unscaled Bessel evaluation,
summation checks, three stored historical gains, 19 unchanged package/config
hashes matching R008, strict JSON, four manifest file identities, exact embedded
runner and all embedded calculation records. Documentation audit passed for
nine Markdown files, 42 local links/anchors, 38 fenced blocks (Python/JSON
syntax where applicable), and five review tables; `git diff --check` passed.
No application suite, FEM/PDE/UFL/dense check, mesh, harmonic pilot, rendering
or encoding ran. Existing tests that calculate 16 terms or changed parameters
were skipped to preserve this task's bounded calculation contract.

**Evidence:** `/tmp/navier-b2-accuracy-r009/` contains the exact runner, initial
and final reference records, watchdog self-checks, read-only audit and validation
record. The versioned appendix preserves calculations and source/config/report
provenance independently of temporary files. Final runner SHA-256:
`d3f821efdf8cae1ae9a977082affe7e19a681bbb573c7c9f2a1052a36b91ab61`.
Final calculation JSON SHA-256:
`aea6e545734dbcaeacf5e29ac7977fa68a8033c0827ee397906efdfadccfdf96`.

**Changed files:** `REQUEST_LOG.md`, `SESSION_HANDOFF.md`, `PROJECT_TRACKS.md`,
`docs/realizability/B2_GATE.md`, `docs/realizability/B2_NEXT_STEPS.md`,
`docs/realizability/B2_RESPONSE_COERCIVITY_RESULT.md`,
`docs/realizability/B2_SCALABLE_STABILITY_REVIEW.md`, and new
`docs/realizability/B2_ACCURACY_REVIEW.md` and `B2_ACCURACY_EVIDENCE.md`.
Numerical source, config, gate behavior, physical thresholds and defaults are
unchanged. The physical B2 gate remains failed and `campaign_ready=false`.

**Next task/recommendation:** GPT-6 Astra, high reasoning, for the review's
single 50 mm alpha=96 response audit: pinned mesh/form/config, current physical
parameters/target/features, one same-factor residual correction, five prescribed
quadrature rules, complete strict evidence, 180 s total/1.5 GiB active-child-tree
RSS cap. Stop after that one case or an explicit failure/refusal; no automatic
retry, larger mesh, second penalty, new solver/form, adjoint, boundary-layer
implementation, gate integration, campaign or B3. Interpret measured corrections
as sensitivities, not certified error bounds. Recommend Luna/medium next only
for a known mechanical fix with exact edits, focused checks and a stop before
interpretation; otherwise retain Astra/high for one bounded numerical question.
Availability was rechecked against this session's catalog and fetched official
model pages using the OpenAI Docs skill. No model switch, delegation or
automation was launched.

**Status at completion:** Complete; stopped at the accuracy-review boundary.

**Git delivery:** `Continue` authorizes the scoped checkpoint
`Review B2 physical response accuracy and bound one diagnostic` and its push
to the configured upstream. The commit identity and actual push outcome are
reported in Git history and the session's final response; no force-push is
authorized.

## R010 — 2026-09-20 — Project status and user goals

**User request (verbatim):**

> Before going on, I would like us to prepare a status report, and put it into whichever markdown file is best.  I would like you to state the goal you are working toward, and how far you have gotten.  Also somehow incorporate my goals, which are (1) try to figure out if exterior sensors and actuators can provide a good enough initial setup to do some orders of magnitude of the process, and (2) provide data so that a separate 3d movie of this process will be both clear and approximately realistic.

**Scope:** Write an accessible project status report connecting the current
numerical-verification milestone to the user's physical-preparation and movie
objectives. Explain completed work, remaining uncertainty, the meaning still
to be assigned to “orders of magnitude,” and the path from validated data to
a separate visualization. Link the report from project navigation and update
session continuity. This documentation request takes precedence over executing
the next numerical experiment; it does not authorize another commit or push.

**Status:** In progress.

**Plan and completion criteria:** Review the existing project descriptions,
implementation and research evidence; select a durable report location; state
the overall and immediate goals, honest milestone status, and remaining
questions; preserve the bounded next numerical task; check links, consistency
and Markdown changes; record the outcome and stop.

**Stopping conditions:** Documentation only. Do not run the next physical
response audit, change scientific parameters/acceptance criteria, implement
movie exports, render, or infer hardware feasibility from numerical fixtures.
Do not silently assume initial preparation suffices without further driving,
or prescribe a contraction range the user has not specified.

**Outcome, 2026-09-20:** Created root-level `STATUS.md` as the accessible,
project-wide status report, linked from `README.md`, `PROJECT_TRACKS.md` and
`SESSION_HANDOFF.md`. It states both user goals, the immediate task of verifying
boundary-to-interior flow calculations, and the current stage: an implemented
illustrative movie pipeline and substantial numerical verification, with no
demonstrated physical preparation, attainable multi-order evolution, sensing
sufficiency, or validated movie flow history.

The report distinguishes initial preparation from continued driving; leaves
“good enough” and the quantity/range of “orders of magnitude” open; explains the
radius/similarity-time distinction without selecting a new physical target;
and describes the proposed data handoff to a separate movie. It separates
prescribed illustrations, numerical benchmark evidence and future physical
claims. Existing numerical comparison thresholds are not presented as physical
success criteria. No scientific parameters, acceptance criteria or numerical
next-task contract changed.

**Changed files:** New `STATUS.md`; updated `README.md`, `PROJECT_TRACKS.md`,
`SESSION_HANDOFF.md` and `REQUEST_LOG.md`.

**Checks and skips:** Documentation validation passed for five Markdown files,
30 local links/anchors, 19 fenced blocks and two status-report tables; verified
the pending numerical handoff and recorded evidence below its next-task heading
are unchanged. The quoted response scale was checked against the existing
accuracy review. `git diff --check` passed. No application tests, CFD/reference
calculations, rendering or encoding were run for this documentation-only request.
Evidence: `/tmp/navier-status-r010/check_docs.py` and `validation.json`; the
versioned-source deliverable is `STATUS.md` (currently uncommitted).

**Unresolved decisions and next task:** The physical preparation tolerances,
which quantity should span orders of magnitude, its intended range, permitted
continued actuation and sufficient sensor arrangement remain open. The next
numerical task remains the R009 single 50 mm alpha=96 diagnostic under its
180 s/1.5 GiB cap and one-case/failure stop. Retain GPT-6 Astra, high reasoning,
for its numerical interpretation; this session's model catalog still lists
that model/effort. Recommend GPT-5.6 Luna, medium, only for an understood
mechanical fix with exact edits, focused checks and a stop before scientific
interpretation. No model switch or task launch occurred.

**Status at completion:** Complete; stopped after the requested status report.
No commit or push was requested for R010, so all five documentation changes are
left in the working tree for review. The previous continuation's publication
authorization was scoped to the completed R009 checkpoint.

## R011 — 2026-09-20 — Commit and push the status report

**User request (verbatim):**

> if the docs are ready, please add commit push

**Scope:** Publish the R010 status-report documentation changes after reviewing
the final diff. Stage only `STATUS.md`, README/project navigation, the request
log and session handoff, then commit and push to the configured upstream.

**Status:** In progress.

**Completion criteria:** Confirm the worktree contains only the intended R010
documentation changes, preserve the pending numerical handoff, commit the scoped
files, push without rewriting history, and report the commit and actual upstream
result. No new scientific work is requested.

**Outcome, 2026-09-20:** The requested status report was committed as
`b84b2c5` (`Add project status report for physical and movie goals`) and pushed
to the configured `origin/main` upstream. The post-request outcome record in
this entry is being delivered as a separate documentation-only log commit.

## R012 — 2026-09-20 — Short continuation request

**User request (verbatim):**

> continue

**Scope:** Complete the pending R009 single 50 mm alpha=96 physical T_00c
response audit, preserving its exact numerical and resource contract. Record
reproducible evidence and interpretation, update continuity documents, then
commit and push the scoped checkpoint to the configured upstream.

**Status:** In progress.

**Plan and completion criteria:** Read the status report and required research,
method and evidence records; build a disposable instrumented runner using the
existing backend/form; validate its watchdog; verify the 19 source/config
identities, mesh identity/size/DOFs and local certificate; run one physical
harmonic solve and one residual correction with existing factors; record the
five prescribed signed-feature quadrature comparisons and independent physical
reference; validate and publish complete or explicitly partial evidence.

**Stopping conditions:** Stop on identity mismatch, numerical inconsistency,
180 s total child-tree wall time, 1.5 GiB active child-tree RSS, or completion
of the single case. No retry/cap increase, mesh sweep, second penalty, new
solver/form, persistent backend API, adjoint, gate integration, campaign or B3.
Preserve physical parameters, features, conventions, thresholds, default guards,
failed physical B2 gate and `campaign_ready=false`. A small residual correction
is not a total error bound. `Continue` authorizes this scoped commit/push.

**Outcome, 2026-09-20:** Completed the single physical response audit and stopped
at its one-case boundary. The mesh identity, 482 cells, 9,522/1,928 V/Q DOFs,
19 source/configuration identities and local alpha=96 certificate all matched.
One unchanged-backend primal solve and one residual correction used the same
MUMPS factors; PETSc counters confirmed one symbolic factorization, one numerical
factorization and exactly two matrix solves. Existing PDE checks, exact block
round trips and the fixed arithmetic identity tolerance passed.

Physical reference accuracy failed at all five prescribed quadrature rules.
At the finest rule the gain is `-1.6734039795256472 - 1.0983726070219908 i 1/m`,
with amplitude 28962.6876 times the independent 128-term reference and phase
error 74.1164 degrees. Absolute complex error is `2.0016562003 1/m`.
The correction magnitude is `2.2498932366e-14 1/m`; the final quadrature step
is `2.9156584710e-4 1/m`, 84.37 times the reference's 5% absolute scale.
These sensitivities are not error bounds; combined spatial, geometry/loading
and unmeasured integration error remain unresolved. No hardware feasibility,
preparation, sensing or validated movie-flow conclusion follows.

**Resources and checks:** The physical child ran once for 38.7542 s; parent
observed and process high-water RSS were both 753.0508 MiB. Maximum sample gap
was 0.08138 s across 718 samples, below the 180 s/1.5 GiB limits. Both ordinary
and final optional-interpreter synthetic watchdog pairs passed before the run.
No attempt was retried. The first scaffold command found no `python` executable;
using `python3` completed setup before any physical attempt. No internal
consistency check failed and no resource stop occurred; the physical reference
comparison itself failed.

Read-only numerical validation passed for eight manifest files, 19 source/config
identities, 482 local trace values, eight finite 22,900-entry coefficient arrays,
30 complex original features, three sets of 49,152 saved disk samples, residual
norms, reference comparisons, factor counts, vector addition and independent
`math.fsum` disk reductions. No point location failed. Documentation validation
covers local links/anchors, exact runner/audit/report records, fenced syntax,
tables, source immutability and `git diff --check`. No full application,
dense/UFL calibration, mesh refinement, changed-parameter suite, rendering or
encoding ran; these were outside the one-case contract and source is unchanged.

**Evidence:** `/tmp/navier-b2-response-r012/`, with durable interpretation and
exact runner/report/audit in `docs/realizability/B2_PHYSICAL_RESPONSE_AUDIT.md`
and `B2_PHYSICAL_RESPONSE_EVIDENCE.md`. Runner SHA-256:
`fcb8dfedfa4f9049ea6c321f3082ada7666219e90cbcfce234222357901d94bb`.
Report SHA-256:
`16da2b4a410fa08291a86c50454e13f4cfd57f183bc671d0d53e45e313d10b2c`.

**Changed files:** New physical response audit and evidence appendix; updated
`REQUEST_LOG.md`, `SESSION_HANDOFF.md`, `STATUS.md`, `PROJECT_TRACKS.md`, and
`docs/realizability/B2_ACCURACY_REVIEW.md`, `B2_GATE.md`, `B2_NEXT_STEPS.md`,
`B2_RESPONSE_COERCIVITY_RESULT.md`, `B2_SCALABLE_STABILITY_REVIEW.md`.
No numerical source/configuration, solver/form, threshold, default guard or
gate behavior changed. Physical B2 stays failed and `campaign_ready=false`.

**Next task/recommendation:** GPT-6 Astra, high reasoning, for the audit's one
bounded geometry and boundary-layer accuracy method review. Use existing
source/reports and elementary calculations to select one affordable experiment
that distinguishes resolution from faceted-boundary model effects, with explicit
boundary equations, identities, reference/output checks, cost caps and stops.
No new mesh, assembly, PDE solve, reference sweep, field reintegration, new
solver/form, adjoint, gate integration, campaign or B3 runs in that review.
If no defensible test can be specified, record the missing decision. Stop before
implementing/running the proposed experiment. Recommend Luna/medium only for
fully specified mechanical work with focused checks and a stop before numerical
interpretation; otherwise retain Astra/high. Availability was rechecked in the
session catalog and fetched official model pages using OpenAI Docs. No switch,
delegation or automation occurred.

**Status at completion:** Complete; stopped after the bounded audit and
interpretation. A complete diagnostic with a failed physical comparison is the
recorded result, not a passing physical gate.

**Git delivery:** `Continue` authorizes the scoped checkpoint
`Record failed B2 physical response accuracy audit` and its push to `origin/main`.
The actual commit and push outcome are reported in Git history and the final
response; no force-push is authorized.

**Final documentation validation, 2026-09-20:** Passed for 11 Markdown files,
63 local links/anchors, 26 fenced blocks and five result/status tables; exact
embedded runner, read-only audit and report records matched their evidence.
Previous request history and all 19 numerical source/configuration identities
were preserved. `git diff --check` passed. Validation records are
`/tmp/navier-b2-response-r012/numerical-validation.json` and
`documentation-validation.json`.

## R013 — 2026-09-20 — Short continuation request

**User request (verbatim):**

> continue

**Scope:** Complete the R012 geometry and boundary-layer accuracy method review.
Use existing source/evidence and elementary calculations to select one affordable
experiment that can distinguish spatial resolution from faceted-boundary model
error. Record a reproducible experiment contract, update continuity, and commit
and push the scoped review to the configured upstream.

**Status:** In progress.

**Plan and completion criteria:** Read the required scientific documents and
R012/R009/R005/R008 evidence; identify the distinct boundary problems; compare
an existing-form 3D boundary-layer mesh, a symmetry-restricted diagnostic and
an output-weighted residual approach; select one justified experiment with
boundary equations, identity/reference/output checks, resource caps and failure
interpretation; validate the documentation and publish the review.

**Stopping conditions:** Stop after the reviewed experiment contract, or an
explicit missing method decision. No new mesh, assembly, PDE solve, reference
sweep, field reintegration, solver/form implementation, adjoint solve, boundary
model change, gate integration, campaign or B3. Preserve the physical parameters,
signed features, phasor, acceptance thresholds, default guards, failed physical
B2 gate and `campaign_ready=false`. The proposed experiment is not run in R013.
`Continue` authorizes the scoped commit and push without rewriting Git history.

**Outcome, 2026-09-20:** Completed the method review and stopped before its
proposed experiment. The selected test uses the unchanged 50 mm alpha=96
operator with the current command and the full complex boundary trace of the
known finite 128-term solution. The latter is an exact continuum verification
problem on the same polyhedron, generally requiring nonzero normal data.
Its error and the discrete change between commands satisfy an explicit complex
identity; the change is not a continuum geometry-error estimate. The review
compares and defers a 3D boundary-layer mesh, a symmetry-restricted solver and
an output-weighted/adjoint study, with their limitations and cost uncertainties.

The next contract fixes two facet quadrature orders, oriented normal-trace
projection, consistent lifting and cell-aware polynomial integration on the
exact disk. It requires orientation, geometry, flux/nullspace, arithmetic,
reference and source/mesh/matrix checks. One matrix/factorization serves three
primary RHSs and three residual corrections; the physical child is capped at
180 s/1.5 GiB, with separate 60 s/512 MiB toy checks. It has explicit refusal,
component-screen, physical-failure and resource-stop interpretations, with no
retry, second mesh or automatic method substitution. These are **proposed
counts and limits**, not completed solves or promised resource use.

**Checks executed:** The standard-library read-only review checked the exact
R012 report/runner hashes, all 19 package/config identities and three existing
appendix identities; it parsed the prior runner without executing it. Elementary
arithmetic reproduced the penetration depth (5.641895835 mm), reference 5% scale
(3.4556100991e-6 1/m), proposed component screens and polynomial dimensions.
The illustrative chord sagitta is not a mesh measurement. No reference function,
Bessel series, stored field integral, mesh, assembly or PDE calculation ran.
The documentation validation result is recorded below.

**Checks skipped:** Application, optional FEM/dense/calibration tests, new
numerical experiments, load/output-kernel implementation, rendering and encoding
are outside this method-review scope. No unexecuted check is claimed passed.
No numerical package/config, solver/form, acceptance threshold, guard or gate
behavior changed. Physical B2 remains failed and `campaign_ready=false`.

**Evidence and changed files:** New durable
`docs/realizability/B2_MATCHED_TRACE_REVIEW.md` and
`docs/realizability/B2_MATCHED_TRACE_EVIDENCE.md`; updated `REQUEST_LOG.md`,
`SESSION_HANDOFF.md`, `STATUS.md`, `PROJECT_TRACKS.md`, and
`docs/realizability/B2_PHYSICAL_RESPONSE_AUDIT.md`, `B2_NEXT_STEPS.md`,
`B2_GATE.md`. Temporary read-only calculations and documentation validation are
in `/tmp/navier-b2-method-r013/`; the exact read-only script/report are embedded
in the new appendix. Existing numerical evidence appendices are unchanged.

**Unresolved:** Total spatial/boundary approximation error and continuum
geometry error remain unallocated. One matched-trace result cannot establish
convergence, penalty robustness, a validated production response or hardware
feasibility. The finite-element normal-trace projection itself remains part of
the approximation error. New load/output cost is unmeasured; a refused or capped
attempt is an acceptable next-task result. Preparation tolerances, continued
actuation, adequate sensing and a validated movie history remain open.

**Next task/recommendation:** GPT-6 Astra, high reasoning, to implement and run
exactly the reviewed disposable experiment, preserve the runner and finite JSON
result (including partial/refused outcomes), update continuity and commit/push,
then stop. Read the full review's checks and stopping conditions first; do not
rerun the completed R012 audit as a separate task. No production backend change,
new mesh family, extra penalty, reduced solver, adjoint, gate integration,
campaign, B3 or movie export follows automatically. Recommend GPT-5.6 Luna,
medium, only if an understood mechanical fix has exact edits/checks and a stop
before scientific interpretation; otherwise retain Astra/high for one bounded
numerical question. Availability was rechecked in the session catalog and
fetched official model pages using OpenAI Docs. No switch, delegation or
automation occurred. The next user prompt is **Continue**.

**Status at completion:** Complete at the method-review boundary. The proposed
matched-trace experiment has not been run.

**Git delivery:** `Continue` authorizes the scoped checkpoint
`Specify B2 matched-trace accuracy experiment` and push to `origin/main`.
The actual commit and push outcome are reported in Git history and the final
response; no force-push is authorized.

**Final documentation validation, 2026-09-20:** Passed for nine Markdown files,
54 local links/anchors, 22 fenced blocks and seven result/status tables. The
exact embedded read-only script/report, proposed inventory, elementary scales
and preserved R012 result table checked consistently. All prior request history,
19 numerical source/config identities and three numerical evidence appendices
were preserved. `git diff --check` passed. Validation record:
`/tmp/navier-b2-method-r013/documentation-validation.json`.

## R014 — 2026-09-20 — Short continuation request

**User request (verbatim):**

> continue

**Scope:** Implement and execute the single disposable matched-trace experiment
specified by R013, preserve complete or explicitly partial evidence, update
continuity, and commit/push the scoped checkpoint to the configured upstream.

**Status:** In progress.

**Plan and completion criteria:** Read the complete R013 contract and required
research/evidence; implement the fixed load/output kernels and prerequisite toy
checks; validate the watchdog; attempt the prescribed paired physical experiment
once if prerequisites pass; preserve the exact runner and finite JSON evidence;
interpret only completed checks and publish the bounded result.

**Stopping conditions:** Honor the contract's 60 s/512 MiB toy budget and
180 s/1.5 GiB physical child-tree cap, fixed source/mesh identities, guards,
compatibility and numerical checks. Stop on prerequisite refusal, inconsistency,
resource cap or completion. No retry/cap increase, extra physical mesh, changed
backend/form/penalty, adjoint, gate integration, campaign, B3 or movie export.
Preserve parameters, features, phasor, thresholds, failed B2 and false readiness.
`Continue` authorizes this scoped commit and push without rewriting history.

**Outcome, 2026-09-20:** The single R014 physical attempt stopped at its required
internal-error boundary. The disposable wrapper failed after the original P
solve when direct comparison of C++/Python function-space objects produced an
empty boundary-constraint list. `numpy.concatenate` raised `ValueError: need at
least one array to concatenate`. There was no retry or cap increase. The
experiment is partial, not a failed matched-trace accuracy comparison.

All 19 source/configuration identities and the exact 482-cell, 9,522/1,928-DOF
mesh matched. The alpha=96 certificate reproduced C_upper=58.12657123078638
and beta=0.22187075813338908 under the 500-cell guard. All 24 permutation/30
polynomial-vector-trace toy checks, disk/arc/jump/tangency checks and quadratic
restriction/stencil checks passed. Two physical polynomial loads agreed with
UFL; all 482 cells were checked for the disk partition, giving 11 positive-area
regions and correct moments/denominator, with no coincident interior facet.
Both q=32/64 full-trace loads and normal projections completed on 282 facets;
all real/imaginary closed-flux ratios passed 1e-8. A pressure-compatibility
checks were not reached. P's existing PDE diagnostics passed and reproduce
R012 exactly except timing.

**Actual inventory and limits:** One physical mesh, one returned P solve,
zero residual corrections and zero matched-trace solves. Matrix/factor hashes
and PETSc event counters were not reached. The physical child took 54.1700 s,
with 734.7539 MiB parent/process peak RSS, 1,003 samples and maximum gap
0.060411 s, below 180 s/1.5 GiB. Two successful toy children used 4.4804 s total
and at most 141.5508 MiB parent RSS, below their shared 60 s/512 MiB cap. Synthetic
wall and two-process RSS watchdog tests passed. No resource stop occurred.

**Evidence and validation:** Durable result and index are
`docs/realizability/B2_MATCHED_TRACE_RESULT.md` and
`B2_MATCHED_TRACE_RUN_EVIDENCE.md`. Exact failed code, reports, normals/projection
moments/fluxes, disk geometry, traceback and watchdog records are under
`docs/realizability/evidence/r014/`; original files remain in
`/tmp/navier-b2-matched-r014/`. The standard-library read-only audit passed for
27 archived artifact identities, 19 numerical identities, 482 local values,
564 facet projection equations/flux reductions, 11 regions, UFL comparisons,
permutation records and P diagnostics. Large facet JSON records were compacted
without changing parsed values; original and archived hashes are recorded.
The audit performs no FEM import, mesh, assembly, reference evaluation or solve.

**Checks skipped/unresolved:** No A lift/pressure check or solve; no correction,
matrix/factor audit, solved-field polynomial reconstruction, feature extraction,
gain, error identity or component/reference comparison. No coefficient vectors
were saved for later output recovery. No full application, dense/calibration,
refinement suite, rendering or encoding ran. No new physical accuracy, geometry
error allocation, preparation, sensor or movie-flow result follows. The failed
B2 gate and `campaign_ready=false` are unchanged. No production source/config,
form/solver, guard or threshold changed; prior numerical appendices are intact.

**Changed files:** This log, `SESSION_HANDOFF.md`, `STATUS.md`,
`PROJECT_TRACKS.md`, `docs/realizability/B2_MATCHED_TRACE_REVIEW.md`,
`B2_PHYSICAL_RESPONSE_AUDIT.md`, `B2_NEXT_STEPS.md`, `B2_GATE.md`; new matched-trace
result, evidence index and the R014 historical artifact directory. The exact
failed runner is preserved, including its unexecuted later code.

**Next task/recommendation:** GPT-5.6 Luna, medium reasoning, for the result's
fully specified toy-only wrapper repair. Replace all three direct space-object
comparisons with `fem.bcs_by_block`, validate groups/offsets/exterior DOFs before
solving, and persist accurate counts/stages/compatibility data before a failure.
Test a reference tetrahedron and synthetic error paths under 60 s/512 MiB,
preserve the repaired copy and finite report, commit/push, then stop. No physical
cylinder, factorization, PDE solve or retry belongs to that next package. After
focused checks pass, recommend Astra/high for review and a separately authorized
R013 attempt; retain Luna/medium only for understood mechanical defects, and
stop for Astra/high if a scientific assumption or threshold decision is needed.
Availability was rechecked in the session catalog and fetched official model
pages with OpenAI Docs. No switch, delegated session or automation occurred.

**Status at completion:** Complete at the prescribed stop; scientific diagnostic
partial due to an instrumentation error. The next prompt is **Continue**.

**Git delivery:** `Continue` authorizes this scoped checkpoint and push to
`origin/main`. Actual commit/push outcome is reported in Git history and the
final response; no force-push is authorized.

**Final documentation validation, 2026-09-20:** Passed for 10 Markdown files,
84 local links/anchors, 20 fenced blocks, 15 finite JSON files and five Python
syntax checks. All previous request history is preserved; stored-evidence checks
also preserve the 19 numerical source/configuration identities and four prior
evidence appendices. `git diff --check` passed. Documentation record:
`/tmp/navier-b2-matched-r014/documentation-validation.json`; durable numerical
record: `docs/realizability/evidence/r014/stored_validation.json`.

**Staged archive check, 2026-09-20:** After newly archived files were staged,
`git diff --cached --check` reported one trailing blank line at EOF in the exact
historical `evidence/r014/toy_runner.py` (line 213). It is retained to preserve
the executed bytes and SHA-256. All other staged files pass the whitespace
check; this exception supersedes any interpretation that the entire new archive
passed the default whitespace check. The earlier unstaged documentation check
passed. No numerical check or artifact was changed to remove this warning.

## R015 — 2026-09-20 — Short continuation request

**User wording:** “continue”

**Interpreted scope:** Apply the repository's Continue workflow. Resume the
toy-only wrapper instrumentation repair specified at the end of R014, complete
its bounded checks and evidence, update continuity documents, then commit and
push the scoped changes to the current upstream. No physical matched-trace
attempt is authorized in this task.

**Status:** In progress.

## R016 — 2026-09-20 — Short continuation request

**User request (verbatim):**

> continue

**Interpreted scope:** Review the archived R015 repaired disposable runner and
carry out the single R013 matched-trace attempt specified by the current
handoff, subject to its original prerequisites, fixed scientific assumptions,
resource limits and stopping conditions. Preserve prior evidence, record the
complete or partial outcome, update continuity, and commit/push only this task's
changes to the configured upstream. This request authorizes that scoped commit
and push; it does not authorize retries or a further numerical campaign.

**Status:** In progress.

**Bounded plan and completion criteria:** Read the required research documents,
R013 contract and R014/R015 evidence; review the repaired runner and production
identities; perform only prescribed prerequisite checks within the shared
60 s/512 MiB toy budget; attempt at most one fixed 50 mm physical child within
180 s/1.5 GiB if all prerequisites pass; archive exact code, finite reports and
resource evidence; document completed checks, skips, interpretation and one
concrete next task, then commit/push and stop.

**Stopping conditions:** Stop on prerequisite or integrity inconsistency,
compatibility/PDE failure, resource cap, scientific assumption/threshold decision,
or completion. No physical retry, cap increase, second mesh, altered form,
penalty, boundary trace, acceptance threshold or correction count. No refinement,
B3, gate integration, rendering or movie export. Preserve the failed physical
B2 gate and `campaign_ready=false`.

**Outcome, 2026-09-20:** Completed at the prescribed internal-error stop. The
single R016 physical child reached the original-command P solve, its one
same-factor correction and checked outputs, then failed during A_32 RHS lifting:
`AttributeError: 'list' object has no attribute '_cpp_object'`. The saved
`stage=P_outputs` is the last checkpoint; the traceback identifies the later
lifting call at `physical.py:465`. Neither A pressure compatibility nor any
matched-trace solve was reached. No physical retry, cap increase or scientific
assumption change followed.

Static inspection shows the copied RHS entered DOLFINx's non-block lifting
branch; loss of `_blocks` at `rhs=b.copy()` is the source/traceback-based
diagnosis, pending a toy reproduction. R015 tested grouping and `bc.set` on
NumPy slices, not the complete PETSc block lifting/assignment path. The exact
R015 child code was used and is preserved without retrospective repair.

**Actual inventory and limits:** One physical mesh, one returned primary P
solve, one correction, one symbolic/numeric factorization and two matrix solves.
The child ran 59.1794507680 s, with 755.86328125 MiB observed/process peak RSS,
1,090 watchdog samples and maximum gap 0.0603705890 s, under 180 s/1.5 GiB.
Toy checks passed within 5.3732977520 s total and 140.99609375 MiB maximum
observed child-tree RSS. An initial sandbox MPI initialization failure occurred
before numerical checks; after approved escalation, checks ran successfully.
Its 0.4231748100 s and failed-import evidence remain in the shared 60 s/512 MiB
budget and archive. No toy numerical failure or physical retry was concealed.

**Completed checks:** All 19 pinned production source/configuration identities
and the exact 482-cell, 9,522/1,928-DOF mesh matched. The local certificate,
24-permutation/30-polynomial load checks, disk/arc/jump/tangency and wrapper
toys, synthetic watchdog tests, physical UFL loads, all 482 disk-cell visits
and 11 positive-area regions passed. Both 282-facet normal projections/loads
and all four closed-flux ratios completed. P's constraint groups, pressure
compatibility, original PDE diagnostics, correction residual, matrix/factor
invariance, polynomial reconstruction, output arithmetic/component screens,
linearity and both original polar-rule reproductions passed.

P's cell-integrated primary gain is
`-1.6734724052233703 - 1.0983702805959774 i 1/m`; the correction magnitude is
`2.2504571344e-14 1/m`. The measured P amplitude remains 28963.4968 times the
reference, with 74.1175-degree phase error, failing the strict 5%/5-degree
comparison. This is a completed P diagnostic within an incomplete paired
experiment. No A error, load-step comparison, discrete boundary sensitivity,
continuum geometry allocation or physical feasibility result follows. The
physical B2 gate remains failed and `campaign_ready=false`.

**Evidence:** New result `docs/realizability/B2_MATCHED_TRACE_LIFTING_RESULT.md`
and index `B2_MATCHED_TRACE_LIFTING_EVIDENCE.md`; 48 exact code/report/log/review
artifacts under `docs/realizability/evidence/r016/`, including both parent
versions, finite partial reports, traceback and watchdogs. The two large facet
JSON files preserve every parsed value with compact whitespace; original and
archived hashes are recorded. Working evidence is in
`/tmp/navier-b2-matched-r016/`. The standard-library `audit.py` and
`stored_validation.json` validate 19 source identities, 79 prior archive files,
four prior evidence appendices, 564 facet records, disk moments, P measurements
and counts without new FEM execution.

**Checks skipped/unresolved:** No completed A lifting/assignment, A pressure
compatibility, A solve/correction/PDE/trace/output, paired identity or load-step
screen. No coefficient vectors were saved for later recovery. Full application,
optional dense/calibration/refinement suites, production changes, gate
integration, campaign, B3, rendering and encoding were outside scope. Physical
preparation tolerances, allowed continued driving, adequate sensing, attained
range and validated movie flow remain open. Alpha=48 and schema-3 certificate
integration remain unresolved as previously recorded.

**Changed files:** This log, `SESSION_HANDOFF.md`, `STATUS.md`,
`PROJECT_TRACKS.md`, `docs/realizability/B2_MATCHED_TRACE_REVIEW.md`,
`B2_MATCHED_TRACE_RESULT.md`, `B2_MATCHED_TRACE_RUN_EVIDENCE.md`,
`B2_MATCHED_TRACE_WRAPPER_REPAIR.md`, `B2_PHYSICAL_RESPONSE_AUDIT.md`,
`B2_GATE.md`, `B2_NEXT_STEPS.md`, the new R016 result/index and artifact directory.
No production numerical source/configuration or old evidence artifact changed.

**Continuity reconciliation for R015, 2026-09-20:** Its initial log entry has
no appended outcome, but the existing repair result, archived validation and
commits `5f48dba`/`349c9a3` establish completion of its toy-only grouping repair.
That completed assignment was not replayed; R016 reviewed and used its code
under the separately continued physical contract.

**Next task/recommendation:** GPT-5.6 Luna, medium reasoning, for the result's
explicit toy-only block RHS repair. Reproduce metadata loss; construct the RHS
through the DOLFINx vector factory; validate owned/ghost layout; test the actual
loading/lifting/scatter/assignment helper with pressure and real/imaginary
couplings against independent toy arithmetic; add pre-operation stage/layout
records and refusal/compatibility fixtures. Keep all toy execution within
60 s/512 MiB, with no physical cylinder, factorization or PDE solve. Preserve
exact artifacts and source identities, update continuity, commit/push, then
stop. On passing, recommend Astra/high for review of the remaining A path and
one separately scoped R013 attempt under its original caps/checks. Retain
Luna/medium only for understood mechanical defects; stop for Astra/high on
scientific or threshold decisions. Availability and effort support were
rechecked in the current catalog and fetched official model pages using
OpenAI Docs. No model switch, sub-agent or automation was launched.

**Status at completion:** Complete at the required stop; paired scientific
diagnostic partial due to wrapper instrumentation. The next prompt is
**Continue**.

**Git delivery:** `continue` authorizes the scoped checkpoint and push to the
configured `origin/main` upstream. Actual commit/push is reported in Git history
and the final response. No force-push or unrelated changes are included.

**Final validation, 2026-09-20:** The stored-data audit passed. Documentation
validation passed for 13 Markdown files, 137 local links/anchors, 20 fenced
blocks and nine Python sources; previous request history is preserved and
R016 is recorded once. The documentation checker initially required its own
not-yet-written linked report; that bootstrap check was corrected, then passed.
Records: `docs/realizability/evidence/r016/stored_validation.json` and
`documentation_validation.json`. No physical or toy rerun followed the stop.

`git diff --check` passed for tracked documentation before staging. The actual
`git diff --cached --check` reports four warnings in exact preserved artifacts:
`evidence/r016/toy_runner.py:213` (blank line at EOF), and
`evidence/r016/toys/kernels.stderr:3`, `:4`, `:5` (raw MPI error trailing spaces).
They are retained for byte/hash fidelity; all other staged files pass. The
whole-archive default whitespace check is therefore not reported as passed.

## R017 — 2026-09-20 — short continuation request

**User wording:** “continue”

**Interpreted scope:** Apply the repository's short continuation workflow.
Resume the bounded R016 toy-only block RHS lifting repair contract in a new
disposable copy; review required research and evidence documents, execute only
the prescribed toy fixtures within the stated caps, preserve unrelated work,
update continuity, and commit/push the scoped result to the configured upstream.

**Status:** Complete.

**Outcome (2026-09-20):** Complete. The repaired disposable helper passed the
block RHS allocation, layout, loading, lifting, reverse-scatter, assignment,
coupling, pressure-compatibility and refusal checks on toys. Seven cumulative
parent-monitored attempts took 8.5012 s, with a maximum observed child-tree RSS
of 183.2071 MiB. All 19 production identities matched; no physical mesh, PDE
solve, factorization or matrix solve ran. The R017 stored-data and documentation
audit passed for its archived files, three byte-compared R016 support sources, 102 local
links/anchors, nine fenced blocks and all Python sources. The separate R016
stored-data audit also passed. Full application/render/encoding checks were
skipped. The physical R013 attempt remains the next bounded task under Astra/high.
The staged whitespace check reports one preserved-source exception at
`docs/realizability/evidence/r017/toy_runner.py:213` (the copied R016 support
file's blank line at EOF); no other staged whitespace findings remain.

**Changed files:** `REQUEST_LOG.md`, `SESSION_HANDOFF.md`, `STATUS.md`,
`PROJECT_TRACKS.md`, `docs/realizability/B2_NEXT_STEPS.md`, the R017 result and
evidence index, and `docs/realizability/evidence/r017/`. Production numerical
sources, R014–R016 evidence and the physical gate were not changed.

**Git delivery:** The `continue` shorthand authorizes the scoped commit and
push to the configured upstream. The actual commit and push result will be
recorded in Git history and the final response.

## R018 — 2026-09-20 — Short continuation request

**User request (verbatim):**

> continue

**Interpreted scope:** Apply the Continue workflow to the handoff's bounded
review of the repaired R017 disposable wrapper and remaining A path against
the original R013 contract. If every prerequisite holds without a scientific
decision, execute at most one separate physical attempt under the original
180 s/1.5 GiB limits. Archive and audit complete or finite partial evidence,
update continuity and commit/push only this task's changes to the configured
upstream. This request authorizes that scoped commit and push.

**Status:** In progress.

**Bounded plan and completion criteria:** Read the required research documents
and R013–R017 records; inspect exact archived code, production identities and
preserved P evidence; review A grouping, layout, compatibility, solve counts,
output checks and stops. Complete one permitted attempt or document the exact
prerequisite/decision preventing execution, audit evidence, record checks and
skips, provide one concrete next task with model/effort and stop conditions,
then commit/push and stop.

**Stopping conditions:** Stop before physical execution on failed prerequisite
or method/tolerance/interpretation choice. After launch, stop on first failure,
resource cap or unexplained result. No retry, increased caps, changed tolerance,
production solver change, gate integration, campaign/B3, rendering or encoding.
Retain the failed physical B2 gate and `campaign_ready=false`.

**Outcome, 2026-09-20:** Complete at the prescribed prerequisite stop, before
physical execution. The fresh watchdog and kernel phases passed; the wrapper
toy failed at `wrapper_toys.py:22` with `IndexError: 4` while resolving
`Path(__file__).resolve().parents[4]`. The exact R017 files were copied into
`/tmp/navier-b2-matched-r018/`, where that ancestor does not exist. R018
preparation overlooked the fixture's archive-depth dependency. No numerical
claim follows from this path failure, and it does not invalidate R017's saved
toy arithmetic. No repair, retry or physical child followed the stop.

**Completed checks and resource accounting:** All 19 production identities and
266 R014–R017 evidence files matched the starting commit `bd4945b`. R016 and
R017 stored-data auditors passed with their writes captured in the new work
directory, leaving old artifacts unchanged. Static review covered A grouping,
layout, complete lifting, compatibility, corrections, common matrix/factors,
own-target diagnostics and outputs. Six child/support files match R017 exactly.
Fresh synthetic wall/RSS watchdog checks and all 24 permutation/polynomial-load
and kernel disk/arc/jump/tangency checks passed. Three child phases, including
the failed wrapper, used 4.8030722210 s total and 141.5703125 MiB maximum
observed child-tree RSS, below 60 s/512 MiB; maximum sample gap was 0.057983 s.
The approved MPI environment was used without a new sandbox MPI failure.

**Failure evidence and skips:** The wrapper failed after imports but before
report construction, its first checkpoint, source verification or tetrahedron
creation. It wrote no child JSON; the parent saved finite refusal/count/resource
data and the exact traceback. Block RHS and extra disk phases were not launched
after refusal. No physical mesh, PDE solve, factorization or matrix solve ran.
A pressure compatibility and accuracy remain unmeasured. R016's P-only output
and the failed physical comparison remain unchanged. Full application,
dense/calibration/refinement suites, production changes, gate integration,
campaign, B3, rendering and encoding were skipped. Preparation, sensing,
physical demands and validated movie flow remain unresolved.

**Changed files/evidence:** This log, `SESSION_HANDOFF.md`, `STATUS.md`,
`PROJECT_TRACKS.md`, `docs/realizability/B2_NEXT_STEPS.md`,
`B2_MATCHED_TRACE_REVIEW.md`, `B2_BLOCK_RHS_TOY_REPAIR_RESULT.md`, the new
`B2_MATCHED_TRACE_PREFLIGHT_RESULT.md` and `B2_MATCHED_TRACE_PREFLIGHT_EVIDENCE.md`,
and `docs/realizability/evidence/r018/`. The archive manifest preserves 29 exact
code/report/log artifacts; the later standard-library audit and validation are
separate. No production numerical source/configuration or old evidence changed.

**Next task/recommendation:** GPT-5.6 Luna, medium reasoning, for the result's
toy-only portability and early-reporting repair. Use the documented
repository-root working directory instead of fixed script ancestry, validate
it against pinned source identities, and persist early failures. Inspect every
child's launch/output/import assumptions. Under one cumulative 60 s/512 MiB
budget, validate the complete five-phase sequence using scripts in a shallow
temporary directory, correct-root success and intentional wrong-root refusal
with finite reports, and the parent's refusal path without a physical child.
Archive/audit evidence, update continuity, commit/push, then stop. Stop on a
resource limit, unexplained numerical failure or scientific decision. On passing,
recommend Astra/high for a separately continued R013 review and at most one
physical attempt under the unchanged contract. Retain Luna/medium only for
understood mechanical fixes; use Astra/high for method, tolerance or physical
interpretation choices. Availability and supported efforts were rechecked in
the current catalog and fetched official model pages using OpenAI Docs. No
model switch, sub-agent or automation occurred.

**Status at completion:** Complete at the prerequisite stop; the paired
scientific diagnostic remains incomplete. The next prompt is **Continue**.

**Git delivery:** `continue` authorizes this scoped checkpoint and push to
`origin/main`, with no force-push. Actual delivery is reported in Git history
and the final response.

**Validation, 2026-09-20:** The R018 stored-data/documentation audit passed for
29 archived artifacts, 19 production identities, 266 preserved historical files,
six unchanged child/support sources, ten Python syntax checks, nine finite
JSON inputs, nine Markdown files, 89 local links/anchors and 17 fenced blocks.
Earlier request history is preserved, and R018 occurs once. Record:
`docs/realizability/evidence/r018/validation.json`. The numerical prerequisite
sequence itself is explicitly recorded as refused, not passed. Tracked
documentation passed `git diff --check` before staging; the exact copied
`toy_runner.py:213` retains the known blank-line-at-EOF exception, to be checked
separately in the staged archive.

**Staged check, 2026-09-20:** `git diff --cached --check` reported exactly the
expected preserved blank line at `docs/realizability/evidence/r018/toy_runner.py:213`.
The staged check excluding that byte-preserved historical source passed. The
whole-archive default whitespace check did not pass; no executed source was
edited to hide the exception.

## R019 — 2026-09-20 — Short continuation request

**User request (verbatim):**

> continue

**Interpreted scope:** Apply the Continue workflow to the bounded R018 toy portability repair in the current handoff. Preserve scientific fixtures and thresholds; validate the complete prerequisite toy sequence and early refusal reporting in a disposable copy, audit and archive evidence, update continuity, then commit and push only this task's changes to the configured upstream.

**Status:** In progress.

**Bounded plan and completion criteria:** Check Git status/history; read the handoff and required research and R013/R016–R018 records. Inspect exact R018 sources and identity pins. In a new disposable copy, remove fixed ancestor assumptions using the documented repository-root working directory, validate root identity and report early errors, inspect child launch/output/import assumptions, and run the five-phase toy prerequisites under 60 s/512 MiB. Verify correct-root execution, intentional wrong-root finite refusal JSON, and the parent's refusal path without any physical child. Archive and audit the result, update the handoff with one next task and model/effort guidance, then commit and push the scoped changes.

**Stopping conditions:** Stop on resource limits, unexplained numerical inconsistency or a scientific decision. No physical cylinder, PDE solve, factorization, changed tolerance, gate integration, campaign/B3, rendering or encoding.

**Outcome, 2026-09-20:** The portability and early-refusal contract passed in a shallow disposable directory. `wrapper_toys.py` now uses the repository-root working directory, verifies all pinned source identities before DOLFINx/MPI imports, and writes an early finite report on an invalid root. The wrong-root report is at stage `imports` with zero mesh/solve/factorization/RHS counts. The parent records `prerequisite_refused` with zero counts and `child_launched=false` when its toy report is failed or incomplete.

**Checks and resource accounting:** The full five-phase sequence plus wrong-root probe passed under the 60 s/512 MiB parent monitor: 5.378702527 s, 140.51171875 MiB maximum observed child-tree RSS, and 0.056604930 s maximum sample gap. This includes the watchdog wall/RSS self-checks, kernel fixtures, wrapper grouping/compatibility fixtures, full block-RHS oracle and extra disk checks. All 19 production identities matched. Four earlier disposable failures (one harness output-directory collision, two wrong-root MPI/UCX startup failures and one kernel MPI/UCX startup failure) are preserved; combined parent-monitored time across all attempts was 6.480515285 s. The final run used the approved MPI environment. The isolated parent refusal probe produced finite JSON and no child launch record.

**Evidence, changed files and skips:** Evidence and source hashes are archived under `docs/realizability/evidence/r019/`; see `B2_TOY_PORTABILITY_RESULT.md`, `B2_TOY_PORTABILITY_EVIDENCE.md` and `validation.json`. Changed documentation is limited to this log, `SESSION_HANDOFF.md`, `STATUS.md`, `PROJECT_TRACKS.md`, `docs/realizability/B2_NEXT_STEPS.md`, the new R019 result/evidence index and the R019 archive. No production numerical sources/configuration or R014–R018 artifacts changed. No physical mesh, PDE solve, factorization or matrix solve ran; no A pressure compatibility or matched-trace gain was measured. The B2 gate remains failed and `campaign_ready=false`. Rendering, encoding, application tests, gate integration, campaign and B3 were skipped.

**Next task/recommendation:** GPT-6 Astra, high reasoning, should review the unchanged R013 physical runner and prerequisites against the original contract. If no method, interpretation or acceptance decision is unresolved and all prerequisites remain valid, perform at most one separate physical attempt under 180 s/1.5 GiB; stop on the first failure, resource cap or unexplained result. No retry or changes to trace, tolerances, solver or gate. Keep Astra/high for numerical/scientific interpretation; recommend Luna/medium next only for an understood mechanical defect. GPT-6 Astra is listed in the current session catalog, and the official model page supports high reasoning for complex research and coding: https://developers.openai.com/api/docs/models/gpt-6-astra. No model switch, delegated session or automation occurred.

**Validation:** `docs/realizability/evidence/r019/audit.py` passed: 19 production hashes, archived runner hashes, all finite JSON, five phases, wrong-root/parent refusal, 103 local links/anchors and 35 JSON files. Eight Python sources parsed successfully; `git diff --check` and `git diff --cached --check` passed. Raw MPI error text is retained as JSON string data so its diagnostic spacing is preserved without trailing whitespace in the staged files.

**Git delivery:** Scoped R019 checkpoint committed as `76cfa81` (`Record R019 toy portability prerequisite pass`) and pushed successfully to `origin/main`; no force-push. This delivery note is recorded in the follow-up continuity commit.

## R020 — 2026-09-20 — Short continuation request

**User request (verbatim):**

> continue

**Interpreted scope:** Apply the Continue workflow to the handoff's bounded
R013 physical-runner review after the R019 toy portability pass. Recheck pinned
production identities, preserved evidence and every prerequisite; if no
scientific or numerical decision remains, run at most one physical attempt
under the original 180 s/1.5 GiB limits. Archive and audit complete or finite
partial evidence, update continuity, and commit/push scoped changes to the
configured upstream. This request authorizes that commit and push.

**Status:** In progress.

**Bounded plan and completion criteria:** Read the required research documents,
R013 contract, R016–R019 results/evidence and exact disposable runner; review
toy phases, wrong-root and parent refusal, output checks and resource caps.
Complete one permitted attempt or record the prerequisite/decision preventing
launch, audit the evidence, update the log and handoff with one concrete next
task and model/effort guidance, commit/push, and stop.

**Stopping conditions:** Stop before launch on a failed prerequisite or
unresolved method, interpretation or acceptance choice. After launch stop on
the first failure, resource cap or unexplained result; no retry, changed
trace/tolerance/solver, gate integration, campaign, B3, rendering or encoding.
Keep the physical B2 gate failed and `campaign_ready=false`.

**Continuity correction, 2026-09-20:** Initial stored-data review passed R016
and all 19 production identities, then the R017 auditor caught an inherited
request-history edit. Commit `76cfa81` had replaced R005's original
`Status: In progress` line with R019's toy outcome. Restored that exact original
line from `0e8e421`; R005's appended completion and validation remain intact.
The initial auditor failure and correction are recorded in
`evidence/r020/continuity_correction.json`. This is a documentation repair
within the authorized continuity work; no physical/toy attempt, numerical
failure, tolerance change or scientific choice occurred. Recheck the static
prerequisites after this correction before any numerical launch.

**Outcome, 2026-09-20:** Complete at the physical pressure-compatibility stop.
The unchanged R019 runner passed fresh prerequisites and completed P's solve,
one correction and all output checks. A_32 completed block RHS allocation,
layout validation, loading, lifting, reverse scatter and assignment, then
failed at `A_32_primary_rhs_compatibility` before solving. Its required removal
`5.856084855505123e-14` exceeded `256*eps*||b||=5.2802161649827306e-15` by
11.0906 times. No A solve, A_64 compatibility, paired comparison or retry ran.
Saved projected flux predicts the measured pressure products within the
absolute-flux arithmetic scale, supporting finite-order trace integration as
the cause. This is a numerical-method decision boundary, not another wrapper
repair. No pressure/return-flow correction or threshold change was accepted.

**Checks and resources:** All 19 production identities and 358 R014–R019
historical files matched; four historical auditors passed after the documented
R005 status restoration, with generated writes redirected into R020. Seven
runner/support files match R019 exactly. Fresh wrong-root, watchdog,
24-permutation/kernel, wrapper, full block RHS and disk phases passed in
5.630006265 s, with 144.60546875 MiB peak observed child-tree RSS and
0.057955449 s maximum sample gap. R019's parent refusal was reaudited. One
physical attempt took 59.972154446 s, with 756.99609375 MiB observed and process
high-water RSS and 0.059124924 s maximum sample gap. One 482-cell mesh, one
symbolic/numeric factorization pair and two matrix solves were recorded.
P's complete outputs reproduce R016 exactly; its physical comparison still
fails. No numerical resource limit was reached.

**Evidence and changed files:** This log (including the explicitly documented
R005 restoration), `SESSION_HANDOFF.md`, `STATUS.md`, `PROJECT_TRACKS.md`,
`docs/realizability/B2_NEXT_STEPS.md`, the current-status introductions in
`B2_MATCHED_TRACE_REVIEW.md` and `B2_BLOCK_RHS_TOY_REPAIR_RESULT.md`, the new
`B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md` and evidence index, and
`docs/realizability/evidence/r020/`. The execution manifest covers 72 exact or
parsed-equivalent artifacts; only facet JSON whitespace was compacted.
Production numerical sources/configuration and all old evidence are unchanged.

**Skips and remaining limits:** No A accuracy, paired error allocation or total
FEM error floor is established. A_64's small flux does not establish its RHS
compatibility. No coefficient vectors were saved. Full application,
dense/calibration/refinement suites, production changes, gate integration,
campaign, B3, rendering and encoding were skipped. The physical B2 gate remains
failed and `campaign_ready=false`; preparation, sensing, hardware demands and
validated movie flow remain unresolved.

**Next task/recommendation:** GPT-6 Astra, high reasoning, for the result's
bounded saved-data compatibility method review. Audit flux/moment cancellation
and nullspace normalization; compare future integration strategies preserving
the same finite reference trace and thresholds; state one justified subsequent
experiment contract or the precise unresolved choice. Specify toy coverage,
compatibility checks before primary solves, output screens, resource caps and
solve/factor inventory. No method implementation, fresh reference/quad sweep,
physical assembly/solve or retry in that review. Archive/audit, update
continuity, commit/push and stop at the review boundary. Retain Astra/high
for numerical choices and interpretation; recommend Luna/medium only for a
fully specified mechanical follow-up. Both models and supported efforts were
rechecked in the current catalog and fetched official pages using OpenAI Docs.
No model switch, delegated session or automation occurred. Next prompt:
**Continue**.

**Git delivery:** This `continue` authorizes the scoped checkpoint and push to
the configured `origin/main` upstream without force-push. Actual delivery is
reported in Git history and the final response.

**Validation, 2026-09-20:** The R020 saved-data/documentation audit passed for
72 execution artifacts, 19 production identities, 358 preserved historical
files, seven exact R019 sources, four historical reaudits, 12 Python syntax
checks, 40 finite JSON inputs, nine Markdown files, 119 local links/anchors
and 18 fenced blocks. Record:
`docs/realizability/evidence/r020/validation.json`. The first new audit draft
incorrectly compared local-certificate elapsed times for exact equality;
comparison now excludes only that timing field, while all scientific values
match. No numerical work was rerun. The physical diagnostic itself remains
explicitly failed at compatibility. Tracked documentation passed
`git diff --check` before staging.

**Staged validation, 2026-09-20:** `git diff --cached --check` passed for the
complete R020 archive and documentation, with no whitespace exceptions.

## R021 — 2026-09-20 — Short continuation request

**User request (verbatim):**

> continue

**Interpreted scope:** Apply the Continue workflow to the R020 handoff's bounded
saved-data compatibility method review. Preserve the finite reference trace,
scientific assumptions and acceptance thresholds. Audit existing evidence and
derive a justified subsequent experiment contract or identify the precise
unresolved decision. Update continuity, commit and push scoped changes to the
configured upstream; this request authorizes that delivery.

**Status:** In progress.

**Bounded plan and completion criteria:** Read required research documents,
the R013 contract, R016–R020 results and exact sources; recheck identities;
audit saved flux, normal-projection moments, pressure-nullspace normalization
and lifting. Explain both compatibility screens, compare higher fixed
quadrature with flux-moment-preserving integration, and write one review with
an explicit next experiment contract or unresolved choice. Specify toy checks,
pre-solve compatibility, output screens, solve/factor counts and resource caps.
Archive and audit saved-data derivations, update continuity, commit/push, stop.

**Stopping conditions:** Saved data and derivation only. No new physical mesh,
FEM assembly/solve, reference evaluation, quadrature sweep, method
implementation, pressure/return-flow repair, changed tolerance, gate
integration, campaign, B3, rendering or encoding. Stop at the method-review
boundary; retain the failed physical B2 gate and `campaign_ready=false`.

**Outcome, 2026-09-20:** Complete at the method-review boundary. Selected a
prospective fixed q=64/q=96 matched-trace comparison, retaining the finite
128-term trace, projection/weak-load construction, parameters and every
threshold. The new contract checks P and both A RHS compatibilities before
factorization or any primary solve, with immediate refusal on failure. It
specifies the actual observer/lifting toy coverage and one conditional physical
attempt. The shared vector-potential edge-moment alternative was derived and
deferred; it is not an automatic fallback. No new integration method or
numerical fixture was implemented or executed during this review.

**Saved-data findings:** All 19 production identities and 433 R014–R020 files
match `e96f81b`. R020's auditor passed with its generated validation redirected
into R021. All 564 saved facet records pass mass-equation arithmetic, matching
orientation, unit-normal, positive-Gram and exact-zero cap checks. The saved
q32/q64 normal-projection relative L2 steps are 1.3433188732e-8 real and
1.6209118858e-10 imaginary; these are not output error estimates. A_32's RHS
arithmetic limit corresponds to a combined flux norm 2.3184899469e-20 m³/s,
explaining why its 2.571353564e-19 real flux passes the relative screen but
fails compatibility by 11.0906 times. Flux predicts the measured pressure
products within the fixed absolute-contribution scale. A_64 assembled
compatibility remains unmeasured, and its tiny saved flux is not acceptance.

**Evidence and changed files:** `docs/realizability/evidence/r021/` contains
standard-library review/audit scripts, input identity hashes, derived arithmetic
and redirected historical validation. The new review and evidence index are
`B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md` and
`B2_COMPATIBLE_TRACE_INTEGRATION_EVIDENCE.md`. Updated this log,
`SESSION_HANDOFF.md`, `STATUS.md`, `PROJECT_TRACKS.md`, `B2_NEXT_STEPS.md`, and
the current-status introductions of `B2_MATCHED_TRACE_REVIEW.md` and
`B2_BLOCK_RHS_TOY_REPAIR_RESULT.md`. Production code/configuration and old
evidence are unchanged; no historical archive payload was duplicated.

**Skips and unresolved limits:** No fresh mesh, FEM assembly/PDE solve,
reference or quadrature evaluation, toy run, method implementation, application
or optional FEM suite, gate integration, campaign, B3, rendering or encoding.
Saved six-by-six Gram arithmetic is not a new PDE factorization. No saved
basis-integral vector permits independent recovery of facet signed flux from
moments; full A RHSs and solution vectors are absent. The proposed pair's
compatibility, output sensitivity and cost remain unknown. R020's P result,
failed physical B2 gate and `campaign_ready=false` remain unchanged. Paired
accuracy, total FEM error floor, geometry allocation, preparation, sensing,
hardware demands and validated movie flow remain unresolved.

**Next task/recommendation:** GPT-6 Astra, high reasoning, for the review's
explicit subsequent experiment contract: create a disposable q=64/q=96 runner,
validate all original prerequisites and the actual pre-solve compatibility
barrier under cumulative 60 s/512 MiB, then at most one physical child under
180 s/1536 MiB if all checks pass and no scientific choice remains. Success
inventory is three primaries, three same-factor corrections, one symbolic and
numeric factorization and six matrix solves. Preserve all R013 output/PDE,
reference and component checks. Archive complete or finite refusal evidence,
update continuity, commit/push and stop. No retry, third order, cap increase,
trace/tolerance/solver change or pressure/return-flow repair. Retain Astra/high
for numerical work and interpretation; recommend Luna/medium only for a fully
specified mechanical follow-up with focused checks and a stop before physical
interpretation. Both models are in the current session catalog; OpenAI Docs
was used to fetch their official model pages and confirm effort support. No
model switch, sub-agent or automation occurred. Next prompt: **Continue**.

**Git delivery:** This `continue` authorizes the scoped checkpoint and push
to the configured `origin/main` upstream, without force-push. Actual delivery
is recorded in Git history and the final response.

**Validation, 2026-09-20:** The R021 saved-data/documentation audit passed:
19 production identities, 433 preserved historical files, 564 facet records,
one redirected R020 re-audit, exact reproduction of saved-data calculations,
two new Python syntax checks, three finite JSON inputs, nine Markdown files,
103 local links/anchors and 23 fenced blocks. Record:
`docs/realizability/evidence/r021/validation.json`. Earlier request history is
byte-preserved and R021 occurs once. `git diff --check` passed. These checks
validate the review evidence, not the proposed numerical experiment.

**Staged validation, 2026-09-20:** `git diff --cached --check` passed for the
complete R021 review/archive and continuity documents, with no exceptions.
Only the 16 scoped documentation/evidence files are staged; no production
source or old evidence is included.
