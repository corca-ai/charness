"""`current_release` refuses an unspeakable adapter version instead of answering
"which package is this release, and where does it live" with a charness guess.

Measured on the real CLI before the repair: a repo declaring `package_id: acme-harness`,
`packaging_manifest_path: vendor/mypkg/manifest.json` and `materialized_plugin_root:
vendor/mypkg` under a refused version got back a `package_id` inferred from its own
directory name and two paths under `packaging/` and `plugins/` that do not exist — at
exit 0, with `valid: false` printed in the same payload and acted on by nothing.

Echoing the flag and using the defaults anyway is the shape the census's
`safe-checks-errors` boundary turns on: a read is not a check.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

from .support import ROOT

SCRIPT = ROOT / "skills" / "public" / "release" / "scripts" / "current_release.py"
DECLARED = (
    "package_id: acme-harness\n"
    "packaging_manifest_path: vendor/mypkg/manifest.json\n"
    "materialized_plugin_root: vendor/mypkg\n"
)


def _repo(tmp_path: Path, adapter: str | None) -> Path:
    repo = tmp_path / "repo"
    (repo / "vendor" / "mypkg" / ".claude-plugin").mkdir(parents=True)
    (repo / "vendor" / "mypkg" / "manifest.json").write_text('{"version": "7.7.7"}\n', encoding="utf-8")
    (repo / "vendor" / "mypkg" / ".claude-plugin" / "plugin.json").write_text(
        '{"version": "7.7.7"}\n', encoding="utf-8"
    )
    if adapter is not None:
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / "release-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _run(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo)], capture_output=True, text=True
    )


def test_an_unspeakable_version_refuses_rather_than_guessing_the_package(tmp_path: Path) -> None:
    result = _run(_repo(tmp_path, "version: 9\n" + DECLARED))
    assert result.returncode == 1, result.stdout
    assert "does not speak" in result.stderr
    # The defaults must not reach stdout at all: a reader who sees a package id believes it.
    assert "package_id" not in result.stdout


def test_a_speakable_version_reports_what_the_repo_declared(tmp_path: Path) -> None:
    result = _run(_repo(tmp_path, "version: 1\n" + DECLARED))
    assert result.returncode == 0, result.stderr
    assert "package_id: acme-harness" in result.stdout
    assert "vendor/mypkg" in result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["versioned_surfaces"] == [
        "packaging_manifest", "claude_plugin", "codex_plugin", "claude_marketplace_version"
    ]
    assert payload["presence_surfaces"] == ["codex_marketplace_source_path"]


def test_no_adapter_at_all_is_not_a_refusal(tmp_path: Path) -> None:
    # The opt-in design survives. A repo that declared nothing is not a repo whose
    # declaration could not be read.
    result = _run(_repo(tmp_path, None))
    assert result.returncode == 0, result.stderr
    assert "package_id:" in result.stdout
