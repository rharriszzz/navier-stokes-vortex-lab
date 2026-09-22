# R182 Gaussian angular-momentum compatibility

The [derivation](../../../../BOUNDARY_CONTROL_HANDOFF.md#78-gaussian-reference-deficit-and-whole-support-compatibility)
uses the existing Gaussian reference and fixed cutoffs. It proves a necessary
whole-support obstruction to exact mean matching by compact internal stresses
with no external transfer/torque. It does not exclude approximate central
features or establish a physically realizable stress/controller.

R183 authorized making SymPy available; R184 permits useful dependency changes.
The optional [dependency file](../../../../requirements-symbolic.txt) records
the versions used. From the repository root, with Python 3.12 available:

```bash
python3.12 -m venv /tmp/navier-symbolic
/tmp/navier-symbolic/bin/python -m pip install -r requirements-symbolic.txt
/tmp/navier-symbolic/bin/python docs/realizability/evidence/r182/check_symbolic.py
```

Use a fresh environment path if that example path already serves another task.
An existing suitable research environment can also install the optional file.
The visualization requirements do not need SymPy.

Observed R183 installation: `/tmp/navier-r183-sympy`, Python 3.12.14,
SymPy 1.14.0 and mpmath 1.3.0. Initial sandbox download failed at DNS; the
approved host retry succeeded. No existing environment or system package was
modified. No FEM dependency is imported by the checker.

[check_symbolic.py](check_symbolic.py) independently differentiates the target
and checks the documented deficit, incompressibility, raw-swirl balance,
transition restrictions, cutoff joins/integral, integration-by-parts identities
and sign under explicit assumptions. The run passed 21 exact checks; its stdout
is saved in [symbolic_validation.json](symbolic_validation.json). Positivity of
the radial moment follows from the window's nonnegative profile and nonempty
plateau as explained in the derivation; the final symbolic sign check takes
that positive moment as an assumption.

No numerical reference sampling, PDE solve, quadrature experiment, stress
realizability test, boundary-response evaluation or physical run was performed.
The manual review also checked units, all enclosing face terms, the regular
axis limit and the distinction between exact whole-mean and central-feature
matching. Follow the [current handoff](../../../../SESSION_HANDOFF.md#next-task)
for the next bounded task; no attempt allowance is granted by this evidence.
