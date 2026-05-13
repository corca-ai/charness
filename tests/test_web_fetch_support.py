from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_helper(script: str, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, script, *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        input=input_text,
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


def test_classify_fetch_response_reports_login_wall() -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/classify_fetch_response.py",
        input_text="<html><body><h1>Sign in</h1><p>Please login to continue.</p></body></html>",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "login-wall"


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
