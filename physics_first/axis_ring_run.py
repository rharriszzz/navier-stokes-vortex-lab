"""Run one bounded 20 ms case after release qualification."""
import argparse
import csv
import json
import resource
import time
from pathlib import Path

import numpy as np

from .axis_ring import CORE, GAMMA, NU, RADIUS, Grid, release
from .axis_ring_measure import locate, measure


def memory():
    fields = dict(line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
    return {k: int(fields[k].split()[0]) for k in ('MemAvailable','SwapFree')}


def run(path, n, length, steps, nu, save_fields, shift=False):
    start = time.monotonic()
    initial_mem = memory()
    floor = initial_mem['MemAvailable']//4
    # External timeout also covers setup/factorization and blocked calls.
    cap = min(2560*1024, initial_mem['MemAvailable'] - floor)*1024
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (min(v for v in (soft,hard,cap) if v>0), hard))
    g = Grid(n, length)
    offset = g.h/2 if shift else 0.
    eta = release(g.R,g.Z-offset)
    ridge,_ = locate(g,g.R*eta)
    markers = np.array([[RADIUS,offset], ridge, [RADIUS,offset+CORE/2], [RADIUS,offset-CORE/2],
                        [RADIUS+CORE/2,offset], [RADIUS-CORE/2,offset]])
    prefix = f'n{n}_L{round(length*1000)}_s{steps}' + ('' if nu else '_inviscid')
    if shift:
        prefix += '_shift'
    dt = .0005/steps
    history, snapshots = [], []
    status = 'complete'
    min_available, min_swap = initial_mem.values()
    sample_r = np.linspace(RADIUS-3*CORE,RADIUS+3*CORE,49)
    sample_z = np.linspace(-3*CORE,4*CORE,57)
    rr, zz = np.meshgrid(sample_r,sample_z,indexing='ij')
    with (path/(prefix+'.csv')).open('w') as stream:
        for frame in range(41):
            row, fields = measure(g,eta,markers,nu,frame*.0005)
            if not history:
                writer = csv.DictWriter(stream, fieldnames=list(row), lineterminator='\n')
                writer.writeheader()
            writer.writerow(row)
            stream.flush()
            history.append(row)
            if save_fields:
                snapshots.append([g.interpolate(v)(rr,zz).astype('float32') for v in fields])
            if not np.isfinite(list(row.values())).all():
                status = 'nonfinite measurement'
            if abs(row['rim_loop']-row['ridge_flux'])>.005*GAMMA:
                status = 'section Stokes discrepancy'
            if abs(row['box_impulse_Ns']/history[0]['box_impulse_Ns']-1)>1e-5:
                status = 'global impulse drift'
            if len(history)>1 and nu:
                loss = history[0]['box_energy_J']-row['box_energy_J']
                power = [sum(rec['box_'+key] for key in ('adv_W','pressure_W','stress_W','diss_W'))
                         for rec in history]
                residual = abs(np.trapezoid(power, dx=.0005)-loss)
                if residual > min(.01*history[0]['box_energy_J'],.1*abs(loss)):
                    status = 'global energy discrepancy'
            current = memory()
            min_available = min(min_available,current['MemAvailable'])
            min_swap = min(min_swap,current['SwapFree'])
            if min_available < floor or min_swap < initial_mem['SwapFree'] or time.monotonic()-start>450:
                status = 'resource limit'
            if frame==40 or status!='complete':
                break
            for _ in range(steps):
                eta,markers = g.step(eta,markers,dt,nu)
    if save_fields:
        np.savez_compressed(path/(prefix+'_fields.npz'), r_m=sample_r,z_m=sample_z,
                            t_s=np.array([rec['t_s'] for rec in history]),
                            names=['ur_m_s','uz_m_s','omega_s_inv','stretch_s_inv','visc_s_inv2'],
                            fields=np.array(snapshots))
    record = dict(status=status, frames=len(history), nodes=g.shape, nu=nu, dt_s=dt,
                  elapsed_s=time.monotonic()-start, peak_RSS_KiB=resource.getrusage(0).ru_maxrss,
                  address_limit_bytes=cap, initial_memory_KiB=initial_mem,
                  min_available_KiB=min_available, min_swap_free_KiB=min_swap)
    (path/(prefix+'.json')).write_text(json.dumps(record,indent=2)+'\n')
    print(prefix,record,flush=True)
    return status=='complete'


if __name__=='__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path)
    p.add_argument('n',type=int,choices=(8,12,16))
    p.add_argument('--mm',type=int,choices=(80,160),default=80)
    p.add_argument('--steps',type=int,choices=(2,4,8),default=2,help='steps per 0.5 ms')
    p.add_argument('--inviscid',action='store_true')
    p.add_argument('--shift',action='store_true',help='move the release half an axial grid cell')
    p.add_argument('--fields',action='store_true')
    a = p.parse_args()
    if not json.loads((a.directory/'qualification.json').read_text())['passed']:
        p.error('release qualification failed')
    raise SystemExit(0 if run(a.directory,a.n,a.mm/1000,a.steps,0 if a.inviscid else NU,a.fields,a.shift) else 1)
