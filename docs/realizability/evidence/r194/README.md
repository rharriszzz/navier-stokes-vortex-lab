# R194 retained analytical checks

[Base-flow contract](../../PORT_BASE_FLOW_CONTRACT_R194.md).

```bash
.venv/bin/python docs/realizability/evidence/r194/check_contract.py
```

Python 3.12.14, standard library only; prints JSON without writing by default.
The retained [contract_checks.json](contract_checks.json) was produced with
`--output docs/realizability/evidence/r194/contract_checks.json`.

Twelve groups passed: exact circular profile moments; inlet/return normalization;
instantaneous ramp compatibility; nominal port clearance; straight oblique-bore
moment arm; angular flux with independent profile quadrature; kinetic flux;
finite-footprint averaging counterexample; C16/m=4 restrictions; independent
Poiseuille power/pressure identity; nonzero affine angular and energy surface
budgets; and pressure-gauge invariance. The affine field uses u=(x,2y,-3z),
p=-rho*(x²+4y²+9z²)/2 on [0,1]×[0,2]×[0,3], an exact stationary unforced
Navier–Stokes field with prescribed boundary velocities. Tensor Gauss-3 integrates
its polynomial fluxes exactly up to floating-point arithmetic. It tests the
continuum accounting, not the proposed mixed return discretization.

Inputs are declared R192/R194 design assumptions. No FEM import, mesh, assembly,
PDE solve, saved-field integration, physical/optical test or trajectory ran.
Clearance checks are nominal geometric inequalities, not a CAD/mesh certificate.
No actual base, return split, core delivery, settling or error floor is measured.
