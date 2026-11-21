# Reproduce the R294 two-dimensional water benchmark

Run at the repository root. On WSL2 daisy the existing water environment supplies Python 3.12.14, NumPy 2.5.5 and CoolProp 7.2.0. All stored fields are binary64. The independent inventory accumulation uses x86 NumPy long double. The plotter uses system Python with Matplotlib. [Equations, comparisons and decision](../VISCOUS_WATER_2D.md)

```bash
set -eu
wp="$HOME/.local/opt/water-acoustics/tools/bin/python"
export OPENBLAS_NUM_THREADS=1
ev=docs/physics-first/r294
out=$(mktemp -d)
"$wp" -m unittest -v tests.test_liquid_imex_2d tests.test_water_shear tests.test_liquid_imex tests.test_water_acoustics
/usr/bin/time -v -o "$out/pilot_resources.txt" "$wp" -m physics_first.liquid_shear "$out" --pilot
/usr/bin/time -v -o "$out/matrix_resources.txt" "$wp" -m physics_first.liquid_shear "$out"
for f in pilot.json pilot.npz matrix.json matrix.npz pressure_modes.json refinement.json; do
    cmp "$out/$f" "$ev/$f"
done
MPLBACKEND=Agg python3 -m physics_first.plot_liquid_shear "$out" "$out/shear.png"
cmp "$out/shear.png" "$ev/shear.png"
```

The 32 × 4 pilot covers the complete physical interval in 256 steps and must pass before the matrix runs. The 12 principal integrations cover two phases × three grids × two step sizes. Five additional runs cover 64 × 8 transverse resolution, two tighter 64 × 4 pressure solves, and 512/1,024 steps at 32 × 4 for temporal order with the pilot. Case keys give Nx × Ny, total steps, phase (0 original, 1 shifted by +λ/4) and pressure tolerance in Pa. The driver writes the results of each completed case and exits nonzero on a failed gate. [Driver](../../../physics_first/liquid_shear.py) · [Flux and pressure operators](../../../physics_first/liquid_imex_2d.py)

- [Pilot fields](pilot.npz) and [matrix fields](matrix.npz) have shape (5, 6, Ny, Nx) per case. Axis 0 denotes 0, 2, 4, 6, 8 acoustic crossings. Axis 1 contains r (kg/m³), positive-x face momentum and positive-y face momentum (kg/m²/s), H (J/m³), implicit perturbation pressure and independent incremental perturbation pressure (Pa). The last two axes contain only independent periodic samples.
- [Pilot measurements](pilot.json) and [matrix measurements](matrix.json) give Fourier phase in radians relative to x = 0, amplitude, interval/whole-run viscosity and independent kinetic fits, per-column y ranges, temperature and pressure perturbations, longitudinal speed, integrated heating and precision. Interval rates end at the indexed checkpoint. Inventory changes, measured absolute cell defects, precision allowances, stress work, pressure dilatation, peak nonlinear residual and iteration counts are cumulative from release. Four-component inventories have units kg/m, kg/s, kg/s, J/m. Aligned maxima cover both pressure readers at each checkpoint. Use `np.ptp(fields[:,5], axis=1)` on one case array to recompute the independently recovered range at each x and saved time.
- [Pressure stress tests](pressure_modes.json) contain signed pressure and vector momentum projections for 16 steps each, with physical transport and inviscid controls for three Nyquist modes. [Refinement ratios](refinement.json) use fitted viscosity on independently varied grids and steps. [Independent tests](../../../tests/test_liquid_imex_2d.py) check both momentum and work fluxes on nonsymmetric data, the pressure adjoint, translating and zero-viscosity fixed points, and archived Fourier modes against the discrete diffusion amplification factor.
- GNU time measured **1.02 s, 122236 KiB peak RSS** for the final pilot and **85.67 s, 122664 KiB peak RSS** for the 17-case matrix including pressure-mode checks, checkpoint recovery and archive writing. Both reported zero swaps. The first pilot invocation encountered a NumPy-boolean JSON serialization error after the pressure-mode tests, before shear integration. Converting the gate to a native boolean resolved the output error. The initial completed pilot took 0.92 s, 122588 KiB, before per-column range output was added. [Pilot log](pilot_resources.txt) · [Matrix log](matrix_resources.txt) · [Initial writer error timing](pilot_writer_error_resources.txt)

The R284–R286 readers regenerate the previous measurements directly from SU2 archives. R284 and R286 return scientific exit 1. The historical R293 driver regenerates its 36 resolved cases and controls, iteration budgets and field archive. [R284 replay](../SHEAR_DECAY.md#reproduction) · [R285 replay](../SHEAR_TRANSLATION.md#reproduce-without-running-cfd) · [R286 replay](../SHEAR_QUALIFICATION.md#reproduce-the-qualification-without-running-cfd) · [R293 replay](../r293/REPLAY.md)
