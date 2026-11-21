# Rebuilding daisy's SU2 water solver

The working command on daisy is `su2-water`. Its target is `~/.local/opt/water-acoustics/install-8.6.0/bin/SU2_CFD`. These steps document a rebuild on x86-64 Linux using Git, GCC/G++ and Python 3.12. Use a **fresh installation directory**. Building only SU2_CFD needs about 0.7 GiB for source, build products and tools on this host. Three compile jobs fit the observed available memory. The solver uses the host CPU architecture.

```bash
prefix="$HOME/.local/opt/water-acoustics-rebuild"
mkdir -p "$prefix"
python3.12 -m venv "$prefix/tools"
export PATH="$prefix/tools/bin:$PATH"
python -m pip install meson==1.8.5 ninja==1.13.0 cmake==3.31.10 numpy==2.5.5 CoolProp==7.2.0
git clone --depth 1 --branch v8.6.0 https://github.com/su2code/SU2.git "$prefix/SU2-8.6.0"
cd "$prefix/SU2-8.6.0"
git submodule update --init --depth 1 externals/eigen externals/FADO externals/mel subprojects/CoolProp
git -C subprojects/CoolProp submodule update --init --depth 1 --jobs 4
ln -s "$prefix/tools/bin/ninja" ninja
python preconfigure.py --no-codi --no-medi --no-opdi --no-mpp --no-mlpcpp
meson setup build-water --prefix="$prefix/install-8.6.0" \
  -Denable-coolprop=true -Dwith-mpi=disabled -Dwith-omp=false \
  -Denable-cgns=false -Denable-tecio=false -Dbuildtype=release -Doptimization=1
ninja -C build-water -j3 SU2_CFD/src/SU2_CFD
install -D -m755 build-water/SU2_CFD/src/SU2_CFD "$prefix/install-8.6.0/bin/SU2_CFD"
"$prefix/install-8.6.0/bin/SU2_CFD" --help
```

The first build attempt established two concrete dependencies. SU2 requires its preconfiguration step even with a separately installed Meson, and the output code includes MEL in the serial CFD build. Both are included above. The Python CoolProp wheel supplies the initializer and the independent endpoint reader. The C++ executable links its own compiled CoolProp implementation at the same revision. Check `python -c 'import CoolProp; print(CoolProp.__gitrevision__)'` against `git -C subprojects/CoolProp rev-parse HEAD`. Validate a rebuilt executable with the [periodic case](ACOUSTIC_RESULT.md#installation-and-reproducibility). The official stock OpenMP binary lacks this EOS configuration.
