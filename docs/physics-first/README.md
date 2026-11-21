# How tightly can a vortex in water concentrate?

**R292 · 21 November 2026.** Balancing the initial SU2 mass flux reduced the core residual 34,674-fold. All four 12 ns runs passed radial acceleration. The full and half-step local vorticity-rate discrepancies of 0.0942 and 0.0725 s⁻¹ both exceeded 0.02 s⁻¹. Recovered pressure differences dominate the discrepancy between endpoint spatial forces at the worst cell. Slow-time rotating water remains unqualified. [Report and decision](DISK_MASS_BALANCE.md) · [Next task](../../SESSION_HANDOFF.md#next-task)

**R291 · 21 November 2026.** In 20 ms the isolated ring’s whole-section effective area grew 1.463%, and all three fixed-circulation radii grew. The corrected liquid-water face matrix passed its independent finest-perturbation check. At 12 ns the relocated disk passed pressure but missed radial acceleration and local vorticity-rate targets. Decision B calls for a 2D release mass-flux balance test after review. [Report and decision](CONCENTRATION_AND_WATER_STEP.md) · [Next task](../../SESSION_HANDOFF.md#next-task)

**R290 · 21 November 2026.** The unforced incompressible isolated ring traveled 1.631 mm in 20 ms. Its core flattened and its half-circulation radius grew 1.317%. The nominal area change was −0.460% with a ±1.936 percentage-point envelope across aperture, centering and numerical choices. Core contraction remains unresolved. [Measured history and decision](RING_EVOLUTION.md) · [Figure](ring-evolution/history.png) · [Next task](../../SESSION_HANDOFF.md#next-task)

**R289 · 21 November 2026.** The full-disk SU2 release force passes on the two finer meshes. Moving the mesh junction outside the core cuts the 12 ns inner pressure disturbance from 1.29 to 0.0446 Pa. The 25 µs dual-time trial diverges. Rotating time evolution and 3D water remain unqualified. [Scientific decision](ROTATING_DECISION.md) · [Disk measurements and figure](ROTATING_DISK.md) · [Next task](../../SESSION_HANDOFF.md#next-task)

**R288 · 21 November 2026.** The 8 mm gap still gives centerline decay at the original circulation. At Γ = 0.0036 m²/s and a = 2 mm, the facing peak gains vorticity at +0.142 s⁻¹. Strong radial shoulders retain a positive sign across the one-factor variations, while the peak sign changes with width, gap or tilt. Decision A supports a 20 ms pair and isolated-ring comparison after rotating-water and slow-time qualification. [Thresholds](RING_THRESHOLDS.md) · [Core sections](RING_SECTIONS.md) · [Preparation](RING_PREPARATION.md) · [Evolution design](RING_EVOLUTION_DESIGN.md) · [Next task](../../SESSION_HANDOFF.md#next-task)

### Reproduce the ring experiment

Run from the repository root. The reference numerical files use Python 3.12.14, NumPy 2.5.5, SciPy 1.17.1 and one OpenBLAS thread. On daisy the Python/SciPy paths are recorded in the [R287 reproduction notes](RING_STRAIN.md). Generate the figure with the system Matplotlib used for the reference PNG.

```sh
export OPENBLAS_NUM_THREADS=1
out=$(mktemp -d)
python -m physics_first.ring_thresholds "$out"
python -m physics_first.ring_sections "$out"
python -m physics_first.ring_preparation "$out"
python -m unittest tests.test_ring_sections tests.test_ring_strain tests.test_water_scales
env -u PYTHONPATH MPLBACKEND=Agg python3 -m physics_first.plot_ring_sections "$out" "$out/facing.png"
diff -qr "$out" docs/physics-first/ring-experiment
```

### Earlier water investigations

**R287 · 21 November 2026.** Both water rings stretch along every sampled centerline arc at release. At the facing points the partner supplies +0.27530 s⁻¹ against −1.00677 s⁻¹ from viscosity. The net is −0.73147 s⁻¹ there, and more negative everywhere else sampled. The isolated ring loses vorticity at −1.00677 s⁻¹. [Budget, figure and checks](RING_STRAIN.md) · [Next task](../../SESSION_HANDOFF.md#next-task)

**R286 · 21 November 2026.** Removing fourth-order JST dissipation corrected the phase-dependent seam error at 64 cells. Viscosity converged under axial refinement. At 128 cells and the original step, the largest cross-strip pressure error grew to 0.07090 Pa against a 0.001 Pa limit. Halving the step restored both phases below 0.00060 Pa. The fixed-step qualification remains failed. The preferred physical experiment is a pair of detached water vortex rings on obliquely converging paths. [Qualification and raw measurements](SHEAR_QUALIFICATION.md) · [Physical design and release geometry](INTERACTING_VORTICES.md) · [Next task](../../SESSION_HANDOFF.md#next-task)

**R285 · 21 November 2026.** A 16-cell shift left the cross-strip pressure disturbance at the periodic seam. Its peak fell from 23.95 to 5.12 Pa, and viscosity excess fell from 15.64% to 4.73%. R286 completed the proposed corner-dissipation test. [Translation control and evidence](SHEAR_TRANSLATION.md) · [Next task](../../SESSION_HANDOFF.md#next-task)

**R284 · 21 November 2026.** The 10 µm transverse shear wave decayed too quickly. Effective viscosity exceeded the physical value by 95.51% on the coarse grid and 15.64% on the fine grid. Halving the time step preserved the excess. The fine-grid pressure field also developed a 23.95 Pa difference across the strip. R285 completed the proposed translation control. [Results, plot and reproduction](SHEAR_DECAY.md) · [Next task](../../SESSION_HANDOFF.md#next-task)

**R283 · 21 November 2026.** The 10 mm vortex starts with a 15.90564 Pa pressure rise from the axis to 30 mm. The radial acceleration meets its target on all grids. EOS recovery limits force-gradient convergence on the finest grid. R284 completed the proposed shear test. [Initial state and results](VORTEX_EQUILIBRIUM.md) · [Independent review brief](INDEPENDENT_REVIEW.md) · [Next task](../../SESSION_HANDOFF.md#next-task)

Start with a vortex whose fate we can predict. In still surroundings, viscosity transports rotation out of a straight column. The peak swirl moves **outward** and weakens. A three-dimensional flow can instead pull the column lengthwise and narrow it. Measuring the natural outward drift gives us the amount of stretching a later experiment has to beat.

The first round supplies dimensional estimates and a design. Round two evaluated the finite-cylinder reference and passed its conservation and refinement checks. [Five-second result and profiles](SPREADING_RESULT.md). The earlier [water feasibility study](../realizability/WATER_EXPERIMENT_FEASIBILITY_AND_COST.md) supplies apparatus context. [Water model and conservation laws](PHYSICAL_MODEL.md) · [Code assessment and solver choice](EXISTING_CODE.md) · [Round-two test specification](#round-two-test)

## Reference A · A vortex left alone

For the infinite, incompressible Lamb–Oseen column, start at a **finite** Gaussian width b₀. At elapsed time t, with radius r from the axis and circulation Γ,

```text
b²(t) = b₀² + 4νt                   ω_z = Γ exp(−r²/b²)/(π b²)
u_θ = Γ[1 − exp(−r²/b²)]/(2πr)     u_r = u_z = 0
dp/dr = ρ u_θ²/r                    p(∞) − p(0) = ρ[Γ/(2πb)]² ln 2
```

The regular axis has zero swirl speed. Throughout this plan R is the **radius of peak swirl** and U its speed. R = √x b, where x ≈ 1.256431 solves exp(x) = 1+2x on the positive branch. Thus R² grows at 4xν. With R₀ = 10 mm and U₀ = 0.1 m/s, b₀ = 8.921 mm and Γ = 0.008784 m²/s. After 5 s the infinite reference predicts **R = 11.19 mm, U = 0.0894 m/s** and 80% of the initial axial vorticity on axis. The absolute pressure increases radially because pressure must accelerate the water inward. Viscosity converts kinetic energy to heat. Compute energies in a finite volume because the infinite column's 1/r velocity tail has logarithmically divergent kinetic energy per length. [Gallay & Maekawa, *Existence and stability of viscous vortices*](https://arxiv.org/abs/1610.08384)

### Dimensional estimates

The rows are separate Gaussian profiles at **imposed constant Γ** and the same water properties. Thus UR is constant. No dynamics, contraction time or boundary power follows from these rows. The pressure deficit is the infinite-column swirl contribution alone.

| R (mm) | U (m/s) | Re = UR/ν | Ma = U/c | R²/ν (s) | ρU²/2 (Pa) | p∞ − p_axis (Pa) | U/R (s⁻¹) | Axial strain to hold width (s⁻¹) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 0.100 | 1000 | 6.76×10⁻⁵ | 100 | 4.99 | 16.99 | 10 | 0.0503 |
| 3 | 0.333 | 1000 | 2.25×10⁻⁴ | 9 | 55.4 | 188.7 | 111 | 0.558 |
| 1 | 1.000 | 1000 | 6.76×10⁻⁴ | 1 | 499 | 1699 | 1000 | 5.03 |

At 10 mm the advective time R/U is 0.10 s and sound crosses R in 6.76 μs. The Gaussian width **squared** doubles in b₀²/(4ν) = 19.9 s. The 17 Pa pressure signal is about 0.017% of atmospheric pressure. Its isentropic density contrast Δp/(ρc²) is only 7.8×10⁻⁹ fractionally. Isothermal initialization uses the EOS's isothermal derivative. Dissipating U²/2 per unit mass would raise temperature by about U²/(2cₚ) = 1.2 μK at 10 mm or 0.12 mK at 1 mm at constant pressure. These are energy scales, not heating predictions for a sealed or pumped tank. Even the conditional 1 mm core has p_axis ≈ 99.6 kPa for p∞ = 101.325 kPa, well above 2.34 kPa saturation at 20 °C. Local suction, heating, loss of circulation or breakup could change that comparison.

Reproduce the rows with `python -m physics_first.water_scales` from the repository root. The pressure test integrates the radial force independently. [Calculation](../../physics_first/water_scales.py) · [Tests](../../tests/test_water_scales.py)

### Round-two test

**Compute one finite-cylinder viscous spreading reference by radial mode summation.** This is an incompressible analytical benchmark evaluated numerically. It gives a finite energy inventory, a measurable radius shift and a known zero wall torque. It needs no CFD solver or acoustic time marching.

- **Initial and boundary data.** Cylinder radius L = 0.10 m, axial period 0.10 m, regular axis, stationary impermeable shear-free sidewall, adiabatic for the eventual liquid run. Use the above swirl at t = 0 multiplied by W(r), unity to 0.06 m and zero from 0.08 m. In between, set y = (r−0.06)/0.02 and W = 1−10y³+15y⁴−6y⁵, a C² taper. The outer return vorticity gives zero initial circulation around the wall. Report circulation on interior circles. Take constant ρ, ν as above, and initialize pressure by the radial balance with p(L,0) = 101325 Pa. In the incompressible reference this outer pressure fixes a gauge. Temperature is a reference input of 293.15 K.
- **Calculate from the initial profile only.** Project uθ onto the rigid-rotation mode r and J₁(λr/L) using weight r dr. Positive λ are zeros of J₂ because uθ′−uθ/L = 0 at the wall. Each nonzero mode decays by exp(−νλ²t/L²). The rigid mode retains angular momentum. This mode expansion solves ∂tuθ = ν(∂rruθ + ∂ruθ/r − uθ/r²) in this geometry. Recover ω_z = (1/r)∂r(ruθ), ring circulation, sub-grid peak radius, U and radial pressure differences from the resulting profiles at 0, 1 and 5 s. Compare the inner 30 mm to Lamb–Oseen at equal ν. Use pressure differences over the same radii.
- **Independent checks.** Per unit length, L_z = 2πρ∫r²uθ dr is constant, mass is fixed and net vector momentum is zero by symmetry. K = πρ∫r uθ² dr decreases by the time integral of 2πμ∫r(uθ′−uθ/r)² dr. This is the heat released in the incompressible mechanical balance. Record ρ and T as inputs and leave the actual thermal response for the compressible test.
- **Decision.** Try 32/64/128 nonzero modes and 512/1024/2048 radial quadrature points, varying each separately. The exponentials are exact in time. Halve the time spacing for the dissipation integral from 0.1 to 0.05 to 0.025 s. Require the final two refinements to agree within 0.02 mm in R, 0.05 Pa in p(30 mm)−p(0), and 0.5% of K(0)−K(5) in the integrated energy balance. Also require the energy residual itself below 0.5% of the measured kinetic-energy loss and |ΔL_z|/|L_z(0)| < 10⁻⁶. Report the initial reconstruction error against the input profile. Expect R(5) within 0.05 mm of 11.19 mm. A converged discrepancy calls for checking confinement, taper and peak extraction. A failed budget or unresolved shift stops progression. Report it as a reference problem, without drawing a water-limit conclusion.

### Physical test after the reference

R281 measured the energy precision at tenfold pressure amplitude. [100 Pa comparison](ACOUSTIC_100PA.md) · [Next task](../../SESSION_HANDOFF.md#next-task)

R279/R280 completed the acoustic control with SU2 and CoolProp. Speed, amplitude, mass and momentum met the specified checks. The signed energy difference is near the precision floor at 10 Pa. [Results and procedure](ACOUSTIC_RESULT.md) · [Installation](SU2_WATER_SETUP.md)

Keep the cylinder, taper, velocity and T₀. For compressible water integrate **dp/dr = ρ(p,T₀)uθ²/r** inward from the initial wall pressure, then set ρ and e from the same EOS and E = e+|u|²/2. The wall pressure is subsequently free to evolve. Regularity, zero tangential wall traction, insulation and periodic ends admit no energy input or net torque. This is a balanced initial state. Viscosity immediately changes the profile, the liquid can launch sound and its temperature evolves.

First qualify the candidate's acoustic response in a tiny periodic 0.10 m line of the same water. Start with one right-moving sinusoid of 10 Pa amplitude about the stated p₀, uniform entropy s₀, ρ and T from (p,s₀) and axial velocity p′/(ρ₀c₀). Measure speed and amplitude over one period L/c, all three conserved inventories, ρ and T. Swirl, vorticity and core are absent by construction. Use 32/64/128 cells and independently halve an acoustically resolving step (start with cΔt/Δx ≤ 0.5). Require phase speed within 1% of the EOS and amplitude error under 2% on the finest two resolutions. Use the same budgets below. Failure leaves acoustic signatures uninterpretable.

Then compare the compressible vortex to the **finite** reference at 0, 1 and 5 s. Use rotational symmetry with swirl for this check. Start at 16/32/64 radial cells per initial peak radius. Resolve startup at acoustic steps and compare p′, radial velocity and wave arrival/reflection times. For slow evolution use implicit pressure coupling and independently halve physical steps (e.g. 0.02/0.01/0.005 s). An implicit step may step over sound in the slow segment. Resolve any claimed acoustic transient in physical time. Use double precision, perturbation pressure around a thermodynamic absolute base, tight iterative tolerances, and evaluate energy differences relative to a fixed reference e₀, subtracting e₀ times the mass balance. Test a half-speed vortex at the same ν for the expected U² pressure scaling and U-independent leading spreading rate.

#### Acceptance for a physical run

Require independent spatial/time refinement, negligible change on tightening solver tolerances, and balances over each stored interval from actual face fluxes. As initial design tolerances use mass defect < 10⁻¹⁰ of inventory, momentum and torque-impulse defects < 10⁻⁴ of MU and MUR respectively (M is total mass, U and R are characteristic scales), and energy defect < 1% of the resolved kinetic-energy change over the 5 s window. For the acoustic control also compute wave energy from p′²/(2ρ₀c₀²)+ρ₀u′²/2, use the wave velocity amplitude as U and report the roundoff floor of the total-energy difference. Distinguish attenuation of resolved wave energy from total-energy drift. Report absolute defects too.

Require agreement with the finite reference to 0.05 mm in R and 0.2 Pa in the inner pressure difference at 5 s, or a converged physical explanation. Compare ΔK, Δinternal energy, Φ and pressure dilatation. If heat or acoustic amplitudes fall below the numerical floor, report an upper bound. Neither a converged velocity alone nor a small residual qualifies the solver.

## Reference B · What stretching would have to supply

The steady incompressible Burgers vortex uses the same Gaussian swirl with an **imposed** strain s = ∂u_z/∂z > 0, u_z = sz and u_r = −sr/2. For an aligned Gaussian in uniform time-dependent strain the width obeys d(b²)/dt = 4ν − s b². Thus s = 4ν/b² merely holds the width. To shrink it the local axial strain must exceed that value while rotation remains coherent. The table's U/R is a swirl-gradient scale, not the imposed s. Infinite linear strain requires velocities growing without bound at large distance. In a finite control volume inward flow carries angular momentum and axial outflow exports it. For constant ρ the steady momentum equations give ∂rp = ρ(uθ²/r − s²r/4) and ∂zp = −ρs²z. These strain-induced gradients explain why the swirl-only pressure table cannot be used for the entire strained flow. Pressure tractions, advective momentum, boundary work and viscous dissipation have to balance. The steady formula supplies neither a finite pump power nor a source of indefinite unforced stretching. [Burgers vortex analysis](https://arxiv.org/abs/1002.2489)

**Later paired finite experiment, contingent on A.** Consider a filled cylinder with initial L = 0.10 m, height H = 0.20 m, centred at z = 0. Use the same initial swirl and multiply by W(|z|), with the same 0.06/0.08 m cutoffs. The vortex ends smoothly inside stationary no-slip walls. Initialize T₀, calculate a leading pressure field from ∇²p = −ρ₀ div[(u·∇)u] with the normal momentum condition at the stationary walls and mean 101325 Pa, then use the EOS for ρ,e. This leading low-Mach preparation allows axial adjustment. Check startup sound. Compare two copies of this finite-energy initial state through 5 s, recording the stroke and relaxation separately.

1. **Unforced.** Hold all walls fixed and insulated. The finite ends allow internal axial motion and transient self-stretching to be measured, with zero continuing wall work. Account for the wall reaction and any removal of angular momentum. Loss of initial kinetic energy bounds what the surrounding water can supply.
2. **Boundary driven.** Prescribe only the motion of a flexible cylindrical sleeve and two compliant end diaphragms on symmetric translating supports. Over 2 s set L(t)/L₀ = 1−0.05 h(t/2 s), H(t)/H₀ = [L₀/L(t)]² with h(y) = 10y³−15y⁴+6y⁵ for 0≤y≤1. Hold still thereafter. Move each boundary point by this affine radial/axial map, use no slip and insulation. Volume is fixed, the sleeve moves inward 5 mm and the end supports draw the water axially as the diaphragms contract radially. The mean logarithmic axial extension rate is 0.0513 s⁻¹, close to the initial ideal holding rate. **Interior strain is an output.** Measure forces and wall power separately on sleeve and end diaphragms. This idealization specifies wetted-surface displacements. Actual diaphragm shape, available force and junction losses would need measurement.

Run the same refinement and interval-budget checks as A, including the moving-volume fluxes, signed boundary impulse, torque and work. In B normalize energy defects by resolved energy exchanged or dissipated, and establish uncertainty from the two finest resolutions. Compare plane-by-plane centreline, R, peak swirl, Γ(r), vorticity magnitude and direction, axial strain, stretching (ω·∇)u, dilatation, viscous transport and the pressure/density-gradient contribution to vorticity. Track pressure minima, ρ, T, angular-momentum flux and work through a **fixed inner cylinder** as well as the whole vessel. Recenter slices on the moving core and report azimuthal variation. In a tank these observables would need resolved multi-plane velocity measurements, pressure taps or probes with absolute calibration, thermometry and synchronized wall displacement/force records. A displaced or split core can mimic a narrower azimuthal average.

Require a sustained decrease in R exceeding the summed radius uncertainties, increasing aligned vorticity, a consistent circulation profile and an accounted source of energy/strain. Report duration and rates against the fixed-wall control. If strain is too weak, viscosity can explain spreading. If a core fragments before narrowing, report coherence loss. If the signal is below refinement error, the result is unresolved. Axisymmetry with swirl can represent axial stretching but suppresses nonaxisymmetric breakup. A stability claim would require a later three-dimensional perturbation comparison. No DNS, contraction to a specified radius, mechanism ranking or singularity conclusion follows from this first round.
