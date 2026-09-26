# R247 — Fixed-oracle review and next verification milestone

2026-09-26, PC/WSL daisy. Base `3076956`; STARTED `349dee7`.
**Select the existing rigid-rotation exact-field assembly oracle as the next
verification milestone. Implement its source and tests next; no execution or
new allocation is admitted here.** All five allocations remain spent.
[R246](POISEUILLE_RESULT_R246.md) remains PASS under its frozen contract;
R242 remains INCOMPLETE under its different original contract.

## What the passing run establishes

The [standard-library audit](evidence/r247/audit.py) replays the actual R246
schema-2 report through its controller validator. It passes. Sixty raw files
from all five runs match retained hashes and original bytes; reservations
persist, recorded PIDs/cgroups are absent, and all 29 source/test/pin hashes
match R245. [Audit output](evidence/r247/audit.json) retains these checks.

R246 demonstrates a complete held-worker/import/mesh/assembly/SuperLU/Newton/
diagnostic/persistence/exit/cleanup path for one exactly representable steady
Poiseuille solution on the n=2 cube. Its non-exact initial guess required three
verified corrections. Both-degree physical checks and all 30 comparisons pass.
The measured three-row Gram screen is not full-matrix rank or an inf-sup proof.

The R242 and R246 raw scalar inventories at both degrees are identical. The
new report is accepted under the prospective R244 policy and explicit schema;
this does not repair or reclassify the earlier run. The observation neither
proves roundoff was the only source of the earlier differences nor establishes
an error bound. R244's common-mode-error controls remain necessary: the
controller and worker share a deterministic physical-report implementation.

Resource evidence still ends before final handshake/exit; final save tails and
independent parent wall time were not measured. R246's 2.898 s caller interval
is not a cold-cache benchmark. R229's earlier setup resource predicate remains
false. Exact FFCx and SuperLU package/embedded-label exceptions remain separate
from loaded-file proof or broader environment certification.

## Why rotation is the smallest useful next milestone

[R195](NONLINEAR_VERIFICATION_R195.md) already specifies rotation as a
constitutive and centrifugal-balance assembly oracle, distinct from a PDE
pressure-exactness test. [R196](CUBE_ADAPTER_R196.md) retains that distinction.
The exact polynomial and algebra test exist. No rotation assembly driver or
report validator exists, and `step_forms` expressly refuses rotation solves.

| Candidate | Added evidence | Remaining prerequisites / decision |
|---|---|---|
| Repeat Poiseuille | Repeatability for the same case | No fresh allowance; does not address the next missing mechanism |
| Rotation exact-field assembly | Symmetric strain/stress, nonzero convection and pressure-gradient cancellation, face integration | Small injected form builder plus strict independent-target reducer; selected |
| Manufactured spatial sequence | Non-affine approximation and mesh rates | General driver, exact-history/discrete-forcing diagnostics, nonzero return targets/multipliers, fixture-specific acceptance and resource evidence |
| Affine temporal sequence | BE startup/BDF2 history and rates | Complete accepted-history loop, changing traces, physical endpoint/integrated budgets and time-series persistence |
| Tank/boundary response | Physical base flow and response observables | Solver verification, mesh/time convergence, geometry/actuator/sensor decisions and separate admission |

Rotation adds a mechanism the Poiseuille test cannot distinguish: rigid spin
has nonzero velocity gradient but exactly zero symmetric strain. The chosen
assembly oracle does not validate the production weak-form operator by itself.
It verifies its explicit diagnostic/form path and external assembly conventions.
No solver, boundary-condition or physical actuation choice is changed.
Because D=0, rotation alone cannot distinguish an incorrect scalar coefficient
multiplying D or a hard-coded zero viscous stress. The builder must actually
form the derivatives; the nonzero-strain response remains a separate test.

## Exact mathematical contract

Use dimensionless [0,1]^3, rho=1, mu=0.1, n=2 affine tetrahedra, degrees 24/26.
Put X=x-1/2 and Y=y-1/2:

```text
u=(-Y,X,0), p=(X^2+Y^2-1/6)/2
G=grad(u)=[[0,-1,0],[1,0,0],[0,0,0]]
D=(G+G^T)/2=0, tau=2 mu D=0, sigma=-p I+tau
c=div(u tensor u)=(-X,-Y,0), grad(p)=(X,Y,0)
r=c+grad(p)-div(tau)=0, f=0, div(u)=0
```

