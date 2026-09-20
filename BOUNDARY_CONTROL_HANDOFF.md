# Boundary-control research handoff

Prepared 2026-09-19 against repository commit `1fbd82d`.

## Start here

**Next deliverable: a verified boundary-mode response benchmark, with an honest
account of what its inputs and sensors can resolve.** Do not start with an
optimizer, estimator, full contracting-core simulation, or hardware purchase.

Implement work packages B0–B3 below in order. B0 is useful without any CFD
installation. B1–B3 produce the first actual fluid-response calculation. Return
a short report and reproducible commands at each package boundary. B4 describes
the next research decision; it is not part of the initial coding assignment.

Read `AGENTS.md` and the four research documents it names first. This document
makes their next step concrete. Where older plans suggest tracking optimization
before response experiments, follow `CONTROL_RESEARCH_ROADMAP.md`: response
and sensing studies come first.

The choices below are **proposed research defaults for a reversible numerical
benchmark**, stated here for review. They are not previously approved apparatus
specifications or demonstrated physical results. The coding agent can implement
these defaults without inventing a different geometry, actuator mechanism,
target, or interpretation. Flag a necessary scientific change before adopting
it; routine implementation choices do not need another review.

## 1. Findings from the existing repository

- There is no Navier–Stokes solver, control dataset, or solver verification suite
  here yet. `make_trajectories.py` prescribes velocities and clips escaped
  tracers. Its displayed `CoreRadius` is a separate animation formula, not a
  radius measured from the velocity field. Neither is a CFD initial condition
  or validated target trajectory.
- `tank.inc` depicts a box; `actuators.inc` depicts internal rings. An internal
  ring of objects is not a continuous fluid-domain boundary. The new benchmark
  must explicitly define its own physical boundary.
- The roadmap's state `[r_c, U_theta, U_z, a_1, ...]` needs measurement definitions.
  Core radius does not exist at rest, and an azimuthal amplitude without phase
  loses information. A scalar positive amplitude is also unsuitable for a
  derivative at zero amplitude.
- The initial environment has Python 3.10.12, NumPy, SciPy, and Matplotlib.
  DOLFINx, PETSc Python bindings, Gmsh, MPI executables, OpenFOAM, Docker, and
  Podman were not found in the initial inspection. Do not report CFD results
  until a solver actually runs. Keep Track A's dependencies unchanged.

