# R101 manager capability decision

Reviewed 2026-09-21 on PC/WSL `daisy`; synchronized base `c2d700d`,
STARTED `4b6c4db`. **Unsupported under the unchanged R099 contract;
OS-source admission remains refused.** The documented interfaces supply useful
pieces, but do not establish the selected existing user manager as the bounded,
durable reservation-to-terminal authority required by R099. This is a scoped
capability verdict, not a proof that every possible OS design is impossible.

Inputs: [R099 contract](B2_MONITOR_TRUSTED_ADAPTER_CONTRACT.md),
[R098 acceptance](B2_MONITOR_R097_REVIEW.md),
[R097 interface](evidence/r097/source/certificate.py),
[R081 suite](B2_MONITOR_LIVE_VALIDATION_CONTRACT.md#5-frozen-future-pc-suite),
[R083 boundary](B2_MONITOR_R082_REVIEW.md#missing-harness-implementation-boundary).
These inputs and all historical evidence remain unchanged. The
[handoff](../../SESSION_HANDOFF.md#next-task) owns the next policy review.

## Evidence scope

Official upstream systemd manuals and Linux kernel/man-pages documentation
were opened through web retrieval. Freedesktop rendered pages returned 403;
the project's own raw manual sources supplied the systemd evidence instead.
The [source index](evidence/r101/sources.json) records URLs, sections and concise
observations. Upstream `main` and online kernel documentation are moving
references; no installed version, running configuration, permissions, storage
mode or API availability was inspected. No downloaded-source byte snapshot or
upstream commit pin is claimed. This is documentation evidence only.

Below, API behavior comes from the linked primary sources. Sufficiency and
failure judgments are this review's inferences against R099. A timeout request,
a successful job, an authentic process identity and a durable application
transaction are different facts.

## Concrete API and obligation map

| Obligation | Documented candidate | Evidence and decision |
|---|---|---|
| E0 exclusive reservation before any task setup | `StartTransientUnit(name, mode, properties, aux)`; job signals | Creates/starts a uniquely named transient unit; it is not a documented application ledger transaction. No binding of prior-attempt closure, source/nonce, initial timestamp, durable reservation and enforcement-before-entry is supplied. **Unsupported.** [Manager API](https://raw.githubusercontent.com/systemd/systemd/main/man/org.freedesktop.systemd1.xml) |
| E0 queue/entry bound | `JobTimeoutSec`, `JobRunningTimeoutSec` | Timing begins at queue insertion or job execution. Expiry cancels the job without itself changing unit state. It neither covers earlier request processing nor provides R099's reservation transaction. **Insufficient.** [Unit manual](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.unit.xml) |
| E1 O lifetime enforcement | `TimeoutStartSec`, `RuntimeMaxSec`, `TimeoutStopSec` | Startup, active runtime and stop are separate phases; runtime limiting is not an absolute E0–E8 transaction limit. Notify extensions and extra runtime randomization would need exclusion. No concrete composition here proves prior arming plus all finalization inside D. **Partial primitives only.** [Service manual](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.service.xml) |
| E1 absolute scheduling | Monotonic timer units, `AccuracySec`, timer-slack settings | Timer activation schedules another unit. Default coalescing is one minute; reducing it does not document a hard upper dispatch/completion latency or protect a blocked manager from itself. A new stop service adds charged work. **Does not close E0/E8.** [Timer manual](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.timer.xml) |
| E1 real unit identity | `InvocationID` / `INVOCATION_ID` | Identifies a unit runtime cycle, shared by its processes. It does not individually identify O and R, bind their executable bytes or freeze the application Admission. **Useful identity component only.** [Execution manual](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.exec.xml) |
| E1 held process bootstrap | `clone3(CLONE_INTO_CGROUP | CLONE_PIDFD)` into a frozen cgroup | Linux supports creating a child directly in its destination, including a frozen cgroup, and obtaining a pidfd. This is a possible bootstrap primitive, not evidence that `StartTransientUnit` exposes R099's complete held-identity transaction. **Bootstrap authority remains unsupported.** [clone](https://man7.org/linux/man-pages/man2/clone.2.html) |
| E6/E7 independent exit observation | `ExecMainExitTimestampMonotonic`, `ExecMainCode`, `ExecMainStatus`; pidfd and direct reaper | Manager properties describe the main process as known; child pidfds support waiting. Neither proves native cleanup, all descendants reaped, receipt durability or complete stop history. **Partial witness inputs.** [Manager API](https://raw.githubusercontent.com/systemd/systemd/main/man/org.freedesktop.systemd1.xml), [pidfd](https://man7.org/linux/man-pages/man2/pidfd_open.2.html) |
| E7 receipt persistence | File `fsync`, plus directory `fsync` where needed | Successful synchronization supplies a persistence primitive; it can block or fail and has no deadline parameter. M is not documented to authenticate the exact receipt's sync completion before O exits. **Required witness fact absent.** [fsync](https://man7.org/linux/man-pages/man2/fsync.2.html) |
| E8 final query and retention | `GetUnit`, property reads, retained unit references, journal | Unit state can be garbage-collected, losing execution results except those logged. References keep state available, not durably immutable. A query response is not a source-bound witness/ledger commit. **Unsupported terminal transaction.** [Unit manual](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.unit.xml) |
| E8 synchronization acknowledgement | `journalctl --sync`; `sd_notify_barrier` | Journal sync waits for persistence of earlier messages; it does not document a finite completion bound or an application transaction. Notification barriers acknowledge processing, not disk durability. Invoking either adds task work. **No terminal certificate.** [journalctl](https://raw.githubusercontent.com/systemd/systemd/main/man/journalctl.xml), [notification API](https://raw.githubusercontent.com/systemd/systemd/main/man/sd_notify.xml) |
| E1–E8 resource scope | `MemoryMax`, `MemorySwapMax`, `TasksMax`, `Delegate`, `DelegateSubgroup` | These configure the unit hierarchy; subgroup placement can keep the delegated root empty. They do not establish per-request attribution/enforcement for the external manager, bus or journal. **Outside-unit task costs unresolved.** [Resource control](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.resource-control.xml) |

The Manager API's start-job acknowledgement must be distinguished from job
completion. Subscribing before submission avoids missing the relevant job
result, but does not turn the stream into a durable application ledger.
`SetUnitProperties` can modify settings; readback alone does not establish the
immutable effective admission required here.
[Manager API](https://raw.githubusercontent.com/systemd/systemd/main/man/org.freedesktop.systemd1.xml)

## Identity, clock and commit consequences

A future bootstrap would need two immutable stages: a reservation bound to
boot/manager/source/nonce before creation, then an Admission binding held O/R,
cgroup directory identities, direct reapers and native creation/Job identities
before workload release. No stage may retroactively exclude its bootstrap time.
Linux held-child mechanisms make individual identity acquisition plausible;
they do not solve who authoritatively reserves and persists both stages.
Freezing a unit after starting it cannot prove that no earlier child code ran.
An inherited environment token is not an authenticated observation.

With a pidfd, exit readiness and direct-child waiting remain distinct. Likewise,
`cgroup.events` population describes live membership; zombies are absent from
`cgroup.procs`. Neither an empty group nor wrapper exit substitutes for the
existing Linux reaping and independent Windows launcher/Job/query obligations.
No new Windows design is selected here.
[pidfd](https://man7.org/linux/man-pages/man2/pidfd_open.2.html),
[kernel cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)

R099 requires one Linux monotonic domain and boot origin. `CLOCK_MONOTONIC`
excludes suspend; `CLOCK_BOOTTIME` includes it. A timer's clock, process timestamps
and reservation must agree. Suspend/clock uncertainty therefore remains an
admission refusal until handled by a reviewed policy; silently switching clock
domains is not a repair. This review does not change the clock definition.
[Linux clocks](https://man7.org/linux/man-pages/man2/clock_gettime.2.html)

Journal monotonic timestamps identify receipt time, paired with boot ID; they
are not disk-commit timestamps. Default periodic sync can be five minutes, and
storage/retention settings matter. An earlier timestamp in a subsequently
synced record does not prove that synchronization finished by D.
[Journal fields](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.journal-fields.xml),
[journal configuration](https://raw.githubusercontent.com/systemd/systemd/main/man/journald.conf.xml)

The decisive E8 gap survives even if storage is persistent and all API versions
are available: a caller may bracket a successful sync and reject a late result,
but who bounds and durably authenticates that caller's final observation after
O exits? Assigning it to a hook, finalizer, journal client or new service creates
task work whose startup, resources and terminal observation must be covered.
The reviewed manager interfaces do not document R099's combined operation.
This is an inference about the specified composition, not an assertion that
filesystem durability is impossible or that every failed attempt must persist
a failure report. Absence of terminal evidence already blocks continuation.

## Accounting and failure disposition

No new budget is allocated. R081/R083 remain 180 s total: 30 setup + ten 12 s
cases + 30 final reporting; each case has 5 active + 5 cleanup + 2 evidence.
Task-created Linux work retains 768 MiB whole-unit/no-swap/32 PIDs; sampled
workload RSS stays 512 MiB, native aggregate working set <=128 MiB. These metrics
are not interchangeable. Hierarchical cgroup controls cover members, not
arbitrary remote work performed on their behalf.
[Kernel cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)

E0 request processing, E1 unit/timer/delegation/identity operations and E8
queries, validation, synchronization and retention remain charged task work.
The pre-existing unrelated manager lifetime and passive E9 storage alone are
excluded. Moving the entire shared manager/editor environment under a cap would
change scope and affect unrelated work; no such change is proposed. A fixed
unmeasured reserve cannot establish either time or resource compliance.

| Failure | Required disposition under unchanged policy |
|---|---|
| Entry/arming request blocks or fails | No release; no fabricated zero setup charge. Any incomplete reservation remains unavailable. |
| R/O blocks or dies | Independent cleanup obligations remain; unknown exit, native query or persistence yields partial/unconfirmed evidence. |
| M blocks, dies or restarts; bus history is lost | No demonstrated independent E0/E8 authority remains. Latch unknown and stop; a manager timer is not proof of recovery from manager failure. |
| Sync/write/query denied, blocked, failed or late | Do not certify success or clip elapsed time. Retain the last durable state; absent final state blocks another attempt. |
| Unit unload, reused identity, missing source or unknown clock | Refuse witness acquisition; reconstructing a matching JSON object does not recover authority. |
| Kernel/hardware hang or unconfirmed enforcement | Report uncertainty, preserve the reservation and require reconciliation. No universal recovery guarantee is claimed. |

No live attempt exists in R101. Repository delivery and retained PC ownership
do not release an unresolved experiment. R097's 5.34962656602147/120 s historical
charge and its startup/final-write/exit exclusions remain unchanged. Whole-recorder
and live certification remain false; physical 180 s / 1536 MiB limits, unused
q64/q96 allowance and failed B2 accuracy remain unchanged.

## Exact policy choice for user review

The capability decision is complete. Repeating generic contract drafting or
implementing an adapter cannot by itself settle these missing semantics.
Choose one policy before further OS-source work:

| Choice | Exact effect |
|---|---|
| **A — Retain current requirements (recommended pending user decision)** | Keep whole E0–E8 accounting, enforcement and durable authority as requirements. Record the current user-manager route as unsupported and keep OS-source/live admission closed. Reopening requires a specifically evidenced alternative, not another assumed helper. |
| **B — Narrow the assurance claim explicitly** | Authorize a documentation-only revision distinguishing enforced task-process limits from externally observed setup/finalization. Preserve the 180 s success ceiling and charge observed E0–E8 elapsed time, but explicitly relinquish independent whole-transaction enforcement and bounded durable final commit; separately disclose unbounded/unattributed infrastructure operations. Unknown/late evidence still refuses success, reservations stay blocked and no whole-recorder certificate is claimed. This changes R099 policy and requires review of R081/R083 compatibility; it does not authorize source or execution. |
| **C — Change the trusted boundary** | Authorize one documentation-only feasibility review of a specifically named alternative authority with entry enforcement, held identity, durable bounded terminal transaction and resource scope. Keep existing caps and current refusal; approve no assumed capability, installation or helper launch. The user must name or authorize selection of the candidate. |

No policy change is selected in R101. A is the recommendation to preserve the
existing requirements while the user decides; B is a deliberate reduction in
the strength of the claim, not an implementation detail; C is not evidence that
an alternative exists. One next task is **user policy selection A/B/C and recording
its exact scope**, using GPT-6 Astra/high. A bare Continue may resume that policy
review but cannot imply B/C consent, source admission or another experiment.

Completion evidence is [R101 documentation validation](evidence/r101/README.md).
No fixture/import/replay, native/adapter code, live inspection/mutation,
build/helper/workload, FEM, rendering, encoding or physical execution occurred.
Retain Astra/high for unsettled authority/accounting semantics; it is available
in the session catalog and high effort is supported by the opened official
[OpenAI model page](https://developers.openai.com/api/docs/models/gpt-6-astra).
OpenAI Docs was used only for that recommendation. Reconsider a smaller model
when the selected next task is mechanical. No model switch, delegation or automation.
