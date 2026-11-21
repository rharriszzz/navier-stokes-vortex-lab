# An isolated water ring in its first 20 milliseconds

## Equations and finite boundary

The origin is fixed at the initial ring center. Positive z follows the oriented left ring's normal. Density is fixed at 998.2 kg/m³ and ν at 1.003395 × 10⁻⁶ m²/s for the 20 °C reference. There is no swirl velocity, forcing or moving wall. Azimuthal vorticity is positive. In smooth axisymmetric flow ωθ = rη with η even in r. Taking the curl of incompressible momentum gives Dωθ/Dt = (uᵣ/r)ωθ + ν(Δ − 1/r²)ωθ. The radial motion cancels the stretching term in D(ωθ/r)/Dt. The result is Dη/Dt = νLη with L = ∂rr + (3/r)∂r + ∂zz. The dimensional material stretching of ωθ survives when it is reconstructed. [Mathematical setting](https://arxiv.org/abs/1609.02030)

Write ψ = r²φ. The streamfunction equation becomes Lφ = −η. At r = 0 the radial part of Lf is 4fᵣᵣ for either even scalar, by Taylor expansion. Velocity is uᵣ = −rφ𝓏, u𝓏 = 2φ + rφᵣ. On the axis uᵣ = 0, u𝓏 = 2φ and lim uᵣ/r = −φ𝓏. On the grid the two mass fluxes use the same tensor derivative of ψ. Their mixed derivatives commute. The axial velocity on the axis uses the analytic limit. Even reflection supplies the radial stencils for η and φ. This prevents singular floating-point divisions.

The velocity outside a compact ring decays in free space. For φ, L is the five-dimensional Laplacian with four radial dimensions and one axial dimension. Its Newton kernel is 1/(8π²d³). Averaging over the source three-sphere (area 2π²) and expanding in source/observer distance gives the boundary potential. For s = √(r²+z²) and c = z/s, moment n is ∫ r′³η s′ⁿ Cₙ(c′) dr′dz′ / [4 Cₙ(1)]. Multiply by Cₙ(c)/sⁿ⁺³ and sum n = 0 through 6, with Gegenbauer index 3/2. The code scales distances by the box radius. It recomputes all moments at each RK stage from the current flow. Through-flow carries energy across each finite face. Truncating the multipole series, quadrature of its moments, the exterior grid spacing and setting the remote η trace to its negligible release value are boundary approximations. Domain doubling tests their combined influence. The Gaussian extends mathematically beyond the box.

Five-node local polynomial differences act on a tensor mesh, uniform through r = 22 mm and |z| = 8 mm, then stretched with a sinh mapping. SciPy SuperLU factors the interior elliptic operator once per grid. A three-stage, third-order Runge–Kutta method advances both η and the carried marker coordinates, updating velocity at every stage. The release uses the scaled modified Bessel I₁ angular integral of the archived Gaussian line convolution, including its finite analytic axis limit. Independent checks call the original 512-segment Cartesian quadrature. [Solver](../../physics_first/axis_ring.py) · [Verification script](../../physics_first/axis_ring_verify.py)

## Verification before evolution

A Gaussian potential crossing the axis supplies an exact source and Dirichlet trace. For a second independent problem, a Gaussian pulse of η centered on the axis diffuses in five dimensions. Its width squared grows by 4νt and its amplitude decays as (1+4νt/a²)⁻⁵ᐟ². Error below is normalized by the actual 5 ms change. Coupled ring pilot endpoints at 0.5 ms use 2, 4 and 8 steps, holding space fixed. The material-rate check extrapolates the first-step difference of log vorticity on moving markers to zero step. The count is 73 strong points among 97 release probes.

| Cells/a | Max potential error | Axis axial-velocity error | Heat change relative error | Max velocity error (m/s) | Max projected / material rate errors (s⁻¹) | Time order |
|---:|---:|---:|---:|---:|---:|---:|
|8|2.11e−6|4.21e−6|3.32e−4|1.10e−5|0.00109 / **0.02181**|3.010|
|12|4.11e−7|8.21e−7|6.85e−5|2.17e−6|0.000194 / 0.00748|3.001|
|16|1.29e−7|2.58e−7|2.20e−5|6.86e−7|0.0000624 / 0.00262|2.996|

The coarse material rate exceeds 0.02 s⁻¹ and is diagnostic only. Both required finer levels pass. In the doubled box the a/12 line speed changes by 3.19 × 10⁻⁸ m/s. Fine release line speed is 0.06457756 m/s. The signed circulation and axial impulse agree with Γ and ρπΓR² within 1.1 × 10⁻¹⁰ relative across the tests. The maximum manufactured divergence away from the axis, including near-axis nodes, is below 9 × 10⁻¹¹ s⁻¹. The axis cancellation follows from 2∂ᵣuᵣ + ∂𝓏u𝓏 = 0. Four verification cases took 5.21 s together and peaked at 405 MiB RSS on daisy. [All measurements and gates](ring-evolution/qualification.json)
