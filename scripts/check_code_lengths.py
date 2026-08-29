#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _scripts_repo_file_listing_module.iter_matching_repo_files

REPO_SCRIPT_FILE_MAX = 480
SKILL_HELPER_FILE_MAX = 360
TEST_FILE_MAX = 800
# Rust joined this gate on 2026-08-29. It had NO length gate at all while the ratio
# gate counted `native/*/src/**.rs` in its production denominator, so 11,891 lines
# grew unmeasured to a 1,340-code-line file against a 480 Python cap.
#
# The source limit is a RATCHET set from measurement, not a judgement that 1,340 is
# acceptable: it is exactly today's maximum, so nothing may grow past where it
# already stands, and the warn band is set at the PYTHON cap so every file above it
# reports as debt on every run. Five files sit in that band today. Lowering the hard
# limit toward 480 is the work this makes visible; raising it is the treadmill
# `2026-05-20-quality-treadmill-vs-root-cause.md` names.
NATIVE_SOURCE_FILE_MAX = 1340
# Rust tests share the Python test budget; the largest is 406 today, so this is a
# real ceiling rather than a ratchet.
NATIVE_TEST_FILE_MAX = 800

# Advisory file-length warn band (tokei code lines, Python and Rust — function length
# is gated separately by ruff PLR0915, a statement-count rule, since tokei does
# not report function-level counts). A file in ``[warn, limit]`` keeps exit 0 but
# emits a ``WARN:`` line so
# this saturated codebase gets an early signal before the existing hard fail.
# The ``WARN:`` prefix is load-bearing: ``run-quality.sh`` only surfaces a
# *passing* gate's output when it matches
# ``^(WARNING|WARN|WEAK|ADVISORY)(:|[[:space:]])`` — an unprefixed advisory is
# captured to the log but never shown, silently defeating the tier.
REPO_SCRIPT_FILE_WARN = 432
SKILL_HELPER_FILE_WARN = 330
TEST_FILE_WARN = 720
NATIVE_SOURCE_FILE_WARN = REPO_SCRIPT_FILE_MAX
NATIVE_TEST_FILE_WARN = 720

# Advisory interpretation contract (see skills/shared/references/
# advisory-interpretation-contract.md). This attaches ONLY to the advisory
# warn-band/headroom signal — a length *smell*. The hard limit (over-limit
# ValidationError) is a verified deterministic fact and stays trusted: it never
# carries this declaration.
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
    # Both languages, because this gate stopped being Python-only on 2026-08-29. The
    # module name still says otherwise; renaming it touches 73 sites and is its own
    # change. Reading one language here while requesting two from tokei is exactly how
    # the caller would get "tokei did not return counts" for every Rust file it asked
    # about -- measured, not hypothetical.
    for language in ("Python", "Rust"):
        section = payload.get(language)
        if isinstance(section, dict):
            raw_reports = section.get("reports")
            if isinstance(raw_reports, list):
                reports.extend(report for report in raw_reports if isinstance(report, dict))
    total = payload.get("Total")
    if isinstance(total, dict):
        children = total.get("children")
        if isinstance(children, dict):
            for language in ("Python", "Rust"):
                raw_reports = children.get(language)
                if isinstance(raw_reports, list):
                    reports.extend(report for report in raw_reports if isinstance(report, dict))
    return reports


def tokei_code_counts(paths: list[Path]) -> dict[Path, int]:
    if not paths:
        return {}
    if shutil.which("tokei") is None:
        raise TokeiError(
            "tokei binary not found on PATH; install per integrations/tools/tokei.json. "
            "check_code_lengths uses tokei Python and Rust code-line counts and does not "
            "fall back to physical splitlines totals."
        )
    requested = {path.resolve(): path for path in paths}
    completed = subprocess.run(
        ["tokei", "--output", "json", "--types", "Python,Rust", *[str(path) for path in paths]],
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
            "skills/shared/scripts/*.py",
            "tests/*.py",
            "tests/**/*.py",
            "native/*/src/*.rs",
            "native/*/src/**/*.rs",
            "native/*/tests/*.rs",
            "native/*/tests/**/*.rs",
            "native/*/build.rs",
        ),
        require_git=require_git,
    )


def _is_native_test(relative: Path) -> bool:
    return "tests" in relative.parts[1:-1]


def file_limit_for(path: Path, root: Path) -> int:
    relative = path.relative_to(root)
    if relative.parts[:1] == ("native",):
        return NATIVE_TEST_FILE_MAX if _is_native_test(relative) else NATIVE_SOURCE_FILE_MAX
    if relative.parts[:1] == ("scripts",):
        return REPO_SCRIPT_FILE_MAX
    if relative.parts[:1] == ("tests",):
        return TEST_FILE_MAX
    return SKILL_HELPER_FILE_MAX


