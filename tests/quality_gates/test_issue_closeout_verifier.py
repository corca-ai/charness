from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

from tests.quality_gates.issue_closeout_support import (
    SCRIPT,
    bug_closeout_body,
    load_verify_module,
    seed_commit,
)
from tests.quality_gates.support import (
    run_script,
    write_argv_logging_fake,
    write_issue_adapter_with_backend,
)
from tests.quality_gates.seeding_support import (
    environment_with_path,
    verify_closeout_args,
    write_json_executable,
)


def test_issue_verify_closeout_rejects_missing_direct_commit_close_keyword(tmp_path: Path) -> None:
    seed_commit(tmp_path, bug_closeout_body(close_line="Resolved work without an auto-close carrier."))

    result = run_script(SCRIPT, *verify_closeout_args(tmp_path, commit_ref="HEAD"))

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert payload["missing_close_keywords"] == [42]
    assert payload["missing_fields"] == []
    assert payload["confirmation"]["line"] is None


def test_issue_verify_closeout_accepts_direct_commit_carrier_without_final_state(tmp_path: Path) -> None:
    seed_commit(tmp_path, bug_closeout_body(close_line="Close #42."))

    result = run_script(SCRIPT, *verify_closeout_args(tmp_path, commit_ref="HEAD"))

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload["status"] == "carrier_verified"
    assert payload["verified_state"] == []
    assert payload["confirmation"] == {
        "observer": "issue_verify_closeout@gh",
        "channel": "carrier-body-checks",
        "scope": "carrier-checks-only",
        "line": "carrier-checked: issue_verify_closeout@gh via carrier-body-checks (carrier-checks-only)",
    }


def test_issue_verify_closeout_uses_github_keyword_boundaries(tmp_path: Path) -> None:
    seed_commit(tmp_path, bug_closeout_body(close_line="Close #420."))

    result = run_script(SCRIPT, *verify_closeout_args(tmp_path, commit_ref="HEAD"))

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["missing_close_keywords"] == [42]


def test_issue_verify_closeout_rejects_wrong_repo_qualified_keyword(tmp_path: Path) -> None:
    seed_commit(tmp_path, bug_closeout_body(close_line="Close corca-ai/other#42."))

    result = run_script(SCRIPT, *verify_closeout_args(tmp_path, commit_ref="HEAD"))

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["missing_close_keywords"] == [42]


def test_issue_verify_closeout_accepts_matching_repo_qualified_keyword(tmp_path: Path) -> None:
    seed_commit(tmp_path, bug_closeout_body(close_line="Close corca-ai/charness#42."))

    result = run_script(SCRIPT, *verify_closeout_args(tmp_path, commit_ref="HEAD"))

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "carrier_verified"


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


def test_issue_verify_closeout_rejects_open_expected_state(tmp_path: Path) -> None:
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
        "--expect-state",
        "OPEN",
    )

    assert result.returncode == 2
    assert "invalid choice: 'OPEN'" in result.stderr


def test_issue_verify_closeout_function_rejects_open_expected_state(tmp_path: Path) -> None:
    verify_module = load_verify_module()

    try:
        verify_module.verify_closeout(
            repo_root=tmp_path,
            repo="corca-ai/charness",
            numbers=[42],
            classification="bug",
            carrier="direct-commit",
            backend={"id": "gh", "binary": "gh", "commands": None},
            commit_ref="HEAD",
            expect_state="OPEN",
        )
    except RuntimeError as exc:
        assert "requires --expect-state CLOSED" in str(exc)
    else:
        raise AssertionError("expected function-level OPEN verification guard")


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


