from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any


def _load_discovery_lib() -> Any:
    module_path = Path(__file__).resolve().with_name("standing_gate_discovery_lib.py")
    spec = importlib.util.spec_from_file_location("standing_gate_discovery_lib", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_DISCOVERY = _load_discovery_lib()
discover_surfaces = _DISCOVERY.discover_surfaces
iter_snippets = _DISCOVERY.iter_snippets

IGNORED_DIRS = {".git", ".hg", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv", "node_modules", "vendor"}
TEST_FILE_PATTERNS = (
    "test_*.py",
    "*_test.py",
    "*.test.js",
    "*.test.jsx",
    "*.test.ts",
    "*.test.tsx",
    "*.spec.js",
    "*.spec.jsx",
    "*.spec.ts",
    "*.spec.tsx",
)
TRANSPILE_EXTENSIONS = {".ts", ".tsx"}
NESTED_CLI_RE = re.compile(
    r"\b(subprocess\.(?:run|check_call|check_output|Popen)|spawnSync|execFileSync|execSync|spawn\(|execa\()"
)
NODE_TEST_RE = re.compile(r"(?:^|\s)node\b[^\n]*(?:^|\s)--test(?:\s|$)")
TS_LOADER_RE = re.compile(r"\b(tsx|ts-node|swc-node|esbuild-register)\b")


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def _test_files(repo_root: Path) -> list[Path]:
    files: dict[Path, None] = {}
    for pattern in TEST_FILE_PATTERNS:
        for path in repo_root.rglob(pattern):
            if path.is_file() and not _is_ignored(path.relative_to(repo_root)):
                files[path] = None
    return sorted(files)


def _nested_cli_files(repo_root: Path, test_files: list[Path]) -> list[str]:
    matches: list[str] = []
    for path in test_files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if NESTED_CLI_RE.search(text):
            matches.append(path.relative_to(repo_root).as_posix())
    return matches


def _runner_snippets(repo_root: Path) -> list[dict[str, str]]:
    surfaces = discover_surfaces(repo_root)
    snippets = [item for item in iter_snippets(surfaces) if any(token in item["snippet"] for token in ("pytest", "node --test", "vitest", "jest", "cargo test", "go test"))]
    package_path = repo_root / "package.json"
    if package_path.is_file():
        payload = json.loads(package_path.read_text(encoding="utf-8"))
        scripts = payload.get("scripts", {}) if isinstance(payload, dict) else {}
        if isinstance(scripts, dict):
            for name, command in scripts.items():
                if isinstance(name, str) and isinstance(command, str) and ("test" in name or NODE_TEST_RE.search(command)):
                    snippets.append({"path": "package.json", "origin": f"script:{name}", "snippet": command})
    return snippets


def inventory(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    test_files = _test_files(repo_root)
    by_extension: dict[str, int] = {}
    for path in test_files:
        by_extension[path.suffix] = by_extension.get(path.suffix, 0) + 1
    snippets = _runner_snippets(repo_root)
    node_test_snippets = [item for item in snippets if NODE_TEST_RE.search(item["snippet"])]
    ts_loader_snippets = [item for item in snippets if TS_LOADER_RE.search(item["snippet"])]
    nested_cli_files = _nested_cli_files(repo_root, test_files)
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
    if node_test_snippets and not any("--experimental-test-isolation=none" in item["snippet"] for item in node_test_snippets):
        findings.append(
            {
                "type": "node_test_isolation_unknown",
                "severity": "advisory",
                "message": "Node test runner commands should make isolation cost visible before test-count cleanup.",
                "evidence": "; ".join(item["path"] for item in node_test_snippets),
                "recommended_action": "Compare the standing command with an explicit shared-process or isolated runner mode, then keep the cheapest honest layer.",
            }
        )
    if sum(count for ext, count in by_extension.items() if ext in TRANSPILE_EXTENSIONS) and ts_loader_snippets:
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
        findings.append(
            {
                "type": "nested_cli_fanout",
                "severity": "advisory",
                "message": "Tests spawn nested processes inside the standing suite.",
                "evidence": ", ".join(nested_cli_files[:10]),
                "recommended_action": "Keep a small real-binary smoke and move repeated contract proof in-process where honest.",
            }
        )
    return {
        "repo_root": str(repo_root),
        "test_file_count": len(test_files),
        "test_files_by_extension": dict(sorted(by_extension.items())),
        "runner_snippets": snippets,
        "nested_cli_file_count": len(nested_cli_files),
        "nested_cli_files": nested_cli_files,
        "findings": findings,
    }
