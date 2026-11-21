"""Reconcile measured histories and form deterministic, release-relative error envelopes."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.optimize import minimize_scalar

from .axis_ring import CORE, GAMMA, NU, RADIUS, release
from .axis_ring_measure import shape


def change(data, column):
    return 100*(data[column]/data[column][0]-1)


def cumulative(y, t):
    return cumulative_trapezoid(y, t, initial=0)


def budgets(a):
    t = a['t_s']
    result = {}
    for zone in ('box','local'):
        def get(key):
            return a[zone+'_'+key]
        powers = {k:cumulative(get(k),t) for k in ('adv_W','pressure_W','stress_W','diss_W')}
        energy = get('energy_J')-get('energy_J')[0]
        impulse = get('impulse_Ns')-get('impulse_Ns')[0]
        gamma = get('gamma')-get('gamma')[0]
        result[zone] = dict(energy_change_J=energy[-1], energy_terms_J={k:v[-1] for k,v in powers.items()},
                            energy_defect_J_max=max(abs(energy+sum(powers.values()))),
                            impulse_change_Ns=impulse[-1],
                            impulse_out_Ns=cumulative(get('impulse_out_N'),t)[-1],
                            impulse_source_Ns=cumulative(get('impulse_source_N'),t)[-1],
                            impulse_defect_Ns_max=max(abs(impulse+cumulative(
                                get('impulse_out_N')-get('impulse_source_N'),t))),
                            gamma_defect_max=max(abs(gamma+cumulative(get('gamma_out'),t))))
    velocity = [np.gradient(a['ridge_'+axis],t,edge_order=2) for axis in ('r','z')]
    rim_motion = sum(a['rim_move_'+axis]*v for axis,v in zip(('r','z'),velocity))
    flux_change = a['ridge_flux']-a['ridge_flux'][0]
    terms = {k:cumulative(v,t) for k,v in
             [('advection',a['rim_adv_out']),('diffusion',a['rim_visc_out']),('motion',-rim_motion)]}
    result['section'] = dict(change=flux_change[-1], outward_terms={k:v[-1] for k,v in terms.items()},
                             defect_max=max(abs(flux_change+sum(terms.values()))),
                             stokes_over_gamma_max=max(abs(a['rim_loop']-a['ridge_flux']))/GAMMA)
    result['markers'] = []
    for i in range(6):
        w = a[f'm{i}_omega']
        stretch = cumulative(w*a[f'm{i}_stretch'],t)
        visc = cumulative(a[f'm{i}_visc'],t)
        result['markers'].append(dict(change=w[-1]-w[0], stretching=stretch[-1], viscosity=visc[-1],
                                      defect_max=max(abs(w-w[0]-stretch-visc))))
    return result


def analyze(path):
    cases = {}
    for meta in sorted(path.glob('n*.json')):
        status = json.loads(meta.read_text())
        if status['status']!='complete' or status['frames']!=41:
            raise ValueError('Incomplete case: '+meta.stem)
        cases[meta.stem] = np.genfromtxt(meta.with_suffix('.csv'),delimiter=',',names=True)
    fine = cases['n16_L80_s4']
    mid, big = (cases[key] for key in ('n12_L80_s2','n12_L160_s2'))
    paired = [('space',fine,cases['n12_L80_s4']),('step',fine,cases['n16_L80_s2']),
              ('domain',mid,big),('phase',fine,cases['n16_L80_s4_shift'])]
    rows = []
    decision = {}
    for metric in ('minor','major','area','flux'):
        column = 'ridge_'+metric
        nominal = change(fine,column)
        errors = {name:abs(change(a,column)-change(b,column)) for name,a,b in paired}
        errors['interpolation'] = abs(change(fine,'linear_'+metric)-nominal)
        errors['ridge_fit'] = abs(change(fine,'quadratic_'+metric)-nominal)
        errors['center'] = abs(change(fine,'line_'+metric)-nominal)
        errors['aperture'] = np.maximum(*[abs(change(fine,v+'_'+metric)-nominal) for v in ('small','large')])
        fixed = sum(errors[k] for k in errors if k not in ('center','aperture'))
        envelope = fixed+errors['center']+errors['aperture']
        for j,t in enumerate(fine['t_s']):
            rows.append(dict(t_s=t, metric=metric, change_pct=nominal[j], **{k:v[j] for k,v in errors.items()},
                             fixed_envelope_pp=fixed[j], total_envelope_pp=envelope[j],
                             lower_pct=nominal[j]-envelope[j], upper_pct=nominal[j]+envelope[j]))
        decision[metric] = dict(change_pct=nominal[-1], fixed_pp=fixed[-1],total_pp=envelope[-1],
                                last_three_quarter_signal=bool(np.all(envelope[-3:]<abs(nominal[-3:])/4)))
    with (path/'uncertainty.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    t = fine['t_s']
    physical = cases['n16_L80_s4_inviscid']
    attribution = {}
    for k in ('ridge_area','ridge_minor','ridge_major','ridge_flux','ridge_peak','half_radius','m0_omega'):
        attribution[k] = dict(viscous_pct=change(fine,k)[-1],inviscid_pct=change(physical,k)[-1],
                              difference_pp=change(fine,k)[-1]-change(physical,k)[-1])
    # Convolution commutes with pure diffusion; a² -> a²+4νt. Follow its ridge.
    pure = []
    for width in (CORE,np.sqrt(CORE**2+4*NU*t[-1])):
        def w(r,z):
            return r*release(r,z,width)
        center = minimize_scalar(lambda r:-w(r,0.),bounds=(RADIUS-CORE,RADIUS+CORE),
                                 method='bounded',options={'xatol':1e-14}).x
        pure.append(shape(w,np.array([center,0.]),2*CORE))
    gold = json.loads((path.parent/'rotating-disk/isolated_section.json').read_text())[-1]
    release_errors = dict(flux_rel_gamma=(fine['line_flux'][0]-gold['flux_m2_s'])/GAMMA,
                          stokes_rel=(fine['rim_loop'][0]-fine['ridge_flux'][0])/GAMMA,
                          minor_m=fine['line_minor'][0]-gold['minor_mm']/1000,
                          major_m=fine['line_major'][0]-gold['major_mm']/1000)
    speed = np.gradient(fine['ridge_z'],t,edge_order=2)
    center_speed = np.gradient(fine['ridge_centroid_z'],t,edge_order=2)
    with (path/'translation.csv').open('w') as f:
        writer = csv.writer(f,lineterminator='\n')
        writer.writerow(('t_s','ridge_z_m','ridge_speed_m_s','section_centroid_z_m','centroid_speed_m_s',
                         'line_marker_z_m','line_marker_speed_m_s','ridge_length_m','line_marker_length_m'))
        writer.writerows(zip(t,fine['ridge_z'],speed,fine['ridge_centroid_z'],center_speed,
                             fine['m0_z'],fine['m0_uz'],2*np.pi*fine['ridge_r'],2*np.pi*fine['m0_r']))
    fixed_probe_errors = {k: {name: np.max(abs(change(a,k)-change(b,k))) for name,a,b in paired}
                          for k in ('ridge_peak','half_radius')}
    archive = dict(uncertainty=decision, fixed_probe_errors_pp=fixed_probe_errors, matched_inviscid=attribution,
                   diffusion_only_pct={k:100*(pure[1][k]/pure[0][k]-1) for k in ('minor','major','area','flux')},
                   release_section_errors=release_errors, balances={k:budgets(v) for k,v in cases.items()},
                   medium_fine_marker_fractional_rate_max=max(np.max(abs(
                       fine[f'm{i}_Domega']/fine[f'm{i}_omega']-
                       cases['n12_L80_s4'][f'm{i}_Domega']/cases['n12_L80_s4'][f'm{i}_omega'])) for i in range(6)))
    (path/'analysis.json').write_text(json.dumps(archive,indent=2,allow_nan=False)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path)
    analyze(p.parse_args().directory)
