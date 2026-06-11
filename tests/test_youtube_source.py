from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "support" / "web-fetch" / "scripts"))
import acquire_public_url  # noqa: E402
import agent_browser_session  # noqa: E402
import youtube_browser_ui  # noqa: E402
import youtube_source  # noqa: E402
from acquisition_trace_lib import AcquisitionAttempt  # noqa: E402


def run_helper(script: str, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, script, *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def _fake_ytdlp(tmp_path: Path, body: str, *, exit_code: int = 0) -> dict[str, str]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    script = bin_dir / "yt-dlp"
    script.write_text(f"#!/bin/sh\ncat <<'EOF'\n{body}\nEOF\nexit {exit_code}\n", encoding="utf-8")
    script.chmod(0o755)
    return {**os.environ, "PATH": f"{bin_dir}{os.pathsep}/usr/bin{os.pathsep}/bin"}


def _fake_ytdlp_and_browser(tmp_path: Path, ytdlp_body: str, *, ytdlp_exit_code: int = 0) -> dict[str, str]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    ytdlp = bin_dir / "yt-dlp"
    ytdlp.write_text(f"#!/bin/sh\ncat <<'EOF'\n{ytdlp_body}\nEOF\nexit {ytdlp_exit_code}\n", encoding="utf-8")
    ytdlp.chmod(0o755)
    browser = bin_dir / "agent-browser"
    browser.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, sys",
                "args = sys.argv[1:]",
                "if 'get' in args and args[-2:] == ['text', 'body']:",
                "    payload = {'videoDetails': {'videoId': 'abc123', 'title': 'Browser Video', 'author': 'Demo Channel', 'lengthSeconds': '12'}, 'captions': {'playerCaptionsTracklistRenderer': {'captionTracks': [{'languageCode': 'en'}]}}}",
                "    print('ytInitialPlayerResponse = ' + json.dumps(payload) + ';')",
                "elif 'snapshot' in args:",
                "    print('- textbox \"스크립트 검색\" [ref=e1]')",
                "    print('- button \"Anthropic is definitively riding\" [ref=e2]')",
                "    print('- button \"7초 They are trying to become a platform\" [ref=e3]')",
                "    print('- link \"Recommended video\" [ref=e4]')",
                "else:",
                "    print('ok')",
                "",
            ]
        ),
        encoding="utf-8",
    )
    browser.chmod(0o755)
    return {**os.environ, "PATH": f"{bin_dir}{os.pathsep}/usr/bin{os.pathsep}/bin"}


def _fake_ytdlp_browser_guard(
    tmp_path: Path,
    *,
    guard_cleanup_exit: int = 0,
) -> tuple[dict[str, str], Path, Path]:
    env = _fake_ytdlp_and_browser(tmp_path, json.dumps({"id": "abc123", "title": "Metadata Only"}))
    browser_log = tmp_path / "browser.log"
    guard_log = tmp_path / "guard.log"
    browser = tmp_path / "bin" / "agent-browser"
    original = browser.read_text(encoding="utf-8")
    browser.write_text(
        original.replace(
            "import json, sys",
            "import json, os, sys\nfrom pathlib import Path\nPath(os.environ['BROWSER_LOG']).write_text(Path(os.environ['BROWSER_LOG']).read_text() + ' '.join(sys.argv[1:]) + '\\n' if Path(os.environ['BROWSER_LOG']).exists() else ' '.join(sys.argv[1:]) + '\\n')",
        ),
        encoding="utf-8",
    )
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "agent_browser_runtime_guard.py").write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import os, sys",
                "from pathlib import Path",
                "log = Path(os.environ['GUARD_LOG'])",
                "log.write_text((log.read_text() if log.exists() else '') + ' '.join(sys.argv[1:]) + '\\n')",
                f"sys.exit({guard_cleanup_exit} if '--cleanup-orphans' in sys.argv else 0)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    env.update({"BROWSER_LOG": str(browser_log), "GUARD_LOG": str(guard_log)})
    return env, repo, guard_log


