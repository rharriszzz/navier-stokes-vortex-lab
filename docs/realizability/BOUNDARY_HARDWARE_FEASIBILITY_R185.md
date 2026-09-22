# Boundary hardware and optical feasibility — R185

Research date: 2026-09-22. Owner: PC/WSL `daisy`.
Current execution priority: [the handoff](../../SESSION_HANDOFF.md#next-task).

Commercial components exist for a credible boundary-driven water experiment.
Their existence does not establish that they can reproduce the paper's flow.
The strongest candidate for study combines balanced recirculation, independent
swirl input, and volumetric optical velocity measurements. This is a design
proposal, not a selected bill of materials or a feasibility verdict.

R185 explicitly permits tracer measurements inside the water using cameras at
or outside the boundary. These measurements may inform the experimental
estimator; exact hidden CFD state is still unavailable to a controller. The
old pressure-only benchmark remains a separate comparison case. The user
prioritizes quantified experimental fidelity before further movie work.

## Commercial components and custom assemblies

These are manufacturer offerings checked on the research date, not verified
stock, quotations, or measured performance in our plumbing. Catalog maxima
are not simultaneous operating points. Select wetted materials, ranges and
pump curves only after calculating the actual demand.

| Function | Commercial example and documented capability | What would need building or testing |
|---|---|---|
| Sustained inflow/outflow | [KNF FP 400](https://knf.com/en/uk/solutions/pumps/series/diaphragm-liquid-pump-fp-400): up to 4.6 L/min, maximum pressure 1 bar, adjustable motor; flow at pressure follows its pump curve | Recirculation manifold, distributed ports, return paths, pressure/flow readbacks and pulsation control. A check-valved pump is not a reversible signed-flow actuator. Paired supply/return branches or a suitable reversing arrangement are needed. |
| Independently regulated port pressures | [Fluigent Flow EZ](https://www.fluigent.com/research/instruments/pressure-flow-controllers/flow-ez/): up to eight independent modules; range variants down to −800 mbar or up to 7 bar; advertised response down to 30 ms | Gas pressure acts on a liquid reservoir. Small-channel precision hardware is an option for a pilot, not evidence of multi-liter/minute array capacity. Reservoir, tubing and nozzle impedance determine actual liquid response. |
| Alternative pressure/flow control | [Elveflow OB1](https://www.elveflow.com/microfluidic-products/microfluidics-flow-control-systems/ob1-pressure-controller/): four channels; positive and pressure/vacuum variants; advertised response down to 10 ms measured with a 12 mL reservoir and 0→200 mbar step | Larger reservoirs, finite supply capacity and simultaneous channels require characterization. Manufacturer indicative sensor-compatible flow range extends to 500 mL/min; no tank-loop bandwidth follows from the small-reservoir step test. |
| Local oscillatory wall motion | [H2W VCS24-029-LB-03](https://www.h2wtech.com/product/voice-coil-stages/VCS24-029-LB-03): 61 mm total travel, 12.9 N continuous / 38.7 N peak force | Couple a commercial dry motion stage to a sealed piston, bellows or diaphragm. This example establishes component availability, not suitable size or wet dynamic performance. Fluid added mass, seal friction, membrane stiffness, stroke and heating matter. |
| Swirl/angular-momentum input | Custom angled inlet/return ports supplied by commercial pumps; alternatively motor-driven end plates, sleeves or wall rings | Jet angular momentum and return extraction must be accounted for. Rotating walls introduce seals and viscous boundary layers. An angled jet is not equivalent to prescribing tangential no-slip wall velocity. |
| Wall pressure | [Validyne DP15](https://www.validyne.com/product/dp15_variable_reluctance_pressure_sensor_capable_of_range_changes/): wet–wet differential sensing, interchangeable ranges starting at ±2.22 inches water (about ±553 Pa) | A flush or short liquid-filled pressure connection, appropriate electronics, hydrostatic correction, calibration and measured noise spectrum. This catalog range does not establish the historical benchmark's 0.1 Pa noise assumption. |
| Interior 3D velocity through exterior cameras | [LaVision Shake-the-Box](https://www.lavision.de/de/download.php?id=4029&name=download.pdf) supports 2–8 camera configurations, volumetric laser/LED illumination and water tracers. [Dantec volumetric PTV](https://www.dantecdynamics.com/solutions/fluid-mechanics/volumetric-velocimetry-tomographic-piv-and-tomographic-ptv/tomographic-ptv/) offers time-resolved 3D particle tracking | Optical windows, filled-tank calibration, synchronized exposures, adequate illumination and measured reconstruction delay/error. Product availability establishes a measurement route, not closed-loop latency or resolved stresses at our smallest scale. |
| Liquid tracers | [Dantec seeding particles](https://www.dantecdynamics.com/product-category/seeding-consumables/seeding-particles/): fluorescent polymers, polyamide and hollow glass spheres | Select size, density, fluorescence and concentration together. The actual particle population must follow the flow and remain optically resolvable. |

Other buildable options are segmented porous liners with separate plenums,
paired piston chambers, and synthetic jets. Porous segments smooth discrete
jets but add hydraulic resistance and couple neighboring commands. Piston
chambers suit finite-volume pulses; they cannot supply sustained throughput
without refilling. Synthetic jets have zero cycle-mean volume delivery but
can transport momentum nonlinearly; they cannot replace a required steady
source/sink pair in a linear Stokes calculation. Piezo membranes trade small
stroke for rapid motion. Boundary ultrasound creates acoustic streaming and
would need a separate compressible/acoustic model; it is not the first route
for interpreting an incompressible boundary-controlled analogue.

## A candidate architecture to evaluate

Use a transparent water vessel with flat optical windows, a central comparison
volume, independently supplied sidewall sectors, and distributed extraction
through both endcaps. Recirculate the extracted water to the side supplies.
Allow additional independently controlled tangential ports or moving boundary
sections for swirl. Keep top/bottom commands separately adjustable: enforcing
reflection symmetry prematurely could exclude needed axial structure.

Three axial bands with sixteen sectors each are a useful *candidate* modal
layout, not a minimum or a selected 48-actuator build. Sixteen angular samples
can represent both phases through m=6 in an ideal sampled basis; eight cannot
represent both m=4 phases. Port footprints, windows, plumbing coupling and the
fluid response may still make modes ineffective. Three axial bands do not
resolve arbitrary axial structure or the paper's fine perturbations.

For a fixed incompressible test volume, total outward flow must sum to zero
at each instant. Water may freely cross individual ports while the external
loop conserves volume. The central comparison region is an imaginary surface,
not a membrane: fluid and angular momentum cross it. An internal actuator ring
would define a different experiment from actuation only at the vessel wall.

A rigid impermeable wall does not become a flow actuator merely by specifying
its pressure. Pressure control needs a compliant/moving wall or a fluid port.
Do not prescribe arbitrary velocity and pressure independently at the same
port; use a consistent pump/valve/impedance or traction boundary model.
Radial pressure on a circular cylindrical wall supplies no torque about its
axis. Swirl requires angular-momentum flux, tangential traction, or redistribution
from previously prepared surrounding water. Track the return loop as well as
the supply: zero net water flow does not mean zero net angular momentum.

Compare two custom routes: recirculating ports offer sustained flux and torque
but introduce jet structure; moving wall sections offer smoother tangential
traction but may transmit rapid changes poorly to a distant core. No route is
selected before a boundary-to-core response calculation/measurement.

## What beads and cameras can establish

Use a synchronized multi-view system, initially evaluate four camera views,
with an overall view and a separate magnified central volume as needed. Planar
PIV measures two velocity components in a sheet; stereo PIV adds the third
component in that sheet. Neither alone establishes general 3D stress transport.
Volumetric PTV or tomographic PIV is the appropriate candidate for core shape,
axial variation and radial/axial momentum fluxes.

Dantec describes 10–100 µm spheres for water PTV and laser or high-power LED
illumination on its linked PTV page. Smaller particles may be necessary as the
core shrinks. LaVision's linked brochure describes blue LED excitation for
fluorescent water tracers to suppress reflections; select the actual light and
emission filter to match the particle spectrum. Pulsed lasers are another
commercial route when photon budget and exposure duration demand them.

More beads help only up to a finite image density. Overlapping particle images,
occlusion, multiple scattering, false matches and particle loading eventually
reduce fidelity. A bright rendered bead is not an appropriate physical tracer
specification. Density matching, centrifugal slip, settling and finite size
must be evaluated, including their bias in measured correlations.

Illustrative optical arithmetic: a 100 mm field spanning 2048 pixels gives
48.8 µm/pixel. A 1 mm *radius* core spans about 41 pixels across its diameter;
a 0.1 mm radius core spans only 4.1. Subpixel particle localization does not
turn four pixels into a resolved velocity-gradient profile. Narrow the field,
add magnified views, or change scales. Pixel pitch is not PIV vector resolution;
interrogation support, track density, depth resolution and calibration also enter.

Choose exposure from motion blur, e.g. U*t_exp below the intended fraction of
a pixel, and sampling from particle displacement and the fastest target mode.
Camera frame rate is not processed-feedback update rate. Measure the entire
exposure→reconstruction→estimation→actuation delay. Initially retain raw images
for independent offline validation; a later controller receives only delayed,
noisy optical features and measured actuator/wall signals. Inferring pressure
from particle acceleration is model-dependent and is not an independent wall
pressure measurement.

Do not infer vortex-core contraction from a shrinking ring of beads alone.
Fit a declared velocity/vorticity profile and track its centre, width and
uncertainty; material trajectories and viscously evolving core width differ.

## What one to four decades would demand

R186 explicitly asks to evaluate both radius and time until their feasible
tradeoffs become clear. Neither metric is selected or required from the user.
Report both ratios and the physical elapsed duration. Under a fixed square-root
scale law the two ratios are linked; changing the contraction schedule or
geometry changes strain and hardware demand and must preserve or explicitly
relax the intended similarity.
For the illustrative relation b ∝ sqrt(tau), N decades of similarity time give
10^(N/2) radius contraction. Starting at b0 = 10 mm, the arithmetic is:

| Similarity-time decades | Radius contraction | Final radius b | b²/nu in nominal water | Gaussian strain floor 2nu/b² |
|---:|---:|---:|---:|---:|
| 1 | 3.16× | 3.16 mm | 10 s | 0.2 s⁻¹ |
| 2 | 10× | 1 mm | 1 s | 2 s⁻¹ |
| 3 | 31.6× | 0.316 mm | 0.1 s | 20 s⁻¹ |
| 4 | 100× | 0.1 mm | 0.01 s | 200 s⁻¹ |

These are our dimensional/model calculations with nu = 10⁻⁶ m²/s, not vendor
claims, a paper-witness evaluation, or an achieved physical range. For the
Gaussian width equation d(b²)/dt = 4nu − 2ab², contraction requires
`a = 2nu/b² − d(log b)/dt > 2nu/b²`. The table is only the diffusion-balancing
floor; actual contraction costs additional strain. b²/nu is a local diffusion
time, not an actuator-frequency specification or the selected tau schedule.

At that floor, maintaining the ideal strain through a fixed cylinder of radius
R and half-height H requires side inflow Q = 4*pi*a*H*R², balanced by total
endcap outflow. For R=H=25 mm, Q is approximately 2.36, 23.6, 236 and 2356 L/min
for the four rows, respectively. These are throughputs *across that hypothetical
central control surface*, not calculated pump requirements or a global lower
bound for a localized design. Confining strong strain to a smaller region
changes the demand drastically; the boundary-to-core transport problem must
then establish whether such localization is possible. The calculation shows
why extrapolating a modest pump-controlled vortex to four decades is unsafe.

If the user means one to four decades of *radius*, the final radii from 10 mm
would instead be 1 mm, 100 µm, 10 µm and 1 µm; these correspond to 2, 4, 6 and 8
decades in tau. They are fundamentally different experimental regimes.

R186 comparison axes are initial/final radius, radius ratio, similarity-time
ratio, actual duration, peak strain/flow/torque, optical resolution and error.
Longer duration can reduce the contraction-rate term in a, but cannot remove
the viscous floor at a fixed final radius. Since b² = C*tau fixes the ratio
but not C, a radius ratio alone does not fix elapsed seconds. The dimensional
mapping and target dynamics must fix the schedule. Compare attainable profiles
and momentum balances across these axes before selecting a target.

My engineering recommendation is to investigate roughly one similarity-time
decade first, then two, with three/four treated as research extensions pending
measured limits. This ranks study priorities; even one decade is unproven.
Larger geometrically similar water experiments slow viscous dynamics as L²
and increase dimensional throughput at comparable strain balance as L. Scaling
up helps optical/time resolution but changes facility demands; independently
slowing a fixed-size flow does not preserve its Navier–Stokes similarity.

## Essential dynamical similarity — R188 clarification

R188 changes the primary success criterion: seek a physically realizable
finite flow that preserves the important dynamics while allowing substantial
numerical differences. Percentage agreement with one paper field is optional,
not the definition of success or a prerequisite for investigating hardware.
The mathematical volume force is a construction device, not an available
experimental actuator; boundary driving defines a different physical problem.

The following is a proposed similarity contract for review, not a finding that
any criterion has been achieved or that every row must be a first-stage gate.

| Candidate essential property | Evidence to seek | Differences that can be allowed |
|---|---|---|
| A coherent contracting swirling core | Resolved velocity/vorticity-based core size and centre over a sustained interval; reproducible contraction and swirl/shear evolution | Initial size, contraction schedule, peak speed and profile shape |
| Coupled radial and axial dynamics | Measured inflow/axial transport and their role in concentration; distinguish material stretching from the evolving axial extent of the core | Vessel geometry, aspect ratio, return path, axial profile and asymmetry |
| Competition between concentration and viscous spreading | Quantified strain, width evolution and diffusion contribution; assess dimensionless balance and ordering of relevant time scales | Numerical coefficients and exponents, provided the claimed dynamical balance is retained |
| Perturbation-assisted momentum transport, if claimed | Spatially resolved stress flux and budget closure; compare phase/amplitude changes or perturbation-on/off cases with mean driving accounted for | Excitation waveform, frequency, detailed modes and pulse shape if the relevant transfer mechanism survives |
| Physical boundary realization | Measured inflow/outflow, torque/work, preparation and sensor/actuator limits with conservation and uncertainty accounting | Boundary inputs and exterior flow can differ from the mathematical construction |

Define essential properties before testing and document departures. Fit observed
scaling instead of imposing a paper exponent as a pass condition. Retain radius
ratio and elapsed time as direct observables; quote equivalent similarity-time
decades only when a stated relation justifies that conversion. The square-root
and Gaussian estimates above remain conditional illustrations, not mandatory
laws for every acceptable analogue. Dimensionless ratios need justified ranges
or qualitative ordering, not automatically exact equality to the paper.

A useful contracting-vortex analogue can succeed without establishing the
paper's stress mechanism. For a mechanism claim, shrinking the core through
stronger mean suction alone is insufficient evidence that perturbations caused
the relevant transfer. Phase/on-off comparisons help discriminate causes but
must be interpreted alongside the full momentum budget and changed base flow.
Quantitative measurements remain essential even when percentage matching is
not the objective: measure attained range, repeatability and uncertainty.

The [primary paper](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf)
remains the source of inspiration. The earlier review distinguishes its mean,
annular perturbations and corrections from the implemented Gaussian surrogate.
The [finite-field extraction contract](../../BOUNDARY_CONTROL_HANDOFF.md#11-what-a-finite-paper-derived-target-would-require)
remains available for a later quantitative replication claim; it is not a gate
for the broader analogue study. A complete finite paper witness need not be
implemented before defining or testing a specific analogous mechanism.

R191 completed the [measurable essential-similarity contract](ESSENTIAL_SIMILARITY_CONTRACT_R191.md),
including the criteria/hardware/evidence table, allowed differences, uncertainty,
radius-duration comparison and a proposed fixed-core phase test. Its Gaussian
central budget is a checked null explanation for contraction without perturbation
stress, not a tank solution. R192 supplies the [conditional operating-point/detectability sheet](FIXED_CORE_OPERATING_POINT_R192.md).
R194 completed the [base-flow contract](PORT_BASE_FLOW_CONTRACT_R194.md).
Neither route is admitted. Next implement only its isolated verification prototype
and verification path, following the [handoff](../../SESSION_HANDOFF.md#next-task).
B2's failed accuracy gate still prevents trusting that solver's response results;
relaxing the target does not relax numerical or experimental evidence quality.
No attainable range or mechanism success has been established.
