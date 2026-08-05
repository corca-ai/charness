from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_REF = ROOT / "skills/public/setup/references/hook-failure-visibility.md"
PLUGIN_REF = ROOT / "plugins/charness/skills/setup/references/hook-failure-visibility.md"
SOURCE_SKILL = ROOT / "skills/public/setup/SKILL.md"
PLUGIN_SKILL = ROOT / "plugins/charness/skills/setup/SKILL.md"
SOURCE_SEAMS = ROOT / "skills/public/setup/references/bootstrap-seams.md"
PLUGIN_SEAMS = ROOT / "plugins/charness/skills/setup/references/bootstrap-seams.md"


def test_hook_failure_guidance_is_mirrored_and_names_the_contract() -> None:
    source = SOURCE_REF.read_text(encoding="utf-8")
    assert PLUGIN_REF.read_text(encoding="utf-8") == source
    assert "pre-commit" in source and "pre-push" in source
    for marker in (
        "pre-commit.commands.<id>",
        "pre-push.commands.<id>",
        "fail_text",
        "logs/pre-push-quality-failure.log",
        "provision a stable stage-specific log directory before the hook runs",
        "fail_text` is self-contained",
        "send the operator to normal output",
        "truncation can hide",
        "final visible ordering as a consumer acceptance check",
        "Do not pipe a state-changing hook or gate through `tail`, `head`",
        "pipefail",
    ):
        assert marker in source


def test_setup_routes_detected_hook_manager_to_failure_guidance() -> None:
    setup_skill = SOURCE_SKILL.read_text(encoding="utf-8")
    bootstrap_seams = SOURCE_SEAMS.read_text(encoding="utf-8")
    assert PLUGIN_SKILL.read_text(encoding="utf-8") == setup_skill
    assert PLUGIN_SEAMS.read_text(encoding="utf-8") == bootstrap_seams
    assert "detected Lefthook configuration" in setup_skill
    assert "## Hook Failure Visibility" in bootstrap_seams
    assert "Charness's worktree adapter `prepare.commands`" in bootstrap_seams
