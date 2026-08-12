from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

NESTED_CLI_RE = re.compile(
    r"\b(subprocess\.(?:run|check_call|check_output|Popen)|spawnSync|execFileSync|execSync|spawn\(|execa\()"
)
_PYTHON_SUBPROCESS_CALLS = {"run", "check_call", "check_output", "Popen"}
_JS_SYNC_CALLS = {"spawnSync", "execFileSync", "execSync"}
_JS_CALL_RE = re.compile(r"\b(spawnSync|execFileSync|execSync|spawn|execa)\s*\(")


def nested_cli_files(repo_root: Path, test_files: list[Path]) -> list[str]:
    matches: list[str] = []
    for path in test_files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if NESTED_CLI_RE.search(text):
            matches.append(path.relative_to(repo_root).as_posix())
    return matches


def _call_parts(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, ast.Attribute):
        return [*_call_parts(node.value), node.attr]
    return []


def _literal_truth(node: ast.AST | None) -> bool | None:
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value
    return None


def _literal_deadline_state(node: ast.AST | None) -> str:
    if node is None or (isinstance(node, ast.Constant) and node.value is None):
        return "absent"
    if (
        isinstance(node, ast.Constant)
        and isinstance(node.value, (int, float))
        and not isinstance(node.value, bool)
    ):
        return "present"
    return "unknown"


def _python_output_bounding(keywords: dict[str, ast.AST]) -> str:
    values = [keywords.get(name) for name in ("stdout", "stderr")]
    rendered = [ast.unparse(value) for value in values if value is not None]
    if _literal_truth(keywords.get("capture_output")) is True or any("PIPE" in value for value in rendered):
        return "unbounded"
    if len(rendered) == 2 and all("DEVNULL" in value for value in rendered):
        return "bounded"
    return "unknown"


def _python_settlement_seams(repo_root: Path, path: Path, text: str) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return []
    seams: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        parts = _call_parts(node.func)
        if len(parts) != 2 or parts[0] != "subprocess" or parts[1] not in _PYTHON_SUBPROCESS_CALLS:
            continue
        keywords = {keyword.arg: keyword.value for keyword in node.keywords if keyword.arg is not None}
        deadline = _literal_deadline_state(keywords.get("timeout"))
        seams.append(
            {
                "path": path.relative_to(repo_root).as_posix(),
                "line": node.lineno,
                "call": ".".join(parts),
                "deadline": deadline,
                # A synchronous helper only waits; without a deadline it can wait forever.
                "lifecycle": "finite"
                if parts[1] != "Popen" and deadline == "present"
                else "unknown",
                # Process-group creation alone is not termination ownership; only a runtime protocol can prove it.
                "process_tree_termination": "unknown",
                "output_bounding": _python_output_bounding(keywords),
            }
        )
    return seams


def _js_settlement_seams(repo_root: Path, path: Path, text: str) -> list[dict[str, Any]]:
    seams: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in _JS_CALL_RE.finditer(line):
            call = match.group(1)
            timeout_match = re.search(r"\btimeout\s*:\s*([^,}\s]+)", line)
            timeout_value = timeout_match.group(1) if timeout_match else None
            deadline = (
                "absent"
                if timeout_value is None
                else "present"
                if re.fullmatch(r"\d+(?:\.\d+)?", timeout_value)
                else "unknown"
            )
            if re.search(r"\bstdio\s*:\s*['\"]ignore['\"]", line):
                output_bounding = "bounded"
            elif re.search(r"\bstdio\s*:\s*['\"]pipe['\"]", line):
                output_bounding = "unbounded"
            else:
                output_bounding = "unknown"
            seams.append(
                {
                    "path": path.relative_to(repo_root).as_posix(),
                    "line": line_number,
                    "call": call,
                    "deadline": deadline,
                    "lifecycle": "finite"
                    if call in _JS_SYNC_CALLS and deadline == "present"
                    else "unknown",
                    "process_tree_termination": "unknown",
                    "output_bounding": output_bounding,
                }
            )
    return seams


