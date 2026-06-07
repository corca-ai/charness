#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skill_ergonomics_lib as elib  # noqa: E402


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


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

# Advisory interpretation contract (see skills/shared/references/
# advisory-interpretation-contract.md): the ergonomics heuristics are an
# inference-layer proxy, so they self-declare blind spots and the question the
# `quality` consumer must answer before treating a hit as debt.
INTERPRETATION = {
    "measures": (
        "per-skill ergonomic/portability heuristic hits — long core, mode/option "
        "pressure, prose-ritual fences, ambiguous helper paths, package issue/dated "
        "anchors, host-surface references, and unlisted reference files (the "
        "`subcheck_counts` rollup)"
    ),
    "proxy_for": "skill packages that are hard to read, maintain, or port to another host",
    "blind_spots": (
        "lexical/structural counting — a long but well-sectioned core, an intentional "
        "host-surface reference inside an adapter example, or deliberate per-package "
        "boilerplate each counts as a hit; it cannot see whether the trigger boundary "
        "is honest or whether the prose actually reads well"
    ),
    "interpretation_question": (
        "which of these heuristic hits are real ergonomic/portability debt for THIS "
        "skill versus intentional structure the lexical heuristic cannot distinguish?"
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for the skill ergonomics inventory")
    parser.add_argument("--skill-path", action="append", default=[], help="Skill directory or SKILL.md to inventory (repeatable; defaults applied if omitted)")
    parser.add_argument("--max-core-lines", type=int, default=160, help="Non-empty line count above which a SKILL.md core is flagged as long")
    parser.add_argument("--json", action="store_true", help="Emit the full inventory payload as JSON")
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
        "interpretation": dict(INTERPRETATION),
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
        for advisory in payload.get("advisories", []):
            print(f"ADVISORY: {advisory['message']} Next action: {advisory['next_action']}")
        for item in skills:
            heuristics = ", ".join(item["heuristics"]) or "none"
            print(
                f"{item['skill_path']}: type={item['skill_type']} lines={item['core_nonempty_lines']} "
                f"refs={item['reference_file_count']} scripts={item['script_file_count']} "
                f"heuristics={heuristics}"
            )
        if skills:
            interpretation = payload["interpretation"]
            print(
                "INTERPRETATION (inference-layer heuristic, not a verdict): "
                f"measures {interpretation['measures']}; proxy for "
                f"{interpretation['proxy_for']}; blind spots: {interpretation['blind_spots']}. "
                f"Consumer must answer first: {interpretation['interpretation_question']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
