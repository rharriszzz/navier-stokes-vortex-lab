# R249 — Rotation integration contract and admission prerequisites

2026-09-26, PC/WSL daisy. Base `3bd7d4a`; STARTED `06c7296`.
**The integration contract is ready for source implementation. Execution is
not admitted.** This review changes no runtime source and grants zero attempts.
All five old allocations remain spent; R246 Poiseuille remains PASS and R242
remains INCOMPLETE. PC retains ownership; Mac remains released.

## Review findings and evidence

The [R248 source](../../verification/nonlinear_port/rotation_oracle.py) matches
[R247's exact contract](VERIFICATION_MILESTONE_R247.md):
`u=(-Y,X,0)`, quadratic `p=(X²+Y²-1/6)/2`, conservative convection,
**positive** pressure gradient, `tau=2 mu sym(grad(u))`, full stress `tau-pI`,
local squared momentum residual and all six tagged faces. It does not
interpolate pressure into P1. The 38 scalar inventory, two degrees, independent
rational targets, squared-zero limits and pair gate agree with the proposal.
The reducer rechecks strict native JSON types, raw values and every cached
numerical decision. Its accepted flag remains numerical-only.

The [R249 audit](evidence/r249/audit.py) and [output](evidence/r249/audit.json)
reproduce the R247 rational/saved-data audit, revalidate the R246 worker report,
verify 60 original raw files and all 31 R248 source/test/pin hashes, and confirm
five retained reservations with recorded PIDs/cgroups absent. No numerical
modules were loaded. The R248 **85 passing stdlib tests are reused, not rerun**;
all their source bindings are unchanged. Fake expression strings establish
wiring only, not UFL semantics, JIT, assembly or actual resource cost.

A concrete zero-form risk was identified by reading, without importing, the
installed `dolfinx/fem/forms.py`; its hash is in the audit. Its `ZeroBaseForm`
branch requires at least one argument space to obtain a mesh. A scalar has no
argument space. The corresponding [published source](https://docs.fenicsproject.org/dolfinx/v0.10.0.post0/python/_modules/dolfinx/fem/forms.html)
and [form/assembly API](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/generated/dolfinx.fem.html)
were checked. This supports a **conditional failure risk**, not a claim that
our derivative forms actually reduce to that object. Normal domain-bound UFL
Forms may compile to zero kernels successfully. No real library path ran here.

The oracle tests its explicit diagnostic/assembly path. Rotation has D=0,
so it cannot validate the viscosity coefficient or exclude a hard-coded zero
stress by numerical output alone. R247's omitted-pressure residual 1/6,
reversed-sign residual 2/3, nonsymmetric-stress norm 1/50, six-face traction
norm 1/25 and erroneous dissipation 1/5 remain independent negative controls.
No production weak-form verification, PDE solve, pressure approximation rate,
inf-sup result, tank accuracy or physical control follows from this oracle.

## Fixed implementation architecture

Keep the current Poiseuille public API, manifest, schema 2, diagnostic policy,
Newton/compatibility/flux/backflow/CSR checks and worker path intact. Do not
change `manifest.validate()` to accept rotation by changing its fixture label.
Do not pass an assembly report through `validate_worker_result()`.

Implement these bounded additions under `verification/nonlinear_port/`:

| Component | Required behavior |
|---|---|
| `rotation_manifest.py`, `future_rotation.json` | Separate strict source-native proposal validator and JSON manifest, fixed below; never an admission |
| `rotation_driver.py` | Injected mesh/form/assembly driver, pure envelope validator and strict JSON reader/writer helpers; no external imports at module scope |
| `rotation_worker.py` | Separate held entry point; requires exactly a reserved directory and rotation manifest; imports numerical modules only after verified release |
| `supervision.py` | Add `supervise_rotation_once`; extract the existing finite lifecycle into a private helper shared with unchanged public `supervise_once` |
| `systemd_backend.py` | Derive a finite allowlisted unit prefix from reserved fixture (`navier-rotation-` or existing `navier-poiseuille-`); preserve containment/expiry/cleanup behavior |
| Focused tests | Manifest/envelope, driver wiring, worker held ordering, shared lifecycle and fixture isolation using injected fakes only |

Each public supervisor wrapper validates its own manifest and admission before
reservation, then supplies a **literal** worker module name and its matching
report validator to the private lifecycle. Unknown fixtures/modes refuse.
There is no module path, callback or import string accepted from JSON. Existing
`supervise_once` remains Poiseuille-only; `supervise_rotation_once` remains
rotation-only. A rotation admission/report cannot enter the old path and a
Poiseuille admission/report cannot enter the new one. Preserve original
Poiseuille fixture field values and saved report semantics during extraction.

Reuse `worker.load_pinned_modules()` from the new worker (the import of
`worker.py` itself is stdlib-only). Retain all existing version/artifact gates
and serial rank checks even though no KSP solve occurs. Do not refactor the
loader or weaken its package identity rules in this task. Reuse handshake,
source binding and backend; no new monitor/client process or generic CLI.
No executable admission caller is added until separate admission review.

### Mesh choice and geometry receipt

Reuse the existing injected `create_cube(..., 2, 'rotation')` unchanged. This
creates an unused P2/P1 space, which is a bounded and disclosed setup cost.
It avoids changing the previously executed mesh/tag adapter during this step.
Never call `interpolate_state`, `step_forms`, a PDE solver or `LatestSystem`.
The unused space does not represent the oracle pressure or define its results.

The driver must measure and the controller must validate this exact geometry
receipt (strict integer types, booleans only for the last field):

```json
{
  "subdivisions": 2,
  "cell_type": "tetrahedron",
  "topological_dimension": 3,
  "geometric_dimension": 3,
  "cells": 48,
  "vertices": 27,
  "exterior_facets": 48,
  "facet_counts": {"1": 8, "2": 8, "3": 8, "4": 8, "5": 8, "6": 8},
  "mixed_space_dofs": 402,
  "mixed_space_ghosts": 0,
  "space_used_for_field_representation": false
}
```

These are the fixed n=2 uniform tetrahedral-cube counts, not measurements from
a new run. Obtain them from actual mesh topology, exterior inventory, MeshTags
and space map; never emit this template as the measurement. Existing
`merge_tags` must still establish six nonempty disjoint groups whose union is
the exterior boundary. The 38 assembled targets independently check unit
volume, face areas and outward normals. Retain the 20,000 setup-space DOF cap;
402 is the fixture-specific expected value. No global bordered-system DOFs
or matrix are created. If the API cannot supply the receipt, refuse.

### Exact proposal and binding

The new manifest has exactly these top-level keys:
`schema`, `kind`, `fixture`, `mode`, `execution_admitted`, `attempts_granted`,
`proposed_attempts`, `contract`, `versions`, `proposed_caps`, `report_bytes_max`.
Freeze schema 1, kind `rotation_assembly`, fixture `rotation`, mode
`exact_field_assembly`, execution_admitted false, attempts_granted 0,
proposed_attempts 1, report_bytes_max 2000000. `contract` is the exact R248
`contract_record()`; `versions` exactly copies the existing manifest's nine
pins. `proposed_caps` exactly copies `supervision.CAPS` (including the unused
setup-space cap). Use type-sensitive canonical JSON equality; booleans cannot
stand for integers. Reject missing/extra keys and duplicate JSON object keys.

Contract digest = SHA256 of UTF-8 `json.dumps(contract, sort_keys=True,
separators=(',', ':'), allow_nan=False)`. The audit records this digest.
Manifest digest hashes the actual file bytes. Do not use R244's Poiseuille
policy hash for rotation. Separate future admission must bind approved true,
fixture/mode/kind, worker envelope schema 1, attempts 1, a fixed fresh absolute
run directory, exact launch commit, manifest digest, contract digest, resolved
interpreter/hash and artifact inventory digest. Reservation carries the same
binding plus existing owner, nonce, UTC/monotonic start and caps. Enforce exact
types and cross-record equality in both supervisor and worker. The source
binding receipt must match independently computed expected binding; neither
worker nor controller trusts a self-declared report source hash.

The source manifest remains a proposal even after an admission is separately
issued. Old manifests, callers, policy hashes and historical receipts stay
unchanged. No allocation directory is named or created by this review.

## Worker assembly and report contract

Before `held()`, validate the proposal, admission/reservation matching,
interpreter, source and actual cgroup. No numerical imports, mesh or JIT before
held release. After release, retain thread environment checks, invoke the
pinned loader, and run one n=2 rotation driver. Use the existing serial
communicator; `assemble_scalar` is local, so rank=1 is mandatory.

For each degree 24 then 26, construct the actual 38 forms from
`rotation_forms`. Require an ordinary UFL Form with zero arguments, the actual
mesh domain and the expected tagged measures. Call `fem.form` then
`fem.assemble_scalar` for **every** key, including expected zeros. Require a
compiled rank-zero form and a finite real scalar; convert the numerical scalar
to native float only after checking its real scalar type (reject booleans,
complex values, arrays and nonfinite values). Never populate raw values from
rational targets, clip negative norms, catch assembly exceptions as zero, or
substitute a symbolic zero shortcut. A `ZeroBaseForm`, missing domain, wrong
rank or compilation failure refuses this attempt with the degree/key/stage in
the error evidence. No retry with modified forms or relaxed gates.

Preserve per-degree, per-key assembly receipts with exactly `method`,
`ufl_integrals`, `compiled_rank`: method `fem.form+assemble_scalar`, positive
integer original UFL integral count, compiled_rank integer 0. Zero compiled
kernel counts are allowed; original Forms must still have domain-bound
integrals. These receipts establish routing under source binding, not an
independent proof of assembly. All 76 calls must finish before a complete
numerical report can be accepted. Record a concise progress/error log during
execution so a refusal identifies the failing key without inventing raw data.

The worker envelope has **exactly** these keys:

```text
worker_schema, kind, fixture, mode, manifest_sha256, contract_sha256,
source_binding, geometry, oracle, assembly_receipts, phase_seconds,
worker_intervals, actual_versions, ffcx_artifact
```

Schema 1, kind/fixture/mode as above; `oracle` is the complete strict R248
schema-1 report. There is no outer numerical PASS flag. `assembly_receipts`
has string degree keys 24/26 and exactly the 38 scalar keys at each degree.
`phase_seconds` has exactly `mesh_and_tags`, `degree24_form_jit_assembly`,
`degree26_form_jit_assembly`, `report_reduction`; `worker_intervals` has exactly
`import_seconds`, `fixture_setup_jit_and_assembly_seconds`. All times are finite
native nonnegative real values, not booleans. Report the actual versions and
FFCx artifact with existing `validate_versions` rules. No fabricated Newton,
flux, backflow, multiplier, CSR or constraint-condition fields.

The controller checks exact envelope/types/binding/geometry/receipts/timings,
recomputes `validate_report(oracle, manifest['contract'])` from all raw values,
and validates versions/artifact. Missing/extra/corrupt cached fields refuse.
Apply the 2,000,000-byte limit to **actual serialized envelope bytes**, including
indentation and metadata, before exclusive creation/fsync and before reading;
the nested reducer's compact size check is insufficient. The rotation JSON
reader rejects duplicate keys, trailing data and nonstandard NaN/Infinity.
Persist the complete assembled report even if its numerical gates fail; let
the controller reject it. An exception before a complete report leaves the
partial log and spent reservation, never a synthetic complete report.

## Lifecycle and later admission

The shared lifecycle must preserve exclusive reservation, held facts/source
verification before release, actual worker exit, resource snapshot, group stop,
empty cleanup and finite persistence timing. Include partial-start cleanup
through `backend.active_handle`. Save failure evidence without resetting the
reservation. Numerical acceptance alone cannot set workload PASS.

Retain the frozen 180-second outer total, setup/work/finish 15/150/15 seconds,
149-second independent worker runtime plus 1-second stop grace, 1536 MiB whole
managed task memory, zero swap, 32 tasks, one MPI rank and one numerical thread.
All newly spawned task workers/JIT children remain in the managed cgroup.
The existing caller and OS manager boundary remains as disclosed in R103;
these limits do not retrospectively measure their entire RSS. Require zero
memory.max/OOM/OOM-kill and PID-limit events, finite peak values within caps,
worker/caller zero exits, no unknown children and empty manager/cgroup cleanup.
Retain result PROVISIONAL_PASS, completion/caller/late-marker precedence and
exclusive fsync persistence. Final save tails and resource snapshot ending
before final handshake/exit remain explicitly unobserved; do not upgrade them
to full wall-time or peak-memory proof. No cold-cache timing claim.

**Admission prerequisites after source implementation:** Astra/high reviews
actual diffs and source-only checks below; fixes the fresh directory and
finite caller; freezes the newly published source inventory (including all
integration files), manifest/contract/envelope, caller, interpreter and artifact
hashes. Recheck live host capacity and unchanged manager/cgroup capability at
launch. Preserve the narrow FFCx package/runtime exception and prior artifact
label limitations. Bind the existing reviewed runtime/library inventory or
refresh read-only artifact evidence if it drifted; do not infer artifact
identity from a version string. Include inspected DOLFINx `forms.py` in the
new artifact inventory. No installs or artifact substitution by inference.

A separately admitted **one-use** real run is the first place allowed to
establish actual zero/nonzero assembly, 76 raw scalars, both-degree exact and
pair gates, geometry receipts, version/binding, timing/resource and exit/cleanup
evidence. That evidence is required to accept a runtime result; it is not a
circular demand to execute before admission. Admission may approve measuring
the disclosed API risk, or withhold execution if source review reveals a new
blocker. Source-only tests cannot certify resource sufficiency or JIT success.

A recoverable caller error must demonstrably precede directory reservation,
managed worker start and numerical imports. Preserve its evidence, verify
absence of the fixed run directory and any new task in the manager, fix/test
it and publish a clean source binding before continuing the same allocation.
Directory creation/reservation, partial worker start, numerical/resource failure
or uncertain process state triggers the one-attempt stop rule. Stop and
preserve evidence; never delete/reuse the directory or infer a budget reset.
All five historical allowances remain spent irrespective of this review.

## Required checks and next task

Implement the additions and focused stdlib/fake tests together. Completion
requires the following, followed by publication and a stop for Astra/high:

1. Exact proposal/envelope/digest binding, malformed types, duplicate JSON keys,
   cross-fixture admissions/reports, changed source/interpreter/schema/contracts
   and wrong versions refuse before launch or acceptance as applicable.
2. Injected driver proves n=2 rotation dispatch, unused setup space, measured
   tag/mesh receipt, both degrees and all 76 assembly calls. Fakes that raise
   on solver/interpolation/CSR use must remain untouched. Exercise exact
   zero returning through assembly and reject domainless/ZeroBaseForm/wrong-rank
   inputs, skipped faces, nonfinite/complex/array scalars and JIT errors.
3. Controller recomputes saved raw data: common-mode/one-degree wrong targets,
   cached acceptance corruption, geometry/receipts/binding omissions and
   envelope byte-limit/partial-write failures cannot pass. Preserve rejection
   of a negative squared value; no roundoff clamping.
4. Worker fakes prove no import/mesh before release, wrong nonce/cgroup/thread
   refusal, version checks after release and complete report before finished
   handshake. All source/test imports remain free of numerical packages.
5. Shared lifecycle fakes cover partial start, no release on bad limits/source,
   timeout, nonzero exit, missing counters, memory/PID events, unknown cleanup,
   report corruption, save failure and late completion. Existing Poiseuille
   tests and R246 saved-report replay must still pass. Do not rewrite historical
   evidence or rerun any old caller. Run the complete stdlib regression suite
   once after integration, with import audit, plus AST/JSON/link/whitespace checks.

**Next: GPT-6 Sol / high on PC/WSL implements this fixed contract only.**
The model's high support was checked in [official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-sol);
task fit is judgment. No model switch occurred. Return to Astra/high for
source/admission review once implementation and checks are complete, or earlier
if implementation requires changing scientific gates, the zero-form rule,
containment or the report contract. No FEM import/JIT/assembly/solve, manager
connection, numerical reservation, real caller, full suite/tank/B2, physical
rendering or Mac transfer during implementation. Next prompt: **Continue**.
