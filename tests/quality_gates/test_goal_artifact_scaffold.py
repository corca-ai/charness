from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_LIB = ROOT / "skills/public/achieve/scripts/goal_artifact_lib.py"
_spec = importlib.util.spec_from_file_location("goal_artifact_lib", _LIB)
gal = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gal)


def _write_adapter(repo: Path, lines: list[str]) -> None:
    adapter = repo / ".agents" / "achieve-adapter.yaml"
    adapter.parent.mkdir(parents=True, exist_ok=True)
    rendered = "\n".join(f"    - {line!r}" for line in lines)
    adapter.write_text(
        f"version: 1\nscaffold:\n  draft_active_frame_lines:\n{rendered}\n",
        encoding="utf-8",
    )


def test_upsert_uses_adapter_draft_active_frame_lines_for_new_artifacts(tmp_path: Path) -> None:
    _write_adapter(
        tmp_path,
        [
            "- Current slice: real draft/backlog awaiting activation.",
            "- Current slice intent: reshape before activation if the boundary changed.",
            "- Next action: activate with `/goal @{goal_rel}` after review.",
        ],
    )

    gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")

    text = gal.goal_path(tmp_path, "2026-05-27", "g").read_text(encoding="utf-8")
    frame = text[text.index("## Active Operating Frame") : text.index("## Goal")]
    assert "real draft/backlog awaiting activation" in frame
    assert "activate with `/goal @charness-artifacts/goals/2026-05-27-g.md` after review" in frame
    assert "Current slice: before activation." not in frame


def test_default_scaffold_names_draft_lifecycle_disposition(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")

    text = gal.goal_path(tmp_path, "2026-05-27", "g").read_text(encoding="utf-8")
    frame = text[text.index("## Active Operating Frame") : text.index("## Goal")]

    assert "- Current slice: real draft/backlog awaiting activation." in frame
    assert "reshape before\n  activating if the acceptance boundary has changed" in frame
    assert "after confirming the draft is\n  still intended" in frame
    assert "Current slice: before activation." not in frame


def test_upsert_keeps_existing_adapter_scaffold_body_idempotent(tmp_path: Path) -> None:
    first = gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")
    assert first["action"] == "created"
    path = gal.goal_path(tmp_path, "2026-05-27", "g")
    original = path.read_text(encoding="utf-8")

    _write_adapter(tmp_path, ["- Current slice: custom."])

    again = gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="New title", status="active")

    updated = path.read_text(encoding="utf-8")
    assert again["action"] == "updated"
    assert "Status: active" in updated
    assert updated.replace("Status: active", "Status: draft") == original


def test_upsert_refuses_new_artifact_when_scaffold_adapter_is_invalid(tmp_path: Path) -> None:
    _write_adapter(tmp_path, ["## Not a frame line"])

    result = gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")

    assert result["action"] == "refused"
    assert result["adapter_errors"]
    assert not gal.goal_path(tmp_path, "2026-05-27", "g").exists()


def test_existing_artifact_status_update_does_not_revalidate_scaffold_adapter(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")
    _write_adapter(tmp_path, ["## Not a frame line"])

    result = gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T", status="active")

    assert result["action"] == "updated"
    assert "Status: active" in gal.goal_path(tmp_path, "2026-05-27", "g").read_text(encoding="utf-8")
