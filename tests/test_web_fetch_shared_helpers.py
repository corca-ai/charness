from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
WEB_FETCH_SCRIPTS = ROOT / "skills" / "support" / "web-fetch" / "scripts"
sys.path.insert(0, str(WEB_FETCH_SCRIPTS))

import browser_fallback_stages as bfs  # noqa: E402
import url_reader  # noqa: E402
from acquisition_trace_lib import AcquisitionAttempt  # noqa: E402

GATHER_RENDERING_SPEC = importlib.util.spec_from_file_location(
    "gather_record_rendering_under_test",
    ROOT / "skills" / "public" / "gather" / "scripts" / "gather_record_rendering.py",
)
assert GATHER_RENDERING_SPEC is not None and GATHER_RENDERING_SPEC.loader is not None
gather_record_rendering = importlib.util.module_from_spec(GATHER_RENDERING_SPEC)
GATHER_RENDERING_SPEC.loader.exec_module(gather_record_rendering)

ACQUIRE_IO_SPEC = importlib.util.spec_from_file_location(
    "acquire_public_url_io_under_test",
    WEB_FETCH_SCRIPTS / "acquire_public_url_io.py",
)
assert ACQUIRE_IO_SPEC is not None and ACQUIRE_IO_SPEC.loader is not None
acquire_public_url_io = importlib.util.module_from_spec(ACQUIRE_IO_SPEC)
ACQUIRE_IO_SPEC.loader.exec_module(acquire_public_url_io)


def test_youtube_browser_stage_success_uses_shared_finish(monkeypatch) -> None:
    args = SimpleNamespace(url="https://www.youtube.com/watch?v=abc", timeout=1)
    route = {"route_id": "yt-dlp-metadata"}
    attempts: list[AcquisitionAttempt] = []
    expected = {"disposition": "success"}

    monkeypatch.setattr(
        bfs.youtube_browser_ui,
        "run_browser_ui_transcript_stage",
        lambda *_args, **_kwargs: AcquisitionAttempt(
            "youtube-browser-transcript-ui",
            "agent-browser",
            status="success",
            confidence="strong",
            content_text="transcript",
        ),
    )
    monkeypatch.setattr(bfs, "_close_cleanup_error", lambda *_args, **_kwargs: None)
    assert bfs.run_youtube_browser_stage(
        args,
        route,
        attempts,
        proof_required=False,
        script_dir=WEB_FETCH_SCRIPTS,
        run_command=lambda *_args, **_kwargs: ("", None),
        payload_for=lambda *_args, **_kwargs: expected,
    ) is expected
    assert attempts[0].stage_id == "youtube-browser-transcript-ui"


def test_url_reader_decodes_success_response(monkeypatch) -> None:
    class Headers:
        def get_content_charset(self) -> None:
            return None

    class Response:
        headers = Headers()

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def read(self) -> bytes:
            return b"hello ok"

    monkeypatch.setattr(url_reader.urllib.request, "urlopen", lambda *_args, **_kwargs: Response())
    text, error = url_reader.read_url("https://example.com", timeout=1)
    assert error is None
    assert text == "hello ok"


def test_gather_record_rendering_defensive_paths() -> None:
    assert gather_record_rendering.attempt_lines([object()]) == []
    assert gather_record_rendering.is_open_gap(
        {"stage_id": "agent-browser-network-recon", "status": "success"}
    )
    fence = gather_record_rendering._fence_for("``` fenced\n```` longer")
    assert fence == "`````"
    selected, text = gather_record_rendering.selected_content_text({"selected_content": {"text": "   "}})
    assert selected == {"text": "   "}
    assert text is None


def test_acquire_public_url_io_reports_command_exceptions(monkeypatch) -> None:
    def boom(*_args, **_kwargs):
        raise RuntimeError("synthetic failure")

    monkeypatch.setattr(acquire_public_url_io.subprocess, "run", boom)
    stdout, error = acquire_public_url_io.run_command(["demo"], timeout=1)
    assert stdout == ""
    assert error == "RuntimeError:synthetic failure"
