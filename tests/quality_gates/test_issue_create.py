"""#232: issue body must survive creation byte-identical.

These tests drive `issue_tool.py create` against a fake backend that captures
the file handed to `--body-file` and reads it back, proving the body never
passes through a shell-quoting layer that could corrupt multi-line Korean /
Markdown / fenced-code / quote / dollar-sign / URL content.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from tests.quality_gates.support import run_script

SCRIPT = "skills/public/issue/scripts/issue_tool.py"

# A body that exercises every corruption-prone category #232 names: Korean text,
# Markdown headings/bullets, backticks, a fenced code block, single/double
# quotes, dollar signs / shell-looking snippets, and URLs.
HOSTILE_BODY = "\n".join(
    [
        "## 문제 (Problem)",
        "",
        "- 한국어 불릿 with `inline backticks`",
        "- \"double\" and 'single' quotes on one line",
        "",
        "```bash",
        'echo "$HOME and ${VAR}"',
        "cost=$5.00; run $(whoami) && rm -rf $PWD",
        "```",
        "",
        "Inline shell-looking text: `echo \"$1\"` and $(date).",
        "URL: https://github.com/corca-ai/charness/issues/232",
        "Slack: https://corca.slack.com/archives/C0123/p456789",
        "",
    ]
)


def _write_capture_backend(bin_dir: Path, store: Path, *, echo_body: str | None = None) -> None:
    """Write a fake `gh` that stores the --body-file content on create and
    returns it (or `echo_body`) as JSON on view."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    fake = bin_dir / "gh"
    override = "None" if echo_body is None else repr(echo_body)
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, os, sys",
                "from pathlib import Path",
                "argv = sys.argv[1:]",
                "store = Path(os.environ['GH_BODY_STORE'])",
                f"override = {override}",
                "if 'create' in argv:",
                "    i = argv.index('--body-file')",
                "    store.write_text(Path(argv[i + 1]).read_text(encoding='utf-8'), encoding='utf-8')",
                "    print('https://github.com/corca-ai/charness/issues/777')",
                "elif 'view' in argv:",
                "    body = override if override is not None else (store.read_text(encoding='utf-8') if store.exists() else '')",
                "    print(json.dumps({'body': body}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)


def test_create_round_trips_hostile_body_byte_identical(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    store = tmp_path / "captured-body.md"
    _write_capture_backend(bin_dir, store)
    body_file = tmp_path / "body.md"
    body_file.write_text(HOSTILE_BODY, encoding="utf-8")

    result = run_script(
        SCRIPT,
        "create",
        "--repo",
        "corca-ai/charness",
        "--title",
        "샘플 issue: $cost & `code`",
        "--body-file",
        str(body_file),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_BODY_STORE": str(store)},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["created_number"] == 777
    assert "issues/777" in payload["created_url"]
    assert payload["body_verified"] is True
    # The backend received the body via file, byte-identical to the input.
    assert store.read_text(encoding="utf-8") == HOSTILE_BODY
    # And the argv carried --body-file, never an inline --body string.
    assert "--body-file" in payload["create_argv"]
    assert "--body" not in payload["create_argv"]


def test_create_applies_labels_and_milestone_as_flags(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    store = tmp_path / "captured-body.md"
    _write_capture_backend(bin_dir, store)
    body_file = tmp_path / "body.md"
    body_file.write_text("body\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "create",
        "--repo",
        "corca-ai/charness",
        "--title",
        "t",
        "--body-file",
        str(body_file),
        "--label",
        "bug",
        "--label",
        "triage",
        "--milestone",
        "v0.13.0",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_BODY_STORE": str(store)},
    )

    assert result.returncode == 0, result.stderr
    argv = json.loads(result.stdout)["create_argv"]
    assert argv.count("--label") == 2
    assert "bug" in argv and "triage" in argv
    assert argv[argv.index("--milestone") + 1] == "v0.13.0"


def test_create_reports_unverified_when_readback_differs(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    store = tmp_path / "captured-body.md"
    # Backend reports back a mangled body — create must flag it, not claim success.
    _write_capture_backend(bin_dir, store, echo_body="corrupted body")
    body_file = tmp_path / "body.md"
    body_file.write_text(HOSTILE_BODY, encoding="utf-8")

    result = run_script(
        SCRIPT,
        "create",
        "--repo",
        "corca-ai/charness",
        "--title",
        "t",
        "--body-file",
        str(body_file),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_BODY_STORE": str(store)},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["body_verified"] is False
    assert "stored_body_bytes" in payload


def test_create_fails_when_body_file_missing(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    store = tmp_path / "captured-body.md"
    _write_capture_backend(bin_dir, store)

    result = run_script(
        SCRIPT,
        "create",
        "--repo",
        "corca-ai/charness",
        "--title",
        "t",
        "--body-file",
        str(tmp_path / "does-not-exist.md"),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_BODY_STORE": str(store)},
    )

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "body file not found" in payload["error"]
