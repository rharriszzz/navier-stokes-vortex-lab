# R009 accuracy-review calculation evidence

Companion to the [accuracy review](B2_ACCURACY_REVIEW.md), completed 2026-09-20.
This appendix preserves the final reference-only calculation and its exact
runner. It neither contains nor implies a new FEM/harmonic solve. Raw records
and validation scripts are in `/tmp/navier-b2-accuracy-r009/`; conclusions and
reproduction do not depend on that directory surviving.

## Reproduction

Save the exact runner below as `/tmp/r009-reference.py`, then from the repository
root use a SciPy-enabled Python (the isolated environment is documented in
[B1_SETUP.md](B1_SETUP.md)). Use fresh output directories:

```bash
python /tmp/r009-reference.py --self-check --output /tmp/r009-watchdog-check
python /tmp/r009-reference.py --output /tmp/r009-reference-output
```

The runner imports NumPy/SciPy and dependency-light feature helpers, not DOLFINx.
It sets BLAS/OpenMP threads to one and launches the calculation in a new session
under a 120 s/1 GiB parent watchdog. No mesh generation or operator assembly is
called. All series use 32/64/128 terms; quadrature stays at or below 512 points
per integrated coordinate. Historical report comparisons are optional in a
fresh clone; if present the exact recorded hash is required. If absent, the
calculation records null rather than fabricating a rerun. All other comparisons
are reproducible from tracked source.

An initial wrapper directory-creation defect affected only watchdog self-check
startup. After fixing it, both watchdog checks and a final reference pass ran.
The final command included `--previous-calculation-seconds 0.475233504010248`
to deduct the first reference pass from the total calculation budget. The two
passes consumed 0.844224944 s cumulatively. Fresh reproduction uses the default
zero prior time. Synthetic watchdog checks are separate from the reference
calculation and use no numerical model. They observe and terminate deliberate
wall-time and two-process RSS limit violations.

The JSON records below are evidence, not exact-value portability requirements.
Small floating-point/runtime differences across platforms are expected. The
runner's numerical consistency guards (2e-18 gain and 4e-14 coefficient
comparisons) are diagnostic self-checks, not physical B2 acceptance thresholds.

## Resource and file identities

```json
{
  "final_watch": {
    "command": [
      "/tmp/navier-fenicsx/bin/python",
      "/tmp/navier-b2-accuracy-r009/runner.py",
      "--child",
      "--output",
      "/tmp/navier-b2-accuracy-r009/evidence-final"
    ],
    "returncode": 0,
    "elapsed_seconds": 0.3689914400019916,
    "parent_observed_peak_rss_mib": 62.2734375,
    "samples": 8,
    "nominal_poll_seconds": 0.05,
    "maximum_sample_gap_seconds": 0.053416813010699116,
    "largest_observed_process_tree": 1,
    "stop_reason": null,
    "previous_calculation_seconds": 0.475233504010248,
    "cumulative_calculation_seconds": 0.8442249440122396
  },
  "initial_watch": {
    "command": [
      "/tmp/navier-fenicsx/bin/python",
      "/tmp/navier-b2-accuracy-r009/runner.py",
      "--child",
      "--output",
      "/tmp/navier-b2-accuracy-r009/evidence"
    ],
    "returncode": 0,
    "elapsed_seconds": 0.475233504010248,
    "parent_observed_peak_rss_mib": 66.90625,
    "samples": 10,
    "nominal_poll_seconds": 0.05,
    "maximum_sample_gap_seconds": 0.053172455009189434,
    "largest_observed_process_tree": 1,
    "stop_reason": null
  },
  "synthetic_watchdog_checks": {
    "scope": "synthetic watchdog validation; no mesh/PDE work",
    "timeout": {
      "command": [
        "/tmp/navier-fenicsx/bin/python",
        "-c",
        "import time; time.sleep(3)"
      ],
      "returncode": -9,
      "elapsed_seconds": 0.15169279900146648,
      "parent_observed_peak_rss_mib": 8.78125,
      "samples": 4,
      "nominal_poll_seconds": 0.05,
      "maximum_sample_gap_seconds": 0.053014310004073195,
      "largest_observed_process_tree": 1,
      "stop_reason": "wall_time_limit"
    },
    "memory": {
      "command": [
        "/tmp/navier-fenicsx/bin/python",
        "-c",
        "import subprocess,sys,time; subprocess.Popen([sys.executable,\"-c\",'import time; data=bytearray(32*1024**2); time.sleep(3)']); time.sleep(3)"
      ],
      "returncode": -9,
      "elapsed_seconds": 0.05208357999799773,
      "parent_observed_peak_rss_mib": 52.453125,
      "samples": 2,
      "nominal_poll_seconds": 0.05,
      "maximum_sample_gap_seconds": 0.050256575996172614,
      "largest_observed_process_tree": 2,
      "stop_reason": "rss_limit"
    }
  },
  "calculation_sha256": "aea6e545734dbcaeacf5e29ac7977fa68a8033c0827ee397906efdfadccfdf96",
  "runner_sha256": "d3f821efdf8cae1ae9a977082affe7e19a681bbb573c7c9f2a1052a36b91ab61",
  "manifest": {
    "calculation.json": "aea6e545734dbcaeacf5e29ac7977fa68a8033c0827ee397906efdfadccfdf96",
    "calculation.stderr": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "calculation.stdout": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "watch.json": "d869c540e2cc62f58ecaa78def65491d21c900d367dd1a018d5949bab1adec32"
  }
}
```

