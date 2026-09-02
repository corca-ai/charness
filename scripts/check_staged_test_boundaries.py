#!/usr/bin/env python3
"""Low-cost, non-blocking advisory for new staged test process boundaries.

The full ``check_boundary_bypass_ratchet.py`` remains the exact whole-tree
no-increase layer. This hook-side probe answers a smaller question: did a staged
Python test add or edit a direct process call or a Git repository-construction
call, and did the call receive a structured boundary reason?

The staged diff is read once and all staged test blobs are read through one
``git cat-file --batch`` request. The probe deliberately does not follow helper
indirection, dynamic commands, or fixture functions. That creates false
negatives, while ordinary wrappers and legitimate protocol/exit-code tests can
create false positives. A non-empty ``pytest.mark.boundary_contract`` reason
declares intent but is not proof and can be abused to silence this advisory;
the full ratchet remains the stronger independent guard. Findings never block a
commit, including when Git or AST parsing is unavailable.
"""

from __future__ import annotations

import argparse
import ast
import re
import shlex
import sys
import tempfile
from pathlib import Path
from typing import Iterable

from runtime_bootstrap import import_repo_module
from yaml_output import emit_yaml

_subprocess_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_process = _subprocess_guard.run_process

SCHEMA_VERSION = "charness.quality.staged_test_boundary_advisory.v1"
BOUNDARY_MARKER = "boundary_contract"
_HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
_SUBPROCESS_ATTRS = frozenset({"run", "call", "check_call", "check_output", "Popen"})
_OS_ATTRS = frozenset({"system", "popen", "fork", "posix_spawn", "posix_spawnp"})
_GIT_OPERATIONS = frozenset({"init", "clone", "worktree", "submodule"})
_PROCESS_HELPER_NAMES = frozenset({"run_script", "run_at", "run_cli", "_run_cli"})
_GIT_HELPER_NAMES = frozenset(
    {"git", "_git", "run_git", "_run_git", "git_run", "git_cmd", "git_command"}
)


def _is_test_path(path: str) -> bool:
    candidate = Path(path)
    return (
        len(candidate.parts) >= 2
        and candidate.parts[0] == "tests"
        and candidate.suffix == ".py"
        and (candidate.name.startswith("test_") or candidate.name.endswith("_test.py"))
    )


def _staged_diff(repo_root: Path) -> bytes:
    result = run_process(
        [
            "git",
            "diff",
            "--cached",
            "--unified=0",
            "--no-color",
            "--no-ext-diff",
            "--diff-filter=ACMR",
            "--",
            "tests",
        ],
        cwd=repo_root,
        timeout_seconds=None,
    )
    if result.returncode != 0:
        detail = result.stderr.strip()
        raise RuntimeError(f"git diff --cached failed: {detail or result.returncode}")
    return result.stdout.encode("utf-8")


def _changed_ranges(diff: bytes) -> dict[str, list[tuple[int, int]]]:
    ranges: dict[str, list[tuple[int, int]]] = {}
    current: str | None = None
    for line in diff.decode("utf-8", errors="surrogateescape").splitlines():
        if line.startswith("+++ "):
            path = line[4:]
            current = None if path == "/dev/null" else path.removeprefix("b/")
            continue
        match = _HUNK_RE.match(line)
        if match is None or current is None:
            continue
        start = int(match.group(1))
        count = int(match.group(2) or "1")
        if count:
            ranges.setdefault(current, []).append((start, start + count - 1))
    return {path: spans for path, spans in ranges.items() if _is_test_path(path)}


def _staged_blobs(repo_root: Path, paths: Iterable[str]) -> dict[str, bytes]:
    selected = list(paths)
    if not selected:
        return {}
    request = b"".join(f":{path}\n".encode("utf-8", errors="surrogateescape") for path in selected)
    with tempfile.NamedTemporaryFile() as input_file:
        input_file.write(request)
        input_file.flush()
        result = run_process(
            f"git cat-file --batch < {shlex.quote(input_file.name)}",
            cwd=repo_root,
            shell=True,
            timeout_seconds=None,
        )
    if result.returncode != 0:
        detail = result.stderr.strip()
        raise RuntimeError(f"git cat-file --batch failed: {detail or result.returncode}")
    output = result.stdout.encode("utf-8")
    blobs: dict[str, bytes] = {}
    cursor = 0
    for path in selected:
        header_end = output.find(b"\n", cursor)
        if header_end < 0:
            raise RuntimeError("git cat-file --batch returned a truncated header")
        header = output[cursor:header_end].decode("utf-8", errors="replace").split()
        cursor = header_end + 1
        if len(header) >= 3 and header[1] == "blob":
            size = int(header[2])
            end = cursor + size
            blobs[path] = output[cursor:end]
            cursor = end
            if output[cursor : cursor + 1] == b"\n":
                cursor += 1
    return blobs


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _literal_strings(node: ast.AST) -> list[str]:
    return [
        child.value
        for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    ]


