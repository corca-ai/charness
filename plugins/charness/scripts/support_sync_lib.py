#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from scripts.control_plane_render import render_generated_wrapper
from scripts.repo_layout import discovery_stub_dir, generated_support_dir, support_skill_cache_dir

SUPPORT_FIXTURES_ENV = "CHARNESS_SUPPORT_SYNC_FIXTURES"
GITHUB_ARCHIVE_URL = "https://codeload.github.com/{repo}/tar.gz/{ref}"


def support_state_for_manifest(manifest: dict[str, Any]) -> str:
    if manifest.get("kind") == "support_runtime":
        return "native-support"
    support = manifest.get("support_skill_source")
    if not support:
        return "integration-only"
    if support["source_type"] == "local_wrapper":
        return "wrapped-upstream"
    return "upstream-consumed"


def inspect_support_sync(repo_root: Path, previous_lock: dict[str, Any] | None) -> dict[str, Any]:
    support = previous_lock.get("support") if previous_lock else None
    if not support:
        return {
            "status": "not-tracked",
            "expected_paths": [],
            "missing_paths": [],
        }
    expected_paths = support.get("materialized_paths", [])
    missing_paths = [path for path in expected_paths if not (repo_root / path).exists()]
    return {
        "status": "ok" if not missing_paths else "missing",
        "expected_paths": expected_paths,
        "missing_paths": missing_paths,
    }


def parse_upstream_checkout(value: str) -> tuple[str, Path]:
    upstream_repo, separator, raw_path = value.partition("=")
    if not separator or not upstream_repo.strip() or not raw_path.strip():
        raise ValueError("`--upstream-checkout` must look like `owner/name=/abs/path/to/checkout`")
    checkout_root = Path(raw_path).expanduser().resolve()
    if not checkout_root.is_dir():
        raise ValueError(f"`--upstream-checkout` path does not exist: `{checkout_root}`")
    return upstream_repo.strip(), checkout_root


def clear_materialized_target(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.is_dir():
        shutil.rmtree(path)


def support_link_name(manifest: dict[str, Any]) -> str:
    support = manifest.get("support_skill_source") or {}
    if support.get("source_type") == "local_wrapper":
        return support["wrapper_skill_id"]
    return manifest["tool_id"]


def _fixture_checkout_root(repo: str, ref: str | None) -> Path | None:
    fixture_path = os.environ.get(SUPPORT_FIXTURES_ENV)
    if not fixture_path:
        return None
    payload = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"`{SUPPORT_FIXTURES_ENV}` must point at a JSON object")
    lookup_keys = [f"{repo}@{ref}"] if ref else []
    lookup_keys.append(repo)
    for key in lookup_keys:
        raw_path = payload.get(key)
        if not raw_path:
            continue
        checkout_root = Path(raw_path).expanduser().resolve()
        if not checkout_root.is_dir():
            raise ValueError(f"`{SUPPORT_FIXTURES_ENV}` entry `{key}` points at missing directory `{checkout_root}`")
        return checkout_root
    return None


def _safe_extract_tarball(archive_bytes: bytes, destination: Path) -> Path:
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as tar:
        for member in tar.getmembers():
            target = destination / member.name
            resolved_target = target.resolve()
            if destination.resolve() not in {resolved_target, *resolved_target.parents}:
                raise ValueError(f"refusing to extract archive entry outside destination: `{member.name}`")
        tar.extractall(destination)
    roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise ValueError("expected a single extracted archive root")
    return roots[0]


