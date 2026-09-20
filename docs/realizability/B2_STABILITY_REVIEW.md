# B2 stability review and implementation handoff

The subsequent [acceptance-logic review](B2_GATE_REVIEW.md) reproduces the
implemented small-cylinder results, identifies two reporting/gating defects,
and gives the current bounded repair task and model-switch stopping point.

Prepared against commit `a6295da1b4a13e853481b8bae33dc2c28dfa32d5`.
All 49 tracked files were inspected, including the preview image and empty
directory placeholders, together with the stored B0/B1/B2 reports. The initial
working tree was clean. This review advances the small stability study requested
in [B2_NEXT_STEPS.md](B2_NEXT_STEPS.md); it does not rerun the large response gate.

## Decision

Repair and gate viscous stability and boundary consistency before spending more
on response refinement. The current default SIP penalty of 6 is unstable on
the tested cylinder meshes, even inside the discretely divergence-free space.
The cube test alone cannot select a cylinder penalty: 12 passes that cube but
fails both cylinders below, and 24 fails one cylinder.

Keep the existing physical model, feature definitions, and acceptance thresholds.
Use 48 as a candidate for subsequent small verification experiments only.
Positivity on two coarse meshes does not certify any other mesh or establish
response accuracy. No production defaults were changed during this review.
A new solver, larger uniform campaign, six-input report, and B3 remain premature.

## New evidence: the unforced discrete operator can add energy

Let A be the assembled SIP viscous matrix including the physical viscosity,
M the velocity mass matrix, and B the divergence matrix. Eliminate all exterior
normal-trace DOFs, then let the columns of Z span the nullspace of the remaining
B. Compute the smallest generalized eigenvalue

```text
(Z^T A Z) y = lambda (Z^T M Z) y.
```

This is a velocity-space dissipation test, not an eigenvalue test of the
indefinite velocity-pressure saddle-point matrix. Unlike eigenvalues in the
coefficient Euclidean metric, these lambda values have units 1/s.

With zero wall commands and zero volume force, the semidiscrete equations give
`d(0.5*u^T*M*u)/dt = -u^T*A*u`. For an eigenmode the amplitude evolves as
`exp(-lambda*t)`; a negative lambda therefore represents artificial growth.
A frequency-domain linear solve can still have a tiny residual in this case.
That does not establish an attracting periodic response.

The geometry, Gmsh mesh generator, BDM2/DG1 spaces, and SIP form are the same
ones used by the production backend. R = 0.10 m, H = 0.15 m, nu = 1e-6 m²/s.
These deliberately coarse meshes are stability fixtures, not resolved response
meshes.

| Requested mesh size | Cells | Free velocity DOFs | Divergence-free DOFs |
|---:|---:|---:|---:|
| 0.100 m | 82 | 1260 | 933 |
| 0.070 m | 171 | 2658 | 1975 |

| Penalty alpha | Minimum lambda, 100 mm (1/s) | Minimum lambda, 70 mm (1/s) |
|---:|---:|---:|
| 6 | -0.0838845803371 | -0.0341772362200 |
| 12 | -0.0559664829022 | -0.000917893895442 |
| 24 | -0.00312520956158 | +0.00163460031658 |
| 48 | +0.00185910664480 | +0.00168736418397 |

For every reconstructed eigenvector, the directly integrated SIP quadratic form
agreed with the generalized Rayleigh quotient to less than 1e-15 /s absolute.
The largest dimensionless divergence was 1.70e-14; exterior normal traces were
at roundoff. Matrix symmetry errors were at most 5.13e-16 and projected
eigenpair relative residuals at most 2.52e-12.

An independent mixed backward-Euler step, using the reconstructed minimum
eigenvector as initial data, confirms the consequence on the 70 mm mesh:

| Penalty | Time step | Measured E_after/E_before | Eigenvalue prediction |
|---:|---:|---:|---:|
| 6 | 1 s | 1.072025523823309 | 1.072025523823311 |
| 48 | 1 s | 0.996633794049131 | 0.996633794049132 |

