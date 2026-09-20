# R022 compatible-trace prerequisite evidence

Read the [result and next bounded task](B2_COMPATIBLE_TRACE_PREFLIGHT_RESULT.md).
This archive records a toy resource refusal, not a physical response result.

- [Identity manifest](evidence/r022/identities.json): 19 production pins and
  440 prior evidence files; [redirected R021 validation](evidence/r022/reaudit-r021-validation.json).
- [Static preflight](evidence/r022/preflight.json): final disposable source
  hashes and original experiment limits; its pass means static review only.
- [Physical runner](evidence/r022/physical.py),
  [pre-solve observer](evidence/r022/presolve.py) and
  [new tests](evidence/r022/advanced_toys.py): implemented; actual observer and
  physical execution were not reached.
- [Parent](evidence/r022/run_contract.py), [watchdog/kernel runner](evidence/r022/toy_runner.py),
  [projection kernel](evidence/r022/kernels.py), [disk kernel](evidence/r022/disk.py),
  [wrapper toys](evidence/r022/wrapper_toys.py) and [lifting oracle](evidence/r022/block_rhs_toys.py).
- [First attempt](evidence/r022/attempts/attempt-01/toys/report.json),
  [wrapper traceback](evidence/r022/attempts/attempt-01/toys/wrapper.stderr),
  [initial physical source](evidence/r022/attempts/attempt-01/physical.py) and
  [cumulative budget record](evidence/r022/toy_budget.json): reporting defect,
  corrected before the second attempt.
- [Second attempt and watchdog records](evidence/r022/toys/report.json),
  [last advanced checkpoint](evidence/r022/toys/advanced/advanced-report.json),
  [actual parent-refusal probe](evidence/r022/toys/parent-refusal/refused/report.json):
  16 high-order facet passes, then 513.61 MiB RSS stop before observer cases.
- [Post-stop cache metadata](evidence/r022/cache_metadata.json): read-only
  context for a possible compiler contribution; not per-process memory proof.
- [Derived result](evidence/r022/result.json) and [derivation script](evidence/r022/poststop.py):
  saved-data-only resource and coverage summary.
- [Archive script](evidence/r022/archive.py) and [artifact manifest](evidence/r022/archive_manifest.json):
  86 exact execution artifacts mapped to 79 files, sharing identical support
  sources. Every initial and final source is recoverable from that mapping.
- [Audit](evidence/r022/audit.py) and [validation](evidence/r022/validation.json):
  source/evidence preservation, finite data, syntax and documentation checks.

From the repository root, these commands operate on saved data only:

```bash
python3 docs/realizability/evidence/r022/poststop.py
python3 docs/realizability/evidence/r022/audit.py
git diff --check
```

The archive script is for the recorded disposable directory and is not a test
runner. Historical execution scripts are evidence, not authorization to rerun
numerical work. No physical child was launched during R022; the experiment
requires completion of the separately bounded toy follow-up first.
