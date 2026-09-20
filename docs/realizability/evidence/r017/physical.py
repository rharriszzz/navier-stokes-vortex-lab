"""R014 one matched-trace attempt; parent monitors all physical work."""
import argparse
import hashlib
import inspect
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
import toy_runner as support
import numpy as np

HERE=Path(__file__).resolve().parent
E5=3.4556100991268897e-6
REFERENCE=complex(2.0662858857221768e-5,-6.595106312048072e-5)
def pair(z): return [float(z.real),float(z.imag)]

def collect_constraints(fem, spaces, bcs, offsets, expected_exterior_dofs, grouping_spaces=None):
    """Collect global essential DOFs using DOLFINx's space-aware BC grouping."""
    groups = fem.bcs_by_block(grouping_spaces if grouping_spaces is not None else spaces, bcs)
    if (len(groups) != len(spaces) or len(offsets) != len(spaces) + 1
            or offsets[0] != 0):
        raise RuntimeError('Constraint block layout mismatch')
    global_sets = []
    local_sets = []
    for index, (space, group) in enumerate(zip(spaces, groups)):
        expected_size = space.dofmap.index_map.size_local * space.dofmap.index_map_bs
        if offsets[index + 1] - offsets[index] != expected_size:
            raise RuntimeError('Constraint block offset mismatch')
        dofs = np.concatenate([bc.dof_indices()[0] for bc in group]) if group else np.empty(0, dtype=np.int32)
        if len(dofs) != len(np.unique(dofs)):
            raise RuntimeError('Duplicate constrained DOFs in a block')
        if len(dofs) and (np.min(dofs) < 0 or np.max(dofs) >= expected_size):
            raise RuntimeError('Constraint DOF outside its block')
        local_sets.append(np.sort(dofs))
        global_sets.append(np.sort(dofs + offsets[index]))
        expected = np.sort(np.asarray(expected_exterior_dofs[index], dtype=np.int32))
        if not np.array_equal(local_sets[-1], expected):
            raise RuntimeError(f'Boundary constraint group {index} does not match exterior DOFs')
    if len(np.concatenate(global_sets)) != len(np.unique(np.concatenate(global_sets))):
        raise RuntimeError('Global constraint blocks overlap')
    return groups, global_sets, local_sets


def raw_vector_layout(vector):
    blocks = vector.getAttr('_blocks')
    owned, ghosts = (None, None) if blocks is None else blocks
    return dict(type=vector.getType(), local_size=vector.getLocalSize(),
                global_size=vector.getSize(), ownership_range=list(vector.getOwnershipRange()),
                owned_offsets=None if owned is None else list(owned),
                ghost_offsets=None if ghosts is None else list(ghosts),
                array_size=len(vector.array))


def vector_layout(vector):
    """Return a block layout, refusing vectors whose metadata was lost."""
    layout = raw_vector_layout(vector)
    if layout['owned_offsets'] is None:
        raise RuntimeError('Block RHS is missing DOLFINx _blocks layout')
    return layout


def make_lifted_rhs(create_vector, apply_lifting, set_bc, PETSc, spaces, forms,
                    reference, loads, grouped_bcs, record, checkpoint):
    """Allocate, validate, populate and lift one disposable block RHS."""
    checkpoint('rhs_allocation')
    rhs = create_vector(spaces, kind=reference.getType())
    try:
        expected = vector_layout(reference)
    except RuntimeError:
        record['rhs_layout'] = dict(reference=raw_vector_layout(reference),
            replacement=raw_vector_layout(rhs),
            block_sizes=[space.dofmap.index_map.size_local * space.dofmap.index_map_bs
                         for space in spaces])
        checkpoint('rhs_layout_validation')
        raise
    actual = vector_layout(rhs)
    record['rhs_layout'] = dict(reference=expected, replacement=actual,
                                block_sizes=[space.dofmap.index_map.size_local *
                                             space.dofmap.index_map_bs for space in spaces])
    checkpoint('rhs_layout_validation')
    keys = ('type', 'local_size', 'global_size', 'ownership_range',
            'owned_offsets', 'ghost_offsets', 'array_size')
    if any(actual[key] != expected[key] for key in keys):
        raise RuntimeError('Replacement RHS block layout differs from captured RHS')
    if len(actual['owned_offsets']) != len(spaces) + 1 or len(loads) != len(spaces):
        raise RuntimeError('Replacement RHS block count mismatch')
    checkpoint('rhs_loading')
    rhs.set(0.0)
    owned = actual['owned_offsets']
    for index, values in enumerate(loads):
        start, end = owned[index], owned[index + 1]
        if end - start != len(values):
            raise RuntimeError(f'RHS block {index} load length differs from owned layout')
        rhs.array[start:end] = values
    checkpoint('rhs_lifting')
    apply_lifting(rhs, forms, bcs=grouped_bcs)
    rhs.ghostUpdate(addv=PETSc.InsertMode.ADD, mode=PETSc.ScatterMode.REVERSE)
    checkpoint('rhs_assignment')
    set_bc(rhs, grouped_bcs)
    return rhs


