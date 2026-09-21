# R081 source review and live-validation specification evidence

The [review and frozen contract](../../B2_MONITOR_LIVE_VALIDATION_CONTRACT.md)
records eleven reproduced R076 counterexamples, additional source findings,
read-only PC capability facts and the future ten-case benign suite. R076 remains
archived; no repair is claimed implemented here. Physical launch stays disabled.

| Artifact | Meaning |
|---|---|
| [audit.py](audit.py) | Standard-library fake-input audit and read-only capability collector; imports reviewed sources without running their validators/recorders. |
| [attempt_01/started.json](attempt_01/started.json) | Exclusive audit start/command; one audit attempt, no retry. |
| [attempt_01/review.json](attempt_01/review.json) | Eleven reproduced findings; 61 source bindings and original-copy preservation; disabled launch check; sandbox capability snapshot. |
| [host_readonly_capabilities.json](host_readonly_capabilities.json) | Separately approved read-only inspection outside the sandbox, to distinguish actual WSL from sandbox visibility. |
| [delegation_candidates.json](delegation_candidates.json) | Standard user-manager delegation paths and access metadata only; no cgroup operations or service startup. |
| [live_suite.json](live_suite.json) | Immutable future invocation/case/cap specification, not an implemented runner or execution authorization. |
| [documentation_validation.json](documentation_validation.json) | Final documentation/integrity, historical preservation and contract-consistency checks. |

The audit used Python 3.12.13 at `/tmp/navier-fenicsx/bin/python`. It measured
0.160194137 s from script entry through checks and 21,929,984 bytes
(20.9141 MiB) process-lifetime high-water RSS. Duration excludes interpreter
startup/final report writing, and RSS is one process, not aggregate-tree memory.
The audit set 256 MiB address-space, 10 s CPU and 120 s alarm limits after
imports; these are distinct limits, not a certification of end-to-end overhead.
Read-only metadata inspections and documentation checks are not experiments
and do not consume/reset any historical allowance.

The original R076 recorder measures validator-subprocess time, excluding its
own source hashing, startup and final persistence. Its saved 14-attempt total
0.5964585269 s / maximum child lifetime RSS 23,801,856 bytes remains unchanged;
it is not proof of whole-recorder resource compliance. See section 1 of the
review for refusal/checkpoint requirements in the next implementation.

The host inspection was invoked with Python `-c`, importing `audit.capabilities`
and exclusively writing `host_readonly_capabilities.json`. A second Python
`-c` inspected only the standard user service/slice and user-manager socket
metadata. No Windows program, live adapter workload, cgroup write, signal,
FEM/MPI/JIT, mesh/assembly/solve, physical attempt, render or encoder ran.
No task process remains; the independent user-managed Mac build was not checked.

To reproduce the counterexamples in a future review, use a **new output path**:

```bash
/tmp/navier-fenicsx/bin/python -B docs/realizability/evidence/r081/audit.py --output /tmp/r081-new-review
```

This is not the current next task. Do not rerun R076's recorder, which mutates
its archive. Follow the [handoff](../../../../SESSION_HANDOFF.md#next-task)
for the new fixture-only repair and its separate budget.
