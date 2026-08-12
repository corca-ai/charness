from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from .support import ROOT, _load_script_module

LIFECYCLE = _load_script_module(
    "quality_declaration_path_resolution_under_test",
    ROOT / "skills/public/quality/scripts/quality_declaration_lifecycle.py",
)
LIFECYCLE_PATH = ROOT / "skills/public/quality/scripts/quality_declaration_lifecycle.py"


def _declared_paths(repo: Path, *declarations: str) -> list[dict[str, object]]:
    return LIFECYCLE._declared_skill_paths(
        repo, {"skill_ergonomics_skill_paths": list(declarations)}
    )


def test_repo_module_bootstraps_repo_import_path_and_fails_loudly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root_text = str(ROOT)
    monkeypatch.setattr(
        LIFECYCLE.sys, "path", [entry for entry in sys.path if entry != root_text]
    )

    module = LIFECYCLE._repo_module("scripts.adapter_lib")

    assert module.__name__ == "scripts.adapter_lib"
    assert LIFECYCLE.sys.path[0] == root_text
    with pytest.raises(ImportError, match="not found from quality skill runtime"):
        LIFECYCLE._repo_module("scripts.quality_module_that_does_not_exist")


def test_declaration_lifecycle_loads_when_importlib_util_was_not_preloaded() -> None:
    source = LIFECYCLE_PATH.read_text(encoding="utf-8")
    program = "\n".join(
        [
            "import importlib",
            "assert not hasattr(importlib, 'util')",
            f"namespace = {{'__file__': {str(LIFECYCLE_PATH)!r}, '__name__': 'isolated_lifecycle'}}",
            f"exec(compile({source!r}, {str(LIFECYCLE_PATH)!r}, 'exec'), namespace)",
        ]
    )

    result = subprocess.run(
        [sys.executable, "-S", "-c", program],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_declaration_helpers_skip_non_values_without_creating_routes(
    tmp_path: Path,
) -> None:
    command_rows, packets = LIFECYCLE._declared_commands(
        {"gate_commands": [None, "", "python3 -m pytest"]}, []
    )
    repo = tmp_path / "app"
    repo.mkdir()

    path_rows = LIFECYCLE._declared_skill_paths(
        repo, {"skill_ergonomics_skill_paths": [None, ""]}
    )

    assert [row["command"] for row in command_rows] == ["python3 -m pytest"]
    assert len(packets) == 1
    assert path_rows == []


def test_declared_paths_report_uninterpretable_patterns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "app"
    repo.mkdir()

    def fail_listing(_repo: Path, _patterns: tuple[str, ...]):
        raise ValueError("bad pattern")

    monkeypatch.setattr(
        LIFECYCLE._REPO_FILE_LISTING, "iter_matching_repo_files", fail_listing
    )

    row = _declared_paths(repo, "skills/*/SKILL.md")[0]

    assert row["target_state"] == "unreachable"
    assert row["resolved_paths"] == []
    assert row["declaration_error"] == "path pattern could not be interpreted"


def test_declared_paths_skip_non_skills_and_count_unresolvable_candidates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    readme = repo / "README.md"
    readme.write_text("# app\n", encoding="utf-8")

    class UnresolvableSkill:
        name = "SKILL.md"

        @staticmethod
        def is_file() -> bool:
            return True

        @staticmethod
        def resolve() -> Path:
            raise OSError("unreadable target")

    monkeypatch.setattr(
        LIFECYCLE._REPO_FILE_LISTING,
        "iter_matching_repo_files",
        lambda _repo, _patterns: [readme, UnresolvableSkill()],
    )

    row = _declared_paths(repo, "**/*")[0]

    assert row["target_state"] == "unreachable"
    assert row["routing_state"] == "partial"
    assert row["excluded_match_count"] == 1


def test_declaration_lifecycle_treats_non_mapping_yaml_as_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    modules = {
        "scripts.quality_adapter_lib": SimpleNamespace(
            load_quality_adapter_permissive=lambda _repo: {
                "found": True,
                "valid": True,
                "path": str(tmp_path / ".agents" / "quality-adapter.yaml"),
                "errors": [],
                "warnings": [],
            }
        ),
        "scripts.adapter_lib": SimpleNamespace(load_yaml_file=lambda _path: []),
        "scripts.quality_bootstrap_detect": SimpleNamespace(
            detect_preset_lineage=lambda _repo: []
        ),
    }
    monkeypatch.setattr(LIFECYCLE, "_repo_module", modules.__getitem__)

    report, packets = LIFECYCLE.build_declaration_lifecycle(
        tmp_path, skills=[], catalog_gates=[]
    )

    assert report["status"] == "configured"
    assert report["commands"] == []
    assert report["surfaces"] == []
    assert report["declared_skill_paths"] == []
    assert packets == []


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
