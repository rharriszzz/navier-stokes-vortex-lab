# Replaying the R293 liquid-water acoustics experiment

Run from the repository root on daisy. The existing water interpreter is Python 3.12.14 with NumPy 2.5.5 and CoolProp 7.2.0, revision 98b3523d. NumPy long double on this x86 host has 63 explicit mantissa bits for inventory accumulation. All evolved fields are binary64. The production and decimal audit require no SciPy or new solver. The plot uses system Python with Matplotlib 3.10.7. [Scientific report, equations and gates](../LIQUID_IMEX.md)

```bash
wp="$HOME/.local/opt/water-acoustics/tools/bin/python"
ev=docs/physics-first/r293
out=$(mktemp -d)
export OPENBLAS_NUM_THREADS=1
"$wp" -m unittest -v tests.test_liquid_imex tests.test_water_acoustics
"$wp" -m physics_first.liquid_imex_benchmark "$ev" --replay
"$wp" -m physics_first.liquid_imex_benchmark "$out"
cmp "$out/fields.npz" "$ev/fields.npz"
cmp "$out/solves.json" "$ev/solves.json"
cmp "$out/results.json" "$ev/results.json"
"$wp" -m physics_first.liquid_helmholtz_check > "$out/decimal.json"
cmp "$out/decimal.json" "$ev/decimal.json"
MPLBACKEND=Agg python3 -m physics_first.plot_liquid_imex "$out" "$out/acoustics.png"
cmp "$out/acoustics.png" "$ev/acoustics.png"
```

The benchmark driver defines the complete input matrix. Domain length, reference pressure and temperature come from the original acoustic initializer. The archived matrix contains all 36 resolved runs (two amplitudes × two directions × three cell counts × three physical step counts). The resolved checks cover both pressure readers, phase and amplitude, independent refinement, conservative budgets and solver residuals. A failed gate returns exit 1 and skips the large-step controls. The five controls are two under-resolved step sizes, their two inviscid damping controls and one tenfold tighter resolved solve. Archive keys encode cells, steps per crossing, amplitude, direction, pressure tolerance in Pa and optional zero-transport flag. [Benchmark driver](../../../physics_first/liquid_imex_benchmark.py) · [Solver](../../../physics_first/liquid_imex.py)

- [fields.npz](fields.npz) contains five snapshots per case at 0, ¼, ½, ¾ and one acoustic period. Each array has shape (5, 4, N). Channels are ρ−ρ₀ in kg/m³, ρu in kg/(m² s), ρ(E−e₀) in J/m³, and π in Pa. Positions are (i+½)L/N.
- [solves.json](solves.json) gives maximum local nonlinear/linear pressure residuals in Pa, maximum number of corrections and peak absolute perturbation over evolved steps. The three-component arrays sum measured absolute cell defects or roundoff allowances over the trip, in kg/m², kg/(m s), J/m².
- [results.json](results.json) gives all checkpoint measurements, gates, refinement orders and the amplitude sweep. Each checkpoint inventory change is relative to the immediately preceding checkpoint. All energies per area use unit cross section. Recovered and raw pressure modes store the real and imaginary parts of twice the normalized first Fourier coefficient. Relative speed and amplitude errors are fractions. Replay remeasures the raw fields and combines them with the archived iteration/flux diagnostics. Full regeneration also recomputes those diagnostics.
- [decimal.json](decimal.json) contains separate positive and negative cell inversions for four probe amplitudes. [acoustics.png](acoustics.png) uses the stored implicit pressure fields, the pressure-recovery sweep and the decimal checks.
- [resources.txt](resources.txt) records the complete driver with GNU time on WSL2 daisy, and a separate fine-grid integration. Wall time and peak resident memory depend on host load and library versions. Reproduce the single-case timing with the command below.

```bash
/usr/bin/time -v "$wp" -c 'from physics_first.liquid_imex_benchmark import Liquid, integrate; integrate(Liquid(), 128, 512, 10, 1)'
```
