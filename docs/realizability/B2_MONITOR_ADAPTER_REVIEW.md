# R074 host monitor adapter review

Recorded 2026-09-21 on PC/WSL `daisy`, Linux/x86_64, from base
`3fcc82f832737381bed90b7d6073644cd87c52e0`. This completes
[R074](../../REQUEST_LOG.md#r074--2026-09-21--continue-review-process-changes-and-specify-monitor-adapters).
Inputs are [R067's resource policy](B2_PHYSICAL_RUNNER_REVIEW.md#workload-and-host-decision),
the archived [R033 monitor](evidence/r033/source/toy_runner.py),
[R070 guard](evidence/r070/source/launch_guard.py), and
[R073 contract](evidence/r073/monitor_contract.md).

## Decision and scope

The adapters were specified here; R076 has since implemented their policy
core and fixture-facing adapters in a new disposable copy, without validating
them on the host. R070's physical entry remains disabled. R073's 16 passing
fake checks establish
the cases they tested, but do not establish an executable sampling schedule,
complete process coverage or confirmed cleanup. R076 used a new versioned copy
and preserved the R033/R070/R073 sources, reports and ledgers.
The original implementation and subsequent
[R081 review](B2_MONITOR_LIVE_VALIDATION_CONTRACT.md) are complete. R081 found
eleven further counterexamples and froze the future live-validation contract;
R082 implemented fixture repairs. The [R083 review](B2_MONITOR_R082_REVIEW.md)
finds remaining acceptance/provenance gaps and bounds the missing harness.
Follow the current [next task](../../SESSION_HANDOFF.md#next-task). Windows collection, live validation
and physical launch remain separate obligations specified below.

No numerical method, boundary condition, observer, solver, package pin or
scientific acceptance threshold changes. Physical limits remain **180 s and
1536 MiB**. R020 remains the last physical attempt; q64/q96 is unused, B2
accuracy remains failed and `campaign_ready=false`. No FEM/MPI import, JIT,
mesh, assembly, factorization, solve, host API or live adapter workload ran.

## Findings in the saved implementations

[audit.py](evidence/r074/audit.py) loads only standard-library archive modules
in memory and supplies fake clocks/readers/callbacks. Its
[first attempt](evidence/r074/audit_attempt_01.json) reproduces nine behaviors
and passes three preservation checks (12 checks total). These are confirmed
review findings, not a passing replacement-monitor suite.

| Finding | Consequence and required correction |
|---|---|
| R073 exits when `root_alive` is false even with count 2 and positive RSS | Require empty verified membership, root reaping and a successful return code; root exit alone cannot complete a run. |
| Termination callback raises, is called again, then escapes the exception handler | Separate the primary stop reason from cleanup errors; make cleanup idempotent and always preserve a partial report. Never equate requested termination with confirmed cleanup. |
| Launch validation occurs outside the cleanup boundary | A prelaunch validator must run before launch; a supervisor entered with a live child must own cleanup even if initialization fails. Distinguish these APIs explicitly. |
| NaN deadline and Boolean process count are accepted | Validate all configuration and sample types, including real Boolean liveness, finite clocks/deadlines and positive intervals/caps. Reject Boolean numeric impostors. |
| A tree timestamp 0.5 s ahead of the clock is accepted | Timestamp acquisitions before and after the actual read in the supervisor's clock domain; do not infer bounded read latency from a future sample. |
| A valid 5 s old launch sample immediately fails runtime gap checking | Separate the 30 s prelaunch window from the fresh runtime baseline; prime runtime collection before releasing the child. |
| Three readings occur with no clock advance | `poll_seconds` does not schedule anything. The test reader advances time; the real core needs explicit deadline-based waiting and independently serviced host collection. |
| R070 `finalize_child` accepts a complete checkpoint with return code 9 | A future integration must require return code zero, successful monitor status, verified cleanup and complete validated child evidence together. |

Source review adds two limitations not exercised by these counterexamples.
R033 rescans session/ancestry but stores no process start identity; raw PID
signaling can race reuse, and a descendant that creates a new session and is
reparented between scans can be missed. Its descendant test uses RSS > 0, which
is not a liveness test. R073 also compares synchronous host reads to a clock
read taken before the provider call; normal read latency can appear as a future
timestamp. An exact one-second polling schedule has no scheduling margin.

R073's validator starts its timer inside `main`, excludes imports/reporting,
and appends only successful runs. The first two saved failures have null RSS
and 0.1 s accounting entries without measured duration provenance. Thus
0.200314582 s is the **recorded ledger total**, not proof of full end-to-end
wall/RSS compliance across all four attempts. The two later RSS values are
Linux process-lifetime high-water readings, not aggregate tree measurements.
Preserve these records; do not reset their history or rerun R073 to replace it.

## Preserved resource policy

| Quantity | Required interpretation |
|---|---|
| Before PC workload release | WSL `MemAvailable` >= 4096 MiB and Windows available physical memory >= selected tree cap + 1024 MiB; each acquisition <= 30 s old. For the physical cap, Windows requires 2560 MiB. |
| Runtime workload memory | Sampled sum of resident bytes for the owned Linux workload processes, divided by 2^20. Stop on RSS > selected cap; equality does not exceed it. |
| Runtime Windows pressure | Stop below 1024 MiB or when a required reading fails/expires. Equality passes. Do not substitute swap, commit allowance or guest memory. |
| Runtime deadline | Stop at monotonic time >= the absolute deadline. Include launches, imports, compilation and reporting in the task's all-attempt allowance. |
| Cadence | Nominal Linux sampling 0.05 s; report actual acquisition and decision gaps. Windows acquisitions no more than 1 s apart. No new general tree-gap threshold is selected here. |

Host and guest readings overlap and must not be added. Runtime guest readings
may be recorded diagnostically; R067 specified a guest launch gate, not a new
runtime guest threshold. Memory sampling is an estimate and may miss short
peaks. It is not an OS-enforced resident-memory ceiling.

Linux documents `MemAvailable` as an estimate of capacity without swapping;
`stat` exposes process ancestry/session/start time/RSS, and its RSS accounting
can be approximate. Keep these semantics explicit. [Linux `/proc` documentation](https://docs.kernel.org/filesystems/proc.html)

## Core interface and scheduling

Use a schema-versioned policy and report. Separate `validate_launch(inputs,
policy)` from `supervise(owned_workload, providers, clock, wait, report_sink)`.
The first API cannot start a process. The second assumes cleanup responsibility
as soon as it receives ownership, including configuration/provider failures.

Represent each reading with `sequence`, acquisition start/end monotonic times,
provider/machine identity, units, status and any error. Tree records additionally
carry a list of process identities/states/RSS, membership completeness,
root status and root return code. Host records carry available/total physical
bytes and the request ID. Use finite JSON with null for unknown values.
No missing reading becomes a zero-memory or dead-process reading.

Prime both guest/host launch inputs and a fresh runtime host baseline before
releasing the workload. Recheck the launch gates at release, after setup.
Validate `start <= end <= now`, monotonic sequences, nonnegative finite bytes,
positive finite caps/intervals, exact integer counts and actual Boolean flags.
Report acquisition duration separately from intersample gap and decision delay.

Use absolute deadlines from one Linux monotonic clock. Schedule the next tree
sample at 50 ms increments with an injected wait function; do not busy spin or
manufacture catch-up readings. Check deadline/host freshness before and after
provider work and waits. The host transport must be nonblocking to this loop,
with bounded queues and at most one outstanding request. Provider exceptions,
EOF, malformed data and clock regressions cause a stop with preserved evidence.
Independent outer supervision must cover a stuck provider/supervisor during
later live validation; a same-thread timeout cannot prove that property.

As a transport scheduling choice, request host samples every 0.5 s to leave
margin under the unchanged 1 s maximum. Bound each response by the earlier of
request time + 0.5 s and the last accepted acquisition's freshness deadline.
This is a stricter implementation timeout, not permission to lengthen the 1 s
policy. A future change to these transport timings must be recorded/tested.
Do not compare independent Windows and Linux monotonic clock origins.

## Linux and WSL process membership and termination

For complete workload membership select an already delegated, task-specific
cgroup v2 subtree. Before executing workload code, place a held launcher in
that group and verify membership, controller path and access; descendants
inherit it. Keep the supervisor and host collector outside the workload group
and report their overhead separately. Use a serial, cooperative workload;
no privileged process or external service may migrate work out of the group.
Refuse physical readiness if membership/kill access is unavailable. This review
does not enable systemd, alter WSL configuration or grant cgroup permissions.

The session/ancestry scan remains useful diagnostic coverage for fixture tests;
it cannot silently replace the selected complete-membership prerequisite.
A delegated cgroup supplies membership and termination, while `/proc` RSS
remains the policy metric. `memory.current` includes different charges and
must not replace RSS under the same cap. The kernel documents cgroup process
membership, `cgroup.events` population, `cgroup.kill`, and memory-accounting
fields. [cgroup v2 documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html)

Parse `/proc/PID/stat` using its final closing parenthesis, preserving names
with spaces/parentheses; record PID, start time, PPID, session, process group,
state and resident pages. Convert with the local page size. Enumerate only
numeric process entries; count processes once, not each thread. A disappeared
PID is an exit race only after a membership recheck; missing/inaccessible live
members, inconsistent start identity or malformed values make coverage unknown.
Do not silently clamp corrupt negative RSS to zero. Distinguish zombie/reaped
state from an executing process, even when its RSS is zero.

Use pidfds for stable per-process handles and diagnostic signaling where
available, validating identity/membership around handle acquisition. Python
3.12 exposes `os.pidfd_open` and `signal.pidfd_send_signal`; test actual support
on the receiving host. [Python OS API](https://docs.python.org/3.12/library/os.html#os.pidfd_open),
[Python signal API](https://docs.python.org/3.12/library/signal.html#signal.pidfd_send_signal)
An isolated POSIX session is also useful, but is not the containment boundary;
`start_new_session=True` invokes `setsid` in the child.
[Python subprocess API](https://docs.python.org/3.12/library/subprocess.html#subprocess.Popen)

On resource/monitor failure, preserve the trigger and request immediate group
kill through the verified task cgroup; do not grant a graceful-compute interval
past the limit. Reap the direct child and verify empty membership/population.
Use at most 5 s for cleanup verification, retaining R033's bounded wait scale;
count it in total elapsed time and report it separately from workload time.
Reaching the deadline does not cancel cleanup. A kill error, uninterruptible
survivor, unreadable group or exhausted cleanup wait gives `cleanup_unknown`
or `cleanup_failed`, never success or owner release. Record identity-specific
errors and remaining members. Do not kill by broad name, user, distro or a
stale numeric PID list. A successful root exit with remaining descendants is
an abnormal stop requiring the same cleanup, not a successful run.

## Windows host-pressure adapter

Use native Windows `GlobalMemoryStatusEx`, with `MEMORYSTATUSEX.dwLength` set
correctly, API-success checked, and `ullAvailPhys`/`ullTotalPhys` serialized as
integer bytes. `ullAvailPhys` includes reusable standby/free/zero-list physical
memory. Page-file/virtual fields do not implement the physical-memory gate.
[Microsoft API](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-globalmemorystatusex),
[structure semantics](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/ns-sysinfoapi-memorystatusex)

Specify a persistent Windows helper with a bounded newline-delimited JSON
request/reply channel. It loads its native API binding once before readiness,
then answers one request with one new API call, echoed sequence/run nonce,
values and error status. Startup cost belongs to the task allowance and occurs
before releasing any Linux workload. Do not launch PowerShell/CIM anew on each
50 ms tree tick or block tree sampling on an interop call.

Bracket each request in Linux monotonic time: acquisition lies between send
and receipt. Use send time as the conservative freshness origin; require
receipt before the response deadline. To bound the unknown true acquisition
gap, require new receipt minus previous request-send <= 1 s. Reject duplicate,
out-of-order, mismatched, delayed or unsolicited replies; cap line length and
queue size. Store both bounds instead of relabeling receipt as measurement time.

The helper has separate native Windows lifetime/identity records. A Linux
`Popen` wrapper exiting does not certify Windows process death. A native
launcher must retain a process handle and establish an owned Windows Job
Object without breakaway, with kill-on-close and explicit bounded termination
verification; assignment failure refuses readiness. Retain helper exit status
and cleanup confirmation separately from the Linux workload. Job Objects can
manage/terminate grouped Windows processes, subject to assignment and nesting
constraints. [Microsoft Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
How the WSL/native helper and its launcher behave together must be tested on
this PC; a source review cannot certify that integration. Build native helpers
locally when needed; never transfer compiled artifacts between hosts.

No Windows workload-tree adapter is selected: the scientific child runs in
Linux/WSL. Windows collection only supplies host pressure. No Mac adapter or
Mac available-memory definition is validated by this decision.

## Reports, attempts and disabled-launch integration

Before validation, an outer recorder creates an exclusive attempt record and
records source/policy hashes, command, start time, remaining cumulative budget
and measurement method. It records every completion, exception, timeout and
interruption, including failed imports and final reporting. Keep each attempt's
result and output; append outcomes rather than overwrite earlier files.
An interrupted STARTED attempt with unknown elapsed/cleanup blocks an automatic
retry pending reconciliation. A budget/cleanup stop never authorizes a retry.
Keep wall time, sampled tree RSS, process-lifetime high-water and address-space
limits distinct; they are not interchangeable measurements.

Monitor result fields must include status, primary and secondary reasons,
counts of accepted samples, last valid readings, maximum gaps/latencies,
sampled peak RSS with per-process contributions, return code, membership
coverage, cleanup requested/confirmed/errors/survivors and elapsed setup/run/
cleanup/report times. Write checkpoints atomically and preserve secondary
write failures. After launch, unknown scientific event counts remain null;
last durable child counts are explicitly last-observed, not final.

In a future copied R070 integration, acceptance requires all of: no monitor
failure, child return code zero, verified empty workload/helper cleanup,
complete bound child evidence and scientific checks. Physical enablement must
still be false in CLI and reusable entry points during the next task. Synthetic
sentinels use a separate test entry and cannot consume the real q64/q96 record.
Do not simply pass `enabled=True` to the saved test-oriented callback API and
call it a reviewed physical path. The real once-only sequence, cache/environment
gate and solver-event checks still require a later launch review.

## Required validation before physical readiness

| Layer | Required cases and evidence |
|---|---|
| Core with fake clock/providers | All nine counterexamples above; exact cap/deadline/headroom boundaries; actual wait cadence; delayed and hung provider; stale/future/repeated/NaN/infinite/Boolean data; clock regression; simultaneous stop reasons; exceptions during initialization, cleanup and reporting. |
| Linux fixtures | `stat` names/units/start identity; fork/reparent/setsid membership; PID reuse; permission/malformed/disappearing entries; zero-RSS live member; zombie; root exit with descendants; missing cgroup delegation/kill support; cleanup success/failure/unknown. |
| Host protocol fixtures | Two launch gates independently; units/API failure; one outstanding request; request/receipt bounds; duplicate/mismatched nonce or sequence; EOF, huge line, full queue, transport timeout; Windows-helper cleanup unconfirmed. |
| Live Linux, later | Harmless sleep and bounded allocation, parent/child/grandchild with held readiness barriers, root exit, reparent/setsid, zero-output early exit and failure injection. Prove cgroup containment and cleanup of owned identities, independent outer watchdog, actual sample gaps and per-process RSS. |
| Live Windows, later | Native API identity/units, collector startup/latency, runtime cadence during harmless Linux work, timeout/EOF/native helper death and Job Object cleanup. Inject low-memory values for stop tests; never exhaust host RAM to test the guard. |
| Integration, later | Default-deny CLI/API, test sentinel separate from physical attempt record, durable partial counts under interruption, return-code/report disagreement, source bindings, complete helper/workload cleanup and preserved all-attempt budgets. |

Fake checks cannot pass the live rows. No live workload is authorized by this
review. Before live validation, freeze its benign commands and memory sizes,
select an independently enforced cumulative cap, refresh capacity and verify
the host-specific containment/monitor capabilities. If those capabilities are
absent, document the exact refusal; do not relax the contract or install/change
system configuration implicitly. Later Astra review must decide readiness
from those results before any FEM work.

## R076 implementation result

The fixture-only implementation is in
[`evidence/r076/`](evidence/r076/README.md). It provides the versioned core,
pure `/proc` stat and membership helpers, a Windows JSON-line protocol
validator, finite partial reports, explicit waits, cleanup classification,
an all-outcome attempt recorder and strict completion gates in a new R070
copy. Completion verifies the source manifest and binds the child report digest
to the monitor report. The original R070/R073 sources and manifests are preserved. All attempts
are recorded; the final run passed 16 fixture and continuity groups in Python
3.12.13 within the 120 s / 256 MiB validation allowance. Two initial failures
were retained and corrected: a duplicate fake tree sequence in the deadline
fixture and an R070 disabled-entry branch that reached its launch code.

This is fixture evidence only. It does not certify live `/proc` or cgroup
membership, process identity races, signal behavior, cgroup cleanup, Windows
`GlobalMemoryStatusEx`, host transport, Job Object behavior or independent
watchdogs. The native Windows collector and the actual host capabilities
remain unimplemented/unverified; R070 physical execution remains disabled.
The physical 180 s / 1536 MiB policy is unchanged.

## Implementation contract (historical)

R076 used **GPT-5.6 Luna/medium** on this PC to implement the versioned core,
Linux membership/RSS/termination helpers and host request/reply validation
facade in a new disposable source bundle. OS reads, signals and transport
operations are injectable; R076 ran fixture/fake checks only, with no real
process signaling, child workload, cgroup writes or Windows helper startup.
The bundle includes finite reports, a source manifest, an all-attempt recorder
and default-deny integration checks on a new R070 copy. The prescribed
120 s / 256 MiB validation allowance included the validator subprocess's
startup/import/reporting, and failed attempts were preserved. Live adapters,
FEM and physical execution remain unvalidated.

That **GPT-6 Astra/high** review completed as R081; its
[contract](B2_MONITOR_LIVE_VALIDATION_CONTRACT.md) supersedes this historical
next-task recommendation. It qualifies R076's recorded time/RSS as validator
subprocess measurements, identifies remaining fixture/recorder gaps, and maps
future native/Linux cases without running them. Follow the single handoff task.
Use Astra if containment, timing, cleanup or
measurement semantics need a new decision; do not turn uncertain behavior into
permissive fallbacks. Official OpenAI model pages were rechecked on
2026-09-21; this is a recommendation only, not a model switch.
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna),
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)
