"""#335: cover the text-mode reporting helpers extracted into
``slice_closeout_reporting`` (the run_slice_closeout module split). The split
shipped these print helpers with their text-mode branches changed-but-uncovered,
which the changed-line mutation gate flagged. One fully-populated payload drives
``print_text`` through every ``_print_*`` helper; the cross-module broad-pytest
policy printer is stubbed so this stays scoped to the reporting module's lines.
"""
from __future__ import annotations

from scripts import slice_closeout_reporting as reporting


def _full_payload() -> dict:
    return {
        "status": "completed",
        "changed_paths": ["scripts/x.py"],
        "matched_surfaces": [{"surface_id": "repo-python", "description": "repo python"}],
        "unmatched_paths": ["docs/loose.md"],
        "cautilus_plan": {
            "run_mode": "evaluate",
            "next_action": "evaluate skill-experiment",
            "required": True,
            "proof_kinds": ["skill-experiment"],
            "changed_public_skills": ["quality"],
            "scenario_registry_review_required": True,
            "notes": ["a note"],
            "skill_validation_recommendations": [{"skill_id": "quality", "validation_tier": "tier-2"}],
            "recommended_followups": ["wire a fixture"],
        },
        "risk_interrupt_plan": {
            "status": "interrupt",
            "artifact_path": "charness-artifacts/debug/latest.md",
            "interrupt_id": "seam-x",
            "handoff_artifact": "charness-artifacts/spec/x.md",
            "chosen_next_step": "spec",
            "impl_status": "blocked",
            "next_action": "design the seam",
            "reasons": ["host-disproves-local"],
        },
        "headroom": [
            {"path": "scripts/x.py", "lines": 470, "limit": 480, "headroom": 10, "near_limit": True},
            {"path": "scripts/y.py", "lines": 10, "limit": 480, "headroom": 470, "near_limit": False},
        ],
        "usage_episode": {
            "status": "recorded",
            "records_path": "charness-artifacts/usage/x.jsonl",
            "episode_id": "ep-1",
            "error": "none-but-shown",
        },
        "executed_commands": [
            {"phase": "verify", "command": "pytest -q", "returncode": 0, "stdout": "", "stderr": ""},
            {"phase": "verify", "command": "ruff check", "returncode": 1, "stdout": "bad out", "stderr": "bad err\n"},
        ],
    }


def test_print_text_drives_every_reporting_helper(monkeypatch, capsys) -> None:
    monkeypatch.setattr(reporting, "print_broad_pytest_policy", lambda payload: None)
    reporting.print_text(_full_payload())
    out = capsys.readouterr().out

    # status + lists
    assert "Closeout status: completed" in out
    assert "Changed paths:" in out and "- scripts/x.py" in out
    assert "Matched surfaces:" in out and "repo-python: repo python" in out
    assert "Unmatched paths:" in out and "- docs/loose.md" in out
    # cautilus plan (visible work)
    assert "Cautilus proof:" in out
    assert "- run_mode: evaluate" in out
    assert "- proof_kinds: skill-experiment" in out
    assert "- next_action: evaluate skill-experiment" in out
    assert "- changed_public_skills: quality" in out
    assert "- scenario_registry_review_required: true" in out
    assert "- note: a note" in out
    assert "- skill_review: quality (tier-2)" in out
    assert "- followup: wire a fixture" in out
    # risk interrupt
    assert "Risk interrupt:" in out
    assert "- status: interrupt" in out
    assert "- handoff_artifact: charness-artifacts/spec/x.md" in out
    assert "- reason: host-disproves-local" in out
    # headroom (only the near-limit row)
    assert "WARN: changed files near the length limit" in out
    assert "scripts/x.py: 470/480 code lines (10 left)" in out
    assert "scripts/y.py" not in out
    # executed commands (only the FAIL echoes streams)
    assert "Executed commands:" in out
    assert "[verify] PASS pytest -q" in out
    assert "[verify] FAIL ruff check" in out
    assert "bad out" in out and "bad err" in out
    # usage episode
    assert "Usage episode:" in out
    assert "- status: recorded" in out
    assert "- records_path: charness-artifacts/usage/x.jsonl" in out
    assert "- episode_id: ep-1" in out
    assert "- error: none-but-shown" in out


def test_print_text_omits_optional_blocks_when_absent(monkeypatch, capsys) -> None:
    # the not-applicable / empty arms: no cautilus (no visible work), risk
    # interrupt not-applicable, no headroom/usage/executed.
    monkeypatch.setattr(reporting, "print_broad_pytest_policy", lambda payload: None)
    reporting.print_text(
        {
            "status": "completed",
            "changed_paths": [],
            "matched_surfaces": [],
            "unmatched_paths": [],
            "cautilus_plan": {"run_mode": "none", "next_action": "none"},
            "risk_interrupt_plan": {"status": "not-applicable"},
            "headroom": [],
            "usage_episode": None,
            "executed_commands": [],
        }
    )
    out = capsys.readouterr().out
    assert "Cautilus proof:" not in out
    assert "Risk interrupt:" not in out
    assert "WARN: changed files near the length limit" not in out
    assert "Usage episode:" not in out
    assert "Executed commands:" not in out
