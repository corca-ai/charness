#!/usr/bin/env python3
"""Reference gate for unfloored-file drift.

This sample is intentionally generic. Adapt the constants or convert them to
CLI arguments inside the target repo.

What it demonstrates:

- enumerate meaningful source files before trusting prior review artifacts
- discover gate scripts by glob instead of a hardcoded tuple
- strip shell comments before matching floored paths
- fail on contradictions: floored and exempted at the same time
- keep a warn band visible on stderr even when the gate passes
- cross-check inventory-discovered gate scripts with lefthook and CI references
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    from scripts.repo_file_listing import RepoFileListingError, RepoFileSnapshot
except ModuleNotFoundError:
    from repo_file_listing import RepoFileListingError, RepoFileSnapshot

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
POLICY = {
    "min_statements_threshold": 30,
    "fail_below_pct": 80.0,
    "warn_ceiling_pct": 95.0,
    "exemption_list_path": "scripts/coverage-floor-exemptions.txt",
    "gate_script_pattern": "*-quality-gate.sh",
    "lefthook_path": "lefthook.yml",
    "ci_workflow_glob": ".github/workflows/*.yml",
}
FLOOR_PATH_RE = re.compile(r'"(src/[A-Za-z0-9_./-]+\.py)"')
# Any path-shaped token in a lefthook or CI file. Deliberately generic: which of
# these are GATES is decided by `matches_gate_pattern`, never by the extractor.
PATH_TOKEN_RE = re.compile(r"[A-Za-z0-9_.][A-Za-z0-9_./-]*/[A-Za-z0-9_.][A-Za-z0-9_./-]*")


def strip_shell_comments(text: str) -> str:
    return "\n".join(line.split("#", 1)[0] for line in text.splitlines())


def anchored_gate_pattern() -> str:
    """`gate_script_pattern` as a single REPO-ROOT-RELATIVE glob.

    A bare filename glob (`*-quality-gate.sh`) keeps its historical anchor under
    `scripts/` and is returned as `scripts/*-quality-gate.sh`. A pattern carrying a
    separator is already repo-root-relative, which is the only way a repo whose stop
    gate is `.githooks/pre-commit` can name it: anchoring everything under `scripts/`
    resolved that spelling to `scripts/.githooks/pre-commit` and matched nothing, so
    the policy could describe the repo or be resolvable, never both.

    ONE anchored pattern, not a (prefix, suffix) pair. The first cut derived a
    directory prefix with `Path(pattern).parent` and a suffix with `Path(pattern).suffix`,
    and both are wrong the moment the pattern holds a metacharacter outside the
    basename: `**/*-quality-gate.sh` yielded the literal prefix `**/`, which no real
    path starts with, and `*-gate.*` yielded the suffix `.*`, which no real path ends
    with. Each silently emptied the meta-check's `foreign` half and simultaneously
    made its `orphaned` half fire on everything -- a false red whose only remedy was
    to stop naming the pattern correctly. Matching the whole anchored pattern with
    one glob engine (`_glob_to_regex`) has no such decomposition to get wrong.
    """
    pattern = POLICY["gate_script_pattern"]
    if "/" in pattern:
        return pattern
    return f"scripts/{pattern}"


def tracked_repo_files() -> list[str]:
    """Repo-relative paths from `git ls-files`, so the scan is gitignore-aware.

    A filesystem walk sees build output, virtualenvs and anything else `.gitignore`
    excludes, and a gate that discovers an ignored file is reporting on something the
    repo does not own. Using the git listing as the FILE SOURCE and `matches_gate_pattern`
    as the filter also means discovery and the meta-check ask one question of one
    population -- a `glob` here and a pattern match there is two readers that can
    disagree.

    PRECONDITION, stated because it is new: a git repository and a `git` binary. This
    gate refuses without them rather than falling back to a walk, because an
    unestablished population under a passing verdict is the false green it exists to
    prevent. A repo adapting this sample without git must replace this function and
    say so.
    """
    try:
        listed = RepoFileSnapshot(REPO_ROOT, require_git=True).list_files(
            include_untracked=True
        )
    except RepoFileListingError as exc:
        raise SystemExit(
            "FAIL: git file listing failed; this gate scans a tracked population and "
            f"cannot report over an unestablished one.\n{exc}"
        ) from exc
    except OSError as exc:
        raise SystemExit(f"FAIL: git is required to establish the scanned population: {exc}") from exc
    if listed is None:
        raise SystemExit(
            "FAIL: git file listing failed; this gate scans a tracked population and "
            "cannot report over an unestablished one."
        )
    return [path.relative_to(REPO_ROOT).as_posix() for path in listed]


def discover_gate_scripts() -> list[Path]:
    pattern = anchored_gate_pattern()
    if pattern.startswith("/"):
        # An absolute pattern can never match a repo-relative listing. Every other bad
        # input in this file gets a `FAIL:` line, and this one used to raise out of
        # `Path.glob` as a traceback the operator cannot act on.
        raise SystemExit(
            f"FAIL: gate_script_pattern must be repo-relative, got absolute {pattern!r}"
        )
    return [REPO_ROOT / path for path in sorted(tracked_repo_files()) if matches_gate_pattern(path)]


def collect_declared_floors(gate_paths: list[Path]) -> set[str]:
    declared: set[str] = set()
    for gate_path in gate_paths:
        text = strip_shell_comments(gate_path.read_text(encoding="utf-8"))
        for match in FLOOR_PATH_RE.finditer(text):
            declared.add(match.group(1))
    return declared


def collect_exemptions() -> set[str]:
    # `.get`, for the same reason `operational_ref_sources` uses it: a repo that
    # declares `coverage_floor_policy.exemption_list_path` absent has no such key.
    exemption_list = POLICY.get("exemption_list_path")
    if not exemption_list:
        return set()
    exemption_path = REPO_ROOT / exemption_list
    if not exemption_path.is_file():
        return set()
    exempted: set[str] = set()
    for raw in exemption_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        full_path = REPO_ROOT / line
        if not full_path.is_file():
            raise SystemExit(f"FAIL: exemption path does not exist: {line}")
        exempted.add(line)
    return exempted


def _glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Shell/`Path.glob` semantics: `*` stops at `/`, `**/` spans zero or more segments.

    NOT `fnmatch`. `fnmatch`'s `*` crosses `/`, and its `**/` requires a literal
    separator, so it disagrees with the glob a consumer reads the pattern AS in both
    directions at once. Measured on the two spellings this repo actually ships:
    `fnmatch("scripts/archive/old-quality-gate.sh", "scripts/*-quality-gate.sh")` is
    True (a retired nested gate gets discovered and then reported as drift), and
    `fnmatch("repo-quality-gate.sh", "**/*-quality-gate.sh")` is False (a root-level
    gate drops out of DISCOVERY, so the floors it declares are never read and every
    file floored only there is reported as unfloored).

    One engine, used by both discovery and the meta-check, is the whole point: two
    readers of one pattern is what the previous prefix/suffix decomposition was.

    This repo already owns the same translator in `scripts/what_reads_this.py`, with
    the same recorded reason for rejecting `fnmatch`. It is duplicated here rather
    than imported because this file is a REFERENCE SAMPLE a consuming repo copies
    wholesale: a sample that only runs when a charness-internal helper is importable
    is not a sample. The duplication is classified in the duplicate ratchet.
    """
    out: list[str] = []
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if pattern.startswith("**/", index):
            out.append("(?:[^/]+/)*")
            index += 3
        elif pattern.startswith("**", index):
            out.append(".*")
            index += 2
        elif char == "*":
            out.append("[^/]*")
            index += 1
        elif char == "?":
            out.append("[^/]")
            index += 1
        else:
            out.append(re.escape(char))
            index += 1
    return re.compile(f"^{''.join(out)}$")


