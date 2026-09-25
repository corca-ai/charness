"""Direct unit tests for the #873 `bootstrap_probe` feature module.

These pure version/release helpers only run inside purged phase-2 flows in
the suite, so in-process coverage never reaches them without direct calls.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import scripts.cli.bootstrap_probe as probe


def test_parse_iso_timestamp_shapes() -> None:
    assert probe.parse_iso_timestamp("2026-09-25T10:00:00Z") == datetime(
        2026, 9, 25, 10, 0, tzinfo=timezone.utc
    )
    assert probe.parse_iso_timestamp(None) is None
    assert probe.parse_iso_timestamp("") is None
    assert probe.parse_iso_timestamp(123) is None
    assert probe.parse_iso_timestamp("not-a-time") is None


def test_normalize_version_token_shapes() -> None:
    assert probe.normalize_version_token("v1.2.3") == "1.2.3"
    assert probe.normalize_version_token("V8.13.0") == "8.13.0"
    assert probe.normalize_version_token("1.0") == "1.0"
    assert probe.normalize_version_token("  ") is None
    assert probe.normalize_version_token(None) is None
    assert probe.normalize_version_token("v") == "v"


def test_parse_semver_like_shapes() -> None:
    assert probe.parse_semver_like("1.2.3") == ((1, 2, 3), ())
    assert probe.parse_semver_like("v2.0.0-rc.1") == ((2, 0, 0), ((1, "rc"), (0, 1)))
    assert probe.parse_semver_like(None) is None
    assert probe.parse_semver_like("abc") is None
    assert probe.parse_semver_like("") is None


def test_compare_semver_like_orders_releases() -> None:
    assert probe.compare_semver_like("1.2.3", "1.2.3") == 0
    assert probe.compare_semver_like("1.2", "1.2.0") == 0
    assert probe.compare_semver_like("1.2.3", "1.2.4") == -1
    assert probe.compare_semver_like("2.0.0", "1.9.9") == 1
    assert probe.compare_semver_like("1.0.0-rc.1", "1.0.0") == -1
    assert probe.compare_semver_like("1.0.0", "1.0.0-rc.1") == 1
    assert probe.compare_semver_like("1.0.0-a", "1.0.0-b") == -1
    assert probe.compare_semver_like("1.0.0-b", "1.0.0-a") == 1
    assert probe.compare_semver_like("nope", "1.0.0") is None
    assert probe.compare_semver_like("1.0.0", "nope") is None


def test_self_release_repo_parses_remote(monkeypatch) -> None:
    assert probe.self_release_repo() == "corca-ai/charness"
    monkeypatch.setattr(probe, "REPO_URL", "not-a-remote")
    assert probe.self_release_repo() == "corca-ai/charness"


def test_fixture_release_reads_env_probe(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("CHARNESS_RELEASE_PROBE_FIXTURES", raising=False)
    assert probe.fixture_release("o/r") is None
    fixtures = tmp_path / "fixtures.json"
    fixtures.write_text(
        json.dumps({"o/r": {"tag_name": "v9.0.0"}, "o/other": [1]}),
        encoding="utf-8",
    )
    monkeypatch.setenv("CHARNESS_RELEASE_PROBE_FIXTURES", str(fixtures))
    assert probe.fixture_release("o/r") == {"tag_name": "v9.0.0"}
    assert probe.fixture_release("o/missing") is None
    assert probe.fixture_release("o/other") is None


def test_extract_version_shapes() -> None:
    assert probe.extract_version("release v8.13.0 is out") == "8.13.0"
    assert probe.extract_version("no version here") is None
    assert probe.extract_version(None) is None


def test_normalize_release_payload_shapes() -> None:
    payload = probe.normalize_release_payload(
        "o/r",
        {
            "tag_name": "v9.0.0",
            "html_url": "https://example.test/r",
            "published_at": "2026-09-25T10:00:00Z",
            "assets": [{"name": "a"}, {"name": 1}, "x"],
        },
    )
    assert payload["status"] == "ok"
    assert payload["latest_tag"] == "v9.0.0"
    assert payload["latest_version"] == "9.0.0"
    assert payload["asset_names"] == ["a"]
    assert payload["error"] is None
    overridden = probe.normalize_release_payload("o/r", {"status": "error", "error": "boom"})
    assert overridden["status"] == "error"
    assert overridden["error"] == "boom"
    assert overridden["latest_tag"] is None


def test_probe_self_release_prefers_fixture(tmp_path: Path, monkeypatch) -> None:
    fixtures = tmp_path / "fixtures.json"
    fixtures.write_text(json.dumps({"o/r": {"tag_name": "v9.0.0"}}), encoding="utf-8")
    monkeypatch.setenv("CHARNESS_RELEASE_PROBE_FIXTURES", str(fixtures))
    release = probe.probe_self_release("o/r")
    assert release["status"] == "ok"
    assert release["latest_tag"] == "v9.0.0"


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *exc_info) -> bool:
        return False

    def read(self) -> bytes:
        return self._payload


def test_probe_self_release_reads_latest_over_http(monkeypatch) -> None:
    import urllib.error
    import urllib.request

    monkeypatch.delenv("CHARNESS_RELEASE_PROBE_FIXTURES", raising=False)
    body = json.dumps({"tag_name": "v9.1.0", "html_url": "https://example.test/r"}).encode()
    monkeypatch.setattr(urllib.request, "urlopen", lambda request, timeout=10: _FakeResponse(body))
    release = probe.probe_self_release("o/r")
    assert release["status"] == "ok"
    assert release["latest_tag"] == "v9.1.0"
    assert release["latest_version"] == "9.1.0"


def test_probe_self_release_maps_http_errors(monkeypatch) -> None:
    import urllib.error
    import urllib.request

    monkeypatch.delenv("CHARNESS_RELEASE_PROBE_FIXTURES", raising=False)

    def _missing(request, timeout=10):
        raise urllib.error.HTTPError(request.full_url, 404, "missing", {}, None)

    monkeypatch.setattr(urllib.request, "urlopen", _missing)
    release = probe.probe_self_release("o/r")
    assert release["status"] == "no-release"
    assert release["error"] == "http 404"

    def _failed(request, timeout=10):
        raise urllib.error.HTTPError(request.full_url, 500, "boom", {}, None)

    monkeypatch.setattr(urllib.request, "urlopen", _failed)
    release = probe.probe_self_release("o/r")
    assert release["status"] == "error"
    assert release["error"] == "http 500"

    def _unreachable(request, timeout=10):
        raise urllib.error.URLError("down")

    monkeypatch.setattr(urllib.request, "urlopen", _unreachable)
    release = probe.probe_self_release("o/r")
    assert release["status"] == "error"
    assert "down" in release["error"]

    def _garbage(request, timeout=10):
        return _FakeResponse(b"not json")

    monkeypatch.setattr(urllib.request, "urlopen", _garbage)
    release = probe.probe_self_release("o/r")
    assert release["status"] == "error"


def test_latest_release_cache_is_fresh_shapes() -> None:
    fresh_at = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    fresh = {
        "checked_at": fresh_at,
        "current_version": "v8.13.0",
    }
    assert probe.latest_release_cache_is_fresh(fresh, "8.13.0") is True
    assert probe.latest_release_cache_is_fresh(fresh, "8.12.0") is False
    assert probe.latest_release_cache_is_fresh({}, "8.13.0") is False
    stale_at = (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat()
    assert (
        probe.latest_release_cache_is_fresh(
            {"checked_at": stale_at, "current_version": "8.13.0"}, "8.13.0"
        )
        is False
    )


def test_compute_update_available_shapes() -> None:
    assert probe.compute_update_available("8.12.0", "8.13.0") is True
    assert probe.compute_update_available("8.13.0", "8.13.0") is False
    assert probe.compute_update_available("9.0.0", "8.13.0") is False
    assert probe.compute_update_available("nope", "8.13.0") is None


def test_build_self_update_notice_shapes() -> None:
    assert probe.build_self_update_notice(None) is None
    assert probe.build_self_update_notice({"status": "error"}) is None
    assert probe.build_self_update_notice({"status": "ok", "update_available": False}) is None
    notice = probe.build_self_update_notice(
        {
            "status": "ok",
            "update_available": True,
            "current_version": "8.12.0",
            "latest_tag": "v8.13.0",
            "html_url": "https://example.test/r",
        }
    )
    assert notice is not None and "8.12.0" in notice and "v8.13.0" in notice
    assert "https://example.test/r" in notice
    bare = probe.build_self_update_notice(
        {"status": "ok", "update_available": True, "latest_version": "9.0.0"}
    )
    assert bare is not None and "unknown" in bare and "9.0.0" in bare
    assert (
        probe.build_self_update_notice({"status": "ok", "update_available": True, "latest_tag": ""})
        is None
    )
