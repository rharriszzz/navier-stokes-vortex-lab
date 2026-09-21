"""R014 cell-plane partition and quadratic reconstruction. Disposable only."""
import itertools
import math
import numpy as np
from kernels import (EPS, MOMENTS, MONOMIALS3, polynomial_values,
                     circle_polygon_moments, cross2)

REF=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
STENCIL=np.array([*REF,*[(a+b)/2 for a,b in itertools.combinations(REF,2)]])
INVERSE=np.linalg.inv(polynomial_values(STENCIL,MONOMIALS3))
CHECK=np.array([[.17,.21,.23],[.08,.11,.31],[.29,.13,.27]])

def multiply(p,q):
    result={}
    for (a,b),v in p.items():
        for (c,d),w in q.items():
            result[a+c,b+d]=result.get((a+c,b+d),0.)+v*w
    return result

def restriction(vertices,d):
    """Coefficients in X,Y for each local quadratic monomial, x=dX,y=dY,z=0."""
    invJ=np.linalg.inv((vertices[1:]-vertices[0]).T)
    origin=-invJ@vertices[0]
    linear=[{(0,0):origin[j],(1,0):d*invJ[j,0],(0,1):d*invJ[j,1]} for j in range(3)]
    result=[]
    for powers in MONOMIALS3:
        poly={(0,0):1.}
        for j,power in enumerate(powers):
            for _ in range(power):
                poly=multiply(poly,linear[j])
        result.append(poly)
    return result

def plane_cut(vertices):
    """Exact sign classifications; retain all nonzero cuts, with no snapping."""
    points={tuple(p[:2]) for p in vertices if p[2]==0}
    for a,b in itertools.combinations(vertices,2):
        if a[2]*b[2]<0:
            p=(a[2]*b-b[2]*a)/(a[2]-b[2])
            points.add(tuple(p[:2]))
    if len(points)<3:
        return np.empty((0,2))
    points=np.array(sorted(points))
    center=np.mean(points,axis=0)
    points=points[np.argsort(np.arctan2(points[:,1]-center[1],points[:,0]-center[0]))]
    area2=math.fsum(cross2(a,b) for a,b in zip(points,np.roll(points,-1,axis=0)))
    if area2<=0:
        raise RuntimeError('Unresolved plane-cut orientation')
    return points

def prepare(domain,d,record,checkpoint):
    import basix
    domain.topology.create_connectivity(2,3)
    domain.topology.create_connectivity(3,2)
    f2c=domain.topology.connectivity(2,3)
    c2f=domain.topology.connectivity(3,2)
    # Reject ambiguous positive-area interior facets before any field evaluation.
    faces=basix.topology(basix.CellType.tetrahedron)[2]
    coincident=[]
    for cell in range(domain.topology.index_map(3).size_local):
        vertices=domain.geometry.x[domain.geometry.dofmap[cell],:3]
        for j,ids in enumerate(faces):
            facet=int(c2f.links(cell)[j])
            if len(f2c.links(facet))==2 and np.all(vertices[ids,2]==0):
                poly=plane_cut(vertices[ids])
                moments=circle_polygon_moments(poly/d)
                if moments['moments'][0]>0:
                    coincident.append(dict(cell=cell,facet=facet,vertices=vertices[ids].tolist(),
                                           area_m2=moments['moments'][0]*d*d))
    record['coincident_interior_facets']=coincident
    checkpoint('disk_partition')
    if coincident:
        raise RuntimeError('Positive-area coincident interior facet intersects disk')
    regions=[]
    keys=set()
    for cell in range(domain.topology.index_map(3).size_local):
        vertices=domain.geometry.x[domain.geometry.dofmap[cell],:3]
        cut=plane_cut(vertices)
        if len(cut)<3:
            continue
        result=circle_polygon_moments(cut/d)
        area=result['moments'][0]
        if area<0:
            raise RuntimeError('Negative disk-cut area')
        # Exact zero only: no positive area is discarded.
        if area==0:
            continue
        key=tuple(sorted(map(tuple,cut)))
        if key in keys:
            raise RuntimeError('Duplicate plane region')
        keys.add(key)
        regions.append(dict(cell=cell,vertices=vertices,cut=cut,moments=result,
                            restriction=restriction(vertices,d)))
    totals=[math.fsum(r['moments']['moments'][i] for r in regions) for i in range(10)]
    expected=[math.pi if (a,b)==(0,0) else math.pi/4 if (a,b) in ((2,0),(0,2)) else 0.
              for a,b in MOMENTS]
    scales=[math.fsum(r['moments']['absolute_boundary_contributions'][i] for r in regions)
            for i in range(10)]
    errors=np.abs(np.array(totals)-expected)
    tolerances=256*EPS*np.array(scales)
    record['disk_partition']=dict(visited_cells=int(domain.topology.index_map(3).size_local),
        positive_area_regions=len(regions),cell_ids=[r['cell'] for r in regions],
        dimensionless_moments=totals,expected_moments=expected,errors=errors.tolist(),
        arithmetic_tolerances=tolerances.tolist(),area_m2=totals[0]*d*d,
        denominator_m4=(totals[MOMENTS.index((2,0))]+totals[MOMENTS.index((0,2))])*d**4,
        exact_denominator_m4=math.pi*d**4/2)
    checkpoint('disk_partition_checked')
    if np.any(errors>tolerances):
        raise RuntimeError('Disk partition moment/coverage check failed')
    return regions

