from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from scripts.adapter_lib import render_yaml_mapping

LIB_REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_SEARCH_PATHS = (
    Path(".agents/markdown-preview.yaml"),
    Path(".codex/markdown-preview.yaml"),
    Path(".claude/markdown-preview.yaml"),
    Path("docs/markdown-preview.yaml"),
    Path("markdown-preview.yaml"),
)
DEFAULT_OUTPUT_PATH = Path(".agents/markdown-preview.yaml")
DEFAULT_WIDTHS = [80, 100]
DEFAULT_ARTIFACT_DIR = ".artifacts/markdown-preview"
DEFAULT_INCLUDE_CANDIDATES = [
    "README*.md",
    "INSTALL.md",
    "UNINSTALL.md",
    "docs/**/*.md",
    "specs/**/*.md",
]
HELPER_RELATIVE_PATHS = (
    Path("skills/support/markdown-preview/scripts/render_markdown_preview.py"),
    Path("support/markdown-preview/scripts/render_markdown_preview.py"),
)
GLOB_CHARS = set("*?[]")


def _expand_pattern(repo_root: Path, pattern: str) -> list[Path]:
    if any(char in pattern for char in GLOB_CHARS):
        return sorted(path for path in repo_root.glob(pattern) if path.is_file())
    candidate = repo_root / pattern
    return [candidate] if candidate.is_file() else []


def existing_markdown_preview_config(repo_root: Path) -> str | None:
    for rel_path in CONFIG_SEARCH_PATHS:
        if (repo_root / rel_path).is_file():
            return rel_path.as_posix()
    return None


def infer_markdown_preview_include(repo_root: Path) -> list[str]:
    selected: list[str] = []
    for pattern in DEFAULT_INCLUDE_CANDIDATES:
        if _expand_pattern(repo_root, pattern):
            selected.append(pattern)
    return selected


def render_markdown_preview_config(
    *,
    include: list[str],
    widths: list[int],
    artifact_dir: str,
    on_change_only: bool,
) -> str:
    return render_yaml_mapping(
        [
            ("enabled", True),
            ("backend", "glow"),
            ("widths", widths),
            ("include", include),
            ("on_change_only", on_change_only),
            ("artifact_dir", artifact_dir),
        ]
    )


def _helper_script_path() -> Path:
    for rel_path in HELPER_RELATIVE_PATHS:
        candidate = LIB_REPO_ROOT / rel_path
        if candidate.is_file():
            return candidate
    rendered = ", ".join(str(path) for path in HELPER_RELATIVE_PATHS)
    raise FileNotFoundError(f"Markdown preview helper not found. Searched: {rendered}")


def preview_command(repo_root: Path, config_path: str) -> list[str]:
    helper_path = _helper_script_path()
    return [
        sys.executable,
        str(helper_path),
        "--repo-root",
        str(repo_root),
        "--config",
        str(repo_root / config_path),
    ]


def scaffold_markdown_preview(
    repo_root: Path,
    *,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    widths: list[int] | None = None,
    artifact_dir: str = DEFAULT_ARTIFACT_DIR,
    on_change_only: bool = False,
    dry_run: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    existing_config = existing_markdown_preview_config(repo_root)
    if existing_config is not None:
        return {
            "status": "existing-config",
            "config_status": "preserved",
            "config_path": existing_config,
            "widths": None,
            "artifact_dir": None,
            "include": None,
            "warnings": [],
            "preview_command": preview_command(repo_root, existing_config),
        }

    include = infer_markdown_preview_include(repo_root)
    if not include:
        return {
            "status": "not-applicable",
            "config_status": "not-written",
            "config_path": None,
            "widths": widths or list(DEFAULT_WIDTHS),
            "artifact_dir": artifact_dir,
            "include": [],
            "warnings": [
                "No checked-in Markdown files matched the candidate preview scope.",
            ],
            "candidate_include_patterns": list(DEFAULT_INCLUDE_CANDIDATES),
            "preview_command": None,
        }

    final_widths = list(widths or DEFAULT_WIDTHS)
    config_text = render_markdown_preview_config(
        include=include,
        widths=final_widths,
        artifact_dir=artifact_dir,
        on_change_only=on_change_only,
    )
    resolved_output = output_path if output_path.is_absolute() else repo_root / output_path
    relative_output = resolved_output.relative_to(repo_root).as_posix()
    existing_text = resolved_output.read_text(encoding="utf-8") if resolved_output.is_file() else None

    if existing_text is None:
        config_status = "would-write" if dry_run else "written"
    elif existing_text == config_text:
        config_status = "unchanged"
    elif not force:
        config_status = "preserved-existing"
    else:
        config_status = "would-update" if dry_run else "updated"

    if config_status in {"written", "updated"}:
        resolved_output.parent.mkdir(parents=True, exist_ok=True)
        resolved_output.write_text(config_text, encoding="utf-8")

    warnings: list[str] = []
    if config_status == "preserved-existing":
        warnings.append(
            f"Config already exists at {relative_output}; rerun with --force to replace it."
        )

    return {
        "status": "scaffolded",
        "config_status": config_status,
        "config_path": relative_output,
        "widths": final_widths,
        "artifact_dir": artifact_dir,
        "include": include,
        "warnings": warnings,
        "preview_command": preview_command(repo_root, relative_output),
    }


def run_markdown_preview(repo_root: Path, *, config_path: str) -> tuple[int, dict[str, Any] | None, str]:
    command = preview_command(repo_root, config_path)
    completed = subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    payload: dict[str, Any] | None = None
    if completed.stdout.strip():
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            payload = None
    return completed.returncode, payload, completed.stderr.strip()