## Calculation records

### Parameters

```json
{
  "cylinder_radius": 0.1,
  "half_height": 0.15,
  "disk_radius": 0.025,
  "viscosity": 1e-06,
  "frequency_hz": 0.01
}
```

### Probe velocity m per s

```json
1e-07
```

### Config

```json
{
  "schema_version": 1,
  "geometry": {
    "radius": 0.1,
    "half_height": 0.15
  },
  "fluid": {
    "kinematic_viscosity": 1e-06,
    "density": 1000.0
  },
  "reference": {
    "duration": 100.0,
    "initial_core_radius": 0.01,
    "final_core_radius": 0.003,
    "initial_peak_swirl": 0.01,
    "radial_plateau": 0.04,
    "radial_cutoff": 0.08,
    "axial_plateau": 0.05,
    "axial_cutoff": 0.12
  },
  "probe_velocity": 1e-07,
  "frequencies_hz": [
    0.01,
    0.1,
    1.0,
    30.0
  ],
  "mode_order": [
    "N_02c",
    "T_00c",
    "N_40c",
    "N_40s",
    "T_40c",
    "T_40s"
  ]
}
```

### Reference

```json
{
  "gain_per_m": {
    "real": 2.0662858857221768e-05,
    "imaginary": -6.595106312048072e-05
  },
  "magnitude_per_m": 6.911220198253779e-05,
  "phase_degrees": -72.60391709725774,
  "omega_amplitude_per_s": 6.911220198253778e-12
}
```

### Series

```json
[
  {"terms": 32, "gain_per_m": {"real": 2.0662858857221768e-05, "imaginary": -6.595106312048072e-05}, "difference_to_128_per_m": 0.0},
  {"terms": 64, "gain_per_m": {"real": 2.0662858857221768e-05, "imaginary": -6.595106312048072e-05}, "difference_to_128_per_m": 0.0},
  {"terms": 128, "gain_per_m": {"real": 2.0662858857221768e-05, "imaginary": -6.595106312048072e-05}, "difference_to_128_per_m": 0.0}
]
```

### Coefficient quadrature

```json
{
  "order": 512,
  "terms": 128,
  "max_coefficient_error": 2.886579864025407e-15,
  "gain_difference_per_m": 2.1894777686578917e-19
}
```

### Unscaled bessel difference per m

```json
1.1030957909870672e-19
```

### Cancellation

```json
{
  "series": 1.0523307850368,
  "radial_512": 1.1728816591732705,
  "series_reverse_sum_difference_per_m": 0.0,
  "series_fsum_difference_per_m": 0.0
}
```

### Radial quadrature

