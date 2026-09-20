# Project Tracks

This repository deliberately contains two related but distinct projects.

## Track A — Visualization

### Question

What does the proposed flow and apparatus look like in three dimensions?

### Current status

Implemented and actively usable.

### Current pipeline

```text
prescribed velocity field
        ↓
Python RK4 tracer integration
        ↓
POV-Ray frame rendering
        ↓
ffmpeg movie
```

### Important limitation

The rendered actuator hardware does **not** generate the tracer flow.

The visualization is useful for understanding motion, apparatus layout, actuator placement, sensor placement, PIV optical access, and communication. It is not evidence that the physical boundary-control concept works.

### Work that can proceed now

- improve appearance,
- improve tracer visibility,
- optimize render speed,
- improve tank/hardware geometry,
- add useful views,
- validate frame/movie pipeline.

---

## Track B — Physical realizability and boundary control

### Question

Can physically realizable external actuators and sensors reproduce something meaningfully similar to a finite portion of the desired interior dynamics?

### Current status

The research track has implemented B0 benchmark diagnostics and optional B1/B2
linear Stokes verification backends. This is a bounded verification pipeline,
not a validated boundary-control system or a physical realization of the target.

- **B0:** NumPy-only configuration, boundary-mode, observable, and sensor
  diagnostics run without a CFD solver. They check benchmark assumptions and
  verification fixtures; they do not calculate a controlled flow.
- **B1:** An optional DOLFINx Taylor–Hood backend runs linear unsteady-Stokes
  verification cases and coarse boundary pilots. Its strong-divergence check
  failed the required tolerance, so B1 does not establish a reliable
  divergence-free response.
- **B2:** A separate optional DOLFINx BDM2/DG1 backend adds divergence-conforming
  Stokes verification, stability audits, and a pre-campaign response gate. The
  stored physical-pilot gate remains failed: the tangential response has not
  converged against the independent reference, and stability/boundary issues
  still require numerical-method review. Schema-3 reports now make physical
  reference discrepancies and unresolved campaign blockers explicit; even a
  passing legacy aggregate leaves readiness false until actual response-mesh
  stability and physical accuracy are reviewed.

Changed-parameter manufactured and swirl cases are verification fixtures only;
they do not validate the physical 0.01 Hz response or demonstrate physical
control. The six-input campaign and B3 sensing work have not begun.

The acceptance-report repair and physical-reference diagnostics are complete.
The [scalable stability review](docs/realizability/B2_SCALABLE_STABILITY_REVIEW.md)
calibrates a sufficient local coercivity bound against dense small-cylinder
fixtures and compares it with sparse constrained inertia counts. The next
bounded task packages the local certificate as a separate diagnostic, with
inconclusive results kept explicit. Response-mesh stability and physical
accuracy remain unresolved. Use [SESSION_HANDOFF.md](SESSION_HANDOFF.md) for
the current model recommendation, completion criteria, and stopping conditions.

### Core constraint

The final model should not rely on arbitrary volumetric forcing.

Reference fields may use such forcing, but the realizable model should use boundary mechanisms that map to plausible hardware.

### Proposed pipeline

```text
finite reference trajectory
        ↓
bounded-domain CFD
        ↓
normal/tangential boundary modes
        ↓
input → interior-state response tests
        ↓
reachability analysis
        ↓
state → sensor response tests
        ↓
observability analysis
        ↓
finite actuator array
        ↓
hardware limits
        ↓
open-loop tracking
        ↓
realistic estimator
        ↓
closed-loop CFD
        ↓
bench experiment
```

### Immediate milestone

Do **not** begin with full control.

First answer:

> Can a modest set of physically interpretable boundary modes independently influence the reduced central-flow quantities we care about?

Then answer:

> Can realistic pressure/PIV measurements distinguish those quantities?

These questions are smaller, falsifiable, and highly informative.

---

## Shared scientific rules

Both tracks must maintain the distinctions among:

- mathematical target,
- kinematic visualization,
- CFD solution,
- boundary-control calculation,
- physical experiment.

Do not describe success in one category as success in another.

A failure or finite limitation is useful data.

---

## Documentation map

- `README.md` — project entry point and practical visualization instructions.
- `AGENTS.md` — implementation and AI-agent rules.
- `REQUEST_LOG.md` — user requests, scope, validation, and outcomes.
- `SESSION_HANDOFF.md` — current bounded task, reusable continuation request,
  model/effort recommendations, and stop conditions.
- `EXPERIMENT.md` — physical experiment concept.
- `PHYSICAL_REALIZABILITY_PLAN.md` — broad realizability philosophy and plan.
- `CONTROL_RESEARCH_ROADMAP.md` — concrete staged computational research program.
- `BOUNDARY_CONTROL_HANDOFF.md` — proposed benchmark decisions, scientific
  diagnostics, and implementation/testing work packages for the next coding agent.
- `PROJECT_TRACKS.md` — this high-level separation of the two avenues.
