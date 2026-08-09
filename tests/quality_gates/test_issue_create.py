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

import pytest

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


def _write_counting_backend(bin_dir: Path, count_file: Path) -> None:
    """Write a fake backend that records create/view invocations and returns a URL."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    fake = bin_dir / "gh"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, os, sys",
                "from pathlib import Path",
                "count_file = Path(os.environ['GH_CALL_COUNT'])",
                "calls = count_file.read_text().splitlines() if count_file.exists() else []",
                "calls.append('view' if 'view' in sys.argv else 'create' if 'create' in sys.argv else 'other')",
                "count_file.write_text('\\n'.join(calls) + '\\n')",
                "if 'create' in sys.argv:",
                "    print('https://github.com/corca-ai/charness/issues/778')",
                "elif 'view' in sys.argv:",
                "    print(json.dumps({'body': 'body\\n'}))",
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
    # The canonical names the skill contract tells the agent to report from. Asserted at
    # RUNTIME, not just as source literals: without these, deleting `number`/`url` from
    # the payload leaves this behavioral suite fully green and only the static doc-key
    # guard catches it.
    assert payload["number"] == 777
    assert "issues/777" in payload["url"]
    assert payload["body_verified"] is True
    assert payload["body_preview"] == HOSTILE_BODY
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
    assert payload["body_preview"] == HOSTILE_BODY
    assert "stored_body_bytes" in payload


def test_create_body_preview_is_bounded_to_closeout_excerpt(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    store = tmp_path / "captured-body.md"
    _write_capture_backend(bin_dir, store)
    body_file = tmp_path / "body.md"
    long_body = "A" * 1300
    body_file.write_text(long_body, encoding="utf-8")

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
    assert payload["body_preview"] == "A" * 1200


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


@pytest.mark.parametrize(
    "image_markup",
    [
        "![private screenshot](https://corca.slack.com/files/U01/F02/screenshot.png)",
        '<img src="https://files.slack.com/files-pri/T01-F02/screenshot.png">',
        "<img src=https://files.slack.com/files-pri/T01-F02/screenshot.png>",
        "![private screenshot][capture]\n\n[capture]: https://corca.slack.com/files/U01/F02/screenshot.png",
        "![capture][]\n\n[capture]: https://corca.slack.com/files-tmb/U01/F02/screenshot.png",
        "![capture]\n\n[capture]: https://corca.slack.com/files/U01/F02/screenshot.png",
    ],
)
def test_create_refuses_private_provider_image_before_backend_mutation(
    tmp_path: Path, image_markup: str
) -> None:
    bin_dir = tmp_path / "bin"
    count_file = tmp_path / "calls.log"
    _write_counting_backend(bin_dir, count_file)
    body_file = tmp_path / "body.md"
    body_file.write_text(image_markup + "\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "create",
        "--repo",
        "corca-ai/charness",
        "--title",
        "private media boundary",
        "--body-file",
        str(body_file),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_CALL_COUNT": str(count_file)},
    )

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["error_code"] == "private_provider_media_unpublished"
    assert "Media evidence unavailable:" in payload["error"]
    assert not count_file.exists()


def test_create_allows_private_source_identity_with_explicit_media_disposition(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    count_file = tmp_path / "calls.log"
    _write_counting_backend(bin_dir, count_file)
    body_file = tmp_path / "body.md"
    body_file.write_text(
        "Source identity: https://corca.slack.com/archives/C01/p123\n\n"
        "Media evidence unavailable: private provider attachment was not published.\n",
        encoding="utf-8",
    )

    result = run_script(
        SCRIPT,
        "create",
        "--repo",
        "corca-ai/charness",
        "--title",
        "private source identity remains traceable",
        "--body-file",
        str(body_file),
        "--skip-readback",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_CALL_COUNT": str(count_file)},
    )

    assert result.returncode == 0, result.stderr
    assert count_file.read_text().splitlines() == ["create"]


@pytest.mark.parametrize(
    "example",
    [
        "```markdown\n![example](https://corca.slack.com/files/U01/F02/example.png)\n```\n",
        "`![example](https://corca.slack.com/files/U01/F02/example.png)`\n",
        "\\![example](https://corca.slack.com/files/U01/F02/example.png)\n",
        "    ![example](https://corca.slack.com/files/U01/F02/example.png)\n",
        '<!-- <img src="https://files.slack.com/files-pri/T01-F02/example.png"> -->\n',
    ],
)
def test_create_ignores_private_image_example_in_nonrendering_context(
    tmp_path: Path, example: str
) -> None:
    bin_dir = tmp_path / "bin"
    count_file = tmp_path / "calls.log"
    _write_counting_backend(bin_dir, count_file)
    body_file = tmp_path / "body.md"
    body_file.write_text(example, encoding="utf-8")

    result = run_script(
        SCRIPT,
        "create",
        "--repo",
        "corca-ai/charness",
        "--title",
        "documented example",
        "--body-file",
        str(body_file),
        "--skip-readback",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_CALL_COUNT": str(count_file)},
    )

    assert result.returncode == 0, result.stderr
    assert count_file.read_text().splitlines() == ["create"]


def test_create_allows_plain_private_file_url_as_provenance(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    count_file = tmp_path / "calls.log"
    _write_counting_backend(bin_dir, count_file)
    body_file = tmp_path / "body.md"
    body_file.write_text(
        "Source identity: https://corca.slack.com/files/U01/F02/screenshot.png\n",
        encoding="utf-8",
    )

    result = run_script(
        SCRIPT,
        "create",
        "--repo",
        "corca-ai/charness",
        "--title",
        "private file provenance",
        "--body-file",
        str(body_file),
        "--skip-readback",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_CALL_COUNT": str(count_file)},
    )

    assert result.returncode == 0, result.stderr
    assert count_file.read_text().splitlines() == ["create"]


@pytest.mark.parametrize("title", [" X ", "  TeSt  "])
def test_create_rejects_placeholder_title_before_backend_mutation(tmp_path: Path, title: str) -> None:
    bin_dir = tmp_path / "bin"
    count_file = tmp_path / "calls.log"
    _write_counting_backend(bin_dir, count_file)
    body_file = tmp_path / "body.md"
    body_file.write_text("body\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "create",
        "--repo",
        "corca-ai/charness",
        "--title",
        title,
        "--body-file",
        str(body_file),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_CALL_COUNT": str(count_file)},
    )

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "placeholder title" in payload["error"]
    assert not count_file.exists()


def test_normal_verified_create_runs_create_then_view_once(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    count_file = tmp_path / "calls.log"
    _write_counting_backend(bin_dir, count_file)
    body_file = tmp_path / "body.md"
    body_file.write_text("body\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "create",
        "--repo",
        "corca-ai/charness",
        "--title",
        "normal title",
        "--body-file",
        str(body_file),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_CALL_COUNT": str(count_file)},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["body_verified"] is True
    assert count_file.read_text().splitlines() == ["create", "view"]


def test_create_allows_intentional_placeholder_title(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    count_file = tmp_path / "calls.log"
    _write_counting_backend(bin_dir, count_file)
    body_file = tmp_path / "body.md"
    body_file.write_text("body\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "create",
        "--repo",
        "corca-ai/charness",
        "--title",
        " TEST ",
        "--body-file",
        str(body_file),
        "--allow-placeholder-title",
        "--skip-readback",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_CALL_COUNT": str(count_file)},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["created_number"] == 778
    assert payload["readback_skipped"] is True
    assert count_file.read_text().splitlines() == ["create"]


def test_no_verify_is_rejected_and_skip_readback_still_creates(tmp_path: Path) -> None:
    body_file = tmp_path / "body.md"
    body_file.write_text("body\n", encoding="utf-8")

    rejected = run_script(
        SCRIPT,
        "create",
        "--repo",
        "corca-ai/charness",
        "--title",
        "normal title",
        "--body-file",
        str(body_file),
        "--no-verify",
        "--repo-root",
        str(tmp_path),
    )
    assert rejected.returncode == 2
    assert "unrecognized arguments: --no-verify" in rejected.stderr

    bin_dir = tmp_path / "bin"
    count_file = tmp_path / "calls.log"
    _write_counting_backend(bin_dir, count_file)
    created = run_script(
        SCRIPT,
        "create",
        "--repo",
        "corca-ai/charness",
        "--title",
        "normal title",
        "--body-file",
        str(body_file),
        "--skip-readback",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_CALL_COUNT": str(count_file)},
    )
    assert created.returncode == 0, created.stderr
    payload = json.loads(created.stdout)
    assert payload["created_number"] == 778
    assert payload["body_verified"] is None
    assert payload["readback_skipped"] is True
    assert "issue created" in payload["verify_skipped"]
    assert count_file.read_text().splitlines() == ["create"]
