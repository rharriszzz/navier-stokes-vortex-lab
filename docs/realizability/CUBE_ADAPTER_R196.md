# Unit-cube adapter and diagnostic review — R196

2026-09-22; PC/WSL `daisy`. Added reviewable, **unexecuted** cube assembly and
field-diagnostic source to the [isolated prototype](../../verification/nonlinear_port/README.md).
Twenty-four standard-library tests pass. No FEM library was imported; no UFL
form was constructed, compiled or assembled; no mesh or PDE solve ran.
**Execution decision: not admitted; zero attempts.** The remaining necessary
work is a small end-to-end fixture driver with concrete supervision and complete
result gates. This is not evidence of a physical contraction or tank solution.
Follow the single [next task](../../SESSION_HANDOFF.md#next-task).

## Adapter choices and review

The six exterior cube faces receive disjoint tags 1..6; z returns are 5 and 6.
A boundary inventory check refuses missing, overlapping or interior facets.
Only affine tetrahedral unit cubes at subdivisions 2/4/8 and one MPI rank are
supported. The mixed P2/P1 space is capped at 20,000 unknowns before form setup.
The three global unknowns follow the mixed vector: P-minus, P-plus, eta.
Scalars are assembled once in the serial communicator, never separately per rank.
The adapter rejects the rotation fixture as a PDE solve; its exact pressure is
quadratic and remains a separate constitutive/balance assembly oracle.

The raw mixed Jacobian is assembled without boundary elimination. The border
adds both positive normal-test pressure columns, the continuity eta column,
both flux rows and the pressure-mean row. All scalar-scalar entries are zero.
Only after the full current trace is installed and **all residual rows** are
assembled are constrained increment columns zeroed and their momentum rows
replaced with identities. Scalar/continuity residuals retain the lift.
The adapter converts trial arguments to test arguments for vector assembly of
constraint rows. It explicitly destroys owned PETSc matrices/vectors/solvers.

R195 Newton accepted dense matrices only. The new CSR branch validates and
multiplies stored nonzeros without allocating an N-by-N dense array. A small
bordering test reproduces the independent full-rank toy matrix and dense
lifting result. A 20,003-entry diagonal test checks the sparse path at the
proposed maximum mixed-plus-scalar dimension; this is not a memory benchmark.
Serial PETSc native LU is explicit, with no ambient `setFromOptions`, nullspace
projection, diagonal shift, fallback or automatic retry. Both solver reason
and the true linear residual must pass. Sparse LU and its cost remain untested.

Unknowns are dimensionless with identity column scales. Row scales are the
inverse of max(1, initial Jacobian absolute row sum), frozen per Newton step.
Physical flux/gauge/eta/error gates remain unscaled. The three constraint rows,
after removing fixed columns, have a 3-by-3 Gram condition/rank screen; the
reported sqrt infinity-norm Gram condition bounds their 2-norm condition.
This is **not** a bound on the whole mixed matrix or an inf-sup certificate.
The later driver must use measured rows and boundary integrals; it cannot insert
an assumed condition of one or claim the algebra toy measures the mesh.

Manufactured spatial BE uses an exact previous-field expression and the exact
BE difference in its load. No interpolated old swirl enters that residual.
The affine temporal study uses continuous forcing and full solved BE/BDF2
histories. Poiseuille uses its exactly representable steady history. These
choices preserve R195's spatial/time error isolation.

Read-only inspection covered the installed DOLFINx 0.10 Python assembly and
boundary APIs in `/tmp/navier-fenicsx/lib/python3.12/site-packages`, alongside
[official assembly API](https://docs.fenicsproject.org/dolfinx/v0.10.0.post3/python/generated/dolfinx.fem.petsc.html),
[mesh API](https://docs.fenicsproject.org/dolfinx/v0.10.0.post3/python/generated/dolfinx.mesh.html)
and [PETSc matrix API](https://petsc.org/release/petsc4py/reference/petsc4py.PETSc.Mat.html).
The implementation is our adapter design, not a library-validated example.
No installed source or environment was modified. Syntax review cannot verify
those calls, scalar type compatibility, quadrature handling or generated forms.

## Diagnostics and scientific limits

Errors include velocity L2/H1, mean-zero pressure L2, divergence L2 and physical
stress traction L2 on both returns. Individual signed flux/multiplier errors,
raw pressure mean and eta remain separate. The six-face angular and energy
budgets retain storage, advection, traction, body torque/work and dissipation.
The energy residual also retains **both**

```text
+ (rho/2) integral |u|^2 div(u)
- integral p div(u).
```

R195 noted the first term but did not implement field budgets. Omitting the
second would leave an incomplete discrete physical-stress identity whenever
strong divergence is nonzero. An independent non-solenoidal polynomial example
has both terms nonzero and closes only with these signs. This is a diagnostic
completion, not a changed weak form or relaxed tolerance.

The diagnostic builder uses rho=1, mu=0.1 and verified unit volume/cap areas,
as frozen for these fixtures. It reports kinetic/angular inventories, discrete
kinetic derivative, momentum time-work and the BE/BDF2 energy decomposition.
Trapezoidal integrated signed terms are labelled as such; a separate physical
endpoint budget substitutes the change in kinetic/angular inventory for the
integrated discrete storage. Their difference is retained. Passing the BDF2
algebraic identity does not certify a physical time-integrated balance.

Rate checks examine both adjacent refinements. Below-floor pairs have no
invented rate; a transition below the floor supplies only a lower bound, and
an insufficient bound refuses acceptance. Quadrature checks preserve the
manifest's max(1e-10, abs(value)) denominator. Missing/nonfinite terms refuse.
A field report never sets an overall accepted flag. Numerical step gates are
necessary only; backflow quadrature samples must come from the later driver,
and only complete suite/exit/cleanup validation could accept a run.

## Concrete bounded launch path and admission decision

Retain the [practical supervision policy](B2_MONITOR_PRACTICAL_SUPERVISION_POLICY.md).
Do not build a general monitor or port the deferred R021 infrastructure.
The useful next deliverable is one fixture-specific entry point, initially for
n=2 Poiseuille, joining the adapter and diagnostics. A subsequent explicit
admission must choose whether that first fixture is a standalone attempt or
part of the proposed suite; **neither is granted here**, and no old allowance
is reset. Full n=2/4/8 convergence is not admitted merely because the tiny
fixture becomes runnable.

The finite launch/report checklist is:

1. Reserve an explicit future attempt in a new, exclusive run directory before
   setup. Bind source commit, manifest hash, fixture, interpreter, owner and
   monotonic start. An existing or interrupted reservation blocks another run.
2. The trusted controller creates a held Linux task scope and verifies actual
   whole-task memory <=1536 MiB, swap 0, PIDs <=32, one rank/thread and independent
   process expiry before releasing any imports/JIT. Use an existing OS manager
   if available; query the effective limits and actual cgroup identity. Include
   compiler/JIT children and task-created reporters in the scope. Shared OS
   services are outside byte attribution; elapsed waits still count.
3. A proposed subdivision of the unchanged 180 s ceiling is 15 s setup,
   <=150 s managed workload and <=15 s cleanup/reporting. Abort on the first
   exceeded allowance; no automatic second attempt or full-suite escalation.
   The managed process expiry is independent of the trusted outer controller;
   end-to-end setup/save time is observed, not recursively certified.
4. Under that scope only, check exact FEM pins and dimensions. The n=2 driver
   starts with a non-exact free-dof guess (exact historical Poiseuille velocity
   and installed lateral trace), requiring at least one verified correction.
   Assemble compatibility/rank, freeze scales, run bounded Newton, collect both
   return quadrature samples and degrees-24/26 diagnostics. Require u/p errors
   <=1e-9 and all applicable flux/gauge/eta/budget gates; no convergence claim.
5. Save `result.json` and a readable log with actual versions, limits, times,
   matrix/dof inventory, condition method, full diagnostics and residual history.
   Separately retain exit reason, cgroup memory peak/events, PID/child inventory,
   setup/JIT/solve/cleanup/save intervals and cleanup observation. Missing data,
   unknown children, overflow, late saving or a failed gate means refused or
   incomplete, never passed. Needed cleanup after expiry is still performed
   and charged honestly; it cannot extend the success ceiling.

No supervisor or end-to-end entry point is present yet. Within the current
restricted namespace, `/proc/1/comm` reported `codex`, `/proc/self/cgroup` was
`0::/`, and the visible root listed memory/pids controllers. These observations
**do not establish host systemd availability, delegation, effective limits or
whole-task enforcement**. A later host check must resolve that before release;
a process-only timeout is not a substitute for the required memory scope.
No host/cgroup configuration was changed. No setup/JIT/solve/cleanup costs have
been measured; they are unknown, not zero. Unknown cleanup blocks another run.

## Evidence, boundary and next step

[Retained evidence](evidence/r196/README.md): 24 import-free tests, syntax/JSON/
link checks and source scope. Sparse border/lifting/rank, Newton failure paths,
face partition, signed non-solenoidal energy balance, rate/floor/quadrature and
missing-output/eta refusals pass. UFL construction, FEM assembly, sparse LU,
actual facet quadrature samples, mesh rank/convergence, resource enforcement
and process cleanup have **not** been validated. No task workload child ran.

Next implement the one-fixture driver and finite supervisor path above, using
mocked supervisor outcomes and import-free checks first; review admission once
those concrete pieces exist. Stop before FEM execution until that decision.
Early Mac validation is portable algebra only after normal ownership handoff;
Mac performance/containment parity does not block this source increment.
B2 accuracy still failed; q64/q96 unused; tank/controller/hardware unadmitted;
R021 launch integration remains deferred. Production sources, scientific
thresholds and dependency pins are unchanged.

Retain GPT-6 Astra/high on PC/WSL `daisy` for this mixed assembly/admission task.
The [official model page](https://developers.openai.com/api/docs/models/gpt-6-astra)
was fetched through OpenAI Docs and lists high support. This is a task-fit
recommendation, not an account entitlement check. The user reports R195 ran
at medium, then changed to high; account snapshots include another project.
Recommend a cheaper model only once remaining work is mechanical and current
availability is checked. PC retains ownership; no delegation or transfer.
