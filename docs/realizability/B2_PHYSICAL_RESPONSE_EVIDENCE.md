# R012 physical response audit evidence

This appendix accompanies [B2_PHYSICAL_RESPONSE_AUDIT.md](B2_PHYSICAL_RESPONSE_AUDIT.md).
It preserves the complete finite report and exact disposable runner for the
single 50 mm alpha=96 attempt. The numerical source/configuration is unchanged
from R009; the execution worktree differed from `339b3ee` only by the R012 log
entry. The physical accuracy comparison failed; the runner completed normally.
Generated arrays and process logs remain outside Git at
`/tmp/navier-b2-response-r012/`.

## Reproduction and limits

Save the exact runner below as `/tmp/r012-response.py`. From the repository root,
in the existing serial optional environment, the commands are:

```bash
/tmp/navier-fenicsx/bin/python /tmp/r012-response.py --self-check --output /tmp/r012-watchdog-check
/tmp/navier-fenicsx/bin/python /tmp/r012-response.py --output /tmp/r012-response-evidence
```

Output directories must be new. A reproduction would be another physical
attempt and is **not** part of R012 or its next review task. It requires its
own scope/authorization. The runner fixes one mesh, one primal solve and one
same-factor correction; it refuses mismatched source/mesh identities and
writes atomic progress reports. The parent enforces 180 s and 1536 MiB active
child-tree RSS at nominal 0.05 s sampling, including imports and output.
It records a partial result on failure or termination, without a retry.

Only the runner monkey-patches the harmonic module in its disposable child.
The direct helper itself runs unchanged; a return-frame observer captures its
locals. PETSc log counters check factor reuse. All generated records use strict
finite JSON; an undefined phase/cancellation ratio is explicit `null`. A
nonfinite field triggers a partial failure rather than a fabricated number.
The complete run below encountered no such outcomes.

The report includes all six signed complex features at every requested rule,
correction/corrected features, physical diagnostics and units. Raw coefficients
and finest disk samples are identified by the manifest; their compact reductions
are preserved here, and the exact runner recreates them. No binary arrays or
assembled matrix are added to the source repository.

## Resource, validation and file identities

```json
{
  "runner_sha256": "fcb8dfedfa4f9049ea6c321f3082ada7666219e90cbcfce234222357901d94bb",
  "audit_sha256": "14c1cba2fe20c9632d58ab196135f77079b6a8a72e51c46296339b6bb8f460d8",
  "report_sha256": "16da2b4a410fa08291a86c50454e13f4cfd57f183bc671d0d53e45e313d10b2c",
  "watch": {
    "command": [
      "/tmp/navier-fenicsx/bin/python",
      "/tmp/navier-b2-response-r012/runner.py",
      "--child",
      "--output",
      "/tmp/navier-b2-response-r012/evidence"
    ],
    "returncode": 0,
    "elapsed_seconds": 38.754202111013,
    "parent_observed_peak_rss_mib": 753.05078125,
    "samples": 718,
    "nominal_poll_seconds": 0.05,
    "maximum_sample_gap_seconds": 0.08137771100155078,
    "largest_observed_process_tree": 1,
    "stop_reason": null
  },
  "initial_watchdog_check": {
    "scope": "synthetic watchdog validation; no mesh/PDE work",
    "timeout": {
      "command": [
        "/usr/bin/python3",
        "-c",
        "import time; time.sleep(3)"
      ],
      "returncode": -9,
      "elapsed_seconds": 0.15203069502604194,
      "parent_observed_peak_rss_mib": 8.29296875,
      "samples": 4,
      "nominal_poll_seconds": 0.05,
      "maximum_sample_gap_seconds": 0.05397540298872627,
      "largest_observed_process_tree": 1,
      "stop_reason": "wall_time_limit"
    },
    "memory": {
      "command": [
        "/usr/bin/python3",
        "-c",
        "import subprocess,sys,time; subprocess.Popen([sys.executable,\"-c\",'import time; data=bytearray(32*1024**2); time.sleep(3)']); time.sleep(3)"
      ],
      "returncode": -9,
      "elapsed_seconds": 0.052317874011350796,
      "parent_observed_peak_rss_mib": 49.1875,
      "samples": 2,
      "nominal_poll_seconds": 0.05,
      "maximum_sample_gap_seconds": 0.050449931994080544,
      "largest_observed_process_tree": 2,
      "stop_reason": "rss_limit"
    }
  },
  "final_watchdog_check": {
    "scope": "synthetic watchdog validation; no mesh/PDE work",
    "timeout": {
      "command": [
        "/tmp/navier-fenicsx/bin/python",
        "-c",
        "import time; time.sleep(3)"
      ],
      "returncode": -9,
      "elapsed_seconds": 0.15635241699055769,
      "parent_observed_peak_rss_mib": 8.95703125,
      "samples": 4,
      "nominal_poll_seconds": 0.05,
      "maximum_sample_gap_seconds": 0.05400015498162247,
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
      "elapsed_seconds": 0.05555149901192635,
      "parent_observed_peak_rss_mib": 52.3046875,
      "samples": 2,
      "nominal_poll_seconds": 0.05,
      "maximum_sample_gap_seconds": 0.05185936999623664,
      "largest_observed_process_tree": 2,
      "stop_reason": "rss_limit"
    }
  },
  "evidence_manifest": {
    "calculation.stderr": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "calculation.stdout": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "coefficients.npz": "3080273ccc0275d038bf61779ff889d94e49c9030b9f194817ffc7b8e539d0aa",
    "finest_disk_samples.npz": "3f39238073d9d3c6ef837c5f290cc2230fce3e978a96e35962f1fa9945119e73",
    "local_bound.json": "d5d55c4e08da1bbb01d4302be6204ef61d1736bb2825be7b03fb04a870fdee42",
    "pinned_helper.py": "e47efbb5c81862972aa253add122d008e4b78861a9a29c376b73186e010ff563",
    "report.json": "16da2b4a410fa08291a86c50454e13f4cfd57f183bc671d0d53e45e313d10b2c",
    "watch.json": "db55d54d18c74119c04926e3ddf719f8b4276e981b5a7f777783371572c8b6ae"
  },
  "read_only_validation": {
    "status": "passed",
    "scope": "stored evidence only; no PDE work",
    "manifest_files": 8,
    "source_config_identities": 19,
    "local_trace_values": 482,
    "coefficient_arrays": 8,
    "signed_feature_values": 30,
    "finest_disk_sample_sets": 3,
    "disk_points_per_set": 49152,
    "physical_rotation_amplitude_per_s": 2.0016751141352977e-07,
    "amplitude_ratio_to_reference": 28962.687582158796,
    "finest_quadrature_step_over_scale": 84.37463681777515,
    "default_to_finest_over_scale": 1021.3491245013778,
    "largest_to_finest_over_scale": 4165.948550370064,
    "finest_absolute_error_over_scale": 579248.2782770232,
    "maximum_quadrature_gain_pair_distance": 0.017924429409580465,
    "finest_reference_phase_deg": -146.72029601717458
  }
}
```

