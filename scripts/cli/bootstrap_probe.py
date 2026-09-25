"""Self-release probe and version-comparison helpers (#873).

Split from bootstrap_state.py: pure helpers around the GitHub releases
``/latest`` probe (fixture short-circuit, payload normalization, freshness,
semver comparison, update notice). No state I/O here.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli.bootstrap import REPO_URL  # noqa: E402


def parse_iso_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def normalize_version_token(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if normalized.startswith(("v", "V")) and len(normalized) > 1:
        normalized = normalized[1:]
    return normalized


def _parse_prerelease_identifier(value: str) -> tuple[int, int | str]:
    if value.isdigit():
        return (0, int(value))
    return (1, value.lower())


def parse_semver_like(
    value: object,
) -> tuple[tuple[int, ...], tuple[tuple[int, int | str], ...]] | None:
    normalized = normalize_version_token(value)
    if normalized is None:
        return None
    core, _, prerelease = normalized.partition("-")
    try:
        core_parts = tuple(int(part) for part in core.split("."))
    except ValueError:
        return None
    if not core_parts:  # pragma: no cover - `"".split(".")` never yields `()`
        return None
    prerelease_parts = (
        tuple(_parse_prerelease_identifier(part) for part in prerelease.split(".") if part)
        if prerelease
        else ()
    )
    return core_parts, prerelease_parts


def compare_semver_like(left: object, right: object) -> int | None:
    parsed_left = parse_semver_like(left)
    parsed_right = parse_semver_like(right)
    if parsed_left is None or parsed_right is None:
        return None
    left_core, left_prerelease = parsed_left
    right_core, right_prerelease = parsed_right
    max_length = max(len(left_core), len(right_core))
    left_core_padded = left_core + (0,) * (max_length - len(left_core))
    right_core_padded = right_core + (0,) * (max_length - len(right_core))
    if left_core_padded < right_core_padded:
        return -1
    if left_core_padded > right_core_padded:
        return 1
    if left_prerelease == right_prerelease:
        return 0
    if not left_prerelease:
        return 1
    if not right_prerelease:
        return -1
    if left_prerelease < right_prerelease:
        return -1
    return 1


def self_release_repo() -> str:
    match = re.search(r"github\.com/([^/]+/[^/]+?)(?:\.git)?$", REPO_URL)
    return match.group(1) if match else "corca-ai/charness"


def fixture_release(repo: str) -> dict[str, object] | None:
    fixture_path = os.environ.get("CHARNESS_RELEASE_PROBE_FIXTURES")
    if not fixture_path:
        return None
    data = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    payload = data.get(repo)
    return payload if isinstance(payload, dict) else None


def extract_version(text: object) -> str | None:
    if not isinstance(text, str):
        return None
    match = re.search(r"(?<!\d)(\d+(?:\.\d+){1,}(?:-[0-9A-Za-z.-]+)?)(?![0-9A-Za-z.-])", text)
    return match.group(1) if match else None


def normalize_release_payload(repo: str, payload: dict[str, object]) -> dict[str, object]:
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
        "api_url": f"https://api.github.com/repos/{repo}/releases/latest",
        "html_url": html_url if isinstance(html_url, str) else None,
        "latest_tag": latest_tag if isinstance(latest_tag, str) else None,
        "latest_version": extract_version(latest_tag),
        "published_at": published_at if isinstance(published_at, str) else None,
        "asset_names": asset_names,
        "error": None,
    }
    if isinstance(payload.get("status"), str):
        release["status"] = payload["status"]
    if isinstance(payload.get("error"), str):
        release["error"] = payload["error"]
    return release


def probe_self_release(repo: str | None = None) -> dict[str, object]:
    # Imported here, not at module scope: `urllib.request` pulls in `http.client`,
    # `ssl`, and `email.parser`, which measured 17ms of this CLI's ~114ms startup —
    # paid by every `charness` invocation, while the one network path that needs it
    # is this function, past the fixture short-circuit.
    import urllib.error
    import urllib.request

    repo = repo or self_release_repo()
    fixture = fixture_release(repo)
    if fixture is not None:
        return normalize_release_payload(repo, fixture)

    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/releases/latest",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "charness-self-update-check",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        status = "no-release" if exc.code == 404 else "error"
        return {
            "provider": "github",
            "repo": repo,
            "status": status,
            "api_url": f"https://api.github.com/repos/{repo}/releases/latest",
            "html_url": None,
            "latest_tag": None,
            "latest_version": None,
            "published_at": None,
            "asset_names": [],
            "error": f"http {exc.code}",
        }
    except (TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {
            "provider": "github",
            "repo": repo,
            "status": "error",
            "api_url": f"https://api.github.com/repos/{repo}/releases/latest",
            "html_url": None,
            "latest_tag": None,
            "latest_version": None,
            "published_at": None,
            "asset_names": [],
            "error": str(exc),
        }
    return normalize_release_payload(repo, payload)


def latest_release_cache_is_fresh(
    latest_release: dict[str, object], current_version: str | None
) -> bool:
    checked_at = parse_iso_timestamp(latest_release.get("checked_at"))
    if checked_at is None:
        return False
    if checked_at < datetime.now(timezone.utc) - timedelta(hours=24):
        return False
    return normalize_version_token(
        latest_release.get("current_version")
    ) == normalize_version_token(current_version)


def compute_update_available(current_version: str | None, latest_version: object) -> bool | None:
    comparison = compare_semver_like(current_version, latest_version)
    if comparison is None:
        return None
    return comparison < 0


def build_self_update_notice(latest_release: object) -> str | None:
    if not isinstance(latest_release, dict):
        return None
    if latest_release.get("status") != "ok" or latest_release.get("update_available") is not True:
        return None
    current_version = latest_release.get("current_version") or "unknown"
    latest = latest_release.get("latest_tag") or latest_release.get("latest_version")
    if not isinstance(latest, str) or not latest:
        return None
    url = latest_release.get("html_url")
    suffix = f" {url}" if isinstance(url, str) and url else ""
    return (
        f"charness release available: `{current_version}` -> `{latest}`. "
        f"Upgrade with `charness update` from the installed CLI.{suffix}"
    )
