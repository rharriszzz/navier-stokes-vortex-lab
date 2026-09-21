# R088 fixture integration contract, schema 4

This is the new R085 H01–H04 repair interface, using R081/R083 policies.
All effects are injected. No OS helper, containment unit, signal, native source,
FEM import or physical launch is provided. Physical limits remain 180 s / 1536
MiB and q64/q96 remains unused. Historical evidence and allowances are preserved.

## Ownership and transitions

`Ownership` is frozen and binds run ID, exact positive integer attempt, nonce,
source manifest digest and the two independently acquired resource domains.
Each domain has immutable process identities, a container identity token
(Linux delegated unit/workload or native Job) and root-reaper/launcher identity.
A missing domain denotes not acquired, never successful observed cleanup.
Tokens are fixture values, not live handles or permission to open a path.
The future acquisition layer must register each acquired resource before any
operation that can fail; this implementation starts with that owned inventory.

| Current state | Normal next state | Failure/stop |
|---|---|---|
| RESERVED | OWNED_HELD | STOPPING |
| OWNED_HELD | READY | STOPPING |
| READY | RUNNING | STOPPING |
| RUNNING | STOPPING | STOPPING |
| STOPPING | FINALIZED | preserve errors; attempt both domains |
| FINALIZED | return immutable saved result | never repeat callbacks or clear failure |

Failures latch and prevent release/acceptance. Finalization is valid from every
acquired state, including held work and invalid policy. Dispatch stop to both
owned domains before observing either. Dispatch is a nonblocking interface;
a future independent OS guard is required if an injected implementation blocks.
The fixture event model checks guard progress while an inner generator remains
blocked. It does not certify live independence, thread safety or kernel cleanup.

A workload observation must match its owned unit/identities/reaper and show
root reaped, empty complete membership, `populated=false`, no survivors/errors.
A helper observation must match its Job/identities/launcher and show exact
integer active-count zero, verified launcher exit, empty complete membership,
no survivors/errors. Nonapplicable domain fields must be null. No caller-supplied
`confirmed=true` can replace these observations.

## Time, protocol and persistence

Policy uses the existing 50 ms absolute tree phase, 0.5 s host requests,
strict send+0.5 s reply bound, previous accepted send+1 s freshness,
1024 MiB runtime Windows floor, RSS `> cap`, and active deadline `>=` stop.
Launch rechecks guest >=4096 MiB and Windows >=cap+1024 MiB plus acquisition age
before release. Guest/host values are independent. Cleanup reserves five seconds
before release, is bounded by the shared outer deadline, and permits equality
only at the cleanup boundary. Every returned callback, including persistence,
is followed by a finite, nonregressing clock check. Clock failure revokes success
but cannot skip the second cleanup domain. Stop dispatch to both comes before
those verification clock reads, preserving independent requests on clock failure.

One HostProtocol instance is authoritative for request, transport and supervisor.
Any request/reply/EOF/overflow/API/time error is terminal; ordered local brackets,
exact integer schemas/identities and the fixed 4096-byte line bound are mandatory.
No widened constructor bound or new valid reply revives a stopped protocol.

The durable cleanup document has status `candidate`. It cannot certify itself:
the receipt, emitted after persistence returns, binds its canonical digest and
records the post-write clock and any errors. R070 acceptance requires both,
matching ownership and child observations, exact schema/fields and six exact
integer sentinel zeros. Recomputed hashes cannot hide semantic contradictions.
Future OS acceptance must additionally receive the independently persisted outer
guard receipt; that native/live path remains disabled. A failed or delayed write
can leave a candidate on disk but cannot produce an accepted composed result.

## Validation and evidence budget

One new R088 allowance: 120 s cumulative fixture execution reservation; validator
address space 256 MiB, CPU 10 s, per-file 1 MiB. Twenty seconds are reserved for
setup/final evidence before release. Exclusive `attempt_01` creation consumes
admission; existing/open/failed/unknown attempts cannot be silently retried under
a new directory or request ID. This recorder deliberately has no retry switch.
All nonzero/unknown exits fail; signals, timeout, MemoryError and unknown return
codes are conservatively resource-or-unknown stops. Later reconciliation requires
review of preserved evidence within this same allowance.

The guard snapshots all executed sources and the external ledger, reconciliation,
contract and handoff/log inputs before release. The validator executes that copy,
checks the full inventory, and durably saves active-function progress before the
first function and after each function. The enclosing process bounds validator
startup/imports, fixture activity, partial/final persistence and exit. Its receipt
binds saved outputs and lifetime child RSS. Guard startup before its entry timer
and its own final receipt/ledger fsync/exit are excluded and explicitly charged
with a five-second unmeasured reserve, not represented as zero or certified as
independently bounded. This is not whole-recorder/live compliance certification.
No archived validator/recorder main is executed.

Completion: positive owner/core/protocol/R070 composition, H01–H04 negative cases,
all owned states, both failure orders, exact/overrun time boundaries, fake blocked
inner guard, durable progress/final evidence and source/input bindings. Stop at
unexplained failure/resource stop or a policy decision, and before native/live/
physical execution. Acceptance review must decide whether the declared outer
measurement boundary suffices before separately authorizing OS source work.