## Complete calculation report

```json
{
  "schema_version": 1,
  "status": "complete",
  "stage": "complete",
  "campaign_ready": false,
  "physical_gate_passed": false,
  "solve_calls": 1,
  "correction_solve_calls": 1,
  "checked_mesh_reuses": 1,
  "limits": {
    "total_wall_seconds": 180.0,
    "active_child_tree_rss_mib": 1536.0,
    "nominal_poll_seconds": 0.05,
    "local_cell_cap": 500,
    "unchanged_dense_free_dof_cap": 3000
  },
  "failed_cell_locations": [],
  "quadrature": [
    {
      "orders": [
        12,
        12,
        64
      ],
      "features_gain": [
        [
          -0.007686328169796755,
          0.060878856772077876
        ],
        [
          -1.6876065555637287,
          -1.1007239033827334
        ],
        [
          0.004791834689918827,
          0.0017993838157383379
        ],
        [
          -0.006069488157330158,
          -0.0004034047849069154
        ],
        [
          0.0009741848872750257,
          -0.002590655674732687
        ],
        [
          0.0014062081115020285,
          -0.0033472379636489188
        ]
      ],
      "absolute_complex_error_per_m": 2.014828418591806,
      "relative_complex_error": 29153.005703694438,
      "relative_magnitude_error": 29152.276589015975,
      "wrapped_phase_error_deg": 74.28209864947996,
      "magnitude_passed": false,
      "phase_passed": false,
      "primary_absolute_change_from_previous_per_m": null,
      "primary_absolute_change_from_finest_per_m": 0.014395893883101819
    },
    {
      "orders": [
        18,
        18,
        96
      ],
      "features_gain": [
        [
          -0.007741797600103706,
          0.06305112436568511
        ],
        [
          -1.6699089264053721,
          -1.0978815290526496
        ],
        [
          0.004890184413325177,
          0.0017814468594993115
        ],
        [
          -0.006043948038145047,
          -0.00041231004750882043
        ],
        [
          0.000910668519944844,
          -0.0025916883881086645
        ],
        [
          0.0014523048286965647,
          -0.003321096406857504
        ]
      ],
      "absolute_complex_error_per_m": 1.9984653803297874,
      "relative_complex_error": 28916.245221570698,
      "relative_magnitude_error": 28915.51961520067,
      "wrapped_phase_error_deg": 74.07316557715039,
      "magnitude_passed": false,
      "phase_passed": false,
      "primary_absolute_change_from_previous_per_m": 0.017924429409580465,
      "primary_absolute_change_from_finest_per_m": 0.003529384349361368
    },
    {
      "orders": [
        24,
        24,
        128
      ],
      "features_gain": [
        [
          -0.007074188599468932,
          0.06345448478595717
        ],
        [
          -1.6717362953781498,
          -1.097682442371396
        ],
        [
          0.0049181524755943645,
          0.001780010787237552
        ],
        [
          -0.006051352128037133,
          -0.00041072175104849815
        ],
        [
          0.0009823953267039279,
          -0.0025684542965409302
        ],
        [
          0.001455113231457756,
          -0.003317634353445096
        ]
      ],
      "absolute_complex_error_per_m": 1.999883318947818,
      "relative_complex_error": 28936.76169445618,
      "relative_magnitude_error": 28936.035525362357,
      "wrapped_phase_error_deg": 74.10669190852015,
      "magnitude_passed": false,
      "phase_passed": false,
      "primary_absolute_change_from_previous_per_m": 0.0018381819467406216,
      "primary_absolute_change_from_finest_per_m": 0.0018048539167325377
    },
    {
      "orders": [
        48,
        48,
        256
      ],
      "features_gain": [
        [
          -0.007675818145591359,
          0.06323819986470292
        ],
        [
          -1.6736953515464452,
          -1.0983832366358068
        ],
        [
          0.004882945745803806,
          0.0017808533635442036
        ],
        [
          -0.00606812745971674,
          -0.0004124472696475927
        ],
        [
          0.0009446664846808596,
          -0.0025833434140061424
        ],
        [
          0.0014663705834159955,
          -0.0033209229803899025
        ]
      ],
      "absolute_complex_error_per_m": 2.00190563130846,
      "relative_complex_error": 28966.022987001208,
      "relative_magnitude_error": 28965.296582763134,
      "wrapped_phase_error_deg": 74.12070051352885,
      "magnitude_passed": false,
      "phase_passed": false,
      "primary_absolute_change_from_previous_per_m": 0.002080628191572762,
      "primary_absolute_change_from_finest_per_m": 0.0002915658470976673
    },
    {
      "orders": [
        96,
        96,
        512
      ],
      "features_gain": [
        [
          -0.00731041250887067,
          0.0635401404068063
        ],
        [
          -1.6734039795256472,
          -1.0983726070219908
        ],
        [
          0.004891770037777418,
          0.0017822054164528653
        ],
        [
          -0.006061828071111397,
          -0.0004123455507964639
        ],
        [
          0.0009565882007262312,
          -0.0025783459578130738
        ],
        [
          0.0014684040083753236,
          -0.00332010334913543
        ]
      ],
      "absolute_complex_error_per_m": 2.0016562003159444,
      "relative_complex_error": 28962.413913851164,
      "relative_magnitude_error": 28961.687582158793,
      "wrapped_phase_error_deg": 74.11637891991684,
      "magnitude_passed": false,
      "phase_passed": false,
      "primary_absolute_change_from_previous_per_m": 0.0002915658470976673,
      "primary_absolute_change_from_finest_per_m": 0.0
    }
  ],
  "elapsed_child_seconds": 38.64557207599864,
  "process_peak_rss_mib": 753.05078125,
  "config": {
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
  },
  "versions": {
    "dolfinx": "0.10.0",
    "basix": "0.10.0",
    "ufl": "2025.2.1",
    "ffcx": "0.10.0",
    "gmsh": "4.15.2",
    "numpy": "2.5.3",
    "petsc": "3.25.5",
    "petsc_scalar_type": "float64",
    "mpi": "MPICH Version:      5.0.1"
  },
  "provenance": {
    "commit": "339b3ee214e3e7e493e2873f5826830c7d6d9a1d",
    "worktree_status": " M REQUEST_LOG.md\n",
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
    "runner_sha256": "fcb8dfedfa4f9049ea6c321f3082ada7666219e90cbcfce234222357901d94bb",
    "direct_helper_sha256": "e47efbb5c81862972aa253add122d008e4b78861a9a29c376b73186e010ff563",
    "python": "3.12.13 | packaged by conda-forge | (main, Mar  5 2026, 16:50:00) [GCC 14.3.0]"
  },
  "parameters": {
    "mode": "T_00c",
    "frequency_hz": 0.01,
    "mesh_size_m": 0.05,
    "penalty_factor": 96,
    "disk_radius_m": 0.025,
    "phasor": "exp(i omega t)",
    "boundary_target": "existing facet-consistent symbolic target",
    "field_scale": 1e-07,
    "matrix_rhs_scale": "unit boundary speed; no rescaling of K or b",
    "feature_order": [
      "a_z",
      "Omega",
      "C_r4",
      "S_r4",
      "C_theta4",
      "S_theta4"
    ],
    "gain_units": [
      "1/m",
      "1/m",
      "dimensionless",
      "dimensionless",
      "dimensionless",
      "dimensionless"
    ]
  },
  "mesh": {
    "cells": 482,
    "velocity_dofs": 9522,
    "pressure_dofs": 1928,
    "mesh_sha256": "423ab057c5738ae3e2dcef6e82c238ee7e61bc1d0af7f1e212d04b8a2cd6bfb4"
  },
  "certificate": {
    "cell_count": 482,
    "facet_count": 1105,
    "exterior_facet_count": 282,
    "interior_facet_count": 823,
    "minimum_cell_volume_m3": 6.216355693824102e-06,
    "minimum_cell_diameter_m": 0.042899157353743854,
    "worst_cell": 320,
    "worst_cell_trace_eigenvalue": 48.96418141363834,
    "C_upper": 58.12657123078638,
    "C_safe": 58.12657123659904,
    "elapsed_seconds": 0.05355219601187855,
    "classification": {
      "penalty_factor": 96,
      "status": "certified_positive",
      "beta": 0.22187075813338908,
      "reason": null
    }
  },
  "solver": {
    "mode": "T_00c",
    "frequency_hz": 0.01,
    "mesh_size": 0.05,
    "cells": 482,
    "velocity_dofs": 9522,
    "pressure_dofs": 1928,
    "mesh_sha256": "423ab057c5738ae3e2dcef6e82c238ee7e61bc1d0af7f1e212d04b8a2cd6bfb4",
    "flux_correction_coefficient": 0.0,
    "corrected_flux_ratio": 0.0,
    "input_diagnostics": {
      "actual_peak_speed": 1e-07,
      "side_rms_speed": 6.371791452108136e-08,
      "inward_volume_flow_amplitude": 0.0,
      "displacement_amplitude": 1.5915494309189531e-06,
      "acceleration_amplitude": 6.283185307179586e-09,
      "pressure_demand": "not assessed",
      "force_and_power": "not assessed"
    },
    "real_boundary_trace": {
      "side_tangential_relative_l2": 0.07793993528349372,
      "cap_tangential_relative_l2": 0.0046674600702256005,
      "target_normal_mismatch_relative_l2": 0.07611947253714767,
      "actual_side_normal_relative_l2": 8.061801034352195e-17,
      "actual_cap_normal_relative_l2": 2.7168929407351363e-17,
      "interior_tangential_jump_relative_l2": 0.0415061376827475
    },
    "imaginary_boundary_trace": {
      "side_tangential_relative_l2": 0.1506122058533231,
      "cap_tangential_relative_l2": 0.004259906878454019,
      "target_normal_mismatch_relative_l2": 0.0,
      "actual_side_normal_relative_l2": 3.133824096243799e-17,
      "actual_cap_normal_relative_l2": 6.7196668747266084e-18,
      "interior_tangential_jump_relative_l2": 0.02451221607116883
    },
    "elapsed_seconds": 1.2019331649935339,
    "real": {
      "velocity_l2": 1.7232353109062644e-09,
      "pressure_l2": 1.9149141420391576e-13,
      "divergence_l2": 2.7868641344852176e-22,
      "divergence_ratio": 1.617227848598101e-14,
      "algebraic_residual": 8.503429445731727e-15,
      "boundary_dof_residual": 0.0
    },
    "imaginary": {
      "velocity_l2": 7.37669509220273e-10,
      "pressure_l2": 1.2774587708006112e-13,
      "divergence_l2": 1.633764624447768e-22,
      "divergence_ratio": 2.214765018788265e-14,
      "algebraic_residual": 8.503429445731727e-15,
      "boundary_dof_residual": 0.0
    },
    "formulation": "BDM2/DG1 divergence-conforming SIP Stokes"
  },
  "pde_diagnostics_passed": true,
  "algebraic": {
    "matrix_shape": [
      22900,
      22900
    ],
    "projected_rhs_norm": 0.10374689140977104,
    "projected_rhs_pressure_constant_dots": [
      0.0,
      0.0
    ],
    "original": {
      "absolute_norm": 8.822043713169791e-16,
      "relative_norm": 8.503429445731727e-15,
      "pressure_constant_dots": [
        2.7993915229043616e-21,
        5.489463994538582e-20
      ]
    },
    "original_reason": 4,
    "solver_type": "preonly",
    "factor_solver": "mumps",
    "pressure_nullspace_checks": [
      {
        "right_absolute_norm": 3.430628669834334e-14,
        "left_absolute_norm": 3.4582940511606334e-14
      },
      {
        "right_absolute_norm": 3.430628669834334e-14,
        "left_absolute_norm": 3.458294051160634e-14
      }
    ],
    "correction_rhs": {
      "absolute_norm": 8.822043696046447e-16,
      "relative_norm": 0.9999999980590275,
      "pressure_constant_dots": [
        0.0,
        1.2031184680666113e-35
      ]
    },
    "correction_projection_removed": {
      "absolute_norm": 5.496597208848453e-20,
      "relative_norm": 6.230525927504735e-05,
      "pressure_constant_dots": [
        2.7993915229043383e-21,
        5.489463994538583e-20
      ]
    },
    "factor_counts_before_correction": {
      "MatLUFactorSym": 1,
      "MatLUFactorNum": 1,
      "MatSolve": 1
    },
    "factor_counts_after_correction": {
      "MatLUFactorSym": 1,
      "MatLUFactorNum": 1,
      "MatSolve": 2
    },
    "correction_reason": 4,
    "correction_equation": {
      "absolute_norm": 2.989417236828406e-28,
      "relative_norm": 3.3885767740734474e-13,
      "pressure_constant_dots": [
        -9.767657630761935e-33,
        1.515036616183967e-32
      ]
    },
    "corrected_primal": {
      "absolute_norm": 1.2052300692044855e-16,
      "relative_norm": 1.1617023438747342e-15,
      "pressure_constant_dots": [
        6.911571932450243e-22,
        5.493767183980969e-20
      ]
    },
    "same_factor_handle": true,
    "unchanged_matrix_state": true
  },
  "reconstruction": {
    "exact_unit_block_roundtrips": true,
    "original_physical_coefficients_equal": true
  },
  "reference": {
    "terms": 128,
    "gain_per_m": [
      2.0662858857221768e-05,
      -6.595106312048072e-05
    ],
    "magnitude_per_m": 6.911220198253779e-05,
    "physical_rotation_amplitude_per_s": 6.911220198253778e-12,
    "five_percent_absolute_scale_per_m": 3.4556100991268897e-06
  },
  "finest": {
    "correction_features_gain": [
      [
        -2.2955857836450398e-15,
        -7.235135567792252e-15
      ],
      [
        -5.9784503836114406e-15,
        2.1690091946140843e-14
      ],
      [
        1.3850667127149445e-16,
        8.231257896731433e-17
      ],
      [
        1.0496605574304761e-16,
        2.772418542360593e-17
      ],
      [
        2.301475808457145e-17,
        3.078358159897084e-17
      ],
      [
        -5.997262555636861e-17,
        -9.379604999430362e-17
      ]
    ],
    "corrected_features_gain": [
      [
        -0.007310412508872931,
        0.06354014040679906
      ],
      [
        -1.673403979525653,
        -1.098372607021969
      ],
      [
        0.004891770037777557,
        0.0017822054164529481
      ],
      [
        -0.006061828071111293,
        -0.0004123455507964367
      ],
      [
        0.000956588200726253,
        -0.0025783459578130425
      ],
      [
        0.0014684040083752625,
        -0.0033201033491355235
      ]
    ],
    "direct_primary_difference_per_m": [
      -5.773159728050814e-15,
      2.1760371282653068e-14
    ],
    "disk_numerators": {
      "original": {
        "numerator": [
          -1.0267878219854842e-13,
          -6.739529908446373e-14
        ],
        "denominator_m4": 6.135923151542543e-07,
        "combined_absolute_numerator_sum": 1.2943234926167184e-13,
        "split_absolute_numerator_sum": 1.3341811042411258e-13,
        "cancellation_ratio": 1.053827026592577,
        "split_cancellation_ratio": 1.0862787502805353,
        "primary_gain_per_m": [
          -1.673403979525647,
          -1.0983726070219908
        ]
      },
      "correction": {
        "numerator": [
          -3.6683312119149835e-28,
          1.3308873733141208e-27
        ],
        "denominator_m4": 6.135923151542543e-07,
        "combined_absolute_numerator_sum": 2.8929824141755325e-27,
        "split_absolute_numerator_sum": 3.6891772791738e-27,
        "cancellation_ratio": 2.0955786819331754,
        "split_cancellation_ratio": 2.6723153318275834,
        "primary_gain_per_m": [
          -5.9784503836114406e-15,
          2.1690091946140846e-14
        ]
      },
      "corrected": {
        "numerator": [
          -1.026787821985488e-13,
          -6.73952990844624e-14
        ],
        "denominator_m4": 6.135923151542543e-07,
        "combined_absolute_numerator_sum": 1.2943234926167146e-13,
        "split_absolute_numerator_sum": 1.3341811042411202e-13,
        "cancellation_ratio": 1.0538270265925773,
        "split_cancellation_ratio": 1.0862787502805344,
        "primary_gain_per_m": [
          -1.6734039795256532,
          -1.0983726070219693
        ]
      }
    },
    "S_gain_per_m": 4.348754282901129,
    "identity_tolerance_per_m": 2.4719806122568166e-13,
    "linearity_identity_error_per_m": 2.1698718487761074e-16,
    "reconstruction_error_per_m": 0.0,
    "direct_reduction_errors_per_m": {
      "original": 2.220446049250313e-16,
      "correction": 3.1554436208840472e-30,
      "corrected": 3.1401849173675503e-16
    },
    "arithmetic_checks_passed": true,
    "absolute_disk_correction_per_m": 2.2498932366255684e-14,
    "absolute_physical_rotation_correction_per_s": 2.2498932366255682e-21,
    "correction_over_five_percent_scale": 6.51084228858469e-09
  }
}
```

