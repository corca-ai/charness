from __future__ import annotations

import json
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest
import yaml

from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]


def run_helper(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    module = load_script_module(
        f"web_fetch_content_{Path(script).stem}", ROOT / script
    )
    previous_cwd = Path.cwd()
    try:
        os.chdir(ROOT)
        result = run_loaded_script_main(script, module, *args)
    finally:
        os.chdir(previous_cwd)
    return subprocess.CompletedProcess(
        [script, *args], result.returncode, result.stdout, result.stderr
    )


class _MarkdownNegotiationHandler(BaseHTTPRequestHandler):
    accepts: list[str] = []

    def do_GET(self) -> None:  # noqa: N802
        accept = self.headers.get("Accept", "")
        self.accepts.append(accept)
        if "text/markdown" in accept:
            body = b"# Public Markdown\nmarkdown body\n"
        else:
            body = b"<html><body><h1>Sign in</h1><p>Please login to continue.</p></body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/markdown; charset=utf-8" if "text/markdown" in accept else "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: object) -> None:
        return


def test_gather_public_url_negotiates_markdown_after_html_login_wall(tmp_path: Path) -> None:
    _MarkdownNegotiationHandler.accepts = []
    server = HTTPServer(("127.0.0.1", 0), _MarkdownNegotiationHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/article"
        result = run_helper(
            "skills/public/gather/scripts/gather_public_url.py",
            "--repo-root",
            str(tmp_path),
            "--url",
            url,
            "--expect-text",
            "markdown body",
            "--browser-mode",
            "off",
            "--slug",
            "negotiated-markdown",
            "--date",
            "2026-08-06",
            "--persist-extracted-content",
            "--execute",
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["acquisition_disposition"] == "success"
    assert payload["final_status"] == "success"
    assert payload["content_persistence"] == "extracted"
    assert payload["acquisition"]["selected_attempt"]["stage_id"] == "content-negotiated-markdown"
    assert "text/markdown" in _MarkdownNegotiationHandler.accepts
    record = Path(payload["write_record"]["record_artifact_path"]).read_text(encoding="utf-8")
    assert "markdown body" in record


def test_gather_public_url_does_not_persist_raw_json_response(tmp_path: Path) -> None:
    direct = tmp_path / "direct.json"
    direct.write_text(
        json.dumps({"title": "Readable Title", "body": "secret API body should not persist"}),
        encoding="utf-8",
    )

    result = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://example.com/api/article",
        "--direct-response-file",
        str(direct),
        "--expect-json-field",
        "title",
        "--browser-mode",
        "off",
        "--slug",
        "example-json-url",
        "--date",
        "2026-05-16",
        "--persist-extracted-content",
        "--execute",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["content_persistence"] == "unavailable"
    assert "selected_content" not in payload["acquisition"]
    record = Path(payload["write_record"]["record_artifact_path"]).read_text(encoding="utf-8")
    assert "- Content Persistence: `unavailable`" in record
    assert "## Extracted Content" not in record
    assert "secret API body should not persist" not in record


def test_gather_public_url_rejects_non_positive_content_limit(tmp_path: Path) -> None:
    result = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://example.com/article",
        "--persist-extracted-content",
        "--max-extracted-content-chars",
        "0",
    )

    assert result.returncode == 2
    assert "must be a positive integer" in result.stderr


@pytest.mark.parametrize(
    ("filename", "body", "url", "expect"),
    [
        pytest.param(
            "direct.json",
            json.dumps({"title": "Readable Title", "body": "secret API body should not persist"}),
            "https://example.com/api/article",
            ("--expect-json-field", "title"),
            id="json",
        ),
        pytest.param(
            "direct.ndjson",
            '{"title":"Readable Title"}\n{"body":"secret NDJSON body should not persist"}',
            "https://example.com/api/stream",
            ("--expect-text", "Readable Title"),
            id="ndjson",
        ),
        pytest.param(
            "direct.json",
            '\ufeff{"title":"Readable Title","body":"secret BOM JSON body should not persist"}',
            "https://example.com/api/article",
            ("--expect-text", "Readable Title"),
            id="bom-json",
        ),
        pytest.param(
            "direct.txt",
            ")]}'\n" + json.dumps({"title": "Readable Title", "body": "secret XSSI body should not persist"}),
            "https://example.com/api/xssi",
            ("--expect-text", "Readable Title"),
            id="xssi-json",
        ),
        pytest.param(
            "direct.js",
            'callback({"title":"Readable Title","body":"secret JSONP body should not persist"});',
            "https://example.com/api/jsonp",
            ("--expect-text", "Readable Title"),
            id="jsonp",
        ),
        pytest.param(
            "direct.js",
            'window.__DATA__={"title":"Readable Title","body":"secret JS body should not persist"};',
            "https://example.com/api/data",
            ("--expect-text", "Readable Title"),
            id="js-assignment",
        ),
    ],
)
def test_acquire_public_url_does_not_include_raw_structured_selected_content(
    tmp_path: Path,
    filename: str,
    body: str,
    url: str,
    expect: tuple[str, str],
) -> None:
    """`--include-selected-content` still refuses JSON-shaped bodies, every encoding door."""
    direct = tmp_path / filename
    direct.write_text(body, encoding="utf-8")
    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        url,
        "--direct-response-file",
        str(direct),
        *expect,
        "--browser-mode",
        "off",
        "--include-selected-content",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "success"
    assert "selected_content" not in payload


def test_acquire_public_url_can_persist_plain_text_starting_with_bracket(tmp_path: Path) -> None:
    direct = tmp_path / "direct.txt"
    direct.write_text("[Update] " + ("readable article text " * 80), encoding="utf-8")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/plain-text",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "off",
        "--include-selected-content",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "success"
    assert payload["selected_content"]["text"].startswith("[Update]")


def test_acquire_public_url_rejects_non_positive_content_limit(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>" + ("useful content " * 120) + "</body></html>", encoding="utf-8")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--include-selected-content",
        "--selected-content-max-chars",
        "-1",
    )

    assert result.returncode == 2
    assert "must be a positive integer" in result.stderr
