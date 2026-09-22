# Finite-port base-flow calculation contract — R194

2026-09-22; PC/WSL `daisy`. **Specify a new nonlinear, three-dimensional,
boundary-driven calculation. Admit only an isolated verification prototype as
the next implementation step; do not admit a tank run or reuse B2 as a validated
solver.** A steady core at the R192 point has not been demonstrated. The
axisymmetric average and a periodically repeated sector are restricted screens,
with no quantified error bound for the complete vessel.

This is a proposed calculation and verification contract, not CFD evidence or
hardware approval. It completes the [R193 task](INWARD_TRANSPORT_SCREEN_R193.md#decision-and-minimal-next-calculation).
[R191's claims](ESSENTIAL_SIMILARITY_CONTRACT_R191.md) and
[R192's operating point and uncertainty gates](FIXED_CORE_OPERATING_POINT_R192.md)
remain unchanged. All new geometry, preparation, method and tolerance choices
below are design proposals for this separate calculation. Follow the single
[current handoff task](../../SESSION_HANDOFF.md#next-task).

## One definite boundary problem

The physical question is whether the 4 L/min port route creates inward feeding,
axial extension and one resolved swirling core near the nominal 11.209 mm peak
radius and 50 mm/s peak swirl. These are outputs, never volume constraints or
initial data. Failure to approach them is a result for this boundary problem,
not a reason to overwrite the computed base with the Gaussian target.

Use the R192 closed cylinder r<100 mm, -100<z<100 mm and water rho=1000 kg/m³,
nu=1e-6 m²/s. The fixed diagnostic cylinder remains R=H=25 mm. No free surface,
interior stirrer, imposed azimuthal body force, turbulence closure or artificial
Gaussian source is included. Gravity is absorbed in reduced pressure for this
constant-density, fixed-domain problem; absolute pump pressures require the
hydrostatic contribution and external circuit separately.

Define theta_j=2*pi*j/16. Make the previously unspecified row staggering concrete:
normal 4 mm bores meet the cylindrical wall at z=±55 mm; angled 4 mm bores at
z=±65 mm, all at theta_j. Thus all openings stay inside the |z|=45–75 mm bands.
Normal jets point along d_n=-e_r(theta_j); angled jets along
 d_a=(-e_r(theta_j)+e_theta(theta_j))/sqrt(2). The upper/lower patterns have the
same swirl handedness. Returns are the 32 axial 6 mm bores at r=35 mm,
z=±100 mm, theta_j. All remaining wetted surfaces are fixed no-slip walls.
No midplane symmetry condition is imposed on the full-vessel problem.

Represent openings by actual straight circular-bore/cylinder intersections,
not circular patches of equal area on the curved wall. Extend each bore outward
from its wall-centre intersection by an initial length 5d along its axis; the
remote circular cut lies perpendicular to that axis. Union the bore fluids and
tank interior with no interior end wall at the junction. These are numerical
stubs, not a specification of physical wall thickness or a resolved manifold.
Check positive passage area, disjoint bores, connected fluid, tags, normals and
boundary area before assembly. Sharp junction edges are an explicit idealization;
rounding and curved-wall approximation are later model sensitivities. A planar
45-degree footprint has area A_b/cos45, but that approximation is not the mesh
geometry or the flow normalization.

At each remote inlet disk of radius a_b=2 mm impose

```text
u = Ubar(t) * g(s) * d_j,   s = distance_from_bore_axis/a_b,
g(s) = 2*(1-s²),  0<=s<=1;    area_mean(g)=1.
Q_bank = 2 L/min;  q_j = Q_bank/32;  Ubar=q_j/(pi*a_b²).
```

There are 32 normal and 32 angled supplies. Ubar=82.893 mm/s per bore at full
flow; the parabolic peak is 165.786 mm/s. R192's nominal bore speed and future
20 mm/s modulation are **section means** in this proposed profile model. Its
old uniform-profile torque number was explicitly conditional; do not apply it
to these profiles. A laminar inlet shape is an imposed candidate condition,
not a prediction of the plumbing. The inlet Reynolds number based on section
mean and diameter is 331.573; that number does not establish tank stability.

Initial state: u=0 everywhere and all imposed fluxes zero. Ramp both banks and
the returns by S(t)=3 xi²-2 xi³ for xi=t/20 s in [0,1], then S=1. This arbitrary
20 s smooth ramp is a reproducible preparation input, not a settling estimate.
All m=4 modulation is off for the base. Keep transient inventories and work.
Later repeat with a changed ramp and a small compatible nonsymmetric disturbance
before claiming preparation independence; no automatic multi-run campaign is
admitted here. Record any continuation from an earlier state explicitly.

## Return closure and pressure gauge

At the union Gamma_+ or Gamma_- of remote return disks on each cap prescribe a
**total flux constraint**, with a spatially uniform unknown traction multiplier
P_+(t) or P_-(t):

```text
sigma = -p I + 2 mu D(u),     D(u)=(grad u+grad u^T)/2,
sigma n = -P_+ n  on Gamma_+,   integral_Gamma_+ u.n dS = S(t)*2 L/min,
sigma n = -P_- n  on Gamma_-,   integral_Gamma_- u.n dS = S(t)*2 L/min.
integral_Omega p dV = 0.
```

P_± are solved reaction pressures, not independently commanded pressures.
This models separately regulated cap totals and equal traction at the branch
cuts, with equal numerical stubs and neglected downstream branch impedance.
The split among sixteen returns on one cap is an output. Mean return speed
is 73.683 mm/s only if the split is equal; each cap's imposed total does not
force equal individual speeds. At the cut the two tangential tractions vanish;
tangential velocity and angular-momentum extraction remain free. Do not set
u_theta=0 at the tank mouth: that would insert an artificial angular-momentum
sink. No per-port pressure and velocity pair is prescribed simultaneously.

There is one redundant total-flux identity from incompressibility and the
inlet data. Fix the simultaneous constant shift of p and P_± with the volume
pressure gauge, and check the resulting constraint rank on a toy problem.
A generic pressure-only null vector from a full-Dirichlet Stokes problem is
wrong here: the multipliers shift too. In the gauge-fixed mixed formulation,
mean-zero pressure tests enforce divergence up to its constant component;
the exactly balanced aggregate flux constraints supply that component.

This closure is physically interpretable as an ideal regulated recirculation
loop, with an unresolved pressure/impedance response. It is neither a selected
pump nor a prediction of the 10 kPa circuit allowance. Report inlet traction,
P_+-P_-, each branch flow, torque and hydraulic power. An alternative is a
specified pump/manifold impedance network with cap split as an output; that
would be a different boundary problem needing calibrated resistances and
compliance. Prescribing all return velocities is simpler but suppresses swirl
and branch redistribution and is not selected.

Require nonnegative outward velocity at the artificial return cuts, apart from
quantified numerical error. If resolved backflow occurs, this simple traction
closure is not admitted: retain the result and design a longer stub or a reviewed
energy-stable open-boundary/impedance treatment. Do not clip velocity, silently
add damping, or infer incoming swirl from hidden truth. Compare 5d with 10d
stubs before trusting tank outputs; independence has not been established.
The changing stub volume must be included in the enclosing inventory, while
reporting the original tank inventory separately.

## Why inlet averaging changes the question

For a circular section with the stated profile,

```text
beta = area_mean(g²)=4/3,     alpha = area_mean(g³)=2,
T_in,angled = rho * Q_angled * Ubar * beta * R_v * sin45,
P_kin,in = sum_banks (rho/2) * Q_bank * Ubar² * alpha.
```

Here R_v*sin45 is the central bore-line angular lever arm. Extending a straight
bore along its axis leaves (x cross d_j)_z unchanged; the transverse odd moment
of the symmetric profile integrates to zero. These are advective fluxes at the
remote cuts. Bore-wall pressure/shear torque between cut and tank can alter
delivery. The normal bank's net advective axial torque is zero by section
symmetry, not by omission of its tractions.

| Remote-inlet quantity | Uniform reference | Parabolic candidate |
|---|---:|---:|
| Angled bank advective angular input (µN m) | 195.381 | 260.508 |
| Total inlet kinetic-energy flux (mW) | 0.22904 | 0.45809 |
| Peak inlet speed (mm/s) | 82.893 | 165.786 |

The 65.127 µN m profile difference is about 498 times R192's separate
0.1309 µN m phase-confound allocation. It is a **base-model sensitivity**, not
a measured phase mismatch; identical known profiles can cancel between phases.
It shows why matching total Q is insufficient. The kinetic flux above excludes
pressure work and is not pump electrical or hydraulic demand.

Let angular averaging be denoted by a bar. A boundary or interior average obeys

```text
mean(u_n*u_theta) = mean(u_n)*mean(u_theta) + C_ntheta.
```

A smeared boundary preserving the mean velocities generally loses C_ntheta and
higher moments. In a simple flat-port example with active area fraction f and
constant jet components, mean velocities give f² U_n U_theta rather than the
actual f U_n U_theta. Holding mass fixed does not hold angular input or energy
fixed. In the bulk the same averaging produces unresolved stress terms. Adding
them by guesswork is a new closure, not an axisymmetric Navier–Stokes solution
for the finite ports. An averaged annular calculation may explore a different
actuator, but cannot admit or exclude R192's ports without discrepancy evidence.

A 22.5-degree rotationally periodic wedge with the full height does retain one
normal and one angled port per band, and one return per cap. Vector fields must
rotate across the seam, not be copied componentwise. It is the smallest exact
geometric repetition of the candidate, but enforces C16 rotational symmetry and
excludes m=1…15 disturbances, including m=4. It can find a symmetric branch;
it cannot establish that the full vessel prepares or maintains that branch.
A steady C16 base couples later perturbation modes m to m+16k. A real m=4
forcing is compatible with a 90-degree ordinary periodic sector (four pitches),
or a linearized complex phase-shifted 22.5-degree sector, not the unmodified
base wedge. These reductions do not test all symmetry-breaking instabilities.

**Selection:** the first credible vessel base is full 360-degree, three-
dimensional transient Navier–Stokes with the finite openings. A symmetric wedge
is an optional cost screen only; do not make its successful convergence a tank
stability claim. No axisymmetric solve is a required preliminary detour.

## Numerical method and actual repository capability

Source reviewed at R194's starting commit 95f7065:

| Existing component | What it actually supplies | Reuse limit |
|---|---|---|
| [B1 backend](../../realizability/backends/fenicsx_stokes.py), `harmonic_pilot`, `transient_pulse` | Taylor–Hood Stokes response/time stepping; cylinder tags and direct block solve. | No nonlinear convection or finite ports. Strong-divergence gate failed; no accuracy inheritance. |
| [B2 backend](../../realizability/backends/hdiv_stokes.py), `harmonic_response` | BDM2/DG1 SIP Stokes about rest, strong normal and weak tangential data. | No nonlinear base/time integration, return multipliers or nozzle geometry; full-gradient viscosity is not a physical-traction open-boundary implementation. |
| B2 stability/trace diagnostics | Scoped dissipation and trace/compatibility checks. | Neither physical accuracy nor stability of a different method/domain follows. |
| [Existing FEM pins](../../environment-b1.yml) | DOLFINx 0.10.0 and related package declarations. | Read only in R194; no runtime import, package validation, upgrade or new dependency. |

The [physical-response audit](B2_PHYSICAL_RESPONSE_AUDIT.md) found amplitude
28,962.69 times reference and about 74.12 degrees phase discrepancy despite a
small algebraic residual. The later [R020 result](B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md)
retains P's failed response and stops A_32 on pressure compatibility; A_64 was
not solved. q64/q96 remains unused and R021 launch integration stays deferred.
These failures do not prove the new nonlinear problem impossible. They prohibit
using old residual/stability passes as validation of a new base solver.

**Proposed first verification implementation:** a separate conforming P2/P1
Taylor–Hood prototype with the symmetric physical stress above, conservative
convection, backward Euler startup and BDF2 time stepping, and Newton iteration
to a recorded residual. This choice makes physical traction and the return
multipliers explicit. It does not promise exact cellwise mass conservation.
Do not invoke the B1 pilot or mutate B2 operators. Reuse library conventions or
small utilities only after checking their boundary/gauge assumptions.

For trial velocity u and test v vanishing on inlet and fixed-wall Dirichlet
boundaries, use the following dimensional momentum weak form:

```text
(rho*d_t u,v) - (rho*u tensor u,grad v) + (2*mu*D(u),D(v)) - (p,div v)
 + integral_returns rho*(u.n)*(u.v) dS
 + sum_{s=+,-} P_s * integral_Gamma_s v.n dS = 0,
(q,div u)=0,   integral_Gamma_s u.n dS=Q_s(t),   mean(p)=0.
```

Use mean-zero pressure trial/test spaces and two scalar multipliers. Supply
nonhomogeneous inlet data by consistent lifting, retaining every coupled row.
Convection at inflow is set by prescribed inlet data; return convection uses
the interior outflow trace. For verification only, add a known manufactured
volume load and/or traction. Physical runs must set volume forcing to zero.
Cartesian coordinates avoid an axis singularity. Use consistent geometry and
quadrature for loads, constraints, traction and diagnostic integrals.

Conservative convection preserves the continuum momentum accounting; weak
incompressibility can still create an energy defect involving
(rho/2)*integral |u_h|² div(u_h) dV. Record its sign/magnitude and the temporal
and algebraic defects separately. Do not add unreported grad-div stabilization,
eddy viscosity or divergence repair. If convergence cannot reduce these errors,
review a divergence-conforming alternative rather than relaxing output gates.
BDF2's numerical energy is not exactly the physical kinetic energy: use both
its discrete identity and converged time-integrated physical budgets.

The official [DOLFINx divergence-conforming Navier–Stokes demo](https://docs.fenicsproject.org/dolfinx/v0.10.0.post3/python/demos/demo_navier-stokes.html)
provides an alternative mass-conserving method with upwinding. Its documented
problem prescribes velocity on the entire boundary, so it does not supply the
selected mixed return closure. A BDM alternative would need a fresh consistent
physical-stress, open-boundary and numerical-flux derivation. A mature finite-
volume implementation is another alternative, but would require a separate
version/feature and verification review; no package selection is implied.
The conservative and physical-stress equations here are our proposed formulation;
[MIT's viscous-flow notes](https://web.mit.edu/2.25/www/pdf/viscous_flow_eqn.pdf)
were rechecked for the underlying Newtonian equations.

## Verification and output gates

No solver residual alone can pass this contract. Preserve signed quantities,
unrounded terms, finite failure reports and reasons for refusal.

1. **Verify the new method before tank implementation.** Use a non-affine,
   divergence-free manufactured transient field with nonzero convection;
   verify velocity, pressure, divergence, traction, torque and observed spatial/
   temporal convergence. Include an independent Poiseuille profile/pressure-drop
   case, rigid rotation (zero physical viscous stress), and a mixed-boundary
   manufactured case with two independently constrained outlet groups. For the
   latter use known compatible fluxes and exact tractions, allowing manufactured
   nonconstant traction offsets plus the unknown constants. Check gauge/rank,
   both flow rows and rejection of incompatible totals. Nonzero manufactured
   traction is a verification fixture, not the tank return condition.
2. **Geometry and discrete compatibility before a tank solve.** Integrate every
   opening, inspect normals/overlaps and certify total and cap flux compatibility
   of the assembled constraints/lift at arithmetic scale. Use a tolerance derived
   from absolute term sums and conditioning, declared before running. Never
   subtract an unexplained pressure-nullspace component or silently repair flow.
   Check curved geometry refinement independently of solution refinement.
3. **Mass, angular momentum and energy.** On the enclosing domain and separately
   the tank and central cylinder, evaluate the continuum identities below using
   physical stress and the actual u. Track both caps and every inlet/return, and
   surrounding J=J_tank-J_central. Do not omit nozzle walls or pressure torque on
   oblique/noncylindrical surfaces. On the central circular side/flat caps,
   pressure axial torque is zero. Use cell-aware cut-surface integration with
   converged geometry/quadrature; a nodal sum or one disk is insufficient.
4. **Base outputs and delivery.** Report r_c and U_p at z=0 and ±10 mm, peak
   uniqueness, centre/tilt, circulation, radial inflow, partial_z U_z and fits
   for a_eff, without Gaussian fitting constraints. Report full side/cap mean
   fluxes and azimuthal covariances (discrete steady jets can give nonzero C),
   wall/port torque, J, kinetic energy and dissipation. From the computed flow,
   measure inlet-labelled first entry into the central volume, cap bypass and
   flux-weighted travel-time distribution; distinguish first-entry fraction
   from repeated recirculating flux. Converge streamline/pathline integration
   and count trajectories not arriving within the observation horizon as
   censored. A steady streamline is invalid for a fluctuating base. These
   diagnostics are future work; none was integrated in R194.
5. **Convergence and settling.** Independently refine mesh, time step, nonlinear/
   linear tolerance, boundary representation and output quadrature. Use at
   least three ordered mesh levels and three time steps to assess convergence;
   two agreeing numbers can share bias. Begin geometry planning near h<=d/8
   across inlet bores and <=1 mm centrally, then resolve actual gradients and
   boundary layers. These are seed spacings, not an accuracy guarantee or an
   affordable mesh estimate. Backflow, multiple peaks, unresolved gradients or
   missing closed-budget terms refuse admission.

For a fixed fluid control volume with n outward, l=(x cross u)_z and
K=integral rho*|u|²/2, J=integral rho*l:

```text
integral_boundary u.n dS = 0,
dJ/dt + integral_boundary rho*l*(u.n) dS
      = integral_boundary (x cross (sigma n))_z dS,
dK/dt + integral_boundary (rho/2)*|u|²*(u.n) dS
      = integral_boundary u.(sigma n) dS - integral_volume 2*mu*D:D dV.
```

Fixed walls do no mechanical work, but exert torque and dissipate energy in
the adjacent fluid. No pressure work is dropped at the open cuts. Compute
integrated balances over windows as well as instantaneous defects.

Proposed **screening**, not M1, tolerances: global flux defect below 1e-8 of
4 L/min; successive resolved core radius, swirl, strain, inventories, first-entry
fraction and median transit changes below 1% of declared nonzero reporting
scales; time-integrated angular and energy closure defects below 1% of the
sums of absolute budget contributions. State an absolute scale for a zero or
near-zero observable; do not divide by its vanishing net value. Check local
incompressibility and the conservation defects directly as well as global flux.
Three levels must show a consistent decreasing error trend; otherwise unresolved.
These are proposed screening gates, not rigorous error bounds or replacements
for B1/B2 or R191/R192 thresholds.

After the ramp, assess at least three consecutive nonoverlapping 100 s windows
for drift in central and exterior J/K, outputs and fluctuations, with statistical
errors for correlated samples. Window agreement alone does not prove settling:
compare preparation histories and retain unresolved slow drift. A nominal
94.248 s tank-volume/flow time is only an inventory ratio. If intrinsic
fluctuations persist, report a statistically settled state and its stress budget;
do not linearize a steady transfer function about its time average while
omitting the fluctuation closure. A steady Newton root also needs a stability/
preparation test; symmetry-preserving time marching from rest is not that test.

Before a later m=4 response, demonstrate a reproducible base and convergence of
its full central surface fields and exterior transport. The 1% base screens do
not certify a 0.1309 µN m error floor: 1% of 260.508 µN m is 2.605 µN m.
Allocate numerical and boundary-model errors within the actual phase-contrast
budget, which must include R192's separate residual and confound limits and
1.528e-7 m²/s² covariance allocation. Test output sensitivity to base/return/
profile errors in the coupled response. No gain or phase bound follows from
base convergence alone. Preserve both standing-wave traveling components and,
where symmetry is unproved, both spatial quadratures and coupled m+16k modes.

## Admission, missing evidence and next task

**Boundary problem specified; tank implementation/execution not admitted.**
Missing evidence: verified mixed-boundary nonlinear discretization, affordable
geometry/resolution and linear-solver plan, profile/stub/return sensitivity,
full-domain preparation/stability, and measured plumbing/optical uncertainty.
Ideal regulated fluxes and assumed profiles permit a conditional numerical study;
they cannot establish hardware delivery. No feasible contraction range follows.

**Admit one separate verification-prototype implementation next.** Implement the
weak form above with manufactured data and independent analytic oracles, outside
production B1/B2 paths. First derive exact fixture boundary tractions/fluxes and
the gauge-fixed constraint rank, then implement and run only standard-library
algebra/schema tests. Include explicit guards excluding the physical tank and
B2 campaign. Prepare a reviewed manifest for tiny FEM verification (method,
versions, mesh/time sequence, outputs, error gates, resource/attempt caps), but
stop before FEM imports/JIT, mesh creation, assembly or PDE solves. This leaves
a concrete code review rather than another general solver survey. If deriving
the fixtures exposes a well-posedness or consistency error, stop with that
specific result instead of improvising boundary conditions.

The later FEM fixtures need a fresh bounded execution contract under the
[practical supervision policy](B2_MONITOR_PRACTICAL_SUPERVISION_POLICY.md).
Do not extrapolate old LU costs or consume the deferred q64/q96 allowance.
Existing physical caps remain 180 s / 1536 MiB; no larger tank workload or new
attempt allowance is granted here. If a credible resolution cannot fit an
approved future budget, report the resource/method decision rather than run an
under-resolved tank as evidence. No CFD, optical, hardware, procurement,
trajectory, rendering or encoding work ran in R194.

Retain GPT-6 Astra/high on PC/WSL `daisy` for the boundary/method implementation
and review. [Official Astra documentation](https://developers.openai.com/api/docs/models/gpt-6-astra)
was fetched through OpenAI Docs and confirms high support; account access and
user-reported quotas were not verified. Recommend a cheaper model only when
remaining implementation is mechanical and its availability has been checked.
No model switch, delegation or machine transfer occurred.

[Retained analytical checks](evidence/r194/README.md) verify profile moments,
fluxes, moment-arm invariance, rotational mode restrictions, compatible ramping
and an independent continuum budget oracle. They do not validate a discretization
or the proposed tank. Production code, dependency pins, benchmark scientific
sections, thresholds and once-only allowances remain unchanged.