## Exact runner

```python
"""R012 single response audit; run from repository root. Disposable instrumentation."""
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
WALL_S = 180.0
RSS_MIB = 1536.0
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path, value):
    temporary = Path(str(path) + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)

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


EXPECTED_SOURCES = {'realizability/__init__.py': '197df2cae0b7fcc3908afebfd9359b21244fc8aa0460b0167af04a2f1c7f219c', 'realizability/backends/__init__.py': '8b40aa33331d5a627dbd4aa1681f9da523a21e31e2b0e71f48203967481f20b2', 'realizability/backends/b1_verification.py': '287512f423a3c147c009802c2de9d6cf11538d3c80fc3fbc98dffaf586bb1e5c', 'realizability/backends/b2_coercivity.py': 'be10e484ffd5c36aef45962242dea2bcaaaa3cbad37df83e297fcc366bf96bcc', 'realizability/backends/b2_gate.py': '3151ac8a85de4b242e53b28a3d2815d7ecf5e8e6ed8c654f440aa5a8778a6d05', 'realizability/backends/b2_stability.py': '18b2e75712255a681a0c22f012d81ab3a129e147c41f3f8974bb46cf6a8df9f1', 'realizability/backends/b2_verification.py': '42e11041c5f1edbca13737010456247f059d92e874a9398454bf4b6f17498d25', 'realizability/backends/fem_observables.py': 'f5dbc8a47d2f5c61d9228daf49c80ae1011ab542ee12335398a52eaf89ed0a64', 'realizability/backends/fenicsx_stokes.py': '37ecd62121553e13f273fb99c7bc2649f51d9cea57658f4bce8069c4ac80a206', 'realizability/backends/hdiv_stokes.py': 'f23b252f91c406e3e279c7e6e7049e301ad604fae232dd0a610a73319864d2e9', 'realizability/boundary_modes.py': '586d2667b8ac4b6a460d590afc884a05be5f9843484df74de8a4568261f84d18', 'realizability/cli.py': 'c163e6a3dc8e6a2c08c7dc48a7205624947fce938dea1aec3489ef62135bd850', 'realizability/config.py': '3cb3edbb28e203226056cf4ac5e7832951c33e5f932b13a5ec438de88c786d12', 'realizability/observables.py': '428fd794b00669593f87b694bca10a94454ccbd9ee012fa656a61c7b30375a05', 'realizability/reference.py': '7f032634768a3f8b8a7a649e4d83dc45fd6f969a1c1ba679d1628867d2f13305', 'realizability/response.py': '5318e4d6ea917433909e6e9718c90ed9cf48a5ee4b779b4446b83b3452d71317', 'realizability/sensors.py': 'c93cd68cc902970f27ecdce7deb1d272f146890cfe99b076b87e190222483d9a', 'realizability/swirl_reference.py': '375e057ff365858cb5dc698e1b397eb34b18a9898d5a82482e2391ea11d81e4a', 'configs/realizability/pilot.json': '0e60a6ee85063f5d86b84db5af053f2166126249255edeafae4b4e6242db10d0'}

def verify_sources():
    actual = {path: sha(path) for path in EXPECTED_SOURCES}
    if actual != EXPECTED_SOURCES:
        raise RuntimeError('Pinned source/config identity mismatch')
    return actual


def capture_return(function, captured, *args, **kwargs):
    """Observe the unchanged helper's return frame; no assembly/BC edits."""
    if sys.getprofile() is not None:
        raise RuntimeError('An existing profiler would be overwritten')
    returns = []
    def observer(frame, event, value):
        if frame.f_code is function.__code__ and event == 'return':
            captured.update(frame.f_locals)
            returns.append(value)
    sys.setprofile(observer)
    try:
        result = function(*args, **kwargs)
    finally:
        sys.setprofile(None)
    if len(returns) != 1 or returns[0] is not result:
        raise RuntimeError('Helper capture count/return identity mismatch')
    return result


def calculate(output):
    sys.path.insert(0, str(Path.cwd()))
    started = time.monotonic()
    record = dict(schema_version=1, status='partial', stage='imports',
        campaign_ready=False, physical_gate_passed=False,
        solve_calls=0, correction_solve_calls=0, checked_mesh_reuses=0,
        limits=dict(total_wall_seconds=WALL_S, active_child_tree_rss_mib=RSS_MIB,
                    nominal_poll_seconds=POLL_S, local_cell_cap=500,
                    unchanged_dense_free_dof_cap=3000),
        failed_cell_locations=[], quadrature=[])
    def checkpoint(stage):
        record['stage'] = stage
        record['elapsed_child_seconds'] = time.monotonic() - started
        record['process_peak_rss_mib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        write_json(output/'report.json', record)
    checkpoint('imports')
    try:
        import inspect
        import numpy as np
        from dataclasses import asdict
        from dolfinx import fem
        from dolfinx.fem.petsc import assign
        from petsc4py import PETSc
        PETSc.Log.begin()
        from realizability.config import load_config
        from realizability.backends import hdiv_stokes as hdiv
        from realizability.backends import fenicsx_stokes as base
        from realizability.backends import fem_observables as obs
        from realizability.backends.b2_coercivity import calculate_local_bound, _classify
        from realizability.backends.b2_gate import _pde_diagnostics_passed
        from realizability.swirl_reference import disk_rotation_gain
        sources = verify_sources()
        config = load_config(Path('configs/realizability/pilot.json'))
        U = config.probe_velocity
        record['config'] = config.as_dict()
        record['versions'] = asdict(base.solver_versions())
        helper_source = inspect.getsource(base._block_direct_solve)
        (output/'pinned_helper.py').write_text(helper_source)
        record['provenance'] = dict(
            commit=subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
            worktree_status=subprocess.check_output(['git','status','--porcelain'], text=True),
            source_sha256=sources, runner_sha256=sha(__file__),
            direct_helper_sha256=sha(output/'pinned_helper.py'),
            python=sys.version)
        record['parameters'] = dict(mode='T_00c', frequency_hz=0.01,
            mesh_size_m=0.05, penalty_factor=96, disk_radius_m=0.025,
            phasor='exp(i omega t)', boundary_target='existing facet-consistent symbolic target',
            field_scale=U, matrix_rhs_scale='unit boundary speed; no rescaling of K or b',
            feature_order=['a_z','Omega','C_r4','S_r4','C_theta4','S_theta4'],
            gain_units=['1/m','1/m','dimensionless','dimensionless','dimensionless','dimensionless'])
        checkpoint('mesh_and_local_certificate')
        checked = base.create_cylinder(config, 0.05)
        domain, _, tags = checked
        V, Q = hdiv.create_hdiv_spaces(domain)
        cells = int(domain.topology.index_map(3).size_global)
        nv = int(V.dofmap.index_map.size_global * V.dofmap.index_map_bs)
        nq = int(Q.dofmap.index_map.size_global * Q.dofmap.index_map_bs)
        mesh_hash = base._mesh_sha256(domain)
        record['mesh'] = dict(cells=cells, velocity_dofs=nv, pressure_dofs=nq,
            mesh_sha256=mesh_hash)
        if (cells,nv,nq,mesh_hash) != (482,9522,1928,
                '423ab057c5738ae3e2dcef6e82c238ee7e61bc1d0af7f1e212d04b8a2cd6bfb4'):
            raise RuntimeError('Mesh identity mismatch before assembly')
        bound = calculate_local_bound(domain, max_cells=500)
        write_json(output/'local_bound.json', bound)
        record['certificate'] = {key:value for key,value in bound.items()
                                 if key != 'cell_trace_eigenvalues'}
        record['certificate']['classification'] = _classify(bound['C_upper'],96)
        if abs(bound['C_upper']/58.12657123078638 - 1) > 1e-10:
            raise RuntimeError('Local bound mismatch before assembly')
        if record['certificate']['classification']['status'] != 'certified_positive':
            raise RuntimeError('Alpha=96 certificate failed before assembly')
        def same_mesh(request_config, size):
            if request_config != config or size != 0.05 or record['checked_mesh_reuses']:
                raise RuntimeError('Unexpected mesh request')
            record['checked_mesh_reuses'] += 1
            if base._mesh_sha256(domain) != mesh_hash:
                raise RuntimeError('Checked mesh changed before assembly')
            return checked
        captured = {}
        original_direct = base._block_direct_solve
        def capture_direct(*args, **kwargs):
            if record['solve_calls']:
                raise RuntimeError('Second primal solve forbidden')
            record['solve_calls'] += 1
            if any(space.mesh is not domain for space in args[3]):
                raise RuntimeError('Assembly uses a different mesh')
            checkpoint('original_assembly_and_solve')
            return capture_return(original_direct, captured, *args, **kwargs)
        hdiv.create_cylinder = same_mesh
        hdiv._block_direct_solve = capture_direct
        checkpoint('harmonic_response')
        result, fields = hdiv.harmonic_response(config, 'T_00c', 0.01, 0.05,
                                               penalty_factor=96, _return_fields=True)
        record['solver'] = result.as_dict()
        record['pde_diagnostics_passed'] = _pde_diagnostics_passed(result)
        if not record['pde_diagnostics_passed']:
            raise RuntimeError('Existing PDE diagnostics failed; stop before interpretation')
        if result.mesh_sha256 != mesh_hash or record['checked_mesh_reuses'] != 1:
            raise RuntimeError('Returned mesh identity mismatch')
        K, b, x, ksp = (captured[name] for name in
                        ('matrix','vector','solution_vector','solver'))
        ns = captured['nullspace']
        null_vectors = captured['null_vectors']
        spaces = captured['spaces']
        assert captured['pressure_indices'] == (1,3)
        def residual(rhs, vector):
            value = rhs.copy()
            K.mult(vector, value)
            value.aypx(-1.0, rhs)
            return value
        def dots(vector):
            return [float(n.dot(vector)) for n in null_vectors]
        def residual_data(value, denominator):
            absolute = float(value.norm())
            return dict(absolute_norm=absolute,
                        relative_norm=absolute/max(float(denominator),np.finfo(float).tiny),
                        pressure_constant_dots=dots(value))
        r = residual(b,x)
        rhs_norm = float(b.norm())
        record['algebraic'] = dict(matrix_shape=list(K.getSize()),
            projected_rhs_norm=rhs_norm, projected_rhs_pressure_constant_dots=dots(b),
            original=residual_data(r,rhs_norm), original_reason=int(ksp.getConvergedReason()),
            solver_type=ksp.getType(), factor_solver=ksp.getPC().getFactorSolverType())
        if record['algebraic']['original']['relative_norm'] != captured['relative_residual']:
            raise RuntimeError('Captured/recomputed primal residual mismatch')
        null_checks = []
        for n in null_vectors:
            right, left = b.duplicate(), b.duplicate()
            K.mult(n,right)
            K.multTranspose(n,left)
            null_checks.append(dict(right_absolute_norm=float(right.norm()),
                                    left_absolute_norm=float(left.norm())))
        record['algebraic']['pressure_nullspace_checks'] = null_checks
        projected = r.copy()
        ns.remove(projected)
        removed = r.copy()
        removed.axpy(-1.0,projected)
        record['algebraic']['correction_rhs'] = residual_data(projected,float(r.norm()))
        record['algebraic']['correction_projection_removed'] = residual_data(removed,float(r.norm()))
        checkpoint('residual_correction')
        def factor_counts():
            return {name:int(PETSc.Log.Event(name).getPerfInfo()['count'])
                    for name in ('MatLUFactorSym','MatLUFactorNum','MatSolve')}
        counts_before = factor_counts()
        record['algebraic']['factor_counts_before_correction'] = counts_before
        factor_before = ksp.getPC().getFactorMatrix()
        factor_handle = factor_before.handle
        matrix_state = K.stateGet()
        dx = x.duplicate()
        record['correction_solve_calls'] += 1
        ksp.solve(projected,dx)
        counts_after = factor_counts()
        record['algebraic']['factor_counts_after_correction'] = counts_after
        corrected = x.copy()
        corrected.axpy(1.0,dx)
        correction_r = residual(projected,dx)
        corrected_r = residual(b,corrected)
        record['algebraic'].update(
            correction_reason=int(ksp.getConvergedReason()),
            correction_equation=residual_data(correction_r,float(projected.norm())),
            corrected_primal=residual_data(corrected_r,rhs_norm),
            same_factor_handle=bool(ksp.getPC().getFactorMatrix().handle == factor_handle),
            unchanged_matrix_state=bool(K.stateGet() == matrix_state))
        checkpoint('correction_completed')
        if not (record['algebraic']['correction_reason'] > 0
                and counts_before['MatLUFactorNum'] == counts_after['MatLUFactorNum'] == 1
                and counts_before['MatLUFactorSym'] == counts_after['MatLUFactorSym'] == 1
                and counts_after['MatSolve'] == counts_before['MatSolve'] + 1
                and record['algebraic']['same_factor_handle']
                and record['algebraic']['unchanged_matrix_state']
                and record['algebraic']['correction_equation']['relative_norm'] < 1e-9
                and record['algebraic']['corrected_primal']['relative_norm'] < 1e-9):
            raise RuntimeError('Correction self-consistency failed; stop before interpretation')
        def physical_fields(vector):
            pack = [fem.Function(space) for space in spaces]
            assign(vector,pack)
            back = vector.duplicate()
            assign(pack,back)
            if not np.array_equal(back.array,vector.array):
                raise RuntimeError('Exact block/field roundtrip failed')
            for f in pack:
                f.x.array[:] *= U
                f.x.scatter_forward()
            return tuple(pack)+(tags,)
        reconstructed = physical_fields(x)
        correction_fields = physical_fields(dx)
        corrected_fields = physical_fields(corrected)
        record['reconstruction'] = dict(exact_unit_block_roundtrips=True,
            original_physical_coefficients_equal=bool(all(
                np.array_equal(a.x.array,c.x.array) for a,c in zip(fields[:4],reconstructed[:4]))))
        if not record['reconstruction']['original_physical_coefficients_equal']:
            raise RuntimeError('Original/physical block reconstruction failed')
        np.savez(output/'coefficients.npz', original=x.array, correction=dx.array,
                 corrected=corrected.array, projected_rhs=b.array,
                 original_residual=r.array, correction_rhs=projected.array,
                 correction_equation_residual=correction_r.array, corrected_residual=corrected_r.array)
        reference = disk_rotation_gain(cylinder_radius=0.10, half_height=0.15,
            disk_radius=0.025, viscosity=1e-6, frequency_hz=0.01, terms=128)
        def pair(value):
            return [float(value.real),float(value.imag)]
        record['reference'] = dict(terms=128, gain_per_m=pair(reference),
            magnitude_per_m=abs(reference), physical_rotation_amplitude_per_s=U*abs(reference),
            five_percent_absolute_scale_per_m=0.05*abs(reference))
        if abs(reference-complex(2.0662858857221768e-5,-6.595106312048072e-5)) > 2e-18:
            raise RuntimeError('Independent reference identity mismatch')
        evaluate = obs.evaluate_function
        def checked_evaluate(function,points):
            try:
                values = evaluate(function,points)
            except RuntimeError as error:
                record['failed_cell_locations'].append(str(error))
                raise
            if not np.isfinite(values).all():
                raise RuntimeError('Nonfinite FEM point evaluation')
            return values
        obs.evaluate_function = checked_evaluate
        def features(pack, rule):
            value = obs.extract_complex_linear_features(pack, plane_order=rule[0],
                        radial_order=rule[1],angular_order=rule[2])/U
            if not np.isfinite(value).all():
                raise RuntimeError('Nonfinite signed features')
            return value
        rules = [(12,12,64),(18,18,96),(24,24,128),(48,48,256),(96,96,512)]
        originals = []
        for rule in rules:
            checkpoint('quadrature_'+ '_'.join(map(str,rule)))
            gain = features(fields,rule)
            originals.append(gain)
            primary = gain[1]
            magnitude_error = abs(abs(primary)-abs(reference))/abs(reference)
            phase_error = None if primary == 0 else abs(float(np.angle(primary/reference,deg=True)))
            record['quadrature'].append(dict(orders=list(rule),features_gain=[pair(g) for g in gain],
                absolute_complex_error_per_m=abs(primary-reference),
                relative_complex_error=abs(primary-reference)/abs(reference),
                relative_magnitude_error=magnitude_error, wrapped_phase_error_deg=phase_error,
                magnitude_passed=bool(magnitude_error < 0.05),
                phase_passed=bool(phase_error is not None and phase_error < 5),
                primary_absolute_change_from_previous_per_m=None if len(originals)==1 else
                    abs(primary-originals[-2][1])))
        for row,gain in zip(record['quadrature'],originals):
            row['primary_absolute_change_from_finest_per_m'] = abs(gain[1]-originals[-1][1])
        checkpoint('finest_correction_features')
        fine = rules[-1]
        delta_features = features(correction_fields,fine)
        corrected_features = features(corrected_fields,fine)
        reconstructed_features = features(reconstructed,fine)
        points,_,weights,_ = obs._polar_rule(0,0.025,fine[1],fine[2])
        denominator = float(np.sum(weights*(points[:,0]**2+points[:,1]**2)))
        assert denominator > 0
        disk_records = {}
        sample_arrays = dict(points=points,weights=weights)
        for name,pack in (('original',fields),('correction',correction_fields),
                          ('corrected',corrected_fields)):
            values = checked_evaluate(pack[0],points)+1j*checked_evaluate(pack[2],points)
            positive = weights*points[:,0]*values[:,1]
            negative = -weights*points[:,1]*values[:,0]
            contributions = positive+negative
            numerator = complex(np.sum(contributions.real),np.sum(contributions.imag))
            combined_absolute = float(np.sum(np.abs(contributions)))
            split_absolute = float(np.sum(np.abs(positive))+np.sum(np.abs(negative)))
            disk_records[name] = dict(numerator=pair(numerator),
                denominator_m4=denominator, combined_absolute_numerator_sum=combined_absolute,
                split_absolute_numerator_sum=split_absolute,
                cancellation_ratio=None if numerator==0 else combined_absolute/abs(numerator),
                split_cancellation_ratio=None if numerator==0 else split_absolute/abs(numerator),
                primary_gain_per_m=pair(numerator/denominator/U))
            sample_arrays[name+'_values'] = values
        S = sum(item['split_absolute_numerator_sum'] for item in disk_records.values())/denominator/U
        tolerance = 256*np.finfo(float).eps*S
        linearity = abs((corrected_features[1]-originals[-1][1])-delta_features[1])
        reconstruction_error = abs(reconstructed_features[1]-originals[-1][1])
        reduction_errors = {name:abs(complex(*disk_records[name]['primary_gain_per_m'])-g)
            for name,g in (('original',originals[-1][1]),('correction',delta_features[1]),
                           ('corrected',corrected_features[1]))}
        record['finest'] = dict(correction_features_gain=[pair(g) for g in delta_features],
            corrected_features_gain=[pair(g) for g in corrected_features],
            direct_primary_difference_per_m=pair(corrected_features[1]-originals[-1][1]),
            disk_numerators=disk_records, S_gain_per_m=S, identity_tolerance_per_m=tolerance,
            linearity_identity_error_per_m=linearity, reconstruction_error_per_m=reconstruction_error,
            direct_reduction_errors_per_m=reduction_errors,
            arithmetic_checks_passed=bool(max(linearity,reconstruction_error,*reduction_errors.values()) <= tolerance),
            absolute_disk_correction_per_m=abs(delta_features[1]),
            absolute_physical_rotation_correction_per_s=U*abs(delta_features[1]),
            correction_over_five_percent_scale=abs(delta_features[1])/(0.05*abs(reference)))
        np.savez(output/'finest_disk_samples.npz',**sample_arrays)
        if not record['finest']['arithmetic_checks_passed']:
            raise RuntimeError('Fixed arithmetic identity tolerance failed')
        verify_sources()
        record['status'] = 'complete'
        checkpoint('complete')
    except Exception as error:
        record['status'] = 'partial_failed'
        record['error'] = dict(type=type(error).__name__,message=str(error))
        checkpoint(record['stage'])
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--child',action='store_true')
    parser.add_argument('--self-check',action='store_true')
    args = parser.parse_args()
    if args.self_check:
        verify_sources()
        captured = {}
        def fixture():
            preserved = object()
            return preserved
        value = capture_return(fixture,captured)
        assert value is captured['preserved'] and sys.getprofile() is None
        self_check(args.output)
    elif args.child:
        calculate(args.output)
    else:
        verify_sources()
        args.output.mkdir(parents=True,exist_ok=False)
        for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
            os.environ[key] = '1'
        watch = monitor([sys.executable,str(Path(__file__).resolve()),'--child',
            '--output',str(args.output)],time.monotonic()+WALL_S,RSS_MIB,args.output/'calculation')
        write_json(args.output/'watch.json',watch)
        report_path = args.output/'report.json'
        report = read_json(report_path) if report_path.exists() else dict(status='partial_no_child_report')
        if watch['stop_reason'] or watch['returncode'] != 0:
            report['parent_stop'] = watch
            if watch['stop_reason']:
                report['status'] = 'partial_resource_or_process_stop'
            write_json(report_path,report)
        write_json(args.output/'manifest.json',{p.name:sha(p) for p in sorted(args.output.iterdir())
            if p.is_file() and p.name!='manifest.json'})
        print(json.dumps(dict(watch=watch,status=report['status'],stage=report.get('stage')),
                         indent=2,allow_nan=False),flush=True)
```

