"""Injected assembly and cross-file controls; no numerical library imports."""
from copy import deepcopy
from math import fsum
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from . import manufactured_angular as audit
from .prototype import Refusal
from .test_manufactured_angular import BINDING, sample


class Array(list):
    def tolist(self): return list(self)
    def __neg__(self): return Array(-x for x in self)
    def __setitem__(self, index, values):
        if isinstance(index, list):
            for i, value in zip(index, values): super().__setitem__(i, value)
        elif isinstance(index, slice) and isinstance(values, (int, float)):
            super().__setitem__(index, [values]*len(self[index]))
        else: super().__setitem__(index, values)


class Expr:
    """Scalar expression at a scripted boundary sample, retaining Constants."""
    def __init__(self, fn): self.fn = fn
    def __call__(self, tag): return self.fn(tag)
    def __add__(self, other): return Expr(lambda t: self(t)+evaluate(other, t))
    __radd__ = __add__
    def __neg__(self): return Expr(lambda t: -self(t))
    def __sub__(self, other): return self+-as_expr(other)
    def __rsub__(self, other): return as_expr(other)+-self
    def __mul__(self, other):
        if isinstance(other, Face): return Form([(other.tag, self)], other.degree)
        return Expr(lambda t: self(t)*evaluate(other, t))
    __rmul__ = __mul__


def evaluate(value, tag): return value(tag) if isinstance(value, Expr) else value

def as_expr(value): return value if isinstance(value, Expr) else Expr(lambda t: value)


class Tensor(tuple):
    def __add__(self, other): return Tensor(a+b for a,b in zip(self,other))
    def __neg__(self): return Tensor(-v for v in self)
    def __mul__(self, value): return Tensor(v*value for v in self)
    __rmul__ = __mul__


class Constant(Expr):
    def __init__(self, value):
        self.value=value
        super().__init__(lambda t: self.value)


class Face:
    def __init__(self, tag, degree): self.tag, self.degree=tag,degree


class Form:
    domain = None
    tags = None
    def __init__(self, terms, degree, rank=0, residual=None):
        self.terms,self.degree,self.rank,self.residual=terms,degree,rank,residual
    def __add__(self, other):
        if other == 0: return self
        assert self.degree == other.degree
        return Form(self.terms+other.terms, self.degree)
    __radd__=__add__
    def arguments(self): return tuple(range(self.rank))
    def ufl_domains(self): return (self.domain,)
    def integrals(self):
        tags = [t for t,_ in self.terms] if self.residual is None else ['everywhere',5,6]
        return [NS(integral_type=lambda t=t:'cell' if t=='everywhere' else 'exterior_facet',
                   subdomain_id=lambda t=t:t, subdomain_data=lambda:self.tags) for t in tags]


