from __future__ import annotations

import json
import re
import stat
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

sys.path.append(str(Path(__file__).resolve().parent))
_DISCOVERY = __import__("standing_gate_discovery_lib")
_MARKERS = __import__("surface_marker_lib")
# Test-file discovery is an adapter-owned contract, held in its own module.
_TEST_DISCOVERY = __import__("test_discovery_lib")
# The `du`-backed pytest temp scan is its own concern, with its own retry policy
# and failure taxonomy.
_SCAN = __import__("pytest_temp_scan_lib")
discover_surfaces = _DISCOVERY.discover_surfaces
iter_snippets = _DISCOVERY.iter_snippets
find_nested_cli_files = _MARKERS.nested_cli_files
find_pytest_file_test_counts = _MARKERS.pytest_file_test_counts
find_subprocess_settlement_seams = _MARKERS.subprocess_settlement_seams
resolve_test_files = _TEST_DISCOVERY.resolve_test_files

TRANSPILE_EXTENSIONS = {".ts", ".tsx"}
NODE_TEST_RE = re.compile(r"(?:^|\s)node\b[^\n]*(?:^|\s)--test(?:\s|$)")
TS_LOADER_RE = re.compile(r"\b(tsx|ts-node|swc-node|esbuild-register)\b")
# Recognize both pytest's own numbered session dirs (`pytest-<n>`) and the standing
# runner's explicit basetemp (`charness-run-<time_ns>`, deliberately not named
# `pytest-*` so pytest's numbered-dir cleanup cannot delete it mid-run — see
# scripts/run_standing_pytest.py default_basetemp). Both hold the same
# `popen-gw*`/seed footprint the drill-down inventory reports.
PYTEST_SESSION_RE = _SCAN.PYTEST_SESSION_RE
PYTEST_WORKER_RE = _SCAN.PYTEST_WORKER_RE
PYTEST_SEED_PREFIXES = _SCAN.PYTEST_SEED_PREFIXES
PYTEST_TEMP_SCAN_ATTEMPTS = _SCAN.PYTEST_TEMP_SCAN_ATTEMPTS


def _iter_child_stats(path: Path):
    try:
        iterator = path.iterdir()
    except OSError:
        return
    while True:
        try:
            child = next(iterator)
        except StopIteration:
            break
        except OSError:
            break
        try:
            child_stat = child.stat(follow_symlinks=False)
        except OSError:
            continue
        yield child, child_stat


def _iter_child_dirs(path: Path) -> list[Path]:
    return [
        child for child, child_stat in _iter_child_stats(path) if stat.S_ISDIR(child_stat.st_mode)
    ]


def _runner_snippets(repo_root: Path) -> list[dict[str, str]]:
    surfaces = discover_surfaces(repo_root)
    snippets = [
        item
        for item in iter_snippets(surfaces)
        if any(
            token in item["snippet"]
            for token in ("pytest", "node --test", "vitest", "jest", "cargo test", "go test")
        )
    ]
    package_path = repo_root / "package.json"
    if package_path.is_file():
        payload = json.loads(package_path.read_text(encoding="utf-8"))
        scripts = payload.get("scripts", {}) if isinstance(payload, dict) else {}
        if isinstance(scripts, dict):
            for name, command in scripts.items():
                if (
                    isinstance(name, str)
                    and isinstance(command, str)
                    and ("test" in name or NODE_TEST_RE.search(command))
                ):
                    snippets.append(
                        {"path": "package.json", "origin": f"script:{name}", "snippet": command}
                    )
    return snippets


def _du_bytes(path: Path, *args: str) -> int | None:
    try:
        result = run_process(["du", *args, str(path)], cwd=Path.cwd(), timeout_seconds=10)
        if result.returncode != 0:
            return None
        return int(result.stdout.split()[0])
    except (OSError, ValueError, IndexError):
        return None


_du_bytes_many = _SCAN.du_bytes_many


