#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SEMVER_RE = re.compile(r"(?<!\d)\d+(?:\.\d+){1,}(?!\d)")
GITHUB_API_TEMPLATE = "https://api.github.com/repos/{repo}/releases/latest"


def extract_version(text: str | None) -> str | None:
    if not text:
        return None
    match = SEMVER_RE.search(text)
    return match.group(0) if match else None


def fixture_release(repo: str) -> dict[str, Any] | None:
    fixture_path = os.environ.get("CHARNESS_RELEASE_PROBE_FIXTURES")
    if not fixture_path:
        return None
    data = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    payload = data.get(repo)
    return payload if isinstance(payload, dict) else None


def normalize_release_payload(repo: str, payload: dict[str, Any]) -> dict[str, Any]:
    latest_tag = payload.get("tag_name")
    html_url = payload.get("html_url")
    published_at = payload.get("published_at")
    assets = payload.get("assets", [])
    asset_names = [
        asset["name"]
        for asset in assets
        if isinstance(asset, dict) and isinstance(asset.get("name"), str)
    ]
    release = {
        "provider": "github",
        "repo": repo,
        "status": "ok",
        "api_url": GITHUB_API_TEMPLATE.format(repo=repo),
        "html_url": html_url if isinstance(html_url, str) else None,
        "latest_tag": latest_tag if isinstance(latest_tag, str) else None,
        "latest_version": extract_version(latest_tag if isinstance(latest_tag, str) else None),
        "published_at": published_at if isinstance(published_at, str) else None,
        "asset_names": asset_names,
        "error": None,
        "reason": payload["reason"] if isinstance(payload.get("reason"), str) else None,
    }
    if isinstance(payload.get("status"), str):
        release["status"] = payload["status"]
    if isinstance(payload.get("error"), str):
        release["error"] = payload["error"]
    return release


def error_release(repo: str, *, status: str, reason: str, error: str) -> dict[str, Any]:
    return {
        "provider": "github",
        "repo": repo,
        "status": status,
        "reason": reason,
        "api_url": GITHUB_API_TEMPLATE.format(repo=repo),
        "html_url": None,
        "latest_tag": None,
        "latest_version": None,
        "published_at": None,
        "asset_names": [],
        "error": error,
    }


def _github_api_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "charness-release-probe",
    }
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _release_from_payload(repo: str, payload: Any, *, source: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return error_release(
            repo,
            status="error",
            reason="github-malformed-release",
            error=f"{source} response was not a JSON object",
        )
    return normalize_release_payload(repo, payload)


def _probe_github_release_with_gh(repo: str) -> dict[str, Any] | None:
    if os.environ.get("CHARNESS_RELEASE_PROBE_NO_GH") == "1":
        return None
    if shutil.which("gh") is None:
        return None
    completed = subprocess.run(
        ["gh", "api", f"/repos/{repo}/releases/latest"],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if completed.returncode != 0:
        return None
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None
    return _release_from_payload(repo, payload, source="gh")


def probe_github_release(repo: str) -> dict[str, Any]:
    fixture = fixture_release(repo)
    if fixture is not None:
        return normalize_release_payload(repo, fixture)

    gh_release = _probe_github_release_with_gh(repo)
    if gh_release is not None:
        return gh_release

    request = urllib.request.Request(
        GITHUB_API_TEMPLATE.format(repo=repo),
        headers=_github_api_headers(),
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return error_release(repo, status="no-release", reason="github-no-release", error="http 404")
        if exc.code == 403:
            return error_release(repo, status="error", reason="github-forbidden", error="http 403")
        return error_release(repo, status="error", reason=f"github-http-{exc.code}", error=f"http {exc.code}")
    except json.JSONDecodeError as exc:
        return error_release(repo, status="error", reason="github-invalid-json", error=str(exc))
    except (TimeoutError, urllib.error.URLError) as exc:
        return error_release(repo, status="error", reason="github-network-error", error=str(exc))
    return _release_from_payload(repo, payload, source="github api")


def probe_release(manifest: dict[str, Any]) -> dict[str, Any] | None:
    repo = manifest.get("upstream_repo")
    if not isinstance(repo, str) or "/" not in repo:
        return None
    homepage = manifest.get("homepage")
    if not isinstance(homepage, str) or "github.com" not in homepage:
        return None
    return probe_github_release(repo)
