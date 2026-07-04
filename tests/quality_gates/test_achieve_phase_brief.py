"""Tests for the achieve phase-keyed dispatch demote.

`check_goal_artifact.py` runs at every achieve invocation and already knows the
goal's `status`. It now attaches a declarative `phase_brief` naming exactly
which `references/lifecycle-<phase>.md` file (and its H2 heading) and which
`references/goal-artifact.md` sections are relevant to that status, so
SKILL.md can route a run to the phase-scoped file instead of the full
three-phase contract. This is advisory routing only -- never a blocking floor.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _ROOT / "skills/public/achieve/scripts"
_REFERENCES = _ROOT / "skills/public/achieve/references"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


brief_lib = _load("goal_artifact_phase_brief")
gal = _load("goal_artifact_lib")

_REQUIRED_KEYS = {"phase", "lifecycle_file", "lifecycle_section", "goal_artifact_sections", "note"}


# --- phase_brief() unit coverage ---------------------------------------------


def test_every_valid_status_gets_a_non_none_brief_with_required_keys() -> None:
    for status in gal.VALID_STATUSES:
        brief = brief_lib.phase_brief(status)
        assert brief is not None, status
        assert _REQUIRED_KEYS.issubset(brief.keys()), (status, brief)
        assert brief["phase"] in ("before", "during", "after")
        assert brief["lifecycle_file"].startswith("references/lifecycle-")
        assert (_ROOT / "skills/public/achieve" / brief["lifecycle_file"]).is_file()
        assert brief["lifecycle_section"].startswith("## ")
        assert brief["goal_artifact_sections"], status
        for section in brief["goal_artifact_sections"]:
            assert section.startswith("## ")


def test_unknown_or_none_status_yields_no_brief() -> None:
    assert brief_lib.phase_brief("bogus-status") is None
    assert brief_lib.phase_brief(None) is None
    assert brief_lib.phase_brief("") is None


# --- headings named in PHASE_BRIEFS must be real, unfenced H2s --------------


def _strip_fences(text: str) -> str:
    """Drop fenced code-block content so example ``## `` lines inside ``` ```` ```
    fences (lifecycle.md and goal-artifact.md both show sample sections inside
    fenced markdown examples) are never mistaken for real headings."""
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def _real_h2_lines(text: str) -> list[str]:
    return [line for line in _strip_fences(text).splitlines() if line.startswith("## ")]


def _heading_present(heading: str, real_lines: list[str]) -> bool:
    return any(line == heading for line in real_lines)


def test_lifecycle_sections_are_real_unfenced_h2_headings() -> None:
    # Each brief's `lifecycle_section` heading must be a real H2 inside its own
    # `lifecycle_file` (lifecycle.md was split by phase; the heading no longer
    # lives in one monolithic file).
    for brief in brief_lib.PHASE_BRIEFS.values():
        phase_text = (_ROOT / "skills/public/achieve" / brief["lifecycle_file"]).read_text(
            encoding="utf-8"
        )
        real_lines = _real_h2_lines(phase_text)
        assert _heading_present(brief["lifecycle_section"], real_lines), (
            brief["lifecycle_file"],
            brief["lifecycle_section"],
            real_lines,
        )


def test_goal_artifact_sections_are_real_unfenced_h2_headings() -> None:
    artifact_text = (_REFERENCES / "goal-artifact.md").read_text(encoding="utf-8")
    real_lines = _real_h2_lines(artifact_text)
    named = {
        section
        for brief in brief_lib.PHASE_BRIEFS.values()
        for section in brief["goal_artifact_sections"]
    }
    assert named, "expected at least one goal_artifact_sections entry to check"
    for heading in named:
        assert _heading_present(heading, real_lines), (heading, real_lines)


# --- end-to-end: check_goal_artifact.py CLI surfaces phase_brief -------------


def _run_checker(*extra_args: str) -> dict:
    result = subprocess.run(
        ["python3", str(_SCRIPTS / "check_goal_artifact.py"), *extra_args],
        cwd=_ROOT,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def test_draft_goal_carries_before_phase_brief(tmp_path: Path) -> None:
    date = "2026-07-04"
    slug = "phase-brief-demo"
    created = gal.upsert_goal(tmp_path, date=date, slug=slug, title="Phase brief demo")
    assert created["action"] == "created"
    goal_path = tmp_path / created["path"]
    assert goal_path.exists()

    payload = _run_checker("--repo-root", str(tmp_path), "--slug", slug, "--date", date)

    assert payload["status"] == "draft"
    assert "phase_brief" in payload
    brief = payload["phase_brief"]
    assert brief["phase"] == "before"
    assert brief["lifecycle_section"] == "## Before"
    assert brief["goal_artifact_sections"] == ["## Location", "## Shape", "## Helper Scripts"]


def test_active_goal_carries_during_phase_brief(tmp_path: Path) -> None:
    date = "2026-07-04"
    slug = "phase-brief-active-demo"
    gal.upsert_goal(tmp_path, date=date, slug=slug, title="Phase brief active demo")
    updated = gal.upsert_goal(
        tmp_path, date=date, slug=slug, title="Phase brief active demo", status="active"
    )
    assert updated["status"] == "active"

    payload = _run_checker("--repo-root", str(tmp_path), "--slug", slug, "--date", date)

    assert payload["status"] == "active"
    assert payload["phase_brief"]["phase"] == "during"
    assert payload["phase_brief"]["lifecycle_section"] == "## During"


def test_pursue_ready_mode_also_carries_a_phase_brief(tmp_path: Path) -> None:
    date = "2026-07-04"
    slug = "phase-brief-pursue-demo"
    created = gal.upsert_goal(tmp_path, date=date, slug=slug, title="Phase brief pursue demo")
    goal_path = tmp_path / created["path"]

    payload = _run_checker("--repo-root", str(tmp_path), "--goal-path", str(goal_path), "--pursue-ready")

    # A freshly scaffolded goal is still `draft`, so pursue-ready mode should
    # carry the same Before-phase brief as the full check.
    assert payload["phase_brief"]["phase"] == "before"