def fixture():
    item=sample(); phi_data=item['phi']; events=[]
    coords=phi_data['velocity_node_coordinates']
    velocity=NS(dofmap=NS(index_map_bs=3), tabulate_dof_coordinates=lambda:Array(coords))
    pressure=object()
    space=NS(sub=lambda i:NS(collapse=lambda:(velocity if i==0 else pressure,
        phi_data['velocity_parent_map'] if i==0 else phi_data['pressure_parent_map'])))
    domain=NS(); domain.ufl_domain=lambda:domain
    tags=object(); Form.domain=domain; Form.tags=tags
    def function(vspace):
        result=NS(x=NS(array=Array([0.]*(375 if vspace is velocity else 402)),
                         scatter_forward=lambda:events.append('scatter')))
        def interpolate(callback):
            x=Array([Array(c[i] for c in coords) for i in range(3)])
            x.shape=(3,125)
            rows=callback(x)
            result.x.array[:]=[rows[i][j] for j in range(125) for i in range(3)]
        result.interpolate=interpolate
        return result
    w=function(space); w.x.array[:]=item['state'][:402]
    x=Tensor((as_expr(.3),as_expr(.7),as_expr(.4)))
    normals={1:(-1,0,0),2:(1,0,0),3:(0,-1,0),4:(0,1,0),5:(0,0,-1),6:(0,0,1)}
    n=Tensor(Expr(lambda t,i=i:normals[t][i]) for i in range(3))
    u=Tensor(as_expr(v) for v in (2.,3.,4.))
    phi=Tensor((-x[1],x[0],as_expr(0.)))
    grad=Tensor(Tensor(as_expr(v) for v in row) for row in ((1.,2.,3.),(2.,4.,5.),(3.,5.,6.)))
    def dot(a,b):
        if isinstance(a[0],Tensor): return Tensor(dot(row,b) for row in a)
        return sum(v*z for v,z in zip(a,b))
    constants={str(d):[Constant(9.) for _ in range(3)] for d in (24,26)}
    raw_vectors={str(d):list(item['degrees'][str(d)]['raw_residual']) for d in (24,26)}
    action_values={24:7.25,26:-9.5}  # independent of the scripted vector action
    def action(form, mixed):
        assert mixed.x.array.tolist()==phi_data['coefficients']
        events.append(('action',form.degree))
        return Form([],form.degree,residual='action')
    U=NS(Form=Form,split=lambda f:(u,1.2) if f is w else (phi,0.),
         SpatialCoordinate=lambda d:x, FacetNormal=lambda d:n,
         Identity=lambda d:Tensor(Tensor(float(i==j) for j in range(d)) for i in range(d)),
         grad=lambda f:grad,sym=lambda f:f,dot=dot,action=action)
    def compile_form(form):
        assert [c.value for c in constants[str(form.degree)]]==item['state'][402:]
        events.append(('compile',form.degree,form.rank))
        return form
    def scalar(form):
        value=action_values[form.degree] if form.residual=='action' else fsum(
            evaluate(expr,tag)*tag for tag,expr in form.terms)
        events.append(('scalar',form.degree,value)); return value
    def vector(form):
        assert form.rank==1 and form.residual=='raw'
        def ghost(**kw):
            assert kw==dict(addv='ADD',mode='REVERSE')
            events.append(('ghost',form.degree))
        def array(**kw):
            assert kw==dict(readonly=True) and events[-1]==('ghost',form.degree)
            return Array(raw_vectors[str(form.degree)])
        return NS(ghostUpdate=ghost,getArray=array,
                  destroy=lambda:events.append(('destroy',form.degree)))
    modules=dict(ufl=U,fem=NS(Function=function,form=compile_form,assemble_scalar=scalar),
        fem_petsc=NS(assemble_vector=vector),
        np=NS(vstack=lambda rows:rows,zeros=lambda n:Array([0.]*n)),
        PETSc=NS(InsertMode=NS(ADD_VALUES='ADD'),ScatterMode=NS(REVERSE='REVERSE')))
    inputs={}
    for degree in (24,26):
        inputs[str(degree)]=(dict(momentum_continuity=Form([],degree,1,'raw')),
            constants[str(degree)],dict(history=('exact','exact'),force='BE',
                ds=lambda tag,d=degree:Face(tag,d),
                exact=dict(offsets=[Tensor((.2,.4,.6)),Tensor((.8,1.,1.2))])))
    kwargs=dict(modules=modules,domain=domain,space=space,tags=tags,w=w,
        state=item['state'],fixed=dict(zip(item['fixed_indices'],item['fixed_values'])),
        degree_inputs=inputs,raw_by_degree={d:{'angular.'+k:v for k,v in
          e['original'].items() if k!='physical_defect'} for d,e in item['degrees'].items()},
        geometry=item['geometry'],binding=BINDING)
    return kwargs,events,raw_vectors,action_values


