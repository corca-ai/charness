"""#232: issue body must survive creation byte-identical.

These tests drive `issue_tool.py create` against a fake backend that captures
the file handed to `--body-file` and reads it back, proving the body never
passes through a shell-quoting layer that could corrupt multi-line Korean /
Markdown / fenced-code / quote / dollar-sign / URL content.
"""

from __future__ import annotations

import json
import os
import runpy
import subprocess
from pathlib import Path

import pytest

from tests.quality_gates.support import run_script

SCRIPT = "skills/public/issue/scripts/issue_tool.py"
CREATE = runpy.run_path(str(Path(__file__).resolve().parents[2] / "skills/public/issue/scripts/issue_create.py"))

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


def _write_capture_backend(
    bin_dir: Path,
    store: Path,
    *,
    echo_body: str | None = None,
    create_stdout: str = "https://github.com/corca-ai/charness/issues/777",
    view_url: str | None = "https://github.com/corca-ai/charness/issues/777",
    view_number: int = 777,
) -> None:
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
                "argv_store = os.environ.get('GH_ARGV_STORE')",
                "if argv_store and 'create' in argv: Path(argv_store).write_text(json.dumps(argv), encoding='utf-8')",
                f"override = {override}",
                "if 'create' in argv:",
                "    i = argv.index('--body-file')",
                "    store.write_text(Path(argv[i + 1]).read_text(encoding='utf-8'), encoding='utf-8')",
                f"    print({create_stdout!r})",
                "elif 'view' in argv:",
                "    body = override if override is not None else (store.read_text(encoding='utf-8') if store.exists() else '')",
                f"    print(json.dumps({{'number': {view_number}, 'body': body, 'url': {view_url!r}}}))",
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
                "    print(json.dumps({'number': 778, 'body': 'body\\n', 'url': 'https://github.com/corca-ai/charness/issues/778'}))",
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
    # The fake backend stores only the file content; no inline body argument can
    # recreate the hostile input as a second transport channel.
    assert "create_argv" not in payload


def test_create_bare_number_uses_validated_readback_url_or_null_when_skipped(tmp_path: Path) -> None:
    body_file = tmp_path / "body.md"
    body_file.write_text("body\n", encoding="utf-8")
    bin_dir = tmp_path / "bin"
    store = tmp_path / "body-store.md"
    _write_capture_backend(
        bin_dir,
        store,
        create_stdout="538",
        view_url="https://tracker.example/acme/demo/issues/538",
        view_number=538,
    )

    verified = run_script(
        SCRIPT, "create", "--repo", "acme/demo", "--title", "bare backend", "--body-file", str(body_file),
        "--repo-root", str(tmp_path), env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_BODY_STORE": str(store)},
    )
    assert verified.returncode == 0, verified.stderr
    verified_payload = json.loads(verified.stdout)
    assert verified_payload["number"] == 538
    assert verified_payload["url"] == "https://tracker.example/acme/demo/issues/538"
    assert verified_payload["verification"] == {
        "command": "verify-create",
        "repo": "acme/demo",
        "number": 538,
        "body_file": str(body_file),
    }

    skipped = run_script(
        SCRIPT, "create", "--repo", "acme/demo", "--title", "bare skipped", "--body-file", str(body_file),
        "--skip-readback", "--repo-root", str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_BODY_STORE": str(store)},
    )
    assert skipped.returncode == 0, skipped.stderr
    skipped_payload = json.loads(skipped.stdout)
    assert skipped_payload["number"] == 538
    assert skipped_payload["url"] is None
    assert skipped_payload["verification"]["command"] == "verify-create"


