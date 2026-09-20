# R018 prerequisite stop: evidence index

Recorded for [R018](../../REQUEST_LOG.md#r018--2026-09-20--short-continuation-request).
Read the [result and next task](B2_MATCHED_TRACE_PREFLIGHT_RESULT.md).
No physical child was launched.

- [Static review and source identities](evidence/r018/preflight.json),
  [review script](evidence/r018/preflight_review.py), and
  [post-stop record](evidence/r018/poststop_review.json).
- [Exact parent](evidence/r018/run_contract.py),
  [unchanged R017 physical runner](evidence/r018/physical.py), and
  [wrapper toy with the path assumption](evidence/r018/wrapper_toys.py).
  The sibling block RHS, kernel, disk and watchdog sources are also archived.
- [Aggregate prerequisite report](evidence/r018/toys/report.json),
  [wrapper traceback](evidence/r018/toys/wrapper.stderr),
  [kernel report](evidence/r018/toys/kernels/toy-report.json), and
  [synthetic watchdog results](evidence/r018/toys/watchdog/self-check.json).
- [Re-executed R016 audit](evidence/r018/reaudit-r016-stored_validation.json)
  and [R017 audit](evidence/r018/reaudit-r017-validation.json).
  Historical audit writes were captured in the R018 directory; the old archives
  were not rewritten. These are checks of saved data, not FEM reruns.
- [Archive script](evidence/r018/archive.py) and
  [manifest](evidence/r018/archive_manifest.json) preserve 29 exact artifacts,
  with original and archived hashes. No JSON whitespace compaction was needed.
- [Standard-library audit](evidence/r018/audit.py) and
  [validation report](evidence/r018/validation.json), added after the execution
  manifest, check source/evidence identities, finite values, stop evidence,
  resource accounting and documentation.

The original work directory is `/tmp/navier-b2-matched-r018/`. Parent commands
are recorded in each watchdog. Scripts were invoked from the repository root
using `/tmp/navier-fenicsx/bin/python` in the approved MPI environment, with
single-thread numerical libraries. The parent returned normally with a JSON
status of `prerequisite_refused`; its exit code alone does not indicate success.
The wrapper child returned 1 before creating its own report. Missing child JSON
is recorded explicitly, rather than replaced with fabricated numerical output.

Run `python3 docs/realizability/evidence/r018/audit.py` from the repository root
to audit saved artifacts only. Do not rerun the historical parent or child
scripts to recreate outputs. There is no physical launch record, mesh,
factorization, coefficient vector, pressure check or new gain in this archive.
The next bounded task is toy-only and is specified in the result.

The exact copied `toy_runner.py` retains its historical trailing blank line
at EOF (line 213). That whitespace exception preserves its executed bytes;
the whole-archive default whitespace check must not be reported as passed.
