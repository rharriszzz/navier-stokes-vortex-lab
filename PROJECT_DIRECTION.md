# Project direction — physics and engineering first

**R291 · 21 November 2026.** In 20 ms the isolated ring’s whole-section effective area grew 1.463%, and all three fixed-circulation radii grew. The corrected liquid-water face matrix passed its independent finest-perturbation check. At 12 ns the relocated disk passed pressure but missed radial acceleration and local vorticity-rate targets. Decision B calls for a 2D release mass-flux balance test after review. [Report and decision](docs/physics-first/CONCENTRATION_AND_WATER_STEP.md) · [Next task](SESSION_HANDOFF.md#next-task)

**R290 · 21 November 2026.** The unforced incompressible isolated ring traveled 1.631 mm in 20 ms. Its core flattened and its half-circulation radius grew 1.317%. The nominal area change was −0.460% with a ±1.936 percentage-point envelope across aperture, centering and numerical choices. Core contraction remains unresolved. [Measured history and decision](docs/physics-first/RING_EVOLUTION.md) · [Figure](docs/physics-first/ring-evolution/history.png) · [Next task](SESSION_HANDOFF.md#next-task)

**R289 · 21 November 2026.** The full-disk SU2 release force passes on the two finer meshes. Moving the mesh junction outside the core cuts the 12 ns inner pressure disturbance from 1.29 to 0.0446 Pa. The 25 µs dual-time trial diverges. Rotating time evolution and 3D water remain unqualified. [Scientific decision](docs/physics-first/ROTATING_DECISION.md) · [Disk measurements and figure](docs/physics-first/ROTATING_DISK.md) · [Next task](SESSION_HANDOFF.md#next-task)

**R288 · 21 November 2026.** The 8 mm gap still gives centerline decay at the original circulation. At Γ = 0.0036 m²/s and a = 2 mm, the facing peak gains vorticity at +0.142 s⁻¹. Strong radial shoulders retain a positive sign across the one-factor variations, while the peak sign changes with width, gap or tilt. Decision A supports a 20 ms pair and isolated-ring comparison after rotating-water and slow-time qualification. [Thresholds](docs/physics-first/RING_THRESHOLDS.md) · [Core sections](docs/physics-first/RING_SECTIONS.md) · [Preparation](docs/physics-first/RING_PREPARATION.md) · [Evolution design](docs/physics-first/RING_EVOLUTION_DESIGN.md) · [Next task](SESSION_HANDOFF.md#next-task)

**R287 · 21 November 2026.** Both water rings stretch along every sampled centerline arc at release. At the facing points the partner supplies +0.27530 s⁻¹ against −1.00677 s⁻¹ from viscosity. The net is −0.73147 s⁻¹ there, and more negative everywhere else sampled. The isolated ring loses vorticity at −1.00677 s⁻¹. [Budget, figure and checks](docs/physics-first/RING_STRAIN.md) · [Next task](SESSION_HANDOFF.md#next-task)

**R286 · 21 November 2026.** Removing fourth-order JST dissipation corrected the phase-dependent seam error at 64 cells. Viscosity converged under axial refinement. At 128 cells and the original step, the largest cross-strip pressure error grew to 0.07090 Pa against a 0.001 Pa limit. Halving the step restored both phases below 0.00060 Pa. The fixed-step qualification remains failed. The preferred physical experiment is a pair of detached water vortex rings on obliquely converging paths. [Qualification and raw measurements](docs/physics-first/SHEAR_QUALIFICATION.md) · [Physical design and release geometry](docs/physics-first/INTERACTING_VORTICES.md) · [Next task](SESSION_HANDOFF.md#next-task)

**R285 · 21 November 2026.** A 16-cell shift left the cross-strip pressure disturbance at the periodic seam. Its peak fell from 23.95 to 5.12 Pa, and viscosity excess fell from 15.64% to 4.73%. R286 completed the proposed corner-dissipation test. [Translation control and evidence](docs/physics-first/SHEAR_TRANSLATION.md) · [Next task](SESSION_HANDOFF.md#next-task)

**R284 · 21 November 2026.** The 10 µm transverse shear wave decayed too quickly. Effective viscosity exceeded the physical value by 95.51% on the coarse grid and 15.64% on the fine grid. Halving the time step preserved the excess. The fine-grid pressure field also developed a 23.95 Pa difference across the strip. R285 completed the proposed translation control. [Results, plot and reproduction](docs/physics-first/SHEAR_DECAY.md) · [Next task](SESSION_HANDOFF.md#next-task)

**R275 · 2026-11-21.** The owner selected the physical limits of vortex concentration in ordinary water. Study unforced dynamics and physically plausible boundary motion using compressible viscous mass, momentum and energy conservation. The first round establishes an interpretable viscous-spreading benchmark and the strain needed to oppose it. The limiting mechanism and attainable radius remain open. [Research plan](docs/physics-first/README.md)

R277 completed the [finite-cylinder spreading reference](docs/physics-first/SPREADING_RESULT.md). R280 installed SU2 with a liquid-water EOS and [qualified acoustic phase and amplitude](docs/physics-first/ACOUSTIC_RESULT.md). The [100 Pa precision control](docs/physics-first/ACOUSTIC_100PA.md) supports a storage-precision explanation for the 10 Pa total-energy discrepancy. R283 established the time-zero pressure and conservative state. The radial-stencil acceleration meets the magnitude target, with a finest-grid precision limit after EOS recovery. [Initial state and force balance](docs/physics-first/VORTEX_EQUILIBRIUM.md)

R272 is historical and requires an explicit choice to resume. [Next task](SESSION_HANDOFF.md#next-task)

## Earlier direction decision · November 1

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
