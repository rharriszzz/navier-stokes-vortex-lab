"""Lossless endpoint archive and measurement of the R291 wide disk trials."""
import argparse
import io
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np

from .acoustic_initial_state import background
from .cylinder_spreading import INNER, INITIAL
from .disk_pilot import flash
from .disk_step_trial import TRIALS
from .rotating_disk import dual_geometry, mesh
from .su2_acoustic import read_restart, FIELDS


def conservative(data):
    return np.column_stack([data[k] for k in FIELDS[2:]])


def pack(root, dest):
    with ZipFile(dest,'x',compression=ZIP_DEFLATED) as archive:
        for case,(steps,_,_) in TRIALS.items():
            directory=root/case
            base=conservative(read_restart(directory/'state_00000.dat')).view('<u8')
            for name in ('wave.cfg','solver.log','resources.txt','history_00001.csv'):
                archive.write(directory/name,case+'/'+name)
            for j in range(1,steps+1):
                q=conservative(read_restart(directory/f'state_{j:05d}.dat'))
                buf=io.BytesIO()
                np.save(buf,q.view('<u8')^base)
                archive.writestr(f'{case}/{j}.npy',buf.getvalue())


def measure(archive, old_archive):
    xy,cells,wall = mesh(32,True)
    vol,_ = dual_geometry(xy,cells,wall)
    edge = np.roll(xy[cells],-1,axis=1)-xy[cells]
    normal = np.stack((edge[:,:,1],-edge[:,:,0]),axis=2)
    center = xy[cells].mean(axis=1)
    area = .5*np.sum((xy[cells]-center[:,None,:])*normal,axis=(1,2))
    r = np.linalg.norm(xy,axis=1)
    core = (r>0)&(r<=INNER+1e-15)
    radial = xy/np.where(r>0,r,1)[:,None]
    rc = np.linalg.norm(center,axis=1)
    square = np.max(abs(center),axis=1)<.01
    props = background()
    mu = props['mu_Pa_s']
    nu = mu/props['rho_kg_m3']
    ref_power = .0001670970848767434  # R289 no-slip release (W/m)
    w2 = INITIAL.gaussian_width_m**2
    radial_ref = INITIAL.circulation_m2_s/(np.pi*w2)*np.exp(-rc**2/w2)
    strong = radial_ref > .25*radial_ref.max()

    def gradient(uv):
        vertices=uv[cells]
        face=.5*(vertices+np.roll(vertices,-1,axis=1))
        return np.einsum('cei,cej->cij',face,normal)/area[:,None,None]

    def stress(grad):
        strain=.5*(grad+grad.transpose(0,2,1))
        div=strain.trace(axis1=1,axis2=2)
        return 2*mu*(strain-div[:,None,None]*np.eye(2)/3)

    def curl(grad):
        return grad[:,1,0]-grad[:,0,1]

    def rms(a,weight):
        return np.sqrt(np.average(a*a,weights=weight))

    with ZipFile(old_archive) as old:
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            original=Path(temp)/'release.dat'
            original.write_bytes(old.read('r289-wide32/state_00000.dat'))
            state=read_restart(original)
            np.testing.assert_allclose(xy,np.column_stack((state['x'],state['y'])),atol=1e-16,rtol=0)
            q0=conservative(state)
        states={}
        for step in (2,4):
            with np.load(io.BytesIO(old.read(f'wide32/state_{step:05d}.npz'))) as diff:
                q=np.column_stack([(state[k].view('<u8')^diff[k]).view('<f8') for k in FIELDS[2:]])
            states['reference',step*3]=q
    with ZipFile(archive) as trials:
        for case,(steps,_,_) in TRIALS.items():
            for j in range(1,steps+1):
                diff=np.load(io.BytesIO(trials.read(f'{case}/{j}.npy')))
                states[case,12*j//steps]=(q0.view('<u8')^diff).view('<f8')

    p0,_=flash(q0)
    u0=q0[:,1:3]/q0[:,:1]
    grad0=gradient(u0)
    base_omega=curl(grad0)
    initial_ke=np.sum(vol*q0[:,0]*(u0*u0).sum(axis=1)/2)
    results={}
    comparisons={}
    fields={}
    wall_normal=normal[-len(wall):,1,:]
    def traction(p,tau):
        # Wall vertices follow the outer perimeter in cell-edge order.
        wall_p=(p[wall]+np.roll(p[wall],-1))/2
        return np.sum(-(wall_p-wall_p.mean())[:,None]*wall_normal+
                      np.einsum('cij,cj->ci',tau[-len(wall):],wall_normal),axis=0)
    wall_integrals = {}
    release_force = traction(p0,stress(grad0))
    for (case,ns),q in states.items():
        t=ns*1e-9
        p,T=flash(q)
        dp=p-p0
        dq=q-q0
        u=q[:,1:3]/q[:,:1]
        du=(dq[:,1:3]-u0*dq[:,:1])/q[:,:1]
        dg=gradient(du)
        dw=curl(dg)
        w_rate=dw[strong]/(t*base_omega[strong])
        radial_acc=(du*radial).sum(axis=1)/t
        grad=grad0+dg
        tau=stress(grad)
        power=(tau*grad).sum(axis=(1,2))@area
        wall_force=traction(p,tau)
        earlier_ns, earlier_force, impulse = wall_integrals.get(case,(0,release_force,np.zeros(2)))
        dt=(ns-earlier_ns)*1e-9
        # BE uses the end-time wall flux. Explicit reference has only saved
        # output-time tractions, so its tiny net impulse is trapezoidal.
        impulse=impulse+dt*(wall_force if case!='reference' else .5*(wall_force+earlier_force))
        wall_integrals[case]=(ns,wall_force,impulse)
        dk=.5*((u+u0)*dq[:,1:3]).sum(axis=1)-.5*(u*u0).sum(axis=1)*dq[:,0]
        change=vol@dq
        loss=-(vol@dk)
        pressure_rise=np.mean(p[np.isclose(r,INNER,rtol=0,atol=1e-15)])-p[r.argmin()]
        analytic_rate=4*nu/w2*(rc**2/w2-1)
        gamma0=area[square]@base_omega[square]
        gamma_change=area[square]@dw[square]
        ref_gamma_change=t*(area[square]@(radial_ref*analytic_rate)[square])
        # Independently integrate around the four oriented sides of the square.
        loop=0.
        for axis in (0,1):
            for sign in (-1,1):
                side=np.isclose(xy[:,axis],sign*.01,rtol=0,atol=1e-15)&(abs(xy[:,1-axis])<=.01+1e-15)
                order=np.argsort(xy[side,1-axis])
                loop+=sign*(1-2*axis)*np.trapezoid(du[side,1-axis][order],xy[side,1-axis][order])
        key=f'{case}_{ns}ns'
        results[key]=dict(liquid_nodes=len(p),p_min_Pa=p.min(),T_range_K=[T.min(),T.max()],
            inner_pressure_rise_Pa=pressure_rise,core_dp_peak_Pa=np.max(abs(dp[r<=INNER+1e-15])),
            core_dp_rms_Pa=rms(dp[core],vol[core]),radial_acc_rms_m_s2=rms(radial_acc[core],vol[core]),
            core_density_rate_rms=rms(dq[core,0]/t,vol[core]),
            conserved_change_per_m=change.tolist(),wall_force_N_m=wall_force.tolist(),
            integrated_wall_impulse_per_m=impulse.tolist(),
            momentum_defect_per_m=(change[1:3]-impulse).tolist(),
            internal_change_J_m=change[3]+loss,
            mass_drift_fraction=change[0]/(vol@q0[:,0]),kinetic_loss_J_m=loss,
            initial_kinetic_J_m=initial_ke,energy_drift_over_loss=abs(change[3])/loss,
            energy_one_ulp_bound_J_m=vol@np.spacing(q[:,3]),
            dissipation_W_m=power,stress_power_rel_error=power/ref_power-1,
            loss_rate_rel_error=loss/(t*ref_power)-1,gamma_square_m2_s=gamma0+gamma_change,
            gamma_change_m2_s=gamma_change,gamma_loop_change_m2_s=loop,
            gamma_diffusion_change_m2_s=ref_gamma_change,
            gamma_decay_rel_error=gamma_change/ref_gamma_change-1,strong_cells=int(strong.sum()),
            max_strong_fractional_rate_error_s=np.max(abs(w_rate-analytic_rate[strong])))
        fields[case,ns]=(dp[core],radial_acc[core],w_rate)
    for (a,b,ns) in [('full','reference',12),('half','reference',6),('half','reference',12),
                      ('tight','reference',12),('full','half',12),('full','tight',12)]:
        dp,acc,rate=[x-y for x,y in zip(fields[a,ns],fields[b,ns],strict=True)]
        comparisons[f'{a}-{b}_{ns}ns']=dict(core_pressure_max_Pa=np.max(abs(dp)),
            radial_acc_diff_rms_m_s2=rms(acc,vol[core]),max_strong_rate_diff_s=np.max(abs(rate)))
    gates = {}
    for key, result in results.items():
        gates[key] = dict(inner_pressure=bool(result['core_dp_peak_Pa'] <= .05 and
                                              abs(result['inner_pressure_rise_Pa']-15.90531581)<=.05),
                          radial_acceleration=bool(result['radial_acc_rms_m_s2'] < .001),
                          mass=bool(abs(result['mass_drift_fraction'])<1e-11),
                          energy_inventory=bool(abs(result['conserved_change_per_m'][3]) <
                                                .01*result['initial_kinetic_J_m']),
                          energy_loss_scale_raw=bool(result['energy_drift_over_loss']<.10),
                          kinetic_rate=bool(abs(result['loss_rate_rel_error'])<.05),
                          stress_power=bool(abs(result['stress_power_rel_error'])<.05),
                          square_circulation_rate=bool(abs(result['gamma_decay_rel_error'])<.05))
    rate_gates={key:bool(d['max_strong_rate_diff_s']<.02) for key,d in comparisons.items()}
    return dict(endpoints=results,comparisons=comparisons,gates=gates,
                strong_rate_agreement=rate_gates,
                physical_window_passed=all(all(g.values()) for g in gates.values()) and all(rate_gates.values()))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['pack','measure'])
    parser.add_argument('first',type=Path)
    parser.add_argument('second',type=Path)
    parser.add_argument('--require-qualified',action='store_true')
    a=parser.parse_args()
    if a.mode=='pack':
        pack(a.first,a.second)
    else:
        report=measure(a.first,a.second)
        print(json.dumps(report,indent=2,allow_nan=False))
        if a.require_qualified and not report['physical_window_passed']:
            raise SystemExit(1)
