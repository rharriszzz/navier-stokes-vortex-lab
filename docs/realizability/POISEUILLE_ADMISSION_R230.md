# R230 — One later Poiseuille fixture admitted

**The existing environment is admitted for one separately authorized, bounded
n=2 Poiseuille attempt on PC/WSL daisy. No numerical attempt ran in this review.**
The artifact-bound FFCx gate is implemented in both worker and result validation.
The complete manufactured convergence suite, rotation case, tank and B2 campaign
remain unadmitted. The frozen proposal still grants zero suite attempts; this
review grants one separate single-fixture allocation, with zero spent.

## Environment decision

[R229](ENVIRONMENT_RECOVERY_R229.md) completed the exact transaction, archive
hash verification, installed-record comparison, required-file inventory,
committed history and isolated Python 3.12.13 identity check. Installer and
worker exited zero; cleanup was confirmed. Its top-level setup result remains
**false**: 303 memory.max events at 1536 MiB, without OOM/kill. Prior setup
charges and the old partial `/tmp/navier-fenicsx` remain unchanged.

Reuse is justified by those completed artifact postconditions, not by treating
resource refusal as success. The saved counters establish pressure at the ceiling, but do not identify
whether anonymous memory or file cache caused it. We neither attribute the cause nor estimate a
FEM footprint. The independent numerical attempt must satisfy its own unchanged
zero-memory-event gate. A setup workload and a tiny fixture have different work;
there is no evidence that the fixture will fit, and that uncertainty is accepted
only within the enforced caps and single-attempt stop rule.

R230 read the retained evidence and current FFCx record/source metadata, confirmed
prefix/interpreter-file presence, and observed the recorded R229 PID 140105 and
cgroup absent. All 17 R229 ledger hashes match. No new environment verification
scope, interpreter execution, archive scan, installation or numerical import was
run. Existing metadata/file-presence evidence does not prove every ABI or installed
byte; this follows R103's ordinary owner/OS trust, not hostile-writer protection.
Actual package imports and API behavior remain tests for the admitted attempt.

## Exact FFCx handling

The pinned package remains `fenics-ffcx 0.10.1 pyhbc3ee6d_1`, conda-forge/noarch,
SHA-256 `727926ec2782375707cd036f86ab3d5004d53074ee80cf127619134f763e3473`.
The [upstream v0.10.1 source](https://raw.githubusercontent.com/FEniCS/ffcx/v0.10.1/pyproject.toml)
was opened again and still declares 0.10.0; installed distribution metadata uses
that version, and `ffcx.__version__` reads distribution metadata.

[package_identity.py](../../verification/nonlinear_port/package_identity.py)
requires the exact name, package version, build, subdir, URL, SHA-256 and MD5,
plus checksummed R229 archive-verification and installation-verification records.
Inside the released worker it checks the Conda record, listed module/metadata
files, prefix containment and unique expected embedded name/version. The imported
FFCx module must resolve to that prefix's checked module location. It then accepts
**only runtime 0.10.0 for this exact artifact**. The saved `actual_versions.ffcx`
remains the observed 0.10.0; `ffcx_artifact.package.version` remains 0.10.1.
The result reader uses the same gate and requires the provenance evidence.
Other runtime pins and all numerical/resource/raw-result checks are retained.
This is not a general allowance for any 0.10.0 installation or another build.

Fifty-six tests passed in 0.570 s under project Python 3.12.14; the numerical
module import audit passed. Seven new tests exercise synthetic installed files,
missing/changed recovery records, every wrong artifact field, unexpected embedded
versions, duplicate metadata versions, external symlinks, runtime/origin mismatch,
raw-result omissions and the real worker import wiring with fake modules.
The real FFCx module was not imported. All 23 prototype Python files parse.
[Check record and reviewed source inventory](evidence/r230/checks.json).

## One-use execution contract

A later explicit **Continue** authorizes execution of this one allocation. This
review stops before creating a run reservation or executable admission record.
The source/manifest and interpreter conditions below are mandatory at launch:

- Owner: PC/WSL daisy, same checkout, normal clean synchronization and published
  lifecycle STARTED first. Read the current request/lifecycle log to ensure the
  allocation has not already been reserved, spent or left unresolved. A missing
  `/tmp` directory does not reset a logged attempt.
- Exactly one absolute output directory: `/tmp/navier-poiseuille-r230-once`.
  Never change its name to retry. Any reservation/partial start consumes this
  allocation; preserve incomplete results and stop. No automatic retry.
- Verify the source hashes in `evidence/r230/checks.json` and the frozen manifest
  SHA-256 `7a8bda917e6b46994ad24c68e0b6c6013b7d6776f90c86a6de763f31f52fa558`.
  Bind the actual clean launch commit to both admission and reservation. Later
  log/status-only commits may differ from R230's delivery commit, but reviewed
  executable source and manifest must match the inventory. A source change
  requires renewed review, not an overwritten hash ledger.
- Use `/tmp/navier-fenicsx-r229/bin/python`; its resolved binary must match R229
  SHA-256 `5f083df36ec986d5cd13d2549ca6cfe1ddaf658509f9e419b454b2fb375c27a3`.
  Require the held worker/controller source and executable bindings to match.
  Check the expected binary hash in the finite caller before starting the unit;
  the backend/worker also compare the actual executable hash before release.
  No opportunistic reinstall, pin change or substitution of project Python.
- Refresh live capacity and manager availability. Use the existing in-process
  SystemdBackend and supervise_once. Construct its one-use admission with
  approved=true, fixture=poiseuille, attempts_granted=1, exact run directory,
  actual source_commit and manifest_sha256. Record interpreter/hash with the
  allocation; no standalone FEM import smoke test or prewarming.
- Reserve 180 s observed end to end, split 15 s setup / 150 s work / 15 s finish;
  independent worker expiry 149+1 s; 1536 MiB, no swap, 32 tasks, one MPI rank
  and one thread per library, at most 20,000 velocity/pressure DOFs. Include
  finite caller preflight and final persistence in outer observed accounting;
  a late or missing outer record cannot upgrade an inner PASS.
- Execute only one exactly representable Poiseuille n=2, dt=0.125 BE step, exact
  history/trace and non-exact free velocity guess. Require a checked correction,
  compatibility/rank, degree-24/26 diagnostics, both return samples, raw numerical
  decisions and actual exit/cleanup. Any max/OOM/PID event refuses success.
  Do not change the stringent quadrature rule or other thresholds after seeing
  results. Report any source/API/accuracy/resource failure and stop for review.

The finite caller/OS manager trust boundary and pre-final-exit counter snapshot
tail remain the [R103](B2_MONITOR_PRACTICAL_SUPERVISION_POLICY.md) and
[R226](POISEUILLE_LAUNCHER_R226.md) limits. Actual FEM import/JIT/mesh/assembly/
solve cost, library compatibility, measured rank and numerical accuracy remain
unknown. A pass would verify only this fixture, not convergence or physical flow.
No model/session switch, delegation, machine transfer, physical/render work or
production solver change occurred. Mac remains released.

Next: **GPT-6 Sol/high** executes that fixed contract once after a later Continue,
then publishes evidence and stops. Official [OpenAI Docs](https://developers.openai.com/api/docs/models/gpt-6-sol)
was searched/opened and confirms Sol/high support; task fit is judgment, not
account-access verification. Recommend Astra/high afterward to interpret the
result or any changed scientific/admission choice. Follow the single
[handoff task](../../SESSION_HANDOFF.md#next-task).