def _fake_ytdlp_captcha_browser_no_transcript(tmp_path: Path) -> dict[str, str]:
    env = _fake_ytdlp_and_browser(
        tmp_path,
        "ERROR: Sign in to confirm you are not a bot",
        ytdlp_exit_code=1,
    )
    browser = tmp_path / "bin" / "agent-browser"
    browser.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, sys",
                "args = sys.argv[1:]",
                "if 'get' in args and args[-2:] == ['text', 'body']:",
                "    payload = {'videoDetails': {'videoId': 'abc123', 'title': 'Browser Metadata', 'author': 'Demo Channel'}}",
                "    print('ytInitialPlayerResponse = ' + json.dumps(payload) + ';')",
                "elif 'snapshot' in args:",
                "    print('- textbox \"스크립트 검색\" [ref=e1]')",
                "    print('- link \"Recommended video\" [ref=e4]')",
                "else:",
                "    print('ok')",
                "",
            ]
        ),
        encoding="utf-8",
    )
    browser.chmod(0o755)
    return env


def _direct_file(tmp_path: Path) -> Path:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>short YouTube shell</body></html>", encoding="utf-8")
    return direct


def _direct_text_file(tmp_path: Path, text: str) -> Path:
    direct = tmp_path / "direct.html"
    direct.write_text(text, encoding="utf-8")
    return direct


def test_acquire_youtube_transcript_from_ytdlp_subtitles(tmp_path: Path) -> None:
    info = {
        "id": "abc123",
        "title": "Demo Video",
        "channel": "Demo Channel",
        "upload_date": "20260611",
        "webpage_url": "https://www.youtube.com/watch?v=abc123",
        "subtitles": {
            "en": [
                {
                    "ext": "vtt",
                    "data": "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nHello transcript.\n",
                }
            ]
        },
    }
    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://youtu.be/abc123",
        "--direct-response-file",
        str(_direct_file(tmp_path)),
        "--include-selected-content",
        env=_fake_ytdlp(tmp_path, json.dumps(info)),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "success"
    assert payload["source_identity"] == "youtube-transcript"
    assert payload["selected_attempt"]["details"]["transcript_language"] == "en"
    assert payload["selected_content"]["format"] == "markdown"
    assert "Hello transcript." in payload["selected_content"]["text"]


def test_youtube_source_parses_json3_captions_and_url_variants(monkeypatch) -> None:
    monkeypatch.setattr(youtube_source.shutil, "which", lambda _name: "/bin/yt-dlp")
    json3 = json.dumps(
        {
            "events": [
                "not-a-dict",
                {"segs": [{"utf8": "Hello "}, {}, {"utf8": "world"}]},
            ]
        }
    )
    info = {
        "id": "abc123",
        "title": "JSON3 Video",
        "subtitles": {
            123: [{"ext": "vtt", "data": "ignored"}],
            "en": {"not": "a-list"},
            "ko": [{"ext": "json3", "url": "https://captions.example/json3"}],
        },
    }

    attempts = youtube_source.run_youtube_stage(
        "https://www.youtube.com/watch?v=abc123",
        run_command=lambda _command: (json.dumps(info), None),
        fetch_url=lambda url: (json3, None),
    )

    assert attempts[0].status == "success"
    assert attempts[0].details["transcript_language"] == "ko"
    assert attempts[0].details["caption_ext"] == "json3"
    assert "Hello world" in (attempts[0].content_text or "")


def test_youtube_source_caption_error_paths_and_metadata_only(monkeypatch) -> None:
    monkeypatch.setattr(youtube_source.shutil, "which", lambda _name: "/bin/yt-dlp")
    info = {
        "id": "abc123",
        "title": "Caption Errors",
        "subtitles": {
            "en": [
                {"ext": "vtt"},
                {"ext": "vtt", "url": "https://captions.example/fail"},
            ]
        },
    }

    attempts = youtube_source.run_youtube_stage(
        "https://youtu.be/abc123",
        run_command=lambda _command: (json.dumps(info), None),
        fetch_url=lambda _url: ("", "HTTPError:blocked"),
    )

    assert attempts[0].status == "metadata-only"
    assert attempts[0].details["caption_errors"] == [
        "en:caption-missing-url",
        "en:HTTPError:blocked",
    ]


