"""R192 conditional engineering arithmetic; no fluid solver or hardware response."""
import json
import math
import platform
from pathlib import Path

p = math.pi
rho, nu, mu = 1000.0, 1e-6, 1e-3
R, H, b, vessel_r, vessel_h = .025, .025, .01, .1, .2
xpeak = 1.2564312086261697
rc = b * math.sqrt(xpeak)
c = .05 * rc / (1 - math.exp(-xpeak))
a = 2 * nu / b**2
x = R**2 / b**2
I = (R**2 - b**2 * (1 - math.exp(-x))) / 2
J = 4*p*rho*H*c*I
side = -4*p*rho*a*H*c*R**2*(1-math.exp(-x))
caps = 8*p*rho*a*H*c*I
visc = 8*p*rho*nu*H*c*((1+x)*math.exp(-x)-1)
A, B, f, duration = .002, .002, .1, 100.
ws = 4*p*rho*H*R**2
wc = 4*p*rho*R**3/3  # absolute lever-arm weights, BOTH caps
contrast = ws*A*B/2
impulse = contrast*duration
limit = impulse/3
area, Q, amp = p*.004**2/4, 2/60000, .02
speed = Q/(32*area)
peak_speed = speed+amp
inlet_torque = rho*vessel_r*Q*speed/math.sqrt(2)
delta = math.sqrt(nu/(p*f))
wall_weight = .8*2*p*vessel_r**2*.06
wall_stress = mu*amp*math.sqrt(2*p*f/nu)
pixel = .06/2048
sigma = math.sqrt(2)*.1*pixel/.005
cov_limit = 4e-6/(duration*(ws+wc))
# Independent, zero-mean velocity noise only; spatial/time RMS A/2 and B/2.
product_sd = math.sqrt(sigma**2*(A*A+B*B)/4+sigma**4)
needed_n = math.ceil((2*math.sqrt(2)*product_sd/cov_limit)**2)
checks = []
def check(name, condition):
    assert condition, name
    checks.append(name)
check('peak equation', abs(math.exp(xpeak)-1-2*xpeak)<1e-12)
check('steady central signed momentum balance', abs(-side-caps+visc)<1e-20)
check('side and cap volume flow agree', math.isclose(2*p*R*2*H*a*R, 2*p*R**2*2*a*H))
for phase in [0, p/2, p, 3*p/2]:
    values = [math.cos(4*2*p*j/16+phase) for j in range(16)]
    check(f'balanced sixteen-sector phase {phase:.6f}', abs(sum(values))<1e-13)
check('positive inlet velocities at modulation limit', speed>amp)
check('laminar branch screening Reynolds number', peak_speed*.004/nu<500)
# Independent quadrature of the local phase identity; not a sampled fluid field.
def average(phase):
    return sum(A*math.cos(4*2*p*j/64)*math.cos(2*p*k/64)*B*
               math.cos(4*2*p*j/64+phase)*math.cos(2*p*k/64)
               for j in range(64) for k in range(64))/64**2
check('opposite-phase covariance difference', math.isclose(average(0)-average(p), A*B/2))
check('quadrature phase null', abs(average(p/2))<1e-20)
# Independent midpoint integration of both cap lever-arm weights.
cap_quad = 4*p*rho*sum(((j+.5)*R/10000)**2*R/10000 for j in range(10000))
check('both cap weights', math.isclose(cap_quad,wc,rel_tol=1e-8))
check('residual allocations respect one-third gate', (4+4+2+2+1)*1e-6 <= limit)
check('wall harmonic diffusion solution', abs(nu*complex(1,1)**2/delta**2-complex(0,2*p*f))<1e-15)
check('wall diffusion sensitivity threshold', math.isclose(math.exp(-.075/math.sqrt(nu/(p*(nu/p*(math.log(10)/.075)**2)))), .1))
check('independent sample bound brackets target', 2*math.sqrt(2)*product_sd/math.sqrt(needed_n)<=cov_limit<2*math.sqrt(2)*product_sd/math.sqrt(needed_n-1))
result = dict(classification='conditional arithmetic only; no response or measurement admitted',
 python=platform.python_version(), checks_passed=len(checks), checks=checks,
 core=dict(vessel_L=p*vessel_r**2*vessel_h*1000, peak_radius_mm=rc*1000,
 circulation_m2_s=2*p*c, strain_per_s=a, central_flow_L_min=4*p*a*H*R**2*60000,
 angular_momentum_kg_m2_s=J, mean_side_N_m=side, mean_caps_N_m=caps, viscous_N_m=visc),
 detection=dict(phase_contrast_N_m=contrast, phase_contrast_N_m_s=impulse,
 expanded_residual_limit_N_m_s=limit, external_torque_contrast_limit_N_m=limit/duration,
 covariance_contrast_expanded_limit_m2_s2=cov_limit, random_only_N_effective_min=needed_n,
 coherent_normal_mean_contrast_error_m_s=4e-6/(duration*(ws+wc)*.05),
 shear_contrast_expanded_error_Pa=2e-6/(duration*(ws+wc)/rho)),
 ports=dict(mean_speed_m_s=speed, peak_speed_m_s=peak_speed,
 branch_Re=peak_speed*.004/nu, inlet_torque_N_m=inlet_torque,
 oscillation_mean_torque_N_m=rho*vessel_r*32*area*amp**2/(4*math.sqrt(2)),
 inlet_relative_matching=limit/duration/inlet_torque,
 branch_pressure_Pa=[32*mu*.5*peak_speed/.004**2+k*rho*peak_speed**2/2+rho*.5*2*p*f*amp for k in (2,10)],
 common_tube_pressure_Pa=[(fd*2/.012+10)*rho*((4/60000)/(p*.012**2/4))**2/2 for fd in (.03,.05)]),
 wall=dict(diffusion_depth_mm=delta*1000, planar_attenuation_75mm=math.exp(-.075/delta),
 amplitude_travel_mm=amp/(2*p*f)*1000, acceleration_m_s2=2*p*f*amp,
 stress_amplitude_Pa=wall_stress, absolute_torque_envelope_N_m=wall_weight*wall_stress,
 diffusion_frequency_for_gain_point1_Hz=nu/p*(math.log(10)/.075)**2),
 optical=dict(pixel_um=pixel*1e6, velocity_noise_m_s=sigma,
 max_exposure_s=.25*pixel/.06, gradient_noise_per_s=math.sqrt(2)*sigma/.001))
Path(__file__).with_name('operating_point.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
