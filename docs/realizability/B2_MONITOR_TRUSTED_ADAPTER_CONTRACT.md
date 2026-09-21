# R099 trusted-adapter authority and accounting contract

Written 2026-09-21 on PC/WSL `daisy`; source base
`d26b1adbef44d49582a88f058a5cfbcd222bfd32`, STARTED `fe67f6a`.
**Decision: specification complete; implementation admission refused.**
The existing records do not establish an authority that can both enforce the
whole task boundary and retain its terminal facts durably. This document makes
that missing obligation concrete; it does not assert that such an authority
exists, select a replacement containment policy, or authorize execution.
The [handoff](../../SESSION_HANDOFF.md#next-task) owns the next decision.

Inputs are the [R098 review](B2_MONITOR_R097_REVIEW.md),
[R097 contract](evidence/r097/contract.md), exact
[Admission and TerminalWitness definitions](evidence/r097/source/certificate.py),
[ownership interface](evidence/r097/source/integration.py),
[frozen policy](evidence/r097/source/primitives.py),
[R081 suite](B2_MONITOR_LIVE_VALIDATION_CONTRACT.md#5-frozen-future-pc-suite) and
[R083 boundary](B2_MONITOR_R082_REVIEW.md#missing-harness-implementation-boundary).
All are preserved. This is a required adapter contract, not OS capability evidence.

## Authorities and finite trust root

`M` means the **already selected, pre-existing systemd user manager**, whose
candidate delegation path was recorded by R081. `M` is the only proposed
external authority here, not an extra task-created watchdog. No claim is made
that its current interfaces satisfy this contract. `O` is the task-created
outer observer/guard; `R` is the task-created recorder/control path that it
observes. Both startups, all their descendants, and task-specific manager
requests are charged. R083's independent native launcher/watchdog and bounded
exit query remain required; Linux wrapper exit never substitutes for them.

Trusted infrastructure may include the existing manager, kernel clocks/process
identity and persistence primitives. Their pre-existing lifetime, unrelated
work and passive storage after a successful terminal commit are outside the
attempt. **Their work on this invocation is inside its accounting boundary**:
reservation, timer configuration, unit creation, identity reads, stop dispatch,
exit queries, verification, ledger writes and terminal retention. No script,
unit hook, new daemon, forwarding helper or finalizer becomes infrastructure
merely by running outside `R` or `O`.

A successful adapter must obtain authority through an identity-bound manager
interface with protected state. A caller-provided dataclass, matching JSON,
hash, filename, distinct token or zero return code does not authenticate it.
The trust root ends at a documented manager transaction and its persistence
primitive, not at another recorder claiming to have measured itself. The
transaction must expose a durable, immutable result and a conservative timing
bound that includes its commit. This capability is **required, unestablished**.
No guarantee against kernel/hardware hangs is added.

The authority record must bind the existing manager instance, machine/boot,
user identity, unique suite/attempt/nonce, selected contract and complete source
manifest, unit invocation and directory identity, process creation identities
and direct reapers, and one clock domain. A PID or reusable unit name alone is
insufficient. Native process creation/Job/handle facts remain independently
bound to that same attempt. Manager restart, clock discontinuity, unknown
identity, missing evidence or source replacement invalidates admission.

All admission/witness times use one manager-verifiable Linux monotonic domain
and boot origin. Bracket acquisitions and conservatively use the latest possible
completion for deadlines. Windows times remain diagnostic; Linux send/receipt
brackets bound native observations. Do not translate wall-clock logs or native
timestamps into this domain without an admitted conversion bound. An unknown
bound refuses success. No source hash authenticates an observation by itself.

## Admission field authority map

Each row is an obligation of the future adapter, not an implemented factory.
`M` must retain the reservation before releasing task-created work. Where actual
process identities are unavailable before creation, retain a manager-owned
reservation first, create only held resources within it, then bind the complete
Admission before release. This bootstrap needs explicit compatibility review:
R097 uses injected pre-existing identity tokens and has no real bootstrap API.
It cannot authorize uncharged setup or rebinding an already released owner.

| Exact field | Authority, acquisition and binding | Refusal |
|---|---|---|
| `owner_sha256` | M's exclusive reservation binds the canonical R097 ownership record: run ID, attempt, nonce, manifest, workload/helper container identities and reapers. O checks actual held-resource identities against it before release. | Caller-only ownership, reused invocation, unknown reaper, missing domain binding or changed record. |
| `policy` | M admits the named frozen contract/case; independent adapter validates every Policy field below. It is not copied from a child report. | Arbitrary caller policy, wrong case or any relaxed constant. |
| `reserved_at` | M records the start of this invocation before its first task-specific setup action, including reservation persistence; setup delays consume this time. | Timestamp taken after setup, unknown earlier interval or unresolved prior attempt. |
| `recorder_deadline` | M derives an absolute bound within the existing case/suite reservation; O enforces R exit by it. At least five cleanup seconds follow the active deadline. | Deadline shift, less cleanup reserve, no independent enforcement or exit too late. |
| `enclosing_deadline` | M arms O's absolute lifetime bound before O startup, within the original total, with positive time after the recorder bound. Terminal retention must also fit the total, as below. | A bound relative to late startup, additional allowance, missing arming evidence or no retained outcome. |
| `clock_domain` | M binds the monotonic source, origin/boot and manager instance before time acquisition. O/R inherit that association. | Clock/boot/manager mismatch, regression or unknown conversion. |
| `recorder` | M's admitted invocation-role token maps to R's actual creation identity, source manifest and owning reaper before release. O observes startup and exit. | Unbound name/PID, wrong executable/source or reused identity. |
| `observer` | M's invocation-role token maps to O's creation identity, source and reaper; M observes O independently of R. | R can forge/replace the binding, O startup unobserved or O/R identities coincide. |
| `backstop` | M's pre-existing instance and per-invocation timer/enforcement record; distinct from O and R. | A new unaccounted helper, string-only identity, stale timer or dependence on O/R responsiveness. |

The nested `policy` fields are exhaustive: `schema` remains exact integer 3;
`tree_cap_mib` comes from the named case (512 MiB live suite, explicit L06 test
cap only); `deadline` is its absolute active deadline; `tree_interval_s=0.05`,
`host_interval_s=0.5`, `host_minimum_mib=1024`, `cleanup_limit_s=5.0` remain fixed.
Launch age/headroom, host freshness, framing and benign-suite cadence rules
remain R081 obligations even where not serialized inside Policy. Schema 5's
fake example start/active/recorder/enclosing values 0/10/15/17 are not new live
limits. Physical limits remain 180 s / 1536 MiB, q64/q96 unused, B2 accuracy failed.

## TerminalWitness field authority map

O writes OuterReceipt after observing R; M constructs the witness from its own
retained facts and source-bound persistence evidence. The consumer must retrieve
those facts through the admitted authority path and verify the bindings before
calling the pure R097 validator. It must never deserialize arbitrary JSON into
an apparently trusted witness. An unavailable observation is unknown, not false
or zero. Exact Boolean/integer and finite-number rules remain in force.

| Exact field | Authority and observation event | Refusal |
|---|---|---|
| `receipt_sha256` | M binds the canonical OuterReceipt whose committed bytes it can retrieve from the admitted store; compare admission/owner/source/monitor/child/candidate/inner-receipt digests too. | Hash-only caller assertion, different bytes, absent commit or binding mismatch. |
| `observer` | M resolves the admitted O invocation to its creation identity/reaper and retained exit event. | Reused PID/name, another observer or unobserved identity. |
| `backstop` | M's same instance and per-attempt enforcement record that armed the admitted timer. | Different/stale authority, self-assertion by O or record lost on restart. |
| `clock_domain` | M's admission-bound monotonic domain for arming, persistence and exit brackets. | Any cross-boot/domain mismatch or unknown bound. |
| `armed_at` | M records completed activation of enforcement, before O startup; task-specific arming begins no earlier than the accounted reservation. | Merely requested timer, activation after startup or omitted setup time. |
| `armed_deadline` | M reads back the effective absolute O lifetime bound; it equals `enclosing_deadline`, independent of O/R loops. | Requested-only configuration, relative restart or mismatched effective deadline. |
| `receipt_durable_at` | M obtains authoritative completion of the exact O receipt's persistence transaction, at/after its write-start and before O exit. A writer's timestamp before final sync is insufficient. | Failed/blocked write, missing file/directory durability semantics or unverifiable completion time. |
| `observer_exited_at` | M's identity-bound terminal observation/reaping evidence after receipt durability, conservatively within the enclosing deadline. | EOF alone, O's own exit claim, unreaped/unknown identity or late bound. |
| `exit_code` | M's retained O wait/terminal status; exact integer zero required for successful completion. | Boolean zero, unknown status, signal death or nonzero status. |
| `terminal_confirmed` | M confirms O exit and absence of residual task-owned work, including required R083 Linux/native cleanup and launcher-query facts; retain the underlying observations. | A success flag without facts, surviving/unknown members or unresolved query. |
| `timed_out` | M's latched outer deadline event history; False only with complete history through terminal retention. | Missing history, expiry or late final transaction; clean later exit cannot erase it. |
| `resource_stop` | M's bound enforcement observations plus required O/native evidence; False only with complete coverage and no real resource stop. | Unknown coverage, actual backstop/pressure stop or discarded stop record. |

R097 validates only receipt-through-O-exit facts. Even a fully authentic
TerminalWitness is insufficient to certify M's later retention/accounting.
A future version needs a separate **manager terminal transaction record** binding
the witness/receipt, reservation, stop history and final ledger, with bounded
start/completion, durable terminal state and authoritative retrieval semantics.
This document specifies the obligation but neither introduces executable schema
nor changes the archived R097 dataclass. Success cannot be obtained by leaving
that extra record to an unmeasured `finally` block.

## Event and accounting map

Let `S` be the already-reserved suite start and `D` its immutable total deadline.
For R081, all attempts together have at most 180 s: 30 shared setup + ten 12 s
cases + 30 final validation/reporting. Each case retains 5 active + 5 cleanup +
2 evidence seconds. These are ceilings/subdivisions, never fresh budgets after
failure. The historical 120 s fake reservations are separate and unchanged;
R099 consumes no execution attempt or allowance.

| Ordered event | Responsible authority and required durable evidence | Charge and enforcement |
|---|---|---|
| E0 reservation begins | M receives the admitted invocation, excludes any prior open attempt, fixes source/contract/nonce and retains STARTED/reservation. No caller launches a bootstrap process first. | Suite setup starts at S, including reservation work. Pre-existing M must enforce this entry phase; a timer created later cannot cover it retroactively. |
| E1 arm backstop and prepare ownership | M configures/verifies the absolute timer, limits, held unit/resources, identities and complete Admission. Retain activation/effective settings and bootstrap bindings. | Within the same 30 s setup ceiling and D; failure consumes time and leaves held work subject to cleanup. No uncharged pre-unit helper. |
| E2 O startup | M creates source-bound O under the admitted boundary and records its startup; O cannot define its own starting time after imports. | Startup, interpreter/imports and source checks counted; M's timer already active. |
| E3 R startup and readiness | O creates/observes R; verify both cleanup domains, fresh gates and held children before release. | Shared setup/case reservation as applicable; no overlap double-counting or omitted gap. Guard/control/workload remain under the selected unit backstop. |
| E4 active case | R/O observe fixed stimulus, membership, memory and timing. Periodic bounded durable checkpoints preserve the first stop and unknown counts. | At most 5 s, within immutable case deadline; guard/native watchdogs independent of blocking providers. |
| E5 both-domain cleanup | Dispatch Linux and native stops before waiting on either; verify identities, empty membership, root reaping, native Job/collector and launcher exit. | One shared <=5 s interval inside that case, including native verification query; exceptions still attempt both domains. |
| E6 R durable outputs and exit | O verifies exact candidate/inner receipt/monitor/child bytes, durability and R's independently observed zero exit. | R exits by recorder_deadline; reporting/exit consumes reserved evidence time, no appended grace. |
| E7 O receipt durable and O exit | M obtains the authoritative persistence and exit facts in the witness map. | O lifetime ends by enclosing_deadline. Per-case evidence shares its existing 2 s ceiling; suite-wide receipt work uses the existing final 30 s. |
| E8 terminal query, validation and retention | M validates/binds witness and ledger and durably commits the terminal outcome after O exit, with all task-created workers stopped. | Query, commit and all task-specific finalization must finish by D inside the final reserve; M must enforce this transaction too. No new task-created final observer. |
| E9 passive retention | The committed immutable terminal record remains retrievable, with replay/identity protection. | Idle storage and unrelated M lifetime excluded. Any task-specific retry, repair, polling or revalidation is work, not passive retention. |

For a successful interval, require
`S <= armed <= O_start <= R_start <= R_durable <= R_exit <= O_receipt_durable <= O_exit <= terminal_commit <= D`,
with the finer receipt-write/active/cleanup checks still enforced. Shared setup,
case intervals and final reporting must all lie in their frozen subdivisions.
Unused time does not authorize an extra case, replay or resumed stopped attempt.
If O can use its full enclosing deadline D, no positive final persistence reserve
remains; the adapter must reserve E8 beforehand within the existing final 30 s
and choose O's earlier bound accordingly. R097's check `O_exit <= enclosing`
alone does not enforce that separation. A later detailed schedule is required
before admission; this document grants no numeric enlargement.

A successful charge includes every task-specific elapsed interval from E0 to
E8, including gaps/blocked work. Concurrent subintervals are reported separately
but not added twice to wall elapsed. Across attempts the ledger accumulates all
charges; unknown duration is never zero. If E8 cannot be observed, keep the
reservation unavailable and the attempt open/failed. Record any later observed
overrun honestly; do not clip elapsed to the limit to fabricate compliance.
Cleanup remains necessary after expiry, but cannot justify more compute, a new
attempt or a successful within-budget claim.

The existing 768 MiB whole-unit/no-swap/32-PID backstop covers task Linux leaves;
512 MiB is sampled workload RSS, and native aggregate working set stays <=128 MiB
with separate measurements. They are distinct metrics. Task-specific manager
operations outside the unit must be identified and their resource/enforcement
scope justified; calling them infrastructure cannot make them covered by the
unit limit. This is another part of the unresolved M capability, not permission
to move the editor shell or assume a new aggregate cap.

## Failure and continuation rules

| Condition | Required outcome |
|---|---|
| Missing admission, timer activation, source/identity or prior-attempt closure | Refuse release. Retain charged setup and any held-resource cleanup evidence. |
| Late/mismatched fact, even followed by correct values | Latch refusal; never overwrite the first stop or move a deadline. |
| Blocked provider, pipe, checkpoint or cleanup | O/M and native watchdog obligations remain independent; try both cleanups. Missing final evidence remains partial. |
| R death | O retains last durable state, actual status and cleanup; no successful certificate from a stale candidate. |
| O death | M retains actual exit/timer facts and last durable state. A receipt missing its durable commit is not completed. |
| M death/restart, lost event stream or unknown boot | No independent terminal authority remains; open/unknown, stop further attempts and execution-owner release pending reconciliation. No extra manager is assumed. |
| Receipt or ledger persistence fails, blocks or completes after D | Refuse success. Preserve prior durable state; if even failure reporting cannot persist, absent terminal state itself blocks continuation. |
| Terminal query denied/hung, nonzero exit, membership/reaping unknown | Partial/unconfirmed; no success, fresh suite ID, retry or transfer of execution ownership. |
| Hardware/kernel hang or unconfirmed enforcement | Report uncertainty and stop; no watchdog guarantee or silently extended cleanup allowance. |

No task runs in this documentation session, so its normal repository completion
and retained PC ownership do not represent release of an unresolved live attempt.

## Compatibility and decision boundary

| Existing obligation | R099 reconciliation / remaining gap |
|---|---|
| R097 J01–J03, schema 5 and frozen Admission | Preserve every gate and all saved positives/negatives. External authority must precede release; a bootstrap reservation for real held identities requires a reviewed future interface, not mutation of historical ownership. |
| R097 J04 receipt plus typed witness | Preserve all 12 witness fields and validations. Add authenticated acquisition outside the pure validator; object type/digests alone are insufficient. |
| R097 exclusion of enclosing backstop lifetime/output | Exclude only pre-existing unrelated infrastructure lifetime/passive storage. E0/E1/E8 task work is charged. This narrows future claims; it does not retroactively certify R097. |
| R081/R083 whole-reservation accounting | E0–E8 includes startup, setup, failures, both cleanups, queries and final persistence. The required manager transaction is not established by an inner timer or fixed unmeasured reserve. |
| R081/R083 containment and resources | Keep selected user-manager delegation, owned cgroups/direct reaping, native Job/watchdog/query and existing limits. Manager entry/final-transaction enforcement and outside-unit task overhead remain unestablished. |
| Historical measurements | R097 charge 5.34962656602147/120 s remains historical; its five-second addition is unmeasured/unenforced, guard startup/final writes/exit excluded. No new fixture, live or physical certification. |

**Implementable under established capabilities: no admission can be justified.**
This is not proof that systemd cannot support a suitable design. The repository
contains no demonstrated or documented mapping from the selected manager to
an atomic, authoritative reservation/enforcement/terminal-retention interface
covering E0/E1/E8. Naming M does not supply that interface.

The exact unresolved policy choice is whether the existing manager can serve
as the finite trusted boundary for those operations with a documented durable
completion bound and resource scope. If it cannot, a different trusted boundary
or a weakened accounting claim would require an explicit policy decision; neither
is selected here. Creating another unmeasured helper is not a repair. The real
identity bootstrap also needs to be mapped to that same boundary before source
implementation. Stop here rather than assume either capability.

One next task: **GPT-6 Astra/high documentation-only capability decision** for
this selected manager. Using official manager/kernel documentation and these
saved contracts, map E0/E1/E8 and identity bootstrap to concrete APIs and their
limits; produce a supported design or an explicit unsupported verdict with the
precise policy choice for user review. No live inspection, adapter/native source,
fixtures, build/startup or execution allowance. Do not write another generic
contract or authorize OS source from hypothetical capability. Only a supported,
settled boundary may yield a separately bounded OS-source task. Otherwise stop
with the decision for the user. Local links/preservation/pointer checks suffice.

Retain Astra/high for that unresolved authority decision; it is listed in this
session's catalog and high effort is supported by the opened official
[Astra documentation](https://developers.openai.com/api/docs/models/gpt-6-astra),
checked using OpenAI Docs. Recheck model availability and consider a smaller
model only once the work is mechanical. No model switch, delegation or automation.