def subprocess_settlement_seams(repo_root: Path, test_files: list[Path]) -> list[dict[str, Any]]:
    """Return conservative static settlement signals for nested subprocess call sites.

    The fields describe visible syntax only; ``unknown`` is intentional when
    process lifecycle or tree ownership needs runtime evidence.
    """
    seams: list[dict[str, Any]] = []
    for path in test_files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if path.suffix == ".py":
            seams.extend(_python_settlement_seams(repo_root, path, text))
        elif path.suffix in {".js", ".mjs", ".cjs", ".ts", ".tsx"}:
            seams.extend(_js_settlement_seams(repo_root, path, text))
    return sorted(
        seams,
        key=lambda item: (str(item["path"]), int(item["line"]), str(item["call"])),
    )


def _name_parts(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, ast.Attribute):
        return [*_name_parts(node.value), node.attr]
    if isinstance(node, ast.Call):
        return _name_parts(node.func)
    return []


def _pytest_aliases(tree: ast.Module) -> tuple[set[str], set[str]]:
    pytest_aliases = {"pytest"}
    mark_aliases: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "pytest":
                    pytest_aliases.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module == "pytest":
            for alias in node.names:
                if alias.name == "mark":
                    mark_aliases.add(alias.asname or alias.name)
    return pytest_aliases, mark_aliases


def _is_release_only_marker(node: ast.AST, pytest_aliases: set[str], mark_aliases: set[str]) -> bool:
    parts = _name_parts(node)
    return (
        (len(parts) >= 3 and parts[-3] in pytest_aliases and parts[-2:] == ["mark", "release_only"])
        or (len(parts) >= 2 and parts[-2] in mark_aliases and parts[-1] == "release_only")
    )


def _module_release_only(tree: ast.Module) -> bool:
    pytest_aliases, mark_aliases = _pytest_aliases(tree)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if "pytestmark" not in targets:
            continue
        if _is_release_only_marker(node.value, pytest_aliases, mark_aliases):
            return True
        if isinstance(node.value, (ast.List, ast.Tuple)):
            if any(_is_release_only_marker(item, pytest_aliases, mark_aliases) for item in node.value.elts):
                return True
    return False


def _class_release_only(node: ast.ClassDef, pytest_aliases: set[str], mark_aliases: set[str]) -> bool:
    if any(_is_release_only_marker(decorator, pytest_aliases, mark_aliases) for decorator in node.decorator_list):
        return True
    for item in node.body:
        if not isinstance(item, ast.Assign):
            continue
        targets = [target.id for target in item.targets if isinstance(target, ast.Name)]
        if "pytestmark" in targets and _is_release_only_marker(item.value, pytest_aliases, mark_aliases):
            return True
        if "pytestmark" in targets and isinstance(item.value, (ast.List, ast.Tuple)):
            if any(_is_release_only_marker(marker, pytest_aliases, mark_aliases) for marker in item.value.elts):
                return True
    return False


def _function_release_only(
    node: ast.FunctionDef | ast.AsyncFunctionDef, pytest_aliases: set[str], mark_aliases: set[str]
) -> bool:
    return any(_is_release_only_marker(decorator, pytest_aliases, mark_aliases) for decorator in node.decorator_list)


def _iter_tests(tree: ast.Module) -> list[tuple[str, bool]]:
    pytest_aliases, mark_aliases = _pytest_aliases(tree)
    module_release_only = _module_release_only(tree)
    tests: list[tuple[str, bool]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            tests.append((node.name, module_release_only or _function_release_only(node, pytest_aliases, mark_aliases)))
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            class_release_only = module_release_only or _class_release_only(node, pytest_aliases, mark_aliases)
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith("test_"):
                    tests.append(
                        (
                            f"{node.name}.{item.name}",
                            class_release_only or _function_release_only(item, pytest_aliases, mark_aliases),
                        )
                    )
    return tests


def pytest_file_test_counts(repo_root: Path, rel_paths: list[str]) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for rel_path in rel_paths:
        try:
            text = (repo_root / rel_path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            tree = ast.parse(text, filename=rel_path)
        except SyntaxError:
            continue
        tests = _iter_tests(tree)
        release_only_count = sum(1 for _, marked in tests if marked)
        files.append(
            {
                "path": rel_path,
                "test_count": len(tests),
                "release_only_count": release_only_count,
                "standing_count": len(tests) - release_only_count,
            }
        )
    return files


def module_release_only_files(repo_root: Path, rel_paths: list[str]) -> list[str]:
    matches: list[str] = []
    for rel_path in rel_paths:
        try:
            text = (repo_root / rel_path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            tree = ast.parse(text, filename=rel_path)
        except SyntaxError:
            continue
        if _module_release_only(tree):
            matches.append(rel_path)
    return matches
