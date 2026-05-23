#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


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


def _read_package_json(repo_root: Path) -> dict[str, Any] | None:
    path = repo_root / "package.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _detect_lefthook_lint(repo_root: Path) -> dict[str, Any] | None:
    for name in ("lefthook.yml", "lefthook.yaml"):
        path = repo_root / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for stage in ("pre-commit", "pre-push"):
            block = _yaml_block(text, stage)
            if not block.strip():
                continue
            if re.search(r"lint|eslint|ruff|clippy|golangci|pylint|format", block, re.IGNORECASE):
                return {
                    "command": f"lefthook run {stage}",
                    "surface": "lefthook",
                    "source": str(path.relative_to(repo_root)),
                    "stage": stage,
                }
    return None


def _detect_git_hook_lint(repo_root: Path) -> dict[str, Any] | None:
    for stage in ("pre-commit", "pre-push"):
        for relative in (Path(".githooks") / stage, Path(".husky") / stage):
            path = repo_root / relative
            if path.is_file():
                return {
                    "command": f"bash {relative.as_posix()}",
                    "surface": "git_hook",
                    "source": relative.as_posix(),
                    "stage": stage,
                }
    return None


def _yaml_block(text: str, key: str) -> str:
    block, started, indent = [], False, 0
    for line in text.splitlines():
        stripped = line.strip()
        current_indent = len(line) - len(line.lstrip(" "))
        if not started:
            if stripped == f"{key}:":
                started, indent = True, current_indent
                block.append(line)
            continue
        if stripped and current_indent <= indent and re.match(r"[A-Za-z0-9_-]+:\s*$", stripped):
            break
        block.append(line)
    return "\n".join(block)


def _detect_npm_lint(repo_root: Path) -> dict[str, Any] | None:
    payload = _read_package_json(repo_root)
    if payload is None:
        return None
    scripts = payload.get("scripts", {}) if isinstance(payload.get("scripts"), dict) else {}
    for name in ("lint", "verify", "quality"):
        if isinstance(scripts.get(name), str):
            runner = "npm"
            if (repo_root / "pnpm-lock.yaml").is_file():
                runner = "pnpm"
            elif (repo_root / "yarn.lock").is_file():
                runner = "yarn"
            elif (repo_root / "bun.lockb").is_file():
                runner = "bun"
            return {
                "command": f"{runner} run {name}",
                "surface": "package_json",
                "source": "package.json",
                "script": name,
            }
    return None


def _detect_python_lint(repo_root: Path) -> dict[str, Any] | None:
    pyproject = repo_root / "pyproject.toml"
    if pyproject.is_file():
        text = pyproject.read_text(encoding="utf-8", errors="ignore")
        # Require an actual lint subtable; bare `[tool.ruff]` for formatter-only
        # settings (e.g. line-length) is not a lint enforcement signal.
        if re.search(r"\[tool\.ruff\.lint", text) or re.search(r"\[tool\.ruff\.lint\.", text):
            return {"command": "ruff check .", "surface": "ruff_config", "source": "pyproject.toml"}
        if re.search(r"\[tool\.flake8", text) or (repo_root / ".flake8").is_file():
            return {"command": "flake8", "surface": "flake8_config", "source": "pyproject.toml"}
    if (repo_root / ".ruff.toml").is_file() or (repo_root / "ruff.toml").is_file():
        text = ""
        for name in ("ruff.toml", ".ruff.toml"):
            path = repo_root / name
            if path.is_file():
                text = path.read_text(encoding="utf-8", errors="ignore")
                break
        if re.search(r"^\s*\[lint", text, re.MULTILINE) or "select" in text or "ignore" in text:
            return {"command": "ruff check .", "surface": "ruff_config", "source": "ruff.toml"}
    return None


def _detect_cargo_lint(repo_root: Path) -> dict[str, Any] | None:
    if (repo_root / "Cargo.toml").is_file():
        return {"command": "cargo clippy --all-targets", "surface": "cargo", "source": "Cargo.toml"}
    return None


def _detect_go_lint(repo_root: Path) -> dict[str, Any] | None:
    if (repo_root / "go.mod").is_file():
        return {"command": "go vet ./...", "surface": "go_mod", "source": "go.mod"}
    return None


def detect_lint_gate(repo_root: Path) -> dict[str, Any]:
    """Probe the repo for a likely lint/static-analysis gate.

    Probe order: lefthook pre-commit/pre-push (when its block mentions a lint
    tool) -> package.json scripts.lint -> Python (ruff/flake8) -> Cargo clippy
    -> go vet. Returns the first match. Repos can override or disable detection
    via .agents/impl-adapter.yaml verification_tools (declare the canonical
    command there).
    """
    for probe in (
        _detect_lefthook_lint,
        _detect_git_hook_lint,
        _detect_npm_lint,
        _detect_python_lint,
        _detect_cargo_lint,
        _detect_go_lint,
    ):
        hit = probe(repo_root)
        if hit is not None:
            return {"detected": True, **hit}
    return {"detected": False, "command": None, "surface": None, "source": None}


def _group_specs(adapter_data: dict[str, object]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for field in ("verification_tools", "ui_verification_tools"):
        for raw_spec in adapter_data.get(field, []):
            spec = str(raw_spec)
            grouped.setdefault(spec, []).append(field)
    return grouped


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root to survey for verification tools")
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

    lint_gate = detect_lint_gate(repo_root)
    if lint_gate["detected"]:
        warnings.append(
            f"Lint gate detected ({lint_gate['surface']}): run `{lint_gate['command']}` before closeout and record Lint Gate in the slice report."
        )
    else:
        warnings.append(
            "No standing lint gate detected; record `Lint Gate: not-detected` in closeout if the slice touches source files."
        )

    output = {
        "adapter_found": adapter["found"],
        "adapter_valid": adapter["valid"],
        "adapter_path": adapter["path"],
        "tool_checks": [asdict(check) for check in checks],
        "missing_tools": missing,
        "missing_ui_tools": missing_ui,
        "install_proposals": adapter["data"].get("verification_install_proposals", []) if missing else [],
        "lint_gate": lint_gate,
        "warnings": warnings,
        "summary": {
            "configured_total": len(checks),
            "available_total": sum(1 for check in checks if check.available),
            "missing_total": len(missing),
            "configured_ui_total": sum(1 for check in checks if "ui_verification_tools" in check.groups),
            "missing_ui_total": len(missing_ui),
            "lint_gate_detected": lint_gate["detected"],
        },
    }
    sys.stdout.write(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
