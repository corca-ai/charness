from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path

from tests.quality_gates.support import run_script, write_issue_adapter_with_backend

SCRIPT = "skills/public/issue/scripts/issue_tool.py"
VERIFY_MODULE_PATH = Path(__file__).resolve().parents[2] / "skills" / "public" / "issue" / "scripts" / "issue_verify_closeout.py"


def _load_verify_module():
    spec = importlib.util.spec_from_file_location("issue_verify_closeout_test", VERIFY_MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    return "\n\n".join(parts)


def test_issue_verify_closeout_rejects_missing_direct_commit_close_keyword(tmp_path: Path) -> None:
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Resolved work without an auto-close carrier."))

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
    assert payload["missing_close_keywords"] == [42]
    assert payload["missing_fields"] == []


def test_issue_verify_closeout_accepts_direct_commit_carrier_without_final_state(tmp_path: Path) -> None:
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close #42."))

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
    assert payload["status"] == "carrier_verified"
    assert payload["verified_state"] == []


def test_issue_verify_closeout_uses_github_keyword_boundaries(tmp_path: Path) -> None:
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close #420."))

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
    assert payload["missing_close_keywords"] == [42]


def test_issue_verify_closeout_rejects_wrong_repo_qualified_keyword(tmp_path: Path) -> None:
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close corca-ai/other#42."))

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
    assert payload["missing_close_keywords"] == [42]


def test_issue_verify_closeout_accepts_matching_repo_qualified_keyword(tmp_path: Path) -> None:
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close corca-ai/charness#42."))

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
    assert payload["status"] == "carrier_verified"


def test_issue_verify_closeout_accepts_pr_body_carrier(tmp_path: Path) -> None:
    body = tmp_path / "pr-body.md"
    body.write_text(_bug_closeout_body(close_line="Resolves #42."), encoding="utf-8")

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
        "pr-body",
        "--body-file",
        str(body),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "carrier_verified"


def test_issue_verify_closeout_rejects_empty_bug_sibling_proof(tmp_path: Path) -> None:
    _seed_commit(
        tmp_path,
        "\n\n".join(
            [
                "Close #42.",
                "JTBD: resolve GitHub issues end-to-end.",
                "Root cause: the issue closeout carrier was prose-only.",
                "Debug artifact: charness-artifacts/debug/latest.md.",
                "Siblings: same nearby file.",
                "Prevention: verify-closeout blocks missing carriers.",
            ]
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
    assert "siblings_decision_and_proof" in payload["missing_fields"]


def test_issue_verify_closeout_requires_manual_fallback_reason(tmp_path: Path) -> None:
    body = tmp_path / "closeout.md"
    body.write_text(_bug_closeout_body(close_line="Manual close comment."), encoding="utf-8")

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
        "manual-fallback",
        "--body-file",
        str(body),
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
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
    verify_module = _load_verify_module()

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
    log = tmp_path / "ceal-log.json"
    fake = bin_dir / "ceal"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, os, sys",
                "from pathlib import Path",
                "log = Path(os.environ['CEAL_LOG'])",
                "entries = json.loads(log.read_text()) if log.exists() else []",
                "entries.append(sys.argv[1:])",
                "log.write_text(json.dumps(entries))",
                "if 'view' in sys.argv:",
                "    print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42', 'comments': [{'body': os.environ['COMMENT_BODY']}]}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    write_issue_adapter_with_backend(tmp_path, backend_id="ceal-github", binary="ceal")
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
        _bug_closeout_body(close_line="Manual close comment.")
        + "\nManual close reason: auto-close failed after remote verification.\n"
    )
    body.write_text(body_text, encoding="utf-8")

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
        "manual-fallback",
        "--body-file",
        str(body),
        "--manual-fallback-reason",
        "auto-close-failed-after-remote-verification",
        "--expect-state",
        "CLOSED",
        env={
            **os.environ,
            "PATH": f"{bin_dir}:/usr/bin:/bin",
            "CEAL_LOG": str(log),
            "COMMENT_BODY": body_text,
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "verified"
    assert payload["verified_state"][0]["state"] == "CLOSED"
    entries = json.loads(log.read_text(encoding="utf-8"))
    assert ["github", "issue", "view", "-R", "corca-ai/charness", "42", "--json", "number,state,url,comments"] in entries


def test_issue_verify_closeout_rejects_adapter_view_without_target_placeholders(tmp_path: Path) -> None:
    write_issue_adapter_with_backend(tmp_path, backend_id="ceal-github", binary="ceal")
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
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close #42."))

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
        env={**os.environ, "PATH": "/usr/bin:/bin"},
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert "missing required placeholders" in payload["error"]
    assert "repo" in payload["error"]
    assert "number" in payload["error"]


def test_issue_verify_closeout_uses_default_gh_comments_for_manual_fallback(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    fake = bin_dir / "gh"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, os, sys",
                "from pathlib import Path",
                "log = Path(os.environ['GH_LOG'])",
                "entries = json.loads(log.read_text()) if log.exists() else []",
                "entries.append(sys.argv[1:])",
                "log.write_text(json.dumps(entries))",
                "if 'view' in sys.argv:",
                "    print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42', 'comments': [{'body': os.environ['COMMENT_BODY']}]}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    body = tmp_path / "closeout.md"
    body_text = (
        _bug_closeout_body(close_line="Manual close comment.")
        + "\nManual close reason: auto-close failed after remote verification.\n"
    )
    body.write_text(body_text, encoding="utf-8")

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
        "manual-fallback",
        "--body-file",
        str(body),
        "--manual-fallback-reason",
        "auto-close-failed-after-remote-verification",
        "--expect-state",
        "CLOSED",
        env={
            **os.environ,
            "PATH": f"{bin_dir}:/usr/bin:/bin",
            "GH_LOG": str(log),
            "COMMENT_BODY": body_text,
        },
    )

    assert result.returncode == 0, result.stderr
    entries = json.loads(log.read_text(encoding="utf-8"))
    assert ["issue", "view", "--repo", "corca-ai/charness", "42", "--json", "number,state,url,comments"] in entries


def test_issue_verify_closeout_rejects_wrong_issue_number_from_backend(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "gh"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, sys",
                "if 'view' in sys.argv:",
                "    print(json.dumps({'number': 99, 'state': 'CLOSED', 'url': 'https://example.test/99'}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close #42."))

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
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["state_mismatches"][0]["field"] == "number"


def test_issue_verify_closeout_rejects_open_final_state(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "gh"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, sys",
                "if 'view' in sys.argv:",
                "    print(json.dumps({'number': 42, 'state': 'OPEN', 'url': 'https://example.test/42'}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close #42."))

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
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["state_mismatches"][0]["actual"] == "OPEN"


def test_issue_verify_closeout_rejects_unposted_manual_fallback_comment(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "gh"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, sys",
                "if 'view' in sys.argv:",
                "    print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42', 'comments': [{'body': 'different comment'}]}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    body = tmp_path / "closeout.md"
    body.write_text(
        _bug_closeout_body(close_line="Manual close comment.")
        + "\nManual close reason: auto-close failed after remote verification.\n",
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
        "bug",
        "--carrier",
        "manual-fallback",
        "--body-file",
        str(body),
        "--manual-fallback-reason",
        "auto-close-failed-after-remote-verification",
        "--expect-state",
        "CLOSED",
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["manual_comment_missing"] == [42]

