#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skill_ergonomics_lib as elib  # noqa: E402


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)

_scripts_skill_markdown_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.skill_markdown_lib")
_scripts_quality_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.quality_adapter_lib")
_scripts_vendored_path_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.vendored_path_lib")
load_quality_adapter = _scripts_quality_adapter_lib_module.load_quality_adapter_permissive
vendored_prefixes = _scripts_vendored_path_lib_module.vendored_prefixes
is_vendored = _scripts_vendored_path_lib_module.is_vendored
is_vendored_relative = _scripts_vendored_path_lib_module.is_vendored_relative

MARKDOWN_HELPERS = {
    "count_fence_blocks": _scripts_skill_markdown_lib_module.count_fence_blocks,
    "extract_h2_section_lines": _scripts_skill_markdown_lib_module.extract_h2_section_lines,
    "strip_fenced_lines": _scripts_skill_markdown_lib_module.strip_fenced_lines,
    "strip_frontmatter": _scripts_skill_markdown_lib_module.strip_frontmatter,
}

DEFAULT_REVIEW_PROMPTS = elib.DEFAULT_REVIEW_PROMPTS
RUNTIME_INSTALL_REVIEW_PROMPTS = elib.RUNTIME_INSTALL_REVIEW_PROMPTS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--skill-path", action="append", default=[])
    parser.add_argument("--max-core-lines", type=int, default=160)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def _iter_skill_path_value(repo_root: Path, value: str) -> Iterable[Path]:
    path = (repo_root / value).resolve()
    if path.name == "SKILL.md":
        yield path
        return
    direct_skill = path / "SKILL.md"
    if direct_skill.is_file():
        yield direct_skill
        return
    if path.is_dir():
        yield from sorted(candidate for candidate in path.glob("*/SKILL.md") if "generated" not in candidate.parts)


def _adapter_payload(repo_root: Path) -> dict[str, object]:
    adapter = load_quality_adapter(repo_root)
    return adapter if isinstance(adapter, dict) else {}


def _adapter_data(adapter: dict[str, object]) -> dict[str, object]:
    data = adapter.get("data", {})
    return data if isinstance(data, dict) else {}


def _string_list(data: dict[str, object], key: str) -> list[str]:
    values = data.get(key, [])
    return values if isinstance(values, list) and all(isinstance(item, str) for item in values) else []


def _adapter_skill_paths(data: dict[str, object]) -> list[str]:
    return _string_list(data, "skill_ergonomics_skill_paths")


def iter_skill_paths(
    repo_root: Path,
    requested: list[str],
    adapter_skill_paths: list[str] | None = None,
) -> Iterable[Path]:
    seen: set[Path] = set()
    values = requested or (
        adapter_skill_paths
        if adapter_skill_paths is not None
        else _adapter_skill_paths(_adapter_data(_adapter_payload(repo_root)))
    )
    used_configured_paths = bool(values)
    if values:
        for value in values:
            for skill_path in _iter_skill_path_value(repo_root, value):
                if skill_path in seen:
                    continue
                seen.add(skill_path)
                yield skill_path
        if requested or used_configured_paths:
            return
    for parent in (repo_root / "skills", repo_root / "skills" / "public", repo_root / "skills" / "support"):
        if not parent.is_dir():
            continue
        for skill_path in sorted(parent.glob("*/SKILL.md")):
            if "generated" in skill_path.parts:
                continue
            if skill_path not in seen:
                seen.add(skill_path)
                yield skill_path


def inventory_skill(repo_root: Path, skill_path: Path, *, max_core_lines: int, runtime_install_prefixes: list[str] | None = None) -> dict[str, object]:
    prefixes = runtime_install_prefixes or []
    return elib.inventory_skill(
        repo_root,
        skill_path,
        max_core_lines=max_core_lines,
        is_runtime_install=lambda rel: is_vendored_relative(rel, prefixes),
        markdown_helpers=MARKDOWN_HELPERS,
    )


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    adapter = _adapter_payload(repo_root)
    data = _adapter_data(adapter)
    adapter_skill_paths = _adapter_skill_paths(data)
    runtime_prefixes = vendored_prefixes(_string_list(data, "skill_ergonomics_runtime_install_skill_paths"))
    vendored = vendored_prefixes(_string_list(data, "vendored_paths"))
    skill_paths = [
        path
        for path in iter_skill_paths(repo_root, args.skill_path, adapter_skill_paths=adapter_skill_paths)
        if path.is_file() and not is_vendored(repo_root, path, vendored)
    ]
    skills = [
        inventory_skill(repo_root, skill_path, max_core_lines=args.max_core_lines, runtime_install_prefixes=runtime_prefixes)
        for skill_path in skill_paths
    ]
    status = elib.scope_status(len(skills), args.skill_path, adapter_skill_paths)
    findings = elib.finding_status(skills)
    payload = {
        "repo_root": str(repo_root),
        "max_core_lines": args.max_core_lines,
        "adapter_path": adapter.get("path"),
        "adapter_valid": adapter.get("valid", True),
        "adapter_errors": adapter.get("errors", []),
        "adapter_warnings": adapter.get("warnings", []),
        "adapter_load_mode": adapter.get("load_mode", "permissive"),
        **status,
        **findings,
        "skills": skills,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload["status"] == "unconfigured":
            print(f"status=unconfigured: {payload.get('reason', '')}")
        elif payload["finding_status"] == "zero_heuristic_findings":
            print(
                f"status=zero_heuristic_findings: checked {payload['checked_skill_count']} skill(s); "
                "prose review still required for trigger boundaries and judgment-only risks."
            )
        elif payload["finding_status"] == "not_evaluated":
            print(f"status=not_evaluated: {payload.get('reason', '')}")
        if payload["adapter_valid"] is False:
            print("adapter=invalid: advisory inventory is best-effort until adapter errors are repaired.")
        for item in skills:
            heuristics = ", ".join(item["heuristics"]) or "none"
            print(
                f"{item['skill_path']}: type={item['skill_type']} lines={item['core_nonempty_lines']} "
                f"refs={item['reference_file_count']} scripts={item['script_file_count']} "
                f"heuristics={heuristics}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
