# R286 · Removing fourth-order JST dissipation in liquid water

**The original 64-cell periodic-seam defect is corrected to the prescribed tolerance. The full refinement qualification fails.** With the same mesh, initial states, physical properties and time step, disabling the fourth-order JST term reduced the two phases' worst cross-strip pressure ranges from 23.954 and 5.123 Pa to 0.000643 and 0.000570 Pa. On the 128-cell grid at that time step, short pressure waves grew in both phases. The measured shear damping still converged at approximately second order. A viscosity fit alone would have given the wrong solver decision. [Earlier failed shear test](SHEAR_DECAY.md) · [R285 stencil diagnosis and prospective gates](SHEAR_TRANSLATION.md)

## The two-phase test

We used the archived 10 µm shear wave and its quarter-wavelength translation, eight acoustic crossings, and the installed SU2 8.6.0/CoolProp 7.2.0 executable. The sole configuration change was `JST_SENSOR_COEFF= (0.5, 0.0)`. Both solver logs confirm it. Every pair passed the mesh/periodic donor audit and exact inverse translation of all four initial conservative fields. All runs use four transverse cells. Refinement here is in the direction of variation of the exact solution.

The table uses independent liquid-EOS pressure recovery. Range is max over x of (max over y − min over y). Aligned error is max |Δp| over all independent vertices after undoing the translation. Column i is measured from the seam, in each phase's own mesh coordinates. Both pressure limits are 0.001 Pa at **each** saved endpoint.

| Crossings | Original range (Pa), column i | Shifted range (Pa), column i | Aligned error (Pa) |
|---:|---:|---:|---:|
| 2 | 0.000493, 39 | 0.000411, 23 | 0.000464 |
| 4 | 0.000500, 13 | 0.000558, 34 | 0.000516 |
| 6 | 0.000643, 54 | 0.000463, 0 | 0.000548 |
| 8 | 0.000592, 0 | 0.000570, 43 | 0.000535 |

At eight crossings the global pressure minimum/maximum were at (row, column) (3,49)/(2,31) originally and (3,45)/(1,62) after translation. The peak no longer follows the R285 seam pattern. The viscosity fits from the five Fourier amplitudes were 1.002589571 and 1.002589567 × 10⁻⁶ m²/s, each 0.08028% below physical. Phase sensitivity was 0.000000432% of physical ν, down from 10.91%. The four interval fits spanned less than 0.000005% in each phase. The kinetic-energy fits agree to the displayed viscosity precision.

The final assembled momentum residual RMS (longitudinal, transverse) was (3.46 × 10⁻¹¹, 1.34 × 10⁻⁷) N/m originally and (3.36 × 10⁻¹¹, 1.34 × 10⁻⁷) N/m after translation. Their aligned differences were (4.68, 2.38) × 10⁻¹¹ N/m. The transverse residual includes the physical shear decay. Projecting the last-stage residuals gave ν between 1.00259479 and 1.00259483 × 10⁻⁶ m²/s. These residuals are sampled instantaneous rates. Their small differences and the phase agreement identify the removed term as responsible for the large original error in this test, without decomposing each flux contribution.

## Refinement and timestep control

After the 64-cell screen passed, we compared 32, 64 and 128 cells at 2048 steps and halved the step separately at 64 cells. Both 128-cell pressure ranges exceeded the original gate at the full step. We used one final time-step control on that grid, again in both phases with the same gates. Axial acoustic CFL = cΔt/Δx. The entries below are maxima across all four evolved outputs, including both phases in the aligned comparison.

