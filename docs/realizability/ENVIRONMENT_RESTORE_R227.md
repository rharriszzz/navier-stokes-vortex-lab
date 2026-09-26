# R227–R228 — Exact environment restoration attempt

**Restoration is incomplete.** The bounded setup reached all 338 selected package
records, then the installer exceeded its 65-second subdeadline. Its remaining
children caused the completion snapshot to refuse; the supervisor stopped the
unit and confirmed cleanup. `/tmp/navier-fenicsx` is a retained **partial,
unvalidated prefix**, not a runnable FEM environment. Zero numerical attempts
were granted or spent; no FEM workload or numerical import was requested by
the setup/verification code. The standalone target-interpreter check was not
reached. Installer helpers were not instrumented for their own import tracing.

R228 asked whether the current step had finished and requested continued work.
The existing R227 step continued through reconciliation and publication, with
no new installation attempt or reset allocation. The source-bound checkout was
left unchanged until the running worker stopped; then R228 was appended.

## Allocation, source and observations

STARTED publication: d170ae5 after clean synchronization at 669d2a0. The
[finite restoration procedure](evidence/r227/restore.py) and allocation were
published as `6cf892caa079a6a82521a476d1fd61db5e5aff2d`; both held workers verified
that clean source and the actual project interpreter before release. It uses
the unchanged R226 launcher and disclosed R103 caller/OS-manager trust boundary.

Initial cache inventory found 337 extracted package records and twelve of the
thirteen direct pins. The manager executable and old prefix were absent.
`python-gmsh` was not cached. The petsc4py py310 build's payload was ABI3 and its
metadata allowed CPython >=3.10, so the filename alone was not a Python 3.12
incompatibility. No package pin was changed.

The pre-recorded setup allocation was bootstrap <=60 s (manager expiry 49+1 s),
then resolve/install <=180 s (149+1 s expiry), within a 900 s setup wall window
including intervening review. Both units observed memory.max=1536 MiB, swap=0,
pids.max=32 and one-thread settings before release. Numerical budgets are
separate and unchanged. Only these two phases ran; no retry was made.

| Phase | Observed result |
|---|---|
| Bootstrap | Micromamba 2.9.0 downloaded from the official Linux endpoint; archive and executable hashes saved. Actual worker exit 0 and empty cleanup. 2.155504145 s through result save; pre-exit snapshot 67,821,568 bytes / 5 tasks peak, zero limit/OOM events. |
| Resolve/install | Exact-version plan passed; 338 packages selected. Its FETCH plan listed 48 artifacts / 377,962,800 bytes, not a measurement of transferred bytes. Installation timed out at its 65 s subdeadline. Worker finished with descendants, so no resource snapshot/actual worker-exit success was accepted. Cleanup empty, unknown_children=false. Phase 73.649600392 s through result save. |

The observed phase sum is 75.805104537 s. Bootstrap entry through installation
result save, including the intervening gap, is 105.012757848 s. The attempt still
failed. Later read-only reconciliation was at an observed 4641.794490448 s since
bootstrap entry; do not label that later work a success inside the 900 s window.
Final stdout/return tails are unmeasured. Installation peak memory/PID counters
and completed interpreter-verification records are unavailable, not zero.
Both exact cgroups and the observed worker PIDs were also absent at the later
check. R225/R226 evidence and charges remain unchanged.

## What the partial prefix establishes

[Metadata reconciliation](evidence/r227/partial_metadata.json), produced by the
[read-only inspector](evidence/r227/inspect_partial.py), found:

- All 338 planned records present, with no version/build mismatch or unexpected
  record. All thirteen direct versions equal environment-b1.yml. PETSc is real,
  and MPICH remains selected. Full build/URL/digest inventory is retained.
- Of 76,252 file entries, 972 are missing; all are `.pyc` bytecode entries.
  No non-bytecode file entry was missing in that check. This is file-presence
  evidence, not a complete file-content or ABI validation.
- `conda-meta/history` is empty. Installer success and its required postconditions
  were never recorded. The target Python binary exists and was hashed, but it
  received no standalone identity/version check; package metadata alone does not
  verify the interpreter. Installer helper execution is a separate, untraced fact.
- FFCx's Conda record is 0.10.1 / pyhbc3ee6d_1 while embedded distribution metadata
  is 0.10.0. This is the already documented R056 discrepancy: the official
  [v0.10.1 source](https://raw.githubusercontent.com/FEniCS/ffcx/v0.10.1/pyproject.toml)
  still declares 0.10.0. Preserve artifact identity and runtime strings separately.

Missing bytecode and unfinished history are consistent with late installation
work being interrupted. The exact descendant command was not retained, so this
is an inference, not proof that bytecode compilation caused the timeout.
The current worker's strict `ffcx.__version__ == 0.10.1` check will need an
explicit artifact-aware admission review before FEM release; do not lower the
package pin or silently bypass all version checks. No worker code was changed.

The [check ledger](evidence/r227/checks.json) hashes the source and retained raw
phase files. The explicit package list, solver JSON, stdout/stderr, handshakes,
failed task message and cleanup results are preserved under `evidence/r227/run`.
Large binaries/cache/prefix remain local. Micromamba is at
`/tmp/navier-r227-restore/bin/micromamba`; the package cache is
`/home/rharris/.local/share/mamba/pkgs`. Existing environments were not modified;
the cache gained artifacts. The pre-existing environment registry already named
this prefix, so its entry is not evidence that this transaction completed.
Source AST, metadata consistency, artifact hashes, JSON, links, prior-log
preservation and Git checks apply. Numerical/full-suite tests are skipped.

## Concrete next task

On a later **Continue**, Sol/high performs **one newly allocated offline recovery
transaction from the saved explicit package list into a new prefix**, retaining
this partial prefix and failed evidence. Use the verified cached manager and
artifacts; check their hashes first. Disable eager bytecode compilation with
micromamba's documented-in-local-help `--no-pyc` option. Do not skip link scripts,
change pins, repeat the solver, redownload opportunistically or erase history.
Use the same 180 s observed / <=150 s independent worker / 1536 MiB / no swap /
32 tasks limits; remove the now-unneeded solver reservation from the internal
time division. Record the new allocation before launch, and stop on failure.

Require actual transaction success, nonempty committed history, exact records,
required files, isolated Python -I -S identity/version/hash and confirmed cleanup.
Keep missing optional bytecode distinct from required source/binary files.
Stop before any numerical import or FEM execution. Then recommend Astra/high
for artifact-aware FFCx version handling and separate one-fixture admission.
Follow the single [handoff task](../../SESSION_HANDOFF.md#next-task).
[Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-sol)
was searched/opened again; Sol supports high reasoning. This task-fit choice is
judgment, not account-access verification. No model/session switch occurred.

Primary setup references: [Micromamba installation](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html)
and [user guide](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html).
The downloaded executable's exact create-help output is retained with the run.
No new scientific result, B2 pass, q64/q96 use, R021 integration, hardware work
or Mac ownership transfer is claimed.
