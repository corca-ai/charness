#!/usr/bin/env python3
"""Check that a declared native artifact is present in the latest release."""

from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from urllib.parse import urlparse

SCRIPT_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(SCRIPT_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_REPO_ROOT))

from scripts.native_core_resolution_lib import (  # noqa: E402
    artifact_declaration,
    checkout_version,
    host_tuple,
    read_native_declaration,
    repository_url,
)
from scripts.yaml_output import emit_yaml  # noqa: E402


class ReleaseAssetCheckError(RuntimeError):
    """Raised when the release asset check cannot establish a result."""


def _repository_slug(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip().removesuffix(".git")
    if text.startswith("git@") and ":" in text:
        text = text.split(":", 1)[1]
    elif "://" in text:
        parsed = urlparse(text)
        text = parsed.path.strip("/")
    if text.count("/") != 1 or text.startswith("/"):
        return None
    return text


def _load_charness(repo_root: Path) -> ModuleType:
    candidates = (repo_root / "charness", SCRIPT_REPO_ROOT / "charness")
    source = next((path for path in candidates if path.is_file()), None)
    if source is None:
        raise ReleaseAssetCheckError("the self-release probe script is unavailable")
    name = "charness_release_probe"
    loader = importlib.machinery.SourceFileLoader(name, str(source))
    spec = importlib.util.spec_from_loader(name, loader)
    if spec is None:
        raise ReleaseAssetCheckError(f"could not load self-release probe from {source}")
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def check_native_release_asset(
    repo_root: Path, *, release_probe=None
) -> dict[str, object]:
    """Return a typed pass/fail result for the checkout's declared asset."""
    repo_root = repo_root.resolve()
    version = checkout_version(repo_root)
    declaration = read_native_declaration(repo_root)
    tuple_name = host_tuple()
    if declaration is None:
        return {
            "status": "not-applicable",
            "version": version,
            "tuple": tuple_name,
            "reason": "native_core declaration is absent",
        }
    if version is None:
        raise ReleaseAssetCheckError("product version cannot be read from packaging/charness.json")
    expected = artifact_declaration(declaration, version, tuple_name)
    if expected is None:
        return {
            "status": "not-applicable",
            "version": version,
            "tuple": tuple_name,
            "reason": "checkout version has no native artifact declaration",
        }
    canonical_name = f"repograph-v{version}-{tuple_name}.tar.gz"
    if expected["name"] != canonical_name:
        return {
            "status": "fail",
            "version": version,
            "tuple": tuple_name,
            "asset": expected["name"],
            "reason": f"native artifact declaration must use {canonical_name}",
        }
    if release_probe is None:
        module = _load_charness(repo_root)
        release_probe = module.probe_self_release
    source = declaration.get("source") or repository_url(repo_root)
    repo = _repository_slug(source)
    try:
        release = release_probe(repo) if repo else release_probe()
    except Exception as exc:  # probe adapters turn fixture/network failures into a typed result
        raise ReleaseAssetCheckError(f"self-release probe failed: {exc}") from exc
    if not isinstance(release, dict):
        raise ReleaseAssetCheckError("self-release probe returned a non-object payload")
    if release.get("status") != "ok":
        return {
            "status": "fail",
            "version": version,
            "tuple": tuple_name,
            "asset": canonical_name,
            "reason": f"self-release probe status is {release.get('status')!r}: {release.get('error') or 'no release'}",
        }
    assets = release.get("asset_names")
    if not isinstance(assets, list):
        raise ReleaseAssetCheckError("self-release probe did not return asset names")
    if canonical_name not in assets:
        return {
            "status": "fail",
            "version": version,
            "tuple": tuple_name,
            "asset": canonical_name,
            "release": release.get("latest_tag"),
            "reason": "declared native artifact is absent from release asset names",
        }
    return {
        "status": "pass",
        "version": version,
        "tuple": tuple_name,
        "asset": canonical_name,
        "release": release.get("latest_tag"),
        "reason": "declared native artifact is present in release asset names",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True, help="Checkout to inspect")
    args = parser.parse_args()
    try:
        result = check_native_release_asset(args.repo_root)
    except ReleaseAssetCheckError as exc:
        result = {"status": "fail", "reason": str(exc)}
    emit_yaml(result)
    return 0 if result["status"] in {"pass", "not-applicable"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
