"""Installed-plugin portability for the shared reviewer boundary assets."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[2]
_export = import_repo_module(__file__, "scripts.export_plugin")


def test_exported_plugin_carries_boundary_helper_and_claude_agent(tmp_path: Path) -> None:
    manifest = _export.load_manifest(ROOT, "charness")
    plugin_root = _export.export_plugin(ROOT, tmp_path / "export", manifest, "claude", False)

    assert (plugin_root / "shared/scripts/reviewer_boundary_fingerprint.py").is_file()
    assert (plugin_root / "agents/bounded-reviewer.md").is_file()
    envelope = (plugin_root / "agents/bounded-reviewer.md").read_text(encoding="utf-8")
    assert "skills/shared/references/" not in envelope
    assert "fresh-eye contract packet" in envelope
    reference = (plugin_root / "shared/references/fresh-eye-subagent-review.md").read_text(
        encoding="utf-8"
    )
    assert '"$SKILL_DIR/../../shared/scripts/reviewer_boundary_fingerprint.py"' in reference
    assert "<repo-root>/skills/shared/scripts/reviewer_boundary_fingerprint.py" not in reference
    assert "host-enforced typed read-only reviewer" in reference
    assert "Untyped reviewer sharing the parent" in reference

    # Exercise the command exactly as a consumer invokes it: cwd is the
    # consuming repository while the helper is resolved from the installed
    # skill directory, never from ``<consumer>/skills/shared``.
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=consumer, check=True)
    (consumer / "README.md").write_text("consumer\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=consumer, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=test@example.com",
            "-c",
            "user.name=test",
            "commit",
            "-qm",
            "seed",
        ],
        cwd=consumer,
        check=True,
    )
    skill_dir = plugin_root / "skills" / "critique"
    result = subprocess.run(
        [
            "sh",
            "-c",
            'export SKILL_DIR="$1"; python3 "$SKILL_DIR/../../shared/scripts/reviewer_boundary_fingerprint.py" snapshot --repo-root "$2"',
            "charness-portability-test",
            str(skill_dir),
            str(consumer),
        ],
        cwd=consumer,
        env=os.environ.copy(),
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_source_reference_does_not_claim_consumer_repo_claude_agent_path() -> None:
    reference = (ROOT / "skills/shared/references/fresh-eye-subagent-review.md").read_text(
        encoding="utf-8"
    )
    assert "<repo-root>/.claude/agents/bounded-reviewer.md" not in reference
    assert "host-enforced typed read-only reviewer" in reference
    assert "isolated worktree" in reference
    assert "fingerprint fallback" in reference
