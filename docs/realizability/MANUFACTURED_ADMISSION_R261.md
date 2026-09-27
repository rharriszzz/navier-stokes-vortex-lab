# R261 — Bounded diagnostic pilot source review and one-use admission

2026-09-26 (America/New_York), PC/WSL `daisy`. **One NEW later n=2
manufactured spatial BE diagnostic pilot is admitted; zero attempts are spent
in this review. Stop before launch.** All seven prior allocations remain spent.
The [single next task](../../SESSION_HANDOFF.md#next-task) controls execution.

## Source decision

The [R259 diagnostic contract](MANUFACTURED_FAILURE_REVIEW_R259.md) and
[R260 implementation](MANUFACTURED_DIAGNOSTICS_R260.md) were reviewed against
the worker, driver, helper and fake tests. Arming follows validated reservation,
admission and source verification. Thirteen ordered begin/end markers cover
pinned imports through completion. An ordinary failure attempts a separate
exclusive `failure.json`, retaining stage, source binding, exception type and
bounded file/function/line traceback. The walk, field and 32,768-byte UTF-8
limits retain the deepest observed frame. Diagnostic failure preserves exit 1.
The record is evidence of location only; controller numerical and resource
acceptance still require their original gates.

This review repaired two small diagnostic defects. A newline or carriage
return in an exception message now stays in the saved message while the stderr
summary remains one line; `str(exc)` raising a `BaseException` gets the fixed
format fallback. The `return_sampling_and_report` end marker now follows
construction of the driver's returned payload, so a failure while building it
does not falsely mark that stage completed. The numerical calls, operation
counts, solver, exact history/corrected load, diagnostic scalar routes,
manifest and scientific/resource gates remain fixed.

The [46-file inventory](evidence/r261/source_inventory.json) binds all R260
source/test/pin/reference files with the three reviewed changes. The
[finite caller](evidence/r261/run_once.py) and [allocation](evidence/r261/allocation.json)
are separately bound by SHA256, as are the [eleven runtime artifacts and four
library resolutions](evidence/r261/artifacts.json). The frozen proposal and
contract hashes match R257. The new fixed directory is
`/tmp/navier-manufactured-r261-once`; it and any dangling link are absent at
review. The R257 caller and directory remain spent and cannot be reused.

The [114 source/fake tests](evidence/r261/tests.json) and [six fake caller
checks](evidence/r261/caller_tests.json) pass under pinned Python 3.12.13
without numerical imports. Saved R246/R253 validators replay PASS; R258
remains INCOMPLETE. The [read-only audit](evidence/r261/audit.json) verifies
84 original raw files, seven spent reservations, absent recorded PIDs/cgroups,
the 46 source hashes, interpreter/archive and runtime artifacts. No manager,
worker, reservation, numerical import, JIT, assembly or solve ran here.

## One-use execution boundary

The new caller accepts only an exact clean launch HEAD after a later Continue
STARTED publication. It checks the 46 source hashes, caller/allocation,
manifest/contract, interpreter, eleven artifacts, four resolutions, cached
archive, new directory absence, host memory/controllers and reviewed manager
version before reservation. Its timer starts before project imports. The
existing held worker and finite supervisor enforce the same 180-second outer,
15/150/15-second setup/work/finish, independent 149-second worker plus one
second grace, 1536 MiB/no-swap, 32-task and one-rank/thread limits. The
numerical envelope remains 2,000,000 bytes and latest sparse system is capped
at 512 DOFs, 4 MiB and 65,536 entries. The same n=2, t=dt=1/8, 402 mixed /
405 bordered DOF, degree-24/26 60-scalar scientific policy applies. No
convergence, tank or B2 work is admitted.

Reservation/directory creation or partial worker start spends this one new
allowance, including an INCOMPLETE result. Preserve every partial file,
failure record, resource receipt and cleanup result; stop after one outcome.
A proven caller/preflight error before reservation, managed worker and
numerical import is recoverable only under the repository recovery protocol:
save the error and elapsed gap, verify the fixed directory and manager have no
new task process, repair/test the cause and publish a clean binding before
continuing the same unspent allocation. Uncertain state stops for review.
There is no alternate directory, gate relaxation or inferred reset.

A future PASS would establish only one-level discrete solve and diagnostic
consistency. The actual R258 recursion site/import progress, current FEM/JIT
behavior, manufactured accuracy, resource peaks/events, convergence and rank
remain unknown. The saved R242 INCOMPLETE and R229 setup predicate remain
unchanged. Resource sampling before final handshake/exit and unobserved save
tails remain stated measurement limits.

**Next:** use `/new` at this published source/admission boundary, select
GPT-6 Sol / high, then Continue on PC/WSL `daisy` to run only the fixed R261
caller once after clean synchronization and STARTED publication. Preserve raw
evidence, hash copies, cleanup and spent state, publish the result, then stop
for Astra/high interpretation. [Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-sol)
lists high reasoning support; task fit is judgment, account availability is
unverified, and no model/session switch occurred in this review.