```json
[
  {"terms": 32, "radial_order": 12, "gain": {"real": 2.0662858857221812e-05, "imaginary": -6.595106312048087e-05}, "absolute_difference_per_m": 1.554484317276036e-19, "cancellation_ratio": 1.172881659220217},
  {"terms": 32, "radial_order": 18, "gain": {"real": 2.066285885722146e-05, "imaginary": -6.595106312048064e-05}, "absolute_difference_per_m": 3.1886262509726037e-19, "cancellation_ratio": 1.172881659173271},
  {"terms": 32, "radial_order": 24, "gain": {"real": 2.0662858857221957e-05, "imaginary": -6.59510631204809e-05}, "absolute_difference_per_m": 2.5892066776395734e-19, "cancellation_ratio": 1.1728816591732696},
  {"terms": 32, "radial_order": 64, "gain": {"real": 2.0662858857221568e-05, "imaginary": -6.595106312048073e-05}, "absolute_difference_per_m": 2.0035865655883678e-19, "cancellation_ratio": 1.1728816591732694},
  {"terms": 32, "radial_order": 128, "gain": {"real": 2.0662858857222947e-05, "imaginary": -6.595106312048142e-05}, "absolute_difference_per_m": 1.3736273526914378e-18, "cancellation_ratio": 1.1728816591732705},
  {"terms": 32, "radial_order": 256, "gain": {"real": 2.0662858857221937e-05, "imaginary": -6.595106312048085e-05}, "absolute_difference_per_m": 2.169462877787276e-19, "cancellation_ratio": 1.17288165917327},
  {"terms": 32, "radial_order": 512, "gain": {"real": 2.0662858857222533e-05, "imaginary": -6.595106312048115e-05}, "absolute_difference_per_m": 8.800016030395972e-19, "cancellation_ratio": 1.1728816591732705},
  {"terms": 64, "radial_order": 12, "gain": {"real": 2.0662858857221812e-05, "imaginary": -6.595106312048087e-05}, "absolute_difference_per_m": 1.554484317276036e-19, "cancellation_ratio": 1.172881659220217},
  {"terms": 64, "radial_order": 18, "gain": {"real": 2.066285885722146e-05, "imaginary": -6.595106312048064e-05}, "absolute_difference_per_m": 3.1886262509726037e-19, "cancellation_ratio": 1.172881659173271},
  {"terms": 64, "radial_order": 24, "gain": {"real": 2.0662858857221957e-05, "imaginary": -6.59510631204809e-05}, "absolute_difference_per_m": 2.5892066776395734e-19, "cancellation_ratio": 1.1728816591732696},
  {"terms": 64, "radial_order": 64, "gain": {"real": 2.0662858857221568e-05, "imaginary": -6.595106312048073e-05}, "absolute_difference_per_m": 2.0035865655883678e-19, "cancellation_ratio": 1.1728816591732694},
  {"terms": 64, "radial_order": 128, "gain": {"real": 2.0662858857222947e-05, "imaginary": -6.595106312048142e-05}, "absolute_difference_per_m": 1.3736273526914378e-18, "cancellation_ratio": 1.1728816591732705},
  {"terms": 64, "radial_order": 256, "gain": {"real": 2.0662858857221937e-05, "imaginary": -6.595106312048085e-05}, "absolute_difference_per_m": 2.169462877787276e-19, "cancellation_ratio": 1.17288165917327},
  {"terms": 64, "radial_order": 512, "gain": {"real": 2.0662858857222533e-05, "imaginary": -6.595106312048115e-05}, "absolute_difference_per_m": 8.800016030395972e-19, "cancellation_ratio": 1.1728816591732705},
  {"terms": 128, "radial_order": 12, "gain": {"real": 2.0662858857221812e-05, "imaginary": -6.595106312048087e-05}, "absolute_difference_per_m": 1.554484317276036e-19, "cancellation_ratio": 1.172881659220217},
  {"terms": 128, "radial_order": 18, "gain": {"real": 2.066285885722146e-05, "imaginary": -6.595106312048064e-05}, "absolute_difference_per_m": 3.1886262509726037e-19, "cancellation_ratio": 1.172881659173271},
  {"terms": 128, "radial_order": 24, "gain": {"real": 2.0662858857221957e-05, "imaginary": -6.59510631204809e-05}, "absolute_difference_per_m": 2.5892066776395734e-19, "cancellation_ratio": 1.1728816591732696},
  {"terms": 128, "radial_order": 64, "gain": {"real": 2.0662858857221568e-05, "imaginary": -6.595106312048073e-05}, "absolute_difference_per_m": 2.0035865655883678e-19, "cancellation_ratio": 1.1728816591732694},
  {"terms": 128, "radial_order": 128, "gain": {"real": 2.0662858857222947e-05, "imaginary": -6.595106312048142e-05}, "absolute_difference_per_m": 1.3736273526914378e-18, "cancellation_ratio": 1.1728816591732705},
  {"terms": 128, "radial_order": 256, "gain": {"real": 2.0662858857221937e-05, "imaginary": -6.595106312048085e-05}, "absolute_difference_per_m": 2.169462877787276e-19, "cancellation_ratio": 1.17288165917327},
  {"terms": 128, "radial_order": 512, "gain": {"real": 2.0662858857222533e-05, "imaginary": -6.595106312048115e-05}, "absolute_difference_per_m": 8.800016030395972e-19, "cancellation_ratio": 1.1728816591732705}
]
```

### Polar features

