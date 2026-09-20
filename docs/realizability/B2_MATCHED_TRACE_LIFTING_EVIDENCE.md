# R016 matched-trace attempt: evidence index

Recorded 2026-09-20 for [R016](../../REQUEST_LOG.md#r016--2026-09-20--short-continuation-request).
Read the [result and next bounded task](B2_MATCHED_TRACE_LIFTING_RESULT.md).
The attempt stopped during A_32 RHS lifting after the P solve, one correction
and P output checks. No matched-trace solution exists in these artifacts.

## Exact code and provenance

- [Physical runner](evidence/r016/physical.py),
  [load/moment kernels](evidence/r016/kernels.py),
  [disk integrator](evidence/r016/disk.py),
  [toy support/watchdog](evidence/r016/toy_runner.py), and
  [wrapper fixtures](evidence/r016/wrapper_toys.py) match R015 byte for byte.
- [R016 parent](evidence/r016/run_contract.py) enforces the shared toy budget,
  validates prerequisites and refuses a second physical launch into the same
  directory. The [initial parent](evidence/r016/run_contract_initial.py) is
  preserved before the narrowly scoped sandbox-import recovery was added.
- [Preflight](evidence/r016/preflight.json) records the base commit, exact code
  and 19 source identities, and static review. The
  [post-stop review](evidence/r016/poststop_review.json) records only saved-data
  arithmetic and the static traceback/API diagnosis, including installed-source
  hashes. It is not a new numerical experiment.

These are historical disposable artifacts, not an approved rerun command.
The working directory was `/tmp/navier-b2-matched-r016/`. Child scripts assume
the repository as working directory and import sibling files. Read the current
handoff before using them; the next task is toy-only.

## Execution evidence

- [Physical partial report](evidence/r016/physical/report.json),
  [traceback](evidence/r016/physical/physical.stderr),
  [watchdog](evidence/r016/physical/watch.json), and
  [launch record](evidence/r016/physical/launch.json).
- [Local certificate](evidence/r016/physical/local_bound.json),
  [disk regions](evidence/r016/physical/disk_regions.json), and
  [A_32](evidence/r016/physical/A_32_facets.json)/
  [A_64](evidence/r016/physical/A_64_facets.json) normal projections and fluxes.
- [Aggregate toy report](evidence/r016/toys-approved/report.json),
  [kernel fixtures](evidence/r016/toys-approved/kernels/toy-report.json),
  [wrapper fixtures](evidence/r016/toys-approved/wrapper/toy-repair-report.json),
  [extra disk fixtures](evidence/r016/toys-approved/disk/extra-toys.json), and
  [watchdog self-check](evidence/r016/toys-approved/watchdog/self-check.json).
- [Initial sandbox report](evidence/r016/toys/report.json) and
  [MPI import error](evidence/r016/toys/kernels.stderr). The failed process
  never reached numerical checks; its time remains in the 60-second toy total.

The [manifest](evidence/r016/archive_manifest.json) covers 48 exact execution,
code and review artifacts. The two facet JSON files use compact whitespace
with identical parsed values; original and archived hashes are both recorded.
Empty output logs are retained. The stored-data and documentation validators
and their reports were added afterward and are not entries in that execution
manifest.

## Stored-data validation

Run `python3 docs/realizability/evidence/r016/audit.py` from the repository.
The [audit](evidence/r016/audit.py) uses only the standard library and writes
its [validation record](evidence/r016/stored_validation.json). It checks stored
identities and arithmetic without any FEM imports or physical recalculation.
The audit passed for prior evidence, projection equations, disk partition,
completed P measurements, resource records and the mandatory stop.
The [documentation check](evidence/r016/check_docs.py) and its
[report](evidence/r016/documentation_validation.json) verify local links,
anchors, fences, Python syntax and preservation of earlier request history.

The report preserves P's normalized numerator (m³), denominator (m⁴), gain
(1/m), coordinate/velocity scales, three sets of reconstruction checks,
independent arc differences, all six signed features under both original rules,
and actual factor/solve counts. It does not contain velocity coefficient vectors
or A compatibility/output data. Missing stages are not represented as passing.
Each `polar[].gains` array uses the fixed order
`[a_z, Omega, C_r4, S_r4, C_theta4, S_theta4]`, with complex values stored as
`[real, imaginary]`. Division by `U=1e-7 m/s` gives gain units
`[1/m, 1/m, dimensionless, dimensionless, dimensionless, dimensionless]`.
The corresponding unnormalized feature units are s⁻¹ for strain/rotation
and m/s for the four signed perturbation coefficients.

The staged whitespace check reports the historical blank line at EOF in
`toy_runner.py:213` and trailing spaces in the raw MPI traceback at
`toys/kernels.stderr:3`, `:4` and `:5`. These four warnings are retained to
preserve exact executed code and captured error bytes. All other staged files
pass; the default whole-archive whitespace check does not pass.
