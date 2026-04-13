from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from .support import make_fake_claude, make_git_repo_copy

PROBE_SKILL_ID = "update-probe-extra"


def test_installed_cli_update_propagates_new_skill_into_exported_plugin_root(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_repo = make_git_repo_copy(source_root)
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    standalone_cli = tmp_path / "bin" / "charness"
    standalone_cli.parent.mkdir(parents=True, exist_ok=True)
    standalone_cli.write_text((source_repo / "charness").read_text(encoding="utf-8"), encoding="utf-8")
    standalone_cli.chmod(0o755)

    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{standalone_cli.parent}:{env.get('PATH', '')}"

    init_result = subprocess.run(
        ["python3", str(standalone_cli), "init", "--home-root", str(home_root), "--repo-url", str(source_repo)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert init_result.returncode == 0, init_result.stderr

    exported_skill = home_root / ".codex" / "plugins" / "charness" / "skills" / PROBE_SKILL_ID / "SKILL.md"
    managed_skill = home_root / ".agents" / "src" / "charness" / "skills" / "public" / PROBE_SKILL_ID / "SKILL.md"
    assert exported_skill.exists() is False
    assert managed_skill.exists() is False

    source_skill_dir = source_repo / "skills" / "public" / PROBE_SKILL_ID
    source_skill_dir.mkdir(parents=True, exist_ok=True)
    source_skill_dir.joinpath("SKILL.md").write_text(
        f"""\
---
name: {PROBE_SKILL_ID}
description: "Use when verifying that charness update propagated a new upstream skill into the installed host-visible plugin surface."
---

# Update Probe

Use this only to confirm that a newly added public skill became visible after
`charness update` refreshed the installed plugin surface.
""",
        encoding="utf-8",
    )

    packaging_path = source_repo / "packaging" / "charness.json"
    packaging = json.loads(packaging_path.read_text(encoding="utf-8"))
    packaging["version"] = "0.0.1-update-probe"
    packaging["codex"]["manifest"]["version"] = "0.0.1-update-probe"
    packaging["claude"]["manifest"]["version"] = "0.0.1-update-probe"
    packaging_path.write_text(json.dumps(packaging, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sync_result = subprocess.run(
        ["python3", "scripts/sync_root_plugin_manifests.py", "--repo-root", "."],
        cwd=source_repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert sync_result.returncode == 0, sync_result.stderr
    subprocess.run(
        [
            "git",
            "add",
            f"skills/public/{PROBE_SKILL_ID}/SKILL.md",
            "packaging/charness.json",
            "plugins/charness",
            ".agents/plugins/marketplace.json",
            ".claude-plugin/marketplace.json",
        ],
        cwd=source_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add update-probe skill"],
        cwd=source_repo,
        check=True,
        capture_output=True,
        text=True,
    )

    installed_cli = home_root / ".local" / "bin" / "charness"
    update_result = subprocess.run(
        ["python3", str(installed_cli), "update", "--home-root", str(home_root), "--json"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert update_result.returncode == 0, update_result.stderr
    payload = json.loads(update_result.stdout)

    manifest = json.loads(
        (home_root / ".codex" / "plugins" / "charness" / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    assert payload["codex_source_version"] == "0.0.1-update-probe"
    assert payload["codex_cache_manifest_version"] in (None, "0.0.1-update-probe")
    assert payload["codex_source_cache_drift"] is False
    assert manifest["version"] == "0.0.1-update-probe"
    assert exported_skill.is_file()
    assert managed_skill.is_file()