```json
[
  {"radial_order": 12, "angular_order": 64, "gain": {"real": 2.0662858857221812e-05, "imaginary": -6.595106312048088e-05}, "absolute_difference_per_m": 1.6848931049131583e-19, "summation_cancellation_ratio": 1.1728816592202167, "m4_tangential_leak_max": 3.6887772564594836e-22},
  {"radial_order": 18, "angular_order": 96, "gain": {"real": 2.066285885722147e-05, "imaginary": -6.595106312048074e-05}, "absolute_difference_per_m": 2.9938511026802824e-19, "summation_cancellation_ratio": 1.1728816591732707, "m4_tangential_leak_max": 2.097227333255418e-22},
  {"radial_order": 24, "angular_order": 128, "gain": {"real": 2.0662858857221917e-05, "imaginary": -6.595106312048079e-05}, "absolute_difference_per_m": 1.6375580868516828e-19, "summation_cancellation_ratio": 1.1728816591732698, "m4_tangential_leak_max": 2.2880524543007698e-22},
  {"radial_order": 64, "angular_order": 256, "gain": {"real": 2.0662858857221595e-05, "imaginary": -6.595106312048081e-05}, "absolute_difference_per_m": 1.9712405817619023e-19, "summation_cancellation_ratio": 1.1728816591732696, "m4_tangential_leak_max": 1.8507839698776344e-22},
  {"radial_order": 128, "angular_order": 512, "gain": {"real": 2.066285885722282e-05, "imaginary": -6.595106312048102e-05}, "absolute_difference_per_m": 1.0950796264510033e-18, "summation_cancellation_ratio": 1.1728816591732703, "m4_tangential_leak_max": 1.4805869767267652e-22}
]
```

### Scales

```json
{
  "penetration_depth_m": 0.005641895835477563,
  "gap_in_penetration_depths": 13.293403881791372,
  "half_height_in_penetration_depths": 26.586807763582737,
  "delta_over_four_m": 0.0014104739588693908,
  "nominal_h_over_delta": {
    "0.05": 8.86226925452758,
    "0.04": 7.089815403622064,
    "0.03": 5.317361552716548,
    "0.025": 4.43113462726379
  },
  "five_percent_absolute_per_m": 3.4556100991268897e-06,
  "five_percent_omega_per_s": 3.4556100991268893e-13,
  "five_degree_guarantee_per_m": 6.023525296714254e-06,
  "largest_corner_error_per_m": 7.0789027735646575e-06,
  "worst_phase_at_five_percent_degrees": 2.8659839825988622,
  "fitted_edge_velocity_m_per_s": 1.727805049563445e-13,
  "float64_epsilon": 2.220446049250313e-16
}
```

### Profile

```json
[
  {"radius_m": 0.0, "normalized_velocity": {"real": 0.0, "imaginary": 0.0}, "physical_speed_m_per_s": 0.0},
  {"radius_m": 0.025, "normalized_velocity": {"real": 2.509915660458959e-06, "imaginary": -1.9954634144608425e-06}, "physical_speed_m_per_s": 3.20648574939432e-13},
  {"radius_m": 0.08871620832904488, "normalized_velocity": {"real": -0.05899111177307341, "imaginary": -0.13035918109999586}, "physical_speed_m_per_s": 1.4308552465321137e-08},
  {"radius_m": 0.09435810416452245, "normalized_velocity": {"real": 0.20486520215431148, "imaginary": -0.3176023007989465}, "physical_speed_m_per_s": 3.77943081067125e-08},
  {"radius_m": 0.1, "normalized_velocity": {"real": 1.0000001230162971, "imaginary": 2.2055815262098404e-21}, "physical_speed_m_per_s": 1.0000001230162972e-07}
]
```

### Historical

```json
{
  "sha256": "b3f1ebde3577fb400ea56ecf3bab0e36b9dbc4d889135bf915c2c42e5017d2bd",
  "penalty": 6,
  "provenance": {
    "repository_commit": "ab268b2818139f8a85f92d46842bb885e7089b06",
    "repository_dirty": true,
    "source_sha256": {
      "configs/realizability/pilot.json": "0e60a6ee85063f5d86b84db5af053f2166126249255edeafae4b4e6242db10d0",
      "realizability/backends/b1_verification.py": "287512f423a3c147c009802c2de9d6cf11538d3c80fc3fbc98dffaf586bb1e5c",
      "realizability/backends/b2_gate.py": "6972e650adffec115c37ea0808fb6dd5075c8f9e9a03c44f310b9e95f9a0a2f3",
      "realizability/backends/fem_observables.py": "f5dbc8a47d2f5c61d9228daf49c80ae1011ab542ee12335398a52eaf89ed0a64",
      "realizability/backends/fenicsx_stokes.py": "37ecd62121553e13f273fb99c7bc2649f51d9cea57658f4bce8069c4ac80a206",
      "realizability/backends/hdiv_stokes.py": "7419a94746b3722012ff025fa38da5185563043f51d6dfff85130e5d3d15c4ca"
    }
  },
  "rows": [
    {
      "mesh_size_m": 0.04,
      "mesh_sha256": "a7006604f0da3df5c8b9f92aaf0e8f1eaae8522554c4378e1e9ce1369a85e59b",
      "gain_per_m": {
        "real": -0.07533532889640583,
        "imaginary": 0.008436300240941155
      },
      "absolute_error_per_m": 0.07583412009548665,
      "relative_complex_error": 1097.2609455367556,
      "error_over_five_percent_scale": 21945.21891073511,
      "residual": 2.710253007521878e-12
    },
    {
      "mesh_size_m": 0.03,
      "mesh_sha256": "9096deae45c24dcdb028082e2b971fb197657574e1b43af71a9ec036dc2ff7bf",
      "gain_per_m": {
        "real": -0.013475907042611892,
        "imaginary": 0.01564211886429397
      },
      "absolute_error_per_m": 0.020709921775559276,
      "relative_complex_error": 299.6565176839821,
      "error_over_five_percent_scale": 5993.130353679641,
      "residual": 8.164256540736358e-13
    },
    {
      "mesh_size_m": 0.025,
      "mesh_sha256": "42fa3aac5c2bc762514c5cadb642edc2a1a8acfdf81ea9df7df992b696a04895",
      "gain_per_m": {
        "real": 1.4187509158011336e-05,
        "imaginary": 0.018138161157616555
      },
      "absolute_error_per_m": 0.018204113372404084,
      "relative_complex_error": 263.3994121183351,
      "error_over_five_percent_scale": 5267.9882423667,
      "residual": 1.4389546591337446e-12
    }
  ],
  "rerun": false
}
```

