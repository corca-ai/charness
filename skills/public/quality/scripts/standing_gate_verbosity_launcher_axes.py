"""Launcher-level verbosity axes: per-phase signal and the verbose escape hatch.

Split from `standing_gate_verbosity_lib` when the thin `run-quality.sh`
launcher delegated both to the declared-gate engine; the reader that
recognizes that delegation lives here beside the axes it affects.
"""

from __future__ import annotations

import re
from typing import Any

VERBOSE_VAR_RE = re.compile(r"\b[A-Z0-9_]*VERBOSE[A-Z0-9_]*\b")


def _phase_axis(surfaces: list[dict[str, Any]]) -> dict[str, Any]:
    findings = []
    for surface in surfaces:
        if surface["surface_type"] not in {"git_hook", "husky_hook", "shell_script"}:
            continue
        text = surface["text"]
        structured = (
            any(token in text for token in ("elapsed_ms", "format_elapsed", "date +%s%N"))
            and any(token in text for token in ("summary", "PASS", "FAIL", "print_phase_output"))
        ) or "run_quality_engine" in text
        # A thin launcher that execs the declared-gate engine owns no phase output
        # itself; the engine prints per-phase labels, elapsed time, and the summary.
        if structured:
            findings.append(
                {
                    "type": "phase_level_signal",
                    "path": surface["path"],
                    "surface_type": surface["surface_type"],
                    "state": "structured",
                    "suggestion": "",
                }
            )
        elif surface["commands"]:
            findings.append(
                {
                    "type": "phase_level_signal",
                    "path": surface["path"],
                    "surface_type": surface["surface_type"],
                    "state": "minimal",
                    "suggestion": "Print per-phase labels and elapsed time so success answers which gate ran and failure answers where to look first.",
                }
            )
    return {
        "status": "not_applicable"
        if not findings
        else ("healthy" if any(item["state"] == "structured" for item in findings) else "weak"),
        "findings": findings,
    }


def _escape_axis(surfaces: list[dict[str, Any]]) -> dict[str, Any]:
    findings = []
    for surface in surfaces:
        verbose_vars = sorted(set(VERBOSE_VAR_RE.findall(surface["text"])))
        verbose_scripts = sorted(set(surface["metadata"].get("verbose_scripts", [])))
        if verbose_vars or verbose_scripts:
            findings.append(
                {
                    "type": "escape_hatch",
                    "path": surface["path"],
                    "surface_type": surface["surface_type"],
                    "state": "present",
                    "evidence": ", ".join([*verbose_vars, *verbose_scripts]),
                    "suggestion": "",
                }
            )
    if findings:
        return {"status": "healthy", "findings": findings}
    if any(surface["commands"] for surface in surfaces):
        return {
            "status": "missing",
            "findings": [
                {
                    "type": "escape_hatch_missing",
                    "path": "",
                    "surface_type": "standing_gate",
                    "state": "missing",
                    "evidence": "",
                    "suggestion": "Keep a verbose-on-demand seam such as `VERBOSE=1`, `CI=1`, or a sibling `*:verbose` script.",
                }
            ],
        }
    return {"status": "not_applicable", "findings": []}