def test_create_with_an_unparseable_backend_result_does_not_advertise_verify_create(tmp_path: Path) -> None:
    body_file = tmp_path / "body.md"
    body_file.write_text("body\n", encoding="utf-8")
    bin_dir = tmp_path / "bin"
    store = tmp_path / "body-store.md"
    _write_capture_backend(bin_dir, store, create_stdout="created successfully")

    result = run_script(
        SCRIPT,
        "create",
        "--repo",
        "acme/demo",
        "--title",
        "unparseable backend",
        "--body-file",
        str(body_file),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_BODY_STORE": str(store)},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["number"] is None
    assert payload["verification"] is None
    assert "could not parse" in payload["verify_error"]


@pytest.mark.parametrize("create_stdout", ["0", "https://github.com/corca-ai/charness/issues/0"])
def test_create_with_a_nonpositive_backend_number_does_not_advertise_verify_create(
    tmp_path: Path, create_stdout: str
) -> None:
    body_file = tmp_path / "body.md"
    body_file.write_text("body\n", encoding="utf-8")
    bin_dir = tmp_path / "bin"
    store = tmp_path / "body-store.md"
    _write_capture_backend(bin_dir, store, create_stdout=create_stdout)

    result = run_script(
        SCRIPT,
        "create",
        "--repo",
        "corca-ai/charness",
        "--title",
        "nonpositive backend number",
        "--body-file",
        str(body_file),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_BODY_STORE": str(store)},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["number"] is None
    assert payload["verification"] is None
    assert "could not parse" in payload["verify_error"]


@pytest.mark.parametrize(
    "value",
    [
        "538",
        "https://@/issues/538",
        "https:// /issues/538",
        "https://github.com/issue path",
        "https://github.com/issues/538\nnot-a-url",
        "https://[::1",
        "https://[invalid]",
        "https://github.com:99999/issues/538",
        "https://github.com:invalid/issues/538",
        "https://github.com\\evil/issues/538",
    ],
)
def test_create_url_identity_rejects_non_navigable_backend_text(value: str) -> None:
    assert CREATE["_http_url"](value) is None


def test_create_url_identity_accepts_complete_http_urls() -> None:
    assert CREATE["_http_url"]("https://tracker.example/acme/demo/issues/538") == "https://tracker.example/acme/demo/issues/538"
    assert CREATE["_http_url"]("http://localhost:8080/issues/538") == "http://localhost:8080/issues/538"


def test_create_applies_labels_and_milestone_as_flags(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    store = tmp_path / "captured-body.md"
    argv_store = tmp_path / "create-argv.json"
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
        env={
            **os.environ,
            "PATH": f"{bin_dir}:/usr/bin:/bin",
            "GH_BODY_STORE": str(store),
            "GH_ARGV_STORE": str(argv_store),
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert "create_argv" not in payload
    argv = json.loads(argv_store.read_text(encoding="utf-8"))
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
    assert payload["number"] == 778
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
    assert payload["number"] == 778
    assert payload["body_verified"] is None
    assert payload["readback_skipped"] is True
    assert "issue created" in payload["verify_skipped"]
    assert count_file.read_text().splitlines() == ["create"]


def test_verify_create_keeps_deferred_readback_inside_the_issue_tool_grammar(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    count_file = tmp_path / "calls.log"
    _write_counting_backend(bin_dir, count_file)
    body_file = tmp_path / "body.md"
    body_file.write_text("body\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "verify-create",
        "--repo",
        "corca-ai/charness",
        "--number",
        "778",
        "--body-file",
        str(body_file),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_CALL_COUNT": str(count_file)},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["readback_verified"] is True
    assert payload["body_verified"] is True
    assert payload["body_verification"] == "byte-identical"
    assert count_file.read_text().splitlines() == ["view"]


def test_verify_create_without_a_body_file_does_not_claim_body_fidelity(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    count_file = tmp_path / "calls.log"
    _write_counting_backend(bin_dir, count_file)

    result = run_script(
        SCRIPT,
        "verify-create",
        "--repo",
        "corca-ai/charness",
        "--number",
        "778",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_CALL_COUNT": str(count_file)},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["readback_verified"] is True
    assert payload["body_verified"] is None
    assert payload["body_verification"] == "not-requested"
    assert "view_argv" not in payload
    assert "create_argv" not in payload


@pytest.mark.parametrize("missing", ["repo", "number", "json_fields"])
def test_verify_create_refuses_a_custom_view_template_missing_identity_before_backend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, missing: str
) -> None:
    template = ["view", "{repo}", "{number}", "--json", "{json_fields}"]
    template = [part for part in template if "{" + missing + "}" not in part]
    called = False

    def no_backend_call(_argv: list[str]) -> subprocess.CompletedProcess[str]:
        nonlocal called
        called = True
        return subprocess.CompletedProcess(_argv, 0, "{}", "")

    monkeypatch.setitem(CREATE["verify_created_issue"].__globals__, "run_backend", no_backend_call)
    with pytest.raises(RuntimeError, match="missing required placeholders"):
        CREATE["verify_created_issue"](
            "acme/demo",
            7,
            backend={"id": "acme", "binary": "acme", "commands": {"view": template}},
        )
    assert called is False


@pytest.mark.parametrize("returned", [{}, {"number": 778, "body": None, "url": "https://github.com/corca-ai/charness/issues/778"}])
def test_verify_create_refuses_missing_or_non_string_body_for_byte_verification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, returned: dict[str, object]
) -> None:
    body_file = tmp_path / "empty.md"
    body_file.write_text("", encoding="utf-8")

    monkeypatch.setitem(
        CREATE["verify_created_issue"].__globals__,
        "run_backend",
        lambda argv: subprocess.CompletedProcess(argv, 0, json.dumps(returned), ""),
    )
    with pytest.raises(RuntimeError, match="did not return a string body|unidentifiable issue"):
        CREATE["verify_created_issue"]("corca-ai/charness", 778, body_file=body_file)


def test_verify_create_refuses_a_returned_number_or_repository_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body_file = tmp_path / "body.md"
    body_file.write_text("body\n", encoding="utf-8")
    responses = iter(
        [
            {"number": 779, "body": "body\n"},
            {"number": 778, "body": "body\n", "url": "https://github.com/other/repo/issues/778"},
        ]
    )
    monkeypatch.setitem(
        CREATE["verify_created_issue"].__globals__,
        "run_backend",
        lambda argv: subprocess.CompletedProcess(argv, 0, json.dumps(next(responses)), ""),
    )

    with pytest.raises(RuntimeError, match="different or unidentifiable issue"):
        CREATE["verify_created_issue"]("corca-ai/charness", 778, body_file=body_file)
    with pytest.raises(RuntimeError, match="different repository"):
        CREATE["verify_created_issue"]("corca-ai/charness", 778, body_file=body_file)


def test_verify_create_refuses_repository_silence_and_boolean_or_nonpositive_numbers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body_file = tmp_path / "body.md"
    body_file.write_text("body\n", encoding="utf-8")
    responses = iter(
        [
            {"number": 778, "body": "body\n"},
            {"number": True, "body": "body\n", "url": "https://github.com/corca-ai/charness/issues/1"},
        ]
    )
    monkeypatch.setitem(
        CREATE["verify_created_issue"].__globals__,
        "run_backend",
        lambda argv: subprocess.CompletedProcess(argv, 0, json.dumps(next(responses)), ""),
    )

    with pytest.raises(RuntimeError, match="did not identify its repository"):
        CREATE["verify_created_issue"]("corca-ai/charness", 778, body_file=body_file)
    with pytest.raises(RuntimeError, match="different or unidentifiable issue"):
        CREATE["verify_created_issue"]("corca-ai/charness", 1, body_file=body_file)
    with pytest.raises(RuntimeError, match="positive integer"):
        CREATE["verify_created_issue"]("corca-ai/charness", 0, body_file=body_file)


@pytest.mark.parametrize("number", ["0", "-1"])
def test_verify_create_cli_refuses_nonpositive_numbers_before_backend(tmp_path: Path, number: str) -> None:
    result = run_script(
        SCRIPT,
        "verify-create",
        "--repo",
        "corca-ai/charness",
        "--number",
        number,
        "--repo-root",
        str(tmp_path),
    )

    assert result.returncode == 2
    assert "positive integer" in result.stderr


def test_create_help_never_primes_exact_placeholder_title_values() -> None:
    result = run_script(SCRIPT, "create", "--help")

    assert result.returncode == 0, result.stderr
    assert "Allow a known placeholder title intentionally" in result.stdout
    assert "titles `x` or `test`" not in result.stdout
