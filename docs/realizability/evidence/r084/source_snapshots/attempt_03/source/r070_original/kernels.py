"""Disposable R014 local projection and exact-circle polynomial moments.

No PDE solve and no physical parameters are selected in this module.
"""
import cmath
import itertools
import math
import numpy as np

EPS = np.finfo(float).eps
MOMENTS = [(a, b) for a in range(4) for b in range(4-a)]
MONOMIALS3 = [(a,b,c) for a in range(3) for b in range(3-a)
              for c in range(3-a-b)]

def gauss(n):
    x, w = np.polynomial.legendre.leggauss(n)
    return (x+1)/2, w/2

def trig_integral(p, q, start, end):
    """Exact finite Fourier expansion of cos(theta)^p sin(theta)^q."""
    terms = []
    for j in range(p+1):
        for k in range(q+1):
            frequency = p+q-2*(j+k)
            coefficient = math.comb(p,j)*math.comb(q,k)*(-1)**k/(2**(p+q)*1j**q)
            # Midpoint/sinc avoids subtracting nearly equal complex exponentials.
            midpoint = (start+end)/2
            width = end-start
            primitive = width if frequency == 0 else (
                2*math.sin(frequency*width/2)/frequency
                * cmath.exp(1j*frequency*midpoint))
            terms.append(coefficient*primitive)
    value = complex(math.fsum(t.real for t in terms),math.fsum(t.imag for t in terms))
    assert abs(value.imag) <= 256*EPS*max(1,sum(abs(t) for t in terms))
    return value.real

def cross2(a, b):
    return a[0]*b[1]-a[1]*b[0]

def circle_polygon_moments(polygon):
    """Convex CCW polygon intersect unit disk; retain straight edges and arcs.

    No vertex snapping or small-area filtering. Long-double signs classify
    line/circle intersections; an exactly zero-area polygon has zero moments.
    """
    polygon = np.asarray(polygon, dtype=np.longdouble)
    empty = dict(moments=[0.]*10, gauss16=[0.]*10, gauss32=[0.]*10,
                 absolute_boundary_contributions=[0.]*10, segments=0, arcs=0)
    if len(polygon) < 3:
        return empty
    area2 = sum(cross2(a,b) for a,b in zip(polygon,np.roll(polygon,-1,axis=0)))
    if area2 == 0:
        return empty
    if area2 < 0:
        raise RuntimeError('Clockwise polygon refused')
    segments, angles = [], [0., 2*math.pi]
    for a,b in zip(polygon,np.roll(polygon,-1,axis=0)):
        v = b-a
        aa, bb, cc = v@v, 2*(a@v), a@a-1
        if aa == 0:
            raise RuntimeError('Duplicate polygon edge')
        disc = bb*bb-4*aa*cc
        if disc < 0:
            continue
        root = np.sqrt(disc)
        lo, hi = (-bb-root)/(2*aa), (-bb+root)/(2*aa)
        for t in (lo,hi):
            if 0 <= t <= 1:
                p = a+t*v
                angles.append(math.atan2(float(p[1]),float(p[0])) % (2*math.pi))
        lo, hi = max(np.longdouble(0),lo),min(np.longdouble(1),hi)
        if hi > lo:
            segments.append((np.asarray(a+lo*v,float),np.asarray(a+hi*v,float)))
    angles = sorted(set(angles))
    arcs = []
    for start,end in zip(angles[:-1],angles[1:]):
        if end <= start:
            continue
        mid = (start+end)/2
        point = np.array([math.cos(mid),math.sin(mid)],dtype=np.longdouble)
        inside = all(cross2(b-a,point-a) >= 0 for a,b in
                     zip(polygon,np.roll(polygon,-1,axis=0)))
        if inside:
            count = max(1,math.ceil((end-start)/(math.pi/4)))
            for i in range(count):
                arcs.append((start+(end-start)*i/count,start+(end-start)*(i+1)/count))
    outputs = [[],[],[]]
    absolute = []
    line_x, line_w = gauss(3)
    arc_rules = [gauss(16),gauss(32)]
    for a,b in MOMENTS:
        straight = []
        for p,q in segments:
            points = p+line_x[:,None]*(q-p)
            straight.append(float(np.sum(line_w*points[:,0]**(a+1)*points[:,1]**b)
                                  *(q[1]-p[1])/(a+1)))
        analytic = [trig_integral(a+2,b,s,e)/(a+1) for s,e in arcs]
        outputs[0].append(math.fsum(straight+analytic))
        absolute.append(math.fsum(abs(t) for t in straight+analytic))
        for i,(nodes,weights) in enumerate(arc_rules):
            numerical=[]
            for s,e in arcs:
                theta=s+(e-s)*nodes
                numerical.append(float((e-s)*np.sum(weights*np.cos(theta)**(a+2)
                                                     *np.sin(theta)**b)/(a+1)))
            outputs[i+1].append(math.fsum(straight+numerical))
    return dict(moments=outputs[0],gauss16=outputs[1],gauss32=outputs[2],
                absolute_boundary_contributions=absolute,
                segments=len(segments),arcs=len(arcs))

