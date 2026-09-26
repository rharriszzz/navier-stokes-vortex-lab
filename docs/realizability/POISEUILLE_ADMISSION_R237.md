# R237 — One instrumented Poiseuille diagnostic fixture admitted

**GO for one NEW later bounded n=2 Poiseuille attempt, 0/1 spent.** Its fixed
exclusive directory is `/tmp/navier-poiseuille-r237-once`. No reservation,
numerical import or live scope occurred in this review. A later **Continue**
authorizes the prepared caller's execution after the normal clean start protocol.
R232 and R235 remain INCOMPLETE and spent 1/1 in their original directories.

## Why this attempt is justified

[R236](POISEUILLE_KSP_REVIEW_R236.md) added a tested minimal diagnostic for
R235's ambiguous refusal: integer KSP reason, nonfinite-answer count and optional
PC failure reason. The operator, solver and gates are unchanged. This attempt
is admitted to measure the failure category, not on evidence that the solver
has been repaired. Another incomplete result may still answer the immediate
question and guide a specific subsequent source/method review.

The saved R235 log cannot recover those quantities. The diagnostic has passed
scripted status/answer/error and cleanup checks within the 62-test suite. It
uses the existing flushed worker stderr path, whose real R235 output was
retained. Therefore the expected information gain is concrete and the change
adds no extra solve, dense matrix, monitor or alternative solver. If termination,
an earlier API error, or a cleanup exception prevents the diagnostic from being
saved, retain that incomplete outcome; it does not justify an automatic retry.

The [R234 contract](POISEUILLE_ADMISSION_R234.md) supplies the unchanged fixture,
containment and acceptance requirements. R226 benign host evidence and R235's
actual held limits/exit/cleanup remain relevant because supervision is unchanged.
R229's installed-artifact checks support using its interpreter while its setup
resource predicate stays false (303 memory.max events, no OOM/kill). No missing
R235 resource snapshot or short runtime is treated as a numerical-footprint
measurement or a resource pass. Live capacity and manager availability must be
refreshed by the caller during the actual launch.

## Frozen allocation and caller

[allocation.json](evidence/r237/allocation.json) binds the new charge, both old
spent charges, source inventory, caller digest, interpreter and caps.
[run_once.py](evidence/r237/run_once.py) derives from the reviewed R234 caller
with only description, owner, output directory and source-inventory changes.
Old callers, allocations and ledgers remain unchanged.

| Requirement | Contract |
|---|---|
| Fixture | One n=2 Poiseuille BE step, dt=0.125, exact history/lateral trace, non-exact free velocity guess and checked correction |
| Source | All 25 `source_sha256` entries in R236 checks.json; actual clean launch HEAD bound to admission/reservation/held worker |
| Directory | `/tmp/navier-poiseuille-r237-once`; one exclusive reservation, no alternate directory |
| Interpreter | `/tmp/navier-fenicsx-r229/bin/python`; resolved SHA-256 `5f083df36ec986d5cd13d2549ca6cfe1ddaf658509f9e419b454b2fb375c27a3` |
| Manifest | `verification/nonlinear_port/future_fem.json`; SHA-256 `7a8bda917e6b46994ad24c68e0b6c6013b7d6776f90c86a6de763f31f52fa558` |
| Solver | Serial PREONLY / LU / PETSc; fixed row scaling, no ambient options, fallback, shift or operator change |
| Time | 180 s observed outer interval; 15 s setup / 150 s work / 15 s finish; 149 s independent worker runtime plus 1 s stop grace |
| Resources | 1536 MiB whole worker cgroup, no swap, 32 tasks, one rank/thread, at most 20,000 mixed u/p DOFs |
| Resource acceptance | Zero memory.max, OOM, OOM-kill and PID-limit events; finite saved peak, actual exit and empty cleanup |
| Numerical acceptance | Unchanged compatibility/Gram, Newton/true residual, eta/gauge/both fluxes, degree-24/26 comparison, return sampling, oracle errors and physical endpoint budgets |
| Package identity | Existing exact versions/artifact gate; only the verified FFCx 0.10.1 package artifact permits embedded/runtime 0.10.0 |

