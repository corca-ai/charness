#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


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

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process
_quality_universes = import_repo_module(__file__, "scripts.adapters.quality_universes_lib")
_quality_adapter = import_repo_module(__file__, "scripts.adapters.quality_adapter_lib")
DEFAULT_UNIVERSES = _quality_universes.DEFAULT_UNIVERSES
Universe = _quality_universes.Universe
matching_files = _quality_universes.matching_files
refuse_if_declared_and_empty = _quality_universes.refuse_if_declared_and_empty
resolve_universe = _quality_universes.resolve_universe
load_quality_adapter = _quality_adapter.load_quality_adapter

try:
    from scripts.core.repo_file_listing import iter_repo_files
except ModuleNotFoundError:
    from scripts.core.repo_file_listing import iter_repo_files

IGNORED_DIRS = {
    ".artifacts",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "evals",
    "node_modules",
    "plugins",
}
DEFAULT_MAX_RATIO = 1.0
SUPPORTED_ENGINES = ("auto", "splitlines", "tokei")
SURFACE_BUCKETS = (
    "python",
    "python-shebang",
    "shell",
    "rust",
    "rust-tests",
    "tests-python",
)
TOKEI_TYPES = "Python,Shell,Rust"
SKIPPED_PYTHON_REASON = "unreadable-python-source"


class RatioError(Exception):
    pass


class TokeiUnavailableError(RuntimeError):
    pass


def _relative_parts(path: Path, repo_root: Path) -> tuple[str, ...]:
    return path.relative_to(repo_root).parts


def _is_native_fixture(relative_parts: tuple[str, ...]) -> bool:
    return (
        len(relative_parts) >= 3
        and relative_parts[0] == "native"
        and relative_parts[2] == "fixtures"
    )


def _is_ignored_source_path(relative_parts: tuple[str, ...]) -> bool:
    return any(part in IGNORED_DIRS for part in relative_parts[:-1]) or _is_native_fixture(
        relative_parts
    )


