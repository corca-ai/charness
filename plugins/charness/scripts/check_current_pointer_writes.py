#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

CURRENT_POINTER_NAMES = {"latest.md", "latest.json"}
WRITE_CALL_TOKENS = ("write_text", "write_bytes", "open")
HELPER_FILES = {
    Path("scripts/current_pointer_writer_lib.py"),
}
SCAN_ROOTS = (
    Path("scripts"),
    Path("skills/public"),
    Path("skills/support"),
    # `skills/shared` was omitted, so a direct current-pointer write there was
    # never scanned and the gate reported clean over a scope excluding it (D9).
    # Confirmed: an identical violation was caught under `scripts/` and
    # `skills/public/` and invisible under `skills/shared/`.
    Path("skills/shared"),
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


_POINTER_STEMS = tuple(sorted({name.split(".", 1)[0] for name in CURRENT_POINTER_NAMES}))


def _could_write_current_pointer(text: str) -> bool:
    # Matches the STEM (`latest`), not only the full filename. Requiring
    # `latest.md`/`latest.json` verbatim meant a file that builds the name —
    # `f"latest.{ext}"` — never reached the AST scan at all, so the computed-name
    # detector below could not have fired even once (D9).
    return any(f"{stem}." in text for stem in _POINTER_STEMS) and any(
        token in text for token in WRITE_CALL_TOKENS
    )


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


def _computed_pointer_name_in(node: ast.AST) -> str | None:
    """A pointer filename BUILT at runtime rather than written as a literal.

    ``_pointer_names_in`` matches string constants only, so ``f"latest.{ext}"``
    or ``"latest" + suffix`` produced a path this gate could not see and it
    reported clean over it (D9). Deliberately narrow — an f-string or
    concatenation whose literal head is a pointer stem — because the point is to
    refuse silence about a computed pointer name, not to chase every expression
    that could theoretically evaluate to one.
    """
    for child in ast.walk(node):
        parts: list[str] = []
        if isinstance(child, ast.JoinedStr):
            parts = [v.value for v in child.values if isinstance(v, ast.Constant) and isinstance(v.value, str)]
        elif isinstance(child, ast.BinOp) and isinstance(child.op, ast.Add):
            # BOTH operands. Inspecting only `left` missed the shape that
            # actually occurs: Python parses `a + b + c` left-associatively, so
            # in `str(out) + "/latest." + ext` the pointer-ish literal is only
            # ever a RIGHT operand and was never looked at.
            parts = [
                side.value
                for side in (child.left, child.right)
                if isinstance(side, ast.Constant) and isinstance(side.value, str)
            ]
        for part in parts:
            head = part.split("/")[-1]
            if any(head == f"{stem}." or head.startswith(f"{stem}.") for stem in _POINTER_STEMS):
                return f"{head}<computed>"
            if head in _POINTER_STEMS:
                return f"{head}.<computed>"
    return None


def _write_target_node(call: ast.Call) -> ast.AST | None:
    """The expression a MUTATING write call targets, or ``None``.

    One dispatch for `Path.write_text` / `write_bytes`, `Path.open(mode=...)`
    and builtin `open(path, mode)`. The literal and computed resolvers below had
    grown a copy each, which is one place for the three call shapes to drift
    apart and two places to fix when a fourth appears.
    """
    func = call.func
    if isinstance(func, ast.Attribute) and func.attr in {"write_text", "write_bytes"}:
        return func.value
    if isinstance(func, ast.Attribute) and func.attr == "open":
        if _write_mode_is_mutating(call.args[0] if call.args else None, call.keywords):
            return func.value
        return None
    if isinstance(func, ast.Name) and func.id == "open" and call.args:
        if _write_mode_is_mutating(call.args[1] if len(call.args) > 1 else None, call.keywords):
            return call.args[0]
    return None


def _call_target_name(call: ast.Call, assigned: dict[str, str], constants: dict[str, str]) -> str | None:
    node = _write_target_node(call)
    if node is None:
        return None
    if isinstance(node, ast.Name) and node.id in assigned:
        return assigned[node.id]
    pointer_names = _pointer_names_in_resolved(node, constants, _scope_assigned_names(call))
    return sorted(pointer_names)[0] if pointer_names else None


def _assigned_computed_names(tree: ast.AST) -> dict[str, str]:
    """Locals bound to a COMPUTED pointer name, mirroring
    ``_assigned_pointer_names`` for the literal case.

    Without this the detector saw only the single-expression form. The
    two-statement form — ``target = out / f"latest.{ext}"`` then
    ``target.write_text(...)`` — is the idiom this repo actually writes, and the
    literal detector already handles its literal twin, so covering one and not
    the other left the dominant shape invisible.
    """
    names: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        computed = _computed_pointer_name_in(node.value)
        if computed is None:
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                names[target.id] = computed
    return names


def _write_mode_is_mutating(mode_node: ast.AST | None, keywords: list[ast.keyword]) -> bool:
    node = mode_node
    if node is None:
        node = next((kw.value for kw in keywords if kw.arg == "mode"), None)
    text = node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else "r"
    return any(flag in text for flag in ("w", "a", "+"))


def _computed_write_target(call: ast.Call, computed_assigned: dict[str, str]) -> str | None:
    """The computed-name counterpart of ``_call_target_name``: same write calls,
    same dispatch, but the filename is assembled rather than spelled out."""
    node = _write_target_node(call)
    if node is None:
        return None
    if isinstance(node, ast.Name):
        return computed_assigned.get(node.id)
    return _computed_pointer_name_in(node)


def _scan_text(repo_root: Path, path: Path, text: str) -> list[Finding]:
    relative = path.relative_to(repo_root)
    if relative in HELPER_FILES:
        return []
    try:
        tree = ast.parse(text, filename=str(relative))
    except SyntaxError:
        return []
    _attach_parent_links(tree)
    constants = _resolved_string_constants(tree)
    assigned = _assigned_pointer_names(tree, constants)
    computed_assigned = _assigned_computed_names(tree)
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = _call_target_name(node, assigned, constants)
        reason = "direct write to current-pointer filename; use scripts.current_pointer_writer_lib"
        if target is None:
            target = _computed_write_target(node, computed_assigned)
            if target is None:
                continue
            reason = (
                "write to a current-pointer filename BUILT at runtime; this gate cannot prove "
                "the target is not a current pointer -- use scripts.current_pointer_writer_lib, "
                "or write the literal filename so the scope is establishable"
            )
        findings.append(
            Finding(
                path=relative.as_posix(),
                line=getattr(node, "lineno", 0),
                target=target,
                reason=reason,
            )
        )
    return findings


def scan_path(repo_root: Path, path: Path) -> list[Finding]:
    relative = path.relative_to(repo_root)
    if relative in HELPER_FILES:
        return []
    text = path.read_text(encoding="utf-8")
    return _scan_text(repo_root, path, text)


def scan_repo(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _git_visible_python_files(repo_root):
        relative = path.relative_to(repo_root)
        if relative in HELPER_FILES:
            continue
        text = path.read_text(encoding="utf-8")
        if not _could_write_current_pointer(text):
            continue
        findings.extend(_scan_text(repo_root, path, text))
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