The manifest stays non-executable by itself. Only the prepared caller creates
the executable one-use admission after clean preflight. Before launching,
verify that logs and directory inventory still show this new allowance unspent,
check the caller digest and R236 inventory, publish STARTED, and obtain the
actual full `git rev-parse HEAD`. Invoke the R237 caller once with that commit
using the pinned interpreter. Keep the checkout unchanged during execution.
Do not prewarm imports or invoke the worker directly.

## Interpret the diagnostic without changing acceptance

If the same refusal is reached, retain the complete `worker.log` line containing
`ksp_reason`, `nonfinite_answer_entries` and `pc_failed_reason`.

| Observation | What it establishes / next interpretation |
|---|---|
| KSP reason nonpositive, count zero | Status gate refused despite a finite answer; a finite answer alone is insufficient |
| KSP reason positive, count nonzero | Answer finiteness gate refused despite positive status |
| KSP reason nonpositive, count nonzero | Both gates refuse; neither alone explains the other |
| PC reason identifies a pivot category | Factorization reported that category; singularity, pivot location and a suitable method change remain unresolved |
| PC reason identifies memory failure | PETSc reports a factor memory failure; cgroup events still need separate saved evidence |
| PC reason unavailable | Preserve its exception type and the primary KSP/count evidence; do not substitute a guessed code |
| No matching line / earlier exception | Save the actual failure and missing fields; no inference or retry |
| Solve proceeds further | Apply all unchanged numerical/resource gates; diagnostics alone never accept the run |

Code interpretation uses the pinned PETSc version and R236's linked official
source/API review. The executable diagnostic reports raw codes. This review
adds no runtime classifier or altered aggregate status. A useful refusal remains
INCOMPLETE, even when it answers the diagnostic question. The diagnostic does
not save the matrix, prove mixed rank or recover the prior run's values.

## Consumption, evidence and checks

Directory/reservation creation or any partial worker start spends the new
allowance, including failures and missing evidence. After that boundary, stop,
retain all raw records, actual exit/elapsed gaps and cleanup, and mark 1/1 spent.
No second command, alternate directory or changed solver/gate is authorized.
A demonstrated caller/preflight error before reservation, worker and numerical
import remains recoverable only by preserving its evidence, verifying absent
fixed directory and no new manager task, fixing/testing the cause, publishing a
clean source binding, then continuing the same unspent contract. Uncertain
process state requires review. Neither old charge can be reset by missing files.

This review verified all 25 R236 source hashes and three retained test-evidence
hashes, 20 old raw files and their local originals, 17 R229 artifact hashes,
interpreter binary/current conda history, both old reservations and absent
recorded PIDs/cgroups. The new directory is absent, including no dangling link.
The unchanged 62-test source suite and R226 host suite were reused, not rerun.
No package installation, environment interpreter execution, numerical import,
manager connection, live probe or full environment rescan occurred.

[check_caller.py](evidence/r237/check_caller.py) passed outside-directory imports,
timer-before-imports/preflight, changed instrumented-source and existing/
dangling-directory refusals before manager/reservation. Its Git answers are
synthetic only for those explicit refusal cases. The unmocked direct caller
with an invalid commit exited 1 before manager/reservation; its caller-observed
interval was 0.016646823 s (parent observed 0.038151012 s). That intentional
preflight test is not a numerical attempt. Two new Python ASTs and all new JSON
files were checked; [checks.json](evidence/r237/checks.json) retains the bindings.

Next: **GPT-6 Sol/high** executes the prepared caller once after a later Continue,
preserves the raw diagnostic/result and cleanup, publishes and stops. Return to
Astra/high for interpreting the failure or any scientific/method/admission change.
No new chat is needed. [Official OpenAI Docs](https://developers.openai.com/api/docs/models/gpt-6-sol)
was searched/opened for Sol/high support; task fit is judgment, not an account
check or an agent-initiated model switch. Follow the
[single handoff task](../../SESSION_HANDOFF.md#next-task). PC/WSL daisy retains
ownership; Mac remains released. Full suite, rotation, tank/B2, physical/render
work and installation remain unadmitted.
