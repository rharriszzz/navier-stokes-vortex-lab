# Water experiment: feasibility, physical limits and cost

September 22, 2026. A feasibility and cost assessment of a boundary-driven
water analogue of a contracting, stretching and swirling flow.

**My recommendation is to start with a small atmospheric-pressure experiment,
then pursue roughly 10 mm to 3 mm core contraction if the first measurements
justify it.** I am cautiously optimistic about that finite analogue. Reaching
1 mm is a more expensive and uncertain research goal. Reaching 0.1 mm is doubtful
with the present practical apparatus concept, although water's properties alone
do not clearly rule out that scale at the illustrative speeds.

The likely first obstacles are creating the right motion from the boundaries
and measuring it accurately. Extra pressure postpones cavitation but does little
to solve those problems. A modest contraction apparatus might cost **$12k–35k
from scratch**, or **$5k–18k in additional equipment in a suitable laboratory**,
excluding research labor. Proving the proposed perturbation mechanism requires
more instrumentation and a separate uncertainty budget.

These are scientific judgments and budget estimates. We have not demonstrated
a boundary-driven contraction or established its attainable range. No apparatus
purchase or implementation has begun as part of this review.

## The finite result worth pursuing

The mathematical inspiration uses incompressible Navier–Stokes with fixed
positive viscosity and a prescribed smooth force in the fluid volume. It does
not supply a boundary-actuated water tank or a coupled temperature/acoustic
model. See [the paper, Theorem 1.1 and equation (1.1)](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=1).

Our attainable goal is a **finite analogue** with measurable contraction,
spin-up, coupled inward/axial motion and competition with viscosity. A stronger
result would show that imposed oscillations transfer momentum in a way that
helps sustain or contract the core. A shrinking bead ring or an attractive
vortex movie establishes neither the complete flow nor that mechanism.

“One or two orders of magnitude” needs a named quantity. If the core radius
follows the illustrative relation r∝sqrt(tau), where tau is remaining similarity
time, the interpretation is:

| Intended range | Radius change starting at 10 mm | Present judgment with real hardware |
|---|---:|---|
| One decade in similarity time | About 10→3.16 mm | Cautiously optimistic about a useful analogue. |
| Two decades in similarity time; one decade in radius | 10→1 mm | Ambitious and uncertain. |
| Two decades in radius; four decades in similarity time | 10→0.1 mm | Doubtful for the current apparatus concept. |

A decade means a factor of ten. The square-root law is conditional, not an
established experimental exponent. Report measured radius ratios and elapsed
seconds unless the scaling is supported. More generally, if r∝tau^p,
D_tau=log10(r_initial/r_final)/p. Choosing a convenient terminal time cannot
manufacture evidence for extra decades.

Throughout the practical comparisons, **core radius means the radius of the
measured swirl-speed peak**. Some analytical examples use Gaussian vorticity
width b; for that profile, the peak radius is 1.1209 b. Those examples label the
width explicitly. The [existing experimental criteria](ESSENTIAL_SIMILARITY_CONTRACT_R191.md)
distinguish contraction, complete momentum accounting, fixed-core perturbation
transfer and perturbation-assisted contraction.

## Water as an incompressible approximation

Water is compressible, carries sound and changes properties with temperature.
Nevertheless, constant-density modeling can be very accurate when density
changes are small and sound crosses the relevant region much faster than the
flow evolves. Radial contraction of an incompressible vortex is compensated by
motion in other directions; it does not require squeezing each parcel into a
smaller volume.

Useful rounded properties near 20 °C and atmospheric pressure are:

| Property | Approximate value |
|---|---:|
| Density | 998 kg/m³ |
| Dynamic viscosity | 1.00 mPa s |
| Kinematic viscosity | 1.0e-6 m²/s |
| Sound speed | 1482 m/s |
| Heat capacity | 4180 J/(kg K) |
| Thermal conductivity | 0.60 W/(m K) |

