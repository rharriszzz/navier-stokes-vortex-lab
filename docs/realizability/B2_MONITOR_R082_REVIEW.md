# R083 monitor repair review and harness boundary

Reviewed 2026-09-21 on PC/WSL `daisy`, Python 3.12.13, from clean upstream
`c5ffc2c8041144d8b0362f44bbcfbb7ae8daaa0d`; STARTED published as `13b38ae`.
The [current handoff](../../SESSION_HANDOFF.md#next-task) is the single next task.

**R082 is not ready to become the live harness.** Its repairs address the
original examples, but this review found omitted regressions, false completion,
host freshness and provenance gaps. The [one audit](evidence/r083/README.md)
confirms seven finding groups. This is a review result, not a replacement
implementation or live-validation pass. No numerical method or policy changes.
Physical execution remains disabled, the physical **180 s / 1536 MiB** limits
are preserved, q64/q96 remains unused, and B2 accuracy remains failed.

## R081 finding-to-source and evidence map

Paths below are relative to [R082 source](evidence/r082/source/). Historical
17-group results are in [attempt 3](evidence/r082/fixture_results_attempt_03.json).
R083 calls only the two omitted test functions and its own small counterexamples;
it never runs an archived validator main or recorder.

| R081 item | R082 source / existing evidence | R083 disposition |
|---|---|---|
| F01 incomplete membership | `monitor_core._validate_tree` immediately rejects incomplete coverage; `validate.test_incomplete_membership_and_provider_freshness` | Function omitted from `main`; direct R083 call passes. Original example repaired, historical coverage overstated. G01. |
| F02 normal-exit finalization | `supervise` enters cleanup on `completed_pending_cleanup`; scheduler fixture records callback/checkpoint | Callback runs, but all-path independent ownership is still an adapter obligation; elapsed cleanup is not enforced. G02 and ownership boundary below. |
| F03 post-provider freshness | `supervise` checks after tree calls; same omitted test as F01 | Direct R083 call passes the 1.1 s tree example. Post-host-poll refresh still hides an expired previous baseline. G03. |
| F04 conservative launch age | `validate_launch` uses guest/host acquisition start; `test_launch_gate` covers stale guest and headroom boundaries | Source repair present. Runtime baseline before actual release remains an unimplemented harness duty; no release was tested. |
| F05 tree brackets | `_validate_tree(previous_end)` and actual call-start check; `test_tree_brackets_and_host_identity` | Second omitted function passes when directly called in R083. Scheduling after a missed slot still uses `captured_now + interval`, losing the absolute 50 ms phase. |
| F06 cleanup types/contradictions | `_validate_cleanup`, `linux_adapter.classify_cleanup`; cleanup-error/classification fixtures | Type/error checks improved; no root-reaped, populated, native-Job or launcher-exit fields bind the cleanup claim to its owner. A single callback cannot itself guarantee both domains are attempted after an exception. |
| F07 finite reporting | `_safe_report`, `durable_checkpoint`; cleanup-error/partial-report fixtures | Tested NaN sanitation and bounded secondary messages are present. Normal report sink receives the pre-final-timing object; outer final evidence and checkpoints during blocked cleanup are still required. |
| F08 core host sequence | `supervise` checks pending/sequence/nonce/stable provider identity; second omitted function | Direct R083 call passes original unsolicited/nonce examples. State is duplicated with `HostProtocol`, whose stricter previous-send test is absent from core. G03/G06. |
| F09 host framing | `HostProtocol.reply` rejects duplicate keys, nonfinite constants, extra fields/frames and contradictory API results; registered parser fixtures | Original examples repaired. No incremental transport/EOF handling, fixed-bound enforcement at integration, or terminal-error latch. G06. |
| F10 R070 acceptance | `r070_copy/launch_guard.finalize_child`, `_exact_counts`, `_cleanup_ok`; registered completion-binding fixture | Nested zero counts are checked but top-level fields populate final counts; contradictory watch cleanup fields and floating schemas pass. G04/G05. |
| F11 absent root / duplicate PID | `make_membership_reading` permits absent root; `verify_launch_root` separately checks launch; `_validate_tree` rejects duplicate PID | Empty/reparented inventories representable; runtime enumeration, stable ownership and reaping remain unimplemented. No live membership claim. |
| Recorder/history | `run_fixtures.py`, `attempt_accounting.py`; registered pure ledger test | Exclusive lock/start files and refusal improvements exist; missing historical source bodies/outer bindings and unmeasured intervals limit the claims. G07. |
| Periodic checkpoints | `durable_checkpoint` and `checkpoint_sink` in loop/post-cleanup; scheduler fixture | Atomic file/directory sync exists. Blocking callback/sink and cleanup-before-return need independently retained state. |
| Fixed policy | `Policy.validate`; registered invalid-policy fixture | Cadence/floor/cleanup values cannot be relaxed there. Integration must bind workload cap/deadline and parser limits to named contract/case, never arbitrary caller values. |
| Missing OS adapters | Pure Linux decoding and complete-line host parser only | Native launcher/collector, incremental pipes, delegated unit, guard and ten live cases remain absent. Boundary below specifies their obligations. |

## Confirmed new gaps

These findings are reproducible in [review.json](evidence/r083/review.json).
Fix them in a new version; preserve the R082 archive and all failed attempts.

| ID | Concrete result | Required acceptance |
|---|---|---|
| G01 | 19 test functions exist, only 17 are registered. The two omitted functions test F01/F03/F05/F08 and duplicate PIDs. | Collect every intended test exactly once; assert registration completeness before running. Record function names and actual attempt ID. |
| G02 | Fake normal completion followed by 6 s cleanup returns `completed`, no primary reason, although cleanup limit is 5 s and total deadline is 1 s. | Preserve cleanup evidence, but overrun must prevent success. Use absolute active/cleanup/final deadlines within one reservation; do not turn active-deadline expiry into permission for more compute. Test exact 5 s and >5 s separately. |
| G03 | First host send/receipt 0/0.4; second send/receipt 0.8/1.1. Core completes although receipt is 1.1 s after the previous accepted send. | Before replacing the old baseline, compare current receipt against its send; enforce the same rule at core and transport. Check after every potentially blocking boundary, including checkpoint and poll. |
| G04 | Valid nested zero counts produce `complete` with all-null final counts. Adding top-level counts of 7 still completes and publishes 7. | One canonical nested count schema; accepted sentinel output must contain those exact integer zeros. Reject legacy duplicate count keys rather than silently choosing an interpretation. Post-release unknown counts remain null only on partial results. |
| G05 | With correct hashes and clean nested cleanup, monitor `cleanup_errors=[...]`, `survivors=[[99,1]]`, and `schema=3.0` are accepted. | Exact integer versions and complete versioned schema validation; no contradictory error/survivor channels. Reject unsupported/extra fields. Mutated-child tests must recompute the report hash to isolate semantic rejection. |
| G06 | Parser rejects a malformed reply but accepts a good reply for the same pending request afterward. | Terminal failure latch shared with core/transport: no more requests/replies after malformed/API/EOF/timeout/overflow/identity failure. A parser exception alone relies on every caller preserving this rule. |
| G07 | Final fixture file says attempt 1 although its filename/ledger say 3; result “maximum” is 24,166,400 B, while ledger maximum is 24,367,104 B. Historical outer sources are not bound. | Reconcile metadata additively; preserve old bytes. New attempts bind all executable sources before execution and archive changed source bodies, with correct derived summaries. |

Source-only findings also remain: the tree schedule must advance integer slots
from its original epoch when skipping missed slots; cleanup must explicitly
attempt workload and helper finalization independently; and strict acceptance
must tie cleanup observations to recorded owned identities. These are existing
R074/R081 requirements, not new physical thresholds. Frozen L04 expects
`root_returncode_failure`, while core currently emits a combined abnormal-exit
reason. A future adapter must preserve the raw reason and apply an explicit,
tested case-level classification; it must not rename every abnormal exit L04.

## Historical provenance decision

Keep R082's three attempts and its reconciliation unchanged. The saved
attempt-2 traceback is consistent with the missing cleanup-status fixture
described by the author; its 15.076110466994578 s charge stays included. This
review does not retroactively authorize a retry or certify that historical
execution. Hash lists identify earlier source versions but do not preserve
their bodies. The final checked-out source matches attempt 3; at least one
source differs for attempts 1 and 2. Neither changing outer-recorder nor
imported `attempt_accounting.py` is bound in those per-attempt source maps.
Only their final hashes are preserved.

The **recorded** total is 45.24748005397851 s, including three 15 s reserves;
the ledger's maximum child lifetime RSS is 24,367,104 B. These are useful
records, not proof of whole-recorder compliance. The final recorder starts
timing inside `main` after interpreter startup/imports, computes its child
timeout before source hashing and durable setup, samples elapsed before final
hashing/persistence, and does not enforce/measure the final 15 s reserve.
Its `capture_output` allocation is unbounded before later truncation, and only
the validator has address-space/CPU limits. No independent guard bounds a
stalled recorder. Passing pure `prior_elapsed` fixtures does not test these
failure paths. Missing `resource_stop` is treated as no stop, and return-code
equality permits Boolean zero; new schemas must require exact typed fields.

The obsolete copied `source/run_attempt.py` remains a runnable second recorder
with old semantics. It must be inert in the next bundle; entry-point inventory
checks must prevent bypassing the new ledger. Do not execute it in the archive.

R082 README's artifact row still says 19 final groups, despite its prose and
the request-log correction saying 17. This review supplies the additive
correction, along with the attempt-ID and summary-RSS qualifications above.
Do not rewrite that evidence to make it appear originally correct.

Before any later live work, require a **new** fixture/provenance package:
source bodies plus hashes for launcher, recorder, accounting, parser, test
registry and invoked child; exclusive STARTED and terminal events bound to
the same attempt; checked before/after identities; complete case/report hashes;
and measured outer intervals through child final persistence. A fixed final
reservation must actually be enforced and its overrun must block continuation.
Unknown/open durations or resource stops remain terminal. Never manufacture
old hashes, infer missing time as zero, or rerun historical experiments to
replace their evidence. R082 cannot serve as a live implementation-review
binding. Documentation repair is made here; implementation repair is still due.

## Missing harness implementation boundary

This section specifies a later implementation, not permission to build/start
native helpers or execute the [R081 frozen suite](evidence/r081/live_suite.json).
Use its exact case IDs, fixed child commands, capacities and time reservations.
No arbitrary-command option, FEM import, archived runner fallback, or physical
attempt file is part of this harness. Keep sources in a new disposable bundle;
native binaries and caches remain machine-local.

| Component | Owned responsibility / narrow interface |
|---|---|
| `monitor_validation.py` | `inspect`, `fixtures`, `live` facade from R081. Bind exact contract/source/review/capability/fixture identities; `live` refuses while any binding or implementation is missing. `inspect` only reads metadata. |
| `owned_run.py` | Immutable suite/case/attempt ID and nonce; Linux unit invocation/cgroup directory identities, root PID/start ticks and owning reaper; native launcher/collector creation identities and Job owner. Advance `RESERVED → OWNED_HELD → READY → RUNNING → STOPPING → FINALIZED`; failures latch and never return to READY. |
| `linux_guard.py` | Independent timer and guard process; guard leaf is a sibling of `control/` and `workload/`. Own direct child launchers/reaping, release barrier, group cleanup and durable outer state. Never await an inner provider to service its deadline. |
| `linux_live.py` | Task-specific directory-handle-relative membership/stat reads and confirmed group cleanup. Only the guard's created unit is writable; no editor-shell migration, process-name kill or raw-PID fallback. |
| `host_transport.py` | Bounded incremental UTF-8 framing, one pending request and reply slot, 4096-byte line bound, terminal protocol latch. Nonblocking operations return facts to the state machine; no synchronous pipe read in core. |
| Native source module | A small C# launcher/collector via explicit Win32 bindings is the bounded implementation candidate. Pin source/toolchain/build inputs before a separately authorized local build. Existing compiler availability must be established; no automatic install or PowerShell process-name termination fallback. |
| `case_evidence.py` / recorder | Validate each frozen expected outcome and both cleanup domains; retain failures, checkpoints, timing and hashes. Record host/native overhead separately from workload RSS. |

The native language choice implements the existing OS contract; it changes no
solver, actuator, sensor or scientific assumption. If available tooling cannot
implement that interface, stop for review rather than switching containment.

Linux launch ownership must originate in the selected user-manager service.
Keep its delegated root empty of tasks; place the guard in its own leaf before
enabling domain controllers for children. `DelegateSubgroup` may arrange this
on supported systemd versions; a later inspect must establish actual support.
No systemd operation ran here. The upstream manual documents delegation and
its optional subgroup placement. [systemd source documentation](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.resource-control.xml)

The guard opens/binds unit and leaf directory identities, verifies effective
limits (768 MiB whole-unit memory backstop, no swap, 32 PIDs), and launches
only fixed held children. Workload RSS remains separately sampled at 512 MiB.
Enumerate and recheck all membership; fail on unknown coverage or unexpected
subgroups. Root absence requires reaping evidence. Kernel cgroup membership
omits zombies, so empty membership cannot substitute for direct-child reaping.
`cgroup.kill` acts hierarchically; use it only on the owned leaves and verify
`populated=0` afterward. [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)

Native readiness requires a source/binary-bound launcher identity and collector
created suspended, successfully assigned to its non-breakaway Job, then resumed.
Pass only the intended pipe handles; close partial handles on every failure.
Creation/assignment failure is terminal before child release.
[Process creation](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw),
[Job assignment](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject)

The collector obtains physical-byte values using initialized and checked
`GlobalMemoryStatusEx`; failures produce null values with native errors.
[Memory API](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-globalmemorystatusex)
The launcher owns the Job and collector handle and has a watchdog independent
of pipe parsing/API calls. Frozen heartbeat/expiry are 0.5/1 s; its local
absolute lifetime includes startup/cleanup. Job close is a kill backstop;
explicit membership and handle-exit evidence are still required by our contract.
[Windows Jobs](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
After wrapper exit, the bounded native verification query must confirm the
recorded launcher's creation identity has exited. Denial, missing identity,
hang or wrapper EOF alone leaves native cleanup unknown.

Issue both Linux stop and native stop requests before awaiting either domain;
attempt each even if the other raises. Share the existing 5 s cleanup deadline,
not 5 s per domain. If inner control stalls, guard cleanup and native heartbeat
expiry remain independent. Never certify success from a callback Boolean.
Store root-reaped/return code, empty membership/populated observations, native
Job active count, collector handle exit, launcher exit probe, survivors/errors,
identity binding and observation brackets. Acquisition/verification failures
produce a finite partial report and block the next case and owner release.

Guard startup, setup, all failed attempts, case cleanup and final writes consume
the frozen 180 s suite reservation (30 + 10×12 + 30). Each 12 s case includes
5 active, 5 cleanup, 2 evidence seconds. A manager/backstop covering guard
failure and a recorder outside the inner control loop must retain last durable
state; process death during reporting cannot invent a completed event. No
watchdog claims recovery from kernel/hardware hangs. Unknown termination is a
stop requiring reconciliation, never a fresh suite ID or budget reset.

## Frozen case evidence and refusal map

Every row also requires source/contract bindings, bounded acquisition/decision
gaps, two-domain cleanup plus launcher exit, durable parent state, all-attempt
accounting, and untouched physical sentinel. These obligations are unchanged
from R081; none of the live rows has run.

| Case | Required distinctive evidence | Refusal / expected-stop rule |
|---|---|---|
| L01 | 3 s sleep, root identity/zero exit, membership and baseline RSS | Missing root/reaping/cleanup or cadence failure refuses success. |
| L02 | Three identities and barriers at baseline/16/64/128 MiB each; two accepted samples per stage; touched-page deltas | Preserve R081 tolerance and 384 MiB payload limit. Missing plateau samples fail; never extend barriers. |
| L03 | Root exit, `setsid` descendant still in owned membership | Expected abnormal-root stop requires actual descendants and verified group cleanup; root disappearance is insufficient. |
| L04 | Exit 7 before first checkpoint, observed return code, null unknown scientific counts | Classify return-code failure distinctly; no invented final zero counts. |
| L05 | Inner 0.25 s timeout and independent guard responsiveness | Expected wall stop only with cleanup; outer timeout is an unexpected failure. |
| L06 | Identity-specific RSS sample exceeding test-only 24 MiB cap after 32 MiB payload | Expected injected RSS stop; real 512 MiB/host/backstop breach is terminal failure. |
| W01 | Native API units, request/receipt brackets, Job/collector and launcher identities | Missing native final/query evidence refuses even with Linux zero exit. |
| W02 | Suppressed reply for 0.6 s, real watchdog evidence and raw versus injected samples | Expected host timeout by send+0.5 s; no cached reading or delayed-success revival. |
| W03 | Collector exits on request 2, native handle/EOF and Job cleanup | Expected helper failure is a test pass only with both domains clean. |
| I01 | Inner heartbeat stall, guard 0.25 s fault deadline, last durable parent checkpoint | Independent guard stop, null unknown counts and native cleanup; stalled inner loop cannot write its own success oracle. |

## Next bounded implementation and stop

Use **GPT-5.6 Luna/medium** for one new **fixture-only** repair bundle, before
implementing the OS harness. Repair G01–G07, absolute schedule phase, strict
owned-cleanup schema and an injected two-domain finalizer. Add a terminal
incremental parser and deterministic owner-state transitions behind fake
operations. Do not add native source/build, systemd/cgroup operations or a live
entry implementation in this step. The table above bounds the later OS work;
it is not a concurrent second task.

Preserve all archives and production pins. Use Python 3.12.13 with a **120 s
total execution reservation / 256 MiB validator address space**. Keep failed
attempts and charge enclosing execution, including startup/setup/final
persistence; independently measure child/recorder lifetimes, bound output, and
reserve final bookkeeping before release. Declare any uncovered measurement
scope rather than claiming end-to-end coverage. Refuse unknown/open/resource-
stopped history. No request ID, copy or output path resets a consumed allowance.

Completion requires all intended test functions executed exactly once, F01–F11
and G01–G07 regressions with valid rebound hashes, deadline/cleanup/host boundary
checks, independent cleanup despite either callback failure, exact zero final
sentinel counts, inert legacy entry points, complete per-attempt source bodies
and hashes, durable failure/partial records, and correct derived attempt/RSS
summaries. Test native ownership and guard failure only through injected facts.
Stop on unexplained failure, resource stop, unsettled policy or before any live
OS operation. Then recommend Astra/high for acceptance/ownership/provenance
review and a decision on the separately bounded OS implementation. Use Astra
earlier if a required containment/timing/accounting choice cannot be resolved
within this frozen contract.

The session catalog and official OpenAI Docs were checked for
[Luna/medium](https://developers.openai.com/api/docs/models/gpt-5.6-luna) and
[Astra/high](https://developers.openai.com/api/docs/models/gpt-6-astra).
This recommendation is task-specific; no model switch, delegation or automation
occurred. PC retains ownership and stops after scoped delivery. **Next prompt:
Continue.**

## R084 fixture implementation outcome

R084 implements the G01–G07 and ownership/reporting repairs in a new
[fixture bundle](evidence/r084/README.md); the R082 source, evidence and three
attempts remain unchanged. All 22 discovered fixture functions are registered
once and passed in attempt 3. Attempts 1 and 2 each exposed a known fixture
assertion (terminal-protocol instance reuse; then a source-manifest path base),
not a resource stop. Both failures, complete source bodies/hashes, partial
progress, and source-bound reconciliation events are preserved and fully
charged; cumulative total is 15.690793/120 s. Maximum validator lifetime RSS
is 30,060,544/268,435,456 B. Python 3.12.13 was used. The test run also checks
the saved R082 source manifest and R084 per-attempt snapshots, exact R070
sentinel count/schema acceptance, parser terminal state, 5 s cleanup boundary,
absolute sampling phase and independent cleanup after callback failure.

The recorder measures setup/snapshot, validator child and finalization
intervals; it conservatively charges a five-second final persistence reserve.
Interpreter startup/imports and that reserve are explicitly outside timed
intervals, so this is not whole-process resource certification. No native
implementation/build/startup, live OS operation, cgroup write, signal,
workload, FEM/MPI/JIT, mesh/solve, render, encode or physical run occurred. The
R070 physical CLI/API remains disabled; 180 s / 1536 MiB physical limits and
the unused q64/q96 allowance are unchanged. The current handoff selects
Astra/high review of acceptance, ownership and provenance before any OS
harness implementation decision.
