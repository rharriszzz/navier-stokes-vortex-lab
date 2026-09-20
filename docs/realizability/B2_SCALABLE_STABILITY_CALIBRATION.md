# R005 stability calibration appendix

This is a review-only reproduction record for
[B2_SCALABLE_STABILITY_REVIEW.md](B2_SCALABLE_STABILITY_REVIEW.md).
It adds no backend command or production solver. The script uses the existing
3,000-free-DOF guard and only the 100/70 mm cylinder fixtures. The sparse
inertia comparison is restricted to the 100 mm fixture. Read the review for
interpretation, acceptance criteria, resource caps, and the next task.

## Recorded provenance

The working tree differed from the recorded commit only by request-log and
review documentation work. Numerical source was unchanged. Runtime evidence
was generated with `PilotConfig()`; the pilot file hash is recorded for
provenance, but the script does not load configuration from that file.

```json
{
  "commit": "21676b96ced6c2372fc8ca350c9650a90960fe3a",
  "source_sha256": {
    "realizability/config.py": "3cb3edbb28e203226056cf4ac5e7832951c33e5f932b13a5ec438de88c786d12",
    "realizability/backends/fenicsx_stokes.py": "37ecd62121553e13f273fb99c7bc2649f51d9cea57658f4bce8069c4ac80a206",
    "realizability/backends/hdiv_stokes.py": "f23b252f91c406e3e279c7e6e7049e301ad604fae232dd0a610a73319864d2e9",
    "realizability/backends/b2_stability.py": "18b2e75712255a681a0c22f012d81ab3a129e147c41f3f8974bb46cf6a8df9f1",
    "configs/realizability/pilot.json": "0e60a6ee85063f5d86b84db5af053f2166126249255edeafae4b4e6242db10d0"
  },
  "script_sha256": "de7057ae94e4996f0125fbd9de2ba8008532714b7161b68510539a9f6000b39e",
  "versions": {
    "dolfinx": "0.10.0",
    "basix": "0.10.0",
    "ufl": "2025.2.1",
    "ffcx": "0.10.0",
    "gmsh": "4.15.2",
    "numpy": "2.5.3",
    "petsc": "3.25.5",
    "petsc_scalar_type": "float64",
    "mpi": "MPICH Version:      5.0.1"
  },
  "scipy_version": "1.18.1",
  "elapsed_seconds": 46.863936199995806,
  "peak_rss_mib": 796.05859375
}
```

## Reproduction

From the repository root with the optional environment in
[B1_SETUP.md](B1_SETUP.md), extract the Python block below to
`/tmp/navier-b2-stability-method-r005/calibrate.py`, creating that directory
first. Run it with the repository on the Python import path:

```bash
# Use the optional environment's python executable.
timeout 180s python -c 'exec(compile(open("/tmp/navier-b2-stability-method-r005/calibrate.py").read(), "/tmp/navier-b2-stability-method-r005/calibrate.py", "exec"))'
```

The script writes strict `dense.json`, `local.json`, and `provenance.json` to
that temporary directory and asserts local-form and sparse-inertia agreement.
It reproduces the calculation at the checked-out source; compare source and
mesh hashes before interpreting a difference. Normal imports/cache creation
require the optional environment's usual filesystem permissions.

The following block is byte-for-byte the script used for the recorded run.
Its SHA-256 is included above. The dense audit deliberately reports false for
unstable cases; successful script execution does not mean all physical cases
passed. No full response solve is performed.

