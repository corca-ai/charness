#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _scripts_repo_file_listing_module.iter_matching_repo_files
_subprocess_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_process = _subprocess_guard.run_process

REPO_SCRIPT_FILE_MAX = 480
SHELL_FILE_MAX = 205
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
SHELL_FILE_WARN = SHELL_FILE_MAX + 1
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
    # Both languages, because this gate stopped being Python-only on 2026-08-29 -- the
    # module was renamed from `check_python_lengths` to match, since a gate whose name
    # narrows its scope is read wrong by everyone who has not opened it.
    # Reading one language here while requesting two from tokei is exactly how
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
    completed = run_process(
        ["tokei", "--output", "json", "--types", "Python,Rust", *[str(path) for path in paths]],
        cwd=REPO_ROOT,
        timeout_seconds=None,
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
            raise TokeiError(
                f"tokei report for {requested[resolved]} is missing integer `stats.code`"
            )
        counts[requested[resolved]] = code
    missing = [path for path in paths if path not in counts]
    if missing:
        missing_list = ", ".join(str(path) for path in missing)
        raise TokeiError(f"tokei did not return Python code-line counts for: {missing_list}")
    return counts


#: The one place the gated universe is spelled. `gated_globs_summary` renders it for
#: the operator, so a glob added here cannot leave the "nothing was validated" message
#: describing a narrower gate than the one that ran -- which is what it did while it
#: said "Python" and "scripts/, tests/, and skill package scripts/" over a set that
#: had included `native/**/*.rs` since the Rust core landed.
#: Spans two code families on purpose: Python and Rust are measured by the SAME tokei
#: code-line rule with per-class limits, so splitting the set per language would give
#: one file-length policy two owners that could drift apart.
# discovery-boundary: one tokei code-line policy owns both Python and Rust here
GATED_GLOBS = (
    "scripts/*.py",
    "scripts/**/*.py",
    "scripts/*.sh",
    "scripts/**/*.sh",
    "tools/*.py",
    "tools/**/*.py",
    "tools/*.sh",
    "tools/**/*.sh",
    "skills/public/*/scripts/*.py",
    "skills/public/*/scripts/**/*.py",
    "skills/public/*/scripts/*.sh",
    "skills/public/*/scripts/**/*.sh",
    "skills/support/*/scripts/*.py",
    "skills/support/*/scripts/**/*.py",
    "skills/support/*/scripts/*.sh",
    "skills/support/*/scripts/**/*.sh",
    "skills/shared/scripts/*.py",
    "skills/shared/scripts/**/*.py",
    "skills/shared/scripts/*.sh",
    "skills/shared/scripts/**/*.sh",
    "tests/*.py",
    "tests/**/*.py",
    "native/*/src/*.rs",
    "native/*/src/**/*.rs",
    "native/*/tests/*.rs",
    "native/*/tests/**/*.rs",
    "native/*/build.rs",
)

#: The validated verdict, as ONE source. The tests that pin it format this rather
#: than re-spelling the sentence: renaming the message used to mean chasing string
#: literals across test files serially, while the COUNT -- the part that carries the
#: invariant -- is still asserted by the caller.
VALIDATED_VERDICT_TEMPLATE = "Validated code length limits for {count} file(s)."


def validated_verdict(count: int) -> str:
    return VALIDATED_VERDICT_TEMPLATE.format(count=count)


def gated_globs_summary() -> str:
    """Operator-facing rendering of the gated universe, derived from GATED_GLOBS."""

    roots = sorted({glob.split("/", 1)[0] + "/" for glob in GATED_GLOBS})
    suffixes = sorted({"." + glob.rsplit(".", 1)[1] for glob in GATED_GLOBS})
    return f"{', '.join(roots)} for {', '.join(suffixes)}"


def iter_python_targets(root: Path, *, require_git: bool = False) -> list[Path]:
    return iter_matching_repo_files(root, GATED_GLOBS, require_git=require_git)


def _is_native_test(relative: Path) -> bool:
    return "tests" in relative.parts[1:-1]


def file_limit_for(path: Path, root: Path) -> int:
    relative = path.relative_to(root)
    if relative.suffix == ".sh":
        return SHELL_FILE_MAX
    if relative.parts[:1] == ("native",):
        return NATIVE_TEST_FILE_MAX if _is_native_test(relative) else NATIVE_SOURCE_FILE_MAX
    if relative.parts[:1] in (("scripts",), ("tools",)):
        return REPO_SCRIPT_FILE_MAX
    if relative.parts[:1] == ("tests",):
        return TEST_FILE_MAX
    return SKILL_HELPER_FILE_MAX


def file_warn_for(path: Path, root: Path) -> int:
    relative = path.relative_to(root)
    if relative.suffix == ".sh":
        return SHELL_FILE_WARN
    if relative.parts[:1] == ("native",):
        return NATIVE_TEST_FILE_WARN if _is_native_test(relative) else NATIVE_SOURCE_FILE_WARN
    if relative.parts[:1] in (("scripts",), ("tools",)):
        return REPO_SCRIPT_FILE_WARN
    if relative.parts[:1] == ("tests",):
        return TEST_FILE_WARN
    return SKILL_HELPER_FILE_WARN


SHELL_LENGTH_EXEMPTIONS = {
    "scripts/run-quality.sh": "2026-09-02; retired by #769",
}


def validate_file_length(path: Path, root: Path, *, code_lines: int) -> str | None:
    """Hard-fail when a file exceeds its code-line limit; otherwise return an advisory
    ``WARN:`` line when the file sits in the ``[warn, limit]`` band, or ``None``.
    """
    relative = path.relative_to(root)
    exemption = SHELL_LENGTH_EXEMPTIONS.get(relative.as_posix())
    limit = file_limit_for(path, root)
    if exemption is not None and code_lines > limit:
        return (
            f"WARN: {relative}: physical lines {code_lines} exceed shell cap {limit}; "
            f"NAMED EXEMPTION ({exemption})."
        )
    measurement = "physical lines" if relative.suffix == ".sh" else "tokei code lines"
    if code_lines > limit:
        # Operator-endorsed teeth (charness-artifacts/gather/2026-07-04-enforcing-
        # quality-of-ai-generated-code.md): a max-file-length linter constraint stays
        # blocking even on reversible work. The message still teaches the north-star
        # response instead of leaving the evasion path implicit: split the file into
        # a cohesion-scoped module or delete dead code -- do NOT mechanically spill
        # into an _extra_lib/_lib companion just to dodge the cap.
        raise ValidationError(
            f"{relative}: {measurement} {code_lines} exceed limit {limit}. Split the file "
            "into a cohesive new module or delete code; do not mechanically spill into an "
            "_extra_lib/_lib companion to dodge the cap (docs/deferred-decisions.md D33)."
        )
    warn = file_warn_for(path, root)
    if code_lines >= warn:
        return (
            f"WARN: {relative}: {measurement} {code_lines} are within the advisory warn "
            f"band [{warn}, {limit}]; separate a concept or delete before it reaches the hard "
            f"limit {limit} — do not shave lines to stay under the bar."
        )
    return None


def shell_line_counts(paths: list[Path]) -> dict[Path, int]:
    """Measure shell files by physical lines; tokei is not a shell counter here."""

    counts: dict[Path, int] = {}
    for path in paths:
        try:
            counts[path] = path.read_bytes().count(b"\n")
        except OSError as exc:
            raise ValidationError(f"cannot read {path}: {exc}") from exc
    return counts


def code_line_counts(paths: list[Path]) -> dict[Path, int]:
    """Use the established tokei measurement for code and physical lines for shell."""

    non_shell = [path for path in paths if path.suffix != ".sh"]
    counts = tokei_code_counts(non_shell) if non_shell else {}
    counts.update(shell_line_counts([path for path in paths if path.suffix == ".sh"]))
    return counts


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
    if not targets:
        scope = "named --paths (they resolve to nothing)" if paths is not None else "the repository"
        raise ValidationError(
            f"refusing empty matched universe for {scope}; nothing was measured "
            f"(gated globs: {', '.join(GATED_GLOBS)})."
        )
    counts = code_line_counts(targets)
    rows: list[dict[str, object]] = []
    for path in targets:
        lines = counts[path]
        limit = file_limit_for(path, root)
        warn = file_warn_for(path, root)
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "lines": lines,
                "measurement": "physical-lines"
                if path.suffix == ".sh"
                else "tokei-python-code-lines",
                "limit": limit,
                "warn": warn,
                "headroom": limit - lines,
                "near_limit": lines >= warn,
            }
        )
    return rows


def select_targets(root: Path, *, paths: list[Path] | None, require_git: bool) -> list[Path]:
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
    targets = select_targets(root, paths=args.paths, require_git=args.require_git_file_listing)
    if not targets:
        scope = (
            "named --paths (they resolve to nothing)"
            if args.paths is not None
            else "the repository"
        )
        raise ValidationError(
            f"refusing empty matched universe for {scope}; nothing was validated "
            f"(gated globs: {', '.join(GATED_GLOBS)})."
        )
    counts = code_line_counts(targets)
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
    print(validated_verdict(len(targets)))
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
