# R270 — One-use manufactured angular diagnostic result

2026-09-26 (America/New_York), PC/WSL `daisy`. **INCOMPLETE; the new R269
allocation is spent 1/1.** The worker exited 0 and wrote all expected raw
records, including `angular_audit.json`. The fixed physical angular budget and
interval checks fail at both degrees. A consistent diagnostic sidecar cannot
promote this physical refusal. All nine older allocations remain spent.

The first caller command ran inside the sandbox and stopped at the manager
version query with sd-bus errno 1 after 0.089545386 s. It had not invoked the
supervisor, created the fixed directory, reserved a unit, launched a worker or
imported numerical code. The host manager listed only two previously recorded
failed manufactured units. [The failure and output](evidence/r270/preflight.json)
were published in clean commit `950c2a7` before the unchanged caller ran with
host manager access. This was a pre-reservation recovery, not a numerical
attempt or budget reset. The first command's outer shell elapsed time was not
recorded.

The host caller used exact clean source commit
`950c2a72fe04fadc2d5a262539f0748d24924646` and only
`/tmp/navier-manufactured-r269-once`. Its reservation is attempt 1. The
worker exited 0 in about 9.22 s and the caller returned INCOMPLETE in about
9.34 s. The supervised unit cleaned up empty; its recorded PID and cgroup are
absent, and the host manager lists no new active manufactured unit. The resource
snapshot reports 486,866,944 bytes peak, six tasks, and zero memory-max,
OOM, OOM-kill or PID-limit events. Its measurement boundary precedes final
handshake/exit, so final save tails and an independent parent wall interval
remain unobserved; the R229 setup resource predicate remains false.

| Saved degree | Angular physical defect | Fixed budget limit | Lateral mismatch | Return mismatch | Free residual action |
|---|---:|---:|---:|---:|---:|
| 24 | -0.005145516124005005 | 0.0003759966274385022 | -0.005296861310889651 | 0.00015134518688357518 | -1.60e-16 |
| 26 | -0.005145516124007139 | 0.00037599662743847755 | -0.005296861310889460 | 0.00015134518688357618 | 1.30e-15 |

The [saved-data verifier](evidence/r270/verify_saved.py) checks the copied
files byte-for-byte against their retained originals, hashes all 16 files,
checks source, geometry, time, fixed-value and multiplier aliases, reconstructs
the 375/27 parent maps and 125 angular coordinates, and independently reduces
the 402 raw residual entries. Its five identities per degree reproduce the
saved comparisons, with zero difference under the recorded reduction order.
The [verification record](evidence/r270/verification.json) includes every file
hash and measured split. The sidecar is 40,705 bytes, under its 262,144-byte
cap; the caller records its hash and all ten comparisons as accepted. All 16
[raw run files](evidence/r270/run/) total 298,884 bytes and include worker and
caller logs, numerical and linear-system reports, sidecar, reservation,
resource snapshot, completion and cleanup receipts. Both caller outputs are
retained. No second numerical run was performed.

These values show that the signed defect in this discrete pilot is dominated
by the saved lateral mismatch, partly offset by the return mismatch. They do
not establish why the lateral contribution differs from the exact field, prove
mesh approximation is the sole cause, or validate a manufactured Navier–Stokes
solution. The old physical gates, solver, manifest and historical results were
not changed. Full convergence, tank/B2, rendering and Mac transfer were skipped.

**Next:** Astra/high should review the saved signed reaction/traction split
against R267's algebra and the exact reference, then publish a source-only
interpretation with a justified repair contract or precise blocker. Stop
before implementation, fresh admission or numerical launch. The consumed
R269 allocation cannot be retried.