```python
import itertools
import json
import resource
import hashlib
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy
import scipy.linalg as la
from dolfinx import fem, mesh as dmesh
from dolfinx.fem import petsc as fp
from petsc4py import PETSc
from scipy import sparse
import ufl

from realizability.config import PilotConfig
from realizability.backends.fenicsx_stokes import create_cylinder, _mesh_sha256, solver_versions
from realizability.backends.hdiv_stokes import create_hdiv_spaces, sip_viscosity_form, _jump
from realizability.backends.b2_stability import _dense, run_cylinder_stability_audit

def assembled(form):
    mat = fp.assemble_matrix(fem.form(form))
    mat.assemble()
    indptr, indices, values = mat.getValuesCSR()
    result = sparse.csr_matrix((values.copy(), indices.copy(), indptr.copy()), shape=mat.getSize())
    mat.destroy()
    return result

def local_bound(domain):
    started = time.perf_counter()
    assert domain.comm.size == 1
    assert domain.geometry.dofmap.shape[1] == 4
    xyz = domain.geometry.x[domain.geometry.dofmap]
    nc = len(xyz)
    volumes = np.abs(np.linalg.det(xyz[:, 1:] - xyz[:, :1])) / 6
    diameters = np.max([np.linalg.norm(xyz[:, i]-xyz[:, j], axis=1)
                       for i, j in itertools.combinations(range(4), 2)], axis=0)
    faces = {}
    for cell, nodes in enumerate(domain.geometry.dofmap):
        for local in itertools.combinations(range(4), 3):
            faces.setdefault(tuple(sorted(int(nodes[i]) for i in local)), []).append((cell, local))
    trace = np.zeros((nc, 4, 4))
    for entries in faces.values():
        assert len(entries) in (1, 2)
        h = float(np.mean([diameters[k] for k, _ in entries]))
        weight = 1 if len(entries) == 1 else .5
        for k, local in entries:
            vertices = xyz[k, list(local)]
            area = np.linalg.norm(np.cross(vertices[1]-vertices[0], vertices[2]-vertices[0])) / 2
            trace[k][np.ix_(local, local)] += weight*h*area/12*(np.ones((3, 3))+np.eye(3))
    mass = volumes[:, None, None]/20*(np.ones((4, 4))+np.eye(4))
    transform = np.eye(4) - (1-1/np.sqrt(5))/4*np.ones((4, 4))
    whitened = 20/volumes[:, None, None]*(transform @ trace @ transform)
    exact = np.linalg.eigvalsh(whitened)[:, -1]
    upper = np.max(np.sum(np.abs(whitened), axis=2), axis=1)
    residual = 0.
    for k in range(nc):
        vals, vecs = la.eigh(trace[k], mass[k])
        z = vecs[:, -1]
        residual = max(residual, float(np.linalg.norm(trace[k]@z-vals[-1]*(mass[k]@z)) /
                       (np.linalg.norm(trace[k]@z)+abs(vals[-1])*np.linalg.norm(mass[k]@z))))
        assert np.isclose(vals[-1], exact[k], rtol=1e-12)
    assert np.all(upper >= exact-1e-11)
    Q = fem.functionspace(domain, ('DG', 1))
    p, q = ufl.TrialFunction(Q), ufl.TestFunction(Q)
    h = ufl.CellDiameter(domain)
    local_mass = assembled(p*q*ufl.dx)
    local_trace = assembled(ufl.avg(h)/2*(p('+')*q('+')+p('-')*q('-'))*ufl.dS + h*p*q*ufl.ds)
    ufl_error = 0.
    for cell in range(nc):
        dofs = Q.dofmap.cell_dofs(cell)
        tm = local_trace[dofs][:, dofs].toarray()
        mm = local_mass[dofs][:, dofs].toarray()
        actual = la.eigvalsh(tm, mm)[-1]
        ufl_error = max(ufl_error, float(abs(actual-exact[cell])/exact[cell]))
    assert ufl_error < 1e-12
    k = int(np.argmax(upper))
    return dict(cells=nc, local_exact_max=float(max(exact)), gershgorin_upper=float(max(upper)),
                worst_cell=k, minimum_volume_m3=float(min(volumes)), local_eigen_residual=residual,
                ufl_relative_error=ufl_error, elapsed_seconds=time.perf_counter()-started)

def sparse_inertia(A, B, M, shift):
    started = time.perf_counter()
    # B has exactly one constant-pressure row dependency in these fixtures.
    reduced = B[1:]
    K = sparse.bmat([[A-shift*M, reduced.T], [reduced, None]], format='csr')
    K = (K+K.T)*.5
    K = K.tocsr()
    mat = PETSc.Mat().createAIJ(size=K.shape, csr=(K.indptr, K.indices, K.data), comm=PETSc.COMM_SELF)
    mat.setOption(PETSc.Mat.Option.SYMMETRIC, True)
    mat.setOption(PETSc.Mat.Option.SPD, False)
    opts = PETSc.Options()
    opts['r005_mat_mumps_icntl_13'] = 1
    opts['r005_mat_mumps_icntl_24'] = 1
    pc = PETSc.PC().create(PETSc.COMM_SELF)
    pc.setOptionsPrefix('r005_')
    pc.setOperators(mat)
    pc.setType('cholesky')
    pc.setFactorSolverType('mumps')
    pc.setFromOptions()
    pc.setUp()
    factor = pc.getFactorMatrix()
    inertia = factor.getInertia()
    pc.destroy()
    mat.destroy()
    return dict(shift_per_s=shift, inertia=list(inertia), constraint_rank=B.shape[0]-1,
                elapsed_seconds=time.perf_counter()-started)

cfg = PilotConfig()
started = time.perf_counter()
audit = run_cylinder_stability_audit(cfg, penalty_factors=(6.,12.,24.,48.,96.))
Path('/tmp/navier-b2-stability-method-r005/dense.json').write_text(json.dumps(audit, indent=2, allow_nan=False)+'\n')
records=[]
for size in (.10, .07):
    start = time.perf_counter()
    domain, _, _ = create_cylinder(cfg, size)
    bound = local_bound(domain)
    record = dict(mesh_size_m=size, mesh_sha256=_mesh_sha256(domain), bound=bound)
    if size == .10:
        V, Q = create_hdiv_spaces(domain)
        u, v, q = ufl.TrialFunction(V), ufl.TestFunction(V), ufl.TestFunction(Q)
        domain.topology.create_connectivity(2, 3)
        boundary = fem.locate_dofs_topological(V, 2, dmesh.exterior_facet_indices(domain.topology))
        free = np.setdiff1d(np.arange(V.dofmap.index_map.size_global), boundary)
        assert len(free) <= 3000
        B = assembled(-q*ufl.div(u)*ufl.dx)[:, free]
        M = assembled(ufl.inner(u,v)*ufl.dx)[free][:, free]
        assert np.linalg.norm(B.T@np.ones(B.shape[0]))/sparse.linalg.norm(B) < 1e-12
        Z = la.null_space(B.toarray())
        assert Z.shape[1] == len(free)-(B.shape[0]-1)
        inertia_records=[]
        for alpha in (6.,48.):
            A = assembled(sip_viscosity_form(u,v,ufl.FacetNormal(domain),ufl.CellDiameter(domain),cfg.fluid.kinematic_viscosity,alpha))[free][:, free]
            eigenvalues = la.eigvalsh(Z.T@A@Z, Z.T@M@Z)
            for shift in (0., float(eigenvalues[0]-1e-7), float(eigenvalues[0]+1e-7)):
                result = sparse_inertia(A,B,M,shift)
                result['penalty_factor'] = alpha
                result['dense_negative_count'] = int(np.sum(eigenvalues<shift))
                assert result['inertia'][0]-result['constraint_rank'] == result['dense_negative_count']
                assert result['inertia'][1] == 0
                inertia_records.append(result)
        record['inertia_calibration'] = inertia_records
    records.append(record)
    print(json.dumps(record), flush=True)
Path('/tmp/navier-b2-stability-method-r005/local.json').write_text(json.dumps(records, indent=2, allow_nan=False)+'\n')
files = ['realizability/config.py', 'realizability/backends/fenicsx_stokes.py', 'realizability/backends/hdiv_stokes.py', 'realizability/backends/b2_stability.py', 'configs/realizability/pilot.json']
provenance = dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    source_sha256={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files},
    script_sha256=hashlib.sha256(Path('/tmp/navier-b2-stability-method-r005/calibrate.py').read_bytes()).hexdigest(),
    versions=asdict(solver_versions()), scipy_version=scipy.__version__,
    elapsed_seconds=time.perf_counter()-started, peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
Path('/tmp/navier-b2-stability-method-r005/provenance.json').write_text(json.dumps(provenance, indent=2, allow_nan=False)+'\n')
print(json.dumps(provenance), flush=True)
```

