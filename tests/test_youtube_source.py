from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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
    return {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}


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


def test_gather_youtube_metadata_only_writes_partial_record(tmp_path: Path) -> None:
    info = {
        "id": "abc123",
        "title": "Metadata Video",
        "channel": "Demo Channel",
        "upload_date": "20260611",
        "description": "metadata summary only",
        "chapters": [{"title": "Intro", "start_time": 0}],
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
    assert "## Extracted Content" not in record


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
