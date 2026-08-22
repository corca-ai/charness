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
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.artifact_quantities import inconsistent_quantities  # noqa: E402
from scripts.critique_enforcement_scope import date_from_filename  # noqa: E402
from scripts.repo_path_display import display_path as _display_path  # noqa: E402

from scripts.artifact_referents import (  # noqa: E402
    DISPOSITION_LINE_RE,
    INLINE_DISPOSITION_RE,
    ResolverUnavailable,
    check_disposition_referents,
    git_commit_exists,
    sha_candidates,
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

# The disposition vocabulary is IMPORTED, not redefined. Two near-identical
# copies existed after round 1; the failure mode is not "they drift" but "one
# grows and the other silently degrades" -- adding a keyword here would have
# quietly reverted the library's value-scoping to whole-line behaviour,
# reintroducing the M2 and M3 evasions at once.

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



def audit_file(path: Path, repo_root: Path, scope: dict[str, int]) -> list[dict[str, object]]:
    """Findings for one artifact, accumulating SCOPE counters into `scope`.

    The counters exist because a gate that silently drops part of its own scope
    prints the same clean line as one with nothing to drop -- a lesson this
    session recorded and this gate then violated. `dispositions` and
    `shas_resolved` must be NUMBERS in the report so a regex that stopped
    matching, or a resolver that stopped answering, is visible as a scope
    collapse rather than as a pass.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    enforced = is_enforced(path)
    findings: list[dict[str, object]] = []
    for number, line in disposition_lines(text):
        scope["dispositions"] += 1
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
        try:
            bad_shas = unresolvable_shas(line, repo_root, run=_cached_commit_exists)
        except ResolverUnavailable as exc:
            # Named, counted, and NOT silently clean. The run continues -- a
            # missing resolver must not block -- but the report says the rung
            # stood down and why.
            scope["sha_resolver_unavailable"] += 1
            scope.setdefault("sha_resolver_reason", str(exc))  # type: ignore[arg-type]
            break
        # Count TOKENS actually put to the resolver, not lines walked. The
        # previous per-line increment could not fall even if `SHA_RE` stopped
        # matching entirely, which is the exact blindness the counter exists to
        # remove.
        scope["shas_resolved"] += len(sha_candidates(line))
        for sha in bad_shas:
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
    scope: dict[str, int] = {
        "dispositions": 0, "shas_resolved": 0, "sha_resolver_unavailable": 0,
    }
    unreadable: list[str] = []
    for target in targets:
        if not target.is_file():
            # A `--path` that names nothing, or names a directory, is an INPUT
            # ERROR and must not read as a pass. Silently skipping it while
            # still counting it in `scanned` made a typo'd wiring line
            # indistinguishable from a clean run -- the gate asserting it
            # scanned a file it never opened.
            unreadable.append(_display_path(target, repo_root))
            continue
        findings.extend(audit_file(target, repo_root, scope))

    #: "ran, established nothing" -- the runner's own byte for a lane that could
    #: not judge part of its scope. Opted into per label in run-quality.sh.
    UNESTABLISHED_EXIT = 3

    blocking = [f for f in findings if f["enforced"]]
    grandfathered = [f for f in findings if not f["enforced"]]
    empty_corpus = not args.path and not targets
    status = "blocked" if (blocking or unreadable or empty_corpus) else "clean"
    report = {
        "scanned": len(targets) - len(unreadable),
        "unreadable": unreadable,
        # Scope is reported as NUMBERS so a regex that stopped matching, or a
        # resolver that stopped answering, shows up as a collapse rather than as
        # a pass. Without these, a corpus-wide false negative prints byte-for-byte
        # the same line as a real clean run.
        "dispositions_examined": scope["dispositions"],
        "shas_resolved": scope["shas_resolved"],
        "sha_resolver_unavailable_files": scope["sha_resolver_unavailable"],
        "sha_resolver_reason": scope.get("sha_resolver_reason"),
        "findings": len(findings),
        "blocking": len(blocking),
        "grandfathered": len(grandfathered),
        "enforced_from": ENFORCED_FROM.isoformat(),
        "empty_corpus": empty_corpus,
        "status": status,
        "blocking_findings": blocking,
    }

    print(f"scanned: {report['scanned']} artifact(s)")
    print(f"dispositions_examined: {report['dispositions_examined']}")
    print(f"shas_resolved: {report['shas_resolved']}")
    if report["sha_resolver_unavailable_files"]:
        # `WARNING:` is load-bearing, not decoration: run-quality.sh prints a
        # PASSING gate's log only when it matches (WARNING|WARN|WEAK|ADVISORY),
        # and a passing phase's log is deleted at EXIT. Without the token the
        # stand-down was invisible AND its explanation was destroyed.
        print(
            f"WARNING: sha_rung STOOD DOWN on {report['sha_resolver_unavailable_files']} "
            f"file(s) — {report['sha_resolver_reason']}"
        )
    print(f"enforced_from: {report['enforced_from']}")
    print(f"grandfathered (reported, not rewritten): {report['grandfathered']}")
    if report["unreadable"]:
        print(f"UNREADABLE (input error, not a pass): {', '.join(report['unreadable'])}")
    if report["empty_corpus"]:
        print("EMPTY CORPUS: the scanned globs matched nothing — a clean verdict here "
              "would mean the gate found nothing to look at, not that nothing was wrong")
    print(f"status: {report['status']}")
    for finding in blocking:
        print(f"- [blocking] {finding['file']}:{finding['line']} {finding['kind']}: {finding['detail']}")
    for finding in grandfathered:
        print(f"- [grandfathered] {finding['file']}:{finding['line']} {finding['kind']}: `{finding['token']}`")

    # Derived from `status`, NOT recomputed from `blocking`. An earlier version
    # returned `1 if blocking else 0` while `status` also accounted for unreadable
    # inputs and an empty corpus -- so the gate printed `status: blocked` and
    # exited 0. A message that disagrees with the exit code is worse than either
    # alone: the runner believes the code, the human believes the message.
    if status != "clean":
        return 1
    # A rung that could not run did not pass. Exit 3 keeps this off the runner's
    # PASS line without laundering it into a failure -- the distinction the
    # runner's own comment says cost this repo a cycle and two dead guards.
    if report["sha_resolver_unavailable_files"]:
        return UNESTABLISHED_EXIT
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
