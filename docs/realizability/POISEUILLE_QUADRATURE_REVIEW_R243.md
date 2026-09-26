# R243 — Quadrature refusal, cancellation and a prospective accuracy policy

2026-09-26, PC/WSL daisy. Base `332d902`, STARTED `d74a670`.
**Review completed; runtime gates/source unchanged, no new allocation.**
R242 remains INCOMPLETE and all four allocations remain spent 1/1.

## Finding and decision

There is no demonstrated comparator implementation error. The frozen rule
explicitly demands `abs(q26-q24) <= 1e-8*max(1e-10, abs(q24))` for every raw
quantity. The twelve R242 failures all use its 1e-18 near-zero limit.
[R195](NONLINEAR_VERIFICATION_R195.md), [R196](CUBE_ADAPTER_R196.md) and
[R225](POISEUILLE_REVIEW_R225.md) deliberately preserve that denominator.
`test_adapter.py` explicitly rejects a zero-to-1e-15 comparison. Changing
`relative*max(floor, abs(value))` to `max(floor, relative*abs(value))` would
change the method, not repair a typo.

**Recommend a prospective, Poiseuille-only accuracy-budget revision**, with an
explicit absolute target for a fixed set of signed diagnostics and physical
validation at both quadrature degrees. Section “Proposed policy” specifies it.
This is a review proposal for the next source/test step, not a new live gate,
permission to rerun, or retroactive acceptance of saved evidence.

The observed discrepancies are consistent with floating-point cancellation.
The available totals cannot prove rounding is the sole cause or exclude a
kernel, mapping, coefficient-evaluation or assembly defect. A reported pair
comparison is a consistency check, not an accuracy certificate.

## Source trace and reproduced evidence

The R242 handoff named `gates.py`, which does not exist in this prototype.
The applicable chain is:

1. `future_fem.json:gates` specifies relative change 1e-8; `manifest.py`
   validates the inventory/positive finite values. The comparator's 1e-10
   scale floor is a source default, distinct from the manifest's error floor.
2. `fixture_driver.py:run_poiseuille` assembles degree-24 and degree-26 scalar
   forms from the same final installed field, then calls
   `diagnostics.py:quadrature_comparison` with the relative value.
3. `numerical_decision` requires all comparison flags. It combines them with
   separate correction, exact-field, constraint and physical-budget checks.
4. `supervision.py:validate_worker_result` rebuilds the comparison, field
   report, step and endpoint checks from saved values and refuses false or
   inconsistent evidence. It does not trust the worker's acceptance flag.

The [reproducible standard-library audit](evidence/r243/audit.py) and
[output](evidence/r243/audit.json) compare all 30 quantities, reproduce the
12 failures byte-for-value in the comparison objects, and obtain the original
controller refusal. They also rebuild physical diagnostics at degree 26 under
unchanged physical thresholds: these saved-data checks pass at both degrees.
They reuse the saved degree-24 backflow minimum; no degree-26 sampling claim.
No FEM, JIT, matrix analysis, new solve or manager connection occurred.

All 27 bound source/pin files match R241. All 45 retained raw files from four
attempts match their original directories; reservations remain, recorded PIDs
and cgroups are absent. R242 source provenance remains launch commit
`8622c8af8481ec4c4c11194dbc7d41571aa38ad8`. The matrix in that record is before
correction 3, not the final field; final DOF coefficients/coordinates are not
retained, so independent final-field reintegration cannot be inferred.

## What cancellation does and does not explain

An independent rational integration of the exact oracle gives:

| Quantity | Exact total | Sum of absolute face integrals |
|---|---:|---:|
| angular advection | 0 | 8/15 |
| angular traction | 0 | 14/15 |
| energy advection | 0 | 16/35 |
| total boundary flux | 0 | 4/3 |
| energy traction | -8/15 | 8/15 |

