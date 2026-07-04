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


def test_commit_msg_gate_rejects_bare_close_keyword_with_no_staged_artifact_and_no_carrier(
    tmp_path: Path,
) -> None:
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text("Fixes #123\n", encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed"
    assert payload["artifacts"] == []
    assert payload["bare_close_numbers"] == [123]
    assert payload["reports"][0]["source_artifact"] is None
    assert payload["reports"][0]["numbers"] == [123]
    assert payload["reports"][0]["missing_fields"]

    human_readable = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message))
    assert human_readable.returncode == 1
    assert "bare `#N`" in human_readable.stderr
    assert "close #123` -> `#123`" in human_readable.stderr


def test_commit_msg_gate_allows_bare_issue_reference_without_close_keyword(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text("See #123 for context.\n", encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "not_applicable"


def test_commit_msg_gate_accepts_bare_close_keyword_when_message_carries_full_ledger(
    tmp_path: Path,
) -> None:
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text(_bug_closeout_body(), encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "verified"
    assert payload["artifacts"] == []
    assert payload["bare_close_numbers"] == [42]
    assert payload["reports"][0]["source_artifact"] is None


def test_commit_msg_gate_staged_artifact_behavior_is_unaffected_by_bare_keyword_floor(
    tmp_path: Path,
) -> None:
    _init_repo(tmp_path)
    _stage_issue_closeout(tmp_path, _bug_closeout_body())
    message = tmp_path / "message.txt"
    message.write_text(_bug_closeout_body(), encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "verified"
    assert len(payload["artifacts"]) == 1
    # The commit message's own close keyword already covers #42 via the staged
    # artifact; the bare-keyword trigger must not double-report the same issue.
    assert payload["bare_close_numbers"] == []
    assert len(payload["reports"]) == 1


def test_commit_msg_gate_rejects_bare_colon_close_keyword_with_no_carrier(tmp_path: Path) -> None:
    """GitHub's documented colon form (`Closes: #10`) auto-closes exactly like
    the space form; the scanner must recognize it too."""
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text("Closes: #123\n", encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed"
    assert payload["bare_close_numbers"] == [123]
    assert payload["reports"][0]["numbers"] == [123]


def test_commit_msg_gate_captures_all_numbers_in_single_keyword_comma_list(tmp_path: Path) -> None:
    """A single keyword followed by a comma list (`Closes #10, #11, #12`) must
    bind every listed number, not only the first."""
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text("Closes #10, #11, #12\n", encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed"
    assert payload["bare_close_numbers"] == [10, 11, 12]
    assert payload["reports"][0]["numbers"] == [10, 11, 12]


def test_commit_msg_gate_bare_close_with_answer_substring_defaults_to_bug_not_question(
    tmp_path: Path,
) -> None:
    """Seeded escape: a loose `Answer:` substring previously flipped a bare
    commit's inferred classification to the fully-exempt `question`, silently
    skipping the behavioral-verdict and resolution-critique floors. A bare
    close keyword with no explicit `Classification:` line must default to
    `bug` instead, so those floors stay live."""
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text(
        "\n\n".join(
            [
                "Fixes #123",
                "JTBD: understand whether we should ship this.",
                "Answer: yes, ship it.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed"
    report = payload["reports"][0]
    assert report["source_artifact"] is None
    # `root_cause`/`debug_artifact` only appear in `missing_fields` for `bug`;
    # a `question` classification would never surface them, so their presence
    # proves the bare path did not adopt the loose `Answer:` inference.
    assert "root_cause" in report["missing_fields"]
    assert "debug_artifact" in report["missing_fields"]


def test_commit_msg_gate_staged_artifact_question_inference_is_unaffected(tmp_path: Path) -> None:
    """The bare-commit tightening must not regress the staged-artifact path: an
    artifact whose body infers `question` through the existing loose
    `answer:`/`decision:` heuristic still gets that classification and still
    only needs the question-classification ledger fields — the exemption stays
    available when a staged issue artifact carries the question-classified
    ledger, exactly as before."""
    _init_repo(tmp_path)
    body = "\n\n".join(
        [
            "Close #55.",
            "JTBD: decide whether to ship the change.",
            "Answer: yes, proceed.",
        ]
    )
    _stage_issue_closeout(tmp_path, body)
    message = tmp_path / "message.txt"
    message.write_text(body, encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "verified"
    assert payload["artifacts"][0]["classification"] == "question"
    assert payload["reports"][0]["missing_fields"] == []


def test_commit_msg_gate_surfaces_exemption_advisory_for_question_close(tmp_path: Path) -> None:
    """D36: a `question`/`decision-needed` close self-exempts from the
    behavioral-verdict and resolution-critique floors. On the commit-msg carrier
    that exemption must be SURFACED (non-blocking, exit 0) exactly as it already
    is on `close-with-comment`, so it is never the silent path. Falsifiable pair:
    the exempt close surfaces the advisory here; the bug-close case below does
    not."""
    _init_repo(tmp_path)
    body = "\n\n".join(
        [
            "Close #55.",
            "JTBD: decide whether to ship the change.",
            "Answer: yes, proceed.",
        ]
    )
    _stage_issue_closeout(tmp_path, body)
    message = tmp_path / "message.txt"
    message.write_text(body, encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "verified"
    assert len(payload["review_advisory"]) == 1
    assert "#55" in payload["review_advisory"][0]
    assert "exempts this close" in payload["review_advisory"][0]

    human_readable = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message))
    assert human_readable.returncode == 0, human_readable.stderr
    assert "exempts this close" in human_readable.stderr
    assert "#55" in human_readable.stderr


def test_commit_msg_gate_bug_close_surfaces_no_exemption_advisory(tmp_path: Path) -> None:
    """Falsifiable counterpart: a `bug` close has live behavior to confirm, so it
    is NOT floor-exempt and surfaces no exemption advisory."""
    _init_repo(tmp_path)
    _stage_issue_closeout(tmp_path, _bug_closeout_body())
    message = tmp_path / "message.txt"
    message.write_text(_bug_closeout_body(), encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "verified"
    assert payload["review_advisory"] == []


def test_commit_msg_gate_fenced_close_keyword_in_message_still_triggers_floor(tmp_path: Path) -> None:
    """Regression: GitHub parses the raw commit message for close keywords and
    treats backticks as literal, so a close keyword inside a ``` code fence in
    the COMMIT MESSAGE still auto-closes the issue. The bare-close floor must not
    strip fences from the message — doing so reported `not_applicable` while
    GitHub closed the issue with no floor anywhere (the escape this floor exists
    to close)."""
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text("```\nFixes #123\n```\n", encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--commit-msg-file", str(message), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed"
    assert payload["bare_close_numbers"] == [123]
    assert payload["reports"][0]["source_artifact"] is None


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
