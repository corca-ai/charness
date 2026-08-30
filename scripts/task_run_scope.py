"""Scope normalization, glob freezing, and candidate classification."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from scripts.task_run_contract import FAIL, PASS, TaskRunError
from scripts.task_run_git import _candidate_carrier, _git_output, _parse_nul_paths

_SUSPICIOUS_RUNTIME_PARTS = frozenset(
    {".pytest_cache", ".ruff_cache", "__pycache__", ".coverage", "coverage", "pytest-tmp", "tmp"}
)


def _normalize_scope(value: str) -> str:
    scope = value.strip()
    if scope.startswith("./"):
        scope = scope[2:]
    if not scope or scope.startswith("/") or "\\" in scope or any(
        part in {"", ".", ".."} for part in scope.split("/")
    ):
        raise TaskRunError(f"scope must be a repository-relative path: {value!r}")
    return scope


def normalize_scopes(scopes: Sequence[str]) -> list[str]:
    """Return one deterministic repository-relative scope list."""
    if not scopes:
        raise TaskRunError("at least one --scope is required")
    return sorted({_normalize_scope(value) for value in scopes})


def _is_glob_scope(scope: str) -> bool:
    return any(marker in scope for marker in ("*", "?", "[", "]"))


def _validate_glob_scope(scope: str) -> None:
    index = 0
    while index < len(scope):
        marker = scope[index]
        if marker == "]":
            raise TaskRunError(f"scope glob has an unmatched ']': {scope!r}")
        if marker != "[":
            index += 1
            continue
        close = scope.find("]", index + 1)
        minimum = index + 2 if scope[index + 1 : index + 2] not in {"!", "^"} else index + 3
        if close < minimum:
            raise TaskRunError(f"scope glob has an invalid character class: {scope!r}")
        index = close + 1


def _glob_path_matches(path: str, pattern: str) -> bool:
    """Match repository path components with inclusive ``**`` semantics."""
    path_parts = path.split("/")
    pattern_parts = pattern.split("/")

    def match(path_index: int, pattern_index: int) -> bool:
        if pattern_index == len(pattern_parts):
            return path_index == len(path_parts)
        component = pattern_parts[pattern_index]
        if component == "**":
            return match(path_index, pattern_index + 1) or (
                path_index < len(path_parts) and match(path_index + 1, pattern_index)
            )
        return path_index < len(path_parts) and fnmatch.fnmatchcase(
            path_parts[path_index], component
        ) and match(path_index + 1, pattern_index + 1)

    return match(0, 0)


def _git_tree_paths(root: Path, base_sha: str) -> tuple[set[str], set[str]]:
    files = _parse_nul_paths(
        _git_output(root, "ls-tree", "-r", "--name-only", "-z", base_sha, "--")
    )
    return _paths_with_directories(files)


def _paths_with_directories(files: Sequence[str]) -> tuple[set[str], set[str]]:
    paths = set(files)
    directories: set[str] = set()
    for path in files:
        for parent in Path(path).parents:
            if parent.as_posix() == ".":
                break
            directory = parent.as_posix()
            paths.add(directory)
            directories.add(directory)
    return paths, directories


def _glob_matches(root: Path, pattern: str) -> tuple[list[str], list[str]]:
    """Match the Git candidate universe, leaving ignored residue separate."""
    files = _parse_nul_paths(
        _git_output(
            root,
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
            "--",
        )
    )
    paths, directories = _paths_with_directories(files)
    matches = sorted(path for path in paths if _glob_path_matches(path, pattern))
    directory_matches = sorted(path for path in matches if path in directories)
    return matches, directory_matches


def resolve_scope_specs(
    root: Path, scopes: Sequence[str], base_sha: str
) -> list[dict[str, Any]]:
    """Freeze scope semantics and expand globs from the selected Git tree."""
    tree_paths, tree_directories = _git_tree_paths(root, base_sha)
    specs: list[dict[str, Any]] = []
    for scope in scopes:
        if scope in tree_paths:
            specs.append(
                {"path": scope, "kind": "directory" if scope in tree_directories else "exact"}
            )
            continue
        if not _is_glob_scope(scope):
            specs.append({"path": scope, "kind": "exact"})
            continue
        _validate_glob_scope(scope)
        matches = sorted(path for path in tree_paths if _glob_path_matches(path, scope))
        directories = sorted(path for path in matches if path in tree_directories)
        if not matches:
            raise TaskRunError(f"scope glob matched no paths: {scope!r}")
        specs.append(
            {
                "path": scope,
                "kind": "glob",
                "matches": matches,
                "match_count": len(matches),
                "directory_matches": directories,
            }
        )
    return specs


def _refresh_scope_specs(
    root: Path,
    specs: Sequence[Mapping[str, Any]],
    *,
    glob_matches: Callable[[Path, str], tuple[list[str], list[str]]] | None = None,
) -> list[dict[str, Any]]:
    refreshed: list[dict[str, Any]] = []
    matcher = glob_matches or _glob_matches
    for source in specs:
        spec = dict(source)
        if spec["kind"] == "glob":
            current, _ = matcher(root, str(spec["path"]))
            matches = sorted(set(spec.get("matches", ())) | set(current))
            spec.update(matches=matches, match_count=len(matches))
        refreshed.append(spec)
    return refreshed


def _scope_matches(path: str, spec: Mapping[str, Any]) -> bool:
    scope = spec["path"]
    if spec["kind"] == "glob":
        return path in spec.get("matches", ()) or any(
            path.startswith(directory.rstrip("/") + "/")
            for directory in spec.get("directory_matches", ())
        )
    return path == scope or (
        spec["kind"] == "directory" and path.startswith(scope.rstrip("/") + "/")
    )


def _paths_in_scopes(paths: Sequence[str], specs: Sequence[Mapping[str, Any]]) -> list[str]:
    return sorted(path for path in paths if any(_scope_matches(path, spec) for spec in specs))


def _scope_result(
    repo_root: Path,
    base_sha: str,
    specs: Sequence[Mapping[str, Any]],
    require_change: bool,
    populations: Mapping[str, Sequence[str]] | None = None,
    head: str | None = None,
    branch: str | None = None,
) -> dict[str, Any]:
    carrier = _candidate_carrier(repo_root, base_sha, populations, head, branch)
    changed = carrier.pop("changed_paths")
    allowed = _paths_in_scopes(changed, specs)
    disallowed = sorted(set(changed) - set(allowed))
    if disallowed:
        verdict, reason = FAIL, "candidate changes paths outside the declared scope"
    elif require_change and not changed:
        verdict, reason = FAIL, "the task required a change but the worktree is unchanged"
    else:
        verdict, reason = PASS, "all candidate changes are within the declared scope"
    return {
        "verdict": verdict,
        "reason": reason,
        "specs": [dict(spec) for spec in specs],
        "changed_paths": changed,
        "disallowed_paths": disallowed,
        "require_change": require_change,
        "candidate_carrier": carrier,
    }


def _path_cause(path: str) -> str:
    parts = set(Path(path).parts)
    if path.endswith(".pyc") or parts & _SUSPICIOUS_RUNTIME_PARTS:
        return "runtime/cache output appeared inside the worktree; inspect PYTHONPYCACHEPREFIX, pytest cache, coverage, and TMPDIR"
    if "node_modules" in parts:
        return "dependency/install output appeared inside the worktree; compare with the prepare step"
    return "the child command produced a file outside the tracked task candidate; inspect the captured Codex log"


def _generated_files(
    populations: Mapping[str, Any],
    specs: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    generated: list[dict[str, str]] = []
    for population in ("untracked", "ignored"):
        for path in populations[population].get("added", []):
            candidate = population == "untracked" and any(
                _scope_matches(path, spec) for spec in specs
            )
            generated.append(
                {
                    "population": population,
                    "path": path,
                    "classification": "candidate" if candidate else "diagnostic",
                    "cause": (
                        "new candidate path is within the declared scope"
                        if candidate
                        else _path_cause(path)
                    ),
                }
            )
    return generated
