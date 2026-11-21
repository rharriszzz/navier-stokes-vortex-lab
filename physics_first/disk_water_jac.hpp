// Experimental stationary-mesh HEOS/JST block. Include after SU2 common.hpp.
#pragma once

template<class Prim, class Secondary>
auto waterPressureRow(const Prim& v, const Secondary& sec) {
  constexpr auto dim = Prim::nDim;
  const Double k = sec(1) / v.density();
  const Double E = v.enthalpy() - v.pressure()/v.density();
  VectorDbl<dim+2> dp;
  dp(0) = sec(0) + k*(squaredNorm<dim>(v.velocity())-E);
  for (size_t i = 0; i < dim; ++i) dp(i+1) = -k*v.velocity(i);
  dp(dim+1) = k;
  return dp;
}

// Differentiate rho_bar*(v_bar.n), its momentum flux, and mdot*H_bar
// w.r.t. one side. Bars are independent primitive arithmetic means in SU2.
template<class Prim, class Secondary, size_t dim>
auto waterCenteredJac(const Prim& v, const Prim& mean, const Secondary& sec,
                      const VectorDbl<dim>& normal) {
  const auto dp = waterPressureRow(v, sec);
  const Double vn = dot(mean.velocity(), normal);
  const Double mdot = mean.density()*vn;
  MatrixDbl<dim+2> jac;
  for (size_t j = 0; j < dim+2; ++j) {
    const double drho = j == 0;
    const Double dH = ((j == dim+1) + dp(j) - v.enthalpy()*drho)/v.density();
    VectorDbl<dim> du;
    for (size_t i = 0; i < dim; ++i)
      du(i) = ((j == i+1) - v.velocity(i)*drho)/v.density();
    const Double dm = 0.5*(drho*vn + mean.density()*dot(du,normal));
    jac(0,j) = dm;
    for (size_t i = 0; i < dim; ++i)
      jac(i+1,j) = mean.velocity(i)*dm + 0.5*(mdot*du(i) + normal(i)*dp(j));
    jac(dim+1,j) = mean.enthalpy()*dm + 0.5*mdot*dH;
  }
  return jac;
}

template<class Prim, class Secondary, size_t nVar>
void waterJumpJac(const Prim& v, const Secondary& sec, const Double factor, MatrixDbl<nVar>& jac) {
  const auto dp = waterPressureRow(v, sec);
  for (size_t j = 0; j < nVar; ++j) {
    jac(j,j) += factor;
    jac(nVar-1,j) += factor*dp(j);
  }
}
