from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB_PATH = REPO_ROOT / "scripts/classify_push_diff_lib.py"
CLI_PATH = REPO_ROOT / "scripts/classify_push_diff.py"

_spec = importlib.util.spec_from_file_location("classify_push_diff_lib", LIB_PATH)
lib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lib)


def test_docs_artifact_only_classification() -> None:
    result = lib.classify(
        [
            "docs/handoff.md",
            "charness-artifacts/quality/latest.md",
            "README.md",
        ]
    )
    assert result["classification"] == "docs-artifact-only"
    assert result["unconditional_full_gate_hits"] == []
    assert result["non_allowlist_paths"] == []


def test_empty_diff_is_safe_to_skip() -> None:
    result = lib.classify([])
    assert result["classification"] == "docs-artifact-only"
    assert "no changed paths" in result["reason"]


def test_plugins_path_unconditionally_forces_full_gate() -> None:
    # Stop-condition path: plugins/ unconditionally triggers a full gate,
    # even if every other change is on the docs/artifact allowlist.
    result = lib.classify(
        [
            "docs/handoff.md",
            "plugins/charness/SKILL.md",
            "charness-artifacts/quality/latest.md",
        ]
    )
    assert result["classification"] == "full-gate-required"
    assert "plugins/charness/SKILL.md" in result["unconditional_full_gate_hits"]


def test_claude_plugin_path_unconditionally_forces_full_gate() -> None:
    result = lib.classify(["docs/handoff.md", ".claude-plugin/marketplace.json"])
    assert result["classification"] == "full-gate-required"
    assert ".claude-plugin/marketplace.json" in result["unconditional_full_gate_hits"]


def test_agents_plugin_path_unconditionally_forces_full_gate() -> None:
    result = lib.classify(["charness-artifacts/release/latest.md", ".agents/plugins/marketplace.json"])
    assert result["classification"] == "full-gate-required"
    assert ".agents/plugins/marketplace.json" in result["unconditional_full_gate_hits"]


def test_source_path_forces_full_gate_even_with_docs_changes() -> None:
    result = lib.classify(
        [
            "docs/handoff.md",
            "skills/public/issue/SKILL.md",
        ]
    )
    assert result["classification"] == "full-gate-required"
    assert "skills/public/issue/SKILL.md" in result["full_gate_pattern_hits"]


def test_test_path_forces_full_gate() -> None:
    result = lib.classify(["tests/quality_gates/test_release_publish.py"])
    assert result["classification"] == "full-gate-required"
    assert "tests/quality_gates/test_release_publish.py" in result["full_gate_pattern_hits"]


def test_githooks_path_forces_full_gate() -> None:
    # A change to the hook itself must run the broad gate so the changed
    # hook is validated before any subsequent push silently uses it.
    result = lib.classify([".githooks/pre-push"])
    assert result["classification"] == "full-gate-required"


def test_pyproject_path_forces_full_gate() -> None:
    result = lib.classify(["pyproject.toml"])
    assert result["classification"] == "full-gate-required"


def test_unknown_top_level_path_is_non_allowlist() -> None:
    # A new top-level directory not on either list forces a full gate by
    # default - the allowlist is conservative on purpose.
    result = lib.classify(["new-experiment/foo.txt"])
    assert result["classification"] == "full-gate-required"
    assert "new-experiment/foo.txt" in result["non_allowlist_paths"]


def test_duplicate_paths_are_deduped() -> None:
    result = lib.classify(["docs/handoff.md", "docs/handoff.md", "README.md"])
    assert result["files"] == ["docs/handoff.md", "README.md"]


def test_charness_artifacts_subdirectory_is_allowlisted() -> None:
    # Any path under charness-artifacts/ is on the allowlist - it is durable
    # repo state, not runtime code.
    result = lib.classify(
        [
            "charness-artifacts/goals/2026-05-28-x.md",
            "charness-artifacts/retro/2026-05-28-y.md",
            "charness-artifacts/find-skills/latest.json",
        ]
    )
    assert result["classification"] == "docs-artifact-only"


def test_cli_emits_classification_for_explicit_path_list() -> None:
    process = subprocess.run(
        [sys.executable, str(CLI_PATH), "--repo-root", str(REPO_ROOT), "--paths-stdin"],
        input="docs/handoff.md\nREADME.md\n",
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(process.stdout)
    assert payload["classification"] == "docs-artifact-only"


def test_top_level_dotfile_forces_full_gate() -> None:
    # Slice-7 critique F3: any top-level dotfile/dir is runtime-shaping
    # config and must trip the full gate, not be silently classified as
    # bookkeeping.
    for path in (
        ".gitignore",
        ".gitattributes",
        ".editorconfig",
        ".pre-commit-config.yaml",
        ".vscode/settings.json",
        ".envrc",
        ".python-version",
    ):
        result = lib.classify([path])
        assert result["classification"] == "full-gate-required", path
        assert path in result["full_gate_pattern_hits"], path


def test_cli_emits_full_gate_for_unconditional_path_via_stdin() -> None:
    process = subprocess.run(
        [sys.executable, str(CLI_PATH), "--repo-root", str(REPO_ROOT), "--paths-stdin"],
        input="docs/handoff.md\nplugins/charness/SKILL.md\n",
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(process.stdout)
    assert payload["classification"] == "full-gate-required"
    assert "plugins/charness/SKILL.md" in payload["unconditional_full_gate_hits"]
