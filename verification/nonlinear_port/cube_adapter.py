"""Unexecuted serial DOLFINx 0.10 adapter source; all external modules injected.

There is intentionally no importer, CLI or execution admission here. A future
supervised driver must supply the pinned modules and own the full attempt.
"""
from math import isfinite
from . import fixtures
from .polynomial import face
from .prototype import Refusal, make_space, build_forms, require_fixture, time_coefficients
from .sparse import CSR, border_and_lift


FACE_TAGS = {(axis, side): 1+2*axis+side
             for axis in range(3) for side in (0, 1)}
RETURNS = (5, 6)


def merge_tags(groups, exterior):
    """Refuse missing, duplicate or interior facets before making MeshTags."""
    found = {}
    if set(groups) != set(range(1, 7)) or any(not len(g) for g in groups.values()):
        raise Refusal('all six nonempty cube faces required')
    for tag, facets in groups.items():
        for facet in facets:
            if int(facet) in found:
                raise Refusal('overlapping boundary facet groups')
            found[int(facet)] = tag
    if set(found) != set(map(int, exterior)):
        raise Refusal('tag inventory does not equal exterior boundary')
    ordered = sorted(found)
    return ordered, [found[i] for i in ordered]


def create_cube(np, meshlib, fem, basix_ufl, comm, subdivisions, fixture):
    require_fixture(fixture)
    if comm.size != 1 or type(subdivisions) is not int or subdivisions not in (2, 4, 8):
        raise Refusal('serial frozen cube levels only')
    domain = meshlib.create_unit_cube(comm, subdivisions, subdivisions, subdivisions,
                                     cell_type=meshlib.CellType.tetrahedron)
    fdim = domain.topology.dim-1
    domain.topology.create_connectivity(fdim, domain.topology.dim)
    groups = {}
    for (axis, side), tag in FACE_TAGS.items():
        groups[tag] = meshlib.locate_entities_boundary(
            domain, fdim, lambda x, a=axis, s=side: np.isclose(x[a], s, rtol=0, atol=1e-12))
    ids, values = merge_tags(groups, meshlib.exterior_facet_indices(domain.topology))
    tags = meshlib.meshtags(domain, fdim, np.asarray(ids, dtype=np.int32),
                           np.asarray(values, dtype=np.int32))
    space = make_space(fem, basix_ufl, domain, fixture)
    dofs = space.dofmap.index_map.size_global * space.dofmap.index_map_bs
    if not 0 < dofs <= 20000 or space.dofmap.index_map.num_ghosts:
        raise Refusal('invalid serial dof inventory or cap exceeded')
    lateral = np.concatenate([groups[tag] for tag in (1, 2, 3, 4)])
    return domain, space, tags, lateral


def fields(name):
    require_fixture(name)
    return getattr(fixtures, name)()


def exact_data(U, domain, name, time):
    """Time may be a DOLFINx Constant; polynomial coefficients remain exact."""
    u, p = fields(name)
    coordinates = [*U.SpatialCoordinate(domain), time]
    vector = lambda polys: U.as_vector([v.evaluate(coordinates) for v in polys])
    sigma = fixtures.stress(u, p)
    targets, pressures, offsets = [], [], []
    for side in (0, 1):
        sign = 2*side-1
        # P = -mean(n.sigma.n), making the normal offset area mean zero.
        pressure = -face(sigma[2][2], 2, side)
        traction = [sign*sigma[i][2].at(2, side) for i in range(3)]
        offset = [v + (sign*pressure if i == 2 else 0)
                  for i, v in enumerate(traction)]
        targets.append(face(sign*u[2], 2, side).evaluate(coordinates))
        pressures.append(pressure.evaluate(coordinates))
        offsets.append(vector(offset))
    return dict(u=vector(u), p=p.evaluate(coordinates),
                force=vector(fixtures.forcing(u, p)), targets=targets,
                pressures=pressures, offsets=offsets)


def interpolate_state(np, fem, space, fixture, time):
    """Exact nodal interpolation, NOT a claim of exact interior representation."""
    u, p = fields(fixture)
    w = fem.Function(space)
    for component, polys in ((0, u), (1, [p])):
        collapsed, mapping = space.sub(component).collapse()
        value = fem.Function(collapsed)
        def evaluate(x, polys=polys, component=component):
            result = [np.broadcast_to(v.evaluate([*x, time]), x.shape[1]) for v in polys]
            return np.asarray(result if component == 0 else result[0])
        value.interpolate(evaluate)
        w.x.array[mapping] = value.x.array
    w.x.scatter_forward()
    return w


def boundary_values(fem, space, lateral, trace):
    """Extract parent mixed-space indices, including cap/lateral edge dofs."""
    indices = fem.locate_dofs_topological(space.sub(0), 2, lateral)
    return {int(i): float(trace.x.array[i]) for i in indices}