def matches_gate_pattern(path: str) -> bool:
    """Whether a repo-relative path is one `gate_script_pattern` claims."""
    return bool(_glob_to_regex(anchored_gate_pattern()).match(path))


def operational_ref_sources() -> list[Path]:
    """The lefthook and CI files this repo actually has, in that order.

    `.get`, not `[...]`: a repo that declares `coverage_floor_policy.lefthook_path`
    absent (the documented way to say "no lefthook here") resolves a policy with no
    such key at all, and an unconditional lookup turned following the documentation
    into a `KeyError` traceback.
    """
    tracked = set(tracked_repo_files())
    sources: list[Path] = []
    lefthook = POLICY.get("lefthook_path")
    # The SAME population discovery reads. Resolving lefthook with `is_file()` while
    # resolving workflows from the git listing is two readers over two populations
    # inside the one function whose comment claims otherwise: a gitignored lefthook
    # would count and a gitignored workflow would not.
    if lefthook and lefthook in tracked:
        sources.append(REPO_ROOT / lefthook)
    workflow_glob = POLICY.get("ci_workflow_glob")
    if workflow_glob:
        workflow_re = _glob_to_regex(workflow_glob)
        sources.extend(REPO_ROOT / path for path in sorted(tracked) if workflow_re.match(path))
    return sources


def declared_operational_keys() -> list[str]:
    """The operational sub-keys this policy still claims, as opposed to declared absent.

    The discriminator the meta-check needs. `sources == []` alone cannot separate
    "this repo has no lefthook and no CI, and said so" from "lefthook_path says
    `lefthook.yml` and this repo's file is `lefthook.yaml`" -- and reporting the
    second as an honest SKIP is a misconfigured reference rendered as a pass, which is
    strictly worse than the loud wrong red it replaced.
    """
    return [key for key in ("lefthook_path", "ci_workflow_glob") if POLICY.get(key)]


def load_operational_refs(sources: list[Path]) -> set[str]:
    """Every path-shaped token in the operational files, plus the files themselves.

    Extraction is deliberately generic and the FILTERING is `matches_gate_pattern`.
    Deriving a regex from the pattern instead put the pattern's metacharacters inside
    `re.escape`, which is how `**/` and `.*` produced expressions nothing could match.
    """
    refs: set[str] = set()
    for source in sources:
        refs.add(source.relative_to(REPO_ROOT).as_posix())
        refs.update(PATH_TOKEN_RE.findall(source.read_text(encoding="utf-8")))
    return refs


