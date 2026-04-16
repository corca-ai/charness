#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


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







_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter

SKILL_DIR_CANDIDATES = (
    Path(".agents/skills"),
    Path(".codex/skills"),
    Path.home() / ".codex" / "skills",
    Path.home() / ".agents" / "skills",
)


@dataclass
class ToolCheck:
    spec: str
    groups: list[str]
    kind: str
    name: str
    available: bool
    resolved_path: str | None = None
    warning: str | None = None


def _parse_spec(spec: str) -> tuple[str, str, str | None]:
    if ":" not in spec:
        return "command", spec, "Tool spec should use an explicit prefix; treating bare name as cmd:<name>"
    prefix, _, name = spec.partition(":")
    prefix = prefix.strip()
    name = name.strip()
    if prefix == "cmd":
        return "command", name, None
    if prefix == "skill":
        return "skill", name, None
    return "unknown", name or spec, f"Unsupported tool spec prefix: {prefix}"


def _resolve_skill(name: str, repo_root: Path) -> tuple[Path | None, str | None]:
    for candidate in SKILL_DIR_CANDIDATES:
        base = candidate if candidate.is_absolute() else repo_root / candidate
        path = base / name
        if path.is_symlink() and not path.exists():
            return None, f"Broken skill symlink: {path}"
        if path.is_dir():
            return path.resolve(), None
        markdown_path = path.with_suffix(".md")
        if markdown_path.is_symlink() and not markdown_path.exists():
            return None, f"Broken skill symlink: {markdown_path}"
        if markdown_path.is_file():
            return markdown_path.resolve(), None
    return None, None


def _check_tool(spec: str, groups: list[str], repo_root: Path) -> ToolCheck:
    kind, name, warning = _parse_spec(spec)
    if kind == "command":
        resolved = shutil.which(name)
        return ToolCheck(
            spec=spec,
            groups=groups,
            kind=kind,
            name=name,
            available=resolved is not None,
            resolved_path=resolved,
            warning=warning,
        )
    if kind == "skill":
        resolved, skill_warning = _resolve_skill(name, repo_root)
        return ToolCheck(
            spec=spec,
            groups=groups,
            kind=kind,
            name=name,
            available=resolved is not None,
            resolved_path=str(resolved) if resolved else None,
            warning=skill_warning or warning,
        )
    return ToolCheck(spec=spec, groups=groups, kind=kind, name=name, available=False, warning=warning)


def _group_specs(adapter_data: dict[str, object]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for field in ("verification_tools", "ui_verification_tools"):
        for raw_spec in adapter_data.get(field, []):
            spec = str(raw_spec)
            grouped.setdefault(spec, []).append(field)
    return grouped


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    grouped = _group_specs(adapter["data"])
    checks = [_check_tool(spec, groups, repo_root) for spec, groups in grouped.items()]

    missing = [check.spec for check in checks if not check.available]
    missing_ui = [
        check.spec for check in checks if not check.available and "ui_verification_tools" in check.groups
    ]
    warnings = [check.warning for check in checks if check.warning]
    if missing_ui:
        warnings.append("Preferred UI verification tools are missing; do not claim rendered behavior without a real viewport path.")
    if missing and adapter["data"].get("verification_install_proposals"):
        warnings.append("Repo-specific verification install proposals are available.")

    output = {
        "adapter_found": adapter["found"],
        "adapter_valid": adapter["valid"],
        "adapter_path": adapter["path"],
        "tool_checks": [asdict(check) for check in checks],
        "missing_tools": missing,
        "missing_ui_tools": missing_ui,
        "install_proposals": adapter["data"].get("verification_install_proposals", []) if missing else [],
        "warnings": warnings,
        "summary": {
            "configured_total": len(checks),
            "available_total": sum(1 for check in checks if check.available),
            "missing_total": len(missing),
            "configured_ui_total": sum(1 for check in checks if "ui_verification_tools" in check.groups),
            "missing_ui_total": len(missing_ui),
        },
    }
    sys.stdout.write(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
