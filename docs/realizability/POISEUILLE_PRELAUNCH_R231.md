# R231 — Poiseuille prelaunch refusal

**The single R231 launch command exited before the finite caller's `main()` ran.**
There is no numerical result, reservation, held service or FEM import. The fixed
`/tmp/navier-poiseuille-r230-once` directory remains absent. The R230 one-use
numerical allocation has **zero numerical attempts spent**, but R231's
stop-after-any-refusal rule ends this task. No second command was launched.

The [allocation](evidence/r231/allocation.json) and [finite caller](evidence/r231/run_once.py)
were committed and published as `c3b55986f0ad9bffde243423bb3d6875824c6b9f`
before launch. The checkout was clean at that commit. All 25 R230 reviewed
source hashes, the frozen manifest hash, and R229 interpreter SHA-256 matched.
The host had about 6.2 GiB `MemAvailable`, the fixed run directory was absent,
and the existing user manager reported version 249.11-0ubuntu3.22. The command
was run with host manager access as required by the R226 backend.

The [raw command result](evidence/r231/prelaunch_result.json) has exit code 1:
`ModuleNotFoundError: No module named 'verification'` at the top-level
`supervision` import in `run_once.py`. Invoking this nested file by path makes
Python use its evidence directory as the initial module search path; the caller
did not first add the repository root. The timer, caller preflight,
`supervise_once`, `SystemdBackend`, reservation, held worker and numerical
imports were never reached. The command elapsed time is not certified by the
caller. No resource counters or numerical thresholds were exercised.

Read-only reconciliation found no run directory. The user manager lists only a
historical failed `navier-poiseuille-7b32282cf40b49b4b220c1350b92272b`
service: its recorded start was 2026-09-26 00:22:36 EDT, result timeout,
`MainPID=0` and empty `ControlGroup`. This is the R226 benign expiry case,
not a new R231 worker. The R229 setup predicate remains false with 303
memory.max events; no setup or numerical result was reclassified.

Next: Astra/high reviews this prelaunch refusal and the precise one-use
allocation state. Correct and test the caller's import path using standard
library checks only, then make an explicit new go/no-go decision for the same
fixed directory and unchanged source/interpreter/caps. Stop before FEM in that
review. A later execution needs a new Continue after the review; no automatic
retry or alternate run directory follows from this zero-spent observation.

## R232 correction to the stopping decision

The user subsequently directed a change to the premature-stop rule. This page
retains the exact R231 failure and original decision as history; the failed
caller bytes remain available at commit `c3b5598`. R232 repairs the caller's
import path and verifies its timer without a manager or FEM. Because R231 never
reserved the directory or started a worker, the original one-use numerical
allocation remains zero spent. The earlier Continue's scoped authorization
persists for R232 to carry that same fixed contract forward; see the current
[handoff](../../SESSION_HANDOFF.md#next-task) for its result and stop boundary.