Viscosity falls to about 0.890 mPa s at 25 °C, roughly 11% below its 20 °C value.
These are reference properties, not calibration of our seeded water.
[IAPWS liquid-water correlations](https://iapws.org/technical-guidance/release/LiquidWater.download).

Water's acoustic bulk modulus rho c² is about 2.19 GPa. A 10 kPa pressure change
corresponds to a fractional density change of roughly 4.6e-6. Sound crosses
0.20 m in about 0.135 ms. At speeds of 0.05 and 0.5 m/s, Mach number U/c is
only about 0.000034 and 0.00034. These estimates support a close incompressible
approximation for the initial low-speed experiment, subject to its actual
pressure and temperature histories.

Viscosity already removes mechanical energy in the mathematical model. The
omitted effect is that dissipation becomes heat, which can then change viscosity,
density and the subsequent flow. Small thermal changes may matter to precise
momentum measurements long before the water becomes noticeably warm.

## Practical limits of boundary control and measurement

The larger change from the mathematical construction is **replacing an arbitrary
interior force with boundary actuation**. Distributed forces do exist—gravity
is an example—but we cannot independently prescribe any desired force vector
at every point in the water. Ports inject momentum at the boundary; the flow
must transport it inward. Uniform gravity can be incorporated into hydrostatic
pressure for homogeneous water, while thermal buoyancy generally cannot.

Pressure communicates quickly, but that does not mean a wall can instantly
create arbitrary interior swirl and shear. A strong pressure response at a
sensor does not prove that the core received the intended velocity perturbation.

| Likely limit | When it could matter | Why it matters |
|---|---|---|
| Boundary delivery and coherent flow | From the first experiment; increasingly toward 1 mm | Jets may bypass the core; returns, phase dispersion and instability may prevent the intended central motion. |
| Actuator stroke, flow and loaded response | From initial hardware selection | Motor update rate is not usable flow-control bandwidth. Plumbing and water load alter gain and phase. |
| Optical resolution, tracer bias and momentum accounting | Immediately for the mechanism claim; increasingly at smaller cores | Seeing motion is easier than resolving gradients, correlations and small differences between large fluxes. |
| Pressure information and drift | Immediately for pressure-based feedback | A core change may have a weak or ambiguous wall-pressure signature despite fast sensors. |
| Temperature gradients and viscosity drift | Long comparisons and sensitive balances | Drift changes the physical balance; uneven heating also introduces buoyancy. |
| Bubbles, suction and hydraulic transients | At any size with unsuitable plumbing; more likely with stronger suction | Bubbles change the flow and obscure optical measurements. |
| Large bulk compression or intrinsic sound absorption | Unlikely to set the first millimetre-scale limit at the example speeds | Acoustic noise may interfere much earlier than appreciable compressibility or acoustic energy loss. |

### Delivering motion from the wall

The [current conditional design](FIXED_CORE_OPERATING_POINT_R192.md) uses a
cylinder of radius 100 mm and height 200 mm, about 6.28 L. The diagnostic
cylinder of radius and half-height 25 mm is an imaginary observation surface,
not an interior actuator wall. The initial proposal is a fixed-core test and
claims no contraction yet.

In a quiescent comparison, a tangential wall oscillation at 0.1 Hz has viscous
penetration length sqrt(nu/(pi f))≈1.78 mm. Across 75 mm, its amplitude falls
by a factor of about 5.5e-19. This strongly disfavors relying on diffusion alone.
It is **not a bound on a circulating tank**: inward transport can help, but its
paths, entrainment and phase must work. The [transport review](INWARD_TRANSPORT_SCREEN_R193.md)
explains why a pump's total flow does not establish delivery to the core.

A sinusoidal wall speed of 20 mm/s at 0.1 Hz requires 31.8 mm displacement
amplitude. Small-stroke diaphragms are not automatically suitable. Recirculating
ports avoid finite stroke limits but introduce jets, losses and coupling between
commands. Uniform radial pressure on a circular wall also supplies no axial
torque: swirl needs tangential traction, angular-momentum flux or redistribution
of previously prepared swirl.

In the illustrative Gaussian core, opposing diffusion requires strain at least
2 nu/b². For b² declining linearly from a 10 mm width over 100 s, the following
final demands result:

| Final Gaussian width b | Final strain | Throughput across the fixed 25 mm-radius, 50 mm-high central cylinder |
|---:|---:|---:|
| 3 mm | 0.273 s^-1 | 3.21 L/min |
| 1 mm | 2.495 s^-1 | 29.4 L/min |
| 0.3 mm | 27.8 s^-1 | 327 L/min |
| 0.1 mm | 250 s^-1 | 2945 L/min |

These are **internal comparison-flow numbers, not pump specifications or global
lower bounds**. They assume strain over a fixed observation region; concentrating
it in a smaller region changes the flow requirement. They show why slower
operation helps only partly: it cannot remove the viscous strain needed to
hold a given width. Smaller scales may also develop wandering or multiple cores.
There is no universal instability threshold determined by radius alone.

### Measuring the result

At a characteristic speed of 0.05 m/s, rho U²/2 is only about 1.25 Pa. A 0.1 mm
height mismatch between pressure connections corresponds to about 0.98 Pa of
hydrostatic pressure. Calibration, drift and plumbing noise therefore matter.
A shrinking fixed-circulation core can have little effect on distant wall
pressure, so faster sampling alone may not reveal its state. Piezoelectric
sensors are normally AC coupled; a long, slow comparison needs a verified
low-frequency response. [Pressure-sensor principles](https://www.pcb.com/resources/technical-information/introduction-to-pressure-sensors).

At 2048 pixels across 60 mm, a 1 mm-radius core spans 68 pixels in diameter;
a 0.1 mm-radius core spans only 6.8. Pixels are not independent velocity samples.
The proposed requirement of ten independent spatial resolution lengths across
a core diameter means effective support no larger than 0.2 mm at 1 mm radius,
and 0.02 mm at 0.1 mm radius. Magnification helps locally, but surrounding-flow
measurements are still needed for momentum accounting.

The physical tracers are approximately 10–20 µm particles, not the large rendered
beads. Their lag may be small in slow flows, yet settling and centrifugal slip
can bias small signals. In R192's example, a 20 µm particle of assumed density
1030 kg/m³ settles at 6.54 µm/s, already larger than one illustrative mean-contrast
bias allocation. More images do not remove an unknown systematic bias.

The fixed-core mechanism test illustrates the difficulty: its ideal stress-transfer
contrast is only **0.3927 µN m**, with separate residual and external-torque-confound
allowances of **0.1309 µN m** each. Its proposed covariance-contrast error allocation
is **1.528e-7 m²/s²**. None has been demonstrated. Three-dimensional particle
tracking offers a possible measurement route, not a guarantee of that precision.
[R192 error budget](FIXED_CORE_OPERATING_POINT_R192.md#detectability-and-error-allocation),
[Dantec volumetric tracking](https://www.dantecdynamics.com/solutions/fluid-mechanics/volumetric-velocimetry-tomographic-piv-and-tomographic-ptv/tomographic-ptv/).

## Heat and sound during the initial experiment

Dissipation per unit mass in incompressible Newtonian flow is 2 nu S:S, where
S is the symmetric velocity-gradient tensor. Strong vorticity alone is not a
heating rate: rigid-body rotation has no viscous shear dissipation.

For a well-mixed 6.28 kg water inventory with no heat removal, use
DeltaT=P_water t/(m c_p):

| Net heat retained in water | Rise in 100 s | Rise in one hour |
|---:|---:|---:|
| 0.667 W | 0.0025 °C | 0.091 °C |
| 10 W | 0.038 °C | 1.37 °C |
| 100 W | 0.38 °C | 13.7 °C |

The 0.667 W case comes from 4 L/min against an assumed 10 kPa loop loss. Actual
losses, motor heat, illumination, cooling and external-loop thermal mass change
the result. Hydraulic power later dissipated into heat must not be counted again
as a separate viscous energy source.

Near room temperature, viscosity changes roughly 2–3% per degree. Even 0.1 °C
of drift can affect a sensitive comparison. Spatial gradients also matter:
a buoyancy velocity scale sqrt(g beta DeltaT L), with beta≈2.1e-4 K^-1,
DeltaT=0.1 K and L=50 mm, is about 3.2 mm/s, comparable to the proposed 2 mm/s
perturbations. This is a scale comparison, not a convection prediction in the
forced tank. It explains why one bulk thermometer is insufficient.

Intrinsic acoustic absorption is unlikely to consume the useful low-speed
vortical motion first. It concerns compression waves and increases strongly
with frequency. [NPL absorption discussion](https://resource.npl.co.uk/acoustics/techguides/seaabsorption/physics.html).
Sound may nevertheless matter early through pump noise, resonance and water
hammer. An ideal rigid 0.20 m half-wave cavity has a frequency near 3.7 kHz;
flexible walls, hoses and gas pockets can resonate much lower. An abrupt 0.1 m/s
flow stop gives an ideal water-hammer pressure scale near 0.148 MPa if wave speed
equals water's sound speed; pipe compliance and closure time govern the actual
pulse. [Caltech water-hammer discussion](https://shepherd.caltech.edu/EDL/publications/reprints/WaterHammerIgnitionEDL2019-001.pdf).

## Physical limits even with perfect instruments

**Removing hardware and measurement limits makes me more optimistic about the
first one or two similarity-time decades.** It also removes the main practical
reason for doubting a core near 0.1 mm. The remaining question is whether the
prescribed fields are consistent with real water's conservation laws, equation
of state and phase behavior.

Here “perfect” grants accurate sensing and whatever boundary actuation can
physically deliver the finite flow. It does not grant an arbitrary interior heat
sink, infinite tensile strength or a different equation of state. If exact
reproduction under every condition is guaranteed by definition, failure has
already been excluded from the premise.

### Small departures before dramatic failure

Mass conservation and the water equation of state give the identity

```text
D rho / Dt = -rho div(u)
d rho / rho = kappa_T d p - beta d T
div(u) = beta D T / Dt - kappa_T D p / Dt
```

Here D/Dt follows a parcel, beta is thermal expansion and kappa_T is isothermal
compressibility. Exact div(u)=0 requires material pressure and temperature
changes to cancel in a particular way. The prescribed pressure history and
viscous heating generally do not guarantee that cancellation. Tiny departures
can leave the incompressible approximation excellent while preventing exact
agreement of velocity, pressure and material properties together.
[Mass conservation and thermal-flow foundations](https://web.mit.edu/fluids-modules/www/fluid_transport/4-1-2energy.pdf).

A compatible temperature equation is

```text
rho c_p D T / Dt = beta T D p / Dt + Phi + div(k_th grad T)
Phi = viscous stress : grad u
```

Compression can reversibly heat the water; viscous dissipation irreversibly
creates entropy. Temperature-dependent viscosity then changes the momentum
balance. Warmer water may permit a narrower core at the same strain rather
than simply arresting contraction. Uneven heating can introduce buoyancy and
vorticity where pressure and density gradients are not aligned. No general
argument establishes inevitable thermal runaway or inevitable arrest.

Heat removal also has a timescale. Thermal diffusivity near room temperature
is about 1.44e-7 m²/s: conduction over 1 mm takes roughly 7 s, versus a 1 s
viscous timescale there. Advection or replacement water can remove heat faster,
but perfect flow control alone does not specify that thermal history.

For an illustrative extrapolation, take U b=0.0005 m²/s and let b² decline at
k=9.9e-7 m²/s, corresponding to 10→1 mm width over 100 s. A parcel continually
exposed to shear of order U/b, with no heat exchange or pressure heating, has
cumulative heating scale

```text
DeltaT_scale = [nu (U b)² / (c_p k)] (1/b_final² - 1/b_initial²).
```

This gives about 0.000060 K at 1 mm width, 0.0060 K at 0.1 mm, and 0.60 K at
0.01 mm. These are hypothetical shear exposures, not parcel temperatures in
the full solution. Fine oscillations can produce much larger gradients. A high
instantaneous heating rate does not guarantee large accumulated heating during
a short final stage; conversely, bounded total energy does not bound local
temperature when energy concentrates into a shrinking mass.

### Cavitation is my leading candidate for a dramatic atmospheric-pressure change

For the same Gaussian swirl, assuming quasi-steady centrifugal pressure balance,

```text
u_theta = C/r (1 - exp(-r²/b²)),   C = Gamma/(2 pi)
p_far - p_axis = rho C² ln(2)/b² = 1.702 rho U_peak².
```

At a far-field pressure of 101.325 kPa and vapor pressure about 2.34 kPa, the
model reaches vapor pressure at peak speed **7.63 m/s**, Gaussian width **65.5 µm**
and swirl-peak radius **73.4 µm**. Mach number is only about 0.005. At a 0.1 mm
width it predicts a 42.5 kPa pressure depression, leaving an atmospheric margin.
Thus water alone does not exclude that width in this particular example.

This is not a tank cutoff. Other accelerations, pressure minima, boundaries,
dissolved gas and nuclei affect inception; very clean water can temporarily
sustain tension. Bubbles may also enter through plumbing or a free surface
before vapor cavitation occurs. Once a vapor cavity or mixture develops, density,
compressibility and momentum transport change substantially. Bubble collapse
can emit pulses and create local heating. Perfect control could sustain a new
flow, but not the original homogeneous-liquid solution.
[Brennen, Cavitation and Bubble Dynamics](https://media.library.caltech.edu/CaltechBOOK:1995.001/chap1.htm).

### If pressure suppresses bubbles, thermal and acoustic limits remain

Increasing background pressure can postpone cavitation. It also changes real
water's thermodynamic state, so the arbitrary pressure offset of an incompressible
calculation becomes a physical design choice. Heating raises vapor pressure.
In a perfectly rigid, filled and sealed fixed-volume system, uniform warming
instead raises mean pressure by approximately K_T beta DeltaT—about **0.46 MPa
per kelvin** near 20 °C. A regulated external loop or compliant volume behaves
differently.

Compressible dynamics become important as U/c or L/(c T_change) cease to be small.
Use the scale of the fastest relevant feature, which may be a perturbation rather
than the visible core. Acoustic waves carry energy, reflect and dissipate into
heat; sufficiently strong compressive waves can steepen into shocks. Shocks are
possible, not inevitable for every concentrating vortex.
[Sound propagation and compressibility](https://www.feynmanlectures.caltech.edu/I_47.html).

The same U b example reaches Mach 0.1 near b=3.4 µm and U=148 m/s, well beyond
its atmospheric cavitation screen. This is a marker, not a universal failure
threshold, and its assumed properties need rechecking before that extrapolation.
A whole-tank sound-crossing time alone does not forbid a prepared local flow
from evolving faster: it may not need a new boundary instruction at every step.

My expectation is a transition to different physics rather than infinite fluid
velocity. Whether the core widens, forms a cavity, emits strong pulses or keeps
concentrating under a different law requires the actual pressure, gradient and
thermal histories. This expectation is not a proof of mathematical regularity
for compressible flow.

## The cost of a convincing finite experiment

Restoring real sensors and actuators brings the practical limit back toward
larger scales. The equipment needed to show a contracting core differs from
the equipment needed to establish why it contracts. That distinction matters
more to the initial budget than the difference between atmospheric and modestly
pressurized water.

The following amounts are rough **USD equipment budgets**, informed by public
component prices checked on September 22, 2026. The complete systems have not
been quoted. “From scratch” includes a modest computer, purchased fabrication,
calibration fixtures, necessary optical enclosure and roughly 25% equipment
contingency. It assumes a suitable room and owner/researcher integration effort.
“Equipped lab” means the appropriate imaging, illumination, synchronization,
software, common data-acquisition and temperature equipment, computer and
workshop resources are already available for that level of work.

Both columns exclude research labor, facility charges, taxes, shipping,
institutional overhead and room renovation. Existing laboratory instruments
have an economic cost even when they require no new cash purchase. The rows
are alternative total equipment budgets for each capability, not amounts to
add together as successive stages.

| Intended capability | Buy from scratch | Additional equipment in a suitable lab | Result to pursue |
|---|---:|---:|---|
| Small feasibility bench | $3k–8k | $1k–4k | A reproducible core and measured response to a few boundary inputs; no contraction range promised. |
| Modest contraction apparatus | $12k–35k | $5k–18k | Roughly 10→3 mm contraction and spin-up; about one conditional similarity-time decade. |
| Quantitative 3D mechanism study | $40k–120k | $20k–65k | Phase-dependent momentum transfer at a fixed core size, followed by contraction if justified. |
| Quantitative contraction toward 1 mm | $80k–250k | $40k–150k | Roughly two conditional similarity-time decades, with resolved central and surrounding flow. |
| Submillimetre research program | $250k–750k+ | $150k–500k+ | Exploration below 1 mm, possibly toward 0.1 mm; substantial redesign and no reliable range prediction. |

The mechanism study and the 1 mm extension are different research directions.
One seeks a small, convincingly attributed effect; the other seeks greater
concentration with adequate measurements. Neither guarantees the other.
The expensive rows are research allowances, not prices at which success can be
purchased. Configuration uncertainty is large, and custom-design surprises could
still change a budget by roughly a factor of two despite the included contingency.

The modest apparatus allowance can be understood through a simple allocation:
$1k–3k for vessel and supports, $2k–5k for recirculation and plumbing,
$2k–6k for approximately four to eight controlled flow channels and drivers,
$1k–4k for a few pressure channels and calibration, $3k–7k for one or two cameras
and their illumination/optics, and $1k–3k for computer, timing and basic temperature
equipment. The subtotal is $10k–28k; adding 25% gives $12.5k–35k, abbreviated here
as roughly $12k–35k. This assumes substantial owner integration and limited
mean-flow control, not a fully independent 64-channel array or a commercial
volumetric laser system.

Public prices help explain the jump to a larger system. Selected Bürkert Type
2875 valves list at $435 in brass and $524 in stainless steel. Sixty-four valves
alone therefore cost roughly $28k–34k, before drivers, plumbing and calibration.
[Manufacturer prices](https://www.burkert-usa.com/en/type/2875).
Kron lists the Chronos 2.1-HD from $6,800, so four camera bodies start at $27,200;
that does not buy illumination, lenses or a validated continuous measurement
system. [Camera comparison](https://www.krontech.ca/product-comparison/).
By comparison, LabJack data-acquisition devices list at $570–1,400 across the
T7, T7-Pro and T8, so basic acquisition need not dominate the small bench.
[Device listings](https://labjack.com/collections/t-series-devices).

A wet/wet pressure transmitter listed from $550.90 is a useful plumbing-price
reference, but its advertised 0.5% accuracy does not establish suitability for
a roughly 1 Pa signal. [Seller listing](https://usa.alphacontrols.com/products/629c-wet-wet-differential-pressure-transmitter).
Conversely, a published low-cost planar PIV build reported a $520.50 hardware
bill in 2024. That shows that exploratory imaging can be inexpensive; it does
not validate the much harder three-dimensional momentum measurement here.
[Authors' study](https://pmc.ncbi.nlm.nih.gov/articles/PMC11362640/).
The appropriate purchase is determined by required measurement error and flow
response, not by the most impressive camera or actuator specification.

Labor may exceed equipment cost. As a planning scenario, 200–800 hours for a
modest apparatus and its initial calibration would add $15k–120k if hired at
an assumed $75–150/hour. A quantitative mechanism or 1 mm program might require
1,000–3,000 hours, or $75k–450k at those rates. These are workload/rate assumptions,
not quotes or completion promises. They exclude fabrication and mechanical
design already purchased in the equipment package. Owner time or salaried staff
can reduce new cash spending without reducing the work required.

Shared access can be valuable even without a full collaboration. The University
of Cincinnati lists external micro-PIV equipment use at $60/hour and staff time
at $100/hour: twenty equipment hours plus ten staff hours would be $2,200.
That is an example of the billing model, not a claim that a microscope system
can accept this tank or supply its volumetric data. Suitable tank-scale access
would need its own agreement. [Facility rates](https://www.ceas.uc.edu/research/centers-labs/clean-room/equipment.html).
A further provisional allowance is $1k–5k per active year for small-apparatus
consumables, reference checks and maintenance, or $5k–20k+ for an extensive
system, before paid access, staffing, software renewals or major repairs.

## The limited return on pressurization

Atmospheric operation means near-atmospheric background pressure in the test
region, not zero pump pressure. A vented reservoir can set the background while
the viewed tank is filled; pumps still overcome losses around the loop. Keeping
a free surface away from the core can avoid one source of air entrainment.

For the Gaussian example, increasing the available pressure margin postpones
cavitation according to

```text
b_cav = 0.0005 * sqrt(1.702 rho / (p_abs - p_v))
r_cav = 1.1209 b_cav
extra contraction factor = sqrt[(p_abs - p_v)/(p_atm - p_v)]
extra similarity-time decades = log10[(p_abs - p_v)/(p_atm - p_v)].
```

The final line additionally assumes square-root similarity scaling. In the
table, radii use the swirl-peak definition throughout. Gauge pressure is added
above the atmosphere; absolute pressure includes the atmosphere.

| Added gauge pressure | Approximate absolute pressure | Illustrative cavitation radius | Potential extra contraction factor | Extra conditional similarity-time decades | Estimated pressure-system addition |
|---:|---:|---:|---:|---:|---:|
| 0 bar | 1.01 bar | 73.4 µm | 1× | 0 | $0 |
| +1 bar, about 14.5 psi | 2.01 bar | 51.8 µm | 1.42× | 0.30 | +$15k–40k |
| +4 bar, about 58 psi | 5.01 bar | 32.7 µm | 2.25× | 0.70 | +$30k–90k |
| +9 bar, about 131 psi | 10.01 bar | 23.1 µm | 3.18× | 1.00 | +$60k–180k |

These are cavitation-only comparisons at fixed circulation and profile,
not predictions of attainable radii. If delivery or imaging stops at 1 mm,
moving a theoretical cavitation threshold from 73 to 33 µm captures no extra
range. Achieving ten times smaller radius solely by postponing cavitation would
require approximately 99 bar absolute in this example. That is not a proposed
or costed design.

The pressure-system additions are particularly uncertain estimates for a
roughly 6 L apparatus with several useful optical views and many fluid connections.
They cover pressure-containing hardware, windows and seals, pressure regulation
and relief, compatible loop/sensor changes, mechanical design/testing and
contingency. They exclude new high-end imaging equipment and the flow research
labor. A small pressure cell with one tiny window can be much cheaper and would
not provide the same experiment.

These additions are approximately the same for either ownership route unless
the lab already has an appropriate pressure-rated optical vessel and loop.
Adding the +4 bar option to the 1 mm research apparatus would therefore give
roughly **$110k–340k from scratch**, or **$70k–240k additional equipment in a
suitable lab**. The pressure options are alternatives, not charges to add in
sequence. A retrofit may also discard some earlier purchases.

No public quote was found for this particular multi-window vessel. Parr's
window descriptions show how aperture, mounting and pressure rating interact,
but do not establish these dollar estimates. Preserving broad optical access
is why the price of an ordinary pressure container is a poor comparison.
[Pressure-vessel optical windows](https://www.parrinst.com/products/stirred-reactors/options-accessories/windows/).

In a balanced pressurized recirculation loop, hydraulic power primarily depends
on flow times loop pressure loss, not flow times background absolute pressure.
Containment and optical integration can be the expensive parts of pressurization.
Higher background pressure also does not amplify a small differential signal;
measuring it can become harder. Thus extra pressure should follow evidence of
a pressure-limited operating point, rather than precede the first useful flow
and measurement results.

## A practical path forward

The best initial investment is the small atmospheric feasibility bench. It
should establish that boundary inputs create a reproducible core and that
velocity and pressure measurements resolve its response. Only then is the
modest 10→3 mm contraction apparatus a justified next expense. Reusable equipment
reduces the upgrade cost; the two budget rows should not simply be added.

After that, the choice is scientific as well as financial: extend contraction
toward 1 mm, or measure the perturbation mechanism more convincingly at a larger
and steadier core. Suitable borrowed or shared optics may save more than
simplifying the tank. Larger physical scales can ease imaging, while slower
schedules or lower circulation may reduce some demands; each alternative must
retain the intended viscous and perturbation dynamics and have its flow and
cost estimates recalculated.

I would regard a well-measured atmospheric analogue covering roughly the first
similarity-time decade as a worthwhile result. Two decades remain a credible
ambition to investigate, rather than a performance commitment. A supported
negative result—showing exactly where delivery, measurement or water physics
changes the behavior—would also answer the central experimental question.