def step_forms(U, fem, domain, space, tags, w, previous, older,
               time, dt, step, fixture, degree=24):
    """Compile nothing here. Spatial BE uses exact expression history/load.

    The caller freezes forms per step and sets w/P/eta for every evaluation.
    For affine_time, both historical Functions contain the solved full lift.
    """
    time_coefficients(step, dt)
    if degree not in (24, 26) or not isfinite(time) or not dt <= time <= 1:
        raise Refusal('frozen quadrature and fixture time interval required')
    if fixture in ('manufactured', 'poiseuille') and step != 1:
        raise Refusal('spatial/oracle fixture is a single BE step')
    if fixture == 'rotation':
        raise Refusal('rotation is an exact-field constitutive oracle, not a PDE solve')
    exact = exact_data(U, domain, fixture, time)
    dx = U.Measure('dx', domain=domain, metadata={'quadrature_degree': degree})
    ds = U.Measure('ds', domain=domain, subdomain_data=tags,
                   metadata={'quadrature_degree': degree})
    test, increment = U.TestFunction(space), U.TrialFunction(space)
    constants = [fem.Constant(domain, 0.0) for _ in range(3)]
    history = None
    force = exact['force']
    if fixture == 'manufactured':
        old = exact_data(U, domain, fixture, time-dt)['u']
        history = (old, old)
        u_poly, _ = fields(fixture)
        coords = [*U.SpatialCoordinate(domain), time]
        continuous_dt = U.as_vector([v.d(3).evaluate(coords) for v in u_poly])
        force += (exact['u']-old)/dt-continuous_dt
    result = build_forms(U, w, previous, older, test, increment,
                         U.FacetNormal(domain), dx, ds, RETURNS,
                         constants[:2], constants[2], force, exact['offsets'],
                         exact['targets'], 1.0, step, dt, fixture,
                         exact_history=history)
    # Re-label trial arguments to test arguments before linear-vector assembly.
    result['scalar_rows'] = [U.replace(row, {increment: test})
                             for row in [*result['flux_rows'], result['gauge_row']]]
    return result, constants, dict(exact=exact, force=force, history=history, dx=dx, ds=ds)


class Assembler:
    """One-step raw assembly, followed by bordered zero-increment elimination."""
    def __init__(self, fem, fem_petsc, PETSc, w, forms, constants, fixed):
        if w.function_space.mesh.comm.size != 1:
            raise Refusal('serial adapter only; no per-rank global scalars')
        self.fem, self.fp, self.P = fem, fem_petsc, PETSc
        self.w, self.constants, self.fixed = w, constants, fixed
        self.core = fem.form(forms['jacobian'])
        self.residual = fem.form(forms['momentum_continuity'])
        self.columns = [fem.form(f) for f in [*forms['pressure_columns'], forms['eta_column']]]
        self.rows = [fem.form(f) for f in forms['scalar_rows']]
        self.scalars = [fem.form(f) for f in [*forms['flux_residuals'], forms['gauge_residual']]]

    def vector(self, form):
        vector = self.fp.assemble_vector(form)
        try:
            vector.ghostUpdate(addv=self.P.InsertMode.ADD_VALUES,
                               mode=self.P.ScatterMode.REVERSE)
            return vector.getArray(readonly=True).tolist()
        finally:
            vector.destroy()

    def __call__(self, state):
        n = len(self.w.x.array)
        if len(state) != n+3 or not all(isfinite(v) for v in state):
            raise Refusal('invalid mixed/scalar state')
        if any(state[i] != value for i, value in self.fixed.items()):
            raise Refusal('install new lift before residual evaluation')
        self.w.x.array[:] = state[:n]
        self.w.x.scatter_forward()
        for constant, value in zip(self.constants, state[n:]):
            constant.value = value
        matrix = self.fp.assemble_matrix(self.core)  # no early BC elimination
        try:
            matrix.assemble()
            ptr, cols, vals = matrix.getValuesCSR()
            core = CSR(n, tuple(map(int, ptr)), tuple(map(int, cols)), tuple(map(float, vals)))
        finally:
            matrix.destroy()
        return border_and_lift(core, [self.vector(f) for f in self.columns],
                               [self.vector(f) for f in self.rows], self.vector(self.residual),
                               [float(self.fem.assemble_scalar(f)) for f in self.scalars],
                               state, self.fixed)


def sparse_solve(np, PETSc, comm, matrix, rhs):
    """Serial LU, with explicit status AND true residual checks; no fallback."""
    if comm.size != 1:
        raise Refusal('serial solve only')
    matrix.validate(len(rhs))
    objects = []
    try:
        csr = (np.asarray(matrix.indptr, dtype=PETSc.IntType),
               np.asarray(matrix.indices, dtype=PETSc.IntType),
               np.asarray(matrix.values, dtype=PETSc.ScalarType))
        a = PETSc.Mat().createAIJ(size=(matrix.n, matrix.n), csr=csr, comm=comm)
        objects.append(a)
        a.assemble()
        b = a.createVecRight()
        objects.append(b)
        x = a.createVecRight()
        objects.append(x)
        b.getArray()[:] = rhs
        ksp = PETSc.KSP().create(comm)
        objects.append(ksp)
        ksp.setOperators(a)
        ksp.setType('preonly')
        ksp.getPC().setType('lu')
        ksp.getPC().setFactorSolverType('petsc')
        # No setFromOptions: ambient command-line options must not alter method.
        ksp.solve(b, x)
        answer = x.getArray(readonly=True).tolist()
        if ksp.getConvergedReason() <= 0 or not all(isfinite(v) for v in answer):
            raise Refusal('sparse linear solve failed')
        from math import sqrt, fsum
        defect = sqrt(fsum((v-b)**2 for v, b in zip(matrix.matvec(answer), rhs)))
        if defect > max(1e-13, 1e-8*sqrt(fsum(v*v for v in rhs))):
            raise Refusal('sparse linear true residual failed')
        return answer
    finally:
        for obj in reversed(objects):
            obj.destroy()