def duffy(vertices, order):
    nodes,weights=gauss(order)
    xi,eta=np.meshgrid(nodes,nodes,indexing='ij')
    wx,wy=np.meshgrid(weights,weights,indexing='ij')
    A,B,C=np.asarray(vertices)
    points=A+xi.ravel()[:,None]*(B-A)+((1-xi)*eta).ravel()[:,None]*(C-A)
    w=(wx*wy*(1-xi)).ravel()*np.linalg.norm(np.cross(B-A,C-A))
    return points,w

def cell_basis(V, cell, points, derivatives=True):
    """Oriented physical BDM basis and gradients under affine Piola mapping."""
    mesh=V.mesh
    vertices=mesh.geometry.x[mesh.geometry.dofmap[cell],:3]
    J=(vertices[1:]-vertices[0]).T
    invJ=np.linalg.inv(J)
    detJ=float(np.linalg.det(J))
    ref=(np.asarray(points)-vertices[0])@invJ.T
    table=V.element.basix_element.tabulate(1 if derivatives else 0,ref)
    mesh.topology.create_entity_permutations()
    info=mesh.topology.get_cell_permutation_info()[cell:cell+1]
    oriented=np.ascontiguousarray(table.transpose(2,0,1,3))
    V.element.T_apply(oriented.reshape(-1), info, oriented.shape[1]*oriented.shape[2]*3)
    table=oriented.transpose(1,2,0,3)
    values=np.einsum('pbi,ji->pbj',table[0],J)/detJ
    if not derivatives:
        return values
    gradients=np.einsum('kpbi,ji,kl->pbjl',table[1:4],J,invJ)/detJ
    return values,gradients

def facet_geometry(V,cell,local_facet):
    import basix
    vertices=V.mesh.geometry.x[V.mesh.geometry.dofmap[cell],:3]
    local_vertices=basix.topology(basix.CellType.tetrahedron)[2][local_facet]
    triangle=vertices[local_vertices]
    normal=np.cross(triangle[1]-triangle[0],triangle[2]-triangle[0])
    normal/=np.linalg.norm(normal)
    if np.dot(normal,np.mean(vertices,axis=0)-triangle[0]) > 0:
        normal=-normal
    h=max(np.linalg.norm(a-b) for a,b in itertools.combinations(vertices,2))
    return triangle,normal,h

