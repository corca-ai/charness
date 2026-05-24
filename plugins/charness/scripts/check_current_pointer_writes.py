#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

CURRENT_POINTER_NAMES = {"latest.md", "latest.json"}
HELPER_FILES = {
    Path("scripts/current_pointer_writer_lib.py"),
    Path("plugins/charness/scripts/current_pointer_writer_lib.py"),
}
SCAN_ROOTS = (
    Path("scripts"),
    Path("skills/public"),
    Path("skills/support"),
    Path("plugins/charness/scripts"),
    Path("plugins/charness/skills"),
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    target: str
    reason: str


def _git_visible_python_files(repo_root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.py"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        files = []
        for raw in result.stdout.splitlines():
            path = repo_root / raw
            if path.is_file() and any(Path(raw).is_relative_to(root) for root in SCAN_ROOTS):
                files.append(path)
        return sorted(files)
    fallback: list[Path] = []
    for root in SCAN_ROOTS:
        scan_root = repo_root / root
        if scan_root.is_dir():
            fallback.extend(path for path in scan_root.rglob("*.py") if path.is_file())
    return sorted(fallback)


def _string_constants(node: ast.AST) -> set[str]:
    return {item.value for item in ast.walk(node) if isinstance(item, ast.Constant) and isinstance(item.value, str)}


def _pointer_names_in(node: ast.AST) -> set[str]:
    return _string_constants(node) & CURRENT_POINTER_NAMES


def _assigned_pointer_names(tree: ast.AST, constants: dict[str, str]) -> dict[str, str]:
    names: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        pointer_names = _pointer_names_in_resolved(node.value, constants, _scope_assigned_names(node))
        if not pointer_names:
            continue
        pointer_name = sorted(pointer_names)[0]
        for target in node.targets:
            if isinstance(target, ast.Name):
                names[target.id] = pointer_name
    return names


def _resolved_string_constants(tree: ast.AST) -> dict[str, str]:
    constants: dict[str, str] = {}
    body = tree.body if isinstance(tree, ast.Module) else []
    for node in body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            constants[target.id] = node.value.value
    return constants


def _attach_parent_links(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, "_parent", parent)


def _scope_assigned_names(node: ast.AST) -> set[str]:
    scope = getattr(node, "_parent", None)
    while scope is not None and not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
        scope = getattr(scope, "_parent", None)
    if scope is None:
        return set()
    names: set[str] = set()
    for child in ast.walk(scope):
        if isinstance(child, ast.Assign):
            for target in child.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def _pointer_names_in_resolved(node: ast.AST, constants: dict[str, str], shadowed: set[str]) -> set[str]:
    names = _pointer_names_in(node)
    for child in ast.walk(node):
        if (
            isinstance(child, ast.Name)
            and child.id not in shadowed
            and constants.get(child.id) in CURRENT_POINTER_NAMES
        ):
            names.add(constants[child.id])
    return names


def _call_target_name(call: ast.Call, assigned: dict[str, str], constants: dict[str, str]) -> str | None:
    shadowed = _scope_assigned_names(call)
    func = call.func
    if isinstance(func, ast.Attribute) and func.attr in {"write_text", "write_bytes"}:
        receiver = func.value
        if isinstance(receiver, ast.Name) and receiver.id in assigned:
            return assigned[receiver.id]
        pointer_names = _pointer_names_in_resolved(receiver, constants, shadowed)
        if pointer_names:
            return sorted(pointer_names)[0]
    if isinstance(func, ast.Attribute) and func.attr == "open":
        receiver = func.value
        pointer_names = set()
        if isinstance(receiver, ast.Name) and receiver.id in assigned:
            pointer_names.add(assigned[receiver.id])
        pointer_names.update(_pointer_names_in_resolved(receiver, constants, shadowed))
        if pointer_names:
            mode = call.args[0] if call.args else None
            mode_text = mode.value if isinstance(mode, ast.Constant) and isinstance(mode.value, str) else "r"
            if any(flag in mode_text for flag in ("w", "a", "+")):
                return sorted(pointer_names)[0]
    if isinstance(func, ast.Name) and func.id == "open" and call.args:
        pointer_names = _pointer_names_in_resolved(call.args[0], constants, shadowed)
        if pointer_names:
            mode = call.args[1] if len(call.args) > 1 else None
            mode_text = mode.value if isinstance(mode, ast.Constant) and isinstance(mode.value, str) else "r"
            if any(flag in mode_text for flag in ("w", "a", "+")):
                return sorted(pointer_names)[0]
    return None


def scan_path(repo_root: Path, path: Path) -> list[Finding]:
    relative = path.relative_to(repo_root)
    if relative in HELPER_FILES:
        return []
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text, filename=str(relative))
    except SyntaxError:
        return []
    _attach_parent_links(tree)
    constants = _resolved_string_constants(tree)
    assigned = _assigned_pointer_names(tree, constants)
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = _call_target_name(node, assigned, constants)
        if target is None:
            continue
        findings.append(
            Finding(
                path=relative.as_posix(),
                line=getattr(node, "lineno", 0),
                target=target,
                reason="direct write to current-pointer filename; use scripts.current_pointer_writer_lib",
            )
        )
    return findings


def scan_repo(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _git_visible_python_files(repo_root):
        findings.extend(scan_path(repo_root, path))
    return sorted(findings, key=lambda item: (item.path, item.line, item.target))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-empty", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    findings = scan_repo(repo_root)
    payload = {
        "status": "clean" if not findings else "findings",
        "finding_count": len(findings),
        "findings": [asdict(item) for item in findings],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif findings:
        for item in findings:
            print(f"{item.path}:{item.line}: {item.reason} (`{item.target}`)")
    else:
        print("No direct current-pointer writes found.")
    return 1 if args.require_empty and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
