# R191 conditional design checks

Supports the [essential-similarity design](../../ESSENTIAL_SIMILARITY_CONTRACT_R191.md).
The retained [checker](check_design.py) performs 13 exact SymPy identities,
one Gaussian peak-root numerical check and one four-row scale-arithmetic group:
15 passing groups in [the observed output](design_validation.json).

The independent volume/face integrations check inventory, both endcaps,
side transport/viscosity and the time-dependent Gaussian balance. Phase checks
separately integrate angular and temporal products, avoiding a missing factor
of two. The annular example checks that nonzero covariance need not have a
nonzero divergence. Manual review covers units, signs, covariance definitions,
pressure torque, fixed versus recentered surfaces, and the inference limits.

Reproduce with Python 3.12 and [optional symbolic dependencies](../../../../requirements-symbolic.txt):

```bash
/tmp/navier-r183-sympy/bin/python docs/realizability/evidence/r191/check_design.py
```

That interpreter is local/disposable; recreate a separate environment if absent.
Observed environment: Python 3.12.14, SymPy 1.14.0. The checker writes only to
stdout. No CFD/reference-field sampling, trajectory, control, physical flow,
optical data or sensor simulation occurs. It does not certify feasibility,
uncertainty thresholds, a realizable perturbation field or a bounded-tank solution.