def test_issue_verify_closeout_rejects_wrong_issue_number_from_backend(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    fake = write_json_executable(
        bin_dir / "gh",
        {"number": 99, "state": "CLOSED", "url": "https://github.com/corca-ai/charness/issues/99"},
    )
    seed_commit(tmp_path, bug_closeout_body(close_line="Close #42."))

    result = run_script(
        SCRIPT,
        *verify_closeout_args(tmp_path, commit_ref="HEAD", expect_state="CLOSED"),
        env=environment_with_path(bin_dir, path_tail="/usr/bin:/bin"),
    )

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["state_mismatches"][0]["field"] == "number"


def test_issue_verify_closeout_rejects_open_final_state(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    fake = write_json_executable(
        bin_dir / "gh",
        {"number": 42, "state": "OPEN", "url": "https://github.com/corca-ai/charness/issues/42"},
    )
    seed_commit(tmp_path, bug_closeout_body(close_line="Close #42."))

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
        "--expect-state",
        "CLOSED",
        env=environment_with_path(bin_dir, path_tail="/usr/bin:/bin"),
    )

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["state_mismatches"][0]["actual"] == "OPEN"


def test_issue_verify_closeout_rejects_unposted_manual_fallback_comment(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    fake = write_json_executable(
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


def test_issue_verify_closeout_accepts_colon_close_keyword_form(tmp_path: Path) -> None:
    """GitHub's documented colon form (`Closes: #42`) must count as a close
    keyword exactly like the plain space form."""
    seed_commit(tmp_path, bug_closeout_body(close_line="Closes: #42."))

    result = run_script(SCRIPT, *verify_closeout_args(tmp_path, commit_ref="HEAD"))

    assert result.returncode == 0, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["missing_close_keywords"] == []


def test_issue_verify_closeout_accepts_single_keyword_comma_list(tmp_path: Path) -> None:
    """A single keyword followed by a comma list (`Close #42, #43.`) must bind
    every listed number, not only the first."""
    seed_commit(
        tmp_path,
        bug_closeout_body(
            close_line="Close #42, #43.",
            critique_line=(
                "Critique #42 #43: blocked synthetic-test-harness: this test does not "
                "spawn a real resolution critique subagent"
            ),
            behavior_line=(
                "Behavior #42 #43: exercised through the shared test fixture "
                "(distinct channel from CLOSED)"
            ),
        ),
    )

    result = run_script(
        SCRIPT,
        *verify_closeout_args(tmp_path, numbers=(42, 43), commit_ref="HEAD"),
    )

    assert result.returncode == 0, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["missing_close_keywords"] == []


def test_issue_verify_closeout_rejects_a_right_number_from_the_wrong_repository(tmp_path: Path) -> None:
    """The other half of an issue's identity, at the boundary where a wrong verdict is final.

    This surface always REQUIRED `{repo}` in its template, so the backend is always told which
    repository to answer about — but being told is not obeying, and a wrong-repo answer carries
    the right number, so the number check above passes it. The repository was already in hand:
    `url` is fetched and reported in both existing mismatch records, and was never read.

    Constructed rather than inferred: this backend returns the asked-for number and the expected
    state, and differs from a correct answer only in the repository its URL names.
    """
    bin_dir = tmp_path / "bin"
    fake = write_json_executable(
        bin_dir / "gh",
        {"number": 42, "state": "CLOSED", "url": "https://github.com/someone-else/charness/issues/42"},
    )
    seed_commit(tmp_path, bug_closeout_body(close_line="Close #42."))

    result = run_script(
        SCRIPT,
        *verify_closeout_args(tmp_path, commit_ref="HEAD", expect_state="CLOSED"),
        env=environment_with_path(bin_dir, path_tail="/usr/bin:/bin"),
    )

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    mismatch = next(m for m in payload["state_mismatches"] if m.get("field") == "repository")
    assert mismatch["expected"] == "corca-ai/charness"
    assert mismatch["actual"] == "someone-else/charness"
    # And the verdict sentence must not be rendered over a refused result.
    assert payload["confirmation"]["line"] is None


def test_issue_verify_closeout_rejects_a_payload_that_names_no_repository(tmp_path: Path) -> None:
    """A missing repository is an unknown target, never a successful readback."""
    bin_dir = tmp_path / "bin"
    fake = write_json_executable(
        bin_dir / "gh",
        {"number": 42, "state": "CLOSED"},
    )
    seed_commit(tmp_path, bug_closeout_body(close_line="Close #42."))

    result = run_script(
        SCRIPT,
        *verify_closeout_args(tmp_path, commit_ref="HEAD", expect_state="CLOSED"),
        env=environment_with_path(bin_dir, path_tail="/usr/bin:/bin"),
    )

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert any(item.get("field") == "repository" for item in payload["state_mismatches"])
    assert payload["status"] == "failed"
