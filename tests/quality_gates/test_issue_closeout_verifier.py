from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import yaml

from tests.quality_gates.issue_closeout_support import (
    SCRIPT,
    bug_closeout_body,
    load_verify_module,
    seed_commit,
)
from tests.quality_gates.seeding_support import (
    environment_with_path,
    verify_closeout_args,
    write_json_executable,
)
from tests.quality_gates.support import (
    run_script,
    write_argv_logging_fake,
    write_issue_adapter_with_backend,
)


def _close_body(close_line: str, numbers: tuple[int, ...]) -> str:
    if numbers == (42,):
        return bug_closeout_body(close_line=close_line)
    tags = " ".join(f"#{number}" for number in numbers)
    return bug_closeout_body(
        close_line=close_line,
        critique_line=(
            f"Critique {tags}: blocked synthetic-test-harness: this test does not "
            "spawn a real resolution critique subagent"
        ),
        behavior_line=(
            f"Behavior {tags}: exercised through the shared test fixture "
            "(distinct channel from CLOSED)"
        ),
    )


def test_direct_commit_close_keyword_grammar() -> None:
    missing_keywords = load_verify_module()._missing_close_keywords
    repo = "corca-ai/charness"
    cases = (
        ("Resolved work without an auto-close carrier.", (42,), [42]),
        ("Close #420.", (42,), [42]),
        ("Close corca-ai/other#42.", (42,), [42]),
        ("Close #42.", (42,), []),
        ("Close corca-ai/charness#42.", (42,), []),
        ("Closes: #42.", (42,), []),
        ("Close #42, #43.", (42, 43), []),
    )
    for close_line, numbers, missing in cases:
        body = _close_body(close_line, numbers)
        assert missing_keywords(body, list(numbers), repo) == missing, close_line


