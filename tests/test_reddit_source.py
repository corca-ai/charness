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
import reddit_source as rs  # noqa: E402


def run_helper(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, script, *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_reddit_source_helper_branches(monkeypatch) -> None:
    assert rs._normalized_url("not-a-url") == "not-a-url"
    assert rs._endpoints("https://example.com/r/python/") == []
    assert [endpoint["url"] for endpoint in rs._endpoints("https://www.reddit.com/r/python/comments/abc/title/")] == [
        "https://www.reddit.com/r/python/comments/abc/title.rss",
        "https://www.reddit.com/r/python/comments/abc/title.json",
    ]
    assert rs._looks_like_json("not json") is False
    assert rs._looks_like_json("{}") is False
    assert rs._looks_like_json('{"ok": true}') is True

    skipped = rs.run_reddit_stage("https://example.com/not-reddit", fetcher=lambda endpoint: ("", None))
    assert skipped[0].details["reason"] == "not-reddit-url"

    attempts = rs.run_reddit_stage(
        "https://www.reddit.com/r/python/",
        fetcher=lambda endpoint: ("not feed", None)
        if endpoint["kind"] == "rss"
        else ('{"data": {"children": [{"title": "Python"}]}}', None),
    )
    assert attempts[-1].details["outcome"] == "json-fetched"

    bad = rs.run_reddit_stage("https://www.reddit.com/r/python/", fetcher=lambda endpoint: ("not feed", None))
    assert bad[-1].details["reason"] == "no-feed-or-json"

    assert rs.classify_source_identity({"route": {"route_id": "other"}, "attempts": []}) == "not-applicable"
    serialized_attempts = [attempt.to_dict() for attempt in attempts]
    assert rs.classify_source_identity({"route": {"route_id": "reddit-feed"}, "attempts": serialized_attempts}) == "json-fetched"
    assert rs.classify_source_identity({"route": {"route_id": "reddit-feed"}, "attempts": []}) == "feed-unavailable"

    monkeypatch.setattr(apu, "_read_direct", lambda url, *, timeout, direct_response_file: ("live:" + url, None))
    args = SimpleNamespace(domain_route_response_file=None, timeout=1)
    assert apu._seeded_or_live_fetcher(args)({"url": "https://www.reddit.com/r/python/.rss"}) == (
        "live:https://www.reddit.com/r/python/.rss",
        None,
    )


def test_acquire_public_url_uses_reddit_rss_before_generic_fallback(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>captcha verify you are human</body></html>", encoding="utf-8")
    seed = tmp_path / "reddit-seed.json"
    seed.write_text(
        json.dumps({
            "https://www.reddit.com/r/python/.rss": {
                "text": "<?xml version='1.0'?><rss><channel><item><title>Python news</title></item></channel></rss>"
            }
        }),
        encoding="utf-8",
    )

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://www.reddit.com/r/python/",
        "--direct-response-file",
        str(direct),
        "--domain-route-response-file",
        str(seed),
        "--browser-mode",
        "off",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "success"
    assert payload["route"]["route_id"] == "reddit-feed"
    assert payload["source_identity"] == "feed-fetched"
    assert payload["attempts"][0]["stage_id"] == "domain-specific-route"
    direct_attempts = [attempt for attempt in payload["attempts"] if attempt["stage_id"] == "direct-public-fetch"]
    assert direct_attempts == [
        {
            "stage_id": "direct-public-fetch",
            "tool_id": None,
            "status": "skipped",
            "confidence": "none",
            "elapsed_s": 0.0,
            "output_chars": 0,
            "details": {"reason": "prior-stage-sufficient"},
        }
    ]
    domain_attempt = next(attempt for attempt in payload["attempts"] if attempt["stage_id"] == "domain-specific-route")
    assert domain_attempt["status"] == "success"
    assert domain_attempt["tool_id"] == "reddit-rss"
    assert domain_attempt["details"]["outcome"] == "feed-fetched"
    assert payload["selected_attempt"]["stage_id"] == "domain-specific-route"


def test_reddit_seed_file_missing_endpoint_does_not_fetch_live(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>captcha verify you are human</body></html>", encoding="utf-8")
    seed = tmp_path / "reddit-seed.json"
    seed.write_text("{}", encoding="utf-8")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://www.reddit.com/r/python/",
        "--direct-response-file",
        str(direct),
        "--domain-route-response-file",
        str(seed),
        "--browser-mode",
        "off",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    domain_attempts = [attempt for attempt in payload["attempts"] if attempt["stage_id"] == "domain-specific-route"]
    assert [attempt["error"] for attempt in domain_attempts] == ["seed-missing", "seed-missing"]
    assert payload["source_identity"] == "feed-blocked"


def test_reddit_direct_page_fallback_has_coherent_source_identity(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>" + ("reddit thread content " * 80) + "</body></html>", encoding="utf-8")
    seed = tmp_path / "reddit-seed.json"
    seed.write_text("{}", encoding="utf-8")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://www.reddit.com/r/python/",
        "--direct-response-file",
        str(direct),
        "--domain-route-response-file",
        str(seed),
        "--browser-mode",
        "off",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    stages = [attempt["stage_id"] for attempt in payload["attempts"]]
    assert stages[:3] == ["domain-specific-route", "domain-specific-route", "direct-public-fetch"]
    assert payload["disposition"] == "success"
    assert payload["source_identity"] == "direct-page-fetched"
    assert payload["selected_attempt"]["stage_id"] == "direct-public-fetch"


def test_reddit_feed_does_not_satisfy_missing_positive_proof(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>captcha verify you are human</body></html>", encoding="utf-8")
    seed = tmp_path / "reddit-seed.json"
    seed.write_text(
        json.dumps({
            "https://www.reddit.com/r/python/.rss": {
                "text": "<?xml version='1.0'?><rss><channel><item><title>Python news</title></item></channel></rss>"
            }
        }),
        encoding="utf-8",
    )

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://www.reddit.com/r/python/",
        "--direct-response-file",
        str(direct),
        "--domain-route-response-file",
        str(seed),
        "--expect-text",
        "not present in feed",
        "--browser-mode",
        "off",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    domain_attempt = payload["attempts"][0]
    assert domain_attempt["stage_id"] == "domain-specific-route"
    assert domain_attempt["status"] == "unclear"
    assert "missing-positive-proof" in domain_attempt["classification"]["signals"]
    assert payload["source_identity"] == "feed-blocked"
    assert payload["disposition"] != "success"
