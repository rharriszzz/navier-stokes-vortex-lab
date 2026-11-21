# A 10 Pa wave in liquid water

**The installed solver passed the pressure propagation test.** After one trip around a 0.10 m periodic line, the 128-cell, 512-step calculation returned **9.99980 Pa** amplitude and **1481.79 m/s** phase speed. The independently evaluated water EOS gives **1482.35 m/s**, or **67.4606 μs** per trip. This establishes that the solver can carry a disturbance comparable in size to the 12.49 Pa inner pressure difference in the earlier vortex. Slow vortical evolution and viscous heating still need their own checks. [Spreading reference](SPREADING_RESULT.md) · [Acoustic specification](README.md#physical-test-after-the-reference)

## Measured results

| Axial cells | Physical steps per period | Acoustic CFL | Measured speed (m/s) | Speed error (%) | Final amplitude (Pa) | Amplitude error (%) |
|---:|---:|---:|---:|---:|---:|---:|
| 32 | 256 | 0.125 | 1472.99 | −0.6315 | 9.98547 | −0.1453 |
| 32 | 512 | 0.0625 | 1472.88 | −0.6388 | 9.98540 | −0.1460 |
| 64 | 256 | 0.250 | 1480.11 | −0.1506 | 9.99837 | −0.0163 |
| 64 | 512 | 0.125 | 1480.00 | −0.1581 | 9.99827 | −0.0173 |
| 128 | 256 | 0.500 | 1481.90 | −0.0301 | 9.99990 | −0.0010 |
| 128 | 512 | 0.250 | 1481.79 | −0.0376 | 9.99980 | −0.0020 |

At fixed 512 steps, doubling the number of cells reduced speed error about fourfold each time. At 128 cells, halving the physical time step changed the measured speed by 0.11 m/s. Both of the finest grids passed at both step sizes against the saved limits of 1% speed error and less than 2% amplitude error. This sinusoid moved to the right. We followed the phase of its first Fourier mode at each quarter period and unwrapped it before calculating the speed. An endpoint-only comparison would miss a whole-cycle phase error. The pressure amplitude comes from the same mode, independent of where its crest falls between nodes. [Six runs and signed budgets](acoustic_results.json) · [Measurement code](../../physics_first/measure_acoustic.py)

## Physical and numerical setup

The single-phase IAPWS-95 Helmholtz water EOS at 293.15 K and 101325 Pa gives density 998.20715 kg/m³. Initial pressure is p₀ + 10 sin(kx + φ) Pa, k = 2π/0.10 m. Entropy is uniform and axial velocity is (p−p₀)/(ρ₀c₀), with amplitude only 6.758 μm/s. The half-cell phase offset φ = π/N avoids putting the same extremum on a node at every resolution. Each initial state is obtained from (p,s₀), refined once using (∂s/∂T)ₚ = cₚ/T, and encoded as (ρ, ρu, ρv, ρE). The correction reduces sensitivity to inversion tolerance at this small amplitude. The Python initializer and C++ solver use the same CoolProp revision. At the finest endpoint ρ ranged from 998.20714592 to 998.20715502 kg/m³ and T varied by about ±0.145 μK. This is chiefly reversible acoustic compression and expansion. [EOS code](../../physics_first/acoustic_initial_state.py) · [CoolProp water formulation](https://coolprop.org/fluid_properties/fluids/Water.html) · [IAPWS-95](https://iapws.org/technical-guidance/release/IAPWS-95)

SU2 8.6.0 advances laminar compressible Navier–Stokes with total energy, constant shear viscosity 1.001596 mPa s and conductivity 0.598012 W/(m K). We use its ordinary viscous stress without an added bulk-viscosity term. The two-dimensional strip has two cells across its 0.01 m height, identical initial states across the strip, axial periodicity and insulating symmetry boundaries across the height. There is no forcing, pump or boundary work. The restarts supply the initial state at every vertex. We integrated with the centered JST flux and two-stage explicit midpoint time stepping, storing the conservative state and residual every physical step. Pressure and temperature were recovered from each measured endpoint's conservative state. This explicit acoustic configuration resolves sound on purpose. A five-second vortex calculation would require a separate slow-time integration decision. [Case generator](../../physics_first/su2_acoustic.py)

## What the budgets resolve

Per unit cross-sectional area, the box contains about 99.82 kg/m² of water. We compared storage changes with the signed time integral of SU2's assembled face-flux residuals. The second midpoint stage has weight one in the final update relative to the beginning of the step. We checked that the reported nodal residual actually predicts that update. Duplicate end nodes count as half a node when integrating periodic residuals, and the physical inventories use the dual volumes. We retained both momentum components, the signed net residual, and the independently differenced inventories for each quarter period. The largest mass defect was 8.72×10⁻¹⁷ of inventory. The largest vector momentum defect was 9.17×10⁻¹⁷ of mass times acoustic velocity amplitude. Both meet the saved tolerances. [SU2 explicit update](https://github.com/su2code/SU2/blob/7048fd35f56d4bf52e586429d6746a36a10255f8/SU2_CFD/include/solvers/CFVMFlowSolverBase.hpp) · [SU2 residual outputs](https://github.com/su2code/SU2/blob/7048fd35f56d4bf52e586429d6746a36a10255f8/SU2_CFD/src/output/CFlowCompOutput.cpp)

**Total energy has a precision limit at 10 Pa.** The expected mean acoustic energy density is A²/(2ρ₀c₀²) = 2.28×10⁻⁸ J/m³. The spacing between adjacent double-precision values of the background total-energy density is 1.49×10⁻⁸ J/m³. The maximum local difference between the stored energy update and the signed residual prediction was 7.46×10⁻⁹ J/m³, about half that spacing. We subtracted e₀ times the mass balance and accumulated the signed differences in extended precision. This can reduce postprocessing cancellation, but it cannot restore precision lost when the solver stored ρE.

Across all six settings, the largest quarter-period shifted energy defect was 1.22×10⁻⁹ J/m², about 53.5% of the initial acoustic energy per area. At 128 cells and 512 steps the largest quarter-period defect was 45.4%. The pressure/velocity wave-energy diagnostic on that run fell by about 0.0039% over the full trip. The two quantities measure different things. The total-energy difference cannot resolve that small loss or establish a heating rate. No angle or vortex core exists in this longitudinal control.

## Installation and reproducibility

The standard WSL path, local software and package directories, and standard mounted Windows installation directories showed no usable SU2 or Fluent installation. Windows executable lookup from this WSL session returned an executable-format error. The official SU2 Linux OpenMP release matched the periodic mesh and then explicitly refused the CoolProp fluid model. With the owner's installation authorization, we built the tagged SU2 CFD executable with CoolProp enabled. The build was user-local, serial at runtime, with no changes to the project's virtual environment, system packages or historical FEM environment. [SU2 nonideal-flow setup](https://su2code.github.io/docs_v7/Setup-Guide-NICFD/) · [Tagged release](https://github.com/su2code/SU2/releases/tag/v8.6.0)

On daisy, `su2-water --help` finds the installed solver. The binary, source, tool environment, build logs and seven raw case directories (six settings plus a repeat) are under `~/.local/opt/water-acoustics/`, alongside the stock-binary probe. The build uses tag `v8.6.0` at `7048fd35` and its pinned CoolProp 7.2.0 at `98b3523d`. The executable SHA-256 is recorded in the JSON. Use the dedicated interpreter under `tools/bin/python`. [Installation recipe](SU2_WATER_SETUP.md)

From the repository root, the following reproduces the 128-cell case in a fresh directory:

```bash
water_python="$HOME/.local/opt/water-acoustics/tools/bin/python"
"$water_python" -m physics_first.su2_acoustic ./wave-128 128 512
(cd ./wave-128 && su2-water wave.cfg > solver.log)
"$water_python" -m physics_first.measure_acoustic ./wave-128 128 512
```

The generated inputs and final binary restart reproduced byte-for-byte on daisy. The unit tests also compare sound speed with an independent isentropic density secant and check the periodic input, phase, amplitude and energy units.

**Next proposed decision.** Repeat only the 128-cell, 512-step acoustic case at 100 Pa, keeping the background, transport, method and conservation accounting fixed. Linear wave energy grows by a factor of 100. Compare absolute and wave-normalized energy defects against this saved 10 Pa run. This single control can distinguish a precision floor from a defect that grows with wave energy, before investing in thermal claims or a compressible vortex simulation.
