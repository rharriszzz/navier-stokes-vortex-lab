# R269 — Angular sidecar review and separate diagnostic admission

2026-09-26 (America/New_York), PC/WSL `daisy` retains ownership.
**Accept the R268 assembly source with the R269 validation repair and admit
one NEW later diagnostic pilot. Zero new attempts are spent in this review.**
R266 remains INCOMPLETE and all nine older allocations remain spent. This task
stops before numerical imports, manager access, reservation or worker launch.

## Contract review and source repairs

The [R267 contract](MANUFACTURED_ANGULAR_REVIEW_R267.md#fixed-next-source-contract-record-the-missing-angular-evidence)
and [R268 implementation](MANUFACTURED_ANGULAR_SIDECAR_R268.md) are accepted as
an evidence addition. The residual, solver, exact history/corrected BE load,
30 original diagnostics, numerical envelope and physical/resource gates are
unchanged. The physical angular defect remains the scientific decision.

| R267 requirement | Review finding |
|---|---|
| Final raw residual | Driver installs the accepted state before diagnostics. Helper compares all 402 installed field coefficients with that state and uses the original momentum/continuity form, direct vector assembly and reverse ghost accumulation. It calls no lift, elimination, scaling, Jacobian assembler or solver. |
| Mixed angular test | Collapsed velocity interpolation maps through the returned parent map into a zeroed mixed Function. Pressure entries stay zero. The fixed solution trace is not applied to Phi. |
| Both degrees and final multipliers | Both residuals reference the installed field. Each degree's three Constants receives the accepted P_minus/P_plus/eta before any sidecar scalar or vector assembly. Degree26 is diagnostic only. |
| Face signs and independent action | A_D/C_D use exactly tags1–4; A_R/C_R/G_R use tags5–6. C uses minus physical stress torque, G uses P times Phi.n minus offset.Phi. UFL action replaces the original test by Phi; the vector dot is reduced separately. |
| Five identities | fsum fixed/free action, reaction plus lateral advection, signed physical/prescribed traction split and all five independent comparisons match R267. Finite measured failures remain evidence. |
| Persistence and original refusal | Worker supplies the mandatory callback. Exclusive finite schema1 JSON is capped at 262,144 bytes; old linear evidence is untouched. Callback runs before the old envelope returns, including on physical-budget refusal. |

Review found two validation/test gaps. R268 checked a partition of 402 entries
but allowed wrong component counts; a synthetic 372/30 partition passed its
old structural checks after consistent re-reduction, reproduced by the
[old/new source probe](evidence/r269/review_probe.json). R269 requires exactly
375 velocity entries, 27 pressure entries and a list of 125 coordinate rows.
Malformed coordinate containers now raise the repository refusal explicitly.
The old five tests never invoked `assemble_record`; the new injected assembly
test exercises that actual helper without importing numerical libraries.

The new `validate_numerical_aliases` helper verifies source identity, geometry,
step/time/dt, fixed values/count, final multipliers and all eight original
angular terms against the saved numerical envelope. Booleans are rejected as
fixed numeric values. This check is used only by the new caller: historical
payloads and their validators have no new sidecar requirement. The old envelope
contains no full final field, so a cross-file comparison of its 402 coefficients
is unavailable; the helper's installed-field comparison supplies that check
inside the worker, under the bound source and ordinary process trust.

The pinned DOLFINx source documents collapse as a new-to-parent DOF map and
coordinate tabulation for point-evaluation elements. Its vector routine zeros
a newly allocated vector and assembles without boundary elimination, leaving
ghost accumulation to the caller. The pinned UFL action implementation expands
derivatives and replaces the final Argument with the supplied coefficient.
Four inspected API files are now additionally hashed in the artifact inventory;
all eleven prior artifact identities remain unchanged. The public
[DOLFINx 0.10 API](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/generated/dolfinx.fem.html)
supports the collapse/coordinate interface. These source checks do not establish
actual JIT or assembly success; no numerical library was imported here.

## Checks and preserved evidence

[127 guarded tests](evidence/r269/tests.json) pass under the pinned Python
3.12.13, including the 123 prior cases and four new focused cases. The new
assembly fixture has nontrivial maps, nonzero face partitions, distinct final
multipliers, separate scripted scalar/vector action paths and a deliberate
mismatch. It checks all fourteen compile/assembly routes, reverse ghost update,
vector destruction, pressure weights and refusal of a pre-correction state or
wrong-rank residual. It does not simulate a real UFL compiler or FEM discretization.

The first test run had one failure in a hand-calculated C_D expected value.
The independently recalculated fake face sums are C_D=-0.42 and G_R=1.66;
those two test literals were corrected without changing the runtime formulas.
The [initial test output](evidence/r269/initial_test_failure.txt) is retained.
Final tests also cover map/container refusal and cross-file mutation controls.

[Eight caller tests](evidence/r269/caller_tests.json) use fake Git/manager/
supervisor responses, real bound-file hashes and temporary synthetic result
folders. They cover the six existing preflight/dispatch cases plus bounded
strict sidecar parsing, numerical aliases, preserved measured mismatch, and
missing/inconsistent sidecar refusal even after an inner PASS. They never create
the fixed run directory. Saved R246/R253 PASS validators, rebuilt R266 refusal,
R255 exact reference and R267's four decomposition controls reproduce.

The [audit](evidence/r269/audit.json) verifies 48 unchanged of 49 older source
bindings, the one validation edit and one new test file, all 116 raw/caller
originals and Git-index bytes, 1,814 unchanged historical evidence files,
nine spent reservations, and absent recorded PIDs/cgroups. Fifteen artifacts,
four library resolutions, cached archive and interpreter verify. The new
[source inventory](evidence/r269/source_inventory.json) binds 50 files.
Publication checks cover AST/JSON, local links, append-only logs, sequential
request IDs, lifecycle records, scope and whitespace. No numerical imports,
JIT, assembly, solve, manager/worker, full convergence/tank/B2, physical/render
work or Mac transfer occurred.

## New allocation and finite caller

The [allocation](evidence/r269/allocation.json) and
[caller](evidence/r269/run_once.py) authorize exactly one later attempt at
`/tmp/navier-manufactured-r269-once`, currently absent including any dangling
link. It is separate from all nine spent allowances. The exact launch commit
must be a clean HEAD after the later Continue STARTED publication; caller,
source/artifact inventories, manifest, contract and interpreter hashes must
match before manager access or reservation. Keep the checkout unchanged during
execution. No standalone numerical import or compiler prewarming is allowed.

The caller retains the reviewed supervisor and manager path, outer timer and
15/150/15-second phases. Caps stay 180 seconds observed total, independent
149-second worker expiry plus one-second grace, 1536 MiB/no swap, 32 tasks,
one MPI rank and one numerical thread per library. The same n=2, t=dt=1/8,
402 mixed / 405 bordered DOF pilot, degree24/26, 2,000,000-byte numerical report
and <=512 DOF / 4 MiB / 65,536-entry latest system limits apply. Memory-max,
OOM, OOM-kill and PID-limit events continue to refuse acceptance.

After the supervisor returns, including INCOMPLETE, the new caller reads at
most 262,145 sidecar bytes, validates strict schema/aliases and records its
hash, size and ten consistency flags in `caller.json`. A missing or malformed
sidecar raises a recorded reason; a finite inconsistent sidecar remains saved
with false flags. Either prevents outer PASS. A sidecar PASS cannot promote
an inner INCOMPLETE or a failed physical budget. The original controller and
worker numerical decisions are unmodified. The extra read/reduction work stays
inside the existing outer timer; the worker's extra twelve scalar assemblies
and two residual assemblies stay inside its existing work/resource allowance.

The admission is justified by the fixed diagnostic question: independently
measure how the failed physical defect splits into lateral reaction/stress,
return traction, and free residual contributions. A repeated physical failure
is expected to remain INCOMPLETE and can still provide useful evidence. No
new scientific threshold or mesh/stress/residual definition is selected.
Additional compilation cost, real sidecar size, API behavior, signed split and
whether these measurements isolate the cause remain unknown. A compilation,
resource or evidence failure is an admissible spent outcome, never permission
to relax a gate or retry. R266's pre-exit resource snapshot remains historical;
final save tails and an independent parent wall interval remain unobserved.
R229's environment setup resource predicate remains false. No cold-start,
convergence, validated manufactured solve or physical-control claim follows.

Reservation/directory creation or partial worker start spends this new 1/1
allowance. Preserve all complete/partial files, caller output, failure stages,
resource observations and cleanup result; ensure raw logs are included in Git.
Stop after that outcome. Only a demonstrated caller/preflight error before
reservation, worker or numerical import follows the existing recovery rule:
retain error/timing gaps, verify absent fixed directory and no new manager
process, repair/test and publish a clean binding before proceeding with the
same unspent allowance. Uncertain state stops for review. Never reset a spent
allowance or choose an alternate directory.

Next: **use `/new`, select GPT-6 Sol / high, then Continue** on PC/WSL daisy
to execute only this fixed caller once, preserve/publish all evidence and stop
for Astra/high interpretation. The admission is a saved task boundary; no
current context percentage was supplied. [Official OpenAI Docs](https://developers.openai.com/api/docs/models/gpt-6-sol)
confirms Sol supports high reasoning; account availability is unverified and
no model/session switch occurred. Follow the [single handoff task](../../SESSION_HANDOFF.md#next-task).