def _is_python_shebang(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8") as source:
            first_line = source.readline().rstrip("\n\r")
    except (OSError, UnicodeDecodeError):
        return False
    if not first_line.startswith("#!"):
        return False
    interpreter_parts = first_line[2:].strip().split()
    if not interpreter_parts:
        return False
    interpreter = interpreter_parts[0]
    if Path(interpreter).name == "env":
        interpreter = next((part for part in interpreter_parts[1:] if not part.startswith("-")), "")
    interpreter_name = Path(interpreter).name.lower()
    version = interpreter_name.removeprefix("python")
    return interpreter_name.startswith("python") and (
        not version or version.replace(".", "").isdigit()
    )


def _resolved_test_universe(
    repo_root: Path, *, require_git: bool = False
) -> tuple[Universe, list[Path]]:
    adapter = load_quality_adapter(repo_root)
    if adapter.get("valid") is False:
        errors = "; ".join(str(error) for error in adapter.get("errors", []))
        raise SystemExit(
            "check-test-production-ratio: quality adapter is invalid"
            f"{f': {errors}' if errors else '.'}"
        )
    universe = resolve_universe(
        adapter,
        "test_roots",
        default=DEFAULT_UNIVERSES["test_roots"],
    )
    try:
        files = matching_files(repo_root, universe, require_git=require_git)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
    refusal = refuse_if_declared_and_empty(universe, files, "check-test-production-ratio")
    if refusal is not None:
        raise SystemExit(refusal)
    return universe, files


def _surface_files(
    repo_root: Path,
    *,
    require_git: bool = False,
    test_paths: set[Path] | None = None,
) -> dict[str, list[Path]]:
    """Return the one shared file inventory used by both line-counting engines.

    Python keeps the historical repository listing, including non-ignored
    untracked files. The newly admitted extensionless, shell, and Rust surfaces
    use tracked files when Git is available. YAML/JSON/TOML are intentionally
    absent: they are policy/configuration data, not executable source. Native
    crate fixtures are also absent in every bucket, including their Python files.
    """

    if test_paths is None:
        _test_universe, test_files = _resolved_test_universe(repo_root, require_git=require_git)
        test_paths = set(test_files)
    all_files = iter_repo_files(repo_root, include_untracked=True, require_git=require_git)
    tracked_files = iter_repo_files(repo_root, include_untracked=False, require_git=require_git)

    source_python: list[Path] = []
    test_python: list[Path] = []
    for path in all_files:
        relative_parts = _relative_parts(path, repo_root)
        if path.suffix == ".py":
            if path in test_paths:
                test_python.append(path)
            elif not _is_ignored_source_path(relative_parts):
                source_python.append(path)

    surface: dict[str, list[Path]] = {
        "python": sorted(source_python),
        "python-shebang": [],
        "shell": [],
        "rust": [],
        "rust-tests": [],
        "tests-python": sorted(test_python),
    }
    for path in tracked_files:
        relative_parts = _relative_parts(path, repo_root)
        if _is_native_fixture(relative_parts):
            continue
        if (
            len(relative_parts) >= 4
            and relative_parts[0] == "native"
            and relative_parts[2] == "tests"
            and path.suffix == ".rs"
        ):
            surface["rust-tests"].append(path)
            continue
        if _is_ignored_source_path(relative_parts):
            continue
        if path.suffix == "" and _is_python_shebang(path):
            surface["python-shebang"].append(path)
        if path.suffix == ".sh" or ".githooks" in relative_parts[:-1]:
            surface["shell"].append(path)
        if (
            len(relative_parts) >= 4
            and relative_parts[0] == "native"
            and relative_parts[2] == "src"
            and path.suffix == ".rs"
        ) or (
            len(relative_parts) == 3 and relative_parts[0] == "native" and path.name == "build.rs"
        ):
            surface["rust"].append(path)
    return {bucket: sorted(paths) for bucket, paths in surface.items()}


def _surface_file_names(
    surface_files: dict[str, list[Path]], repo_root: Path
) -> dict[str, list[str]]:
    return {
        bucket: [path.relative_to(repo_root).as_posix() for path in paths]
        for bucket, paths in surface_files.items()
    }


def count_lines(paths: list[Path], *, skipped_paths: list[Path] | None = None) -> int:
    lines = 0
    for path in paths:
        try:
            contents = path.read_text(encoding="utf-8")
            if "\x00" in contents:
                raise ValueError("Python source contains a null byte")
            lines += len(contents.splitlines())
        except (OSError, UnicodeDecodeError, ValueError):
            if skipped_paths is not None:
                skipped_paths.append(path)
    return lines


def _splitlines_summary(
    repo_root: Path, *, require_git: bool = False, test_paths: set[Path] | None = None
) -> dict[str, object]:
    surface_files = _surface_files(repo_root, require_git=require_git, test_paths=test_paths)
    skipped_paths: list[Path] = []
    line_counts = {
        bucket: count_lines(paths, skipped_paths=skipped_paths)
        for bucket, paths in surface_files.items()
    }
    source_lines = sum(line_counts[bucket] for bucket in SURFACE_BUCKETS[:4])
    test_lines = sum(line_counts[bucket] for bucket in SURFACE_BUCKETS[4:])
    return {
        "source_lines": source_lines,
        "test_lines": test_lines,
        "source_file_count": sum(len(surface_files[bucket]) for bucket in SURFACE_BUCKETS[:4]),
        "test_file_count": sum(len(surface_files[bucket]) for bucket in SURFACE_BUCKETS[4:]),
        "surface_breakdown": line_counts,
        "surface_file_buckets": _surface_file_names(surface_files, repo_root),
        "skipped_paths": sorted(path.relative_to(repo_root).as_posix() for path in skipped_paths),
    }


def _ensure_tokei_available() -> None:
    if shutil.which("tokei") is None:
        raise TokeiUnavailableError(
            "tokei binary not found on PATH; install per integrations/tools/tokei.json or "
            "fall back to --engine splitlines."
        )


def _tokei_code(paths: list[Path], *, language: str, repo_root: Path) -> tuple[int, set[Path]]:
    """Count an exact path list with tokei and return its reported files."""

    cmd = [
        "tokei",
        "--output",
        "json",
        "--types",
        TOKEI_TYPES,
        "--no-ignore",
        "--hidden",
        *(str(path) for path in paths),
    ]
    completed = run_process(cmd, cwd=repo_root, timeout_seconds=None)
    if completed.returncode != 0:
        raise TokeiUnavailableError(
            f"tokei exited with status {completed.returncode}: {completed.stderr.strip()}"
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise TokeiUnavailableError(f"tokei returned invalid JSON: {exc}") from exc
    details = payload.get(language)
    if not isinstance(details, dict):
        return 0, set()
    reports = details.get("reports", [])
    if not isinstance(reports, list):
        raise TokeiUnavailableError(f"tokei returned an invalid {language} reports list")
    reported_paths: set[Path] = set()
    for report in reports:
        if not isinstance(report, dict) or not isinstance(report.get("name"), str):
            raise TokeiUnavailableError(f"tokei returned an invalid {language} report")
        report_path = Path(report["name"])
        if not report_path.is_absolute():
            report_path = repo_root / report_path
        reported_paths.add(report_path.resolve())
    return int(details.get("code", 0)), reported_paths


def _tokei_bucket_code(
    paths: list[Path], *, bucket: str, language: str, repo_root: Path
) -> tuple[int, dict[str, object] | None]:
    if not paths:
        return 0, None
    code, reported_paths = _tokei_code(paths, language=language, repo_root=repo_root)
    missing_paths = [path for path in paths if path.resolve() not in reported_paths]
    if not missing_paths:
        return code, None

    # Tokei 14 detects the extensionless Python shebang but does not classify
    # extensionless Bash hooks. Re-present any missed selected file with the
    # known language extension so the adjustment still uses tokei's code count,
    # while keeping the original file in the measured set.
    suffix = {"Python": ".py", "Shell": ".sh", "Rust": ".rs"}[language]
    with tempfile.TemporaryDirectory(prefix="test-production-ratio-") as temp_dir:
        remapped_paths: list[Path] = []
        for index, path in enumerate(missing_paths):
            remapped = Path(temp_dir) / f"{index}{suffix}"
            shutil.copyfile(path, remapped)
            remapped_paths.append(remapped)
        adjusted_code, adjusted_reported_paths = _tokei_code(
            remapped_paths, language=language, repo_root=repo_root
        )
    if len(adjusted_reported_paths) != len(missing_paths):
        missing = ", ".join(path.relative_to(repo_root).as_posix() for path in missing_paths)
        raise TokeiUnavailableError(f"tokei did not classify selected {bucket} files: {missing}")
    return code + adjusted_code, {
        "files": [path.relative_to(repo_root).as_posix() for path in missing_paths],
        "code_lines": adjusted_code,
        "method": "tokei-explicit-extension",
    }


def _tokei_summary(
    repo_root: Path, *, require_git: bool = False, test_paths: set[Path] | None = None
) -> dict[str, object]:
    _ensure_tokei_available()
    surface_files = _surface_files(repo_root, require_git=require_git, test_paths=test_paths)
    languages = {
        "python": "Python",
        "python-shebang": "Python",
        "shell": "Shell",
        "rust": "Rust",
        "rust-tests": "Rust",
        "tests-python": "Python",
    }
    line_counts: dict[str, int] = {}
    adjustments: dict[str, dict[str, object]] = {}
    for bucket in SURFACE_BUCKETS:
        code, adjustment = _tokei_bucket_code(
            surface_files[bucket],
            bucket=bucket,
            language=languages[bucket],
            repo_root=repo_root,
        )
        line_counts[bucket] = code
        if adjustment is not None:
            adjustments[bucket] = adjustment
    surface_breakdown: dict[str, object] = dict(line_counts)
    if adjustments:
        surface_breakdown["tokei_adjustments"] = adjustments
    return {
        "source_lines": sum(line_counts[bucket] for bucket in SURFACE_BUCKETS[:4]),
        "test_lines": sum(line_counts[bucket] for bucket in SURFACE_BUCKETS[4:]),
        "source_file_count": sum(len(surface_files[bucket]) for bucket in SURFACE_BUCKETS[:4]),
        "test_file_count": sum(len(surface_files[bucket]) for bucket in SURFACE_BUCKETS[4:]),
        "surface_breakdown": surface_breakdown,
        "surface_file_buckets": _surface_file_names(surface_files, repo_root),
    }


def _resolve_engine(engine: str) -> tuple[str, str]:
    if engine not in SUPPORTED_ENGINES:
        raise ValueError(f"unsupported engine {engine!r}; expected one of {SUPPORTED_ENGINES}")
    if engine == "auto":
        return ("tokei" if shutil.which("tokei") is not None else "splitlines", "auto")
    return engine, "explicit"


def summarize(
    repo_root: Path, *, engine: str = "auto", require_git: bool = False
) -> dict[str, object]:
    test_universe, test_files = _resolved_test_universe(repo_root, require_git=require_git)
    resolved_engine, engine_selection = _resolve_engine(engine)
    if resolved_engine == "tokei":
        counts = _tokei_summary(repo_root, require_git=require_git, test_paths=set(test_files))
    else:
        counts = _splitlines_summary(repo_root, require_git=require_git, test_paths=set(test_files))
    source_lines = int(counts["source_lines"])
    test_lines = int(counts["test_lines"])
    ratio = test_lines / source_lines if source_lines else 0.0
    return {
        "schema_version": 1,
        "scope": "executable-surface",
        "engine": resolved_engine,
        "engine_selection": engine_selection,
        "source_lines": source_lines,
        "test_lines": test_lines,
        "ratio": round(ratio, 4),
        "surface_breakdown": counts["surface_breakdown"],
        "source_file_count": counts["source_file_count"],
        "test_file_count": counts["test_file_count"],
        "test_roots": {
            "patterns": list(test_universe.patterns),
            "source": test_universe.source,
            "matched_files": len(test_files),
            "status": "configured" if test_files else "discovered-empty",
        },
        "excluded_source_dirs": sorted(IGNORED_DIRS),
        "skipped": {
            "status": "skipped",
            "reason": SKIPPED_PYTHON_REASON,
            "count": len(counts.get("skipped_paths", [])),
            "paths": counts.get("skipped_paths", []),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=repo_root_from_script(__file__))
    parser.add_argument("--max-ratio", type=float, default=DEFAULT_MAX_RATIO)
    parser.add_argument("--engine", choices=SUPPORTED_ENGINES, default="auto")
    parser.add_argument("--require-git-file-listing", action="store_true")
    parser.add_argument(
        "--advisory",
        action="store_true",
        help=(
            "report an over-threshold ratio as a non-blocking WARN posture instead of "
            "failing. A test/production LOC ratio is a smell sensor, not an "
            "irreversible-boundary contract (north-star P1); a hard cap pressures "
            "AGAINST writing tests as the ratio approaches it. The posture stays "
            "visible; judgment owns the split-vs-bloat call."
        ),
    )
    args = parser.parse_args()

    try:
        summary = summarize(
            args.repo_root.resolve(),
            engine=args.engine,
            require_git=args.require_git_file_listing,
        )
    except TokeiUnavailableError as exc:
        print(str(exc))
        return 2
    # `max_ratio` lived ONLY in the deleted human line -- the summary payload never
    # carried the bar the ratio is judged against, so a bare `ratio: 0.87` said
    # nothing about whether it passed. Output is unconditionally YAML now, so the
    # bar, the verdict and the advisory posture all ride on the payload.
    payload = {**summary, "max_ratio": args.max_ratio}
    over = float(summary["ratio"]) > args.max_ratio
    message = f"test-production ratio {summary['ratio']:.2f} exceeds max {args.max_ratio:.2f}"
    if over and args.advisory:
        payload["status"] = "advisory-warn"
        payload["advisory"] = f"WARN: {message} (advisory posture; not blocking)"
    else:
        payload["status"] = "over-max" if over else "within-max"
    emit_yaml(payload)
    if over:
        if args.advisory:
            return 0
        raise RatioError(message)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RatioError as exc:
        print(str(exc))
        raise SystemExit(1)