def test_youtube_source_error_and_identity_edge_cases(monkeypatch) -> None:
    assert youtube_source.parse_video_id("https://example.com/watch?v=abc123") is None
    assert youtube_source.run_youtube_stage("https://example.com/not-youtube", run_command=lambda _command: ("", None))[
        0
    ].details["reason"] == "missing-video-id"
    assert youtube_source._classify_error("plain failure") == ("error", "fetch-failed")
    monkeypatch.setattr(youtube_source.shutil, "which", lambda _name: "/bin/yt-dlp")
    invalid = youtube_source.run_youtube_stage(
        "https://youtu.be/abc123",
        run_command=lambda _command: ("{", None),
    )
    assert invalid[0].error == "invalid-json:Expecting property name enclosed in double quotes"
    assert youtube_source.classify_source_identity({"route": {"route_id": "other"}}) == "not-applicable"
    assert (
        youtube_source.classify_source_identity({"route": {"route_id": "yt-dlp-metadata"}, "selected_attempt": None})
        == "youtube-unavailable"
    )


def test_youtube_source_default_fetch_url_success_and_error(monkeypatch) -> None:
    class Headers:
        def __init__(self, charset: str | None) -> None:
            self._charset = charset

        def get_content_charset(self) -> str | None:
            return self._charset

    class Response:
        headers = Headers(None)

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self) -> bytes:
            return "caption body".encode()

    monkeypatch.setattr(youtube_source.urllib.request, "urlopen", lambda _url, timeout=20: Response())
    assert youtube_source._default_fetch_url("https://captions.example/ok") == ("caption body", None)

    def raise_url_error(_url, timeout=20):
        raise RuntimeError("network down")

    monkeypatch.setattr(youtube_source.urllib.request, "urlopen", raise_url_error)
    assert youtube_source._default_fetch_url("https://captions.example/fail") == ("", "RuntimeError:network down")


