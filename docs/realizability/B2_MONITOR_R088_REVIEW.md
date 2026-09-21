# R096 acceptance review of R088

Reviewed on PC/WSL `daisy`, 2026-09-21, from clean synchronized base
`aeb7de5b48f142b387cf212b39f31d23204dfacf`; STARTED publication `a10d4a5`.
**Refuse OS implementation admission.** R088's saved 14-function pass is
internally consistent and its original owner/cleanup counterexamples now refuse.
Three residual completion-evidence gaps and the missing independently bounded
outer receipt prevent full H01–H04 acceptance. This review does not change
R088's source, evidence, attempt allowance or historical claims.

The [audit](evidence/r096/README.md) confirms nine observations in one separate
bounded invocation. Its positive control reproduces the saved accepted result,
including six exact integer zeros. No archived validator/recorder main ran.
Physical **180 s / 1536 MiB** limits, unused q64/q96 allowance and failed B2
accuracy remain unchanged. The [handoff](../../SESSION_HANDOFF.md#next-task)
owns the single next task.

## H01–H04 disposition

Source references below are to [R088 source](evidence/r088/source/); saved
examples and all 14 pass labels are in [fixtures.json](evidence/r088/attempt_01/output/fixtures.json).

| Obligation | Source and evidence | Acceptance decision |
|---|---|---|
| H01 immutable ownership and composition | `integration.Domain/Ownership`, `Owner`, `cleanup_observation`, `finalize`, `accept_sentinel`; all-state, failure-order, identity and positive fixtures; R096 `rebound_owner_attempt_refused` and `rebound_cleanup_identity_refused` | Accept the fixed owner/run/attempt/cleanup binding, all acquired-state finalization and repeat-safe returned result within the synchronous fake interface. Refuse the complete completion-evidence obligation: monitor counts/samples remain unchecked (J02). Live resource acquisition and independent dispatch remain unimplemented assumptions. |
| H02 callbacks, deadlines and persistence | `Clock`, `supervise.active_boundary`, `finalize.boundary`; exact 5/5.001 s, combined 3+2.001 s, write/clock failure and fake guard fixtures | Accept checks after returned callbacks and shared cleanup timing in the generated composition. Refuse complete timing certification: acceptance lacks an authoritative absolute reservation (J03), and the outer startup/final-write interval remains unmeasured and unenforced (J04). |
| H03 terminal, ordered, fixed framing | `host_protocol.request/reply/feed/expired`, the single protocol instance in `supervise`; both protocol fixtures and runtime simultaneous-stop fixture | Accept R085's three repairs for the composed interface: failed requests latch, completed acquisition brackets cannot regress, bound fixed at 4096 bytes, and core/transport share state. This is not native transport/watchdog validation. |
| H04 exact types, input bindings and all-attempt accounting | `Policy.validate`, `attempt_accounting.prior_elapsed`, `recorder_policy`, `run.py`; accounting/source fixtures, inventory, bound event, progress, receipt, ledger | Accept exact successful return-code/policy types and this saved attempt's source/input/output bindings and arithmetic. Refuse full exact-schema/durable acceptance (J01/J02) and whole-recorder accounting (J04). Historical exclusions remain explicit. |

## Residual findings

All executed rows below have the original positive control and saved hashes in
[review.json](evidence/r096/attempt_01/review.json). These mutate copies of saved
evidence; none demonstrates an actual over-budget supervisor run.

| ID | Finding and source | Executed evidence / required repair |
|---|---|---|
| J01 durable candidate comparison aliases types | `integration.py:371` compares dictionaries using Python equality, then hashes only the in-memory candidate. The separately supplied persisted candidate is not schema-validated or canonically hashed. | Changing only persisted `schema` from integer `4` to float `4.0` leaves dictionary equality true and completion accepted, even though the receipt digest differs from the persisted candidate digest. Validate the durable object independently and bind its canonical bytes as well as the in-memory object. |
| J02 incomplete monitor evidence validation | `integration.py:353–358` checks field names/status/code, but never validates `monitor.counts` or `monitor.samples`; lines 407–415 then synthesize a successful legacy watch. | Changing all monitor counts to integer `7` while child counts stay zero still completes. Removing every runtime sample also completes. Validate the full monitor schema and required sample evidence; distinguish explicitly unknown post-release monitor counts from known child zeros and refuse contradictory known counts. Do not synthesize evidence completeness from status alone. |
| J03 no admitted deadline binding at acceptance | `integration.py:381–385` checks only relative cleanup ordering and a five-second span. Ownership binds no policy/deadline; `accept_sentinel` receives no authoritative reservation. | Rebinding candidate+receipt to cleanup start/observation 20 s, deadline 25 s completes, despite the source fixture's active/outer deadlines being 10/15 s. Bind the named policy and absolute active/outer reservation at admission and independently check them during acceptance. This is a missing acceptance input, not evidence that `supervise` ignored its deadline. |
| J04 outer boundary unresolved in implementation | `run.py` starts `ENTRY` after interpreter startup and persists receipt/ledger after sampling `charged_seconds`; `integration.finalize` returns an in-memory receipt after candidate persistence. | Source/saved-data finding, no hang launched. The five-second charge is a reservation, not an observed or enforced upper bound. There is no independent receipt covering this enclosing guard's final persistence/exit. Refuse whole-recorder/live admission until the external observation/timeout/persistence interface is bound and reviewed. |

H03's acceptance is scoped to composition: `feed` does not call `check_time`
on a fragment without a newline. The supervisor checks time around every poll,
so a standalone caller must maintain that same boundary; the future transport
must not call it as an independently timed interface. This is source inspection,
not a separately executed counterexample or a claim of complete parser coverage.

## Review of all 14 saved functions

Names below follow `test_`. R096 compares AST discovery with unique registration,
progress and final checks; no archived test body is re-executed. Line locations
are retained in the audit JSON.

| Function | What the assertions establish / limit |
|---|---|
| `positive_composition_and_physical_deny` | Positive owner/protocol/cleanup/R070 path, ordered calls and exact zeros; both physical entry refusals. No external guard receipt. |
| `every_acquired_state_and_idempotency` | Four states × four domain inventories, prior failure latched, repeated finalization has no repeated callbacks. Acquisition itself and concurrent finalizers are outside scope. |
| `cleanup_failure_orders` | Either stop or observation fails; both stop requests precede observations and helper observation is attempted. No blocking callback is run. |
| `owned_identity_and_schema_refusals` | Frozen public owner fields, malformed admission, rebound candidate owner/cleanup mutations, strict child counts/extra fields. It does not mutate the separately persisted candidate or monitor counts. |
| `deadline_cleanup_and_persistence_boundaries` | Exact five seconds accepted, 5.001 refused, shared cleanup span, write error and six-second post-write refusal. Candidate may survive without an accepted receipt. |
| `clock_faults_and_policy_types` | NaN/negative/Boolean clocks, float/Boolean policy version, fixed policy values, clock throw during cleanup and regression. Second domain remains attempted. |
| `early_launch_and_callback_refusals` | Guest/host headroom, delayed guest, pre-release zeros, release-then-fail unknown counts, missing five-second reserve. No live acquisition barrier. |
| `protocol_terminal_request_and_order` | Duplicate/invalid request remains terminal; regressed completed brackets and widened frame limit refuse. |
| `protocol_framing_timeout_and_exact_types` | Trailing/multiple/oversize/API/wrong-type frames, split frame, EOF, send deadline and previous-send freshness. Partial-fragment timing relies on composition. |
| `runtime_boundaries_and_simultaneous_stops` | RSS equality; simultaneous RSS/deadline/host expiry; active equality and provider mismatch. No real memory pressure or OS scheduling. |
| `absolute_scheduler_and_tree_refusals` | Skip multiple 50 ms slots without phase drift; incomplete membership, Boolean/nonzero root code, surviving members refuse. No runtime container/reaper acquisition binding tested. |
| `fake_independent_guard_event_order` | A suspended generator and manually advanced guard event demonstrate logical ordering only. No independent process/watchdog/blocked syscall certification. |
| `accounting_exact_returncode_and_history` | R084 total and selected Boolean/open/resource/unknown refusals; conservative death classification. `recorder_policy.admit` is not invoked by the one-shot `run.py`; exclusive attempt directory provides that runner's no-retry gate. |
| `source_and_saved_evidence_bindings` | Full snapshot inventory; changed source and late receipt refuse. Does not test durable type alias, rebased complete interval or missing monitor evidence. |

## Provenance and outer measurement decision

All 16 snapshot entries match their saved hashes. Readable sources, recorder and
contract match the executed copies. Pre-release bound event, inventory digest,
progress/fixtures output digests and final receipt/ledger agree. R084's preserved
three-attempt history/reconciliations still totals **15.69079346198123 s**.
R088 has exactly one attempt charged **5.632544717984274/120 s**, child lifetime
**0.5840597350033931 s**, observed guard **0.6325276519928593 s**, and validator
peak RSS **23,941,120/268,435,456 B**. Nothing consumes or resets its remainder.
Input snapshots of logs/contracts remain historical bytes; later appended notes
are not retroactively substituted into that attempt.

**The declared outer boundary is insufficient for whole-recorder compliance
or OS-source admission.** Preserve its useful validator measurement. A future
outer observation must start before the enclosed recorder's interpreter/setup,
bind run/attempt/owner/source/policy and its absolute reservation, and observe
the recorder's last durable output plus exit. Acceptance must bind the candidate,
inner receipt, monitor/child reports and independent outer receipt together.
Missing, late, open, resource-stopped or unconfirmed evidence must leave a finite
partial/refused result and block continuation. A charged reserve alone cannot
discharge this requirement.

For the observer itself, require an already armed enclosing lifetime backstop
and a separately observable terminal event; its startup and persistence also
consume the declared total. A record cannot measure its own final fsync/exit.
If that enclosing observation is unavailable, state the exclusion and keep
whole-recorder admission disabled. The existing R081/R083 manager/native design
bounds later implementation; this review does not select a new OS mechanism or
pretend that fake evidence certifies it. This is the stopping boundary for R096.

## One bounded follow-up

Use **GPT-6 Astra/high** on PC/WSL `daisy` for one **completion-certificate
repair in new source with fake checks only**, addressing J01–J04 together.
Read this review and R088's contract/source, with R085/R083/R081 for the outer
obligations. First specify the immutable admitted policy/reservation and the
independent outer-receipt schema/trust boundary. Then implement typed canonical
durable binding, complete monitor/count/sample validation, admitted absolute
deadline checks and a required outer-receipt gate. Model the guard/recorder
events with injected facts only; keep real OS and physical entries disabled.

Completion requires the positive composed sentinel and J01–J03 negatives,
missing/late/mismatched/unpersisted outer-receipt refusals, exact deadline
boundaries, unknown counts preserved on partial results, both cleanup domains,
all intended tests registered once, and source-bound partial/final evidence.
Use Python 3.12.13, at most **120 s cumulative new fixture reservation / 256 MiB
validator address space**, reserving setup/final evidence before each release.
This is prospective work, not permission to retry R088 or rerun R096.
Preserve all failures; open/unknown/resource stops block further attempts.
Declare any execution measurement exclusions honestly; even passing fake
guard tests cannot certify whole-recorder or live behavior.

Stop before native source/build/startup, live OS/cgroup/signal/helper/workload,
FEM/MPI/JIT, physical work, and at a containment/timing/accounting choice that
cannot satisfy the existing contract. Do not resolve that choice by widening
limits or calling an unenforced reserve measured. End with Astra/high acceptance
review as the next task; recommend Luna/medium only after interfaces and outer
semantics are settled and remaining edits are mechanical.

Model/effort availability was rechecked in the session catalog and opened
official [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) pages using
OpenAI Docs. The supplied usage snapshot does not establish current entitlement.
No model switch, delegation or automation was performed. **Next prompt: Continue.**
