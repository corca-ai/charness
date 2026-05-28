"""After-phase closeout-evidence parsing and gating for goal artifacts.

Split out of ``goal_artifact_lib.py`` so the artifact module stays under the
single-file line gate; the closeout-evidence contract (Retro + Host log probe
binding to the shared closeout helper) is also a separable concept.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any


def _load_shared_helper():
    """Load the repo-owned shared closeout-evidence helper.

    Resolution walks parent directories until ``scripts/`` is found, so the
    helper stays portable across the working tree and any installed export.
    """
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "scripts" / "check_prescribed_skill_executed_lib.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(
                "check_prescribed_skill_executed_lib", candidate
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scripts/check_prescribed_skill_executed_lib.py not found")


# After-phase evidence names. The achieve closeout requires a checked-in retro
# artifact plus a host-log probe output; either may be skipped with an
# enum-valid reason (see ``check_prescribed_skill_executed_lib.ALLOWED_SKIP_REASONS``).
CLOSEOUT_EVIDENCE_NAMES = ("retro_artifact", "host_log_probe")

_EVIDENCE_LINE = re.compile(
    r"^[\s>*-]*(Retro|Host[- ]log[- ]probe)\s*:\s*(.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)


def _mask_fences(text: str) -> str:
    """Mirror of ``goal_artifact_lib._mask_fences`` so this module stays
    self-contained without a circular sibling import.
    """
    masked: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            masked.append("".join("\n" if char == "\n" else " " for char in line))
            continue
        masked.append("".join("\n" if char == "\n" else " " for char in line) if in_fence else line)
    if in_fence:
        return text
    return "".join(masked)


def _normalize_evidence_name(label: str) -> str:
    label = label.strip().lower()
    if label == "retro":
        return "retro_artifact"
    if re.fullmatch(r"host[- ]log[- ]probe", label):
        return "host_log_probe"
    return label.replace(" ", "_").replace("-", "_")


def parse_closeout_evidence(text: str) -> dict[str, dict[str, str]]:
    """Extract ``Retro:`` and ``Host log probe:`` lines from the goal body.

    Returns ``{name: {"kind": "evidence"|"skip", "value": <path-or-reason>}}``.
    A value that starts with ``skipped:`` (case-insensitive) is treated as a
    skip and the remaining text is the reason; otherwise the value is a
    repo-relative or absolute path to the evidence file.
    """
    masked = _mask_fences(text)
    parsed: dict[str, dict[str, str]] = {}
    for match in _EVIDENCE_LINE.finditer(masked):
        name = _normalize_evidence_name(match.group(1))
        raw_value = match.group(2).strip()
        if not raw_value:
            continue
        skip_match = re.match(r"^skipped\s*:\s*(.+)$", raw_value, re.IGNORECASE)
        if skip_match:
            parsed[name] = {"kind": "skip", "value": skip_match.group(1).strip()}
        else:
            parsed[name] = {"kind": "evidence", "value": raw_value}
    return parsed


def check_complete_evidence(repo_root: Path, text: str) -> dict[str, Any]:
    """Run the shared closeout-evidence helper for an ``achieve`` After-phase.

    The wrapper extracts ``Retro:`` and ``Host log probe:`` lines from the
    goal artifact body and feeds them as evidence/skip arguments to the
    portable ``check`` function. The wrapper supplies the contract
    (CLOSEOUT_EVIDENCE_NAMES); the helper is the gate.
    """
    helper = _load_shared_helper()
    parsed = parse_closeout_evidence(text)
    evidence: dict[str, str] = {}
    skips: dict[str, str] = {}
    for name, payload in parsed.items():
        if payload["kind"] == "evidence":
            evidence[name] = payload["value"]
        else:
            skips[name] = payload["value"]
    return helper.check(
        repo_root=repo_root,
        required=list(CLOSEOUT_EVIDENCE_NAMES),
        evidence=evidence,
        skips=skips,
        kind="achieve-after",
    )
