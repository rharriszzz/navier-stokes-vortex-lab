# R251 — Rotation source review and one-use admission

2026-09-26, PC/WSL daisy. Base `698bd2f`; STARTED `ea8e824` published.
**Admit one NEW later n=2 exact-field rotation assembly, with the fixed caller
and bindings below. Zero attempts spent in this review. Stop before launch.**
The five historical allocations remain spent. R246 Poiseuille stays PASS;
R242 stays INCOMPLETE. The source proposal itself still grants zero attempts;
this separate admission is the only authority for the fresh allocation.

## Review decision

The R250 integration conforms to the [R249 contract](ROTATION_INTEGRATION_REVIEW_R249.md).
The [audit](evidence/r251/audit.json) verifies all 36 source/test/pin hashes
unchanged, replays the R250 audit and saved R246 report, verifies 60 retained
raw files against their original directories, and confirms all five old
reservations remain with their recorded PIDs/cgroups absent. R250's 93 passing
stdlib tests are reused with unchanged source bindings, not rerun.

The exact-field driver obtains measured mesh/tag/unused-space receipts from
`create_cube`, requires one rank and ordinary rank-zero forms on the actual
domain, checks face identities, and routes each of 38 keys at degrees 24/26
through `fem.form` and `fem.assemble_scalar`. Geometry is fixed to 48 cells,
27 vertices, 48 exterior facets, eight facets per face and 402 unused mixed
space DOFs. The space neither interpolates the fields nor enters a PDE solve.
The pure validator independently checks both-degree exact targets and all
38 pair differences, including five squared zero norms <=1e-20. Expected
numbers never populate assembled values. No scientific threshold changes.

The strict rotation manifest, admission/reservation and schema-1 envelope are
fixture-bound. Duplicate/nonfinite/malformed JSON refuses; the actual serialized
envelope is limited to 2,000,000 bytes. Numerical values, cached decisions,
geometry, receipts, source, executable and versions are revalidated. A complete
finite report can be preserved with failed numerical gates, but cannot produce
controller PASS. Held verification precedes numerical imports. Both wrappers
retain the shared reservation/exit/resource/cleanup/persistence lifecycle;
Poiseuille public schema-2 and solver gates remain separate and unchanged.
No runtime source repair was required by this review.

### Explicitly admitted API risk

