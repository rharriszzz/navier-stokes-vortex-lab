# R020 pressure compatibility stop: evidence index

Read the [result and next bounded task](B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md).
One physical child stopped before A_32's solve. No matched-trace solution is
present in these artifacts.

- [Preflight](evidence/r020/preflight.json) and
  [review script](evidence/r020/preflight_review.py) verify 19 production files,
  358 historical evidence files and seven unchanged R019 runner/support sources.
- [Physical runner](evidence/r020/physical.py),
  [parent](evidence/r020/run_contract.py),
  [block RHS fixtures](evidence/r020/block_rhs_toys.py),
  [wrapper fixtures](evidence/r020/wrapper_toys.py),
  [watchdog](evidence/r020/toy_runner.py), [kernels](evidence/r020/kernels.py),
  and [disk integrator](evidence/r020/disk.py) are the exact executed copies.
- [Fresh prerequisite report](evidence/r020/toys/report.json),
  [wrong-root refusal](evidence/r020/toys/wrong-root/toy-repair-report.json),
  [watchdog checks](evidence/r020/toys/watchdog/self-check.json),
  [kernels](evidence/r020/toys/kernels/toy-report.json),
  [wrapper](evidence/r020/toys/wrapper/toy-repair-report.json),
  [block RHS](evidence/r020/toys/block-rhs/block-rhs-report.json), and
  [disk fixtures](evidence/r020/toys/disk/extra-toys.json) passed within their caps.
- [Physical report](evidence/r020/physical/report.json),
  [traceback](evidence/r020/physical/physical.stderr),
  [watchdog](evidence/r020/physical/watch.json) and
  [launch record](evidence/r020/physical/launch.json) preserve the one attempt.
- [Local bound](evidence/r020/physical/local_bound.json),
  [disk partition](evidence/r020/physical/disk_regions.json),
  [A_32 facets](evidence/r020/physical/A_32_facets.json) and
  [A_64 facets](evidence/r020/physical/A_64_facets.json) reproduce R016's saved data,
  apart from the local bound's elapsed time.
- [Post-stop review](evidence/r020/poststop_review.json) and its
  [standard-library calculation](evidence/r020/poststop_review.py) relate saved
  A_32 flux to pressure products and record all skips. They perform no FEM work.
- Reaudits of [R016](evidence/r020/reaudit-r016-stored_validation.json),
  [R017](evidence/r020/reaudit-r017-validation.json),
  [R018](evidence/r020/reaudit-r018-validation.json) and
  [R019](evidence/r020/reaudit-r019-validation.json) passed after the
  [historical-log correction](evidence/r020/continuity_correction.json).
  Their generated writes were captured here; old archives were not rewritten.
- [Archive script](evidence/r020/archive.py) and
  [manifest](evidence/r020/archive_manifest.json) preserve 72 artifacts with
  original and archived hashes. Only the facet JSON whitespace was compacted;
  parsed values are identical. The subsequently added
  [audit](evidence/r020/audit.py) and [validation](evidence/r020/validation.json)
  are outside that execution manifest.

Run `python3 docs/realizability/evidence/r020/audit.py` from the repository root
to audit saved evidence. The historical parent/child sources are records, not
authorization to rerun the physical attempt. The working directory was
`/tmp/navier-b2-matched-r020/`, with the repository root as subprocess cwd,
serial MPI and single-thread numerical libraries in the approved environment.
The parent exited normally while reporting `partial_failed`; its exit code
alone does not indicate a successful experiment.

The report retains P's primary/corrected numerators, denominator and gain,
all six signed features under both original rules, projection/flux records,
A_32 block layout and compatibility products, actual solve/factor counts,
and resource records. Feature gain order is
`[a_z, Omega, C_r4, S_r4, C_theta4, S_theta4]`, with units
`[1/m, 1/m, dimensionless, dimensionless, dimensionless, dimensionless]`
after division by `U=1e-7 m/s`. No solution coefficient vectors, A gains,
A_64 RHS compatibility or paired output differences were saved or inferred.
