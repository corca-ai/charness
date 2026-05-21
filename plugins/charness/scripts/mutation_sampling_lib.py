"""Helpers for coverage-aware Cosmic Ray sample selection."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
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


def coverage_run_command(test_command: str, data_file: Path) -> list[str]:
    parts = shlex.split(test_command)
    if len(parts) >= 3 and parts[0] in {"python", "python3"} and parts[1:3] == ["-m", "pytest"]:
        return [
            parts[0],
            "-m",
            "coverage",
            "run",
            "--data-file",
            str(data_file),
            "-m",
            "pytest",
            *parts[3:],
        ]
    if parts and parts[0] == "pytest":
        return [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--data-file",
            str(data_file),
            "-m",
            "pytest",
            *parts[1:],
        ]
    raise SystemExit(
        "mutation coverage sampling supports pytest commands shaped as "
        "`python3 -m pytest ...` or `pytest ...`; use a helper script for other runners"
    )


def run_test_coverage(repo_root: Path, test_command: str, coverage_json: Path) -> None:
    coverage_json.parent.mkdir(parents=True, exist_ok=True)
    data_file = coverage_json.with_name(".mutation-coverage")
    rcfile = coverage_json.with_name(".mutation-coveragerc")
    sitecustomize_dir = coverage_json.with_name(".mutation-sitecustomize")
    sitecustomize_dir.mkdir(parents=True, exist_ok=True)
    sitecustomize_dir.joinpath("sitecustomize.py").write_text(
        "\n".join(
            [
                "import os",
                "import coverage",
                "",
                "coverage.process_startup()",
                "current = coverage.Coverage.current()",
                "raw_context = os.environ.get('PYTEST_CURRENT_TEST', '').split(' (', 1)[0]",
                "if current is not None and raw_context:",
                "    path_part, *rest = raw_context.split('::')",
                "    if path_part.endswith('.py'):",
                "        context = path_part[:-3].replace('/', '.')",
                "        if rest:",
                "            context += '.' + '.'.join(rest)",
                "    else:",
                "        context = raw_context",
                "    current.switch_context(context)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    rcfile.write_text(
        "\n".join(
            [
                "[run]",
                f"data_file = {data_file}",
                "dynamic_context = test_function",
                "disable_warnings = dynamic-conflict",
                "parallel = True",
                "",
            ]
        ),
        encoding="utf-8",
    )
    if data_file.exists():
        data_file.unlink()
    for stale_shard in data_file.parent.glob(data_file.name + ".*"):
        stale_shard.unlink()
    command = coverage_run_command(test_command, data_file)
    existing_pythonpath = os.environ.get("PYTHONPATH")
    env = {
        **os.environ,
        "COVERAGE_PROCESS_START": str(rcfile),
        "COVERAGE_RCFILE": str(rcfile),
        "PYTHONPATH": (
            str(sitecustomize_dir)
            if not existing_pythonpath
            else os.pathsep.join([str(sitecustomize_dir), existing_pythonpath])
        ),
    }
    subprocess.run(command, cwd=repo_root, check=True, env=env)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "coverage",
            "combine",
            "--rcfile",
            str(rcfile),
            "--data-file",
            str(data_file),
            str(coverage_json.parent),
        ],
        cwd=repo_root,
        check=True,
        env=env,
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "coverage",
            "json",
            "--rcfile",
            str(rcfile),
            "--show-contexts",
            "--data-file",
            str(data_file),
            "-o",
            str(coverage_json),
        ],
        cwd=repo_root,
        check=True,
        env=env,
    )


def _coverage_relative_path(repo_root: Path, raw_path: str) -> str | None:
    path = Path(raw_path)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(repo_root).as_posix()
        except ValueError:
            return None
    return path.as_posix()


def load_covered_lines(repo_root: Path, coverage_json: Path) -> dict[str, set[int]]:
    data = json.loads(coverage_json.read_text(encoding="utf-8"))
    covered: dict[str, set[int]] = {}
    for raw_path, payload in (data.get("files") or {}).items():
        rel = _coverage_relative_path(repo_root, raw_path)
        if rel is None:
            continue
        lines = payload.get("executed_lines") or []
        covered[rel] = {int(line) for line in lines}
    return covered


def load_file_statement_lines(repo_root: Path, coverage_json: Path) -> dict[str, tuple[set[int], set[int]]]:
    data = json.loads(coverage_json.read_text(encoding="utf-8"))
    coverage: dict[str, tuple[set[int], set[int]]] = {}
    for raw_path, payload in (data.get("files") or {}).items():
        rel = _coverage_relative_path(repo_root, raw_path)
        if rel is None:
            continue
        executed = {int(line) for line in payload.get("executed_lines") or []}
        missing = {int(line) for line in payload.get("missing_lines") or []}
        coverage[rel] = (executed, missing)
    return coverage


def filter_eligible_by_coverage(
    eligible: list[str],
    covered_lines: dict[str, set[int]],
    statement_lines: dict[str, tuple[set[int], set[int]]] | None = None,
    *,
    min_file_coverage: float = 0.0,
) -> list[str]:
    selected: list[str] = []
    for path in eligible:
        if not covered_lines.get(path):
            continue
        if statement_lines is not None and min_file_coverage > 0:
            executed, missing = statement_lines.get(path, (set(), set()))
            total = len(executed | missing)
            ratio = (len(executed) / total) if total else 0.0
            if ratio < min_file_coverage:
                continue
        selected.append(path)
    return selected


def rewrite_cosmic_ray_targets(config_path: Path, paths: list[str]) -> None:
    text = config_path.read_text(encoding="utf-8")
    block = "module-path = [\n" + "".join(f'    "{path}",\n' for path in paths) + "]"
    pattern = re.compile(r"^module-path\s*=\s*\[.*?\]", re.MULTILINE | re.DOTALL)
    if not pattern.search(text):
        raise SystemExit(f"could not find cosmic-ray module-path list in {config_path}")
    config_path.write_text(pattern.sub(block, text, count=1), encoding="utf-8")


def rewrite_cosmic_ray_test_command(config_path: Path, test_command: str) -> None:
    text = config_path.read_text(encoding="utf-8")
    escaped = test_command.replace("\\", "\\\\").replace('"', '\\"')
    pattern = re.compile(r"^test-command\s*=\s*([\"']).*?\1\s*$", re.MULTILINE)
    if not pattern.search(text):
        raise SystemExit(f"could not find cosmic-ray test-command in {config_path}")
    config_path.write_text(
        pattern.sub(f'test-command = "{escaped}"', text, count=1),
        encoding="utf-8",
    )


def mutation_probe_paths(repo_root: Path) -> tuple[Path, Path]:
    probe_dir = repo_root / "reports" / "mutation"
    return probe_dir / "cosmic-ray-sample-probe.toml", probe_dir / "cosmic-ray-sample-probe.sqlite"


def build_mutation_line_coverage(
    repo_root: Path,
    config_path: Path,
    candidates: list[str],
    covered_lines: dict[str, set[int]],
) -> dict[str, dict[str, int]]:
    if not candidates:
        return {}
    try:
        from cosmic_ray.work_db import use_db

        from scripts.filter_cosmic_ray_mutants import should_skip_mutation
    except ImportError as exc:
        raise SystemExit(
            "cosmic-ray is required for mutation-line sampling; install Cosmic Ray 8.4.6 first"
        ) from exc

    probe_config, probe_session = mutation_probe_paths(repo_root)
    probe_config.parent.mkdir(parents=True, exist_ok=True)
    probe_config.write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")
    rewrite_cosmic_ray_targets(probe_config, candidates)
    if probe_session.exists():
        probe_session.unlink()
    result = subprocess.run(
        ["cosmic-ray", "init", str(probe_config), str(probe_session)],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(
            "cosmic-ray init failed during mutation-line sampling\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    stats = {path: {"mutable": 0, "covered": 0, "uncovered": 0} for path in candidates}
    with use_db(probe_session) as db:
        for item in db.work_items:
            for mutation in item.mutations:
                module_path = mutation.module_path.as_posix()
                if module_path not in stats:
                    continue
                if should_skip_mutation(repo_root, mutation):
                    continue
                line_number, _start_col = mutation.start_pos
                stats[module_path]["mutable"] += 1
                if int(line_number) in covered_lines.get(module_path, set()):
                    stats[module_path]["covered"] += 1
                else:
                    stats[module_path]["uncovered"] += 1
    return stats


def filter_eligible_by_mutation_line_coverage(
    eligible: list[str],
    mutation_line_coverage: dict[str, dict[str, int]],
) -> list[str]:
    selected: list[str] = []
    for path in eligible:
        stats = mutation_line_coverage.get(path) or {}
        if int(stats.get("mutable", 0)) <= 0:
            continue
        if int(stats.get("uncovered", 0)) == 0:
            selected.append(path)
    return selected


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
    repo_root: Path,
    sample: list[str],
    line_contexts: dict[str, dict[int, set[str]]],
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
    repo_root: Path,
    path: str,
    line_contexts: dict[str, dict[int, set[str]]],
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
