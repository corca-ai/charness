#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

CANONICAL_MODULE = "tests/repo_copy.py"
# Files allowed to mention the patterns this guard searches for. The guard's own
# self-test file is included so it can write sample drift code into temporary
# fake repos without tripping itself.
ALLOWED_FILES = frozenset(
    {
        CANONICAL_MODULE,
        "tests/quality_gates/test_repo_copy_invariants.py",
    }
)
# Copy-heavy tests deliberately kept in the STANDING lane, keyed `path::test_name`
# so the exemption covers exactly one test's marker requirement and nothing else.
#
# Deliberately NOT `ALLOWED_FILES`: that set skips a file from ALL FOUR checks --
# inline `shutil.ignore_patterns`, `copytree(ROOT, ...)`, the marker rule, and
# direct writes to the real checkout -- and its two current members are files the
# rule cannot structurally apply to (the canonical module, and this guard's own
# self-test, which must write violating sample code into fake repos). Adding an
# ordinary test file there would silently disarm three unrelated checks over every
# test in it, permanently.
#
# The bar for an entry: the test must observe something no standing gate otherwise
# observes, and the cost of keeping it standing must be MEASURED.
#
# A MAPPING, not a set, so the measured cost is a required VALUE rather than a
# comment. A comment can be deleted with nothing red; a missing value cannot, and
# `tests/quality_gates/test_repo_copy_invariants.py` asserts each one carries a
# figure and a time unit. Membership is pinned there too, so a second entry has to
# be argued in a gate test and not only added here as one string.
STANDING_COPY_HEAVY_TESTS = {
    # `charness tool doctor`'s exit code and payload shape is a public CLI contract
    # a consumer hits on day one, and this is its only STANDING observer -- the
    # other `tool doctor` drivers in tests/charness_cli/test_tool_lifecycle.py are
    # all release_only. It sat in the release-only lane too, so a flag rename broke
    # it and nothing said so until an operator hit the same break by hand. Moving
    # the whole release lane into standing was rejected instead: that adds minutes
    # of subprocess-heavy tests, and merging the two labels is what previously made
    # the runtime budget blind to a standing regression.
    "tests/control_plane/test_integrations_validation.py"
    "::test_tool_doctor_cli_returns_nonzero_for_blocking_disposition": (
        "+1.7s on this file (2.09s -> 3.75s) against a ~44s standing pytest phase; overlaps under xdist"
    ),
}

SKIP_DIR_NAMES = {
    ".charness",
    ".git",
    ".venv",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
}

IGNORE_PATTERNS_RE = re.compile(r"\bshutil\.ignore_patterns\s*\(")
COPYTREE_ROOT_RE = re.compile(r"\bshutil\.copytree\s*\(\s*ROOT\b")
COPY_HEAVY_FIXTURES = frozenset(
    {
        "seeded_charness_repo",
        "seeded_charness_git_repo",
        "seeded_managed_home",
    }
)
COPY_HEAVY_HELPERS = frozenset(
    {
        "clone_seeded_charness_repo",
        "clone_seeded_managed_home",
    }
)
COPY_HEAVY_TOKEN_RE = re.compile(
    r"\b("
    + "|".join(
        re.escape(name)
        for name in sorted(COPY_HEAVY_FIXTURES | COPY_HEAVY_HELPERS)
    )
    + r")\b"
)
REPO_ROOT_NAMES = frozenset({"ROOT", "REPO_ROOT", "_ROOT", "_REPO_ROOT", "PLUGIN_ROOT"})
PATH_WRITE_METHODS = frozenset(
    {
        "chmod",
        "mkdir",
        "rename",
        "replace",
        "rmdir",
        "symlink_to",
        "touch",
        "unlink",
        "write_bytes",
        "write_text",
    }
)
# floor-addition-restraint: merge a reproduced xdist shared-worktree escape
# into the existing test-isolation gate; this is a finite direct-Path ratchet,
# not a claim to sandbox arbitrary Python, libraries, or subprocesses.


def _name_parts(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, ast.Attribute):
        return [*_name_parts(node.value), node.attr]
    if isinstance(node, ast.Call):
        return _name_parts(node.func)
    return []


def _is_release_only_marker(node: ast.AST) -> bool:
    parts = _name_parts(node)
    return len(parts) >= 3 and parts[-3:] == ["pytest", "mark", "release_only"]


def _module_is_release_only(tree: ast.Module) -> bool:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "pytestmark" for target in node.targets):
            continue
        if _is_release_only_marker(node.value):
            return True
        if isinstance(node.value, (ast.List, ast.Tuple)):
            if any(_is_release_only_marker(item) for item in node.value.elts):
                return True
    return False


