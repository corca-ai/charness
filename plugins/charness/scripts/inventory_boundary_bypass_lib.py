"""Boundary-bypass testability inventory (repo-owned, stack-specific probe).

A *boundary-bypass* test reaches an import-safe entrypoint through a process
boundary (spawns ``python3 scripts/X.py`` and inspects exit code / stdout)
when the same logic is reachable in-process (``import X; X.main()`` or a
``X_lib`` function). Per ``skills/public/quality/references/testability-and-selection.md``
that is a candidate testability smell: a delivery-boundary test compensating
for behavior reachable through a smaller, statically-visible surface.

This module owns ONLY the Python + charness-layout detection. The portable
policy (advisory vs no-increase ratchet, exemptions) lives in the ``quality``
skill; a non-Python repo ships its own probe with the same payload shape.

Detection is a deliberately cheap heuristic: a test file that contains any
spawn token is scanned for in-repo script-path literals. It over-reports
rather than under-reports (advisory), and ``likely_keep_boundary`` marks
exit-code/stderr-contract tests that may legitimately stay at the boundary.

Relation: this refines the already-portable spawn-smell that
``skills/public/quality/scripts/standing_test_economics_lib.py`` detects
multi-language (``nested_cli_fanout``). The genuine stack-specific delta added
here is ``is_import_safe`` + in-repo target resolution — deciding which spawns
are in-process-convertible. See ``docs/testability-dsl-initiative.md``.
"""

from __future__ import annotations

import ast
import re
from collections.abc import Iterator
from pathlib import Path

# The payload contract (schema + fields) is conceptually quality-skill-owned — the
# portable policy/ratchet consumes it; this scripts/ probe is one stack-specific
# Python+charness-layout emitter. A non-Python repo emits the same shape from its own probe.
SCHEMA_VERSION = "charness.quality.boundary_bypass_inventory.v1"

# Delivery-boundary spawn tokens, multi-language (mirrors the set already used
# by standing_test_economics_lib). Presence gates whether a test file is scanned.
_SPAWN_RE = re.compile(
    r"\b(run_script|run_at|subprocess\.(?:run|check_call|check_output|Popen)"
    r"|spawnSync|execFileSync|execSync|spawn|execa)\s*\("
)
# In-repo script entrypoints the test targets. This literal shape is the
# charness-layout-specific part and is intentionally confined to this probe.
_TARGET_RE = re.compile(r"""['"]((?:scripts|skills)/[A-Za-z0-9_./-]+\.py)['"]""")
_BEHAVIOR_RE = re.compile(r"json\.loads\([^\n]*stdout|\.file_json\(|\.file_text\(")
_EXIT_RE = re.compile(r"returncode\s*[!=]=\s*[0-9]")
_GIT_RE = re.compile(r"""['"]git['"]|(?:^|[^\w-])git\s+(?:[A-Za-z-])""")
_IGNORE_DIRS = {"mutants", "__pycache__", ".git", "node_modules"}
_SPAWN_FUNC_NAMES = {"run_script", "run_at", "spawnSync", "execFileSync", "execSync", "spawn", "execa"}
_SUBPROCESS_ATTRS = {"run", "check_call", "check_output", "Popen"}


def _iter_test_files(repo_root: Path) -> Iterator[Path]:
    tests_dir = repo_root / "tests"
    if not tests_dir.is_dir():
        return
    for path in sorted(tests_dir.rglob("test_*.py")):
        parts = path.relative_to(repo_root).parts
        if any(part in _IGNORE_DIRS for part in parts):
            continue
        yield path


def _spawn_targets(text: str) -> list[str]:
    if not _SPAWN_RE.search(text):
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return sorted(set(_TARGET_RE.findall(text)))
    targets: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not _is_spawn_call(node):
            continue
        for child in list(node.args) + [kw.value for kw in node.keywords]:
            for value in _iter_string_constants(child):
                targets.update(_TARGET_RE.findall(repr(value)))
    return sorted(targets)


