# R196 source/algebra evidence

- [Test output](algebra_checks.txt): 24 checks passed under project Python 3.12.14.
- [Machine-readable record](checks.json): count, import exclusions and SHA-256
  bindings for the reviewed prototype/adapter/diagnostic sources and manifest.
- [Reproducer](check_source.py): standard library only; from the repository root,
  run `.venv/bin/python docs/realizability/evidence/r196/check_source.py`.
  It overwrites only these two R196 evidence outputs, never experiment inputs.

The tests cover exact fixture balances, mixed gauge/rank, dense versus sparse
bordering/lifting, fixed scaling/Newton/refusals, CSR structure at the proposed
maximum dimension, six-face inventory, signed non-solenoidal energy balance,
physical endpoint versus discrete storage, rate/floor/quadrature handling and
missing-output/eta refusals. No fake adapter result is a library-validation pass.

No FEM imports, UFL construction, JIT, mesh, assembly, PDE solve, resource-limit
trial or workload child occurred. `execution_admitted: false` and zero attempts
remain in the manifest. Actual assembly, runtime cost, backflow samples,
convergence and process cleanup are untested. Source/interface review and the
concrete remaining launch path are in the [R196 review](../../CUBE_ADAPTER_R196.md).
The [handoff](../../../../SESSION_HANDOFF.md#next-task) is the single next task.
