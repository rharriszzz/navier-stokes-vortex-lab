# R229 — Offline recovery completed; setup resource check refused

**The new environment transaction and metadata/interpreter verification
completed, but the overall setup contract did not pass.** The cgroup reached
its 1536 MiB limit and recorded 303 memory.max events. No OOM or OOM kill occurred.
Both installer and worker exited 0, and cleanup confirmed an empty removed group.
The completed prefix `/tmp/navier-fenicsx-r229` is retained for admission review;
no FEM release or numerical attempt is granted. Do not reinstall merely because
the setup run's resource predicate refused success.

## Supplied status and task boundary

REQUEST_LOG.md R229 records the supplied Codex v0.155.1 snapshot, account address
redacted: Astra/high, session 01a0cbe6-635a-7761-a6b1-454b78e9b316, 28% context left
(190K/258K), weekly 99% (11:23 Oct 3 reset), Luna Reserve 99% (10:18 Oct 3 reset).
No worked-for/token-total/credit-count excerpt was supplied. These are reported
account/session values, not independent measurements or project-specific usage.
The user's continuation authorized this one newly bounded recovery; no model
switch was inferred. STARTED e4cb868 followed the clean pull of 23a84be.

The [recovery procedure](evidence/r229/recover.py) and allocation were published
as `c38a6685237b1c327c15db678020f570e8d091b3`. The held worker verified that clean
revision, executable and one-thread settings before release. The R226 launcher
and numerical source/pins/manifest were unchanged. R227's failed prefix and all
prior charges/evidence remain intact.

One offline transaction was allocated: <=180 s observed total, independent
149+1 s worker expiry, 1536 MiB/no swap/32 tasks, one numerical thread. Cache
verification, installation, checks, cleanup and result saving were charged.
There was no solver, download, retry, numerical import request or FEM workload.
The existing R103 trusted caller/OS-manager boundary remains explicit.

## Evidence

[Raw result](evidence/r229/run/result.json), [verification](evidence/r229/run/verification.json)
and [artifact ledger](evidence/r229/checks.json) preserve the distinct outcomes.

| Observation | Result |
|---|---|
| Cached inputs | All 338 archives, 841,552,029 bytes, verified against SHA-256 and MD5; manager SHA-256 verified; 2.046302514 s. URL-encoded filenames were decoded for local paths. |
| Install | Micromamba 2.9.0, exact explicit transaction, `--offline --no-pyc`, normal link scripts; return code 0, 8.419695197 s. |
| Package records | All 338 names/versions/builds/SHA-256/MD5 equal the selected R227 transaction, hence all thirteen direct pins unchanged. |
| Files/history | 76,252 entries checked; no required file missing, 973 optional bytecode entries absent as disclosed; committed history 38,537 bytes. File presence is not a full ABI/content proof. |
| Interpreter | `/tmp/navier-fenicsx-r229/bin/python -I -S` reports Python 3.12.13 and the expected prefix/executable; binary SHA-256 saved. No numerical modules requested. |
| Resources | Peak snapshot 1,610,612,736 bytes; memory.max events=303, oom=0, oom_kill=0; tasks peak=7, PID max events=0. |
| Exit/cleanup | Worker exit 0 / manager success; unit not-found, group removed, unknown_children=false; observed worker PID absent in later read-only check. |
| Observed elapsed | 11.434067521 s through result save. Final stdout/return tail unmeasured under R103. Counter snapshot excludes final worker handshake/exit tail while limits remain active. |

`task.success=true` describes the installer and artifact checks. Top-level
`success=false` correctly preserves the stricter setup resource predicate.
There is no retroactive waiver or relabelling of that failed predicate.
The retained snapshot does not distinguish anonymous memory from file cache,
so do not attribute the events solely to cache or infer the later FEM footprint.
The kernel ceiling was reached; no measured value above that ceiling is claimed.

The old `/tmp/navier-fenicsx` still has empty history and remains partial. The
new prefix has committed history and checked artifacts. Its Python executable
hash differs from the old prefix; both package records name the same selected
artifact, while installation relocates prefix-dependent content. No claim of
byte-identical installed executables across prefixes is needed.
FFCx remains artifact 0.10.1 / embedded metadata 0.10.0 as documented in R056/R227;
no version gate or package pin was changed here.

The finite procedure parsed and ran. Live checks above are the task validation;
numerical/full-suite tests were not rerun because numerical source is unchanged.
Artifact/JSON/link/log-prefix/Git checks precede publication. The large binary
prefix/cache remains local, while messages, outputs, history and checksums are
committed. No physical/render workload, delegation or ownership transfer occurred.

## Next decision

**Astra/high: assess the completed environment for single-fixture admission,
with no reinstall and no FEM execution.** Preserve the failed setup result and
all caps. Review whether the existing artifact evidence is sufficient for later
use despite the setup resource event; if further verification is needed, declare
one small bounded metadata/interpreter-only scope first. Such a check validates
existing artifacts, not a retry that converts the installation result to PASS.
Do not change numerical memory-event gates or grant a numerical attempt by
inference. Implement and test the smallest artifact-bound FFCx version handling
that retains exact package provenance while recognizing its upstream embedded
0.10.0 string. Finish with explicit one-fixture admission or a specific refusal,
and leave actual imports/JIT/mesh/assembly/solve to a separate authorized step.
See the single [handoff task](../../SESSION_HANDOFF.md#next-task).

This completed installation-to-review boundary is a reasonable **/new** point,
especially with the user's reported remaining context. After publication,
recommend `/new`, retain Astra/high, then **Continue**. This is advice, not an
agent-initiated session switch. OpenAI Docs was searched/opened for
[Astra/high](https://developers.openai.com/api/docs/models/gpt-6-astra) and
[CLI commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli).
Task/model fit and choosing this boundary are judgment; no account access check.