def file_warn_for(path: Path, root: Path) -> int:
    relative = path.relative_to(root)
    if relative.parts[:1] == ("native",):
        return NATIVE_TEST_FILE_WARN if _is_native_test(relative) else NATIVE_SOURCE_FILE_WARN
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
        # Operator-endorsed teeth (charness-artifacts/gather/2026-07-04-enforcing-
        # quality-of-ai-generated-code.md): a max-file-length linter constraint stays
        # blocking even on reversible work. The message still teaches the north-star
        # response instead of leaving the evasion path implicit: split the file into
        # a cohesion-scoped module or delete dead code -- do NOT mechanically spill
        # into an _extra_lib/_lib companion just to dodge the cap.
        raise ValidationError(
            f"{path}: tokei code lines {code_lines} exceed limit {limit}. Split the file "
            "into a cohesive new module or delete code; do not mechanically spill into an "
            "_extra_lib/_lib companion to dodge the cap (docs/deferred-decisions.md D33)."
        )
    warn = file_warn_for(path, root)
    if code_lines >= warn:
        relative = path.relative_to(root)
        return (
            f"WARN: {relative}: tokei code lines {code_lines} are within the advisory warn "
            f"band [{warn}, {limit}]; separate a concept or delete before it reaches the hard "
            f"limit {limit} — do not shave lines to stay under the bar."
        )
    return None


def headroom_for(paths: list[Path] | None, root: Path) -> list[dict[str, object]]:
    """Advisory pre-write/closeout headroom report for the gated subset of
    ``paths`` (``None`` means every gated file, matching the gate's own default):
    per file, ``headroom = limit - current`` where ``current`` is the
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
            "writing. File current is tokei code lines (Python and Rust). Function length is "
            "gated separately by ruff PLR0915 (statement count)."
        ),
    )
    args = parser.parse_args()

    root = args.repo_root.resolve()
    if args.headroom:
        # `args.paths`, not `args.paths or []`: an omitted --paths is None (report
        # every gated file, as --help promises), while `[]` would be read by
        # `select_targets` as an explicit empty selection and print nothing.
        rows = headroom_for(args.paths, root)
        near = [r["path"] for r in rows if r["near_limit"]]
        payload: dict[str, object] = {"headroom": rows}
        if near:
            # The exact `limit - current` headroom values are verified facts; the
            # warn-band/near-limit judgment is the inference layer, so the
            # self-declaration rides only when a near-limit smell is present.
            payload["interpretation"] = dict(INTERPRETATION)
            # Folded in from the deleted human branch, which was the only carrier
            # of the "choose a new module before adding more" advice and of the
            # near-limit roll-up. Output is unconditionally YAML, so a per-row
            # `near_limit: true` with no advice is all a reader would get.
            payload["near_limit_paths"] = near
            payload["advisory"] = (
                f"WARN: {len(near)} file(s) near the length limit; consider a new "
                "module before adding more."
            )
        emit_yaml(payload)
        return 0
    targets = select_targets(
        root, paths=args.paths, require_git=args.require_git_file_listing
    )
    if args.paths is not None and not targets:
        # A NAMED scope that measured nothing must not read as a pass. Two shapes,
        # deliberately answered differently:
        #  - a named path that does not exist at all (a typo, or paths expressed
        #    relative to a subdirectory so they never resolve under --repo-root) is
        #    a broken scope and refuses;
        #  - named paths that exist but sit outside the gated glob universe (the
        #    generated `plugins/` mirror, root-level `runtime_bootstrap.py`) are the
        #    caller saying "none of this is yours" — a legitimate pass, as for the
        #    artifact family, but it may not print `Validated ... 0 file(s)`.
        unresolved = [
            path for path in args.paths
            if not (path if path.is_absolute() else root / path).exists()
        ]
        if unresolved:
            raise ValidationError(
                "named --paths resolve to nothing under "
                f"{root}: {', '.join(str(path) for path in unresolved)}; nothing was "
                "validated. Pass paths relative to --repo-root, or drop --paths to "
                "gate the whole repo."
            )
        print(
            f"No gated Python files among the {len(args.paths)} named path(s); "
            "nothing was validated (the gated globs are scripts/, tests/, and skill "
            "package scripts/)."
        )
        return 0
    counts = tokei_code_counts(targets)
    warnings: list[str] = []
    hard_failures: list[str] = []
    for path in targets:
        try:
            warning = validate_file_length(path, root, code_lines=counts[path])
        except (ValidationError, SyntaxError) as exc:
            hard_failures.append(str(exc))
            continue
        if warning is not None:
            warnings.append(warning)

    if hard_failures:
        for failure in hard_failures:
            print(failure, file=sys.stderr)
        print(
            f"Validation failed for {len(hard_failures)} file(s); all hard length "
            "failures are listed above.",
            file=sys.stderr,
        )
        return 1

    for warning in warnings:
        print(warning)
    print(f"Validated code length limits for {len(targets)} file(s).")
    if warnings:
        print(
            f"WARN: {len(warnings)} file(s) within the advisory file-length warn band "
            "(exit 0; separate a concept or delete before they reach the hard limit)."
        )
        _print_warn_band_interpretation()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
