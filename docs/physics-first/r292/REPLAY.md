# Replaying the release and 12 ns comparison

Use the R291 environment on daisy, Python 3.12.14, CoolProp 7.2.0, NumPy 2.5.5 and SciPy 1.17.1. Start in the repository root. The first archive contains the original release and explicit endpoints. The second contains the projected release, raw matched JST-off and projected SU2 release probes, all six comparison snapshots, five endpoint/release spatial samples, configs, histories, timings and solver stdout. Each snapshot preserves all four conserved doubles by XOR with the common projected release. Spatial samples store the actual pressure and four integrated SU2 residual fields, component-first in native node order. The current native runs are also retained in `~/r292-lab` on daisy. [R289 archive](../rotating-disk/fields.zip) · [R292 archive](fields.zip) · [Scientific decision](../DISK_MASS_BALANCE.md)

## Replay without advancing water

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export PYTHONPATH=/tmp/water-r277-scipy.MZ7N4z
wp="$HOME/.local/opt/water-acoustics/tools/bin/python"
ev=docs/physics-first/r292
work=$(mktemp -d)
"$wp" -m physics_first.disk_archive unpack docs/physics-first/rotating-disk/fields.zip "$work/old"
unzip -q "$ev/fields.zip" 'centered/*' 'release/*' -d "$work"
base="$work/old/r289-wide32"
"$wp" -m physics_first.disk_mass_balance baseline "$base" "$work/centered" \
  "$work/old/wide32/state_00004.dat" > "$work/baseline.json"
cmp "$work/baseline.json" "$ev/baseline.json"
"$wp" -m physics_first.disk_release_screen "$base" "$work/release" > "$work/release.json"
cmp "$work/release.json" "$ev/release.json"
"$wp" -m physics_first.disk_balance_evidence measure "$ev/fields.zip" > "$work/endpoints.json"
cmp "$work/endpoints.json" "$ev/endpoints.json"
"$wp" -m unittest -v tests.test_disk_mass_balance tests.test_rotating_disk tests.test_water_acoustics \
  tests.test_water_shear tests.test_vortex_equilibrium tests.test_cylinder_spreading
```

The measurement command with `--require-qualified` prints the same evidence and returns 1 on the failed physical window. R291's original archive and its independent gates still replay with the historical reader. The same cell quadrature, physical windows, reference definition, masks and gates apply to both sets of comparisons. The corrected release screen also checks the actual conservative forward-Euler update against the reported release residual. The release screen reconstructs thermodynamic metadata from the packed state and verifies any existing release record. [Screen and storage identity](../../../physics_first/disk_release_screen.py) · [Shared endpoint measurements](../../../physics_first/disk_step_evidence.py)

## Regenerate from the original case

The historical native source is `~/.local/opt/water-acoustics/runs/r289/r289-wide32`. For portable replay, regenerate the relocated mesh with `python -m physics_first.rotating_disk "$work/mesh" 32 --wide` and copy its `line.su2` to the unpacked original case above. The original mesh and restart SHA-256 bindings are in the [R291 trial driver](../../../physics_first/disk_step_trial.py). The original release, measured solver residual and the wall are inputs to the projection. The following commands use fresh run directories.

```bash
run=$(mktemp -d)
installed="$HOME/.local/bin/su2-water"
experimental="$HOME/r291-lab/experimental/SU2_CFD_water"
"$wp" -m physics_first.disk_mass_balance project "$base" "$run/release" > "$run/projection.json"
cmp "$ev/projection.json" "$run/projection.json"
cmp "$work/release/state_00000.dat" "$run/release/state_00000.dat"
(cd "$run/release" && /usr/bin/time -v -o resources.txt timeout 180 prlimit --as=2684354560 \
  "$installed" wave.cfg > solver.log 2>&1)
"$wp" -m physics_first.disk_release_screen "$base" "$run/release" > "$run/screen.json"
cmp "$run/screen.json" "$ev/release.json"
```

To regenerate the independent centered-flux control, copy the historical mesh, input restart and configuration to another fresh directory, change only `JST_SENSOR_COEFF= (0.5, 0.0)` to `(0.0, 0.0)` and run the same one-evaluation release probe. Its output state is discarded after extracting the release residual. The nonlinear projected probe uses the original JST coefficients. All physical comparisons start again from the pre-probe projected input, SHA-256 `693b762dca36f6275190fd03d77cb37d4a2352287ac5db3779cb76e8b991301f`. The three implicit configurations and the explicit configuration are loaded byte-for-byte from their historical archives. The runner checks the mesh, restart, screen decision and both executable hashes. [Bounded driver](../../../physics_first/disk_balance_trials.py) · [R291 binary build and bindings](../r291/REPLAY.md#face-audit-and-disk-experiment)

```bash
"$wp" -m physics_first.disk_balance_trials "$run" "$installed" "$experimental"
"$wp" -m physics_first.disk_spatial_probe "$run" "$installed"
"$wp" -m physics_first.plot_mass_balance extract "$base" "$run" "$run/map.npz"
env -u PYTHONPATH MPLBACKEND=Agg /usr/bin/python3 -m physics_first.plot_mass_balance plot \
  "$run/map.npz" "$run/flux-and-rate.png"
```

The four physical runs use a single serial process, 2.5 GiB address-space and 420 s per-case caps. Measured explicit/full/half/tight wall times were 91.50/40.76/66.09/42.19 s. Peak RSS was 312 MiB explicit and 1.01 GiB implicit. Projection took 6.17 s and 436 MiB. Steady residual probes use one pseudo-iteration with CFL 10⁻¹⁵, zero physical elapsed time, the original spatial flux and a 180 s cap. The release steady probe reproduced all 661,252 components of the forward-Euler release residual bit for bit. Checks verify each steady input against its exact endpoint. The first postprocessor assumed an absolute 10⁻²³ momentum tolerance at nearly zero momentum and flagged a 5.42 × 10⁻²³ pseudo-update. The sampler now checks the actual residual times a conservative local time bound plus storage rounding. The original probe was reused after verification. All physical thresholds and endpoints were retained. [Static probes](../../../physics_first/disk_spatial_probe.py) · [Archive and backward-Euler defect measurement](../../../physics_first/disk_balance_evidence.py)

In the JSON, conservative components are density, x momentum density, y momentum density and total-energy density, in SI. Spatial rates use −R/V. Domain integrals are per metre of axial depth. All core RMS values use dual-area weights on 0 < r ≤ 30 mm. Curl and loop measurements use cell circulation. The strong region has 3,560 cells above one quarter of the initial reference peak. The local fractional rate is Δω/(ω₀ Δt), in s⁻¹. The spatial residual, time-averaged state change and dimensionful pseudo-iteration history describe different measurements.
