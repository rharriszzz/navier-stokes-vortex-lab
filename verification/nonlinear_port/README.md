# Isolated nonlinear port verification prototype — R195

This is **verification source and algebra evidence, not a validated FEM solver**.
The [review](../../docs/realizability/NONLINEAR_VERIFICATION_R195.md) derives the
fixtures, gauge equivalence, lifting, signs and remaining implementation boundary.
No production B1/B2 module imports this directory. No dependencies changed.

- `polynomial.py` and `fixtures.py`: standard-library rational polynomial oracles,
  exact manufactured data, plane Poiseuille and rigid rotation.
- `prototype.py`: injected P2/P1 space and UFL residual/Jacobian block builders,
  coupled gauge/return constraints, strong-lifting treatment, damped Newton and
  fixed-step BE/BDF2 iteration kernels. Imports no FEM libraries. `launch()`
  always refuses. There is no mesh or assembly driver.
- `future_fem.json` and `manifest.py`: a proposed bounded verification manifest
  and checks for its non-executable state, pins, sequences, gates and caps.
- `test_algebra.py`: exact identities, independent special cases, rank/lifting,
  time integration, iteration failures and scope checks; no FEM imports/JIT.

From the repository root:

```sh
.venv/bin/python -m unittest verification.nonlinear_port.test_algebra -v
```

The future adapter must assemble the returned blocks, install current boundary
values before evaluating every residual row, select a sparse linear solve,
implement diagnostic acceptance and obey external resource supervision. Passing
these algebra checks does not establish that UFL construction, DOLFINx assembly,
mesh inf-sup stability or numerical convergence works. No tank/campaign entry
exists. Follow the single [handoff task](../../SESSION_HANDOFF.md#next-task).
