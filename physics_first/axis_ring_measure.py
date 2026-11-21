"""Section geometry, material probes and mechanical budgets for the meridional solve."""
import numpy as np
from scipy.integrate import cumulative_simpson, simpson
from scipy.interpolate import RectBivariateSpline
from scipy.optimize import brentq, root

from .axis_ring import CORE, GAMMA, RADIUS, RHO

nodes, weights = np.polynomial.legendre.leggauss(20)
angles = np.arange(80) * 2*np.pi/80
normal = np.array([np.cos(angles), np.sin(angles)])
polar = normal[:, None, :] * ((nodes+1)/2)[None, :, None]
area_weights = weights[:, None]*(nodes[:, None]+1)*np.pi/(2*len(angles))


def locate(g, omega):
    i,j = np.unravel_index(np.argmax(omega), omega.shape)
    # Fit a local spline and, independently, the quadratic Taylor polynomial.
    sl = np.s_[i-3:i+4,j-3:j+4]
    patch = RectBivariateSpline(g.r[i-3:i+4], g.z[j-3:j+4], omega[sl])
    center = np.array([g.r[i], g.z[j]])
    def grad(x):
        r,z = center + g.h*x
        return g.h*np.array([patch.ev(r,z,dx=1), patch.ev(r,z,dy=1)])
    solved = root(grad, np.zeros(2))
    if np.linalg.norm(grad(solved.x)) > 1e-8 or np.max(abs(solved.x)) > 1:
        raise ValueError('Unresolved ridge in local patch')
    y = omega[sl][2:5,2:5]
    first = np.array([y[2,1]-y[0,1], y[1,2]-y[1,0]])/2
    mixed = (y[2,2]+y[0,0]-y[2,0]-y[0,2])/4
    hess = np.array([[y[2,1]-2*y[1,1]+y[0,1], mixed],
                     [mixed, y[1,2]-2*y[1,1]+y[1,0]]])
    return center+g.h*solved.x, center-g.h*np.linalg.solve(hess,first)


def shape(interp, center, radius):
    offsets = radius*polar
    r,z = offsets + center[:,None,None]
    signed = interp(r,z)*area_weights*radius**2
    positive = signed.clip(min=0)
    mass = positive.sum()
    centroid = np.einsum('ijk,jk->i', offsets, positive)/mass
    deviations = offsets-centroid[:,None,None]
    covariance = np.einsum('ijk,ljk,jk->il', deviations,deviations,positive)/mass
    minor,major = np.sqrt(2*np.linalg.eigvalsh(covariance))
    return dict(flux=signed.sum(), positive=mass, minor=minor, major=major,
                area=np.pi*minor*major, centroid_r=center[0]+centroid[0],
                centroid_z=center[1]+centroid[1])


def mechanics(g, eta, phi, ur, uz, rhs, nu):
    """Pressure gradient from both momentum components, anchored at one outer corner."""
    omega = g.R*eta
    ur_z, uz_z = g.axial(ur), g.axial(uz)
    hoop = -g.axial(phi)
    ur_r, uz_r = hoop + g.R*(g.dr @ hoop), g.dr @ uz
    ur_t, uz_t = g.velocity(g.invert(rhs))
    visc_r, visc_z = nu*g.axial(omega), -nu*(2*eta+g.R*(g.dr @ eta))
    pr = RHO*(visc_r - ur_t - ur*ur_r - uz*ur_z)
    pz = RHO*(visc_z - uz_t - ur*uz_r - uz*uz_z)
    side = cumulative_simpson(pz[-1], x=g.z, initial=0)
    radial = cumulative_simpson(pr, x=g.r, axis=0, initial=0)
    p = side + (radial-radial[-1])
    kinetic = .5*RHO*(ur**2+uz**2)
    shear = RHO*nu*(ur_z+uz_r)
    diss = 2*RHO*nu*(ur_r**2+hoop**2+uz_z**2+.5*(ur_z+uz_r)**2)
    out = {}
    for name, bounds in [('box',(0,g.r[-1],g.z[0],g.z[-1])),
                         ('local',(.011,.019,-.004,.004))]:
        i,k = [np.argmin(abs(g.r-b)) for b in bounds[:2]]
        j,l = [np.argmin(abs(g.z-b)) for b in bounds[2:]]
        xx, yy = g.r[i:k+1], g.z[j:l+1]
        def integral(a):
            return simpson(simpson(a[i:k+1,j:l+1], x=yy), x=xx)
        def flux(a,b):
            return simpson(a[k,j:l+1]-a[i,j:l+1], x=yy)+simpson(b[i:k+1,l]-b[i:k+1,j], x=xx)
        surface = 2*np.pi*g.R
        fr, fz = ur*omega+visc_z, uz*omega-visc_r
        moment = np.pi*RHO*g.R**2
        values = dict(energy_J=integral(surface*kinetic), diss_W=integral(surface*diss),
                      adv_W=flux(surface*kinetic*ur,surface*kinetic*uz),
                      pressure_W=flux(surface*p*ur,surface*p*uz),
                      stress_W=flux(-surface*(2*RHO*nu*ur_r*ur+shear*uz),
                                    -surface*(shear*ur+2*RHO*nu*uz_z*uz)),
                      impulse_Ns=integral(moment*omega), impulse_out_N=flux(moment*fr,moment*fz),
                      impulse_source_N=integral(2*np.pi*RHO*g.R*fr),
                      gamma=integral(omega), gamma_out=flux(fr,fz))
        out.update({name+'_'+key:value for key,value in values.items()})
    return out


