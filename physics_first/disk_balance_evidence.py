"""Lossless measured fields and endpoint diagnostics for the projected 12 ns disk."""
import argparse
import csv
import io
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np

from .disk_mass_balance import eos_rates, mass_matrix, regions, rms
from .disk_spatial_probe import FINAL_STEPS
from .disk_step_evidence import conservative, measure_states
from .disk_step_trial import TRIALS
from .rotating_disk import dual_geometry, mesh, INITIAL
from .su2_acoustic import read_restart, FIELDS


def save_array(archive, name, data):
    buf = io.BytesIO()
    np.save(buf, np.ascontiguousarray(data.T), allow_pickle=False)
    archive.writestr(name, buf.getvalue())


def pack(root, dest):
    with ZipFile(dest, 'x', compression=ZIP_DEFLATED) as z:
        base = conservative(read_restart(root/'release/state_00000.dat')).view('<u8')
        for run in ('release', 'centered', *FINAL_STEPS, *('spatial_'+k for k in ('release', *FINAL_STEPS))):
            directory = root/run
            for name in ('wave.cfg', 'solver.log', 'resources.txt'):
                z.write(directory/name, run+'/'+name)
            for hist in directory.glob('history*.csv'):
                z.write(hist, run+'/'+hist.name)
            if run in ('release', 'centered'):
                z.write(directory/'state_00001.dat', run+'/state_00001.dat')
            if run == 'release':
                z.write(directory/'state_00000.dat', run+'/state_00000.dat')
                z.write(directory/'initial.json', run+'/initial.json')
            if run.startswith('spatial_'):
                data = read_restart(directory/'sampled.dat')
                residuals = np.column_stack([data['Residual_'+k] for k in FIELDS[2:]])
                save_array(z, run+'/residual.npy', residuals)
                save_array(z, run+'/pressure.npy', data['Pressure'])
            if run in FINAL_STEPS:
                np.testing.assert_array_equal(conservative(read_restart(directory/'state_00000.dat')).view('<u8'), base)
                for path in sorted(directory.glob('state_*.dat'))[1:]:
                    q = conservative(read_restart(path)).view('<u8')
                    save_array(z, run+'/'+path.stem+'.npy', q^base)
        z.write(root/'projection.resources', 'projection.resources')


def curl_integral(field, cells, edge):
    vertices = field[cells]
    return (.5*(np.roll(vertices, -1, axis=1)+vertices)*edge).sum(axis=(1, 2))


def rate_budget(q0, states, residuals, pressures, xy, vol, cells):
    """Signed decomposition at the worst full-step cell, using the same release curl."""
    vertices = xy[cells]
    edge = np.roll(vertices, -1, axis=1)-vertices
    center = vertices.mean(axis=1)
    profile = np.exp(-(center**2).sum(axis=1)/INITIAL.gaussian_width_m**2)
    strong = profile>.25*profile.max()
    u0 = q0[:, 1:3]/q0[:, :1]
    circulation = curl_integral(u0, cells[strong], edge[strong])
    def fractional(field):
        return curl_integral(field, cells[strong], edge[strong])/circulation
    measured, spatial = {}, {}
    for case in ('full', 'reference'):
        q = states[case, 12]
        dq = q-q0
        measured[case] = fractional((dq[:, 1:3]-u0*dq[:, :1])/(q[:, :1]*12e-9))
        rate = -residuals[case]/vol[:, None]
        # Using release velocity here makes the finite-difference BE identity exact.
        spatial[case] = fractional((rate[:, 1:3]-u0*rate[:, :1])/q[:, :1])
    diff = measured['full']-measured['reference']
    index = np.argmax(abs(diff))
    parts = dict(measured_difference=diff, be_endpoint_defect=measured['full']-spatial['full'],
                 difference_of_endpoint_operators=spatial['full']-spatial['reference'],
                 reference_endpoint_minus_average=spatial['reference']-measured['reference'])
    # In the interior, the arithmetic-mean pressure gradient is minus the
    # transpose of the unit-density divergence (dual normals close). Only
    # interior nodes enter the strong-cell loops. Constant pressure cancels.
    divergence = mass_matrix(xy, cells, np.ones(len(xy)))
    full, ref = states['full', 12], states['reference', 12]
    dp = pressures['full']-pressures['reference']
    dp_linear, _ = eos_rates(ref, full-ref)
    def pressure_response(delta):
        accel = (divergence.T@delta).reshape(-1, 2)/(vol*full[:, 0])[:, None]
        return fractional(accel)
    pressure = pressure_response(dp)
    linear = pressure_response(dp_linear)
    core = regions(xy)['core']
    operator_difference = parts['difference_of_endpoint_operators']
    pressure_audit = dict(
        solver_dp_rms_Pa=rms(dp[core], vol[core]), linear_heos_dp_rms_Pa=rms(dp_linear[core], vol[core]),
        dp_minus_linear_rms_Pa=rms((dp-dp_linear)[core], vol[core]),
        pressure_curl_at_peak_s=pressure[index], linear_heos_curl_at_peak_s=linear[index],
        max_operator_minus_pressure_s=max(abs(operator_difference-pressure)),
        max_pressure_minus_linear_s=max(abs(pressure-linear)),
        max_linear_heos_pressure_curl_s=max(abs(linear)))
    return dict(peak_xy_m=center[strong][index].tolist(), pressure_audit=pressure_audit,
                at_peak_s={key:value[index] for key,value in parts.items()},
                max_abs_s={key:max(abs(value)) for key,value in parts.items()})


