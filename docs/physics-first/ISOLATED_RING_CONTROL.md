# First 3D control and the accuracy it would need

**Use one isolated, freely translating ring before the interacting pair.** The single ring supplies known circulation, symmetry, translation and spreading against which to test whether the measurement can detect narrowing. No 3D field was advanced. The present serial solver and PC cannot resolve the proposed endpoint within the measured resource envelope.

## Reproducible release

- Retain only the left curve of the selected 8 mm-gap geometry. In metres use C = (−0.016990381,0,0), e₁ = (cos 30°,0,−sin 30°), e₂ = (0,1,0). Parameterize X(θ)=C+0.015(e₁cosθ+e₂sinθ) with positive orientation. Use Γ=0.0036 m²/s, kernel width a=0.002 m. Convolve its line tangent with exp(−|x−X|²/a²)/(π³ᐟ²a³) for ω. Obtain u from the enclosed-Gaussian Biot–Savart integral. Sample 256 then 512 source angles. The coincident limit is implemented. Compare u, curl u, ∇u and Δω to direct free-space quadrature. With only one ring in its own axial frame, velocity is meridional and vorticity azimuthal. [Kernel](../../physics_first/ring_strain.py) · [Geometry](RING_EVOLUTION_DESIGN.md#initial-fields-and-thermodynamics)
- In a 160 mm periodic cube, periodize the Gaussian vorticity then solve for the zero-mean solenoidal velocity with the discrete curl inverse. Average onto the actual mesh and enforce flux compatibility there. Evaluate the **actual** mass and energy residuals and their predicted pressure rate as well as the irrotational momentum residual. The disk shows why a small net radial force alone is insufficient. Compare a 320 mm cube at matched core spacing. Require image changes in speed <0.000646 m/s, projected net rate <0.01 s⁻¹, and flux <0.2% Γ. Also require the change in the eventual pair-minus-single width signal under box doubling to be <¼ of its magnitude. Periodic images differ from physical tank walls.
- Solve Δp′=−ρ₀∂ᵢuⱼ∂ⱼuᵢ with zero mean and periodic boundaries, check source compatibility and the discrete projection. Set p=101325 Pa+p′ and T=293.15 K. Flash liquid ρ,e and store (ρ,ρu,ρE). Independently recover p,T,c and the saturation margin. Use true sound speed, molecular viscosity and conductivity and zero external forcing. Resolve startup sound with short cadence. Repeat for combined velocity before a pair run because pressure contains cross terms.
- As a direct check, we re-evaluated **only the left curve** at the facing section with 8×24 and 16×48 aperture quadratures and 256/512 source angles. In the disk of radius 2a the signed flux is 0.003533146 m²/s (98.14294% Γ), and positive-vorticity covariance gives widths **1.923641 and 1.927089 mm**. The centroid sits 0.061952 mm radially inward. At the finest quadrature Stokes flux and contour circulation agree within 3.7 × 10⁻¹⁶ Γ. The prescribed full Gaussian width is 2 mm. Apply this same finite-aperture measurement to a remeshed release. [Isolated measurements](rotating-disk/isolated_section.json) · [Section integration](../../physics_first/ring_sections.py)

Reproduce the isolated section with the same Python/SciPy environment as the disk.

```python
from physics_first.ring_sections import CANDIDATE, section_shape
for nr, na, ns in ((8, 24, 256), (16, 48, 512)):
    print(section_shape(0, CANDIDATE, nr, na, ns, sides=(-1,)))
```

## What to follow for 20 ms

Use an initial 0.5, ⅓ and 0.25 mm near-core spacing sequence, extending finer if the last pair fails. Keep a padded refinement region around the whole ring and its expected 1.29 mm flight. Restrict, prolong and synchronize conserved face fluxes. Retain matched discretization around both future ring positions for a pair subtraction. Shift the ring half a cell and rotate it relative to the mesh. Refining the kernel quadrature alone leaves the grid error untested.

Advect marked material arcs with time-consistent velocity interpolation. Separately locate the vorticity ridge at each output and slice normal to it. Track the translation of both centroid and ridge along e₁×e₂; the free-space line-point speed at release is about **0.0646 m/s**. Report velocity gradients, stretching ω̂·∇u·ω̂, dilatation, baroclinic torque and curl[(div τ)/ρ] projected on ω̂. Check their sum by differencing material ln|ω|. The isolated geometric centerline starts near −1.00677 s⁻¹, and the rotating section has different tendencies away from the center. Report weak-vector masks. Distinguish marker migration from viscous migration of the ridge.

At least every 0.5 ms record both principal widths, their product, half-circulation radius, signed flux, positive flux, contour circulation, material segment length and ridge length. Vary the aperture, resolution, probe phase and reconstruction. Compare each quantity to its own release value and to the isolated result at the same age. A roll-up can intensify while its sectional area grows. Require a fall in area and in half-circulation radius together with lengthening and increasing material intensity before claiming concentration. Stop assigning a parent width if sectional identity is lost.

Difference the periodic mass, three momentum components and total energy cellwise from release. Require relative mass drift <10⁻¹¹, momentum change <10⁻⁵ρΓπR², energy defect <1% of initial kinetic energy and <10% of the resolved loss. Account for pressure work, viscous work and heat conduction. At release require Stokes agreement <0.5% Γ and projected material rate error <0.02 s⁻¹. Measure startup acoustic changes and enforce <0.05 Pa unexplained core ripple after adjustment. Halve physical Δt, tighten the inner solve by 10×, enlarge the box, and compare the resulting changes with the measurement uncertainty. [Detailed budget equations and criteria](RING_EVOLUTION_DESIGN.md#measurements-and-prospective-decision-limits)

At the interacting facing peak, 0.14157 s⁻¹ × 0.020 s gives **0.283%**, conditional on persistence. Its sign changes for some plausible width, gap and tilt variations. A quarter-signal envelope is 0.071% in intensity, equivalent to about 0.035 s⁻¹ average rate uncertainty. The release-rate gate is stricter. The actual area or width change requires its **own** uncertainty envelope below ¼ of the claimed change over three successive outputs. At a 2 mm width even 0.07% is just 1.4 µm. Subcell fits can reach such precision only with measured convergence. The isolated control can falsify this accuracy and calibrate the method under curvature and diffusion. Passing it cannot establish the uncertainty of two interacting, tilting cores. Matched pair refinements and prepared-ring measurements are still essential.

## Daisy sizing for the isolated ring

One isolated-only estimate uses a fine 48×50×36 mm patch, a middle 76×80×64 mm patch, both centered on the single ring and aligned to Cartesian axes, inside the periodic 160 mm box. At 0.25/0.5/1 mm the replacement count is 160³−76·80·64 + 8(76·80·64−48·50·36) + 64·48·50·36 = **11,658,240 cells**. The larger box with unchanged patches has 40,330,240. The prior pair-ready layout retains 19.44 M active cells in the small box. Refinement padding, ghost layers, conservative mesh interfaces and adequate interface smoothness have to be verified on the actual solver.

| Estimate for 160 mm isolated layout | On daisy |
|---|---:|
| 5 conservative doubles, one output | 445 MiB |
| 41 outputs at 0.5 ms spacing including release | 17.8 GiB |
| Static XYZ coordinates, stored once | 267 MiB |
| 3 extra doubles per output for vorticity | +10.7 GiB per sequence |
| Explicit memory proxy from disk RSS slope | 16.9 GiB |
| Implicit memory proxy including measured extra solver storage | ~66 GiB |

The PC exposes 28 logical CPUs on an i7-14700F; this SU2 binary uses one. It had 5.2 GiB available out of 7.6 GiB at preflight. Preserve 25% of available RAM and avoid swap, leaving ~3.9 GiB for a pilot under those conditions. The explicit 32→64 disk RSS slope is ~1.55 kB/additional point. At the same 32 resolution implicit peak RSS exceeded explicit by ~4.55 kB/point. Using their sum gives ~66 GiB as a planning proxy for the single-ring layout. These are extrapolations from 2D nodes to an assumed comparable number of 3D control volumes. Extra 3D connectivity, a fifth equation, pressure/Krylov vectors and refinement management may raise either figure. The output estimates omit mesh connectivity, derived fields and duplicate checkpoints. Save probes at high cadence and separate them from bulk fields.

The measured explicit throughput on the medium disk is 4.48 s per 36,993 points per two-stage step. At matched per-point throughput, ~1.8 million explicit steps for 20 ms at 0.25 mm would take **about 80 serial years** on the isolated layout. For comparison only, 2.82 s per 36,993 points per implicit inner iteration × 12 iterations × 800 physical steps projects to **about 99 days**, even though those 12 iterations actually diverged. There is no credible forecast for a converged 3D implicit run. Neither scenario fits local RAM. A different implementation or host needs its own bytes/cell and seconds/step measurement. No 3D pilot, memory allocation or output was used to make these estimates.
