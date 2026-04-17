#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _find_repo_root() -> Path:
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        if (ancestor / "runtime_bootstrap.py").is_file() and (ancestor / "scripts").is_dir():
            return ancestor
    raise ImportError("runtime_bootstrap.py not found")


REPO_ROOT = _find_repo_root()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

load_yaml_file = importlib.import_module("scripts.adapter_lib").load_yaml_file


DEFAULT_WIDTHS = [100]
DEFAULT_INCLUDE = [
    "README*.md",
    "INSTALL.md",
    "UNINSTALL.md",
    "docs/**/*.md",
    "specs/**/*.md",
]
DEFAULT_ARTIFACT_DIR = ".artifacts/markdown-preview"
SUPPORTED_BACKENDS = {"glow"}
CONFIG_SEARCH_PATHS = [
    Path(".agents/markdown-preview.yaml"),
    Path(".codex/markdown-preview.yaml"),
    Path(".claude/markdown-preview.yaml"),
    Path("docs/markdown-preview.yaml"),
    Path("markdown-preview.yaml"),
]
GLOB_CHARS = set("*?[]")
SANITIZE_RE = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True)
class PreviewConfig:
    enabled: bool
    backend: str
    widths: list[int]
    include: list[str]
    on_change_only: bool
    artifact_dir: str
    config_path: str | None


def _normalize_backend(value: Any) -> str:
    backend = str(value or "glow").strip()
    if backend not in SUPPORTED_BACKENDS:
        supported = ", ".join(sorted(SUPPORTED_BACKENDS))
        raise SystemExit(
            f"Unsupported markdown preview backend `{backend}`. Supported backend(s): {supported}."
        )
    return backend


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--file", action="append", default=[])
    parser.add_argument("--width", action="append", type=int, default=[])
    parser.add_argument("--artifact-dir")
    parser.add_argument("--backend")
    parser.add_argument("--changed-only", action="store_true")
    return parser.parse_args()