def _record_module_import(
    node: ast.Import,
    subprocess_modules: set[str],
    os_modules: set[str],
    multiprocessing_modules: set[str],
) -> None:
    for alias in node.names:
        bound = alias.asname or alias.name
        if alias.name == "subprocess":
            subprocess_modules.add(bound)
        elif alias.name == "os":
            os_modules.add(bound)
        elif alias.name in {"multiprocessing", "concurrent.futures"}:
            multiprocessing_modules.add(alias.asname or alias.name.split(".")[-1])


def _record_from_import(node: ast.ImportFrom, direct_process_names: set[str]) -> None:
    module = node.module or ""
    if module in {"subprocess", "asyncio"}:
        for alias in node.names:
            if alias.name in _SUBPROCESS_ATTRS or alias.name.startswith("create_subprocess_"):
                direct_process_names.add(alias.asname or alias.name)
    elif module == "os":
        for alias in node.names:
            if alias.name in _OS_ATTRS or alias.name.startswith("spawn"):
                direct_process_names.add(alias.asname or alias.name)
    elif module == "multiprocessing":
        for alias in node.names:
            if alias.name == "Process":
                direct_process_names.add(alias.asname or alias.name)


def _imports(tree: ast.AST) -> tuple[set[str], set[str], set[str], set[str]]:
    subprocess_modules = {"subprocess"}
    os_modules = {"os"}
    multiprocessing_modules = {"multiprocessing"}
    direct_process_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            _record_module_import(node, subprocess_modules, os_modules, multiprocessing_modules)
        elif isinstance(node, ast.ImportFrom):
            _record_from_import(node, direct_process_names)
    return subprocess_modules, os_modules, multiprocessing_modules, direct_process_names


def _process_kind(name: str, aliases: tuple[set[str], set[str], set[str], set[str]]) -> str | None:
    subprocess_modules, os_modules, multiprocessing_modules, direct_names = aliases
    if name in direct_names:
        return "direct-process-spawn"
    parts = name.split(".")
    if parts[-1] in _PROCESS_HELPER_NAMES:
        return "process-helper-boundary"
    if len(parts) < 2:
        return None
    root, attr = parts[0], parts[-1]
    if root in subprocess_modules and attr in _SUBPROCESS_ATTRS:
        return "direct-process-spawn"
    if root in os_modules and (attr in _OS_ATTRS or attr.startswith("spawn")):
        return "direct-process-spawn"
    if root in multiprocessing_modules and attr in {"Process", "ProcessPoolExecutor"}:
        return "direct-process-spawn"
    if (
        name.endswith(".ProcessPoolExecutor")
        or name.endswith(".create_subprocess_exec")
        or name.endswith(".create_subprocess_shell")
    ):
        return "direct-process-spawn"
    return None


def _command_strings(node: ast.Call) -> list[str]:
    if node.args:
        return _literal_strings(node.args[0])
    for keyword in node.keywords:
        if keyword.arg in {"args", "cmd", "command"}:
            return _literal_strings(keyword.value)
    return []


def _git_operations(node: ast.Call, process_kind: str | None) -> list[str]:
    strings = _command_strings(node) if process_kind else _literal_strings(node)
    if process_kind:
        first = strings[0].strip() if strings else ""
        is_git = first == "git" or first.endswith("/git") or re.match(r"^git\s+", first)
        if not is_git:
            return []
        if first != "git" and not first.endswith("/git"):
            strings = re.split(r"\s+", first) + strings[1:]
    else:
        name = _call_name(node.func).rsplit(".", 1)[-1].lower()
        if name not in _GIT_HELPER_NAMES and not name.endswith("_git"):
            return []
    return sorted({value for value in strings if value in _GIT_OPERATIONS})


def _marker(node: ast.AST) -> tuple[bool, str | None]:
    name = _call_name(node.func) if isinstance(node, ast.Call) else _call_name(node)
    marker_name = f"pytest.mark.{BOUNDARY_MARKER}"
    if name != marker_name:
        return False, None
    if isinstance(node, ast.Call):
        positional = [
            arg.value
            for arg in node.args
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
        ]
        keyword = next(
            (
                item.value.value
                for item in node.keywords
                if item.arg == "reason"
                and isinstance(item.value, ast.Constant)
                and isinstance(item.value.value, str)
            ),
            None,
        )
        reason = keyword if isinstance(keyword, str) else positional[0] if positional else None
        return True, reason.strip() if isinstance(reason, str) and reason.strip() else None
    return True, None


