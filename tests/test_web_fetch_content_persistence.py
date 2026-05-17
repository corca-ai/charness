from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_helper(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, script, *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


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
    payload = json.loads(result.stdout)
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


def test_acquire_public_url_does_not_include_raw_json_selected_content(tmp_path: Path) -> None:
    direct = tmp_path / "direct.json"
    direct.write_text(
        json.dumps({"title": "Readable Title", "body": "secret API body should not persist"}),
        encoding="utf-8",
    )

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/api/article",
        "--direct-response-file",
        str(direct),
        "--expect-json-field",
        "title",
        "--browser-mode",
        "off",
        "--include-selected-content",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "success"
    assert payload["selected_attempt"]["stage_id"] == "direct-public-fetch"
    assert "selected_content" not in payload


def test_acquire_public_url_does_not_include_raw_ndjson_selected_content(tmp_path: Path) -> None:
    direct = tmp_path / "direct.ndjson"
    direct.write_text(
        '{"title":"Readable Title"}\n{"body":"secret NDJSON body should not persist"}',
        encoding="utf-8",
    )

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/api/stream",
        "--direct-response-file",
        str(direct),
        "--expect-text",
        "Readable Title",
        "--browser-mode",
        "off",
        "--include-selected-content",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "success"
    assert "selected_content" not in payload


def test_acquire_public_url_does_not_include_bom_json_selected_content(tmp_path: Path) -> None:
    direct = tmp_path / "direct.json"
    direct.write_text(
        '\ufeff{"title":"Readable Title","body":"secret BOM JSON body should not persist"}',
        encoding="utf-8",
    )

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/api/article",
        "--direct-response-file",
        str(direct),
        "--expect-text",
        "Readable Title",
        "--browser-mode",
        "off",
        "--include-selected-content",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "success"
    assert "selected_content" not in payload


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
