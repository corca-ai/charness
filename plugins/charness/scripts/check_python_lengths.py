#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import json
import shutil
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _scripts_repo_file_listing_module.iter_matching_repo_files

REPO_SCRIPT_FILE_MAX = 480
SKILL_HELPER_FILE_MAX = 360
TEST_FILE_MAX = 800
FUNCTION_MAX = 100
TEST_FUNCTION_MAX = 150

# Advisory file-length warn band (tokei Python code lines only — function limits
# stay hard-only and AST-span based because tokei does not report function-level
# counts). A file in ``[warn, limit]`` keeps exit 0 but emits a ``WARN:`` line so
# this saturated codebase gets an early signal before the existing hard fail.
# The ``WARN:`` prefix is load-bearing: ``run-quality.sh`` only surfaces a
# *passing* gate's output when it matches
# ``^(WARNING|WARN|WEAK|ADVISORY)(:|[[:space:]])`` — an unprefixed advisory is
# captured to the log but never shown, silently defeating the tier.
REPO_SCRIPT_FILE_WARN = 432
SKILL_HELPER_FILE_WARN = 330
TEST_FILE_WARN = 720

# Advisory interpretation contract (see skills/shared/references/
# advisory-interpretation-contract.md). This attaches ONLY to the advisory
# warn-band/headroom signal — a length *smell*. The hard limit (over-limit
# ValidationError) and the function-length AST check are verified deterministic
# facts and stay trusted: they never carry this declaration.
INTERPRETATION = {
    "measures": (
        "a gated file's tokei Python code-line count sitting inside its per-class "
        "advisory warn band [warn, limit] (below the hard length limit)"
    ),
    "proxy_for": "a file accreting toward the hard length limit — over-accumulation that will soon force a split",
    "blind_spots": (
        "counts code lines, not cohesion — an intentional, well-factored module near "
        "its limit sits in the band the same as a grab-bag that should already be "
        "split; it cannot see whether the lines belong together"
    ),
    "interpretation_question": (
        "is this warn-band file an honest cohesive unit near its limit, or genuine "
        "over-accumulation THIS repo should split now?"
    ),
}


def _print_warn_band_interpretation() -> None:
    # `ADVISORY:` prefix is load-bearing: run-quality.sh only surfaces a *passing*
    # gate's output matching ^(WARNING|WARN|WEAK|ADVISORY)(:|space), so an
    # unprefixed INTERPRETATION line would be logged but never shown on a warn-band
    # pass — silently defeating the declaration (the same trap the warn-band
    # constants comment documents).
    print(
        "ADVISORY: INTERPRETATION (inference-layer length smell, not a verdict): "
        f"measures {INTERPRETATION['measures']}; proxy for "
        f"{INTERPRETATION['proxy_for']}; blind spots: {INTERPRETATION['blind_spots']}. "
        f"Consumer must answer first: {INTERPRETATION['interpretation_question']}"
    )


class ValidationError(Exception):
    pass


class TokeiError(ValidationError):
    pass


def _collect_tokei_reports(payload: object) -> list[dict[str, object]]:
    if not isinstance(payload, dict):
        return []
    reports: list[dict[str, object]] = []
    python = payload.get("Python")
    if isinstance(python, dict):
        raw_reports = python.get("reports")
        if isinstance(raw_reports, list):
            reports.extend(report for report in raw_reports if isinstance(report, dict))
    total = payload.get("Total")
    if isinstance(total, dict):
        children = total.get("children")
        if isinstance(children, dict):
            raw_reports = children.get("Python")
            if isinstance(raw_reports, list):
                reports.extend(report for report in raw_reports if isinstance(report, dict))
    return reports


