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
alongside `uncovered`, the count of files under each skill root this walk cannot
structurally reach, broken down by why (nested beneath scripts/ or references/, wrong
suffix at that top level, or anywhere else under the skill root besides SKILL.md).
Both are additive-only: they never change `findings`, `status`, or the exit code.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from scripts.yaml_output import emit_yaml
except ModuleNotFoundError:
    from yaml_output import emit_yaml

ART_RE = re.compile(r"charness-artifacts/([a-z][a-z0-9-]*)/")
ADP_RE = re.compile(r"\.agents/([a-z][a-z0-9-]*)-adapter\.yaml")

ALLOWLIST_PATH = Path("scripts/check_skill_ownership_overlap.allowlist.txt")


def parse_allowlist(path: Path) -> set[tuple[str, str, str]]:
    if not path.is_file():
        return set()
    out: set[tuple[str, str, str]] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(":", 3)]
        if len(parts) < 3:
            continue
        out.add((parts[0], parts[1], parts[2]))
    return out


def _scan_file(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for m in ART_RE.finditer(text):
        found.append(("artifact", m.group(1)))
    for m in ADP_RE.finditer(text):
        found.append(("adapter", m.group(1)))
    return found


# Directory names walked past rather than counted, matching this repo's existing
# file-tree-walk idiom (check_doc_links.py, check_coverage.py, source_guard_scan_lib.py,
# among others): build artifacts are not skill content, and counting them would make the
# uncovered total move with whether a test happened to run first rather than with the
# skill tree itself.
#
# The set is the union of what those three siblings skip, not a narrower guess. A first
# cut listed only `__pycache__` while claiming to match them; this file is EXPORTED, and
# a consumer with `node_modules/` or `.venv/` under a skill root would have gotten both
# a slow recursive walk and a `skill_root_other` in the thousands.
#
# These files are unreachable by the scan too, so they are REPORTED as their own count
# rather than dropped silently -- see `excluded_build_artifacts`.
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

#: Reported beside the buckets but NOT summed into `total`. These are unreachable by the
#: scan as well, so leaving them uncounted made `scanned_files + uncovered.total` look
#: like the whole tree when it was not -- on this repo the gap was several hundred files
#: against a published total in the tens. Kept out of `total` so the headline number
#: stays a property of skill CONTENT rather than of whether a test ran first, and
#: reported so the identity `scanned + total + excluded == walked` is checkable.
_EXCLUDED_KEY = "excluded_build_artifacts"

_EMPTY_UNCOVERED = {**{key: 0 for key in _UNCOVERED_KEYS}, _EXCLUDED_KEY: 0, "total": 0}


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
            counts["excluded_build_artifacts"] += 1
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


def scan(repo_root: Path, allowlist: set[tuple[str, str, str]]) -> dict:
    public_root = repo_root / "skills" / "public"
    findings: list[dict] = []
    consumed: set[tuple[str, str, str]] = set()
    if not public_root.is_dir():
        return {
            "findings": findings,
            "scanned_skills": 0,
            "scanned_files": 0,
            "uncovered": dict(_EMPTY_UNCOVERED),
            "stale_allowlist": [],
        }
    skill_count = 0
    scanned_files = 0
    uncovered_totals = {key: 0 for key in _UNCOVERED_KEYS}
    uncovered_totals[_EXCLUDED_KEY] = 0
    for skill_dir in sorted(public_root.iterdir()):
        if not skill_dir.is_dir():
            continue
        sid = skill_dir.name
        skill_count += 1
        files: list[Path] = []
        skill_md = skill_dir / "SKILL.md"
        if skill_md.is_file():
            files.append(skill_md)
        for sub in ("scripts", "references"):
            sub_dir = skill_dir / sub
            if sub_dir.is_dir():
                for p in sorted(sub_dir.iterdir()):
                    if p.is_file() and p.suffix in {".py", ".md"}:
                        files.append(p)
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
    # The repo already decided this posture and already built it -- the header of
    # `scripts/validate_scenario_conditional_reads.allowlist.txt` says a waiver that is no
    # longer needed is "surfaced as a stale-allowlist advisory, never silently dropped",
    # and `validate_scenario_conditional_reads.py` implements it. This is that same
    # sentence applied to the other allowlist, not a new principle.
    #
    # Advisory, not a violation, matching the sibling. A stale waiver is a documentation
    # defect, not an ownership breach, and the scan is what proves it stale -- so failing
    # the gate on it would block a correct repo on a bookkeeping lag.
    stale = sorted(entry for entry in allowlist if entry not in consumed)
    return {
        "findings": findings,
        "scanned_skills": skill_count,
        "scanned_files": scanned_files,
        # `total` sums the three CONTENT buckets only. `excluded_build_artifacts` is
        # reported beside them and deliberately left out, so the headline number does
        # not swing with whether pytest last wrote bytecode.
        "uncovered": {
            **uncovered_totals,
            "total": sum(
                value for key, value in uncovered_totals.items() if key != _EXCLUDED_KEY
            ),
        },
        # Unconditional, matching the three sibling gates in this repo that publish a
        # `did_not_judge`. The caveat used to live ONLY inside the stale-allowlist
        # advisory, which is emitted conditionally -- so a clean run said nothing about
        # partial coverage, which is the defect this gate was changed to remove.
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
    allowlist = parse_allowlist(repo_root / ALLOWLIST_PATH)
    result = scan(repo_root, allowlist)
    payload: dict = {**result, "allowlist_size": len(allowlist)}
    payload["status"] = "violations" if result["findings"] else "ok"
    if result["stale_allowlist"]:
        payload["stale_allowlist_advisory"] = STALE_ALLOWLIST_ADVISORY
    emit_yaml(payload)
    return 0 if not result["findings"] else 2


if __name__ == "__main__":
    sys.exit(main())
