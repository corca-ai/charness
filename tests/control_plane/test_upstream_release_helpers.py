from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.upstream_release_lib as upstream


def test_extract_version_and_fixture_release_handle_empty_and_non_dict_payloads(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture_path = tmp_path / "fixtures.json"
    fixture_path.write_text(
        json.dumps(
            {
                "example/tool": {"tag_name": "v1.2.3"},
                "example/list": ["not-a-dict"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CHARNESS_RELEASE_PROBE_FIXTURES", str(fixture_path))

    assert upstream.extract_version(None) is None
    assert upstream.extract_version("release-2026.04 build") == "2026.04"
    assert upstream.fixture_release("example/tool") == {"tag_name": "v1.2.3"}
    assert upstream.fixture_release("example/list") is None
    assert upstream.fixture_release("example/missing") is None


def test_normalize_release_payload_filters_assets_and_preserves_error_fields() -> None:
    payload = {
        "status": "error",
        "reason": "fixture-error",
        "error": "broken",
        "tag_name": "release v3.4.5",
        "html_url": "https://github.com/example/tool/releases/tag/v3.4.5",
        "published_at": "2026-04-16T00:00:00Z",
        "assets": [{"name": "tool.tar.gz"}, {"name": 7}, "bad"],
    }

    release = upstream.normalize_release_payload("example/tool", payload)

    assert release == {
        "provider": "github",
        "repo": "example/tool",
        "status": "error",
        "api_url": "https://api.github.com/repos/example/tool/releases/latest",
        "html_url": "https://github.com/example/tool/releases/tag/v3.4.5",
        "latest_tag": "release v3.4.5",
        "latest_version": "3.4.5",
        "published_at": "2026-04-16T00:00:00Z",
        "asset_names": ["tool.tar.gz"],
        "error": "broken",
        "reason": "fixture-error",
    }


def test_probe_release_requires_github_manifest_shape() -> None:
    assert upstream.probe_release({"tool_id": "demo"}) is None
    assert upstream.probe_release({"upstream_repo": "example/demo", "homepage": "https://example.com/demo"}) is None


def test_probe_gh_release_helper_returns_none_when_cli_is_disabled_or_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHARNESS_RELEASE_PROBE_NO_GH", "1")
    assert upstream._probe_github_release_with_gh("example/tool") is None

    monkeypatch.delenv("CHARNESS_RELEASE_PROBE_NO_GH", raising=False)
    monkeypatch.setattr(upstream.shutil, "which", lambda _name: "/usr/bin/gh")

    class InvalidJson:
        returncode = 0
        stdout = "{not-json"
        stderr = ""

    monkeypatch.setattr(upstream.subprocess, "run", lambda *_args, **_kwargs: InvalidJson())
    assert upstream._probe_github_release_with_gh("example/tool") is None