def measure(g, eta, markers, nu, t):
    omega = g.R*eta
    ridge, quadratic = locate(g, omega)
    phi = g.invert(eta)
    ur, uz = g.velocity(phi)
    rhs = g.tendency(eta, ur, uz, nu)
    visc = nu*g.R*g.diffusion(eta)
    hoop = -g.axial(phi)
    w = g.interpolate(omega)
    sample_u, sample_v = g.interpolate(ur), g.interpolate(uz)
    result = dict(t_s=t, ridge_r=ridge[0], ridge_z=ridge[1], ridge_peak=w(*ridge),
                  ridge_ur=sample_u(*ridge), ridge_uz=sample_v(*ridge))
    for tag,center,radius,interp in [('ridge',ridge,2*CORE,w),('quadratic',quadratic,2*CORE,w),
                                     ('line',markers[0],2*CORE,w),('small',ridge,1.8*CORE,w),
                                     ('large',ridge,2.2*CORE,w),
                                     ('linear',ridge,2*CORE,g.interpolate(omega,1))]:
        result.update({tag+'_'+k:v for k,v in shape(interp,center,radius).items()})
    def half_residual(radius):
        r,z = ridge[:,None,None]+radius*polar
        return (w(r,z)*area_weights).sum()*radius**2-GAMMA/2
    result['half_radius'] = brentq(half_residual, CORE/2, 1.5*CORE, xtol=1e-14)
    r,z = ridge[:,None]+2*CORE*normal
    dl = 2*CORE*2*np.pi/len(angles)
    u,v = sample_u(r,z), sample_v(r,z)
    # Positive theta normal means clockwise in the (r,z) plotting plane.
    result['rim_loop'] = dl*np.sum(u*normal[1]-v*normal[0])
    result['rim_adv_out'] = dl*np.sum(w(r,z)*(u*normal[0]+v*normal[1]))
    result['rim_visc_out'] = -nu*dl*np.sum(
        g.interpolate(2*eta+g.R*(g.dr @ eta))(r,z)*normal[0]+
        g.interpolate(g.axial(omega))(r,z)*normal[1])
    result['rim_move_r'], result['rim_move_z'] = dl*(w(r,z)*normal).sum(axis=1)
    material_w = w(*markers.T)
    stretch = g.interpolate(hoop)(*markers.T)
    material_visc = g.interpolate(visc)(*markers.T)
    for i,point in enumerate(markers):
        values = dict(r=point[0], z=point[1], omega=material_w[i], ur=sample_u(*point),
                      uz=sample_v(*point), stretch=stretch[i], visc=material_visc[i],
                      Domega=stretch[i]*material_w[i]+material_visc[i])
        result.update({f'm{i}_'+k:v for k,v in values.items()})
    result.update(mechanics(g, eta, phi, ur, uz, rhs, nu))
    return result, (ur, uz, omega, hoop, visc)
