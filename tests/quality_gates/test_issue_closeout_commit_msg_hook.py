from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from tests.quality_gates.support import run_script

SCRIPT = "scripts/check_issue_closeout_commit_msg.py"


def _init_repo(repo: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Codex Test"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "codex-test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _stage_issue_closeout(repo: Path, body: str) -> Path:
    path = repo / "charness-artifacts" / "issue" / "closeout.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    subprocess.run(["git", "add", str(path.relative_to(repo))], cwd=repo, check=True, capture_output=True, text=True)
    return path


def _bug_closeout_body(close_line: str = "Close #42.") -> str:
    return "\n\n".join(
        [
            close_line,
            "JTBD: resolve GitHub issues end-to-end.",
            "Root cause: the issue closeout carrier was prose-only.",
            "Debug artifact: charness-artifacts/debug/latest.md.",
            "Siblings: issue closeout | decision: same carrier bug | proof: commit-msg hook.",
            "Prevention: commit-msg blocks missing closeout carriers.",
            "Critique: blocked synthetic-test-harness: this test does not spawn a real reviewer",
            "Behavior #42: behavior test exercises the fix (distinct channel from CLOSED)",
            "AI-provenance: agent-drafted; human-audited per the resolution critique",
        ]
    )


def test_commit_msg_gate_skips_when_no_issue_closeout_artifact_is_staged(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text("Ordinary commit\n", encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "not_applicable"


def test_commit_msg_gate_rejects_staged_closeout_artifact_without_commit_carrier(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _stage_issue_closeout(tmp_path, _bug_closeout_body())
    message = tmp_path / "message.txt"
    message.write_text("Resolve issue without close keywords\n", encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed"
    assert payload["reports"][0]["missing_close_keywords"] == [42]
    assert set(payload["reports"][0]["missing_fields"]) >= {"root_cause", "debug_artifact", "siblings", "prevention"}


def test_commit_msg_gate_accepts_commit_message_closeout_carrier(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _stage_issue_closeout(tmp_path, _bug_closeout_body())
    message = tmp_path / "message.txt"
    message.write_text(_bug_closeout_body(), encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "verified"
    assert payload["reports"][0]["carrier"] == "commit-msg"
    assert payload["reports"][0]["missing_close_keywords"] == []
    assert payload["reports"][0]["missing_fields"] == []


def test_commit_msg_gate_ignores_close_keywords_inside_staged_code_fence(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _stage_issue_closeout(tmp_path, "```text\nClose #42.\n```\n")
    message = tmp_path / "message.txt"
    message.write_text("Ordinary commit\n", encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "not_applicable"


def test_commit_msg_checker_resolves_exported_plugin_skill_layout(tmp_path: Path) -> None:
    plugin = tmp_path / "plugin"
    shutil.copytree(Path(__file__).resolve().parents[2] / "plugins" / "charness", plugin)
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    _stage_issue_closeout(repo, _bug_closeout_body())
    message = repo / "message.txt"
    message.write_text(_bug_closeout_body(), encoding="utf-8")

    result = subprocess.run(
        [
            "python3",
            str(plugin / "scripts" / "check_issue_closeout_commit_msg.py"),
            "--repo-root",
            str(repo),
            "--commit-msg-file",
            str(message),
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "verified"
