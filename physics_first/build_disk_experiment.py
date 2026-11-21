"""Relink one experimental translation unit in a new directory, using an existing SU2 build."""
import argparse
import json
import shlex
import shutil
import subprocess
from pathlib import Path


def build(source, dest):
    rev = subprocess.check_output(['git','rev-parse','HEAD'], cwd=source, text=True).strip()
    if rev != '7048fd35f56d4bf52e586429d6746a36a10255f8':
        raise ValueError('Unexpected SU2 source revision')
    dest.mkdir(parents=True, exist_ok=False)
    inc = dest/'SU2_CFD/include'
    shutil.copytree(source/'SU2_CFD/include', inc)
    for name in ('Common','externals','subprojects'):
        (dest/name).symlink_to(source/name, target_is_directory=True)
    directory = inc/'numerics_simd/flow/convection'
    shutil.copy(Path(__file__).with_name('disk_water_jac.hpp'), directory)
    file = directory/'centered.hpp'
    code = file.read_text()
    def replace(old, new):
        nonlocal code
        if old not in code:
            raise ValueError('Source context mismatch')
        code = code.replace(old,new,1)
    replace('#include "common.hpp"', '#include "common.hpp"\n#include "disk_water_jac.hpp"')
    replace('const su2double fixFactor;', 'const bool waterBlock;\n  const su2double fixFactor;')
    replace('fixFactor(config.', '''waterBlock(nDim == 2 && config.GetKind_FluidModel() == COOLPROP &&
               config.GetKind_Centered_Flow() == CENTERED::JST && !config.GetDynamic_Grid() &&
               config.GetKappa_4th_Flow() == 0.0), fixFactor(config.''')
    replace('if (implicit) {\n      jac_i = inviscidProjJac', '''if (implicit && waterBlock) {
      jac_i = waterCenteredJac(V.i, avgV, gatherVariables<2>(iPoint,solution.GetSecondary()), normal);
      jac_j = waterCenteredJac(V.j, avgV, gatherVariables<2>(jPoint,solution.GetSecondary()), normal);
    } else if (implicit) {
      jac_i = inviscidProjJac''')
    replace('scalarDissipationJacobian(V.i, gamma, dissip_i, jac_i);\n      scalarDissipationJacobian(V.j, gamma, dissip_j, jac_j);',
            '''if (Base::waterBlock) {
        waterJumpJac(V.i, gatherVariables<2>(iPoint,solution.GetSecondary()), dissip_i, jac_i);
        waterJumpJac(V.j, gatherVariables<2>(jPoint,solution.GetSecondary()), dissip_j, jac_j);
      } else {
        scalarDissipationJacobian(V.i, gamma, dissip_i, jac_i);
        scalarDissipationJacobian(V.j, gamma, dissip_j, jac_j);
      }''')
    file.write_text(code)
    builddir = source/'build-water'
    command = next(row['command'] for row in json.loads((builddir/'compile_commands.json').read_text())
                   if row['file'].endswith('/CNumericsSIMD.cpp'))
    flags = shlex.split(command)
    obj = str(dest/'numerics.o')
    subprocess.run(flags[:flags.index('-MD')]+['-c',str(inc/'numerics_simd/CNumericsSIMD.cpp'),
                   '-o',obj], cwd=builddir, check=True)
    cmd = subprocess.check_output(['ninja','-t','commands','SU2_CFD/src/SU2_CFD'], cwd=builddir,text=True)
    link = shlex.split(cmd.splitlines()[-1])
    link[link.index('-o')+1] = str(dest/'SU2_CFD_water')
    link.insert(link.index('-Wl,--start-group'),obj)
    subprocess.run(link,cwd=builddir,check=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('destination', type=Path)
    a = p.parse_args()
    build(a.source.resolve(), a.destination.resolve())