Use exact coordinate expressions for both fields, **not P1-interpolated
pressure**. Pressure is quadratic. No solve, time advance, multipliers, eta,
Newton correction or CSR record is part of this assembly oracle.
The prescribed n=2 mesh checks assembly; it does not turn exact expressions
into a discretization-error experiment. No backflow gate is inferred from this
oracle: its z-return velocity is identically zero.

The [UFL form-language manual](https://docs.fenicsproject.org/ufl/2025.2.0.post0/manual/form_language.html)
confirms that vector `grad(u)[i,j]` differentiates component i with respect to
coordinate j, tensor divergence contracts the last axis, and `ds` is exterior
facet integration. This is API convention evidence, not validation of our
forms or runtime. The unqualified 2025.2.0 manual URL failed; the published
2025.2.0.post0 manual was retrieved. Installed UFL pin remains 2025.2.1.

The rational audit derives the following constants and compares them with
separately written closed values (exact integration, no FEM):

| Integral over unit cube unless marked boundary | Exact value |
|---|---:|
| volume; each of six face areas | 1 |
| squared velocity L2 norm | 1/6 |
| squared gradient Frobenius L2 norm | 2 |
| pressure integral; squared pressure L2 norm | 0; 1/360 |
| squared convection L2 norm; squared pressure-gradient L2 norm | 1/6; 1/6 |
| squared strain/divergence/momentum-residual/viscous-stress L2 norms | 0 each |
| squared viscous traction L2 norm, all six faces | 0 |
| squared total traction L2 norm, all six faces | 7/180 |
| viscous dissipation, integral 2 mu D:D | 0 |

For each tag `1+2*axis+side`, additionally integrate all three normal components:
component `axis` is `2*side-1`, the others zero. This gives 38 exact scalar keys,
including volume, six areas and 18 normal integrals. Complete explicit targets
and categories are frozen in [rotation_proposal.json](evidence/r247/rotation_proposal.json).
The tag checks catch swapped opposite faces; full exterior inventory validation
still belongs to the eventual mesh adapter.

### Avoid cancellation-only acceptance

The audit proves that omitting pressure leaves all three **signed volume
momentum integrals zero**, although the squared momentum residual is 1/6.
Reversing the pressure-gradient sign gives 2/3. Therefore use an assembled
squared residual norm and separate positive convection/pressure-gradient norm
anchors, not just whole-domain signed force sums or pair agreement.

Using the wrong nonsymmetric viscous stress `mu*grad(u)` has squared volume norm
1/50 and squared boundary traction norm 1/25. Its z-cap viscous traction remains
zero, so a returns-only traction test misses it. The gradient-based dissipation
is 1/5 instead of zero. These are required algebraic/wiring negative controls.
Zeroing all fields/outputs also fails the nonzero target anchors.

### Prospective acceptance for this oracle only

This concretizes R195's existing rotation absolute tolerance 1e-10; it does
not inherit or broaden the Poiseuille signed policy or legacy comparator.
At **each** degree independently:

- Require exactly the 38 keys, finite native numbers, no booleans; squared norms,
  areas, volume and dissipation must be nonnegative. Missing/extra/nonfinite
  values refuse. No clipping a negative squared norm into a pass.
- Geometry volume/areas/normal integrals must match exact targets within 1e-12.
- The five zero norm-squared quantities named in the proposal must be <=1e-20,
  equivalent to their L2/Frobenius norms <=1e-10. Record both raw squares and
  derived norms; compare squares directly to the specified squared threshold.
- Every other scalar must match its exact target within absolute 1e-10.
- Degree-26 minus degree-24 differences must have absolute value <=1e-10 for
  every key. This pair gate supplements both-degree target checks; it cannot
  accept common-mode wrong values. This is a small fixed nondimensional oracle,
  not a reusable general convergence tolerance.

A source report uses schema 1, exact `rotation_assembly_v1` contract/context,
raw records under string keys `24` and `26`, recomputed per-degree and pair
checks, and a numerical-only accepted flag. Type-strict validation rejects
schema booleans, drifted context/policy, missing degree records and corrupted
cached decisions. No resource or overall execution PASS can be set by this
source reducer. Preserve the 2,000,000-byte report cap at later integration.

## Source implementation boundary and checks

**Next: Sol/high implements only `rotation_oracle.py` and its focused tests.**
It should expose an injected UFL form builder (domain/tag/degree inputs; no
external imports), a strict contract record/validator and pure scalar report
builder/validator. Geometry measures carry an explicit domain. Actual fields
come from `fixtures.rotation()` through coordinate evaluation; apply the
stated tensor derivatives in the form builder, rather than substituting
precomputed zero residuals or expected scalar constants as results.
Zero forms may simplify symbolically; fake tests must not claim real zero-form
JIT/assembly succeeded. That remains a later runtime check.

Tests use exact rational targets and injected fakes/recorders, with independent
constants and the negative controls above. Require common-mode wrong data,
one-degree-only failure, negative squared quantities, NaN/Inf/bools, key/schema/
context omissions, corrupted decisions and geometry-tag errors to refuse.
Exercise actual form-builder/reducer wiring sufficiently to catch omitted
pressure, gradient-versus-symmetric-gradient stress and omitted side faces.
Run the existing standard-library regression suite and import audit as well.
If the fixed contract cannot be implemented without a scientific choice,
report that blocker for Astra/high instead of silently modifying the proposal.

Leave current Poiseuille source, manifest, policy, solver, worker/controller,
caller and historical evidence untouched. No standalone FEM import, mesh/JIT/
assembly, manager connection, allocation or executable launch path in this step.
Publish implementation/checks and stop for **Astra/high integration review**.
The exact model's high support was rechecked in
[official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-sol);
fit is judgment and no model/session switch occurred.

## Later integration/admission prerequisites and roadmap

A later review must bind rotation-specific worker/controller dispatch and its
report to the proposed contract, preserving the existing Poiseuille refusal
boundary. Do not merely relabel a Poiseuille report or force it through Newton/
compatibility/CSR gates that do not apply to assembly. Preserve source/executable/
artifact identity, held release, actual effective limits, timing, persistence,
actual exit, finite saved peaks, zero limit events and empty cleanup. No generic
launcher redesign is needed. No artifact rescan/install is proposed absent drift.

Only after tested integration may a separate review grant one new exclusive
directory and clean source-bound caller. Proposed ceilings remain 180 s total,
15/150/15 phases, 149 s independent expiry plus 1 s grace, 1536 MiB/no swap,
32 tasks, one rank/thread. Runtime fit is unmeasured. Reservation/directory
creation or partial worker start spends any later allowance; refusal means
preserve/publish/stop, no retry or gate relaxation. A demonstrated pre-reservation,
pre-worker, pre-numerical caller error is recoverable only after preserved
failure, absent fixed directory/no manager task, repair/test and clean binding.
Uncertain process state stops. This review grants **zero** attempts/directories.

After a later successful rotation oracle, manufactured spatial verification
still needs its own source/report and admission. Reuse exact previous UFL
history with the discrete exact BE load; do not introduce interpolated old
swirl. Nonzero independent return totals/multipliers and manufactured body terms
must replace Poiseuille-only expectations. Diagnostics must use that discrete
force and distinct endpoint/time meanings. The Poiseuille policy is explicitly
fixture-bound. Spatial levels 2/4/8 and current rate gates remain proposals;
the 512-global-DOF latest-matrix cap would need explicit review before larger
meshes, not an implicit inheritance from the 20,000 mixed-DOF cap.

Temporal verification still needs full solved histories with current/historical
lifts, one BE startup then BDF2, continuous exact forcing for the affine-time
companion, all accepted steps, saved time series and independent physical
endpoint budgets. The existing ODE/algebra checks are not FEM time convergence.
The research roadmap requires mesh/time-converged observables before boundary
response, followed by actuator/sensor and reachability/observability review.
A unit-cube oracle does not repair the separate B1/B2 physical-pilot gates.

No new numerical work, rank/alternative-factor analysis, install, full suite,
tank/B2, physical/rendering work or Mac transfer occurred. R244's 77 tests and
R245's caller checks are reused, not rerun. The review audit itself passes with
no numerical modules loaded. Current next task is in the
[handoff](../../SESSION_HANDOFF.md#next-task). PC retains ownership; Mac released.
