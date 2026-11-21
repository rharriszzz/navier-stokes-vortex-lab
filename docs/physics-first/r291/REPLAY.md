# R291 evidence and reproduction

The [scientific decision](../CONCENTRATION_AND_WATER_STEP.md) uses the [measurement definitions committed before reanalysis](PROTOCOL.md). All commands start in the repository root. Use Python 3.12.14 with NumPy 2.5.5, SciPy 1.17.1 and CoolProp 7.2.0 for the numerical readers. Daisy's system Python supplies Matplotlib. The existing environment setup is documented in the [ring report](../RING_EVOLUTION.md#reproduction-and-data-columns) and [SU2 setup](../SU2_WATER_SETUP.md).

## Ring evidence

The ten CSVs in [sections](sections/) hold nine numerical histories plus an analytic pure-diffusion control, each at 41 times. Each row carries frame, seconds, definition, metric and SI value. The primary case adds disks of radius 1.8a through 5a and independent center, quadrature and sampled-field measurements. The section weights use dr dz, with no cylindrical volume factor. The full-section Simpson weights include the stretched exterior. The diffusion-only ring uses the archived Gaussian convolution solution with a² → a²+4νt. The signed flux benchmark is Γ = 0.0036 m²/s. The equilibrium null/overlap experiment uses the independently oriented analytic ring field at fixed prescribed shape. Blank entries in the assignment table indicate missing crossings before the midplane. Radii in that table use the geometric line center. Rings at the smaller gaps are hypothetical measurement controls.

```bash
out=$(mktemp -d)
evidence=docs/physics-first/r291
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
timeout 480 python -m physics_first.ring_concentration docs/physics-first/ring-evolution "$out/sections"
diff -qr "$evidence/sections" "$out/sections"
python -m physics_first.ring_concentration_summary "$out/sections" > "$out/ring_summary.json"
python -m physics_first.ring_assignment "$out/assignment.csv"
cmp "$evidence/ring_summary.json" "$out/ring_summary.json"
cmp "$evidence/assignment.csv" "$out/assignment.csv"
env -u PYTHONPATH MPLBACKEND=Agg /usr/bin/python3 -m physics_first.plot_concentration \
  "$out/sections" "$out/concentration.png"
```

## Measurement details

The full-section integrals use the meridional plane from the axis to the remote box boundaries. Total circulation stayed within 10⁻¹¹ of its release value in relative terms. The projected vorticity had effectively one sign. Ellipse area is π times the product of the positive-weight covariance widths √(2λ). The two area definitions have different normalizations, so compare their changes. Diffusion broadened all three radii nearly equally. In the inviscid control the inner quarter tightened while the outer three quarters spread. The viscous ring spread more slowly in effective area than heat flow alone, by 0.549 percentage points. Turning viscosity on in the advecting ring increased its area change by 2.041 points. These matched comparisons include changes in the flow itself. [41-sample histories, controls and component uncertainties](ring_summary.json)

**Accuracy depends on the question.** All nine native histories were reconstructed because the archived fine field patch ends inside the tails needed for the full area. At every output we checked ridge coordinates, carried marker, circulation and half-radius against the original records. Independent checks used the saved float32 fields, 16×64 versus 32×128 polar quadrature, a quadratic peak versus a spline stationary point, the circulation centroid, and a material center. The two native ridge fits differed by at most 1.11 µm. For each release-relative signal we summed absolute sensitivity to grid, step, domain and half-cell shift, plus measurement effects. For full-section areas we used the 4a/5a tail check. The effective and ellipse area envelopes at 20 ms are ±0.00030 and ±0.00170 percentage points. Both clear the quarter-signal criterion at the last three outputs. These are empirical sensitivities for this ring.

