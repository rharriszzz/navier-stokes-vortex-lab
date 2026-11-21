# How close and how strong do the rings need to be?

At the original circulation, closing the initial gap from 12.019 to 8 mm increases the strongest axial extension by a factor of 2.09. It offsets 57.2% of the local viscous loss. **All 256 centerline locations still lose vorticity at 8 mm.** The first sampled centerline to break even requires Γ = 0.003147 m²/s per ring at 8 mm, 1.75 times the original circulation.

## Change only the center spacing

Keep the R287 oriented circles at R = 15 mm, equal Γ = 0.0018 m²/s, Gaussian e-folding a = 2 mm, tilt ±30° from vertical and ν = 1.0034 × 10⁻⁶ m²/s. Translate the centers to x = ±(R cos 30° + gap/2). This sets the minimum three-dimensional distance exactly since the facing points realize the minimum x separation at equal y,z. Superpose the free-space fields and use the total vorticity direction for both projections. The fractional material rate is s + v where s = ω̂·∇u·ω̂ and v = ν ω̂·Δω/|ω|. Multiplication by |ω| gives s⁻². These are leading uniform-property, solenoidal release budgets. The small dilatational, baroclinic and variable-property contributions of a prepared compressible state require separate checks.

| Gap mm | Range of s, s⁻¹ | v at facing, s⁻¹ | Net range, s⁻¹ | Facing magnitude rate, s⁻² | Facing offset |
|---:|---:|---:|---:|---:|---:|
|12.019|0.01737 to 0.27530|−1.00677|−0.98940 to −0.73147|−104.43|27.3%|
|10|0.02151 to 0.38934|−1.00677|−0.98527 to −0.61744|−88.15|38.7%|
|8|0.02687 to 0.57592|−1.00678|−0.97991 to −0.43086|−61.51|57.2%|

Both rings attain their largest sampled net at facing. The isolated control gives −1.00677 s⁻¹ throughout. Across the three cases the 256→512 change in any net rate is below 10⁻¹⁴ s⁻¹. Independent Cartesian centered gradients projected on ω̂ differ by at most 0.00246 and 0.000615 s⁻¹ at a/8 and a/16. Independent directional differences, the partner-only checks, both reflections, curl and divergence also pass the original gates. These bound line quadrature and differentiation errors at the specified targets. They do not bound uncertainty in a nozzle release. [Both rings at all azimuths](ring-experiment/centerlines.csv) · [All three resolutions and checks](ring-experiment/gap_checks.json) · [Kernel derivation and baseline tests](RING_STRAIN.md)

## Critical circulation

Scale both rings by the same positive factor k. Then u, ∇u, ω and Δω scale with k, ω̂ stays fixed, s becomes ks and v stays fixed. With v negative at every centerline sample here, take the minimum of −Γ₀v/s over positive s. All nine minima occur at facing. Reintegrating the kernels at 0.99, 1 and 1.01 times each calculated threshold gives respectively negative, zero within 2.5 × 10⁻¹⁵ s⁻¹, and positive maximum net rate. The largest 256→512 change at threshold is below 9 × 10⁻¹⁴ s⁻¹. Reflection gives the other ring. These are thresholds for the sampled geometric centerlines.

| Gap mm | a mm | Γ critical, 10⁻³ m²/s | ReΓ | Isolated line speed m/s | Peak swirl m/s | Axis deficit Pa | Swirl Mach ×10⁴ |
|---:|---:|---:|---:|---:|---:|---:|---:|
|12.019|1.5|11.685|11646|0.2275|0.791|1063|5.34|
|12.019|2.0|6.583|6560|0.1181|0.334|190|2.26|
|12.019|2.5|4.221|4207|0.0707|0.171|50|1.16|
|10|1.5|8.263|8235|0.1609|0.559|532|3.78|
|10|2.0|4.655|4639|0.0835|0.236|95|1.60|
|10|2.5|2.985|2975|0.0500|0.121|25|0.82|
|8|1.5|5.586|5567|0.1087|0.378|243|2.55|
|8|2.0|3.147|3136|0.0564|0.160|43|1.08|
|8|2.5|2.018|2012|0.0338|0.082|11|0.55|

ReΓ = Γ/ν. Isolated line speed comes from the curved-ring quadrature. Swirl uses the straight Gaussian vθ = Γ(1−exp(−r²/a²))/(2πr) at r = 1.121a. Integrating ρvθ²/r gives the straight-core center-to-ambient pressure deficit ρ ln(2)[Γ/(2πa)]². Use ρ = 998 kg/m³ and c = 1482 m/s. Curvature and the cross term in pressure from two rings change the actual field. [Direct threshold measurements](ring-experiment/critical.csv)

The a⁻² viscous penalty makes a thin core harder to amplify. Broadening the core also reduces the space between its outer layers. As an overlap indicator, each isolated straight Gaussian contributes exp[−(gap/2a)²] of peak magnitude at the midpoint. The 8/2.5 case gives 7.73% per parent, with opposing directions there. The 8/2 and 10/2.5 cases give 1.83%, and every other case is below 0.31%. All have distinct peaks, but the 8/2.5 shoulders and outer circulation cannot safely be assigned to isolated parents across the gap. Cancellation can conceal the two tails. At the other extreme, a thin high-Re core well separated geometrically still needs an independent formation and stability check.

## Reproduction

From the repository root with Python, NumPy and SciPy, run the following into a fresh directory. The default kernel also reproduces the archived R287 CSV and JSON byte for byte in the original environment.

```sh
export OPENBLAS_NUM_THREADS=1
python -m physics_first.ring_thresholds /tmp/water-thresholds
python -m unittest tests.test_ring_strain tests.test_water_scales
```

[Parameter study](../../physics_first/ring_thresholds.py) · [Shared kernel](../../physics_first/ring_strain.py)
