# Mac inventory for the B2 machine comparison

**Historical inventory prompt:** R034/R046 completed the hardware/import checks;
R058 checked the package manager, encoder and native FEM package provenance.
For the current remaining installation and benchmark tasks, start with
[MAC_INSTALL_AND_BENCHMARK_PLAN.md](MAC_INSTALL_AND_BENCHMARK_PLAN.md).
Use the commands below only for a fresh inventory when needed; this prompt
does not perform the setup or performance comparison.

Use GPT-5.6 Luna with medium reasoning for this bounded, read-only inventory.
Run Codex CLI on the Mac from the project checkout, then use this short prompt:

> Read `docs/realizability/MAC_INVENTORY_PROMPT.md` and follow it. Run the listed read-only inventory commands and report their output and what it establishes about this Mac's architecture, OS, available memory, Python, and installed project numerical packages. Do not install software, change settings, benchmark, migrate files, or run project numerical work. Stop after the inventory report.

Run these commands in Terminal on the Mac:

```sh
sw_vers -productVersion
uname -m
system_profiler SPHardwareDataType | grep -E 'Chip|Processor Name|Memory:'
sysctl -n hw.memsize
memory_pressure
```

If the project's Python environment is installed, activate it first and also
run:

```sh
python3 -c 'import platform,sys; print("Python:",sys.version.split()[0],"Architecture:",platform.machine())'
python3 -c 'import importlib.util as u; print({n: bool(u.find_spec(n)) for n in ("dolfinx","petsc4py","mpi4py")})'
```

Report whether those Python packages were checked in the project environment
or the default Python interpreter. Do not infer that the Mac can run the
physical calculation from its installed RAM alone. The next decision is to
compare these facts with the expected workload; the following scientific
review remains on the PC under GPT-6 Astra with high reasoning. No software
installation, benchmark, repository transfer, or numerical run is part of this
inventory.