def _function_is_release_only(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(_is_release_only_marker(decorator) for decorator in node.decorator_list)


def _copy_heavy_reason(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    local_fixtures: frozenset[str] = frozenset(),
    local_helpers: frozenset[str] = frozenset(),
) -> str | None:
    fixture_hits = sorted(
        arg.arg
        for arg in node.args.args
        if arg.arg in COPY_HEAVY_FIXTURES or arg.arg in local_fixtures
    )
    helper_hits: set[str] = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        parts = _name_parts(child.func)
        if parts and (parts[-1] in COPY_HEAVY_HELPERS or parts[-1] in local_helpers):
            helper_hits.add(parts[-1])
    reasons: list[str] = []
    if fixture_hits:
        reasons.append(f"copy-heavy fixture(s): {', '.join(fixture_hits)}")
    if helper_hits:
        reasons.append(f"copy-heavy helper(s): {', '.join(sorted(helper_hits))}")
    return "; ".join(reasons) if reasons else None


def _module_local_copy_heavy(tree: ast.Module) -> tuple[frozenset[str], frozenset[str]]:
    """Module-local functions that REACH a copy-heavy source, to any depth.

    The enumerated form of this check saw only the names in `COPY_HEAVY_FIXTURES` and
    `COPY_HEAVY_HELPERS`, and only when they appeared inside a `test_` function. One hop
    defeated it: `tests/quality_gates/test_gate_summary_names_failures.py` wrapped
    `clone_seeded_charness_repo` in a module-local `gate_repo` fixture, so no test named a
    listed identifier and no listed call sat in a test body. It was the most expensive
    copy-heavy test in the standing lane -- 7.3s of SETUP per test, five tests -- and this
    gate, which exists for exactly that, reported clean over it.

    So the question is not "does this test mention a known name" but "can this test reach
    a copy-heavy source". Fixed point over module-local functions, because a wrapper can
    wrap a wrapper.
    """

    functions = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    reached: set[str] = set()
    changed = True
    while changed:
        changed = False
        for name, node in functions.items():
            if name in reached or name.startswith("test_"):
                continue
            frozen = frozenset(reached)
            if _copy_heavy_reason(node, local_fixtures=frozen, local_helpers=frozen) is not None:
                reached.add(name)
                changed = True
    # A module-local function is reachable from a test BOTH ways: as a fixture parameter
    # (pytest resolves it by name) and as a direct call. Neither form is more honest than
    # the other, so both carry the same verdict.
    return frozenset(reached), frozenset(reached)


def _copy_heavy_marker_violations(source: str, rel_path: Path) -> list[str]:
    try:
        tree = ast.parse(source, filename=rel_path.as_posix())
    except SyntaxError:
        return []
    if _module_is_release_only(tree):
        return []
    local_fixtures, local_helpers = _module_local_copy_heavy(tree)
    violations: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue
        reason = _copy_heavy_reason(
            node, local_fixtures=local_fixtures, local_helpers=local_helpers
        )
        if reason is None or _function_is_release_only(node):
            continue
        if f"{rel_path.as_posix()}::{node.name}" in STANDING_COPY_HEAVY_TESTS:
            continue
        violations.append(
            f"{rel_path.as_posix()}::{node.name}: uses {reason}. "
            "Copy-heavy repo/home/plugin tests must be marked `pytest.mark.release_only` "
            "so standing pre-push excludes full-copy lifecycle proof. The only alternative is a "
            "`path::test_name` entry in `STANDING_COPY_HEAVY_TESTS` in "
            "scripts/check_test_repo_copy_invariants.py, whose bar is BOTH halves: the test "
            "observes something no standing gate otherwise observes, AND its cost as a standing "
            "test is measured and recorded as the entry's value."
        )
    return violations


def _expr_uses_repo_path(node: ast.AST, tainted_names: set[str]) -> bool:
    if isinstance(node, ast.Name):
        return node.id in tainted_names
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        return _expr_uses_repo_path(node.left, tainted_names)
    if isinstance(node, ast.Attribute):
        return _expr_uses_repo_path(node.value, tainted_names)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr in {"absolute", "joinpath", "resolve"}:
            return _expr_uses_repo_path(node.func.value, tainted_names)
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Path"
        and node.args
    ):
        return _expr_uses_repo_path(node.args[0], tainted_names)
    return False


def _references_dunder_file(node: ast.AST) -> bool:
    return any(isinstance(child, ast.Name) and child.id == "__file__" for child in ast.walk(node))


def _module_repo_path_names(tree: ast.Module) -> set[str]:
    tainted: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            tainted.update(
                target.id
                for target in targets
                if (
                    isinstance(target, ast.Name)
                    and target.id in REPO_ROOT_NAMES
                    and node.value is not None
                    and _references_dunder_file(node.value)
                )
            )
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            tainted.update(
                alias.asname or alias.name
                for alias in node.names
                if alias.name in REPO_ROOT_NAMES
            )
    changed = True
    while changed:
        changed = False
        for node in tree.body:
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            value = node.value
            if value is None or not _expr_uses_repo_path(value, tainted):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and target.id not in tainted:
                    tainted.add(target.id)
                    changed = True
    return tainted


