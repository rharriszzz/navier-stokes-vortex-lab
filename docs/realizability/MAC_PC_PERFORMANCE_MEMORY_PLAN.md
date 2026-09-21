# Mac and PC performance and memory test plan

Designed 2026-09-21 for R077, after receiving R076 in source/base commit
`f1c24c628f78f21fdffeb079cbe85aa7f58277b9`. This is a plan for future runs on
the native arm64 Mac and the PC's Linux/WSL environment. **No benchmark has
run under this plan and no faster machine has been established.**

The result should tell us which machine to use for each project workload,
how much resident memory it needs, and whether it leaves adequate operating
headroom. The current movie is kinematic. The numerical reference below tests
assembly and observer behavior; it does not establish physical accuracy or
predict the memory or speed of a full fluid solve.

This document replaces the comparison protocol formerly embedded in the
[Mac setup guide](MAC_INSTALL_AND_BENCHMARK_PLAN.md). That guide retains the
installation and movie-readiness instructions. The
[current handoff](../../SESSION_HANDOFF.md#next-task) is the single next task;
the stages below are a roadmap, not an instruction to launch them all.

R081 completed the PC source review and froze the
[ten-case PC live-validation contract](B2_MONITOR_LIVE_VALIDATION_CONTRACT.md),
including 180 s cumulative / 512 MiB workload RSS, separate outer/native
backstops, calibration tolerances and commands for a future harness. It also
reproduced eleven remaining fixture gaps, so repairs must precede live work.
Its read-only delegation metadata is not tested containment. The new contract
refines section 5 for PC only; Mac membership/memory decisions and live tests
remain unvalidated. No comparison budget or physical limit changes.

## 1. Sequence and readiness gates

| Stage | Work on each machine | Completion evidence / stop |
|---|---|---|
| A: review and freeze | Review R076; specify the missing live adapters, including the Mac memory/membership contract and Windows collector; freeze measurement schema, harmless validation commands and caps | Reviewed source/contract and explicit missing capabilities; stop before running live workloads. PC first completes its existing R076 review; Mac-specific review follows in a separate task. |
| B: implement and validate monitors | Implement reviewed OS adapters in new source, then conduct the bounded benign checks on each actual host in separate owner sessions | Correct units, complete membership, timely readings, independent watchdog and confirmed cleanup. A fake-provider pass alone cannot complete this stage. |
| C: prepare inputs | Verify local software; validate one image before a short movie; create the frozen comparison manifest and checksum inventory | Commands, versions, workers, exact inputs and correctness rules fixed before timing; unresolved readiness or missing input blocks that case. |
| D: baseline | Run T, R and E below on Mac, publish/release, then run the same frozen cases on PC after receiving checks | One warm-up and three measured fresh processes per case and host, all outputs checked; no automatic retry after an unexpected failure. |
| E: optional numerical reference | Run F only after both hosts' FEM prerequisites and the R067 reference contract pass review | One cold-JIT run and three warm runs per host, unchanged oracle screens and zero factor/solve events. A visualization failure need not prevent a separately ready F case, or vice versa. |
| F: compare | Collect both hosts' small evidence on the current owner; compare correctness first, then timings, memory and headroom | Per-workload recommendation or explicit inconclusive/blocked result. Stop before scaling or any physical run. |

R076's [fixture bundle](evidence/r076/README.md) completed 16 check groups.
Its Linux helpers inject OS operations, and its Windows facade does not start
a native collector. It contains no validated Mac adapter. Review it against
the [R074 specification](B2_MONITOR_ADAPTER_REVIEW.md), preserving all archived
sources/evidence. Do not rerun completed R033/R076 assignments to create a
benchmark. Use a separately identified reference copy where required.

Only one repository owner writes or executes at a time. R079 transferred
ownership to Mac `fire.lan` for this plan; R080 explicitly returns ownership to
PC `daisy` after publication, to resume its previously planned R076 review.
Follow [AGENTS.md](../../AGENTS.md#switching-between-the-mac-and-pc) at every
transfer. A Mac session does not run or inspect the PC remotely. If ordering
must change because a tool is unavailable, record the new order and preserve
the same frozen case and attempts. No computer switch resets a budget.

## 2. Freeze the comparison before either host runs

Create a versioned `comparison_id` manifest with these fields:

- Workload source commit and SHA-256 hashes of source, scene, support includes,
  monitor, validators, input inventory and policy. Evidence delivery commits
  are separate: archive the frozen workload revision on both machines even
  when later evidence commits change checkout HEAD.
- Exact argument arrays, working directories, seed, frame/particle counts,
  render/encode options, cache directories, ranks/threads, repetition IDs,
  caps and acceptance rules. Refuse dirty or unbound source.
- OS/kernel/WSL version, architecture, CPU model/topology, RAM, executable
  paths, Python and NumPy versions, POV-Ray/ffmpeg/libx264 builds, and compiler,
  DOLFINx/FFCx/Basix/PETSc/MPI/BLAS provenance for F. Use Python 3.12, retaining
  the project's 3.12.13 environment pin. Verify native arm64 on Mac and the
  actual interpreter version/path after environment activation on each host.
- Package build/channel/artifact identities with secrets removed. Match
  software versions and options where practical; otherwise label results as
  comparisons of the installed stacks, without attributing differences solely
  to hardware. Do not install or change packages as part of a timed run.
- Power mode, AC power, background activity and available local disk. Use
  local source/output storage and WSL's Linux filesystem on PC; `/mnt/c`,
  network volumes and external drives are separate configurations.

Use one MPI rank for F and one numerical-library thread for all baselines.
Set and record `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`,
`VECLIB_MAXIMUM_THREADS` and `NUMEXPR_NUM_THREADS` to 1; verify effective
threading rather than assuming the environment settings were honored.
Use explicit POV-Ray and ffmpeg thread settings as shown below. Additional
codec/filter threads must also be fixed and recorded by the final runner.

Run each repetition in a fresh isolated source/output directory. The generator
removes matching trajectory files; existing user output must never be reused
as scratch space. Preserve one canonical include set for R and one canonical
PNG set for E. Transfer these ignored artifacts explicitly with per-file hashes,
or regenerate only if their complete hashes match the manifest. Do not copy
compiled binaries, virtual environments or JIT caches between architectures.
Missing irreplaceable input stops the case.

Pause competing project builds before a measurement through a separate
user-managed action; do not terminate the independently managed Mac POV-Ray
build. If it is still active, defer timing. Record a 30 s idle baseline and
fresh capacity at each release; record after-run capacity and background load.
Keep both machines in a documented stable power/thermal state. Record cooling
intervals rather than silently discarding slow runs.

## 3. Fixed workloads and correctness

The commands here are **workload payloads for the future guarded runner**,
not currently approved standalone launch commands. Stage A/B must supply and
validate that runner; no such cross-platform runner is claimed delivered here.

| ID | Fixed baseline | Checks before accepting its timing |
|---|---|---|
| T: trajectories | 240 frames, 30 fps, 500 tracers, 8 RK4 substeps, seed 20260919 | Exactly 240 includes and 500 tracers/frame; all coordinates/scalars finite; inspect frames 1, 120, 240; numerical motion; radius <= 0.92 and abs(z) <= 0.98, allowing 1e-9 serialization tolerance. Report extrema. |
| R: rendering | Same canonical 240-frame includes and scene, frames 1–10, 1280x720, antialiasing 0.2, jitter off, one worker | Exactly ten PNGs with expected dimensions; inspect frames 1, 5, 10 for motion and artifacts; preserve decoded pixel comparisons. The full 240-frame timeline must stay fixed. |
| E: encoding | Same ten canonical PNGs in manifest order, 30 fps, software libx264, medium, CRF 18, one codec thread, yuv420p | ffprobe confirms H.264, 1280x720, 30 fps, ten decoded frames, duration 10/30 s within 1 ms; decode every frame without errors and compare decoded content. |
| F: assembly/observer | Frozen new copy of R033 advanced reference tetrahedra/polynomial suite and support modules, per R067; one rank/thread | Four trace/order cases, 16 facet checks, nine block-oracle comparisons, compatible P/A/A and three refusals, exact discrete inventories, zero factor/solve events, all unchanged numerical screens. |

Payloads T, R and E, each in its own prepared directory:

```bash
python make_trajectories.py --frames 240 --fps 30 --beads 500 --substeps 8 --seed 20260919

povray fluid.pov +W1280 +H720 +KFI1 +KFF240 +SF1 +EF10 +KI0 +KF1 +FN -D -V +A0.2 -J +WT1 +Oframes/frame

ffmpeg -nostdin -y -framerate 30 -pattern_type glob -i 'frames/frame*.png' \
  -c:v libx264 -preset medium -crf 18 -threads 1 -filter_threads 1 \
  -pix_fmt yuv420p -movflags +faststart movie/navier-stokes-vortex-lab.mp4
```

Verify the final runner's glob order equals the ten-file manifest, with no
stale images. Movie smoke readiness is separate from the timed case: first
render one frame, inspect it, then the ten-frame sequence. It is completed
once per unchanged environment/source and recorded outside the timing medians.

For T, compare same-host output hashes first. Across architectures require
exact particle/frame inventories and compare parsed numbers using
`abs(a-b) <= 1e-9 + 1e-10*max(abs(a),abs(b))`, including scalar state. These
are proposed portability tolerances for this serialized kinematic case,
frozen before execution; they do not change physical acceptance criteria.
Record maximum absolute differences and their locations, even when passing.

For R/E, compressed-file hashes are provenance checks. The initial baseline
requires equal decoded pixels between repetitions and hosts using one frozen
decoder/configuration for the comparison. If decoded pixels differ, preserve
the maximum error, RMSE and differing-pixel fraction plus example images and
mark output equivalence unresolved; do not declare a performance winner.
A later reviewed comparison contract may define perceptual tolerances before
new measurements. Container timestamps alone do not make decoded outputs fail.

For F, retain the [R067 reference decision](B2_PHYSICAL_RUNNER_REVIEW.md#repeatable-reference-decision)
exactly: each host passes its `256*eps` absolute-contribution oracle and `1e-8`
flux screens; cross-host entry differences are at most
`256*eps*(S_PC+S_Mac)` with recorded contribution scales and matched identities.
Preserve the operands and scales needed to recompute that check. Never compare
near-zero entries using relative error alone or use raw matrix byte equality
as numerical accuracy. The guarded F command/source manifest remains to be
implemented and reviewed. No physical cylinder, Bessel trace, LU factorization
or q64/q96 physical attempt belongs to this benchmark.

## 4. Timing and memory measurements

Measure monotonic end-to-end workload time from launch through verified exit
of all owned workload processes. Record runner setup, workload, cleanup and
output-validation/reporting time separately; cumulative budgets include all
of them, warm-ups, failed attempts and imports. Retain stdout/stderr and exit
status. Stage times are supplemental and must not replace end-to-end time.
Report CPU user/system time only where the adapter can account for all children.

Sample the sum of resident memory of all live workload processes at each
timestamp, then report the maximum sum in MiB (2^20 bytes). Retain per-process
identity/RSS at that peak and counts of live descendants. Do not sum individual
high-water marks from different instants. Shared pages may be counted more
than once; this is an operational RSS budget, not unique physical RAM usage.
Sampled peak can miss short spikes; label it as sampled and retain OS high-water
measurements separately with their documented units/scope. Do not substitute
virtual address space, cgroup charges, Mac physical footprint or Windows host
usage for RSS under the same field name.

The [R074 monitor policy](B2_MONITOR_ADAPTER_REVIEW.md#preserved-resource-policy)
retains nominal 50 ms tree sampling and host readings no more than 1 s apart;
it selects no new general tree-gap threshold. For this benchmark propose a
100 ms maximum tree gap, consistent with the earlier Mac guide; Stage A must
freeze and validate it as a benchmark-specific requirement. Record observed gaps, acquisition latency,
missed samples and decision delay. Missing, stale or malformed data fails
closed. Independent supervision must stop owned work if the monitor hangs.
The monitor/collector are outside the workload RSS sum; report their memory,
CPU/time overhead and include their startup/cleanup in cumulative time.

On PC, require both guest `MemAvailable` and native Windows available physical
memory; they are overlapping views and must not be added. Validate the
selected cgroup membership/termination and Windows helper lifetime/Job Object
contract from R074 on the actual machine. Root process exit alone is not
complete cleanup. On Mac, Stage A must select and document stable process
identities, descendant coverage including reparenting, termination verification
and a conservative available-memory definition. A `ps` ancestry walk or a
`memory_pressure` percentage alone does not satisfy those requirements.
If the Mac cannot meet the contract, record that blocker instead of inferring
readiness from installed RAM or package imports.

Capture host headroom minima, guest headroom minima, swap/compression changes,
and disk space before/after each run alongside the RSS trace. Changes in swap
are context, not extra RAM capacity. Increasing RSS across fresh-process
repetitions is a diagnostic flag, not proof of a leak; a retained-memory or
leak study needs a separately reviewed persistent-process workload.

## 5. Benign monitor and memory checks

Stage A must turn this matrix into exact source, commands and expected results;
Stage B runs it once per host/adapter version after fixtures pass. Proposed
suite ceiling: **180 s cumulative, 512 MiB workload RSS per host**. This is a
new benign-suite allowance, not a reset of R076 or a change to physical caps.
Setup, failures and cleanup consume it. No live check is executed by this plan.

| Check | Bounded stimulus | Required evidence |
|---|---|---|
| Idle and timing | A 3 s sleep under the monitor | Cadence, elapsed time, monitor overhead and zero survivors. |
| RSS units and membership | Barrier-held parent/child/grandchild, each touching every page in 16, 64, then 128 MiB buffers; at most 384 MiB payload simultaneously | All three stable identities captured; RSS changes consistent with the committed calibration tolerance and baseline; include page size/allocator overhead. Do not expect byte-exact RSS equality with payload. |
| Exit and reparenting | Root exits while a known held descendant remains; test supported session changes | No premature success; owned descendant remains discoverable and cleanup is confirmed. |
| Stops and watchdog | Lower synthetic time/RSS thresholds around a small bounded child; inject delayed/missing host readings and monitor failure | Expected refusal/stop reason, durable partial report, independently enforced outer ceiling and cleanup. Never allocate host RAM to exhaustion. |
| Platform helper | PC native helper lifecycle and host/guest readings; Mac selected local provider | Source/units/identity validation, API failure refusal, bounded latency and confirmed helper exit. |

Freeze calibration tolerances and exact allocations before these checks run.
An expected injected stop passes only with its expected reason and verified
cleanup. An unexpected real resource stop, unknown membership, failed cleanup
or exhausted budget stops the suite; preserve evidence and do not retry or
increase limits automatically. Cleanup continues after a timeout, but any
unconfirmed survivors block owner release and further work.

## 6. Benchmark budgets, repetitions and caches

These are **proposed planning ceilings**, not measured resource forecasts or
permission to launch. Freeze or lower them at Stage A/C before either host's
measurements; if they are unsuitable, revise the contract before the first run.
Never enlarge a budget in response to a failed run within the same comparison.

| Case | Per-run deadline | Cumulative allowance per host, including warm-up and checks | Workload RSS ceiling |
|---|---:|---:|---:|
| T | 60 s | 300 s | 512 MiB |
| R | 240 s | 1200 s | 1024 MiB |
| E | 60 s | 300 s | 512 MiB |
| F | Remaining cumulative allowance | 600 s, retained from R067 | 1536 MiB, retained from R067 |

T/R/E together have an 1800 s per-host ceiling; F is separately gated at
600 s. A 5 s cleanup-verification interval is reserved within each applicable
cumulative allowance, not added as workload time after its deadline. Idle
baseline, readiness smoke checks, input preparation/validation and controller
reporting must be assigned time in the case manifest and deducted from that
case's remaining allowance. If too little remains, refuse the next run.
Record human wait/inspection and powered-off intervals separately; they are
not subprocess compute allowance. Failed/interrupted records remain in the
ledger, with unknown durations blocking automatic resumption.

Before PC launch retain the R074 gates: WSL available >= 4096 MiB and Windows
available >= workload cap + 1024 MiB; stop below the specified runtime Windows
1024 MiB floor. Stage A must freeze a Mac available-byte definition and floors;
the planning proposal is >= workload cap + 2048 MiB at release, with a 2048 MiB
runtime reserve. These Mac values are unvalidated and must not be passed to
the PC policy under a renamed field. Validate both policies with fixtures and
live capability evidence. Missing headroom measurement or failed gate refuses
launch. Refresh gates after setup immediately before releasing work.

For each T/R/E case use one labeled warm-up and three measured fresh processes,
keeping inputs, options and worker counts fixed. Retain warm-up time/memory;
exclude it only from the warm median. For F the warm-up is one cold-JIT run
using a new empty host-local cache selected through actual DOLFINx `cache_dir`;
three warm runs reuse that cache with fresh process/solver state. Record cache
inventory and effective path. Do not clear shared caches or transfer compiled
cache files. Cold JIT is not cold filesystem cache.

Three independent cold-JIT repetitions would require a separately budgeted
extension if startup speed drives the decision. Do not rank cold performance
confidently from one sample. No extra attempts are permitted merely to obtain
three successful measurements after failure. If a case is too short relative
to timing/monitor resolution, label it inconclusive and design a future longer
fixed case; do not change size or batch count midway through a comparison.

## 7. Results, decision rules and completion

Store small manifests, attempt ledger, summaries and validation evidence under
`docs/realizability/evidence/<request-id>/`. Keep large trajectories, images,
movies and raw telemetry in ignored `results/realizability/<comparison-id>/`
or a recorded local directory. Record checksum, size, retention/transfer path
and deterministic regeneration method for required artifacts. Temporary paths
alone are not a transfer mechanism. Preserve compact peak samples, gap summaries
and failed-run diagnostics in Git even when the full trace stays local.

Each result row must include:

```text
comparison_id, case_id, host, run_id, repetition, status, stop_reason,
workload_source_commit, monitor_hash, policy_hash, input_manifest_hash,
environment_manifest, command, ranks, threads, cache_state,
setup_s, workload_s, cleanup_s, validation_reporting_s, total_accounted_s,
sampled_tree_peak_mib, peak_processes, sample_count, max_sample_gap_s,
host_headroom_min_mib, guest_headroom_min_mib, swap_compression_delta,
monitor_overhead, returncode, cleanup_confirmed, correctness, output_metrics
```

Use JSON null plus a reason for unavailable metrics. Record evidence publication
hashes after delivery via Git history/final reports; a file cannot contain its
own committing hash. Counts last observed before interruption are not final
counts. Separate planned, attempted, refused, complete and correctness-passed.

Produce one comparison table with a row for T, R, E and F, showing both hosts'
three individual warm times, median and min/max, worst sampled RSS over all
attempts (including warm-up), host/guest headroom minima, correctness status,
and recommendation. Preserve failed runs alongside successful ones; never
report them as zero seconds or omit their memory peak. Report F cold timing
separately and assembly/compilation stage timings only when measured.

Define speed ratio = PC median seconds / Mac median seconds (>1 favors Mac).
If warm ranges overlap, variation is material or fewer than three valid
measurements exist, report no reliable speed winner; three samples are an
exploratory comparison, not a statistical significance claim. A speed ranking
requires comparable accepted outputs, valid monitoring and matched settings.
A memory-limited host may be unsuitable even if its successful runs are fast.
Do not extrapolate F's small polynomial assembly memory to high-order physical
assembly or LU. No benchmark outcome changes the failed B2 accuracy gate.

Completion means every selected case has either both validated host records
and a comparison, or an explicit blocker with partial evidence and consumed
budget. Recommendations may differ by task. Equal-worker baseline comes first;
parallel worker scaling, larger frame sizes, larger particle counts, persistent
memory/leak checks and any solve benchmark are later contracts. The once-only
physical q64/q96 attempt remains unused and its 180 s / 1536 MiB limits remain
unchanged by this plan.

## 8. Next bounded task and model handoff

R080 returned ownership to **PC/WSL `daisy`**; R081 received the delivery and
completed the source review and bounded PC contract. The single
[handoff task](../../SESSION_HANDOFF.md#next-task) now selects a new fixture-only
repair bundle before native/Linux harness implementation or live execution.
Mac memory/membership decisions and the rest of Stage A remain later,
separately bounded tasks. Do not repeat R081 or start benchmarks from this plan.

After those decisions are settled, recommend **GPT-5.6 Luna/medium** for one
bounded implementation task with fixtures and unchanged acceptance rules;
return to Astra/high for unresolved monitoring semantics, numerical mismatch,
limit changes or interpreting a prospective physical run. Both models/efforts
were checked in the current session catalog and official
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) documentation
on 2026-09-21. No switch, sub-agent, automation or remote execution was started.
The authoritative task and completion criteria remain in the
[handoff](../../SESSION_HANDOFF.md#next-task). Next prompt: **Continue**.
