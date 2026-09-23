"""Scope normalization, glob freezing, and candidate classification."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.task_run.task_run_contract import FAIL, PASS, TaskRunError  # noqa: E402
from scripts.task_run.task_run_git import (  # noqa: E402
    _candidate_carrier,
    _git_output,
    _parse_nul_paths,
)

_SUSPICIOUS_RUNTIME_PARTS = frozenset(
    {".pytest_cache", ".ruff_cache", "__pycache__", ".coverage", "coverage", "pytest-tmp", "tmp"}
)


def _normalize_scope(value: str) -> str:
    scope = value.strip()
    while scope.startswith("./"):
        scope = scope[2:]
    if (
        not scope
        or scope.startswith("/")
        or "\\" in scope
        or any(part in {"", ".", ".."} for part in scope.split("/"))
    ):
        raise TaskRunError(f"scope must be a repository-relative path: {value!r}")
    return scope


def _expand_braces(value: str) -> list[str]:
    """Expand shell-style `{a,b}` groups into one scope per alternative.

    One `--scope` names one owner seam; a seam that spans two roots
    (`{packages,gateway}/**`) used to degrade to `**` because a brace group
    matched nothing literally (#790). Groups nest and repeat; an unbalanced
    brace or an empty group is refused rather than passed to the matcher as a
    literal that can never match.
    """
    start = value.find("{")
    if start == -1:
        if "}" in value:
            raise TaskRunError(f"scope has an unmatched '}}': {value!r}")
        return [value]
    depth = 0
    for index in range(start, len(value)):
        if value[index] == "{":
            depth += 1
        elif value[index] == "}":
            depth -= 1
            if depth == 0:
                end = index
                break
    else:
        raise TaskRunError(f"scope has an unmatched '{{': {value!r}")
    body = value[start + 1 : end]
    alternatives: list[str] = []
    depth = 0
    current = ""
    for char in body:
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        if char == "," and depth == 0:
            alternatives.append(current)
            current = ""
        else:
            current += char
    alternatives.append(current)
    if len(alternatives) < 2 or any(not alternative for alternative in alternatives):
        raise TaskRunError(f"scope brace group needs two or more non-empty alternatives: {value!r}")
    expanded: list[str] = []
    for alternative in alternatives:
        expanded.extend(_expand_braces(value[:start] + alternative + value[end + 1 :]))
    return expanded


def normalize_scopes(scopes: Sequence[str]) -> list[str]:
    """Return one deterministic repository-relative scope list, as declared.

    Brace groups are expanded later, in `resolve_scope_specs`, so an existing
    literal path whose name carries braces keeps the same precedence a literal
    with glob metacharacters already has.
    """
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
        return (
            path_index < len(path_parts)
            and fnmatch.fnmatchcase(path_parts[path_index], component)
            and match(path_index + 1, pattern_index + 1)
        )

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


def resolve_scope_specs(root: Path, scopes: Sequence[str], base_sha: str) -> list[dict[str, Any]]:
    """Freeze scope semantics and expand globs from the selected Git tree."""
    tree_paths, tree_directories = _git_tree_paths(root, base_sha)
    specs: list[dict[str, Any]] = []
    for declared in scopes:
        if declared in tree_paths:
            specs.append(
                {
                    "path": declared,
                    "kind": "directory" if declared in tree_directories else "exact",
                }
            )
            continue
        for scope in _expand_braces(declared):
            spec = _resolve_one_scope(scope, tree_paths, tree_directories)
            if scope != declared:
                spec["expanded_from"] = declared
            specs.append(spec)
    return specs


def _resolve_one_scope(
    scope: str, tree_paths: set[str], tree_directories: set[str]
) -> dict[str, Any]:
    if scope in tree_paths:
        return {"path": scope, "kind": "directory" if scope in tree_directories else "exact"}
    if not _is_glob_scope(scope):
        return {"path": scope, "kind": "exact"}
    _validate_glob_scope(scope)
    matches = sorted(path for path in tree_paths if _glob_path_matches(path, scope))
    directories = sorted(path for path in matches if path in tree_directories)
    if not matches:
        # A zero-match glob is a creation seam, not a preflight refusal
        # (#836): warn like an unmatched exact scope and admit paths the
        # lane creates that match the pattern on refresh.
        return {
            "path": scope,
            "kind": "glob",
            "matches": [],
            "match_count": 0,
            "directory_matches": [],
        }
    return {
        "path": scope,
        "kind": "glob",
        "matches": matches,
        "match_count": len(matches),
        "directory_matches": directories,
    }


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
            # File matches union with post-freeze additions, but the frozen
            # directory-match set never grows: a lane-created directory is
            # not admitted as a scope root on refresh (#831). Paths that
            # literally match the glob pattern itself are still unioned;
            # admitting a new scope root is an explicit operator-approved
            # rescope (see rescope_result), never an automatic refresh.
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
        verdict, reason = (
            FAIL,
            ("candidate changes paths outside the declared scope: " + ", ".join(disallowed)),
        )
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
        return (
            "dependency/install output appeared inside the worktree; compare with the prepare step"
        )
    return "the child command produced a file outside the tracked task candidate; inspect the captured Codex log"


#: Blocker fragment a require-change lane emits when the real owner of the
#: requested behavior lies outside the declared scope (#831). The carrier
#: prompt fixes this wording, so the receipt can parse it back into a typed
#: scope-extension request instead of forcing a fresh lane relaunch.
SCOPE_MISMATCH_BLOCKER_MARKER = "scope mismatch - real owner"


def parse_scope_extension_request(blocker: str | None) -> dict[str, Any] | None:
    """Parse a lane-reported scope-mismatch blocker into a typed request (#831).

    Returns ``{"requested_paths": [...], "reason": blocker}`` when the blocker
    names an out-of-scope owner path, else None. Warning-only parsing: it never
    expands any scope, it only records what the lane asked to add so the
    operator can approve or refuse it before any re-validation.
    """
    if not blocker or SCOPE_MISMATCH_BLOCKER_MARKER not in blocker:
        return None
    after = blocker.split("real owner", 1)[1].strip()
    candidate = after.split(" is outside", 1)[0].strip().strip("<>").strip()
    if not candidate:
        return None
    return {"requested_paths": [candidate], "reason": blocker}


def scope_closure_warnings(
    specs: Sequence[Mapping[str, Any]],
    tree_paths: set[str],
) -> list[dict[str, str]]:
    """Name statically discoverable scope-closure gaps before launch (#831, #836).

    An ``exact`` spec absent from the base tree never matches an existing
    path: it is either an intended-new file (creation seam) or a typo / missed
    companion path that will fail late at candidate validation. A ``glob``
    spec with no frozen matches is the same shape: either a creation seam for
    paths the lane will create or a mistyped pattern. The scope itself is
    unchanged (warning-only, never expands); the caller surfaces these on the
    preflight/dry-run receipt so the operator can correct the declaration
    before spending a lane run.
    """
    warnings: list[dict[str, str]] = []
    for spec in specs:
        if spec.get("kind") == "exact":
            path = str(spec.get("path", ""))
            if path in tree_paths:
                continue
            warnings.append(
                {
                    "code": "unmatched-literal-scope",
                    "path": path,
                    "message": (
                        f"scope {path!r} matches no path in the base tree: "
                        "either an intended-new file or a missed companion path; "
                        "the scope is unchanged"
                    ),
                }
            )
            continue
        if spec.get("kind") == "glob" and not spec.get("matches"):
            path = str(spec.get("path", ""))
            warnings.append(
                {
                    "code": "unmatched-glob-scope",
                    "path": path,
                    "message": (
                        f"scope glob {path!r} matches no path in the base tree: "
                        "either a creation seam for paths the lane will create "
                        "or a mistyped pattern; the scope is unchanged"
                    ),
                }
            )
    return warnings


def rescope_result(
    repo_root: Path,
    base_sha: str,
    existing_specs: Sequence[Mapping[str, Any]],
    extra_scopes: Sequence[str],
    require_change: bool,
    populations: Mapping[str, Sequence[str]] | None = None,
    head: str | None = None,
    branch: str | None = None,
) -> dict[str, Any]:
    """Re-validate the same worktree candidate with an approved scope addition.

    The operator-approved counterpart to a lane-reported
    :func:`parse_scope_extension_request` (#831): the extra scopes are
    normalized, resolved against the same base, unioned with the existing
    specs, refreshed, and re-run through :func:`_scope_result` on the SAME
    worktree. No new lane runs; truly forbidden paths still refuse because
    only explicitly approved additions are admitted.
    """
    added_specs = resolve_scope_specs(repo_root, normalize_scopes(extra_scopes), base_sha)
    merged: list[dict[str, Any]] = [dict(spec) for spec in existing_specs]
    seen = {(str(spec.get("path")), str(spec.get("kind"))) for spec in merged}
    for spec in added_specs:
        key = (str(spec.get("path")), str(spec.get("kind")))
        if key not in seen:
            seen.add(key)
            merged.append(dict(spec))
    refreshed = _refresh_scope_specs(repo_root, merged)
    result = _scope_result(
        repo_root, base_sha, refreshed, require_change, populations, head, branch
    )
    result["added_specs"] = added_specs
    return result


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
