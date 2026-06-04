from __future__ import annotations

import json
from pathlib import Path

from tests.quality_gates.support import run_script

SCRIPT = "skills/public/issue/scripts/issue_tool.py"


def _bug_body(close_line: str = "Close #42.") -> str:
    return "\n\n".join(
        [
            close_line,
            "JTBD: resolve GitHub issues end-to-end.",
            "Root cause: the issue closeout carrier was prose-only.",
            "Debug artifact: cite-only.",
            "Siblings: issue_tool finalization | decision: same bug, fix now | proof: static scan.",
            "Prevention: validate-closeout-draft blocks malformed bodies before mutation.",
            "Critique: blocked synthetic-test-harness: this test does not spawn a real reviewer",
        ]
    )


def test_validate_closeout_draft_accepts_pr_body_before_state_mutation(tmp_path: Path) -> None:
    body = tmp_path / "closeout.md"
    body.write_text(_bug_body(), encoding="utf-8")

    result = run_script(
        SCRIPT,
        "validate-closeout-draft",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--classification",
        "bug",
        "--body-file",
        str(body),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["draft"] is True
    assert payload["status"] == "draft_verified"
    assert payload["verified_state"] == []
    assert payload["publication_status"] == "ready_to_publish"


def test_validate_closeout_draft_accepts_direct_commit_message_before_push(
    tmp_path: Path,
) -> None:
    commit_message = tmp_path / "commit-message.txt"
    commit_message.write_text(_bug_body(), encoding="utf-8")

    result = run_script(
        SCRIPT,
        "validate-closeout-draft",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--classification",
        "bug",
        "--carrier",
        "direct-commit",
        "--commit-message-file",
        str(commit_message),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["carrier"] == "direct-commit"
    assert payload["draft"] is True
    assert payload["status"] == "draft_verified"
    assert payload["publication_status"] == "ready_to_commit_push"
    assert payload["verified_state"] == []
    assert payload["commit_message_file"] == str(commit_message)


def test_validate_closeout_draft_direct_commit_requires_message_file(
    tmp_path: Path,
) -> None:
    result = run_script(
        SCRIPT,
        "validate-closeout-draft",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--classification",
        "bug",
        "--carrier",
        "direct-commit",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert "direct-commit draft requires --commit-message-file" in payload["error"]


def test_validate_closeout_draft_rejects_missing_ledger_before_mutation(tmp_path: Path) -> None:
    body = tmp_path / "closeout.md"
    body.write_text("Close #42.\n\nJTBD: too thin.\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "validate-closeout-draft",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--classification",
        "bug",
        "--body-file",
        str(body),
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "draft_failed"
    assert set(payload["missing_fields"]) >= {"root_cause", "debug_artifact", "siblings", "prevention"}


def test_validate_closeout_draft_accepts_manual_fallback_body(tmp_path: Path) -> None:
    body = tmp_path / "closeout.md"
    body.write_text(
        _bug_body("Manual close comment.")
        + "\n\nManual fallback reason: auto-close unsupported by host backend.\n",
        encoding="utf-8",
    )

    result = run_script(
        SCRIPT,
        "validate-closeout-draft",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--classification",
        "bug",
        "--carrier",
        "manual-fallback",
        "--manual-fallback-reason",
        "auto-close-unsupported",
        "--body-file",
        str(body),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["carrier"] == "manual-fallback"
