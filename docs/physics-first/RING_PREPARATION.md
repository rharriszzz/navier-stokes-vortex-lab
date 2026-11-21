# Can two detached water rings reach the candidate state?

A pair with **R = 15 mm, a = 2 mm, Γ = 0.0036 m²/s per ring, 8 mm centerline gap and 60° included angle** has a credible mechanical speed, energy and circulation scale. The open experimental question is whether two rings reach those five properties **together**, after detachment and before either core has deformed appreciably. The candidate was selected by doubling the nominal 0.072 m/s discharge at the original stroke. It keeps the original width, well clear of the 8 mm / 2.5 mm overlap case, as a target to measure. [Gap and critical circulation results](RING_THRESHOLDS.md) · [Core measurements](RING_SECTIONS.md)

## From a nozzle setting to a measured release

For a 25 mm circular exit and 50 mm slug length, the displaced volume is 24.54 mL per nozzle and L/D = 2. For nearly uniform, constant exit speed U, the starting shear-layer estimate Γ_slug ≈ ½∫U²dt = UL/2 gives the following settings. If piston and exit areas differ, convert piston motion to exit flow by volume continuity. With ramps, measure both ∫U dt and ∫U²dt. The piston does mechanical work only during preparation. A remote return accommodates displacement in a filled tank and is quiescent by the observation interval.

| Target at a = 2 mm | Γ, 10⁻³ m²/s | Nominal exit m/s | Nominal stroke time s |
|---|---:|---:|---:|
| Original |1.800|0.072|0.694|
| Threshold at 12.019 mm |6.583|0.263|0.190|
| Threshold at 10 mm |4.655|0.186|0.269|
| Threshold at 8 mm |3.147|0.126|0.397|
| 8 mm candidate |3.600|0.144|0.347|

