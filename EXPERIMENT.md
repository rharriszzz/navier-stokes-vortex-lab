# Experimental Concept: Finite-Scale Forced Vortex Analogue

R196 completed [cube adapter and diagnostic source](docs/realizability/CUBE_ADAPTER_R196.md).
Twenty-four import-free checks pass; FEM construction/assembly and convergence
remain untested. Execution is unadmitted, with zero attempts. Next implement the
single-fixture driver and finite supervision path; follow the single
[handoff task](SESSION_HANDOFF.md#next-task). Stop before FEM execution.
No tank/hardware route or feasible contraction range is established.

R188 priority update (2026-09-22): establish measurable essential dynamical
similarity before further movie work. Numerical profiles and timing may differ;
percentage agreement with a paper field is not required. Interior particle measurements from
boundary/exterior cameras are explicitly allowed alongside boundary sensors
and actuation, including balanced fluid ports. See the
[hardware/optical survey](docs/realizability/BOUNDARY_HARDWARE_FEASIBILITY_R185.md)
and follow the single [current task](SESSION_HANDOFF.md#next-task).
Older stage recommendations below do not override that task or establish
hardware capabilities; diffusion times are not actuator-bandwidth specifications.

## Purpose

This document describes the physical experiment that the `navier-stokes-vortex-lab` project is intended to visualize and eventually help design.

The goal is **not** to reproduce or claim a mathematical Navier–Stokes singularity. The experiment is instead a **finite-scale laboratory analogue** inspired by a forced, contracting, stretching, swirling flow with localized oscillatory perturbations.

The project should distinguish clearly among:

1. the mathematical forced Navier–Stokes construction that motivated the work,
2. the simplified kinematic velocity field used for visualization,
3. a future laboratory apparatus,
4. any later CFD or control-system model.

The current rendering should be physically plausible enough to communicate the proposed apparatus and tracer motion, while remaining explicit about its simplifying assumptions.

---

# 1. Physical idea

The central flow is intended to have four qualitative features:

- inward radial contraction,
- axial stretching,
- strong swirl,
- small oscillatory perturbations applied in an annular region around the core.

A useful idealized mean flow in cylindrical coordinates is

```math
u_r = -a(t)r,
\qquad
u_z = 2a(t)z,
```

with an additional azimuthal velocity

```math
u_\theta = u_\theta(r,z,t).
```

The linear radial/axial part is incompressible because

```math
\frac{1}{r}\frac{\partial (r u_r)}{\partial r}
+
\frac{\partial u_z}{\partial z}
=
-2a + 2a = 0.
```

The experiment is meant to create a small, strongly sheared, swirling core whose transverse scale decreases over time while the axial structure stretches.

The perturbations are intended to have approximately zero mean but nonzero quadratic correlations, so that quantities such as

```math
\langle u'_r u'_\theta \rangle
```

can be measured.

One important experimental question is whether oscillatory perturbations can produce a repeatable Reynolds-stress contribution that materially changes the mean momentum balance.

---

# 2. Fluid

## Baseline fluid

The initial experiment should use **water**.

Representative room-temperature kinematic viscosity:

```math
\nu \approx 10^{-6}\ {\rm m^2/s}.
```

Water is preferred initially because it is inexpensive, transparent, compatible with standard PIV techniques, easy to seed with tracer particles, well characterized, and safer than many specialized fluids.

Temperature should be measured because viscosity varies with temperature. A practical target is to keep temperature variations small enough that viscosity drift is not a dominant uncertainty.

## Possible later fluids

Later experiments might use water-glycerol mixtures for higher viscosity, density-matched fluids for special particles, or index-matched fluids if optical distortion becomes important. Those should not be introduced until the basic apparatus and control system work in water.

---

# 3. Approximate size and vessel

A reasonable first apparatus is a transparent closed tank on the order of:

- 20 cm × 20 cm cross section,
- 30 cm tall,
- approximately 10–12 liters total volume.

Inside it, define a central controlled region approximately:

- 8–10 cm diameter,
- 10–15 cm high.

The exact dimensions are not fixed yet.

The tank should be transparent from multiple directions so that both top and side imaging are possible.

The apparatus should contain a fixed amount of water. Any boundary actuation that produces radial or axial flow must therefore satisfy zero net volume flux over the full boundary:

```math
\int_{\partial\Omega} u_n\,dS = 0.
```

That means actuators should preferably operate in paired or balanced modes rather than adding net fluid to the vessel.

---

# 4. Mean flow structure

The experiment should create a swirling core centered approximately on the vertical axis.

The desired qualitative motion is:

1. water moves inward toward the axis,
2. axial velocity stretches the core vertically,
3. the fluid rotates about the vertical axis,
4. the characteristic core radius decreases with time.

A useful illustrative scaling is

```math
r_c \propto \tau^{1/2},
\qquad
\tau = t_* - t,
```

over a finite experimental interval.

The purpose is not to take $\tau$ literally to zero. Instead, the experiment should try to reproduce the scaling over perhaps two or more decades in $\tau$.

For example, a practical first target might be a core-radius change from about 10 mm to about 1 mm. A later apparatus might attempt smaller scales if the imaging and actuation systems support them.

---

# 5. Perturbation field

The perturbations should initially be simple, low-order, controlled modes rather than arbitrary turbulence.

An especially useful first mode is an azimuthal mode with $m=4$.

For example,

```math
u'_r = A\cos(m\theta),
```

```math
u'_\theta = B\cos(m\theta+\phi).
```

Their average values are zero around the circumference, but their product has mean

```math
\langle u'_r u'_\theta\rangle
=
\frac{AB}{2}\cos\phi.
```

This provides a clean laboratory demonstration that a zero-mean perturbation can produce a nonzero quadratic momentum-transfer term.

A useful boundary representation is

```math
u_n(\theta,t)
=
A_0(t)
+
\sum_{m=1}^{6}
\left[
A_m(t)\cos(m\theta)
+
B_m(t)\sin(m\theta)
\right].
```

The first apparatus can concentrate on modes $m=1$ through $m=6$, with particular emphasis on $m=4$.

---

# 6. Actuators

Pressure sensors do not create the flow. Separate mechanical actuators are required.

Possible actuator types include flexible diaphragms, small pistons, voice-coil driven membranes, synthetic jets, or small recirculating ports with controlled pumps.

The preferred early concept is a set of actuators distributed in rings around the controlled region. A starting geometry might use:

- 3 vertical actuator rings,
- 12–16 actuators per ring.

The rings might be located approximately at the lower region, midplane, and upper region.

The actuators should be capable of both positive and negative displacement relative to their mean position so that they can transfer momentum without adding net water to the vessel.

The animation currently uses red markers and arrows to represent these actuators.

---

# 7. Actuation bandwidth

The system contains motions over a wide range of time scales.

For water, the viscous diffusion time associated with a length scale $L$ is approximately

```math
T_\nu \sim \frac{L^2}{\nu}.
```

Using $\nu \approx 10^{-6}\ {\rm m^2/s}$:

| Length scale | Approximate viscous time | Approximate frequency |
|---|---:|---:|
| 10 mm | 100 s | 0.01 Hz |
| 3 mm | 9 s | 0.1 Hz |
| 1 mm | 1 s | 1 Hz |
| 0.3 mm | 0.09 s | 11 Hz |
| 0.1 mm | 0.01 s | 100 Hz |

A practical first actuator design might therefore target:

- mean-flow control: DC to about 2 Hz,
- perturbation control: roughly 0.5–30 Hz,
- later extension toward 50–100 Hz if needed.

The exact frequency range should be based on measured flow response, not just actuator specifications.

---

# 8. Tracer particles

The small particles shown in the rendering represent **PIV tracer particles**, not physical beads of macroscopic size.

A reasonable first choice is fluorescent tracer particles approximately 10–20 µm in diameter.

The particles should closely follow the water velocity, have sufficiently small settling velocity, scatter or fluoresce strongly enough for imaging, be compatible with the chosen illumination wavelength, and not aggregate significantly during an experimental run.

Fluorescent particles are attractive because optical filters can suppress reflections from the tank walls and actuators.

In the POV-Ray visualization, particle diameter may be exaggerated dramatically so that their motion is visible. That visual exaggeration should be understood as rendering convenience, not physical scale.

---

# 9. Particle motion in the simulation

In the current computational model, tracer particles satisfy

```math
\frac{d\mathbf{x}}{dt}
=
\mathbf{u}(\mathbf{x},t).
```

Their trajectories are integrated numerically using classical fourth-order Runge-Kutta (RK4).

The tracer particles are passive: they respond to the specified velocity field, do not affect the velocity field, ignore collisions, ignore particle inertia, ignore Brownian motion, and ignore settling.

Those assumptions are appropriate for the first visualization.

The Python code should remain responsible for computing trajectories. POV-Ray should render the precomputed particle positions rather than perform the numerical integration.

---

# 10. PIV imaging

Particle Image Velocimetry should be the primary interior velocity measurement.

The initial visualization shows a green vertical plane representing a PIV laser sheet.

A practical development path is:

- first stage: one illuminated plane and one camera for a two-dimensional velocity field,
- second stage: a second view or stereo PIV for three velocity components within the illuminated plane,
- later stage: scanning PIV or tomographic PIV if true volumetric measurements are needed.

Useful camera views include a side view and a top view.

The field of view should include both the core and enough surrounding fluid to characterize the annular perturbations.

The optical system must have enough spatial and temporal resolution to follow the smallest intended experimental scales.

---

# 11. Pressure sensors

Pressure transducers should be distributed around the controlled region.

A starting system might use approximately 12–24 pressure sensors.

The visualization currently represents them as blue markers.

Their purposes include measuring pressure fluctuations, estimating the response to actuator commands, providing high-bandwidth feedback, and comparing pressure-mode structure with velocity-mode structure.

Pressure sensing can operate much faster than PIV and is therefore useful in the inner control loop.

---

# 12. Other instrumentation

Useful additional measurements include:

- water temperature,
- actuator displacement,
- actuator velocity,
- motor or voice-coil current,
- pressure at multiple positions,
- any recirculating flow rate,
- synchronization timing,
- camera trigger timing,
- laser trigger timing.

If pumps or synthetic jets are used, add flowmeters and differential pressure measurements where useful.

All channels should share a common time reference.

---

# 13. Control architecture

The control system should probably use two time scales.

## Fast inner loop

Approximate update rate:

```math
1\text{–}5\ {\rm kHz}.
```

Inputs may include pressure sensors, actuator position, actuator velocity, and motor current. Outputs are actuator drive signals.

The fast loop stabilizes the hardware and executes requested boundary modes.

## Slower outer flow loop

Approximate update rate:

```math
20\text{–}100\ {\rm Hz},
```

depending on the PIV system.

The outer loop estimates quantities such as core radius $r_c$, characteristic swirl velocity $U_\theta$, axial velocity $U_z$, circumferential mode amplitudes $a_m$, and Reynolds-stress quantities.

It then adjusts the desired actuator-mode amplitudes.

---

# 14. Useful state representation

Rather than attempting full real-time control of the entire velocity field, use a reduced state such as

```math
x_{\rm state}
=
\left(
r_c,
U_\theta,
U_z,
a_1,
a_2,
\ldots,
a_6
\right).
```

This state can be estimated from PIV and pressure measurements.

The controller can then command corresponding low-order actuator modes.

This makes the initial control problem tractable and experimentally interpretable.

---

# 15. Important experimental measurements

Important measurements include:

- core radius $r_c(t)$,
- swirl profile $u_\theta(r,z,t)$,
- axial velocity $u_z(r,z,t)$,
- circumferential Fourier amplitudes $a_m(t)$,
- Reynolds stress $\langle u'_r u'_\theta\rangle$.

A useful finite-range test is whether

```math
r_c \propto \tau^{1/2}
```

and whether the velocity profiles show approximate collapse under appropriate rescaling.

The mean-flow momentum balance should be evaluated both without and with the measured perturbation-stress contribution. A successful perturbation experiment should reduce the unexplained residual when the measured Reynolds stress is included.

---

# 16. Suggested first experiments

## Experiment A: static optical test

Fill the tank with water, seed it with tracer particles, illuminate a plane, confirm that particles are clearly visible, and measure optical distortion and reflections.

## Experiment B: one actuator

Drive one actuator sinusoidally, measure pressure and PIV response, and determine amplitude and phase versus frequency.

## Experiment C: actuator ring

Operate one circumferential ring, generate simple modes $m=1,2,3,4$, and verify their spatial mode shapes.

## Experiment D: zero-mean Reynolds-stress test

Create approximately

```math
u'_r=A\cos(m\theta),
\qquad
u'_\theta=B\cos(m\theta+\phi).
```

Measure whether

```math
\langle u'_r u'_\theta\rangle
```

follows the expected dependence on $\phi$.

This is an important standalone experiment even before trying to create a contracting vortex core.

## Experiment E: steady vortex

Produce a stable axisymmetric swirling flow and measure core size, swirl profile, axial profile, and pressure field.

## Experiment F: controlled contraction

Slowly vary the actuator commands to reduce the core radius and test whether the system can track a prescribed target $r_c(t)$.

## Experiment G: contraction plus perturbation

Add the controlled oscillatory perturbation while the core contracts and measure perturbation amplification, damping, Reynolds stress, and changes to the mean flow.

---

# 17. Initial experimental success criteria

A useful first-generation apparatus does not need to approach a singularity.

Success would include several of the following:

1. reproducible creation of a central swirling core,
2. controlled reduction of its radius,
3. measurable axial stretching,
4. profile collapse after appropriate rescaling,
5. at least about two decades in the chosen similarity-time variable if practical,
6. controlled low-order perturbation modes,
7. repeatable zero-mean perturbations with measurable nonzero quadratic stress,
8. evidence of shear amplification followed by viscous damping,
9. improved momentum-balance closure when measured perturbation stresses are included,
10. reproducibility across multiple runs.

---

# 18. Visualization requirements

The POV-Ray scene should communicate the experiment rather than merely look attractive.

The rendering should include:

- transparent tank,
- central controlled region,
- tracer particles,
- shrinking/stretching vortex core,
- actuator rings,
- actuator arrows,
- pressure sensors,
- PIV light sheet.

Suggested colors:

- tracer particles: cyan or light blue,
- vortex core: orange,
- actuators: red,
- pressure sensors: blue,
- PIV plane: green.

The particle motion should be visibly three-dimensional.

The camera should initially remain fixed so that actual tracer motion is easy to distinguish from camera motion.

The first useful animation should prioritize:

1. obvious particle motion,
2. clear apparatus geometry,
3. stable camera,
4. correct frame-to-frame evolution,
5. only then photorealism.

---

# 19. Relationship between the visualization and the eventual apparatus

The POV-Ray model should not be treated as a detailed CAD design.

It is intended to help answer questions such as:

- Where should actuators be placed?
- How many circumferential modes can a given ring represent?
- What regions require optical access?
- Where should pressure sensors go?
- Will the PIV plane intersect important hardware?
- Can the tracer motion be visually understood?
- Does the proposed apparatus geometry make sense in three dimensions?

Later, a true mechanical design should be developed separately in CAD.

---

# 20. Important limitations

The initial simulation does **not** currently include:

- a Navier–Stokes PDE solver,
- exact no-slip boundary conditions,
- exact pressure solution,
- exact incompressibility everywhere,
- free-surface effects,
- actuator fluid-structure interaction,
- tracer inertia,
- finite-size tracer effects,
- heat transfer,
- structural vibration,
- real camera optics.

The current tapered velocity field may have nonzero divergence near the artificial boundaries.

A high-value future improvement is therefore to construct the entire kinematic velocity field from an axisymmetric Stokes streamfunction for the radial/axial flow plus divergence-free perturbations generated from a vector potential.

That would enforce

```math
\nabla\cdot\mathbf{u}=0
```

analytically.

---

# 21. Longer-term possibilities

If the basic apparatus works, later experiments could investigate controlled transport and mixing rather than focusing only on the original vortex motivation.

Possible applications include localized micromixing, droplet breakup, precipitation and crystallization, particle suspension, controlled material-history experiments, colloidal transport, and convection-suppressed crystal-growth studies.

In microgravity, the same apparatus would be interesting because buoyancy and sedimentation would be strongly reduced.

However, an Earth-based control system can only cancel some buoyancy-driven **fluid motion**. It cannot reproduce true microgravity forces on suspended particles.

---

# 22. Guidance for the coding agent

When implementing or revising the visualization:

- treat this document as the physical intent,
- treat `AGENTS.md` as the coding/architecture rules,
- keep physics computation separate from rendering,
- do not silently claim greater physical fidelity than the code provides,
- prefer small test renders before full movies,
- preserve deterministic tracer initialization,
- keep all generated data and render frames out of Git,
- document meaningful changes to the physical model.

If the code and this document disagree about an important physical assumption, flag the discrepancy rather than silently choosing one.
