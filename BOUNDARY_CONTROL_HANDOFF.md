# Boundary-control research handoff

Revised 2026-09-22 (America/New_York), R181, from repository `382e7f2`.
The original specification remains in Git history; implemented formulas and
scientific thresholds below are retained unless explicitly labelled proposals.

## Start here

**R181 result:** [Sections 7.5–7.7](#75-finite-annular-angular-momentum-balance)
derive the finite annular angular-momentum budget, give an incompressible
counterexample to midplane-feature sufficiency, and specify offline stress-flux
closure and target tests. A nonzero correlation alone cannot establish the
needed transfer. The [next task](SESSION_HANDOFF.md#next-task) applies the
balance symbolically to the Gaussian reference, including its cutoffs and
whole-support torque compatibility. Section 10's launch integration remains
deferred. R177's benchmark assumptions and numerical gates are unchanged.

**Proposed benchmark: prepare a vortex from rest using the cylinder boundary,
then track the existing 10 mm → 3 mm Gaussian reference for 100 s, while testing
whether strictly boundary-supported measurements distinguish the required
interior features.** This is one finite engineering question with separate
actuation, sensing and numerical verdicts. It is not an achieved contraction,
a final user-approved target, or authorization to run the experiment.

Use a proposed 300 s preparation interval followed by 100 s of tracking;
Section 7 defines the commands and Section 9 defines success and useful failure.
The modest range is deliberate: it is 0.523 radius decades, or 1.046 decades
in the reference's radius-squared similarity variable, short of the user's
longer-term “first few orders of magnitude” goal. Neither the paper nor the
movie certifies this benchmark. A transient spike alone does not pass.

**Immediate prerequisite:** resolve the B2 small-response accuracy comparison
before deriving a response campaign from it. Section 10 preserves the existing
R021/R033 diagnostic and gives the single next implementation task. B0 and the
R033 prerequisites are completed work, not assignments to repeat. No new CFD,
controller, hardware selection, physical attempt or movie belongs to R177.
The authoritative execution scope is [the current handoff](SESSION_HANDOFF.md#next-task).

## 1. Evidence and boundaries of the claim

The confirmed inspiration is OpenAI's
[*Finite time blowup for Navier–Stokes*, Theorem 1.1 and Section 2](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf).
Its construction starts from rest with smooth forcing in the volume, develops
unbounded velocity with bounded energy, and has shrinking radial and axial
core scales. Boundary-only engineering is an additional problem. Our Gaussian
reference does not reproduce its oscillatory stress construction or axial
scale law. Material axial stretching is different from growth of core height.

| Object | What it supplies | What it does not establish |
|---|---|---|
| Paper | Mathematical motivation and finite-scale comparisons | A finite boundary-actuated/sensed tank |
| [Gaussian reference](realizability/reference.py) | Divergence-free SI target, core/swirl/strain formulas | An unforced bounded-domain solution or attainable trajectory |
| [Kinematic movie](make_trajectories.py) | Prescribed tracer motion and working rendering pipeline | CFD, measured core contraction or wall-generated motion |
| B1/B2 Stokes backends | Verification tools and saved pilot evidence | Accurate B2 physical response, nonlinear preparation or control |
| Future benchmark solution | Must solve unforced-interior Navier–Stokes with recorded boundary histories | No solution or feasibility verdict exists yet |

B0 implements configuration, six boundary modes, features, sensors and matrix
analysis. B1's Taylor–Hood strong-divergence check failed. B2's BDM2/DG1
formulation supplies scoped stability and arithmetic evidence, but the
[R020 original-command response](docs/realizability/B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md)
has amplitude ratio **28,963.4968** and phase error **74.1175 degrees** against
its independent reference. Matched-trace solves were not reached. The
[R033 prerequisites](docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_FOLLOWUP.md)
passed without a physical solve. `campaign_ready=false` remains unchanged.

The movie's internal actuator rings are not the tank boundary; its separate
CoreRadius formula is not a fluid measurement. This benchmark uses the actual
cylindrical wall below. The nominal water properties are assumptions, not
measurements. See [STATUS.md](STATUS.md) for the broader evidence inventory.

### 1.1 What a finite paper-derived target would require

The paper constructs velocity and pressure, then defines force by their
momentum residual. Oscillatory annular momentum flux cancels a singular
background imbalance; corrections control the remaining residual. Section
10.1 localizes through potentials and cutoffs before forming the force,
including cutoff derivatives. This is more information than an existence
assertion, but it supplies no wall-command table.
[Primary paper, Sections 2 and 10.1, equations (10.4)–(10.5)](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=118)

Our proposed extraction contract below is a reproducibility requirement, not
an extraction performed in R180. Mathematical existence of an admissible
choice does not select a numerical value or certify its finite truncation.

| Needed input | Available now | What must be fixed or derived before evaluation |
|---|---|---|
| Source and fidelity claim | Primary PDF and its construction; separate Gaussian code | Pin source version/hash and choose full finite witness approximation, leading-profile approximation, or mechanism surrogate; name omitted terms |
| Finite space/time window | A singular time and asymptotic core scales in the paper | Explicit interval ending strictly before that time, comparison region, scale definitions and initial field; a late window starts from a nonzero state that boundary preparation must produce |
| Profiles and free choices | Profile equations, supported corrections and localization construction | Numerical constants, profile initial data, exact smooth cutoff/bump functions and support margins; verify their required conditions |
| Oscillations and corrections | Construction of annular pulses and mean/residual corrections | Exact retained terms, envelopes, phases, wave numbers and summation choices; a derivative-aware remainder estimate on the selected window |
| Units and water mapping | Proposed tank and viscosity in Section 2 | Consistent length/time/velocity/pressure scaling; record the resulting dimensionless groups and tank fit |
| Evaluator and comparison | Existing feature definitions in Section 5 | Values and derivatives of the chosen field, axis limits, divergence and momentum-residual checks; resolved sampling and separate target-approximation uncertainty |

For units, if a dimensionless field uses viscosity nu_hat, selecting length L
and time T gives velocity scale L/T, kinematic pressure scale L²/T² and
acceleration-force scale L/T², with `nu_water = nu_hat*L²/T`. Pressure in Pa
also requires density. Independently stretching radial and axial coordinates
or selecting arbitrary speed and duration does not preserve the same isotropic
Navier–Stokes equation. These are dimensional deductions, not chosen values.

A finite approximation must be checked in the derivatives used by the
momentum residual, not just in velocity norm. Small unresolved oscillations
can contribute appreciable stress or derivatives. Form the residual of the
actual retained/localized approximation; do not assume the residual of a
truncated sum is the truncated exact force. Report its rotational part or
curl as in Section 3.5 before asking for pointwise unforced matching.

The Gaussian reference is the only explicit finite target already implemented
here. Its reference interval and formulas are available, while its preparation,
engineering tolerances and command budgets remain proposals. No concrete
paper-derived field, truncation error or boundary response is supplied by this
review. Copying the paper's force spectrum would not fill those gaps.

## 2. Proposed decisions and retained assumptions

| Item | Definition for this proposal | Limitation / retained alternative |
|---|---|---|
| Domain | Fixed cylinder R = 0.10 m, half-height H = 0.15 m | About 9.42 litres; box and discrete hardware deferred |
| Fluid | nu = 1e-6 m²/s, rho = 1000 kg/m³ | Incompressible Newtonian fluid, nominal water |
| Boundary | Six side-wall velocity modes in Section 4; zero velocity on caps | Ideal balanced porous recirculation plus moving tangential elements |
| Interior | No imposed volume actuation | Hydrostatic gravity may be absorbed in pressure; no free surface/buoyancy dynamics |
| Numerical prerequisite | Existing B2 harmonic Stokes problem about rest | Same method/mesh/thresholds; no new solver selected |
| Finite engineering model | Nonlinear Navier–Stokes, initial velocity zero at t = 0 | Requires later nonlinear verification; Stokes cannot be rescaled to this regime |
| Target | Existing Gaussian reference, local time s = t - 300 s, 0 <= s <= 100 s | Proposed initial milestone, not the paper's witness or approved final range |
| Commands | Six time histories, fixed 10 s knots on 0...400 s, defined in Section 7 | Finite command family; failure does not exclude other timing/bases |
| Measurements | 48 finite wall-pressure patches and boundary actuator readbacks | Pressure-only fluid sensing baseline; interior PIV is validation only |
| Alternative sensing | Interior PIV from exterior cameras, or added wall shear/torque | Requires an explicit later choice; neither is silently available |

The ideal combined Dirichlet wall would require interleaved pumping/shear
patches or another separately designed liner. No actuator product, finite array,
force/power capability or experimentally realistic pressure/noise specification
is selected. Proposed speed/noise budgets below are transparent test assumptions.
A pump interpretation does not confer unlimited diaphragm stroke.

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
are chosen benchmarks, not optimized experimental settings. B0 already contains target-time sensitivity diagnostics. R177 retains T = 100 s;
no new sensitivity sweep is assigned.

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

The following verification obligations are retained, not an instruction to
restart B1. B2 uses its existing H(div) weak boundary formulation and pinned
penalty; the R021/R013 contract controls its immediate diagnostic. The future
finite-amplitude benchmark adds `(u · grad)u` to the left side of the transient
momentum equation and needs separate nonlinear verification.

For the existing small-signal prerequisite and later linear response screens,
solve, with pi = p/rho,

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
pi to Pa for sensor outputs. The [official mixed example](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/demos/demo_stokes.html) and
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

## 7. Finite command histories and response maps

### 7.1 One clock, preparation and tracking

Use laboratory time t in seconds. Start from rest at t = 0; prepare during
0...300 s; track the Section 5 reference during 300...400 s. The 300 s allowance
is a proposed finite budget, not a predicted spin-up time. It is much shorter
than the 8100 s diffusion estimate in Section 3.2: preparation failure would
therefore be informative but specific to this horizon and transport mechanism.
No initialized reference vortex may be substituted for boundary preparation.
Reference time is s = t - 300 s; Section 5's t is s when evaluating that target.

Define six coefficient rows c[j,k] in m/s, ordered as Section 4, at
`t_k = 10*k s`, k = 0,...,40. Set c[j,0] = c[j,40] = 0. Between knots use

```text
v = (t-t_k)/(10 s),   S(v) = 3*v² - 2*v³
A_j(t) = (1-S(v))*c[j,k] + S(v)*c[j,k+1]
u_side(x,t) = sum_j A_j(t)*b_j(x);  u_caps = 0
```

Set commands zero outside 0...400 s. This C1 interpolation fixes timing and
avoids step accelerations. The 234 free coefficients (six times 39) define the
entire proposed command family. A saved coefficient table, mode normalization,
clock origin and interpolation rule are sufficient to replay a candidate.
No optimized coefficient table exists yet. Continue does not launch a search.

For a fully specified baseline candidate, set `c[N_02c,k] = 0.010 m/s` for
k = 1,...,39 and `c[T_00c,k] = 0.010 m/s` for k = 2,...,39, all other entries
zero. Normal pumping ramps up over 0...10 s, swirl over 10...20 s, and both
ramp down over 390...400 s. This satisfies the proposed command bounds and
makes the initial relative timing reproducible. It is an untested baseline,
not a prediction that constant driving will follow the contracting target.
Later selected histories must publish their full coefficient tables before
validation; failure of this single candidate cannot reject the whole family.

A reproducible diagnostic input, rather than an invented successful controller,
is one nonzero coefficient `c[j,k] = U_probe = 1e-7 m/s`, all others zero. Its
20 s pulse rises for 10 s and falls for 10 s, with integral `10 s * U_probe`.
For a bounded first temporal screen use j = N_02c or T_00c and k = 1,5,9,
all starting from rest and observed at the same terminal t = 100 s. Six columns
then distinguish early/middle/late strain/swirl response. These are proposed
future solves, subject to their own cost/accuracy admission, not authorized now.
They extend the old single 10 s pulse to independent command times; they do not
replace or consume the frozen R021 harmonic diagnostic.

For later six-mode analysis define each column by one independent (j,k)
coefficient and keep outputs at common times. Positive/negative coefficients
and both m=4 spatial quadratures allow signed combinations and relative timing.
For `C*cos(4*theta)+S*sin(4*theta)`, report phase `atan2(S,C)` with the explicit
convention `amplitude*cos(4*theta-phase)`; phase is invalid at zero amplitude.
Temporal phase is encoded by the complete histories, not an assumed wave delay.
The 10 s knots restrict time structure; no claim of a strict Fourier bandlimit
is made. A failed coarse time basis does not exclude faster or longer commands.
The FloWave analogy motivates timing only, not free-surface physics here.

### 7.2 Command budgets and finite-time maps

For the finite-amplitude proposal require at every instant

```text
sum_j |A_j(t)| <= 0.020 m/s
sum_j |dA_j/dt| <= 0.005 m/s².
```

Peak-normalized spatial modes make these conservative bounds on wall speed
and its time derivative. Check the interpolants, not only sampled commands:
on an interval the derivative bound is
`1.5*sum_j |c[j,k+1]-c[j,k]|/(10 s)`. The coefficient bound is satisfied if it
holds at both endpoints. These are proposed computational limits, not verified
hardware ratings; the small-signal probe uses a different, much smaller scale.

Report actual peak/RMS wall speed, instantaneous flux, inbound recirculation
`Q_in = integral_side max(-u_side·n,0) dS` in m³/s, its time integral in m³,
and cumulative local displacement `integral u_side dt` in m. The latter is a
stroke demand only under an explicitly valid moving-wall interpretation.
Report boundary pressure/traction and work if resolved. Pump head, force,
efficiency and power ratings are **not assessed**, so no complete hardware
feasibility pass is possible from the velocity budgets alone.

For rest Stokes with zero initial perturbation, compute the causal map

```text
delta_x_i(t) = sum_j integral_0^t K_ij(t-s)*A_j(s) ds.
```

K must come from a verified solver/response dataset. A single harmonic gain at
0.01 Hz does not determine K. A terminal matrix has all columns evaluated at
the same time. A trajectory matrix stacks the same common output times for
all independent input histories; one pulse sampled at many times does not
supply independent controls. For a moving nonlinear base use a two-time
linearized kernel K(t,s), with both convection derivatives, or the verified
nonlinear map directly. Do not assume the six features form a closed ODE.

Save SI maps first. Retain the spatial Gram matrix M from Section 4 and the
space-time input Gram matrix
`W[(j,k),(l,m)] = M[j,l]*integral phi_k(t)*phi_m(t) dt`, where phi is the nodal
interpolation basis above. Normalize outputs using declared error allowances
and inputs using this effort metric; save the inverse transformations. This
measures boundary velocity effort, not power. Compare normal-only, tangential-
only and combined allowed columns at identical horizons. Keep singular values
reliable only above ten times the estimated normalized matrix error, as in the
original contract; a small unresolved value is not a proven zero.

Fit response models on declared histories and validate them on held-out
combinations/timing. For nonlinear preparation, a linear predictor's success
needs verification in the full equations; its failure is local evidence only.
Do not prolong preparation or alter the basis after a failure without recording
a new problem. Track errors over the whole 100 s, rather than selecting the
best instant or shifting the time origin to a favorable peak.

### 7.3 Worked symbolic example: wall patterns, timing and interior response

**Assumptions:** exact circular cylinder, constant viscosity, infinitesimal
unsteady Stokes perturbations about rest, zero initial velocity and the fixed
linear features of Section 5.2. Every nonzero gain below is an unknown response
to be verified, not measured CFD data. The example derives the structure of
the inverse problem; it does not prepare the finite-amplitude Gaussian vortex.

Take only `b_N = N_02c` and `b_T = T_00c` from the existing normalized basis:

```text
u_side(theta,z,t) = n(t)*b_N(theta,z) + v(t)*b_T(theta,z)
u_caps = 0
d(t) = [a_z(t), Omega(t)]^T.
```

Both patterns have azimuthal order m=0. Their axial shapes differ: b_N uses
the balanced Z2 return-flow pattern; b_T uses Z0 for swirl. Coefficients n,v
are speeds in m/s, not body-force densities. The boundary Fourier order,
axial shape and temporal history are three independent specifications.

In axisymmetric Stokes, the azimuthal velocity obeys

```text
partial_t u_theta = nu*(partial_rr + r^-1*partial_r
                         + partial_zz - r^-2)*u_theta.
```

There is no meridional velocity or pressure term in that equation. Conversely,
the meridional Stokes equations contain no swirl term. Thus these two inputs
give the exact continuum structure

```text
a_z(t)   = integral_0^t k_a(t-s)*n(s) ds
Omega(t) = integral_0^t k_O(t-s)*v(s) ds.
```

The cross-responses vanish under these assumptions; the diagonal responses
need not be strong or even useful at a selected time. Kernels have units
1/(m*s), since outputs have units 1/s. A numerical cross-response is a useful
symmetry check, subject to actual geometry and discretization errors.

For settled harmonic operation only, write n(t) = Re[n_hat exp(i*omega*t)]
and likewise for v, a_z and Omega. Then

```text
[a_hat]   [g_a(omega)    0        ] [n_hat]
[O_hat] = [0             g_O(omega)] [v_hat],    g in 1/m.

n_hat = a_hat_target/g_a;    v_hat = O_hat_target/g_O.
```

Division requires resolved nonzero gains. For example, if
`g_O = |g_O|*exp(-i*phi_O)`, the swirl command must have amplitude
`|O_hat_target|/|g_O|` and phase `arg(O_hat_target)+phi_O`. This is the fluid
phase correction. It does not follow from the phase of the desired volume
force. Weak gain demands large wall speed; zero gain prevents that harmonic
feature within this model. For a sinusoidal coefficient of amplitude B,
peak slew is omega*B. Compare both speed and slew with Section 7.2, and check
the combined histories. A harmonic illustration is not itself a member of
the finite C1 knot family unless represented and validated there.

For the actual finite timing basis, let phi_k be Section 7.1's unit-height
20 s pulse centred at t_k. Use k=1,5,9, observe all columns at 100 s, and set

```text
n(t) = n_1*phi_1(t) + n_5*phi_5(t) + n_9*phi_9(t)
v(t) = v_1*phi_1(t) + v_5*phi_5(t) + v_9*phi_9(t)
alpha_k = integral_0^100 k_a(100-s)*phi_k(s) ds
beta_k  = integral_0^100 k_O(100-s)*phi_k(s) ds

c = [n_1, n_5, n_9, v_1, v_5, v_9]^T
[a_z(100)]   [alpha_1 alpha_5 alpha_9  0      0      0     ]
[O(100)  ] = [0       0       0        beta_1 beta_5 beta_9] c
```

Each alpha/beta has units 1/m. If only k=5 is allowed and both gains are
resolved, the formal terminal solution is `n_5=a_target/alpha_5` and
`v_5=O_target/beta_5`; reject it if commands violate the budgets. With more
columns, solve a constrained fit using the input Gram metric and feature
error scales. A target outside the resolved range has a nonzero unattainable
component; a small singular value amplifies required effort and model error.
No alpha/beta value, ordering or successful command is inferred here.

Early and late pulses can have different gains because diffusion and decay
continue between actuation and observation. A terminal match does not imply
tracking: stack all common output times for a trajectory test. Include the
initial-state response if it is unknown or nonzero. A frequency response
describes this convolution only for a time-invariant linearization; finite
startup is not eliminated by specifying phases.

For a developed vortex, both convection derivatives enter the linearized
equation and an evolving base gives K(t,s). Pumping can transport swirl, so
the diagonal rest structure no longer applies. Use an actual boundary-driven
base; expansion about a forced reference instead leaves an affine momentum
defect that must be retained. A homogeneous perturbation map alone would
silently assume the missing sustaining force is available.

### 7.4 What m=4 and force spectra add, and what they leave unresolved

The other four implemented wall columns prescribe normal and tangential
`cos(4*theta)` and `sin(4*theta)` patterns with axial shape Z0. At each time,
`C*cos(4*theta)+S*sin(4*theta)` sets a spatial amplitude and orientation;
changing C(t),S(t) sets a timed command. Their interior response is a four-input
map to `[C_r4,S_r4,C_theta4,S_theta4]`, using a verified kernel or harmonic
matrix. Normal/tangential and spatial-quadrature responses may couple; assigning
the same coefficients at the wall and in the annulus assumes an unjustified
identity map. A single axial shape also cannot prescribe arbitrary axial
structure.

Rotational symmetry separates azimuthal orders in the *linear field equations*
about an axisymmetric base. It does not make every diagnostic an angular
projection: the existing a_z uses one vertical sheet, so an m=4 velocity can
contribute to it. Do not impose block zeros on the full six-feature map merely
from mode labels. The two-column example above is restricted to m=0 inputs.

To expose the stress issue, consider a local, radial-constant illustrative
interior pattern, not a globally specified incompressible solution:

```text
u'_r     = R*cos(4*theta)*cos(omega*t)
u'_theta = V*cos(4*theta-psi)*cos(omega*t+delta)
mean_(theta,time)(u'_r*u'_theta) = R*V*cos(psi)*cos(delta)/4.
```

Angular orthogonality supplies one factor 1/2 and averaging over a temporal
period supplies the other. Spatial alignment and temporal phase both affect
the sign or cancellation. With general fields these phases and amplitudes
must come from the fluid response, and the stress must be formed *locally
before spatial averaging*. Products of annulus-averaged Fourier coefficients
do not recover stresses when radial profiles vary.

In rest Stokes the quadratic stress does not feed back on the mean, because
the nonlinear term was omitted. This correlation identity therefore cannot
demonstrate the paper's mean-flow mechanism. For nonlinear Navier–Stokes,
mode products can create a mean and higher harmonics; the divergence of the
stress tensor, including radial/axial structure and other components, enters
the mean momentum balance. A nonzero scalar correlation alone is insufficient.

One may separately decompose a specified volume force into angular, radial,
axial and temporal components to identify where and how fast its residual
acts. That uses a **volume** response operator. Wall velocities use a different
domain, units and response operator. Matching selected outputs would require
solving `G_boundary*c ≈ d_target` (or a nonlinear counterpart), not restricting
the force to the wall or copying its spectrum. Pressure-gradient force parts
can also be absorbed in pressure; Section 3.5's curl test isolates the local
obstruction relevant to exact velocity matching.

Sensing is another map. Even if g_O is usable, a homogeneous-wall unknown
axisymmetric swirl perturbation has zero pressure-difference signature in
rest Stokes and can change Omega. With the same commands its ideal velocity
readbacks are identical. This is a concrete actuation/observation distinction;
Sections 8.1–8.2 retain strict wall sensing and the unknown-state test. Interior
CFD/PIV supplies validation truth only. No phase adjustment removes that
pressure blind direction in this linearization.

R181 completes that calculation in Sections 7.5–7.7 below; these extend the
diagnostic specification without changing the existing feature definitions.

### 7.5 Finite annular angular-momentum balance

R181 derives the following identity for smooth incompressible Newtonian flow
with constant density rho and kinematic viscosity nu, about a fixed laboratory
z axis. It applies to nonlinear Navier–Stokes, not the rest-Stokes response
model with its quadratic term omitted. The primary paper describes radial
inflow, axial transport and viscous loss in Section 2.1, and oscillatory flux
redistribution supplying a background deficit in Section 2.2. Our finite
control-volume identity tests one component of that mechanism; it neither
extracts nor verifies the paper's full construction or its axial-momentum
cancellation. [Primary paper, Sections 2.1–2.2, pp. 3–6](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=3).

**Local derivation.** Positive theta is right-handed about +z. Write pi = p/rho
and let f be imposed acceleration (m/s²), not force per volume. For cylindrical
components, the azimuthal equation and incompressibility are

```text
D = partial_t + u_r*partial_r + (u_theta/r)*partial_theta + u_z*partial_z
Delta_s = partial_rr + (1/r)*partial_r + (1/r²)*partial_thetatheta + partial_zz
D u_theta + u_r*u_theta/r
  = -(1/r)*partial_theta pi
    + nu*(Delta_s u_theta - u_theta/r² + 2*partial_theta u_r/r²) + f_theta
(1/r)*partial_r(r*u_r) + (1/r)*partial_theta u_theta + partial_z u_z = 0.
```

For specific angular momentum ell = r*u_theta, multiplying the first equation
by r absorbs the curvature term into D ell, since D r = u_r:

```text
D ell = -partial_theta pi
        + nu*(Delta_s ell - 2*partial_r ell/r + 2*partial_theta u_r/r)
        + r*f_theta.
```

Define a bar as a full 0...2*pi angular average **at fixed r,z,t**, with no
time average. Set U_j = bar(u_j), u'_j = u_j-U_j, L = bar(ell) = r*U_theta,
Q_r = bar(u'_r*u'_theta), Q_z = bar(u'_z*u'_theta). These are covariances of
the actual field; they need not be turbulent or single-mode. Periodicity
removes pressure torque and theta derivatives; incompressibility permits
conservative advection. Thus

```text
partial_t L + (1/r)*partial_r(r*U_r*L) + partial_z(U_z*L)
  = V + C + r*bar(f_theta)
V = nu*(partial_rr L - partial_r L/r + partial_zz L)
C = -(1/r)*partial_r(r²*Q_r) - partial_z(r*Q_z).
```

Equivalently, mean advection is U_r*partial_r L + U_z*partial_z L.
The curvature factor is essential: C is not just -partial_r Q_r. Introduce
viscous flux factors and total outward-transport components

```text
K_r = nu*(partial_r L - 2*L/r) = nu*r*(partial_r U_theta - U_theta/r)
K_z = nu*partial_z L             = nu*r*partial_z U_theta
V   = (1/r)*partial_r(r*K_r) + partial_z K_z
F_r = U_r*L + r*Q_r - K_r
F_z = U_z*L + r*Q_z - K_z
partial_t L + (1/r)*partial_r(r*F_r) + partial_z F_z = r*bar(f_theta).
```

The averaged shear stresses are tau_rtheta = rho*K_r/r and
tau_ztheta = rho*K_z/r. Before averaging they also include
rho*nu*partial_theta u_r/r and rho*nu*partial_theta u_z/r respectively;
these integrate to zero around a complete circle. Pressure has zero torque
about z on cylindrical and horizontal faces, even if pressure varies with
theta. No axisymmetry of the instantaneous field is assumed.

**All finite boundary terms.** Take the fixed volume
`V_A = {r1 <= r <= r2, 0 <= theta < 2*pi, z1 <= z <= z2}`, with r1 > 0.
Its outward normals are -e_r,+e_r,-e_z,+e_z at r1,r2,z1,z2 respectively.
This is an extension in z of a diagnostic annulus, not a change to the existing
midplane observable A. Define

```text
H = 2*pi*rho * integral_z1^z2 integral_r1^r2 L*r dr dz
Phi_mean = 2*pi*rho * { integral_z1^z2 [r*U_r*L]_r1^r2 dz
                       + integral_r1^r2 r*[U_z*L]_z1^z2 dr }
Phi_pert = 2*pi*rho * { integral_z1^z2 [r²*Q_r]_r1^r2 dz
                       + integral_r1^r2 r²*[Q_z]_z1^z2 dr }
T_visc   = 2*pi*rho * { integral_z1^z2 [r*K_r]_r1^r2 dz
                       + integral_r1^r2 r*[K_z]_z1^z2 dr }
T_vol    = 2*pi*rho * integral_z1^z2 integral_r1^r2 r²*bar(f_theta) dr dz

dH/dt = -Phi_mean - Phi_pert + T_visc + T_vol.
T_pert = -Phi_pert = integral_V_A rho*C dV.
```

Brackets mean upper value minus lower. Positive Phi removes positive angular
momentum; positive T adds it. T_pert is an effective mean momentum transfer,
not an externally imposed torque. For example Q_r > 0 at the outer face
exports positive angular momentum, while the same positive Q_r at the inner
face imports it into this annulus. Both endcaps must be retained; reflection
symmetry, a midplane measurement or zero net volume flux does not generally
cancel their angular-momentum fluxes. The theta seam is periodic, so its two
contributions cancel. There is no extra edge torque for a smooth Cauchy stress.

| Quantity | SI units |
|---|---|
| L, ell | m²/s |
| Q_r, Q_z, K_r/r, K_z/r | m²/s² |
| F_r, F_z, K_r, K_z | m³/s² |
| partial_t L, V, C, r*f_theta | m²/s² |
| H | kg m²/s |
| Phi_mean, Phi_pert, T_visc, T_vol, dH/dt | kg m²/s² (N m) |

Dividing H by the fixed fluid mass rho*pi*(r2²-r1²)*(z2-z1) gives mean
specific angular momentum. Its change need not track peak swirl or core
radius: inward transport can spin up a core while another region loses
angular momentum. A moving core-following volume requires Reynolds transport
with velocity relative to the moving surface; it is not this identity.

An **internal control face** is fluid, so its advective and stress fluxes
must be measured, not set to wall commands or zero. Adjacent volumes cancel
shared-face fluxes. At a fixed impermeable tank wall u_n = 0 pointwise, both
mean and perturbation advective fluxes through that wall vanish; tangential
traction can still supply viscous torque. A velocity command determines
traction only through the solved flow. For a port/porous boundary with u_n
nonzero, retain the full advective angular-momentum flux even when total
volume flux is zero. A physically moving wall requires a moving-domain balance.
Noncylindrical walls may also exert pressure torque; the general traction term
is integral_boundary r*(sigma*n)_theta dS, sigma = -p*I + viscous stress.
These qualifications do not select new actuator hardware or boundary conditions.

Checks on the identity: solid rotation U_theta = Omega*r has K_r = 0;
U_theta = B/r has nonzero radial shear but constant r*K_r, hence zero radial
viscous divergence. The r1 -> 0 limit has no inner flux for smooth axis-regular
fields. On a whole fixed impermeable cylinder, perturbation transport cannot
change total angular momentum by itself; it redistributes it internally.
A later time average must retain endpoint storage and averages of products:
replacing bar_time(U_r*L) by bar_time(U_r)*bar_time(L) drops another covariance.

### 7.6 Why the existing averages cannot determine the transfer

For each nonzero angular order m, let c_jm(r,z,t), s_jm(r,z,t) be *local*
Fourier coefficients. Angular orthogonality gives, for a resolved complete
expansion,

```text
Q_r(r,z,t) = (1/2)*sum_m>=1 [c_rm*c_thetam + s_rm*s_thetam].
```

The four existing m=4 observables retain only radial area averages at z=0.
Products of those averages lose radial covariance, other angular orders,
face values and radial derivatives. Even the separately computed scalar
R_rtheta retains only `2/(r2²-r1²)*integral_r1^r2 r*Q_r(r,0,t) dr`.
It contains neither the radial boundary values of r²*Q_r at general z nor
Q_z, axial variation, mean advection, storage or shear. A weighted integral
of Q_r does not fix a weighted boundary difference of Q_r.

Here is a complete **instantaneous divergence-free counterexample** that also
shows why finite axial data matter. On a neighbourhood of V_A with z1=-h,
z2=h, take m=4, constants k (m²/s), beta (1/(m s)) and the vector potential

```text
A_r = -beta*z³*cos(m*theta)/3,   A_theta = 0,
A_z = k*sin(m*theta)/m,         u' = curl A
u'_r     = k*cos(m*theta)/r
u'_theta = -beta*z²*cos(m*theta)
u'_z     = -m*beta*z³*sin(m*theta)/(3*r).
```

All components have zero angular mean. The radial divergence vanishes;
the theta and z divergence terms are +m*beta*z²*sin(m*theta)/r and its
negative. Thus this is incompressible for every beta. To embed it in a smooth
closed tank, multiply the **potential** by a smooth axisymmetric cutoff equal
to one on a neighbourhood of V_A and supported away from the axis and tank
walls, then take its curl. That preserves these formulas on V_A, gives a
smooth solenoidal extension and zero wall velocity; multiplying the velocity
itself by a cutoff would not suffice. The tank is assumed to leave room for
this internal annulus and its cutoff neighbourhood.

At z=0 every beta has exactly the same field and observables:

```text
C_r4 = 2*k/(r1+r2),  S_r4 = C_theta4 = S_theta4 = 0,  R_rtheta = 0.
Q_r = -k*beta*z²/(2*r),    Q_z = 0  throughout V_A
C   = k*beta*z²/(2*r)
T_pert = 2*pi*rho*k*beta*(r2-r1)*h³/3.
```

The last result follows both from the two radial-face fluxes and from the
volume integral of C; axial perturbation flux is zero in this example.
Changing beta changes the transfer while preserving all five existing
annulus observables. The fields specify admissible initial data, not a claimed
steady or time-dependent Navier–Stokes solution. With f_theta = 0 and zero
initial angular means, their instantaneous mean tendencies are partial_t L=C;
viscous and mean-advection terms vanish at that instant. The smooth exterior
extension supplies compensating redistribution, so no whole-tank torque is
created. Adding the same smooth axisymmetric base to both fields leaves the
covariances and their difference in mean tendency unchanged.

Even a nonzero local correlation need not drive a local mean change. As a
stress-level identity, Q_r=q0/r² independent of z and Q_z=0 gives C=0 and
Phi_pert=0 on every such annulus, although Q_r is nonzero: equal radial flux
enters and leaves. Here q0 has units m⁴/s²; this statement is an identity about
stress transport, not an additional claimed velocity solution. Conversely,
compactly supported stresses may redistribute momentum among subregions
while their net transfer across an enclosing volume is zero. A single total
budget therefore cannot certify a spatially resolved mechanism.

### 7.7 Minimal offline validation and the finite-target boundary

This is a **data and diagnostic specification**, not an implementation or run.
Use actual CFD or independently measured PIV truth offline. It grants no new
feedback measurements: Section 8's strict wall support remains the baseline.
A linear Stokes run cannot validate the nonlinear stress mechanism.

The smallest budget for one volume needs angular-momentum storage plus the
mean, perturbation and viscous fluxes on **both cylindrical faces and both
annular endcaps**, together with known volume torque. To test spatial transfer
rather than only net torque, evaluate that same conservative budget on a fixed
partition in r and z with shared faces. A 2-by-2 radial/axial partition is a
minimal initial localization check, not sufficient resolution for an arbitrary
pulse; refine where opposing contributions or gradients remain unresolved.
Keep the old midplane A observable unchanged. Do not choose a numerical axial
extent or new resolution allowance in this derivation.

| Retained data | What it resolves |
|---|---|
| Fixed origin, face coordinates, rho, nu, physical quadrature weights and synchronized times | Geometry, units, face orientation and storage interval |
| Three velocity components around full circles at each face sample and in each cell | U_r,U_theta,U_z, L, Q_r,Q_z; integrate products locally before averaging |
| Neighbouring velocity samples or resolved derivatives at faces | partial_r U_theta-U_theta/r and partial_z U_theta for viscous torque |
| Cell-integrated L at interval endpoints; face flux histories | Storage and time-integrated transport without differentiating noisy storage |
| Declared actual volume acceleration and boundary history | T_vol and provenance; never insert a target's manufactured force into an unforced run |
| Target mean fields and derivatives on the same geometry/time window, with error estimates | Required angular-momentum transfer and finite-target comparison |

For storage only the interior mean U_theta is needed; the three-component
interior field also permits a local divergence comparison. CFD can export
these restricted samples and integrals rather than a full-domain archive.
PIV must resolve the required components, full angular support, axial variation
and gradient neighbourhoods, simultaneously or through demonstrated repeatability
with phase synchronization. One two-component midplane image cannot close this
balance. This states the information requirement, not a camera or sensor choice.
Do not assume single-mode purity, reflection symmetry or vanishing axial flux.
No universal angular sample count suffices without a bandwidth/error bound;
check angular quadrature on quadratic products and unresolved harmonics.

For each fixed cell c and interval [t_a,t_b], in angular-impulse units kg m²/s,
form independently

```text
B_c = H_c(t_b)-H_c(t_a)
      + integral_ta^tb (Phi_mean,c - T_visc,c - T_vol,c) dt
I_pert,c = -integral_ta^tb Phi_pert,c dt
E_c = B_c - I_pert,c.
```

B_c is the unexplained mean budget when perturbation transport is omitted;
E_c is the full closure residual. Retain radial and axial face contributions
separately and their time histories. Use short resolved intervals as well as
the full finite window so positive/negative transfers cannot hide by temporal
cancellation. Shared-face contributions must cancel in the sum over cells;
check mass-flux balance and angular quadrature separately. Where derivatives
are resolved, compare cell-average C with the conservative face expression.
Do not obtain I_pert by solving the balance for it: that would make closure
circular. In CFD report both the scheme's discrete conservation defect and an
independently reconstructed physical budget; algebraic conservation alone
cannot validate an inaccurate velocity/stress field.

For a specified finite mean target U*, define its required local perturbation
contribution under the **admissible actual** volume torque f_adm (zero in the
boundary-only study):

```text
L* = r*U_theta*
D* = partial_t L* + U_r* * partial_r L* + U_z* * partial_z L*
     - nu*(partial_rr L* - partial_r L*/r + partial_zz L*)
     - r*bar(f_adm,theta).
J*_c = integral_ta^tb integral_cell rho*D* dV dt.
```

The face/storage form using U* gives the same J*_c. If the mean target were
matched, its perturbation stress would need to supply J*_c; the target's own
manufactured volume force is not a permissible cancellation. For a paper
approximation specify which angular mean is U*, including retained mean
corrections. The leading background alone need not equal the exact angular
mean. This requirement constrains a divergence, not a unique stress tensor;
stress realizability by solenoidal velocities and boundary reachability remain
separate unsolved problems.

Report both `I_pert,c-J*_c` and actual mean-profile/feature errors. Small closure
E alone shows accounting of the observed flow, not tracking of U*. Conversely,
a matching net torque does not establish its spatial distribution or the
radial/axial momentum equations. Comparing B and E holds the measured mean
fixed; it is not a prediction of a second flow with perturbations removed.
A causal command-on/off claim would need separately validated comparison data.

Use a fixed norm across the retained cells/time intervals, for example the
maximum absolute component in angular-impulse units. Predeclare positive
absolute budgets epsilon_close, epsilon_target and uncertainty estimates for
B, E, I_pert-J*, including correlated errors from shared velocity samples.
Do not divide by J* when it is near zero or reuse Section 9's velocity
percentages as a torque tolerance. For F0=norm(B), F1=norm(E), uncertainties
delta0,delta1 on those norms give a conservative improvement test
`F1+delta1 < F0-delta0`. Bounds may conservatively sum component estimates
unless justified joint propagation is available. Include angular/radial/axial
quadrature, mesh/time resolution, velocity-gradient extraction, viscosity,
geometry/centering, PIV noise/bias and synchronization, plus target truncation
and derivative error in the target comparison. Refinement differences estimate
uncertainty; they are not automatically rigorous bounds. Missing dominant
uncertainty prevents a verdict.

| Outcome | Required interpretation |
|---|---|
| Resolved mechanism improvement | The uncertainty-separated inequality holds on the declared norm, closure satisfies F1+delta1 <= epsilon_close, and individual cell/time residuals show where transport acted. A nonzero Q alone does not qualify. |
| Finite-target support | Additionally norm(I_pert-J*) plus its uncertainty is <= epsilon_target, target mean/feature tracking passes its declared limits, and spatial/temporal resolution gates pass. This supports only the angular-momentum component for this finite target and tested commands. |
| Resolved failure for the tested case | With adequate closure and uncertainty, target transfer or mean tracking exceeds its budget even at the favourable uncertainty bound; report cells, times and sign/direction responsible. Resolved absence of improvement is a failure of that proposed explanation, not a universal boundary-control impossibility. |
| Inconclusive | Closure, target definition, gradients, missing faces, sampling or uncertainty cannot resolve the criteria. Closure failure flags unresolved data/model/numerics, not proof of physical impossibility. If B is already indistinguishable from zero, this case cannot demonstrate a needed perturbation correction. |

No finite paper mean/correction fields, derivative-aware target error,
comparison axial interval or angular-impulse tolerances have yet been fixed.
The existing Gaussian target is axisymmetric and initially requests zero m=4;
its finite formulas are available, but that does not assign a paper-mechanism
stress target. Therefore this session reaches a research boundary without a
numerical mechanism verdict or a new numerical allowance. B2 remains failed,
q64/q96 unused, and all existing Section 9/B2 criteria remain unchanged.

**Next scientific calculation:** apply this balance symbolically to the
existing Gaussian reference and its fixed cutoffs. Derive D* in the core and
transition regions, and the whole-support angular-momentum compatibility
condition for a compactly supported perturbation stress with no volume torque.
Determine what can be redistributed internally and what requires external
boundary transport/torque. This is a surrogate-specific necessary-condition
check, not paper-witness extraction or a numerical feasibility test. See the
single [next task](SESSION_HANDOFF.md#next-task) for completion criteria/stops.

## 8. Strict boundary measurement and independent truth

### 8.1 Allowed measurement operator

Use 48 wall patches with centres `(theta,z) = (2*pi*l/16, z_h)`, l = 0,...,15,
`z_h = -0.08, 0, 0.08 m`. Each spans 5 mm of side-wall arc and 5 mm in height.
Patch support is on r = R, never in the volume. Let

```text
p_bar[h,l](t) = area_average_patch(p(x,t))   # Pa, p = rho*pi
reference patch = (h=0,l=0), z = -0.08 m, theta = 0
y_p[h,l](t) = p_bar[h,l](t) - p_bar[0,0](t)  # other 47 patches
```

Use a proposed sample period 0.005 s (200 Hz), 5 ms availability latency,
and independent pre-difference Gaussian pressure noise sigma_p = 0.1 Pa per
patch/sample. The 47 difference channels have covariance
`sigma_p²*(I + 1*1^T)`; they are not independent. Time independence is a declared
ideal noise model, not an instrument fact. Retain 0.01 and 1 Pa only as later
sensitivity alternatives, not extra runs in this task. Hydrostatic offsets
must use the same subtraction/calibration in truth and observations.

Permitted actuator readbacks are the six realized boundary-mode velocity
coefficients, in m/s, at the same timing, provisionally sigma_A = 1e-5 m/s
independent noise per coefficient/sample. A future instrument would need
encoders and flow measurement/calibration to infer these coefficients. In an
ideal Dirichlet model they merely report known commands and add no information
about an unknown interior perturbation. Motor current or torque is not silently
included: its fluid-dependent measurement map is a separate proposed extension.

Only the available history of these channels, commands, clock and fixed model
parameters may enter a later estimator/controller. Never give it a CFD/PIV
core radius, full velocity, true centre, pressure gauge, hidden perturbation
coefficient or future sensor sample. Exact initialization/model prediction
alone is not proof of sensing. All sensing claims must include unknown states.

Interior CFD/PIV fields are **validation truth only**, used offline to compute
Section 5 features and the Section 9 errors. Keep truth, sensor and estimated
state outputs separate. External cameras observing interior particles still
have interior measurement support. Allowing that feedback requires the user's
explicit choice; strict boundary support remains the baseline. Boundary shear
or torque might help while preserving boundary support, but needs its own
hardware/noise/operator definition before selection.

### 8.2 What the sensing test must distinguish

Input-to-pressure transfer is not state observability. Test unknown,
divergence-free, homogeneous-wall initial perturbations under the **same known
commands**, including states not produced by the six actuator columns.
Retain the finite family of curls of compact C2 potentials inside
`|x|,|y| < 0.03 m`, `|z| < 0.05 m`: each Cartesian potential direction times
1,x,y,z, plus a compact axisymmetric pure-swirl field. Save exact shapes and
kinetic-energy normalization; project into the discretely divergence-free
space and report projection error. No family has been run for this proposal.

At rest first use x_lin, not an invented core radius. Over a common 10 s
observation interval, let P map initial-family coefficients to noise-whitened
boundary sensor histories and Q map them to the normalized desired initial
features. Exact identifiability requires `ker(P) subset ker(Q)`. Show Q on the
nullspace and compare near-null signatures with numerical error and noise.
State the finite family/horizon; test held-out combinations. A finite-family
pass is not full-flow observability or an implemented observer.

In particular, an axisymmetric pure-swirl perturbation about rest has constant
pressure in linear Stokes while its Omega changes. Identical commands produce
identical readbacks. It therefore provides an exact pressure/readback blind
state for this model. No better pressure sampling or command timing can repair
that exact null direction in the rest linearization. Boundary shear sensing or
a developed nonlinear base could change the result; neither is assumed here.

Around a future boundary-prepared vortex, repeat the finite-family test using
its actual evolving base and the available histories; the rest null result
cannot be transplanted unchanged. For the engineering target, desired Q must
include core, signed peak swirl and strain wherever their derivatives exist.
A valid sensing pass needs uncertainty in those features below Section 9's
budgets under the stated noise/latency, with held-out state errors reported.
Do not build a controller merely because P has a numerically nonzero rank.

## 9. Target, errors and interpretable outcomes

### 9.1 Proposed finite acceptance criteria

Keep the existing Section 5 reference and circulation. For s = 0...100 s,

```text
r_star(s) = sqrt(1e-4 - 9.1e-7*s) m   # s supplied in seconds
U_star(s) = (1e-4 m²/s)/r_star(s), positive swirl
strain_star(s) = Section 5 a(s)       # s^-1; includes viscous spreading
x_required = [r_c, U_peak, a_r, a_z]
```

Use the unique resolved swirl peak and fixed-plane integrals of Section 5,
not a fitted reference imposed as truth. Report centre displacement separately;
require <= 1 mm throughout tracking, so recentering cannot hide a displaced
core. Keep fixed-origin Fourier diagnostics. Initially target all four m=4
coefficients at zero; require each absolute value <= 0.001 m/s. Report their
phases when resolved and R_rtheta in m²/s², but do not claim reproduction of
the paper's perturbation-stress mechanism from this axisymmetric milestone.

For each required nonzero feature define
`e_i(s) = (x_i(s)-x_star_i(s))/|x_star_i(s)|`. Proposed acceptance is RMS over
100 s <= 10% and maximum absolute error <= 20%, with both endpoints <= 10%.
Require a valid core and positive swirl/strain throughout; a missing or
unresolved peak fails the measurement gate, not a zero-radius success.
Evaluate at all retained solver times, initially output spacing <= 0.1 s,
and refine temporal sampling/integration to bound missed peaks. These new
engineering tolerances do not alter the existing B2 <5%/<5-degree gate.

Compute observed scale range independently of prescribed TauRatio:

```text
D_r = log10(r_c(300 s)/r_c(400 s))
D_r2 = 2*D_r
reference: D_r = log10(10/3) = 0.522879; D_r2 = 1.045757
```

D_r2 describes the observed radius-squared range; interpret it as similarity-
time range only to the extent the trajectory matches r_star(s)². Require a
conservative lower bound D_r >= 0.48 (approximately threefold contraction), in addition to
the full-history error checks. This blocks a marginal endpoint-only claim.
Report the smaller achieved range if this fails, without relabelling it as
“two decades.” A 10 mm → 1 mm target would span two radius-squared decades
but remains a later proposed problem, not an automatic extension.

Use identical normalizations for estimated-feature errors against independent
truth. Report error histories and uncertainty, including startup/latency; do
not hide transients in an average. A joint simulation success needs boundary-
only estimation within these budgets as well as actual flow tracking and
command compliance. Open-loop tracking without sensing can be a partial success,
but does not fulfill the boundary-only actuation-and-sensing goal. Feedback
implementation, nonlinear robustness and real-apparatus claims are later stages.

### 9.2 Numerical uncertainty is a gate

Before drawing physical conclusions require the applicable independent
reference checks, at least two resolved meshes/time steps and independent
feature quadrature comparisons; refine again if the trend is unclear. Treat
these differences as estimated uncertainty, not a rigorous bound by themselves.
For the finite benchmark reserve at most 2% of each nonzero target feature for
the combined numerical/measurement-extraction error, <= 0.2 mm for centre,
and <= 0.0002 m/s for each m=4 coefficient. Include all identified components
rather than assigning that budget separately to each. Radius sampling starts
at <= r_c/10 and must be refined. These are future engineering budgets, not
permission to refine the once-only fixed-mesh R021 diagnostic.

A pass requires errors plus their uncertainty to meet every limit. A negative
threshold claim requires errors minus uncertainty to exceed the limit. An
overlap is inconclusive. For D_r use the adverse endpoint uncertainties;
report an uncertainty interval as well as the nominal value. Use response-map
error and sensor noise separately when interpreting weak directions.
Missing temporal, spatial, geometry or operator error estimates cannot be
replaced by small linear residuals. The current B2 evidence does not pass.

### 9.3 What success, failure and inconclusiveness mean

| Outcome | Required evidence | Scope of conclusion and what may still work |
|---|---|---|
| Joint finite success | Boundary-generated preparation; whole-history errors/range within budget; command compliance; independently validated boundary-only estimation | Success for these equations, target, input family and sensor model; hardware and the paper's full mechanism remain unvalidated |
| Actuation success, sensing failure | Validated flow tracks, but two admissible states have indistinguishable wall histories and required features differ beyond tolerance | Open-loop production might work; this feedback inference task cannot. A different boundary observable/base could help |
| Inaccessible target direction | A resolved left-null witness w for the finite-time map with nonzero target component, or a certified lower bound on best tracking error | Failure for that basis, operating point and horizon, not every boundary actuator or nonlinear flow |
| Beyond specified command limits | A verified constrained lower bound exceeds tolerance with the speed/slew budgets, while a larger command family can meet it | This declared budget fails; stronger/faster hardware or more preparation might help. Unknown force/power ratings preclude a complete apparatus conclusion |
| Preparation failure | A particular reproducible command never forms a valid target core by 300 s | That command failed. Universal failure over the family needs a lower bound or other proof; an optimizer stopping is insufficient |
| Numerical or measurement inconclusive | Accuracy, resolution, compatibility, uncertainty or signal-to-noise checks cannot resolve the criterion | No physical impossibility or feasibility inference; preserve partial data and the first unresolved gate |

For a linear normalized trajectory map G and bounded coefficient set C, use
`min_(c in C) ||G*c-d||` with the same declared error metric as the proposed
criterion. An optimizer's candidate is an upper bound, not a proof of failure;
a dual bound or explicit separating direction can supply a lower bound.
Discount the lower bound by the uncertainty in G and d over C before rejecting
the target. State what time/space discretization and linearization it covers.
For sensing exhibit a concrete invisible/near-invisible state pair, not only a
condition number. Preserve physical units for both witnesses.

Section 3.5's nonzero curl of the target residual forbids exact full-field
unforced matching where that residual is nonzero; it does not forbid these
reduced-feature tolerances. The pressure-blind rest swirl is a separate scoped
obstruction. Neither the B2 discrepancy nor failure to reproduce an interior
volume-forced field proves the entire engineering goal impossible.

## 10. One accuracy prerequisite and one subsequent task

**The next numerical question is the existing R021 matched-trace comparison,
not a new transient or control campaign.** It tests whether the large central
response error persists with a known solution's full boundary trace on the
same mesh, versus the original wall command. Read the
[R021 preserved contract](docs/realizability/B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md),
[R033 completed prerequisites](docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_FOLLOWUP.md),
and [R070 completed launch/report repair](docs/realizability/evidence/r070/result.json).
R067's launch/report repair recommendation has already been implemented in
R070; neither it nor R033 should be restarted from historical next-task prose.

Keep the exact 482-cell mesh, 22,900 real unknowns, BDM2/DG1 alpha=96,
0.01 Hz, U_probe=1e-7 m/s, 128-term reference, fixed q=64/q=96 pair and all
production/configuration pins. P is the original command; A_64/A_96 use the
matched trace. All three complete lifted RHS compatibility checks must precede
factorization. Preserve one common factorization, three primary solves and
one correction each, stage-local checks and finite refusal on the first failed
arithmetic/PDE/resource condition. No extra mesh, quadrature, retry or solver.

Retain `G_star = 2.0662858857221768e-5 - 6.595106312048072e-5 i 1/m`,
strict magnitude error <5% and wrapped phase error <5 degrees; preserve
`E5 = 3.4556100991268897e-6 1/m`, output/correction screens E5/100,
load-step screen E5/10, pressure-removal and all R013/R021 checks unchanged.
The difference P-A measures discrete boundary-data sensitivity, not a clean
continuum geometry-error decomposition. A good A result alone neither fixes P
nor clears the campaign. A failed compatible A points toward unresolved
approximation/measurement error; failed compatibility means no comparison.

**Single next implementation deliverable:** connect the already-repaired R070
runner to a minimal task-specific practical launch path for this diagnostic,
with a default-disabled physical command and a reviewable dry-run result.
Reuse existing source/evidence binding and refusal/count handling. Add only
what is needed for reservation, independent task timeout, resource observation,
owned-child cleanup and complete/partial result acceptance under
[R103/R104](docs/realizability/B2_MONITOR_PRACTICAL_SUPERVISION_POLICY.md).
Identify remaining actual-FEM validation of the R070 stage checks explicitly.
Validate the connection using saved evidence and benign children/fake events;
do not run the physical cylinder, Bessel trace, JIT or completed R033 toys.
Produce code and focused checks, not another general infrastructure contract.

Physical execution remains separately gated and **unauthorized by this
specification**. Its unused q64/q96 allowance stays 180 s / 1536 MiB, including
its prescribed extraction/reporting; old attempts and prerequisite charges
remain recorded. The implementation must not enlarge or reset any allowance.
If using the existing benign monitor suite, retain its separate 180 s/768 MiB
whole-unit, 512 MiB workload RSS, no-swap/32-PID and native <=128 MiB limits.
R103 allows ordinary disclosed OS trust; no recursive supervisor certification
or complete PC/Mac performance benchmark is a prerequisite. An early Mac check
of the shared dry-run/report interface belongs to a later explicit ownership
handoff; it cannot consume the physical attempt. No Mac transfer is needed now.
The next task's exact files, benign-check limits and stopping point are in
[SESSION_HANDOFF.md](SESSION_HANDOFF.md#next-task).

## 11. Review status and remaining choices

R177 is a source-and-document specification. It checked the implemented
reference/configuration, saved B2/R020/R021/R033/R070 evidence, practical policy
and the primary paper. No reference evaluation, numerical workload, solver
test, controller, hardware selection, rendering or package change ran. Existing
Section 5 scalar values and Section 6 verification thresholds are inherited
records, not newly measured results. Documentation checks and delivery are
recorded in [REQUEST_LOG.md](REQUEST_LOG.md) and [WORK_SESSIONS.md](WORK_SESSIONS.md).

Remaining user-level choices before a full engineering experiment: accept or
revise the proposed finite range/tolerances, 300 s preparation budget and command
limits; retain strict wall sensing or explicitly allow interior optical
feedback; later select credible hardware/noise limits. None prevents preparing
the unchanged accuracy diagnostic. The present proposal defaults to strict
support and retains the existing 10 mm → 3 mm reference for review.

R180 completed the conceptual/modal review in Sections 1.1 and 7.3–7.4.
R181 adds the symbolic balance, incompressible counterexample and offline
validation contract in Sections 7.5–7.7. The [next task](SESSION_HANDOFF.md#next-task)
is the Gaussian target's angular-momentum deficit and global compatibility
calculation; Section 10 remains deferred. No finite paper target, new tolerance,
response coefficient or hardware/sensor decision was selected. Manual algebra,
units, face signs, counterexample divergence/flux integrals and documentation
checks are recorded in the logs. No numerical evaluation or solver test ran.
Retain GPT-6 Astra/high on PC/WSL daisy for scientific interpretation; use
Luna/medium only for a later fully specified mechanical change and return to
Astra for unresolved physics. No model/platform switch occurred.
