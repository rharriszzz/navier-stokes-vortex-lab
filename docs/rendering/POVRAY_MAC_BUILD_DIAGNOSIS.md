# Mac POV-Ray blank-render diagnosis — R136–R138

The MacPorts `povray @3.7.0.8_5` executable produces background-only images
because its fast-math build mishandles the camera parser's infinity sentinels.
An isolated build of the same release with `-O2 -fno-fast-math` renders the
unchanged sphere, user's beads example, official torus example and project
frames correctly. No project geometry, camera, materials or trajectory was
changed. The installed `/opt/local/bin/povray` is still the original executable;
the working build is local and temporary. Follow the single
[next task](../../SESSION_HANDOFF.md#next-task) for durable installation.

## What “blank” means

The user's `../beads/beads1.jpg` is a valid reference showing a red/green/blue
bead ring on an intentional white background. The fresh MacPorts rendering of
`../beads/beads.pov` contained no ring or floor: all 19,200 pixels were exactly
RGB `(0, 0, 0)`. The test sphere and official torus showed only their uniform
background colors. A successful exit and valid PNG were insufficient.

## Controlled evidence

All renderer invocations ran outside the agent sandbox, with a 30-second
per-render limit, two threads and fresh output directories. Diagnostic examples
were 160x120 without antialiasing; project checks were 320x180 with antialiasing
and jitter disabled. Every render exited 0; visual/statistical results differ:

| Build | Default-camera sphere | Explicit-camera sphere | Beads / official torus |
|---|---|---|---|
| Installed MacPorts, Clang 17, `-ffast-math` | No geometry; 0 successful sphere intersections | Visible; 11,158 successful sphere intersections | No geometry |
| Same 3.7.0.8 source, Apple Clang 21, `-O2 -fno-fast-math` | Visible; 11,102 successful sphere intersections | Visible | Visible geometry |
| Same new build, **only `parse.cpp` recompiled with `-ffast-math`** | No geometry; 0 successful sphere intersections | Visible; 11,090 successful sphere intersections | No visible geometry |

Turning automatic bounding off did not repair the default-camera sphere.
The parser-only comparison holds compiler, libraries, source and other objects
fixed, so the result does not depend solely on comparing Clang 17 with 21.
The experimental parser was then restored to conservative math; the resulting
binary was compared byte-for-byte with the saved working executable.

POV-Ray 3.7.0.8 `source/backend/parser/parse.cpp` initializes omitted camera
fields using `HUGE_VAL` (infinity), around lines 1385–1393, then tests that value
when restoring defaults around lines 1633–1745. Assuming finite-only arithmetic
is incompatible with those tests. Supplying `up`, `right`, `look_at`, `angle`
and `focal_point` explicitly bypasses this particular failure, but cannot
establish correctness of other fast-math code paths. The fix tested here is a
conservative renderer build, not scene-level workarounds or changing infinity
to an arbitrary large finite value.

Primary sources supporting the investigation:

- [POV-Ray issue 460](https://github.com/POV-Ray/povray/issues/460) reports the
  related camera-angle failure under newer compilers. This also means R111's
  missing-angle error was not evidence that omitting `angle` is invalid syntax.
- [POV-Ray developer discussion](https://news.povray.org/povray.unix/thread/%3Cweb.66763a7d165794de9a328caa7597fb06%40news.povray.org%3E/)
  explains the finite-math/infinity incompatibility and recommends disabling
  fast-math or finite-math-only.
- [Clang floating-point documentation](https://clang.llvm.org/docs/UsersManual.html#controlling-floating-point-behavior)
  documents the assumptions enabled by fast-math.
- [POV-Ray Unix build instructions](https://github.com/POV-Ray/povray/blob/v3.7.0.8/unix/README.md)
  describe the prebuild/configure/make workflow.

## Project validation

The existing Python 3.12.13 checker passed all 240 saved frames, 500 beads per
frame, finite bounds, time ordering and observed motion. The saved
[report](evidence/r136/trajectory-check.json) records the extrema. No trajectory
regeneration ran. After the sphere and first project frame were inspected,
frames [1](evidence/r136/frame001.png), [120](evidence/r136/frame120.png) and
[240](evidence/r136/frame240.png) were rendered and individually inspected:
the tank and tracers are visible, and the tracer distribution changes toward
the top and bottom. This validates illustrative rendering, not physical flow.
No movie/ffprobe, FEM, physical, tracing or benchmark work ran.

[Raw render logs and small images](evidence/r136/) preserve the installed,
conservative and parser-only comparisons. [Measurements](evidence/r136/measurements.json)
record binary/source hashes and image extrema. The beads source/reference
checkout was read-only; its working tree stayed clean.

## Working local executable and reproduction

Working executable:
`/tmp/povray-build-diagnosis.JO4kJZ/povray-safe-math`.
SHA-256: `905b84d24b0705f80cf4e359f7caf64428eb22ceef69e57c8451ed0441a1c26e`.
It uses the existing MacPorts libraries, include files and user configuration.
No `make install`, package replacement or user-config modification ran.
Temporary artifacts may disappear; do not transfer this Mac binary to the PC.

From the repository root, in an external host execution context:

```bash
POV_RAY=/tmp/povray-build-diagnosis.JO4kJZ/povray-safe-math \
  bash diagnose_renderer_external.sh
POV_RAY=/tmp/povray-build-diagnosis.JO4kJZ/povray-safe-math \
  WIDTH=320 HEIGHT=180 TIMEOUT_SECONDS=30 \
  OUTPUT_DIR=/tmp/povray-renderer-recheck \
  bash render_three_frames_external.sh
```

The same source build can be reproduced without installing it:

1. Download `https://distfiles.macports.org/povray/povray-3.7.0.8.tar.gz` into
   a fresh `mktemp -d` directory. Verify SHA-256
   `e86427f83b9bc356e6694bd053eb23b310aa0f942ac9215860c86f0035865ce2` before
   extracting. The source directory is `POV-Ray-povray-908900d`.
2. Run `./prebuild.sh` from its `unix/` directory. This task bounded prebuild
   to 60 seconds. Apply the installed MacPorts port's existing
   `truetype.cpp.patch`, `patch-lseek64.diff` and `patch-vfe-uint.diff` only to
   this extracted tree. These supply the same Mac compatibility changes as
   the port; no camera or intersection source changes were made.
3. Rename the generated root `VERSION`, `unix/VERSION` and
   `libraries/tiff/VERSION` to `VERSION.saved` after prebuild, to avoid
   collision with C++ `<version>` on the Mac filesystem. Original bytes are
   retained. Do not repeat prebuild afterward without restoring its input.
4. From the source root, configure (120-second limit used here):

```bash
./configure --prefix=/opt/local --disable-optimiz --disable-optimiz-arch \
  --with-boost=/opt/local/libexec/boost/1.76 \
  --with-boost-thread=boost_thread-mt \
  --with-libjpeg=/opt/local/lib --with-libpng=/opt/local/lib \
  --with-libsdl=/opt/local/lib --with-libtiff=/opt/local/lib \
  --with-openexr=/opt/local/libexec/openexr2/lib --with-zlib=/opt/local/lib \
  'COMPILED_BY=R136 isolated math comparison' \
  'CXXFLAGS=-O2 -fno-fast-math -std=c++11 -I/opt/local/include -I/opt/local/libexec/boost/1.76/include' \
  'CPPFLAGS=-I/opt/local/include' \
  'LDFLAGS=-L/opt/local/lib -L/opt/local/libexec/boost/1.76/lib' \
  'LIBS=-lboost_system-mt -lboost_thread-mt' \
  'PKG_CONFIG_PATH=/opt/local/libexec/openexr2/lib/pkgconfig'
gtimeout --signal=KILL 300 make -j2
```

This creates `unix/povray` in the temporary source tree. The prefix locates
existing runtime resources; it does not install anything. This build passed
despite old autotools/deprecation warnings. Broad renderer compatibility is
not certified by these small examples.

For the causal test, save the good executable, rebuild only
`source/backend/parser/parse.o` using `make -C source -W backend/parser/parse.cpp
backend/parser/parse.o` with the same flags except `-ffast-math`, then relink
with `make -j2`. Restore that object with `-fno-fast-math` afterward. Compiler
flags embedded in the banner remain the original configure flags, so the
parser-only binary is identified by its separate hash and build log, not its
banner. The [parser fast-math build log](evidence/r136/parser-fast-math-build.txt)
and [restoration build log](evidence/r136/parser-restored-build.txt) are saved;
the full initial build log remains in `/tmp/povray-build-diagnosis.JO4kJZ/`.