## Exact read-only evidence audit

```python
"""Read-only R012 evidence audit. No FEM imports, assembly, or solve."""
import ast
import hashlib
import json
import math
from pathlib import Path
import re
import numpy as np

root=Path.cwd()
base=Path('/tmp/navier-b2-response-r012')
evidence=base/'evidence'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    def reject(value): raise ValueError(value)
    return json.loads(p.read_text(),parse_constant=reject)
def close(a,b,rtol=2e-13,atol=0):
    assert abs(a-b) <= atol+rtol*max(abs(a),abs(b)),(a,b)
r=read(evidence/'report.json')
w=read(evidence/'watch.json')
manifest=read(evidence/'manifest.json')
for name,digest in manifest.items(): assert sha(evidence/name)==digest,name
assert r['status']=='complete' and r['stage']=='complete'
assert r['solve_calls']==r['correction_solve_calls']==r['checked_mesh_reuses']==1
assert r['campaign_ready'] is False and r['physical_gate_passed'] is False
assert r['pde_diagnostics_passed'] and r['finest']['arithmetic_checks_passed']
assert r['failed_cell_locations']==[]
assert w['returncode']==0 and w['stop_reason'] is None
assert w['elapsed_seconds']<180 and w['parent_observed_peak_rss_mib']<1536
assert r['process_peak_rss_mib']<1536 and w['maximum_sample_gap_seconds']<0.1
for path,digest in r['provenance']['source_sha256'].items(): assert sha(root/path)==digest
assert len(r['provenance']['source_sha256'])==19
assert sha(base/'runner.py')==r['provenance']['runner_sha256']
source=(root/'realizability/backends/fenicsx_stokes.py').read_text()
function=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='_block_direct_solve')
assert (evidence/'pinned_helper.py').read_text()==ast.get_source_segment(source,function)+'\n'
assert sha(evidence/'pinned_helper.py')==r['provenance']['direct_helper_sha256']
prior=(root/'docs/realizability/B2_ACCURACY_EVIDENCE.md').read_text()
prior_provenance=json.loads(re.search(r'### Provenance\n\n```json\n(.*?)\n```',prior,re.S).group(1))
assert prior_provenance['source_sha256']==r['provenance']['source_sha256']
assert r['mesh']==dict(cells=482,velocity_dofs=9522,pressure_dofs=1928,
 mesh_sha256='423ab057c5738ae3e2dcef6e82c238ee7e61bc1d0af7f1e212d04b8a2cd6bfb4')
bound=read(evidence/'local_bound.json')
assert len(bound['cell_trace_eigenvalues'])==482
assert all(math.isfinite(x) and x>0 for x in bound['cell_trace_eigenvalues'])
close(max(bound['cell_trace_eigenvalues']),bound['worst_cell_trace_eigenvalue'])
close(bound['C_upper'],58.12657123078638)
close(r['certificate']['classification']['beta'],1-math.sqrt((bound['C_upper']+1e-10*bound['C_upper'])/96))
assert r['certificate']['classification']['status']=='certified_positive'
algebra=r['algebraic']
assert algebra['factor_counts_before_correction']==dict(MatLUFactorSym=1,MatLUFactorNum=1,MatSolve=1)
assert algebra['factor_counts_after_correction']==dict(MatLUFactorSym=1,MatLUFactorNum=1,MatSolve=2)
assert algebra['same_factor_handle'] and algebra['unchanged_matrix_state']
for name in ('original','correction_equation','corrected_primal'):
    assert algebra[name]['relative_norm']<1e-9
coeff=np.load(evidence/'coefficients.npz')
for name in coeff.files:
    assert coeff[name].shape==(22900,) and np.isfinite(coeff[name]).all(),name
assert np.array_equal(coeff['original']+coeff['correction'],coeff['corrected'])
close(np.linalg.norm(coeff['projected_rhs']),algebra['projected_rhs_norm'])
for name,key,denominator in (
 ('original_residual','original',np.linalg.norm(coeff['projected_rhs'])),
 ('correction_equation_residual','correction_equation',np.linalg.norm(coeff['correction_rhs'])),
 ('corrected_residual','corrected_primal',np.linalg.norm(coeff['projected_rhs']))):
    close(np.linalg.norm(coeff[name]),algebra[key]['absolute_norm'])
    close(np.linalg.norm(coeff[name])/denominator,algebra[key]['relative_norm'])
close(np.linalg.norm(coeff['original_residual']-coeff['correction_rhs']),
      algebra['correction_projection_removed']['absolute_norm'])
rows=r['quadrature']
assert [x['orders'] for x in rows]==[[12,12,64],[18,18,96],[24,24,128],[48,48,256],[96,96,512]]
reference=complex(*r['reference']['gain_per_m'])
assert reference==complex(2.0662858857221768e-5,-6.595106312048072e-5)
gains=[complex(*row['features_gain'][1]) for row in rows]
scale=0.05*abs(reference)
for i,(row,gain) in enumerate(zip(rows,gains)):
    assert len(row['features_gain'])==6
    assert np.isfinite(row['features_gain']).all()
    close(row['absolute_complex_error_per_m'],abs(gain-reference))
    close(row['relative_complex_error'],abs(gain-reference)/abs(reference))
    close(row['relative_magnitude_error'],abs(abs(gain)-abs(reference))/abs(reference))
    close(row['wrapped_phase_error_deg'],abs(math.degrees(math.atan2((gain/reference).imag,(gain/reference).real))))
    assert row['magnitude_passed'] is False and row['phase_passed'] is False
    close(row['primary_absolute_change_from_finest_per_m'],abs(gain-gains[-1]))
    if i: close(row['primary_absolute_change_from_previous_per_m'],abs(gain-gains[i-1]))
samples=np.load(evidence/'finest_disk_samples.npz')
points,weights=samples['points'],samples['weights']
assert points.shape==(96*512,3) and weights.shape==(96*512,)
assert (weights>0).all()
D=math.fsum(weights*(points[:,0]**2+points[:,1]**2))
close(D,math.pi*0.025**4/2)
U=r['parameters']['field_scale']
S=0.0
for name,expected in (
 ('original',gains[-1]),
 ('correction',complex(*r['finest']['correction_features_gain'][1])),
 ('corrected',complex(*r['finest']['corrected_features_gain'][1]))):
    values=samples[name+'_values']
    assert values.shape==(96*512,3) and np.isfinite(values).all()
    positive=weights*points[:,0]*values[:,1]
    negative=-weights*points[:,1]*values[:,0]
    terms=positive+negative
    numerator=complex(math.fsum(terms.real),math.fsum(terms.imag))
    absolute=math.fsum(abs(positive))+math.fsum(abs(negative))
    S+=absolute/D/U
    close(expected,numerator/D/U,atol=r['finest']['identity_tolerance_per_m'])
    disk=r['finest']['disk_numerators'][name]
    close(disk['split_absolute_numerator_sum'],absolute)
    close(disk['cancellation_ratio'],math.fsum(abs(terms))/abs(numerator))
close(S,r['finest']['S_gain_per_m'])
close(256*np.finfo(float).eps*S,r['finest']['identity_tolerance_per_m'])
correction=complex(*r['finest']['correction_features_gain'][1])
corrected=complex(*r['finest']['corrected_features_gain'][1])
close(abs(corrected-gains[-1]-correction),r['finest']['linearity_identity_error_per_m'])
assert r['finest']['linearity_identity_error_per_m']<=r['finest']['identity_tolerance_per_m']
for folder in ('self-check','self-check-final'):
    check=read(base/folder/'self-check.json')
    assert check['timeout']['stop_reason']=='wall_time_limit'
    assert check['memory']['stop_reason']=='rss_limit'
    assert check['memory']['largest_observed_process_tree']>=2
result=dict(status='passed',scope='stored evidence only; no PDE work',
    manifest_files=len(manifest),source_config_identities=19,
    local_trace_values=482,coefficient_arrays=len(coeff.files),
    signed_feature_values=5*6,finest_disk_sample_sets=3,
    disk_points_per_set=96*512,
    physical_rotation_amplitude_per_s=U*abs(gains[-1]),
    amplitude_ratio_to_reference=abs(gains[-1])/abs(reference),
    finest_quadrature_step_over_scale=abs(gains[-1]-gains[-2])/scale,
    default_to_finest_over_scale=abs(gains[1]-gains[-1])/scale,
    largest_to_finest_over_scale=max(abs(x-gains[-1]) for x in gains)/scale,
    finest_absolute_error_over_scale=abs(gains[-1]-reference)/scale,
    maximum_quadrature_gain_pair_distance=max(abs(a-b) for a in gains for b in gains),
    finest_reference_phase_deg=math.degrees(math.atan2(gains[-1].imag,gains[-1].real)))
(base/'numerical-validation.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(result,indent=2))
```
