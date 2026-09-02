#!/usr/bin/env python3

"""Changed-line coverage for the native crates, the parity Python already has.

`release_changed_line_coverage.py` blocks a release on uncovered CHANGED Python
lines. Rust had no floor of any kind while the ratio gate counted
`native/*/src/**/*.rs` in its production denominator, so 11,891 lines could change
with nothing asking whether a test executed them.

A whole-repo percentage is deliberately NOT the answer here. This repo already
rejected that shape for the duplicate-ratio cap: a percentage pressures against
writing code near the line and says nothing about the change in front of you. The
parity with Python is a CHANGED-LINE floor -- what did THIS diff add, and did
anything run it.

Measured on this repo when this was written: `cargo llvm-cov --lcov` over
`native/repograph` is 4.8s on a warm build and reports 7,815 executable lines,
6,125 covered (78.37%). That is cheap enough to run the whole crate every time, so
unlike the Python lane there is no test-subset selection here and therefore none
of its "a subset can report a covered line as uncovered" caveat.

Direction of error, stated because it is the whole safety argument: a changed line
with NO lcov `DA:` record is not executable -- a comment, a blank, a `use`, a
declaration the compiler folded away -- and is reported as `not-executable`, never
as uncovered. A line with a `DA:` record and a zero count is uncovered. So this can
under-report (a line llvm-cov never emitted a record for is invisible to it) and
cannot over-report: it will not call an untested line covered.

NOT ARMED by default. It reports and exits 0; `--refuse-uncovered` is the opt-in
that makes it a floor. Arming it at the release boundary is a decision with its own
evidence, and the 2026-08-29 retro's ratio-cap entry is this repo's record of what
happens when a measurement is promoted to blocking a day after it is built.

Blind class:

- It judges ADDED and MODIFIED lines from `git diff --unified=0`, so a change that
  breaks a test's reach over an UNCHANGED line is invisible to it. That is the same
  blind spot the Python lane has.
- Coverage comes from `cargo llvm-cov` running the crate's own test binaries. A line
  exercised only by an integration path outside `cargo test` reads as uncovered.
- It discovers crates by `native/*/Cargo.toml`. A Rust source tree elsewhere in the
  repo is not measured and is not reported as unmeasured.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script
from scripts.subprocess_guard import run_monitored_phase, run_process
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)
_producer = import_repo_module(__file__, "scripts.mutation_coverage_producer")

HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(?P<start>\d+)(?:,(?P<count>\d+))? @@")
COVERAGE_TIMEOUT_SECONDS = 900


class RustCoverageError(RuntimeError):
    """The lane could not establish coverage. Never reported as a clean floor."""


def discover_crates(repo_root: Path) -> list[Path]:
    return sorted(path.parent for path in repo_root.glob("native/*/Cargo.toml"))


def changed_rust_lines(repo_root: Path, base_sha: str) -> dict[str, set[int]]:
    """Added/modified line numbers per changed `.rs` file, from the diff itself."""

    result = run_process(
        ["git", "-C", str(repo_root), "diff", "--unified=0", base_sha, "--", "*.rs"],
        cwd=repo_root,
        timeout_seconds=None,
    )
    if result.returncode != 0:
        raise RustCoverageError(f"git diff against {base_sha} failed: {result.stderr.strip()}")
    changed: dict[str, set[int]] = {}
    current: str | None = None
    for line in result.stdout.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
            continue
        if current is None:
            continue
        match = HUNK_RE.match(line)
        if match:
            start = int(match.group("start"))
            count = int(match.group("count") or "1")
            if count:
                changed.setdefault(current, set()).update(range(start, start + count))
    return changed


def crate_line_counts(crate: Path) -> dict[str, dict[int, int]]:
    """`{repo-relative path: {line: hit count}}` from one `cargo llvm-cov --lcov` run."""

    completed = run_monitored_phase(
        ["cargo", "llvm-cov", "--lcov", "--output-path", "/dev/stdout"],
        cwd=crate,
        phase="rust-coverage",
        timeout_seconds=COVERAGE_TIMEOUT_SECONDS,
        capture=True,
    )
    if completed.returncode != 0:
        raise RustCoverageError(
            f"cargo llvm-cov failed in {crate} with exit {completed.returncode}: "
            f"{completed.stderr.strip()[-500:]}"
        )
    counts: dict[str, dict[int, int]] = {}
    current: str | None = None
    for line in completed.stdout.splitlines():
        if line.startswith("SF:"):
            current = line[3:]
            counts.setdefault(current, {})
        elif line.startswith("DA:") and current is not None:
            raw_line, _, rest = line[3:].partition(",")
            hits = rest.split(",", 1)[0]
            try:
                counts[current][int(raw_line)] = int(hits)
            except ValueError:
                continue
    return counts


def _relative(repo_root: Path, filename: str) -> str:
    try:
        return Path(filename).resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return filename


def build_report(repo_root: Path, *, base_sha: str) -> dict[str, Any]:
    changed = changed_rust_lines(repo_root, base_sha)
    if not changed:
        # A DISCOVERED empty set: this diff touched no Rust. A real answer, and a
        # cheap pass -- but it says so rather than reporting a clean floor.
        return {
            "schema": "charness.rust_changed_line_coverage.v1",
            "base_sha": base_sha,
            "status": "empty-scope",
            "changed_files": 0,
            "changed_lines": 0,
            "covered": 0,
            "uncovered": [],
            "not_executable": 0,
            "unmeasured_files": [],
        }

    measured: dict[str, dict[int, int]] = {}
    for crate in discover_crates(repo_root):
        for filename, lines in crate_line_counts(crate).items():
            measured[_relative(repo_root, filename)] = lines

    covered = 0
    not_executable = 0
    uncovered: list[dict[str, Any]] = []
    unmeasured: list[str] = []
    for path in sorted(changed):
        file_counts = measured.get(path)
        if file_counts is None:
            # Named as changed, never measured: a crate this lane does not discover.
            # Reported, not silently folded into `not_executable`.
            unmeasured.append(path)
            continue
        for line in sorted(changed[path]):
            hits = file_counts.get(line)
            if hits is None:
                not_executable += 1
            elif hits > 0:
                covered += 1
            else:
                uncovered.append({"path": path, "line": line})
    return {
        "schema": "charness.rust_changed_line_coverage.v1",
        "base_sha": base_sha,
        "status": "established",
        "changed_files": len(changed),
        "changed_lines": sum(len(lines) for lines in changed.values()),
        "covered": covered,
        "uncovered": uncovered,
        "not_executable": not_executable,
        "unmeasured_files": unmeasured,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--base-sha", default=None, help="Defaults to the merge-base with origin/main"
    )
    parser.add_argument(
        "--refuse-uncovered",
        action="store_true",
        help="Exit non-zero when a changed executable Rust line is uncovered. OPT-IN.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    base_sha = args.base_sha or _producer.default_mutation_base_sha(repo_root)
    if not base_sha:
        emit_yaml(
            {
                "schema": "charness.rust_changed_line_coverage.v1",
                "status": "unestablished",
                "reason": "no base sha: `git merge-base origin/main HEAD` produced nothing",
            }
        )
        # Unestablished is not a pass and not a floor violation; it is its own state,
        # distinguishable by exit code from both.
        return 3
    try:
        report = build_report(repo_root, base_sha=base_sha)
    except RustCoverageError as exc:
        emit_yaml(
            {
                "schema": "charness.rust_changed_line_coverage.v1",
                "status": "unestablished",
                "base_sha": base_sha,
                "reason": str(exc),
            }
        )
        return 3
    emit_yaml(report)
    if args.refuse_uncovered and report["uncovered"]:
        print(
            f"REFUSED: {len(report['uncovered'])} changed Rust line(s) are executable and uncovered.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