def local_project_load(V,cell,local_facet,target,order,nu=1.,alpha=96.):
    """L2 facet normal projection and matching Nitsche RHS (unit-speed fields).

    Target callable receives at most 256 physical points per evaluation.
    Both polynomial mass and target moments use the specified Duffy rule.
    """
    triangle,normal,h=facet_geometry(V,cell,local_facet)
    points,weights=duffy(triangle,order)
    facet_dofs=np.array(V.element.basix_element.entity_dofs[2][local_facet])
    mass=np.zeros((6,6))
    moment=np.zeros(6,dtype=complex)
    chunks=[]
    for start in range(0,len(points),256):
        p,w=points[start:start+256],weights[start:start+256]
        basis,gradient=cell_basis(V,cell,p)
        psi=basis[:,facet_dofs]@normal
        velocity=np.asarray(target(p),dtype=complex)
        if velocity.shape != p.shape or not np.isfinite(velocity).all():
            raise RuntimeError('Invalid target values')
        exact_normal=velocity@normal
        mass+=np.einsum('p,pi,pj->ij',w,psi,psi)
        moment+=np.einsum('p,pi,p->i',w,psi,exact_normal)
        chunks.append((w,basis,gradient,psi,velocity))
    coefficients=np.linalg.solve(mass,moment)
    load=np.zeros(V.element.space_dimension,dtype=complex)
    absolute=np.zeros_like(load.real)
    signed=0j
    absflux=np.zeros(2)
    max_speed=0.
    for w,basis,gradient,psi,velocity in chunks:
        gamma=psi@coefficients
        gh=velocity-(velocity@normal)[:,None]*normal+gamma[:,None]*normal
        dn=np.einsum('pbij,j->pbi',gradient,normal)
        terms=nu*w[:,None]*np.einsum('pi,pbi->pb',gh,-dn+alpha/h*basis)
        load+=np.sum(terms,axis=0)
        absolute+=np.sum(np.abs(terms),axis=0)
        signed+=np.sum(w*gamma)
        absflux+=np.array([np.sum(w*abs(gamma.real)),np.sum(w*abs(gamma.imag))])
        max_speed=max(max_speed,float(np.max(np.linalg.norm(velocity,axis=1))))
    return dict(coefficients=coefficients,load=load,absolute=absolute,
                facet_dofs=facet_dofs,normal=normal,mass=mass,moment=moment,
                signed_flux=signed,absolute_flux=absflux,sampled_speed=max_speed)

def polynomial_values(points,powers):
    return np.prod(np.asarray(points)[:,None,:]**np.asarray(powers)[None,:,:],axis=2)

def disk_toys():
    """Known moments, exact arcs, jumps and degenerate contacts."""
    square=[[-2,-2],[2,-2],[2,2],[-2,2]]
    quarter=[[0,0],[2,0],[2,2],[0,2]]
    half=[[0,-2],[2,-2],[2,2],[0,2]]
    triangle=[[0,0],[.5,0],[0,.5]]
    segment=[[.5,-2],[2,-2],[2,2],[.5,2]]
    tangent_edge=[[1,-2],[2,-2],[2,2],[1,2]]
    tangent_vertex=[[1,0],[2,-1],[2,1]]
    def quadrant(a,b):
        return math.gamma((a+1)/2)*math.gamma((b+1)/2)/(2*(a+b+2)*math.gamma((a+b+2)/2))
    expected_full=[4*quadrant(a,b) if a%2==b%2==0 else 0. for a,b in MOMENTS]
    cases=[('disk',square,expected_full),
           ('quarter',quarter,[quadrant(a,b) for a,b in MOMENTS]),
           ('half',half,[2*quadrant(a,b) if b%2==0 else 0. for a,b in MOMENTS]),
           ('triangle',triangle,[.5**(a+b+2)*math.factorial(a)*math.factorial(b)/math.factorial(a+b+2)
                                 for a,b in MOMENTS]),
           ('tangent_edge',tangent_edge,[0.]*10),('tangent_vertex',tangent_vertex,[0.]*10)]
    records=[]
    for name,polygon,expected in cases:
        result=circle_polygon_moments(polygon)
        error=float(np.max(np.abs(np.array(result['moments'])-expected)))
        independent=max(float(np.max(abs(np.array(result[k])-result['moments'])))
                        for k in ('gauss16','gauss32'))
        tol=256*EPS*max(1.,sum(result['absolute_boundary_contributions']))
        records.append(dict(name=name,error=error,independent_difference=independent,tolerance=tol))
        if max(error,independent)>tol:
            raise RuntimeError('Disk toy failed: '+name)
    result=circle_polygon_moments(segment)
    expected_area=math.acos(.5)-.5*math.sqrt(.75)
    assert abs(result['moments'][0]-expected_area)<256*EPS
    # Opposite halves partition a disk and integrate different polynomial traces.
    left=circle_polygon_moments([[-2,-2],[0,-2],[0,2],[-2,2]])
    right=circle_polygon_moments(half)
    assert np.max(abs(np.array(left['moments'])+right['moments']-expected_full))<256*EPS
    # Velocity (-y,x) has rotation numerator x^2+y^2; strain (x,-y) has -2xy.
    index={powers:i for i,powers in enumerate(MOMENTS)}
    full=np.asarray(expected_full)
    rotation=full[index[(2,0)]]+full[index[(0,2)]]
    strain=-2*full[index[(1,1)]]
    assert abs(rotation-math.pi/2)<256*EPS and strain==0
    jump=left['moments'][index[(2,0)]]+left['moments'][index[(0,2)]]
    jump+=2*(right['moments'][index[(2,0)]]+right['moments'][index[(0,2)]])
    assert abs(jump-3*math.pi/4)<256*EPS
    records.append(dict(name='segment_partition_rotation_strain_jump',
                        segment_area=result['moments'][0],rotation=rotation,strain=strain,jump=jump))
    return records