The external reference repository describes a periodic, manufactured-force
surrogate, not a bounded-tank boundary-control calculation. Its README also
distinguishes profile contraction from the axial scale and reports unresolved
wave-packet limitations. Importing it is not necessary for the first experiment.
If used later, pin a commit, audit its measured profiles, and specify length,
time, velocity, and viscosity scaling together; a movie does not supply those
scales. [nsblowup source](https://github.com/CokieMiner/nsblowup)

The porous-wall study is relevant background, but reports substantial
limitations on relating its profiles to the motivating construction. It does
not establish that our apparatus works.
[Duraiswami, 2026 preprint](https://arxiv.org/html/2609.17642v1)

The boundary-controllability theorem concerns local steering to an admissible
Navier–Stokes trajectory with mathematical boundary controls. It does not make
an arbitrary manufactured-force target an unforced solution, or supply a finite
actuator count and hardware limits.
[Rodrigues, author preprint](https://www.ricam.oeaw.ac.at/files/reports/12/rep12-12.pdf)

## 2. Decisions and their scope

| Question | Default for the next calculation | Why / alternative retained |
|---|---|---|
| Geometry | Fixed cylinder, radius R = 0.10 m, half-height H = 0.15 m | Exact azimuthal mode definitions and useful symmetry checks. A box and discrete internal hardware remain later geometries. |
| Fluid | Incompressible Newtonian fluid, nu = 1e-6 m²/s, rho = 1000 kg/m³ | Nominal water parameters; record them as assumptions, not measured properties. |
| First operating point | Rest, governed by unsteady Stokes equations | Valid small-signal limit and inexpensive verification. Cannot assess contraction of an established vortex. |
| First CFD backend | DOLFINx, mixed P2 velocity / P1 pressure, Gmsh cylinder | Explicit weak form, boundary basis and sensor operators. Keep a narrow backend interface. |
| Initial inputs | Six balanced normal/tangential modes defined below | Axisymmetric strain/swirl and both phases of m = 4. Expand only after verification. |
| First outputs | Six signed, linear velocity features | Defined at rest; avoid an invented core radius and phase singularity. |
| Reference | Separate, windowed Gaussian-vorticity vortex, 10 mm → 3 mm in 100 s | Explicit finite dimensional target and diagnostic fixtures; not the original mathematical construction. |
| First response tests | Harmonic response at 0.01 Hz, then 0.1 and 1 Hz if resolved; one transient pulse | Harmonic solves avoid waiting thousands of seconds for spin-up. Transients expose finite-horizon limits. |
| First sensing test | Finite pressure patches versus horizontal and vertical planar PIV | Test measurement ambiguities before choosing an observer. |

The cylinder contains about 9.42 liters. Interpret its normal-velocity boundary
as an ideal distributed porous liner with balanced recirculation plumbing. Its
tangential boundary is an ideal distribution of moving surface elements. These
are two different hardware mechanisms; the combined Dirichlet boundary is an
ideal upper-level actuator model, not a finished liner design. A perforated
moving liner or interleaved pumping/shear patches would need separate design.
Endcaps are stationary and impermeable. No free surface, buoyancy dynamics,
or volumetric actuation is included.

OpenFOAM remains an alternative for later finite-port engineering geometries;
spectral elements remain an alternative if resolution/cost demands it. A custom
NumPy projection solver would create substantial verification work. Do not
implement three backends or choose a solver solely to avoid an installation.

Use the versioned DOLFINx 0.10.0 examples as the initial reproducible API target;
this is a deliberate documented version, not a claim that it is the latest.
Pin the compatible environment actually installed, including PETSc scalar type,
MPI, Basix, UFL, FFCx, and Gmsh. A different version is acceptable if documented
and verified against its matching examples. The official download page is the
installation starting point; do not make unreviewed system-wide changes.
[Installation](https://fenicsproject.org/download/),
[mixed Stokes example](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/demos/demo_stokes.html),
[Gmsh integration](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/demos/demo_gmsh.html)

## 3. Physics questions resolved before coding

### 3.1 Flux balance is instantaneous; zero mean over a cycle is insufficient

For the fixed incompressible domain, every prescribed boundary field must obey
`integral_boundary u · n dS = 0` at every instant. An axisymmetric side-wall
inflow with closed endcaps is invalid unless another part of the side wall
returns the same volume. Pressure cannot repair incompatible Dirichlet data.

For diaphragms, displacement is the time integral of wall velocity. A command
that is valid as pump flow may exhaust a diaphragm's stroke. For a sinusoid,
`stroke_amplitude = velocity_amplitude / (2*pi*f)` and
`acceleration_amplitude = 2*pi*f*velocity_amplitude`. A DC velocity has unbounded
stroke. Finite wall motion requires moving geometry or a justified small-motion
linearization; a fixed permeable wall is not a literal moving diaphragm.

Use recirculation ports as the normal-actuation interpretation in this first
study. Synthetic-jet rectification is nonlinear and absent from a Stokes model.
Tangential no-slip speed is not automatically equivalent to an angled jet.

### 3.2 Viscous diffusion time is not a specification for actuator bandwidth

`L²/nu` is a diffusion estimate. It does not establish that oscillating the
outer wall at `nu/r_c²` will control a core of radius `r_c`.

For illustration, the planar oscillating-wall diffusion length is
`delta = sqrt(nu/(pi*f))`, obtained by inserting a harmonic velocity into the
one-dimensional diffusion equation. For the nominal viscosity:

| f (Hz) | delta (mm) |
|---:|---:|
| 0.01 | 5.642 |
| 0.1 | 1.784 |
| 1 | 0.564 |
| 30 | 0.103 |

The wall is about 90 mm from a 10 mm core; `(0.09 m)²/nu = 8100 s`.
These estimates motivate a penetration study. They are not universal attenuation
laws for the vessel: normal pumping also produces pressure-mediated flow, and
an established circulation advects vorticity. Failure of tangential diffusion
from rest does not falsify control around a pumped vortex.

### 3.3 Straining tracer trajectories and shrinking a viscous vortex differ

For `u_r = -a r`, a material radius satisfies `d(log r)/dt = -a`. A viscous
Gaussian vortex also spreads. If its vorticity width is b and circulation is
constant, substitution into the axisymmetric vorticity equation gives

```text
d(b²)/dt = 4*nu - 2*a*b².
```

Thus the target strain must pay for diffusion as well as contraction. Section 5
uses this relation. A stationary straining Gaussian vortex is the classical
Burgers-vortex baseline; its unbounded-domain properties do not establish
stability or realizability in this tank.
[Gallay and Maekawa](https://arxiv.org/html/1002.2489)

### 3.4 Some sensor and actuator limitations follow without CFD

- Axisymmetric pure swirl in the linear Stokes equations about rest has constant
  pressure. Its viscous diffusion does not produce a first-order pressure
  signature. Pressure-only observation therefore has an exact blind direction
  in that benchmark. Around a nonzero swirl, centrifugal pressure has a linear
  perturbation proportional to base swirl times perturbation; recompute there.
- One vertical 2D/2-component PIV sheet misses the azimuthal velocity normal to
  that sheet. Even stereo PIV in one vertical sheet does not recover arbitrary
  azimuthal phase information around a full circle.
- N equally spaced samples require `N >= 2*M + 1` to represent a constant and
  both quadratures through azimuthal order M. Eight devices lose one independent
  phase at m = 4; twelve do so at m = 6. Sixteen support both through m = 6.
  Offsetting an entire ring rotates the missing phase but does not restore rank.
  Finite footprints further filter modes. This applies to sensor rings too.
- A nonzero `mean(u'_r*u'_theta)` is a correlation, not proof of changed mean
  momentum. Its spatial transport/divergence and the remaining momentum terms
  must eventually be measured or computed.

These are deductions for the stated models, not numerical results from this
repository. Include them as independent checks on later code.

### 3.5 Boundary control cannot reproduce every forced target pointwise

Suppose an unforced solution agrees exactly with a smooth target u* throughout
an open interior region over a time interval. In that region its momentum
residual must be a pressure gradient:

```text
R* = partial_t u* + (u* · grad)u* - nu*laplacian(u*)
curl(R*) = 0.                          # necessary local condition
```

If this curl is nonzero, changing boundary controls cannot make that exact
interior target an unforced solution. A boundary-controlled pressure gradient
cannot cancel a rotational volume-force residual there. This is a local
necessary condition, not a global existence or realizability theorem; it also
does not rule out approximate matching of a few measured features.

For any later imported target, check this residual in the proposed comparison
region before optimizing full-field tracking. Our Gaussian reference satisfies
the unwindowed axisymmetric vorticity balance in its central plateau; its
windowed exterior is deliberately not claimed to be an unforced solution.
This is another reason to report reduced-observable success precisely.

## 4. Boundary basis: explicit, balanced, and small

On the cylindrical side wall let `s = z/H`, `theta = atan2(y,x)`, and define

```text
w(s)  = (1-s²)²
Z0(s) = w(s)
Z1(s) = s*w(s)
Z2(s) = (s² - 1/7)*w(s).
```

All vanish smoothly at the endcaps. On `[-1,1]`, `integral Z1 ds = integral Z2
ds = 0`; `integral Z0 ds = 16/15`. The `1/7` follows from
`integral s²*w ds / integral w ds`. Define each vector basis field by

```text
N_mkc = e_r     * Zk(s)*cos(m*theta)   # normal, outward positive
N_mks = e_r     * Zk(s)*sin(m*theta)
T_mkc = e_theta * Zk(s)*cos(m*theta)   # tangential
T_mks = e_theta * Zk(s)*sin(m*theta).
```

Set all fields to zero on the endcaps. Omit sine modes at m = 0. For m = 0
normal actuation, allow k = 1,2 only; `N_00c` is incompatible and must raise an
error. For m >= 1, all k = 0,1,2 have zero continuous flux. Tangential modes
allow all three k. Normalize every retained field to unit maximum speed;
store the normalization. Its scalar coefficient then has units m/s.

Start with these six columns, in this exact order:

```text
N_02c, T_00c, N_40c, N_40s, T_40c, T_40s.
```

Positive `N_02c` injects inward near the midplane and returns outward above
and below. This is a proposed strain-producing geometry, not a guarantee of
the desired interior strain. Add `N_01c` later as an axial-parity check. The
complete m = 0...6, k = 0...2 set has 77 modes; do not launch that sweep first.

On a faceted/curved numerical mesh, analytic `e_r` may not equal the discrete
normal. Measure flux on the actual mesh with the actual imposed boundary
trace. Correct a small quadrature/interpolation residual using a smooth
side-wall return function that vanishes at the rims, and record the correction.
Reject a large residual rather than hiding incompatible physics. Verify that
the correction tends to zero with geometry refinement. Never distribute a
constant correction over supposedly impermeable endcaps.

Retain the boundary Gram matrix `M_ij = integral_side b_i · b_j dS / S_side`.
Peak-normalized polynomials need not be orthogonal; coefficient Euclidean norm
is not necessarily boundary RMS speed. Check M is positive definite for the
retained basis and report its condition number.

## 5. An explicit finite reference and feature definitions

### 5.1 Reference field, implemented separately from Track A

Use this as a diagnostic/reference fixture first. It is not the state about
which the initial rest-response calculation is linearized.

```text
T = 100 s;  0 <= t <= T
r0 = 0.010 m;  rf = 0.003 m
r_c(t)² = r0² + (rf²-r0²)*t/T
q = positive nonzero root of exp(q) = 1 + 2*q
q = 1.256431208626...
b(t)² = r_c(t)²/q
a(t) = [4*nu - d(b²)/dt] / [2*b²]
Gamma = 2*pi*r0*(0.010 m/s)/(1-exp(-q)) = 8.7835949054e-4 m²/s
u_theta_raw = Gamma/(2*pi*r) * [1-exp(-r²/b²)]
```

Evaluate the swirl with
`-expm1(-r²/b²)` and use its regular axis limit. In Cartesian form its angular
coefficient tends to `Gamma/(2*pi*b²)`; do not divide by an arbitrary epsilon.
The peak swirl radius of the raw profile is exactly `r_c`.

Create C2 cutoffs f(r), g(z), equal to one for `r <= 0.04 m`, `|z| <= 0.05 m`,
and zero for `r >= 0.08 m`, `|z| >= 0.12 m`. In each transition use
`1 - (10*v³ - 15*v⁴ + 6*v⁵)`, with v running from 0 to 1. Set

```text
psi(r,z,t) = a(t)*z*r²*f(r)*g(z)
u_r = -(1/r)*partial_z psi = -a*r*f*(g + z*g')
u_z =  (1/r)*partial_r psi =  a*z*(2*f + r*f')*g
u_theta = u_theta_raw*f*g.
```

Use analytic derivatives and regular Cartesian axis limits. This construction
is divergence-free, includes a return flow, and vanishes near all boundaries.
It agrees with the intended straining Gaussian profile in the central region.
The windowed time-dependent field is **only a reference**, not an unforced
bounded-domain Navier–Stokes solution; its exterior generally needs a residual
force. Do not apply that residual in boundary-response runs. A reference with
zero wall trace still cannot be sustained by prescribing zero wall velocity.

Values independently calculated while preparing this handoff:

| t (s) | r_c (mm) | a (1/s) | peak swirl (m/s) |
|---:|---:|---:|---:|
| 0 | 10.000 | 0.029679 | 0.010000 |
| 50 | 7.382 | 0.054456 | 0.013546 |
| 100 | 3.000 | 0.329762 | 0.033333 |

The passive-radius estimate alone would give initial a = 0.00455/s, missing
the viscous contribution. The target has `U_peak*r_c/nu = 100`; a rest Stokes
calculation cannot be extrapolated to it. The time scale 100 s and circulation
are chosen benchmarks, not optimized experimental settings. Repeat the target
arithmetic for T = 30 and 300 s to expose the time/strain tradeoff; no CFD is
needed for that sensitivity table.

### 5.2 Linear features for the first response calculation

Use fixed, laboratory-coordinate sampling regions and physical quadrature
weights. Do not move the measurement annulus with the observed core.

- Horizontal disk D: `z = 0`, `r <= 0.025 m`, measuring u_x,u_y.
- Vertical rectangle V: `y = 0`, `|x| <= 0.025 m`, `|z| <= 0.025 m`, measuring
  u_x,u_z. Boundaries of these regions are diagnostic masks, not fluid walls.
- Horizontal annulus A: `z = 0`, `0.015 <= r <= 0.025 m`.

Define

```text
a_z   = integral_V z*u_z dA / (2*integral_V z² dA)
Omega = integral_D (x*u_y-y*u_x) dA / integral_D r² dA
C_jm  = 2*integral_A u_j*cos(m*theta) dA / area(A)
S_jm  = 2*integral_A u_j*sin(m*theta) dA / area(A),  j in {r, theta}
x_lin = [a_z, Omega, C_r4, S_r4, C_theta4, S_theta4].
```

Subtract the angular mean when forming perturbation fields and stresses;
the m > 0 integrals already reject it in exact quadrature. Save the additional
check `a_r = -integral_D (x*u_x+y*u_y) dA / integral_D r² dA`. In the central
linear reference, `a_r = a_z = a`. Omega is a signed fitted rotation rate,
not peak swirl speed and not circulation. Units are 1/s for a_z,Omega and m/s
for Fourier coefficients. Generalize to m = 1...6 only after the pilot.

### 5.3 Features for a later nonzero vortex

On the horizontal plane, compute an azimuthally averaged signed swirl profile
about a reported center. For synthetic fixtures the center is the origin; for
CFD/PIV fit and report the center separately. Preserve fixed-origin m = 1
coefficients so recentering does not erase displacement errors.

Define `r_c` as the radius of a unique, resolved interior maximum of the swirl
profile magnitude in `0 < r < 0.025 m`; retain its sign in `U_peak`. Return an
invalid flag with a reason if the peak is at the edge, below noise, unresolved,
or not unique. At rest use invalid, never `r_c = 0`. Fit the Gaussian profile
only as a secondary estimate and report its residual; do not force all CFD
vortices into that family. Sample spacing should start at <= r_c/10 and be
refined. Keep a_z instead of ambiguous mean U_z: symmetric axial stretching
has zero volume-average axial velocity.

On A, report `R_rtheta = mean_A[(u_r-mean_theta u_r)*(u_theta-mean_theta
u_theta)]`, with angular means at each radius and area weighting afterward.
For radial-constant single-mode spatial fixtures its angular average is
`(C_rm*C_thetam + S_rm*S_thetam)/2`. Distinguish this from a time average: an
additional common sinusoidal time factor contributes another factor 1/2.
The m = 4 target is initially zero; use controlled perturbations to study it,
not an unvalidated wave packet grafted into the reference field.

## 6. Fluid solver contract and verification

### 6.1 Solve the equations being claimed

For B1–B3 solve, with pi = p/rho,

```text
partial_t u = -grad(pi) + nu*laplacian(u),   div(u) = 0
u|side = sum_j A_j(t)*b_j;                 u|caps = 0.
```

For harmonic convention `u(t) = real(u_hat*exp(i*omega*t))`, solve

```text
i*omega*u_hat - nu*laplacian(u_hat) + grad(pi_hat) = 0
div(u_hat) = 0.
```

Use a mixed saddle-point solve, not a pressure-Poisson shortcut with invented
pressure boundary data. For test velocity v with homogeneous boundary trace,
the momentum weak form is
`i*omega*(u,v) + nu*(grad u,grad v) - (pi,div v) = 0`, with `(div u,q) = 0`.
For complex scalars use conjugated test functions consistently. A real PETSc
build can instead solve the coupled real/imaginary equations with mass blocks
`-omega*M*u_imag` and `+omega*M*u_real`; test both signs against a known response.

All velocity boundaries are Dirichlet. Pressure has a constant nullspace: impose
a zero spatial mean or a proper pressure-only nullspace and solve the compatible
system. For a real/imaginary formulation there are two pressure gauges. Do not
make the entire mixed vector constant when constructing a nullspace. Convert
pi to Pa for sensor outputs. The official mixed example and
[PETSc nullspace documentation](https://petsc.org/release/manualpages/Mat/MatNullSpaceCreate/)
are implementation references.

Start in serial. Cache geometry and operators and reuse factorizations or
preconditioners across right-hand sides at a fixed frequency. Keep full-field
outputs optional. A two-dimensional planar solver cannot model m = 4 around
a three-dimensional vortex. A Fourier-separated cylindrical implementation is
a later optimization, not the initial backend.

### 6.2 Verification before a response sweep

1. Zero boundary and initial data: zero velocity and pressure up to gauge.
2. Exact steady affine field on a verification domain:
   `u = (-a*x-Omega*y, -a*y+Omega*x, 2*a*z)`, constant pressure, prescribed
   on the entire boundary. It solves steady Stokes with no volume force.
   Check velocity, signs, pressure gauge, and divergence. These boundary data
   are a verification fixture, not the production side-wall actuator basis.
3. A smooth divergence-free manufactured unsteady solution on a unit cube:
   set `F = sin(pi*x)^2*sin(pi*y)^2*sin(pi*z)^2`,
   `u = exp(-t)*curl(0,0,F)`, `pi = sin(2*pi*x)*sin(2*pi*y)*sin(2*pi*z)`.
   Derive its forcing independently, impose its exact trace, and verify spatial
   and temporal convergence. Manufactured volume force is allowed **only in
   this clearly labeled verification case**. The production driver must reject
   nonzero volume forcing. Translate this fixture into a harmonic one if needed.
4. Pressure gauge shift leaves pressure differences and velocity unchanged.
5. Each actual boundary trace satisfies flux compatibility. Record
   `abs(integral u·n)/integral |u·n|` for normal inputs; for tangential inputs use
   `abs(integral u·n)/(S_side*U_probe)` instead of a zero denominator.
6. Check linear scaling/sign and superposition, angular phase covariance,
   m = 0 versus m = 4 separation, and the axisymmetric swirl pressure null.
7. Zero-input transient viscous decay: kinetic energy decreases. If computing
   boundary work, include pressure/viscous work and kinetic-energy transport
   through permeable walls as appropriate to the stated equations.

Use three spatial resolutions for smooth manufactured fields; demonstrate the
expected convergence trend rather than hardcoding one formal rate at every
coarse level. For production response, compare at least two resolved meshes
and refine again if differences are appreciable. Start with central h <= 2 mm,
wall-normal h <= delta/4, and azimuthal spacing <= one m = 4 wavelength/16.
These are starting grids, not convergence certificates. At 1 Hz the wall layer
is much thinner than 2 mm. Never label an underresolved small gain as zero.

Record dimensionless divergence `L*||div u||_L2/||u||_L2`, algebraic residual,
boundary residual, and integrated flux. Taylor–Hood enforces incompressibility
weakly, not pointwise. Suggested engineering acceptance targets are flux ratio
< 1e-8 after correction, scaled algebraic residual < 1e-9, and divergence ratio
< 1e-3 with a decreasing refinement trend. Use absolute residuals for zero-flow
fixtures. Report actual values and failures; do not relax thresholds silently.

Resolve dominant gains to 5% and phases to 5 degrees across refinement. Phase
is meaningless below the measured numerical error floor. Weak singular values
need an absolute matrix-error comparison, not just the dominant-gain check.

## 7. Response experiments and defensible interpretation

### 7.1 Pilot dataset

Use physical probe amplitude `U_probe = 1e-7 m/s`; `U_probe*R/nu = 0.01`.
This sets a small-amplitude rest linearization. Solve numerically in sensible
scaled units and convert outputs back to SI, rather than relying on tiny
unscaled residuals. Large-amplitude hardware commands are not validated by
rescaling a Stokes solution.

Run all six columns at 0.01 Hz first. Add 0.1 Hz, then 1 Hz only after the
corresponding wall layers and solver cost are checked. Save complex gain and
phase for velocity features and sensor channels. An optional f = 0 Stokes solve
is an infinite-settling-time comparison, not a finite-time achievable gain.
Harmonic response likewise assumes periodic steady state.

For `N_02c` and `T_00c`, also start from rest and prescribe
`A(t) = U_probe*sin(pi*t/10 s)^2` on 0...10 s and zero afterward. Integrate to
100 s, initially dt = 0.1 s, with backward Euler; halve dt and compare features.
Use the same mixed spatial formulation. This finite pulse is not a normalized
Dirac impulse. Save the actual input, its integral, displacement interpretation,
and response. If the core has barely responded, report that and the diffusion
estimate; an optional longer run requires a cost estimate, not an automatic
10,000-second simulation.

### 7.2 Scaling and singular values

Let G(omega) map physical mode velocities to the six physical features. Save G
before normalization. Set L = R and output scales

```text
D_x = diag(U_probe/L, U_probe/L, U_probe, U_probe, U_probe, U_probe)
G_scaled = inverse(D_x) * G * U_probe * inverse_sqrt(M).
```

Here M is the physical boundary Gram matrix. This compares equal boundary RMS
velocity; it does not equate hardware power or equal actuator stroke. Preserve
the transform to actual mode coefficients. Later hardware-constrained studies
must use their own documented effort and output-error budgets.

Compare normal-only, tangential-only, and combined matrices. Report all
singular values, left/right singular vectors, null output directions, and
singular values before and after scaling. Raw mixed-unit singular values are
stored for reproducibility only; they have no unit-independent interpretation.
For a rectangular or rank-deficient
matrix, state how many of the six output directions are absent. Do not report
a finite condition number on its nonzero subspace as full six-state coverage.

Estimate matrix uncertainty from mesh/time-step/quadrature refinement after
using identical coordinates and normalization. Mark a singular value reliable
only if it exceeds, conservatively, ten times the estimated spectral-norm
matrix error. Separately show sensor/noise resolution. This factor is a
reporting convention, not a physical controllability threshold.

Call these **frequency-dependent input-to-feature gains**. They are not a
controllability Gramian. Stacking output times for one pulse measures response
signatures, not arbitrary finite-horizon controllability. For a later
finite-horizon reachability calculation, columns must correspond to independent
input time functions and outputs at the same terminal time; normalize by their
space-time input Gram matrix. Report the horizon and zero initial perturbation.

Do not fit `dot(x_lin) = A*x_lin+B*u` just because x_lin is short. These features
need not be a closed dynamical state. If a reduced dynamical model is introduced,
validate its predictions on held-out input histories and retain unresolved
state/memory effects. A weak response about rest is a result about rest, the
chosen boundary, frequency, and outputs only.

## 8. Sensor experiment: distinguish visibility from observability

Save sensor operators now, before any feedback code:

- Pressure: averages over finite side-wall patches centered at z = -0.08,0,0.08 m,
  with 16 evenly spaced angles per ring; initial patch extent 5 mm in arc length
  and 5 mm in height. Compute differences to a declared reference patch and
  account for shared-reference noise covariance. This 48-patch layout is an
  ideal comparison, not a commitment to buy 48 sensors. Compare decimated
  8-per-ring and 4-per-ring layouts and document the aliasing.
- Horizontal 2C PIV: u_x,u_y on z = 0, field of view x,y in [-0.03,0.03] m.
- Vertical 2C PIV: u_x,u_z on y = 0, field of view x,z in [-0.03,0.03] m.
- Start with 1 mm spatial averaging cells and 0.5 mm sheet thickness. Make
  masks explicit. These are proposed measurement resolutions, not instrument
  specifications; 3 mm core work will need refinement/error checks.
- Compare pressure only, each sheet alone, and both sheets. Simultaneous sheets
  require synchronized optical hardware; sequential acquisition has separate
  timestamps and cannot be treated as simultaneous in a transient experiment.

Use provisional sensitivity sweeps, not fabricated sensor specifications:
pressure standard deviation 0.01, 0.1, 1 Pa; velocity standard deviation 0.0001,
0.0005, 0.001 m/s. Use 50 Hz PIV with 40 ms latency and 200 Hz pressure with
5 ms latency as explicitly hypothetical timing cases. Propagate averaging,
shared-reference covariance, and temporal sampling. Report when the physical
U_probe is far below these noise levels; conditioning alone is not SNR.

Input-to-sensor transfer functions are not state observability. A driven
pressure signal may simply reveal the known command. Do not regress sensors
against six features and assume a unique mapping `y = H*x_lin` exists.

For B3, construct a small declared family of divergence-free, homogeneous-wall
initial perturbations using curls of smooth potentials, then evolve with zero
boundary perturbation. Include independent radial/axial shapes with identical
or similar x_lin, not only states reached by the six input columns. A concrete
first family is `curl(A)` on a unit cube mapped inside `|x|,|y| < 0.03 m`,
`|z| < 0.05 m`: use compact C2 bumps and each Cartesian direction for A, with
constant, x, y, z polynomial factors. Normalize their velocity fields by
kinetic-energy inner product and remove numerical dependencies. Also include
an explicitly axisymmetric compact pure-swirl perturbation for the pressure
blind-direction test. Record all shapes; the conclusions apply to this family.
Project initial fields into the discretely divergence-free, homogeneous-wall
velocity space and report projection error; interpolation alone need not
preserve discrete incompressibility.

Let columns of Q be normalized desired-feature signatures of these states at
t = 0, and columns of P be their noise-whitened sensor histories over a stated
observation horizon, initially 10 s. With identical known inputs, target
features are identifiable on this family only if `ker(P) is a subset of
ker(Q)`. Compute Q acting on P's numerical nullspace, and quantify near-null
directions relative to noise and discretization error. Validate on held-out
linear combinations. This asks whether sensor histories distinguish the
features of the initial state; an online estimator of the evolving state is
a separate later task. Do not claim full-flow observability from a finite test
family. A positive result warrants a richer family; a null direction is a
useful counterexample.

## 9. Coding work packages and acceptance criteria

Keep the first change set small enough to review. Suggested organization:

```text
realizability/
  __init__.py
  config.py                 # SI units, validation, canonical mode ordering
  boundary_modes.py         # analytic basis, normalization, flux and Gram matrix
  reference.py              # independent divergence-free target fixture
  observables.py            # quadrature, signed features, invalid-core handling
  sensors.py                # masks, averaging, reference-pressure operator
  response.py               # normalization, error-aware SVD, nullspace checks
  cli.py                    # preflight / verify / response / sensors subcommands
  backends/fenicsx_stokes.py # loaded only for PDE work
configs/realizability/      # small versioned JSON configuration files
tests/realizability/        # NumPy tests separated from optional solver tests
docs/realizability/         # setup instructions and compact scientific reports
results/realizability/      # ignored generated arrays, meshes and field files
```

Use Python/NumPy/standard library for B0; isolate optional CFD dependencies.
SciPy and Matplotlib can support later analysis/plots in a separate environment.
Do not modify `make_trajectories.py`, the renderer, or the movie scripts for
these packages. Do not build an elaborate plugin framework, dashboard, or
generic experiment service.

### B0 — Pure-Python scientific contract and preflight

Implement configuration, boundary modes, target evaluator, quadrature and
features, SVD normalization, and a small preflight report. Add the new results
directory to `.gitignore`. Use fixed seeds for noisy fixtures; exact quadrature
and analytic fixtures should be deterministic without randomness.

Required independent checks:

- Axial integrals above; reject N_00c; peak normalization and positive Gram matrix.
- Discrete azimuthal design-matrix ranks for 8,12,16 samples and M = 6 are
  respectively 8,12,13. Both m = 4 quadratures fail with eight equal samples.
- Finite-difference divergence of the target decreases under refinement,
  including transition regions; exact boundary velocity vanishes; all values
  are finite on-axis. Compare analytic Cartesian axis limits independently.
- Sampled swirl peaks recover 10 mm, 7.382 mm, 3 mm and the table's velocities
  under radial refinement; rest/multiple/edge peaks return invalid reasons.
- a_r,a_z recover known strain. Fourier coefficients recover signed cosine and
  sine fixtures and the stated angular/time correlation factors.
- Changing units together with the metric leaves scaled singular values
  unchanged. Known rank-deficient matrices report missing output directions.
- A constructed measurement null direction with nonzero Q signature fails
  identifiability; a null direction also in ker(Q) does not.

Generate a concise preflight table including viscous lengths, probe Reynolds
number, reference parameter sensitivity, and ideal ring aliasing. This is a
complete useful deliverable even before CFD dependencies are available.

### B1 — Verified solver, no campaign yet

Install/pin a separate environment using the platform's approval rules.
Implement the verification cases in Section 6, pressure gauge, cylinder mesh
tags, actual boundary-flux check, harmonic and transient solve. Record setup
commands and successful solver versions. Run one normal and one tangential
0.01 Hz pilot before generalizing. If installation is blocked, report the exact
blocker and completed B0 work; do not replace PDE outputs with synthetic gains.

### B2 — Six-input boundary-response report

Run the pilot and convergence checks; expand frequencies only when affordable
and resolved. Compare all three actuator subsets. Save velocity cross sections,
gain/phase plots, scaled spectra with error floors, input budgets, and the two
finite-pulse histories. Include pressure/PIV transfer channels for reuse.

The report must answer: which features responded; which were symmetry-forbidden
or unresolved; whether tangential inputs added independent directions; and how
gain/phase depended on frequency. A converged negative result completes the
package. It is not a reason to tune definitions until a positive result appears.

### B3 — Measurement visibility and limited observability report

Apply finite sensor footprints/noise/timing; compare layouts. Run the independent
initial-state family and the Q/P test. Demonstrate the pure-swirl pressure blind
direction and the value of horizontal PIV. Report the tested state family and
horizon, ambiguous directions, SNR, and missing velocity components. Do not
implement a controller or estimator in this package.

Suggested interface, to implement rather than assume already exists:

```bash
python3 -m unittest discover -s tests/realizability -p 'test_*.py'
python3 -m realizability.cli preflight --config configs/realizability/pilot.json
python3 -m realizability.cli verify --config configs/realizability/pilot.json
python3 -m realizability.cli response --config configs/realizability/pilot.json
python3 -m realizability.cli sensors --config configs/realizability/pilot.json
```

Separate NumPy-only and optional CFD tests so missing solver dependencies are
clearly reported, not counted as successful PDE validation. Before a campaign,
time one solve and record degrees of freedom, memory, and estimated total cost.
Do not automatically launch all 77 modes or high-frequency fine meshes.

Every generated run must record: schema version; repository commit and dirty
state/source hashes; configuration; solver/dependency versions and scalar type;
geometry/mesh hash and boundary tags; nu/rho; initial and boundary conditions;
mode order/normalizations/Gram matrix; forcing status; frequencies or time step
and horizon; sensor masks/units/noise/timing; solver tolerances; convergence
errors; raw and scaled matrices; singular values and error floors; runtime and
memory. Store compact JSON plus CSV/NPZ using relative paths. JSON should use
null plus validity flags for invalid features, not nonstandard NaN tokens.
Retain small reports/configs in Git, not large generated fields.

For inputs also report actual peak and RMS boundary speed, normal volume flow
`Q_in = integral max(-u_n,0) dS`, cumulative stroke where relevant, acceleration,
and frequency. Report ideal boundary traction/work if computed, with conventions.
Pressure demand, pump efficiency, force, and power limits not modeled must say
“not assessed,” not zero or “within hardware limits.”

## 10. B4: what follows, and what still needs scientific judgment

After B0–B3, the next substantial calculation should introduce convection and
a **boundary-generated** base vortex, not a controller. Reuse the mixed backend
for incompressible Navier–Stokes only after nonlinear verification. Ramp the
balanced axisymmetric normal input and tangential input from rest, measure
the resulting core, and test preparation time, saturation, and stability.
There may be no useful localized core for this boundary geometry; that is a
result requiring a design review.

A separately labeled initialized-vortex release experiment is useful to study
maintenance over a short interval, but it does not demonstrate that the
actuators can create the initial vortex. Likewise, linearizing around the
manufactured reference does not remove the nonzero base momentum residual.

For an actual base trajectory u0, the perturbation equation must include both
`(u0 · grad)delta_u` and `(delta_u · grad)u0`. Recompute boundary gains and sensor
signatures about that trajectory, including nonstationarity if appreciable.
Use symmetric perturbations at several amplitudes to distinguish a local
derivative from nonlinear effects. Then assess finite-horizon feature tracking,
finite actuator footprints, amplitude/stroke/flow/bandwidth limits, and robust
sensing before feedback.

Bring back these specific decisions with data, rather than choosing silently:

1. Does the side-wall return geometry form useful axial strain and localized
   swirl, or are endcap ports/a different recirculation path required?
2. Is the relevant failure diffusion from rest, inadequate transport in a
   developed base, finite actuator effort, sensor ambiguity, or numerical error?
3. Which measurable features and contraction interval remain meaningful for the
   resulting vortex? Does its swirl profile even have a unique core radius?
4. What measured or vendor-supported actuator limits and sensor errors replace
   the hypothetical budgets? Which simultaneous PIV arrangement is feasible?
5. Is a different solver/discretization justified by measured cost or accuracy?

The near-term goal is to replace these unknowns with reproducible evidence.
A controller becomes justified only after the available boundary inputs and
measurements have demonstrated useful influence and information around a
physically prepared flow.

## 11. What was checked when preparing this document

The handoff's scalar target values, diffusion lengths, axial flux integrals,
and 8/12/16-sample Fourier ranks were independently evaluated with NumPy.
Sampled swirl-profile maxima reproduced the three tabulated radii to within
0.00025 mm. The proposed reference was finite on-axis and exactly zero at the
tested cylinder-boundary points. A centered finite-difference divergence check
at 2,000 fixed-seed points gave RMS errors approximately 2.12e-6, 5.30e-7,
1.33e-7 /s at spacings 0.1, 0.05, 0.025 mm, respectively.

These are arithmetic and reference-formula checks, not CFD validation. No
boundary-response gains, reachability results, sensor performance, or hardware
feasibility have been computed. Markdown links, code-fence balance, and
whitespace were checked. The visualization code and generated outputs were
not changed.