def spatial_metrics(q, residual, previous, dt, xy, vol, cells):
    rates = -residual/vol[:, None]
    core = regions(xy)['core']
    rho = q[:, 0]
    u = q[:, 1:3]/rho[:, None]
    radius = np.linalg.norm(xy, axis=1)
    radial = xy/np.where(radius>0, radius, 1)[:, None]
    tangent = np.column_stack((-radial[:, 1], radial[:, 0]))
    acc = (rates[:, 1:3]-u*rates[:, :1])/rho[:, None]
    def norm(v):
        return rms(v[core], vol[core])
    result = dict(core_density_rate_rms=norm(rates[:, 0]),
                  core_momentum_rate_rms=[norm(rates[:, i]) for i in (1, 2)],
                  core_radial_acc_rms_m_s2=norm((acc*radial).sum(axis=1)),
                  core_tangential_acc_rms_m_s2=norm((acc*tangent).sum(axis=1)),
                  signed_conservative_rates=(-residual.sum(axis=0)).tolist())
    if previous is not None:
        # The conservative BE root requires dQ/dt = L(Q_end). This diagnostic
        # uses the stored doubles, including their temporal-density precision floor.
        defect = (q-previous)/dt-rates
        u_previous = previous[:, 1:3]/previous[:, :1]
        a_defect = (defect[:, 1:3]-u_previous*defect[:, :1])/rho[:, None]
        result['be_core_defect_rms'] = [norm(v) for v in defect.T]
        result['be_radial_defect_rms_m_s2'] = norm((a_defect*radial).sum(axis=1))
        result['be_core_momentum_rate_resolution_rms'] = [
            norm((abs(np.spacing(q[:, i]))+abs(np.spacing(previous[:, i])))/(2*dt)) for i in (1, 2)]
        v = xy[cells]
        edge = np.roll(v, -1, axis=1)-v
        center = v.mean(axis=1)
        omega_ref = np.exp(-(center**2).sum(axis=1)/INITIAL.gaussian_width_m**2)
        strong = omega_ref>.25*omega_ref.max()
        curl_defect = curl_integral(a_defect, cells[strong], edge[strong])
        circulation = curl_integral(u, cells[strong], edge[strong])
        result['be_max_strong_fractional_curl_defect_s'] = max(abs(curl_defect/circulation))
    return result


def measure(archive):
    import tempfile
    xy, cells, wall = mesh(32, True)
    vol, _ = dual_geometry(xy, cells, wall)
    states, algebraic, spatial, residuals = {}, {}, {}, {}
    pressures = {}
    with ZipFile(archive) as z, tempfile.TemporaryDirectory() as tmp:
        file = Path(tmp)/'initial.dat'
        file.write_bytes(z.read('release/state_00000.dat'))
        q0 = conservative(read_restart(file))
        for case, end in FINAL_STEPS.items():
            steps = (end//2, end) if end>1 else (end,)
            for step in steps:
                delta = np.load(io.BytesIO(z.read(f'{case}/state_{step:05d}.npy'))).T
                states[case, 12*step//end] = np.ascontiguousarray((q0.view('<u8')^delta).view('<f8'))
            if case in TRIALS:
                rows = list(csv.reader(io.StringIO(z.read(case+'/history_00001.csv').decode()), skipinitialspace=True))
                for step in range(1, end+1):
                    iterations = [r for r in rows[1:] if int(r[0])==step]
                    logs = list(map(float, iterations[-1][-4:]))
                    algebraic[f'{case}_{12*step//end}ns'] = dict(iterations=len(iterations), final_log10_rms=logs,
                        passed=max(logs)<TRIALS[case][1])
        for case in ('release', *FINAL_STEPS):
            residual = np.load(io.BytesIO(z.read(f'spatial_{case}/residual.npy'))).T
            pressures[case] = np.load(io.BytesIO(z.read(f'spatial_{case}/pressure.npy')))
            residuals[case] = residual
            q = q0 if case=='release' else states[case, 12]
            previous, dt = None, None
            if case in TRIALS:
                previous = states['half', 6] if case=='half' else q0
                dt = 12e-9/FINAL_STEPS[case]
            spatial[case] = spatial_metrics(q, residual, previous, dt, xy, vol, cells)
    evidence = measure_states(q0, states)
    evidence.update(algebraic=algebraic, spatial=spatial, mass_one_ulp_kg_m=vol@np.spacing(q0[:, 0]),
                    full_step_rate_budget=rate_budget(q0, states, residuals, pressures, xy, vol, cells))
    evidence['qualified'] = evidence['physical_window_passed'] and all(v['passed'] for v in algebraic.values())
    return evidence


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest='mode', required=True)
    write = commands.add_parser('pack')
    write.add_argument('root', type=Path)
    write.add_argument('archive', type=Path)
    read = commands.add_parser('measure')
    read.add_argument('archive', type=Path)
    read.add_argument('--require-qualified', action='store_true')
    a = p.parse_args()
    if a.mode == 'pack':
        pack(a.root, a.archive)
    else:
        result = measure(a.archive)
        print(json.dumps(result, indent=2, allow_nan=False))
        if a.require_qualified and not result['qualified']:
            raise SystemExit(1)
