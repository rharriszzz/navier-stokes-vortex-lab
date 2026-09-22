# R168 PC renderer comparison

2026-09-21 America/New_York (2026-09-22 UTC), PC/WSL `daisy`.
Source checkpoint `7cb90e4`; resumes the interrupted R167 preview.

The installed default renderer successfully rendered the unchanged centered
sphere and project frame 1 with graphic display disabled, one thread and
160x120 output. This establishes a working bounded configuration, not the
cause of R167's segmentation fault. No rebuild or scene change is justified
by this comparison. The preview remains unfinished.

## Inputs and provenance

Activated `.venv`: CPython 3.12.14. `povray` resolves to
`/usr/local/bin/povray`, version 3.7.0.10.unofficial, g++ 11, x86_64 Linux.
Its SHA-256 before and after rendering was
`c805cf61ecc95eae5fe7a7ccbcef4dbba5a95d5078d06b25697a9a4654961c4e`.
`/usr/bin/povray` also exists, but was not executed in this comparison.
Linux `timeout` and ffprobe are available; WSL reported 6854 MiB available
memory before launch. This is a guest snapshot, not additional host capacity.

The existing checker report `/tmp/r167-check-qQKjqr/result.json` remains intact:
450 frames, 128 beads/frame, pass=true, motion observed, time 0..14.96666667.
Its SHA-256 is
`8fc5e8521a45f15bb54da62a372ebb1a02b2d2e9018f62d0a5583babdc91df0c`.
The checker was not rerun and trajectories were not regenerated.

Read-only review of `/tmp/r167-preview-LKKwQU/separated/frame001.log`
confirmed **Graphic display On**, 320x180, frame 1 of 450 and termination
during parsing. The original full shell argv was not saved in that directory;
the R167 request record preserves animation, antialiasing and two-thread
options. No missing command text was reconstructed from private session data.
The local renderer's `/usr/local/etc/povray/3.7/povray.ini` sets `Display=On`;
the user's config contains only a commented `Display=Off` suggestion.

## Commands and observed results

Working directory: `/home/rharris/git/navier-stokes-vortex-lab`.
Created fresh `/tmp/r168-render-CCQtFZ` using `mktemp -d`.
Each command ran once; `ulimit -c 0` disabled core dumps in its launching shell.
Each render had a 30-second TERM timeout with a two-second KILL grace period.

```bash
/usr/bin/timeout --signal=TERM --kill-after=2s 30s /usr/local/bin/povray \
  +Itests/scenes/centered_sphere.pov +O/tmp/r168-render-CCQtFZ/sphere.png \
  +W160 +H120 +FN -d +WT1 -J +A0.2 \
  > /tmp/r168-render-CCQtFZ/sphere.log 2>&1

/usr/bin/timeout --signal=TERM --kill-after=2s 30s /usr/local/bin/povray \
  +Ifluid.pov +O/tmp/r168-render-CCQtFZ/project.png \
  +W160 +H120 +FN -d +WT1 -J +A0.2 \
  +KFI1 +KFF450 +KI0 +KF1 +SF1 +EF1 \
  > /tmp/r168-render-CCQtFZ/project.log 2>&1
```

| Check | Centered sphere | Project frame 1 |
|---|---|---|
| Exit status | 0 | 0 |
| Graphic display | Off | Off |
| Trace time reported by renderer | 0.004 s | 1.510 s |
| Sphere intersection tests / successes | 35567 / 16509 | 3623 / 1737 |
| Additional successful intersections | — | box 10423505; plane 388290 |
| Output PNG | `sphere.png` | `project001.png` |
| Visual inspection | Shaded red sphere on pale background | Blue transparent tank, edges and small visible tracers |

The reported trace times exclude process startup and are not benchmarks.
Both images were opened and inspected individually. One project frame cannot
establish animation or visible motion. All generated PNGs/logs remain in `/tmp`.

SHA-256 bindings:

| File | SHA-256 |
|---|---|
| `fluid.pov` (before/after) | `a252cdb6f710028fb7d64a91d302b4d712e38588168d9cb48b090727f2bb24e9` |
| `tests/scenes/centered_sphere.pov` (before/after) | `963d4afb9294c3ffc822e747ee75af7ad39338428e00bf28d8c31f8a11b81066` |
| `sphere.png` | `99fed91fa3ae1cf631e9e1297ec15bb4084c6c80c027cc4f2252220666699384` |
| `project001.png` | `dd92e8853ac1cd53b155bb4923268e7bf323384008befb6cd6b9179c31886e84` |
| `sphere.log` | `b690c9dc071fa98c585c1c0e7426a3cfd54be93d7d6382cd65d6ffb8f4eb3a87` |
| `project.log` | `95ec54d140ce46df7196e76c2857ea449b20739b484a165564a31c7c60b4fc85` |

## Interpretation and boundary

R167's failed invocation and R168 differ in display, thread count and image
size. Display is a plausible contributor, but was not isolated. The results
rule out an unconditional parser failure on these unchanged inputs under the
tested configuration; they do not prove that every renderer path works or
that this Linux failure shares the historical Mac fast-math cause.

Both children exited normally. A final `ps -C povray` found no POV-Ray process
visible to this execution context; this does not inspect another machine.
No additional renders, sequence, encoding, ffprobe, package/build, physical,
FEM or trajectory work ran. The handoff explicitly requires stopping after
this comparison before changing the preview plan.

Recommended next action: accept explicit `-d +WT1 -J` for the bounded 320x180
preview through the next Continue, following the [single current task](../../SESSION_HANDOFF.md#next-task).
Luna/medium is appropriate for that routine execution; return to Astra/high
on renewed failure or a new build/format decision. Root-cause isolation is
deferred, not claimed complete.
