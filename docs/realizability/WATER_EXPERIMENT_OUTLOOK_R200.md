# Water experiment: prospects and likely limits — R200

[The consolidated essay](WATER_EXPERIMENT_FEASIBILITY_AND_COST.md) covers the
physical outlook, ideal-instrument limits and both cost routes in one narrative.
This file retains the more detailed supporting analysis.

2026-09-22. Conceptual assessment requested by the user; no implementation,
CFD, equipment selection or experiment performed. Numerical examples below are
conditional estimates, not measured capabilities. Project execution remains
paused; follow the [current handoff](../../SESSION_HANDOFF.md#next-task).

The [R201 ideal-hardware thought experiment](#r201-if-sensing-and-actuation-were-perfect)
separately removes sensing/actuation limits and examines intrinsic water physics.
Its more optimistic finite-range outlook does not revise the practical hardware
forecast below.

[R202/R203 cost versus captured dynamics](COST_VERSUS_CAPTURED_RANGE_R202.md)
restores real sensors/actuators and compares atmospheric and pressurized options,
with both from-scratch and equipped-lab costs, explicit labor exclusions and
conditional scientific milestones.

**My judgment: a useful water experiment with severalfold core contraction is
plausible enough to pursue. I am cautiously optimistic about roughly 10 mm to
3 mm, less confident about 10 mm to 1 mm, and doubtful about 10 mm to 0.1 mm
in the present vessel concept.** Demonstrating the specific perturbation-driven
momentum-transfer mechanism is harder than producing a contracting vortex.
I am already doubtful that distant wall motion alone, without effective inward
transport, can deliver the required perturbations. Balanced boundary ports and
swirl input give a more promising hypothesis, still unvalidated.

The likely first obstacles are **boundary-to-core delivery and measurement
bias**, rather than water becoming appreciably compressible. Temperature control
may matter early for precise measurements, while bulk overheating and intrinsic
sound absorption probably do not set the first contraction limit. These are
engineering judgments; the repository has not yet demonstrated even the first
boundary-driven contraction. Its current fixed-core proposal has radius ratio
one, and the nonlinear numerical verification has not run.

## What “one or two orders of magnitude” means

I interpret the earlier experimental ambition primarily as decades in the
similarity-time variable, but the alternative radius interpretation matters:

| Intended range | If radius is proportional to square root of remaining similarity time | My present forecast |
|---|---|---|
| One decade in similarity time | About 10 mm → 3.16 mm radius | Cautiously optimistic for a useful analogue, conditional on a working boundary-driven base. |
| Two decades in similarity time | About 10 mm → 1 mm radius | Ambitious stretch goal; I would not promise it. Delivery, coherence and quantitative optics are likely limits. |
| One decade in radius | 10 mm → 1 mm | Same difficult goal as the preceding row. |
| Two decades in radius | 10 mm → 0.1 mm | Doubtful for the present apparatus concept; likely requires major changes in geometry, optics and actuation. |

These conversions are conditional, not a demonstrated exponent from the paper
or the experiment. For r proportional to tau^p, the relation is
D_tau = log10(r_initial/r_final)/p. The
[R191 similarity contract](ESSENTIAL_SIMILARITY_CONTRACT_R191.md) requires
measured radius, elapsed seconds and justified scaling; choosing a convenient
terminal time does not establish decades. Speed decades are another quantity:
only under a fixed-circulation, fixed-profile illustration does speed grow as
inverse radius. A slowly shrinking ring of beads does not establish a shrinking
vortex core or the paper-inspired mechanism.

## The mathematical idealization and real water

Yes: the reference paper formulates **incompressible** Navier–Stokes with fixed
positive viscosity and a smooth force in the fluid volume. It has no coupled
water-temperature or acoustic evolution equation. Its theorem is not a
boundary-actuated tank construction. This assessment uses those stated model
assumptions, without attempting to assess the proof. See
[the paper, Theorem 1.1 and equation (1.1)](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=1).

Water has finite compressibility, but “incompressible” can be a very accurate
flow approximation when pressure-induced density changes are small and sound
crosses the apparatus much faster than the flow changes. Viscosity already
removes mechanical energy in the incompressible model. What constant viscosity
omits is the feedback of the resulting temperature change on the motion.

Rounded reference properties near 20 °C and atmospheric pressure are density
998 kg/m³, dynamic viscosity 1.00 mPa s, kinematic viscosity about 1.0e-6 m²/s,
sound speed 1482 m/s, heat capacity about 4180 J/(kg K), and thermal conductivity
about 0.60 W/(m K). Viscosity falls to about 0.890 mPa s at 25 °C: roughly an
11% change over 5 °C. These are reference-property scales, not calibration of
our seeded water. [IAPWS liquid-water correlations, especially §3 and Table 8](https://iapws.org/technical-guidance/release/LiquidWater.download).

Distributed forces do exist physically—gravity is an obvious example. The
unavailable capability here is an **arbitrary independently prescribed vector
force throughout the water**. Uniform gravity can be absorbed into hydrostatic
pressure for homogeneous water; temperature-induced density differences add
buoyancy that cannot generally be removed that way. Boundary ports remain
boundary actuation even though the injected water transports momentum inward.
The optical tracers are measurement aids, not interior actuators.

Replacing a prescribed volume force with boundary inputs is a larger change
than replacing exact incompressibility with low-speed water. Boundary pressure
cannot cancel an arbitrary interior force with nonzero curl. Different finite
flows may still reproduce the essential dynamics. That is why I can be
optimistic about an analogue without predicting replication of the full field.

## Why delivery from the boundary worries me first

Pressure communicates rapidly through water, but that does not mean a wall can
rapidly establish any desired interior swirl or shear pattern. In homogeneous
incompressible flow, the curl of the pressure gradient vanishes: vorticity must
be generated, transported, stretched and diffused consistently with the flow.
A pressure sensor seeing a strong command does not prove that the core received
the intended velocity perturbation.

The current [R192 candidate](FIXED_CORE_OPERATING_POINT_R192.md) is a cylinder
of radius 100 mm and height 200 mm, about 6.28 L. It differs from the older
20 × 20 × 30 cm concept. Its actuators are on the actual vessel wall; the
25 mm-radius diagnostic surface is imaginary. In a quiescent comparison,
a tangential wall oscillation at 0.1 Hz has penetration length
sqrt(nu/(pi f)) = 1.78 mm. Across a 75 mm gap its amplitude factor is about
5.5e-19. This is **not a bound on a circulating tank**: inward transport can
help enormously, but transport paths, entrainment and phase must actually work.
The [R193 transport review](INWARD_TRANSPORT_SCREEN_R193.md) explains why
neither fast port velocity nor total pump flow establishes that result.

For the same desired 20 mm/s sinusoidal wall speed at 0.1 Hz, displacement
amplitude is U/(2 pi f) = 31.8 mm. Small-stroke diaphragms are not automatically
capable of that motion. Recirculating ports avoid a finite stroke limit, but
introduce pressure losses, jets, return-flow coupling and phase errors. The
loaded fluid response, not a motor's electronic update rate, sets usable
control bandwidth. Acoustic compliance in hoses or trapped gas can spoil that
response even at low flow speeds.

The strain needed to oppose viscosity grows as the core shrinks. An explicit
illustration from R191 uses Gaussian vorticity width b, local flow u_r=-a r,
u_z=2a z, and b² declining linearly from b0² to bf² in 100 s:

```text
k = (b0² - bf²)/100 s
required final a = (4 nu + k)/(2 bf²)
central throughput = 4 pi a H R², with R = H = 25 mm
```

| Final Gaussian width b | Final strain a | Throughput across the fixed central surface |
|---:|---:|---:|
| 3 mm | 0.273 s^-1 | 3.21 L/min |
| 1 mm | 2.495 s^-1 | 29.4 L/min |
| 0.3 mm | 27.8 s^-1 | 327 L/min |
| 0.1 mm | 250 s^-1 | 2945 L/min |

These are **internal comparison-flow numbers, not pump requirements or global
lower bounds**. They assume the same strain over a fixed 50 mm-diameter,
50 mm-high diagnostic cylinder; concentrating strain in a smaller region changes
the throughput. For this Gaussian, measured peak radius is 1.1209 b, so widths
are not interchangeable with peak radii. The last two rows are extrapolations
to expose the cost of extending this particular profile, not selected targets.
Slowing the trajectory cannot remove the minimum a=2 nu/b² needed to hold its
width against diffusion. The more modest 10 s, 10→3 mm-width example already
requires peak central throughput 8.57 L/min. This is why “we can always run
more slowly” is only a partial answer.

Loss of coherent flow may precede a hardware limit: jets can bypass the core,
return circulation can interfere, and instabilities can produce wandering,
multiple cores or uncontrolled fluctuations. There is no universal Reynolds
number at which this happens. With fixed circulation and an unchanged profile,
U b/nu stays constant during contraction; shrinking alone does not prove that
Reynolds number rises. Stability still changes with strain, geometry and the
surrounding flow.

## Compressibility, sound and bubbles

From K_s=rho c², water's acoustic bulk modulus is about 2.19 GPa. A 10 kPa
pressure change corresponds to a fractional density change of order 4.6e-6;
the slow isothermal value is very similar near room temperature. At 0.05 m/s,
Mach number U/c is 3.4e-5; at 0.5 m/s it is 3.4e-4. Sound crosses a 0.20 m tank
in about 0.135 ms. These estimates make constant-density modeling quite
credible for gently driven millimetre-scale core motion, subject to the actual
pressure history and temperature gradients.

For orientation, extend the R192 speed of 0.05 m/s at b=10 mm with fixed
circulation and the same Gaussian profile:

| Width b | Peak speed U | Viscous time b²/nu | Dynamic-pressure scale rho U²/2 |
|---:|---:|---:|---:|
| 10 mm | 0.050 m/s | 100 s | 1.25 Pa |
| 3 mm | 0.167 m/s | 9 s | 13.9 Pa |
| 1 mm | 0.50 m/s | 1 s | 125 Pa |
| 0.3 mm | 1.67 m/s | 0.09 s | 1.39 kPa |
| 0.1 mm | 5.0 m/s | 0.01 s | 12.5 kPa |

Even the last row has Mach number only 0.0034. The pressure column is neither
the actual vortex suction nor the signal at a wall sensor; both depend on the
whole velocity field and boundary conditions. The viscous times are not
actuator frequencies or camera-rate specifications.

**Intrinsic sound absorption is unlikely to consume the useful vortex motion
first.** Acoustic compression waves and slowly evolving vortical motion are
different parts of the dynamics. Water's absorption of sound rises strongly
with frequency; NPL distinguishes pure-water absorption from dissolved-salt
relaxation. That supports the qualitative low-frequency assessment, not an
attenuation coefficient for our tank or a seawater formula transplanted to
fresh water. [NPL acoustic absorption physics](https://resource.npl.co.uk/acoustics/techguides/seaabsorption/physics.html).

Sound can nevertheless matter early as pump noise, pressure-channel
contamination, wall vibration, resonance or water hammer. A rigid 0.20 m
half-wave cavity estimate is c/(2L)≈3.7 kHz; flexible walls, hoses, reservoirs
and gas pockets can have much lower resonances. For an abrupt flow stop, the
ideal water-hammer scale rho c_eff DeltaU is about 0.148 MPa for DeltaU=0.1 m/s
if c_eff equals the sound speed of water. Actual pipe compliance and closure
time govern the pulse. Low mean Mach number does not exclude such transients.
[Caltech water-hammer discussion](https://shepherd.caltech.edu/EDL/publications/reprints/WaterHammerIgnitionEDL2019-001.pdf).

**Bubbles and cavitation are more plausible early departures from the
single-phase water model than large bulk compression.** Air can enter through
returns or be trapped before any strong vortex forms. At 20 °C the vapor
pressure is approximately 2.34 kPa absolute. For an atmospheric-pressure
reference and an assumed pressure drop rho U²/2, exhausting that pressure
margin would require about 14 m/s. This is only a coefficient-one screen:
actual vortex profiles, nozzle losses, pump suction and transient minima can
reach low pressure sooner. Nuclei and dissolved gas affect inception, so there
is no universal critical core radius. Bubbles disrupt optics and change acoustic
response; a vortex connected to a free surface can entrain air independently
of vapor cavitation. [Brennen, Cavitation and Bubble Dynamics, Chapter 1](https://media.library.caltech.edu/CaltechBOOK:1995.001/chap1.htm).

## Heat: probably an accuracy problem before an overheating problem

For incompressible Newtonian flow, dissipation per unit mass is
2 nu S:S, where S is the symmetric velocity-gradient tensor. Vorticity alone
is not a heating rate: rigid-body rotation has no viscous shear dissipation.
If actual shear has characteristic size U/b, a local heating scale is
nu (U/b)²/c_p, up to profile factors and before conduction or advection.
The speed illustration above gives about 6e-9 K/s at b=10 mm, 6e-5 K/s at
1 mm, and 0.6 K/s at 0.1 mm. The last value is significant if sustained,
but over its 0.01 s viscous time it amounts to only about 0.006 K. Residence
time and the actual strain distribution matter; these are not temperature
predictions for a fluid parcel or the entire tank.

For a well-mixed 6.28 kg water inventory with no heat removal, the separate
whole-tank estimate is DeltaT=P_water t/(m c_p):

| Net heat retained in the water | Rise in 100 s | Rise in one hour |
|---:|---:|---:|
| 0.667 W | 0.0025 °C | 0.091 °C |
| 10 W | 0.038 °C | 1.37 °C |
| 100 W | 0.38 °C | 13.7 °C |

R192's 4 L/min at an assumed 10 kPa loop loss corresponds to 0.667 W of
hydraulic power. That is neither measured heating nor an upper bound: motor
heat transferred to water, belts, actual plumbing losses, illumination,
ambient exchange and cooling all change P_water. The external loop also adds
thermal mass. Pressure work ultimately dissipating into heat must not be
counted twice as both hydraulic power and viscous heating.

Near 20 °C, viscosity changes by roughly 2–3% per degree. A 0.1 °C drift can
therefore matter to a sub-percent balance long before the water feels warm.
A first conceptual temperature target might be repeatable bulk temperature
within about 0.1 °C, with spatial gradients measured separately; this is not a
validated error allocation. R192's much tighter differential torque test may
require better control or measured corrections.

Uneven heating also creates buoyancy. For orientation, a free-fall scale
sqrt(g beta DeltaT L), using beta≈2.1e-4 K^-1, DeltaT=0.1 K and L=50 mm, is
about 3.2 mm/s—comparable to the proposed 2 mm/s perturbations. This is not a
prediction of convection in a forced tank; stratification, viscosity and the
mean flow may suppress or redirect it. It shows why one bulk thermometer is
insufficient. Temperature gradients also affect optical calibration. I would
expect thermal drift to complicate a long, precise phase comparison before
viscous heating prevents an initial short contraction.

## Pressure sensors and laser/camera measurements

**Pressure sensing may run out of information before it runs out of speed.**
At U=0.05 m/s, the dynamic-pressure scale is only 1.25 Pa, on top of about
2 kPa hydrostatic variation over the vessel height and potentially larger pump
signals. A 0.1 mm elevation mismatch corresponds to about 0.98 Pa. Differential
connections, drift and calibration therefore matter. The wall signal from a
shrinking fixed-circulation core may change very little because the exterior
swirl is already close to Gamma/(2 pi r); higher sampling rate cannot recover
a state that barely affects the observations. Pressure alone also does not
supply the complete angular-momentum flux.

For slow changes and the 0.1 Hz proposal, choose sensing principles with a
measured low-frequency response. Piezoelectric pressure sensors are normally
AC coupled and cannot simply be assumed to retain static pressure throughout
a long comparison. DC-capable wet differential sensing is a plausible route;
no particular sensor's noise floor is established here.
[PCB's pressure-sensor technical explanation](https://www.pcb.com/resources/technical-information/introduction-to-pressure-sensors).

**For optics, seeing the beads is easier than resolving the velocity gradients
and correlations.** The proposed physical tracers are roughly 10–20 micrometres,
not the large rendered beads. A camera and illumination measure displacement;
3D velocity needs suitable simultaneous views and calibration. Commercial
volumetric PTV supplies a possible measurement method, not a guarantee of our
resolution or latency. [Dantec volumetric PTV](https://www.dantecdynamics.com/solutions/fluid-mechanics/volumetric-velocimetry-tomographic-piv-and-tomographic-ptv/tomographic-ptv/).

At 2048 pixels across the proposed 60 mm field, pitch is 29.3 µm. A core with
1 mm **radius** spans 68 pixels across its diameter; a 0.1 mm-radius core spans
only 6.8. Under R191's ten-independent-resolution-length criterion, the former
needs effective spatial support no larger than 0.2 mm, the latter 0.02 mm.
Pixels, overlapping interrogation windows and independent velocity information
are different quantities. The existing fixed-core proposal's <=1 mm support
would not suffice for the 1 mm-radius milestone. Magnification helps locally,
but we still need surrounding-flow and both-cap measurements to close budgets.

R192's illustrative displacement error is already 0.829 mm/s per component
at 5 ms spacing, versus a desired 2 mm/s perturbation. Shorter spacing helps
track faster motion but increases velocity uncertainty for unchanged position
error. At 0.5 m/s, a quarter-pixel motion-blur target at the same magnification
requires exposure below about 15 µs. That constrains illumination and photon
count. Camera frame rate alone does not establish resolved turbulence, accurate
products or timely feedback.

A Stokes-drag particle relaxation screen, rho_p d²/(18 mu), is approximately
6–23 µs for density 1030 kg/m³ and diameters 10–20 µm. It suggests simple
response lag need not defeat slow millimetre-scale motion. It is not a full
near-neutrally-buoyant tracer model: added mass, history forces, density mismatch,
centrifugal slip, finite size and preferential sampling matter. R192's assumed
20 µm particle settles at 6.54 µm/s, already exceeding its illustrative
3.06 µm/s mean-contrast bias allocation. Repeated images cannot average away
an unknown systematic slip or optical covariance bias.

That strict mechanism test is the strongest reason for caution **already at
the initial size**. Its ideal stress-transfer contrast is only 0.3927 µN m;
the separate residual and external-torque-confound allowances are each
0.1309 µN m. The proposed covariance-contrast allocation is 1.528e-7 m²/s²,
and the external-torque allowance is about 0.067% of the illustrative gross
angled-port input. These are unverified requirements from
[R192's error budget](FIXED_CORE_OPERATING_POINT_R192.md#detectability-and-error-allocation).
We could obtain an attractive, contracting water vortex and still fail to
show that the perturbations caused the claimed net transfer.

## My expected order of difficulty

| Potential limit | When I expect it to matter | What would change my assessment |
|---|---|---|
| Boundary delivery, actuator authority and coherent flow | Immediately; increasingly from a few millimetres toward 1 mm | A measured or validated coupled response showing adequate gain, phase and core feeding within loaded actuator limits. |
| Optical/systematic error and external torque accounting | Immediately for the mechanism claim; likely severe below 1 mm with current wide-field optics | Calibrated 3D spatial support, tracer bias and full-budget uncertainty below the actual effect. |
| Pressure information, drift and plumbing noise | Potentially immediately for pressure-only feedback | Demonstrated ability to distinguish core states, with measured low-frequency transfer and synchronized optics. |
| Thermal gradients and viscosity drift | Long comparisons and sensitive balances, even at the starting core size | Measured heat input, spatial temperature history and propagated corrections. |
| Air, cavitation and hydraulic transients | Any size with poor plumbing; stronger suction raises concern | Absolute-pressure histories, controlled gas content and characterized transient response. |
| Intrinsic acoustic absorption / appreciable bulk compressibility | Unlikely to set the first 10→3 mm or 10→1 mm limit at the illustrative speeds | Actual acoustic power, pressure or transient scales much larger than assumed. |

There is no honest universal breakdown radius without circulation, profile,
contraction schedule, actual plumbing response and sensor errors. My working
forecast is: **10→3 mm is a defensible first ambition; 10→1 mm should earn its
way through measured delivery and optical performance; 10→0.1 mm is not a
credible promise for this concept.** Confidence is lower at every stage for
the stronger claim of perturbation-assisted contraction than for contraction
and spin-up alone. This outlook does not establish a physical limit or rule out
a different boundary-driven design.

For a later design review, the most useful next document would be a single
operating envelope linking measured peak radius, swirl speed, elapsed time,
strain, boundary demand, pressure margin, optical support and thermal/error
budgets. Start with the modest contraction and show exactly what reaching
1 mm would require. That is a proposed next review, not an instruction to resume
implementation or build hardware. The [handoff](../../SESSION_HANDOFF.md#next-task)
retains the paused execution task and the user's control over resumption.

## R201: if sensing and actuation were perfect

Added 2026-09-22 at the user's request. **Granting perfect flow delivery makes me
more optimistic about the first one or two similarity-time decades, and removes
my hardware-based reason for doubting a 0.1 mm core. Water itself is not clearly
excluded at that scale under the illustrative speeds.** I would still expect
increasing departures from constant-property incompressible dynamics. Near
atmospheric pressure, my candidate for the first dramatic change is cavitation;
with cavitation suppressed, local heating and compressible/acoustic dynamics
become the main concerns. Their order depends on the actual trajectory.

I take “perfect” to mean accurate sensing and whatever boundary motion is
needed to deliver the desired finite-scale flow whenever that flow is physically
consistent. I set aside actuator stroke, gain, latency, measurement error and
ordinary control instability. I do not quietly grant a new equation of state,
an interior heat sink or the ability to make liquid water sustain arbitrary
tension. If perfection instead means exact reproduction under all conditions
by definition, then failure has been excluded by the premise; the useful
question is where real water makes that premise inconsistent.

### Exact agreement is generally lost before a visible failure

A fluid parcel in the incompressible model keeps its volume even while changing
shape: radial contraction is compensated by motion in other directions. It
is not simply being squeezed into a smaller volume. The new issue is how real
water responds to the pressure and heat needed for that motion.

For single-phase water of fixed composition, combine mass conservation with
its equation of state. With D/Dt following a parcel, thermal expansion beta
and isothermal compressibility kappa_T, the exact local identity is

```text
D rho / Dt = -rho div(u)
d rho / rho = kappa_T d p - beta d T
div(u) = beta D T / Dt - kappa_T D p / Dt
```

Thus the target's div(u)=0 requires a particular cancellation between material
pressure and temperature changes. Arbitrary pressure histories and viscous
heating will not automatically satisfy it. Small density changes can make the
incompressible approximation excellent, but exact simultaneous reproduction
of velocity, pressure and material properties is a stronger requirement.
The identity is our combination of continuity and thermodynamic derivatives;
see [MIT's thermal-flow notes, §§4.1–4.2](https://web.mit.edu/fluids-modules/www/fluid_transport/4-1-2energy.pdf).

For example, an imposed velocity might remain close to its target while the
pressure field acquires compressible corrections, temperature changes, and the
viscous stress becomes div[mu(T,p)(grad u + grad u transposed)] with the
appropriate dilatational stress added. The old constant-nu Laplacian then no
longer represents the complete viscous acceleration. Sensors could report these
departures perfectly; sensing would not remove them. Changes in momentum balance
would have to be supplied physically, within the granted boundary-only premise.

### Viscosity remains part of the target; heating changes its parameters

The original mathematical model already includes viscous dissipation. There
is no additional generic “viscosity suddenly wins” argument if we grant that
the intended viscous solution is being delivered. The new effects are the
energy becoming heat and the dependence of viscosity and density on that heat.

For a compressible Newtonian liquid, one useful temperature equation is

```text
rho c_p D T / Dt = beta T D p / Dt + Phi + div(k_th grad T)
Phi = viscous stress : grad u
```

Here T is absolute temperature and k_th is thermal conductivity. This form
follows from the internal-energy balance and the equation of state; no imposed
volumetric heat source has been added. Compression can reversibly heat the
liquid, expansion can cool it, and viscous dissipation Phi irreversibly creates
entropy. Sound absorption contributes to dissipation and is not an extra energy
loss to add again. [Energy-balance foundation in the MIT notes](https://web.mit.edu/fluids-modules/www/fluid_transport/4-1-2energy.pdf).

Warmer water near room temperature has lower viscosity. At unchanged strain
that can permit a narrower vortex and modify the balance that sets its growth,
instead of simply stopping it. Uneven temperature can also create buoyancy and
new vorticity when pressure and density gradients are not aligned. The resulting
flow could remain spectacular while departing from the proposed similarity.
There is no general conclusion that this feedback necessarily causes thermal
runaway or necessarily arrests contraction.

Boundary cooling is not instantaneous cooling of the core. From the earlier
water properties, thermal diffusivity k_th/(rho c_p) is about 1.44e-7 m²/s.
Conductive equilibration over 1 mm takes roughly 7 s, versus the 1 s viscous
time at that scale. Advection and cold replacement water can remove heat much
faster than diffusion from a distant wall, but that needs an explicit thermal
and residence-time history even with ideal actuators.

A useful **conditional calculation**, not a prediction of the paper's solution:
retain U b = 0.0005 m²/s and let b² decrease at k=9.9e-7 m²/s, corresponding to
10→1 mm Gaussian width over 100 s. Continue that same schedule toward smaller
widths. If a parcel experienced shear of order U/b throughout, neglecting heat
exchange and pressure heating, the cumulative shear-heating scale would be

```text
Delta T_scale = [nu (U b)² / (c_p k)] (1/b_final² - 1/b_initial²).
```

It is about 0.000060 K at 1 mm, 0.0060 K at 0.1 mm, and 0.60 K at 0.01 mm.
These values assume one particular shear factor and parcel exposure; actual
swirl, axial strain, finer perturbations and fluid exchange change them. A
high instantaneous heating rate does not prove a large accumulated temperature
rise if the high-shear stage is very short. Conversely, fine oscillations can
have much larger gradients than the core-width estimate captures.

A bounded total kinetic energy does not bound maximum local temperature or
local dissipation. Concentrating energy into a shrinking mass can raise local
energy per kilogram without making the entire tank hot. We need the full
finite target's gradient and parcel histories to judge that possibility.

### Near atmospheric pressure, I would watch for cavitation first

In a swirling core, radial pressure balance can produce strong suction at the
axis. As concentration increases the pressure depression can grow roughly as
rho U² while the density change is still tiny. This can reach the liquid's
phase-change boundary well before Mach number approaches one.

The Gaussian illustration permits a more specific calculation than the earlier
dynamic-pressure scale. Assume quasi-steady radial centrifugal balance for the
swirl contribution, constant density and

```text
u_theta = C/r (1 - exp(-r²/b²)),   C = Gamma/(2 pi).
p_far - p_axis = rho integral_0^infinity u_theta²/r dr
              = rho C² ln(2)/b²
              = 1.702 rho U_peak².
```

The last coefficient uses the Gaussian swirl maximum at r/b≈1.1209. At a
far-field reference pressure of 101.325 kPa and vapor pressure about 2.34 kPa,
this model reaches vapor pressure at U_peak≈7.63 m/s. With U_peak b=0.0005 m²/s,
that means **b≈66 µm**, or swirl-peak radius about 73 µm. At b=0.1 mm it instead
predicts a swirl pressure depression of about 42.5 kPa, leaving a substantial
atmospheric margin. This is why the water alone does not rule out that width
in the ideal-hardware thought experiment.

This is an infinite-profile swirl calculation, not a tank cavitation forecast:
radial/axial acceleration, finite boundaries, background pressure and local
perturbation minima alter the pressure. Real nuclei and residence times control
bubble inception, and exceptionally clean water can temporarily sustain tension.
The estimate identifies **a plausible tens-of-micrometres departure in one
specified extrapolation**, not a universal cutoff.
[Brennen's discussion of nucleation and cavitation](https://media.library.caltech.edu/CaltechBOOK:1995.001/chap1.htm).

Once bubbles grow, the core may become a mixture or develop a vapor cavity.
Density, effective compressibility, angular-momentum transport and dissipation
then change substantially. Bubble growth and collapse can emit pressure pulses
and create local heating. A perfect actuator might sustain some new two-phase
flow, but it would not be the original homogeneous-liquid solution.

Raising background pressure could postpone cavitation. Unlike the arbitrary
pressure offset in constant-density incompressible equations, that offset has
physical consequences in water: it changes phase margins, density and material
properties. Pressurization therefore changes this thought experiment's outcome;
there is no intrinsic cavitation radius independent of pressure. Heating also
raises vapor pressure, coupling the thermal and cavitation limits.

A related alternative occurs in a completely filled, perfectly rigid, sealed
fixed-volume system: nearly uniform warming raises mean pressure rather than
letting water expand freely. The small-change estimate is
Delta p≈K_T beta Delta T, about **0.46 MPa per kelvin** near 20 °C. This uses
K_T≈2.2 GPa, not a claim that the actual ported tank is sealed or rigid. An
external compliant volume or pressure-regulated loop gives a different result.
It illustrates another way thermal effects can change pressure before any
large temperature rise. [Water-property derivatives: IAPWS](https://iapws.org/technical-guidance/release/LiquidWater.download).

### With bubbles suppressed, finite sound speed still changes the dynamics

The incompressible pressure constraint has no acoustic delay. Real water
transmits compression disturbances at finite speed. Relevant measures are
U/c and L/(c T_change), using the length and evolution time of the feature in
question. The finest oscillatory perturbation may set that scale, not the
visible core. An externally driven fast pressure variation can matter even
when mean flow speed is small. [Sound propagation and compressibility](https://www.feynmanlectures.caltech.edu/I_47.html).

When those ratios cease to be small, density changes and pressure waves must
be included. Acoustic radiation can carry energy away from the core, reflect
from boundaries and return; absorption converts some of it to heat. Strong
compressive waves can steepen into shocks, adding entropy and heating. Shocks
are a possible later regime, not an inevitable result of every shrinking
vortex, and sound emission alone is not proof of substantial damping.

For the same U b illustration and ambient sound speed, Mach 0.1 would occur
at b≈3.4 µm and U≈148 m/s. This is only a marker of growing compressibility,
not a universal failure threshold; the original target pressure/temperature
and single-phase assumptions would need rechecking well before extrapolating
there. The atmospheric Gaussian cavitation screen occurs at Mach≈0.005,
roughly twenty times smaller. This supports cavitation preceding large Mach
number in that particular unpressurized example.

A whole-tank sound-crossing time is not by itself a proof that a preprogrammed
flow must fail at that instant: a prepared local structure need not receive
fresh instructions across the tank on every local timescale. Perfect feedback
cannot send a newly chosen disturbance faster than sound, but the deeper
question is whether the prescribed local fields satisfy the compressible
mass, momentum and energy equations.

### My forecast with the hardware obstacle removed

| Range or condition | Speculative physical outcome |
|---|---|
| First 10→3 mm and 10→1 mm stages at the illustrative speeds | Real-water corrections appear, but compressibility and intrinsic shear heating seem small enough for a close finite analogue. I am more optimistic here than in the practical hardware forecast. |
| Around 0.1 mm width in the same extrapolation | Water physics does not clearly forbid it. Local pressure minima and fine-scale dissipation need attention; the earlier practical doubt was largely about delivery and measurement. |
| Stronger concentration near atmospheric background pressure | Cavitation is my leading candidate for a dramatic change; heating/property drift may alter the solution earlier depending on time and gradients. |
| Higher pressure suppresses cavitation, but heat is not removed | Temperature-dependent viscosity, thermal expansion, pressure drift and possibly phase changes increasingly invalidate the constant-property model. |
| Pressure and cooling also keep the liquid single phase | Compressible/acoustic dynamics and eventually failure of continuum material assumptions remain. This does not establish that compressible equations must stay mathematically regular. |

I would expect **a transition to different physics, not a realization of an
infinite fluid velocity**. I cannot infer whether the core widens, becomes a
vapor cavity, emits strong pressure pulses or continues concentrating under a
different law without its pressure, gradient and thermal histories. A finite
analogue can still succeed before that transition. Perfect instruments extend
the accessible range; they do not make constant-density, constant-viscosity
water an exact description at every scale.
