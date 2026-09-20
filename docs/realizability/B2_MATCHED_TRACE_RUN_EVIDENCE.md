# R014 matched-trace attempt: evidence index

Recorded 2026-09-20 for [R014](../../REQUEST_LOG.md#r014--2026-09-20--short-continuation-request).
Read the [partial result and next task](B2_MATCHED_TRACE_RESULT.md).
The experiment stopped on a wrapper exception after one original-command solve.
There are no matched-trace gains or residual-correction results.

## Exact disposable implementation

- [Physical runner](evidence/r014/physical.py), including the failed comparison
  and later unexecuted code.
- [Original toy runner and watchdog](evidence/r014/toy_runner.py).
- [Oriented facet projection/load and circle moments](evidence/r014/kernels.py).
- [Disk partition, quadratic restriction and output code](evidence/r014/disk.py).

These are historical experiment artifacts, not a production backend or approved
rerun command. The original working directory was
`/tmp/navier-b2-matched-r014/`, with `attempt/` and `physical_attempt/` outputs.
Scripts import sibling files and the repository package; their original parent
commands and temporary paths are retained in the watch records. Reproducing the
failed physical attempt requires a new bounded contract; do not rerun it merely
to recreate temporary files. The next task repairs instrumentation on toys only.
That bounded repair is complete in [R015](B2_MATCHED_TRACE_WRAPPER_REPAIR.md);
no physical retry followed.

## Reports and reproducibility records

- [Complete partial physical report](evidence/r014/physical__report.json),
  [traceback](evidence/r014/physical__physical.stderr), and
  [physical watchdog](evidence/r014/physical__watch.json).
- [Toy report](evidence/r014/toy__toy-report.json),
  [first toy watchdog](evidence/r014/toy__toy-watch.json),
  [additional toy report](evidence/r014/physical__extra-toys.json), and
  [additional toy watchdog](evidence/r014/physical__extra-toys-watch.json).
- [Synthetic watchdog validation](evidence/r014/toy__watchdog__self-check.json).
- [Local certificate with 482 cell values](evidence/r014/physical__local_bound.json)
  and [11 disk regions and their moments](evidence/r014/physical__disk_regions.json).
- [A_32 facet projection/flux data](evidence/r014/physical__A_32_facets.json) and
  [A_64 facet projection/flux data](evidence/r014/physical__A_64_facets.json).

The [archive manifest](evidence/r014/archive_manifest.json) identifies 27 exact
code/report/log artifacts. Original and archived SHA-256 values match except
for whitespace compaction of the two facet JSON files; every parsed value is
preserved. The original child manifests are also archived and refer to their
original temporary filenames/bytes. Empty stdout/stderr records are retained
so those manifests can be checked without implying missing output.

## Read-only validation

The [audit script](evidence/r014/audit.py) and its
[result](evidence/r014/stored_validation.json) check stored identities and
arithmetic. Run from the repository root with
`python3 docs/realizability/evidence/r014/audit.py`. It uses only the standard
library, writes its validation JSON, and performs no FEM import, mesh, reference
evaluation, assembly, solve or field reintegration. If original temporary files
remain, their hashes and parsed JSON values are checked as well.

The archive manifest predates the audit and therefore does not list the audit
or its result. Documentation validation, including those two files, is recorded
in `REQUEST_LOG.md`; no missing physical checks are represented as passed.
