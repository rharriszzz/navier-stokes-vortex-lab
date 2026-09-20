# R021 compatibility method review: evidence index

Read the [review and subsequent experiment contract](B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md).
This archive contains saved-data work only; the proposed q=64/q=96 experiment
has not been implemented or run.

- [Review script](evidence/r021/review.py) uses the Python standard library to
  check identities, re-audit R020 with writes redirected, and calculate saved
  facet/pressure arithmetic. No NumPy, DOLFINx, PETSc, SciPy or field evaluator
  is imported. Positive-pivot checks factor only saved six-by-six facet Gram
  matrices; they are not new FEM assembly or a PDE factorization.
- [Identity manifest](evidence/r021/identities.json) checks 19 production hashes
  and 433 historical R014–R020 files against `e96f81b`.
- [Arithmetic report](evidence/r021/review.json) preserves all 564 facet checks,
  mass-equation residuals, cap zeros, flux sums, projection differences,
  nullspace normalization, translated flux budget and point-count comparison.
- [R020 re-audit](evidence/r021/reaudit-r020-validation.json) and its
  [stdout](evidence/r021/reaudit-r020.stdout) preserve the executed historical
  checks without changing the old validation file.
- [R021 audit](evidence/r021/audit.py) and
  [validation](evidence/r021/validation.json) verify inputs, repeatable saved
  arithmetic, finite records, request history, source syntax and local links.

Inputs remain at their original paths: [R020 physical report](evidence/r020/physical/report.json),
[q=32 facets](evidence/r020/physical/A_32_facets.json),
[q=64 facets](evidence/r020/physical/A_64_facets.json),
[physical runner](evidence/r020/physical.py), [local kernels](evidence/r020/kernels.py),
[direct helper](../../realizability/backends/fenicsx_stokes.py), and
[H(div) forms/spaces](../../realizability/backends/hdiv_stokes.py).
No historical payload was duplicated or edited. P's results and A_32's failed
compatibility remain as recorded; A_64 assembled compatibility is unmeasured.

From the repository root:

```bash
python3 docs/realizability/evidence/r021/review.py
python3 docs/realizability/evidence/r021/audit.py
git diff --check
```

The first command refreshes only R021 review records and redirects R020's
validation output here. The second refreshes R021 validation. Neither launches
a numerical fixture, mesh, reference evaluation, quadrature rule or solve.
Historical child scripts are evidence, not authorization to rerun them.
