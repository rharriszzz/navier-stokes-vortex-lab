"""Difference actual SU2 face kernels in dimensional conservative variables."""
import argparse
import ctypes
import json
import shlex
import subprocess
import tempfile
from pathlib import Path

import CoolProp.CoolProp as CP
import numpy as np

from .su2_acoustic import FIELDS, read_restart


def audit(source, restart):
    build = source/'build-water'
    command = next(entry['command'] for entry in json.loads((build/'compile_commands.json').read_text())
                   if entry['file'].endswith('/CNumericsSIMD.cpp'))
    flags = shlex.split(command)
    eos = CP.AbstractState('HEOS', 'Water')
    state = read_restart(restart)
    index = np.argmin((state['x']-.00625)**2+(state['y']-.00625)**2)
    q = np.array([state[k][index] for k in FIELDS[2:]])

    def primitive(u):
        rho, mx, my, energy = u
        vx, vy = mx/rho, my/rho
        eos.update(CP.DmassUmass_INPUTS, rho, energy/rho-(vx*vx+vy*vy)/2)
        if eos.phase() != CP.iphase_liquid:
            raise ValueError('Non-liquid test state')
        return np.array([eos.T(), vx, vy, eos.p(), rho, (energy+eos.p())/rho, eos.speed_sound(),
                         eos.first_partial_deriv(CP.iP, CP.iDmass, CP.iUmass),
                         eos.first_partial_deriv(CP.iP, CP.iUmass, CP.iDmass)])

    with tempfile.TemporaryDirectory() as tmp:
        convection = source/'SU2_CFD/include/numerics_simd/flow/convection/centered.hpp'
        code = convection.read_text()
        start = code.index('VectorDbl<nVar> diffU;')
        stop = code.index('/*--- Inviscid fluxes',start)
        (Path(tmp)/'su2_jump.inc').write_text(code[start:stop])
        library = str(Path(tmp)/'probe.so')
        subprocess.run(flags[:flags.index('-MD')] + ['-shared', '-I'+str(source), '-I'+tmp,
                       str(Path(__file__).with_name('disk_face_probe.cpp')), '-o', library], cwd=build, check=True)
        kernel = ctypes.CDLL(library).face
        kernel.argtypes = [np.ctypeslib.ndpointer(np.float64, flags='C_CONTIGUOUS')]*3
        kernel.restype = None
        base = primitive(q)

        def evaluate(left):
            out = np.empty(72)
            kernel(primitive(left), base, out)
            return out

        raw = evaluate(q)
        # Perturb density by a few ppm, velocities by ~0.01 m/s and
        # energy density by ~100 J/m³. Both flashes remain liquid.
        estimates = []
        for scale in (1, .5, .25):
            columns = []
            for j, h in enumerate(scale*np.array([.002, 10., 10., 100.])):
                delta = np.eye(4)[j]*h
                columns.append((evaluate(q+delta)[:8]-evaluate(q-delta)[:8])/(2*h))
            estimates.append(np.stack(columns, axis=1).tolist())

        # Independent chain rule at equal face states, including the HEOS
        # derivatives and enthalpy terms in the energy row.
        primitive(q)
        rho, mx, my, E = q
        u, v = mx/rho, my/rho
        k = eos.first_partial_deriv(CP.iP, CP.iUmass, CP.iDmass)/rho
        dp = np.array([eos.first_partial_deriv(CP.iP, CP.iDmass, CP.iUmass)
                       + k*(u*u+v*v-E/rho), -k*u, -k*v, k])
        du = np.array([-u, 1., 0., 0.])/rho
        unit = np.eye(4)
        exact = .5*np.stack([unit[1], mx*du+u*unit[1]+dp, my*du+u*unit[2],
                             (E+base[3])*du+u*(unit[3]+dp)])
        jump = unit.copy()
        jump[-1] += dp
        # A second face has unequal density, speed, pressure and enthalpy.
        # This exercises derivatives of the actual mean-primitives flux.
        base = primitive(q+np.array([.005, 4., -2., 30.]))
        unequal = evaluate(q)[40:].reshape(8,4)
        unequal_study = []
        for scale in (1,.5,.25):
            deltas = np.eye(4)*(scale*np.array([.002,10.,10.,100.]))
            unequal_study.append(np.column_stack([(evaluate(q+d)[:8]-evaluate(q-d)[:8])/(2*d[j])
                                                  for j,d in enumerate(deltas)]))
        unequal_fd = unequal_study[-1]
        for actual, expected in ((unequal, unequal_fd), (raw[40:].reshape(8,4), estimates[-1])):
            np.testing.assert_allclose(actual, expected, atol=3e-6, rtol=2e-6)
        np.testing.assert_allclose(raw[40:].reshape(8,4),np.vstack((exact,jump)), rtol=1e-12,atol=1e-12)
        return dict(unequal_fd_by_scale=[v.tolist() for v in unequal_study],
                    unequal_step_gate_pass=[bool(np.allclose(unequal,x,atol=3e-6,rtol=2e-6))
                                            for x in unequal_study], unequal_corrected=unequal.tolist(), unequal_fd=unequal_fd.tolist(), xy_m=[state[k][index] for k in ('x','y')], q=q.tolist(),
                    normal=[1,0], steps=[.002,10,10,100], scales=[1,.5,.25],
                    rows='centered mass,mx,my,E then normalized JST jump mass,mx,my,rhoH',
                    installed=np.reshape(raw[8:40],(8,4)).tolist(), corrected=raw[40:].reshape(8,4).tolist(), fd=estimates,
                    equal_state_chain_rule=np.vstack((exact,jump)).tolist())


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('restart', type=Path)
    args = p.parse_args()
    print(json.dumps(audit(args.source.resolve(), args.restart), indent=2, allow_nan=False))
