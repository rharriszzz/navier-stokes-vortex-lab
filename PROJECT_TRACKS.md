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

A research plan exists; substantive CFD/control implementation has not yet begun.

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
- `EXPERIMENT.md` — physical experiment concept.
- `PHYSICAL_REALIZABILITY_PLAN.md` — broad realizability philosophy and plan.
- `CONTROL_RESEARCH_ROADMAP.md` — concrete staged computational research program.
- `PROJECT_TRACKS.md` — this high-level separation of the two avenues.
