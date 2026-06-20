"""Resolution-critique gate tests for issue verify-closeout.

Split out of `test_issue_closeout_verifier.py` so the carrier/state file stays
under the test-file length cap. Tests here only exercise the
`resolution_critique_check` payload; the adapter-backed final-state cases live
in the sibling file.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tests.quality_gates.support import run_script

SCRIPT = "skills/public/issue/scripts/issue_tool.py"


def _seed_commit(repo: Path, body: str) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Codex Test"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "codex-test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    (repo / "README.md").write_text("# Test\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True, capture_output=True, text=True)
    command = ["git", "commit", "-m", "Resolve issue"]
    for paragraph in body.split("\n\n"):
        command.extend(["-m", paragraph])
    subprocess.run(command, cwd=repo, check=True, capture_output=True, text=True)


def _bug_closeout_body(
    *,
    close_line: str = "Close #42.",
    critique_line: str | None = (
        "Critique: blocked synthetic-test-harness: this test does not spawn "
        "a real resolution critique subagent"
    ),
    behavior_line: str | None = (
        "Behavior #42: behavior test exercises the fix (distinct channel from CLOSED)"
    ),
    provenance_line: str | None = (
        "AI-provenance: agent-drafted; human-audited per the resolution critique"
    ),
) -> str:
    parts = [
        close_line,
        "JTBD: resolve GitHub issues end-to-end.",
        "Root cause: the issue closeout carrier was prose-only.",
        "Debug artifact: charness-artifacts/debug/latest.md.",
        "Siblings: issue_tool finalization | decision: same bug, fix now | proof: static scan.",
        "Prevention: verify-closeout blocks missing carriers.",
    ]
    if critique_line is not None:
        parts.append(critique_line)
    if behavior_line is not None:
        parts.append(behavior_line)
    if provenance_line is not None:
        parts.append(provenance_line)
    return "\n\n".join(parts)


def test_bug_closeout_without_critique_line_is_rejected(tmp_path: Path) -> None:
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close #42.", critique_line=None))

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--commit-ref",
        "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["resolution_critique_check"]["missing"] == ["resolution_critique"]


def test_bug_closeout_with_critique_artifact_path_is_accepted(tmp_path: Path) -> None:
    critique_path = tmp_path / "charness-artifacts/critique/2026-05-28-42.md"
    critique_path.parent.mkdir(parents=True, exist_ok=True)
    critique_path.write_text("# Critique\n\nbody\n", encoding="utf-8")
    _seed_commit(
        tmp_path,
        _bug_closeout_body(
            close_line="Close #42.",
            critique_line="Critique: charness-artifacts/critique/2026-05-28-42.md",
        ),
    )

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--commit-ref",
        "HEAD",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["resolution_critique_check"]["ok"] is True
    via = {entry["via"] for entry in payload["resolution_critique_check"]["satisfied"]}
    assert via == {"evidence"}


def test_bug_bundle_requires_issue_bound_critique_for_each_number(tmp_path: Path) -> None:
    critique_path = tmp_path / "charness-artifacts/critique/2026-06-02-issue-221.md"
    critique_path.parent.mkdir(parents=True, exist_ok=True)
    critique_path.write_text("# Critique\n\nIssue 221 only.\n", encoding="utf-8")
    _seed_commit(
        tmp_path,
        _bug_closeout_body(
            close_line="Close #184.\nClose #221.",
            critique_line="Critique #221: charness-artifacts/critique/2026-06-02-issue-221.md",
        ),
    )

    result = run_script(
        SCRIPT,
        "verify-closeout",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "184",
        "--number",
        "221",
        "--classification",
        "bug",
        "--carrier",
        "direct-commit",
        "--commit-ref",
        "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["resolution_critique_check"]["missing_issue_bindings"] == [184]


def test_bug_bundle_rejects_unqualified_single_issue_critique(tmp_path: Path) -> None:
    critique_path = tmp_path / "charness-artifacts/critique/2026-06-02-issue-221.md"
    critique_path.parent.mkdir(parents=True, exist_ok=True)
    critique_path.write_text("# Critique\n\nIssue 221 only.\n", encoding="utf-8")
    _seed_commit(
        tmp_path,
        _bug_closeout_body(
            close_line="Close #184.\nClose #221.",
            critique_line="Critique: charness-artifacts/critique/2026-06-02-issue-221.md",
        ),
    )

    result = run_script(
        SCRIPT,
        "verify-closeout",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "184",
        "--number",
        "221",
        "--classification",
        "bug",
        "--carrier",
        "direct-commit",
        "--commit-ref",
        "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["resolution_critique_check"]["checks"] == []
    assert payload["resolution_critique_check"]["missing_issue_bindings"] == [184, 221]


def test_bug_bundle_accepts_explicit_multi_issue_critique_binding(tmp_path: Path) -> None:
    critique_path = tmp_path / "charness-artifacts/critique/2026-06-02-184-221.md"
    critique_path.parent.mkdir(parents=True, exist_ok=True)
    critique_path.write_text("# Critique\n\nBundle for #184 and #221.\n", encoding="utf-8")
    _seed_commit(
        tmp_path,
        _bug_closeout_body(
            close_line="Close #184.\nClose #221.",
            critique_line="Critique #184 #221: charness-artifacts/critique/2026-06-02-184-221.md",
            behavior_line=(
                "Behavior #184: behavior test exercises the fix (distinct channel)\n"
                "Behavior #221: fetch/readback of the affected surface (distinct channel)"
            ),
        ),
    )

    result = run_script(
        SCRIPT,
        "verify-closeout",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "184",
        "--number",
        "221",
        "--classification",
        "bug",
        "--carrier",
        "direct-commit",
        "--commit-ref",
        "HEAD",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["resolution_critique_check"]["missing_issue_bindings"] == []


def test_bug_bundle_rejects_multi_issue_critique_artifact_missing_one_binding(tmp_path: Path) -> None:
    critique_path = tmp_path / "charness-artifacts/critique/2026-06-02-issue-184.md"
    critique_path.parent.mkdir(parents=True, exist_ok=True)
    critique_path.write_text("# Critique\n\nIssue 184 only.\n", encoding="utf-8")
    _seed_commit(
        tmp_path,
        _bug_closeout_body(
            close_line="Close #184.\nClose #221.",
            critique_line="Critique #184 #221: charness-artifacts/critique/2026-06-02-issue-184.md",
        ),
    )

    result = run_script(
        SCRIPT,
        "verify-closeout",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "184",
        "--number",
        "221",
        "--classification",
        "bug",
        "--carrier",
        "direct-commit",
        "--commit-ref",
        "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["resolution_critique_check"]["missing_issue_bindings"] == [221]
    assert payload["resolution_critique_check"]["binding_failures"][0]["number"] == 221
    assert payload["resolution_critique_check"]["binding_failures"][0]["path"] == str(critique_path)
    assert "221" in payload["resolution_critique_check"]["binding_failures"][0]["reason"]


def test_bug_closeout_ignores_fenced_critique_line(tmp_path: Path) -> None:
    _seed_commit(
        tmp_path,
        _bug_closeout_body(
            close_line="Close #42.",
            critique_line=(
                "```text\n"
                "Critique: blocked synthetic-test-harness: this fenced example "
                "does not count as live resolution proof\n"
                "```"
            ),
        ),
    )

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--commit-ref",
        "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["resolution_critique_check"]["missing"] == ["resolution_critique"]


def test_bug_closeout_with_blocked_critique_too_terse_is_rejected(tmp_path: Path) -> None:
    _seed_commit(
        tmp_path,
        _bug_closeout_body(
            close_line="Close #42.",
            critique_line="Critique: blocked host-down",
        ),
    )

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--commit-ref",
        "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["resolution_critique_check"]["ok"] is False
    invalid_names = {entry["name"] for entry in payload["resolution_critique_check"]["invalid_skips"]}
    assert "resolution_critique" in invalid_names


def test_question_closeout_does_not_require_critique(tmp_path: Path) -> None:
    body_file = tmp_path / "body.md"
    body_file.write_text(
        "Close #42.\n\nJTBD: answer a clarification question.\n"
        "Recorded decision: keep the current behavior unchanged.\n",
        encoding="utf-8",
    )

    result = run_script(
        SCRIPT,
        "verify-closeout",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--classification",
        "question",
        "--carrier",
        "pr-body",
        "--body-file",
        str(body_file),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["resolution_critique_check"].get("skipped_classification") == "question"


def test_feature_closeout_with_blocked_critique_is_accepted(tmp_path: Path) -> None:
    body_file = tmp_path / "body.md"
    body_file.write_text(
        "Close #42.\n\n"
        "JTBD: ship the requested feature.\n"
        "Boundary: only the additive surface, not a refactor.\n"
        "Resolution brief: see issue body.\n"
        "Implementation: small additive change behind existing seam.\n"
        "Prevention: closeout discipline added.\n"
        "Critique: blocked claude-code-agent-tool-missing in offline session\n"
        "Behavior #42: behavior test exercises the new surface (distinct channel)\n"
        "AI-provenance: agent-drafted; human-audited per the resolution critique\n",
        encoding="utf-8",
    )

    result = run_script(
        SCRIPT,
        "verify-closeout",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--classification",
        "feature",
        "--carrier",
        "pr-body",
        "--body-file",
        str(body_file),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["resolution_critique_check"]["ok"] is True
    assert payload["resolution_critique_check"]["skipped"][0]["name"] == "resolution_critique"
