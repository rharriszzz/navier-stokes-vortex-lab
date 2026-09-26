# R233 — Preserve structural diagonals in the bordered CSR

**The source defect behind the R232 symbolic-LU refusal is demonstrated and
repaired. No FEM rerun or new allocation occurred.** `CSR.from_rows` discarded
all zero values and never added absent diagonal slots. The scalar border has
three identically zero diagonal entries, so the old path necessarily passed an
incomplete diagonal structure to PETSc. Pressure rows have zero diagonals too.
The fix stores a zero diagonal in each row while preserving every numerical
coefficient. All 59 standard-library tests pass without numerical imports.

The [R232 result](POISEUILLE_RESULT_R232.md) remains **INCOMPLETE, spent 1/1**.
Its exact failing row, actual matrix, rank, accuracy and resource counters were
not saved. This review explains a deterministic source defect sufficient for
the observed error; it does not reconstruct an observed matrix or establish
that the next numerical factorization would succeed.

## Source and failure analysis

The clean R232 execution bound `980ef7f`, whose `sparse.py` matches the source
before this repair. The saved error names `MatLUFactorSymbolic_SeqAIJ`, line 71,
error 73. PETSc's published 3.25.5
[symbolic-LU source](https://petsc.org/release/src/mat/impls/aij/seq/aijfact.c.html)
checks diagonal structure at that line, before applying its ordering to build
the factor pattern. The AIJ
[structure definition](https://petsc.org/release/src/mat/impls/aij/seq/aij.h.html)
describes `diagDense` as whether every diagonal entry is present. A zero value
can occupy such a slot. This is a structural prerequisite, separate from
numerical pivot tests and operator rank.

The audited chain is:

1. `prototype.build_forms` has continuity `q*div(u) + eta*q`, with no p-p
   term. The pressure-pressure diagonal is zero. The independent return flux
   and pressure-gauge residuals depend on mixed u/p, not P-minus/P-plus/eta.
2. `Assembler.__call__` obtains the uneliminated FEM core CSR and adds three
   column vectors, two flux rows and one gauge row using `border_and_lift`.
   Those three rows contain only core columns, so their own diagonal slots
   are absent regardless of what FEM assembly supplied for the core.
3. The lateral lift is already installed in every assembled residual. The
   code removes fixed velocity columns from all rows, replaces fixed rows
   with unit diagonals and sets their increment residual to zero. This is
   consistent with zero Dirichlet increments; no second lift subtraction is
   needed. Constrained velocity diagonals survive as ones.
4. Old `CSR.from_rows` retained only truthy values. It therefore removed any
   zero pressure diagonal slots from the core and omitted all three scalar
   diagonals. A zero free-velocity diagonal would also be dropped, but none
   was observed in R232. The saved log gives no mixed-space row numbering.
5. `scale_system` rebuilds CSR through the same constructor. Fixing only the
   initial border would be insufficient because scaling would remove zeros
   again. `sparse_solve` converts the arrays to PETSc index/scalar types and
   sends their existing pattern to `createAIJ(..., csr=...)`, then selects
   preonly/LU with the PETSc factor backend and no ambient options.

The [petsc4py createAIJ documentation](https://petsc.org/release/petsc4py/reference/petsc4py.PETSc.Mat.html#petsc4py.PETSc.Mat.createAIJ)
describes CSR preallocation. PETSc's
[CSR insertion source](https://petsc.org/release/src/mat/impls/aij/seq/aij.c.html)
inserts the supplied row entries; its sequential AIJ zero-ignore conditions
exclude diagonal entries. Supplying explicit diagonal zeros is supported by
this source path. These are source/documentation checks, not calls into the
installed numerical library. An initial tagged raw-source URL and an obsolete
MatMissingDiagonal documentation URL failed to fetch; the published release
source above supplied the relevant evidence. Installed petsc4py Cython sources
were not found by the targeted local read-only search.

## Minimal correction and regression

[sparse.py](../../verification/nonlinear_port/sparse.py) now copies each row,
adds its diagonal key with value zero only when missing, and retains that key
even when its value is zero. Sorted unique CSR, existing nonzero diagonals,
off-diagonal coefficients, input dictionaries and zero filtering away from the
diagonal retain their behavior. Storage adds at most one entry per row, with
no dense matrix or regularization. Numerical rank and any singularity remain
unchanged. The gauge, both flux constraints, lifting, fixed scales, PETSc
backend, fixture, pins, resource caps and all acceptance thresholds are unchanged.

Three new [adapter regressions](../../verification/nonlinear_port/test_adapter.py)
cover explicit/absent/nonzero diagonals and empty rows; the real border/lift/
scaling chain with two pressure rows and three scalar rows; and the actual
`sparse_solve` CSR handoff up to a capturing `createAIJ` boundary. That last
test deliberately stops before matrix creation, and proves no PETSc execution.
Dense equivalence and exact toy rank checks confirm algebra preservation;
an all-zero matrix remains rank zero. Both unconstrained and lifted variants
are checked, including fixed unit rows, eliminated columns and scalar residuals.

The three regressions were run against the old source first: three test
methods failed, with four assertion failures because both lift subcases failed.
After the repair, all seven modules passed: **59 tests, 0 failures/errors,
0.565381042 s** for the observed test runner interval under project Python
3.12.14. The post-suite module audit found no NumPy/DOLFINx/Basix/UFL/FFCx/
PETSc/MPI imports. Retained output and the reviewed source inventory are in
[evidence/r233](evidence/r233/) and [checks.json](evidence/r233/checks.json).
No numerical library, mesh, assembly, JIT, factorization or supervised scope
was launched. These tests include small standard-library algebra and fake
driver boundaries; they are not a numerical-fixture PASS.

## Preserved evidence and next decision

Read-only checks confirm all ten R232 raw files match their saved hashes and
retained `/tmp/navier-poiseuille-r230-once` originals. Its reservation remains
present, worker PID 144212 and its cgroup are absent. The source fix does not
alter these bytes or the **1/1** charge. R229's 303 memory.max setup-event
refusal remains false. No resource measurement is inferred from a missing
snapshot, and no actual FEM rank or accuracy result is inferred from toy tests.

The existing R230 source ledger and R231 caller stay historical and unchanged;
the old caller will reject the repaired source hashes. Do not update its ledger
to manufacture a retry. A future launch needs a separately reviewed allocation,
fresh exclusive directory and clean source/interpreter binding. The fixed R232
directory must never be reused. Numeric zero pivots, ordering behavior, actual
compatibility/Gram rank, quadrature, accuracy and memory events remain possible
future refusals under the original gates.

Next: **Astra/high makes the separate go/no-go admission decision for one later
bounded n=2 Poiseuille fixture using this repaired source**, retaining the old
charge and every cap/gate. That review stops before execution. Only if it admits
a new allocation should it recommend Sol/high for the mechanical launch after
a later Continue. Use the single [handoff task](../../SESSION_HANDOFF.md#next-task).
No `/new` is needed for this directly connected decision. Official
[OpenAI Docs](https://developers.openai.com/api/docs/models/gpt-6-astra) was
searched and opened and confirms Astra/high support; task fit is judgment and
account-specific availability was not checked. PC/WSL daisy retains ownership,
Mac remains released, and no model/session switch was initiated by the agent.
