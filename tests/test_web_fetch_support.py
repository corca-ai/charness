from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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


def test_route_public_fetch_maps_reddit_to_json_strategy() -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/route_public_fetch.py",
        "--url",
        "https://www.reddit.com/r/python/",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["normalized_host"] == "reddit.com"
    assert payload["route_id"] == "reddit-json"
    assert payload["route_family"] == "public-api"


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


def test_acquire_public_url_rejects_non_http_scheme(tmp_path: Path) -> None:
    local_file = tmp_path / "secret.txt"
    local_file.write_text("not public", encoding="utf-8")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        local_file.as_uri(),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "error"
    assert payload["route"]["route_id"] == "invalid-url-scheme"
    assert [attempt["stage_id"] for attempt in payload["attempts"]] == ["input-validation"]


def test_acquire_public_url_invalid_regex_never_succeeds(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>" + ("useful content " * 120) + "</body></html>", encoding="utf-8")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--expect-regex",
        "[",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "error"
    assert payload["selected_attempt"]["status"] == "invalid-proof"


def test_acquire_public_url_uses_defuddle_after_weak_direct_fetch(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "defuddle").write_text(
        "#!/bin/sh\nif [ \"$1\" = parse ] && [ \"$3\" = --markdown ]; then printf 'clean markdown with target proof\\n'; else exit 64; fi\n",
        encoding="utf-8",
    )
    (bin_dir / "defuddle").chmod(0o755)
    direct = tmp_path / "direct.html"
    direct.write_text("<html><head><meta property=\"og:title\" content=\"Example\"></head></html>", encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--expect-text",
        "target proof",
        "--browser-mode",
        "off",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "success"
    assert [attempt["stage_id"] for attempt in payload["attempts"]] == [
        "direct-public-fetch",
        "defuddle-reader-extraction",
    ]
    assert payload["attempts"][1]["confidence"] == "strong"
    assert payload["selected_attempt"]["stage_id"] == "defuddle-reader-extraction"
    assert payload["final_status"] == "success"


def test_acquire_public_url_uses_agent_browser_network_recon_for_collect_intent(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "agent-browser").write_text(
        """#!/bin/sh
case "$*" in
  *"get text body"*) printf 'rendered target proof from browser\\n' ;;
  *"network requests"*) printf 'GET https://example.com/api/items\\n' ;;
  *) exit 0 ;;
esac
""",
        encoding="utf-8",
    )
    (bin_dir / "agent-browser").chmod(0o755)
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body><div id=\"root\"></div></body></html>", encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/app",
        "--direct-response-file",
        str(direct),
        "--expect-text",
        "target proof",
        "--intent",
        "collect",
        "--browser-mode",
        "auto",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "success"
    assert payload["attempts"][-2]["stage_id"] == "agent-browser-render-recon"
    assert payload["attempts"][-1]["stage_id"] == "agent-browser-network-recon"
    assert payload["attempts"][-1]["status"] == "diagnostic"
    assert payload["attempts"][-1]["details"]["network_candidates"] == [
        "GET https://example.com/api/items"
    ]
    assert payload["selected_attempt"]["stage_id"] == "agent-browser-render-recon"
    assert payload["final_status"] == "success"


def test_acquire_public_url_records_missing_fallback_tools(tmp_path: Path) -> None:
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
    skipped = {
        attempt["stage_id"]: attempt["details"]["reason"]
        for attempt in payload["attempts"]
        if attempt["status"] == "skipped"
    }
    assert skipped["defuddle-reader-extraction"] == "missing-tool"
    assert skipped["agent-browser-render-recon"] == "missing-tool"


def test_acquire_public_url_records_unimplemented_domain_route(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>" + ("reddit content " * 120) + "</body></html>", encoding="utf-8")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://www.reddit.com/r/python/",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "off",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "success"
    domain_attempt = next(attempt for attempt in payload["attempts"] if attempt["stage_id"] == "domain-specific-route")
    assert domain_attempt["status"] == "skipped"
    assert domain_attempt["details"]["reason"] == "not-implemented"
    assert payload["selected_attempt"]["stage_id"] == "direct-public-fetch"


def test_acquire_public_url_network_recon_alone_is_not_success(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "agent-browser").write_text(
        """#!/bin/sh
case "$*" in
  *"get text body"*) printf 'short rendered shell\\n' ;;
  *"network requests"*) printf 'GET https://example.com/api/items\\n' ;;
  *) exit 0 ;;
esac
""",
        encoding="utf-8",
    )
    (bin_dir / "agent-browser").chmod(0o755)
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body><div id=\"root\"></div></body></html>", encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/app",
        "--direct-response-file",
        str(direct),
        "--intent",
        "collect",
        "--browser-mode",
        "auto",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "degraded"
    assert payload["attempts"][-1]["stage_id"] == "agent-browser-network-recon"
    assert payload["attempts"][-1]["status"] == "diagnostic"
    assert payload["selected_attempt"]["stage_id"] == "agent-browser-render-recon"


def test_acquire_public_url_blocker_with_proof_is_blocked(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body><h1>Sign in</h1><p>needle</p></body></html>", encoding="utf-8")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/private",
        "--direct-response-file",
        str(direct),
        "--expect-text",
        "needle",
        "--browser-mode",
        "off",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "blocked"
    assert payload["selected_attempt"]["status"] == "login-wall"
    assert payload["selected_attempt"]["classification"]["proof"] == [{"type": "text", "value": "needle"}]


def test_gather_public_url_writes_web_fetch_trace(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>" + ("useful content " * 120) + "</body></html>", encoding="utf-8")

    result = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "off",
        "--slug",
        "example-public-url",
        "--date",
        "2026-05-16",
        "--execute",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "updated"
    record_path = Path(payload["write_record"]["record_artifact_path"])
    record = record_path.read_text(encoding="utf-8")
    assert "# Gathered Public URL" in record
    assert "## Acquisition Trace" in record
    assert "`direct-public-fetch`" in record
    assert '"selected_attempt"' in record
    assert (tmp_path / "charness-artifacts" / "gather" / "latest.md").is_file()


def test_acquire_public_url_accepts_weak_direct_success_without_positive_proof(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>" + ("useful content " * 120) + "</body></html>", encoding="utf-8")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "off",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "success"
    assert len(payload["attempts"]) == 1
    assert payload["attempts"][0]["stage_id"] == "direct-public-fetch"
    assert payload["attempts"][0]["status"] == "success"
    assert payload["attempts"][0]["confidence"] == "weak"
    assert payload["attempts"][0]["output_chars"] == len(direct.read_text(encoding="utf-8"))