Read-only review of installed DOLFINx `forms.py`, `mesh.py`, UFL `form.py` and
`integral.py` supports the methods used for topology, rank, domain and tag
inspection. Installed `forms.py` is unchanged since R249. Its ordinary Form
path extracts the mesh domain and compiles through FFCx; its ZeroBaseForm path
requires argument spaces. A scalar zero form cannot meet that assertion.
This agrees with the [published DOLFINx source](https://docs.fenicsproject.org/dolfinx/v0.10.0.post0/python/_modules/dolfinx/fem/forms.html),
searched/opened during review. Actual simplification, compilation and zero-kernel
assembly were not exercised. Admission explicitly permits measuring this risk
once: unsupported forms, JIT errors or nonfinite results refuse and spend the
attempt. No symbolic zero substitution, altered form or fallback retry.

Rotation's zero strain cannot independently validate viscosity coefficients,
production weak forms, pressure approximation or mesh/time convergence. This
is a fixed diagnostic/assembly oracle; no tank or physical-control claim follows.
The R247 independent exact targets and negative controls remain the reference.

## Fixed allocation and finite caller

[allocation.json](evidence/r251/allocation.json) freezes the full contract,
limits, original spent allocations and consumption/recovery rules.
[run_once.py](evidence/r251/run_once.py) is the only admitted caller.
The fixed absolute output directory is **`/tmp/navier-rotation-r251-once`**;
it is absent, including dangling links, at review completion.

| Binding | Required value |
|---|---|
| Fixture / mode / envelope | rotation / exact_field_assembly / schema 1 |
| Source | Exact clean launch HEAD passed explicitly after later Continue STARTED publication; all 36 source hashes unchanged |
| Source inventory | [source_inventory.json](evidence/r251/source_inventory.json); digest in allocation |
| Manifest SHA256 | `5f15e1293c95acbf1bce2e7b18307f94655e168b09a4217ffc915e0c3c0fa1cb` |
| Contract SHA256 | `5290c4357dba53fd47dde9e930506ddfd2453acdbe6c460332212c98d3c42507` |
| Caller / artifacts | Exact SHA256 values in allocation; caller checks itself and inventory bytes before reservation |
| Interpreter | `/tmp/navier-fenicsx-r229/bin/python`, resolving to `python3.12`, Python 3.12.13 |
| Executable SHA256 | `5f083df36ec986d5cd13d2549ca6cfe1ddaf658509f9e419b454b2fb375c27a3` |
| Reviewed manager | `249.11-0ubuntu3.22`; caller refreshes it, rejects drift; no manager connection in this review |

The exact launch commit is materialized into the strict admission, reservation
and held source receipt at later launch, avoiding a self-referential publication
hash. Documentation/start records may advance HEAD only with all frozen source,
caller and artifact bindings intact. Keep the owning checkout and environment
unchanged throughout execution; this is the existing single-owner trust boundary.

The [artifact inventory](evidence/r251/artifacts.json) retains R245's seven
runtime files and four library resolutions and adds the four inspected
DOLFINx/UFL source files. All eleven current hashes, all resolutions, interpreter
and cached SuperLU archive were verified by reads only. This preserves the
accepted package/embedded-label discrepancy and the held loader's narrow FFCx
exception. Rotation does not invoke SuperLU, but the unchanged pinned loader
still imports PETSc. No installation or full environment rescan occurred.

The caller starts a 180-second alarm before project imports and preflight.
Before reservation it checks clean exact Git identity, caller/source/manifest/
contract/executable/artifact/archive bindings, absent output directory, at least
1536 MiB available host memory, unified memory/PID controllers and the reviewed
manager version. It supplies a strict rotation admission to
`supervise_rotation_once` with `SystemdBackend(runtime_seconds=149)`.
Actual unit identity/effective caps/held source and independent expiry are
verified before release, including cleanup after a partial start.

A preflight refusal never writes into a pre-existing spent directory. The new
caller writes its receipts only after invoking the supervisor. A fake control
checks this protection along with timer ordering, literal rotation routing and
PASS/INCOMPLETE persistence. The six [caller checks](evidence/r251/tests.txt)
pass under the exact Python with `-I -S`, fake Git/manager only and no numerical
modules. They exercise source/allocation/caller/contract/artifact/archive/
library changes, directory/symlink existence, memory/controller refusal and
manager drift. Real preflight success and manager capability remain launch checks.

## Frozen ceilings and acceptance

Retain 180 seconds total including preflight and caller persistence; controller
setup/work/finish 15/150/15 seconds; independent worker runtime 149 seconds plus
one-second stop grace. Whole managed task memory <=1536 MiB, no swap, <=32 tasks,
one MPI rank and one numerical thread per library. Setup space <=20,000 DOFs;
actual receipt must still equal 402. Report cap 2 MB.

Acceptance requires all 76 actual scalars/receipts, both-degree exact and pair
gates, measured geometry, expected versions/source, actual worker/caller exit 0,
finite peaks within limits, zero memory.max/OOM/OOM-kill/PID-limit events, empty
cleanup and unknown_children=false. Preserve PROVISIONAL_PASS in the saved
controller result, require PASS completion/caller records, and let late or
persistence failure override an earlier status. Do not infer PASS from the
nested numerical flag or process exit alone.

Limits cover the managed worker/JIT descendants under the existing pre-existing
caller/OS-manager boundary. The resource snapshot ends before final handshake/
exit; final completion-save tails and independent parent wall time remain
unobserved. No cold-cache performance claim. R229's setup resource predicate
remains false; this admission does not reclassify that refusal.

Directory creation/reservation, partial worker start, numerical/resource failure
or uncertain process state spends the one attempt and stops. Preserve all
partial files and logs; never delete/reuse the directory or try another path.
A demonstrable caller/preflight error before reservation, managed worker or
numerical import can be repaired within the same unspent authorization only
after preserving failure/timing gaps, verifying absent directory and no new
manager task, testing the fix and publishing a clean source binding. Uncertain
state requires review and cannot justify an inferred reset.

## Next task and completion

**GPT-6 Sol / high, PC/WSL daisy: on later Continue, execute this exact allocation
once, preserve the result and all raw evidence, publish, then stop.** Follow the
[single handoff task](../../SESSION_HANDOFF.md#next-task) for launch order and
completion criteria. Return to Astra/high for interpreting the numerical result
or any change to scientific/resource gates. [Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-sol)
was searched/opened and confirms high support; task fit is judgment. No agent
model/session switch or new chat was performed.

Changed: new R251 admission, finite caller, allocation/source/artifact inventories,
caller checks/results and audit/checks; seven current index/status pages and
request/lifecycle/handoff. Checks: six caller tests, unchanged-source R250 audit
and saved R246 replay, 60 raw originals/five retained reservations with absent
recorded PIDs/cgroups, eleven artifacts/four resolutions/archive/interpreter,
AST/JSON/local links, append-only records and whitespace. Skipped: rerunning
93 unchanged-source regressions, real UFL/FEM/JIT/assembly/solve, manager/worker,
reservation, installs/full rescan, full numerical suite/tank/B2, physical/render
and Mac transfer. Unresolved: actual zero-form/runtime/resource behavior,
convergence, historical R242 discrepancy cause, rank and artifact-label origin.
PC retains ownership; Mac remains released. Completion prepared for publication;
delivery commit/result belongs in Git/final response. Next prompt: **Continue**.