class AngularAssemblyChecks(unittest.TestCase):
    def test_actual_helper_routes_faces_raw_vectors_and_final_constants(self):
        kwargs,events,vectors,actions=fixture()
        with patch('builtins.print'): record=audit.assemble_record(**kwargs)
        self.assertEqual(record['phi'],sample()['phi'])
        # Independent arithmetic: angular(u)=-.5; stress from p=1.2, mu=.1.
        # Face integrals have weights equal to tag; both partitions are nonzero.
        expected=dict(A_D=-2.5,A_R=-2.,C_D=-.42,C_R=.12,G_R=1.66)
        for degree in ('24','26'):
            entry=record['degrees'][degree]
            self.assertEqual(entry['raw_residual'],vectors[degree])
            self.assertEqual(entry['multipliers'],[.23,-.37,.19])
            for key,value in expected.items(): self.assertAlmostEqual(entry['scalar'][key],value)
            self.assertEqual(entry['scalar']['residual_action'],actions[int(degree)])
            self.assertFalse(entry['comparisons']['residual_vector_action']['accepted'])
            self.assertIn(('ghost',int(degree)),events)
            self.assertIn(('destroy',int(degree)),events)
        self.assertEqual(len([e for e in events if isinstance(e,tuple) and e[0]=='compile']),14)

    def test_precorrection_state_and_malformed_forms_refuse(self):
        kwargs,_,_,_=fixture(); kwargs['w'].x.array[1]+=1.
        with self.assertRaisesRegex(Refusal,'installed final'): audit.assemble_record(**kwargs)
        kwargs,_,_,_=fixture()
        kwargs['degree_inputs']['24'][0]['momentum_continuity'].rank=0
        with patch('builtins.print'),self.assertRaisesRegex(Refusal,'form rank'):
            audit.assemble_record(**kwargs)

    def test_map_dimensions_and_coordinate_container_refuse(self):
        item=sample()
        # An all-zero tail velocity node can be reassigned to pressure while
        # preserving the old partition/interpolation checks and cached actions.
        bad=deepcopy(item); vm=bad['phi']['velocity_parent_map']; moved=vm[-3:]
        bad['phi']['velocity_parent_map']=vm[:-3]
        bad['phi']['pressure_parent_map']+=moved
        bad['phi']['velocity_node_coordinates'].pop()
        for i in moved: bad['phi']['coefficients'][i]=0.
        for entry in bad['degrees'].values():
            entry['reductions'],entry['comparisons']=audit._reductions(
                bad['phi']['coefficients'],entry['raw_residual'],bad['fixed_indices'],
                entry['scalar'],entry['original'])
        with self.assertRaisesRegex(Refusal,'parent maps'): audit.validate_record(bad,BINDING)
        bad=deepcopy(item); bad['phi']['velocity_node_coordinates']=None
        with self.assertRaisesRegex(Refusal,'parent maps'): audit.validate_record(bad,BINDING)

    def test_numerical_alias_checks_do_not_override_physical_refusal(self):
        item=sample()
        numerical={k:deepcopy(item[k]) for k in ('source_binding','geometry','step','time','dt')}
        numerical.update(fixed_inventory={str(i):v for i,v in zip(item['fixed_indices'],item['fixed_values'])},
            fixed_velocity_dofs=240,multipliers=item['state'][402:404],eta=item['state'][404],
            raw_by_degree={d:{'angular.'+k:v for k,v in e['original'].items()
                if k!='physical_defect'} for d,e in item['degrees'].items()},
            report=dict(numerical_accepted=False))
        self.assertIs(audit.validate_numerical_aliases(item,numerical,BINDING),item)
        self.assertFalse(numerical['report']['numerical_accepted'])
        for mutate in (
            lambda n:n.update(dt=.25),lambda n:n.update(eta=2.),
            lambda n:n['fixed_inventory'].update({'0':1.}),
            lambda n:n['fixed_inventory'].update({next(iter(n['fixed_inventory'])):True}),
            lambda n:n['source_binding'].update(source_commit='c'*40),
            lambda n:n['raw_by_degree']['26'].update({'angular.body':12.})):
            bad=deepcopy(numerical); mutate(bad)
            with self.assertRaises(Refusal): audit.validate_numerical_aliases(item,bad,BINDING)