def output(real,imag,regions,d,U):
    """Physical fields -> complex gain, exact polynomial cut-cell integration."""
    terms=[[],[],[]]
    absolute=[]
    reconstruction=[]
    for region in regions:
        cell,vertices=region['cell'],region['vertices']
        J=(vertices[1:]-vertices[0]).T
        points=vertices[0]+STENCIL@J.T
        ids=np.full(len(points),cell,dtype=np.int32)
        values=(real.eval(points,ids)+1j*imag.eval(points,ids))/U
        coefficients=INVERSE@values
        points_check=vertices[0]+CHECK@J.T
        ids_check=np.full(len(CHECK),cell,dtype=np.int32)
        exact=(real.eval(points_check,ids_check)+1j*imag.eval(points_check,ids_check))/U
        fit=polynomial_values(CHECK,MONOMIALS3)@coefficients
        error=float(np.max(abs(exact-fit)))
        scale=float(np.max(np.abs(polynomial_values(CHECK,MONOMIALS3))@np.abs(coefficients)))
        reconstruction.append(dict(cell=cell,error=error,tolerance=256*EPS*scale))
        if error>256*EPS*scale:
            raise RuntimeError('Cell polynomial reconstruction failed')
        # Keep each local-polynomial substitution contribution separate in A_out.
        for coeff,poly in zip(coefficients,region['restriction']):
            for (a,b),weight in poly.items():
                for index,c in ((MOMENTS.index((a+1,b)),d*weight*coeff[1]),
                                (MOMENTS.index((a,b+1)),-d*weight*coeff[0])):
                    for k,rule in enumerate(('moments','gauss16','gauss32')):
                        terms[k].append(c*region['moments'][rule][index]*d*d)
                    absolute.append(abs(c*region['moments']['moments'][index]*d*d))
    denominator=math.pi*d**4/2
    numerators=[complex(math.fsum(t.real for t in row),math.fsum(t.imag for t in row))
                for row in terms]
    gains=[x/denominator for x in numerators]
    A=math.fsum(absolute)/denominator
    tolerance=256*EPS*A
    independent=max(abs(g-gains[0]) for g in gains[1:])
    return dict(gain=[gains[0].real,gains[0].imag],numerator=[numerators[0].real,numerators[0].imag],
        denominator_m4=denominator,absolute_contribution_gain=A,
        arithmetic_tolerance_per_m=tolerance,independent_difference_per_m=independent,
        reconstruction=reconstruction,coordinate_scale_m=d,field_scale=U,
        arithmetic_passed=bool(independent<=tolerance),
        component_screen_passed=bool(max(tolerance,independent)<=3.4556100991268895e-8))

def toys():
    # Full tetrahedral stencil, including a non-axis-aligned affine map.
    vertices=np.array([[.2,-.1,-.3],[1.1,.2,.4],[-.2,1.3,.2],[.1,.3,1.1]])
    polys=restriction(vertices,.25)
    points=np.array([[-.3,.1],[.2,.7],[-.1,-.4]])
    invJ=np.linalg.inv((vertices[1:]-vertices[0]).T)
    ref=(np.column_stack((.25*points,np.zeros(len(points))))-vertices[0])@invJ.T
    expected=polynomial_values(ref,MONOMIALS3)
    actual=np.array([[sum(v*p[0]**a*p[1]**b for (a,b),v in poly.items()) for poly in polys]
                     for p in points])
    error=float(np.max(abs(expected-actual)))
    assert error<=256*EPS*max(1.,float(np.max(abs(expected))))
    interpolation_error=float(np.max(abs(INVERSE@polynomial_values(STENCIL,MONOMIALS3)-np.eye(10))))
    assert interpolation_error<=256*EPS
    cut=plane_cut(np.array([[0.,0.,-1.],[1.,0.,1.],[0.,1.,1.],[0.,0.,1.]]))
    area=math.fsum(cross2(a,b) for a,b in zip(cut,np.roll(cut,-1,axis=0)))/2
    assert area==.125
    tangent=plane_cut(np.array([[0.,0.,0.],[1.,0.,1.],[0.,1.,1.],[0.,0.,1.]]))
    assert len(tangent)==0
    return dict(restriction_error=error,stencil_inverse_error=interpolation_error,
                cut_area=area,vertex_contact_empty=True)
