"""Test-file discovery for the standing-test-economics inventory.

File discovery is the consuming repo's contract, not this portable body's. The
inventory resolves its measured test surface by precedence: a non-empty adapter
`command` (the repo's authoritative test-surface lister, consumed verbatim) →
adapter `patterns` (extend or replace the built-in defaults) → the built-in
default globs. A declared command that fails, times out, or returns an empty
surface is surfaced as degraded rather than silently substituting the defaults —
the exact silent-undercount class the adapter seam exists to remove. The
built-in globs stay here only as the zero-config default.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    from scripts.core.subprocess_guard import run_process
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir))
    from scripts.core.subprocess_guard import run_process


def _ensure_scripts_package() -> None:
    here = Path(__file__).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "scripts" / "core" / "repo_file_listing.py").is_file():
            root = str(candidate)
            if root not in sys.path:
                sys.path.insert(0, root)
            return


_ensure_scripts_package()
from scripts.core.repo_file_listing import RepoFileSnapshot  # noqa: E402

IGNORED_DIRS = {
    ".artifacts",
    ".charness",
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "charness-artifacts",
    "mutants",
    "node_modules",
    "vendor",
}
# discovery-boundary: adapter-owned default — consumers override this surface via the adapter `test_file_discovery` command/patterns; this list is only the zero-config fallback.
TEST_FILE_PATTERNS = (
    ":(glob)**/test_*.py",
    ":(glob)**/*_test.py",
    ":(glob)**/*.test.js",
    ":(glob)**/*.test.jsx",
    ":(glob)**/*.test.mjs",
    ":(glob)**/*.test.ts",
    ":(glob)**/*.test.tsx",
    ":(glob)**/*.spec.js",
    ":(glob)**/*.spec.jsx",
    ":(glob)**/*.spec.mjs",
    ":(glob)**/*.spec.ts",
    ":(glob)**/*.spec.tsx",
)
FALLBACK_TEST_FILE_PATTERNS = tuple(
    pattern.removeprefix(":(glob)**/") for pattern in TEST_FILE_PATTERNS
)
DEFAULT_TEST_DISCOVERY: dict[str, Any] = {"command": "", "patterns": [], "patterns_mode": "extend"}
DISCOVERY_COMMAND_TIMEOUT_SECONDS = 30


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def _effective_patterns(discovery: dict[str, Any]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    patterns = [
        pattern
        for pattern in (discovery.get("patterns") or [])
        if isinstance(pattern, str) and pattern
    ]
    if not patterns:
        return TEST_FILE_PATTERNS, FALLBACK_TEST_FILE_PATTERNS
    adapter_glob = tuple(f":(glob)**/{pattern}" for pattern in patterns)
    adapter_fallback = tuple(patterns)
    if discovery.get("patterns_mode") == "replace":
        return adapter_glob, adapter_fallback
    return TEST_FILE_PATTERNS + adapter_glob, FALLBACK_TEST_FILE_PATTERNS + adapter_fallback


def _discover_by_patterns(
    repo_root: Path, patterns: tuple[str, ...], fallback_patterns: tuple[str, ...]
) -> list[Path]:
    _ = patterns
    listed = RepoFileSnapshot(repo_root).list_files(include_untracked=True)
    if listed is None:
        return sorted(
            {
                path
                for pattern in fallback_patterns
                for path in repo_root.rglob(pattern)
                if path.is_file() and not _is_ignored(path.relative_to(repo_root))
            }
        )
    allowed = {path for path in listed if path.is_file()}
    found: list[Path] = []
    seen: set[Path] = set()
    for pattern in fallback_patterns:
        for path in repo_root.rglob(pattern):
            if path in allowed and path not in seen:
                seen.add(path)
                found.append(path)
    return sorted(found)


def _discover_by_command(repo_root: Path, command: str) -> tuple[list[Path] | None, str | None]:
    try:
        result = run_process(
            command,
            cwd=repo_root,
            shell=True,
            timeout_seconds=DISCOVERY_COMMAND_TIMEOUT_SECONDS,
        )
    except OSError as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip().splitlines()
        return None, f"exit {result.returncode}: {detail[-1] if detail else ''}".strip()
    files: set[Path] = set()
    for line in result.stdout.splitlines():
        rel = line.strip()
        if not rel:
            continue
        candidate = Path(rel)
        path = (candidate if candidate.is_absolute() else repo_root / rel).resolve()
        try:
            path.relative_to(repo_root)
        except ValueError:
            continue  # authoritative source must stay inside the repo it measures
        if path.is_file():
            files.add(path)
    return sorted(files), None


def resolve_test_files(
    repo_root: Path, discovery: dict[str, Any] | None
) -> tuple[list[Path], dict[str, Any]]:
    """Return the discovered test files plus a provenance record.

    The provenance record names the resolved `source` (`command` /
    `adapter-patterns` / `default`), the `command_status`
    (`ok` / `empty` / `failed` / None), whether the measurement is `degraded`,
    and any `error`, so the consumer can never mistake a broken authoritative
    lister for a clean zero.
    """
    config = {**DEFAULT_TEST_DISCOVERY, **(discovery or {})}
    command = (config.get("command") or "").strip()
    patterns_declared = bool(
        [
            pattern
            for pattern in (config.get("patterns") or [])
            if isinstance(pattern, str) and pattern
        ]
    )
    patterns_source = "adapter-patterns" if patterns_declared else "default"
    if command:
        files, error = _discover_by_command(repo_root, command)
        if files:
            return files, {
                "source": "command",
                "command_status": "ok",
                "degraded": False,
                "error": None,
            }
        if files is not None:
            # Exited 0 but resolved no test files: an authoritative lister that
            # returns an empty surface is a degraded measurement, not a clean
            # zero — surface it instead of silently reporting no tests. Keep the
            # authoritative (empty) answer; do not substitute the default globs.
            return files, {
                "source": "command",
                "command_status": "empty",
                "degraded": True,
                "error": "authoritative discovery command returned no test files",
            }
        glob_patterns, fallback_patterns = _effective_patterns(config)
        return _discover_by_patterns(repo_root, glob_patterns, fallback_patterns), {
            "source": patterns_source,
            "command_status": "failed",
            "degraded": True,
            "error": error,
        }
    glob_patterns, fallback_patterns = _effective_patterns(config)
    return _discover_by_patterns(repo_root, glob_patterns, fallback_patterns), {
        "source": patterns_source,
        "command_status": None,
        "degraded": False,
        "error": None,
    }
