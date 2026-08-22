#!/usr/bin/env python3
"""Repo gate: a disposition's named destination must resolve.

WHY THIS EXISTS, measured rather than supposed. Four claims-review rounds on one
release (v6.3.0) produced ~14 blockers and not one was in the shipped code. The
dominant class was a disposition that named a destination it had never reached:

- `Structural follow-up: issue #N (recurs: ...)` -- shipped inside a release
  bundle pointing at no issue. It passed every existing gate, because `#N` is
  not in the form floor's placeholder vocabulary (`TODO|TBD|<...>|FIXME`) and
  `issue #N` is a perfectly well-formed disposition.
- `applied: ... publish_release_execute.py renders it` -- naming a mechanism
  that had been deleted, in the disposition for the finding about hardcoded
  claims that had stopped being true.
- `applied: recorded in the goal's Coordination Cues` -- naming a section that
  held only unfilled scaffold prose.

The disposition form floor states its own scope out loud: "form/enum only
(never a content classifier)", deferring substance to a fresh-eye review. That
is a defensible split and this gate does not touch it. It owns the DECIDABLE
middle the split left unclaimed:

    form      -- a disposition is present and well-shaped   (skill-side floors)
    referent  -- the thing it names is real                 (THIS gate)
    substance -- the thing it names is the right thing      (fresh-eye review)

"Is `#N` an issue number?" and "does this path exist?" need no judgment. Asking
a human reviewer to catch them is what four rounds proved does not work: the
same authoring mistake was caught in 0 seconds by the release-notes linter,
which re-derives its numbers, and took four rounds in the goal/retro artifacts,
which do not.

SCOPE. Repo-internal, like `check_spec_evidence_durability`: wired from this
repo's own `run-quality.sh`, not from a consumer install. Date-anchored so
frozen artifacts are reported and never rewritten -- editing a frozen retro so a
checker goes green is evidence edited to fit a gate, which this repo has had to
correct on more than one floor.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.artifact_quantities import inconsistent_quantities  # noqa: E402
from scripts.artifact_referents import (  # noqa: E402
    check_disposition_referents,
    git_commit_exists,
    unresolvable_shas,
)

#: `git cat-file` per SHA per artifact would be thousands of subprocesses across
#: the corpus. Same SHA, same answer, so resolve each once per run.
_SHA_CACHE: dict[str, bool] = {}


def _cached_commit_exists(sha: str, repo_root: Path) -> bool:
    key = f"{repo_root}:{sha}"
    if key not in _SHA_CACHE:
        _SHA_CACHE[key] = git_commit_exists(sha, repo_root)
    return _SHA_CACHE[key]

#: Artifacts dated from here forward are ENFORCED. Earlier ones are counted and
#: reported. This is the date the gate landed.
ENFORCED_FROM = date(2026, 8, 22)

#: Families whose dispositions ship inside release bundles and are read as
#: statements of fact by later sessions.
SCANNED_GLOBS = (
    "charness-artifacts/goals/*.md",
    "charness-artifacts/retro/*.md",
)

#: A line that DISPOSITIONS something -- claims an improvement was routed
#: somewhere. Only these lines are checked; ordinary narrative prose that
#: happens to mention a path is not a disposition and is not this gate's
#: business.
DISPOSITION_LINE_RE = re.compile(
    r"^[\s>*+-]*(?:Retro dispositions|Structural follow-up|Decision|applied|tracked issue)\s*:",
    re.IGNORECASE,
)

#: `applied:` / `tracked issue:` also appear mid-line inside a bullet, e.g.
#: "``applied: skills/... now stamps ...``". Catch those too.
INLINE_DISPOSITION_RE = re.compile(r"\b(?:applied|tracked issue)\s*:", re.IGNORECASE)

_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")


def date_from_filename(path: Path) -> date | None:
    match = _DATE_RE.match(path.name)
    if match is None:
        return None
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None


def is_enforced(path: Path) -> bool:
    """Enforced unless the filename carries a readable date BEFORE the cutoff.

    Fail-CLOSED on an undatable filename, mirroring the durability gate: an
    undated name must not buy a permanent exemption.
    """
    observed = date_from_filename(path)
    if observed is None:
        return True
    return observed >= ENFORCED_FROM


def disposition_lines(text: str) -> list[tuple[int, str]]:
    """Every disposition-bearing line, 1-indexed, fenced blocks excluded.

    Fenced blocks are skipped because this repo quotes BROKEN dispositions inside
    fences when explaining a defect -- including in this gate's own test fixtures
    and in the retro that motivated it. A gate that fired on its own worked
    example would teach authors to stop quoting evidence.
    """
    out: list[tuple[int, str]] = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if DISPOSITION_LINE_RE.match(line) or INLINE_DISPOSITION_RE.search(line):
            out.append((number, line))
    return out


def _display_path(path: Path, repo_root: Path) -> str:
    """Repo-relative when possible, absolute otherwise.

    `--path` accepts a file outside the repo (a fixture under /tmp, which is how
    this gate's own negative control runs), and `Path.relative_to` RAISES on
    that rather than returning something. A checker that crashes on an
    out-of-tree input is a checker whose negative control cannot be written.
    """
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def audit_file(path: Path, repo_root: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    enforced = is_enforced(path)
    findings: list[dict[str, object]] = []
    for number, line in disposition_lines(text):
        for finding in check_disposition_referents(line, repo_root):
            findings.append({
                "file": _display_path(path, repo_root),
                "line": number,
                "enforced": enforced,
                **finding,
            })
    for finding in inconsistent_quantities(text):
        first = finding["sites"][0]["line"] if finding["sites"] else 1
        findings.append({
            "file": _display_path(path, repo_root),
            "line": first,
            # Self-consistency is enforced wherever markers are USED. There is no
            # grandfathering question: an artifact with no `{{q:}}` markers cannot
            # produce a finding, so this can never fire on frozen history.
            "enforced": True,
            "kind": finding["kind"],
            "token": str(finding["id"]),
            "detail": str(finding["detail"]),
        })

    # SHA enforcement is DATED, never fail-closed-on-undatable, and that
    # asymmetry with the disposition rung above is deliberate.
    #
    # `#N` was never a valid issue reference -- it was wrong the moment it was
    # typed, so an undatable artifact carrying one is fail-closed. A commit SHA
    # is different in kind: it can be correct when written and STOP resolving
    # later, when a branch is squashed, a worktree is pruned, or history is
    # rewritten. Blocking an undated rolling digest (`recent-lessons.md`) for
    # citing a commit that has since been rebased away would be punishing an
    # author for a change made after they wrote it -- and the remedy a blocking
    # gate pushes toward is editing a frozen record so a checker goes green,
    # which is the failure this repo has corrected on more than one floor.
    observed = date_from_filename(path)
    sha_enforced = observed is not None and observed >= ENFORCED_FROM
    seen: set[tuple[int, str]] = set()
    for number, line in enumerate(text.splitlines(), 1):
        for sha in unresolvable_shas(line, repo_root, run=_cached_commit_exists):
            if (number, sha) in seen:
                continue
            seen.add((number, sha))
            findings.append({
                "file": _display_path(path, repo_root),
                "line": number,
                "enforced": sha_enforced,
                "kind": "unresolvable-commit-ref",
                "token": sha,
                "detail": (
                    f"`{sha}` does not resolve to a commit. A citation to a commit that is "
                    "not there cannot be checked by a later reader, and a SHA attributed to "
                    "the wrong thing reads exactly like one attributed to the right thing."
                ),
            })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", default=".", help="Repo root that owns charness-artifacts/")
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON")
    parser.add_argument(
        "--path", action="append", default=[],
        help="Audit only these files (repeatable); defaults to the scanned globs",
    )
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()

    if args.path:
        targets = [Path(p) if Path(p).is_absolute() else repo_root / p for p in args.path]
    else:
        targets = sorted({p for glob in SCANNED_GLOBS for p in repo_root.glob(glob)})

    findings: list[dict[str, object]] = []
    for target in targets:
        if target.is_file():
            findings.extend(audit_file(target, repo_root))

    blocking = [f for f in findings if f["enforced"]]
    grandfathered = [f for f in findings if not f["enforced"]]
    report = {
        "scanned": len(targets),
        "findings": len(findings),
        "blocking": len(blocking),
        "grandfathered": len(grandfathered),
        "enforced_from": ENFORCED_FROM.isoformat(),
        "status": "blocked" if blocking else "clean",
        "blocking_findings": blocking,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"scanned: {report['scanned']} artifact(s)")
        print(f"enforced_from: {report['enforced_from']}")
        print(f"grandfathered (reported, not rewritten): {report['grandfathered']}")
        print(f"status: {report['status']}")
        for finding in blocking:
            print(f"- [blocking] {finding['file']}:{finding['line']} {finding['kind']}: {finding['detail']}")
        for finding in grandfathered:
            print(f"- [grandfathered] {finding['file']}:{finding['line']} {finding['kind']}: `{finding['token']}`")

    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
