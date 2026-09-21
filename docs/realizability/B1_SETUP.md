# B1 solver environment

For this Mac's remaining install steps and future comparison with the PC, use
[MAC_INSTALL_AND_BENCHMARK_PLAN.md](MAC_INSTALL_AND_BENCHMARK_PLAN.md). Its
installed environment already passed imports/MPI. The general solver commands
below describe available checks; the [current PC repair task](../../SESSION_HANDOFF.md#next-task)
permits saved/synthetic checks only. R067's scientific review is complete,
and physical execution remains deferred. A visualization smoke test
does not establish FEM readiness.

B1 uses a separate conda-forge environment so the visualization pipeline keeps
its small NumPy-only dependency set.

Prefer **Python 3.12 on both PC and Mac** for project work (R069). This
environment already pins **3.12.13**. After activation, check `python --version`
and `python -c 'import sys; print(sys.executable)'`. Use it for project utilities
and trajectory checks too, or use a separate Python 3.12/NumPy environment for
visualization. The historical MacPorts Python 3.10.19 is not the FEM interpreter.
Keep system interpreters intact and retain the existing reproducibility pins.

Create it with a conda-compatible client:

```bash
micromamba create -f environment-b1.yml
micromamba activate navier-stokes-vortex-b1
```

The verified development environment uses DOLFINx 0.10.0, real PETSc scalars,
MPICH, and Gmsh's Python API. The harmonic solver therefore represents complex
amplitudes as coupled real and imaginary Stokes systems. Do not run the solver
with the repository's ordinary Python interpreter.

Version-reporting note: conda-forge labels the installed `fenics-ffcx` package
as 0.10.1, while its embedded Python distribution metadata and
`ffcx.__version__` report 0.10.0. The [official upstream v0.10.1 tag](https://github.com/FEniCS/ffcx/blob/v0.10.1/pyproject.toml)
still declares project version 0.10.0 in `pyproject.toml`; its [release notes](https://github.com/FEniCS/ffcx/releases/tag/v0.10.1) say it backports a
critical code-generation fix for multiple integrals using the same quadrature
rule. Keep the environment pin at 0.10.1. `verification.json` records the
runtime module's self-reported version, not the Conda artifact version. R056
confirmed the PC build as conda-forge `fenics-ffcx 0.10.1 pyhbc3ee6d_1`; its
package URL and hashes are recorded in
[`evidence/r056/ffcx_pc_environment.json`](evidence/r056/ffcx_pc_environment.json).
R014, R016 and R020 ran after this build was installed in the same environment
and used `/tmp/navier-fenicsx/bin/python`, so their `ffcx: 0.10.0` fields are
runtime strings and do not indicate use of the pre-fix Conda package.

R058 checked the Mac environment's Conda records and found the same FFCx
build, artifact URL and SHA-256 as the PC. Its Python, DOLFINx, PETSc and MPICH
records identify native `osx-arm64` builds. See
[Mac readiness evidence](evidence/r058/mac_readiness.json); assembly/solve and
cross-host numerical comparisons remain unperformed.

In restricted sandboxes, MPI may require execution outside the sandbox because
even a serial communicator initializes local IPC and network interfaces. That
environment limitation is separate from the mathematical solver.

Run NumPy-only tests with the selected Python 3.12 interpreter:

```bash
python -m unittest discover -s tests/realizability -p 'test_*.py'
```

Run B1 checks inside the isolated environment:

```bash
python -m unittest discover -s tests/realizability -p 'test_b1_fenicsx.py'
python -m realizability.cli verify \
  --config configs/realizability/pilot.json \
  --pilot-mesh-size 0.07
```

The `0.07 m` pilot mesh is deliberately a cheap B1 smoke mesh. It verifies
assembly, pressure nullspaces, boundary tags, actual-trace flux correction,
signs, and plumbing. It is not a resolved response mesh: the current run fails
the stated `1e-3` strong-divergence target by orders of magnitude. The generated
report records that failure. B2 must introduce boundary-layer-aware refinement
and demonstrate gain/phase convergence before interpreting small responses.

The production-facing harmonic and backward-Euler transient entry points accept
only boundary modes. Manufactured volume forcing exists only in
`b1_verification.py` for the unit-cube convergence fixture.

Generated meshes, reports, and solution fields belong in
`results/realizability/`, which is ignored by Git.

For the B2 pre-campaign gate, see `docs/realizability/B2_GATE.md`.  Its command
is intentionally separate from B1 verification and will not launch the
six-input response campaign:

```bash
python -m unittest discover -s tests/realizability -p 'test_b2_hdiv.py'
python -m realizability.cli b2-gate \
  --config configs/realizability/pilot.json \
  --mesh-sizes 0.04 0.03 0.025
```
