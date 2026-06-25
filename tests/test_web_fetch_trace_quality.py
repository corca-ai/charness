from __future__ import annotations

import json
import os
import subprocess
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB_FETCH_SCRIPTS = ROOT / "skills" / "support" / "web-fetch" / "scripts"
sys.path.insert(0, str(WEB_FETCH_SCRIPTS))

import acquire_public_url  # noqa: E402
import acquire_public_url_policy as policy  # noqa: E402
import classify_fetch_response  # noqa: E402
import impersonated_fetch_stage  # noqa: E402
import patchright_headless_stage  # noqa: E402
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


def test_classify_fetch_response_reports_cloudfront_403_as_error_page() -> None:
    body = """
    <html><body><h1>403 ERROR</h1>
    <p>The request could not be satisfied. Request blocked.</p>
    </body></html>
    """

    result = run_helper(
        "skills/support/web-fetch/scripts/classify_fetch_response.py",
        input_text=body,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "error-page"
    assert payload["confidence"] == "none"


def test_classify_function_reports_soft_captcha_collect_fallbacks() -> None:
    payload = classify_fetch_response.classify("<html><body>robot check</body></html>", intent="collect")

    assert payload["status"] == "captcha"
    assert payload["signals"] == ["captcha"]
    assert payload["matched_signals"] == ["robot"]
    assert payload["fallback_candidates"] == [
        "impersonated-public-fetch",
        "patchright-render",
        "agent-browser-render",
        "patchright-network-recon",
        "agent-browser-network-recon",
        "clean-stop",
    ]


def test_route_public_fetch_declares_headless_fallbacks() -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/route_public_fetch.py",
        "--url",
        "https://example.com/article",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    stage_ids = [stage["stage_id"] for stage in payload["acquisition_plan"]]
    assert stage_ids.index("impersonated-public-fetch") < stage_ids.index("defuddle-reader-extraction")
    assert stage_ids.index("patchright-render-recon") < stage_ids.index("agent-browser-render-recon")


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


def test_impersonated_fetch_stage_can_succeed_with_fake_fetcher() -> None:
    class Args:
        url = "https://example.com/article"
        timeout = 1
        intent = "single"
        expect_text: list[str] = []
        expect_regex: list[str] = []
        expect_json_field: list[str] = []

    attempts: list[AcquisitionAttempt] = []

    def fetcher(url: str, *, timeout: int, impersonate: str):
        assert url == Args.url
        return "<html><body>" + ("useful content " * 120) + "</body></html>", None, {"impersonate": impersonate}

    result = impersonated_fetch_stage.run_impersonated_fetch_stage(
        Args(),
        {"acquisition_plan": []},
        attempts,
        proof_required=False,
        payload_for=lambda _args, _route, stage_attempts, disposition: {"disposition": disposition, "attempts": stage_attempts},
        fetcher=fetcher,
    )

    assert result is not None
    assert result["disposition"] == "success"
    assert attempts[0].stage_id == "impersonated-public-fetch"
    assert attempts[0].tool_id == "curl_cffi"


def test_impersonated_fetch_stage_http_error_status_blocks_long_body() -> None:
    class Args:
        url = "https://example.com/blocked"
        timeout = 1
        intent = "single"
        expect_text: list[str] = []
        expect_regex: list[str] = []
        expect_json_field: list[str] = []

    attempts: list[AcquisitionAttempt] = []

    def fetcher(url: str, *, timeout: int, impersonate: str):
        return "<html><body>" + ("generic long error body " * 120) + "</body></html>", None, {
            "impersonate": impersonate,
            "http_status": 403,
        }

    result = impersonated_fetch_stage.run_impersonated_fetch_stage(
        Args(),
        {"acquisition_plan": []},
        attempts,
        proof_required=False,
        payload_for=lambda _args, _route, stage_attempts, disposition: {"disposition": disposition, "attempts": stage_attempts},
        fetcher=fetcher,
    )

    assert result is None
    assert {attempt.status for attempt in attempts} == {"error-page"}
    assert attempts[0].classification["matched_signals"] == ["http-status:403"]


def test_impersonated_fetch_stage_records_fetch_exceptions() -> None:
    class Args:
        url = "https://example.com/blocked"
        timeout = 1
        intent = "single"
        expect_text: list[str] = []
        expect_regex: list[str] = []
        expect_json_field: list[str] = []

    attempts: list[AcquisitionAttempt] = []

    def fetcher(url: str, *, timeout: int, impersonate: str):
        raise RuntimeError("network blocked")

    result = impersonated_fetch_stage.run_impersonated_fetch_stage(
        Args(),
        {"acquisition_plan": []},
        attempts,
        proof_required=False,
        payload_for=lambda _args, _route, stage_attempts, disposition: {"disposition": disposition, "attempts": stage_attempts},
        fetcher=fetcher,
    )

    assert result is None
    assert len(attempts) == len(impersonated_fetch_stage.IMPERSONATION_PROFILES)
    assert attempts[0].status == "error"
    assert attempts[0].error == "RuntimeError:network blocked"
    assert attempts[0].details == {"impersonate": "chrome120"}


def test_impersonated_default_fetch_records_response_metadata(monkeypatch) -> None:
    class Response:
        status_code = 200
        url = "https://example.com/final"
        text = "article body"

    def get(url: str, *, impersonate: str, timeout: int):
        assert url == "https://example.com/start"
        assert impersonate == "chrome120"
        assert timeout == 3
        return Response()

    fake_curl = types.ModuleType("curl_cffi")
    fake_curl.requests = types.SimpleNamespace(get=get)
    monkeypatch.setitem(sys.modules, "curl_cffi", fake_curl)

    text, error, details = impersonated_fetch_stage._fetch(  # noqa: SLF001
        "https://example.com/start",
        timeout=3,
        impersonate="chrome120",
    )

    assert text == "article body"
    assert error is None
    assert details == {
        "impersonate": "chrome120",
        "http_status": 200,
        "effective_url": "https://example.com/final",
    }


def test_optional_stage_availability_checks(monkeypatch) -> None:
    monkeypatch.setattr(impersonated_fetch_stage.importlib.util, "find_spec", lambda name: object())
    monkeypatch.setattr(patchright_headless_stage.importlib.util, "find_spec", lambda name: object())

    assert impersonated_fetch_stage.is_available() is True
    assert patchright_headless_stage.is_available() is True


def test_patchright_stage_uses_headless_renderer_and_keeps_network_diagnostic() -> None:
    class Args:
        url = "https://example.com/app"
        timeout = 1
        intent = "collect"
        expect_text = ["target proof"]
        expect_regex: list[str] = []
        expect_json_field: list[str] = []

    attempts: list[AcquisitionAttempt] = []

    def renderer(url: str, *, timeout: int, collect_network: bool = False):
        if collect_network:
            return "GET https://example.com/api/items", None, {"headless": True, "network_candidates": ["https://example.com/api/items"]}
        return "rendered target proof from headless patchright", None, {"headless": True, "channel": "chrome"}

    result = patchright_headless_stage.run_patchright_stage(
        Args(),
        {"acquisition_plan": []},
        attempts,
        proof_required=True,
        payload_for=lambda _args, _route, stage_attempts, disposition: {"disposition": disposition, "attempts": stage_attempts},
        renderer=renderer,
    )

    assert result is not None
    assert result["disposition"] == "success"
    assert [attempt.stage_id for attempt in attempts] == ["patchright-render-recon", "patchright-network-recon"]
    assert attempts[0].details["headless"] is True
    assert attempts[1].details["diagnostic"] is True


def test_patchright_stage_http_error_status_blocks_long_body() -> None:
    class Args:
        url = "https://example.com/blocked"
        timeout = 1
        intent = "single"
        expect_text: list[str] = []
        expect_regex: list[str] = []
        expect_json_field: list[str] = []

    attempts: list[AcquisitionAttempt] = []

    def renderer(url: str, *, timeout: int, collect_network: bool = False):
        return "<html><body>" + ("generic long rendered error " * 120) + "</body></html>", None, {
            "headless": True,
            "http_status": 403,
        }

    result = patchright_headless_stage.run_patchright_stage(
        Args(),
        {"acquisition_plan": []},
        attempts,
        proof_required=False,
        payload_for=lambda _args, _route, stage_attempts, disposition: {"disposition": disposition, "attempts": stage_attempts},
        renderer=renderer,
    )

    assert result is None
    assert attempts[0].status == "error-page"
    assert attempts[0].classification["matched_signals"] == ["http-status:403"]


def test_patchright_default_renderer_stays_headless_and_collects_network(monkeypatch) -> None:
    requested_launches: list[dict[str, object]] = []

    class Request:
        url = "https://example.com/api/items.json"

    class Response:
        status = 200

    class Locator:
        def inner_text(self, *, timeout: int) -> str:
            assert timeout == 5000
            return "rendered article"

    class Page:
        def on(self, event: str, callback):
            assert event == "request"
            callback(Request())

        def goto(self, url: str, *, wait_until: str, timeout: int):
            assert url == "https://example.com/app"
            assert wait_until == "domcontentloaded"
            assert timeout == 10000
            return Response()

        def wait_for_timeout(self, timeout: int) -> None:
            assert timeout == 1000

        def locator(self, selector: str) -> Locator:
            assert selector == "body"
            return Locator()

    class Context:
        def new_page(self) -> Page:
            return Page()

    class Browser:
        def __init__(self) -> None:
            self.closed = False

        def new_context(self) -> Context:
            return Context()

        def close(self) -> None:
            self.closed = True

    browser = Browser()

    class Chromium:
        def launch(self, **kwargs):
            requested_launches.append(kwargs)
            return browser

    class Playwright:
        chromium = Chromium()

    class SyncPlaywright:
        def __enter__(self) -> Playwright:
            return Playwright()

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

    fake_sync_api = types.ModuleType("patchright.sync_api")
    fake_sync_api.sync_playwright = SyncPlaywright
    monkeypatch.setitem(sys.modules, "patchright", types.ModuleType("patchright"))
    monkeypatch.setitem(sys.modules, "patchright.sync_api", fake_sync_api)

    text, error, details = patchright_headless_stage._render(  # noqa: SLF001
        "https://example.com/app",
        timeout=10,
        collect_network=True,
    )

    assert text == "rendered article"
    assert error is None
    assert details == {
        "headless": True,
        "channel": "chrome",
        "http_status": 200,
        "locale": "browser-default",
        "timezone_id": "browser-default",
        "network_candidates": ["https://example.com/api/items.json"],
    }
    assert requested_launches == [{"headless": True, "channel": "chrome"}]
    assert browser.closed is True


def test_patchright_default_renderer_closes_browser_after_render_error(monkeypatch) -> None:
    close_calls = 0

    class Page:
        def goto(self, url: str, *, wait_until: str, timeout: int):
            raise RuntimeError("blocked")

    class Context:
        def new_page(self) -> Page:
            return Page()

    class Browser:
        def new_context(self) -> Context:
            return Context()

        def close(self) -> None:
            nonlocal close_calls
            close_calls += 1
            raise RuntimeError("close failed")

    class Chromium:
        def launch(self, **kwargs):
            return Browser()

    class Playwright:
        chromium = Chromium()

    class SyncPlaywright:
        def __enter__(self) -> Playwright:
            return Playwright()

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

    fake_sync_api = types.ModuleType("patchright.sync_api")
    fake_sync_api.sync_playwright = SyncPlaywright
    monkeypatch.setitem(sys.modules, "patchright", types.ModuleType("patchright"))
    monkeypatch.setitem(sys.modules, "patchright.sync_api", fake_sync_api)

    text, error, details = patchright_headless_stage._render(  # noqa: SLF001
        "https://example.com/app",
        timeout=1,
    )

    assert text == ""
    assert error is not None
    assert error.startswith("bundled-chromium:RuntimeError:")
    assert details == {"headless": True}
    assert close_calls == 2


def test_headless_policy_reports_missing_optional_packages(monkeypatch) -> None:
    attempts = [AcquisitionAttempt(stage_id="direct-public-fetch", tool_id=None, status="error-page")]

    monkeypatch.setattr(policy.importlib.util, "find_spec", lambda name: None)

    assert policy.should_try_impersonated_fetch(
        "direct-then-fallback",
        attempts,
        seeded_direct=False,
    ) == (False, "missing-tool")
    assert policy.should_try_patchright(
        "direct-then-fallback",
        attempts,
        browser_mode="auto",
        seeded_direct=False,
    ) == (False, "missing-tool")


def test_headless_policy_allows_available_optional_packages(monkeypatch) -> None:
    attempts = [AcquisitionAttempt(stage_id="direct-public-fetch", tool_id=None, status="error-page")]

    monkeypatch.setattr(policy.importlib.util, "find_spec", lambda name: object())

    assert policy.should_try_impersonated_fetch(
        "direct-then-fallback",
        attempts,
        seeded_direct=False,
    ) == (True, None)
    assert policy.should_try_patchright(
        "direct-then-fallback",
        attempts,
        browser_mode="always",
        seeded_direct=False,
    ) == (True, None)
    assert policy.should_try_patchright(
        "direct-then-fallback",
        attempts,
        browser_mode="auto",
        seeded_direct=False,
    ) == (True, None)


def test_headless_policy_respects_sufficient_prior_stage(monkeypatch) -> None:
    attempts = [AcquisitionAttempt(stage_id="direct-public-fetch", tool_id=None, status="success", confidence="weak")]

    monkeypatch.setattr(policy.importlib.util, "find_spec", lambda name: object())

    assert policy.should_try_impersonated_fetch(
        "direct-then-fallback",
        attempts,
        seeded_direct=False,
    ) == (False, "prior-stage-sufficient")
    assert policy.should_try_patchright(
        "direct-then-fallback",
        attempts,
        browser_mode="auto",
        seeded_direct=False,
    ) == (False, "prior-stage-sufficient")


def test_headless_policy_requires_prior_content_unless_browser_always(monkeypatch) -> None:
    monkeypatch.setattr(policy.importlib.util, "find_spec", lambda name: object())

    assert policy.should_try_patchright(
        "direct-then-fallback",
        [],
        browser_mode="auto",
        seeded_direct=False,
    ) == (False, "no-prior-content")


def test_acquire_returns_impersonated_payload_when_stage_succeeds(monkeypatch) -> None:
    args = types.SimpleNamespace(
        url="https://example.com/article",
        timeout=1,
        intent="single",
        expect_text=[],
        expect_regex=[],
        expect_json_field=[],
        repo_root=ROOT,
        direct_response_file=None,
        browser_mode="auto",
        include_selected_content=False,
        selected_content_max_chars=None,
    )
    route = {
        "route_id": "direct-then-fallback",
        "acquisition_plan": [
            {"stage_id": "direct-public-fetch", "tool_id": None},
            {"stage_id": "impersonated-public-fetch", "tool_id": "curl_cffi"},
        ],
    }

    def run_stage(stage_args, stage_route, attempts, *, proof_required, payload_for):
        attempts.append(
            AcquisitionAttempt(
                stage_id="impersonated-public-fetch",
                tool_id="curl_cffi",
                status="success",
                confidence="weak",
            )
        )
        return payload_for(stage_args, stage_route, attempts, "success")

    monkeypatch.setattr(acquire_public_url, "route_for_url", lambda url, repo_root: route)
    monkeypatch.setattr(acquire_public_url, "_read_direct", lambda *args, **kwargs: ("", "direct blocked"))
    monkeypatch.setattr(acquire_public_url, "_should_try_impersonated_fetch", lambda *args, **kwargs: (True, None))
    monkeypatch.setattr(acquire_public_url.impersonated_fetch_stage, "run_impersonated_fetch_stage", run_stage)

    payload = acquire_public_url.acquire(args)

    assert payload["disposition"] == "success"
    assert payload["selected_attempt"]["stage_id"] == "impersonated-public-fetch"


def test_acquire_returns_patchright_payload_when_stage_succeeds(monkeypatch) -> None:
    args = types.SimpleNamespace(
        url="https://example.com/article",
        timeout=1,
        intent="single",
        expect_text=[],
        expect_regex=[],
        expect_json_field=[],
        repo_root=ROOT,
        direct_response_file=None,
        browser_mode="auto",
        include_selected_content=False,
        selected_content_max_chars=None,
    )
    route = {
        "route_id": "direct-then-fallback",
        "acquisition_plan": [
            {"stage_id": "direct-public-fetch", "tool_id": None},
            {"stage_id": "patchright-render-recon", "tool_id": "patchright"},
        ],
    }

    def run_stage(stage_args, stage_route, attempts, *, proof_required, payload_for):
        attempts.append(
            AcquisitionAttempt(
                stage_id="patchright-render-recon",
                tool_id="patchright",
                status="success",
                confidence="weak",
            )
        )
        return payload_for(stage_args, stage_route, attempts, "success")

    monkeypatch.setattr(acquire_public_url, "route_for_url", lambda url, repo_root: route)
    monkeypatch.setattr(acquire_public_url, "_read_direct", lambda *args, **kwargs: ("", "direct blocked"))
    monkeypatch.setattr(acquire_public_url, "_should_try_impersonated_fetch", lambda *args, **kwargs: (False, "missing-tool"))
    monkeypatch.setattr(acquire_public_url, "_try_defuddle_reader", lambda *args, **kwargs: None)
    monkeypatch.setattr(acquire_public_url, "_should_try_patchright", lambda *args, **kwargs: (True, None))
    monkeypatch.setattr(acquire_public_url.patchright_headless_stage, "run_patchright_stage", run_stage)

    payload = acquire_public_url.acquire(args)

    assert payload["disposition"] == "success"
    assert payload["selected_attempt"]["stage_id"] == "patchright-render-recon"
