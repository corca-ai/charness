from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB_FETCH_SCRIPTS = ROOT / "skills" / "support" / "web-fetch" / "scripts"
sys.path.insert(0, str(WEB_FETCH_SCRIPTS))

from acquisition_trace_lib import AcquisitionAttempt  # noqa: E402
from acquisition_trace_lib import payload as acquisition_payload  # noqa: E402


def run_helper(
    script: str,
    *args: str,
    input_text: str | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, script, *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        input=input_text,
        env=env,
    )


def test_classify_fetch_response_treats_soft_robot_marker_as_content_when_page_is_long() -> None:
    article = "<html><body><h1>Robotics notes</h1>" + ("robot architecture reference " * 120) + "</body></html>"

    result = run_helper(
        "skills/support/web-fetch/scripts/classify_fetch_response.py",
        input_text=article,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "success"
    assert payload["confidence"] == "weak"


def test_classify_fetch_response_keeps_long_captcha_challenge_blocked() -> None:
    challenge = "<html><body><h1>Captcha</h1>" + ("captcha verify " * 120) + "</body></html>"

    result = run_helper(
        "skills/support/web-fetch/scripts/classify_fetch_response.py",
        input_text=challenge,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "captcha"
    assert payload["confidence"] == "none"


def test_acquire_public_url_records_missing_capabilities_and_untried_routes(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><head><meta property=\"og:title\" content=\"Example\"></head></html>", encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = str(tmp_path / "empty-bin")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "auto",
        env=env,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["missing_capabilities"] == ["defuddle", "agent-browser"]
    assert {
        (route["stage_id"], route["tool_id"], route["reason"])
        for route in payload["untried_routes"]
    } >= {
        ("defuddle-reader-extraction", "defuddle", "missing-tool"),
        ("agent-browser-render-recon", "agent-browser", "missing-tool"),
        ("archive-or-cache", None, "not-implemented"),
    }


def test_acquire_public_url_omits_missing_capabilities_after_later_success() -> None:
    route = {
        "acquisition_plan": [
            {"stage_id": "defuddle-reader-extraction", "tool_id": "defuddle"},
            {"stage_id": "agent-browser-render-recon", "tool_id": "agent-browser"},
            {"stage_id": "archive-or-cache", "tool_id": None},
            {"stage_id": "clean-stop", "tool_id": None},
        ]
    }
    attempts = [
        AcquisitionAttempt(
            stage_id="defuddle-reader-extraction",
            tool_id="defuddle",
            status="skipped",
            details={"reason": "missing-tool"},
        ),
        AcquisitionAttempt(
            stage_id="agent-browser-render-recon",
            tool_id="agent-browser",
            status="success",
            confidence="strong",
        ),
    ]

    payload = acquisition_payload("https://example.com/article", route, attempts, "success")

    assert payload["selected_attempt"]["stage_id"] == "agent-browser-render-recon"
    assert "missing_capabilities" not in payload
    assert "untried_routes" not in payload
