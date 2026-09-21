"""Symbolic form grouping only: no physical mesh, quadrature, C/JIT or assembly."""
import ast, json, __future__
from pathlib import Path
from types import SimpleNamespace
import basix.ufl
import ufl
import numpy as np
from ffcx.analysis import analyze_ufl_objects
path=Path('realizability/backends/hdiv_stokes.py')
tree=ast.parse(path.read_text())
selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('_jump','sip_viscosity_form','_mode_ufl')]
namespace={'ufl':ufl}
exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec',
             flags=__future__.annotations.compiler_flag),namespace)
domain=ufl.Mesh(basix.ufl.element('Lagrange','tetrahedron',1,shape=(3,)))
space=ufl.FunctionSpace(domain,basix.ufl.element('BDM','tetrahedron',2))
u,v=ufl.TrialFunction(space),ufl.TestFunction(space)
n,h=ufl.FacetNormal(domain),ufl.CellDiameter(domain)
alpha=ufl.Constant(domain)
# Exact source expression; abstract UFL domain only, no geometry or DOLFINx mesh.
sip=namespace['sip_viscosity_form'](u,v,n,h,1e-6,alpha)
x=ufl.SpatialCoordinate(domain)
mode=SimpleNamespace(m=0,k=0,phase='c',peak_raw_amplitude=1.,is_normal=False)
config=SimpleNamespace(geometry=SimpleNamespace(half_height=.15))
smooth=namespace['_mode_ufl'](mode,config,x)
normal_coefficient=ufl.Coefficient(space)
g=smooth-ufl.dot(smooth,n)*n+ufl.dot(normal_coefficient,n)*n
side=ufl.Measure('ds',domain=domain)(1)
load=1e-6*(-ufl.inner(ufl.outer(g,n),ufl.grad(v))*side + alpha/h*ufl.inner(ufl.outer(g,n),ufl.outer(v,n))*side)
polynomial=ufl.as_vector((1+x[0]+x[1]**2,x[1]+x[2]*x[0],x[2]+x[0]**2))
polynomial_load=1e-6*(-ufl.inner(ufl.outer(polynomial,n),ufl.grad(v))+96/h*ufl.inner(polynomial,v))*ufl.ds
result={'scope':'Symbolic FFCx analysis only; no generated geometry, quadrature points, C, JIT, assembly or solve','forms':{}}
for name,form in [('sip_velocity_block',sip),('P_T00c_boundary_load',load),
                  ('physical_polynomial_load',polynomial_load),
                  ('reaction_verification_velocity_block',sip+ufl.inner(u,v)*ufl.dx)]:
 data=analyze_ufl_objects([form],np.float64)
 groups=[]
 for d in data.form_data[0].integral_data:
  groups.append({'type':d.integral_type,'subdomain':list(d.subdomain_id),'integrands_after_analysis':len(d.integrals),'metadata':[i.metadata() for i in d.integrals]})
 result['forms'][name]={'raw_integrals':len(form.integrals()),'groups':groups}
print(json.dumps(result,indent=2))