def tokei_code_counts(paths: list[Path]) -> dict[Path, int]:
    if not paths:
        return {}
    if shutil.which("tokei") is None:
        raise TokeiError(
            "tokei binary not found on PATH; install per integrations/tools/tokei.json. "
            "check_python_lengths uses tokei Python code-line counts and does not "
            "fall back to physical splitlines totals."
        )
    requested = {path.resolve(): path for path in paths}
    completed = subprocess.run(
        ["tokei", "--output", "json", "--types", "Python", *[str(path) for path in paths]],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise TokeiError(
            f"tokei exited with status {completed.returncode}: {completed.stderr.strip()}"
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise TokeiError(f"tokei returned invalid JSON: {exc}") from exc

    counts: dict[Path, int] = {}
    for report in _collect_tokei_reports(payload):
        name = report.get("name")
        stats = report.get("stats")
        if not isinstance(name, str) or not isinstance(stats, dict):
            continue
        resolved = Path(name).resolve()
        if resolved not in requested:
            continue
        code = stats.get("code")
        if not isinstance(code, int):
            raise TokeiError(f"tokei report for {requested[resolved]} is missing integer `stats.code`")
        counts[requested[resolved]] = code
    missing = [path for path in paths if path not in counts]
    if missing:
        missing_list = ", ".join(str(path) for path in missing)
        raise TokeiError(f"tokei did not return Python code-line counts for: {missing_list}")
    return counts


def iter_python_targets(root: Path, *, require_git: bool = False) -> list[Path]:
    return iter_matching_repo_files(
        root,
        (
            "scripts/*.py",
            "skills/public/*/scripts/*.py",
            "skills/support/*/scripts/*.py",
            "tests/*.py",
            "tests/**/*.py",
        ),
        require_git=require_git,
    )


def file_limit_for(path: Path, root: Path) -> int:
    relative = path.relative_to(root)
    if relative.parts[:1] == ("scripts",):
        return REPO_SCRIPT_FILE_MAX
    if relative.parts[:1] == ("tests",):
        return TEST_FILE_MAX
    return SKILL_HELPER_FILE_MAX


def file_warn_for(path: Path, root: Path) -> int:
    relative = path.relative_to(root)
    if relative.parts[:1] == ("scripts",):
        return REPO_SCRIPT_FILE_WARN
    if relative.parts[:1] == ("tests",):
        return TEST_FILE_WARN
    return SKILL_HELPER_FILE_WARN


def validate_file_length(path: Path, root: Path, *, code_lines: int) -> str | None:
    """Hard-fail when a file exceeds its code-line limit; otherwise return an advisory
    ``WARN:`` line when the file sits in the ``[warn, limit]`` band, or ``None``.
    """
    limit = file_limit_for(path, root)
    if code_lines > limit:
        raise ValidationError(f"{path}: Python code lines {code_lines} exceed limit {limit}")
    warn = file_warn_for(path, root)
    if code_lines >= warn:
        relative = path.relative_to(root)
        return (
            f"WARN: {relative}: Python code lines {code_lines} are within the advisory warn "
            f"band [{warn}, {limit}]; trim before it reaches the hard limit {limit}."
        )
    return None


def function_limit_for(path: Path, root: Path) -> int:
    relative = path.relative_to(root)
    if relative.parts[:1] == ("tests",):
        return TEST_FUNCTION_MAX
    return FUNCTION_MAX


def validate_function_lengths(path: Path, root: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    limit = function_limit_for(path, root)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
            continue
        length = node.end_lineno - node.lineno + 1
        if length > limit:
            raise ValidationError(
                f"{path}: function `{node.name}` length {length} exceeds limit {limit}"
            )


def headroom_for(paths: list[Path], root: Path) -> list[dict[str, object]]:
    """Advisory pre-write/closeout headroom report for the gated subset of
    ``paths``: per file, ``headroom = limit - current`` where ``current`` is the
    tokei Python code-line count, and whether the file is already inside the warn
    band. This is the affordance behind #256 — the hard gate
    (``validate_file_length``) blocks an over-limit *commit*, but the recurring
    waste is *writing* a large addition into an already-near-limit file and only
    learning at the gate. Surfacing ``limit - current`` lets a slice decide "new
    module vs append" before writing. Advisory only; never blocks on length
    overages, but still fails when the tokei measurement itself is unavailable.
    """
    targets = select_targets(root, paths=paths, require_git=False)
    counts = tokei_code_counts(targets)
    rows: list[dict[str, object]] = []
    for path in targets:
        lines = counts[path]
        limit = file_limit_for(path, root)
        warn = file_warn_for(path, root)
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "lines": lines,
                "measurement": "tokei-python-code-lines",
                "limit": limit,
                "warn": warn,
                "headroom": limit - lines,
                "near_limit": lines >= warn,
            }
        )
    return rows


def select_targets(
    root: Path, *, paths: list[Path] | None, require_git: bool
) -> list[Path]:
    """Whole-repo glob by default. When ``paths`` is given (e.g. staged files in
    a pre-commit hook), restrict to the subset of those paths the whole-repo
    glob would also gate, so the same per-class limits/bands apply and a path
    outside the gated universe (an export mirror, a top-level file) is never
    gated. Staged-only by design: a pre-existing over-limit file not in
    ``paths`` is left to the whole-repo run.
    """
    if paths is None:
        return iter_python_targets(root, require_git=require_git)
    universe = set(iter_python_targets(root, require_git=False))
    requested = {(p if p.is_absolute() else root / p).resolve() for p in paths}
    return sorted(universe & requested)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--require-git-file-listing", action="store_true")
    parser.add_argument(
        "--paths",
        nargs="+",
        type=Path,
        metavar="FILE",
        help=(
            "Explicit files to check (e.g. staged files in a pre-commit hook). "
            "Restricts the check to the subset of these paths the whole-repo "
            "glob would also gate, applying the same per-class limits and warn "
            "bands. Takes precedence over the glob scan; "
            "--require-git-file-listing is then irrelevant."
        ),
    )
    parser.add_argument(
        "--headroom",
        action="store_true",
        help=(
            "Advisory mode (#256): print `limit - current` headroom per gated file "
            "instead of gating, so a slice can choose new-module-vs-append before "
            "writing. Current is measured as tokei Python code lines."
        ),
    )
    parser.add_argument("--json", action="store_true", help="JSON output (with --headroom).")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    if args.headroom:
        rows = headroom_for(args.paths or [], root)
        near = [r["path"] for r in rows if r["near_limit"]]
        if args.json:
            payload: dict[str, object] = {"headroom": rows}
            # The exact `limit - current` headroom values are verified facts; the
            # warn-band/near-limit judgment is the inference layer, so the
            # self-declaration rides only when a near-limit smell is present.
            if near:
                payload["interpretation"] = dict(INTERPRETATION)
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            for row in rows:
                flag = " NEAR-LIMIT" if row["near_limit"] else ""
                print(
                    f"headroom: {row['path']}: {row['lines']}/{row['limit']} code lines "
                    f"({row['headroom']} left){flag}"
                )
            if near:
                print(
                    f"WARN: {len(near)} file(s) near the length limit; consider a new "
                    "module before adding more: " + ", ".join(near)
                )
                _print_warn_band_interpretation()
        return 0
    targets = select_targets(
        root, paths=args.paths, require_git=args.require_git_file_listing
    )
    counts = tokei_code_counts(targets)
    warnings: list[str] = []
    for path in targets:
        try:
            warning = validate_file_length(path, root, code_lines=counts[path])
            validate_function_lengths(path, root)
        except (ValidationError, SyntaxError) as exc:
            raise ValidationError(str(exc)) from exc
        if warning is not None:
            warnings.append(warning)

    for warning in warnings:
        print(warning)
    print(f"Validated Python length limits for {len(targets)} file(s).")
    if warnings:
        print(
            f"WARN: {len(warnings)} file(s) within the advisory file-length warn band "
            "(exit 0; trim before they reach the hard limit)."
        )
        _print_warn_band_interpretation()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