There is no boundary command, reaction term, or manufactured body force in
these steps; the right-hand side contains only the preceding velocity.
The two initial eigenvectors differ and are normalized to unit velocity L2
norm for this linear numerical fixture. Their amplitude is arbitrary.
The alpha=6 step adds 7.20% kinetic energy. Its algebraic residual is 2.85e-16,
so this is not a failed linear solve. A generic smooth decay fixture can miss
such a mode; retain this targeted test as well as smooth convergence fixtures.

These tests establish instability on the stated meshes. They do not quantify
how much of the stored 25 mm harmonic error is caused by instability, geometry,
boundary inconsistency, or inadequate spatial resolution. They also do not
establish the spectrum of the stored 40/30/25 mm operators.

The [official DOLFINx example](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/demos/demo_navier-stokes.html)
uses a degree-dependent penalty in a different element/mesh setting. It is a
formulation reference, not a penalty certificate for these tetrahedra. The
production penalty uses cell diameter; different tetrahedron shapes can have
different trace constants. Do not infer a universal safe alpha from the cube.

## Boundary consistency is a separate issue

For T_00c, production imposes exactly zero normal BDM trace but inserts the full
interpolated cylindrical tangent field g into the Nitsche right-hand side.
That g is not tangent to the planar boundary facets. Measured on the side wall:

| Mesh size | L2(g dot n) / L2(g) |
|---:|---:|
| 100 mm | 0.189658 |
| 70 mm | 0.151401 |
| 40 mm | 0.094160 |

These are discrepancies in the requested boundary data, not computed normal
fluid leakage. They decrease with geometry refinement but are substantial on
the smoke meshes.

For homogeneous normal test traces, the penalty contribution from g's normal
part vanishes. The adjoint consistency contribution
`-nu*integral g_n*(n dot grad(v) dot n) ds` need not vanish: zero v dot n on
a facet does not imply a zero normal derivative there. Thus retaining that
normal component in the weak target can introduce an inconsistent load.

For the next implementation, use an explicitly facet-consistent target:

```text
P_t = I - n tensor n
g_consistent = P_t*g + (g_BDM dot n)*n
```

Here g_BDM is the actually imposed essential normal trace, including any
recorded flux correction. In the pure tangential case this reduces to P_t*g.
Use zero target on the caps. Keep the existing full SIP form when using this
matched full target; projecting only the RHS for normal actuation would
otherwise drop its required normal component.

This specifies the discrete boundary interpretation: preserve the prescribed
normal trace and the facet-tangential component of the smooth-cylinder target.
It changes the finite-mesh load and must be labeled and checked under geometry
refinement. An explicitly tangential Nitsche formulation or curved geometry
are alternatives requiring their own verification; neither is implemented here.
The facet projection does not renormalize the physical command amplitude.

Record the original target, projected target, actual solution trace, cap error,
and interior tangential jumps separately. The current `actual_peak_speed`
reports a nodal maximum of the target field, not the computed weak trace or a
certified continuous maximum.

## Work for the cheaper coding model

The scientific investigation above is complete enough for a bounded
implementation package. Pause for the user's model switch before this work.

**Model-switch reminder:** The user wants a reminder to switch back to the
more capable model when research judgment is needed. Complete the routine
implementation and verification below, then explicitly recommend switching
back before choosing a production mesh, solver, or penalty strategy. Pause
earlier if results contradict this review, instability persists, the resolved
swirl fixture fails to agree with the reference, or progress would require
changing physical assumptions, boundary interpretation, observables, or
acceptance thresholds. Record the evidence and unresolved decision here before
the reminder. Routine coding errors and test failures with an understood fix
do not by themselves require a model switch.

1. Package the small energy audit below into the optional B2 verification code
   and expose a command/report. Preserve the mass metric, homogeneous normal
   elimination, divergence-free restriction, direct quadratic-form check,
   eigenpair residual, and targeted zero-input step. Keep it serial and impose
   a size guard; never densify a production 25 mm matrix. Record configuration,
   dependency versions, all contributing source hashes, mesh hash, DOFs,
   runtime, and memory in strict JSON.
2. Connect stability failures to B2 acceptance before expensive harmonic solves.
   The existing test correctly *passes as a regression test* when it detects
   the known negative eigenvalue at alpha=6. This must not be confused with
   *passing the scientific stability gate*. Known unstable settings must
   produce an explicit failed gate. Make penalty choices explicit in reports
   and CLI options. Use 48/96 for the next small verification comparison,
   conditional on their stability checks; do not silently certify either on
   untested production meshes.
