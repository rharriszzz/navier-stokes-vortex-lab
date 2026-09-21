# R085 review of R084 acceptance, ownership and provenance

Reviewed on PC/WSL `daisy`, 2026-09-21, from upstream
`26f7071a54096822fec78b9ebb16d248870103f1`; R085 STARTED was published as
`5e70f07`. The [handoff](../../SESSION_HANDOFF.md#next-task) owns the next task.

**Do not begin the OS harness yet.** R084's recorded 22-function pass and source
snapshots are internally consistent, and the original G04/G05 examples now
reject correctly. Ownership, cleanup timing, protocol and accounting interfaces
still have gaps. These prevent using R084 as an implementation-review binding.
The [single audit](evidence/r085/README.md) confirms the counterexamples below
with fake inputs. No archived test main or recorder was rerun. No live monitor,
native helper, physical or FEM execution occurred. Physical limits remain
180 s / 1536 MiB, q64/q96 remains unused, and B2 accuracy remains failed.

## G01–G07 disposition

Source paths below refer to the preserved [R084 bundle](evidence/r084/source/).
The [R083 requirements](B2_MONITOR_R082_REVIEW.md) and
[R081 contract](B2_MONITOR_LIVE_VALIDATION_CONTRACT.md) remain authoritative.

| Finding | Reviewed implementation and evidence | Disposition |
|---|---|---|
| G01 registration | `validate.main` compares all discovered names with its unique registry; AST registry, saved report and final progress agree on 22 functions | Repaired for the saved attempt. Individual assertions still have coverage limits below. |
| G02 cleanup time | `supervise` measures the callback and rejects >5 s; exact 5/5.001 fixture exists | Callback example repaired; checkpoint/reporting and owner clock handling remain incomplete, H02. |
| G03 previous-send freshness | Core checks previous accepted send before replacing it; protocol checks receipt against preceding send | Original path repaired by source inspection. Registered test calls the helper at 1/1.000001 s but does not reproduce R083's complete delayed-replacement scenario. Checks after every callback remain incomplete. |
| G04 canonical counts | `finalize_child` uses nested counts, exact keys and integer zero sentinel values; rejects duplicate top-level counts | R085 directly confirmed accepted output has all six exact zeros and rejects a duplicate with recomputed child hash. |
| G05 strict completion | Exact monitor/child key sets and integer schemas; rejects monitor errors/survivors | R085 directly confirmed the three original monitor mutations reject. R084's similarly named mutations actually alter the child without rebinding its hash; those negatives alone did not establish semantic coverage. Owner binding remains absent, H01. |
| G06 terminal framing | `reply`/`feed` latch malformed replies, EOF and overflow; `expired` latches timeouts | Improved; invalid requests are not terminal, frame bound is caller-relaxable, and parser brackets can regress, H03. |
| G07 provenance | All 64 inventoried files have matching before/archive/after maps and 192 preserved snapshot bodies; derived totals and final attempt ID match | Repaired inventory/summary errors. Unbound external inputs, missing attempt-1 progress and unenforced outer timing remain qualifications, H04. |

## Residual findings and executable evidence

| ID | Observed result | Required acceptance before OS implementation |
|---|---|---|
| H01 ownership and integration | A correctly hashed child claiming workload identity `(999,999)` completes against a watch claiming `(10,7)`. `finalize_child` has no authoritative owner argument. `finalize_owned` returns extra fields rejected by core's exact cleanup schema. Finalization from `OWNED_HELD` rejects before either callback. | One versioned owner-to-cleanup-to-completion schema; compare observations with immutable owned identities and run/attempt nonce. Finalize every state with acquired resources, including setup failure and a latched error. Test the complete fake composition, not only each helper. |
| H02 complete timing boundary | A cleanup callback returns immediately, then the cleanup checkpoint advances fake time by 6 s; `supervise` returns `completed` and reports cleanup=6 s with no cleanup error. | Check the shared absolute deadline after checkpoint/report/provider boundaries and before success. Independent outer evidence must cover stalled callbacks and final persistence. Exact deadline, overrun and invalid clock cases must use the composed path. |
| H03 protocol state | A duplicate request raises but the pending good reply still succeeds. A second reply ending at 0.1 s follows one ending at 0.2 s and is accepted. An 8192-byte constructor bound accepts a 4379-byte frame exceeding the frozen 4096-byte limit. | Terminal failure for request as well as reply/transport errors; ordered local brackets; fixed contract framing bound; one authoritative state shared by core/transport. |
| H04 strict accounting and provenance | `prior_elapsed` accepts `False` as the final successful return code; `Policy(schema=3.0)` validates. Saved historical types are correct; these are prospective refusal gaps. | Exact types at every admission boundary. Bind actual external inputs and reconciliation state before release; detect resource deaths conservatively; independently bound and measure outer persistence. Preserve historical exclusions. |

The audit output records 14 result groups, including positive controls,
preservation, exact count/schema controls and the above counterexamples. A
successful audit means the observations were reproduced; it does not mean the
reviewed monitor passed these requirements.

Additional source findings explain the scope of these groups:

- H01: `OwnedRun` identity fields are mutable and omit Linux unit/reaper and
  native Job/launcher ownership. The finalizer invokes a complete workload
  callback before invoking the helper callback; it cannot issue both stop
  requests before awaiting either. A throwing clock can escape between them.
  It cannot be called idempotently after `FINALIZED`. Neither core nor copied
  R070 consumes its complete result. Cleanup dictionaries still contain no
  root-reaped, populated, Job-active-count or launcher-exit observations.
- H02: core continues using the pre-checkpoint `now` for scheduling. Its report
  sink sees an object before final timing is computed. `safe_time` falls back
  after clock errors without invariably revoking completion. The separate
  finalizer does not validate monotonic finite clocks or freeze its deadline
  parameter. No hung callback was launched to demonstrate these source paths.
- H04: outer timing starts inside recorder `main`, and the five-second final
  persistence charge is neither measured nor enforced. No independent recorder
  guard exists. CPU hard-limit termination may appear as SIGKILL, and address
  space exhaustion as `MemoryError`; the recorder's resource classification
  only recognizes timeout, measured RSS excess, SIGXCPU and SIGXFSZ. A later
  reconciliation must not classify an unexplained death as a fixture assertion.

These are unmet existing contract obligations; no new physical threshold,
containment mechanism, solver, sensor or actuation decision was selected here.

## Review of every saved function

All rows refer to attempt 3's saved pass; R085 inspected their bodies and AST
registration without executing the archived suite. Exact saved labels and
function names are retained together in [review.json](evidence/r085/review.json).

| Function after `test_` | What its assertions establish / practical limit |
|---|---|
| `launch_gate` | Independent headroom and age refusals; no actual release or owner binding. |
| `scheduler_completion` | Three samples, waits and durable cleanup checkpoint; no delayed checkpoint. |
| `absolute_scheduler_phase` | Preserves phase after a 0.03 s delay; does not exercise skipped multiple slots. |
| `root_descendants` | Root exit with members refuses success and requests cleanup. |
| `incomplete_membership_and_provider_freshness` | Immediate incomplete-membership refusal and 1.1 s tree delay. |
| `cleanup_error_is_reported` | Callback exception/malformed data and finite report sanitation. |
| `cleanup_deadline` | Callback 5 s passes and 5.001 s fails; H02 extends the boundary. |
| `owned_independent_finalizer` | Workload exception still invokes helper; no helper exception, held-state, hang or composed acceptance test. |
| `tree_brackets_and_host_identity` | Regressing tree bracket, duplicate PID, wrong nonce and unsolicited reply refusals. |
| `invalid_clock_and_bool_flags` | Selected bad flags/caps/cadences; float policy schema not covered. |
| `future_acquisition_and_bad_status` | Future tree bracket and provider status failure. |
| `deadline_boundary` | Active deadline stops at equality. |
| `rss_boundary_and_host_stop` | RSS equality and low host memory; no actual pressure. |
| `partial_report_and_finite_json` | Reporting exception and JSON sanitation; no bound on reporting duration. |
| `host_timeout_and_clock_regression` | Helper freshness boundary, first-response timeout and initial clock regression; no cleanup/report clock fault. |
| `proc_stat_parsing_and_membership` | Injected text, missing/wrong identity, zero RSS, zombie, absent root. |
| `cleanup_classification` | Pure confirmed/failed/unknown classification; no owned OS observation. |
| `attempt_accounting_refuses_open_unknown_failed_and_exhausted` | Selected malformed histories and bound reconciliation; Boolean success return code omitted. |
| `host_protocol_success_and_sequence` | Two sequential replies and terminal duplicate reply. |
| `host_protocol_fail_closed_cases` | Malformed/oversized/API/EOF/identity cases and split frame; H03 cases omitted. |
| `disabled_r070_and_completion_binding` | Physical CLI/API refusal and positive completion; most child mutations retain stale hash, so semantic isolation is incomplete. |
| `continuity_and_source_bindings` | Source/snapshot/archive checks and current docs; external docs/ledger inputs are outside source inventory. |

## Historical accounting and reconciliation

The saved charge is **15.69079346198123 s / 120 s** and maximum child lifetime
RSS is **30,060,544 B / 268,435,456 B**. All three attempt files match their
ledger entries; final fixture digest, progress, result and checkpoint agree.
The saved R082/R076 evidence and production inputs are preserved by the final
Git-object validation. No archive was edited to incorporate this review.

Both reconciliation maps bind the failed snapshot and immediately following
source. Attempt 1's known terminal-protocol fixture reuse and attempt 2's wrong
manifest base are consistent with preserved tracebacks and source changes.
The first correction also added progress persistence, active attempt lookup and
reconciliation support; it was more than a one-line fixture edit. Attempt 1
therefore has no `partial_fixture_progress` field or saved per-function progress
file; its traceback is preserved. Its failure and charge remain useful evidence, without inventing
which checks were durably recorded. Attempt 2 retains 21 completed checks.

The 64-file inventory covers `source/` and the recorder. It does not snapshot
all inputs actually consumed by validation: current handoff/log files, the
generated source manifest, active attempt/ledger/reconciliation data, and R082
manifest/source outside that tree. Their present contents can be checked;
their exact per-attempt external bytes cannot all be reconstructed from this
inventory. This qualification and the outer timing exclusions prevent full
all-input/all-time certification. Do not retroactively authorize retries,
replace old records, infer excluded duration as zero, or rerun an archive.

## Decision and bounded next work

The R083/R081 OS design remains a useful component/responsibility boundary,
but is insufficient as an executable admission contract until H01–H04 are
resolved. **Current next task: GPT-6 Astra/high, one new fixture-only integration
repair.** First make the existing ownership/deadline/evidence obligations
explicit in a single schema and transition table, then implement the composed
fake owner/core/transport/acceptance path and strict recorder admission in a
new version. Use existing policies; stop for review if satisfying them requires
a different containment, timing, cleanup or accounting policy.

Require positive composed completion with exact sentinel zeros, mismatch and
malformed-type refusals, every acquired-resource state, independently issued
stop requests despite either domain's failure, shared deadline overruns,
terminal/ordered/bounded host input and source-bound durable partial evidence.
Preserve all archived sources/results and hard-disabled physical entries.
Use Python 3.12.13, 120 s cumulative fixture execution reservation and 256 MiB
validator address space; reserve setup/final evidence before release, record
every failed attempt and uncovered interval, and refuse open/unknown/resource
stops. A passing fixture result must not be labelled whole-recorder or live
certification. Stop before native source/build/startup, OS mutations, live
adapters, workload, FEM or physical execution. Complete with a reviewable
source-to-contract map, composed fixture evidence and scoped publication.

After that acceptance review, a **separate future OS source task** may implement
the R083 facade/guard/Linux/transport/native source interfaces and all ten R081
case definitions in a new bundle. Its boundary is source plus fake checks only,
120 s fixture reservation / 256 MiB validator, no native build/startup or live
entry release. Verify contract hash, default-deny admission and every case's
expected evidence. Stop on tooling/containment ambiguity; do not install or
change the platform silently. Build and actual ten-case validation need their
own reviewed task; the frozen live allowance remains 180 s cumulative with
512 MiB workload RSS and its distinct backstops, entirely unused here. This
future task is conditional, not a second active assignment.

Keep Astra/high while ownership/timing/accounting interfaces require judgment.
Recommend Luna/medium only once those interfaces are settled and the remaining
task is mechanical; return to Astra/high at a contract or scientific decision.
Both choices were checked in the current session catalog and official
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) documentation.
The supplied old Luna status reports 1% reserve remaining; it is a historical
snapshot, not current account entitlement or a claim of a model switch.