def _iter_file_stats(path: Path):
    stack = [path]
    while stack:
        for child, child_stat in _iter_child_stats(stack.pop()):
            if stat.S_ISDIR(child_stat.st_mode):
                stack.append(child)
            elif stat.S_ISREG(child_stat.st_mode):
                yield child_stat


def _dir_usage(path: Path) -> dict[str, int]:
    apparent = _du_bytes(path, "-sb")
    disk = _du_bytes(path, "-sB1")
    return {
        "bytes": apparent
        if apparent is not None
        else sum(item.st_size for item in _iter_file_stats(path)),
        "disk_bytes": disk
        if disk is not None
        else sum(item.st_blocks * 512 for item in _iter_file_stats(path)),
    }


def _dir_usages(paths: list[Path]) -> dict[Path, dict[str, int]]:
    """Measure a stable path set with two batched ``du`` queries and safe fallbacks."""
    unique_paths = list(dict.fromkeys(paths))
    apparent = _du_bytes_many(unique_paths, "-sb")
    disk = _du_bytes_many(unique_paths, "-sB1")
    return {
        path: (
            {"bytes": apparent[path], "disk_bytes": disk[path]}
            if path in apparent and path in disk
            else _dir_usage(path)
        )
        for path in unique_paths
    }


def _attach_usage_totals(
    usage_paths: list[Path],
    seed_totals: dict[str, dict[str, int]],
    top_tests: list[dict[str, Any]],
) -> dict[Path, dict[str, int]]:
    root = usage_paths[0]
    usages = {root: _dir_usage(root)}
    usages.update(_dir_usages(usage_paths[1:]))
    for prefix in PYTEST_SEED_PREFIXES:
        for path in usage_paths:
            if path.name.startswith(prefix):
                usage = usages[path]
                seed_totals[prefix]["bytes"] += usage["bytes"]
                seed_totals[prefix]["disk_bytes"] += usage["disk_bytes"]
    for item in top_tests:
        usage = usages[root / item["path"]]
        item["bytes"] = usage["bytes"]
        item["disk_bytes"] = usage["disk_bytes"]
    return usages


# The `du`-backed quick scan, its retry policy, and its failure taxonomy live in
# their own module. Re-exported under the historical private names so existing
# callers and the plugin export keep working.
_pytest_temp_root = _SCAN.pytest_temp_root
_du_scan_once = _SCAN.du_scan_once
_du_reported_root_total = _SCAN.du_reported_root_total
_pytest_temp_footprint_quick = _SCAN.pytest_temp_footprint_quick


def _pytest_temp_footprint() -> dict[str, Any]:
    root = _pytest_temp_root()
    if not root.exists():
        return {"status": "missing", "root": str(root)}
    sessions = sorted(path for path in _iter_child_dirs(root) if PYTEST_SESSION_RE.match(path.name))
    seed_totals: dict[str, dict[str, int]] = {
        prefix: {"count": 0, "bytes": 0, "disk_bytes": 0} for prefix in PYTEST_SEED_PREFIXES
    }
    top_tests: list[dict[str, Any]] = []
    usage_paths = [root]
    worker_count = 0
    for session in sessions:
        workers = [path for path in _iter_child_dirs(session) if PYTEST_WORKER_RE.match(path.name)]
        worker_count += len(workers)
        matched_seed_roots: list[Path] = []
        seed_candidates = _iter_child_dirs(session)
        for worker in workers:
            seed_candidates.extend(_iter_child_dirs(worker))
        for path in sorted(seed_candidates, key=lambda candidate: len(candidate.parts)):
            if path.is_symlink() or not path.is_dir():
                continue
            if any(parent in path.parents for parent in matched_seed_roots):
                continue
            for prefix in PYTEST_SEED_PREFIXES:
                if path.name.startswith(prefix):
                    usage_paths.append(path)
                    seed_totals[prefix]["count"] += 1
                    matched_seed_roots.append(path)
                    break
        for worker in workers:
            for path in _iter_child_dirs(worker):
                if path.name.startswith("test_"):
                    usage_paths.append(path)
                    top_tests.append(
                        {
                            "path": path.relative_to(root).as_posix(),
                            "bytes": 0,
                            "disk_bytes": 0,
                        }
                    )
    usages = _attach_usage_totals(usage_paths, seed_totals, top_tests)
    top_tests.sort(key=lambda item: int(item["disk_bytes"]), reverse=True)
    root_usage = usages[root]
    return {
        "status": "available",
        "root": str(root),
        "session_count": len(sessions),
        "session_names": [path.name for path in sessions],
        "worker_dir_count": worker_count,
        "total_bytes": root_usage["bytes"],
        "total_disk_bytes": root_usage["disk_bytes"],
        "seed_totals": seed_totals,
        "top_test_dirs": top_tests[:10],
    }