Gharib, Rambod and Shariff observed the transition to a leading ring plus trailing jet at stroke ratios 3.6–4.5 over their tested conditions. A stroke ratio of two supports trying a single release. Their result does not determine the circulation captured by this ring, its roll-up radius or the effect of deceleration. Matching Γ at 0.072 m/s by doubling the stroke would instead move L/D to four, near the transition. Keep the short stroke in the first comparison. [Primary formation experiment](https://doi.org/10.1017/S0022112097008410)

De Aquino and colleagues measured water rings over piston velocities of 0.06–0.18 m/s. In their apparatus the propagation speed was about 0.576 times generator speed, ring diameter about 1.5 times generator diameter, and core size decreased with generator Reynolds number. They integrated moments inside a 10%-of-peak contour and sampled developed rings several diameters downstream. The candidate’s ratios are 0.448 and 1.20 respectively, and its width is a Gaussian e-folding radius. Their data support the speed range while demonstrating how a change of nozzle speed can alter core width. Reprocess measured sections and the model with the same aperture and spatial filter. Do not substitute their calibration for this nozzle. Schatzle’s submerged oblique collisions at ReΓ ≈ 1800 establish a realizable encounter geometry and report circulation loss and core splitting. Extrapolation to ReΓ ≈ 3588 leaves the lifetime of a smooth core uncertain. [Single-ring measurements, §3 and figure 4](https://doi.org/10.1017/jfm.2025.1099) · [Oblique water-ring experiment](https://thesis.caltech.edu/1471/)

**Placement and timing.** The candidate ring centers are (±16.9904,0,0) mm, normals (∓0.5,0,0.8660), facing points (±4,0,−7.5) mm. Place lip centers at the target centers minus the measured flight distance ℓ along each normal. For example ℓ = 30 mm gives lip centers separated by 63.98 mm, 25.98 mm upstream vertically. This is an adjustable starting placement. Measure center trajectories from the lip, roll-up distance, end-of-stroke time, wake velocity and actual detachment for each nozzle alone. Place and trigger the pair so the target geometry occurs at the same measured post-detachment age. Repeat with both nozzles operating because mutual induction acts during preparation too.

At 0.0646 m/s isolated translation a 30 mm flight scale is 0.46 s. As a diffusion check a detached 1.5 mm straight Gaussian takes (2²−1.5²)/(4ν) ≈ 0.44 s to reach 2 mm, with lengths in consistent units. An already 2 mm core released far upstream would broaden further during the flight. Roll-up and strain change this estimate. A 10 ms trigger mismatch corresponds to about 0.65 mm axial displacement in isolated flight, or 0.32 mm transverse and 0.56 mm vertical for one ring. A simultaneous 10 ms age error at the candidate's initial closure speed changes the gap by about 0.45 mm. Use synchronized trigger and volumetric PIV with a common clock, target a few milliseconds repeatability, then measure actual centerlines, directions and closest distance in 3D. Asymmetric age errors cannot in general be represented by a symmetric gap change.

Record the velocity waveform and pressure work at the exits. Measure the two principal widths, sectional circulation (flux and line integral), axial core flow, radius, trajectory, wakes, wall distances and background strain over repeated single releases. Use stationary tank boundaries after release. Compare pair and single prehistories and quantify run-to-run distributions. A practical first target for velocity-field spatial resolution is ≤0.25 mm across a 2 mm e-folding radius, with acquisition intervals ≤1 ms where gradients change rapidly. Validate the *effective* PIV window and noise by filtering synthetic fields and by varying window size. The nominal +0.142 s⁻¹ peak tendency would amount to only ~0.28% over 20 ms if maintained. Determine uncertainty on that change and use the stronger shoulder signal and isolated controls if peak changes cannot be resolved.

## Motion, pressure and available energy

The kinematic flight estimates use the instantaneous fluid velocity on the geometric centerline as a proxy for the detached core’s propagation. A measured ridge can move relative to that fluid. The candidate's isolated centerline speed is 0.06458 m/s. Isolated straight flight gives 0.124 s to close the initial gap. The actual initial facing velocities give a relative approach of 0.04466 m/s and a local linear extrapolation of 0.179 s. These are two scales, not bounds. At original circulation the 8 mm pair gives 0.248 and 0.358 s, while the original gap gives 0.372 and 0.465 s. The ring-shape and velocity fields evolve during approach. An inviscid filament calculation could refine arrival geometry until core separation is only a few widths. Its core prescription controls the velocity at close range, and it cannot determine viscous cancellation, compressible pressure, reconnection or either physical core width.

Peak straight-core swirl is 0.1828 m/s, Mach 1.23 × 10⁻⁴. Its axis deficit is about 56.8 Pa, compared with about 99 kPa from ambient pressure to saturation at 20 °C. Differences of millimeters in measurement depth matter at this pressure scale. Use a common hydrostatic datum. The corresponding density perturbation scale Δp/c² ≈ 2.6 × 10⁻⁵ kg/m³. The original circulation at the same width gives 0.0914 m/s and 14.2 Pa. Compute interacting pressure from the full velocity field for evolution.

The constant-speed slug kinetic energy is 0.254 mJ per nozzle. The prescribed candidate has free-space kinetic energy 0.198 mJ per isolated ring, a mutual term of −0.0207 mJ, and **0.375 mJ for the pair**. In the uniform-density release model integrate ½ρ∫A·ω dV using the vector potential of a closed loop. Convolving both line distributions yields the scalar factor erf(r/(√2a))/r multiplying dl·dl′ in the double line integral with prefactor ρΓ²/(8π). Its coincident limit is √(2/π)/a. The two source refinements agree to the precision shown. Original-gap pair energy is 0.0955 mJ. The candidate's model inventory is about 74% of the two ideal slugs’ kinetic energy. This demands appreciable transfer but reveals no simple energetic impossibility. Actual pressure work, residual jet energy, entrainment and viscous losses determine the transfer. [Energy, speed and formation-scale calculations](ring-experiment/preparation.csv) · [Calculation source](../../physics_first/ring_preparation.py)

## Which signs survive preparation errors?

Change one quantity at a time, holding the facing gap fixed when changing tilt by translating the centers. Tilt in the table is per ring from vertical. Compare the geometric facing center, the local maximum of |ω| in its section, and two points half a core radius inward/outward on its radial diameter. All entries are fractional material rates, s⁻¹.

| Change from candidate | Center | Section peak | Inward 0.5a | Outward 0.5a |
|---|---:|---:|---:|---:|
| Nominal |+0.145|+0.142|+0.316|+0.441|
| Γ −10% |+0.030|+0.027|+0.208|+0.322|
| Γ +10% |+0.260|+0.256|+0.423|+0.561|
| a = 1.8 mm |−0.090|−0.093|+0.148|+0.263|
| a = 2.2 mm |+0.319|+0.315|+0.437|+0.573|
| Gap 7 mm |+0.429|+0.424|+0.574|+0.726|
| Gap 9 mm |−0.066|−0.069|+0.122|+0.225|
| Tilt 25° |−0.053|−0.056|+0.124|+0.246|
| Tilt 35° |+0.346|+0.343|+0.516|+0.635|

The strong radial shoulders preserve positive growth in every trial while their isolated counterparts diffuse there. Facing-peak growth is sensitive to errors in width, gap and angle. The thinnest, fastest cases in the threshold table demand the largest nozzle speeds and have the greatest unresolved laminarity/formation uncertainty. The broadest case at 8 mm has appreciable overlap. Neither motivates replacing the nominal comparison. The trials bound individual changes only. A faster nozzle producing a thinner core, or unequal circulation and age in the two rings, could erase the nominal peak signal. Recalculate the release budget on measured fields before attributing a tank result to this state. [All sensitivity results, including peak location and number of positive azimuths](ring-experiment/sensitivity.csv)

**Decision A, conditional on release characterization.** The physically moderate candidate has partner-induced material growth in the strongly vortical interior and an informative isolated control. That justifies a short simulation that can also falsify core thinning. Peak growth is too sensitive to use as the sole experimental target. [First time-dependent test and solver qualifications](RING_EVOLUTION_DESIGN.md)

Reproduce the mechanical estimates using `python -m physics_first.ring_preparation OUTPUT_DIR`. SI units are encoded in the CSV headings except for dimensionless Reynolds/Mach numbers, source count n and Γ in m²/s.
