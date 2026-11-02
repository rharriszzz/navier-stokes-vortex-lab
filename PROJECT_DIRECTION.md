# Project direction — physics and engineering first

**Owner's decision: 2026-11-01.** This statement supersedes the priorities
and automatic continuation instructions in older research handoffs. It does
not invalidate, alter or delete prior calculations, documentation or evidence.

## Why the direction changed

The owner became tired of both Navier–Stokes projects because the ongoing
mathematical and computational work was difficult to understand. The owner
has some familiarity with PDEs but wants an **engineering or physical approach**.
The pursuit of a mathematical singularity is left to others.

This is a change in interests and priorities, not a technical claim that
the previous research was false or that it could not succeed.

## What this means for future work

- **Pause the singularity-oriented research program**, including the R272
  n=4 numerical-comparison handoff and related solver investigations.
  Do not restart them merely because an old handoff says `Continue`.
- **Do not automatically start a different research project.** The two
  Navier–Stokes repos can remain inactive indefinitely. A new concrete
  question and explicit approval are required before substantive work.
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

A future proposal should start by answering:
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

This decision is recorded here; **the other repository is unchanged**.
Preserve old plans, negative results, resource gates, and experimental
evidence. Old `SESSION_HANDOFF.md#next-task` text is historical and paused.
A bare `Continue` must not initiate that task. Obtain a new explicit
technical objective before work or execution.
