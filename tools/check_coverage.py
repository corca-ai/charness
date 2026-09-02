#!/usr/bin/env python3

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import runpy
import shutil
import site
import sys
import sysconfig
import tempfile
import trace
from pathlib import Path
from unittest import mock

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

_scripts_check_coverage_lib_module = import_repo_module(__file__, "scripts.gates.check_coverage_lib")
_tools_check_coverage_extra_lib_module = import_repo_module(__file__, "tools.check_coverage_extra_lib")
_scripts_mutation_line_coverage_lib_module = import_repo_module(__file__, "scripts.mutation.mutation_line_coverage_lib")
PER_FILE_WARN_BELOW = _scripts_check_coverage_lib_module.PER_FILE_WARN_BELOW
PER_FILE_MIN_COVERAGE = _scripts_check_coverage_lib_module.PER_FILE_MIN_COVERAGE
build_per_file_floor_report = _scripts_check_coverage_lib_module.build_per_file_floor_report
exercise_control_plane_scenarios = _scripts_check_coverage_lib_module.exercise_control_plane_scenarios
exercise_install_provenance_scenarios = _scripts_check_coverage_lib_module.exercise_install_provenance_scenarios
exercise_lifecycle_scenarios = _scripts_check_coverage_lib_module.exercise_lifecycle_scenarios
exercise_support_sync_scenarios = _scripts_check_coverage_lib_module.exercise_support_sync_scenarios
exercise_upstream_release_scenarios = _scripts_check_coverage_lib_module.exercise_upstream_release_scenarios
exercise_control_plane_helper_scenarios = _tools_check_coverage_extra_lib_module.exercise_control_plane_helper_scenarios
exercise_install_provenance_helper_scenarios = _tools_check_coverage_extra_lib_module.exercise_install_provenance_helper_scenarios
exercise_install_tool_helper_scenarios = _tools_check_coverage_extra_lib_module.exercise_install_tool_helper_scenarios
exercise_support_sync_helper_scenarios = _tools_check_coverage_extra_lib_module.exercise_support_sync_helper_scenarios
exercise_upstream_release_helper_scenarios = _tools_check_coverage_extra_lib_module.exercise_upstream_release_helper_scenarios
executable_statement_lines = _scripts_mutation_line_coverage_lib_module.executable_statement_lines

# A fixed whole-repo target list, intentionally not a changed-file subset. The
# per-file PER_FILE_MIN_COVERAGE floor is safe as a hard blocker only because of
# this: gating a whole-file floor on a changed subset would false-fire on a
# well-tested change to a partially-covered file (the #208 mutation-gate trap).
# If this is ever narrowed to changed files, scope the floor to changed lines as
# scripts/mutation/mutation_changed_files_lib.py:classify_changed_line_scope_gap does.
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
MIN_FILE_COVERAGE = PER_FILE_MIN_COVERAGE
COPY_IGNORE_NAMES = (
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "__pycache__",
    ".coverage",
    # Rust-crate corpus: contains deliberately malformed sources and dangling
    # symlinks that shutil.copytree cannot materialize; coverage never
    # measures it.
    "native",
    ".charness",
    "charness-artifacts",
    ".venv",
    "node_modules",
    "reports",
    "history",
)
COPY_IGNORE = shutil.ignore_patterns(*COPY_IGNORE_NAMES)


class CoverageError(Exception):
    pass


def python_runtime_ignoredirs(repo_root: Path | None = None) -> tuple[str, ...]:
    paths: set[str] = set()
    for key in ("stdlib", "platstdlib", "purelib", "platlib"):
        raw = sysconfig.get_paths().get(key)
        if raw:
            paths.add(os.path.normpath(raw))
    for getter in (site.getusersitepackages, site.getsitepackages):
        try:
            raw = getter()
        except Exception:
            continue
        if isinstance(raw, str):
            paths.add(os.path.normpath(raw))
        else:
            paths.update(os.path.normpath(path) for path in raw)
    if repo_root is not None:
        resolved_repo_root = repo_root.resolve()
        paths = {
            path
            for path in paths
            if os.path.commonpath((path, str(resolved_repo_root))) != path
        }
    return tuple(sorted(paths))


