#!/usr/bin/env python3
"""Validate saved POV-Ray trajectory includes without executing POV-Ray text."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
import sys
from typing import Iterator


SERIALIZATION_TOLERANCE = 1.0e-9
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_LINE_BYTES = 256 * 1024
FRAME_NAME = re.compile(r"^frame([0-9]+)\.inc$")
NUMBER = r"[+-]?(?:(?:[0-9]+(?:\.[0-9]*)?)|(?:\.[0-9]+))(?:[eE][+-]?[0-9]+)?"
SCALAR = re.compile(rf"^#declare ([A-Za-z][A-Za-z0-9_]*) = ({NUMBER});$")
VECTOR = re.compile(rf"^<({NUMBER}), ({NUMBER}), ({NUMBER})>(,)?$")

REQUIRED_SCALARS = (
    "SimTime",
    "TauRatio",
    "CoreRadius",
    "CoreHalfHeight",
    "ActuatorPhase",
    "NBeads",
)


class CheckError(ValueError):
    """An actionable saved-output validation error."""


@dataclass(frozen=True)
class Frame:
    index: int
    path: Path
    sim_time: float
    tau_ratio: float
    core_radius: float
    core_half_height: float
    actuator_phase: float
    coordinates: tuple[tuple[float, float, float], ...]


def _finite(value: float, label: str, path: Path, line_number: int) -> float:
    if not math.isfinite(value):
        raise CheckError(f"{path.name}:{line_number}: {label} is not finite")
    return value


def _content_lines(path: Path) -> Iterator[tuple[int, str]]:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise CheckError(f"{path.name}: cannot stat file: {exc.strerror or exc}") from exc
    if size > MAX_FILE_BYTES:
        raise CheckError(f"{path.name}: file is larger than {MAX_FILE_BYTES} bytes")
    try:
        with path.open("rb") as source:
            for line_number, raw in enumerate(source, 1):
                if len(raw) > MAX_LINE_BYTES:
                    raise CheckError(
                        f"{path.name}:{line_number}: line is larger than {MAX_LINE_BYTES} bytes"
                    )
                try:
                    line = raw.decode("ascii")
                except UnicodeDecodeError as exc:
                    raise CheckError(f"{path.name}:{line_number}: non-ASCII input") from exc
                yield line_number, line.rstrip("\r\n")
    except OSError as exc:
        raise CheckError(f"{path.name}: cannot read file: {exc.strerror or exc}") from exc


def parse_frame(path: Path, index: int, expected_beads: int) -> Frame:
    scalars: dict[str, float] = {}
    coordinates: list[tuple[float, float, float]] = []
    in_array = False
    closed = False
    for line_number, line in _content_lines(path):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        if closed:
            raise CheckError(f"{path.name}:{line_number}: content after array close")
        if not in_array:
            scalar_match = SCALAR.fullmatch(stripped)
            if scalar_match:
                name, text = scalar_match.groups()
                if name not in REQUIRED_SCALARS:
                    raise CheckError(f"{path.name}:{line_number}: unexpected declaration {name}")
                if name in scalars:
                    raise CheckError(f"{path.name}:{line_number}: duplicate declaration {name}")
                value = float(text)
                scalars[name] = value
                continue
            if stripped == "#declare BeadPos = array[NBeads] {":
                missing = [name for name in REQUIRED_SCALARS if name not in scalars]
                if missing:
                    raise CheckError(
                        f"{path.name}:{line_number}: array starts before declarations {', '.join(missing)}"
                    )
                in_array = True
                continue
            raise CheckError(f"{path.name}:{line_number}: malformed declaration or array start")

        if stripped == "};":
            closed = True
            continue
        vector_match = VECTOR.fullmatch(stripped)
        if not vector_match:
            raise CheckError(f"{path.name}:{line_number}: malformed bead coordinate")
        x_text, y_text, z_text, comma = vector_match.groups()
        if comma is None and len(coordinates) + 1 != expected_beads:
            raise CheckError(f"{path.name}:{line_number}: missing comma before final bead")
        if comma is not None and len(coordinates) + 1 >= expected_beads:
            raise CheckError(f"{path.name}:{line_number}: too many bead coordinates")
        coordinates.append(
            (
                _finite(float(x_text), "x coordinate", path, line_number),
                _finite(float(y_text), "y coordinate", path, line_number),
                _finite(float(z_text), "z coordinate", path, line_number),
            )
        )

    if not in_array or not closed:
        raise CheckError(f"{path.name}: truncated BeadPos array")
    missing = [name for name in REQUIRED_SCALARS if name not in scalars]
    if missing:
        raise CheckError(f"{path.name}: missing declaration(s): {', '.join(missing)}")
    declared_beads = scalars["NBeads"]
    if not declared_beads.is_integer() or declared_beads < 0:
        raise CheckError(f"{path.name}: NBeads must be a nonnegative integer")
    if int(declared_beads) != expected_beads:
        raise CheckError(
            f"{path.name}: NBeads is {int(declared_beads)}, expected {expected_beads}"
        )
    if len(coordinates) != expected_beads:
        raise CheckError(
            f"{path.name}: contains {len(coordinates)} bead coordinates, expected {expected_beads}"
        )
    for name in REQUIRED_SCALARS[:-1]:
        _finite(scalars[name], name, path, 0)
    return Frame(
        index=index,
        path=path,
        sim_time=scalars["SimTime"],
        tau_ratio=scalars["TauRatio"],
        core_radius=scalars["CoreRadius"],
        core_half_height=scalars["CoreHalfHeight"],
        actuator_phase=scalars["ActuatorPhase"],
        coordinates=tuple(coordinates),
    )


def _extrema(frames: tuple[Frame, ...]) -> dict[str, float | None]:
    radii = [math.hypot(x, y) for frame in frames for x, y, _ in frame.coordinates]
    zs = [z for frame in frames for _, _, z in frame.coordinates]
    return {
        "radius_min": min(radii) if radii else None,
        "radius_max": max(radii) if radii else None,
        "z_min": min(zs) if zs else None,
        "z_max": max(zs) if zs else None,
    }


def validate(directory: Path, expected_frames: int, expected_beads: int) -> dict[str, object]:
    if expected_frames < 1:
        raise CheckError("expected frame count must be at least 1")
    if expected_beads < 0:
        raise CheckError("expected bead count must be nonnegative")
    if not directory.is_dir():
        raise CheckError(f"input directory does not exist or is not a directory: {directory}")
    paths: list[tuple[int, Path]] = []
    try:
        entries = directory.iterdir()
    except OSError as exc:
        raise CheckError(f"cannot read input directory {directory}: {exc.strerror or exc}") from exc
    for path in entries:
        match = FRAME_NAME.fullmatch(path.name)
        if match:
            if not path.is_file():
                raise CheckError(f"{path.name}: expected a regular file")
            try:
                index = int(match.group(1))
            except ValueError as exc:
                raise CheckError(f"{path.name}: frame index is too large") from exc
            paths.append((index, path))
            if len(paths) > expected_frames:
                raise CheckError(
                    f"frame inventory has more than the expected {expected_frames} files"
                )
    paths.sort()
    actual_indices = [index for index, _ in paths]
    expected_indices = list(range(1, expected_frames + 1))
    if actual_indices != expected_indices:
        raise CheckError(
            f"frame inventory mismatch: found {actual_indices!r}, expected {expected_indices!r}"
        )
    frames = tuple(parse_frame(path, index, expected_beads) for index, path in paths)
    for previous, current in zip(frames, frames[1:]):
        if not current.sim_time > previous.sim_time:
            raise CheckError(
                f"{current.path.name}: SimTime {current.sim_time:g} is not greater than "
                f"{previous.sim_time:g} in {previous.path.name}"
            )
    for frame in frames:
        for bead_number, (x, y, z) in enumerate(frame.coordinates, 1):
            radius = math.hypot(x, y)
            if radius > 0.92 + SERIALIZATION_TOLERANCE:
                raise CheckError(
                    f"{frame.path.name}: bead {bead_number} radius {radius:.12g} exceeds 0.92"
                )
            if abs(z) > 0.98 + SERIALIZATION_TOLERANCE:
                raise CheckError(
                    f"{frame.path.name}: bead {bead_number} z {z:.12g} exceeds abs(z) 0.98"
                )
    motion_observed = any(
        left != right
        for left, right in zip(frames[0].coordinates, frames[-1].coordinates)
    ) if len(frames) > 1 else False
    motion_status = (
        "one_frame_input" if len(frames) == 1 else
        "motion_observed" if motion_observed else "no_motion_observed"
    )
    return {
        "pass": True,
        "frames_checked": len(frames),
        "beads_per_frame": expected_beads,
        "frame_indices": actual_indices,
        "sim_time_min": frames[0].sim_time,
        "sim_time_max": frames[-1].sim_time,
        "extrema": _extrema(frames),
        "motion_observed": motion_observed,
        "motion_status": motion_status,
        "serialization_tolerance": SERIALIZATION_TOLERANCE,
        "note": "Saved-data check only; this is not a runtime or scientific certificate.",
    }


def _write_report(path: Path, report: dict[str, object], input_paths: set[Path]) -> None:
    try:
        resolved = path.resolve()
    except OSError as exc:
        raise CheckError(f"cannot resolve report path {path}: {exc}") from exc
    if resolved in input_paths:
        raise CheckError(f"refusing to overwrite input file with report: {path}")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8", newline="\n") as target:
            json.dump(report, target, indent=2, sort_keys=True, allow_nan=False)
            target.write("\n")
    except FileExistsError as exc:
        raise CheckError(f"report path already exists; refusing overwrite: {path}") from exc
    except OSError as exc:
        raise CheckError(f"cannot write report {path}: {exc.strerror or exc}") from exc


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="directory containing frameNNNN.inc files")
    parser.add_argument("--frames", type=int, required=True, help="expected number of frames")
    parser.add_argument("--beads", type=int, required=True, help="expected beads per frame")
    parser.add_argument("--json-report", type=Path, help="write a new JSON report at this path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report: dict[str, object]
    try:
        report = validate(args.directory, args.frames, args.beads)
    except CheckError as exc:
        report = {
            "pass": False,
            "frames_checked": 0,
            "beads_per_frame": args.beads,
            "motion_observed": False,
            "motion_status": "invalid_input",
            "error": str(exc),
            "note": "Saved-data check only; this is not a runtime or scientific certificate.",
        }
        print(f"FAIL: {exc}", file=sys.stderr)
        if args.json_report:
            try:
                _write_report(args.json_report, report, set())
            except CheckError as report_error:
                print(f"FAIL: {report_error}", file=sys.stderr)
        return 1
    print(
        f"PASS: checked {report['frames_checked']} frames with "
        f"{report['beads_per_frame']} beads/frame; "
        f"motion: {report['motion_status']}"
    )
    extrema = report["extrema"]
    assert isinstance(extrema, dict)
    print(
        f"  radius {extrema['radius_min']:.12g} .. {extrema['radius_max']:.12g}; "
        f"z {extrema['z_min']:.12g} .. {extrema['z_max']:.12g}"
    )
    if args.json_report:
        try:
            input_paths = {
                path.resolve()
                for path in args.directory.iterdir()
                if FRAME_NAME.fullmatch(path.name) and path.is_file()
            }
            _write_report(args.json_report, report, input_paths)
        except (OSError, CheckError) as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
