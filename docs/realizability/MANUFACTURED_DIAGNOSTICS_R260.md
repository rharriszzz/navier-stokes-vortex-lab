# R260 — Bounded manufactured failure diagnostics

2026-09-26 (America/New_York), PC/WSL `daisy`. **The R259 source repair is
implemented and tested. R258 remains INCOMPLETE; all seven reservations remain
spent. No new numerical attempt is admitted.** Follow the
[single current task](../../SESSION_HANDOFF.md#next-task).

## Source result

The manufactured worker now arms a `StageTracker` only after reservation,
admission and source verification. It emits fixed begin/end markers for the
thirteen R259 stages from pinned imports through completion. The driver uses an
optional progress callback around its numerical blocks, preserving the prior
operation order, counts, solver, mathematics and acceptance gates. The old
numerical report and controller schemas remain unchanged.

On an ordinary worker exception, the entry handler retains exit 1 and attempts
one separate exclusive `failure.json` in the validated directory. The record
contains the source binding, last begun/completed stage, exception type and
bounded message, plus file/function/line traceback entries. It reads no frame
locals and evaluates no numerical object `repr`. It walks at most 4,096 links,
retains at most the first eight and last 24 frames, truncates fields to the
contract limits, and checks the 32,768-byte UTF-8 JSON cap before opening the
file. If diagnostic persistence fails, the worker still prints a fixed failure
summary and exits 1. The record is location evidence only; it does not make an
INCOMPLETE numerical or resource result acceptable.

The [source audit](evidence/r260/audit.json) verifies the 44 prior R257
bindings: 41 unchanged and exactly three expected existing files changed. It
adds the helper and focused test to a 46-file current inventory. The manifest,
eleven runtime artifacts, four library resolutions, cached archive and pinned
interpreter remain bound. All 84 original raw files across seven spent
reservations still match their saved hashes; recorded PIDs/cgroups remain
absent. Saved R246/R253 validators replay PASS, R258 remains INCOMPLETE,
R242 remains INCOMPLETE and R229's setup predicate remains false.

## Checks and limits

The [113-test run](evidence/r260/tests.json) under pinned Python 3.12.13 has
zero failures/errors and no numerical modules loaded. Focused fake tests cover
six injected failure locations, stage order and the successful operation path,
pre-arm refusal, exclusive write, unsafe exception formatting, traceback walk,
frame and UTF-8 byte bounds, and entry-handler fallback when persistence fails.
The [completion checks](evidence/r260/checks.json) cover AST/JSON, local links,
append-only logs, request/lifecycle continuity and whitespace. No real FEM
import, manager connection, worker, reservation, JIT, assembly or solve ran.

R258's actual recursion site, FEM import progress, resource peaks/events and
pilot accuracy remain unknown. The repaired source has no new allocation or
executable caller; R257's old caller remains bound to the spent old source and
must not be reused. Full convergence/tank/B2, physical/render and Mac transfer
remain outside this task.

**Next:** GPT-6 Astra/high reviews the repaired source against the R259
contract and evidence, then publishes a separately bound new one-use admission
and caller or a precise blocker. Stop before launch. Any later execution needs
a fresh allocation and its own clean Continue lifecycle.
