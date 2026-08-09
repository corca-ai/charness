from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from .support import ROOT, _load_script_module

LIFECYCLE = _load_script_module(
    "quality_declaration_path_resolution_under_test",
    ROOT / "skills/public/quality/scripts/quality_declaration_lifecycle.py",
)


def _declared_paths(repo: Path, *declarations: str) -> list[dict[str, object]]:
    return LIFECYCLE._declared_skill_paths(
        repo, {"skill_ergonomics_skill_paths": list(declarations)}
    )


def test_declared_paths_do_not_resolve_ignored_repo_skills(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    ignored_skill = repo / "ignored" / "private" / "SKILL.md"
    ignored_skill.parent.mkdir(parents=True)
    ignored_skill.write_text("# ignored\n", encoding="utf-8")
    (repo / ".gitignore").write_text("ignored/\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)

    rows = _declared_paths(
        repo, "ignored/*/SKILL.md", "ignored/private/SKILL.md"
    )

    assert rows == [
        {
            "declaration": "ignored/*/SKILL.md",
            "target_state": "unreachable",
            "resolved_paths": [],
            "routing_state": "routed",
            "packet_id": "skill-ergonomics",
        },
        {
            "declaration": "ignored/private/SKILL.md",
            "target_state": "unreachable",
            "resolved_paths": [],
            "routing_state": "routed",
            "packet_id": "skill-ergonomics",
        },
    ]


@pytest.mark.parametrize(
    "declaration",
    ["../outside/SKILL.md", "../outside/*/SKILL.md", "/tmp/outside/SKILL.md"],
)
def test_declared_paths_refuse_out_of_repo_declarations(
    tmp_path: Path, declaration: str
) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    outside = tmp_path / "outside" / "nested"
    outside.mkdir(parents=True)
    (outside / "SKILL.md").write_text("# outside\n", encoding="utf-8")

    row = _declared_paths(repo, declaration)[0]

    assert row["target_state"] == "unreachable"
    assert row["resolved_paths"] == []
    assert "repo-relative" in row["declaration_error"]


def test_declared_paths_virtualize_configured_external_support(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    support = tmp_path / "support"
    skill = support / "feedback" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("# Feedback\n", encoding="utf-8")
    monkeypatch.setenv("CHARNESS_SUPPORT_DIR", str(support))

    row = _declared_paths(repo, "skills/support/feedback/SKILL.md")[0]

    assert row["target_state"] == "resolved"
    assert row["resolved_paths"] == ["skills/support/feedback/SKILL.md"]
    assert row["target_scope"] == "configured-external-support"
    assert str(tmp_path) not in str(row)


@pytest.mark.parametrize(
    "declaration",
    ["skills/support/private/SKILL.md", "skills/support/*/SKILL.md"],
)
def test_declared_paths_do_not_resolve_ignored_external_support(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, declaration: str
) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    support = tmp_path / "support"
    ignored_skill = support / "private" / "SKILL.md"
    ignored_skill.parent.mkdir(parents=True)
    ignored_skill.write_text("# ignored\n", encoding="utf-8")
    (support / ".gitignore").write_text("private/\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=support, check=True)
    monkeypatch.setenv("CHARNESS_SUPPORT_DIR", str(support))

    row = _declared_paths(repo, declaration)[0]

    assert row["target_state"] == "unreachable"
    assert row["resolved_paths"] == []
    assert row["routing_state"] == "routed"


def test_declared_paths_refuse_external_support_symlink_into_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "app"
    ignored_skill = repo / "ignored" / "private" / "SKILL.md"
    ignored_skill.parent.mkdir(parents=True)
    ignored_skill.write_text("# ignored\n", encoding="utf-8")
    (repo / ".gitignore").write_text("ignored/\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    support = tmp_path / "support"
    alias = support / "alias"
    alias.mkdir(parents=True)
    (alias / "SKILL.md").symlink_to(ignored_skill)
    subprocess.run(["git", "init", "-q"], cwd=support, check=True)
    monkeypatch.setenv("CHARNESS_SUPPORT_DIR", str(support))

    row = _declared_paths(repo, "skills/support/alias/SKILL.md")[0]

    assert row["target_state"] == "unreachable"
    assert row["resolved_paths"] == []
    assert row["routing_state"] == "partial"
    assert row["excluded_match_count"] == 1
    assert "target_scope" not in row


def test_declared_paths_refuse_repo_symlink_escape(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    outside_skill = tmp_path / "outside" / "SKILL.md"
    outside_skill.parent.mkdir()
    outside_skill.write_text("# outside\n", encoding="utf-8")
    alias = repo / "alias"
    alias.mkdir()
    (alias / "SKILL.md").symlink_to(outside_skill)

    row = _declared_paths(repo, "alias/SKILL.md")[0]

    assert row["target_state"] == "unreachable"
    assert row["resolved_paths"] == []
    assert row["routing_state"] == "partial"
    assert row["excluded_match_count"] == 1
