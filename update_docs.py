#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
README = ROOT / "README.md"
AGENTS = ROOT / "AGENTS.md"

README_SECTION = """## Two parallel project tracks

This repository now has two related but distinct tracks:

1. **Visualization** — the existing Python/POV-Ray/ffmpeg pipeline for making the
   proposed flow and apparatus understandable in three dimensions.
2. **Physical realizability / boundary control** — a research program asking
   whether physically realizable external actuators and sensors can reproduce
   experimentally meaningful portions of the desired interior dynamics.

The second track must not rely on arbitrary volumetric forcing as the final
experimental mechanism. See [PROJECT_TRACKS.md](PROJECT_TRACKS.md),
[PHYSICAL_REALIZABILITY_PLAN.md](PHYSICAL_REALIZABILITY_PLAN.md), and
[CONTROL_RESEARCH_ROADMAP.md](CONTROL_RESEARCH_ROADMAP.md).

"""

AGENTS_SECTION = """## Physical-realizability research track

The repository also contains a second track concerned with boundary-controlled
physical realizability. Before substantial work on that track, read:

- `PROJECT_TRACKS.md`
- `EXPERIMENT.md`
- `PHYSICAL_REALIZABILITY_PLAN.md`
- `CONTROL_RESEARCH_ROADMAP.md`

Do not silently make research-significant architectural choices involving CFD
solver selection, reduced-state definition, controllability/observability
interpretation, actuator physics, or boundary-condition design. State
assumptions and alternatives for review first.

For the realizability track:

- arbitrary volumetric forcing may define a reference target, but is not the
  final experimental actuation mechanism;
- every proposed actuator should map to plausible hardware;
- every feedback variable should map to a plausible sensor or estimator;
- do not give a controller exact hidden CFD state unavailable experimentally;
- report actuator amplitude, bandwidth, and other physical limits as well as
  tracking error;
- treat a negative or finite-limit result as scientifically useful.

The first control calculation should be a boundary-mode response study, not a
full closed-loop controller: excite physically interpretable normal and
tangential boundary modes, measure the reduced central-flow response, and
analyze reachability/conditioning. Perform the analogous observability study
for pressure/PIV sensing before attempting full trajectory control.
"""

def update_readme():
    text = README.read_text(encoding="utf-8")
    if "## Two parallel project tracks" in text:
        print("README.md: already updated")
        return

    # Prefer inserting immediately before the preview image so existing practical
    # material remains exactly where it was.
    candidates = [
        "![Representative tracer-render preview](preview.png)",
        "## Repository layout",
        "## Recommended environment",
    ]
    for marker in candidates:
        pos = text.find(marker)
        if pos != -1:
            new = text[:pos] + README_SECTION + text[pos:]
            README.write_text(new, encoding="utf-8", newline="\n")
            print(f"README.md: inserted before {marker!r}")
            return

    # Last-resort safe behavior: append rather than overwrite.
    README.write_text(text.rstrip() + "\n\n" + README_SECTION, encoding="utf-8", newline="\n")
    print("README.md: appended section at end (no preferred marker found)")

def update_agents():
    text = AGENTS.read_text(encoding="utf-8")
    if "## Physical-realizability research track" in text:
        print("AGENTS.md: already updated")
        return
    AGENTS.write_text(text.rstrip() + "\n\n" + AGENTS_SECTION + "\n",
                      encoding="utf-8", newline="\n")
    print("AGENTS.md: appended research-track guidance")

def main():
    for p in (README, AGENTS):
        if not p.exists():
            raise SystemExit(f"Missing {p.name}; run from repository root.")
    update_readme()
    update_agents()
    print("\nReview with:\n  git diff -- README.md AGENTS.md\n  git status")

if __name__ == "__main__":
    main()
