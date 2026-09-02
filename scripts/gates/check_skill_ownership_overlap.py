#!/usr/bin/env python3
"""Detect silent cross-namespace mentions between charness public skills.

Each public skill owns its `charness-artifacts/<skill-id>/` namespace and its
`.agents/<skill-id>-adapter.yaml` adapter file. When a SKILL.md, references,
or scripts under one skill mention another skill's namespace, the boundary
must be explicit -- either documented as a known cross-skill write (seed,
setup bootstrap) or as a known read (cite, spill target, evidence) --
via the allowlist at scripts/check_skill_ownership_overlap.allowlist.txt.

Silent overlap creates drift the next operator hits. This validator surfaces
the overlap so the boundary becomes a deliberate choice instead of prose-only
verification in create-skill/portable-authoring.md.

The scan itself is narrow: SKILL.md plus a NON-RECURSIVE, suffix-filtered walk of
each skill's scripts/ and references/ directories. Every run reports `scanned_files`
alongside `uncovered`, which counts the files this walk cannot structurally reach and
breaks them down by why. `uncovered.total` sums the CONTENT buckets only; generated and
vendored paths are unreachable too and are reported beside them under
`excluded_build_artifacts`, deliberately not summed, so the headline number does not
move with whether a tool last ran. Both fields are additive-only: they never change
`findings`, `status`, or the exit code.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

try:
    from scripts.yaml_output import emit_yaml
except ModuleNotFoundError:
    from scripts.yaml_output import emit_yaml

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_waiver_file_lines = import_repo_module(__file__, "scripts.core.waiver_file_lines")
iter_waiver_lines = _waiver_file_lines.iter_waiver_lines

ART_RE = re.compile(r"charness-artifacts/([a-z][a-z0-9-]*)/")
ADP_RE = re.compile(r"\.agents/([a-z][a-z0-9-]*)-adapter\.yaml")

ALLOWLIST_PATH = Path("scripts/check_skill_ownership_overlap.allowlist.txt")


def parse_allowlist(path: Path) -> tuple[set[tuple[str, str, str]], list[int]]:
    """Waiver entries, and the line numbers of entries too malformed to be one.

    `malformed` is RETURNED rather than dropped silently. A dropped entry is not in the
    allowlist, so the stale arm -- which only walks `allowlist` -- can never report it:
    a malformed entry whose overlap still exists resurfaces as a violation, but one
    whose overlap is GONE produces no finding, no stale row, and no signal of any kind.
    That is the state the stale advisory exists to make visible, so the parser reports
    its own drops instead of asserting that a resurfaced violation covers them.
    """
    if not path.is_file():
        return set(), []
    out: set[tuple[str, str, str]] = set()
    malformed: list[int] = []
    for number, line in iter_waiver_lines(path):
        parts = [p.strip() for p in line.split(":", 3)]
        # Four fields, and the fourth non-empty. The declared format carries a
        # `<reason>` and the comment below calls it REQUIRED; `len(parts) < 3` accepted
        # a reasonless three-field line, so the field that makes a waiver reviewable was
        # optional in fact. The literal template this gate itself suggests is rejected
        # too: an unedited `<reason>` is a placeholder, not a reason.
        if len(parts) < 4 or not all(parts[:3]) or not parts[3] or parts[3] == "<reason>":
            malformed.append(number)
            continue
        out.add((parts[0], parts[1], parts[2]))
    return out, malformed


def _scan_file(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for m in ART_RE.finditer(text):
        found.append(("artifact", m.group(1)))
    for m in ADP_RE.finditer(text):
        found.append(("adapter", m.group(1)))
    return found


# Path segments whose contents are generated or vendored rather than authored. Counted
# into `excluded_build_artifacts`, never into a content bucket, so `uncovered.total`
# moves with the skill tree rather than with whether a tool last ran.
#
# The rule above governs; a name missing from it is a bug against the rule. This is
# classification only -- `rglob` still enumerates these paths, so adding a name changes
# the bucket, not the walk cost. Matched against every path segment INCLUDING the
# filename, so it also governs file basenames despite the name of this constant.
_IGNORED_DIR_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".venv",
    "node_modules",
    ".git",
}

_UNCOVERED_KEYS = (
    "nested_under_scripts_or_references",
    "non_py_md_top_level",
    "skill_root_other",
)

#: Reported beside the content buckets and NOT summed into `total`, so the headline
#: number stays a property of skill content. Reported rather than dropped, because these
#: paths are unreachable by the scan too and silence would make `scanned_files +
#: uncovered.total` read as the whole tree.
_EXCLUDED_KEY = "excluded_build_artifacts"

#: The starting bucket dict, and the one reported when `skills/public/` is absent -- the
#: only case where nothing was traversed either. It carries no `total`: that is derived
#: by `_uncovered_payload`, which every publishing path calls, so the sum rule has one
#: owner.
_EMPTY_BUCKETS = {**{key: 0 for key in _UNCOVERED_KEYS}, _EXCLUDED_KEY: 0}


def _uncovered_counts(skill_dir: Path) -> dict[str, int]:
    """Files under one skill directory the scan above structurally cannot reach.

    Walked ONCE per skill over the same directory scan() already opens the top of --
    not a second gate, not another gate's output. Every file is classified by WHY the
    .py/.md walk above misses it: nested more than one level beneath scripts/ or
    references/ (no recursion, so depth alone hides it regardless of suffix), sitting
    at that top level but carrying some other suffix (the suffix filter drops it), or
    anywhere else under the skill root other than SKILL.md itself (no directory but
    scripts/ and references/ is ever opened, so another top-level file or an entirely
    different subdirectory is unread in full). The three buckets are disjoint by
    construction and their sum is this skill's whole unreachable CONTENT population.
    Build-artifact paths are unreachable too and are counted separately into
    `excluded_build_artifacts` rather than dropped silently -- leaving them out of both
    walks made `scanned_files + total` read as the whole tree when it was not. No count
    here is frozen; every one is recomputed from the tree on each run.
    """
    counts = {key: 0 for key in _UNCOVERED_KEYS}
    counts[_EXCLUDED_KEY] = 0
    for path in skill_dir.rglob("*"):
        if not path.is_file():
            continue
        parts = path.relative_to(skill_dir).parts
        if _IGNORED_DIR_PARTS.intersection(parts):
            counts[_EXCLUDED_KEY] += 1
            continue
        if parts == ("SKILL.md",):
            continue
        if len(parts) >= 2 and parts[0] in ("scripts", "references"):
            if len(parts) == 2:
                if path.suffix not in {".py", ".md"}:
                    counts["non_py_md_top_level"] += 1
            else:
                counts["nested_under_scripts_or_references"] += 1
        else:
            counts["skill_root_other"] += 1
    return counts


def _unwalked_payload(
    findings: list[dict],
    *,
    skill_count: int = 0,
    uncovered_totals: dict[str, int] | None = None,
) -> dict:
    """The payload for a run that READ NO FILE.

    One owner for every way that happens -- `skills/public/` absent, present but
    holding no skill directory, or holding only directories with nothing readable in
    them. These were two shapes: the absent arm returned here and withheld
    `did_not_judge`, while the others fell through to the normal return and PUBLISHED
    one, naming gaps for a walk that read nothing.

    Withholds `did_not_judge`, which cannot be established without a read, and
    PUBLISHES the real `uncovered` counts, which can. The first cut hardcoded those to
    zero, so a skill tree holding an unreachable file with a live cross-namespace
    mention in it reported `uncovered.total: 0`: the over-claim of judgment was removed
    by adding an under-claim of gap, one field over, in the fix for it.
    `scanned_files: 0` beside a nonzero `uncovered.total` is the honest shape --
    nothing was read, and here is how much was there to miss.

    `stale_allowlist: []` is PUBLISHED, not withheld, and that is a decision this repo
    made deliberately -- see `test_a_tree_with_no_public_skills_claims_no_staleness`.
    An unrun scan cannot call a waiver dead, and the empty list says none was called
    dead. `main()` reads the key unconditionally, so withholding it would raise.
    """
    return {
        "findings": findings,
        "scanned_skills": skill_count,
        "scanned_files": 0,
        # `is None`, not truthiness: absent means no traversal, and an all-zero dict is a
        # real measurement of a tree with nothing to miss. (Today the dict is always
        # non-empty and so always truthy, which makes this defensive rather than a live
        # repair -- stated so nobody reads it as a bug that was found.)
        "uncovered": _uncovered_payload(_EMPTY_BUCKETS if uncovered_totals is None else uncovered_totals),
        "stale_allowlist": [],
    }


def _uncovered_payload(totals: dict[str, int]) -> dict[str, int]:
    """`totals` plus the derived `total`, which sums the CONTENT buckets only.

    `excluded_build_artifacts` is reported beside them and deliberately left out, so
    the headline number does not swing with whether pytest last wrote bytecode.

    EVERY path that publishes `uncovered` routes through here, including the
    nothing-was-walked one -- so the key set and the `total` arithmetic cannot diverge
    between them. The first cut kept a separate all-zero literal for that path, which
    is a second source of truth for a shape one docstring already claimed was shared.
    """
    return {
        **totals,
        "total": sum(value for key, value in totals.items() if key != _EXCLUDED_KEY),
    }


def _partition_public_root(public_root: Path) -> tuple[list[Path], int]:
    """`(skill directories, files under ignored directories at this level)`.

    The ignore rule has to be applied HERE as well as inside `_uncovered_counts`,
    which tests segments RELATIVE to the skill directory and so never tests the skill's
    own name: a `skills/public/__pycache__/` was counted as a skill, and its files
    landed in a CONTENT bucket and were summed into `uncovered.total` -- the "moves with
    whether a tool last ran" outcome the rule exists to prevent.

    Returns the count rather than discarding it. The first cut of that fix skipped
    ignored directories entirely, which dropped their files from `excluded_build_artifacts`
    too -- and that field's published `did_not_judge` line asserts it counts exactly these
    paths. Excluding them from the CONTENT buckets is the point; excluding them from the
    accounting made a shipped report field false.
    """
    skills: list[Path] = []
    excluded = 0
    for entry in sorted(public_root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in _IGNORED_DIR_PARTS:
            excluded += sum(1 for path in entry.rglob("*") if path.is_file())
            continue
        skills.append(entry)
    return skills, excluded


def _readable_files(skill_dir: Path) -> list[Path]:
    """SKILL.md plus the non-recursive, suffix-filtered top level of scripts/ and
    references/. Everything this misses is counted by `_uncovered_counts`."""
    files: list[Path] = []
    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        files.append(skill_md)
    for sub in ("scripts", "references"):
        sub_dir = skill_dir / sub
        if sub_dir.is_dir():
            files.extend(
                p for p in sorted(sub_dir.iterdir())
                if p.is_file() and p.suffix in {".py", ".md"}
            )
    return files


def scan(repo_root: Path, allowlist: set[tuple[str, str, str]]) -> dict:
    public_root = repo_root / "skills" / "public"
    findings: list[dict] = []
    consumed: set[tuple[str, str, str]] = set()
    if not public_root.is_dir():
        return _unwalked_payload(findings)
    skill_count = 0
    scanned_files = 0
    uncovered_totals = dict(_EMPTY_BUCKETS)
    skill_dirs, top_level_excluded = _partition_public_root(public_root)
    uncovered_totals[_EXCLUDED_KEY] += top_level_excluded
    for skill_dir in skill_dirs:
        sid = skill_dir.name
        skill_count += 1
        files = _readable_files(skill_dir)
        scanned_files += len(files)
        for key, count in _uncovered_counts(skill_dir).items():
            uncovered_totals[key] += count
        for f in files:
            text = f.read_text(encoding="utf-8")
            for kind, owner in _scan_file(text):
                if owner == sid:
                    continue
                if (sid, kind, owner) in allowlist:
                    consumed.add((sid, kind, owner))
                    continue
                findings.append(
                    {
                        "skill": sid,
                        "file": str(f.relative_to(repo_root)),
                        "kind": kind,
                        "owner": owner,
                        "allowlist_entry": f"{sid}:{kind}:{owner}:<reason>",
                    }
                )
    # A waiver nobody consumed is a design decision the code no longer makes, written in
    # the present tense in a file whose entries are REQUIRED to carry a `<reason>` so the
    # boundary stays explicit. Left unreported, the allowlist can only grow: it is
    # reviewed when an entry is added and silent when one stops being needed.
    #
    # Keep this advisory because stale ownership waivers otherwise accumulate
    # silently; it is a report, not another blocking workflow.
    #
    # Advisory, not a violation, matching the sibling. A stale waiver is a documentation
    # defect, not an ownership breach, and the scan is what proves it stale -- so failing
    # the gate on it would block a correct repo on a bookkeeping lag.
    # Keyed on FILES READ, not on directories seen. `skill_count == 0` was the first
    # cut and it missed one level in: a skill directory holding no SKILL.md and no
    # readable scripts/ or references/ entry increments `skill_count` while reading
    # nothing, so a public root of only such directories fell through here and
    # published `did_not_judge` plus `uncovered.total: 0` over a walk that read no
    # file -- the exact shape this withhold exists to remove. `scanned_files == 0`
    # subsumes the directory case and is the invariant the test asserts.
    if scanned_files == 0:
        return _unwalked_payload(findings, skill_count=skill_count, uncovered_totals=uncovered_totals)
    stale = sorted(entry for entry in allowlist if entry not in consumed)
    return {
        "findings": findings,
        "scanned_skills": skill_count,
        "scanned_files": scanned_files,
        "uncovered": _uncovered_payload(uncovered_totals),
        # On every run that WALKED, including the passing one -- matching the sibling
        # gates in this repo that publish a `did_not_judge`. The caveat used to live
        # ONLY inside the stale-allowlist advisory, which is emitted conditionally --
        # so a clean run said nothing about partial coverage, which is the defect this
        # gate was changed to remove.
        #
        # Not "unconditional": a run that read no file returns above and names no gap,
        # which is right -- it judged nothing. `scanned_files == 0` is the
        # discriminator, the same condition the withhold is keyed on.
        #
        # This sentence has now been wrong twice, each time because it named a
        # DIFFERENT observable than the code branched on. It said "unconditional" while
        # an early return existed, then named `scanned_skills: 0` while that field was
        # hardcoded -- and the next round made it a real count, so the discriminator
        # silently became a false negative. Quote the branch condition, never a field
        # that merely happened to correlate with it.
        "did_not_judge": [
            "whether a cross-namespace mention sits in a file this scan cannot reach -- "
            "the walk reads SKILL.md plus the top level of scripts/ and references/, "
            ".py and .md only, so `uncovered` counts real places a mention could hide",
            "whether an excluded build-artifact path holds a mention -- "
            f"`{_EXCLUDED_KEY}` counts them and the scan reads none of them",
        ],
        "stale_allowlist": [
            {"skill": sid, "kind": kind, "owner": owner, "entry": f"{sid}:{kind}:{owner}"}
            for sid, kind, owner in stale
        ],
    }


# Folded in from the deleted human renderer. The stale rows carried only the
# entry text; the CAVEAT -- that this scan reads just the top-level .py/.md under
# each skill, so a real mention can sit outside it -- lived in the advisory prose.
# With output unconditionally YAML, dropping it would turn a hedged advisory into
# a bare "looks stale" that reads as a delete instruction.
STALE_ALLOWLIST_ADVISORY = (
    f"{ALLOWLIST_PATH} entry looks stale (this scan no longer produces that overlap; "
    "re-check the entry's reason before deleting, because the scan reads only top-level "
    ".py/.md under each skill and a real mention can sit outside it -- see `scanned_files` "
    "and `uncovered` on this same run for exactly how many files that scope leaves unread)"
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    args = ap.parse_args()
    repo_root = args.repo_root.resolve()
    allowlist, malformed = parse_allowlist(repo_root / ALLOWLIST_PATH)
    result = scan(repo_root, allowlist)
    payload: dict = {**result, "allowlist_size": len(allowlist)}
    # Published unconditionally, empty list included. A dropped waiver whose overlap is
    # already gone reaches no other field: not `findings`, not `stale_allowlist`, and it
    # only makes `allowlist_size` quietly smaller than the file's entry count. This is
    # the one place it can surface.
    payload["malformed_allowlist_lines"] = malformed
    payload["status"] = "violations" if result["findings"] else "ok"
    if result["stale_allowlist"]:
        payload["stale_allowlist_advisory"] = STALE_ALLOWLIST_ADVISORY
    emit_yaml(payload)
    return 0 if not result["findings"] else 2


if __name__ == "__main__":
    sys.exit(main())