3. Implement the facet-consistent boundary target above. Add side/cap
   tangential L2 errors normalized by commanded speed and area, target-normal
   mismatch, actual normal error, and interior jump diagnostics. Verify both
   normal and tangential modes and retain the affine consistency check.
4. Add a smooth, non-affine BDM manufactured convergence fixture. Compare a
   modest resolved swirl fixture against the existing independent reference:
   nu=1e-4 m²/s, f=0.001 Hz, unchanged cylinder and disk. Label these changed
   parameters as a verification fixture. Check complex absolute error, gain,
   phase, and quadrature; do not treat series convergence alone as CFD
   agreement. Keep the physical 0.01 Hz reference for later response validation.
5. Stop and report this package before selecting a production mesh strategy.
   If instability remains, or 48/96 cannot give useful small-fixture agreement,
   bring back the evidence for numerical-method review. A shape-aware facet
   penalty, graded mesh, iterative solver, or Fourier separation is a separate
   decision.

The subsequent routine queue remains: preserve complex values/conjugate
transposes in response analysis, fix incomplete report provenance, include PDE
checks for penalty-comparison solves, and update stale package/project status
summaries. Do not let those items hide an unresolved stability or accuracy gate.

## Verification and provenance

- Ordinary Python discovery: 22 tests discovered, 13 passed, 9 optional
  DOLFINx tests skipped. This includes all five SciPy swirl-reference tests.
- Isolated DOLFINx B2 suite: all four tests passed. This suite intentionally
  detects the unstable cube at alpha=6; it does not certify production.
- Existing cube audit was reproduced for alpha=6,12,24,48. Minimum constrained
  coefficient-metric eigenvalues were -8654.18, 28.5198, 33.4021, 39.3128.
- The new cylinder spectral run took about 24.1 s total and peaked at 716 MiB
  RSS. The separate two-case backward-Euler confirmation took 8.36 s.
  Timings include compilation/cache effects and are not performance guarantees.
- B1 verification and the large production response gate were not rerun.
- Five of the stored B2 report's six source/config hashes still match;
  `hdiv_stokes.py` changed in a6295da. Inspection shows its production form
  was extracted into the shared helper without changing its terms. Retain
  the stored report as historical evidence, not a fresh current-source run.

Runtime versions: Python environment `/tmp/navier-fenicsx`; DOLFINx/Basix/FFCx
0.10.0, UFL 2025.2.1, Gmsh 4.15.2, PETSc 3.25.5 real float64, MPICH 5.0.1,
NumPy 2.5.3, SciPy 1.18.1. The absolute environment path is machine-local;
portable setup remains [B1_SETUP.md](B1_SETUP.md).

Cylinder mesh hashes:

```text
100 mm: 97e8d99450223ab6d448dac3c484152b7590aa00ad5fa3fb3f8a4d3a8475ac78
 70 mm: 8d2ffd3d7e7f563035ee6099e54f7e602135d7c3f2d63d81d124bd6bf4d10e5a
```

## Reproduce the new diagnostic

From the repository root in the optional environment, the following bounded
script combines the spectral and time-step checks. It prints one JSON object
per mesh. It does not modify production defaults or run boundary responses.

