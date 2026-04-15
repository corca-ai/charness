from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import scripts.upstream_release_lib as upstream
from scripts.upstream_release_lib import probe_github_release


class FakeResponse:
    def __init__(self, payload: dict[str, Any] | str) -> None:
        self.payload = payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        if isinstance(self.payload, str):
            return self.payload.encode("utf-8")
        return json.dumps(self.payload).encode("utf-8")


def test_probe_github_release_prefers_authenticated_gh_cli(
    tmp_path: Path, monkeypatch
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'printf "%s\\n" "$*" > "$GH_ARGS_PATH"',
                'cat <<\'JSON\'',
                "{",
                '  "tag_name": "v1.2.3",',
                '  "html_url": "https://github.com/example/tool/releases/tag/v1.2.3",',
                '  "published_at": "2026-04-15T00:00:00Z",',
                '  "assets": [{"name": "tool-linux-arm64.tar.gz"}]',
                "}",
                "JSON",
                "",
            ]
        ),
        encoding="utf-8",
    )
    gh.chmod(0o755)
    args_path = tmp_path / "gh-args.txt"

    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
    monkeypatch.setenv("GH_ARGS_PATH", str(args_path))
    monkeypatch.delenv("CHARNESS_RELEASE_PROBE_FIXTURES", raising=False)

    release = probe_github_release("example/tool")

    assert release["status"] == "ok"
    assert release["latest_tag"] == "v1.2.3"
    assert release["latest_version"] == "1.2.3"
    assert release["asset_names"] == ["tool-linux-arm64.tar.gz"]
    assert args_path.read_text(encoding="utf-8").strip() == (
        "api /repos/example/tool/releases/latest"
    )


def test_probe_github_release_falls_back_to_urllib_when_gh_disabled(
    monkeypatch,
) -> None:
    captured: dict[str, urllib.request.Request] = {}

    def fake_urlopen(request: urllib.request.Request, *, timeout: int) -> FakeResponse:
        captured["request"] = request
        assert timeout == 10
        return FakeResponse({"tag_name": "v2.0.0", "assets": []})

    def fail_run(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("gh should not run when CHARNESS_RELEASE_PROBE_NO_GH=1")

    monkeypatch.setenv("CHARNESS_RELEASE_PROBE_NO_GH", "1")
    monkeypatch.delenv("CHARNESS_RELEASE_PROBE_FIXTURES", raising=False)
    monkeypatch.setattr(upstream.subprocess, "run", fail_run)
    monkeypatch.setattr(upstream.urllib.request, "urlopen", fake_urlopen)

    release = probe_github_release("example/tool")

    assert release["status"] == "ok"
    assert release["latest_version"] == "2.0.0"
    assert captured["request"].full_url == "https://api.github.com/repos/example/tool/releases/latest"


def test_probe_github_release_adds_token_header_to_urllib_fallback(monkeypatch) -> None:
    captured: dict[str, urllib.request.Request] = {}

    def fake_urlopen(request: urllib.request.Request, *, timeout: int) -> FakeResponse:
        captured["request"] = request
        return FakeResponse({"tag_name": "v3.4.5", "assets": []})

    monkeypatch.setenv("CHARNESS_RELEASE_PROBE_NO_GH", "1")
    monkeypatch.setenv("GH_TOKEN", "ghp_test_token")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("CHARNESS_RELEASE_PROBE_FIXTURES", raising=False)
    monkeypatch.setattr(upstream.urllib.request, "urlopen", fake_urlopen)

    release = probe_github_release("example/tool")

    assert release["status"] == "ok"
    assert captured["request"].headers["Authorization"] == "Bearer ghp_test_token"
    assert captured["request"].headers["User-agent"] == "charness-release-probe"


def test_probe_github_release_reports_no_release_on_404(monkeypatch) -> None:
    def fake_urlopen(request: urllib.request.Request, *, timeout: int) -> FakeResponse:
        raise urllib.error.HTTPError(request.full_url, 404, "Not Found", hdrs=None, fp=None)

    monkeypatch.setenv("CHARNESS_RELEASE_PROBE_NO_GH", "1")
    monkeypatch.delenv("CHARNESS_RELEASE_PROBE_FIXTURES", raising=False)
    monkeypatch.setattr(upstream.urllib.request, "urlopen", fake_urlopen)

    release = probe_github_release("example/no-release")

    assert release["status"] == "no-release"
    assert release["reason"] == "github-no-release"
    assert release["error"] == "http 404"


def test_probe_github_release_reports_forbidden_on_403(monkeypatch) -> None:
    def fake_urlopen(request: urllib.request.Request, *, timeout: int) -> FakeResponse:
        raise urllib.error.HTTPError(request.full_url, 403, "Forbidden", hdrs=None, fp=None)

    monkeypatch.setenv("CHARNESS_RELEASE_PROBE_NO_GH", "1")
    monkeypatch.delenv("CHARNESS_RELEASE_PROBE_FIXTURES", raising=False)
    monkeypatch.setattr(upstream.urllib.request, "urlopen", fake_urlopen)

    release = probe_github_release("example/forbidden")

    assert release["status"] == "error"
    assert release["reason"] == "github-forbidden"
    assert release["error"] == "http 403"


def test_probe_github_release_reports_invalid_json(monkeypatch) -> None:
    def fake_urlopen(request: urllib.request.Request, *, timeout: int) -> FakeResponse:
        return FakeResponse("{not-json")

    monkeypatch.setenv("CHARNESS_RELEASE_PROBE_NO_GH", "1")
    monkeypatch.delenv("CHARNESS_RELEASE_PROBE_FIXTURES", raising=False)
    monkeypatch.setattr(upstream.urllib.request, "urlopen", fake_urlopen)

    release = probe_github_release("example/bad-json")

    assert release["status"] == "error"
    assert release["reason"] == "github-invalid-json"
