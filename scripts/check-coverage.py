#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import contextlib
import io
import json
import os
import runpy
import shutil
import sys
import tempfile
import trace
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_check_coverage_lib_module = import_repo_module(__file__, "scripts.check_coverage_lib")
PER_FILE_WARN_BELOW = _scripts_check_coverage_lib_module.PER_FILE_WARN_BELOW
build_per_file_floor_report = _scripts_check_coverage_lib_module.build_per_file_floor_report
exercise_control_plane_scenarios = _scripts_check_coverage_lib_module.exercise_control_plane_scenarios
exercise_install_provenance_scenarios = _scripts_check_coverage_lib_module.exercise_install_provenance_scenarios
exercise_lifecycle_scenarios = _scripts_check_coverage_lib_module.exercise_lifecycle_scenarios
exercise_support_sync_scenarios = _scripts_check_coverage_lib_module.exercise_support_sync_scenarios
exercise_upstream_release_scenarios = _scripts_check_coverage_lib_module.exercise_upstream_release_scenarios

TARGET_FILES = (
    Path("scripts/control_plane_lib.py"),
    Path("scripts/control_plane_lifecycle_lib.py"),
    Path("scripts/doctor.py"),
    Path("scripts/install_provenance_lib.py"),
    Path("scripts/install_tools.py"),
    Path("scripts/support_sync_lib.py"),
    Path("scripts/sync_support.py"),
    Path("scripts/update_tools.py"),
    Path("scripts/upstream_release_lib.py"),
)
MIN_COVERAGE = 0.60
MIN_FILE_COVERAGE = 0.85
COPY_IGNORE = shutil.ignore_patterns(
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "__pycache__",
    ".coverage",
    ".venv",
    "node_modules",
    "history",
)


class CoverageError(Exception):
    pass


def executable_lines(path: Path) -> set[int]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lines: set[int] = set()
    for node in ast.walk(tree):
        if not hasattr(node, "lineno"):
            continue
        if isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant) and isinstance(node.value.value, str):
            continue
        lines.add(int(node.lineno))
    return lines


def build_release_fixture(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "corca-ai/charness": {
                    "tag_name": "v0.1.0",
                    "html_url": "https://github.com/corca-ai/charness/releases/tag/v0.1.0",
                    "published_at": "2026-04-12T00:00:00Z",
                    "assets": [{"name": "charness"}],
                },
                "corca-ai/cautilus": {
                    "tag_name": "v1.2.3",
                    "html_url": "https://github.com/corca-ai/cautilus/releases/tag/v1.2.3",
                    "published_at": "2026-04-10T00:00:00Z",
                    "assets": [{"name": "cautilus-linux-amd64.tar.gz"}],
                },
                "vercel-labs/agent-browser": {
                    "tag_name": "v0.25.3",
                    "html_url": "https://github.com/vercel-labs/agent-browser/releases/tag/v0.25.3",
                    "published_at": "2026-04-07T02:11:00Z",
                    "assets": [{"name": "agent-browser-x86_64-unknown-linux-gnu.tar.gz"}],
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def make_fake_agent_browser(bin_dir: Path) -> None:
    script = bin_dir / "agent-browser"
    script.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'case "${1:-}" in',
                '  --version) echo "agent-browser 0.25.3" ;;',
                '  --help) echo "agent-browser help" ;;',
                '  upgrade) echo "agent-browser upgraded" ;;',
                '  *) echo "agent-browser" ;;',
                "esac",
                "",
            ]
        ),
        encoding="utf-8",
    )
    script.chmod(0o755)


def run_traced_entry(
    tracer: trace.Trace,
    script_path: Path,
    *,
    argv: list[str],
    cwd: Path,
    env_overrides: dict[str, str],
) -> None:
    old_argv = sys.argv[:]
    old_cwd = Path.cwd()
    old_env = os.environ.copy()
    os.environ.update(env_overrides)
    sys.argv = [str(script_path), *argv]
    os.chdir(cwd)
    try:
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                tracer.runctx(
                    "runpy.run_path(script_path, run_name='__main__')",
                    {"runpy": runpy, "script_path": str(script_path)},
                    {},
                )
        except SystemExit as exc:  # pragma: no branch
            code = exc.code if isinstance(exc.code, int) else 0
            if code != 0:
                raise CoverageError(f"{script_path.name} exited with {code}")
    finally:
        sys.argv = old_argv
        os.chdir(old_cwd)
        os.environ.clear()
        os.environ.update(old_env)


def run_traced_function(tracer: trace.Trace, function: object) -> None:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        tracer.runfunc(function)