def _scope_markers(
    node: ast.AST, parents: dict[ast.AST, ast.AST], module_reasons: list[str], module_seen: bool
) -> tuple[bool, list[str]]:
    seen = module_seen
    reasons = list(module_reasons)
    current: ast.AST | None = node
    while current is not None:
        decorators = getattr(current, "decorator_list", [])
        for decorator in decorators:
            found, reason = _marker(decorator)
            seen = seen or found
            if reason and reason not in reasons:
                reasons.append(reason)
        current = parents.get(current)
    return seen, reasons


def _analyze_source(path: str, source: bytes, changed: list[tuple[int, int]]) -> dict[str, object]:
    try:
        tree = ast.parse(source.decode("utf-8"))
    except (SyntaxError, UnicodeDecodeError, ValueError) as exc:
        return {"test_file": path, "status": "unparseable", "detail": str(exc)}
    parents: dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent
    module_reasons: list[str] = []
    module_seen = False
    for statement in tree.body:
        if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
            continue
        targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
        if not any(
            isinstance(target, ast.Name) and target.id == "pytestmark" for target in targets
        ):
            continue
        for candidate in ast.walk(statement.value):
            found, reason = _marker(candidate)
            module_seen = module_seen or found
            if reason and reason not in module_reasons:
                module_reasons.append(reason)
    aliases = _imports(tree)
    findings: list[dict[str, object]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not any(
            getattr(node, "lineno", 0) <= end and getattr(node, "end_lineno", node.lineno) >= start
            for start, end in changed
        ):
            continue
        process_kind = _process_kind(_call_name(node.func), aliases)
        operations = _git_operations(node, process_kind)
        kinds = ([process_kind] if process_kind else []) + (
            ["git-repository-construction"] if operations else []
        )
        if not kinds:
            continue
        seen, reasons = _scope_markers(node, parents, module_reasons, module_seen)
        findings.append(
            {
                "line": node.lineno,
                "callee": _call_name(node.func),
                "kinds": kinds,
                "git_operations": operations,
                "declared": bool(reasons),
                "marker_seen": seen,
                "reasons": reasons,
            }
        )
    return {"test_file": path, "status": "analyzed", "findings": findings}


def scan_staged_tests(repo_root: Path) -> dict[str, object]:
    ranges = _changed_ranges(_staged_diff(repo_root))
    blobs = _staged_blobs(repo_root, sorted(ranges))
    files = [_analyze_source(path, blobs[path], ranges[path]) for path in sorted(blobs)]
    findings = [
        {**finding, "test_file": report["test_file"]}
        for report in files
        for finding in report.get("findings", [])
    ]
    undeclared = [finding for finding in findings if not finding["declared"]]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "advisory" if files else "no-staged-tests",
        "staged_test_files": len(files),
        "changed_call_count": len(findings),
        "undeclared_call_count": len(undeclared),
        "findings": findings,
        "unparseable_files": [report for report in files if report["status"] == "unparseable"],
        "warnings": [
            "Each undeclared finding is advisory only; add a non-empty reason to @pytest.mark.boundary_contract(reason=...) when the boundary is intentional."
        ]
        if undeclared
        else [],
        "notes": [
            "The full boundary-bypass ratchet remains the exact whole-tree no-increase layer; this staged probe does not replace or weaken it.",
            "False positives: legitimate protocol/exit-code tests and wrappers may still need a marker; marker reasons declare intent but are not proof and can be abused.",
            "False negatives: dynamic commands, aliases not statically visible, helper indirection, fixture builders, unparseable files, and calls outside added/modified hunk lines are deliberately not inferred.",
            "Git cost: one batched staged diff query plus one git cat-file --batch query, never one Git process per test file.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Advisory only: inspect added/modified AST calls in staged Python tests for direct "
            "process spawns or Git init/clone/worktree/submodule construction. "
            "A non-empty pytest.mark.boundary_contract(reason=...) declares intentional boundaries; "
            "findings and Git/AST failures never block the commit."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = scan_staged_tests(args.repo_root.resolve())
    except Exception as exc:  # advisory must not replace a real commit gate
        payload = {
            "schemaVersion": SCHEMA_VERSION,
            "status": "unavailable",
            "staged_test_files": 0,
            "changed_call_count": 0,
            "undeclared_call_count": 0,
            "findings": [],
            "warnings": [f"staged boundary advisory unavailable: {exc}"],
            "notes": [
                "The advisory degraded to silence; the full boundary-bypass ratchet remains authoritative."
            ],
        }
    emit_yaml(payload)
    if payload["warnings"]:
        print(
            f"ADVISORY: staged test boundary review found {payload['undeclared_call_count']} undeclared call(s); commit was not blocked.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
