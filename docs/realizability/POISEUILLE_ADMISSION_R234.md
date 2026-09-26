# R234 — One new repaired-source Poiseuille fixture admitted

**GO for one later bounded n=2 Poiseuille attempt on PC/WSL daisy. No numerical
work ran in this review.** This is a new allocation, **0/1 spent**, fixed to
`/tmp/navier-poiseuille-r234-once`. A later **Continue** authorizes its execution
under this contract. The R230 allocation used by R232 remains **INCOMPLETE and
spent 1/1**, with its directory and evidence preserved. The full manufactured
suite, rotation, tank/B2 and physical/render workloads remain unadmitted.

## Basis for admission

The [R233 source review](POISEUILLE_SPARSE_REVIEW_R233.md) demonstrated why
the old CSR path necessarily omitted the three scalar diagonals and removed
stored zero pressure diagonals. Its minimal correction retains those structural
slots through bordering, lifting and row scaling, without changing the operator,
rank, pressure gauge, either flux constraint, solver or acceptance threshold.
Three new regressions failed against the old source, then all 59 standard-library
tests passed. Actual factorization, numerical pivots, rank/conditioning,
degree-24/26 diagnostics and accuracy remain untested.

This is a sufficiently specific source correction to justify one controlled
measurement under the existing numerical/resource refusal rules. The admission
does not assume that explicit zero diagonals make PETSc LU succeed, that a
well-conditioned three-row Gram matrix proves mixed-operator stability, or that
the fixture fits its memory cap. Any later numerical or resource refusal still
ends the new attempt without automatic repair-and-rerun.

The [R229 environment](ENVIRONMENT_RECOVERY_R229.md) completed its exact
transaction and artifact/interpreter checks but failed its setup resource
predicate: 303 memory.max events at 1536 MiB, without OOM/kill. Reuse follows
R230's distinction between verified installed artifacts and that failed setup
predicate. The latter remains false. R232 reached FEM assembly and symbolic
LU with verified held limits, then failed without a resource snapshot; it
supplies no actual memory-event or numerical-success evidence. There is no
footprint prediction or retrospective waiver.

The [R226 launcher evidence](POISEUILLE_LAUNCHER_R226.md) and R232's actual
held/source/exit/cleanup evidence remain applicable: launcher, worker, source
binding, resource gates and package checks are unchanged. R103's finite trusted
caller and existing OS-manager boundary, and the unmeasured final counter/save
tails, remain disclosed. No new infrastructure certification is needed.

R234 checked all 25 R233 source hashes, both saved R233 test-output hashes,
all 17 R229 artifact hashes, all ten R232 raw files and their retained originals.
The pinned interpreter binary and current conda history match the saved R229
hashes. The R232 reservation remains present; its worker PID 144212 and cgroup
are absent. The new fixed directory is absent, including no dangling symlink.
No environment interpreter execution, package installation, fresh numerical
imports, archive/file inventory rescan or manager probe ran. Actual launch must
refresh live host capacity and manager availability.

## Exact contract and ready caller

[allocation.json](evidence/r234/allocation.json) records the separate charge,
fixed directory, caps, interpreter and caller hash. The reviewed
[caller](evidence/r234/run_once.py) is derived from the corrected R231/R232
caller, changing only its description, output directory, inventory reference
and owner label. The old caller, allocation and R230/R233 evidence ledgers are
unchanged. This caller reads the **R233** inventory, which includes the repaired
source. It resolves project imports from its own path and starts the outer timer
before importing project components.