def collect_counts(repo_root: Path) -> dict[Path, set[int]]:
    with tempfile.TemporaryDirectory(prefix="charness-coverage-") as tmpdir:
        tmp = Path(tmpdir)
        repo_copy = tmp / "repo"
        home_root = tmp / "home"
        bin_dir = tmp / "bin"
        release_fixture = tmp / "release-fixtures.json"

        shutil.copytree(repo_root, repo_copy, ignore=COPY_IGNORE)
        bin_dir.mkdir()
        make_fake_agent_browser(bin_dir)
        build_release_fixture(release_fixture)

        env = {
            "HOME": str(home_root),
            "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}",
            "CHARNESS_RELEASE_PROBE_FIXTURES": str(release_fixture),
        }
        tracer = trace.Trace(count=True, trace=False, ignoremods=("importlib", "encodings"))
        entries = (
            (repo_root / "charness", ["tool", "doctor", "--repo-root", str(repo_copy), "--json", "agent-browser"]),
            (repo_root / "scripts" / "doctor.py", ["--repo-root", str(repo_copy), "--json", "--write-locks", "--tool-id", "agent-browser"]),
            (repo_root / "scripts" / "sync_support.py", ["--repo-root", str(repo_copy), "--execute", "--json", "--tool-id", "agent-browser"]),
            (repo_root / "scripts" / "update_tools.py", ["--repo-root", str(repo_copy), "--execute", "--json", "--tool-id", "agent-browser"]),
            (repo_root / "scripts" / "update_tools.py", ["--repo-root", str(repo_copy), "--json", "--tool-id", "cautilus"]),
            (repo_root / "scripts" / "install_tools.py", ["--repo-root", str(repo_copy), "--execute", "--json", "--tool-id", "agent-browser"]),
            (repo_root / "scripts" / "install_tools.py", ["--repo-root", str(repo_copy), "--execute", "--json", "--tool-id", "cautilus"]),
        )
        scenario_functions = (
            exercise_control_plane_scenarios,
            exercise_install_provenance_scenarios,
            exercise_support_sync_scenarios,
            exercise_lifecycle_scenarios,
            exercise_upstream_release_scenarios,
        )
        for function in scenario_functions:
            run_traced_function(tracer, function)
        for script_path, argv in entries:
            run_traced_entry(tracer, script_path, argv=argv, cwd=repo_root, env_overrides=env)

        counts = tracer.results().counts
        aggregated: dict[Path, set[int]] = {}
        for (filename, line), hit_count in counts.items():
            if hit_count <= 0:
                continue
            path = Path(filename).resolve()
            aggregated.setdefault(path, set()).add(int(line))
        return aggregated


def summarize(
    repo_root: Path,
    counts: dict[Path, set[int]],
    *,
    min_file_coverage: float = MIN_FILE_COVERAGE,
) -> dict[str, object]:
    files: list[dict[str, object]] = []
    executed_total = 0
    possible_total = 0
    for rel_path in TARGET_FILES:
        path = (repo_root / rel_path).resolve()
        executable = executable_lines(path)
        hit_lines = executable & counts.get(path, set())
        covered = len(hit_lines)
        total = len(executable)
        coverage = covered / total if total else 1.0
        files.append(
            {
                "path": str(rel_path),
                "covered": covered,
                "total": total,
                "coverage": round(coverage, 4),
            }
        )
        executed_total += covered
        possible_total += total
    overall = executed_total / possible_total if possible_total else 1.0
    summary = {
        "schema_version": 1,
        "scope": "control-plane",
        "files": files,
        "covered": executed_total,
        "total": possible_total,
        "coverage": round(overall, 4),
    }
    summary["per_file_floor"] = build_per_file_floor_report(files, floor=min_file_coverage)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--min-coverage", type=float, default=MIN_COVERAGE)
    parser.add_argument("--min-file-coverage", type=float, default=MIN_FILE_COVERAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    summary = summarize(repo_root, collect_counts(repo_root), min_file_coverage=args.min_file_coverage)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        percent = summary["coverage"] * 100
        print(
            f"Control-plane coverage: {percent:.1f}% "
            f"({summary['covered']}/{summary['total']} executable lines)"
        )
        for item in summary["files"]:
            print(
                f"- {item['path']}: {item['coverage'] * 100:.1f}% "
                f"({item['covered']}/{item['total']})"
            )
        floor_report = summary["per_file_floor"]
        assert isinstance(floor_report, dict)
        violations = floor_report["violations"]
        warn_band = floor_report["warn_band"]
        assert isinstance(violations, list)
        assert isinstance(warn_band, list)
        print(
            "Per-file floor: "
            f"{len(violations)} below {args.min_file_coverage * 100:.1f}%, "
            f"{len(warn_band)} in {args.min_file_coverage * 100:.1f}-"
            f"{PER_FILE_WARN_BELOW * 100:.1f}% warn band"
        )

    if summary["coverage"] < args.min_coverage:
        raise CoverageError(
            f"control-plane coverage {summary['coverage']:.3f} is below required floor {args.min_coverage:.3f}"
        )
    floor_report = summary["per_file_floor"]
    assert isinstance(floor_report, dict)
    violations = [
        item
        for item in floor_report["violations"]
        if isinstance(item, dict) and float(item["coverage"]) < args.min_file_coverage
    ]
    if violations:
        details = ", ".join(f"{item['path']}={float(item['coverage']) * 100:.1f}%" for item in violations)
        raise CoverageError(
            f"control-plane per-file coverage below required floor {args.min_file_coverage:.3f}: {details}"
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CoverageError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
