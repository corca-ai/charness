#!/usr/bin/env python3
"""Render the validator-timing classification table from the gate-list data."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from scripts.run_quality_engine_model import load_gate_list
except ImportError:  # run by path from scripts/
    from run_quality_engine_model import load_gate_list

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
DOC_PATH = Path("docs/validator-timing-layers.md")
TABLE_HEADING = "## Classification table"
END_HEADING = "\n## Adding a new timing pull"
BEGIN_MARKER = "<!-- BEGIN GENERATED: validator timing layers -->"
END_MARKER = "<!-- END GENERATED: validator timing layers -->"


def rendered_classification_section(repo_root: Path) -> str:
    gate_list = load_gate_list(repo_root / ".agents" / "quality-gates.yaml")
    grouped: dict[str, list[str]] = {}
    for gate in gate_list.gates:
        timing = gate.timing_layer or "(missing timing_layer)"
        grouped.setdefault(timing, [])
        if gate.label not in grouped[timing]:
            grouped[timing].append(gate.label)
    lines = [
        f"{TABLE_HEADING}\n",
        f"{BEGIN_MARKER}\n",
        "| Check (broad-gate label) | Timing layer |\n",
        "| --- | --- |\n",
    ]
    lines.extend(
        f"| {', '.join(labels)} | {timing} |\n"
        for timing, labels in grouped.items()
    )
    lines.extend([f"{END_MARKER}\n", ""])
    return "".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    path = root / DOC_PATH
    expected = rendered_classification_section(root)
    if args.write:
        current = path.read_text(encoding="utf-8")
        start = current.find(TABLE_HEADING)
        end = current.find(END_HEADING, start + len(TABLE_HEADING)) if start >= 0 else -1
        if start < 0 or end < 0:
            raise SystemExit(f"{DOC_PATH}: cannot locate classification table section")
        path.write_text(current[:start] + expected + current[end + 1 :], encoding="utf-8")
        return 0
    if args.check:
        current = path.read_text(encoding="utf-8") if path.is_file() else ""
        start = current.find(TABLE_HEADING)
        end = current.find(END_HEADING, start + len(TABLE_HEADING)) if start >= 0 else -1
        actual = current[start:end] + "\n" if start >= 0 and end >= 0 else ""
        if actual != expected:
            print(
                f"{DOC_PATH}: classification table is stale; run `python3 scripts/{Path(__file__).name} --write`",
                file=__import__("sys").stderr,
            )
            return 1
        return 0
    print(expected, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
