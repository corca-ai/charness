from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESOLVE_SKILL_PATH_CMD = ("python3", "skills/public/find-skills/scripts/resolve_skill_path.py")


def _write_installed_skill(root: Path, *parts: str) -> Path:
    skill_md = root.joinpath(*parts)
    skill_md.parent.mkdir(parents=True)
    skill_md.write_text("---\nname: github\ndescription: Test.\n---\n# GitHub\n", encoding="utf-8")
    return skill_md


def _run(tmp_path: Path, *args: str, allow_failure: bool = False) -> dict[str, object]:
    result = subprocess.run(
        [*RESOLVE_SKILL_PATH_CMD, "--repo-root", str(tmp_path / "repo"), "--home", str(tmp_path / "home"), *args],
        cwd=REPO_ROOT,
        check=not allow_failure,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_resolve_skill_path_handles_arbitrary_marketplace_and_plugin(tmp_path: Path) -> None:
    codex_home = tmp_path / "codex"
    stale = codex_home / "plugins/cache/openai-curated/github/cc8b2295/skills/github/SKILL.md"
    newest = _write_installed_skill(
        codex_home,
        "plugins",
        "cache",
        "openai-curated",
        "github",
        "f9c12053",
        "skills",
        "github",
        "SKILL.md",
    )
    payload = _run(
        tmp_path,
        "--codex-home",
        str(codex_home),
        "--skill-id",
        "github",
        "--marketplace",
        "openai-curated",
        "--plugin",
        "github",
        "--reported-path",
        str(stale),
    )
    assert payload["status"] == "stale-reported-path"
    assert payload["marketplace"] == "openai-curated"
    assert payload["plugin"] == "github"
    assert payload["resolved_source"] == "codex-plugin-cache"
    assert payload["resolved_path"] == str(newest.resolve())
    assert any("prefer a stable plugin path" in warning for warning in payload["warnings"])


def test_resolve_skill_path_arbitrary_plugin_missing_returns_missing_status(tmp_path: Path) -> None:
    codex_home = tmp_path / "codex"
    payload = _run(
        tmp_path,
        "--codex-home",
        str(codex_home),
        "--skill-id",
        "github",
        "--marketplace",
        "openai-curated",
        "--plugin",
        "github",
        allow_failure=True,
    )
    assert payload["status"] == "missing"
    assert payload["resolved_path"] is None