def meta_check_gate_scripts(gate_paths: list[Path]) -> None:
    discovered = {path.relative_to(REPO_ROOT).as_posix() for path in gate_paths}
    sources = operational_ref_sources()
    if not sources:
        declared = declared_operational_keys()
        if declared:
            # CONFIGURED and unresolvable. The policy still claims these surfaces, and
            # nothing on disk answers -- a spelling drift (`lefthook.yaml`,
            # `.github/workflows/*.yaml`) or an untracked file. That is a broken
            # reference, not an absent one, and skipping it would report an unmeasured
            # meta-check as a pass.
            raise SystemExit(
                "FAIL: coverage_floor_policy still declares "
                + ", ".join(declared)
                + ", but nothing in the tracked listing resolves against them. Fix the "
                "spelling, track the file, or declare the sub-key absent with "
                "`deliberately_absent: coverage_floor_policy.<sub-key>`."
            )
        # DECLARED ABSENT. No lefthook and no CI workflows is a legitimate repo shape --
        # it is the shape the reported consumer has -- and there is then NO operational
        # side to reconcile against. Reporting every discovered gate as `orphaned` here
        # would be a verdict over an empty comparison: "compared nothing" rendered as
        # "found drift", which is the false red this whole gate exists to avoid.
        print(
            "SKIP: coverage_floor_policy declares no lefthook or CI surface, so there is "
            "nothing to reconcile discovered gates against; gate-discovery drift is "
            "unmeasured, not clean.",
            file=sys.stderr,
        )
        return
    refs = load_operational_refs(sources)
    orphaned = sorted(path for path in discovered if path not in refs)
    foreign = sorted(
        path for path in refs if matches_gate_pattern(path) and path not in discovered
    )
    if orphaned or foreign:
        lines = ["FAIL: quality-gate discovery drift detected."]
        for heading, paths in (
            ("Orphaned discovered gates:", orphaned),
            ("Operational refs not matched by gate_script_pattern:", foreign),
        ):
            if paths:
                lines.append(heading)
                lines.extend(f"  - {path}" for path in paths)
        raise SystemExit("\n".join(lines))


def load_coverage_report() -> dict[str, object]:
    report_path = REPO_ROOT / "coverage.json"
    if not report_path.is_file():
        raise SystemExit("FAIL: expected a repo-owned coverage JSON artifact such as coverage.json")
    return json.loads(report_path.read_text(encoding="utf-8"))


def classify_unfloored_files(report: dict[str, object], declared: set[str], exempted: set[str]) -> tuple[list[str], list[str]]:
    offenders: list[str] = []
    warn_band: list[str] = []
    files = report.get("files", {})
    if not isinstance(files, dict):
        raise SystemExit("FAIL: coverage report did not contain a `files` mapping")
    for path, info in sorted(files.items()):
        if not isinstance(path, str) or not path.startswith("src/") or path in declared or path in exempted:
            continue
        summary = info.get("summary", {}) if isinstance(info, dict) else {}
        statements = int(summary.get("num_statements", 0))
        percent = float(summary.get("percent_covered", 0.0))
        if statements < POLICY["min_statements_threshold"]:
            continue
        if percent < POLICY["fail_below_pct"]:
            offenders.append(f"{path}  stmts={statements} cov={percent:.2f}%")
        elif percent < POLICY["warn_ceiling_pct"]:
            warn_band.append(f"{path}  stmts={statements} cov={percent:.2f}%")
    return offenders, warn_band


def main() -> int:
    gate_paths = discover_gate_scripts()
    if not gate_paths:
        raise SystemExit("FAIL: no gate scripts matched gate_script_pattern")
    for gate_path in gate_paths:
        if not gate_path.is_file():
            raise SystemExit(f"FAIL: gate script path does not exist: {gate_path.relative_to(REPO_ROOT)}")
    meta_check_gate_scripts(gate_paths)

    declared = collect_declared_floors(gate_paths)
    exempted = collect_exemptions()
    contradictions = sorted(declared & exempted)
    if contradictions:
        raise SystemExit(
            "FAIL: the following paths are both floored and exempted:\n"
            + "\n".join(f"  - {path}" for path in contradictions)
        )

    offenders, warn_band = classify_unfloored_files(load_coverage_report(), declared, exempted)
    if warn_band:
        print("WARN: unfloored files in warn-band:", file=sys.stderr)
        for line in warn_band:
            print(f"  - {line}", file=sys.stderr)
    if offenders:
        print("FAIL: unfloored files below fail_below_pct:", file=sys.stderr)
        for line in offenders:
            print(f"  - {line}", file=sys.stderr)
        return 1
    print(
        f"OK: {len(declared)} floored, {len(exempted)} exempted, "
        f"{len(warn_band)} in warn-band."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
