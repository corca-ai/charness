"""Choose mutation files and the tests whose coverage contexts reach them.

This module owns deterministic sample ordering, coverage-context decoding, and
the workload/test-node budgets that filter candidates. Keeping selection as a
single concept prevents the coverage producer from being confused with the
policy that decides which already-measured files may enter a sample.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def deterministic_sample(files: list[str], count: int, seed: str) -> list[str]:
    if count <= 0 or not files:
        return []
    return sorted(files, key=lambda path: stable_hash(f"{seed}:{path}"))[:count]


def read_test_command(config_path: Path) -> str:
    text = config_path.read_text(encoding="utf-8")
    match = re.search(r"^test-command\s*=\s*([\"'])(.*?)\1\s*$", text, re.MULTILINE)
    if not match:
        raise SystemExit(f"could not find cosmic-ray test-command in {config_path}")
    return match.group(2)


def _coverage_relative_path(repo_root: Path, raw_path: str) -> str | None:
    path = Path(raw_path)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(repo_root).as_posix()
        except ValueError:
            return None
    return path.as_posix()


def load_line_contexts(repo_root: Path, coverage_json: Path) -> dict[str, dict[int, set[str]]]:
    data = json.loads(coverage_json.read_text(encoding="utf-8"))
    by_file: dict[str, dict[int, set[str]]] = {}
    for raw_path, payload in (data.get("files") or {}).items():
        rel = _coverage_relative_path(repo_root, raw_path)
        if rel is None:
            continue
        contexts = payload.get("contexts") or {}
        line_contexts: dict[int, set[str]] = {}
        for raw_line, values in contexts.items():
            try:
                line_number = int(raw_line)
            except ValueError:
                continue
            line_contexts[line_number] = {str(value) for value in values if value}
        by_file[rel] = line_contexts
    return by_file


def pytest_nodeid_from_coverage_context(repo_root: Path, context: str) -> str | None:
    if not context.startswith("tests."):
        return None
    parts = context.split(".")
    for split_at in range(len(parts), 0, -1):
        candidate = repo_root / Path(*parts[:split_at]).with_suffix(".py")
        if candidate.is_file():
            remainder = parts[split_at:]
            if not remainder:
                return candidate.relative_to(repo_root).as_posix()
            return candidate.relative_to(repo_root).as_posix() + "::" + "::".join(remainder)
    return None


def select_test_nodeids(
    repo_root: Path, sample: list[str], line_contexts: dict[str, dict[int, set[str]]]
) -> list[str]:
    nodeids: set[str] = set()
    for path in sample:
        for contexts in line_contexts.get(path, {}).values():
            for context in contexts:
                nodeid = pytest_nodeid_from_coverage_context(repo_root, context)
                if nodeid:
                    nodeids.add(nodeid)
    return sorted(nodeids)


def file_test_nodeids(
    repo_root: Path, path: str, line_contexts: dict[str, dict[int, set[str]]]
) -> list[str]:
    return select_test_nodeids(repo_root, [path], line_contexts)


def mutation_workload(path: str, mutation_line_coverage: dict[str, dict[str, int]]) -> int:
    stats = mutation_line_coverage.get(path) or {}
    return int(stats.get("covered", stats.get("mutable", 0)) or 0)


def test_nodeid_count(
    repo_root: Path,
    sample: list[str],
    line_contexts: dict[str, dict[int, set[str]]],
    *,
    coverage_enabled: bool,
) -> int:
    if not coverage_enabled:
        return 0
    return len(select_test_nodeids(repo_root, sample, line_contexts))


def select_budgeted_sample(
    *,
    repo_root: Path,
    candidates: list[str],
    limit: int,
    seed: str,
    selected: list[str],
    selected_workload: int,
    mutation_line_coverage: dict[str, dict[str, int]],
    line_contexts: dict[str, dict[int, set[str]]],
    coverage_enabled: bool,
    max_executable_mutants: int,
    max_executable_mutants_per_file: int,
    max_test_nodeids: int,
) -> tuple[list[str], list[str], int]:
    chosen: list[str] = []
    excluded: list[str] = []
    ordered = deterministic_sample(candidates, len(candidates), seed)
    for index, path in enumerate(ordered):
        if len(chosen) >= limit:
            excluded.extend(ordered[index:])
            break
        workload = mutation_workload(path, mutation_line_coverage)
        if max_executable_mutants_per_file and workload > max_executable_mutants_per_file:
            excluded.append(path)
            continue
        if max_executable_mutants and selected_workload + workload > max_executable_mutants:
            excluded.append(path)
            continue
        if coverage_enabled and not file_test_nodeids(repo_root, path, line_contexts):
            excluded.append(path)
            continue
        proposed = selected + chosen + [path]
        nodeid_count = test_nodeid_count(
            repo_root,
            proposed,
            line_contexts,
            coverage_enabled=coverage_enabled,
        )
        if max_test_nodeids and nodeid_count > max_test_nodeids:
            excluded.append(path)
            continue
        chosen.append(path)
        selected_workload += workload
    return chosen, excluded, selected_workload
