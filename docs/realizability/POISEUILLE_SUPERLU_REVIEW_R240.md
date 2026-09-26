# R240 — Explicit serial SuperLU source choice

2026-09-26, PC/WSL daisy. Base `5ed9253`, STARTED `628e04d`.
**Source review/implementation complete; numerical execution is not admitted.**
All three old fixture allocations remain spent 1/1. No FEM import, JIT,
assembly, backend solve, live scope or new allocation occurred.

## Method choice and preserved limits

[R239](POISEUILLE_PIVOT_REVIEW_R239.md) established that a full-rank gauged
toy can fail without numerical pivoting, while a singular toy can pass the
three-row Gram check. R238's actual matrix/rank is still unknown. The chosen
source change replaces native PETSc LU with **serial SuperLU LU**, retaining
PREONLY, one rank/thread, the exact bordered operator and all existing gates.
Pivoting permutes the factorization rather than adding a regularizing term.
This is a justified candidate for the nonsymmetric saddle system, not a proof
of invertibility or successful FEM behavior.

Alternatives considered: repeating unchanged native LU provides little new
information; a diagonal shift changes the operator; a hand-selected ordering
from the toy does not establish stability for the real matrix; MUMPS or
SuperLU_DIST introduce a different interface and are unnecessary for this
serial source increment. No automatic fallback is added.

## Controls and interface review

The settings in [cube_adapter.py](../../verification/nonlinear_port/cube_adapter.py)
are fixed explicitly:

| Control | Value | Purpose |
|---|---|---|
| KSP / PC / backend | preonly / lu / superlu | Full direct serial factorization |
| PETSc factor shift | NONE, amount 0 | No diagonal regularization |
| SuperLU column ordering | COLAMD | Its own sparsity ordering |
| Diagonal pivot threshold | 1 | Largest-magnitude partial pivot policy |
| Symmetric mode | false | No symmetry-based preference |
| Equilibration / refinement | false / NOREFINE | Retain current row scaling and direct solve |
| RowPerm | NOROWPERM | Disable optional preprocessing, not numerical pivoting |
| ReplaceTinyPivot | false | Explicitly exclude replacement |
| ILU_FillTol | 0 | Preserve PETSc's singular-LU status path |
| Workspace | lwork 0 | Normal allocation inside the existing resource cap |
| PrintStat / PivotGrowth / ConditionNumber | false | No extra backend reports/calculations |

