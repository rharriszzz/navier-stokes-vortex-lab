# R257 — Manufactured spatial BE source review and one-use admission

2026-09-26; PC/WSL `daisy` retains ownership. **Admit one NEW later n=2
manufactured spatial BE pilot. Zero attempts spent in this review. Stop before
launch.** The six historical allocations remain spent; saved R246/R253 remain
PASS, R242 INCOMPLETE and the R229 setup predicate false. Follow the
[single next task](../../SESSION_HANDOFF.md#next-task).

## Source review and repairs

The [R256 integration](MANUFACTURED_INTEGRATION_R256.md) implements the fixed
[R255 contract](VERIFICATION_MILESTONE_R255.md). The residual and both degrees
consume exact polynomial history and the corrected discrete load from
`step_forms`. The driver installs the lateral lift, perturbs the lowest free
velocity DOF, freezes row scales, checks measured compatibility/three-row
conditioning and performs checked Newton corrections. Every correction saves
its latest sparse system before factorization. The final state feeds all 60
scalar assemblies and both cap samples; expected rational values are used for
comparisons, never substituted for measured values.

Both degree reports retain signed rate and interval budgets, independent
rational initial inventories and measured final inventories, physical stress,
body terms and BE dissipation. Coarse approximation errors are reported without
Poiseuille exactness or refinement-rate gates. The held worker checks source,
reservation, cgroup and thread settings before imports. Fixture dispatch uses
the existing finite supervision/cleanup path and strict 2 MB envelope.

Three files were repaired within that contract:

- `manufactured_report.py`: the BE identity now uses all three separate absolute
  terms in the R255 roundoff bound and the existing sequential signed defect.
  The prior two-value scale could become too small under cancellation. The
  three-by-three Gram input now rejects booleans and malformed rows explicitly.
- `manufactured_driver.py`: reservation/admission aliases compare types as well
  as values. Latest-system reading is bounded before decoding. Replay requires
  the full recorder schema, CSR and finite vectors, unchanged solver/options,
  caps, source, fixed lift, scale extrema and latest RHS norm; the previous
  validator could accept an otherwise bound record missing matrix/vectors.
- `test_manufactured_integration.py`: cancellation and schema substitutions are
  checked; a real standard-library `LatestSystem` record replaces the minimal
  synthetic record. Rehashed missing/malformed CSR, boolean values, altered
  RHS/lift/scales and changed solver settings all refuse.

This restores or enforces the fixed contract. No fixture mathematics, solver,
scientific threshold, resource cap, old source policy or historical evidence
changed. Saved linear evidence contains the pre-factorization system, not the
solution increment; the recorded true correction residual still comes from the
source-bound driver. Only the latest system persists; earlier receipts retain
hashes. This does not independently reconstruct all prior corrections or prove
full operator rank.

[104 tests](evidence/r257/tests.json) pass under pinned Python 3.12.13, including
saved R246/R253 validator replay, with no numerical modules loaded. The
[six caller checks](evidence/r257/caller_tests.json) pass with fake Git/manager
and no launch. They cover source/caller/manifest/contract/artifact drift,
interpreter/library/archive changes, spent directories/dangling links,
memory/controllers/manager refusal, timer-before-import ordering, no writes on
preflight refusal and PASS/INCOMPLETE persistence.

## Admission, bindings and measurement risks

The [allocation](evidence/r257/allocation.json), [finite caller](evidence/r257/run_once.py),
[44-file source inventory](evidence/r257/source_inventory.json), and
[artifact inventory](evidence/r257/artifacts.json) define the sole new allowance.
The fixed output directory **`/tmp/navier-manufactured-r257-once`** is absent,
including dangling links. The source proposal remains non-executable with zero
attempts; this separate admission grants exactly one later attempt.

| Binding or limit | Fixed requirement |
|---|---|
| Fixture/mode/schema | manufactured / single_be_spatial_pilot / 1 |
| Domain/step | affine unit cube, n=2, one step at t=dt=1/8 |
| DOFs | 402 mixed, 405 bordered; latest-system ceiling 512 |
| Quadrature | residual 24; diagnostics 24/26; 30 scalars each |
| Source | exact clean launch HEAD supplied after later Continue STARTED publication; all 44 hashes match |
| Interpreter | `/tmp/navier-fenicsx-r229/bin/python`, Python 3.12.13; exact binary hash in allocation |
| Runtime artifacts | eleven file hashes, four library resolutions and cached archive; existing exact-artifact acceptance retained |
| Manager | reviewed version 249.11-0ubuntu3.22, refreshed by caller before reservation |
| Time | 180 s overall; setup/work/finish 15/150/15 s; independent worker 149 s + 1 s stop grace |
| Resources | 1536 MiB, no swap, 32 tasks, one rank/thread |
| Persistence | numerical envelope 2,000,000 bytes; latest CSR 4 MiB and 65,536 entries |

The launch commit is materialized into admission, reservation and held source
receipt at execution, avoiding a self-referential publication hash. Later
lifecycle/documentation commits may advance HEAD with the frozen source/caller/
manifest/contract/artifact hashes intact. Keep the owning checkout/environment
unchanged throughout execution. Caller timer starts before project imports
and all preflight checks. No prewarming or standalone numerical imports.

The [read-only audit](evidence/r257/audit.json) verifies the 44 current bindings,
R255 rational reference and five negative controls, all 74 original raw files,
six retained reservations and absent recorded PIDs/cgroups, eleven artifacts,
four resolutions, archive and interpreter. Host memory was 6,443,124 KiB
available and unified memory/PID controllers were present. Those are snapshots;
the caller refreshes them. No manager connection occurred. Installed DOLFINx/UFL
source methods support the form/domain/measure inspection; the scalar
ZeroBaseForm path requires argument spaces, so ordinary rank-zero forms are
required. Actual simplification, JIT, assembly and API behavior remain untested.

This admission explicitly permits measuring once whether the fixed manufactured
forms, nonlinear solve, coarse budgets, quadrature pairs and runtime/resources
pass. Any such refusal spends the attempt; no symbolic-zero substitution,
tolerance tuning, cap expansion, fallback solver or retry. Even a PASS means
one-level discrete solve/diagnostic consistency; spatial/time convergence,
stability/rank and physical realizability remain open. n=4/8 still exceed the
512-DOF recorder ceiling and are not admitted.

Acceptance requires both-degree numerical gates, source/version bindings,
actual exit 0, finite peaks within caps, zero memory.max/OOM/OOM-kill/PID-limit
events and empty known cleanup. Saved controller PROVISIONAL_PASS is insufficient:
completion and caller must be PASS with no late marker or persistence error.
Existing limits remain: sampling ends before final handshake/exit; final save
tails and independent parent wall interval are unobserved. No cold-cache
performance claim or resolution of the SuperLU package/embedded-label origin.

Directory creation/reservation or partial worker start spends the allowance.
Preserve partial results, logs and any latest system; stop after one outcome.
Only a demonstrated caller/preflight error before reservation, managed worker
and numerical import may be repaired within the same unspent authorization:
preserve the failure/timing gaps, verify absent directory and no new manager
task, test the repair, publish a clean binding, then continue the same contract.
Uncertain state stops for review; no inferred reset or alternate directory.

## Next task and session recommendation

**Use `/new` after publication, select GPT-6 Sol / high, then send Continue.**
The supplied context snapshot was 22% remaining and this completes a substantial
review with a durable launch handoff. Task boundaries and saved state guide
this recommendation; there is no fixed context-percentage rule. The
[official CLI guide](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
distinguishes fresh chat (`/new`) from summary (`/compact`). R257 adds an explicit
chat recommendation to AGENTS.md and the session protocol for future completions.

Sol/high should execute only this allocation once on PC/WSL daisy, preserve raw
evidence and cleanup/spent state, publish and stop. Return to Astra/high for
scientific interpretation or gate changes. The [official Sol page](https://developers.openai.com/api/docs/models/gpt-6-sol)
confirms high support; suitability is judgment, account-specific availability
unverified. No agent model/session switch, real worker, reservation, numerical
import, JIT, solve, manager access, installation or machine transfer occurred.