def test_youtube_source_import_bootstrap_adds_script_dir(monkeypatch) -> None:
    module_path = ROOT / "skills" / "support" / "web-fetch" / "scripts" / "youtube_source.py"
    script_dir = str(module_path.parent)
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != script_dir])
    spec = importlib.util.spec_from_file_location("youtube_source_bootstrap_probe", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert script_dir in sys.path


def test_gather_youtube_metadata_only_writes_partial_record(tmp_path: Path) -> None:
    info = {
        "id": "abc123",
        "title": "Metadata Video",
        "channel": "Demo Channel",
        "upload_date": "20260611",
        "description": "metadata summary only",
        "chapters": [{"title": "Intro", "start_time": 0}],
        "subtitles": {"en": [{"ext": "vtt"}]},
    }
    result = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://www.youtube.com/watch?v=abc123",
        "--direct-response-file",
        str(_direct_file(tmp_path)),
        "--slug",
        "youtube-metadata",
        "--date",
        "2026-06-11",
        "--persist-extracted-content",
        "--execute",
        env=_fake_ytdlp(tmp_path, json.dumps(info)),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["acquisition_disposition"] == "success"
    assert payload["final_status"] == "metadata-only"
    assert payload["source_identity"] == "youtube-metadata-only"
    assert payload["content_persistence"] == "unavailable"
    record = Path(payload["write_record"]["record_artifact_path"]).read_text(encoding="utf-8")
    assert "Source Identity: `youtube-metadata-only`" in record
    assert "Source Type: `youtube-metadata-only`" in record
    assert "Title: Metadata Video" in record
    assert "Chapter Count: 1" in record
    assert "Caption Errors: `en:caption-missing-url`" in record
    assert "## Extracted Content" not in record


def test_acquire_youtube_browser_ui_transcript_after_ytdlp_metadata_only(tmp_path: Path) -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://www.youtube.com/watch?v=abc123",
        "--direct-response-file",
        str(_direct_file(tmp_path)),
        "--include-selected-content",
        env=_fake_ytdlp_and_browser(tmp_path, json.dumps({"id": "abc123", "title": "Metadata Only"})),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "success"
    assert payload["source_identity"] == "youtube-transcript-browser-ui"
    assert payload["selected_attempt"]["stage_id"] == "youtube-browser-transcript-ui"
    assert payload["selected_attempt"]["details"]["transcript_segment_count"] == 2
    assert "Anthropic is definitively riding" in payload["selected_content"]["text"]
    assert "They are trying to become a platform" in payload["selected_content"]["text"]


def test_acquire_youtube_browser_ui_transcript_after_weak_direct_success(tmp_path: Path) -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://www.youtube.com/watch?v=abc123",
        "--direct-response-file",
        str(_direct_text_file(tmp_path, "direct shell " + ("useful content " * 140))),
        "--include-selected-content",
        env=_fake_ytdlp_and_browser(tmp_path, json.dumps({"id": "abc123", "title": "Metadata Only"})),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["attempts"][0]["status"] == "success"
    assert payload["attempts"][0]["confidence"] == "weak"
    assert payload["source_identity"] == "youtube-transcript-browser-ui"
    assert payload["selected_attempt"]["stage_id"] == "youtube-browser-transcript-ui"


def test_acquire_youtube_captcha_not_masked_by_browser_metadata_only(tmp_path: Path) -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://www.youtube.com/watch?v=abc123",
        "--direct-response-file",
        str(_direct_file(tmp_path)),
        env=_fake_ytdlp_captcha_browser_no_transcript(tmp_path),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "blocked"
    assert payload["source_identity"] == "youtube-blocked"
    ui_attempt = next(a for a in payload["attempts"] if a["stage_id"] == "youtube-browser-transcript-ui")
    assert ui_attempt["status"] == "diagnostic"
    assert ui_attempt["details"]["diagnostic"] is True


def test_youtube_snapshot_parser_strips_inline_korean_timestamps() -> None:
    snapshot = "\n".join(
        [
            '- button "outside panel" [ref=e0]',
            '- textbox "스크립트 검색" [ref=e1]',
            '- button "Before we begin then 4초 let\\\"s begin with those blocks" [ref=e2]',
            '- button "1분 8초 when sufficient compute capacity allows" [ref=e3]',
            '- link "Recommended video" [ref=e4]',
        ]
    )

    assert youtube_browser_ui.extract_transcript_lines_from_snapshot(snapshot) == [
        'Before we begin then let"s begin with those blocks',
        "when sufficient compute capacity allows",
    ]


def test_youtube_browser_ui_metadata_and_decode_edge_cases() -> None:
    assert youtube_browser_ui._extract_json_object("no marker", "ytInitialPlayerResponse") is None
    assert youtube_browser_ui._extract_json_object("ytInitialPlayerResponse = ;", "ytInitialPlayerResponse") is None
    assert youtube_browser_ui._extract_json_object("ytInitialPlayerResponse = {", "ytInitialPlayerResponse") is None
    body = (
        "ytInitialPlayerResponse = "
        + json.dumps({"microformat": {"playerMicroformatRenderer": {"uploadDate": "2026-06-11"}}})
        + ";"
    )
    assert youtube_browser_ui._metadata_from_player_response(body, "https://youtu.be/abc123")["publish_date"] == "2026-06-11"
    assert youtube_browser_ui._decode_snapshot_label(r'bad\\"label') == r'bad\\"label'.replace(r"\"", '"')


def test_youtube_browser_ui_failure_branches(monkeypatch) -> None:
    failed = youtube_browser_ui._failed_attempt("boom", video_id="abc123", session="s", error="err", output_chars=3)
    assert failed.status == "error"
    assert failed.details["diagnostic"] is True
    assert youtube_browser_ui.run_browser_ui_transcript_stage(
        "https://www.youtube.com/watch", session="s", run_command=lambda _command: ("", None)
    ).details["reason"] == "missing-video-id"
    monkeypatch.setattr(youtube_browser_ui.shutil, "which", lambda _name: None)
    missing = youtube_browser_ui.run_browser_ui_transcript_stage(
        "https://www.youtube.com/watch?v=abc123", session="s", run_command=lambda _command: ("", None)
    )
    assert missing.error == "missing-tool:agent-browser"


def test_youtube_browser_ui_command_failure_branches(monkeypatch) -> None:
    monkeypatch.setattr(youtube_browser_ui.shutil, "which", lambda _name: "/bin/agent-browser")
    command_fail = youtube_browser_ui.run_browser_ui_transcript_stage(
        "https://www.youtube.com/watch?v=abc123",
        session="s",
        run_command=lambda _command: ("out", "open failed"),
    )
    assert command_fail.details["reason"] == "browser-command-failed"

    def body_fail(command):
        if command[-3:] == ["get", "text", "body"]:
            return "", "body failed"
        return "", None

    assert youtube_browser_ui.run_browser_ui_transcript_stage(
        "https://www.youtube.com/watch?v=abc123", session="s", run_command=body_fail
    ).details["reason"] == "body-read-failed"

    def snapshot_fail(command):
        if "snapshot" in command:
            return "", "snapshot failed"
        return "", None

    assert youtube_browser_ui.run_browser_ui_transcript_stage(
        "https://www.youtube.com/watch?v=abc123", session="s", run_command=snapshot_fail
    ).details["reason"] == "snapshot-failed"


def test_youtube_browser_ui_no_metadata_no_transcript_is_diagnostic(monkeypatch) -> None:
    monkeypatch.setattr(youtube_browser_ui.shutil, "which", lambda _name: "/bin/agent-browser")

    def run_command(command):
        if command[-3:] == ["get", "text", "body"]:
            return "plain body", None
        if "snapshot" in command:
            return '- textbox "Search transcript" [ref=e1]\n', None
        return "", None

    attempt = youtube_browser_ui.run_browser_ui_transcript_stage(
        "https://www.youtube.com/watch?v=abc123", session="s", run_command=run_command
    )
    assert attempt.status == "diagnostic"
    assert attempt.error == "transcript-segments-unavailable"


def test_agent_browser_cleanup_orphans_reports_missing_guard(tmp_path: Path) -> None:
    error = agent_browser_session.cleanup_orphans(
        tmp_path / "scripts",
        tmp_path / "repo",
        timeout=1,
        run_command=lambda _command, timeout=1: ("", None),
    )
    assert "guard_unavailable" in str(error)


def test_should_try_youtube_browser_skip_reasons() -> None:
    assert acquire_public_url._should_try_youtube_browser("yt-dlp-metadata", [], browser_mode="off") == (
        False,
        "browser-mode-off",
    )
    attempts = [
        AcquisitionAttempt(
            stage_id=youtube_source.STAGE_ID,
            tool_id="yt-dlp",
            status="success",
            confidence="strong",
            details={"source_type": "youtube-transcript"},
        )
    ]
    assert acquire_public_url._should_try_youtube_browser("yt-dlp-metadata", attempts, browser_mode="auto") == (
        False,
        "prior-stage-sufficient",
    )
    direct = [
        AcquisitionAttempt(
            stage_id="direct-public-fetch",
            tool_id=None,
            status="success",
            confidence="weak",
        )
    ]
    assert acquire_public_url._should_try_youtube_browser("yt-dlp-metadata", direct, browser_mode="auto") == (
        False,
        "prior-stage-sufficient",
    )


def test_youtube_source_identity_for_ui_non_success_statuses() -> None:
    route = {"route_id": "yt-dlp-metadata"}
    assert (
        youtube_source.classify_source_identity(
            {"route": route, "selected_attempt": {"stage_id": youtube_source.UI_STAGE_ID, "status": "metadata-only", "details": {}}}
        )
        == "youtube-metadata-only"
    )
    assert (
        youtube_source.classify_source_identity(
            {"route": route, "selected_attempt": {"stage_id": youtube_source.UI_STAGE_ID, "status": "captcha", "details": {}}}
        )
        == "youtube-blocked"
    )
    assert (
        youtube_source.classify_source_identity(
            {
                "route": route,
                "selected_attempt": {
                    "stage_id": youtube_source.UI_STAGE_ID,
                    "status": "diagnostic",
                    "details": {"source_type": "youtube-metadata-only"},
                },
            }
        )
        == "youtube-unavailable"
    )


def test_youtube_snapshot_parser_keeps_repeated_segments() -> None:
    snapshot = "\n".join(
        [
            '- textbox "스크립트 검색" [ref=e1]',
            '- button "repeat me" [ref=e2]',
            '- button "repeat me" [ref=e3]',
            '- link "Recommended video" [ref=e4]',
        ]
    )

    assert youtube_browser_ui.extract_transcript_lines_from_snapshot(snapshot) == ["repeat me", "repeat me"]


def test_youtube_browser_ui_stage_runs_cleanup_then_assert(tmp_path: Path) -> None:
    env, repo, guard_log = _fake_ytdlp_browser_guard(tmp_path)
    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--repo-root",
        str(repo),
        "--url",
        "https://www.youtube.com/watch?v=abc123",
        "--direct-response-file",
        str(_direct_file(tmp_path)),
        "--include-selected-content",
        env=env,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["selected_attempt"]["stage_id"] == "youtube-browser-transcript-ui"
    assert payload["disposition"] == "success"
    guard_calls = guard_log.read_text(encoding="utf-8").splitlines()
    assert any("--cleanup-orphans --execute" in call for call in guard_calls)
    assert any("--assert-no-orphans" in call for call in guard_calls)
    cleanup_index = next(i for i, call in enumerate(guard_calls) if "--cleanup-orphans --execute" in call)
    assert cleanup_index < next(i for i, call in enumerate(guard_calls) if "--assert-no-orphans" in call)


def test_youtube_browser_ui_stage_degrades_when_cleanup_fails(tmp_path: Path) -> None:
    env, repo, guard_log = _fake_ytdlp_browser_guard(tmp_path, guard_cleanup_exit=1)
    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--repo-root",
        str(repo),
        "--url",
        "https://www.youtube.com/watch?v=abc123",
        "--direct-response-file",
        str(_direct_file(tmp_path)),
        "--include-selected-content",
        env=env,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "degraded"
    ui_attempt = next(a for a in payload["attempts"] if a["stage_id"] == "youtube-browser-transcript-ui")
    assert ui_attempt["status"] == "error"
    assert ui_attempt["details"]["cleanup"] == "failed"
    assert "--cleanup-orphans --execute" in guard_log.read_text(encoding="utf-8")


def test_acquire_youtube_identity_follows_selected_attempt(tmp_path: Path) -> None:
    info = {"id": "abc123", "title": "Metadata Video", "channel": "Demo Channel"}
    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://www.youtube.com/watch?v=abc123",
        "--direct-response-file",
        str(_direct_text_file(tmp_path, "needle " + ("useful content " * 120))),
        "--expect-text",
        "needle",
        "--browser-mode",
        "off",
        env=_fake_ytdlp(tmp_path, json.dumps(info)),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["selected_attempt"]["stage_id"] == "direct-public-fetch"
    assert payload["selected_attempt"]["confidence"] == "strong"
    assert payload["source_identity"] == "youtube-unavailable"


def test_gather_youtube_blocked_writes_honest_record(tmp_path: Path) -> None:
    result = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://youtube.com/shorts/abc123",
        "--direct-response-file",
        str(_direct_file(tmp_path)),
        "--slug",
        "youtube-blocked",
        "--date",
        "2026-06-11",
        "--execute",
        env=_fake_ytdlp(tmp_path, "ERROR: Sign in to confirm you are not a bot", exit_code=1),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["acquisition_disposition"] == "blocked"
    assert payload["final_status"] == "captcha"
    assert payload["source_identity"] == "youtube-blocked"
    record = Path(payload["write_record"]["record_artifact_path"]).read_text(encoding="utf-8")
    assert "Source Identity: `youtube-blocked`" in record
    assert "`domain-specific-route` via `yt-dlp`: captcha / none" in record
    assert "Source Type: `youtube-transcript`" not in record
    assert "Source Type: `youtube-metadata-only`" not in record


def test_gather_youtube_missing_ytdlp_writes_unavailable_record(tmp_path: Path) -> None:
    result = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://youtu.be/abc123",
        "--direct-response-file",
        str(_direct_file(tmp_path)),
        "--slug",
        "youtube-unavailable",
        "--date",
        "2026-06-11",
        "--execute",
        env={**os.environ, "PATH": str(tmp_path / "empty-bin")},
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["acquisition_disposition"] == "degraded"
    assert payload["final_status"] == "error"
    assert payload["source_identity"] == "youtube-unavailable"
    record = Path(payload["write_record"]["record_artifact_path"]).read_text(encoding="utf-8")
    assert "missing-tool:yt-dlp" in record
    assert "Video Id: `abc123`" in record