def _is_spawn_call(node: ast.Call) -> bool:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id in _SPAWN_FUNC_NAMES
    if isinstance(func, ast.Attribute):
        if func.attr in _SPAWN_FUNC_NAMES:
            return True
        return (
            isinstance(func.value, ast.Name)
            and func.value.id == "subprocess"
            and func.attr in _SUBPROCESS_ATTRS
        )
    return False


def _iter_string_constants(node: ast.AST) -> Iterator[str]:
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            yield child.value


def is_import_safe(path: Path) -> bool:
    """A script is import-safe when its logic is reachable via ``main()`` under a
    ``__main__`` guard, so a test could call it in-process instead of spawning it."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return "def main(" in text and "__name__" in text and "__main__" in text


def _has_lib(path: Path) -> bool:
    return path.with_name(path.stem + "_lib.py").is_file()


def has_internal_boundary(path: Path) -> bool:
    """Whether an import-safe target still shells out inside the reachable logic."""
    paths = [path]
    lib_path = path.with_name(path.stem + "_lib.py")
    if lib_path.is_file():
        paths.append(lib_path)
    for candidate in paths:
        try:
            text = candidate.read_text(encoding="utf-8")
        except OSError:
            continue
        if _SPAWN_RE.search(text) or _GIT_RE.search(text):
            return True
    return False


def analyze_test_file(repo_root: Path, test_path: Path) -> dict | None:
    """Return a candidate row when ``test_path`` spawns an import-safe entrypoint,
    else ``None``."""
    text = test_path.read_text(encoding="utf-8")
    targets = _spawn_targets(text)
    if not targets:
        return None
    import_safe = [t for t in targets if (repo_root / t).is_file() and is_import_safe(repo_root / t)]
    if not import_safe:
        return None
    internal_boundary = [t for t in import_safe if has_internal_boundary(repo_root / t)]
    clean_inprocess = [t for t in import_safe if t not in internal_boundary]
    behavior = bool(_BEHAVIOR_RE.search(text))
    exit_contract_only = (not behavior) and bool(_EXIT_RE.search(text)) and ("stderr" in text)
    return {
        "test_file": str(test_path.relative_to(repo_root)),
        "import_safe_targets": import_safe,
        "clean_inprocess_targets": clean_inprocess,
        "internal_boundary_targets": internal_boundary,
        "has_lib": any(_has_lib(repo_root / t) for t in import_safe),
        "behavior_assert": behavior,
        "likely_keep_boundary": exit_contract_only,
    }


def find_boundary_bypass_candidates(repo_root: Path | str) -> dict:
    """Scan ``<repo_root>/tests`` and return the advisory boundary-bypass payload."""
    repo_root = Path(repo_root)
    candidates: list[dict] = []
    scanned = 0
    for test_path in _iter_test_files(repo_root):
        scanned += 1
        row = analyze_test_file(repo_root, test_path)
        if row is not None:
            candidates.append(row)
    keep_boundary = sum(1 for c in candidates if c["likely_keep_boundary"])
    internal_boundary = sum(1 for c in candidates if c["internal_boundary_targets"])
    convertible = sum(
        1
        for c in candidates
        if (not c["likely_keep_boundary"]) and bool(c["clean_inprocess_targets"])
    )
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "advisory",
        "summary": {
            "scanned_test_files": scanned,
            "candidate_count": len(candidates),
            "convertible_count": convertible,
            "keep_boundary_count": keep_boundary,
            "internal_boundary_count": internal_boundary,
        },
        "candidates": candidates,
        "notes": [
            "Advisory: a candidate spawns an import-safe script entrypoint through a "
            "process boundary; the in-process path (import + call, or a *_lib function) likely exists.",
            "Heuristic: only in-repo script literals inside spawn-like calls are counted as targets. "
            "likely_keep_boundary marks exit-code/stderr-contract tests that may legitimately stay at the boundary.",
            "convertible_count counts candidate test files with at least one clean in-process target "
            "and excludes likely keep-boundary rows. internal_boundary_targets flag import-safe targets "
            "that still spawn subprocesses/git internally, where conversion moves the boundary inward "
            "rather than removing it.",
            "Portable policy/ratchet/exemptions live in the quality skill; this probe owns the "
            "Python + charness-layout detection only.",
        ],
    }