## Separate local-cost measurement

A second fresh interpreter executed only the definitions above and then
created the same two meshes and called `local_bound` on each. This omitted the
dense audit and the sparse inertia calculations. It measured a warm-cache
local calculation separately from the full calibration's peak RSS.

```json
{
  "records": [
    {
      "mesh_size_m": 0.1,
      "mesh_seconds": 0.03590021698619239,
      "bound": {
        "cells": 82,
        "local_exact_max": 49.25110289373433,
        "gershgorin_upper": 56.03719011765142,
        "worst_cell": 53,
        "minimum_volume_m3": 4.358929849847638e-05,
        "local_eigen_residual": 6.051484249006961e-16,
        "ufl_relative_error": 4.194445991396837e-15,
        "elapsed_seconds": 0.027398300007916987
      }
    },
    {
      "mesh_size_m": 0.07,
      "mesh_seconds": 0.006199026000103913,
      "bound": {
        "cells": 171,
        "local_exact_max": 31.096973732617343,
        "gershgorin_upper": 36.72009579870269,
        "worst_cell": 86,
        "minimum_volume_m3": 1.9156415060764778e-05,
        "local_eigen_residual": 6.085432474151562e-16,
        "ufl_relative_error": 5.232971071539087e-15,
        "elapsed_seconds": 0.04763752099825069
      }
    }
  ],
  "elapsed_seconds": 0.11722563600051217,
  "peak_rss_mib": 196.73828125
}
```

Run that measurement after extracting the script, using the optional Python:

```python
from pathlib import Path
code = Path('/tmp/navier-b2-stability-method-r005/calibrate.py').read_text()
exec(code.split('cfg = PilotConfig()')[0])
start = time.perf_counter()
records = []
for size in (.10, .07):
    mesh_start = time.perf_counter()
    domain, _, _ = create_cylinder(PilotConfig(), size)
    records.append(dict(mesh_size_m=size,
                        mesh_seconds=time.perf_counter()-mesh_start,
                        bound=local_bound(domain)))
print(json.dumps(dict(records=records,
                     elapsed_seconds=time.perf_counter()-start,
                     peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024),
                 indent=2, allow_nan=False))
```
