# Nonlinear verification prototype and fixture review — R195

R196 update: the [cube adapter/diagnostic source](CUBE_ADAPTER_R196.md) is now
implemented and passes 24 import-free checks with these kernels. This historical
review's missing-adapter statements describe R195. FEM execution remains
unadmitted; follow the [current task](../../SESSION_HANDOFF.md#next-task).

2026-09-22; PC/WSL `daisy`. The [isolated source](../../verification/nonlinear_port/README.md)
implements P2/P1 weak-form builders and nonlinear/time iteration kernels.
**Fifteen standard-library checks pass; no FEM stack was imported and no PDE
was solved.** This fulfills R194's source/algebra boundary, with an explicit
remaining adapter boundary: mesh tagging, sparse global block assembly/solve,
field diagnostics and supervised fixture execution are not implemented or
validated. The tank remains unadmitted. Follow the single
[next task](../../SESSION_HANDOFF.md#next-task).

## Exact manufactured problem

Dimensionless unit cube, 0<=t<=1, rho=1, mu=1/10. The four lateral faces have
exact Dirichlet velocity. z=0 and z=1 are two independent integral-flux return
groups, with outward normals -e_z and +e_z. This is a verification domain,
not the finite-port tank, physical water parameters or a preparation from rest.

```text
A=1+t+t^3, C=1/2+t, E=1+t^2+t^3, H=1+t,
X=x^2(1-x)^2, Y=y^2(1-y)^2, psi=E X Y,
u=(-A x+psi_y, -A y-psi_x, 2 A z-C),
p=H (x^2+y^2+z^2-1).
```

Here `u` denotes velocity (the `u=` line is not kinematic viscosity).
Divergence vanishes identically; pressure has exactly zero volume mean.
Velocity is non-affine, convection is nonzero, and the cubic time dependence
avoids a trivial exact BDF2 derivative. The swirl and its lateral trace vanish
on the four Dirichlet faces. The affine lift (-Ax,-Ay,2Az-C) therefore supplies
exact boundary data in P2, is divergence-free, and has exactly compatible cap
fluxes. No interpolation-induced aggregate flux correction is necessary on
an affine cube. This fact does not transfer to curved tank boundaries.

Define f=rho*(u_t+div(u tensor u))-div(sigma), sigma=-pI+2mu D(u).
The retained rational-polynomial generator evaluates every component, derivative
and integral without symbolic/FEM dependencies. An independent advective-form
check uses f_i=u_i,t+u_j partial_j u_i+partial_i p-mu Laplacian(u_i).
For example f_z=2(1+3t^2)z-1+2A(2Az-C)+2Hz, a separate closed expression.
These loads are verification devices only.

For side s=0 or 1, define prescribed traction offset g_s by
sigma n=-P_s n+g_s. The exact constants and totals are:

```text
Q_-=C, Q_+=2A-C, Q_lateral=-2A,
P_s=H*(s-1/3)-4mu A,
g_s=-H*(x^2+y^2-2/3)*n_s.
```

Both caps have positive outward normal velocity throughout the interval. Their
flux split varies with time and differs between caps. Each offset has zero
area-mean normal component; tangential offsets are zero for this fixture.
The offsets are nonconstant normal loads, not a hidden specification of the
unknown constants. Adding a constant to p and both P_s leaves the equations
unchanged. Do not replace these data by the tank's zero-offset closure.

Exact whole-cube angular momentum and energy checks retain **all six faces**,
body torque integral(x f_y-y f_x), body power integral(u.f), physical traction,
advective flux, storage and symmetric-gradient dissipation. Nonzero terms close
as rational polynomials in t; the tests do not merely compare numerical residuals.
They verify continuum identities, not discrete conservation.

## Independent oracles and time isolation

Plane Poiseuille: u=(4y(1-y),0,0), p=8mu(1/2-x), f=0. Its unit-span flux is
2/3 and streamwise pressure drop 8mu. On x-normal sections the physical shear
traction includes sigma_yx=4mu(1-2y); pressure-only outlet traction would be wrong.
For a future cube fixture using the same z returns, prescribe the exact trace
on all lateral faces and supply exact z traction offsets. The z faces are not
stationary no-slip walls. This verifies plane Poiseuille, not square-duct flow.

Rigid rotation: u=(1/2-y,x-1/2,0),
p=((x-1/2)^2+(y-1/2)^2-1/6)/2, f=0. D(u)=0 exactly, including shear;
centrifugal pressure balances convection. The same lateral traces and z-normal
traction prescription apply. Zero cap totals are valid in these two special
oracles. Use nonzero sums of absolute boundary flux contributions for the
compatibility scale even if the net Dirichlet flux vanishes.

For temporal convergence use `affine_time()`:
u=(-Ax,-Ay,2Az-C), p=H(x+y+z-3/2). Both spatial fields are exactly representable
in P2/P1. The return constants are P_s=H(s-1/2)-4mu A and offsets
-H(x+y-1)n_s. Use continuous exact f, initial u(0), one backward-Euler startup
step and then fixed-step BDF2. This separates time error from spatial error.
The actual time-loop check integrates y'=3t^2 and observes error ratios above
3.5 for the three step sizes. This is an ODE check, not a Navier–Stokes result.

For spatial convergence the non-affine fixture uses one backward-Euler step
with its **discrete exact time difference** in the manufactured load. Previous
exact polynomial data must enter the load as exact expressions, not interpolated
P2 histories; equivalently add rho*(D_BE u_exact-u_exact,t) and cancel the known
history contribution consistently. Otherwise interpolation of the prior field
adds an undeclared spatial load error. Continuous exact forcing is retained
for the separate temporal test; these two error studies are labelled distinctly.

## Gauge, rank and implementation choice

R194 requested a mean-zero pressure space with two return multipliers. The
source uses its algebraically equivalent bordered realization: full P1 pressure,
one scalar eta added to continuity, and the row integral(p)=0. Unknowns are
(u,p,P_-,P_+,eta). The extra row/column avoids inventing a pressure-only nullspace
and avoids a global mean-zero basis transformation in the future sparse adapter.
This is an implementation choice, not a changed physical boundary condition.

For all q in full P1, (q,div u)+eta*(q,1)=0. Constant q gives
eta*volume=-integral_boundary u.n. With compatible imposed totals, eta=0;
the remaining equations are exactly the mean-zero formulation. **An incompatible
flux can be absorbed by eta**, so a run must first reject incompatible assembled
boundary totals and must separately check eta afterward. It must never accept
the bordered solve's small residual as proof of compatibility.

The exact rank toy uses velocity coordinates v0,v1,v2, divergence rows
B_const=(1,1,0), B_zero_mean=(0,0,1), and flux rows C_-=(1,0,0), C_+=(0,1,0).
With nonsingular diagonal velocity block, the ungauged 7x7 matrix has rank 6
and joint null vector (0,0,0,1,0,1,1). A pressure-only shift is not null.
The mean-zero reduced 6x6 matrix has rank 6; the bordered 8x8 matrix has rank 8.
This confirms the structural count; **actual mesh constraint rank and inf-sup
stability remain unmeasured**. Compatible fluxes do not alone prove full rank.

The arithmetic compatibility limit is 128*epsilon*condition*sum_abs_terms,
with a reported condition bound between 1 and 1e6; larger/unknown conditioning
refuses admission. The future adapter must obtain the term sum from quadrature
contributions, and report its conditioning estimate and method. The helper only
checks supplied values; it does not measure geometry or conditioning.

Install the new time-dependent Dirichlet values in the entire state before
computing residuals. Keep continuity, both flux rows and gauge residual intact;
set only constrained Newton increments to zero, eliminating their columns and
replacing their momentum rows by identity. The lifting test demonstrates why
zeroing coupled residual rows would lose a prescribed contribution. Previous
and older full velocities retain their historical lifts.

## Weak form and iteration source review

The builder retains rho*d_t u, conservative -rho*(u tensor u,grad v),
2mu*(D(u),D(v)), -p*div(v), q*div(u), eta*q and -f.v in the volume.
On each return it adds rho*(u.n)*(u.v)+P_s*(v.n)-g_s.v.
Test velocity vanishes on the Dirichlet faces, so their convective boundary
integrals vanish in these equations, while diagnostic budgets still include them.
The full nonlinear derivative includes both factors of return convection.
Separate scalar rows impose both Q_s and pressure mean; scalar-scalar blocks
are zero. The returned pressure columns have **positive** normal-test sign.

`newton()` uses exact Jacobian callbacks, fixed scaling, checked linear
corrections, residual convergence and bounded backtracking. `advance()` supplies
BE/BDF2 coefficients and only advances history after explicit diagnostic
acceptance. Failure raises a refusal, never an automatic retry or time-step
reduction. These are numerical kernels; the callbacks are not an implemented
DOLFINx adapter, sparse solver, convergence verifier or resource supervisor.

The energy defect from conservative convection is
(rho/2)*integral |u_h|^2 div(u_h), with its sign retained. BDF2 satisfies

```text
(3u-4v+w,u)/2 = [||u||²+||2u-v||²-||v||²-||2v-w||²+||u-2v+w||²]/4.
```

Use the appropriate mass inner product and divide by dt. This discrete identity
and time-integrated physical budgets are distinct checks. No grad-div repair,
upwind damping, turbulence model or pressure-null projection has been added.

The official [DOLFINx demo](https://docs.fenicsproject.org/dolfinx/v0.10.0.post3/python/demos/demo_navier-stokes.html)
was rechecked as a source for library conventions and the distinction from its
full-Dirichlet divergence-conforming method. It does not validate this mixed
P2/P1 prototype. UFL forms have been syntax/source reviewed only; they have not
been constructed, compiled or assembled.

## Future manifest review and stopping boundary

The [manifest](../../verification/nonlinear_port/future_fem.json) freezes existing
FEM pins, affine cube levels 2/4/8, separate time steps 1/8,1/16,1/32,
quadrature degrees 24/26, exact error definitions and proposed rates/thresholds.
Errors are physical L2 norms, velocity H1 seminorm, mean-zero pressure L2,
strong divergence L2 and physical-stress traction L2 on both cap unions.
Each ordered adjacent refinement pair must decrease above the 1e-10 error floor
and meet the stated log2 error-ratio gate. Below-floor errors are labelled
roundoff-limited, never assigned fictitious rates. P errors and cap fluxes use
individual signed differences; gauge and eta use absolute values.
Pressure-multiplier errors must decrease across the spatial sequence and be
below 0.02 at the finest level. Quadrature checks use max(1e-10,abs(value)) scales.

Angular/energy budgets include the manufactured body terms and all boundaries.
Normalize integrated defects by sums of absolute contributions, with the stated
absolute floor. Keep instantaneous terms and time integration separately.
Spatial-study budgets must identify discrete manufactured forcing; do not test
them as an unforced continuum physical flow. Poiseuille is an additional single-level n=2 solve before the convergence
sequence; its exactly representable velocity/pressure errors must be <=1e-9,
with all compatibility checks. Rigid rotation instead supplies a constitutive
and centrifugal-balance assembly oracle using its exact polynomial fields:
D(u)=0 and integrated momentum balance must agree within 1e-10. Its quadratic
pressure is not P1-representable; no zero pressure-error PDE gate is imposed.

**Execution admitted: false; attempts granted: zero.** A proposed one-attempt
suite would share 180 s end-to-end and 1536 MiB whole-task/no-swap limits,
one MPI rank/thread, at most 20,000 velocity/pressure unknowns, and retained
exit/cleanup evidence. No fit within those caps has been measured. Setup/JIT,
failed cases, cleanup and report saving all count; exhaustion is inconclusive,
not permission to retry, relax a gate or use an under-resolved tank.
The [practical policy](B2_MONITOR_PRACTICAL_SUPERVISION_POLICY.md) applies without
reopening recursive infrastructure certification. No physical attempt is spent.

Next implement/review only the small cube adapter, diagnostics and launch
contract, with import-free checks, before deciding whether any tiny FEM fixture
is admitted. No FEM imports/JIT, mesh, assembly or solve is authorized by this
review. Early Mac work is limited to these portable algebra checks after an
explicit normal handoff; no machine transfer now. Tank resolution, geometry,
profile/stub sensitivity, stability, physical feedback and contraction remain
unresolved. B2 accuracy failed; q64/q96 unused; R021 deferred.

Retain GPT-6 Astra/high for mixed-form and adapter review on PC/WSL `daisy`.
[Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-astra)
was fetched with OpenAI Docs and confirms high support. The supplied snapshot
says medium; no switch occurred. Account usage includes another project and is
not a measurement of this repository. A cheaper model recommendation waits
until scientific/assembly choices settle and availability is checked.
