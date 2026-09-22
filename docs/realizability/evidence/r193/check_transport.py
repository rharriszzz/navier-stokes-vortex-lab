"""Closed-form R193 comparison arithmetic, not a tank/response solver."""
import cmath
import json
import math
import platform
from pathlib import Path

nu, omega, m = 1e-6, 2*math.pi*.1, 4
R, rv, H, b = .025, .1, .025, .01
rc = b*math.sqrt(1.2564312086261697)
c = .05*rc/(1-math.exp(-1.2564312086261697))
Omega = c*(1-math.exp(-R*R/b**2))/R**2
L = math.hypot(rv-R, .045-H)
checks = []
def check(name, good):
    assert good, name
    checks.append(name)
def kappa(V, detuning, k=0):
    z = nu*k*k+1j*detuning
    if z == 0:
        return 0j
    return 2*z/(V+cmath.sqrt(V*V+4*nu*z))
def gain(V, detuning, k=0):
    return math.exp(-kappa(V,detuning,k).real*L)

# Check the characteristic equation over both traveling-wave signs and scales.
for V in (0, .0005, .002, .005, .01, .02, .08):
    for d in (-omega, omega, 4*Omega-omega, 4*Omega+omega):
        for k in (0, m/R):
            q = kappa(V,d,k)
            assert abs(nu*q*q+V*q-nu*k*k-1j*d)<2e-13
            assert q.real >= 0
check('characteristic PDE residual and decaying branch grid', True)
check('quiescent Stokes limit', abs(kappa(0,omega)-(1+1j)*math.sqrt(omega/(2*nu)))<1e-12)
check('negative detuning conjugacy', abs(kappa(.005,-omega)-kappa(.005,omega).conjugate())<1e-12)
check('zero detuning and transverse wave number gives unity', gain(.001,0)==1)
check('high transport inviscid phase limit', abs(kappa(10,omega)*10/(1j*omega)-1)<1e-7)
check('radial plus axial distance', math.isclose(L*L, .006025))
check('finite band makes radial-only distance too short', L>.075)
# Independent real radical evaluation avoids the complex-root code path.
V,d,k=.01,4*Omega+omega,m/R
x=V*V+4*nu*nu*k*k; y=4*nu*d
alpha=(math.sqrt((math.hypot(x,y)+x)/2)-V)/(2*nu)
check('independent real attenuation expression', math.isclose(alpha,kappa(V,d,k).real,rel_tol=1e-12))
# r times the vector Laplacian of v_theta=ell/r, for monomials ell=r^n.
for n in range(6):
    r=.07
    lhs=r*((n-1)*(n-2)*r**(n-3)+(n-1)*r**(n-3)-(m*m+1)*r**(n-3))
    rhs=(n*(n-1)-n-m*m)*r**(n-2)
    assert math.isclose(lhs,rhs,rel_tol=1e-13,abs_tol=1e-13)
check('angular momentum cylindrical diffusion transform', True)
# Standing forcing must retain BOTH traveling waves.
for j in range(13):
    th=j*.31; t=j*.17
    lhs=math.cos(m*th)*math.cos(omega*t)
    rhs=(math.cos(m*th-omega*t)+math.cos(m*th+omega*t))/2
    assert abs(lhs-rhs)<1e-14
check('standing-wave decomposition', True)
# Conditional strain trajectories, explicitly NOT a vessel base solution.
a=.02; z0=.06; tcap=math.log(.1/z0)/(2*a); tr=math.log(rv/R)/a
check('strain path invariant z*r^2', math.isclose(z0*math.exp(2*a*tcap)*(rv*math.exp(-a*tcap))**2,z0*rv**2))
check('conditional upper-band path reaches cap before diagnostic radius', tcap<tr and rv*math.exp(-a*tcap)>R)
# Equal coherent paths can cancel exactly, so travel speed cannot give lower gain.
check('two-path phase cancellation', abs((cmath.exp(0j)+cmath.exp(1j*math.pi))/2)<1e-15)
# Uniform scalar residual r integrated through dq/dt+lambda*q=r.
lam=.2; T=3.; force=.01; exact=force*(1-math.exp(-lam*T))/lam
check('scalar residual no-growth error bound', exact<=T*force)
rows=[]
for V in (0,.0005,.002,.005,.01,.02):
    rows.append(dict(V_m_s=V,Pe=V*L/nu,travel_s=L/V if V else None,
        no_swirl_gain=gain(V,omega),
        side_frozen_plus_gain=gain(V,4*Omega-omega,m/R),
        side_frozen_minus_gain=gain(V,4*Omega+omega,m/R)))
thresholds=[]
for d,k in ((omega,0),(4*Omega-omega,m/R),(4*Omega+omega,m/R)):
    lo,hi=0.,.1
    for _ in range(60):
        mid=(lo+hi)/2
        if gain(mid,d,k)<.1: lo=mid
        else: hi=mid
    V=(lo+hi)/2; h=math.log(10)/L; beta=d/(V+2*nu*h)
    assert abs(nu*(h*h-beta*beta)+V*h-nu*k*k)<1e-12
    assert abs(gain(V,d,k)-.1)<1e-13
    thresholds.append(V)
check('gain point-one thresholds independently satisfy real characteristic equation', True)
Q=2/60000; U=Q/(32*math.pi*.004**2/4)
result=dict(classification='analytical comparison only; no tank solution or gain bound',
 python=platform.python_version(), checks_passed=len(checks), checks=checks,
 geometry=dict(nearest_surface_m=L,band_center_surface_m=math.hypot(.075,.035),
 nearest_equatorial_peak_m=math.hypot(rv-rc,.045),diffusion_time_s=L*L/nu),
 swirl=dict(Omega_side_rad_s=Omega,Omega_peak_rad_s=.05/rc,
 detunings_side_rad_s=[4*Omega-omega,4*Omega+omega],
 detunings_peak_rad_s=[4*.05/rc-omega,4*.05/rc+omega],
 azimuthal_diffusion_side_s=R*R/(nu*m*m),azimuthal_diffusion_peak_s=rc*rc/(nu*m*m)),
 rows=rows,scalar_gain_point1_speed_m_s=thresholds,
 time_scales=dict(port_bore_speed_m_s=U,normal_speed_distance_ratio_s=L/U,
 angled_radial_speed_distance_ratio_s=L/(U/math.sqrt(2)),
 volume_turnover_wall_s=math.pi*rv*rv*.2/Q,
 volume_turnover_ports_s=math.pi*rv*rv*.2/(2*Q),
 conditional_strain_radial_time_s=tr,conditional_strain_exit_s=tcap,
 conditional_strain_exit_radius_m=rv*math.exp(-a*tcap)),
 phase=dict(five_degree_time_at_drive_s=math.radians(5)/omega,
 five_degree_time_at_side_detunings_s=[math.radians(5)/d for d in (4*Omega-omega,4*Omega+omega)]))
Path(__file__).with_name('transport_screen.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
