# Control Research Roadmap

R231's [prelaunch result](docs/realizability/POISEUILLE_PRELAUNCH_R231.md)
records a caller import-path refusal before timer, reservation or FEM. Zero
numerical attempts spent; this task stopped without retry. R230's artifact-bound
FFCx gate and one-use admission remain the historical contract. R229's setup
resource refusal (303 memory.max events, no OOM/kill) remains unchanged. Full
convergence/tank/B2 execution remains unadmitted. Next: Astra/high reviews and
tests the caller without FEM, then decides separate execution admission; follow
the single [handoff task](SESSION_HANDOFF.md#next-task).
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

## Research question

The primary physical-realizability question is:

> **Can a finite set of physically realizable external actuators, using measurements from physically realizable sensors, reproduce experimentally meaningful portions of the desired interior flow?**

This is different from asking whether an arbitrary distributed body force can reproduce the target.

A volumetrically forced numerical field may be used as a **reference trajectory**, but the realizable calculation should ultimately use boundary actuation only.

---

## 1. Define success before selecting a solver

Do not require exact pointwise agreement with the full target field.

Define a reduced target state such as:

```math
x(t)=
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

Candidate observables:

- `r_c`: vortex-core radius,
- `U_theta`: characteristic swirl velocity,
- `U_z`: characteristic axial velocity/stretching,
- `a_m`: amplitudes/phases of selected azimuthal perturbation modes,
- selected Reynolds-stress observables such as `⟨u'_r u'_theta⟩`.

The first milestone is not singular behavior. It is controlled reproduction over a modest finite interval.

A reasonable staged target is:

```text
first: 10 mm → 3 mm core radius
later: 10 mm → 1 mm
```

provided the reference scaling supports this interpretation.

---

## 2. Reference trajectory

Obtain a finite, well-resolved target trajectory.

Possible source:

- the finite-scale `CokieMiner/nsblowup` surrogate,
- or a separately constructed divergence-free target field.

Export either the full field

```text
u*(x,y,z,t)
```

or enough data to evaluate it at arbitrary sample points.

Also export reduced target observables:

```text
r_c(t)
U_theta(t)
U_z(t)
a_1(t) ... a_6(t)
Reynolds-stress diagnostics
```

### Decision gate

Do not proceed until the target interval is finite, numerically resolved, and clearly distinguished from the mathematical singular limit.

---

## 3. Bounded-domain base CFD

Create a bounded water-domain CFD model representing the proposed vessel.

Initial nominal geometry:

```text
tank:
~20 cm × 20 cm × 30 cm

central target region:
~8–10 cm diameter
~10–15 cm high
```

Initial fluid:

```text
water
nu ≈ 1e-6 m^2/s near room temperature
```

Requirements:

- incompressible Navier–Stokes,
- solid vessel,
- controlled boundary patches,
- no arbitrary interior body force during boundary-control tests.

The domain need not reproduce the entire reference field. The primary comparison region is the central target volume.

### Deliverable

A validated uncontrolled/base-flow simulation.

### Decision gate

Verify mesh/time-step convergence for the observables to be used later.

---

## 4. Boundary-mode response experiment

This should be the **first substantial control calculation**.

Do not begin with closed-loop control.

### Boundary basis

Use low-order, physically interpretable boundary functions.

For normal velocity:

```math
u_n(\theta,z,t)
=
A_{mk}(t)\cos(m\theta) Z_k(z)
```

and corresponding sine modes.

For tangential velocity:

```math
u_\theta(\theta,z,t)
=
B_{mk}(t)\cos(m\theta) Z_k(z).
```

Initial range:

```text
m = 0 ... 6
3–4 axial basis functions
```

Test normal and tangential actuation separately and together.

### Input experiments

For each boundary mode, apply:

- small impulse-like disturbances,
- steps,
- low-amplitude sinusoids over selected frequencies.

Record the central-flow response.

### Reduced response vector

For each input, estimate changes in:

```math
\delta x =
[
\delta r_c,
\delta U_\theta,
\delta U_z,
\delta a_1,
\ldots,
\delta a_6
].
```

### Deliverable

An empirical boundary-input → interior-state response dataset.

---

## 5. Reachability / controllability screening

Before nonlinear trajectory optimization, analyze the response data.

Construct a local linear approximation:

```math
\delta x \approx G\,\delta a
```

or a dynamic state-space approximation if needed.

Examine:

- singular values,
- rank,
- condition number,
- poorly controlled state directions,
- differences between normal-only and normal+tangential actuation,
- dependence on core radius/time along the target trajectory.

Questions:

1. Can the available boundary modes span the desired reduced-state directions?
2. Which state combinations are easy to influence?
3. Which are nearly uncontrollable?
4. Does control degrade rapidly as the core shrinks?
5. Which actuator types materially improve conditioning?

Weak singular values may also reflect poor normalization, insufficient numerical resolution, an inappropriate perturbation amplitude, an inappropriate time horizon, or a poor reduced-state definition. Check these before interpreting weak reachability as physical impossibility.

### Decision gate A

Proceed only if a practical subset of boundary modes has meaningful influence over the required state directions.

---

## 6. Sensor observability experiment

Analyze sensing separately from actuation.

Candidate sensors:

- wall pressure transducers,
- actuator displacement/velocity/current,
- planar PIV,
- stereo PIV later if needed.

Define a measurement vector:

```math
y =
[p_1,\ldots,p_N,\text{PIV features},\text{actuator sensors}].
```

Perturb each reduced-state direction or use CFD snapshots to estimate the corresponding measurement signatures.

Construct a local mapping such as:

```math
\delta y \approx H\,\delta x.
```

Examine:

- singular values,
- state combinations that look similar to the sensors,
- optimal pressure-sensor locations,
- value added by PIV,
- effect of realistic noise.

### Decision gate B

Proceed only if the desired reduced state is estimable with plausible sensor placement and noise.

---

## 7. Replace ideal boundary modes with finite actuators

Once low-order continuous boundary modes are promising, map them to finite actuator footprints.

Candidate layouts:

```text
3 rings × 8 actuators  = 24
3 rings × 12 actuators = 36
3 rings × 16 actuators = 48
4 rings × 12 actuators = 48
```

Compare:

- normal diaphragms/pistons,
- synthetic jets,
- tangential jets,
- rotating/moving boundary sections,
- combinations of normal and tangential devices.

Quantify how well each finite layout reproduces the useful continuous boundary modes.

### Decision gate C

Proceed only if a practical actuator count preserves adequate reachability.

---

## 8. Add hardware constraints

The optimizer/control model must not invent impossible commands.

For each actuator model include plausible limits on:

- displacement,
- velocity,
- acceleration,
- force,
- pressure,
- flow rate,
- tangential speed,
- bandwidth,
- slew rate,
- duty cycle,
- power,
- delay,
- resonance.

A result with low state error but impossible wall motion is a failed physical design.

---

## 9. Open-loop target tracking

Only after reachability and actuator discretization should full trajectory tracking begin.

A representative cost function is:

```math
J =
\int_0^T
\|W_x(x(t)-x^*(t))\|^2 dt
+
\lambda
\int_0^T
\|W_a a(t)\|^2 dt.
```

Use reduced observables first.

Compare:

- tracking error,
- actuator effort,
- peak amplitude,
- required bandwidth,
- robustness to small model perturbations.

### Decision gate D

A promising result should reproduce the important finite-scale observables with actuator commands that are plausibly buildable.

---

## 10. Sensor model and estimator

Introduce:

- pressure noise,
- PIV velocity error,
- camera frame-rate limits,
- latency,
- occasional missing PIV updates,
- actuator-sensor noise.

Build an estimator using only quantities available in the eventual experiment.

Possible approaches, after the reduced model is understood:

- Kalman filtering,
- extended/unscented filters,
- reduced-order observers,
- data-driven estimators.

Do not give the estimator exact CFD fields unavailable experimentally.

---

## 11. Closed-loop CFD

Only now implement feedback control.

A plausible architecture is:

```text
actuator servo:      ~1–5 kHz
fast pressure/model: ~100–1000 Hz
PIV correction:      ~20–100 Hz
```

Possible high-level controllers later include LQR, MPC, or gain scheduling along the target trajectory.

The first closed-loop test should be modest and robust, not maximally aggressive.

---

## 12. Bench experiment before full apparatus

The first physical build should test components and reduced physics.

Suggested sequence:

1. one actuator in water,
2. one actuator ring,
3. pressure response,
4. PIV response,
5. low-order azimuthal modes,
6. phase-controlled zero-mean perturbations,
7. measurement of `⟨u'_r u'_theta⟩`.

The Reynolds-stress experiment is valuable even if the contracting-core program later proves difficult.

Use bench data to calibrate CFD actuator and sensor models.

---

## 13. Full apparatus only after validation

Proceed to a multi-ring system only if:

- CFD predicts adequate reachability,
- finite actuator models remain adequate,
- sensors provide sufficient observability,
- hardware bandwidth is plausible,
- bench measurements reasonably agree with CFD.

---

## 14. Falsification criteria

Actively look for failure mechanisms:

- boundary influence decays before reaching the core,
- desired high-order states are effectively uncontrollable,
- required wall velocity becomes excessive,
- actuator bandwidth grows too rapidly,
- pressure sensors become uninformative,
- PIV cannot resolve the smallest required scale,
- wall boundary layers dominate,
- uncontrolled turbulence destroys the reduced-state model,
- closed-loop control is fragile to modest uncertainty.

If the target becomes unreachable below some radius, record that radius. That is a useful result.

---

## 15. Hard decisions that deserve higher-level review

These should not be delegated blindly:

1. choose the finite reference interval,
2. define the reduced target observables precisely,
3. choose the bounded-domain CFD framework,
4. define the first normal/tangential boundary basis,
5. choose the time horizon and normalization for reachability tests,
6. define sensor observables,
7. decide how to interpret singular values physically.

Once those choices are reviewed, implementation can be delegated more safely.

---

## 16. Lower-risk tasks that can proceed independently

- visualization improvements,
- POV-Ray performance,
- scripts,
- data-format scaffolding,
- CFD installation/build scripts,
- simple solver verification cases,
- plotting tools,
- ffprobe checks,
- automated parameter logging,
- unit tests,
- documentation.

These tasks should not silently settle the hard research decisions above.

---

## 17. Research outputs to preserve

For every CFD/control experiment, save a compact machine-readable record containing:

```text
git commit
solver/version
mesh
time step
viscosity
boundary conditions
actuator basis
actuator limits
sensor definitions
target interval
target observables
normalizations
solver tolerances
error metrics
singular values / condition numbers
```

This will make later results interpretable and reproducible.