| Cells / steps | CFL | ν error, original / shifted (%) | Peak cross-strip range, original / shifted (Pa) | Aligned max (Pa) | Pressure gates |
|---|---:|---:|---:|---:|---|
| 32 / 2048 | 0.125 | −0.32084 / −0.32084 | 0.000639 / 0.000626 | 0.000564 | pass |
| 64 / 2048 | 0.25 | −0.08028 / −0.08028 | 0.000643 / 0.000570 | 0.000548 | pass |
| 128 / 2048 | 0.50 | −0.01998 / −0.01996 | **0.040525 / 0.070898** | **0.048942** | **fail** |
| 64 / 4096 | 0.125 | −0.08028 / −0.08028 | 0.000409 / 0.000525 | 0.000404 | pass |
| 128 / 4096 | 0.25 | −0.02007 / −0.02007 | 0.000542 / 0.000591 | 0.000512 | pass |

In both phases, the 32→64 and 64→128 fixed-step changes in viscosity are about 0.241% and 0.0603% of physical ν. The error drops by a factor of four at each doubling. The three-point centered diffusion operator applied to a sine predicts ν_eff/ν = [sin(π/N)/(π/N)]², giving biases of −0.321%, −0.0803% and −0.0201%. This independent calculation explains the scale and sign of the remaining damping bias. All individual viscosity errors meet 10%, and all interval spreads, phase changes, grid changes and step changes meet their separate <5%-of-material-ν limits. [Fits, pressure extrema, residuals and gates by endpoint](shear_qualification.json)

**Pressure fails for a different reason.** At 128 cells / 2048 steps, the shifted range rose through 0.00143, 0.00515, 0.01932 and 0.07090 Pa. The final extrema were at (3,7) and (3,9), with peak range at column 7. The original peak range was at column 81. After removing the y-mean at each x, the strongest axial Fourier modes across the four outputs were 26–28 cycles per box in the original phase and 27–28 after translation. That is roughly 4.6–4.9 cells per cycle. The largest per-line odd–even pressure amplitude reached 0.00150 Pa across these two runs, versus 0.000159 Pa in the 64-cell screen. A pure axial checkerboard would have mode 64. The spectrum and four endpoint values show short-wave amplification, beyond the approximately 0.00025 Pa discrepancy between SU2's primitive pressure and EOS recovery.

Halving Δt on the same 128-cell mesh restored both pressure gates, with a viscosity change of at most 0.000109% of physical ν. SU2’s stored primitive pressure gives the same pass/fail decisions. The failure therefore depends on the space–time combination. For a centered, undamped acoustic eigenmode with eigenvalue iω, the two-stage RK update has squared amplification |1 + iη − η²/2|² = 1 + η⁴/4, η = ωΔt. This makes amplification of weakly damped short waves plausible at larger CFL. The coupled viscous-EOS operator and finite restart precision also matter. These measurements do not uniquely identify the unstable eigenmode or establish long-time stability.

All stored conservative and primitive fields were finite and all recovered conservative states were liquid. Across ten cases the largest absolute changes in mean density, x/y momentum density and total energy density were 3.06 × 10⁻¹³ kg/m³, 3.99/2.23 × 10⁻¹⁵ kg/(m² s) and 2.19 × 10⁻⁸ J/m³. We differenced nodal values before accumulating dual-volume means. Conservation of averages is compatible with large local errors of opposite sign. The four saved times after release bound what we observed and leave excursions between outputs unmeasured.

## Solver decision

Retain SU2/CoolProp as a short-time reference for acoustics and shear. **Withhold qualification for a rotating physical vortex.** The passed low-CFL pairs support a future short rotating-balance *qualification* at a controlled step. The time-step control quantifies one limitation of the explicit centered scheme. R283's finest recovered radial-force refinement still failed, the discrete rotating momentum balance remains unmeasured, and slow physical evolution needs time integration on the vortex timescale. A successful short shear test cannot resolve those questions. [R283 radial equilibrium and explicit cost](VORTEX_EQUILIBRIUM.md)