A left-state perturbation at a representative wide-disk core state used the compiled SU2 centered momentum/energy flux on averaged primitives and independent HEOS flashes of (ρ,e). The probe separately differences the JST jump per unit frozen dissipation coefficient. Equal states remove the effect of primitive averaging on the Jacobian comparison. We used a unit x normal and varied each of the four conservative components at three perturbation sizes. Selected equal-state entries follow, using dimensional SU2 variables and its one-half centered-face weight. [Full matrices including unequal states](face.json) · [SU2 centered implementation](https://github.com/su2code/SU2/blob/7048fd35f56d4bf52e586429d6746a36a10255f8/SU2_CFD/include/numerics_simd/flow/convection/centered.hpp)

## Face audit and disk experiment

The face probe compiles the qualified release's projected-flux and implicit-matrix kernels and includes its conservative jump statements directly from centered.hpp. It freezes the JST multiplier and reports its jump per unit coefficient. On the actual disk the pressure sensor, corrected spectral radius and fourfold Jacobian fix factor multiply this contribution. In a truly uniform flow the sensor vanishes. The audit isolates the constitutive derivative from these multipliers. The second test uses different left/right primitive states to exercise the arithmetic averaging. Evaluating the corrected matrix uses SU2 secondary variables (∂p/∂ρ at e, ∂p/∂e at ρ). The independent test recovers all perturbed states with CoolProp. The [audit archive](face.json) stores each finite-difference scale. On the unequal face the intermediate perturbation failed the 3×10⁻⁶ absolute + 2×10⁻⁶ relative entry check, including a 6.02×10⁻⁶ difference in the normalized enthalpy row. The coarsest and finest perturbations pass that same test. This nonmonotone finite-difference noise limits small momentum-column comparisons. The large density-column defect persists. The equal-state corrected result also agrees with a separate analytic HEOS chain rule.

The physical trial uses a new executable made by recompiling one SIMD translation unit in a private header copy and linking it against the qualified build objects. The correction is conditional on 2D, stationary mesh, CoolProp, JST and zero fourth-order coefficient. For each left/right conservative perturbation it differentiates mass flux from the mean density and velocity, pressure from the side's EOS, and energy flux from mean total enthalpy. For the JST jump its last row differentiates ρH = ρE+p. The remaining fixed-coefficient preconditioning approximations stay in the matrix. Upstream source revision is 7048fd35f56d4bf52e586429d6746a36a10255f8. On daisy the qualified executable SHA-256 was 0941113d648fbd79bd745ef68f050f982225c479e3ca0f59ad28d582c28d84aa before and after. The separately linked trial executable was e8d2d6bf2e1f1c15e9c8788e9cfdd233dcd4aa1cba85bd4659d1a6ff08d60806. The archive includes conservative fields and logs, with no binary distribution.

```bash
# Requires the existing SU2 build and its compiler and ninja on PATH.
source_tree="$HOME/.local/opt/water-acoustics/SU2-8.6.0"
python -m physics_first.rotating_disk "$out/release" 32 --wide
python -m physics_first.disk_face_audit "$source_tree" "$out/release/state_00000.dat" > "$out/face.json"
cmp "$evidence/face.json" "$out/face.json"
python -m physics_first.build_disk_experiment "$source_tree" "$out/experimental"
for trial in full half tight; do
  python -m physics_first.disk_step_trial "$out/release" "$out/experimental/SU2_CFD_water" \
    "$out/trials" "$trial" || exit 1
done
python -m physics_first.disk_step_evidence pack "$out/trials" "$out/disk.zip"
```

The trial runner verifies the native historical mesh, configuration and initial conservative state by SHA-256. It uses a fresh directory per case and caps each at 420 s, 2.5 GiB virtual memory and ten pseudo-iterations per step. Settings are backward Euler in physical time, pseudo-CFL 10, FGMRES/ILU(0), 50 linear iterations maximum. The four logged nonlinear RMS residuals must each fall below 10⁻⁵ (tight 10⁻⁶), with relative linear tolerance 10⁻⁸ (tight 10⁻⁹). These are SU2's dimensional residual monitors. The maximum final log₁₀ residuals were −5.846 for full, −6.420 and −6.420 at the two half-step endpoints, and −7.208 for tight. Large-step conditioning and the spectrum of the full Jacobian have yet to be measured.

## Replay without a CFD run

[disk.zip](disk.zip) stores the configurations, solver and resource logs, residual histories, and all four implicit endpoint states (including 6 ns). The four conserved nodal fields are losslessly XOR-encoded against the archived wide release. The old [fields archive](../rotating-disk/fields.zip) contains that common release and both explicit reference times. The measurement command uses those archives directly. Local stress power uses a cellwise Green–Gauss velocity gradient and Newtonian stress with zero bulk viscosity. Circulation is checked from an oriented square loop against integrated cell curl, with analytic diffusion over the same cells. The wall momentum impulse uses end-time traction for backward Euler and output-to-output trapezoids for the explicit reference. The net wall force vanishes by symmetry in the continuum. Mass and energy have zero physical flux through the rigid adiabatic wall. Tight and nominal tolerance changes were combined, so they measure joint sensitivity.

```bash
python -m physics_first.disk_step_evidence measure "$evidence/disk.zip" \
  docs/physics-first/rotating-disk/fields.zip > "$out/disk.json"
cmp "$out/disk.json" "$evidence/disk.json"
# The same command with --require-qualified writes the evidence and exits 1 on the scientific failures.
python -m unittest -v tests.test_ring_concentration tests.test_axis_ring tests.test_cylinder_spreading \
  tests.test_rotating_disk tests.test_ring_sections tests.test_ring_strain tests.test_water_scales \
  tests.test_vortex_equilibrium tests.test_water_acoustics tests.test_water_shear
```

Solver exit, algebraic convergence and physical qualification are distinct fields of evidence. The [gate file](disk.json) includes every checkpoint, raw energy criterion, full/half/tight differences, explicit comparison and physical stop. The historical 25 µs trial was on the earlier mesh and used the installed matrix. No matched 25 µs intervention or longer physical-time trial qualified in this round.

The predefined whole-section observables passed their last-three-output uncertainty gates. All three fraction radii missed those gates when center choice was included. Across both integration orders and all static gap/aperture controls the maximum signed-flux difference was 2.6×10⁻¹⁴ Γ. The clipped negative-flux diagnostic differed by up to 0.00081 Γ as quadrature nodes crossed its zero contour. The negative-flux numbers are lower precision than the signed flux.
