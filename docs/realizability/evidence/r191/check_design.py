"""Check R191 conditional algebra/scale arithmetic; no fluid solve or input writes."""
import json
import math
import platform
import sympy as s

checks = []

def exact(name, expression):
    assert s.simplify(expression) == 0, (name, expression)
    checks.append(name)

r, R, H, B, nu, rho, c, a = s.symbols('r R H B nu rho c a', positive=True)
L = c * (1-s.exp(-r*r/B))
I = (R*R-B*(1-s.exp(-R*R/B)))/2
J = 4*s.pi*rho*H*c*I
side = -4*s.pi*rho*a*H*c*R*R*(1-s.exp(-R*R/B))
caps = 8*s.pi*rho*a*H*c*I
mu = 8*s.pi*rho*nu*H*c*((1+R*R/B)*s.exp(-R*R/B)-1)
exact('inventory from volume integral', J-4*s.pi*rho*H*s.integrate(r*L,(r,0,R)))
exact('side mean flux', side-4*s.pi*rho*H*R*(-a*R)*L.subs(r,R))
exact('two endcaps mean flux', caps-8*s.pi*rho*a*H*s.integrate(r*L,(r,0,R)))
exact('side viscous torque', mu-4*s.pi*rho*nu*H*R*(s.diff(L,r)-2*L/r).subs(r,R))
exact('Gaussian central balance', s.diff(J,B)*(4*nu-2*a*B)+side+caps-mu)
exact('regular axis radial advective flux', s.limit(r*(-a*r)*L,r,0))
exact('regular axis radial viscous flux', s.limit(r*(s.diff(L,r)-2*L/r),r,0))
K=s.symbols('K')
exact('annular nonzero correlation zero divergence', s.diff(r*r*(K/r**2),r)/r)
th, phase, tt, lag=s.symbols('theta phi t delta', real=True)
# Separately integrate spatial/temporal products, including cross terms.
space=s.integrate(s.expand_trig(s.cos(4*th)*s.cos(4*th+phase)),(th,0,2*s.pi))/(2*s.pi)
time=s.integrate(s.expand_trig(s.cos(tt)*s.cos(tt+lag)),(tt,0,2*s.pi))/(2*s.pi)
exact('spatial average factor',space-s.cos(phase)/2)
exact('temporal lag factor',time-s.cos(lag)/2)
exact('joint average factor',space*time-s.cos(phase)*s.cos(lag)/4)
exact('opposite phase changes sign',space.subs(phase,phase+s.pi)+space)
exact('quadrature phase null in diagnostic ansatz',space.subs(phase,s.pi/2))
q=float(s.nsolve(s.exp(s.Symbol('q'))-1-2*s.Symbol('q'),1.25))
assert 1.1208 < math.sqrt(q) < 1.1210
checks.append('nonzero Gaussian peak root')
rows=[]
for bf in (.003,.001):
    for duration in (10,100):
        b0=.01
        k=(b0*b0-bf*bf)/duration
        peak=(4e-6+k)/(2*bf*bf)
        flow=4*math.pi*peak*.025**3*60000
        assert math.isclose(b0*b0/k-bf*bf/k,duration)
        assert math.isclose((b0/bf)**2,(b0*b0/k)/(bf*bf/k))
        assert math.isclose(4e-6-2*peak*bf*bf,-k)
        rows.append(dict(final_b_mm=bf*1000,duration_s=duration,
                         radius_ratio=b0/bf,tau_decades=2*math.log10(b0/bf),
                         peak_strain_per_s=peak,central_flow_L_min=flow))
checks.append('four schedule rows: duration ratio and width equation')
print(json.dumps(dict(python=platform.python_version(),sympy=s.__version__,
                     checks_passed=len(checks),checks=checks,
                     gaussian_peak_over_width=math.sqrt(q),rows=rows),indent=2))
