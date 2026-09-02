"""Helpers for coverage-aware Cosmic Ray sample selection."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections.abc import Sequence
from pathlib import Path

import scripts.mutation.coverage_instrumentation_policy as _policy
from scripts.mutation.mutation_line_coverage_lib import (
    covered_statement_spans as _covered_statement_spans,
)
from scripts.mutation.mutation_line_coverage_lib import (
    mutation_line_is_covered as _mutation_line_is_covered,
)


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core.subprocess_guard import run_monitored_phase, run_process  # noqa: E402
from scripts.runtime_bootstrap import (  # noqa: E402
    configure_runtime_environment,
    import_repo_module,
)

DEFAULT_SAMPLE_COVERAGE_JSON = Path("reports/mutation/sample-coverage.json")

_sampling_selection = import_repo_module(__file__, "scripts.mutation.mutation_sampling_selection")
stable_hash = _sampling_selection.stable_hash
deterministic_sample = _sampling_selection.deterministic_sample
read_test_command = _sampling_selection.read_test_command
_coverage_relative_path = _sampling_selection._coverage_relative_path
load_line_contexts = _sampling_selection.load_line_contexts
pytest_nodeid_from_coverage_context = _sampling_selection.pytest_nodeid_from_coverage_context
select_test_nodeids = _sampling_selection.select_test_nodeids
file_test_nodeids = _sampling_selection.file_test_nodeids
mutation_workload = _sampling_selection.mutation_workload
test_nodeid_count = _sampling_selection.test_nodeid_count
select_budgeted_sample = _sampling_selection.select_budgeted_sample


#: The instrumentation policy moved to `coverage_instrumentation_policy` when
#: this file crossed its length cap (S6b-1). Re-exported because callers and
#: tests -- and the producer's own identity pin -- bind these at THIS address.
STANDING_RUNNER_HELPER_FLAG_PREFIX = _policy.STANDING_RUNNER_HELPER_FLAG_PREFIX
PYTEST_KIND = _policy.PYTEST_KIND
STANDING_RUNNER_KIND = _policy.STANDING_RUNNER_KIND
INSTRUMENTABLE_COMMAND_REFUSAL = _policy.INSTRUMENTABLE_COMMAND_REFUSAL
classify_instrumentable_command = _policy.classify_instrumentable_command
is_standing_pytest_runner_command = _policy.is_standing_pytest_runner_command
is_instrumentable_pytest_command = _policy.is_instrumentable_pytest_command
coverage_run_command = _policy.coverage_run_command


class CoverageCommandError(RuntimeError):
    def __init__(self, returncode: int, command, stdout: str, stderr: str):  # noqa: ANN001
        super().__init__(f"coverage test command failed with exit {returncode}")
        self.returncode = returncode
        self.command = command
        self.output = stdout
        self.stderr = stderr


def _sitecustomize_source(*, dynamic_context: bool) -> str:
    """sitecustomize that always enables subprocess coverage capture.

    The per-test `switch_context` block is only emitted for the faithful
    `dynamic_context` probe; the plain producer (the changed-line verdict only
    needs executed-vs-missing lines) drops it, which is what collapses the
    coverage JSON from a multi-GB per-test export down to a small artifact.
    `coverage.process_startup()` stays in both modes so subprocess-executed
    lines are still measured (no new subprocess blind spot vs the faithful probe).

    The size is quoted as a magnitude, not a constant, because it TRACKS THE
    SUITE and this file used to name one figure as if it were fixed. It said
    ~1.34 GB; the 2026-08-22 measurement on a larger suite found 8.22 GB against
    12.26 MB for the same coverage data (#696). Both were true when taken. A
    reader comparing two hardcoded numbers two files apart on one code path has
    no way to tell that, so the current measurement lives in the probe artifact
    and this docstring names the shape instead of a stale scalar.
    """
    lines = ["import os", "import coverage", "", "coverage.process_startup()"]
    if dynamic_context:
        lines += [
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
        ]
    return "\n".join(lines) + "\n"


def coverage_runtime_paths(coverage_json: Path, *, repo_root: Path) -> tuple[Path, Path, Path]:
    """Return the isolated runtime files owned by one coverage report.

    The broad pytest producer and the incremental changed-line producer can run
    in the same quality batch. They write different JSON reports, but the old
    fixed names below made them share one coverage database, rcfile, and
    ``sitecustomize`` directory. The last writer then silently changed the
    other producer's input, turning parallel execution into a nondeterministic
    verdict. Namespace every runtime file by its report stem so parallel
    producers have disjoint write surfaces while keeping their public JSON
    outputs unchanged.
    """
    runtime = configure_runtime_environment(repo_root)
    repo_key = hashlib.sha256(str(repo_root.resolve()).encode("utf-8")).hexdigest()[:16]
    runtime_dir = (
        Path(runtime["CHARNESS_RUNTIME_ROOT"]) / "coverage" / f"{repo_key}-{coverage_json.stem}"
    )
    runtime_dir.mkdir(parents=True, exist_ok=True)
    prefix = f".{coverage_json.stem}"
    return (
        runtime_dir / f"{prefix}.mutation-coverage",
        runtime_dir / f"{prefix}.mutation-coveragerc",
        runtime_dir / f"{prefix}.mutation-sitecustomize",
    )


def _write_coverage_config(
    repo_root: Path, coverage_json: Path, *, dynamic_context: bool
) -> tuple[Path, Path, Path]:
    coverage_json.parent.mkdir(parents=True, exist_ok=True)
    data_file, rcfile, sitecustomize_dir = coverage_runtime_paths(
        coverage_json, repo_root=repo_root
    )
    sitecustomize_dir.mkdir(parents=True, exist_ok=True)
    sitecustomize_dir.joinpath("sitecustomize.py").write_text(
        _sitecustomize_source(dynamic_context=dynamic_context), encoding="utf-8"
    )
    rc_lines = ["[run]", f"data_file = {data_file}", f"source = {repo_root}"]
    if dynamic_context:
        rc_lines += ["dynamic_context = test_function", "disable_warnings = dynamic-conflict"]
    rc_lines += ["parallel = True", ""]
    rcfile.write_text("\n".join(rc_lines), encoding="utf-8")
    return data_file, rcfile, sitecustomize_dir


def coverage_subprocess_env(
    rcfile: Path, sitecustomize_dir: Path, *, data_file: Path | None = None
) -> dict[str, str]:
    """Environment that turns on coverage in pytest and its subprocesses."""
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
    # A parent quality run may already have a default COVERAGE_FILE. Letting that
    # leak into a subprocess-started coverage session sends its data to the parent
    # file instead of this report's namespaced database, so the child disappears
    # from the combined JSON. The report owner is the only honest data-file target.
    if data_file is not None:
        env["COVERAGE_FILE"] = str(data_file)
    return env


def clear_stale_coverage_data(data_file: Path) -> None:
    if data_file.exists():
        data_file.unlink()
    for stale_shard in data_file.parent.glob(data_file.name + ".*"):
        stale_shard.unlink()


def combine_and_export_coverage(
    repo_root: Path,
    rcfile: Path,
    data_file: Path,
    coverage_json: Path,
    env: dict[str, str],
    *,
    show_contexts: bool,
    include_paths: Sequence[str] | None = None,
) -> None:
    # stdout=DEVNULL: coverage's "Combined N files" / "Wrote JSON report" info
    # lines would otherwise pollute the release producer's YAML payload. Errors
    # still surface on stderr.
    result = run_process(
        [
            sys.executable,
            "-m",
            "coverage",
            "combine",
            "--rcfile",
            str(rcfile),
            "--data-file",
            str(data_file),
            str(data_file.parent),
        ],
        cwd=repo_root,
        timeout_seconds=None,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or f"coverage combine failed with exit {result.returncode}"
        )
    json_command = [
        sys.executable,
        "-m",
        "coverage",
        "json",
        "--rcfile",
        str(rcfile),
        *(["--show-contexts"] if show_contexts else []),
        "--data-file",
        str(data_file),
        "-o",
        str(coverage_json),
    ]
    paths = [path for path in include_paths or () if path]
    if paths:
        # coverage.py treats --include as a single-valued option. Repeating it
        # silently keeps only the last path, which would make earlier mapped
        # changed files look uncovered to the consumer.
        json_command.extend(["--include", ",".join(paths)])
    result = run_process(json_command, cwd=repo_root, timeout_seconds=None, env=env)
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or f"coverage json failed with exit {result.returncode}"
        )


def prepare_plain_coverage(
    repo_root: Path, coverage_json: Path
) -> tuple[Path, Path, dict[str, str]]:
    """Set up a plain (no `dynamic_context`) coverage run and return
    ``(data_file, rcfile, env)`` so a caller can run an arbitrary instrumented
    command (for example the release-focused pytest) and then call
    :func:`combine_and_export_coverage` with ``show_contexts=False``."""
    data_file, rcfile, sitecustomize_dir = _write_coverage_config(
        repo_root, coverage_json, dynamic_context=False
    )
    clear_stale_coverage_data(data_file)
    return (
        data_file,
        rcfile,
        coverage_subprocess_env(rcfile, sitecustomize_dir, data_file=data_file),
    )


def run_test_coverage(
    repo_root: Path, test_command: str, coverage_json: Path, *, dynamic_context: bool = True
) -> None:
    data_file, rcfile, sitecustomize_dir = _write_coverage_config(
        repo_root, coverage_json, dynamic_context=dynamic_context
    )
    clear_stale_coverage_data(data_file)
    command = coverage_run_command(test_command, data_file)
    env = coverage_subprocess_env(rcfile, sitecustomize_dir, data_file=data_file)
    # Captured (not streamed) so a failure can be inspected for failing nodeids
    # by the caller; teed back to stdout/stderr to preserve CI step-log fidelity.
    outcome = run_monitored_phase(
        command,
        cwd=repo_root,
        phase="coverage-tests",
        timeout_seconds=None,
        env=env,
        capture=True,
    )
    sys.stdout.write(outcome.stdout)
    sys.stderr.write(outcome.stderr)
    if outcome.returncode != 0:
        raise CoverageCommandError(outcome.returncode, command, outcome.stdout, outcome.stderr)
    combine_and_export_coverage(
        repo_root, rcfile, data_file, coverage_json, env, show_contexts=dynamic_context
    )


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


#: `meta` is the FIRST key coverage.py writes, so this is decidable from a small
#: prefix -- which is the entire point, since the file this asks about may be
#: multiple gigabytes and deciding it by parsing is the cost being avoided.
_SHOW_CONTEXTS_RE = re.compile(rb'"show_contexts"\s*:\s*(true|false)')
_META_PREFIX_BYTES = 4096


def coverage_is_context_bearing(coverage_json: Path) -> bool | None:
    """Whether a coverage JSON carries per-test `contexts`, read from its header.

    ``True``/``False`` when ``meta.show_contexts`` is readable in the first few KB,
    and ``None`` when it is not -- an old export, a truncated file, an unexpected
    key order. Callers must treat ``None`` as "unknown, proceed as before": this
    exists to catch a specific known-bad state cheaply, not to gate on an absence.

    Why a caller wants to know: a context-bearing export of this repo measured
    8.22 GB against 12.26 MB for the same data, and 20.44 GiB of peak RSS to load.
    A consumer that needs only executed/missing lines can detect that it is about
    to pay for a corpus some OTHER writer left at a shared path, and decline,
    instead of discovering it as an out-of-memory crash on a proof surface.
    """
    try:
        with coverage_json.open("rb") as handle:
            head = handle.read(_META_PREFIX_BYTES)
    except OSError:
        return None
    match = _SHOW_CONTEXTS_RE.search(head)
    return None if match is None else match.group(1) == b"true"


def load_file_statement_lines(
    repo_root: Path, coverage_json: Path
) -> dict[str, tuple[set[int], set[int]]]:
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

        from scripts.mutation.filter_cosmic_ray_mutants import (
            is_trivial_entry_guard_mutation,
            should_skip_mutation,
            source_line,
        )
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
    result = run_process(
        ["cosmic-ray", "init", str(probe_config), str(probe_session)],
        cwd=repo_root,
        timeout_seconds=None,
    )
    if result.returncode != 0:
        raise SystemExit(
            "cosmic-ray init failed during mutation-line sampling\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    statement_spans = {
        path: _covered_statement_spans(repo_root / path, covered_lines.get(path, set()))
        for path in candidates
    }
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
                line = source_line(repo_root, mutation.module_path, line_number)
                if is_trivial_entry_guard_mutation(line, getattr(mutation, "operator_name", "")):
                    continue
                stats[module_path]["mutable"] += 1
                if _mutation_line_is_covered(
                    int(line_number),
                    covered_lines.get(module_path, set()),
                    statement_spans.get(module_path, []),
                ):
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
