# B1 solver environment

[R239 pivot review](../../docs/realizability/POISEUILLE_PIVOT_REVIEW_R239.md) gives an exact full-rank toy that fails
without row pivoting and a singular toy that passes the scalar Gram check.
Actual R238 matrix rank remains unknown. Runtime source and all three spent
allocations are unchanged; no FEM ran. Next: Astra/high reviews an explicit
serial SuperLU backend and its controls, with a minimal source change only if
justified; stop before new numerical admission. Follow the
[current task](../../SESSION_HANDOFF.md#next-task).

Current PC status: [R232's one-use Poiseuille result](POISEUILLE_RESULT_R232.md)
is INCOMPLETE at PETSc symbolic LU, and the single numerical allocation is
spent 1/1. [R233](POISEUILLE_SPARSE_REVIEW_R233.md) repairs structural zero
diagonal storage and passes 59 standard-library tests, with no numerical rerun
in that review. [R234](POISEUILLE_ADMISSION_R234.md) admitted one new fixture
in a fresh directory. [R235](POISEUILLE_RESULT_R235.md) spent the new 1/1
allocation: sparse linear solve refused, exit 1, empty cleanup, no numerical
report or resource snapshot. The older 1/1 charge remains unchanged.
[R236](POISEUILLE_KSP_REVIEW_R236.md) adds a tested refusal diagnostic without
changing the solver or running FEM. [R237](POISEUILLE_ADMISSION_R237.md) grants
one diagnostic fixture with the unchanged solver/gates.
[R238](POISEUILLE_RESULT_R238.md) spent it 1/1: KSP -11 and PC reason 2
(reported numeric zero pivot), worker exit 1, empty cleanup and no numerical/
resource report. All three fixture allowances are spent; next is backend review.
R229's transaction/metadata/interpreter checks completed; its setup
memory-event refusal remains unchanged. FFCx's exact artifact/runtime gate is
repaired. Retain `/tmp/navier-fenicsx-r229`; old `/tmp/navier-fenicsx` stays partial.
Follow the [single next task](../../SESSION_HANDOFF.md#next-task); do not reinstall
or run the general B1 suite or reuse the old fixture directory.
For historical Mac setup/comparison, see
[MAC_INSTALL_AND_BENCHMARK_PLAN.md](MAC_INSTALL_AND_BENCHMARK_PLAN.md); no machine
transfer or new remote check is implied. General solver commands below are
reference only and do not grant a workload attempt.

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
