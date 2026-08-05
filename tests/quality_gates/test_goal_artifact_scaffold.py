from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

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


def _write_context_adapter(repo: Path, context_path: str) -> None:
    adapter = repo / ".agents" / "achieve-adapter.yaml"
    adapter.parent.mkdir(parents=True, exist_ok=True)
    adapter.write_text(
        "version: 1\n"
        "scaffold:\n"
        "  execution_efficiency_context_path: "
        f"{context_path!r}\n",
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


def test_default_scaffold_seeds_minimum_closeout_binding_fields(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")

    text = gal.goal_path(tmp_path, "2026-05-27", "g").read_text(encoding="utf-8")
    plan = text[text.index("## Closeout Binding Plan") : text.index("## Off-Goal Findings")]

    for field in gal.CLOSEOUT_PLAN_FIELDS:
        assert field in plan


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


def test_upsert_appends_execution_efficiency_context_pointer_after_frame(tmp_path: Path) -> None:
    context = tmp_path / "docs" / "execution-efficiency.md"
    context.parent.mkdir(parents=True)
    context.write_text("baseline\n", encoding="utf-8")
    _write_context_adapter(tmp_path, "docs/execution-efficiency.md")

    result = gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")

    assert result["action"] == "created"
    text = gal.goal_path(tmp_path, "2026-05-27", "g").read_text(encoding="utf-8")
    frame = text[text.index("## Active Operating Frame") : text.index("## Goal")]
    pointer = "- Execution-efficiency context: read `docs/execution-efficiency.md` before shaping and at resumed-goal pickup."
    assert pointer in frame
    assert frame.index(pointer) > frame.index("- History boundary:")


def test_upsert_keeps_existing_goal_body_byte_identical_when_context_is_added(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")
    path = gal.goal_path(tmp_path, "2026-05-27", "g")
    original = path.read_bytes()
    context = tmp_path / "efficiency.md"
    context.write_text("baseline\n", encoding="utf-8")
    _write_context_adapter(tmp_path, "efficiency.md")

    result = gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="Changed title")

    assert result["action"] == "unchanged"
    assert path.read_bytes() == original


def test_upsert_refuses_invalid_execution_efficiency_context_paths(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-efficiency.md"
    outside.write_text("outside\n", encoding="utf-8")
    cases = {
        "missing.md": "existing regular file",
        "docs": "existing regular file",
        "../outside-efficiency.md": "within the repo",
        str(tmp_path / "absolute.md"): "repo-relative",
    }
    (tmp_path / "docs").mkdir()
    for configured, expected in cases.items():
        _write_context_adapter(tmp_path, configured)
        result = gal.upsert_goal(tmp_path, date="2026-05-27", slug=configured.replace("/", "-"), title="T")
        assert result["action"] == "refused"
        assert any(expected in error for error in result["adapter_errors"])


def test_adapter_example_context_pointer_is_valid_when_uncommented(tmp_path: Path) -> None:
    context = tmp_path / "docs" / "execution-efficiency.md"
    context.parent.mkdir(parents=True)
    context.write_text("baseline\n", encoding="utf-8")
    example = (ROOT / "skills/public/achieve/adapter.example.yaml").read_text(encoding="utf-8")
    enabled = example.replace(
        "# execution_efficiency_context_path: docs/execution-efficiency.md",
        "execution_efficiency_context_path: docs/execution-efficiency.md",
    )
    adapter_path = tmp_path / ".agents" / "achieve-adapter.yaml"
    adapter_path.parent.mkdir(parents=True)
    adapter_path.write_text(enabled, encoding="utf-8")

    adapter = gal._policy.load_adapter(tmp_path)

    assert adapter["valid"] is True
    assert adapter["data"]["scaffold"]["execution_efficiency_context_path"] == (
        "docs/execution-efficiency.md"
    )


@pytest.mark.parametrize(
    ("context_path", "expected"),
    [
        ("", "must not be empty"),
        ("docs/efficiency.md\ncontinued", "single-line repo-relative path"),
        ("docs/efficiency.md\rcontinued", "single-line repo-relative path"),
    ],
)
def test_context_path_rejects_empty_or_multiline_values(
    tmp_path: Path, context_path: str, expected: str
) -> None:
    _validated, errors, _warnings = gal._policy.validate_adapter_data(
        {"scaffold": {"execution_efficiency_context_path": context_path}}, tmp_path
    )

    assert any(expected in error for error in errors)


@pytest.mark.parametrize("error_type", [OSError, RuntimeError])
def test_context_path_reports_resolve_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, error_type: type[Exception]
) -> None:
    target = tmp_path / "efficiency.md"
    target.write_text("baseline\n", encoding="utf-8")
    original_resolve = Path.resolve

    def selective_resolve(path: Path, *, strict: bool = False) -> Path:
        if path == target:
            raise error_type("resolve blocked")
        return original_resolve(path, strict=strict)

    monkeypatch.setattr(Path, "resolve", selective_resolve)
    _validated, errors, _warnings = gal._policy.validate_adapter_data(
        {"scaffold": {"execution_efficiency_context_path": "efficiency.md"}}, tmp_path
    )

    assert any("could not be resolved" in error for error in errors)


def test_upsert_accepts_in_repo_symlink_context_path(tmp_path: Path) -> None:
    target = tmp_path / "efficiency.md"
    target.write_text("baseline\n", encoding="utf-8")
    link = tmp_path / "pointer.md"
    link.symlink_to(target.name)
    _write_context_adapter(tmp_path, "pointer.md")

    result = gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")

    assert result["action"] == "created"


def test_upsert_rejects_symlink_context_path_escaping_repo(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-efficiency.md"
    outside.write_text("outside\n", encoding="utf-8")
    (tmp_path / "pointer.md").symlink_to(outside)
    _write_context_adapter(tmp_path, "pointer.md")

    result = gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")

    assert result["action"] == "refused"
    assert any("within the repo" in error for error in result["adapter_errors"])


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