def _fetch_upstream_archive(repo: str, ref: str) -> bytes:
    archive_url = GITHUB_ARCHIVE_URL.format(repo=repo, ref=ref)
    request = urllib.request.Request(
        archive_url,
        headers={"User-Agent": "charness-support-sync/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
    except urllib.error.URLError as exc:
        raise ValueError(f"failed to fetch upstream support archive `{archive_url}`: {exc}") from exc


def _compute_tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            digest.update(f"symlink:{relative}->{os.readlink(path)}\n".encode("utf-8"))
            continue
        if path.is_dir():
            digest.update(f"dir:{relative}\n".encode("utf-8"))
            continue
        digest.update(f"file:{relative}\n".encode("utf-8"))
        digest.update(path.read_bytes())
        digest.update(b"\n")
    return digest.hexdigest()


def _promote_tree_to_cache(source_root: Path, *, manifest: dict[str, Any], digest: str) -> Path:
    cache_root = support_skill_cache_dir()
    cache_root.mkdir(parents=True, exist_ok=True)
    cache_path = cache_root / manifest["tool_id"] / digest
    if cache_path.exists():
        return cache_path
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    temp_target = cache_path.parent / f".tmp-{digest}"
    clear_materialized_target(temp_target)
    shutil.copytree(source_root, temp_target, symlinks=True)
    temp_target.replace(cache_path)
    return cache_path


def _resolve_upstream_source_path(manifest: dict[str, Any], *, upstream_checkouts: dict[str, Path]) -> Path:
    support = manifest["support_skill_source"]
    relative_source_path = Path(support["path"])
    fixture_root = _fixture_checkout_root(manifest["upstream_repo"], support.get("ref"))
    checkout_root = upstream_checkouts.get(manifest["upstream_repo"]) or fixture_root
    if checkout_root is not None:
        source_path = checkout_root / relative_source_path
        if not source_path.is_dir():
            raise ValueError(
                f"{manifest['tool_id']}: support source `{source_path}` must be a skill root directory "
                f"for `{manifest['upstream_repo']}`"
            )
        return source_path

    ref = support.get("ref")
    if not ref:
        raise ValueError(f"{manifest['tool_id']}: upstream_repo support source requires `ref`")
    with tempfile.TemporaryDirectory(prefix="charness-support-sync-") as temp_dir:
        temp_root = Path(temp_dir)
        archive_root = _safe_extract_tarball(
            _fetch_upstream_archive(manifest["upstream_repo"], ref),
            temp_root,
        )
        source_path = archive_root / relative_source_path
        if not source_path.is_dir():
            raise ValueError(
                f"{manifest['tool_id']}: upstream archive for `{manifest['upstream_repo']}@{ref}` "
                f"does not contain skill root `{support['path']}`"
            )
        promoted_root = _promote_tree_to_cache(
            source_path,
            manifest=manifest,
            digest=_compute_tree_digest(source_path),
        )
    return promoted_root


def _write_local_wrapper_to_cache(repo_root: Path, manifest: dict[str, Any], wrapper_text: str) -> tuple[Path, str]:
    digest = hashlib.sha256(wrapper_text.encode("utf-8")).hexdigest()
    cache_root = support_skill_cache_dir() / manifest["tool_id"] / digest
    if not cache_root.exists():
        cache_root.mkdir(parents=True, exist_ok=True)
        (cache_root / "SKILL.md").write_text(wrapper_text, encoding="utf-8")
    source_path = repo_root / manifest["support_skill_source"]["path"]
    if source_path.exists() and source_path.is_file():
        (cache_root / "UPSTREAM_REFERENCE.txt").write_text(
            str(source_path.relative_to(repo_root)) + "\n",
            encoding="utf-8",
        )
    return cache_root, digest


def materialize_repo_symlink(target_root: Path, dest_root: Path, repo_root: Path) -> list[str]:
    clear_materialized_target(dest_root)
    dest_root.parent.mkdir(parents=True, exist_ok=True)
    dest_root.symlink_to(target_root, target_is_directory=True)
    return [str(dest_root.relative_to(repo_root))]


def materialize_upstream_support(manifest: dict[str, Any], *, upstream_checkouts: dict[str, Path]) -> tuple[Path, str]:
    source_path = _resolve_upstream_source_path(manifest, upstream_checkouts=upstream_checkouts)
    digest = _compute_tree_digest(source_path)
    cache_path = _promote_tree_to_cache(source_path, manifest=manifest, digest=digest)
    return cache_path, digest


def materialize_support(repo_root: Path, manifest: dict[str, Any], *, upstream_checkouts: dict[str, Path]) -> dict[str, Any]:
    support = manifest["support_skill_source"]

    if support["source_type"] == "local_wrapper":
        cache_path, content_digest = _write_local_wrapper_to_cache(
            repo_root,
            manifest,
            render_generated_wrapper(manifest),
        )
    elif support["source_type"] == "upstream_repo":
        cache_path, content_digest = materialize_upstream_support(
            manifest,
            upstream_checkouts=upstream_checkouts,
        )

    link_root = generated_support_dir(repo_root) / support_link_name(manifest)
    materialized_paths = materialize_repo_symlink(cache_path, link_root, repo_root)
    return {
        "materialized_paths": materialized_paths,
        "cache_path": str(cache_path),
        "content_digest": content_digest,
    }


def discovery_stub_path(repo_root: Path, tool_id: str) -> Path:
    return discovery_stub_dir(repo_root) / f"{tool_id}.md"


def render_discovery_stub(*, manifest: dict[str, Any], support_skill_path: str) -> str:
    install = manifest.get("lifecycle", {}).get("install", {})
    intent_triggers = [item for item in manifest.get("intent_triggers", []) if isinstance(item, str) and item]
    trigger_line = ", ".join(intent_triggers) if intent_triggers else "no explicit trigger hints recorded"
    lines = [
        f"# {manifest['tool_id']}",
        "",
        f"Use when task intent matches: {trigger_line}.",
        "",
        "This is a repo-local discovery pointer for a synced support skill.",
        f"- support skill: `{support_skill_path}`",
        f"- integration manifest: `integrations/tools/{manifest['tool_id']}.json`",
    ]
    install_url = install.get("install_url")
    docs_url = install.get("docs_url")
    if isinstance(install_url, str) and install_url:
        lines.append(f"- install docs: {install_url}")
    elif isinstance(docs_url, str) and docs_url:
        lines.append(f"- docs: {docs_url}")
    lines.extend(
        [
            "- discovery command: `python3 skills/public/find-skills/scripts/list_capabilities.py --repo-root .`",
            "",
        ]
    )
    return "\n".join(lines)


def write_discovery_stub(repo_root: Path, manifest: dict[str, Any], *, support_skill_path: str) -> str:
    path = discovery_stub_path(repo_root, manifest["tool_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_discovery_stub(manifest=manifest, support_skill_path=support_skill_path) + "\n", encoding="utf-8")
    return str(path.relative_to(repo_root))
