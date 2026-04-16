from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from scripts.adapter_lib import load_yaml_file

ADAPTER_CANDIDATES = (
    Path(".agents/init-repo-adapter.yaml"),
    Path(".codex/init-repo-adapter.yaml"),
    Path(".claude/init-repo-adapter.yaml"),
    Path("docs/init-repo-adapter.yaml"),
    Path("init-repo-adapter.yaml"),
)
SOURCE_GUARD_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*fixed\s*\|\s*([^|]+?)\s*\|")


def load_init_repo_adapter(repo_root: Path) -> tuple[dict[str, Any], str | None, list[dict[str, str]]]:
    adapter_path = next((repo_root / candidate for candidate in ADAPTER_CANDIDATES if (repo_root / candidate).is_file()), None)
    if adapter_path is None:
        return {}, None, []
    text = adapter_path.read_text(encoding="utf-8")
    first = next((line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")), "")
    if first.startswith("- "):
        return (
            {},
            str(adapter_path),
            [{"type": "adapter_root_not_mapping", "message": "init-repo adapter root must be a mapping."}],
        )
    raw = load_yaml_file(adapter_path)
    if isinstance(raw, dict):
        return raw, str(adapter_path), []
    return (
        {},
        str(adapter_path),
        [{"type": "adapter_root_not_mapping", "message": "init-repo adapter root must be a mapping."}],
    )


def surface_overrides(adapter_data: dict[str, Any]) -> dict[str, Any]:
    surfaces = adapter_data.get("surfaces")
    return surfaces if isinstance(surfaces, dict) else {}


def _iter_markdown_files(repo_root: Path) -> list[Path]:
    ignored_parts = {".git", ".charness", "node_modules", "__pycache__"}
    files: list[Path] = []
    for path in repo_root.rglob("*.md"):
        if any(part in ignored_parts for part in path.relative_to(repo_root).parts):
            continue
        files.append(path)
    return sorted(files)


def _source_guard_rows(repo_root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for spec_path in _iter_markdown_files(repo_root):
        text = spec_path.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            match = SOURCE_GUARD_RE.match(line)
            if not match:
                continue
            target, pattern = (part.strip() for part in match.groups())
            rows.append(
                {
                    "spec_path": spec_path.relative_to(repo_root).as_posix(),
                    "line": line_no,
                    "target_path": target,
                    "pattern_chars": len(pattern),
                }
            )
    return rows


def _matcher_normalizes(adapter_data: dict[str, Any]) -> bool:
    matcher = adapter_data.get("source_guard_matcher")
    if isinstance(matcher, dict) and matcher.get("normalize_whitespace") is True:
        return True
    return adapter_data.get("source_guard_normalizes_whitespace") is True


def prose_wrap_state(repo_root: Path, adapter_data: dict[str, Any]) -> dict[str, object]:
    raw_policy = adapter_data.get("prose_wrap_policy", "semantic")
    policy = raw_policy if raw_policy in {"semantic", "column"} else "invalid"
    guards = _source_guard_rows(repo_root)
    normalizes = _matcher_normalizes(adapter_data)
    explicit_override = adapter_data.get("allow_column_wrap_fixed_guards") is True
    warnings: list[dict[str, object]] = []
    status = "ok" if policy != "invalid" else "invalid_policy"

    if policy == "column" and guards and not normalizes and not explicit_override:
        status = "requires_override"
        warnings.append(
            {
                "type": "column_wrap_fixed_guard_requires_override",
                "message": (
                    "Column-wrapped prose with fixed-string source guards requires "
                    "whitespace-normalized matching or allow_column_wrap_fixed_guards: true."
                ),
                "required_override": "source_guard_matcher.normalize_whitespace: true",
            }
        )

    return {
        "policy": policy,
        "source": "adapter" if "prose_wrap_policy" in adapter_data else "default",
        "source_guard_count": len(guards),
        "source_guards": guards,
        "matcher_normalizes_whitespace": normalizes,
        "explicit_override": explicit_override,
        "status": status,
        "warnings": warnings,
    }
