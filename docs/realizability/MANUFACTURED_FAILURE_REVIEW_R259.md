# R259 — Manufactured worker failure review and diagnostic repair contract

2026-09-26 (America/New_York), PC/WSL `daisy`. **R258 remains INCOMPLETE and
its allocation remains spent. The failure site cannot be recovered from the
saved evidence. Implement bounded failure diagnostics next; zero new numerical
attempts are admitted.** Follow the [single task](../../SESSION_HANDOFF.md#next-task).

## What the evidence establishes

The [audit](evidence/r259/audit.json) verifies all 84 retained raw originals
across seven spent reservations, with recorded worker PIDs/cgroups absent.
It reproduces R258's ten-file audit and the saved R246/R253 PASS validators.
All 44 R257 source/test/pin/reference files, eleven runtime artifacts, four
library resolutions, cached archive and interpreter hashes still match.
R242 remains INCOMPLETE and the R229 setup predicate remains false.

R258's worker reached the held handshake, the controller checked effective
containment and published release, and the worker exited 1. Its only stderr is
`RecursionError: maximum recursion depth exceeded`. No numerical, latest-system,
finished, exit-acknowledgement or resource-snapshot file exists. The final
controller reason concerns missing resource evidence; the earlier worker
failure is retained in `run.log`. Empty cleanup is established independently
of resource acceptance. Missing peak/event observations cannot be treated as
zero, and timing cannot establish which imports or computations completed.

The source path after release is:

```text
thread check → load_pinned_modules → LatestSystem constructor
→ run_manufactured:
  mesh/space/geometry → history/lift interpolation → primary forms/compilation
  → compatibility/initial system → checked Newton → both-degree diagnostics
  → return sampling/report
→ save numerical.json → completed handshake
```

The first driver log with computational progress is the latest-system receipt,
emitted before the first factorization; individual diagnostic form/assembly
markers come later. There is no earlier import/mesh/form progress receipt.
The missing latest-system file places no positive observation beyond release.
Source ordering requires persistence before a sparse correction, but it does
not identify the preceding failing operation.

The top-level exception handler in `manufactured_worker.py` prints only the
exception type/message, discarding the traceback. The [injected probe](evidence/r259/probe.py)
executes that exact AST entry handler around the real worker `main`, with the
manager, release, numerical importer and numerical operations replaced by
fakes. It injects the same RecursionError at three distinct sites:

| Injected site | Distinct prior progress | Observed stderr/exit |
|---|---|---|
| Pinned importer | Fake held release returned | Exactly R258's line; exit 1 |
| Driver entry | Fake importer returned | Exactly R258's line; exit 1 |
| Driver's `create_cube` call | Real driver validation reached using injected modules | Exactly R258's line; exit 1 |

A fourth, successful fake path reaches fake save/completion and exits 0.
An import guard rejects all numerical module imports. The [four checks](evidence/r259/probe.json)
pass and create no real reservation, worker or manager connection. This proves
the observation is ambiguous; it does **not** reproduce R258's actual recursion.

The prior fake integration test replaces `create_cube`, geometry, interpolation,
`step_forms`, `Assembler`, sparse solve and diagnostic assembly. Its routing
checks remain useful, but its PASS does not cover real post-release APIs. The
manufactured polynomial has 30/30/5 velocity terms, eight pressure terms and
221/222/11 forcing terms. These source counts are context, not evidence that
expression depth caused the error. Neither increasing the recursion limit nor
rewriting polynomial/UFL algebra is justified by this log.

## Fixed next implementation

Implement the following source-only diagnostic repair, preserving R255's
fixture, source policy, numerical report schema, solver and resource gates.
Runtime changes should be limited to `manufactured_worker.py`,
`manufactured_driver.py` and one optional small standard-library diagnostic
helper, with focused tests. Keep the old caller/allocation, all old evidence,
Poiseuille/rotation workers and numerical mathematics unchanged.

### 1. Retain a bounded failure location

On an ordinary worker exception, preserve the original exit-1 behavior and
attempt to save one separate `failure.json` in the already validated reserved
directory. Never create a directory or replace an existing diagnostic. Enable
that destination only after reservation/admission and source verification;
invalid arguments or an unmatched reservation must not write to a supplied path.
Keep the original one-line stderr summary for compatibility.

The failure record must contain a schema identifier, fixture, source binding,
last begun stage and last completed stage, exception type, bounded exception
message, and a bounded traceback with file/function/line fields. Do not save
frame locals or call `repr` on numerical objects. Prefer reading code metadata
directly from traceback frames; no evaluation of source expressions is needed.
The record is diagnostic evidence only and cannot establish numerical or
resource acceptance.

Fixed limits: at most 32 frames (first eight and last 24 when truncated), 512
characters per file field, 256 per function field, and 512 for the message.
Walk at most 4,096 traceback links; disclose both frame truncation and an
unfinished walk. Bound the serialized UTF-8 JSON to 32,768 bytes before opening
the exclusive file. If escaping/UTF-8 exceeds this cap, shorten fields and/or
reduce retained frames with explicit truncation flags, retaining at least the
deepest observed frame and stage/type when available. Record whether exception-message formatting failed or was
truncated; use a short fixed fallback if `str(exc)` raises. Record only the
current exception's traceback; disclose that chained exceptions are omitted.
Failure to format/write this diagnostic must retain exit 1 and a short fixed
stderr fallback, never replace the scientific failure with success or start a
second operation. No recursion-limit change, recursive traceback formatter,
unbounded JSON dump, traceback locals or new dependency.

The existing numerical envelope remains unchanged. The controller may continue
to ignore `failure.json` for acceptance; its existing worker-exit/resource rules
already require INCOMPLETE. No controller/resource-monitor redesign is needed.

### 2. Record stage boundaries without changing computation

Use fixed labels and a small injected callback from the worker into the driver.
The driver callback defaults to a no-op for existing callers/tests. Maintain
last-begun and last-completed labels and emit flushed constant begin/end lines
to the existing worker log. Do not print states, expressions or exception
objects in those markers. An end marker means the corresponding call returned,
not that its numerical gates passed. The failure record snapshots those labels.

Use these boundaries, preserving the order and number of original operations:

| Owner | Stage |
|---|---|
| Worker | `imports`, `recorder_init` |
| Driver | `mesh_and_geometry`, `history_and_lift`, `primary_forms`, `primary_compilation` |
| Driver | `compatibility_and_initial_system`, `newton` |
| Driver | `diagnostics_24`, `diagnostics_26`, `return_sampling_and_report` |
| Worker | `numerical_save`, `completion_handshake` |

Place `imports` begin immediately before `load_pinned_modules` and end only
after it returns. Construct the recorder in its own statement before the driver
call. Place primary form construction and `Assembler` construction in separate
stages. Existing per-scalar diagnostic markers and linear receipts remain.
Markers must add no numerical call, repeated import, assembly, solve, retry,
new process, manager query or enlarged time allowance. If the completion
handshake fails after numerical save, the overall result still remains
INCOMPLETE. Stage bookkeeping belongs to the same supervised worker and timer.

### 3. Required source-only checks

- Demonstrate that import, mesh/form, solver and save/handshake failures produce
  different saved stages and useful file/function/line locations while all
  retain exit 1. Use injected failures; no real numerical imports or manager.
- Prove the exact successful operation order/call counts are unchanged, and
  stage markers contain only fixed labels. Reuse the current 60-scalar routing
  test and exact-history/corrected-load assertions.
- Exercise a deep recursive exception without changing the interpreter's
  recursion limit; assert frame/message/file and total byte bounds, truncation
  flags, deepest available frame and no captured locals. Include a non-ASCII
  message because the persistence cap is bytes, and a message whose `__str__`
  raises. Fake a longer-than-4,096 chain if needed to check the walk limit.
- Exercise existing `failure.json`, denied/unmatched reservation and write
  failures; no overwrite/directory creation, no success and no new work. Test
  failures before verified release still cannot import numerical packages.
- Run the full standard-library/injected-fake regression suite (104 tests in
  R257 before additions) and saved R246/R253 PASS validators. Check R258 raw
  hashes and all seven spent reservations; preserve source/manifest/policy
  bindings by reporting the intentional source changes, not editing R257's
  frozen inventory to make it match.

Do not add a caller or grant an allocation during implementation. Publish the
source repair/tests and stop for a separate Astra/high source/admission review.
That review may later admit one fresh diagnostic pilot under the same fixed
scientific/resource gates, or identify a blocker. It must bind new reviewed
source and a fresh directory. R257's allowance remains spent regardless of the
new instrumentation. A future trace may justify a specific code repair; this
review does not promise that diagnostic changes fix the numerical failure.

## Review completion and next task

Changed: this review/implementation contract, injected probe and read-only
audit/checks, seven current status/index pages, request/lifecycle/handoff.
Checks: four guarded fake paths, saved R258/R246/R253 replay, all 84 originals,
seven spent reservations with absent PIDs/cgroups, 44 unchanged source hashes,
11 artifacts/four resolutions/archive/interpreter, JSON/AST/local links,
append-only logs, request IDs and whitespace. Existing 104 regressions are
reused because no runtime/test source changed. Skipped: numerical imports,
manager/worker, reassembly/solve, new admission, full convergence/tank/B2,
physical/render and Mac transfer. Unknown: actual recursion site/import progress,
pilot accuracy/budgets and resource events, convergence/rank, R242 cause and
artifact-label origin.

**Next: GPT-6 Sol / high implements this fixed diagnostic repair and tests,
publishes and stops for Astra/high source/admission review. Continue in this
chat:** the diagnosis and implementation contract are directly connected and
no current context fraction was supplied. The [official Sol model page](https://developers.openai.com/api/docs/models/gpt-6-sol)
was searched/opened and confirms high support. Model suitability is judgment,
account-specific availability remains unverified, and no switch is performed.
PC retains ownership; Mac remains released. Next prompt: **Continue**.