def load_toys(checkpoint):
    """All 24 affine reference-vertex permutations and 30 spanning P2^3 traces."""
    import basix.ufl
    import ufl
    from dolfinx import fem,mesh
    from mpi4py import MPI
    from realizability.backends.hdiv_stokes import create_hdiv_spaces
    ref=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
    ufl_domain=ufl.Mesh(basix.ufl.element('Lagrange','tetrahedron',1,shape=(3,)))
    records=[]
    for permutation in itertools.permutations(range(4)):
        domain=mesh.create_mesh(MPI.COMM_SELF,np.array([[0,1,2,3]],dtype=np.int64),
                                ufl_domain,ref[list(permutation)])
        V,_=create_hdiv_spaces(domain)
        vertices=domain.geometry.x[domain.geometry.dofmap[0],:3]
        sample=vertices[0]+np.array([[.17,.23,.19],[.11,.31,.27]])@(vertices[1:]-vertices[0])
        basis=cell_basis(V,0,sample,False)
        function=fem.Function(V)
        dofs=V.dofmap.cell_dofs(0)
        eval_error=0.
        for j in range(30):
            function.x.array[:]=0
            function.x.array[dofs[j]]=1
            values=function.eval(sample,np.zeros(len(sample),dtype=np.int32))
            eval_error=max(eval_error,float(np.max(abs(values-basis[:,j]))))
        scale=max(1.,float(np.max(abs(basis))))
        if eval_error>256*EPS*scale:
            raise RuntimeError('Oriented basis differs from DOLFINx evaluation')
        projection_error=0.
        load_error=0.
        load_scale=0.
        for powers in MONOMIALS3:
            for component in range(3):
                def target(p):
                    out=np.zeros_like(p)
                    out[:,component]=np.prod(p**np.array(powers),axis=1)
                    return out
                # Independent coefficient values from ordinary interpolation of an exact polynomial.
                function.interpolate(lambda x:target(x.T).T)
                for facet in range(4):
                    result=local_project_load(V,0,facet,target,4)
                    expected=function.x.array[dofs[result['facet_dofs']]]
                    error=float(np.max(abs(expected-result['coefficients'])))
                    projection_error=max(projection_error,error)
                    if error>256*EPS*max(1.,float(np.max(abs(expected)))):
                        raise RuntimeError('Polynomial normal projection/orientation failed')
                    # Independent direct polynomial target, without projected target in weak load.
                    triangle,normal,h=facet_geometry(V,0,facet)
                    p,w=duffy(triangle,5)
                    values,gradient=cell_basis(V,0,p)
                    dn=np.einsum('pbij,j->pbi',gradient,normal)
                    terms=w[:,None]*np.einsum('pi,pbi->pb',target(p),-dn+96/h*values)
                    exact=np.sum(terms,axis=0)
                    absolute=float(np.sum(abs(terms))+np.sum(result['absolute']))
                    discrepancy=float(np.max(abs(exact-result['load'])))
                    load_error=max(load_error,discrepancy)
                    load_scale=max(load_scale,absolute)
                    if discrepancy>256*EPS*absolute:
                        raise RuntimeError('Polynomial weak load failed')
        records.append(dict(permutation=list(permutation),basis_eval_error=eval_error,
                            projection_error=projection_error,load_error=load_error,
                            load_absolute_scale=load_scale))
        checkpoint(records)
    return records
