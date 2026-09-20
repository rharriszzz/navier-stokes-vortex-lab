# R019 toy portability evidence index

Read the [result and next task](B2_TOY_PORTABILITY_RESULT.md). The successful
run was toy-only; no physical child was launched.

- [Final disposable parent and child sources](evidence/r019/run_contract.py),
  [wrapper toy](evidence/r019/wrapper_toys.py), [support runner](evidence/r019/toy_runner.py),
  and [pinned preflight identities](evidence/r019/preflight.json). The unchanged
  block-RHS, kernel, disk and physical child sources are archived alongside them.
- [Complete parent report](evidence/r019/toys/report.json),
  [wrong-root finite refusal](evidence/r019/toys/wrong-root/toy-repair-report.json),
  [watchdog results](evidence/r019/toys/watchdog/self-check.json), and successful
  [kernel](evidence/r019/toys/kernels/toy-report.json),
  [wrapper](evidence/r019/toys/wrapper/toy-repair-report.json),
  [block RHS](evidence/r019/toys/block-rhs/block-rhs-report.json), and
  [disk](evidence/r019/toys/disk/extra-toys.json) reports.
- [Parent refusal input](evidence/r019/parent-refusal/input-report.json) and
  [finite no-child result](evidence/r019/parent-refusal/report.json) record the
  parent's behavior when prerequisites fail.
- The four incomplete [disposable launch attempts](evidence/r019/attempts/)
  retain the output collision and sandbox MPI/UCX failures; they are included in
  cumulative timing and resource accounting.
- [Audit script](evidence/r019/audit.py),
  [archive manifest](evidence/r019/archive_manifest.json), and
  [validation report](evidence/r019/validation.json) verify 19 production
  identities, archived runner identities, finite JSON, refusal counts, parent
  refusal, the five passing phases and cumulative limits.

Run `python3 docs/realizability/evidence/r019/audit.py` from the repository root
to audit stored evidence only. Do not rerun the historical parent or child
launches to recreate these records. The source copies are exact disposable
scripts; only the wrapper and parent harness changed for this toy task.
