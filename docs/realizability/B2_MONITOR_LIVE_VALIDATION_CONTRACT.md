# R081 monitor review and bounded live-validation contract

Reviewed 2026-09-21 on PC/WSL `daisy`, Python 3.12.13, after receipt of the
Mac's R077–R080 delivery `e40ed7b`. The review STARTED record was published
as `c1e1a71`. This completes the source/contract review selected by R076.
The [current handoff](../../SESSION_HANDOFF.md#next-task) owns the next task.

**R076 needs further repairs before live validation.** Eleven counterexamples
were reproduced using fake inputs, with all 61 R076 source bindings and the
R070/R073 original copies preserved. The physical entry still refuses launch.
The [audit evidence](evidence/r081/README.md) records precisely what ran.
No live adapter workload, cgroup write, signal, Windows executable, FEM/MPI/JIT,
mesh, solve, benchmark or physical attempt ran. The **180 s / 1536 MiB physical
limits**, unused q64/q96 allowance and failed B2 accuracy result are unchanged.

This contract freezes interfaces, future commands and test limits; it does
not implement the missing harness or certify the host. The next bounded work
is defined by the current handoff. R082 implemented fixture repairs; the
[R083 review](B2_MONITOR_R082_REVIEW.md) records remaining gaps and bounds the
later harness. The [R085 review](B2_MONITOR_R084_REVIEW.md) confirms residual
R084 integration gaps. [R088](evidence/r088/README.md) adds the composed fixture
repair with 14 passing groups. The [R096 acceptance review](B2_MONITOR_R088_REVIEW.md)
confirms saved bindings and refuses full acceptance until J01–J04 evidence and
outer-receipt obligations are repaired; the handoff owns the next task.
Native collection, live validation, Mac monitor decisions and
performance comparisons remain subsequent work.

## 1. Confirmed findings and required repairs

The identifiers correspond to the new, single
[audit attempt](evidence/r081/attempt_01/review.json). These are counterexamples
to readiness claims, not failures of a replacement implementation. Do not edit
R076's archived sources, passing cases, ledger or result to incorporate fixes.

| ID / reviewed surface | Observed behavior | Required new-version behavior |
|---|---|---|
| F01 `monitor_core.supervise` | An incomplete membership sample with a live root is followed by `completed` | Unknown coverage stops immediately; it cannot be repaired retrospectively by a later empty sample. |
| F02 normal completion | Empty membership/root exit sets `cleanup_confirmed=true` without calling cleanup | Every owned exit goes through finalization, including verified root reaping, empty workload and separate helper cleanup. Normal completion need not kill an already empty group. |
| F03 after provider work | A tree read taking 1.1 s permits completion using the old Windows sample | Check all deadlines and conservative host freshness after every provider/wait and before completion. A blocked provider needs the independent guard below. |
| F04 launch freshness | A bracket `[0,100]` at time 100 is accepted as age zero | Measure conservative age from acquisition start/request send, not receipt. Apply launch age <=30 s to both gates and a fresh runtime host baseline before release. |
| F05 tree timestamps | Sequence increases while tree end regresses from 10 to 9; completion passes | Require nonoverlapping, ordered brackets in the supervisor's clock domain; acquire each tree sample within its actual call bracket. Remove the unused `previous_end` argument or enforce it. |
| F06 cleanup schema | Numeric flags `1/0` pass; `confirmed=true` passes with an error and survivors | Exact Boolean flags, typed identity inventory, finite values, empty survivors/errors and confirmed reaping/empty group are jointly required. |
| F07 final reporting | NaN in cleanup escapes the last `finite_json` call | Convert invalid/unknown provider fields to null with a reason; retain the first stop and bounded secondary errors; final fallback serialization must itself be safe. |
| F08 core host input | A second reply without a pending request is accepted | One authoritative protocol state machine; exact expected sequence, run nonce, provider identity and outstanding request required at the core boundary too. |
| F09 host framing | Duplicate `status` keys and `status=ok` plus an API error are accepted | Reject duplicate JSON keys, nonfinite constants, extra frames, contradictory success/error fields, wrong types and oversize input before accepting values. |
| F10 copied R070 acceptance | Bound hashes plus Boolean success flags accept nonempty `primary_reasons`, helper failure and all-null scientific counts | Versioned monitor and child schemas; no reasons/errors; separate workload/helper cleanup; exact case counts and scientific evidence shape. Hash binding alone is provenance, not semantic validation. |
| F11 Linux membership helper | Empty membership cannot be represented because the root must be present | Separate launch-root verification from runtime enumeration; allow root reaped/empty group, retain descendants after root exit, and reject duplicate PIDs even with different start ticks. |

Additional **source-review** findings (not additional executed counterexamples):

- R076's recorder calculates remaining time from missing elapsed fields as
  zero, does not refuse an open STARTED or earlier timeout, and creates hashes,
  manifests and logs outside its child timer. It records all 14 known attempts,
  totaling **0.5964585269 s** and **22.6992 MiB** maximum child lifetime RSS;
  these are validator-subprocess measurements, not the full recorder's
  startup/setup/final-write cost or a monitored aggregate tree. Preserve the
  historical numbers with this qualification. Reconstructed commands are
  labelled as such. New records must be exclusive, durable and append-only.
- The core's report sink runs once after supervision. Its saved payload lacks
  the subsequently computed report/total times; there are no periodic durable
  parent checkpoints. A killed supervisor can lose its last state. Store
  bounded checkpoints during running/cleanup, and let the outer recorder
  publish final accounting separately to avoid a self-timing final-write loop.
- Policy constructor knobs can relax the fixed host floor/cadence. Select a
  named immutable policy at the integration boundary. Test-only overrides
  must be explicit fault cases and cannot become physical launch settings.
- The pure host parser has no incremental bounded transport/EOF queue, and
  pure Linux helpers neither enumerate nor kill cgroups. Sixteen fixture
  groups do not implement or validate those missing surfaces.

## 2. Frozen core and reporting semantics

Use a new schema/version and source manifest. `validate_launch` is pure;
`supervise(owned_run, ...)` assumes responsibility for all owned resources from
entry, even when validation fails. `owned_run` carries the root identity/reaper,
task-group identity, host session identity and an idempotent bounded finalizer.
No callback merely returning `confirmed=true` can override contradictory data.

Freeze this PC policy in the new integration copy:

| Quantity | Rule |
|---|---|
| Launch gates | Guest `MemAvailable >=4096 MiB`; Windows available physical bytes >= selected workload cap +1024 MiB; oldest possible acquisition <=30 s; recheck after setup immediately before release. |
| Runtime Windows | Floor 1024 MiB, equality passes; request every 0.5 s; receipt strictly before send+0.5 s and conservatively no more than 1 s after the preceding accepted request's send. |
| Runtime freshness | At every decision `now-last_accepted_send <=1 s`; no valid baseline means no child release. Host/guest clocks and memory are never added. |
| Tree sampling | Nominal 0.05 s absolute schedule, skip missed slots; bracket reads in the supervisor clock. Report actual acquisition/decision gaps. No general new physical tree-gap limit is selected. |
| RSS/deadline | Stop when sampled sum RSS > cap, or now >= deadline; preserve simultaneous triggers. RSS equality passes. |
| Cleanup | Immediate stop request on failure; at most 5 s verification, inside the attempt reservation. Always try cleanup after deadline; overrun is reported as failure, never extra compute allowance. |

Record workload and helper cleanup separately, each with identities, requested
actions, native errors, reaping/exit results, membership and survivors. A stopped
run remains stopped even if cleanup succeeds. A normal run becomes complete
only after both cleanups, zero root return code, accepted schema/source bindings
and complete case evidence. For sentinel integration, require zero scientific
events explicitly. A later physical schema must require the reviewed R021
counts/stage oracles; Boolean assertions cannot replace those checks.

After release, unknown scientific counts stay null with last-observed counts
labelled separately. Before release, zero launch/event counts are known. An
exclusive attempt STARTED event precedes setup. Record outer elapsed time
through child exit/checkpoint persistence, plus the enclosing recorder timing
from its independent guard. Unknown/open durations, failed cleanup, exhausted
budget or unexpected resource stop refuse continuation. No fresh directory or
request ID resets a suite budget. Preserve failures and source versions.

## 3. Actual PC capabilities and Linux containment

The [sandbox snapshot](evidence/r081/attempt_01/review.json) has PID 1 `codex`
and a read-only cgroup mount. A separately authorized
[host read-only inspection](evidence/r081/host_readonly_capabilities.json)
has PID 1 `systemd` and a read-write cgroup-v2 mount. These are different
execution contexts; sandbox limitations are not evidence that WSL lacks cgroups.

The [standard delegation-path check](evidence/r081/delegation_candidates.json)
found the user-owned, writable
`/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service`, with `memory pids`
controllers and cgroup membership/event/kill interfaces present. The user-manager
socket exists. This is a **candidate**, not proof that a new delegated unit,
process placement or group kill will work. The present shell is in `0::/`;
moving it directly into the user subtree is not authorized or assumed possible.
Use a future systemd user service to create the held launcher inside a new
delegated unit; never move/kill the editor shell or the existing user service.

Both inspected contexts use Python 3.12.13 with neither `os.pidfd_open` nor
`signal.pidfd_send_signal` exposed. No handle opened or signal was sent. Python
documents these as platform-dependent APIs; their absence does not prove a
kernel lacks the underlying facility. Do not replace the interpreter or add an
unreviewed raw-syscall binding. Use the selected whole-cgroup kill boundary and
owned direct-child reaping; individual pidfd signaling is unavailable in this
version. A new implementation needing it must stop for review.
[Python OS API](https://docs.python.org/3.12/library/os.html#os.pidfd_open)

The future delegated unit has a guard outside `control/` and `workload/` leaf
cgroups. The inner supervisor is in `control/`; the held launcher and all its
descendants start inside `workload/`. No workload code runs before both gates,
membership and the Windows helper are ready. Enumerate the complete subtree,
deduplicate PIDs, read `(pid,start_ticks,state,RSS)` and recheck membership.
Disappearance is an exit race only with a confirming recheck; unreadable live
members or unstable coverage stop. Disallow workload-created subgroups and
migration for these cooperative fixtures, while checking for unexpected ones.

The guard holds only task-specific directory identities/handles, verifies path
ownership, and owns cleanup if the supervisor stalls/exits. Stop through that
group's `cgroup.kill`; verify `populated=0`, empty membership and root reaping.
No raw PID list or process-name termination fallback. Root absence alone is
normal for a reaped root; remaining descendants are an abnormal stop. The kernel
specifies hierarchical kill and non-root placement; root's missing `cgroup.kill`
is expected, not a failed kernel feature test.
[Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)

## 4. Native Windows collector and ownership contract

`powershell.exe` and `dotnet.exe` paths exist; no executable was launched and
no SDK/compiler/API capability was inferred from PATH. The collector is still
missing. Freeze a small Windows-native launcher/collector with one source-bound
protocol, built locally in a later preparation task using an already available
toolchain. Missing toolchain refuses that task; installation or system changes
are separate decisions. Compiled artifacts stay local.

The collector uses `GlobalMemoryStatusEx`, initialized `dwLength`, checked API
success and integer `ullAvailPhys`/`ullTotalPhys` bytes. A failed call returns an
error with unknown values, never a cached success. This API measures physical
availability; commit/page-file fields cannot replace it.
[Microsoft memory API](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-globalmemorystatusex)

The native launcher creates a Job Object with kill-on-close and no breakaway,
creates its collector **suspended**, assigns it before resume, and retains
process/job handles. No Job handle is inherited by the collector. Use an explicit
stdio handle allowlist; failures during creation/assignment/resume trigger cleanup
before readiness. Do not silently opt out of a containing Job or nesting error.
The native launcher has an independent watchdog thread, bounded pipe queues and
a local monotonic absolute deadline; blocked input cannot prevent expiry.
[Windows process creation](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw),
[Job assignment](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject)

Wire messages are UTF-8 JSON lines, <=4096 bytes including newline, one pending
memory request and one bounded reply slot. Required fields: protocol/schema,
nonce, exact integer sequence, operation, native PID/creation identity, status,
available/total bytes or null, native error or null. Readiness additionally binds
the source/binary hashes and Job ownership. The Linux side retains send/receipt
brackets in its own monotonic domain; native clock values are diagnostic only.
Reject duplicates, malformed/multiple frames, EOF, queue overflow, unsolicited
or wrong-session replies. Never log arbitrary environment/credentials.

Freeze memory requests/heartbeats at 0.5 s. The native launcher terminates its
Job on pipe loss, explicit stop, local absolute deadline, or missing heartbeat
for 1 s; no new work is allowed while stopped. On normal completion or failure,
it waits on the collector's native handle and verifies zero active Job members,
then emits a bounded final cleanup record before exiting. Kill-on-close is a
backstop, not an empty-membership observation.
[Microsoft Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)

To cover the launcher itself, the future harness must perform a bounded native
exit-verification query on its recorded PID/creation identity after wrapper
exit. Open a matching process handle and test signaled termination, or establish
that that identity is gone; PID reuse cannot count as the same live process.
Access denied, missing final helper evidence or a timed-out probe is unknown,
not success. This query is part of the cleanup reservation. A Linux wrapper's
return code/EOF alone cannot certify native death. Native watchdog, handle
identity, query exit and fault behavior all require later live evidence.

## 5. Frozen future PC suite

These are design limits for benign validation, **not permission to execute now**.
They refine the PC part of the [Mac/PC plan](MAC_PC_PERFORMANCE_MEMORY_PLAN.md).
No limit below enlarges a physical allowance.

| Allowance | Frozen value / accounting |
|---|---|
| PC suite wall | 180 s cumulative, all attempts; 30 s shared setup, ten case reservations of 12 s, 30 s final validation/reporting. Reserve before starting; all phases and failed attempts consume the same total. |
| Case reservation | Up to 5 s active, 5 s cleanup, 2 s final evidence. A deliberate timeout case stops inner work at 0.25 s; the independent outer deadline still holds. |
| Linux workload | 512 MiB sampled aggregate RSS; allocation payload <=384 MiB. Native helper/supervisor overhead is separately measured. |
| Outer Linux backstop | 768 MiB `memory.max` on the whole dedicated suite unit, no swap, pids.max=32. This includes guard/control/workload charges and differs from the 512 MiB RSS metric; any real backstop event fails the suite. Verify delegation/controllers first. |
| Native overhead | Launcher/collector plus bounded verification query: sampled aggregate working set <=128 MiB, reported separately; native watchdog covers hangs. A guard breach is unexpected and stops the suite. No Job commit limit is called RSS. |
| Headroom | Same PC launch/runtime rules as section 2; selected workload cap=512 MiB gives Windows launch >=1536 MiB. Independently measure overhead; do not add guest and host capacity. |
| Cadence acceptance for this benign suite | Every non-startup tree decision gap <=0.1 s; host bracket rule <=1 s; any missed bound makes this suite unvalidated. This is a benign-test acceptance rule, not a new physical policy limit. |

The outer guard supervises independently of inner provider calls. Its own
absolute suite timer includes unit/helper startup and final reporting. A native
watchdog independently limits Windows lifetime. Neither watchdog can guarantee
bounded cleanup during a kernel/hardware hang; unconfirmed termination blocks
further work and owner release. Do not silently extend the budget for cleanup.

Use one serial pass through these exact ten cases. Held barriers last <=0.25 s
per stage within each 5 s active reservation. At least two consecutive accepted
samples are needed at each held state; otherwise fail, rather than lengthen it.

| Case / R074 row | Fixed stimulus | Expected result and retained evidence |
|---|---|---|
| L01 / live Linux | One 3 s sleep | Zero exit; cgroup membership and root identity; sample gaps, baseline RSS, helper startup and both cleanups. |
| L02 / live Linux | Parent/child/grandchild, each at baseline then total 16, 64, 128 MiB touched bytearray (replace, never stack buffers); touch every page | Barrier records with all three identities, per-process RSS, at most 384 MiB payload. Each plateau delta from that process baseline must be within payload +/- max(8 MiB, 10% payload); sum must stay <=512 MiB. Tolerance is calibration, not exact allocator accounting. |
| L03 / live Linux | Held three-level tree; descendant calls setsid; root exits after readiness | Abnormal-root stop; reparented descendants remain in the owned cgroup; kill/empty verification, no success based on root exit. |
| L04 / live Linux | Zero-output exit code 7 before first child checkpoint | Return-code failure, unknown post-release counts, complete cleanup and finite parent evidence. |
| L05 / live Linux | 3 s sleep with injected inner deadline 0.25 s | Expected wall stop, no grace computation, outer guard remains independently responsive. |
| L06 / live Linux | One child touches 32 MiB; test-only RSS cap 24 MiB | Expected RSS stop with identity-specific sample and cleanup. No host exhaustion. |
| W01 / live Windows | 3 s harmless Linux sleep with native helper active | API units/identities, request/receipt bounds, minimum availability, helper Job and native-launcher exit evidence. |
| W02 / live Windows | Test transport suppresses a reply for 0.6 s while real watchdogs remain active | Host timeout, immediate Linux stop and verified Job/launcher cleanup; record actual samples separately from injected behavior. |
| W03 / live Windows | Collector intentionally exits on request 2 | EOF/native-exit failure; launcher observes handle and clears Job; both domains cleaned. |
| I01 / integration | Inner supervisor deliberately stops heartbeats/blocks; child sleeps 3 s; guard fault deadline 0.25 s | Independent guard terminates control/workload, native watchdog/stop clears helper, durable last parent checkpoint, null unknown counts, zero physical attempt records. |

Low Windows readings, Boolean/malformed/oversize inputs, API errors, clock
regressions, kill/assignment errors and report failures are injected **fixtures
before** this suite. Never force Windows to run low on memory. Unexpected
errors, actual pressure/RSS/backstop stops, unknown membership, cleanup failure
or budget exhaustion stop the suite without retry. An expected injected stop
passes only with its exact reason, preserved partial evidence and both cleanups.

### Invocation contract

The following Bash commands are syntactically executable **future interface
requirements**. `monitor_validation.py`, its benign child, delegated-unit guard
and native helper do not yet exist. Do not paste these as a current workaround;
missing implementations/capability evidence must refuse, never invoke an
archived runner. The immutable machine-readable contract is
[`live_suite.json`](evidence/r081/live_suite.json).

```bash
# From a later, source-bound disposable implementation bundle on this PC.
test -f monitor_validation.py || exit 1
test -f source_manifest.json || exit 1
/tmp/navier-fenicsx/bin/python -B monitor_validation.py inspect --contract /home/rharris/git/navier-stokes-vortex-lab/docs/realizability/evidence/r081/live_suite.json --source-manifest source_manifest.json --output capabilities.json
/tmp/navier-fenicsx/bin/python -B monitor_validation.py fixtures --contract /home/rharris/git/navier-stokes-vortex-lab/docs/realizability/evidence/r081/live_suite.json --source-manifest source_manifest.json --output fixtures.json
# ONLY in a later live-authorized task after review of those outputs:
/tmp/navier-fenicsx/bin/python -B monitor_validation.py live --contract /home/rharris/git/navier-stokes-vortex-lab/docs/realizability/evidence/r081/live_suite.json --source-manifest source_manifest.json --capabilities capabilities.json --fixtures fixtures.json --suite-id pc-monitor-v1 --output pc-monitor-v1
```

`inspect` must have no OS mutations/helper startup. `fixtures` uses injected
operations only and its own separately recorded allowance. `live` must refuse
without a matching implementation-review binding, exact contract hash,
source/capability/fixture bindings, fresh launch gates and an exclusive ledger.
It starts the independent guard through the selected user-manager service;
only that service may create its delegated leaves/release the benign child.
No flags enabling FEM/physical code are accepted. Child commands are fixed
by case ID (no arbitrary command escape hatch) with launch-barrier descriptors
passed explicitly. A physical attempt file is neither created nor consulted.

## 6. Evidence mapping and next implementation

| R074 validation row | R081 coverage / remaining evidence |
|---|---|
| Core fake clock/providers | F01–F08 reproduced; new regression suite must reject each counterexample and cover exact boundaries, simultaneous stops, hung callbacks via fake guard, durable checkpoint failures and immutable policy selection. |
| Linux fixtures | F06/F11 and read-only metadata; add root-absent/empty, zombie/zero-RSS, PID reuse/duplicates, missing/permission/malformed/recheck races, nested membership and structured cleanup failures. |
| Host protocol fixtures | F08/F09; add bounded incremental framing/queues, terminal EOF/API errors, conservative send/receipt ages and independent native-lifecycle state transitions. |
| Live Linux | L01–L06/I01 specified, none run. Need actual delegated-unit placement/kill, sample/calibration results and guard fault evidence. |
| Live Windows | W01–W03/I01 specified, none run. Need native source/build hashes, handle/Job/API evidence, actual cadence and native helper/launcher cleanup. |
| Integration | F10 and hard-disabled entry checked; later strict schema/count checks, source bindings, partial checkpoints, refusal CLI/API, all-attempt persistence, untouched physical sentinel and combined cleanup. |

Historical R081 implementation recommendation, carried out by R082 and
reviewed by [R083](B2_MONITOR_R082_REVIEW.md); the current handoff supersedes
this assignment. R081 selected **GPT-5.6 Luna/medium** for a fixture-only bundle:
F01–F11, the recorder/checkpoint findings and strict copied-R070 acceptance.
Budget **120 s cumulative validator-process wall / 256 MiB address space**,
with outer startup/setup/final-write intervals measured separately and included
in a conservatively reserved **120 s total task-execution ceiling**. Reserve
cleanup/reporting before each invocation; keep exclusive attempt events and
refuse unknown/open attempts. This is a new repair allowance, not a reset of
R076 or a live-suite attempt. Preserve production/archive hashes; stop on
unexplained failure/resource stop, any required policy change, or before OS
adapter execution. Completion requires passing deterministic regressions,
manifests, ledger and the disabled CLI/API evidence. Do not implement/launch
native helpers or systemd units in that next step.

Then recommend **GPT-6 Astra/high** to review the repaired interfaces and scope
the missing native/Linux harness implementation; use Astra sooner for unresolved
ownership/timing/cleanup semantics. Availability and supported efforts were
checked against this session's catalog and official
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) and
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) pages. No
model switch, sub-agent, automation or remote Mac check occurred. The Mac
benchmark contract still needs its own monitor decisions; no computer has a
validated performance result from this work.
