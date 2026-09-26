# R239 — Numeric zero pivot: operator and elimination review

2026-09-26, PC/WSL daisy. Source base: R238 delivery `ce68c04`;
R239 STARTED `4d5acd6`. No runtime source or solver change, numerical import,
FEM assembly, live scope or new allocation. The R232/R235/R238 allocations
remain spent 1/1. Continue remains in the user's existing session.

## Result and limits

The [R238 refusal](POISEUILLE_RESULT_R238.md) reports KSP -11, 405 nonfinite
answer entries and PC reason 2 (numeric zero pivot). It does not identify a
pivot row, permutation, null vector or rank. No assembled matrix was saved.
The nonfinite answer count supplies no independent singularity test.

The existing exact toy is **full rank with its gauge, but natural-order
elimination fails at a zero pivot**. One row swap completes its factorization.
Conversely, a deliberately singular toy still passes the three-row constraint
Gram check. Thus neither the reported pivot failure nor the Gram check settles
the real mixed operator's rank. This review finds no demonstrated sign or
gauge defect to repair. Actual assembly/indexing errors and additional discrete
null modes remain possible; source identities do not certify assembled values.

PETSc's documentation explicitly warns that its native sparse LU lacks
numerical pivoting and can encounter zero pivots on nonsingular matrices.
This makes backend suitability a concrete method question. The toy uses its
own stated order; it does not reproduce the unrecorded PETSc permutation.
See [PETSc 3.25.5 LU documentation](https://petsc.org/release/manual/ksp/).

## Exact operator structure

Read together: [forms](../../verification/nonlinear_port/prototype.py),
[adapter](../../verification/nonlinear_port/cube_adapter.py),
[driver](../../verification/nonlinear_port/fixture_driver.py),
[CSR/lifting](../../verification/nonlinear_port/sparse.py),
[R195 derivation](NONLINEAR_VERIFICATION_R195.md) and
[R196 adapter](CUBE_ADAPTER_R196.md). After removing fixed lateral velocity
increments, group unknowns as velocity u, pressure p, two return pressures P,
and gauge multiplier eta. The homogeneous Jacobian has blocks

```text
         u      p       P      eta
u        A     -B^T     C^T      0
p        B      0       0       m
P        C      0       0       0
eta      0      m^T     0       0
```

Here B integrates pressure tests against divergence, C contains signed outward
return flux rows, and m integrates pressure basis functions. A contains the
time, viscous and convective derivative terms; no positivity/invertibility
claim for the actual A is needed for the following identities.

For the represented constant pressure e and volume V > 0, the divergence
theorem on free velocity tests gives `e^T B = (1,1) C` and `e^T m = V`.
The ungauged block therefore has the joint right null vector
`(u=0, p=e, P=(1,1))`: a common pressure shift cancels in momentum.
Its left row redundancy is constant continuity minus both flux constraints.
For the gauged homogeneous system, summing continuity and using both flux rows
gives `V delta_eta = 0`; the gauge `m^T delta_p = 0` removes the common shift.
This removes that particular ambiguity, without proving a mixed inf-sup
condition or excluding further null modes.

Source audit points:

- Interior pressure has the negative momentum sign and positive continuity
  sign. Return pressure columns and flux rows both use outward normal flux.
  The eta column and pressure-gauge row both use pressure integration.
- Returns are z faces 5/6; fixed lateral velocity uses x/y faces 1–4.
  Poiseuille flows in x and is supplied through its exact lateral trace;
  both z-return targets are zero. Changing return axes would change the fixture.
- The current lift is installed before residual assembly. Fixed increment
  columns are removed, fixed rows become identity and fixed residuals zero;
  other rows retain their already assembled lift contribution.
- Frozen strictly positive row scaling preserves exact rank. Stored zero
  diagonal slots change CSR structure, not the represented operator. Neither
  supplies a numerical pivoting strategy.
- `sparse_solve` explicitly uses PREONLY/LU with PETSc's native backend and
  verifies the true residual. This review leaves all settings and gates intact.

## Reproducible discriminating check

Run from the repository with project Python:

```sh
.venv/bin/python docs/realizability/evidence/r239/check_algebra.py
```

The [script](evidence/r239/check_algebra.py) uses the existing R195 toy and
standard-library exact fractions. [Saved output](evidence/r239/algebra.json):

| Matrix | Exact rank | Natural elimination | Row pivoting |
|---|---:|---|---|
| Ungauged 7 by 7 | 6 | Zero pivot, index 6 | Still singular |
| Gauged 8 by 8 | 8 | Zero pivot, index 6 | Completes, determinant -1 |
| Gauge retained, zero-mean pressure coupling removed | 7 of 8 | Fails | Still singular; scalar Gram is identity |
| Gauged toy plus one fixed coordinate, real border/lift/CSR routines | 9 | Zero pivot, index 7 | Completes before and after positive scaling |

Indices are zero based. For the gauged toy, natural pivots are
`2,2,2,1,1/2,-1/4,0`; row pivoting swaps rows 5 and 7 during elimination,
then completes with `2,2,2,1,1/2,1/2,-1/2,-1`. The 9 by 9 check verifies actual
CSR/lift/scaling helpers on this bounded toy. Fraction arithmetic after scaling
represents stored binary floats exactly. No dense FEM matrix was constructed.
Assertions passed under Python 3.12.14; no numerical modules were loaded.

## Next method decision

Review an explicit **serial SuperLU** backend with numerical row pivoting for
this nonsymmetric bordered operator. PETSc documents its sequential sparse
interface and controls, including tiny-pivot replacement; these controls must
be reviewed and fixed before adopting it. See
[MATSOLVERSUPERLU](https://petsc.org/release/manualpages/Mat/MATSOLVERSUPERLU/).
This is a candidate, not an adopted backend or an assertion it will solve R238.

Static installed `/tmp/navier-fenicsx-r229` build files declare
`PETSC_HAVE_SUPERLU 1` and `SUPERLU_LIB = -lsuperlu`; their hashes and selected
lines are preserved in [checks](evidence/r239/checks.json). They indicate the
candidate is worth review without an install. Dynamic availability and actual
factorization remain untested. SuperLU_DIST and MUMPS are distinct backends;
their build declarations do not substitute for the serial interface review.

The next task is an import-free scientific/backend review, followed by a
minimal source change and focused mocked tests **only if** a fully specified
operator-preserving choice is justified. Specify pivoting and ordering,
disable tiny-pivot replacement/diagonal shifts, exclude ambient options and
fallbacks, retain true-residual/physics/resource gates, and require explicit
backend identity in failure evidence. If configuration cannot be established,
record the precise blocker. Plan minimal bounded matrix/pivot evidence for a
future refusal if needed; do not launch a diagnostic to fill that gap now.
Stop before a new numerical admission or execution. Actual R238 matrix rank
cannot be decided from the retained records alone.

## Verification and stopping point

[Checks](evidence/r239/checks.json) bind the 25 unchanged R236 source/pin files,
the new algebra evidence, and 30 preserved raw files and local originals across
the three spent runs. Old reservations remain; saved worker PIDs/cgroups are
absent. R236's 62-test result is reused under unchanged source, not rerun.
No installation, numerical imports/JIT/assembly/backend solve, live manager
work, full suite/rotation/tank/B2, rendering or Mac transfer occurred. R229's
303-event setup memory refusal remains false. PC retains ownership.

Follow the single [next task](../../SESSION_HANDOFF.md#next-task), Astra/high
for the method choice. No new chat is required; no model/session switch was
performed. Scoped completion publication ends R239.