| Requirement | Frozen value |
|---|---|
| Work | Exactly one Poiseuille n=2, dt=0.125 BE step; exact history/lateral trace, non-exact free velocity guess and checked correction |
| Directory | `/tmp/navier-poiseuille-r234-once`; one exclusive reservation, no alternate directory |
| Source | All 25 `source_sha256` entries in `evidence/r233/checks.json`; actual clean launch HEAD in caller, admission, reservation and held-worker binding |
| Manifest | `verification/nonlinear_port/future_fem.json`, SHA-256 `7a8bda917e6b46994ad24c68e0b6c6013b7d6776f90c86a6de763f31f52fa558` |
| Interpreter | `/tmp/navier-fenicsx-r229/bin/python`; resolved binary SHA-256 `5f083df36ec986d5cd13d2549ca6cfe1ddaf658509f9e419b454b2fb375c27a3` |
| Time | 180 s outer observed interval; 15 s setup / 150 s work / 15 s finish; 149 s independent worker runtime + 1 s stop grace |
| Resources | 1536 MiB whole worker cgroup, no swap, 32 tasks, one MPI rank, one numerical thread per library, at most 20,000 mixed velocity/pressure DOFs |
| Resource acceptance | Zero memory.max/OOM/OOM-kill/PID-limit events; finite saved peak and actual exit/empty cleanup required |
| Numerical acceptance | Unchanged compatibility/constraint Gram, Newton/true linear residual, eta/gauge/both fluxes, degree-24/26 comparison, return samples, oracle errors and physical endpoint budgets |
| Package identity | Exact pinned environment; FFCx package 0.10.1/pyhbc3ee6d_1 permits its verified embedded/runtime 0.10.0 only through the existing artifact gate |

On the later execution turn, complete the clean Continue synchronization and
publish STARTED before launching. Confirm this allocation is still unspent in
the request/lifecycle logs as well as the directory inventory. Verify the
caller hash in allocation.json, the R233 inventory and interpreter; obtain the
actual clean `git rev-parse HEAD`, then run the caller once with that exact
40-character commit argument using the pinned interpreter. The caller refreshes
memory availability and manager connectivity inside its timer, then creates
the executable admission only at the supervised reservation boundary. Keep the
checkout unchanged while its worker runs.

The caller was checked with project Python 3.12.14, without numerical imports:
[check_caller.py](evidence/r234/check_caller.py) verifies outside-directory
imports, the timer before project imports/preflight, and refusal of changed
source or existing/dangling-symlink run paths before a manager connection.
Synthetic Git answers are explicitly limited to the preflight refusal cases.
An [unmocked direct CLI check](evidence/r234/invalid_commit_check.json) from
`/tmp` with an invalid commit exited 1 with the expected clean-commit refusal
in 0.016726162 s as observed by the caller. It created no reservation or worker.
These are deliberate caller tests, not failed numerical attempts. The new two
Python files parse. The unchanged 59-test source suite and benign host suite
were not rerun; their hashes and retained results are reused.

## Consumption, recovery and completion

Creation of the fixed run directory/reservation or any partial managed worker
start consumes this allocation, including an incomplete result. A missing
directory later cannot reset the charge in the logs. A refused solve, API error,
missing resource evidence, cap event, timeout or uncertain cleanup stops the
attempt. Preserve raw outputs, actual elapsed/counter gaps, allocation state
and cleanup. No second command after that boundary, alternate directory,
solver fallback or threshold change is admitted.

A demonstrated caller/preflight error **before** reservation, worker start
and numerical import is recoverable within this same unspent task. Preserve
its command/error and timing gaps, verify the fixed directory is absent and
the manager has no new task process, fix/test the cause without FEM, publish
a clean source binding, and continue. Uncertain process state requires review.
This is the R232 correction to the stopping rule, not a new numerical allowance.

Completion of the later launch requires persisted raw numerical/controller/
caller records or an explicit incomplete outcome, actual exit and confirmed
child cleanup, spent-state accounting, updated status/handoff and scoped
publication. No missing snapshot or final-save tail may be promoted to PASS.
Follow the single [handoff task](../../SESSION_HANDOFF.md#next-task).

Next: **GPT-6 Sol/high**, execute this exact prepared caller once after a later
Continue, publish the outcome and stop. No `/new` is needed for the connected
execution step. Return to Astra/high for numerical interpretation or changed
scientific/admission decisions. Official
[OpenAI Docs](https://developers.openai.com/api/docs/models/gpt-6-sol) was
searched/opened and confirms Sol/high support; model fit is judgment, not an
account-access check. No model/session switch or machine transfer occurred.
