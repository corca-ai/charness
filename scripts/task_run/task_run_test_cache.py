"""Content-addressed green outcomes for individual train test files."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from scripts.core.subprocess_guard import run_process
from scripts.task_run.task_run_state import RESULT_EXIT_CODES, ResultKind

PASS = "pass"


def train_cache_root(report_root: Path) -> Path | None:
    """Use the repo runtime shared by all temporary train worktrees."""
    for parent in Path(report_root).resolve().parents:
        if parent.name == "train-runs":
            return parent.parent / "test-result-cache"
    return None


def _inside_worktree(path: Path, worktree: Path) -> bool:
    try:
        path.relative_to(worktree.resolve())
    except ValueError:
        return False
    return True


def _is_pytest_file(path: Path) -> bool:
    return path.suffix == ".py" and (
        path.name.startswith("test_") or path.name.endswith("_test.py")
    )


def _files_in_targets(worktree: Path, targets: Sequence[str]) -> list[Path]:
    files: set[Path] = set()
    for target in targets:
        path = (worktree / target.split("::", 1)[0]).resolve()
        if not _inside_worktree(path, worktree):
            continue
        if path.is_file() and _is_pytest_file(path):
            files.add(path)
        elif path.is_dir():
            files.update(
                candidate for candidate in path.rglob("*.py") if _is_pytest_file(candidate)
            )
    return sorted(files)


def _standing_test_targets(argv: Sequence[str], worktree: Path) -> list[Path] | None:
    runner_index = next(
        (
            index
            for index, argument in enumerate(argv)
            if argument.endswith("scripts/gates_support/run_standing_pytest.py")
        ),
        None,
    )
    if runner_index is None:
        return None
    query = [
        *argv[: runner_index + 1],
        "--repo-root",
        str(worktree),
        "--print-expanded-targets",
    ]
    result = run_process(query, cwd=worktree, timeout_seconds=30)
    if result.returncode != 0:
        return None
    targets = result.stdout.splitlines()
    files = _files_in_targets(worktree, targets)
    return files or None


def cacheable_command(
    argv: Sequence[str], worktree: Path
) -> tuple[list[Path], list[str]] | None:
    """Resolve test files and the command form that can omit cached files."""
    standing = _standing_test_targets(argv, worktree)
    if standing is not None:
        base = [
            argument
            for index, argument in enumerate(argv)
            if argument not in {"--pytest-target", "--extra-pytest-target"}
            and not (
                index > 0
                and argv[index - 1] in {"--pytest-target", "--extra-pytest-target"}
            )
        ]
        return standing, base
    files: list[Path] = []
    for argument in argv:
        candidate = (worktree / argument.split("::", 1)[0]).resolve()
        if _inside_worktree(candidate, worktree) and candidate.is_file() and _is_pytest_file(candidate):
            files.append(candidate)
    if not files:
        return None
    return sorted(set(files)), list(argv)


def with_pytest_targets(argv: Sequence[str], files: Sequence[Path]) -> list[str]:
    command = [
        argument
        for index, argument in enumerate(argv)
        if argument not in {"--pytest-target", "--extra-pytest-target"}
        and not (
            index > 0
            and argv[index - 1] in {"--pytest-target", "--extra-pytest-target"}
        )
    ]
    for path in files:
        command.extend(("--pytest-target", path.as_posix()))
    return command


def combine_verify_outcomes(
    command_id: str,
    cached: Sequence[Mapping[str, Any]],
    executed: dict[str, Any] | None,
) -> dict[str, Any]:
    result = dict(executed or cached[0])
    result["command_id"] = command_id
    for key in ("known_failures", "new_failures"):
        values = {
            value
            for item in (*cached, *((executed,) if executed is not None else ()))
            for value in item.get(key, [])
        }
        result[key] = sorted(values)
    if cached and executed is not None:
        result["status"] = PASS if executed["status"] == PASS else "fail"
    return result


def prepare_verify(
    cache_root: Path, repo_root: Path, command_id: str, argv: Sequence[str]
) -> dict[str, Any] | None:
    """Return the filtered command or a green result when every file is cached."""
    targets = cacheable_command(argv, repo_root)
    if targets is None:
        return None
    files, filtered_command = targets
    cached: list[Mapping[str, Any]] = []
    uncached: list[Path] = []
    for test_file in files:
        outcome = cached_green_outcome(cache_root, repo_root, test_file)
        if outcome is None:
            uncached.append(test_file)
        else:
            outcome["command_id"] = command_id
            cached.append(outcome)
    if not uncached:
        return {
            "command": list(argv),
            "files": files,
            "cached": cached,
            "skip_result": combine_verify_outcomes(command_id, cached, None),
            "cache_root": Path(cache_root),
            "repo_root": Path(repo_root),
        }
    command = list(argv)
    if cached:
        if any(
            argument.endswith("scripts/gates_support/run_standing_pytest.py")
            for argument in argv
        ):
            command = with_pytest_targets(filtered_command, uncached)
        else:
            cached_paths = {path.resolve() for path in files} - {
                path.resolve() for path in uncached
            }
            command = [
                argument
                for argument in argv
                if (repo_root / argument.split("::", 1)[0]).resolve() not in cached_paths
            ]
    return {
        "command": command,
        "files": files,
        "cached": cached,
        "skip_result": None,
        "cache_root": Path(cache_root),
        "repo_root": Path(repo_root),
    }


def finish_verify(plan: Mapping[str, Any], executed: dict[str, Any]) -> dict[str, Any]:
    """Merge the executed result and remember files only after a green outcome."""
    combined = combine_verify_outcomes(
        str(executed["command_id"]), plan["cached"], executed
    )
    if combined["status"] == PASS:
        for test_file in plan["files"]:
            remember_green_outcome(
                Path(plan["cache_root"]), Path(plan["repo_root"]), test_file, combined
            )
    return combined


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _module_files(root: Path, parts: tuple[str, ...]) -> set[Path]:
    """Resolve a local Python module and its package initializers."""
    if not parts or any(not part.isidentifier() for part in parts):
        return set()
    found: set[Path] = set()
    for index in range(1, len(parts)):
        initializer = root.joinpath(*parts[:index], "__init__.py")
        if initializer.is_file():
            found.add(initializer)
    module = root.joinpath(*parts).with_suffix(".py")
    package = root.joinpath(*parts, "__init__.py")
    if module.is_file():
        found.add(module)
    elif package.is_file():
        found.add(package)
    return found


def _local_import_files(
    root: Path, source: Path, parts: tuple[str, ...]
) -> set[Path]:
    found = _module_files(root, parts)
    local = _module_files(source.parent, parts)
    return found | {path for path in local if _inside(path.resolve(), root)}


def _relative_import_base(root: Path, source: Path, level: int, module: str | None) -> tuple[str, ...]:
    relative = source.relative_to(root)
    package = relative.parts[:-1]
    base = package[: max(0, len(package) - level + 1)]
    return (*base, *(module.split(".") if module else ()))


def _imports(root: Path, source: Path) -> set[Path]:
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    found: set[Path] = set()
    for node in ast.walk(tree):
        modules: list[tuple[str, ...]] = []
        if isinstance(node, ast.Import):
            modules.extend(tuple(alias.name.split(".")) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = _relative_import_base(root, source, node.level, node.module)
            elif node.module:
                base = tuple(node.module.split("."))
            else:
                continue
            modules.append(base)
            modules.extend((*base, alias.name) for alias in node.names if alias.name != "*")
        elif isinstance(node, ast.Call):
            for argument in node.args:
                if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                    name = argument.value
                    if name.startswith(("scripts.", "tests.")):
                        modules.append(tuple(name.split(".")))
        for parts in modules:
            # Resolve repo-root and test-directory imports; external modules miss.
            found.update(_local_import_files(root, source, parts))
    return found


def _closure_files(root: Path, test_file: Path) -> set[Path]:
    pending = _imports(root, test_file)
    for parent in test_file.parents:
        if parent == root.parent:
            break
        if not _inside(parent, root):
            break
        conftest = parent / "conftest.py"
        if conftest.is_file():
            pending.add(conftest)
    seen: set[Path] = set()
    while pending:
        current = pending.pop()
        if current == test_file or current in seen:
            continue
        seen.add(current)
        pending.update(_imports(root, current) - seen - {test_file})
    return seen


def file_hashes(repo_root: Path, test_file: Path) -> dict[str, str] | None:
    """Return the test source and transitive local import-closure hashes."""
    root = Path(repo_root).resolve()
    path = Path(test_file)
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if not _inside(path, root) or not path.is_file() or path.suffix != ".py":
        return None
    try:
        content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        closure_hash = hashlib.sha256()
        for dependency in sorted(_closure_files(root, path), key=lambda item: item.relative_to(root).as_posix()):
            relative = dependency.relative_to(root).as_posix()
            closure_hash.update(relative.encode("utf-8"))
            closure_hash.update(b"\0")
            closure_hash.update(hashlib.sha256(dependency.read_bytes()).digest())
        return {"content_hash": content_hash, "import_closure_hash": closure_hash.hexdigest()}
    except (OSError, SyntaxError, UnicodeError, ValueError):
        return None


def _entry_path(cache_root: Path, relative_path: str, hashes: Mapping[str, str]) -> Path:
    identity = "\0".join(
        (relative_path, hashes["content_hash"], hashes["import_closure_hash"])
    )
    key = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return cache_root / f"{key}.json"


def _green_envelope(record: object) -> dict[str, Any] | None:
    if not isinstance(record, Mapping):
        return None
    success_code = RESULT_EXIT_CODES[ResultKind.SUCCESS]
    if record.get("result_kind") != ResultKind.SUCCESS.value or record.get("exit_code") != success_code:
        return None
    outcome = record.get("verify_outcome")
    if not isinstance(outcome, Mapping):
        return None
    if outcome.get("status") != PASS or outcome.get("timed_out") is not False:
        return None
    if outcome.get("exit_code") != 0:
        return None
    if outcome.get("known_failures") not in (None, []):
        return None
    if outcome.get("new_failures") not in (None, []):
        return None
    return dict(outcome)


def cached_green_outcome(
    cache_root: Path, repo_root: Path, test_file: Path
) -> dict[str, Any] | None:
    """Read back a prior green outcome only when both current hashes still match."""
    hashes = file_hashes(repo_root, test_file)
    if hashes is None:
        return None
    root = Path(repo_root).resolve()
    path = Path(test_file)
    if not path.is_absolute():
        path = root / path
    relative = path.resolve().relative_to(root).as_posix()
    entry = _entry_path(Path(cache_root), relative, hashes)
    try:
        record = json.loads(entry.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeError):
        return None
    if not isinstance(record, Mapping):
        return None
    if record.get("path") != relative or record.get("hashes") != hashes:
        return None
    return _green_envelope(record)


def remember_green_outcome(
    cache_root: Path,
    repo_root: Path,
    test_file: Path,
    verify_outcome: Mapping[str, Any],
) -> bool:
    """Persist a green command outcome with the frozen success envelope."""
    record = {
        "result_kind": ResultKind.SUCCESS.value,
        "exit_code": RESULT_EXIT_CODES[ResultKind.SUCCESS],
        "verify_outcome": dict(verify_outcome),
    }
    if _green_envelope(record) is None:
        return False
    hashes = file_hashes(repo_root, test_file)
    if hashes is None:
        return False
    root = Path(repo_root).resolve()
    path = Path(test_file)
    if not path.is_absolute():
        path = root / path
    relative = path.resolve().relative_to(root).as_posix()
    cache_root = Path(cache_root)
    record.update({"path": relative, "hashes": hashes})
    try:
        cache_root.mkdir(parents=True, exist_ok=True)
        destination = _entry_path(cache_root, relative, hashes)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=cache_root, prefix=".test-cache-", delete=False
        ) as handle:
            temporary = Path(handle.name)
            json.dump(record, handle, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, destination)
    except OSError:
        try:
            temporary.unlink(missing_ok=True)
        except (OSError, UnboundLocalError):
            pass
        return False
    return True
