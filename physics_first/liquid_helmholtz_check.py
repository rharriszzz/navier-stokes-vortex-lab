"""Independent decimal evaluation of IAPWS-95 near the R293 ambient liquid.

Uses the water coefficients from the installed library, no CoolProp property
or derivative calls in the oracle. Central differences of Helmholtz energy
and scalar secants suffice for a few audit points; never used to evolve flow.
"""
import json
from decimal import Decimal as D, localcontext

import CoolProp.CoolProp as CP


class Helmholtz:
    def __init__(self):
        eos = json.loads(CP.get_fluid_param_string("Water", "JSON"), parse_float=D)[0]['EOS'][0]
        self.R = eos['gas_constant'] / eos['molar_mass']
        reducing = eos['STATES']['reducing']
        self.rc = reducing['rhomolar'] * eos['molar_mass']
        self.tc = reducing['T']
        self.ideal = eos['alpha0']
        self.power, self.gauss, self.critical = eos['alphar']

    def alpha(self, d, t):
        lead, log, planck = self.ideal
        a = d.ln() + lead['a1'] + lead['a2']*t + log['a']*t.ln()
        for n, theta in zip(planck['n'], planck['t']):
            a += n*(1-(-theta*t).exp()).ln()
        g = self.power
        for n, i, j, ell in zip(g['n'], g['d'], g['t'], g['l']):
            a += n*d**i*t**j*((-d**ell).exp() if ell else 1)
        g = self.gauss
        for n, i, j, eta, beta, eps, gamma in zip(*(g[k] for k in
                ('n', 'd', 't', 'eta', 'beta', 'epsilon', 'gamma'))):
            a += n*d**i*t**j*(-eta*(d-eps)**2-beta*(t-gamma)**2).exp()
        g = self.critical
        x = (d-1)**2
        for n, A, B, C, F, i, j, beta in zip(*(g[k] for k in
                ('n', 'A', 'B', 'C', 'D', 'a', 'b', 'beta'))):
            theta = 1-t + A*x**(1/(2*beta))
            a += n*d*(theta**2+B*x**i)**j*(-C*x-F*(t-1)**2).exp()
        return a

    def pressure_energy(self, rho, temp):
        d, t = rho/self.rc, self.tc/temp
        h = D('1e-13')
        ad = (self.alpha(d+h,t)-self.alpha(d-h,t))/(2*h)
        at = (self.alpha(d,t+h)-self.alpha(d,t-h))/(2*h)
        return rho*self.R*temp*d*ad, self.R*self.tc*at


def root(f, x, increment):
    old = x + increment
    fo = f(old)
    for _ in range(8):
        fx = f(x)
        if abs(fx) < D('1e-25'):
            return x
        old, x, fo = x, x-fx*(x-old)/(fx-fo), fx
    raise ArithmeticError("decimal reference inversion did not converge")


def samples():
    from .liquid_imex import Liquid, LENGTH, step
    w = Liquid()
    with localcontext() as ctx:
        ctx.prec = 48
        oracle = Helmholtz()
        T, P = D('293.15'), D('101325')
        rho = root(lambda r: oracle.pressure_energy(r,T)[0]-P, D(998), D('.01'))
        _, e = oracle.pressure_energy(rho,T)
        rows = []
        for amplitude in (100., 10., .0001, .000001):
            U = w.initialize(16, amplitude, 1)
            V, pressure, _, _ = step(w, U, LENGTH/(w.c*64), LENGTH/16,
                                     tol=max(1e-17,2e-13*amplitude))
            for i in (4, 12):
                r, m, H = (D.from_float(float(v)) for v in V[:,i])
                density = rho+r
                target = e + H/density - (m/density)**2/2
                temp = root(lambda t: oracle.pressure_energy(density,t)[1]-target,T,D('.0001'))
                p, _ = oracle.pressure_energy(density,temp)
                rows.append(dict(amplitude_Pa=amplitude, cell=i, implicit_Pa=pressure[i],
                                 decimal_Pa=float(p-P), difference_Pa=float(D.from_float(pressure[i])-(p-P))))
        return dict(decimal_digits=ctx.prec, rho0=str(rho), e0=str(e), samples=rows)


if __name__ == '__main__':
    print(json.dumps(samples(), indent=1))
