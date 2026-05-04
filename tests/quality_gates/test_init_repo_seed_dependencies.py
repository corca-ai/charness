from __future__ import annotations

import json
import os
from pathlib import Path

from .support import run_script

SCRIPT = "skills/public/init-repo/scripts/seed_dependencies.py"


def _read_deps(repo: Path) -> dict:
    return json.loads((repo / "integrations" / "tools" / "dependencies.json").read_text(encoding="utf-8"))


def test_seed_dependencies_creates_file_with_explicit_tool_ids(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--tool-id",
        "tokei",
        "--tool-id",
        "ruff",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "seeded"
    assert payload["tool_dependencies"] == ["ruff", "tokei"]
    assert _read_deps(repo) == {"schema_version": 1, "tool_dependencies": ["ruff", "tokei"]}
    schema_text = (repo / "integrations" / "tools" / "dependencies.schema.json").read_text(encoding="utf-8")
    assert "tool_dependencies" in schema_text


def test_seed_dependencies_from_recommendations_includes_charness_tools(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    env = os.environ.copy()
    env.pop("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", None)

    result = run_script(
        SCRIPT, "--repo-root", str(repo), "--from-recommendations", "--json", env=env
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "seeded"
    deps = payload["tool_dependencies"]
    for expected in ("tokei", "ruff", "vulture"):
        assert expected in deps, f"missing {expected} in {deps}"


def test_seed_dependencies_refuses_to_overwrite_without_force(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    first = run_script(SCRIPT, "--repo-root", str(repo), "--tool-id", "tokei")
    assert first.returncode == 0, first.stderr

    second = run_script(SCRIPT, "--repo-root", str(repo), "--tool-id", "ruff", "--json")

    assert second.returncode == 1
    payload = json.loads(second.stdout)
    assert payload["status"] == "skipped"
    assert "force" in payload["reason"]
    assert _read_deps(repo)["tool_dependencies"] == ["tokei"]


def test_seed_dependencies_force_overwrite_replaces_list(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    run_script(SCRIPT, "--repo-root", str(repo), "--tool-id", "tokei")

    overwrite = run_script(
        SCRIPT, "--repo-root", str(repo), "--tool-id", "ruff", "--force", "--json"
    )

    assert overwrite.returncode == 0, overwrite.stderr
    payload = json.loads(overwrite.stdout)
    assert payload["tool_dependencies"] == ["ruff"]
    assert _read_deps(repo)["tool_dependencies"] == ["ruff"]


def test_seed_dependencies_rejects_combined_explicit_and_recommendations(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--tool-id",
        "tokei",
        "--from-recommendations",
    )

    assert result.returncode != 0
    assert "not both" in (result.stdout + result.stderr)
