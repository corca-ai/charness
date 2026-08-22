"""What a claims round is REVIEWING, declared instead of improvised.

WHY, measured on one release. Four claims rounds ran; all four returned
`unproven`; ~14 blockers total; NOT ONE was in the shipped code. Every round
confirmed the quality-status owner mechanism, all five version surfaces and
every derived figure. Every blocker was prose about the review itself, living in
the goal artifact and the retro -- which ship INSIDE the bundle being reviewed.

That is a loop with no fixed point. Repairing a narrative finding changes the
bundle, which changes the record, the path count and the blocker totals, which
requires new prose that nothing has reviewed, which the next round then reads.
Repairing is what generates the next round's findings. Round 4's decisive
finding was the loop in one artifact: the durable claims record added to satisfy
round 3 landed inside the prepared commit and made a `pass` structurally
unpublishable.

v6.0.0 hit the same wall three rounds deep and STOPPED, recording "publishing on
a fourth round would be reviewing until it passes". Two releases have now paid
for this. It is a property of the loop, not of either session's carelessness.

THE FIX IS NOT "REVIEW LESS". It is to say out loud which surfaces a verdict is
ABOUT. A wrong blocker tally in a retro is a real defect and stays reported --
it just does not gate a tag, because a tag is a claim about shipped code and the
retro is not shipped code. Splitting the two lets the round converge: advisory
findings are recorded and published as known-inaccurate rather than repaired
into a new prepared commit, so there is no next round to generate.

WHAT THIS DELIBERATELY DOES NOT DO. It does not hide anything. A `pass` must
carry the advisory findings in the record (`validate_claims_review` requires the
fields), so "converged" can never mean "stopped looking". The failure mode this
guards against is the obvious one: a scope split becoming a way to launder real
findings out of a release.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

#: Paths whose defects BLOCK a tag. These are what a release is a claim about:
#: the code that ships, the notes and record an operator reads, and the version
#: surfaces an install resolves.
BLOCKING_PREFIXES = (
    "scripts/",
    "skills/",
    "plugins/",
    "tests/",
    "packaging/",
    "docs/",
    ".claude-plugin/",
    ".codex-plugin/",
    ".github/",
)

#: Exact-match files (not prefixes). `charness` as a PREFIX matched every
#: `charness-artifacts/...` path, which made the advisory-first loop ordering
#: load-bearing for an undocumented reason and left the explicit
#: `charness-artifacts/release/` entry beside it dead -- it could never be
#: reached. Exact match says what was meant: the CLI entrypoint file.
BLOCKING_EXACT = ("charness",)

#: Paths whose defects are REPORTED but do not block. Session narrative: an
#: account of how the work went, written by the same run being reviewed, and
#: revised by every repair the review provokes. Wrong counts here are real and
#: worth fixing -- on a later pass, not as a tag gate.
ADVISORY_PREFIXES = (
    "charness-artifacts/goals/",
    "charness-artifacts/retro/",
    "charness-artifacts/critique/",
    "charness-artifacts/release-review/",
    "charness-artifacts/probe/",
    "charness-artifacts/issues/",
    "charness-artifacts/quality/",
)


def classify(path: str) -> str:
    """`blocking` or `advisory` for one repo-relative path.

    Advisory means SESSION NARRATIVE, and narrative is a property of the FILE,
    not of the directory. The advisory roots also hold machine-read state that
    controls other gates -- `charness-artifacts/quality/dup-ratchet-baseline.json`
    is an input to the duplicate ratchet, `charness-artifacts/retro/lesson-ledger.json`
    is read by the SessionStart hook, `charness-artifacts/goals/*.slice-manifest.json`
    by the slice-manifest validator. A directory-only rule let a rebaselined dup
    ceiling ship as an "advisory finding": a real behaviour change, escaping
    through the lane meant for prose. Only `.md` under an advisory root is
    narrative; everything else there is blocking.

    Both loops are prefix scans and no path can match one of each (every prefix
    is slash-terminated), so the ordering between them decides nothing. It reads
    advisory-first because that is the narrower rule.
    """
    if path in BLOCKING_EXACT:
        return "blocking"
    for prefix in ADVISORY_PREFIXES:
        if path.startswith(prefix):
            return "advisory" if path.endswith(".md") else "blocking"
    for prefix in BLOCKING_PREFIXES:
        if path.startswith(prefix):
            return "blocking"
    # Unrecognised paths are BLOCKING. Fail-closed: a new top-level surface must
    # not become advisory by being unlisted, which is how a scope split turns
    # into a laundering channel.
    return "blocking"


def partition(paths: list[str]) -> dict[str, list[str]]:
    """Split a release delta into the two scopes, each sorted and deduped."""
    blocking, advisory = set(), set()
    for path in paths:
        (advisory if classify(path) == "advisory" else blocking).add(path)
    return {"blocking": sorted(blocking), "advisory": sorted(advisory)}


def scope_summary(paths: list[str]) -> dict[str, object]:
    """The partition plus counts, for embedding in a claims-review record."""
    split = partition(paths)
    return {
        "blocking_paths": split["blocking"],
        "advisory_paths": split["advisory"],
        "blocking_count": len(split["blocking"]),
        "advisory_count": len(split["advisory"]),
    }


def render_packet_scope(paths: list[str]) -> str:
    """The scope section of a claims-round packet, generated from the delta.

    Generated rather than hand-written because a hand-written scope is one more
    piece of prose that can drift from the tree -- the exact class four rounds
    kept finding.
    """
    split = partition(paths)
    lines = [
        "## What your verdict is ABOUT",
        "",
        f"BLOCKING scope ({len(split['blocking'])} paths). A defect here means "
        "`unproven` and the tag does not move:",
    ]
    lines += [f"- `{path}`" for path in split["blocking"]] or ["- (none)"]
    lines += [
        "",
        f"ADVISORY scope ({len(split['advisory'])} paths). Session narrative — an "
        "account of how the work went, written by the run under review. Report "
        "every defect you find here; it is recorded in the release record and "
        "published as known-inaccurate. It does NOT make the verdict `unproven`:",
    ]
    lines += [f"- `{path}`" for path in split["advisory"]] or ["- (none)"]
    lines += [
        "",
        "This split exists because four rounds on this release found ~14 blockers "
        "and not one was in shipped code, while repairing the narrative ones "
        "regenerated the bundle and the next round's findings. Do not "
        "treat advisory as unimportant — treat it as not-a-tag-gate.",
    ]
    return "\n".join(lines)


def assert_scope_covers_delta(scope: dict[str, Any], delta_paths: list[str]) -> None:
    """The declared scope must ACCOUNT FOR every changed path, with none invented.

    Classification-consistency alone still lets a reviewer omit an inconvenient
    path from both lists and pass. This closes that by set equality, so the
    scope is a partition of the delta rather than a selection from it.
    """
    declared = set(scope.get("blocking_paths", [])) | set(scope.get("advisory_paths", []))
    actual = set(delta_paths)
    # Only BLOCKING delta paths must be accounted for. Requiring set equality
    # over the whole delta was the first cut and is too brittle to be safe: the
    # delta includes files the PREPARE step writes (the release record itself,
    # regenerated manifests), so a reviewer would have to predict artifacts that
    # do not exist when they write the record, and a late refusal at the publish
    # boundary is expensive. Omitting an ADVISORY path costs nothing -- advisory
    # paths gate nothing by construction. Omitting a BLOCKING one is the real
    # hole, and that is what this refuses.
    missing = sorted(p for p in actual - declared if classify(p) == "blocking")
    invented = sorted(declared - actual)
    if missing:
        raise SystemExit(
            f"--resume: claims-review `review_scope` omits {len(missing)} BLOCKING changed "
            f"path(s) the release actually carries: {missing[:8]}. A `pass` must account for "
            "every shipped surface in the delta; an unlisted one is a surface nobody said "
            "they looked at."
        )
    if invented:
        raise SystemExit(
            f"--resume: claims-review `review_scope` names path(s) not in the release delta: "
            f"{invented[:8]}. A scope padded with paths the release does not touch overstates "
            "what was reviewed."
        )


def assert_scope_is_declared(data: dict[str, Any], *, verdict: str) -> None:
    """A `pass` must say what it is a verdict ABOUT, and carry what it waived.

    The scope split exists so a claims round can converge -- narrative defects
    are reported and published rather than repaired into a new prepared commit.
    The obvious way for that to rot is for the split to become a laundering
    channel: findings disappear and the record reads clean.

    So the record must carry BOTH sides. `advisory_findings` is required even
    when empty, because an absent field and an empty list read identically to a
    later auditor, and "nothing was found" must be distinguishable from "nobody
    looked". An `unproven` verdict is exempt: it is already blocking, and
    demanding scope bookkeeping from a refusal would make refusing costlier than
    passing -- the wrong gradient on a proof surface.
    """
    if verdict != "pass":
        return
    scope = data.get("review_scope")
    if not isinstance(scope, dict):
        raise SystemExit(
            "--resume: a `pass` claims-review must carry `review_scope` naming the blocking and "
            "advisory paths its verdict covers; a verdict with no declared scope cannot be audited "
            "later for what it did not look at"
        )
    for field in ("blocking_paths", "advisory_paths"):
        if not isinstance(scope.get(field), list):
            raise SystemExit(f"--resume: claims-review `review_scope.{field}` must be a list")
    if not scope["blocking_paths"]:
        raise SystemExit(
            "--resume: claims-review `review_scope.blocking_paths` is empty -- a `pass` over no "
            "blocking surface is a verdict about nothing"
        )
    # THE CHECK THAT MAKES THE REST MEAN ANYTHING. Without it the declared scope
    # is free text with no relation to the tree: a reviewer could put
    # `skills/public/release/scripts/publish_release_claims_review.py` in
    # `advisory_paths`, file a real defect in the release gate as an advisory
    # finding, and publish. A fresh-eye round found exactly that record shape
    # accepted, and named it the laundering channel this module claims to guard.
    misclassified = [
        path for path in scope["advisory_paths"] if classify(path) != "advisory"
    ]
    if misclassified:
        raise SystemExit(
            "--resume: claims-review `review_scope.advisory_paths` contains path(s) that are "
            f"NOT advisory by classification: {sorted(misclassified)}. Advisory is session "
            "narrative (`.md` under the artifact roots); a shipped surface cannot be waived by "
            "declaring it one."
        )
    mislabelled = [
        path for path in scope["blocking_paths"] if classify(path) == "advisory"
    ]
    if mislabelled:
        raise SystemExit(
            "--resume: claims-review `review_scope.blocking_paths` contains advisory path(s): "
            f"{sorted(mislabelled)}. Reporting narrative as blocking is not harmful, but the "
            "declared scope must match the classifier so a later auditor can reproduce it."
        )
    if not isinstance(data.get("advisory_findings"), list):
        raise SystemExit(
            "--resume: a `pass` claims-review must carry `advisory_findings` (use [] when the "
            "advisory scope was clean). An absent field and an empty list read identically to a "
            "later auditor, so `nothing found` must be distinguishable from `nobody looked`"
        )


def assert_scope_matches_release_delta(repo_root: Path, data: dict[str, Any], *,
                                        prepared: dict[str, str], run) -> None:
    """Check the declared scope against the delta the release actually carries.

    Classification-consistency alone still lets a reviewer omit an inconvenient
    path from both lists. This derives the real delta -- previous tag to the
    prepared commit -- and requires the scope to be a PARTITION of it.

    When the base cannot be resolved (no previous tag: a first release, or a
    shallow clone) the completeness half is SKIPPED and said out loud on stderr.
    It is not silently passed: a check that cannot run must not read as a check
    that ran, which is the defect class this whole slice exists to close. The
    classification half still runs, and that is the half that blocks the
    laundering shape a fresh-eye round demonstrated.
    """
    described = run(["git", "describe", "--tags", "--abbrev=0", f"{prepared['commit']}^"],
                    cwd=repo_root, check=False)
    base = described.stdout.strip() if described.returncode == 0 else ""
    if not base:
        sys.stderr.write(
            "WARNING (claims review): release delta base could not be resolved (no previous tag "
            "reachable from the prepared commit), so `review_scope` COMPLETENESS was not checked; "
            "only its classification was. The scope may omit changed paths.\n"
        )
        return
    listed = run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r",
                  f"{base}..{prepared['commit']}"], cwd=repo_root, check=False)
    if listed.returncode != 0:
        sys.stderr.write(
            f"WARNING (claims review): could not list the release delta {base}..prepared, so "
            "`review_scope` COMPLETENESS was not checked; only its classification was.\n"
        )
        return
    assert_scope_covers_delta(data["review_scope"], [p for p in listed.stdout.splitlines() if p])