### Campaign ready

```json
false
```

### Limitations

```json
[
  "No repaired CFD response or total error bound.",
  "Observed reference sensitivities are not rigorous error bounds."
]
```

### Provenance

```json
{
  "commit": "f7f522b06e8887c84b8635fac1b55c3a2b7e9d58",
  "dirty": true,
  "source_sha256": {
    "realizability/__init__.py": "197df2cae0b7fcc3908afebfd9359b21244fc8aa0460b0167af04a2f1c7f219c",
    "realizability/backends/__init__.py": "8b40aa33331d5a627dbd4aa1681f9da523a21e31e2b0e71f48203967481f20b2",
    "realizability/backends/b1_verification.py": "287512f423a3c147c009802c2de9d6cf11538d3c80fc3fbc98dffaf586bb1e5c",
    "realizability/backends/b2_coercivity.py": "be10e484ffd5c36aef45962242dea2bcaaaa3cbad37df83e297fcc366bf96bcc",
    "realizability/backends/b2_gate.py": "3151ac8a85de4b242e53b28a3d2815d7ecf5e8e6ed8c654f440aa5a8778a6d05",
    "realizability/backends/b2_stability.py": "18b2e75712255a681a0c22f012d81ab3a129e147c41f3f8974bb46cf6a8df9f1",
    "realizability/backends/b2_verification.py": "42e11041c5f1edbca13737010456247f059d92e874a9398454bf4b6f17498d25",
    "realizability/backends/fem_observables.py": "f5dbc8a47d2f5c61d9228daf49c80ae1011ab542ee12335398a52eaf89ed0a64",
    "realizability/backends/fenicsx_stokes.py": "37ecd62121553e13f273fb99c7bc2649f51d9cea57658f4bce8069c4ac80a206",
    "realizability/backends/hdiv_stokes.py": "f23b252f91c406e3e279c7e6e7049e301ad604fae232dd0a610a73319864d2e9",
    "realizability/boundary_modes.py": "586d2667b8ac4b6a460d590afc884a05be5f9843484df74de8a4568261f84d18",
    "realizability/cli.py": "c163e6a3dc8e6a2c08c7dc48a7205624947fce938dea1aec3489ef62135bd850",
    "realizability/config.py": "3cb3edbb28e203226056cf4ac5e7832951c33e5f932b13a5ec438de88c786d12",
    "realizability/observables.py": "428fd794b00669593f87b694bca10a94454ccbd9ee012fa656a61c7b30375a05",
    "realizability/reference.py": "7f032634768a3f8b8a7a649e4d83dc45fd6f969a1c1ba679d1628867d2f13305",
    "realizability/response.py": "5318e4d6ea917433909e6e9718c90ed9cf48a5ee4b779b4446b83b3452d71317",
    "realizability/sensors.py": "c93cd68cc902970f27ecdce7deb1d272f146890cfe99b076b87e190222483d9a",
    "realizability/swirl_reference.py": "375e057ff365858cb5dc698e1b397eb34b18a9898d5a82482e2391ea11d81e4a",
    "configs/realizability/pilot.json": "0e60a6ee85063f5d86b84db5af053f2166126249255edeafae4b4e6242db10d0"
  },
  "runner_sha256": "d3f821efdf8cae1ae9a977082affe7e19a681bbb573c7c9f2a1052a36b91ab61",
  "python": "3.12.13 | packaged by conda-forge | (main, Mar  5 2026, 16:50:00) [GCC 14.3.0]",
  "numpy": "2.5.3",
  "scipy": "1.18.1",
  "peak_rss_mib": 71.78125
}
```

