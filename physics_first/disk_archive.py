"""Pack/replay the fields used by the rotating-disk measurements, losslessly."""

import argparse
import io
from pathlib import Path
import struct
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np

from physics_first.disk_time_cases import CASES
from physics_first.su2_acoustic import FIELDS, MAGIC, read_restart

RELEASES = ("r289-disk16", "r289-disk32", "r289-disk64", "r289-wide32", "r289-halfmu")


def base_case(name):
    if name in RELEASES[:-1]:
        return name
    if name == "wide32":
        return "r289-wide32"
    return "r289-disk32" if name == "r289-halfmu" else f"r289-disk{CASES[name][0]}"


def pack(root, dest):
    with ZipFile(dest, "x", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for name in (*RELEASES, *CASES):
            directory = root/name
            for file in ("initial.json", "wave.cfg", "solver.log", "history_00001.csv", "resources.txt"):
                archive.write(directory/file, f"{name}/{file}")
            b = base_case(name)
            if name == b:
                archive.write(directory/"state_00000.dat", f"{name}/state_00000.dat")
            base = read_restart(root/b/"state_00000.dat")
            for path in sorted(directory.glob("state_*.dat")):
                if path.stem == "state_00000":
                    continue
                final = read_restart(path)
                fields = {k: final[k].view("<u8") ^ base[k].view("<u8") for k in FIELDS[2:]}
                if name in RELEASES:
                    for k in ("Pressure", *("Residual_"+v for v in FIELDS[2:])):
                        fields[k] = final[k]
                buf = io.BytesIO()
                np.savez(buf, **fields)
                archive.writestr(f"{name}/{path.stem}.npz", buf.getvalue())


def unpack(src, root):
    root.mkdir(exist_ok=False, parents=True)
    with ZipFile(src) as archive:
        for name in (*RELEASES, *CASES):
            directory = root/name
            directory.mkdir()
            for file in ("initial.json", "wave.cfg", "solver.log", "history_00001.csv", "resources.txt"):
                (directory/file).write_bytes(archive.read(f"{name}/{file}"))
            (directory/"state_00000.dat").write_bytes(archive.read(f"{base_case(name)}/state_00000.dat"))
            base = read_restart(directory/"state_00000.dat")
            for path in archive.namelist():
                key = Path(path)
                if key.parent.name != name or key.suffix != ".npz":
                    continue
                with np.load(io.BytesIO(archive.read(path)), allow_pickle=False) as fields:
                    data = dict(x=base["x"], y=base["y"])
                    for k, values in fields.items():
                        data[k] = ((values ^ base[k].view("<u8")).view("<f8")
                                   if k in FIELDS[2:] else values)
                with (directory/key.with_suffix(".dat").name).open("xb") as f:
                    f.write(struct.pack("<5i", MAGIC, len(data), len(base["x"]), 8, 0))
                    for k in data:
                        f.write(k.encode().ljust(33, b"\0"))
                    np.column_stack(list(data.values())).astype("<f8").tofile(f)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=("pack", "unpack"))
    ap.add_argument("source", type=Path)
    ap.add_argument("destination", type=Path)
    args = ap.parse_args()
    (pack if args.mode == "pack" else unpack)(args.source, args.destination)