For example, angular traction's four nonzero face contributions are
1/5, 1/5, 1/15 and -7/15. Thus a zero total does not imply small operands.
These are exact-oracle face integrals, not measured absolute quadrature
summands for the numerical field; the latter are unavailable.

For recursively summing exact floating-point inputs, the standard bound is
`gamma_(n-1)*sum(abs(x_i))`, with `gamma_m=m*u/(1-m*u)` and unit roundoff
`u=2^-53` in binary64. Relative conditioning worsens when the signed total
cancels. This addresses summation, not errors already present in integrands,
weights, geometry or basis evaluation. [Higham, 1993, §2](https://nhigham.com/wp-content/uploads/2023/10/high93s.pdf).

The audit's binary-exact toy `[1, 2^-54, -1]` sums to zero by explicit recursive
addition and to 2^-54 with another ordering; the original comparator rejects
the difference. No FEM claim follows. The initial audit used Python 3.12's
improved `sum`, which did not exhibit that loss; its assertion failed and was
corrected to explicit recursive additions. Final audit passes; this was a
source-review script issue, with no reservation or worker.

Pressure mean and lateral flux have signed spatial cancellation. Storage and
energy-identity expressions subtract nearly equal steady quantities. Error
integrals and divergence work can also inherit basis/derivative cancellation.
The nonlinear field error, form evaluation and reduction errors are combined
in the saved numbers; their separate contributions are not recoverable.

For an affine P2 velocity/P1 pressure Poiseuille field, all the polynomial
scalar forms have spatial degree at most six: energy advection is degree six,
conservative-divergence work at most five, angular advection at most five,
and squared velocity errors at most four. Degree 24 already exceeds these
polynomial requirements. Basix defines degree by the polynomial exactness
requirement; this is not floating-point exactness. [Basix 0.10 documentation](https://docs.fenicsproject.org/basix/v0.10.0.post0/python/_autosummary/basix.quadrature.html).
`boundary_absolute_flux` is an exception: absolute value of a general P2
normal velocity is piecewise polynomial with possible internal sign changes.
Its comparison remains necessary and unchanged. No extrapolation to the
higher-degree manufactured fixture, curved geometry or another mesh is made.

Increasing quadrature degree is therefore not an established remedy for these
failures. Compensated reductions and factored storage expressions can reduce
some rounding, but cannot recover upstream integrand errors or guarantee
1e-18 agreement. Requiring tiny scalar totals to be relatively accurate does
not by itself establish physical accuracy either.

## Proposed policy (not installed)

Scope: this nondimensional n=2, affine unit-cube, rho=1, mu=0.1, dt=0.125,
one-step Poiseuille oracle only. Preserve the old rule for the general
comparator and all other fixtures until separately reviewed.

For each of the **17 explicit signed keys** listed in `audit.json`, propose

```text
old_limit_k = 1e-8 * max(1e-10, abs(q24_k))
limit_k     = max(old_limit_k, 1e-14)
```

The keys are all four `angular.*` terms; six `energy.*` terms excluding
`energy.dissipation`; `energy_identity_storage`, `kinetic_discrete_derivative`,
`lateral_flux`, `flux_0`, `flux_1`, `pressure_mean`, `p_error_integral`.
The other 13 keys retain the old limit. No symmetry change to the original
relative term is bundled into this proposal.

**Why 1e-14:** allocate one percent of the tightest applicable signed linear
absolute diagnostic gate, the 1e-12 energy-identity floor, per affected scalar.
This is an engineering accuracy target tied to existing checks, not a rounding
bound or a constant fitted to the largest observed difference. The added floor
allows at most 3e-14 (3%) across three identity terms (the nonnegative term is
actually not widened), at most 7e-14 (0.07%) across seven energy-budget terms,
and 4e-14 (0.04%) across angular terms relative to their 1e-10 budget floors.
Individual flux/pressure-mean comparisons have a 1e-4 fraction of their
1e-10 constraint gate. These bounds describe the new absolute allowance only;
the existing relative term can dominate at larger magnitudes. They do not
bound common-mode error, and do not replace either degree's physical checks.

Quantities already use the fixture's nondimensional units. Pressure-volume,
volume-flow, angular-momentum-rate and power terms have different dimensional
units; the same numeric target is not a universal SI tolerance. A dimensional
or rescaled problem must supply its own reference scales and renewed review.

Squared L2/H1/divergence/traction errors and nonnegative identity dissipation
are **not widened**. A universal 1e-14 floor would hide a squared-error change
of 1e-16, corresponding to a 1e-8 norm, already above the 1e-9 oracle gate.
The audit includes this counterexample. Positive viscous dissipation, geometry,
inventories and absolute boundary flux also keep their original comparison.

Require the same field, constraint, energy identity, exact-error and endpoint
checks separately on both degrees, with finite complete inventories and their
original physical thresholds. Identical wrong answers pass any pair comparison:
a common pressure-mean error 1e-6 passes the candidate comparison but is rejected
by the real constraint check. Preserve this independent protection. Backflow
continues to use the explicitly reported degree-24 sampling unless separately
changed; this review does not add a new point-sampling requirement.

On R242's saved scalars, the candidate has zero pair disagreements, and both
physical replays pass. This sensitivity result is labelled proposal-only.
It does not satisfy the original allocation, prove a rounding bound, or
establish an accepted solver. If a future admitted run misses this target,
preserve its refusal; do not enlarge the target to match it.

### Alternatives considered

- Keep 1e-18 and improve reductions: legitimate for a separate high-accuracy
  study, but no evidence that all form-evaluation paths can attain it here.
- Raise all absolute limits to 1e-10: rejected; mixes squared/unsquared accuracy
  and can conceal errors material to the exact oracle.
- Use epsilon times absolute quadrature summands: useful for a conditional
  reduction-error estimate, but summands/evaluation bounds are not saved.
  Do not manufacture a certified bound from global totals.
- Remove zero-valued quantities or call R242 a PASS: rejected; loses diagnostics
  and violates the original acceptance contract.

## Next implementation and stopping criteria

**Astra/high** should implement and test this prospective Poiseuille-only policy,
with an explicit versioned policy record and strict quantity inventory, while
preserving legacy behavior. Document the deliberate scientific change. Keep
historical admissions/callers and R242 raw data unchanged; old source bindings
will correctly fail after a future runtime change. No new allocation yet.

Required checks: original comparator still rejects zero-to-1e-15; candidate
signed 1e-15 accepts and 2e-14 rejects; squared-error/identity-dissipation
1e-16 rejects; nonzero relative error rejects; common-mode errors fail physical
gates; unknown/missing/nonfinite/negative squared values refuse; corrupted
cached flags and degree-26-only bad physical data refuse in the controller;
real driver wiring carries both-degree decisions. Reuse the existing test
suite and audit numerical imports. Preserve bounds and evidence size limits.
Review an explicit report schema so absence of the new policy cannot select it
implicitly. Do not import the review script into runtime code.

Completion: source/tests and a precise future admission recommendation or
blocker, then stop before numerical admission/execution. Keep Astra/high for
scientific adoption; recommend Sol/high only after the remaining work is
mechanical with frozen checks. [Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-astra)
was searched/opened for high support; model fit is judgment, no switch occurred.

R243 changed only review/evidence and status/handoff records. The existing 69
runtime tests were reused, not rerun; runtime source hashes are unchanged.
Audit checks include original refusal, exact face algebra, synthetic controls,
both-degree saved physical replay, 45 original hashes and four spent states.
No numerical imports, manager scope, rank/alternative factorization, install,
full suite/rotation/tank/B2, physical/render or Mac work. R229 setup refusal and
artifact-label discrepancy remain. Follow the [single next task](../../SESSION_HANDOFF.md#next-task).