## Exact runner

```python
"""R009 reference-only study; run from repository root. No FEM imports/solves."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

POLL_S = 0.05
WALL_S = 120.0
RSS_MIB = 1024.0
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

def read_json(path):
    def reject(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    return json.loads(Path(path).read_text(), parse_constant=reject)

def process_tree_sample(root_pid):
    """Include descendants and the child's entire new session, including orphans."""
    records = {}
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            fields = (entry / 'stat').read_text().rsplit(')', 1)[1].split()
            records[int(entry.name)] = (int(fields[1]), int(fields[3]), int(fields[21]))
        except (FileNotFoundError, ProcessLookupError):
            continue
    included = {pid for pid, (_, session, _) in records.items() if session == root_pid}
    included.add(root_pid)
    while True:
        expanded = included | {pid for pid, (parent, _, _) in records.items() if parent in included}
        if expanded == included:
            break
        included = expanded
    rss_pages = sum(max(0, records[pid][2]) for pid in included if pid in records)
    return rss_pages * os.sysconf('SC_PAGE_SIZE') / 1024**2, included

def terminate_tree(process, pids):
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait(timeout=5)

def monitor(command, deadline, rss_limit, log_prefix):
    started = time.monotonic()
    peak = 0.0
    samples = 0
    max_gap = 0.0
    largest_tree = 0
    previous = started
    reason = None
    with Path(str(log_prefix) + '.stdout').open('w') as stdout, Path(str(log_prefix) + '.stderr').open('w') as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True)
        pids = {process.pid}
        try:
            while True:
                now = time.monotonic()
                max_gap = max(max_gap, now - previous)
                previous = now
                rss, pids = process_tree_sample(process.pid)
                samples += 1
                peak = max(peak, rss)
                largest_tree = max(largest_tree, len(pids))
                if now >= deadline:
                    reason = 'wall_time_limit'
                elif rss > rss_limit:
                    reason = 'rss_limit'
                if reason:
                    terminate_tree(process, pids)
                    break
                if process.poll() is not None:
                    # A successful child must not leave a live descendant behind.
                    remaining_rss, remaining_pids = process_tree_sample(process.pid)
                    if remaining_rss > 0:
                        reason = 'child_left_live_descendants'
                        terminate_tree(process, remaining_pids)
                    break
                time.sleep(min(POLL_S, max(0, deadline-time.monotonic())))
        except BaseException:
            terminate_tree(process, pids)
            raise
    return dict(command=command, returncode=process.returncode,
        elapsed_seconds=time.monotonic()-started, parent_observed_peak_rss_mib=peak,
        samples=samples, nominal_poll_seconds=POLL_S, maximum_sample_gap_seconds=max_gap,
        largest_observed_process_tree=largest_tree, stop_reason=reason)

def self_check(output):
    output.mkdir(parents=True, exist_ok=False)
    timeout_case = monitor([sys.executable, '-c', 'import time; time.sleep(3)'],
        time.monotonic()+0.15, RSS_MIB, output/'timeout')
    grandchild = 'import time; data=bytearray(32*1024**2); time.sleep(3)'
    parent = f'import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",{grandchild!r}]); time.sleep(3)'
    rss_case = monitor([sys.executable, '-c', parent], time.monotonic()+3, 24.0, output/'memory')
    result = dict(scope='synthetic watchdog validation; no mesh/PDE work', timeout=timeout_case, memory=rss_case)
    write_json(output/'self-check.json', result)
    assert timeout_case['stop_reason'] == 'wall_time_limit'
    assert rss_case['stop_reason'] == 'rss_limit' and rss_case['largest_observed_process_tree'] >= 2
    assert max(timeout_case['maximum_sample_gap_seconds'], rss_case['maximum_sample_gap_seconds']) <= 0.1
    print(json.dumps(result, indent=2), flush=True)


def calculate(output):
    sys.path.insert(0, str(Path.cwd()))
    import numpy as np
    import scipy
    from scipy.special import ive, iv
    from realizability.swirl_reference import (
        disk_rotation_gain, normalized_swirl, sidewall_coefficients,
    )
    from realizability.backends.fem_observables import _polar_rule
    from realizability.observables import fitted_rotation, fourier_coefficients

    parameters = dict(cylinder_radius=0.1, half_height=0.15, disk_radius=0.025,
                      viscosity=1e-6, frequency_hz=0.01)
    profile_parameters = {k: v for k, v in parameters.items() if k != 'disk_radius'}
    config = read_json('configs/realizability/pilot.json')
    assert config['geometry'] == dict(radius=0.1, half_height=0.15)
    assert config['fluid']['kinematic_viscosity'] == 1e-6
    assert config['probe_velocity'] == 1e-7
    speed, d, R, H, nu, f = 1e-7, 0.025, 0.1, 0.15, 1e-6, 0.01
    expected = complex(2.0662858857221785e-5, -6.595106312048072e-5)
    def pair(value):
        return dict(real=float(value.real), imaginary=float(value.imag))
    gains = {n: disk_rotation_gain(**parameters, terms=n) for n in (32, 64, 128)}
    reference = gains[128]
    assert abs(reference - expected) < 2e-18, 'reference inconsistency'
    assert max(abs(g-reference) for g in gains.values()) < 2e-18
    nodes, weights = np.polynomial.legendre.leggauss(512)
    n = np.arange(128)
    a = (n+0.5)*np.pi
    b = sidewall_coefficients(128)
    lam = np.sqrt((a/H)**2 + 2j*np.pi*f/nu)
    bq = np.cos(a[:, None]*nodes) @ (weights*(1-nodes*nodes)**2)
    terms = 4/d**2 * b * ive(2, lam*d)/ive(1, lam*R) * np.exp(lam.real*(d-R))/lam
    coefficient_gain = 4/d**2 * np.sum(bq * ive(2, lam*d)/ive(1, lam*R)
                                     * np.exp(lam.real*(d-R))/lam)
    unscaled_gain = 4/d**2 * np.sum(b * iv(2, lam*d)/iv(1, lam*R)/lam)
    assert np.max(abs(b-bq)) < 4e-14
    assert abs(coefficient_gain-reference) < 2e-18
    assert abs(unscaled_gain-reference) < 2e-18
    quadrature = []
    for count in (32, 64, 128):
        for order in (12, 18, 24, 64, 128, 256, 512):
            s, w = np.polynomial.legendre.leggauss(order)
            radius, radial_weights = d*(s+1)/2, d*w/2
            profile = normalized_swirl(radius, 0.0, terms=count, **profile_parameters)
            summands = 4/d**4 * radial_weights*radius**2*profile
            gain = np.sum(summands)
            quadrature.append(dict(terms=count, radial_order=order, gain=pair(gain),
                absolute_difference_per_m=float(abs(gain-reference)),
                cancellation_ratio=float(np.sum(abs(summands))/abs(gain))))
    assert max(q['absolute_difference_per_m'] for q in quadrature) < 2e-18
    polar = []
    for nr, nt in ((12, 64), (18, 96), (24, 128), (64, 256), (128, 512)):
        points, theta, area_weights, radius = _polar_rule(0, d, nr, nt)
        v = np.repeat(normalized_swirl(radius.reshape(nr, nt)[:, 0], 0.0,
                    terms=128, **profile_parameters), nt)
        ux, uy = -v*np.sin(theta), v*np.cos(theta)
        gain = complex(fitted_rotation(points[:, 0], points[:, 1], ux.real, uy.real, area_weights),
                       fitted_rotation(points[:, 0], points[:, 1], ux.imag, uy.imag, area_weights))
        _, at, aw, ar = _polar_rule(0.015, d, nr, nt)
        av = np.repeat(normalized_swirl(ar.reshape(nr, nt)[:, 0], 0.0,
                      terms=128, **profile_parameters), nt)
        leak = np.array(fourier_coefficients(av.real, at, aw, 4)) + 1j*np.array(
                       fourier_coefficients(av.imag, at, aw, 4))
        numerator_terms = area_weights*(points[:, 0]*uy-points[:, 1]*ux)
        polar.append(dict(radial_order=nr, angular_order=nt, gain=pair(gain),
            absolute_difference_per_m=float(abs(gain-reference)),
            summation_cancellation_ratio=float(np.sum(abs(numerator_terms))/abs(np.sum(numerator_terms))),
            m4_tangential_leak_max=float(max(abs(leak)))))
    assert max(q['absolute_difference_per_m'] for q in polar) < 2e-18
    profile_r = np.array([0.0, d, R-2*math.sqrt(nu/(math.pi*f)),
                          R-math.sqrt(nu/(math.pi*f)), R])
    profile = normalized_swirl(profile_r, 0, terms=128, **profile_parameters)
    rho5, phi5 = 0.05*abs(reference), math.sin(math.radians(5))*abs(reference)
    record = dict(parameters=parameters, probe_velocity_m_per_s=speed, config=config,
        reference=dict(gain_per_m=pair(reference), magnitude_per_m=abs(reference),
                       phase_degrees=float(np.angle(reference, deg=True)),
                       omega_amplitude_per_s=speed*abs(reference)),
        series=[dict(terms=n, gain_per_m=pair(g), difference_to_128_per_m=abs(g-reference))
                for n, g in gains.items()],
        coefficient_quadrature=dict(order=512, terms=128,
            max_coefficient_error=float(np.max(abs(b-bq))),
            gain_difference_per_m=abs(coefficient_gain-reference)),
        unscaled_bessel_difference_per_m=abs(unscaled_gain-reference),
        cancellation=dict(series=float(np.sum(abs(terms))/abs(reference)),
            radial_512=quadrature[-1]['cancellation_ratio'],
            series_reverse_sum_difference_per_m=float(abs(np.sum(terms[::-1])-reference)),
            series_fsum_difference_per_m=abs(complex(math.fsum(terms.real), math.fsum(terms.imag))-reference)),
        radial_quadrature=quadrature, polar_features=polar,
        scales=dict(penetration_depth_m=math.sqrt(nu/(math.pi*f)),
            gap_in_penetration_depths=(R-d)/math.sqrt(nu/(math.pi*f)),
            half_height_in_penetration_depths=H/math.sqrt(nu/(math.pi*f)),
            delta_over_four_m=math.sqrt(nu/(math.pi*f))/4,
            nominal_h_over_delta={str(h): h/math.sqrt(nu/(math.pi*f)) for h in (0.05,0.04,0.03,0.025)},
            five_percent_absolute_per_m=rho5, five_percent_omega_per_s=speed*rho5,
            five_degree_guarantee_per_m=phi5,
            largest_corner_error_per_m=abs(reference)*abs(1.05*np.exp(1j*math.radians(5))-1),
            worst_phase_at_five_percent_degrees=math.degrees(math.asin(.05)),
            fitted_edge_velocity_m_per_s=d*speed*abs(reference),
            float64_epsilon=float(np.finfo(float).eps)),
        profile=[dict(radius_m=float(r), normalized_velocity=pair(v),
                      physical_speed_m_per_s=float(abs(v)*speed)) for r,v in zip(profile_r,profile)],
        historical=None, campaign_ready=False,
        limitations=['No repaired CFD response or total error bound.',
                     'Observed reference sensitivities are not rigorous error bounds.'])
    historical_path = Path('results/realizability/b2/gate.json')
    if historical_path.exists():
        assert sha(historical_path) == 'b3f1ebde3577fb400ea56ecf3bab0e36b9dbc4d889135bf915c2c42e5017d2bd'
        old = read_json(historical_path)
        assert old['all_numerical_gates_passed'] is False
        rows = []
        for row in old['pilot_records']['T_00c']:
            solver = row['solver']
            g = next(x for x in row['feature_gains'] if x['name'] == 'Omega')
            gain = complex(g['real'], g['imaginary'])
            error = abs(gain-reference)
            rows.append(dict(mesh_size_m=solver['mesh_size'], mesh_sha256=solver['mesh_sha256'],
                gain_per_m=pair(gain), absolute_error_per_m=error,
                relative_complex_error=error/abs(reference), error_over_five_percent_scale=error/rho5,
                residual=solver['real']['algebraic_residual']))
        record['historical'] = dict(sha256=sha(historical_path), penalty=6,
             provenance=old.get('provenance'), rows=rows, rerun=False)
    paths = sorted(Path('realizability').rglob('*.py')) + [Path('configs/realizability/pilot.json')]
    record['provenance'] = dict(commit=subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
        dirty=bool(subprocess.check_output(['git','status','--porcelain'], text=True)),
        source_sha256={str(p): sha(p) for p in paths}, runner_sha256=sha(__file__),
        python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
        peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
    write_json(output/'calculation.json', record)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--child', action='store_true')
    parser.add_argument('--self-check', action='store_true')
    parser.add_argument('--previous-calculation-seconds', type=float, default=0.0)
    args = parser.parse_args()
    if not args.self_check:
        args.output.mkdir(parents=True, exist_ok=True)
    if args.self_check:
        self_check(args.output)
    elif args.child:
        calculate(args.output)
    else:
        for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
            os.environ[key] = '1'
        assert 0 <= args.previous_calculation_seconds < WALL_S
        started = time.monotonic()
        watch = monitor([sys.executable, str(Path(__file__).resolve()), '--child',
                         '--output', str(args.output)], started+WALL_S-args.previous_calculation_seconds, RSS_MIB,
                         args.output/'calculation')
        watch['previous_calculation_seconds'] = args.previous_calculation_seconds
        watch['cumulative_calculation_seconds'] = args.previous_calculation_seconds + watch['elapsed_seconds']
        write_json(args.output/'watch.json', watch)
        assert watch['stop_reason'] is None and watch['returncode'] == 0, watch
        assert watch['maximum_sample_gap_seconds'] <= 0.1, watch
        report = read_json(args.output/'calculation.json')
        assert report['campaign_ready'] is False
        write_json(args.output/'manifest.json', {p.name: sha(p) for p in sorted(args.output.iterdir())
                   if p.is_file() and p.name != 'manifest.json'})
        print(json.dumps(watch, indent=2, allow_nan=False))
```
