# B2 continuation: independent swirl reference and stability checks

R023 resource-policy update: the user permits using the PC within its
capabilities. The [current handoff](../../SESSION_HANDOFF.md#r023-resource-clarification)
sets a capacity-based allowance for each run. At R033 launch, WSL had about
6.9 GiB available and Windows about 2.66 GiB; the child-tree cap was therefore
reduced to 1536 MiB, with a 600 s cumulative limit. A fresh prelaunch check for
the final pass showed 6.29 GiB available in Windows and 6.77 GiB in WSL.
R024 adds a Windows-host headroom check alongside the WSL availability check;
the two readings must not be added as if they were separate physical RAM.
Capacity-sized limits supersede the earlier 60 s/512 MiB toy guards. The
scientific checks and stop before physical execution remain unchanged.

Current continuation: follow the [single handoff task](../../SESSION_HANDOFF.md#next-task).
R067's observer/compiler review, R070's disposable launch repair and R073's
fake monitor checks are complete within their recorded scope. The
[R074 adapter review](B2_MONITOR_ADAPTER_REVIEW.md) specifies the remaining
monitor/integration work and records counterexamples;
[R076](evidence/r076/README.md) completes the fixture implementation.
[R081](B2_MONITOR_LIVE_VALIDATION_CONTRACT.md) reviews it, reproduces eleven
additional gaps and freezes the future ten-case PC suite.
The [Mac/PC performance and memory plan](MAC_PC_PERFORMANCE_MEMORY_PLAN.md)
defines future comparisons. Live adapters remain unvalidated and physical
execution remains disabled; the handoff selects new fixture-only repairs next.
The following R033 reading sequence and older assignments are historical.

Historical review sequence after R033: review the completed
[R033 prerequisite result](B2_COMPATIBLE_TRACE_PREFLIGHT_FOLLOWUP.md) and
[evidence index](B2_COMPATIBLE_TRACE_PREFLIGHT_EVIDENCE.md), then the
[R022 historical memory stop](B2_COMPATIBLE_TRACE_PREFLIGHT_RESULT.md),
the
[R021 compatibility review and revised experiment contract](B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md)
and [evidence index](B2_COMPATIBLE_TRACE_INTEGRATION_EVIDENCE.md), then the
[R020 pressure-compatibility stop and method-review contract](B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md)
and [evidence index](B2_MATCHED_TRACE_COMPATIBILITY_EVIDENCE.md), then the
[R019 toy portability result](B2_TOY_PORTABILITY_RESULT.md) and
[evidence index](B2_TOY_PORTABILITY_EVIDENCE.md), then the
[R018 prerequisite stop](B2_MATCHED_TRACE_PREFLIGHT_RESULT.md) and
[evidence index](B2_MATCHED_TRACE_PREFLIGHT_EVIDENCE.md), then the
[R017 block RHS toy repair result](B2_BLOCK_RHS_TOY_REPAIR_RESULT.md) and
[evidence index](B2_BLOCK_RHS_TOY_REPAIR_EVIDENCE.md), then the
[R016 lifting failure and original toy repair contract](B2_MATCHED_TRACE_LIFTING_RESULT.md),
its [evidence index](B2_MATCHED_TRACE_LIFTING_EVIDENCE.md), the
[partial matched-trace result](B2_MATCHED_TRACE_RESULT.md), its
[preserved run evidence](B2_MATCHED_TRACE_RUN_EVIDENCE.md), the
[matched-trace experiment specification](B2_MATCHED_TRACE_REVIEW.md), its
[read-only review evidence](B2_MATCHED_TRACE_EVIDENCE.md), the
[single physical response audit](B2_PHYSICAL_RESPONSE_AUDIT.md), its
[exact evidence](B2_PHYSICAL_RESPONSE_EVIDENCE.md), the
[physical-accuracy review](B2_ACCURACY_REVIEW.md), its
[calculation appendix](B2_ACCURACY_EVIDENCE.md), the
[response-geometry result](B2_RESPONSE_COERCIVITY_RESULT.md), its exact-runner
[appendix](B2_RESPONSE_COERCIVITY_EVIDENCE.md), and root
[session handoff](../../SESSION_HANDOFF.md). Alpha=96 now has positive
homogeneous-dissipation certificates on the exact 50/40/30/25 mm meshes;
alpha=48 remains inconclusive. R009 reproduced the physical reference and its
small numerical sensitivity. R012 completed the capped 50 mm alpha=96 physical
audit: PDE/arithmetic checks pass, but all five feature rules fail the physical
reference comparison. R013 completed the method review without new numerical
runs. R014 implemented the disposable kernels and attempted the experiment once.
Toy, mesh, load and disk-geometry checks passed; a wrapper constraint-grouping
error stopped it after one original-command solve, with no correction or A solve.
The R015 grouping repair is complete. R016 subsequently reached P's solve,
correction and checked cell-integrated output, then stopped during A_32 RHS
lifting before any A solve. R017 reproduced copy/duplicate metadata loss and
passed the replacement-vector lifting/assignment oracle and reporting fixtures
in 8.50 s cumulative with 183.21 MiB peak. No physical execution occurred.
R018 reviewed the remaining A path and preserved all identities, but fresh
prerequisites stopped on the wrapper toy's archive-depth repository-root lookup
after watchdog and kernel checks passed. The
[R019 toy portability repair](B2_TOY_PORTABILITY_RESULT.md) moved root checking
inside the report boundary and before DOLFINx/MPI imports, then passed all five
prerequisite phases in a shallow disposable directory. The wrong-root path and
parent refusal both wrote finite zero-count reports. No physical child ran.
R020 subsequently passed fresh prerequisites and ran one physical attempt in
59.97 s/757.00 MiB. P's complete outputs reproduce R016. A_32 completed lifting
and assignment, then failed pressure compatibility at 11.09 times the fixed
arithmetic limit before solving. Saved flux imbalance predicts the failure;
A_64 compatibility and all matched-trace gains remain unmeasured. R021's
completed saved-data review checks 564 facet records and selects fixed
q=64/q=96 loads, retaining the finite trace and thresholds. P and both A
compatibility screens move before factorization. The shared-potential moment
alternative is derived and deferred. No numerical fixture ran in R021. R022's
new observer remained untested after its 512 MiB stop. R033 has now completed
all prerequisite and observer coverage in four disposable attempts and 56.25
cumulative seconds. The 16 high-order facet checks and nine full block-oracle
comparisons passed. Compatible P/A/A reached the pre-KSP sentinel; incompatible
P, first-A and second-A cases refused with unchanged raw vectors. Each
observation occurred once, with zero factor or solve events. The maximum
sampled child-tree RSS across attempts was 571.42 MiB under a 1536 MiB cap; the
final cache-reuse pass peaked at 171.24 MiB. No production files changed and
no physical child ran. R067 subsequently completed the **Astra/high review**
and identified launch/report repairs. Follow the current task above; older
assignments below are historical.

Follow-up at commit `a6295da`: the reference and cube audit are implemented.
The new [stability review](B2_STABILITY_REVIEW.md) tests the actual cylinder
geometry, demonstrates unforced energy growth, and specifies the next bounded
implementation package. The original derivation below remains useful context.

Prepared 2026-09-19 after reading all tracked source, configuration, tests, and
research documents at commit `47b3205`. The tracked working tree was clean.
The stored B2 report's six source/configuration hashes match the current files.
The numerical work below is a new independent reference calculation; the
stored three-dimensional CFD runs were not rerun during this audit.

## Decision

Continue B2 verification before launching the six-input campaign or B3 sensing.
First add an independent reference for `T_00c`, then check the stability and
boundary enforcement of the existing BDM2/DG1 formulation. Larger uniform
meshes are not the first next step.

Keep the current rest operating point, smooth-cylinder dimensions, viscosity,
boundary modes, probe amplitude, feature definitions, and harmonic convention.
The reference below is a verification oracle for one symmetry-restricted case,
not a replacement CFD backend or an extension to nonlinear flow or m=4.

The alternatives in `B2_GATE.md` (iterative solver, graded mesh, or a reviewed
Fourier-separated backend) remain possible after these checks establish the
accuracy and cost requirements. Do not silently select a new production
discretization or reinterpret the failed gates.

## Independent reference for the tangential pilot

For axisymmetric pure swirl about rest, write
`u_hat = v(r,z) e_theta`, with constant kinematic pressure. The linear Stokes
equations reduce exactly to

```text
i*omega*v = nu*(v_rr + v_r/r - v/r^2 + v_zz)
v(R,z) = U*(1-(z/H)^2)^2
v(r,+H) = v(r,-H) = 0
v(0,z) = 0, with v/r finite.
```

These are the existing `T_00c` data on the ideal smooth cylinder. They are not
the exact boundary data on a finite faceted mesh. In particular, a tangential
vector relative to the cylinder need not be tangential to each planar facet.

Separation of variables gives the following series, with n = 0,1,...:

```text
a_n = (n+1/2)*pi
k_n = a_n/H
b_n = integral[-1,1] (1-s^2)^2*cos(a_n*s) ds
    = 16*(-1)^n*(3-a_n^2)/a_n^5
lambda_n = sqrt(k_n^2 + i*omega/nu), choosing positive real part

v(r,z)/U = sum_n b_n * I_1(lambda_n*r)/I_1(lambda_n*R) * cos(k_n*z).
```

The coefficient formula follows by integrating the quartic polynomial by parts;
the cosine basis has squared norm one on [-1,1]. The radial equation is the
order-one modified Bessel equation, and regularity excludes its singular
solution. See the [NIST definition](https://dlmf.nist.gov/10.25) for this equation.

For the existing disk feature of radius d = 0.025 m at z = 0:

```text
G_Omega = Omega_hat/U
        = (4/d^4) * integral[0,d] r^2 * v(r,0)/U dr
        = (4/d^2) * sum_n b_n * I_2(lambda_n*d)
                                  / (lambda_n*I_1(lambda_n*R)).
```

This is the disk-fitted rotation feature, not a pointwise velocity or a core
radius. G_Omega has units 1/m. All five other primary features vanish by
symmetry for this ideal case; pressure differences vanish as well.

Use exponentially scaled Bessel functions to avoid overflow. For positive
real(lambda) and 0 <= r <= R,

```text
I_j(lambda*r)/I_1(lambda*R)
  = ive(j, lambda*r)/ive(1, lambda*R) * exp(real(lambda)*(r-R)).
```

The exponential here is real, as required by
[SciPy's definition of ive](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.ive.html).
Keep SciPy optional; Track A and B0 retain their existing dependency scope.

## New calculation and its limits

At R = 0.10 m, H = 0.15 m, nu = 1e-6 m^2/s, and f = 0.01 Hz:

```text
G_Omega = 2.066285885722e-5 - 6.595106312048e-5 i  [1/m]
|G_Omega| = 6.911220198254e-5  [1/m]
wrapped phase = -72.603917097 degrees
|Omega_hat| at U = 1e-7 m/s = 6.911220198254e-12  [1/s].
```

The wrapped phase is not an unwrapped delay or evidence of a short response
time. The calculation assumes the periodic steady state of linear Stokes flow.
It says nothing about preparing or controlling a finite-amplitude vortex.

| Terms | Magnitude (1/m) | Wrapped phase (degrees) |
|---:|---:|---:|
| 8 | 6.91111092850e-5 | -72.603682684 |
| 16 | 6.91122019877e-5 | -72.603917094 |
| 32 | 6.91122019825e-5 | -72.603917097 |
| 64 | 6.91122019825e-5 | -72.603917097 |
| 128 | 6.91122019825e-5 | -72.603917097 |

Independent 512-point Gauss-Legendre integration agrees with the closed-form
b_n coefficients to 3.4e-15 absolute and with the disk-integral expression to
1.0e-18 absolute. This is evidence of series/quadrature convergence for this
calculation, not a formal error bound or validation of the 3D solver.

The existing B2 tangential gain magnitudes are approximately 1097, 299, and
262 times this reference at 40, 30, and 25 mm mesh sizes, respectively.
The 25 mm complex discrepancy is approximately 0.0182041 1/m. That discrepancy
includes geometry, boundary-data, and discretization effects; it does not
identify which effect dominates. The physical response is small but nonzero.

Reproduce the arithmetic from the repository root with a SciPy-enabled Python:

```bash
python - <<'PY'
import numpy as np
from scipy.special import ive

R, H, d, nu, f = 0.1, 0.15, 0.025, 1e-6, 0.01
s, weights = np.polynomial.legendre.leggauss(512)
for count in (8, 16, 32, 64, 128):
    n = np.arange(count)
    a = (n + 0.5)*np.pi
    b = 16*(-1.0)**n*(3-a*a)/a**5
    lam = np.sqrt((a/H)**2 + 2j*np.pi*f/nu)
    ratio = ive(2, lam*d)/ive(1, lam*R)*np.exp(lam.real*(d-R))
    gain = (4/d**2)*np.sum(b*ratio/lam)
    b_quad = np.cos(a[:, None]*s) @ (weights*(1-s*s)**2)
    radius, radial_weights = d*(s+1)/2, d*weights/2
    profiles = (ive(1, lam[:, None]*radius)/ive(1, lam[:, None]*R)
                * np.exp(lam.real[:, None]*(radius-R)))
    gain_quad = (4/d**4)*np.sum(radial_weights*radius**2*(b @ profiles))
    print(count, gain, abs(gain), np.angle(gain, deg=True),
          max(abs(b-b_quad)), abs(gain-gain_quad))
PY
```

## Implementation work to hand off

1. Package the derived series as an optional diagnostic module and add focused
   tests: coefficient quadrature, regular axis limit, cap conditions, truncated
   side-wall reconstruction, series refinement, and independently integrated
   disk feature. Check a resolved lower-frequency or higher-viscosity fixture
   as well as the physical 0.01 Hz case. Label altered-parameter cases as
   verification fixtures, preserving the production parameters.
2. Audit the existing SIP viscous form before another production refinement.
   Both implementations currently use alpha = 6 directly; the cited
   [DOLFINx demo](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/demos/demo_navier-stokes.html)
   uses alpha = 6*k^2 in a different element/mesh setting. That is a reason to
   test coercivity, not proof that 24 is sufficient for our tetrahedral BDM2
   meshes. Extract a shared form helper so verification and production test
   the same operator. On small meshes test alpha = 6, 12, 24, 48 with no added
   reaction. Check symmetry and the lowest eigenvalues after eliminating
   homogeneous normal boundary DOFs; inspect the discretely divergence-free
   subspace when interpreting stability of the constrained Stokes system.
   Add a homogeneous-wall decay or non-affine manufactured convergence check.
   The current affine reaction fixture verifies consistency for one exactly
   represented field; it cannot certify positive viscous dissipation.
3. Measure tangential boundary error against the declared target, including
   caps, and interior tangential jumps. The current `boundary_dof_residual`
   checks essential normal DOFs only. Distinguish prescribed target speed from
   actual computed trace speed. Audit whether the weak target's normal
   component on planar facets is consistent with the imposed zero normal
   trace; any projection must be explicit and checked under geometry refinement.
4. Compare the complex `T_00c -> Omega` gain with the independent reference,
   recording absolute complex error as well as relative gain/phase error.
   Keep the current numerical thresholds. Do not claim a resolved phase while
   discretization error exceeds the response. Agreement between adjacent
   meshes alone is insufficient if both disagree with the reference.
5. Only then choose the least costly refinement/linear-solver improvement with
   measured degrees of freedom, runtime, memory, and accuracy. At 0.01 Hz the
   viscous penetration length is 5.642 mm; the handoff's initial wall spacing
   delta/4 is approximately 1.410 mm. Merely shrinking the current 25 mm
   uniform mesh once more is unlikely to settle this accuracy question.

Stop after the independent reference and small stability tests and bring back
the results before initiating another large refinement campaign. A converged
small-response result remains useful; it does not authorize relaxing a gate or
claiming failure of boundary control around a developed vortex.

## Additional issues to address before later packages

- Completed 2026-09-20: `realizability/response.py` preserves complex gains,
  Gram matrices, and measurement/feature maps. Inverse roots and right
  nullspaces use conjugate transposes. Five phase-sensitive regressions in
  `tests/realizability/test_response.py` cover whitening, unit invariance,
  rank, nullspace residuals, and identifiable/unidentifiable feature maps.
  Complex inputs describe complex coefficients such as harmonic amplitudes;
  this repair does not establish dynamical observability or pass the B2 gate.
- `b2_gate.py` checks only primary relative gain/phase changes; it has no
  absolute response error floor. Penalty-comparison solves should also satisfy
  the same PDE diagnostic checks as baseline solves. These are report/gate
  improvements, not a reason to reinterpret the stored failed result.
- `PROJECT_TRACKS.md` still says CFD has not begun; the package and CLI
  docstrings also describe only B0. Update these summaries to acknowledge B0,
  B1's documented limitation, and the incomplete B2 gate. Preserve historical
  context in the original handoff.
- The B2 generated report lacks the complete configuration, runtime dependency
  versions, and all contributing source hashes required by the handoff. Add
  these before future result comparisons; the matching existing hashes do not
  establish complete provenance.

## Cost-aware continuation

The research decision and reference derivation are now recorded. Pause here for
a model switch, as requested by the user. A cheaper coding model can implement
the explicit reference, tests, diagnostics, and documentation updates above.
Retain higher-level review for interpreting instability, choosing a new solver
or mesh architecture, changing thresholds, or broadening the physical claims.

### Continuation update, 2026-09-20

The stability implementation was checkpointed and pushed as `a503cbb` before
the response-helper repair above. The five new tests reproduced phase loss on
that checkpoint and passed after the repair. Validation with warnings treated
as errors:

```bash
python3 -W error -m unittest discover -s tests/realizability -v
```

Result: 30 tests discovered, 18 passed, 12 optional DOLFINx tests skipped.
The existing real-valued tests pass. No CFD calculation was rerun for this
algebra-only change, and the stored physical-pilot gate remains failed.

The next routine task is suitable for a cheaper coding model: synchronize the
stale project-status summaries. Handoff and completion instructions:

1. Read `AGENTS.md`, this update, `B2_GATE.md`, and the implementation-results
   section of `B2_STABILITY_REVIEW.md`. Inspect the working tree and preserve
   any uncommitted response-helper changes.
2. Update the Track B status in `PROJECT_TRACKS.md` and the opening docstrings
   of `realizability/__init__.py` and `realizability/cli.py`. Describe implemented
   B0 diagnostics, optional B1/B2 Stokes backends, B1's divergence limitation,
   and B2's unresolved physical response gate. Keep Track A's kinematic status
   and the distinction between verification fixtures and physical validation.
3. Verify the wording against the current commands and reports. Run
   `python3 -m realizability.cli --help`, the test command above, and
   `git diff --check`. Completion means the three summaries agree, checks pass
   with optional skips disclosed, and the final handoff lists changed files.
   This task requires no new CFD runs or generated report changes.
4. Stop after those summaries and recommend returning to a more capable model
   for numerical-method review before selecting a production mesh, solver,
   penalty strategy, or changing any scientific acceptance threshold.
