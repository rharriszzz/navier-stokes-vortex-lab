# Measurable essential similarity and first test — R191

2026-09-22; PC/WSL `daisy`. Design proposal for review, with checked algebra
and scale arithmetic. No measured response, CFD result or hardware admission.
Execution priority remains the [single handoff task](../../SESSION_HANDOFF.md#next-task).

A useful first analogue is a boundary-driven, coherently swirling core that
contracts by a resolved amount while inward transport, axial stretching and
viscous spreading remain measurable. Demonstrating that perturbations help
sustain it is a separate, stronger result. The first proposed mechanism test
is a phase reversal around a prepared, approximately steady vortex, before
attempting contraction plus perturbations. This isolates an interpretable
momentum-transfer question without assuming an attainable shrinking trajectory.

R188 allows different numerical profiles, geometry, schedules and forcing.
The criteria below make that freedom falsifiable. Numerical thresholds here
are proposed experimental design choices, not user requirements or changes to
historical benchmark gates. B2 accuracy still fails; q64/q96 is unused.

## Claims and allowed differences

The [primary paper, Section 2](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=3)
describes radial concentration, axial outflow, swirl amplification and viscous
loss, with oscillatory momentum flux compensating a mean-flow residual. Its
axial core scale can decrease while fluid elements stretch axially. Thus a
lengthening visible column is not a required sign of its mechanism. The
following finite experimental criteria are our proposal, not the paper's theorem.

| Claim / essential property | Observable acceptance and falsifier | Boundary hardware and measurements | Allowed differences / limits |
|---|---|---|---|
| A1: coherent contraction and spin-up | Unique resolved positive swirl peak, declining radius r_c, increasing peak speed U_p and shear scale U_p/r_c over a predeclared interval. Conservative radius ratio at least 3 for the first milestone; reject isolated endpoint spikes, peak switching, or loss of a resolved core. | Independently adjustable swirl supply and balanced normal circulation; volumetric velocity profiles at several z planes, centre and shape histories. | Gaussian shape, circulation, exact exponent and dimensional speed need not match. Smaller resolved contraction is a partial result. A shrinking bead ring alone fails. |
| A2: coupled transport and stretching | Resolved inward mean radial motion in the core-feeding region and positive axial extension there; full side/endcap volume flux closes within its uncertainty. Reject apparent contraction caused solely by translation, cropping or unbalanced fluid inventory. | Side supplies and separately metered upper/lower returns; multi-view velocity and fluid-level/loop checks. | Tank shape, return paths, axial asymmetry and changing axial core length can differ. Material stretching must be distinguished from support length. |
| A3: concentration competes with viscosity | Measured transport and viscous terms have resolved opposing effects in the swirl budget, while contraction/spin-up persists. Estimate strain-to-diffusion ratio and its history; an unresolved viscous term makes this claim inconclusive. | Temperature/viscosity estimate, calibrated velocity gradients on a closed central surface; strain driven by measured flow. | No required Burgers profile or universal critical Reynolds number. A nearly inviscid visual contraction alone does not establish the proposed viscous analogue. |
| A4: physical accounting and repeatability | Fluid and angular-momentum inventories close within bounded uncertainty, including preparation and external return. Repeat after independently preparing the vortex; report attained range and failed runs. | Flow/pressure readbacks, port velocity profiles or calibrated angular flux, wall torque where applicable, synchronized optical data. | Surrounding flow may change and supply stored momentum. It cannot supply an unrecorded infinite reservoir. Pressure at a rigid circular wall is not independently available torque. |
| M1: perturbation-mediated angular-momentum transfer | Phase-dependent signed stress transport through a closed surface is resolved; including it closes the measured budget and a mean-only balance cannot explain that component. Controls below bound changed base flow and delivered torque. | Independently phased normal/tangential boundary patterns; 3D optical velocity on side and both caps, synchronized actuator and loop signals. | Modes/waveforms may differ. A nonzero local correlation, stronger mean suction, or larger total swirl input is insufficient. This result alone does not establish perturbation-assisted contraction. |
| M2: perturbation-assisted contraction, later | During A1–A4 contraction, stress transfer explains a resolved change in the mean balance/performance under matched or explicitly budgeted mean driving. | Same channels, now across the evolving core and feeding annulus. | A fixed-core M1 pass is only a prerequisite; radial/axial momentum and energy exchanges still need separate evidence for broader paper-mechanism claims. |

A1–A4 together define the proposed first contracting-vortex milestone. M1 can
be investigated independently first; M2 is a later claim. None constitutes
quantitative replication or mathematical blow-up. No complete finite paper
witness is required unless that stronger replication comparison is chosen.

## Operational definitions and uncertainty

Use a fixed laboratory axis and predeclare the comparison cylinder and axial
planes. Estimate the core centre separately from velocity, record displacement
and tilt, and use a centre-relative profile only for shape/radius diagnostics.
Keep conservation surfaces fixed in the laboratory frame. A moving surface
would require relative transport terms; never silently recenter the budget.
For the first milestone propose a centre displacement below 0.25 times the
smallest target radius and resolved tilt; if this is unsuitable, revise the
geometry criterion before data collection, not after seeing the result.

Define r_c(z,t) as the unique interior maximum of the angular-mean signed swirl
profile, with sign set by preparation. Fit a locally flexible smooth profile
and propagate measurement and smoothing error to peak location and height.
Do not impose a shrinking Gaussian fit. A flat, unresolved or competing peak
has no valid radius. Check contraction on the predeclared central plane and
at least two flanking planes; report axial variation instead of selecting the
best plane afterward. Vorticity width and circulation profiles are cross-checks,
not interchangeable radius definitions. This excludes hollow/multiple-core
flows from this first contract without excluding them from future studies.

Proposed first reporting gate: at least ten effectively independent spatial
resolution lengths across the smallest core diameter, radius expanded
uncertainty no larger than 10% at the endpoints, and at least ten resolved
time bins across contraction. These are starting design targets; demonstrate
convergence of fitted radius, gradients and surface fluxes when sampling and
processing support change. Overlapping PIV windows/pixels do not count as
independent resolution elements. Preserve all intermediate data; do not hide
re-expansion, missing planes or unresolved intervals in endpoint summaries.

Let u(x) denote combined standard uncertainty, including calibration, optical
refraction, tracer lag/slip, reconstruction bias, missing tracks, differentiation,
viscosity, timing and repeat variability. Account for correlated errors when
forming products, ratios, differences and surface integrals. Use calibrated
95% intervals; an expanded bound 2u is only an approximation when justified.
Report both random and systematic contributions. Covariance noise may have a
nonzero bias; subtract only a separately calibrated bias and propagate its error.

For endpoint intervals [r0_lo,r0_hi] and [rf_lo,rf_hi], the conservative radius
ratio is r0_lo/rf_hi. Predeclare the tracking window and require its contraction
trend and spin-up to survive the uncertainty bands and all selected planes.
The threefold criterion refers to that lower bound, not a nominal best fit.
Use at least five independent preparations as an initial repeatability design;
more frames from one run do not supply independent preparations or remove bias.
If the uncertainty cannot resolve the criterion, report inconclusive.

Useful measured nondimensional histories are a_eff*r_c²/nu,
U_p*r_c/nu, contraction time nu*T/r_c(0)², and, when driven, frequency
f*r_c²/nu and perturbation speed/U_p. Define a_eff = -U_r/r by a reported
core-region fit, and independently estimate partial_z U_z. Departures from
partial_z U_z = 2*a_eff quantify nonuniformity, not automatic rejection of a
nonlinear finite flow. Report the actual radial divergence for mass balance.
No universal acceptable range is assigned without a measured/modelled profile;
the signs and resolved competition in A2–A3 are the minimum here.

Commercial [volumetric PTV](https://www.dantecdynamics.com/solutions/fluid-mechanics/volumetric-velocimetry-tomographic-piv-and-tomographic-ptv/tomographic-ptv/)
provides a candidate route to 3D velocity. It does not establish our spatial
resolution, uncertainty or real-time delay. Initially analyze synchronized raw
images offline; any later feedback receives delayed noisy estimates, never
hidden exact CFD fields. The [hardware survey](BOUNDARY_HARDWARE_FEASIBILITY_R185.md)
remains the component source; no new vendor operating point is selected here.

## The closed-volume diagnostic

Take smooth incompressible constant-density Newtonian flow with no imposed
azimuthal body force. For full angular averages at each r,z,t, define
U_j = mean_theta(u_j), C_jtheta = mean_theta((u_j-U_j)*(u_theta-U_theta)).
These are spatial covariances, not necessarily turbulence. Keep the instantaneous
means/products and integrate them in time afterward; cycle-averaging velocities
first loses an additional covariance.

For a fixed cylinder V: 0 <= r <= R, -H <= z <= H, define angular momentum
J = integral_V rho*r*U_theta dV. With outward normal n, write

```text
Phi_U = integral_boundary rho*r*U_theta*U_n dS
Phi_C = integral_boundary rho*r*C_ntheta dS
T_mu  = integral_boundary r*(mean viscous traction)_theta dS
J(t1)-J(t0) = integral_t0^t1 (-Phi_U-Phi_C+T_mu) dt
```

On the side, C_ntheta = C_rtheta; on upper/lower caps it is respectively
+C_ztheta/-C_ztheta. Side viscous shear is
rho*nu*(partial_r U_theta-U_theta/r); upper/lower shear is
+/-rho*nu*partial_z U_theta. Include the lever arm r and surface measure r dtheta
dr on caps and R dtheta dz on the side. Regularity makes the axis contribution
zero. Pressure has no z torque on these cylindrical/horizontal faces, even
for nonaxisymmetric pressure. For the actual noncylindrical vessel use full
traction, including pressure torque, and include port angular-momentum flux.

This is the [existing exact balance](../../BOUNDARY_CONTROL_HANDOFF.md#75-finite-annular-angular-momentum-balance)
specialized to the central cylinder. Define the time-integrated residual

```text
E = Delta J + integral Phi_U dt + integral Phi_C dt - integral T_mu dt.
```

Closure requires zero within E's propagated interval and an uncertainty small
enough to distinguish the claimed effect. Agreement from very loose intervals
is not evidence. For M1 propose expanded uncertainty u95(E) <= one third of
the measured phase-dependent stress impulse magnitude, and an independently
bounded mean/actuator confound of the same maximum size. These ratios are
proposed detection targets, not percentage agreement with a paper field.
Retain covariances between E and measured Phi_C when comparing full and
mean-only residuals; they are not independent observations.

A directly useful counterexample is C_rtheta = K/r² on an annulus, independent
of z, with C_ztheta = 0. Its correlation is nonzero but
(1/r)*partial_r(r²*C_rtheta) = 0 and the two radial fluxes cancel. Therefore
local stress sign alone is insufficient. This annular example is not continued
to the axis and is not asserted to be a realizable velocity covariance.

For an enclosing volume V_e, the surrounding fluid has J_s = J_e-J.
The common central faces cancel exactly when budgets are added:
Delta J_s = external angular impulse - Delta J. This supplies the accounting
for either boundary torque or depletion of prepared surrounding swirl. It
preserves the R182 whole-field obstruction while allowing a different exterior.

## Radius, duration and engineering demand

For a conditional illustration only, use Gaussian vorticity width b,
U_theta = Gamma/(2*pi*r)*(1-exp(-r²/b²)), and uniform strain
U_r = -a*r, U_z = 2*a*z. The measured swirl-peak radius is about 1.1209*b,
not b. Only for this fixed profile do their contraction ratios agree.
The [Burgers-vortex baseline](https://arxiv.org/html/1002.2489#S1) supports the
strain/viscosity comparison; the following finite schedule is our calculation.

```text
B = b² = b0²-k*t,  k = (b0²-bf²)/T > 0
Bdot = 4*nu-2*a*B,  a(t) = (4*nu+k)/(2*B(t))
D_radius = log10(b0/bf)
tau(t) = B(t)/k,  D_tau = 2*D_radius,  tau0-tauf = T
Q_central = 4*pi*a*H*R²
```

Nominal nu = 1e-6 m²/s; b0 = 10 mm; fixed illustrative R=H=25 mm:

| Final b (mm) | Elapsed T (s) | Radius ratio | Conditional tau decades | Peak a (s^-1) | Peak central throughput (L/min) |
|---:|---:|---:|---:|---:|---:|
| 3 | 10 | 3.33 | 1.046 | 0.728 | 8.57 |
| 3 | 100 | 3.33 | 1.046 | 0.273 | 3.21 |
| 1 | 10 | 10 | 2 | 6.950 | 81.88 |
| 1 | 100 | 10 | 2 | 2.495 | 29.39 |

These widths correspond to peak radii approximately 11.21 -> 3.36 or 1.12 mm.
They are not the benchmark's prescribed 10 -> 3 mm peak-radius values.
The throughput is across an imaginary central surface, not a pump curve,
required loop flow, global lower bound or proof that strain reaches the core.
Longer duration reduces contraction demand but leaves the viscous floor
2*nu/bf². Fixed circulation would give U_p proportional to 1/b; its value,
required torque and hydraulic loss cannot be inferred without Gamma and a
realized exterior. Do not fill those missing columns with catalog maxima.

For this model only, the central side and cap fluxes can be evaluated without
prescribing the exterior. Write c = Gamma/(2*pi), x=R²/B and
I(B) = [R²-B*(1-exp(-R²/B))]/2. Then

```text
J = 4*pi*rho*H*c*I
Phi_U_side = -4*pi*rho*a*H*c*R²*(1-exp(-x))
Phi_U_caps =  8*pi*rho*a*H*c*I
T_mu_side  =  8*pi*rho*nu*H*c*((1+x)*exp(-x)-1)
T_mu_caps  = 0
```

With Bdot above, dJ/dt = -Phi_U_side-Phi_U_caps+T_mu_side exactly.
Swirl can therefore concentrate with no perturbation stress in this conditional
core model. That is a useful null explanation for M2, not proof of a tank
solution: radial/axial momentum, boundary delivery and the exterior remain open.

Outside a supported b proportional to tau^p relation, report radius ratio and
elapsed seconds directly. If p is fitted, include uncertainty and sensitivity
to the fitted terminal time; a short window may not identify either. Never
report extra similarity-time decades by choosing a convenient terminal time.
The initial study preference remains roughly a threefold contraction; a
10-fold or smaller-scale extension requires measured limits first.

## First discriminating test: phase-dependent transfer at fixed core

**Question:** can two physically delivered boundary perturbations change the
signed angular-momentum transfer across the central surface through their
correlations, with that contribution distinguishable from changed mean transport
and external torque? This is an M1 test. No contraction success is required or
claimed from it. The normal/tangential response and optical calibration are
prerequisites, not assumed achievements.

1. Prepare a reproducible, approximately steady swirling base using measured
   balanced circulation and independent swirl input. Select one well-resolved
   core size, fixed R/H and one drive frequency from calibrated boundary-to-core
   response. Register actual amplitudes, frequency, strain/swirl, settling time,
   acquisition time, error budget and non-saturation limits before comparison.
   An initial candidate is b around 10 mm with diagnostic R/H around 25 mm;
   these are interior surfaces, not locations of actuators. All actuators remain
   at the vessel boundary. No interior stirrer is introduced.
2. Use a balanced m=4 normal pattern and an independently driven m=4 tangential
   pattern with the same temporal waveform and controllable angular phase.
   Verify instantaneous zero net normal flux for the realized finite footprints;
   an ideal Fourier label is insufficient. Use a consistent port impedance or
   realized velocity model, not independently prescribed pressure and velocity.
   Proposed comparison conditions are off, normal only, tangential only, and
   both at angular phases 0, pi/2, pi, 3*pi/2. Keep the realized mean normal
   throughput and mean swirl drive matched where possible, logging complete
   flow/torque histories. Commands alone do not establish matched delivery.
   These seven conditions form one test protocol, not seven authorized runs.
3. Randomize condition order within at least five independently prepared blocks.
   Use a fixed settled window of at least ten full cycles per condition, with
   at least twenty acquired time samples per cycle as an initial sampling
   target. Calibrate faster fluctuations/aliasing and effective independent
   samples separately; these counts alone do not establish stress convergence.
   Preserve switching transients and startup/end inventories even when they
   are outside the settled comparison window. No adaptive search for a
   favorable phase/window after inspecting results.
4. Reconstruct U, C_rtheta and C_ztheta on the complete central side and caps,
   gradients for viscous torque, and J at both endpoints. Also measure the
   surrounding budget/port and wall angular input. Fit realized interior
   mode amplitudes and phase, rather than substituting commanded phase.
   Monitor base strain, core position, U_p, circulation, pressure and temperature.
5. Compare the phase-reversed stress impulses and complete integrated budgets.
   Single-input controls expose background/self responses. Opposite phases
   isolate a cross contribution only to the extent measured response linearity
   and repeatability justify it; nonlinear changes are retained in the budget.
   Report both the correlation reversal and its nonzero **net surface transfer**.

For a simple local diagnostic ansatz, at a specified r,z,

```text
u'_r     = A*cos(m*theta)*cos(omega*t)
u'_theta = B*cos(m*theta+phi)*cos(omega*t+delta)
mean_theta,time(u'_r*u'_theta) = (A*B/4)*cos(phi)*cos(delta),  m nonzero integer.
```

The familiar A*B*cos(phi)/2 applies to angular averaging of steady spatial
patterns; an additional sinusoidal time average supplies another factor 1/2
and a lag factor. This identity is not a divergence-free boundary-to-core
solution. General modes have cross-coupled components, harmonics and spatially
varying lag; directly measured surface covariance is authoritative. A commanded
phase reversal may fail to reverse the interior transfer. That is a useful
result, not grounds to assume a phase correction worked.

**Decision:** M1 is supported only if the phase-dependent stress impulse has a
95% interval excluding zero, its sign reverses for a declared opposite-phase
pair, the full budget closes at the specified sensitivity, and a mean-only
balance misses that resolved component. Direct actuator impulse differences
must be matched or bounded below one third of this contrast; otherwise report
boundary-driven redistribution with confounded attribution, not a clean phase
mechanism. Changed mean advection/viscous torque are measured in each condition,
not assumed equal or subtracted as an undocumented correction. Correlated
uncertainty and shared-data residuals must be retained; closure is a necessary
consistency check, not independent causal proof.

A resolved null bounds the transfer at that operating point. Unresolved faces,
large systematic error, drift, saturation, a missing core or unclosed budgets
make the result inconclusive. Even a pass establishes only this angular-transfer
analogue; it does not verify the paper's residual cancellation, shear-powered
amplification, axial momentum mechanism or useful contraction range.

## Completion and next decision

R192 completed the [conditional operating point and detectability](FIXED_CORE_OPERATING_POINT_R192.md)
specified below. Neither route is admitted; its missing-response decision now
leads to the single [handoff task](../../SESSION_HANDOFF.md#next-task). The
following paragraph records R191's original next-step specification.

This document supplies the requested criteria/hardware/evidence table, allowed
differences, uncertainty rules, conditional radius-duration comparison and one
concrete test protocol. Its unspecified operating point is a declared design
input, not permission to run the existing failed B2 solver.

Next: make one quantitative operating-point and detectability sheet for this
fixed-core phase test. Compare recirculating normal ports plus tangential ports
against normal ports plus moving tangential wall, using one explicit vessel/
port/optical geometry. Bound flow, angular impulse, hydraulic loss and velocity/
stress uncertainty; identify missing transfer gains and a minimal calibration
that can decide between the routes. Finish with a supported candidate or an
explicit quantitative reason neither is admitted. Source/algebra work only;
stop before solver/controller code, CFD, procurement, hardware or physical work.
Follow the [handoff](../../SESSION_HANDOFF.md#next-task) for execution scope.

[Retained algebra and arithmetic checks](evidence/r191/README.md) validate the
conditional identities, including both central faces and phase averaging. They
do not validate fluid response or optical performance. No existing benchmark,
reference field, solver configuration or production pins were changed.
