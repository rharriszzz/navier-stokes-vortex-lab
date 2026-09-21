# R098 acceptance review of R097

Reviewed 2026-09-21 on PC/WSL `daisy`, from synchronized base
`9ed35fca076d413916e2b0ab9bb4a041a9adcb02`; STARTED published as `83b19ba`.
**Accept J01–J03 within the fake completion interface. Accept J04's injected
receipt checks, but refuse whole-recorder certification and OS-source admission.**
The remaining task is a specific contract repair for the trusted enclosing
adapter, not another broad fixture rewrite. The
[current handoff](../../SESSION_HANDOFF.md#next-task) owns that task.

This is source/saved-data review only. All nine bodies and their registration
were read; no archived module was imported or executed. The independent
[saved-data check](evidence/r098/saved_validation.json) verifies ten snapshots,
17 output bindings, registration/progress/results, partial examples and ledger
arithmetic. It does not repeat R097's behavioral tests or authenticate its fake
witness. All prior source/evidence and attempt allowances remain unchanged.

## J01–J04 evidence and disposition

Source locations below refer to [R097 integration.py](evidence/r097/source/integration.py),
[certificate.py](evidence/r097/source/certificate.py) and
[validate.py](evidence/r097/source/validate.py). Saved outcomes are in
[fixtures.json](evidence/r097/attempt_01/output/fixtures.json).

| Obligation | Source and saved assertions | Disposition |
|---|---|---|
| J01 independent durable validation | `validate_candidate` (integration line 359) runs on both candidates; `accept_sentinel` (387) compares canonical bytes and the persisted digest. `test_j01_independent_durable_types` covers float/Boolean/null schema, float owner attempt, extra field and rebound in-memory/durable float schema. | Accepted for these schema-5 documents. Python equality no longer suffices. Real durability remains an adapter obligation. |
| J02 full monitor evidence | `validate_monitor` (certificate 66) checks six exact count keys, known integer agreement, nonempty exact sample fields, consecutive sequence, finite ordered brackets/decision, cap, membership and terminal zero-exit/empty members. `accept_sentinel` validates the enclosing monitor, candidate, receipt and child. `test_j02_counts_and_samples` supplies rebound negatives and a known-zero positive. | Accepted for the declared fake schema. Unknown post-release counts remain null; only independently validated child zeros supply completion counts. This does not establish real sampling coverage, the future live cadence, or authenticity of OS readings. |
| J03 admitted policy/deadlines | Frozen `Admission` (certificate 21), frozen `Policy`, `Owner` (integration 86), pre-release policy/deadline comparison in `supervise` (246), independent absolute checks in `validate_candidate` and acceptance. Rebased 20/25 s cleanup refuses; mismatched policy/deadline refuses before release and attempts both cleanups. | Accepted under a trusted supplied admission. Active equality refuses; cleanup/persistence equality at the five-second boundary passes; recorder/enclosing equality at 15/17 s passes and late evidence refuses. Actual backstop enforcement remains J04. |
| J04 enclosing receipt/terminal authority | `validate_outer` (certificate 108) binds admission/owner/source/monitor/child/candidate/inner receipt; checks startup-through-recorder-exit chronology; requires a separate typed witness bound to receipt, clock and identities. Outer/witness groups cover missing, mismatched, open, late, unpersisted and stopped facts. | Accept the fake gate and its refusal behavior. Authority construction, task-specific outer accounting and final durable terminal observation remain unspecified; the real recorder still excludes startup/final writes/exit. OS-source admission remains refused pending the bounded contract repair below. |

These are scoped acceptances, not proof that every malformed Python object or
all possible OS failures are covered. The trusted input assumptions are part of
the interface. No new executed counterexample or actual resource overrun is
claimed in this review.

## All nine function bodies

The AST locations and saved registration order are in the validation JSON.
Names below omit `test_`; each is registered once and has a saved pass.

| Function | Assertions and limit |
|---|---|
| `positive_composed_and_physical_deny` | Ordered release/both stops/both observations/persistence, exact child zeros, monitor nulls, two physical refusal paths, false live/whole-recorder flags. The positive witness is constructed in the fixture itself. |
| `j01_independent_durable_types` | Independent durable and jointly rebound malformed candidates refuse; no OS persistence test. |
| `j02_counts_and_samples` | Nonzero/Boolean/float/negative/string counts refuse, known zero passes; empty/reversed/malformed samples and nonterminal final states refuse. No host/native acquisition or live cadence measurement. |
| `j03_rebased_cleanup_and_admission` | Rebased completion refuses; frozen-field mutation and wrong owner refuse; mismatched launch admission attempts both cleanup observations without release. No trusted admission factory is implemented. |
| `exact_active_cleanup_and_enclosing_boundaries` | 5 versus 5.001 s persistence, active equality, exact 15/17 s recorder/observer ends and just-late ends. Times are injected, not measured callback durations. |
| `outer_missing_mismatched_open_or_stopped` | Empty receipt/witness and individual schema, binding, identity, return-code, stop and chronology mutations refuse with recomputed receipt hash. No independent OS observer runs. |
| `witness_unpersisted_late_unconfirmed` | Wrong receipt/identity/clock, late arming, wrong bound, premature durability/exit, late exit and wrongly typed/unconfirmed/stopped terminal evidence refuse. Typed construction does not confer authority. |
| `partial_cleanup_both_domains_and_unknown_counts` | Stop/observation failures in either domain still attempt both; repeated finalization is callback-free; post-write failure leaves a candidate without acceptance. Five partial examples are saved. No blocked callback is launched. |
| `sources_registry_and_owner_binding` | Every snapshot digest, changed fixture input refusal and rebound helper-reaper mismatch refusal. The main function separately enforces complete unique registration and checkpoints before each test. |

R097 does not rerun every R088 regression; the nine groups are the new repair
coverage. The integration module's inherited mention of a fake event scheduler
is not evidence of an additional R097 test. Its synchronous callbacks still
assume independent external intervention if they block.

## Provenance, measurement and remaining boundary

All ten input snapshots match; readable sources/contract/runner match executed
copies. The historical handoff matches the R097 STARTED commit, rather than
being compared with today's handoff. STARTED and inventory bindings, all 17
receipt-listed outputs, nine AST/registry/progress/result entries and the single
receipt-bound ledger agree. Five saved partial examples preserve unknown counts.

R097's child lifetime is **0.3257114120060578 s**, peak RSS **23,834,624 B**;
observed guard **0.34962656602147035 s**, charge **5.34962656602147/120 s**.
The five-second addition remains unmeasured and unenforced. Interpreter startup
before ENTRY and guard receipt/ledger persistence/exit remain excluded. This
review consumes no new fixture attempt and does not reset historical allowances.

The new receipt/witness division avoids having a recorder assert its own exit.
However, `TerminalWitness` is a public dataclass and `validate_outer` trusts its
values after type/binding checks; `Fixture.proof` constructs it from the same
fake clock as the receipt. Distinct string names are not independent process
or manager identities. This is intentional in R097's fake contract, not evidence
that the checks failed. A real adapter must establish those facts externally.

The [R097 contract](evidence/r097/contract.md) explicitly excludes the enclosing
backstop's lifetime/output. The [R083 boundary](B2_MONITOR_R082_REVIEW.md#missing-harness-implementation-boundary)
and [R081 suite](B2_MONITOR_LIVE_VALIDATION_CONTRACT.md#5-frozen-future-pc-suite)
require task startup, setup, failed attempts, cleanup and final reporting within
the existing reservation. R097 does not distinguish an already-running trusted
system manager from task-specific backstop/verification/reporting work. Nor does
it specify a concrete evidence path from that manager to witness construction,
including clock identity, terminal-query failure and durable retention.

**Decision:** the declaration is sufficient to describe fake acceptance, but
insufficient to bound the later OS-source task under the recorded admission
obligations. An unimplemented adapter alone would not forbid source design;
the unresolved authority and accounting interface is the blocker. Do not infer
actual compliance from the fake witness or retroactively certify R097. A
pre-existing manager can be a finite trust root without measuring the lifetime
of the entire OS; task-created setup/query/persistence must not disappear into
that exclusion. This review stops before selecting a new containment or timing
policy.

## One bounded follow-up

Stay on PC/WSL `daisy`, **GPT-6 Astra/high**, for a **documentation-only repair
of J04's trusted adapter contract**. Preserve R097 and write one new contract
against R081/R083 and this review. No fixture execution, adapter/native source,
build/startup, live inspection/mutation, helper/workload, FEM or physical work.

Specify a concrete authority/evidence table for Admission and every
TerminalWitness field: responsible existing-manager/observer component, bound
invocation/process/source identity, clock origin, acquisition event and refusal
on missing/late/unknown data. Draw one finite event sequence from reservation
through task-specific backstop arming, observer/recorder startup, durable output,
recorder exit, outer receipt durability, observer exit and terminal retention.
State where all task-specific setup, querying and final persistence are charged
and enforced within the existing total; identify precisely what pre-existing
infrastructure is trusted outside it. Include blocking/death/persistence-failure
outcomes and how unknown/open evidence blocks another attempt and owner release.
Do not substitute a caller-authored JSON witness for authority.

Completion requires a field-to-authority map, complete event/accounting map,
compatibility map to R097 and R081/R083, and an explicit implementable/refused
decision. Use source/docs only; check links, append-only history, archived-byte
preservation and consistent next-task pointers. If existing containment/timing
policy cannot supply the facts, document the exact unresolved choice and stop
for review; do not widen limits, add another assumed trusted process or launch
an exploratory test. Only a settled contract may lead to a separately bounded
OS-source task. No new execution allowance is allocated by this follow-up.

Retain Astra/high while authority/accounting decisions remain. Recommend a
smaller model only after semantics settle and remaining work is mechanical,
rechecking availability then. Astra/high is present in the session catalog and
its reasoning setting was checked against the opened official
[Astra model page](https://developers.openai.com/api/docs/models/gpt-6-astra)
using OpenAI Docs. No model switch, delegation or automation occurred.
**Next prompt: Continue.**