def test_issue_verify_closeout_accepts_pr_body_carrier(tmp_path: Path) -> None:
    body = tmp_path / "pr-body.md"
    body.write_text(bug_closeout_body(close_line="Resolves #42."), encoding="utf-8")

    result = run_script(
        SCRIPT,
        *verify_closeout_args(tmp_path, carrier="pr-body", body_file=body),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "carrier_verified"


def test_issue_verify_closeout_rejects_empty_bug_sibling_proof(tmp_path: Path) -> None:
    seed_commit(
        tmp_path,
        "\n\n".join(
            [
                "Close #42.",
                "JTBD: resolve GitHub issues end-to-end.",
                "Root cause: the issue closeout carrier was prose-only.",
                "Debug artifact: charness-artifacts/debug/latest.md.",
                "Siblings: same nearby file.",
                "Prevention: verify-closeout blocks missing carriers.",
                "Behavior #42: behavior test exercises the fix (distinct channel).",
                "AI-provenance: agent-drafted; human-audited per the resolution critique.",
            ]
        ),
    )

    result = run_script(SCRIPT, *verify_closeout_args(tmp_path, commit_ref="HEAD"))

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert "siblings_decision_and_proof" in payload["missing_fields"]


def test_issue_verify_closeout_requires_manual_fallback_reason(tmp_path: Path) -> None:
    body = tmp_path / "closeout.md"
    body.write_text(bug_closeout_body(close_line="Manual close comment."), encoding="utf-8")

    result = run_script(
        SCRIPT,
        *verify_closeout_args(tmp_path, carrier="manual-fallback", body_file=body),
    )

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert "manual-fallback carrier requires --manual-fallback-reason" in payload["error"]


def test_open_is_not_a_valid_expect_state(tmp_path: Path) -> None:
    result = run_script(
        SCRIPT,
        *verify_closeout_args(tmp_path, commit_ref="HEAD", expect_state="OPEN"),
    )
    assert result.returncode == 2
    assert "invalid choice: 'OPEN'" in result.stderr

    with pytest.raises(RuntimeError, match="requires --expect-state CLOSED"):
        load_verify_module().verify_closeout(
            repo_root=tmp_path,
            repo="corca-ai/charness",
            numbers=[42],
            classification="bug",
            carrier="direct-commit",
            backend={"id": "gh", "binary": "gh", "commands": None},
            commit_ref="HEAD",
            expect_state="OPEN",
        )


def test_issue_verify_closeout_uses_adapter_view_for_final_state(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "acme-log.json"
    write_argv_logging_fake(
        bin_dir,
        "acme",
        "ACME_LOG",
        [
            "if 'view' in sys.argv:",
            "    print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://github.com/corca-ai/charness/issues/42', 'comments': [{'body': os.environ['COMMENT_BODY']}]}))",
        ],
    )
    write_issue_adapter_with_backend(tmp_path, backend_id="acme-github", binary="acme")
    adapter_path = tmp_path / ".agents" / "issue-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\n".join(
            [
                "    view:",
                "      - github",
                "      - issue",
                "      - view",
                "      - '-R'",
                "      - '{repo}'",
                "      - '{number}'",
                "      - '--json'",
                "      - '{json_fields}'",
                "",
            ]
        ),
        encoding="utf-8",
    )
    body = tmp_path / "closeout.md"
    body_text = (
        bug_closeout_body(close_line="Manual close comment.")
        + "\nManual close reason: auto-close failed after remote verification.\n"
    )
    body.write_text(body_text, encoding="utf-8")

    result = run_script(
        SCRIPT,
        *verify_closeout_args(
            tmp_path,
            carrier="manual-fallback",
            body_file=body,
            manual_fallback_reason="auto-close-failed-after-remote-verification",
            expect_state="CLOSED",
        ),
        env=environment_with_path(
            bin_dir,
            path_tail="/usr/bin:/bin",
            ACME_LOG=str(log),
            COMMENT_BODY=body_text,
        ),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "verified"
    assert payload["confirmation"] == {
        "observer": "issue_verify_closeout@acme-github",
        "channel": "backend-state-readback",
        "scope": "state-and-carrier-checks-only",
        "line": (
            "confirmed: issue_verify_closeout@acme-github via backend-state-readback "
            "(state-and-carrier-checks-only)"
        ),
    }
    assert payload["verified_state"][0]["state"] == "CLOSED"
    entries = json.loads(log.read_text(encoding="utf-8"))
    assert ["github", "issue", "view", "-R", "corca-ai/charness", "42", "--json", "number,state,url,comments"] in entries


def test_issue_verify_closeout_rejects_adapter_view_without_target_placeholders(tmp_path: Path) -> None:
    write_issue_adapter_with_backend(tmp_path, backend_id="acme-github", binary="acme")
    adapter_path = tmp_path / ".agents" / "issue-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\n".join(
            [
                "    view:",
                "      - github",
                "      - issue",
                "      - view",
                "      - '--json'",
                "      - '{json_fields}'",
                "",
            ]
        ),
        encoding="utf-8",
    )
    seed_commit(tmp_path, bug_closeout_body(close_line="Close #42."))

    result = run_script(
        SCRIPT,
        *verify_closeout_args(tmp_path, commit_ref="HEAD", expect_state="CLOSED"),
        env=environment_with_path(Path("/usr/bin"), base=os.environ, path_tail="/bin"),
    )

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert "missing required placeholders" in payload["error"]
    assert "repo" in payload["error"]
    assert "number" in payload["error"]


def test_issue_verify_closeout_uses_default_gh_comments_for_manual_fallback(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    write_argv_logging_fake(
        bin_dir,
        "gh",
        "GH_LOG",
        [
            "if 'view' in sys.argv:",
            "    print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://github.com/corca-ai/charness/issues/42', 'comments': [{'body': os.environ['COMMENT_BODY']}]}))",
        ],
    )
    body = tmp_path / "closeout.md"
    body_text = (
        bug_closeout_body(close_line="Manual close comment.")
        + "\nManual close reason: auto-close failed after remote verification.\n"
    )
    body.write_text(body_text, encoding="utf-8")

    result = run_script(
        SCRIPT,
        *verify_closeout_args(
            tmp_path,
            carrier="manual-fallback",
            body_file=body,
            manual_fallback_reason="auto-close-failed-after-remote-verification",
            expect_state="CLOSED",
        ),
        env=environment_with_path(
            bin_dir,
            path_tail="/usr/bin:/bin",
            GH_LOG=str(log),
            COMMENT_BODY=body_text,
        ),
    )

    assert result.returncode == 0, result.stderr
    entries = json.loads(log.read_text(encoding="utf-8"))
    assert ["issue", "view", "--repo", "corca-ai/charness", "42", "--json", "number,state,url,comments"] in entries


def test_backend_readback_must_name_this_issue() -> None:
    mismatches = load_verify_module()._ISSUE_IDENTITY_MISMATCHES
    repo = "corca-ai/charness"
    cases = (
        (
            {"number": 99, "state": "CLOSED", "url": "https://github.com/corca-ai/charness/issues/99"},
            "number",
            42,
            99,
        ),
        (
            {"number": 42, "state": "CLOSED", "url": "https://github.com/someone-else/charness/issues/42"},
            "repository",
            repo,
            "someone-else/charness",
        ),
        (
            {"number": 42, "state": "CLOSED"},
            "repository",
            repo,
            None,
        ),
    )
    for payload, field, expected, actual in cases:
        found = mismatches(payload, expected_repo=repo, expected_number=42)
        hit = next(item for item in found if item["field"] == field)
        assert hit["expected"] == expected, field
        assert hit["actual"] == actual, field
    open_payload = {
        "number": 42,
        "state": "OPEN",
        "url": "https://github.com/corca-ai/charness/issues/42",
    }
    assert mismatches(open_payload, expected_repo=repo, expected_number=42) == []
    assert str(open_payload["state"]).upper() != "CLOSED"


def test_issue_verify_closeout_rejects_unposted_manual_fallback_comment(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    write_json_executable(
        bin_dir / "gh",
        {
            "number": 42,
            "state": "CLOSED",
            "url": "https://github.com/corca-ai/charness/issues/42",
            "comments": [{"body": "different comment"}],
        },
    )
    body = tmp_path / "closeout.md"
    body.write_text(
        bug_closeout_body(close_line="Manual close comment.")
        + "\nManual close reason: auto-close failed after remote verification.\n",
        encoding="utf-8",
    )

    result = run_script(
        SCRIPT,
        *verify_closeout_args(
            tmp_path,
            carrier="manual-fallback",
            body_file=body,
            manual_fallback_reason="auto-close-failed-after-remote-verification",
            expect_state="CLOSED",
        ),
        env=environment_with_path(bin_dir, path_tail="/usr/bin:/bin"),
    )

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["manual_comment_missing"] == [42]