def inventory(repo_root: Path, discovery: dict[str, Any] | None = None) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    test_files, test_discovery = resolve_test_files(repo_root, discovery)
    by_extension: dict[str, int] = {}
    for path in test_files:
        by_extension[path.suffix] = by_extension.get(path.suffix, 0) + 1
    snippets = _runner_snippets(repo_root)
    node_test_snippets = [item for item in snippets if NODE_TEST_RE.search(item["snippet"])]
    ts_loader_snippets = [item for item in snippets if TS_LOADER_RE.search(item["snippet"])]
    nested_cli_files = find_nested_cli_files(repo_root, test_files)
    settlement_seams = find_subprocess_settlement_seams(repo_root, test_files)
    nested_cli_test_counts = find_pytest_file_test_counts(repo_root, nested_cli_files)
    nested_cli_release_only_files: list[str] = []
    nested_cli_mixed_release_only_files: list[str] = []
    nested_cli_standing_files: list[str] = []
    nested_cli_standing_or_mixed_files: list[str] = []
    for item in nested_cli_test_counts:
        path = item["path"]
        release_only_count = int(item["release_only_count"])
        standing_count = int(item["standing_count"])
        if release_only_count and not standing_count:
            nested_cli_release_only_files.append(path)
        elif release_only_count and standing_count:
            nested_cli_mixed_release_only_files.append(path)
            nested_cli_standing_or_mixed_files.append(path)
        elif standing_count:
            nested_cli_standing_files.append(path)
            nested_cli_standing_or_mixed_files.append(path)
        else:
            nested_cli_standing_or_mixed_files.append(path)
    pytest_temp = _pytest_temp_footprint()
    findings: list[dict[str, Any]] = []
    if len(test_files) >= 50:
        findings.append(
            {
                "type": "many_test_files",
                "severity": "advisory",
                "message": "Standing test cost may be dominated by per-file runner startup rather than individual test cases.",
                "evidence": f"{len(test_files)} test files",
                "recommended_action": "Measure file count, runner startup, and per-file isolation before pruning tests.",
            }
        )
    if node_test_snippets and not any(
        "--experimental-test-isolation=none" in item["snippet"] for item in node_test_snippets
    ):
        findings.append(
            {
                "type": "node_test_isolation_unknown",
                "severity": "advisory",
                "message": "Node test runner commands should make isolation cost visible before test-count cleanup.",
                "evidence": "; ".join(item["path"] for item in node_test_snippets),
                "recommended_action": "Compare the standing command with an explicit shared-process or isolated runner mode, then keep the cheapest honest layer.",
            }
        )
    if (
        sum(count for ext, count in by_extension.items() if ext in TRANSPILE_EXTENSIONS)
        and ts_loader_snippets
    ):
        findings.append(
            {
                "type": "transpiler_startup_surface",
                "severity": "advisory",
                "message": "TypeScript test files plus a runtime loader can pay transpiler startup in the test runner path.",
                "evidence": f"{sum(count for ext, count in by_extension.items() if ext in TRANSPILE_EXTENSIONS)} TypeScript test files",
                "recommended_action": "Measure whether the loader is paid once per run, per worker, or per isolated file.",
            }
        )
    if nested_cli_files:
        standing_sample = ", ".join(nested_cli_standing_files[:5]) or "none"
        mixed_sample = ", ".join(nested_cli_mixed_release_only_files[:5]) or "none"
        release_only_sample = ", ".join(nested_cli_release_only_files[:5]) or "none"
        findings.append(
            {
                "type": "nested_cli_fanout",
                "severity": "advisory",
                "message": "Tests spawn nested processes inside the standing suite.",
                "evidence": (
                    f"{len(nested_cli_standing_files)} standing file(s), "
                    f"{len(nested_cli_mixed_release_only_files)} mixed release_only/standing file(s), "
                    f"{len(nested_cli_release_only_files)} all-release-only file(s); "
                    f"standing sample: {standing_sample}; "
                    f"mixed sample: {mixed_sample}; "
                    f"all-release-only sample: {release_only_sample}"
                ),
                "recommended_action": "Keep a small real-binary smoke and move repeated contract proof in-process where honest.",
            }
        )
    if pytest_temp.get("status") == "available":
        disk_bytes = int(pytest_temp.get("total_disk_bytes") or pytest_temp.get("total_bytes") or 0)
        if disk_bytes >= 1024 * 1024 * 1024:
            findings.append(
                {
                    "type": "pytest_temp_footprint",
                    "severity": "advisory",
                    "message": "The current user's pytest temp retention is carrying a multi-GB footprint.",
                    "evidence": f"{disk_bytes} allocated bytes across {pytest_temp.get('session_count')} retained session(s)",
                    "recommended_action": "Reduce duplicated repo/home fixture materialization before changing pytest retention or disabling xdist.",
                }
            )
    return {
        "repo_root": str(repo_root),
        "test_discovery": test_discovery,
        "test_file_count": len(test_files),
        "test_files_by_extension": dict(sorted(by_extension.items())),
        "runner_snippets": snippets,
        "nested_cli_file_count": len(nested_cli_files),
        "nested_cli_files": nested_cli_files,
        "nested_cli_all_release_only_file_count": len(nested_cli_release_only_files),
        "nested_cli_all_release_only_files": nested_cli_release_only_files,
        "nested_cli_mixed_release_only_file_count": len(nested_cli_mixed_release_only_files),
        "nested_cli_mixed_release_only_files": nested_cli_mixed_release_only_files,
        "nested_cli_standing_file_count": len(nested_cli_standing_files),
        "nested_cli_standing_files": nested_cli_standing_files,
        "nested_cli_release_only_file_count": len(nested_cli_release_only_files),
        "nested_cli_release_only_files": nested_cli_release_only_files,
        "nested_cli_standing_or_mixed_file_count": len(nested_cli_standing_or_mixed_files),
        "nested_cli_standing_or_mixed_files": nested_cli_standing_or_mixed_files,
        "subprocess_settlement": {
            "seam_count": len(settlement_seams),
            "deadline_counts": {
                state: sum(item["deadline"] == state for item in settlement_seams)
                for state in ("present", "absent", "unknown")
            },
            "lifecycle_counts": {
                state: sum(item["lifecycle"] == state for item in settlement_seams)
                for state in ("finite", "until_interrupted", "unknown")
            },
            "process_tree_termination_counts": {
                state: sum(item["process_tree_termination"] == state for item in settlement_seams)
                for state in ("owned", "not_owned", "unknown")
            },
            "output_bounding_counts": {
                state: sum(item["output_bounding"] == state for item in settlement_seams)
                for state in ("bounded", "unbounded", "unknown")
            },
            "seams": settlement_seams,
        },
        "pytest_temp_footprint": pytest_temp,
        "proof_path_review": (
            {
                "status": "review_recommended",
                "detail_ref": "references/proof-path-efficiency.md",
                "observed_finding_types": [finding["type"] for finding in findings],
            }
            if findings
            else None
        ),
        "findings": findings,
    }
