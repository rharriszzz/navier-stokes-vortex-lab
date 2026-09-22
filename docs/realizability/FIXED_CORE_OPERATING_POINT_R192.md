# Fixed-core operating point and detectability — R192

R196 update: [cube adapter and diagnostic source](CUBE_ADAPTER_R196.md) pass
24 import-free checks; FEM remains untested and execution unadmitted. Earlier
next-step recommendations below are historical. Follow the single
[current task](../../SESSION_HANDOFF.md#next-task) for the one-fixture driver
and finite supervision source; stop before FEM execution.

2026-09-22; PC/WSL `daisy`. **Neither actuator route is admitted for execution.**
The candidate below makes the R191 test quantitative, but boundary-to-core gains,
return torque and measurement bias are unmeasured. The port route merits the
first response assessment; that is a study priority, not a hardware selection.
A local diffusion estimate strongly disfavors a distant oscillating wall in
quiescent water, but cannot rule it out in the prepared, circulating vortex.

This is a conditional design sheet, not a tank solution, pump specification,
procurement list or measured operating point. All numerical choices below are
our proposed design assumptions. They do not change historical benchmark gates.
The [R191 contract](ESSENTIAL_SIMILARITY_CONTRACT_R191.md) supplies the exact
central budget and M1 claim; its seven-condition protocol remains applicable.
Follow the single [next task](../../SESSION_HANDOFF.md#next-task).

## Geometry and operating-point sheet

Use a closed cylindrical water vessel, internal radius 100 mm and height
200 mm (6.283 L), with fixed top/bottom boundaries except declared ports and
moving patches. Take nominal rho=1000 kg/m³, nu=1e-6 m²/s and mu=1e-3 Pa s;
measure temperature and viscosity before using these as physical properties.
The laboratory-fixed budget cylinder is R=H=25 mm (height 50 mm), centered at
z=0. No actuator is placed on that imaginary cylinder.

Two side bands, each 30 mm high and centered at z=±60 mm, each contain sixteen
sectors at theta_j=2*pi*j/16. Each sector has a 4 mm bore normal supply port.
The port alternative adds one 4 mm bore inlet per sector angled 45 degrees
from inward radial toward positive azimuthal direction; its bore area is normal
to the jet, not its elliptical footprint on the vessel. Stagger the two port
rows within each band. Thirty-two 6 mm bore return ports, sixteen per cap on
r=35 mm, connect to separately metered upper/lower return manifolds.

The wall alternative replaces the angled inlets with tangential moving belt
patches occupying 80% of each sector/band, leaving gaps for the normal ports.
Wetted faces move locally along e_theta; belt returns, motors and seals remain
outside the water. This is a custom sealed assembly, not an existing product.
A single rigid rotating sleeve only supplies m=0 and cannot substitute for the
independently phased m=4 patches. Mean belt speed is provisionally limited to
0.05 m/s, with 0.02 m/s peak modulation; required mean speed/torque is unknown.
Ports and belts have finite footprints; their actual Fourier content must be
measured. Sixteen sectors support both m=4 phases in sampling algebra; this does
not prove that either ring drives a useful central mode.

Four synchronized exterior cameras view a 60×60×60 mm central volume through
a transparent cylinder inside a square water-filled optical bath with flat
outer windows. Proposed camera azimuths are 45,135,225,315 degrees, with small
alternating elevations (initially ±5 degrees). The central z=±30 mm sight region
avoids the actuator bands beginning at |z|=45 mm; ray paths and occlusion still
require verification. Filled-vessel multi-view calibration must include the
curved inner wall, refraction and depth error; the bath does not eliminate them.
Volumetric illumination and fluorescent 10–20 µm candidate tracers are proposed.
An additional synchronized wide-field optical view set or equivalent calibrated
inventory measurement is required for surrounding-fluid angular momentum: the
magnified central cameras alone do not close the enclosing budget. No such
measurement system has been validated.

| Quantity | Candidate or calculated scale | Meaning and limit |
|---|---:|---|
| Prepared Gaussian width b; peak radius r_c | 10 mm; 11.209 mm | Candidate profile only; measured radius must be independently fitted. |
| Peak swirl U_p; circulation Gamma | 0.050 m/s; 0.004923 m²/s | Sets dimensional angular-momentum scale. |
| Steady conditional strain a=2nu/b² | 0.020 s^-1 | U_r=-ar, U_z=2az locally; not a global boundary solution. |
| Central side inflow, total cap outflow | 0.2356 L/min each | Internal throughput, never pump demand. |
| Central U_r(R), U_z(H), U_theta(R) | -0.5, +1.0, 31.28 mm/s | Strain is weak compared with swirl. |
| Central angular momentum J | 64.635 µN m s | Actual exterior inventory and preparation impulse unknown. |
| Mean side flux; cap flux; viscous torque | -3.071; +2.585; -0.4854 µN m | Outward-positive flux convention; -Phi_side-Phi_caps+T_mu=0. |
| Normal supply per route | 2 L/min | Explicit trial plumbing flow; no inferred central-delivery efficiency. |
| Extra angled supply / wall route extra flow | 2 L/min / zero | Total pump trial flows 4 / 2 L/min; different base fields require matching at the core. |
| Core perturbation A=B; frequency | 2 mm/s; 0.1 Hz | Desired realized side amplitudes, not predicted from commands. |
| Boundary modulation | 20 mm/s peak bore or belt speed | Tangential component of angled modulation is 14.14 mm/s. |
| Settled window per condition | 100 s = ten cycles | At least five independent preparations; settling is additional and unknown. |
| Optical acquisition proposal | 2048 pixels over 60 mm; 200 Hz | Simultaneous performance unverified; offline processing first. |

The fixed-core test has nominal radius ratio 1 and elapsed comparison windows
of 100 s. No contraction or similarity-time decades are claimed. The prior
[10/100 s contraction tradeoffs](ESSENTIAL_SIMILARITY_CONTRACT_R191.md#radius-duration-and-engineering-demand)
remain conditional later targets. Seven windows in each of five blocks imply
3500 s of settled acquisition for one route, excluding preparation, calibration
and switching. This is planning arithmetic, not an authorized run duration.
Re_p=U_p*r_c/nu is about 560, so a quiescent linear Stokes response is not an
admitted surrogate for this swirling base merely because modulation is small.

## Plumbing, torque and wall scales

For either 32-port supply bank, q0=2/32=0.0625 L/min per bore and
U0=q0/(pi*d²/4)=0.08289 m/s. Command proposed realized bore speeds
U_j=U0+0.020*cos(4theta_j+phi)*cos(2*pi*f*t). The 16-sector sum of the
perturbation is zero at each time for all four comparison phases; U_j stays
positive. Normal supply and angled supply each maintain their own constant
trial total, and cap extraction balances their sum at each instant. Manifold
compliance/leakage breaks command-level balance; actual metered totals govern.
The angled bank changes both normal and tangential components and is not an
independent pure tangential boundary velocity. Record the full two-input response
matrix; do not erase its normal response by assumption. Bore flow or consistent
impedance is prescribed, never independent pressure and velocity on one port.

A 0.5 m long, 4 mm ID branch at maximum 0.10289 m/s has Re≈412. For a laminar
straight-tube estimate, dp_visc=32*mu*L*U/d²=102.9 Pa. Assumed minor-loss
K=2–10 adds 10.6–52.9 Pa. The oscillatory inertial pressure scale
rho*L*omega*U_hat is 6.28 Pa. Adding magnitudes gives a **conditional** branch
screen of 119.8–162.1 Pa, not a guaranteed loaded response (Womersley number
about 1.59; unsteady impedance and valve loss require calibration).

At 4 L/min a 12 mm ID common line has speed 0.589 m/s and Re≈7074; do not use
the laminar branch formula there. For total common-line length 2 m, assumed
Darcy factor 0.03–0.05 and summed K=10 give 2.61–3.19 kPa. A provisional total
loop design allowance is 10 kPa, including unresolved valves, returns, filters
and manifold losses. Hydraulic power Q*dp would then be 0.667 W for ports or
0.333 W for the 2 L/min wall-route loop, excluding motor inefficiency and belt
power. This allowance must be verified against the complete circuit; it is not
an upper bound on real losses. Closed-loop elevation heads cancel around the
full circuit, while local absolute pressures and trapped gas still matter.

The manufacturer [KNF FP 400 page](https://knf.com/en/uk/solutions/pumps/series/diaphragm-liquid-pump-fp-400)
was rechecked: maxima 4.6 L/min and 1 bar are separate catalog limits. They do
not establish 4 L/min at 10 kPa, reserve margin, pulsation or independently
phased liquid response. No pump is selected. The
[R185 survey](BOUNDARY_HARDWARE_FEASIBILITY_R185.md) supplies component options.

For uniform 45-degree inlet jets, neglecting profile corrections, mean angular
input is rho*R_v*sum(q_j*U_j*sin45). With no modulation it is 195.38 µN m.
The m=4 modulation adds a cycle-mean 2.843 µN m through U_j² even though its
net volume perturbation is zero. Ideal phase changes alone preserve this mean;
real phase-dependent loading need not. Return extraction
rho*integral(r*u_theta*u_n)dS, fixed-wall shear, nozzle traction and surrounding
inventory must be included. Momentum flux is not determined by q alone.
For a swirl-free start the prepared central J alone requires 64.635 µN m s;
if the exterior also stores positive swirl, the total preparation impulse is
larger. With counter-rotating exterior, no such global lower bound follows.
Dividing central J by gross inlet torque is not a spin-up time prediction.

For the wall screen derive the planar quiescent half-space equation
partial_t v=nu*partial_y² v, v(0,t)=W*cos(omega*t). Its harmonic solution is
W*exp(-y/delta)*cos(omega*t-y/delta), delta=sqrt(2nu/omega). At 0.1 Hz,
delta=1.784 mm; an optimistic 75 mm radial separation gives attenuation
5.54e-19. Gain 0.1 by this mechanism alone requires f<=0.000300 Hz, or a period
at least 3333 s. This is an exactly checked comparison equation, **not a bound
on the circulating, curved, finite tank**. Inward advection, swirl coupling,
pressure and three-dimensional transport could change it substantially. The
band-to-central-surface separation also has an axial component.

Wall speed amplitude 0.020 m/s at 0.1 Hz requires 31.83 mm displacement
amplitude (63.66 mm peak-to-peak), acceleration 0.01257 m/s². One sector pitch
is 39.27 mm at the wall; a sealed small-stroke slider is not interchangeable
with the proposed recirculating belt. The same local Stokes solution gives
shear amplitude mu*W*sqrt(omega/nu)=0.01585 Pa. Weighting absolute shear over
both bands and 80% coverage gives 47.81 µN m, a local-model torque envelope,
not delivered net m=4 torque or an estimate of steady drag. Ideal spatial
cancellation can make net oscillatory torque zero. Seal/bearing torque, moving
mass, mean-flow drag and their uncertainties are unknown; motor current alone
cannot resolve water torque without independent calibration.

## Detectability and error allocation

Define D as the difference of time-integrated outward stress flux Phi_C between
an opposite-phase pair, each integrated for T=100 s. The corresponding central
angular input is -D. For R191's ideal side ansatz with uniform A=B=0.002 m/s,
zero temporal lag and no cap contrast, the covariance contrast is AB/2=2e-6
m²/s² and

```text
W_s = 4*pi*rho*H*R² = 0.196350 kg
W_caps = 4*pi*rho*R³/3 = 0.065450 kg  (absolute weights of BOTH caps)
D_ideal = T*W_s*A*B/2 = 39.270 micro-N m s
abs(D_ideal)/T = 0.392699 micro-N m
```

The side-only value is a **sensitivity target**, not a divergence-free response
prediction. Let eta=D_actual/D_ideal, including spatial shape, lag, cap
cancellation and cross-coupling. Eta is unknown and may vanish or change sign;
no universal |eta|<=1 is claimed with this normalization. Every error threshold
must scale down with the actual resolved contrast if |eta|<1. Longer acquisition
does not improve torque/systematic-error ratios when both grow proportionally
to T. The target impulse is 61% of the nominal central J: a quasi-steady core
requires compensating mean/viscous transport, not storing this impulse unchecked.
The 2 mm/s radial perturbation is four times the conditional side mean inflow;
small amplitude relative to swirl does not establish linearity of the meridional
response. Single-input amplitude scaling and actual base changes are essential.

For this nominal target, R191's one-third residual and separate confound limits
are each 13.090 µN m s (mean torque difference 0.130900 µN m). Proposed
conservative allocations for **expanded uncertainty of the phase contrast**:

| Contribution to full central residual | Maximum µN m s | Practical implication |
|---|---:|---|
| Integrated stress-flux contrast | 4 | Coherent covariance-contrast error <=1.528e-7 m²/s² on all faces. |
| Mean advective-flux contrast | 4 | Illustrative normal-mean contrast bias <=3.056 µm/s if U_theta<=0.05 m/s and other errors are negligible. |
| Viscous-torque contrast | 2 | Coherent shear-contrast error <=7.639e-5 Pa, equivalent to 0.0764 s^-1 gradient error at nominal mu. |
| Endpoint inventory contrast | 2 | Must include all four endpoints, centering and reconstruction covariance. |
| Geometry, timing and remaining terms | 1 | Combined with the above, conservative sum 13 <13.090. |

These are allocations to be met, not measured errors or independent standard
deviations. Use joint propagated distributions/calibrated coverage for E and D;
shared image products are correlated. The mean-velocity illustration spends
the entire mean-flux allocation on one error and leaves no allowance for swirl
error: it exposes the bias challenge rather than certifying an optical system.
The viscous illustration uses the sum of all lever-arm weights. Real derivative,
viscosity and smoothing errors must share that allocation.

External mean-torque contrast, including uncertainty, must separately be no
larger than 0.130900 µN m. Relative to the gross angled inlet this is **0.0670%**;
if torque scales as U² a uniform speed mismatch alone must be below about
0.0335% (27.8 µm/s at the bore mean), before allocating return/wall/profile
errors. Relative to the wall's local unsigned oscillatory envelope it is 0.274%,
but that comparison is not a wall sensor accuracy specification. Neither route
has measured torque matching or complete inventory closure at these levels.
Matched commands, matched gross pump totals and pressure alone are insufficient.

At 60 mm/2048 pixels, pitch is 29.30 µm/pixel. Assuming 0.1-pixel independent
position noise per exposure and 5 ms displacement spacing gives
sigma_u=sqrt(2)*0.1*pitch/dt=0.829 mm/s per component. This is only a planar
localization calculation; depth error, calibration and tracking can dominate.
For speeds <=0.06 m/s, a quarter-pixel blur target requires exposure <=122 µs.
Require measured effective spatial support <=1 mm: the 22.42 mm peak diameter
then exceeds R191's ten-resolution-length target. Pixel count alone does not
supply that support or a radius confidence interval. A 1 mm two-point derivative
has raw noise about 1.172 s^-1, much larger than the allocated shear-contrast
error before averaging and bias analysis.

For the ideal modes, component RMS is A/2=B/2=1 mm/s across angle/time. With
independent zero-mean component noise sigma_u, noise-only product variance is
sigma_u²*(A²+B²)/4+sigma_u⁴. An approximate expanded opposite-condition error
is 2*sqrt(2)*sigma_product/sqrt(N_eff). Reaching the covariance allocation alone
needs **N_eff>=633** independent paired sampling units under these assumptions.
The 20,000 frames per window do not establish N_eff: track overlap, spatial
correlation, real fluctuations, drift and cross-camera errors reduce information.
Five preparations are still required; extra frames do not replace them. A
correlated velocity-noise covariance of order sigma_u²=6.87e-7 m²/s² exceeds
the allocated 1.53e-7 floor; calibrate its phase dependence explicitly.

[Dantec's volumetric PTV description](https://www.dantecdynamics.com/solutions/fluid-mechanics/volumetric-velocimetry-tomographic-piv-and-tomographic-ptv/tomographic-ptv/)
was rechecked: three/four images reconstruct 3D particle positions, with water
tracers and laser/LED illumination. It does not establish this design's frame
rate, uncertainty, gradient support or processing delay. Particle density/size,
settling, centrifugal slip, illumination, missing tracks and reconstruction bias
remain calibration inputs. As a screening assumption only, 20 µm spheres with
density 1030 kg/m³ in nominal water have Stokes-drag settling speed
(rho_p-rho)*g*d²/(18*mu)=6.54 µm/s; 10 µm gives 1.64 µm/s. The former exceeds
the illustrative mean-contrast error budget unless common-mode cancellation
or a calibrated correction is demonstrated. These assumed particle properties
are not a vendor specification; confinement, acceleration and preferential
sampling still require assessment. Feedback, if later developed, receives noisy delayed
estimates; this initial diagnostic uses synchronized raw images offline.

## Minimal response and calibration specification

The immediate missing information is the loaded, complex boundary-to-central
surface response at 0.1 Hz about this prepared core, together with a noise/torque
floor. A scalar amplitude at one point is insufficient. This specification does
not authorize acquisition or a new CFD calculation.

1. **Base and conservation:** establish one reproducible steady core near the
   sheet values for each route. Register all measured profiles, total/individual
   branch flow, pressure, wall state, upper/lower angular extraction and central/
   enclosing inventories. State uncertainties and a settled-window criterion.
   A changing exterior reservoir cannot masquerade as a settled preparation.
2. **Two-input response:** use off, normal-only and tangential-only at 0.1 Hz,
   with realized boundary modulation 0.01 and 0.02 m/s to check local amplitude
   scaling. Retain complex response of all three velocity components over the
   entire central side/caps, and volume data for J; include cross-components,
   both rings, realized m=4 phase, harmonics and m=0 drift. The normal and
   tangential command-to-velocity columns are independent experiments, not an
   assumed diagonal matrix. Record input normalization before interpreting rank.
3. **Necessary sensitivity:** absent cross-coupling/cap cancellation, obtaining
   A=2 mm/s from 20 mm/s normal modulation needs |G_rn|>=0.10. Angled ports need
   |G_theta,t|>=0.1414 relative to their 14.14 mm/s tangential component; walls
   need >=0.10 relative to belt speed. More generally the normalized net response
   must yield |D|>=39.270 µN m s to use this sheet's fixed error allocations.
   Product gains and phase enter; individual thresholds alone do not admit a
   route. For simple side modes eta_shape*|G_rn*G_theta,t|*cos(delta) must reach
   magnitude 0.01414 for ports or 0.0100 for walls. Calibrate eta_shape from
   complete faces rather than setting it to one.
4. **Cross response:** after the base, optical and single-input gates, the R191
   seven-condition comparison (off, each single input, four paired phases) is
   the minimal full test. Shared-input cross components and nonlinear harmonics
   can alter the prediction. Seek reversal in realized net stress transport,
   matched/bounded external impulse and an explained mean-flow response. Single
   inputs predict sensitivity only if the measured small-signal regime holds.
5. **Instrumentation response:** measure plumbing/belt gain and lag under water
   load, optical error covariances/aliasing and complete water torque. A proposed
   timing allocation is <=5 degrees at 0.1 Hz (139 ms), with jitter <=5 ms;
   deterministic lag may be estimated, not assumed absent. Test saturation and
   drift; 200 Hz imaging does not demonstrate actuator bandwidth. Use filled-tank
   calibration and motion/reference checks, then processing/support convergence,
   independent blocks and uncertainty propagation for the actual surface sums.

Admit a candidate only when these measured or independently validated response
and error quantities satisfy the R191 gates within the stated flow/speed/loss
allowances. If both fail, report the point-specific limit and whether loss of
gain, cap cancellation, torque confounding or optical bias dominates. No failure
here proves all boundary-driven vortex analogues impossible.

## Decision and next task

R194 completed the [base-flow boundary and verification contract](PORT_BASE_FLOW_CONTRACT_R194.md).
Only a separate verification prototype is admitted next; no tank implementation,
CFD execution or hardware route is admitted. Follow the single
[current task](../../SESSION_HANDOFF.md#next-task). The original decision below
is preserved as historical context.


R193 completed the [requested transport screen](INWARD_TRANSPORT_SCREEN_R193.md).
It cannot bound tank gains without a realized base and coupled response; neither
route is admitted. The single [current task](../../SESSION_HANDOFF.md#next-task)
now specifies the port-driven base-flow calculation. The paragraphs below
preserve R192's original decision and next-step specification.

**Neither route passes an evidence-based admission now.** Ports require an
unmeasured normal gain near 0.10, tangential gain near 0.1414 in the simple
uncoupled screen, and external torque contrast below 0.1309 µN m. The wall
requires a comparable gain despite severe quiescent diffusion attenuation and
unmeasured advective transport. Both lack a demonstrated covariance-contrast
floor near 1.53e-7 m²/s² and complete mean/viscous/inventory closure. These
quantitative gaps prevent selection; the central Gaussian algebra fills none.

**Next: assess whether inward transport can rescue the wall response at this
point, using a bounded analytical advection–diffusion screen and its validity
limits.** Compare it with the quiescent wall calculation and port delivery times,
including m=4 azimuthal advection and the actual band/core separation. Decide
whether that reduced calculation can bound the needed gains or whether only a
validated response about a realized base can answer. Produce the equation,
assumptions, dimensionless/time-scale estimates and error/admission criteria;
no solver implementation or run. Do not prescribe the Gaussian mean throughout
the vessel to manufacture favorable delivery. Stop at that decision boundary.

Retain GPT-6 Astra/high on PC/WSL `daisy` for the unresolved physics and
measurement design. Official [Astra documentation](https://developers.openai.com/api/docs/models/gpt-6-astra)
was rechecked with OpenAI Docs and lists high support; no model switch or account
availability claim. Reconsider a cheaper model only once work is fully specified
and mechanical, after rechecking availability. B2 accuracy remains failed,
q64/q96 unused and R021 deferred. No solver/controller, CFD/FEM, hardware,
procurement, physical/optical execution, trajectory, render or encode ran.

[Retained checks and calculated values](evidence/r192/README.md) cover arithmetic,
phase/balance identities and the comparison diffusion equation, not the tank.
