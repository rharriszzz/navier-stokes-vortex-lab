// Isolated probe compiled against the qualified source tree. One SIMD lane,
// unit x-normal, unit area, fixed mesh. No changes to the solver executable.
#include "SU2_CFD/include/numerics_simd/flow/convection/common.hpp"

#include "disk_water_jac.hpp"

extern "C" void face(const double* left, const double* right, double* out) {
  CCompressiblePrimitives<2,7> vi, vj, mean;
  for (int k = 0; k < 7; ++k) {
    vi.all(k) = left[k];
    vj.all(k) = right[k];
    mean.all(k) = 0.5 * (vi.all(k) + vj.all(k));
  }
  VectorDbl<2> normal;
  normal(0) = 1.0;
  normal(1) = 0.0;
  auto ui = compressibleConservatives(vi);
  auto uj = compressibleConservatives(vj);
  auto flux = inviscidProjFlux(mean, compressibleConservatives(mean), normal);
  auto jac = inviscidProjJac(Double(1.4), vi.velocity(), ui.energy(), normal, Double(0.5));
  MatrixDbl<4> dissJac;
  dissJac = Double(0.0);
  scalarDissipationJacobian(vi, Double(1.4), Double(1.0), dissJac);
  VectorDbl<2> sec;
  sec(0) = left[7];
  sec(1) = left[8];
  auto waterJac = waterCenteredJac(vi, mean, sec, normal);
  MatrixDbl<4> jump;
  jump = Double(0.0);
  waterJumpJac(vi, sec, Double(1.0), jump);
  // Use the actual centered.hpp conservative-jump statements from this build.
  constexpr size_t nVar = 4;
  CPair<CCompressiblePrimitives<2,7>> V{vi, vj};
  CPair<CCompressibleConservatives<2>> U{ui, uj};
#include "su2_jump.inc"
  for (int i = 0; i < 4; ++i) {
    out[i] = flux(i)[0];
    // centered.hpp JST jump per unit eps2 * corrected spectral radius.
    out[4+i] = diffU(i)[0];
    for (int j = 0; j < 4; ++j) {
      out[8+4*i+j] = jac(i,j)[0];
      out[24+4*i+j] = dissJac(i,j)[0];
      out[40+4*i+j] = waterJac(i,j)[0];
      out[56+4*i+j] = jump(i,j)[0];
    }
  }
}
