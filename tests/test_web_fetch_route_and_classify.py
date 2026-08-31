from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

from runtime_bootstrap import load_path_module
from tests.quality_gates.support import run_script

ROOT = Path(__file__).resolve().parents[1]
WEB_FETCH_SCRIPTS = ROOT / "skills" / "support" / "web-fetch" / "scripts"
sys.path.insert(0, str(WEB_FETCH_SCRIPTS))

_acquire_public_url_io_surface = load_path_module(
    "acquire_public_url_io_test_surface",
    ROOT / "skills" / "support" / "web-fetch" / "scripts" / "acquire_public_url_io.py",
)
_markdown_negotiation_stage_surface = load_path_module(
    "markdown_negotiation_stage_test_surface",
    ROOT / "skills" / "support" / "web-fetch" / "scripts" / "markdown_negotiation_stage.py",
)
_route_stage_catalog_surface = load_path_module(
    "route_stage_catalog_test_surface",
    ROOT / "skills" / "support" / "web-fetch" / "scripts" / "route_stage_catalog.py",
)

import acquire_public_url as apu  # noqa: E402
import classify_fetch_response as cfr  # noqa: E402
import route_public_fetch_routes as rpf_routes  # noqa: E402
from acquisition_trace_lib import AcquisitionAttempt  # noqa: E402


