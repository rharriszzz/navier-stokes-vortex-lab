# Physical Realizability Plan for `navier-stokes-vortex-lab`

R191 completed the [measurable similarity contract and first-test design](docs/realizability/ESSENTIAL_SIMILARITY_CONTRACT_R191.md).
The next step quantifies an operating point and detectability for the fixed-core
phase test; follow the single [handoff task](SESSION_HANDOFF.md#next-task).
No test has run and no feasible contraction range is established.

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

This document defines the guiding principle for the project:

> **Model and test only what could plausibly be built and measured in a laboratory.**

The mathematical forced Navier–Stokes construction is the inspiration, but the project should not rely on idealized mechanisms that have no credible physical implementation.

In particular, the project should avoid treating an arbitrary volumetric body-force field as experimentally available. A numerical calculation may use such a force as a **reference target**, but the actual realizable model should use:

- boundary motion,
- jets or pumping,
- rotating or tangential boundary elements,
- finite-bandwidth actuators,
- finite-resolution sensors,
- finite camera frame rates,
- realistic water viscosity,
- realistic tank dimensions,
- realistic control latency.

The central engineering question is therefore:

> **Can a finite set of physically plausible boundary actuators make the interior flow behave sufficiently like the desired contracting, stretching, swirling target flow over a useful finite range of scales?**

This is a control and reachability problem before it is a hardware-construction problem.

---

# 1. What is already known computationally

The closest existing CFD project I have found is:

- `CokieMiner/nsblowup`
- https://github.com/CokieMiner/nsblowup

That project performs 3D incompressible pseudo-spectral DNS of a finite-scale collapsing-core surrogate inspired by the 2026 forced Navier–Stokes construction.

Its important feature is that the flow is driven by a **manufactured volumetric force** of the form

```math
\mathbf f =
\mathcal P
\left[
\partial_t \mathbf u^*
+
(\mathbf u^*\cdot\nabla)\mathbf u^*
-
\nu \Delta \mathbf u^*
\right].
```

The prescribed field `u*` is therefore exactly sustained by the numerical forcing.

This is extremely useful as a **reference trajectory**, but it is not directly realizable experimentally because the laboratory cannot apply an arbitrary force independently at every point in the water.

The same project also reports that when its force is removed, the collapsing core rapidly disperses. This reinforces an important point:

> The finite-scale structure should be regarded as an actively maintained driven flow, not as a naturally self-sustaining vortex.

That makes the actuator/control problem central.

A second relevant project is Ramani Duraiswami's 2026 study of self-similar swirl between contracting porous walls:

- https://arxiv.org/abs/2609.17642

This is useful because it studies a geometry with porous walls, radial flow, swirl, and controlled boundary motion. That is much closer to an experiment than a free volumetric body force.

There is also mathematical literature proving local exact boundary controllability for sufficiently regular 3D Navier–Stokes trajectories using control on an open subset of the boundary. One relevant paper is:

- *Local exact boundary controllability of 3D Navier–Stokes equations*
- Nonlinear Analysis, 2014
- https://www.sciencedirect.com/science/article/abs/pii/S0362546X1300309X

This is encouraging because it shows that boundary control is not inherently incapable of steering interior Navier–Stokes states.

However, that theorem does **not** imply that:

- a small finite number of actuators is enough,
- the required actuator amplitudes are practical,
- the required bandwidth is practical,
- the trajectory remains controllable as the core shrinks,
- the required wall motion is mechanically realizable.

Those are exactly the questions this project should answer.

---

# 2. Experimental philosophy

The project should progress through increasingly realistic levels.

Do not jump directly from an ideal target field to a hardware design.

Use the following hierarchy:

```text
ideal target field
        ↓
ideal continuous boundary control
        ↓
finite-dimensional boundary modes
        ↓
finite actuator array
        ↓
real actuator dynamics
        ↓
finite sensors + noise
        ↓
closed-loop CFD
        ↓
bench experiment
        ↓
full apparatus
```

At each stage, ask whether the desired behavior survives the newly introduced physical constraint.

If it fails at one stage, improve the design there rather than compensating with an unrealizable assumption later.

---

# 3. The primary physical target

The first target should **not** be the mathematical singular limit.

The first target should be a finite interval over which the flow shows:

- radial contraction,
- axial stretching,
- increasing swirl/shear,
- controlled azimuthal perturbations,
- measurable Reynolds-stress effects.

A useful approximate scaling target is

```math
r_c \propto \tau^{1/2}
```

over a finite interval.

A first laboratory goal might be a core-radius change such as:

```text
10 mm → 3 mm
```

and later:

```text
10 mm → 1 mm
```

if the first stage is successful.

A factor of 3 in radius corresponds to almost one decade in the similarity-time variable if the square-root scaling holds.

A factor of 10 in radius corresponds to about two decades in similarity time.

That is already experimentally ambitious and scientifically useful.

---

# 4. What the actuators must actually accomplish

The actuators do not need to reproduce the full mathematical forcing point by point.

They need to reproduce the **interior observables that matter**.

A practical target state might be

```math
x(t) =
\left[
r_c,
U_\theta,
U_z,
a_1,
a_2,
\ldots,
a_6
\right].
```

Here:

- `r_c` = core radius,
- `U_theta` = characteristic swirl speed,
- `U_z` = characteristic axial speed,
- `a_m` = low-order azimuthal perturbation amplitudes.

The main experimental question becomes:

> Can realistic boundary actuation make these state variables follow the desired trajectories?

This reduced-order goal is much more physically meaningful than demanding pointwise agreement with every component of the ideal reference field.

---

# 5. Boundary actuation should include both normal and tangential control

Earlier concepts emphasized radial wall motion and synthetic jets.

That may be insufficient.

A physically stronger design should consider **two types of boundary actuation**.

## 5.1 Normal velocity control

Examples:

- diaphragms,
- pistons,
- synthetic jets,
- suction/blowing ports,
- small bidirectional pump loops.

These generate radial and axial strain.

Represent them approximately as

```math
u_n(\theta,z,t).
```

## 5.2 Tangential velocity control

Examples:

- tangential jet nozzles,
- rotating wall segments,
- rotating rings,
- belts or sleeves,
- angled synthetic jets.

These directly inject angular momentum.

Represent them approximately as

```math
u_\theta(\theta,z,t).
```

This is likely much more effective than attempting to create all swirl indirectly from normal pumping.

A combined actuator basis is therefore preferable.

---

# 6. First numerical question: is the target reachable from the boundary?

Before designing hardware, solve this problem numerically.

Construct a bounded tank model with **no volumetric force**.

The only forcing should come through realizable boundary conditions.

Then define a target flow from the finite-scale reference solution.

Optimize the boundary command history so that the interior flow follows that target.

A useful objective is

```math
J =
\int_0^T
\int_{\Omega_{\mathrm{target}}}
w(\mathbf x)
\left|
\mathbf u(\mathbf x,t)
-
\mathbf u^*(\mathbf x,t)
\right|^2
\,dV\,dt
+
\lambda
\int_0^T
|\mathbf a(t)|^2\,dt.
```

Here:

- `u*` is the desired reference field,
- `u` is the CFD solution with boundary forcing only,
- `a(t)` is the actuator command vector,
- `w(x)` emphasizes the central region,
- `lambda` penalizes excessive actuator effort.

The target region should be smaller than the entire tank.

For example:

```text
tank:
20 cm × 20 cm × 30 cm

controlled/observed region:
8–10 cm diameter
10–15 cm high
```

We do not care whether the entire vessel matches the target field. We care whether the central experiment region does.

---

# 7. Do not start with individual actuators

The first boundary-control CFD model should use an **ideal low-dimensional continuous boundary basis**.

For example:

```math
u_n(\theta,z,t)
=
\sum_{m=0}^{M}
\sum_{k=0}^{K}
\left[
A_{mk}(t)\cos(m\theta)
+
B_{mk}(t)\sin(m\theta)
\right]
Z_k(z).
```

A similar expansion can be used for tangential velocity.

Start with something modest, such as:

```text
m = 0 ... 6
3 or 4 axial basis functions
```

This gives tens of control degrees of freedom rather than thousands.

Question:

> Can this idealized but still physically interpretable boundary basis reproduce the desired core?

If the answer is no, a physical actuator array is unlikely to succeed.

If the answer is yes, then discretize the boundary basis into actual actuators.

---

# 8. Perform controllability analysis before expensive optimization

Before performing large nonlinear optimal-control calculations, linearize the dynamics about:

- the steady vortex,
- selected points along the target trajectory.

Then evaluate how strongly each desired state direction responds to the available boundary modes.

Useful tools include:

- controllability Gramian,
- empirical controllability Gramian,
- singular-value analysis,
- balanced truncation,
- impulse-response matrices.

This can reveal:

- which flow modes are easy to control,
- which modes require huge boundary motion,
- which actuator locations are ineffective,
- whether adding tangential actuation helps,
- whether the shrinking core becomes progressively harder to control.

This is one of the highest-value analyses in the project.

---

# 9. The key scaling problem

As the core shrinks, the required spatial and temporal scales become more demanding.

For water,

```math
T_\nu \sim \frac{L^2}{\nu}.
```

With

```math
\nu \approx 10^{-6}\ \mathrm{m^2/s},
```

roughly:

| Scale | Viscous time | Characteristic frequency |
|---|---:|---:|
| 10 mm | 100 s | 0.01 Hz |
| 3 mm | 9 s | 0.1 Hz |
| 1 mm | 1 s | 1 Hz |
| 0.3 mm | 0.09 s | 11 Hz |
| 0.1 mm | 0.01 s | 100 Hz |

This suggests that a first experiment reaching the 1 mm scale is much more plausible than one attempting 0.1 mm structure.

The CFD/controller model should therefore explicitly track:

- required actuator bandwidth,
- required wall velocity,
- required wall acceleration,
- required pressure excursion,
- required spatial mode number.

If any of these exceed realistic hardware capability, stop the collapse trajectory at that point.

That stopping point is itself an important scientific result.

---

# 10. Realistic actuator limits must be built into the optimizer

The optimizer must not be allowed to invent impossible commands.

Include constraints such as:

```text
maximum diaphragm displacement
maximum diaphragm velocity
maximum diaphragm acceleration
maximum jet velocity
maximum pump flow
maximum tangential wall speed
maximum actuator force
maximum actuator frequency
maximum power
```

Also include slew-rate limits.

For example:

```math
|a_i(t)| \le a_{\max}
```

and

```math
|\dot a_i(t)| \le s_{\max}.
```

The numerical study becomes far more useful when it answers:

> Can the target be reproduced **within plausible actuator limits?**

rather than merely:

> Does some mathematical boundary function exist?

---

# 11. Replace the continuous control with finite actuators

If the continuous boundary basis works, test finite actuator layouts.

Candidate configurations:

```text
3 rings × 8 actuators  = 24 actuators
3 rings × 12 actuators = 36 actuators
3 rings × 16 actuators = 48 actuators
4 rings × 12 actuators = 48 actuators
```

Compare:

- normal-only actuation,
- tangential-only actuation,
- combined normal + tangential actuation.

For each design record:

- target tracking error,
- maximum actuator amplitude,
- RMS actuator effort,
- required bandwidth,
- robustness to actuator failure.

This should determine actuator count scientifically rather than aesthetically.

---

# 12. Sensor observability is equally important

A controllable flow is not useful if the state cannot be measured.

The project should separately analyze **observability**.

Possible sensors:

- pressure transducers,
- actuator displacement sensors,
- actuator current,
- PIV,
- possibly flowmeters.

The desired reduced state is again something like:

```math
x = [r_c,U_\theta,U_z,a_1,\ldots,a_6].
```

Question:

> Can this state be reconstructed accurately from the proposed measurements?

Evaluate this using:

- observability Gramian,
- estimator covariance,
- simulated sensor noise,
- delayed PIV measurements,
- pressure-only estimation between PIV frames.

---

# 13. Proposed sensor architecture

A plausible physical architecture is:

## Fast sensing

Pressure transducers and actuator sensors:

```text
100 Hz – several kHz
```

These provide rapid response, phase information, and actuator diagnostics.

## Slower full-field sensing

PIV:

```text
approximately 20–100 Hz
```

depending on camera, laser, field of view, and resolution.

PIV supplies:

- core radius,
- velocity profiles,
- perturbation modes,
- Reynolds stress.

The controller should not depend on obtaining a complete PIV vector field at every actuator update.

---

# 14. Two-rate control system

A realistic controller likely has three levels.

## Level 1: actuator servo loop

Approximate rate:

```text
1–5 kHz
```

Controls actuator displacement, velocity, and force/current.

## Level 2: fast flow estimator/controller

Approximate rate:

```text
100–1000 Hz
```

Uses pressure, actuator signals, and a reduced-order model.

## Level 3: PIV correction

Approximate rate:

```text
20–100 Hz
```

Uses measured interior velocity to correct the state estimate, model drift, and target tracking.

This is more realistic than asking PIV itself to be the high-bandwidth control loop.

---

# 15. The first truly convincing numerical experiment

The first computational result that would materially justify hardware is:

> A bounded-water-tank CFD simulation, with no volumetric body force, using only constrained boundary actuators, reproduces the target central-core observables over a significant finite contraction.

For example:

```text
initial core radius: 10 mm
final core radius:   3 mm
```

while simultaneously reproducing:

- swirl growth,
- axial stretching,
- low-order perturbation modes,
- measurable Reynolds stress.

The actuator commands must stay within plausible ranges.

That would be a strong result.

The next milestone would be:

```text
10 mm → 1 mm
```

---

# 16. A separate experiment may be easier and should be done first

Even if the contracting-core trajectory proves difficult, the Reynolds-stress mechanism can be tested independently.

Produce two controlled zero-mean perturbations:

```math
u'_r = A\cos(m\theta),
```

```math
u'_\theta = B\cos(m\theta+\phi).
```

Then test whether

```math
\langle u'_r u'_\theta\rangle
=
\frac{AB}{2}\cos\phi.
```

This experiment requires much less extreme contraction, much less spatial resolution, and much simpler control.

It provides a clean demonstration of controlled quadratic momentum transfer.

This should probably be the **first real fluid experiment**.

---

# 17. Proposed computational development plan

## Phase 0 — Keep the visualization project working

Continue the existing:

```text
Python trajectories
→ POV-Ray
→ ffmpeg
```

pipeline.

Purpose:

- visualize geometry,
- communicate actuator placement,
- test camera viewpoints,
- reason about sensor access.

Do not turn POV-Ray into the CFD solver.

## Phase 1 — Obtain a reference trajectory

Use the existing finite-scale surrogate from `nsblowup` or construct a comparable divergence-free reference field.

Export:

```text
u*(x,y,z,t)
```

for a finite range of time.

Also export reduced observables:

```text
r_c(t)
U_theta(t)
U_z(t)
a_m(t)
```

The reduced observables are more important than exact pointwise matching.

## Phase 2 — Create bounded-tank CFD

Use a real incompressible Navier–Stokes solver in a closed geometry.

Requirements:

- water viscosity,
- solid boundaries,
- boundary velocity conditions,
- no artificial volume force during the boundary-control experiments.

Possible software choices should be evaluated separately.

Candidates may include:

- OpenFOAM,
- Nek5000 / NekRS,
- FEniCSx,
- spectral-element or finite-volume custom models.

Do not choose solely based on convenience. Boundary-control capability and adjoint/optimization support matter.

## Phase 3 — Continuous ideal boundary control

Implement low-order Fourier/axial boundary modes.

Determine:

- achievable tracking error,
- required boundary velocities,
- required bandwidth.

If the target cannot be followed here, stop and revise the physical concept.

## Phase 4 — Controllability and observability

Compute reduced linear models about selected states.

Analyze:

- controllability singular values,
- observability singular values,
- optimal actuator locations,
- optimal pressure-sensor locations.

Use these results to decide the physical geometry.

## Phase 5 — Finite actuator CFD

Replace continuous modes with discrete actuator footprints.

Test:

```text
24 actuators
36 actuators
48 actuators
```

and combinations of radial, axial, and tangential forcing.

## Phase 6 — Hardware dynamics

Give each actuator a realistic transfer function.

Include:

- delay,
- bandwidth,
- resonance,
- saturation,
- slew limits.

Repeat target tracking.

## Phase 7 — Sensor model

Simulate:

- finite PIV frame rate,
- velocity noise,
- pressure noise,
- latency,
- missing measurements.

Build a state estimator.

## Phase 8 — Closed-loop CFD

Operate the CFD model using the same measurements and control laws intended for the real experiment.

The controller should not have access to hidden exact CFD state variables unavailable in the laboratory.

This point is essential.

## Phase 9 — Bench experiment

Build only enough hardware to test:

- one actuator,
- one actuator ring,
- pressure response,
- PIV,
- simple Fourier modes,
- zero-mean Reynolds-stress experiment.

Validate CFD against the bench measurements.

## Phase 10 — Full vortex apparatus

Only after CFD and bench tests agree reasonably well should the full multi-ring apparatus be constructed.

---

# 18. Decision gates

Each stage should have a clear stop/go criterion.

## Gate A — continuous boundary reachability

Proceed only if physically plausible boundary modes can reproduce the important interior observables.

## Gate B — finite actuator reachability

Proceed only if a reasonable number of actuators can reproduce the continuous-control result.

## Gate C — bandwidth

Proceed only if required actuator frequencies are within available hardware capability.

## Gate D — observability

Proceed only if realistic sensors can estimate the controlled state.

## Gate E — robustness

Proceed only if reasonable parameter errors and measurement noise do not destroy control.

## Gate F — bench validation

Proceed to the full apparatus only if the small experiment agrees sufficiently with CFD.

---

# 19. What would falsify the concept

The project should actively look for reasons the apparatus may not work.

Examples:

- boundary influence decays too strongly before reaching the core,
- required high-order spatial modes are uncontrollable,
- required boundary velocity is excessive,
- required pressure is excessive,
- actuator bandwidth grows too rapidly as the core shrinks,
- PIV cannot resolve the required scale,
- pressure signals do not contain enough state information,
- closed-loop control becomes unstable,
- flow becomes turbulent in an uncontrolled way,
- wall boundary layers dominate the desired central structure.

A negative answer at any of these points is useful.

The goal is not to prove the apparatus can work.

The goal is to determine **how far a physically realizable apparatus can follow the desired dynamics**.

---

# 20. What success would mean

A successful result does not require singular behavior.

A strong experimental result would be:

1. a reproducible contracting swirling core,
2. a controlled scale reduction of at least several-fold,
3. measurable axial stretching,
4. reproducible low-order perturbations,
5. measurable perturbation Reynolds stress,
6. agreement between CFD and experiment,
7. successful closed-loop tracking using only realizable sensors and actuators.

If this works over one or two decades in the similarity-time variable, it would already be an interesting finite-scale analogue.

---

# 21. Guidance for coding agents

When extending `navier-stokes-vortex-lab`, follow these rules.

1. **Do not use arbitrary volumetric forcing as the final experimental mechanism.** It is acceptable only for defining or studying a reference trajectory.
2. **Any proposed control must map to a plausible actuator.**
3. **Any feedback signal must map to a plausible sensor.**
4. **Do not give the controller access to hidden simulation state that the experiment cannot measure.**
5. **Always report actuator amplitude and bandwidth, not just tracking error.**
6. **Prefer reduced physically meaningful observables over perfect pointwise matching.**
7. **Keep ideal-control, finite-actuator, and hardware-realistic models separate.**
8. **Treat failure as informative.** If a target becomes unreachable below some core radius, record that limit.
9. **Do not describe a finite-scale analogue as a realization of mathematical blow-up.**
10. **Preserve a clean separation between visualization, CFD, control optimization, and hardware design.**

---

# 22. Immediate next tasks

The next useful work should be:

1. study the `nsblowup` reference field and identify a clean way to export its finite-scale target trajectory;
2. define the reduced state variables we care about;
3. select a bounded-tank CFD framework capable of prescribed boundary velocities;
4. implement an ideal continuous boundary basis;
5. perform an initial reachability/optimization test for a modest contraction;
6. compare normal-only versus combined normal+tangential actuation;
7. estimate required actuator speed and bandwidth;
8. only then design a specific physical actuator array.

The key question for the next computational phase is:

> **How close can a physically constrained boundary-controlled flow come to the desired central dynamics, and where does that approximation break down?**

That question should guide the project.

---

# References

- CokieMiner, `nsblowup`: https://github.com/CokieMiner/nsblowup
- Ramani Duraiswami, *Self-similar swirl between contracting porous walls*, arXiv:2609.17642: https://arxiv.org/abs/2609.17642
- *Local exact boundary controllability of 3D Navier–Stokes equations*, Nonlinear Analysis 95 (2014), pp. 175–190: https://www.sciencedirect.com/science/article/abs/pii/S0362546X1300309X
