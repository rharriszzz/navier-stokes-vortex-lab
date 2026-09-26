# R232 — Recoverable caller error and renewed launch review

**R231's import failure occurred before reservation or managed work.** The
[original command result](evidence/r231/prelaunch_result.json) preserves exit 1
at the caller's top-level `verification` import. Its `main()`, timer, preflight,
backend and worker did not run; the fixed output directory remains absent.
The original caller bytes are retained in Git at `c3b5598`. The user's R232
correction supersedes the premature R231 stop while keeping the same R230
one-use allocation at zero numerical attempts spent.

The [corrected caller](evidence/r231/run_once.py) derives the repository root
from its own resolved path, adds it to Python's import path and loads the three
project components inside the 180-second outer timer. The timer therefore
covers those imports, caller preflight, supervised execution and final caller
save. No cap, admission field, run directory, worker source or numerical gate
changed. The [standard-library regression](evidence/r232/check_caller.py)
loads the caller from outside the repository, resolves all project components,
observes an active outer timer before a synthetic preflight refusal, confirms
timer cancellation and verifies no numerical module, manager or run directory.
A direct path invocation from `/tmp` with a deliberately wrong 40-character
commit reached the clean-commit refusal in 0.0154 s rather than the former
import failure; it created no reservation or manager unit.

The R230 reviewed inventory still matches all 25 file hashes and the frozen
manifest SHA-256 remains
`7a8bda917e6b46994ad24c68e0b6c6013b7d6776f90c86a6de763f31f52fa558`.
R229's resolved interpreter binary still matches
`5f083df36ec986d5cd13d2549ca6cfe1ddaf658509f9e419b454b2fb375c27a3`.
The corrected caller SHA-256 is
`66eb4820cfe898adaab692e5e1931b6878560ca868e9debec56fd751d46deff2`.
The one-use allocation remains exactly `/tmp/navier-poiseuille-r230-once`;
R229's 303-memory.max-event setup refusal remains false. The original R231
failure and unmeasured command-tail are not reclassified as success.

This review admits continuation of the **same** R230 fixture only after the
corrected caller and coordination records are published as a clean launch
commit. The caller must recheck live capacity, manager, inventory, manifest,
interpreter and absence of the fixed directory inside its outer timer. Bind
that actual clean HEAD in admission and reservation. Any reservation or partial
worker start consumes the sole allocation; thereafter no repair-and-rerun.
The original 180 s observed / 149+1 s independent worker, 1536 MiB/no swap/
32 tasks, one rank/thread, <=20,000 mixed DOFs, degree-24/26 and numerical/
zero-event gates remain. Actual FEM compatibility, cost, rank and accuracy are
unknown until that one attempt. Full suite, rotation, tank/B2 and physical/
render work remain unadmitted.
