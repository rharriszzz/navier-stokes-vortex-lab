# Project direction — physics and engineering first

**Owner's preference: 2026-11-01; clarified in a follow-up.** This document
records an interest in physics- and engineering-based questions. It is **not a
standing priority override** of earlier research plans or an instruction to
abandon them. Preserve the old plans, calculations, and evidence.

**When a new request leaves the direction unclear (especially `Continue`),
ask the owner whether to pursue the prior numerical plan, a physics/engineering
investigation, or neither. Wait for an answer before selecting a research task,
implementing it, or launching any related computation.** A sufficiently
specific new request supplies that choice and can proceed within its scope.

## Why the direction changed

The owner became tired of both Navier–Stokes projects because the ongoing
mathematical and computational work was difficult to understand. The owner
has some familiarity with PDEs but wants an **engineering or physical approach**.
The pursuit of a mathematical singularity is left to others.

This is a change in interests and priorities, not a technical claim that
the previous research was false or that it could not succeed.

## What this means for future work

- The older singularity-oriented work, including the R272 n=4 handoff,
  is **available as an option**, not automatically canceled or chosen.
  If a request such as `Continue` does not identify which direction to take,
  explicitly ask, and wait.
- Likewise, do not automatically switch to an engineering/physics project.
  Neither project needs to be active until the owner selects the next goal.
- If fluid mechanics becomes interesting again, begin with an intelligible
  physical phenomenon, a realistic apparatus, and quantities that could be
  observed or measured.
- Favor sound engineering reasoning: forces, pressure gradients, flow rates,
  power, energy budgets, length/time scales, Reynolds number, and other
  dimensionless parameters as appropriate.
- Use PDE analysis, CFD and optimization as necessary *tools*, not objectives
  in their own right. Explain the physical meaning and limitations before
  proposing elaborate numerics.
- Keep the distinction explicit between a prescribed kinematic animation,
  a validated numerical fluid solution, and an experimentally demonstrated
  flow. The existing rendered actuator hardware does not create its
  illustrated tracer field.

## Possible future questions, not assigned tasks

Examples include measurable vortex stretching or breakdown; how jets, pumps
or moving walls create and control swirl in water; actuator power and
pressure requirements; and whether a small bench experiment agrees with
a simple model. These examples are suggestions, not a new project plan.

If the owner chooses an engineering/physics direction, a proposal should
start by answering:
1. What physical effect are we trying to understand?
2. What apparatus might actually produce it?
3. What should happen, and why?
4. What could we measure to distinguish competing explanations?
5. What is the smallest useful simulation or experiment, and when should it stop?

Prefer a modest, falsifiable physical demonstration over extensive abstract
computations whose engineering interpretation is unclear.

## Scope and historical record

`navier-stokes-vortex-lab` is the better candidate for any eventual
physics-first investigation, but only if the owner decides to return.
`navier-stokes-physical-approximation` remains more closely associated
with the mathematical singularity construction and is not a current priority.

This preference is recorded here; **the other repository is unchanged**.
Preserve old plans, negative results, resource gates, and experimental
evidence. The `SESSION_HANDOFF.md#next-task` remains a viable *candidate*
for future work, but it is not to be selected solely on an ambiguous
`Continue`. Ask which direction the owner wants, and **stop until the
owner answers**. Do not treat this preference as vetoing an explicit request
to resume the prior mathematical/numerical work.
