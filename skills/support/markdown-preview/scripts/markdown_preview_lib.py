from __future__ import annotations

import importlib
import os
import re
import subprocess
import sys
from dataclasses import dataclass
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
DEFAULT_INCLUDE = ["README*.md", "docs/**/*.md", "specs/**/*.md"]
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
    widths = [item for item in raw if isinstance(item, int) and item > 0]
    if len(widths) != len(raw):
        raise SystemExit(f"`widths` items must be positive integers, got {raw!r}")
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
        config_path=str(config_path.relative_to(repo_root)) if config_path is not None else None,
    )


def merge_cli(
    config: PreviewConfig,
    *,
    files: list[str],
    widths: list[int],
    artifact_dir: str | None,
    backend: str | None,
    changed_only: bool,
) -> PreviewConfig:
    return PreviewConfig(
        enabled=config.enabled,
        backend=_normalize_backend(backend or config.backend),
        widths=_normalize_widths(widths or config.widths),
        include=_normalize_include(files or config.include),
        on_change_only=config.on_change_only or changed_only,
        artifact_dir=artifact_dir or config.artifact_dir,
        config_path=config.config_path,
    )


def _expand_pattern(repo_root: Path, pattern: str) -> list[Path]:
    raw_path = Path(pattern)
    if raw_path.is_absolute():
        return [raw_path] if raw_path.is_file() else []
    if any(char in pattern for char in GLOB_CHARS):
        return sorted(path for path in repo_root.glob(pattern) if path.is_file())
    candidate = repo_root / pattern
    return [candidate] if candidate.is_file() else []


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
    changed = set()
    for raw_line in completed.stdout.splitlines():
        if len(raw_line) < 4:
            continue
        path_text = raw_line[3:].split(" -> ", 1)[-1].strip()
        if path_text:
            changed.add(path_text)
    return changed, []


def select_targets(repo_root: Path, config: PreviewConfig) -> tuple[list[Path], list[str]]:
    warnings: list[str] = []
    seen: set[Path] = set()
    selected: list[Path] = []
    for pattern in config.include:
        matches = _expand_pattern(repo_root, pattern)
        if not matches:
            warnings.append(f"No Markdown files matched `{pattern}`.")
            continue
        for path in matches:
            resolved = path.resolve()
            if path.suffix.lower() == ".md" and resolved not in seen:
                seen.add(resolved)
                selected.append(resolved)
    if not config.on_change_only:
        return selected, warnings
    changed, git_warnings = _changed_markdown_paths(repo_root)
    warnings.extend(git_warnings)
    filtered = [
        path for path in selected if str(path.relative_to(repo_root)).replace(os.sep, "/") in changed
    ]
    return filtered, warnings


def artifact_stem(repo_root: Path, path: Path) -> str:
    relative = path.relative_to(repo_root).as_posix()
    if relative.lower().endswith(".md"):
        relative = relative[:-3]
    return SANITIZE_RE.sub("_", relative.replace("/", "__")).strip("_") or "artifact"
