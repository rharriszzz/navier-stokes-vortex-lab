# R088 composed fixture integration

The [schema and transition contract](contract.md) and new
[implementation](source/integration.py) connect ownership, supervision, host
protocol, cleanup, durable evidence and R070 acceptance in one fixture path.
The source is a new copy; R084 and all earlier archives remain unchanged.
No archived validator or recorder main was executed.

The first bounded attempt passed all **14 registered groups**. Its
[fixture evidence](attempt_01/output/fixtures.json) retains a complete positive
composition with six exact integer zeros, a delayed-write refusal, and the fake
independent-guard event trace. [Progress](attempt_01/output/progress.json) records
registration and every completed function. The
[guard receipt](attempt_01/receipt.json) and [ledger](ledger.json) record:

- Child startup through final persistence/exit: **0.584059735 s**.
- Observed guard time before its own final persistence: **0.632527652 s**.
- Conservative charge including a five-second unmeasured guard-write reserve:
  **5.632544718 / 120 s**.
- Validator lifetime peak RSS: **23,941,120 / 268,435,456 bytes**.
- Zero exit, no timeout/resource stop/retry; Python **3.12.13**.

The exclusive [start](attempt_01/started.json), pre-release
[binding](attempt_01/bound.json), and [snapshot inventory](attempt_01/snapshot/inventory.json)
bind every executed source and saved external input, including historical
ledger/reconciliation bytes. The child runs the snapshotted source and verifies
that inventory. `run.py` refuses an existing `attempt_01`; do not copy/rename it
or create another request ID to bypass the consumed allowance. The readable
`source/` matches the executed snapshot; the recorder source matches too.
The copied R070 legacy guard is preserved byte-for-byte behind stricter composed
acceptance; both its physical entry and the new physical API remain disabled.

| R085 finding | New path | Executed evidence |
|---|---|---|
| H01 ownership/composition | Frozen Ownership/Domain, Owner transitions, all-state finalizer, accept_sentinel | Positive composition; all 16 state/domain combinations; both stop and verification failure orders; repeated finalization; rebound owner/cleanup mismatches |
| H02 callbacks/deadlines/persistence | Clock, active boundaries, shared finalization deadline, candidate+receipt | Exact 5 s success/5.001 s refusal, 6 s write refusal, shared 3+2.001 s cleanup refusal, clock failures, post-release unknown counts, absolute 50 ms schedule |
| H03 terminal/ordered/fixed framing | One HostProtocol in supervise | Failed request remains terminal, regressing brackets, oversize/trailing/multiple/EOF/API frames, Boolean/float protocol types, fixed 4096 bytes, send/freshness bounds |
| H04 types/input/accounting | Exact types, snapshot inventory, supervised validator, strict recorder_policy | Boolean return-code rejection, preserved R084 arithmetic, open/unknown/resource refusals, source mutation rejection, all progress/source/output bindings |

These rows describe tested repairs, **not a live or whole-recorder certificate**.
The independent guard test is a deterministic event model. Stop dispatch must
be nonblocking in the future OS adapter; no native watchdog, handle ownership,
cgroup cleanup, Job/launcher exit or hung-kernel behavior was exercised.
The fixture subprocess guard covers the validator's imports through its final
fsync and exit. Guard startup before its timer and its own receipt/ledger fsync
and exit remain excluded; the five-second reserve is charged, not measured or
independently enforced. Acceptance review must retain this qualification and
resolve the outer measurement boundary before OS implementation.

[Documentation validation](documentation_validation.json) checks baseline/archive
preservation, log prefixes, links, syntax/finite JSON, immutable source/input/output
bindings and lifecycle/next-task consistency. The full staged whitespace check
reports one blank-at-EOF in primitives.py and its executed snapshot; those bytes
are retained as an explicit source-preservation exception. It does not replay
the fixtures.

No native/build/startup, live OS/cgroup/signal/helper/workload, FEM/MPI/JIT,
mesh/solve, render/encode or physical run occurred. No background task remains;
no ignored input needs transfer. Physical limits remain **180 s / 1536 MiB**,
q64/q96 remains unused and B2 physical accuracy remains failed. The independent
Mac POV-Ray build is still unverified.

The [single next task](../../../../SESSION_HANDOFF.md#next-task) is Astra/high
acceptance review of this composition, measurement boundary and future OS-source
admission. No new fixture allowance or OS implementation is implied by this
result. User reporting procedure and the subsequently supplied `/new` excerpt are
recorded in R088. The pre-run input snapshot retains the earlier missing-output
note; the later arrival is an additive log event, not a historical snapshot edit.