```bash
python - <<'PY'
import json, time, resource
import numpy as np
import scipy.linalg as la
from dolfinx import fem, mesh as dmesh
from dolfinx.fem import petsc as fp
import ufl
from realizability.config import PilotConfig
from realizability.backends.hdiv_stokes import create_hdiv_spaces, sip_viscosity_form
from realizability.backends.fenicsx_stokes import create_cylinder, _mesh_sha256, _block_direct_solve

def dense(form):
    matrix = fp.assemble_matrix(fem.form(form))
    matrix.assemble()
    rows, cols = matrix.getSize()
    out = matrix.getValues(np.arange(rows,dtype=np.int32), np.arange(cols,dtype=np.int32))
    matrix.destroy()
    return out

cfg=PilotConfig()
for size in (0.10,0.07):
    start=time.perf_counter()
    domain,_,_=create_cylinder(cfg,size)
    assert domain.comm.size == 1, "Run this bounded diagnostic in serial."
    V,Q=create_hdiv_spaces(domain)
    u,v,q=ufl.TrialFunction(V),ufl.TestFunction(V),ufl.TestFunction(Q)
    n,h=ufl.FacetNormal(domain),ufl.CellDiameter(domain)
    domain.topology.create_connectivity(2,3)
    bc=fem.locate_dofs_topological(V,2,dmesh.exterior_facet_indices(domain.topology))
    free=np.setdiff1d(np.arange(V.dofmap.index_map.size_global),bc)
    assert len(free) <= 3000, "This diagnostic is intentionally limited to small meshes."
    B=dense(-q*ufl.div(u)*ufl.dx)[:,free]
    Z=la.null_space(B)
    M=dense(ufl.inner(u,v)*ufl.dx)[np.ix_(free,free)]
    Mz=Z.T@M@Z
    records=[]
    for alpha in (6.,12.,24.,48.):
        A=dense(sip_viscosity_form(u,v,n,h,cfg.fluid.kinematic_viscosity,alpha))[np.ix_(free,free)]
        symmetry=np.linalg.norm(A-A.T)/np.linalg.norm(A)
        Az=Z.T@A@Z
        vals,vecs=la.eigh((Az+Az.T)/2,(Mz+Mz.T)/2,subset_by_index=(0,0))
        rate=float(vals[0]); y=vecs[:,0]
        w=fem.Function(V); w.x.array[free]=Z@y; w.x.scatter_forward()
        mass=float(fem.assemble_scalar(fem.form(ufl.inner(w,w)*ufl.dx)))
        div=float(fem.assemble_scalar(fem.form(ufl.div(w)**2*ufl.dx)))
        normal=float(fem.assemble_scalar(fem.form(ufl.dot(w,n)**2*ufl.ds)))
        viscous=float(fem.assemble_scalar(fem.form(sip_viscosity_form(w,w,n,h,cfg.fluid.kinematic_viscosity,alpha))))
        decay_metrics={}
        if size == 0.07 and alpha in (6.,48.):
            p=ufl.TrialFunction(Q)
            zero=fem.Function(V)
            bc_zero=fem.dirichletbc(zero,bc)
            dt=1.0
            lhs=[[ufl.inner(u,v)/dt*ufl.dx + sip_viscosity_form(u,v,n,h,cfg.fluid.kinematic_viscosity,alpha),-p*ufl.div(v)*ufl.dx],[-q*ufl.div(u)*ufl.dx,None]]
            rhs=[ufl.inner(w/dt,v)*ufl.dx,ufl.ZeroBaseForm((q,))]
            (after,pressure),_,solve_residual,_,_= _block_direct_solve(lhs,rhs,[bc_zero],[V,Q],(1,),"audit_decay_")
            after_mass=float(fem.assemble_scalar(fem.form(ufl.inner(after,after)*ufl.dx)))
            decay_metrics=dict(time_step_s=dt,measured_energy_ratio=after_mass/mass,
                predicted_energy_ratio=1/(1+dt*rate)**2,step_algebraic_residual=solve_residual)
        records.append(dict(**decay_metrics,alpha=alpha,minimum_decay_rate_per_s=rate,symmetry_relative_error=float(symmetry),
          eigenpair_relative_residual=float(np.linalg.norm(Az@y-rate*(Mz@y))/(np.linalg.norm(Az@y)+abs(rate)*np.linalg.norm(Mz@y))),
          velocity_mass=mass,divergence_ratio=float(cfg.geometry.radius*np.sqrt(max(div,0)/mass)),
          boundary_normal_l2=float(np.sqrt(max(normal,0))),assembled_rayleigh_per_s=viscous/mass))
    print(json.dumps(dict(mesh_size=size,cells=domain.topology.index_map(3).size_global,
      mesh_sha256=_mesh_sha256(domain),free_velocity_dofs=len(free),divergence_free_dofs=Z.shape[1],
      divergence_nullspace_relative_residual=float(np.linalg.norm(B@Z)/np.linalg.norm(B)),
      records=records,elapsed_seconds=time.perf_counter()-start,
      peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024),indent=2),flush=True)
PY
```

The target-normal mismatch can be reproduced separately with:

