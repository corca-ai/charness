from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
WEB_FETCH_SCRIPTS = ROOT / "skills" / "support" / "web-fetch" / "scripts"
sys.path.insert(0, str(WEB_FETCH_SCRIPTS))

import acquire_public_url as apu  # noqa: E402
import route_public_fetch_routes as rpf_routes  # noqa: E402
from acquisition_trace_lib import AcquisitionAttempt  # noqa: E402


def run_helper(
    script: str,
    *args: str,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, script, *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        input=input_text,
    )


def test_route_public_fetch_maps_reddit_to_feed_strategy() -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/route_public_fetch.py",
        "--url",
        "https://www.reddit.com/r/python/",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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


def test_route_public_fetch_maps_github_to_grant_or_cli_strategy() -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/route_public_fetch.py",
        "--url",
        "https://github.com/openai/openai-python",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    payload = json.loads(result.stdout)
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
    payload = json.loads(result.stdout)
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
    payload = json.loads(result.stdout)
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
    payload = json.loads(result.stdout)
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
    payload = json.loads(result.stdout)
    assert payload["status"] == "login-wall"
    assert "clean-stop" in payload["fallback_candidates"]


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
    payload = json.loads(result.stdout)
    assert payload["status"] == "partial-content"


def test_classify_fetch_response_reports_success_for_long_article_text() -> None:
    article = "<html><body>" + ("useful content " * 120) + "</body></html>"
    result = run_helper(
        "skills/support/web-fetch/scripts/classify_fetch_response.py",
        input_text=article,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    payload = json.loads(result.stdout)
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
    payload = json.loads(result.stdout)
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
    payload = json.loads(result.stdout)
    assert payload["status"] == "login-wall"
    assert payload["confidence"] == "none"
    assert payload["proof"] == [{"type": "text", "value": "needle"}]