def _normalize_bool(value: Any, *, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
    raise SystemExit(f"Expected a boolean-compatible value, got {value!r}")


def _normalize_widths(raw: Any) -> list[int]:
    if raw is None:
        return list(DEFAULT_WIDTHS)
    if not isinstance(raw, list) or not raw:
        raise SystemExit("`widths` must be a non-empty list")
    widths: list[int] = []
    for item in raw:
        if not isinstance(item, int):
            raise SystemExit(f"`widths` items must be integers, got {item!r}")
        if item <= 0:
            raise SystemExit(f"`widths` items must be positive, got {item!r}")
        widths.append(item)
    return widths


def _normalize_include(raw: Any) -> list[str]:
    if raw is None:
        return list(DEFAULT_INCLUDE)
    if not isinstance(raw, list) or not all(isinstance(item, str) and item for item in raw):
        raise SystemExit("`include` must be a list of non-empty strings")
    return list(raw)


def _locate_config(repo_root: Path, explicit: Path | None) -> Path | None:
    if explicit is not None:
        path = explicit if explicit.is_absolute() else repo_root / explicit
        if not path.is_file():
            raise SystemExit(f"Config file not found: {path}")
        return path
    for rel in CONFIG_SEARCH_PATHS:
        candidate = repo_root / rel
        if candidate.is_file():
            return candidate
    return None


def load_config(repo_root: Path, explicit: Path | None) -> PreviewConfig:
    config_path = _locate_config(repo_root, explicit)
    raw: dict[str, Any] = {}
    if config_path is not None:
        raw = load_yaml_file(config_path)
        if not isinstance(raw, dict):
            raise SystemExit("Markdown preview config must be a YAML mapping")
    return PreviewConfig(
        enabled=_normalize_bool(raw.get("enabled"), default=True),
        backend=_normalize_backend(raw.get("backend")),
        widths=_normalize_widths(raw.get("widths")),
        include=_normalize_include(raw.get("include")),
        on_change_only=_normalize_bool(raw.get("on_change_only"), default=False),
        artifact_dir=str(raw.get("artifact_dir") or DEFAULT_ARTIFACT_DIR),
        config_path=(str(config_path.relative_to(repo_root)) if config_path is not None else None),
    )


def merge_cli(config: PreviewConfig, args: argparse.Namespace) -> PreviewConfig:
    widths = args.width if args.width else config.widths
    include = list(args.file) if args.file else config.include
    artifact_dir = args.artifact_dir or config.artifact_dir
    backend = _normalize_backend(args.backend or config.backend)
    on_change_only = config.on_change_only or args.changed_only
    if not include:
        include = list(DEFAULT_INCLUDE)
    return PreviewConfig(
        enabled=config.enabled,
        backend=backend,
        widths=widths,
        include=include,
        on_change_only=on_change_only,
        artifact_dir=artifact_dir,
        config_path=config.config_path,
    )


def _expand_pattern(repo_root: Path, pattern: str) -> list[Path]:
    raw_path = Path(pattern)
    if raw_path.is_absolute():
        if raw_path.is_file():
            return [raw_path]
        return []
    if any(char in pattern for char in GLOB_CHARS):
        return sorted(path for path in repo_root.glob(pattern) if path.is_file())
    candidate = repo_root / pattern
    if candidate.is_file():
        return [candidate]
    return []


def _changed_markdown_paths(repo_root: Path) -> tuple[set[str], list[str]]:
    completed = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return set(), ["Unable to resolve changed files from git status; using configured scope as-is."]
    changed: set[str] = set()
    for raw_line in completed.stdout.splitlines():
        if len(raw_line) < 4:
            continue
        path_text = raw_line[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        normalized = path_text.strip()
        if normalized:
            changed.add(normalized)
    return changed, []


def select_targets(repo_root: Path, config: PreviewConfig) -> tuple[list[Path], list[str]]:
    warnings: list[str] = []
    selected: list[Path] = []
    seen: set[Path] = set()
    for pattern in config.include:
        matches = _expand_pattern(repo_root, pattern)
        if not matches:
            warnings.append(f"No Markdown files matched `{pattern}`.")
            continue
        for path in matches:
            if path.suffix.lower() != ".md":
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            selected.append(resolved)

    if not config.on_change_only:
        return selected, warnings

    changed, git_warnings = _changed_markdown_paths(repo_root)
    warnings.extend(git_warnings)
    if not changed:
        return [], warnings

    filtered = [
        path
        for path in selected
        if str(path.relative_to(repo_root)).replace(os.sep, "/") in changed
    ]
    return filtered, warnings


def artifact_stem(repo_root: Path, path: Path) -> str:
    relative = path.relative_to(repo_root).as_posix()
    if relative.lower().endswith(".md"):
        relative = relative[:-3]
    relative = relative.replace("/", "__")
    return SANITIZE_RE.sub("_", relative).strip("_") or "artifact"


def _backend_version(backend_path: str | None, backend: str) -> str | None:
    if backend_path is None:
        return None
    completed = subprocess.run(
        [backend, "--version"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    version_text = completed.stdout.strip() or completed.stderr.strip()
    return version_text or None


def _git_head(repo_root: Path) -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    head = completed.stdout.strip()
    return head or None


def _render_with_glow(path: Path, width: int) -> tuple[str | None, str | None]:
    completed = subprocess.run(
        ["glow", "-w", str(width), str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0:
        return completed.stdout, None
    error = completed.stderr.strip() or completed.stdout.strip() or "glow failed without output"
    return None, error


def _degraded_text(path: Path, *, backend: str, reason: str, repo_root: Path) -> str:
    source_text = path.read_text(encoding="utf-8")
    relative = path.relative_to(repo_root).as_posix()
    return "\n".join(
        [
            "MARKDOWN PREVIEW DEGRADED",
            f"backend: {backend}",
            f"reason: {reason}",
            f"source: {relative}",
            "",
            "The text below is raw Markdown source copied only as a reference aid.",
            "It is not equivalent to a rendered readability review.",
            "",
            "---",
            "",
            source_text,
            "",
        ]
    )


def write_artifact(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def render_targets(repo_root: Path, config: PreviewConfig, targets: list[Path]) -> dict[str, Any]:
    artifact_dir = (repo_root / config.artifact_dir).resolve()
    backend_path = shutil.which(config.backend) if config.backend == "glow" else None
    backend_version = _backend_version(backend_path, config.backend)
    warnings: list[str] = []
    preview_items: list[dict[str, Any]] = []
    overall_status = "success"

    for target in targets:
        relative = target.relative_to(repo_root).as_posix()
        for width in config.widths:
            artifact_name = f"{artifact_stem(repo_root, target)}.w{width}.txt"
            artifact_path = artifact_dir / artifact_name
            item: dict[str, Any] = {
                "source_path": relative,
                "width": width,
                "artifact_path": str(artifact_path.relative_to(repo_root)),
                "backend": config.backend,
                "source_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            }
            if backend_path is None:
                reason = f"{config.backend} not found on PATH"
                write_artifact(
                    artifact_path,
                    _degraded_text(target, backend=config.backend, reason=reason, repo_root=repo_root),
                )
                item["status"] = "degraded"
                item["reason"] = reason
                overall_status = "degraded" if overall_status == "success" else overall_status
                preview_items.append(item)
                continue

            rendered, error = _render_with_glow(target, width)
            if rendered is None:
                write_artifact(
                    artifact_path,
                    _degraded_text(target, backend=config.backend, reason=error or "backend error", repo_root=repo_root),
                )
                item["status"] = "backend-error"
                item["reason"] = error or "backend error"
                warnings.append(f"{relative} @ width {width}: {item['reason']}")
                overall_status = "partial"
                preview_items.append(item)
                continue

            write_artifact(artifact_path, rendered)
            item["status"] = "rendered"
            preview_items.append(item)

    payload = {
        "status": overall_status if targets else "no-targets",
        "repo_root": str(repo_root),
        "backend": config.backend,
        "backend_available": backend_path is not None,
        "backend_version": backend_version,
        "config_path": config.config_path,
        "artifact_dir": str(artifact_dir.relative_to(repo_root)),
        "git_head": _git_head(repo_root),
        "widths": list(config.widths),
        "target_count": len(targets),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "previews": preview_items,
        "warnings": warnings,
    }
    artifact_dir.mkdir(parents=True, exist_ok=True)
    write_artifact(artifact_dir / "manifest.json", json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return payload


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    config = merge_cli(load_config(repo_root, args.config), args)
    if not config.enabled:
        payload = {
            "status": "disabled",
            "repo_root": str(repo_root),
            "config_path": config.config_path,
            "warnings": ["Markdown preview is disabled by config."],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    targets, selection_warnings = select_targets(repo_root, config)
    payload = render_targets(repo_root, config, targets)
    payload["warnings"] = selection_warnings + payload["warnings"]
    manifest_path = repo_root / payload["artifact_dir"] / "manifest.json"
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