def run_helper(
    script: str,
    *args: str,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    if input_text is None:
        return run_script(script, *args, cwd=ROOT)
    return subprocess.run(
        [sys.executable, script, *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        input=input_text,
    )


def test_split_web_fetch_modules_are_bound_to_a_standing_surface() -> None:
    assert _acquire_public_url_io_surface.MARKDOWN_ACCEPT == apu.acquire_public_url_io.MARKDOWN_ACCEPT
    assert _markdown_negotiation_stage_surface._markdown_looking_url("https://example.com/read.md")
    assert _route_stage_catalog_surface.FALLBACK_ORDER[0] == "direct-public-fetch"


def test_route_public_fetch_maps_reddit_to_feed_strategy() -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/route_public_fetch.py",
        "--url",
        "https://www.reddit.com/r/python/",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["normalized_host"] == "reddit.com"
    assert payload["route_id"] == "reddit-feed"
    assert payload["route_family"] == "public-api"
    assert payload["required_tools"] == []
    assert [stage["stage_id"] for stage in payload["acquisition_plan"][:2]] == [
        "domain-specific-route",
        "direct-public-fetch",
    ]


def test_route_public_fetch_missing_gather_adapter_fallback(monkeypatch) -> None:
    monkeypatch.setattr(rpf_routes.Path, "is_file", lambda _self: False)
    assert str(rpf_routes._find_gather_adapter_script()) == "__missing_gather_resolve_adapter__.py"


def test_route_public_fetch_github_mode_fallbacks(monkeypatch, tmp_path: Path) -> None:
    assert rpf_routes.resolve_github_mode(None) == "direct-cli"

    monkeypatch.setattr(rpf_routes, "_find_gather_adapter_script", lambda: Path("__missing__.py"))
    assert rpf_routes.resolve_github_mode(tmp_path) == "direct-cli"

    adapter_script = tmp_path / "resolve_adapter.py"
    adapter_script.write_text(
        "def load_adapter(repo_root):\n    raise RuntimeError('adapter unavailable')\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(rpf_routes, "_find_gather_adapter_script", lambda: adapter_script)
    assert rpf_routes.resolve_github_mode(tmp_path) == "direct-cli"

    monkeypatch.setattr(rpf_routes.importlib.util, "spec_from_file_location", lambda *_args, **_kwargs: None)
    assert rpf_routes.resolve_github_mode(tmp_path) == "direct-cli"


def test_route_public_fetch_route_id_for_host_edge_domains() -> None:
    assert rpf_routes.route_id_for_host("news.ycombinator.com", github_mode="direct-cli") == "hacker-news-firebase"
    assert rpf_routes.route_id_for_host("stackoverflow.com", github_mode="direct-cli") == "stackexchange-api"
    assert rpf_routes.route_id_for_host("blog.naver.com", github_mode="direct-cli") == "naver-blog-mobile"


def test_acquire_helper_browser_branch_payloads(monkeypatch) -> None:
    args = SimpleNamespace(
        browser_mode="auto",
        intent="single",
        url="https://www.youtube.com/watch?v=abc",
        timeout=1,
        repo_root=Path("."),
    )
    route = {"route_id": "yt-dlp-metadata", "acquisition_plan": [{"stage_id": "youtube-browser-transcript-ui"}]}
    attempts: list[AcquisitionAttempt] = []
    expected = {"disposition": "success"}
    monkeypatch.setattr(apu, "_should_try_youtube_browser", lambda *_args, **_kwargs: (True, None))
    monkeypatch.setattr(apu.browser_fallback_stages, "run_youtube_browser_stage", lambda *_args, **_kwargs: expected)
    assert apu._try_youtube_browser_payload(args, route, attempts, proof_required=False) is expected


def test_acquire_helper_skip_branches(monkeypatch) -> None:
    args = SimpleNamespace(browser_mode="off", intent="collect", url="https://example.com", timeout=1)
    attempts: list[AcquisitionAttempt] = []
    youtube_route = {
        "route_id": "yt-dlp-metadata",
        "acquisition_plan": [{"stage_id": "youtube-browser-transcript-ui", "tool_id": "agent-browser"}],
    }
    monkeypatch.setattr(apu, "_should_try_youtube_browser", lambda *_args, **_kwargs: (False, "browser-mode-off"))
    assert apu._try_youtube_browser_payload(args, youtube_route, attempts, proof_required=False) is None
    assert attempts[-1].stage_id == "youtube-browser-transcript-ui"

    generic_route = {
        "route_id": "direct-then-fallback",
        "acquisition_plan": [
            {"stage_id": "agent-browser-render-recon", "tool_id": "agent-browser"},
            {"stage_id": "agent-browser-network-recon", "tool_id": "agent-browser"},
        ],
    }
    monkeypatch.setattr(apu, "_should_try_browser", lambda *_args, **_kwargs: (False, "missing-tool"))
    assert apu._try_generic_browser_payload(args, generic_route, attempts, proof_required=False) is None
    assert [attempt.stage_id for attempt in attempts[-2:]] == [
        "agent-browser-render-recon",
        "agent-browser-network-recon",
    ]


def test_acquire_returns_youtube_browser_payload(monkeypatch, tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>short</body></html>", encoding="utf-8")
    args = SimpleNamespace(
        url="https://www.youtube.com/watch?v=abc",
        repo_root=tmp_path,
        intent="single",
        browser_mode="auto",
        timeout=1,
        direct_response_file=direct,
        domain_route_response_file=None,
        live_domain_route=False,
        expect_text=[],
        expect_regex=[],
        expect_json_field=[],
        include_selected_content=False,
        selected_content_max_chars=200_000,
    )
    expected = {"disposition": "success", "source_identity": "youtube-browser-transcript"}
    monkeypatch.setattr(apu, "_run_domain_specific_route", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(apu, "_direct_attempt_sufficient", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(apu, "_try_youtube_browser_payload", lambda *_args, **_kwargs: expected)
    assert apu.acquire(args) is expected


def _markdown_retry_args(tmp_path: Path) -> SimpleNamespace:
    return SimpleNamespace(
        url="https://example.com/article",
        repo_root=tmp_path,
        intent="single",
        browser_mode="off",
        timeout=1,
        direct_response_file=None,
        domain_route_response_file=None,
        live_domain_route=False,
        expect_text=["markdown body"],
        expect_regex=[],
        expect_json_field=[],
        include_selected_content=False,
        selected_content_max_chars=200_000,
    )


def test_acquire_retries_public_markdown_after_direct_login_wall(monkeypatch, tmp_path: Path) -> None:
    args = _markdown_retry_args(tmp_path)
    calls: list[str | None] = []

    def fake_read_direct(url: str, *, timeout: int, direct_response_file: Path | None, accept: str = apu.acquire_public_url_io.HTML_ACCEPT):
        calls.append(accept if direct_response_file is None else "seeded")
        if accept == apu.acquire_public_url_io.MARKDOWN_ACCEPT:
            return "# Public Markdown\nmarkdown body", None
        return "<html><body>Sign in to continue</body></html>", None

    monkeypatch.setattr(apu, "_read_direct", fake_read_direct)
    monkeypatch.setattr(apu, "_run_domain_specific_route", lambda *_args, **_kwargs: None)

    payload = apu.acquire(args)

    assert calls == [apu.acquire_public_url_io.HTML_ACCEPT, apu.acquire_public_url_io.MARKDOWN_ACCEPT]
    assert payload["disposition"] == "success"
    assert payload["selected_attempt"]["stage_id"] == "content-negotiated-markdown"
    markdown_attempt = payload["attempts"][1]
    assert markdown_attempt["details"]["representation"] == "markdown"
    assert markdown_attempt["details"]["route"] == "content-negotiated-markdown"
    assert markdown_attempt["details"]["trigger"] == "direct-login-wall"


def test_acquire_keeps_failed_markdown_retry_blocked(monkeypatch, tmp_path: Path) -> None:
    args = _markdown_retry_args(tmp_path)

    def fake_read_direct(url: str, *, timeout: int, direct_response_file: Path | None, accept: str = apu.acquire_public_url_io.HTML_ACCEPT):
        return "<html><body>Sign in to continue</body></html>", None

    monkeypatch.setattr(apu, "_read_direct", fake_read_direct)
    monkeypatch.setattr(apu, "_run_domain_specific_route", lambda *_args, **_kwargs: None)

    payload = apu.acquire(args)

    assert payload["disposition"] == "blocked"
    assert [attempt["stage_id"] for attempt in payload["attempts"]][:2] == [
        "direct-public-fetch",
        "content-negotiated-markdown",
    ]
    assert payload["attempts"][1]["details"]["representation"] == "markdown"


def test_acquire_retries_markdown_before_domain_route_failure(monkeypatch, tmp_path: Path) -> None:
    args = _markdown_retry_args(tmp_path)
    args.url = "https://news.ycombinator.com/item?id=123"
    calls: list[str | None] = []

    def fake_read_direct(url: str, *, timeout: int, direct_response_file: Path | None, accept: str = apu.acquire_public_url_io.HTML_ACCEPT):
        calls.append(accept if direct_response_file is None else "seeded")
        return "<html><body>Sign in to continue</body></html>", None

    def domain_error(_args, _route, attempts) -> None:
        attempts.append(AcquisitionAttempt(stage_id="domain-specific-route", tool_id="curl", status="error"))

    monkeypatch.setattr(apu, "_read_direct", fake_read_direct)
    monkeypatch.setattr(apu, "_run_domain_specific_route", domain_error)

    payload = apu.acquire(args)

    assert calls == [apu.acquire_public_url_io.HTML_ACCEPT, apu.acquire_public_url_io.MARKDOWN_ACCEPT]
    assert payload["disposition"] == "degraded"
    assert [attempt["stage_id"] for attempt in payload["attempts"]][:3] == [
        "direct-public-fetch",
        "content-negotiated-markdown",
        "domain-specific-route",
    ]


def test_route_plan_places_markdown_before_domain_fallback() -> None:
    stage_ids = [
        stage["stage_id"]
        for stage in apu.route_for_url("https://news.ycombinator.com/item?id=123")["acquisition_plan"]
    ]
    assert stage_ids.index("direct-public-fetch") < stage_ids.index("content-negotiated-markdown")
    assert stage_ids.index("content-negotiated-markdown") < stage_ids.index("domain-specific-route")


def test_route_public_fetch_maps_github_to_grant_or_cli_strategy() -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/route_public_fetch.py",
        "--url",
        "https://github.com/openai/openai-python",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["route_id"] == "github-grant-or-cli"
    assert payload["access_modes"][:2] == ["grant", "binary"]
    assert payload["github_mode"] == "direct-cli"


def test_route_public_fetch_honors_host_mediated_github_mode(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "gather-adapter.yaml").write_text(
        "version: 1\nrepo: demo\ngather_provider:\n  github:\n    mode: host-mediated\n",
        encoding="utf-8",
    )
    result = run_helper(
        "skills/support/web-fetch/scripts/route_public_fetch.py",
        "--url",
        "https://github.com/openai/openai-python",
        "--repo-root",
        str(tmp_path),
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["route_id"] == "github-host-mediated"
    assert "gh" not in payload["required_tools"]
    assert payload["github_mode"] == "host-mediated"


def test_route_public_fetch_honors_none_github_mode(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "gather-adapter.yaml").write_text(
        "version: 1\nrepo: demo\ngather_provider:\n  github:\n    mode: 'none'\n",
        encoding="utf-8",
    )
    result = run_helper(
        "skills/support/web-fetch/scripts/route_public_fetch.py",
        "--url",
        "https://github.com/openai/openai-python",
        "--repo-root",
        str(tmp_path),
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["route_id"] == "github-missing-capability"
    assert "gh" not in payload["required_tools"]
    assert payload["github_mode"] == "none"


def test_route_public_fetch_maps_naver_news_to_reader_fallback() -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/route_public_fetch.py",
        "--url",
        "https://news.naver.com/main/read.naver?oid=001&aid=001",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["route_id"] == "reader-fallback"
    stage_ids = [stage["stage_id"] for stage in payload["acquisition_plan"]]
    assert "defuddle-reader-extraction" in stage_ids
    assert "agent-browser-render-recon" in stage_ids
    assert "agent-browser-network-recon" in stage_ids


def test_route_public_fetch_youtube_declares_ui_transcript_stage() -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/route_public_fetch.py",
        "--url",
        "https://www.youtube.com/watch?v=abc123",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["route_id"] == "yt-dlp-metadata"
    stage_ids = [stage["stage_id"] for stage in payload["acquisition_plan"]]
    assert "domain-specific-route" in stage_ids
    assert "youtube-browser-transcript-ui" in stage_ids
    assert "agent-browser-render-recon" not in stage_ids


def test_classify_fetch_response_reports_login_wall() -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/classify_fetch_response.py",
        input_text="<html><body><h1>Sign in</h1><p>Please login to continue.</p></body></html>",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "login-wall"
    assert "clean-stop" in payload["fallback_candidates"]


def test_classify_fetch_response_token_aware_login_markers() -> None:
    long_content = " useful content" * 120
    cases = (
        ("design intent", "success", []),
        ("Design in the AI era", "success", []),
        ("Sign in", "login-wall", ["sign in"]),
        ("Please log in", "login-wall", ["log in"]),
        ("sign-in", "login-wall", ["sign in"]),
        ("log-in", "login-wall", ["log in"]),
        ("login", "login-wall", ["login"]),
        ("로그인", "login-wall", ["로그인"]),
        ("loginpage", "success", []),
        ("로그인페이지", "success", []),
        ("assign-in", "success", []),
        ("sign--in", "success", []),
        ("sign - in", "success", []),
        ("log---in", "success", []),
        ("Sign <span>in</span>", "login-wall", ["sign in"]),
    )

    for marker, expected_status, expected_matched_signals in cases:
        result = cfr.classify(f"<html><body>{marker}{long_content}</body></html>")
        assert result["status"] == expected_status, marker
        assert result["matched_signals"] == expected_matched_signals, marker


def test_classify_fetch_response_reports_partial_content_for_og_only_page() -> None:
    html_text = """
    <html>
      <head>
        <meta property="og:title" content="Example" />
        <meta property="og:description" content="Summary" />
      </head>
      <body></body>
    </html>
    """
    result = run_helper(
        "skills/support/web-fetch/scripts/classify_fetch_response.py",
        input_text=html_text,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "partial-content"


def test_classify_fetch_response_reports_success_for_long_article_text() -> None:
    article = "<html><body>" + ("useful content " * 120) + "</body></html>"
    result = run_helper(
        "skills/support/web-fetch/scripts/classify_fetch_response.py",
        input_text=article,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "success"
    assert payload["confidence"] == "weak"


def test_classify_fetch_response_reports_strong_success_for_expected_text() -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/classify_fetch_response.py",
        "--expect-text",
        "needle",
        input_text="<html><body>short needle page</body></html>",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "success"
    assert payload["confidence"] == "strong"
    assert payload["proof"] == [{"type": "text", "value": "needle"}]


def test_classify_fetch_response_rejects_invalid_regex_proof() -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/classify_fetch_response.py",
        "--expect-regex",
        "[",
        input_text="<html><body>useful content</body></html>",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "invalid-proof"
    assert payload["confidence"] == "none"
    assert payload["proof_errors"] == [{"type": "invalid-regex", "value": "["}]


def test_classify_fetch_response_blocker_signals_outrank_positive_proof() -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/classify_fetch_response.py",
        "--expect-text",
        "needle",
        input_text="<html><body><h1>Sign in</h1><p>needle</p></body></html>",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "login-wall"
    assert payload["confidence"] == "none"
    assert payload["proof"] == [{"type": "text", "value": "needle"}]