The exact installed SU2 revision rejects `JST_MAT`, `LMROE`, `L2ROE`, Turkel and AUSM-family choices for nonideal compressible water. Its configuration check admits JST, Roe and HLLC. The driver constructs **general-EOS** Roe/HLLC operators for the latter two. The separate `LOW_MACH_CORR` acts in the upwind reconstruction path with thermodynamics recovered from pressure and density. It is rejected in the centered vectorized path used by JST. We checked these source paths and the water EOS (ρ,p) inversion at the reference state. Neither alternative upwind operator has passed these wave tests. Enabling a named option or switching to SU2's incompressible equations supplies no evidence of accurate compressible liquid-water vortex dynamics. [Installed configuration guard](https://github.com/su2code/SU2/blob/7048fd35f56d4bf52e586429d6746a36a10255f8/Common/src/CConfig.cpp#L4582-L4586) · [Roe/HLLC dispatch](https://github.com/su2code/SU2/blob/7048fd35f56d4bf52e586429d6746a36a10255f8/SU2_CFD/src/drivers/CDriver.cpp#L1671-L1756) · [Reconstruction](https://github.com/su2code/SU2/blob/7048fd35f56d4bf52e586429d6746a36a10255f8/SU2_CFD/src/solvers/CEulerSolver.cpp#L1950-L1962) · [Vectorization restriction](https://github.com/su2code/SU2/blob/7048fd35f56d4bf52e586429d6746a36a10255f8/SU2_CFD/src/solvers/CEulerSolver.cpp#L371-L383)

For the eventual compressible simulation, select a conservative all-speed, pressure–velocity coupled method with an acoustic-implicit physical step, true water EOS and resolved viscous work and heat conduction. A concrete discretization reference is the momentum-weighted face interpolation and coupled pressure, velocity and temperature formulation of Denner, Evrard and van Wachem. Their published real-fluid tests used a Noble–Abel stiffened-gas EOS. An implementation with IAPWS water still owes the acoustic, shear and radial tests before use. This is a method choice for a later physical calculation. The [next ring-strain experiment](INTERACTING_VORTICES.md#validation-before-evolving-the-pair) can use just geometry, circulation, physical viscosity and quadrature. [Primary all-speed method paper](https://arxiv.org/abs/2002.10482)

## Reproduce the qualification without running CFD

The [raw archive](shear_qualification_runs.tar.gz) contains the ten actual configs, meshes, initial restarts, four evolved restarts per case, step histories and solver logs. On daisy the binary SHA-256 was `0941113d648fbd79bd745ef68f050f982225c479e3ca0f59ad28d582c28d84aa`. Use the pinned [water environment](SU2_WATER_SETUP.md). The full measurement exits **1** for the failed pressure gates.

```bash
water_python="$HOME/.local/opt/water-acoustics/tools/bin/python"
report=docs/physics-first
work=$(mktemp -d)
tar -xzf "$report/shear_qualification_runs.tar.gz" -C "$work"
"$water_python" -m physics_first.shear_qualification screen "$work" > "$work/screen.json"
status=0
"$water_python" -m physics_first.shear_qualification qualify "$work" > "$work/result.json" || status=$?
test "$status" -eq 1 && cmp "$work/result.json" "$report/shear_qualification.json"
"$water_python" -m unittest -v tests.test_water_shear tests.test_water_acoustics
```

**Checkpoint provenance.** The translated 128/4096 process returned 143 after recording 3948 iterations, without its final restart. The cause of termination is unknown. We retained that log and history, resumed the same physical case from saved step 3072, and changed only the restart index. All 876 overlapping iteration and printed residual rows agree exactly. The resumed clock starts at zero at the checkpoint. The reader checks the two clocks, overlapping rows, matching mesh, checkpoint and final state. The final measurement for this phase uses the continued segment. Both histories and configs are in the archive.

The input generator's `prepare-screen`, `prepare-refinement` and `prepare-step-control` commands accept a fresh common directory. The run command in each generated case is `su2-water wave.cfg > solver.log 2>&1`. The archived R284 and R285 measurements reproduce with their historical settings. No rotating flow was advanced in R286.
