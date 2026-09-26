# R244 — Explicit Poiseuille policy and both-degree physical validation

2026-09-26, PC/WSL daisy. Base `b8327da`, STARTED `32b444a`.
**Implemented and tested; no new numerical admission or execution.**
All four allocations remain spent 1/1. R242 remains INCOMPLETE under its
original contract. [R243](POISEUILLE_QUADRATURE_REVIEW_R243.md) gives the
scientific rationale, alternatives and uncertainty behind this deliberate
prospective accuracy-policy change.

## Implemented method and scope

[poiseuille_policy.py](../../verification/nonlinear_port/poiseuille_policy.py)
defines `poiseuille_signed_accuracy_v1`, policy schema 1. It has a complete
30-key inventory and the reviewed 17-key signed subset. Those signed keys use
`max(1e-8*max(1e-10,abs(q24)),1e-14)`; the other 13 keep the old rule. In
particular, squared errors, identity dissipation, viscous dissipation,
geometric measures, inventories and absolute boundary flux are not widened.
All raw values must be finite native numbers; nonnegative quantities refuse
negative values. Unknown or missing quantities refuse on either side.

The policy is stored explicitly in the non-executable
[manifest](../../verification/nonlinear_port/future_fem.json). Validation
compares the complete canonical policy record, including version, keys,
thresholds, nondimensional context, affine unit-cube domain, rho=1, mu=0.1,
n=2, step 1, dt=0.125 and degrees 24/26. Manifest context additionally binds
rho/mu/domain/dt/one step, the n=2 oracle and 1e-8 relative value. Missing or
changed policy/context refuses. The driver remains the fixed Poiseuille
one-step route; other fixture names cannot select this policy through the
one-fixture controller. General manufactured/rotation execution is not added.

The original general `diagnostics.quadrature_comparison` is unchanged,
including its zero-to-1e-15 refusal. This new absolute target is an accuracy
budget, not a measured roundoff bound. No new threshold was fitted during
implementation. R243's assumptions and limitations still apply.

## Worker/controller report contract

`evaluate_poiseuille_pair` in
[fixture_driver.py](../../verification/nonlinear_port/fixture_driver.py)
rebuilds a field report, step checks, exact-error checks and physical endpoint
budgets separately for degrees 24 and 26. Both must pass. The expected
Poiseuille cap pressure means and fluxes are zero, as already used by the
controller and exact oracle; no new boundary condition is introduced.

The serialized numerical report now requires:

- `numerical_schema: 2`, an explicit exact `diagnostic_policy` record and
  `backflow_sampling_degree: 24`;
- `degree_validation` containing field report, step checks, endpoint budgets,
  checks and numerical acceptance for both `24` and `26`;
- the familiar degree-24 aliases and raw `diagnostics_degree26`, retained for
  readability; every duplicate is checked on read;
- aggregate checks formed by conjunction over both degrees.

The controller obtains its expected policy from the validated manifest,
requires the report schema/policy and recomputes the entire result from raw
scalar values through the shared deterministic helper. Missing evidence,
changed cached decisions or a failure at either degree refuses acceptance.
This is recomputation, not an independent second implementation of the physics.

Backflow uses the actual degree-24 sample minimum/counts, as before. The
physical evaluations share it; no degree-26 sampling claim is made. The
2,000,000-byte report cap, sparse solver settings, true-residual checks,
Newton/compatibility/Gram gates, physical thresholds, resource limits and
dependency pins are unchanged. No extra assembly or solve was introduced:
the driver already assembled both scalar inventories; the new work reduces
and validates those saved values.

## Tests and saved-data replay

**77 standard-library tests pass**, no numerical modules loaded. Focused
policy/driver/controller/package tests: 26 pass. See
[tests](evidence/r244/tests.json) and [test output](evidence/r244/tests.txt).
New controls cover:

- legacy rejection and prospective small/too-large signed changes;
- untouched squared-error and nonnegative-dissipation limits;
- nonzero relative-error failure; missing/unknown/nonfinite/boolean/negative
  raw values; missing/altered policy and physical context;
- identical wrong values that pass the pair comparison but fail physical
  constraints or exact-error checks;
- a degree-26-only pressure-mean failure while the pair comparison passes,
  through both controller validation and real driver wiring with fake FEM;
- missing schema/degree reports, wrong sampling-degree claims and altered
  caches, including physical-budget and field values;
- explicit saved-data replay, byte cap and preservation of original bytes.

[Saved replay](evidence/r244/saved_replay.json) records the separation:
R242's original comparator still has 12 failures. Its original report lacks
the new schema/policy and is rejected by the current controller. An explicitly
constructed prospective report from the same saved raw values passes both
degrees and controller validation; its pretty JSON size is **34,928 bytes**.
This is a source test of future behavior, not an admitted run or retrospective
PASS. The R242 report and all prior evidence are unchanged.

[Checks/source inventory](evidence/r244/checks.json) bind 29 code/test/pin
files. Seven old entries changed (driver, manifest JSON/validator, supervision,
driver supervision/wiring tests and package-identity test calls); the policy
module/test are new. All 45 retained raw files match the four original run
directories; reservations persist and recorded worker PIDs/cgroups are absent.
Historical caller/source hashes are intentionally invalidated by the source
change. Historical audits remain records for their original source commits;
do not alter their bindings or run their old numerical callers.

## Admission recommendation and stop

**Recommend a separate Astra/high admission review for one NEW later n=2
fixture**, because the prospective source contract and negative controls are
now concrete. This recommendation grants no allocation. That review should:

1. Review the exact method/schema diff and these tests; verify the new 29-file
   source inventory and manifest digest. Retain all spent allocations.
2. Recheck the exact R229 interpreter and R241 PETSc/SuperLU artifact bindings,
   preserving the accepted package/embedded-version discrepancy and R229's
   false setup resource predicate. Do not reinstall or infer capability from
   metadata. No standalone numerical imports/prewarming.
3. If justified, prepare a separately named, exclusive one-use directory and
   finite caller with the new source/manifest/policy binding. Freeze the same
   180-second total, 15/150/15 phase budgets, independent expiry, 1536 MiB,
   no swap, 32 tasks, one rank/thread and latest-system evidence bounds.
   Keep all numerical/physical gates except the explicit R244 policy change.
4. Test preflight/refusal paths without reservation or manager workload,
   publish admission or precise blocker, and stop before execution. Any later
   Continue execution must still publish its clean STARTED binding first.

Retain Astra/high for the scientific/admission decision. Only after a concrete
admission/caller is frozen should routine execution be handed to Sol/high with
one-attempt stopping rules. [Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-astra)
was searched/opened for high support; task fit is judgment, no switch occurred.

Skipped: live FEM/import/JIT/assembly/solve, rank/alternative factorization,
manager scope, artifact rescan/install, full suite/rotation/tank/B2,
physical/render and Mac transfer. Future target attainability and the cause
of R242 discrepancies remain unverified; actual rank/permutation and the
artifact-label origin remain unknown. PC retains ownership; Mac released.
Follow the [single next task](../../SESSION_HANDOFF.md#next-task).
