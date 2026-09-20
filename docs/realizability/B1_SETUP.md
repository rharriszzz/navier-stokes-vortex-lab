# B1 solver environment

B1 uses a separate conda-forge environment so the visualization pipeline keeps
its small NumPy-only dependency set.

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
as 0.10.1, while the installed Python distribution metadata and
`ffcx.__version__` both report 0.10.0. `verification.json` records the runtime
module version. The environment file retains the conda package label needed to
recreate the solved environment.

In restricted sandboxes, MPI may require execution outside the sandbox because
even a serial communicator initializes local IPC and network interfaces. That
environment limitation is separate from the mathematical solver.

Run NumPy-only tests with the ordinary interpreter:

```bash
python3 -m unittest discover -s tests/realizability -p 'test_*.py'
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