```bash
python - <<'PY'
import json
from basix.ufl import element
from dolfinx import fem
import ufl
from realizability.config import PilotConfig
from realizability.boundary_modes import parse_mode
from realizability.backends.fenicsx_stokes import create_cylinder,_mode_expression,SIDE_TAG
cfg=PilotConfig(); rows=[]
for h in (0.10,0.07,0.04):
    d,_,tags=create_cylinder(cfg,h)
    W=fem.functionspace(d,element("Lagrange",d.basix_cell(),2,shape=(3,)))
    g=fem.Function(W); g.interpolate(_mode_expression(parse_mode("T_00c"),cfg,1.))
    n=ufl.FacetNormal(d); ds=ufl.Measure("ds",domain=d,subdomain_data=tags)
    norm2=float(fem.assemble_scalar(fem.form(ufl.inner(g,g)*ds(SIDE_TAG))))
    normal2=float(fem.assemble_scalar(fem.form(ufl.dot(g,n)**2*ds(SIDE_TAG))))
    rows.append(dict(mesh_size=h,target_normal_to_full_l2_ratio=(normal2/norm2)**.5))
print(json.dumps(rows,indent=2))
PY
```

## 2026-09-20 implementation result

The bounded implementation package described above is now available without
changing the physical pilot, its feature definitions, or its acceptance
thresholds.

```bash
python -m realizability.cli b2-stability \
  --config configs/realizability/pilot.json
python -m realizability.cli b2-verify \
  --config configs/realizability/pilot.json
```

`b2-stability` writes strict JSON and Markdown.  Its JSON records the complete
benchmark configuration, dependency versions, contributing source hashes, mesh
hashes, free and divergence-free DOFs, elapsed time, peak RSS, the mass-metric
eigenpair check, direct SIP quadratic-form check, and the targeted unforced
backward-Euler step.  The dense path is serial and refuses a mesh with more
than 3000 free velocity DOFs.

The B2 gate now performs this audit before any harmonic solve.  Its defaults
are explicitly alpha=48 and alpha=96 for a bounded verification comparison;
they are candidates only, not a production certificate.  A failed requested
penalty returns an explicit failed gate and does not launch the pilot solves.
The historical alpha=6 report remains historical evidence of a failed gate.

On the 100 and 70 mm cylinder fixtures, alpha=48 and alpha=96 had positive
minimum decay rates (1/s):

| Mesh | alpha=48 | alpha=96 |
|---:|---:|---:|
| 100 mm | 0.00185910664480 | 0.00200938619304 |
| 70 mm | 0.00168736418397 | 0.00175832058384 |

The 70 mm backward-Euler energy ratios agreed with their eigenvalue
predictions to roundoff: 0.996633794049 for alpha=48 and 0.996492612209 for
alpha=96.  This establishes only the stated small-fixture energy check.

The weak target is now evaluated facet-wise as `P_t*g + (g_BDM dot n)*n` on
the tagged side boundary.  Harmonic reports include normalized side/cap
tangential trace error, target-normal mismatch, actual normal error, and
interior tangential jumps.  The smooth-target normal mismatch for `T_00c`
remains visible on the planar side mesh (9.812% at 70 mm and 7.612% at 50 mm),
but it is no longer present in the weak target's normal component.

`b2-verify` also runs a smooth non-affine, divergence-free manufactured cube
fixture.  Its BDM velocity L2 error decreased from 0.0587035 at cube
resolution 3 to 0.0245511 at resolution 4, with divergence below
`1.7e-13` and algebraic residual below `8.2e-14`.

For the deliberately easier swirl fixture (`nu=1e-4 m^2/s`, `f=0.001 Hz`),
the independent smooth-cylinder gain is `8.26699750702 - 0.588020446807 i`
1/m.  With alpha=48, the 70 mm and 50 mm BDM gains had respectively 9.471%
and 4.855% relative magnitude error, with phase errors 0.246 and 0.218
degrees.  The 50 mm alpha=48-to-96 comparison changed magnitude by 4.225%
and phase by 0.105 degrees.  Fixed feature quadrature changes were at most
0.00276 1/m.  These are verification-fixture results, not validation of the
physical 0.01 Hz pilot.

No production mesh, solver, or universal penalty has been selected.  The next
step requires numerical-method review before any physical-pilot gate is rerun
or a six-mode campaign is considered.
