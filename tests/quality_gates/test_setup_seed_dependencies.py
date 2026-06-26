from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

from runtime_bootstrap import import_repo_module

from .support import ROOT, run_script

SCRIPT = "skills/public/setup/scripts/seed_dependencies.py"
_seed_dependencies = import_repo_module(ROOT / SCRIPT, "skills.public.setup.scripts.seed_dependencies")


def run_seed_dependencies(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["seed_dependencies.py", *args])
    try:
        returncode = _seed_dependencies.main()
    except SystemExit as exc:
        if isinstance(exc.code, int):
            returncode = exc.code
        else:
            print(str(exc), file=sys.stderr)
            returncode = 1
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


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


def test_seed_dependencies_from_recommendations_includes_charness_tools(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.delenv("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", raising=False)

    result = run_seed_dependencies(monkeypatch, capsys, "--repo-root", str(repo), "--from-recommendations", "--json")

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


def test_seed_dependencies_force_overwrite_replaces_list(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    run_script(SCRIPT, "--repo-root", str(repo), "--tool-id", "tokei")

    overwrite = run_seed_dependencies(
        monkeypatch, capsys, "--repo-root", str(repo), "--tool-id", "ruff", "--force", "--json"
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
