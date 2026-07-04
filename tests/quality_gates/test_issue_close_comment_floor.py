from __future__ import annotations

import json
import os
from pathlib import Path

from tests.quality_gates.issue_closeout_support import bug_closeout_body
from tests.quality_gates.support import run_script, write_argv_logging_fake

SCRIPT = "skills/public/issue/scripts/issue_tool.py"


def test_close_with_comment_refuses_silent_body_before_any_gh_call(tmp_path: Path) -> None:
    """Seeded escape: manual close-with-comment previously mutated GitHub on an
    evidence-free body (only `body_file.is_file()` was checked). The rung-1
    presence floor must refuse before the comment/close backend is ever invoked."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    write_argv_logging_fake(
        bin_dir,
        "gh",
        "GH_LOG",
        [
            "if 'comment' in sys.argv: print('commented')",
            "if 'close' in sys.argv: print('closed')",
            "if 'view' in sys.argv: print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42'}))",
        ],
    )
    body = tmp_path / "body.md"
    body.write_text("Body.\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--body-file",
        str(body),
        "--classification",
        "bug",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_LOG": str(log)},
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "rung-1" in payload["error"]
    assert "missing behavioral verdict" in payload["error"]
    assert "missing/invalid resolution-critique evidence" in payload["error"]
    assert not log.exists(), "no gh call should have run before the floor refused"


def test_close_with_comment_proceeds_with_compliant_body(tmp_path: Path) -> None:
    """A body that carries the behavioral verdict and a bound (blocked) critique
    line passes the floor and the mutation proceeds through the backend."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    write_argv_logging_fake(
        bin_dir,
        "gh",
        "GH_LOG",
        [
            "if 'comment' in sys.argv: print('commented')",
            "if 'close' in sys.argv: print('closed')",
            "if 'view' in sys.argv: print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42'}))",
        ],
    )
    body = tmp_path / "body.md"
    body.write_text(bug_closeout_body(), encoding="utf-8")

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--body-file",
        str(body),
        "--classification",
        "bug",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_LOG": str(log)},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["review_advisory"] == []
    entries = json.loads(log.read_text(encoding="utf-8"))
    assert ["issue", "comment", "--repo", "corca-ai/charness", "42", "--body-file", str(body)] in entries
    assert ["issue", "close", "--repo", "corca-ai/charness", "42", "--reason", "completed"] in entries


def test_close_with_comment_question_classification_emits_review_advisory(tmp_path: Path) -> None:
    """`question`/`decision-needed` legitimately skip the behavioral-verdict and
    resolution-critique floors (no live behavior to confirm), but the
    caller-supplied classification is not independently checked. The close
    must still succeed (exit 0, advisory only, never blocks) while surfacing a
    REVIEW line so the bypass is visible rather than silent."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    write_argv_logging_fake(
        bin_dir,
        "gh",
        "GH_LOG",
        [
            "if 'comment' in sys.argv: print('commented')",
            "if 'close' in sys.argv: print('closed')",
            "if 'view' in sys.argv: print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42'}))",
        ],
    )
    body = tmp_path / "body.md"
    body.write_text("Answer: yes, proceed as discussed.\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--body-file",
        str(body),
        "--classification",
        "question",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_LOG": str(log)},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert len(payload["review_advisory"]) == 1
    assert payload["review_advisory"][0].startswith("REVIEW:")
    assert "question" in payload["review_advisory"][0]
    assert "advisory only, never blocks" in payload["review_advisory"][0]


def test_close_with_comment_refuses_on_missing_source_preservation_for_external_body(
    tmp_path: Path,
) -> None:
    """An externally-sourced body (`Source origin:` present) must also carry a
    preservation form; otherwise the floor refuses even when the behavioral
    verdict and critique lines are present."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    write_argv_logging_fake(bin_dir, "gh", "GH_LOG", [])
    body = tmp_path / "body.md"
    body.write_text(bug_closeout_body() + "\n\nSource origin: slack\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--body-file",
        str(body),
        "--classification",
        "bug",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_LOG": str(log)},
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "source preservation" in payload["error"]
    assert not log.exists()