PETSc documents these serial options and distinguishes the distributed
backend. It does not use PETSc's ordering for this interface.
[Serial SuperLU manual](https://petsc.org/release/manualpages/Mat/MATSOLVERSUPERLU/).

The upstream 7.0.1 pivot routine selects a maximal available entry at threshold
1 and returns a positive status when the candidate column is exactly zero.
The local header labels RowPerm as an ILU/distributed control and tiny-pivot
replacement as distributed-only; setting both conservatively does not disable
LU's numerical pivoting. [Pivot source](https://raw.githubusercontent.com/xiaoyeli/superlu/v7.0.1/SRC/dpivotL.c).

The PETSc 3.25.5 interface factors a transpose representation of the CSR input
and performs the matching transpose solve. Thus SuperLU row permutations are
not directly original CSR row identities. It reads options during symbolic
factorization even without KSP/PC `setFromOptions`. Fresh factor state is zero
initialized; several false boolean options leave those defaults untouched.
Its numeric failure path also consults ILU_FillTol, so that value is fixed to
zero. The `n+1` condition warning is not automatically a factor failure; true
residual and all downstream physics checks remain essential, and passing them
does not prove a condition bound.
[Pinned PETSc interface](https://raw.githubusercontent.com/petsc/petsc/v3.25.5/src/mat/impls/aij/seq/superlu/superlu.c).

### Ambient options and cleanup

The source reserves `navier_port_superlu_`, refuses any existing key under
that prefix (including unknown keys), temporarily supplies its twelve fixed
options, then removes them in `finally`. Other options are untouched. The PC
prefix is propagated by the LU setup to the factor matrix; only the prefixed
backend settings are read. No KSP/PC `setFromOptions` is called. This design
assumes the existing single serial worker/thread, not concurrent independent
solves sharing PETSc's global options database.
[LU setup](https://petsc.org/release/src/ksp/pc/impls/factor/lu/lu.c.html),
[factor creation](https://petsc.org/release/src/mat/interface/matrix.c.html).

A flushed configuration line precedes setup/solve, so exceptions retain the
requested backend/settings. It is a configuration record, not a measurement
of successful option application. Existing status refusal adds `backend=superlu`;
solver exceptions propagate, and matrix/vector/KSP cleanup remains in `finally`.
True residual tolerance remains `max(1e-13, 1e-8 * norm(rhs))`. No acceptance
threshold, lifting, gauge, flux row, manifest, dependency pin or resource cap
changed.

## Installed artifact evidence and discrepancy

R229's installed PETSc declares serial SuperLU support. Conda metadata reports
`superlu 7.0.1 h8f6e6c4_0`, archive SHA256
`4e748f877553c7ed42290420ba1e9aa0e80cf72b23b463f12dbb7927c16f0437`.
However, its installed header, CMake version and library filename say **7.0.0**.
All three installed files match the package's own file hashes. This rules out
an unexplained local modification of those files; it does not explain the
upstream/package version discrepancy. The installed header differs from the
currently fetched upstream v7.0.1 header only in the patch-version macro.
The cached recipe records a v7.0.1 source archive, SHA256
`a24fcbdf7efa455bf272f63e7bc4ddeced9bfcecb69ce6ddffd12360d43bed3c`.

[Checks](evidence/r240/checks.json) preserve metadata/file hashes and seven
upstream source retrieval receipts. The source snapshots remain locally in
`/tmp/navier-r240-source`; URLs/hashes permit content verification on another
checkout, but mutable tags must not be assumed byte-identical on re-fetch.
No package was installed or relabelled. Dynamic loading, API behavior and
factorization remain untested. The later admission must explicitly resolve
or accept this artifact identity on evidence, rather than assuming the package
label proves identical current-tag source. The source implementation alone
does not authorize use of the artifact.

## Checks and future failure evidence

All **65 standard-library tests pass**, including three new tests for option
isolation/collisions/partial insertion and updated checks for failure, cleanup,
success and the true residual. The earlier focused 18-test run passed too.
No NumPy/FEM/PETSc/MPI/SymPy modules loaded. These mocks test our control flow;
they do not validate PETSc, option propagation or actual factorization.
[Test report](evidence/r240/tests.json), [output](evidence/r240/tests.txt).
Of the 25 tracked source/pin files, only adapter and its test changed. Thirty
old raw files match retained originals; all three reservations remain and
saved worker PIDs/cgroups are absent. No live manager query was needed.

Before admitting another fixture, close the previous status-only evidence gap:
save the exact **already assembled, lifted, scaled CSR plus RHS**, shape,
state/step/Newton identity, row scales, fixed-index list and source/backend
settings before its first factorization. Use a bounded latest-system record,
atomically replaced per correction, within the same run directory and timer;
for n=2 require explicit finite size/byte caps and refuse oversized/nonfinite
records. Preserve the latest record on success or failure; no second assembly
or alternate solve is needed. Hash the record and retain status/exception logs.
Actual factor permutation/pivot coordinates are not exposed by this Python
interface; label them unavailable unless a separately reviewed source path
captures them. Never call an external `info` index an original matrix row
without its mapping. A saved CSR enables later independent rank/nullspace
analysis under a separate bound.

This specifies the required evidence addition; it is not implemented here and
is a prerequisite of the next admission review. That review should implement
and test the bounded record without numerical imports, bind the exact artifacts
and source, then grant one later attempt in a new directory only if justified.
Keep 180 s total / 150 s worker / 1536 MiB / no swap / 32 tasks / one rank/thread,
no retry, all scientific gates, and R229's false setup memory-event predicate.
Stop before execution; full suite/rotation/tank/B2 and physical/render work
remain unadmitted. Follow the [next task](../../SESSION_HANDOFF.md#next-task).