class _RepoWriteVisitor(ast.NodeVisitor):
    def __init__(self, module_tainted_names: set[str]) -> None:
        self.tainted_names = set(module_tainted_names)
        self.violations: list[tuple[int, str]] = []

    def visit_Assign(self, node: ast.Assign) -> None:
        if _expr_uses_repo_path(node.value, self.tainted_names):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.tainted_names.add(target.id)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if (
            node.value is not None
            and isinstance(node.target, ast.Name)
            and _expr_uses_repo_path(node.value, self.tainted_names)
        ):
            self.tainted_names.add(node.target.id)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute):
            method = node.func.attr
            if method in PATH_WRITE_METHODS and _expr_uses_repo_path(
                node.func.value, self.tainted_names
            ):
                self.violations.append((node.lineno, method))
            elif method == "open" and _expr_uses_repo_path(
                node.func.value, self.tainted_names
            ):
                mode = self._open_mode(node)
                if any(flag in mode for flag in "wax+"):
                    self.violations.append((node.lineno, f"Path.open(mode={mode!r})"))
        elif isinstance(node.func, ast.Name) and node.func.id == "open" and node.args:
            mode = self._open_mode(node)
            if any(flag in mode for flag in "wax+") and _expr_uses_repo_path(
                node.args[0], self.tainted_names
            ):
                self.violations.append((node.lineno, f"open(mode={mode!r})"))
        self.generic_visit(node)

    @staticmethod
    def _open_mode(node: ast.Call) -> str:
        mode = "r"
        if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
            mode = str(node.args[1].value)
        for keyword in node.keywords:
            if keyword.arg == "mode" and isinstance(keyword.value, ast.Constant):
                mode = str(keyword.value.value)
        return mode


def _function_scopes(body: list[ast.stmt]) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    scopes: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scopes.append(node)
        elif isinstance(node, ast.ClassDef):
            scopes.extend(_function_scopes(node.body))
    return scopes


def _shared_repo_write_violations(source: str, rel_path: Path) -> list[str]:
    try:
        tree = ast.parse(source, filename=rel_path.as_posix())
    except SyntaxError:
        return []
    module_tainted_names = _module_repo_path_names(tree)
    violations: list[str] = []
    module_visitor = _RepoWriteVisitor(module_tainted_names)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    module_visitor.visit(child)
        elif not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            module_visitor.visit(node)
    for line, operation in module_visitor.violations:
        violations.append(
            f"{rel_path.as_posix()}:{line}: module import mutates a path derived from the "
            f"real repository root via `{operation}`. Use tmp_path or an isolated repo."
        )
    for node in _function_scopes(tree.body):
        visitor = _RepoWriteVisitor(module_tainted_names)
        visitor.visit(node)
        for line, operation in visitor.violations:
            violations.append(
                f"{rel_path.as_posix()}:{line}: `{node.name}` mutates a path derived from the "
                f"real repository root via `{operation}`. Use tmp_path or an isolated repo so "
                "xdist workers and snapshot-based tests cannot observe transient worktree state."
            )
    return violations


def _iter_python_files(tests_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in tests_root.rglob("*.py"):
        rel_path = path.relative_to(tests_root.parent)
        if any(part in SKIP_DIR_NAMES for part in rel_path.parts):
            continue
        files.append(rel_path)
    return sorted(files)


def find_violations(repo_root: Path) -> list[str]:
    tests_root = repo_root / "tests"
    if not tests_root.is_dir():
        return []
    violations: list[str] = []
    for rel_path in _iter_python_files(tests_root):
        if rel_path.as_posix() in ALLOWED_FILES:
            continue
        text = (repo_root / rel_path).read_text(encoding="utf-8")
        if IGNORE_PATTERNS_RE.search(text):
            violations.append(
                f"{rel_path.as_posix()}: defines shutil.ignore_patterns(...). "
                f"Use REPO_COPY_IGNORE from {CANONICAL_MODULE} instead so the ignore set stays a single source of truth."
            )
        if COPYTREE_ROOT_RE.search(text):
            violations.append(
                f"{rel_path.as_posix()}: calls shutil.copytree(ROOT, ...) inline. "
                f"Use clone_seeded_charness_repo(...) with seeded_charness_repo or seeded_charness_git_repo "
                f"from {CANONICAL_MODULE} so fixtures share a session-scoped seed."
            )
        if COPY_HEAVY_TOKEN_RE.search(text):
            violations.extend(_copy_heavy_marker_violations(text, rel_path))
        violations.extend(_shared_repo_write_violations(text, rel_path))
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Enforce isolated test repositories: keep repo-copy policy centralized, keep copy-heavy "
            "tests out of standing pytest, and reject direct pathlib writes derived from the real "
            "checkout root."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    tests_root = repo_root / "tests"
    if not tests_root.is_dir() or not _iter_python_files(tests_root):
        # `find_violations` returns [] for a missing/empty tests tree, and
        # --repo-root defaults to the cwd, so a wrong cwd used to certify PASS
        # over zero files. Scanning nothing is an unestablished scope, not a
        # clean one (charness-artifacts/critique/2026-07-27-empty-scope-family.md).
        print(
            f"no test Python files found under {tests_root}; nothing was scanned. "
            "Check --repo-root (it defaults to the current directory).",
            file=sys.stderr,
        )
        return 1
    violations = find_violations(repo_root)
    if not violations:
        return 0

    print(
        "Test isolation drift: repo-copy policy must stay centralized and tests must not mutate the real checkout.",
        file=sys.stderr,
    )
    for violation in violations:
        print(f"- {violation}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
