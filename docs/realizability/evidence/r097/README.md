# R097 completion-certificate repair

New source/fake-only implementation of [R096 J01–J04](../../B2_MONITOR_R088_REVIEW.md),
from base `dc73ec0`, STARTED publication `57b90a1`. The
[contract](contract.md) was specified before implementation/execution.
Acceptance review is next in the [handoff](../../../../SESSION_HANDOFF.md#next-task).
No OS-source or live admission is claimed.

| Repair | Implementation | Registered evidence |
|---|---|---|
| J01 persisted aliases | `integration.validate_candidate` independently validates both candidates; canonical bytes and durable digest must agree | `test_j01_independent_durable_types` mutates durable schema/owner/fields and both candidates with recomputed bindings |
| J02 monitor evidence | `certificate.validate_monitor` checks all count keys/types/known agreement, nonempty samples, strict sequence, finite brackets/RSS, membership and terminal root evidence | `test_j02_counts_and_samples`; unknown monitor counts retained, validated child supplies final exact zeros |
| J03 authoritative admission | Frozen Admission binds owner, Policy, clock, identities and three absolute reservation boundaries; candidate/receipt bind its hash | `test_j03_rebased_cleanup_and_admission` and exact active/cleanup/outer boundaries |
| J04 independent receipt gate | Strict outer receipt binds all documents; separate frozen TerminalWitness supplies receipt durability, observer exit and prior lifetime backstop | missing/mismatched/open/stopped outer and unpersisted/late/unconfirmed witness groups; trusted facts are injected, no OS adapter implemented |

The remaining groups cover positive full composition/physical refusal, both
domain cleanup failures/idempotency/unknown counts, and source/owner bindings.
Nine unique registered functions ran exactly once on the first attempt. No
historical validator/recorder main was run. New `integration.py` derives from
R088; `primitives.py` only removes trailing blank lines, and `host_protocol.py`
and `r070_legacy.py` are byte-identical copies. The new validator reuses the
fixture helper shape and provides a new nine-function registry.

- [Source](source/), [one-shot recorder](run.py), [ledger](ledger.json).
- [Admission/start](attempt_01/started.json), [prelaunch bindings](attempt_01/bound.json),
  [executed snapshot inventory](attempt_01/snapshot/inventory.json).
- [Progress](attempt_01/output/progress.json), [results and partial examples](attempt_01/output/fixtures.json),
  [actual execution receipt](attempt_01/receipt.json).
- [Integrity checker](validate_docs.py), [integrity result](documentation_validation.json).

Python 3.12.13. Validator startup through output persistence/exit: **0.325711412 s**;
lifetime peak RSS **23,834,624 B** under **268,435,456 B** address-space limit.
Observed guard time **0.349626566 s**, charged **5.349626566/120 s** including the
five-second **unmeasured, unenforced** final reserve. Child wall limit 60 s,
CPU 10 s, one MiB per output; 20 seconds reserved for setup/final evidence before
release. Exactly one attempt, no failure, retry, timeout or resource stop.

Actual guard interpreter startup before ENTRY and its final receipt/ledger
persistence and exit are excluded. Fake successful TerminalWitness values do
not certify those actual intervals. Whole-recorder/live certification stays
false. Observer independence, trusted-adapter authentication, real backstop
arming and terminal observation remain unimplemented OS obligations. The
backstop's own lifetime is outside the defined observed boundary, explicitly
not certified by its own output. Review must assess that boundary before any
future OS implementation admission.

All historical evidence/allowances and physical 180 s / 1536 MiB limits remain
unchanged; q64/q96 unused and B2 accuracy failed. No native source/build/startup,
live OS/cgroup/signal/helper/workload, FEM/MPI/JIT, render, encode or physical
work occurred. Fixture child exited/reaped; temporary fake files cleaned.