def record_compatibility(vector, null_vectors, record, checkpoint, key, stage):
    """Persist compatibility diagnostics before a possible refusal."""
    before = vector.copy()
    products = [float(null.dot(before)) for null in null_vectors]
    for null in null_vectors:
        vector.axpy(-null.dot(vector), null)
    removed = before.copy()
    removed.axpy(-1, vector)
    rhs_norm = float(before.norm())
    data = dict(pressure_constant_products_before=products,
                removed_norm=float(removed.norm()), rhs_norm=rhs_norm,
                tolerance=256*np.finfo(float).eps*rhs_norm)
    record[key] = data
    checkpoint(stage)
    if data['removed_norm'] > data['tolerance']:
        raise RuntimeError('Primal pressure compatibility failed before solve')
    return data


def record_returned_solve(record, checkpoint, stage, factor_counts):
    """Checkpoint a solve as soon as its direct helper returns."""
    record['matrix_solves'] = record.get('matrix_solves', 0) + 1
    record['returned_primary_solves'] = record.get('returned_primary_solves', 0) + 1
    record['factor_counts_at_return'] = factor_counts()
    checkpoint(stage)

def identities():
    return {name:support.sha(HERE/name) for name in ('physical.py','toy_runner.py','kernels.py','disk.py')}

def calculate(output):
    sys.path.insert(0,str(Path.cwd()))
    started=time.monotonic()
    record=dict(status='partial',stage='imports',campaign_ready=False,physical_gate_passed=False,
        physical_meshes=0,primary_rhs=0,correction_rhs=0,matrix_solves=0,
        limits=dict(total_wall_seconds=180.,active_child_tree_rss_mib=1536.,nominal_poll_seconds=.05,
                    local_cell_cap=500,dense_free_dof_cap=3000),
        source_sha256=support.verify_sources(),runner_sha256=identities(),
        commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        physical_parameters=dict(R_m=.1,H_m=.15,nu_m2_per_s=1e-6,f_hz=.01,U_m_per_s=1e-7,
            disk_radius_m=.025,mesh_size_m=.05,penalty=96,phasor='exp(i omega t)',terms=128),
        tolerances=dict(flux_ratio=1e-8,arithmetic_epsilon_multiplier=256,
            algebraic_relative_residual=1e-9,divergence_ratio_strict=1e-3,
            boundary_coefficient_residual_strict=1e-14,load_component_per_m=E5/10,
            output_component_per_m=E5/100,magnitude_relative_strict=.05,phase_degrees_strict=5.),
        loads={},outputs={})
    def checkpoint(stage):
        record['stage']=stage
        record['elapsed_child_seconds']=time.monotonic()-started
        record['process_peak_rss_mib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
        support.write_json(output/'report.json',record)
    checkpoint('imports')
    try:
        import numpy as np
        import ufl
        from dataclasses import asdict
        from dolfinx import fem
        from dolfinx.fem.petsc import assign,apply_lifting,create_vector,set_bc
        from petsc4py import PETSc
        import kernels,disk
        from realizability.config import load_config
        from realizability.backends import hdiv_stokes as hdiv,fenicsx_stokes as base,fem_observables as obs
        from realizability.backends.b2_coercivity import calculate_local_bound,_classify
        from realizability.backends.b2_gate import _pde_diagnostics_passed
        from realizability.swirl_reference import normalized_swirl,disk_rotation_gain
        PETSc.Log.begin()
        def factor_counts():
            return {name:int(PETSc.Log.Event(name).getPerfInfo()['count'])
                    for name in ('MatLUFactorSym','MatLUFactorNum','MatSolve')}
        config=load_config(Path('configs/realizability/pilot.json'))
        assert (config.geometry.radius,config.geometry.half_height,config.fluid.kinematic_viscosity,
                config.probe_velocity)==(.1,.15,1e-6,1e-7)
        U=config.probe_velocity
        record['versions']=asdict(base.solver_versions())
        checkpoint('mesh_and_certificate')
        checked=base.create_cylinder(config,.05)
        record['physical_meshes']=1
        domain,_,tags=checked
        V,Q=hdiv.create_hdiv_spaces(domain)
        nv,nq=V.dofmap.index_map.size_global,Q.dofmap.index_map.size_global
        mesh_hash=base._mesh_sha256(domain)
        cells=domain.topology.index_map(3).size_global
        record['mesh']=dict(cells=cells,velocity_dofs=nv,pressure_dofs=nq,mesh_sha256=mesh_hash)
        assert (cells,nv,nq,mesh_hash)==(482,9522,1928,
            '423ab057c5738ae3e2dcef6e82c238ee7e61bc1d0af7f1e212d04b8a2cd6bfb4')
        bound=calculate_local_bound(domain,max_cells=500)
        support.write_json(output/'local_bound.json',bound)
        record['certificate']={k:v for k,v in bound.items() if k!='cell_trace_eigenvalues'}
        record['certificate']['classification']=_classify(bound['C_upper'],96)
        assert abs(bound['C_upper']/58.12657123078638-1)<=1e-10
        assert record['certificate']['classification']['status']=='certified_positive'
        checkpoint('disk_partition')
        regions=disk.prepare(domain,.025,record,checkpoint)
        support.write_json(output/'disk_regions.json',[
            dict(cell=r['cell'],vertices=r['vertices'].tolist(),cut=r['cut'].tolist(),moments=r['moments'])
            for r in regions])
        domain.topology.create_connectivity(2,3)
        domain.topology.create_connectivity(3,2)
        f2c=domain.topology.connectivity(2,3)
        c2f=domain.topology.connectivity(3,2)
        facets=[]
        for facet,tag in zip(tags.indices,tags.values):
            adjacent=f2c.links(facet)
            assert len(adjacent)==1
            cell=int(adjacent[0])
            local=int(np.flatnonzero(c2f.links(cell)==facet)[0])
            facets.append((int(facet),cell,local,int(tag)))
        assert len(facets)==sum(len(f2c.links(f))==1 for f in range(domain.topology.index_map(2).size_local))
        record['boundary_facets']=len(facets)
        checkpoint('physical_polynomial_UFL_validation')
        x=ufl.SpatialCoordinate(domain)
        v=ufl.TestFunction(V)
        n=ufl.FacetNormal(domain)
        h=ufl.CellDiameter(domain)
        expressions=[ufl.as_vector((1+x[0]+x[1]**2,x[1]+x[2]*x[0],x[2]+x[0]**2)),
                     ufl.as_vector((-x[1],x[0],0.))]
        callbacks=[lambda p:np.column_stack((1+p[:,0]+p[:,1]**2,p[:,1]+p[:,2]*p[:,0],p[:,2]+p[:,0]**2)),
                   lambda p:np.column_stack((-p[:,1],p[:,0],np.zeros(len(p))))]
        validations=[]
        for expression,callback in zip(expressions,callbacks):
            assembled=fem.assemble_vector(fem.form(1e-6*(-ufl.inner(ufl.outer(expression,n),ufl.grad(v))
                        +96/h*ufl.inner(expression,v))*ufl.ds))
            manual=np.zeros(nv,dtype=complex)
            absolute=0.
            for facet,cell,local,tag in facets:
                result=kernels.local_project_load(V,cell,local,callback,4,nu=1e-6)
                manual[V.dofmap.cell_dofs(cell)]+=result['load']
                absolute+=float(np.sum(result['absolute']))
            discrepancy=float(np.max(abs(manual-assembled.array)))
            tolerance=256*np.finfo(float).eps*absolute
            validations.append(dict(maximum_coefficient_difference=discrepancy,
                sum_absolute_assembled_contributions=absolute,tolerance=tolerance))
            record['physical_UFL_validation']=validations
            checkpoint('physical_polynomial_UFL_validation')
            if discrepancy>tolerance:
                raise RuntimeError('Physical polynomial UFL/load mismatch')
        reference=disk_rotation_gain(cylinder_radius=.1,half_height=.15,disk_radius=.025,
                                     viscosity=1e-6,frequency_hz=.01,terms=128)
        assert abs(reference-REFERENCE)<=2e-18
        record['reference']=dict(gain_per_m=pair(reference),five_percent_scale_per_m=E5)
        def target(points):
            assert len(points)<=256
            radius=np.linalg.norm(points[:,:2],axis=1)
            swirl=normalized_swirl(radius,points[:,2],cylinder_radius=.1,half_height=.15,
                                    viscosity=1e-6,frequency_hz=.01,terms=128)
            result=np.zeros(points.shape,dtype=complex)
            active=radius!=0
            result[active,0]=-points[active,1]*swirl[active]/radius[active]
            result[active,1]=points[active,0]*swirl[active]/radius[active]
            return result
        loads={}
        for order in (32,64):
            name='A_'+str(order)
            projection=np.zeros(nv,dtype=complex)
            load=np.zeros(nv,dtype=complex)
            signed=[]
            absolute=[]
            facet_records=[]
            maximum=0.
            checkpoint(name+'_boundary_loading')
            for facet,cell,local,tag in facets:
                callback=target if tag==base.SIDE_TAG else lambda p:np.zeros(p.shape,dtype=complex)
                result=kernels.local_project_load(V,cell,local,callback,order,nu=1e-6)
                dofs=V.dofmap.cell_dofs(cell)
                projection[dofs[result['facet_dofs']]]=result['coefficients']
                load[dofs]+=result['load']
                signed.append(result['signed_flux'])
                absolute.append(result['absolute_flux'])
                maximum=max(maximum,result['sampled_speed'])
                facet_records.append(dict(facet=facet,cell=cell,local_facet=local,tag=tag,
                    normal=result['normal'].tolist(),coefficients=[pair(c) for c in result['coefficients']],
                    projection_moments=[pair(c) for c in result['moment']],
                    mass=result['mass'].tolist(),signed_flux_si=pair(U*result['signed_flux']),
                    absolute_flux_si=(U*result['absolute_flux']).tolist()))
                if len(facet_records)%20==0:
                    record['loads'][name]=dict(completed_facets=len(facet_records),status='partial')
                    checkpoint(name+'_boundary_loading')
            total=complex(math.fsum(x.real for x in signed),math.fsum(x.imag for x in signed))
            denom=np.sum(absolute,axis=0)
            ratios=[abs(val)/den if den else 0. if val==0 else None
                    for val,den in zip((total.real,total.imag),denom)]
            support.write_json(output/(name+'_facets.json'),facet_records)
            record['loads'][name]=dict(status='assembled',completed_facets=len(facets),
                signed_flux_si=pair(U*total),absolute_flux_si=(U*denom).tolist(),flux_ratios=ratios,
                sampled_boundary_speed_m_per_s=U*maximum,
                sampled_displacement_scale_m=U*maximum/(2*math.pi*.01),
                sampled_acceleration_scale_m_per_s2=U*maximum*(2*math.pi*.01),
                sampled_maximum_is_global_bound=False,force_power='not assessed',pressure_demand='not assessed')
            checkpoint(name+'_flux_checked')
            if any(r is None or r>=1e-8 for r in ratios):
                raise RuntimeError(name+' prescribed normal closed-flux check failed')
            loads[name]=(projection,load)
        captured={}
        constraint_expectations={}
        original=base._block_direct_solve
        reuses=[]
        def same_mesh(request_config,size):
            assert request_config==config and size==.05 and not reuses
            assert base._mesh_sha256(domain)==mesh_hash
            reuses.append(True)
            return checked
        def capture(*args,**kwargs):
            assert record['primary_rhs']==0
            assert all(space.mesh is domain for space in args[3])
            assert np.array_equal(args[3][0].dofmap.list,V.dofmap.list)
            assert np.array_equal(args[3][2].dofmap.list,V.dofmap.list)
            from dolfinx import mesh as dmesh
            spaces_in, bcs_in = args[3], args[2]
            sizes=[space.dofmap.index_map.size_local*space.dofmap.index_map_bs for space in spaces_in]
            offsets_in=np.cumsum([0,*sizes])
            exterior=dmesh.exterior_facet_indices(domain.topology)
            expected=[np.empty(0,dtype=np.int32) for _ in spaces_in]
            expected[0]=fem.locate_dofs_topological(spaces_in[0],domain.topology.dim-1,exterior)
            expected[2]=fem.locate_dofs_topological(spaces_in[2],domain.topology.dim-1,exterior)
            constraint_expectations['expected']=expected
            record['stage']='P_boundary_constraint_validation'
            checkpoint(record['stage'])
            grouping_spaces=fem.extract_function_spaces(fem.form(args[0]),1)
            grouped,global_sets,local_sets=collect_constraints(
                fem,spaces_in,bcs_in,offsets_in,expected,grouping_spaces)
            record['P_constraint_groups']=[len(group) for group in grouped]
            record['P_constraint_dofs_per_block']=[len(group) for group in local_sets]
            if record['P_constraint_dofs_per_block'] != [len(expected[0]),0,len(expected[2]),0]:
                raise RuntimeError('Unexpected velocity/pressure constraint groups')
            if any(len(expected[index]) == 0 for index in (0,2)):
                raise RuntimeError('Velocity boundary constraint group is empty')
            record['constrained_dofs_by_block']=[group.tolist() for group in global_sets]
            # Observe original helper immediately before nullspace removal. This records
            # P compatibility without changing its assembly, solve, or pressure gauge.
            source_lines,line0=inspect.getsourcelines(original)
            projection_line=line0+next(i for i,s in enumerate(source_lines) if 'nullspace.remove(vector)' in s)
            def trace(frame,event,arg):
                if frame.f_code is original.__code__ and event=='line' and frame.f_lineno==projection_line:
                    local=frame.f_locals
                    copy=local['vector'].copy()
                    record_compatibility(copy,local['null_vectors'],record,checkpoint,
                        'P_pressure_compatibility','P_pressure_compatibility')
                return trace
            record['primary_rhs']+=1
            checkpoint('P_primary_solve')
            sys.settrace(trace)
            try:
                result=support.capture_return(original,captured,*args,**kwargs)
            finally:
                sys.settrace(None)
            record_returned_solve(record,checkpoint,'P_solver_returned',factor_counts)
            return result
        hdiv.create_cylinder=same_mesh
        hdiv._block_direct_solve=capture
        P,physical_fields=hdiv.harmonic_response(config,'T_00c',.01,.05,penalty_factor=96,_return_fields=True)
        record['P_diagnostics']=P.as_dict()
        if not _pde_diagnostics_passed(P):
            raise RuntimeError('P PDE diagnostics failed')
        K,b,x,ksp=(captured[k] for k in ('matrix','vector','solution_vector','solver'))
        spaces=captured['spaces']
        nulls=captured['null_vectors']
        ns=captured['nullspace']
        offsets=captured['offsets']
        bcs=captured['bcs']
        expected=constraint_expectations['expected']
        grouping_spaces=fem.extract_function_spaces(captured['a'],1)
        _,constrained_blocks,local_constraints=collect_constraints(
            fem,spaces,bcs,offsets,expected,grouping_spaces)
        constrained=np.concatenate([constrained_blocks[i] for i in (0,2)])
        def matrix_digest():
            digest=hashlib.sha256()
            for array in K.getValuesCSR(): digest.update(array.tobytes())
            digest.update(np.asarray(offsets).tobytes())
            digest.update(constrained.tobytes())
            return digest.hexdigest()
        original_digest=matrix_digest()
        original_state=K.stateGet()
        factor=ksp.getPC().getFactorMatrix()
        factor_handle=factor.handle
        factor_state=factor.stateGet()
        def counts():
            return factor_counts()
        record['operator']=dict(digest=original_digest,offsets=offsets.tolist(),
            constrained_count=len(constrained),factor_counts=counts())
        def trace_diagnostics(fields,projection,order):
            accum=np.zeros((2,5))
            areas=np.zeros(2)
            for facet,cell,local,tag in facets:
                triangle,normal,_=kernels.facet_geometry(V,cell,local)
                points,weights=kernels.duffy(triangle,order)
                cap=tag==base.CAP_TAG
                areas[int(cap)]+=float(np.sum(weights))
                for start in range(0,len(points),256):
                    p,w=points[start:start+256],weights[start:start+256]
                    ids=np.full(len(p),cell,dtype=np.int32)
                    value=(fields[0].eval(p,ids)+1j*fields[2].eval(p,ids))/U
                    exact=np.zeros(p.shape,dtype=complex) if cap else target(p)
                    basis=kernels.cell_basis(V,cell,p,False)
                    gamma=np.einsum('pbi,b,i->p',basis,projection[V.dofmap.cell_dofs(cell)],normal)
                    tangent=value-exact-((value-exact)@normal)[:,None]*normal
                    normal_error=value@normal-gamma
                    projection_error=exact@normal-gamma
                    for component,part in enumerate((np.real,np.imag)):
                        accum[component,int(cap)]+=np.sum(w*np.sum(part(tangent)**2,axis=1))
                        accum[component,2+int(cap)]+=np.sum(w*part(normal_error)**2)
                        if not cap:accum[component,4]+=np.sum(w*part(projection_error)**2)
            n=ufl.FacetNormal(domain)
            measure=ufl.Measure('dS',domain=domain)
            interior_area=float(fem.assemble_scalar(fem.form(1.*measure)))
            result=[]
            for component,index in enumerate((0,2)):
                jump=ufl.jump(fields[index])
                tangent=jump-ufl.dot(jump,n('+'))*n('+')
                jump_sq=float(fem.assemble_scalar(fem.form(ufl.inner(tangent,tangent)*measure)))
                result.append(dict(target='own full 128-term complex trace; own projected normal',
                    facet_duffy_order=order,side_tangential_relative_l2=math.sqrt(max(0.,accum[component,0]/areas[0])),
                    cap_tangential_relative_l2=math.sqrt(max(0.,accum[component,1]/areas[1])),
                    actual_side_normal_error_relative_l2=math.sqrt(max(0.,accum[component,2]/areas[0])),
                    actual_cap_normal_error_relative_l2=math.sqrt(max(0.,accum[component,3]/areas[1])),
                    target_normal_projection_mismatch_relative_l2=math.sqrt(max(0.,accum[component,4]/areas[0])),
                    interior_tangential_jump_relative_l2=math.sqrt(max(0.,jump_sq/interior_area))/U))
            return result
        def residual(rhs,solution):
            result=rhs.copy()
            K.mult(solution,result)
            result.aypx(-1.,rhs)
            return result
        def pack(vector):
            fields=[fem.Function(s) for s in spaces]
            assign(vector,fields)
            back=vector.duplicate()
            assign(fields,back)
            assert np.array_equal(back.array,vector.array)
            for f in fields:
                f.x.array[:]*=U
                f.x.scatter_forward()
            return tuple(fields)+(tags,)
        def correction(name,rhs,solution):
            before=solution.array[constrained].copy()
            solution.array[constrained]=rhs.array[constrained]
            r=residual(rhs,solution)
            maximum=float(np.max(abs(r.array[constrained])))
            assert maximum==0.
            projected=r.copy()
            dots=[float(n.dot(r)) for n in nulls]
            ns.remove(projected)
            removed=r.copy()
            removed.axpy(-1.,projected)
            dx=solution.duplicate()
            record['correction_rhs']+=1
            ksp.solve(projected,dx)
            record['matrix_solves']+=1
            corrected=solution.copy()
            corrected.axpy(1.,dx)
            equation=residual(projected,dx)
            final=residual(rhs,corrected)
            data=dict(enforced_essential_change=float(np.linalg.norm(before-rhs.array[constrained])),
                constrained_residual_maximum=maximum,primary_relative_residual=float(r.norm()/rhs.norm()),
                correction_pressure_products_before=dots,correction_removed_norm=float(removed.norm()),
                correction_relative_residual=float(equation.norm()/max(projected.norm(),np.finfo(float).tiny)),
                corrected_relative_residual=float(final.norm()/rhs.norm()),reason=ksp.getConvergedReason(),
                factor_counts=counts(),matrix_digest=matrix_digest(),
                same_matrix_state=K.stateGet()==original_state,
                same_factor_handle=ksp.getPC().getFactorMatrix().handle==factor_handle,
                same_factor_state=ksp.getPC().getFactorMatrix().stateGet()==factor_state)
            record['outputs'][name]=dict(algebraic=data)
            checkpoint(name+'_correction')
            if not (data['reason']>0 and max(data[k] for k in ('primary_relative_residual',
                'correction_relative_residual','corrected_relative_residual'))<1e-9
                and all(data[k] for k in ('same_matrix_state','same_factor_handle','same_factor_state'))
                and data['matrix_digest']==original_digest):
                raise RuntimeError(name+' correction/PDE/operator check failed')
            return pack(solution),pack(dx),pack(corrected)
        def outputs(name,packs):
            row=record['outputs'][name]
            for key,fields in zip(('primary','correction','corrected'),packs):
                row[key]=disk.output(fields[0],fields[2],regions,.025,U)
                if not row[key]['arithmetic_passed']:
                    raise RuntimeError(name+' disk arithmetic check failed')
            g,dg,gc=[complex(*row[k]['gain']) for k in ('primary','correction','corrected')]
            scale=sum(row[k]['absolute_contribution_gain'] for k in ('primary','correction','corrected'))
            row['linearity_error_per_m']=abs(gc-g-dg)
            row['linearity_tolerance_per_m']=256*np.finfo(float).eps*scale
            assert row['linearity_error_per_m']<=row['linearity_tolerance_per_m']
            row['correction_component_passed']=abs(dg)<=E5/100
            row['polar']=[]
            for rule in ((18,18,96),(96,96,512)):
                values=obs.extract_complex_linear_features(packs[0],plane_order=rule[0],
                            radial_order=rule[1],angular_order=rule[2])/U
                assert np.isfinite(values).all()
                row['polar'].append(dict(rule=list(rule),gains=[pair(v) for v in values]))
            magnitude_error=abs(abs(g)-abs(reference))/abs(reference)
            phase_error=None if g==0 else abs(float(np.angle(g/reference,deg=True)))
            row['comparison']=dict(absolute_complex_error_per_m=abs(g-reference),
                relative_complex_error=abs(g-reference)/abs(reference),relative_magnitude_error=magnitude_error,
                wrapped_phase_error_deg=phase_error,magnitude_passed=magnitude_error<.05,
                phase_passed=phase_error is not None and phase_error<5.)
            checkpoint(name+'_outputs')
        packs=correction('P',b,x)
        outputs('P',packs)
        import re
        previous=json.loads(re.search(r'^## Complete calculation report\n\n```json\n(.*?)^```',
            Path('docs/realizability/B2_PHYSICAL_RESPONSE_EVIDENCE.md').read_text(),re.M|re.S).group(1))
        prior_rows=[previous['quadrature'][1],previous['quadrature'][-1]]
        for row,old in zip(record['outputs']['P']['polar'],prior_rows):
            assert abs(complex(*row['gains'][1])-complex(*old['features_gain'][1]))<=2.4719806123e-13
        record['P_polar_reproduction_passed']=True
        for name,(projection,load) in loads.items():
            normal_real,normal_imag=fem.Function(spaces[0]),fem.Function(spaces[2])
            normal_real.x.array[:]=projection.real
            normal_imag.x.array[:]=projection.imag
            zero_real,zero_imag=fem.Function(spaces[0]),fem.Function(spaces[2])
            real_bcs,_,_=base._velocity_boundary_conditions(spaces[0],tags,normal_real,zero_real)
            imag_bcs,_,_=base._velocity_boundary_conditions(spaces[2],tags,normal_imag,zero_imag)
            new_bcs=real_bcs+imag_bcs
            record['stage']=name+'_constraint_collection'
            checkpoint(record['stage'])
            new_grouped,new_constraint_blocks,new_local_constraints=collect_constraints(
                fem,spaces,new_bcs,offsets,expected,grouping_spaces)
            new_constrained=np.concatenate([new_constraint_blocks[i] for i in (0,2)])
            assert np.array_equal(np.sort(new_constrained),np.sort(constrained))
            block_loads=[load.real,np.zeros(offsets[2]-offsets[1]),
                         load.imag,np.zeros(offsets[4]-offsets[3])]
            rhs=make_lifted_rhs(create_vector,apply_lifting,set_bc,PETSc,spaces,
                                captured['a'],b,block_loads,new_grouped,record,checkpoint)
            record['stage']=name+'_primary_rhs_compatibility'
            checkpoint(record['stage'])
            record_compatibility(rhs,nulls,record['loads'][name],checkpoint,
                                'pressure_compatibility',record['stage'])
            solution=x.duplicate()
            record['primary_rhs']+=1
            checkpoint(name+'_primary_solve')
            ksp.solve(rhs,solution)
            record_returned_solve(record,checkpoint,name+'_solver_returned',factor_counts)
            packs=correction(name,rhs,solution)
            # Exact essential-normal coefficient and volume diagnostics use this fixture's own targets.
            diagnostics=[]
            for index,normal in ((0,normal_real),(2,normal_imag)):
                norm,pnorm,div=base._field_norms(packs[0][index],packs[0][index+1])
                target_coeff=normal.x.array*U
                dofs=np.concatenate([bc.dof_indices()[0] for bc in new_grouped[index]])
                essential=float(np.max(abs(packs[0][index].x.array[dofs]-target_coeff[dofs])))
                diagnostics.append(dict(velocity_l2=norm,pressure_l2=pnorm,divergence_l2=div,
                    divergence_ratio=.1*div/max(norm,np.finfo(float).tiny),boundary_dof_residual=essential,
                    target='own real/imaginary L2-projected full trace'))
            record['outputs'][name]['PDE']=diagnostics
            if any(d['divergence_ratio']>=1e-3 or d['boundary_dof_residual']>=1e-14 for d in diagnostics):
                raise RuntimeError(name+' divergence/essential-normal check failed')
            record['outputs'][name]['boundary_traces']=trace_diagnostics(packs[0],projection,int(name[2:]))
            outputs(name,packs)
        gp=complex(*record['outputs']['P']['primary']['gain'])
        for name in ('A_32','A_64'):
            ga=complex(*record['outputs'][name]['primary']['gain'])
            E,D=ga-reference,gp-ga
            tolerance=256*np.finfo(float).eps*(abs(gp)+abs(ga)+abs(reference)+abs(E)+abs(D))
            error=abs(gp-reference-(D+E))
            record['outputs'][name]['identity']=dict(E_Ah=pair(E),D_h=pair(D),sum=pair(E+D),
                arithmetic_error=error,tolerance=tolerance)
            assert error<=tolerance
        load_step=abs(complex(*record['outputs']['A_64']['primary']['gain'])-
                      complex(*record['outputs']['A_32']['primary']['gain']))
        record['load_step']=dict(absolute_gain_per_m=load_step,component_passed=load_step<=E5/10)
        assert counts()=={'MatLUFactorSym':1,'MatLUFactorNum':1,'MatSolve':6}
        assert record['primary_rhs']==record['correction_rhs']==3 and record['matrix_solves']==6
        support.verify_sources()
        record['status']='complete'
        checkpoint('complete')
    except Exception as error:
        record['status']='partial_failed'
        record['error']=dict(type=type(error).__name__,message=str(error))
        checkpoint(record['stage'])
        raise

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--child',action='store_true')
    parser.add_argument('--extra-toys',action='store_true')
    args=parser.parse_args()
    if args.child:
        calculate(args.output)
    elif args.extra_toys:
        import disk
        support.write_json(args.output/'extra-toys.json',dict(status='passed',checks=disk.toys(),
            disk_sha256=support.sha(HERE/'disk.py'),
            process_peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024))
    else:
        args.output.mkdir(parents=True,exist_ok=False)
        for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
        support.verify_sources()
        previous=support.read_json(HERE/'attempt/toy-report.json')
        assert previous['status']=='passed' and previous['kernels_sha256']==support.sha(HERE/'kernels.py')
        first_watch=support.read_json(HERE/'attempt/toy-watch.json')
        assert support.sha(HERE/'toy_runner.py')==previous['runner_sha256']
        remaining=60-first_watch['elapsed_seconds']
        extra=support.monitor([sys.executable,str(Path(__file__)),'--extra-toys','--output',str(args.output)],
                              time.monotonic()+remaining,512.,args.output/'extra-toys')
        support.write_json(args.output/'extra-toys-watch.json',extra)
        if extra['stop_reason'] or extra['returncode']!=0:
            support.write_json(args.output/'report.json',dict(status='partial_failed',stage='extra_toys',
                physical_meshes=0,primary_rhs=0,correction_rhs=0,matrix_solves=0,campaign_ready=False,
                physical_gate_passed=False,parent_stop=extra))
        else:
            watch=support.monitor([sys.executable,str(Path(__file__)),'--child','--output',str(args.output)],
                                  time.monotonic()+180.,1536.,args.output/'physical')
            support.write_json(args.output/'watch.json',watch)
            path=args.output/'report.json'
            report=support.read_json(path) if path.exists() else dict(status='partial_no_child_report')
            if watch['stop_reason'] or watch['returncode']!=0:
                report['parent_stop']=watch
                if watch['stop_reason']:report['status']='partial_resource_or_process_stop'
                support.write_json(path,report)
        support.write_json(args.output/'manifest.json',{str(p.relative_to(args.output)):support.sha(p)
            for p in sorted(args.output.rglob('*')) if p.is_file() and p.name!='manifest.json'})
        result=support.read_json(args.output/'report.json')
        print(json.dumps(dict(status=result['status'],stage=result.get('stage'),
                             counts={k:result.get(k) for k in ('physical_meshes','primary_rhs','correction_rhs','matrix_solves')}),indent=2))
