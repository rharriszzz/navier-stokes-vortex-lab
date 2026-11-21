# Energy precision in a 100 Pa liquid-water wave

Increasing the pressure amplitude tenfold increased the initial wave energy one hundredfold. The largest absolute quarter-period energy discrepancy fell from 1.04 to 0.639 nJ/m². Its fraction of initial wave energy fell from 45.4% to 0.280%. This pair supports a storage-precision explanation for the large relative discrepancy at 10 Pa. It establishes neither a universal error floor nor a heating rate. [10 Pa experiment and budget definition](ACOUSTIC_RESULT.md) · [100 Pa signed budgets and snapshots](acoustic_100pa.json)

| Measured over one trip | 10 Pa | 100 Pa |
|---|---:|---:|
| Final pressure amplitude (Pa) | 9.99980 | 99.99804 |
| Phase speed (m/s), EOS prediction 1482.346 | 1481.78811 | 1481.78810 |
| Initial acoustic energy per area (nJ/m²) | 2.27955 | 227.9555 |
| Largest absolute quarter-period total-energy defect (nJ/m²) | 1.03517 | 0.63935 |
| Same defect / initial acoustic energy (%) | 45.411 | 0.28047 |
| Change in pressure/velocity wave energy over one trip (%) | −0.003926 | −0.003923 |
| Largest mass defect / initial reference mass | 1.58×10⁻¹⁷ | 6.58×10⁻¹⁷ |
| Largest momentum defect / (reference mass × wave velocity amplitude) | 4.25×10⁻¹⁷ | 5.54×10⁻¹⁷ |

**What changed.** The initial pressure perturbation went from 10 to 100 Pa peak and the corresponding axial velocity from 6.76 to 67.6 μm/s. The liquid EOS supplied density and internal energy at uniform initial entropy. The initial conserved state and SU2 reference Mach number changed accordingly. The mesh was byte-identical, and every other solver configuration line matched. Both cases used the same SU2 binary and CoolProp water at 293.15 K and 101325 Pa, the same viscous and thermal properties, periodic 0.10 m length, symmetry sides, and zero external work. We ran just the 128-cell, 512-step case for one period (67.46 μs). The earlier six runs establish the grid and time-step sensitivity at 10 Pa. This control isolates amplitude at one resolution. [Setup and earlier refinement](ACOUSTIC_RESULT.md#physical-and-numerical-setup)

**Where the discrepancy occurs.** In the four successive quarter periods, the signed total-energy defects per area were +1.035, −0.323, +0.030 and −0.091 nJ/m² at 10 Pa. At 100 Pa they were +0.494, −0.141, −0.639 and −0.436 nJ/m². Each includes the storage change and integrated outward flux, after subtracting the background specific internal energy times the mass balance. At each amplitude the largest local energy-update discrepancy was 7.45×10⁻⁹ J/m³, half the spacing of the stored background energy density. Signs and magnitudes can vary when many rounded updates are summed. Two amplitudes distinguish the observed scaling from growth proportional to wave energy in this comparison.

**What the water did.** Both amplitudes propagated within 0.038% of the EOS speed. The 100 Pa endpoint temperature oscillation was ±1.45 μK, consistent with the tenfold larger reversible compression and expansion. The wave-energy diagnostic uses pressure and velocity and measures all attenuation of the resolved wave, including numerical effects. At 100 Pa it lost 0.00894 nJ/m² over the trip. Even the magnitude of the signed full-trip total-energy defect, 0.723 nJ/m², was about 81 times that loss. The total-energy balance cannot tell how much of that loss became heat. This experiment measured sound propagation in initially quiescent water; sustaining or concentrating a vortex remains an open problem.

**Reproduction.** Use the [installed solver and dedicated interpreter](SU2_WATER_SETUP.md) in a fresh case directory. The analysis checks the specified amplitude against the initial velocity. The default remains 10 Pa for historical cases. On daisy the raw 100 Pa restarts are under `~/.local/opt/water-acoustics/runs/r281-100pa-n128-t512/`. The JSON records checksums for the solver, mesh, config and initial/final state. The matched 10 Pa result is the 128-cell, 512-step entry in the [original evidence](acoustic_results.json).

```bash
water_python="$HOME/.local/opt/water-acoustics/tools/bin/python"
"$water_python" -m physics_first.su2_acoustic ./wave-100pa 128 512 --amplitude-pa 100
(cd ./wave-100pa && su2-water wave.cfg > solver.log)
"$water_python" -m physics_first.measure_acoustic ./wave-100pa 128 512 --amplitude-pa 100
```

**Next decision.** Return to the vortex at time zero. Construct the radial pressure, density and energy that balance the saved 10 mm swirl at 20°C with 101325 Pa at the finite wall. Compare the axis-to-30 mm pressure rise with the incompressible reference (15.902 Pa). Check radial refinement and the centrifugal force balance after recovering pressure from the stored conservative state. A small imbalance here can launch sound that would be mistaken for vortex evolution. Stop with the initialization check before time integration. [Finite-cylinder benchmark](SPREADING_RESULT.md)