def executable_lines(path: Path) -> set[int]:
    return executable_statement_lines(path)


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


def build_support_sync_fixture(path: Path, fixture_root: Path) -> None:
    mappings: dict[str, str] = {}
    for repo, skill_id in {
        "vercel-labs/agent-browser": "agent-browser",
    }.items():
        upstream_root = fixture_root / skill_id
        skill_root = upstream_root / "skills" / skill_id
        skill_root.mkdir(parents=True, exist_ok=True)
        skill_root.joinpath("SKILL.md").write_text(
            f"---\nname: {skill_id}\ndescription: \"coverage fixture\"\n---\n\n# {skill_id}\n",
            encoding="utf-8",
        )
        mappings[f"{repo}@main"] = str(upstream_root)
    path.write_text(json.dumps(mappings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def make_fake_npm(bin_dir: Path) -> None:
    script = bin_dir / "npm"
    script.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'if [[ "${1:-}" == "install" ]]; then',
                '  echo "npm fixture installed ${*: -1}"',
                "  exit 0",
                "fi",
                'echo "npm fixture"',
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


def exercise_doctor_scenarios() -> None:
    import scripts.doctor as doctor

    manifest = {"tool_id": "demo", "version_expectation": {"constraint": "local"}}
    payload = {
        "tool_id": "demo",
        "doctor_status": "missing",
        "support_state": "integration-only",
        "doctor_disposition": "blocking-install-needed",
        "previous_lock_present": False,
    }
    with mock.patch.object(doctor, "load_capabilities", return_value=[manifest]):
        with mock.patch.object(doctor, "inspect_manifest", return_value=payload):
            with mock.patch.object(sys, "argv", ["doctor.py", "--repo-root", "."]):
                doctor.main()


def collect_counts(repo_root: Path) -> dict[Path, set[int]]:
    with tempfile.TemporaryDirectory(prefix="charness-coverage-") as tmpdir:
        tmp = Path(tmpdir)
        repo_copy = tmp / "repo"
        home_root = tmp / "home"
        plugin_root = tmp / "plugin"
        bin_dir = tmp / "bin"
        release_fixture = tmp / "release-fixtures.json"
        support_fixture = tmp / "support-fixtures.json"
        support_fixture_root = tmp / "support-fixtures"

        shutil.copytree(repo_root, repo_copy, ignore=COPY_IGNORE)
        bin_dir.mkdir()
        make_fake_agent_browser(bin_dir)
        make_fake_npm(bin_dir)
        build_release_fixture(release_fixture)
        build_support_sync_fixture(support_fixture, support_fixture_root)

        env = {
            "HOME": str(home_root),
            "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}",
            "CHARNESS_RELEASE_PROBE_FIXTURES": str(release_fixture),
            "CHARNESS_SUPPORT_SYNC_FIXTURES": str(support_fixture),
            "CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS": "1",
        }
        tracer = trace.Trace(
            count=True,
            trace=False,
            ignoremods=("importlib", "encodings"),
            ignoredirs=python_runtime_ignoredirs(repo_root),
        )
        entries = (
            (repo_root / "charness", ["tool", "doctor", "--repo-root", str(repo_copy), "agent-browser"]),
            (repo_root / "scripts" / "doctor.py", ["--repo-root", str(repo_copy), "--write-locks", "--tool-id", "agent-browser"]),
            (
                repo_root / "scripts" / "sync_support.py",
                ["--repo-root", str(repo_copy), "--plugin-root", str(plugin_root), "--execute", "--tool-id", "agent-browser"],
            ),
            (
                repo_root / "scripts" / "sync_support.py",
                ["--repo-root", str(repo_copy), "--execute", "--tool-id", "agent-browser"],
            ),
            (repo_root / "scripts" / "update_tools.py", ["--repo-root", str(repo_copy), "--execute", "--tool-id", "agent-browser"]),
            (repo_root / "scripts" / "install_tools.py", ["--repo-root", str(repo_copy), "--execute", "--tool-id", "agent-browser"]),
        )
        scenario_functions = (
            exercise_control_plane_scenarios,
            exercise_control_plane_helper_scenarios,
            exercise_doctor_scenarios,
            exercise_install_provenance_scenarios,
            exercise_install_provenance_helper_scenarios,
            exercise_install_tool_helper_scenarios,
            exercise_support_sync_scenarios,
            exercise_support_sync_helper_scenarios,
            exercise_lifecycle_scenarios,
            exercise_upstream_release_scenarios,
            exercise_upstream_release_helper_scenarios,
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
                # `covered/total if total else 1.0` reports a perfect score for a
                # file with nothing to measure — a missing file, an unparseable
                # one, an empty one. 1.0 there is not a measurement (E5).
                "measured": bool(total),
            }
        )
        executed_total += covered
        possible_total += total
    overall = executed_total / possible_total if possible_total else 1.0
    unmeasured = [item["path"] for item in files if not item["measured"]]
    summary = {
        "schema_version": 1,
        "scope": "control-plane",
        # Whether a number was MEASURED is part of the number. Zero observations
        # produced `coverage: 1.0, covered: 0, total: 0` — indistinguishable from
        # a fully covered surface, on the gate that reports test confidence.
        "measurement_scope": "evaluated" if possible_total else "empty",
        "unmeasured_files": unmeasured,
        "files": files,
        "covered": executed_total,
        "total": possible_total,
        "coverage": round(overall, 4) if possible_total else None,
    }
    summary["per_file_floor"] = build_per_file_floor_report(files, floor=min_file_coverage)
    return summary


def coverage_report(summary: dict[str, object]) -> dict[str, object]:
    """The emitted document: the summary, plus the caveat only the text arm carried.

    Output is unconditionally YAML, so the UNESTABLISHED reading has to live in the
    payload. `per_file_floor` already reports `status`/`files_evaluated`; what the
    dropped renderer added was the instruction not to read an empty floor
    comparison as a passing one — the whole reason that arm exists (#465).

    Keyed on the evaluated COUNT rather than on `measurement_scope`, so a partial
    payload fails CLOSED onto the caveat instead of taking the green numeric arm.

    Deliberately NOT an exit-code change: `main` already refuses when nothing was
    measured at all (`summary["coverage"] is None` -> CoverageError), and turning
    `status == "unestablished"` into a refusal is a gate-contract change that
    belongs to whoever narrows `TARGET_FILES`, not to this repair.
    """
    payload = dict(summary)
    floor_report = summary.get("per_file_floor")
    if isinstance(floor_report, dict) and not floor_report.get("files_evaluated"):
        payload["per_file_floor_caveat"] = (
            "UNESTABLISHED — zero files reached the floor comparison "
            f"(received {floor_report.get('files_received', 'an unrecorded number of')}; "
            "the rest were unmeasured or below the statement threshold), so the floor was "
            "not enforced over anything. Read this as a missing measurement, not a passing one."
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--min-coverage", type=float, default=MIN_COVERAGE)
    parser.add_argument("--min-file-coverage", type=float, default=MIN_FILE_COVERAGE)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    summary = summarize(repo_root, collect_counts(repo_root), min_file_coverage=args.min_file_coverage)
    # Emitted BEFORE the refusals below, exactly where the payload was emitted
    # before: a run that refuses still shows the measurement it refused on.
    emit_yaml(coverage_report(summary))
    if summary["coverage"] is None:
        # Nothing was measured. Refuse LEGIBLY: reaching the comparison below
        # with `None` raised a bare TypeError traceback instead of this gate's
        # own error, and returning 1.0 (the pre-fix behavior) reported a perfect
        # score over zero observations (E5).
        raise CoverageError(
            "control-plane coverage was never measured: "
            f"{len(summary['unmeasured_files'])} target file(s) yielded zero executable lines "
            f"({', '.join(summary['unmeasured_files']) or 'no target files configured'}). "
            "A coverage number cannot be reported over an empty scope."
        )
    # The per-file lines, the exempt-population line and the unmeasured line that
    # used to print here are every one of them a projection of `files`,
    # `per_file_floor.exempt_below_floor` and `unmeasured_files` in the payload
    # above, which now rides on EVERY run rather than on an opt-in flag.
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
