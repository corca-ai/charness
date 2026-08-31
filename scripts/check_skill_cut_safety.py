#!/usr/bin/env python3
"""Pre-cut lossless + contract-safe check for public/support SKILL.md body edits.

Before a skill-body cut lands, two questions must be answered *before* a late gate
rejects the edit (the WS-B instrument gap from recent-lessons):

- contract-safe: does the cut remove a phrase that a CORE/PACKAGE contract or a
  ``tests/`` literal pins? Removing a pinned phrase deterministically breaks a
  gate or test, so this is a hard BLOCK.
- lossless: does a removed prose line survive somewhere (a reference home or
  elsewhere in the body), or did its content vanish? A vanished line is either a
  *justified no-op deletion* (the §5 no-op test — legitimate, needs no reference
  home) or an *accidental lossy cut*. A deterministic check cannot tell these two
  apart (that is the behavioral no-op judgment), so a reference-home gap is
  surfaced for REVIEW, never auto-blocked. Blocking "every removed line must
  reappear in a reference" would forbid the prune cure that the diagnosis-first
  doctrine depends on.

This composes the existing deterministic surfaces rather than re-implementing
them: ``check_skill_contracts`` owns the CORE/PACKAGE/FORBIDDEN pin phrases and
``check_prose_pin`` owns the ``tests/`` literal-pin scan. The value here is a
single pre-cut report, keyed to the lines a cut actually removes, that turns the
manual lossless+contract-safe ritual into one declarative command.

Exit status: 1 when any BLOCK (contract or test pin) is present; 0 otherwise
(reference-home gaps are REVIEW-only and do not fail the command). Use ``--strict``
to also fail on REVIEW items when a caller wants the stricter gate.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)
_prose_pin = import_repo_module(__file__, "scripts.check_prose_pin")
_contracts = import_repo_module(__file__, "scripts.check_skill_contracts")

# A removed line is "prose worth a reference home" only when it carries a human
# phrase; reuse the prose-pin threshold so identifiers, short tokens, bare list
# punctuation, and blank markup do not masquerade as lossy content.
MIN_PROSE_LENGTH = _prose_pin.MIN_PROSE_LENGTH


def _is_skill_md(rel: str) -> bool:
    parts = Path(rel).parts
    return (
        len(parts) == 4
        and parts[0] == "skills"
        and parts[1] in {"public", "support"}
        and parts[3] == "SKILL.md"
    )


def _is_skill_surface_path(rel: str) -> bool:
    """SKILL.md or a references/*.md contract home under a public/support skill,
    OR a skills/shared/references/*.md cross-skill contract.

    Scoped to the deletion-finding pass only (``deleted_skill_surfaces``) --
    ``skills/shared`` has no per-skill SKILL.md layer (it is
    ``skills/shared/references/*.md`` directly, cited by many skills), so a
    deleted shared reference is just as irreversible to lose as a deleted
    public/support one, but ``_is_skill_md`` and the CORE/PACKAGE contract checks
    stay public/support-only since ``skills/shared`` has no SKILL.md to key on.
    """
    parts = Path(rel).parts
    if len(parts) < 2 or parts[0] != "skills":
        return False
    if parts[1] == "shared":
        return len(parts) >= 4 and parts[2] == "references" and parts[-1].endswith(".md")
    if parts[1] not in {"public", "support"}:
        return False
    if _is_skill_md(rel):
        return True
    return len(parts) >= 5 and parts[3] == "references" and parts[-1].endswith(".md")


def changed_skill_md(repo_root: Path, *, staged: bool = False) -> list[str]:
    """Changed (non-deleted) public/support SKILL.md paths in the diff vs HEAD."""
    rows = _prose_pin.changed_status(repo_root, staged=staged)
    return sorted({new for code, _old, new in rows if code != "D" and _is_skill_md(new)})


def deleted_skill_surfaces(repo_root: Path, *, staged: bool = False) -> list[str]:
    """Deleted (git status ``D``) public/support skill surfaces -- SKILL.md or a
    references/*.md contract home -- in the diff vs HEAD.

    ``changed_skill_md`` filters ``code != "D"``, so a whole-file deletion never
    reaches the default target list; a maximal cut (delete the whole skill) then
    silently produced zero findings. This is the deliberate second pass over the
    SAME diff that a deletion cannot structurally escape: each path returned here
    becomes a forced REVIEW question, never a silent pass.
    """
    rows = _prose_pin.changed_status(repo_root, staged=staged)
    return sorted({old for code, old, _new in rows if code == "D" and _is_skill_surface_path(old)})


def _package_reference_text(repo_root: Path, rel: str) -> str:
    """Concatenated current text of the skill's references/*.md (a reference home)."""
    refs_dir = repo_root / Path(rel).parent / "references"
    if not refs_dir.is_dir():
        return ""
    parts: list[str] = []
    for ref in sorted(refs_dir.rglob("*")):
        if ref.is_file() and ref.suffix in _contracts.REFERENCE_CONTRACT_SUFFIXES:
            parts.append(ref.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def contract_pin_breaks(repo_root: Path, rel: str) -> list[dict[str, Any]]:
    """CORE/PACKAGE pins for ``rel`` that the post-edit state no longer satisfies.

    After-state, not removed-line matching: a pin break is exactly "a pinned phrase
    is no longer present where the contract requires it", which a removed (or
    multi-line-broken) phrase triggers directly.
    """
    breaks: list[dict[str, Any]] = []
    skill_md = repo_root / rel
    if not skill_md.is_file():
        return breaks
    body = skill_md.read_text(encoding="utf-8")
    package = body + "\n" + _package_reference_text(repo_root, rel)
    for pin in _contracts.CORE_CONTRACTS.get(rel, ()):
        if pin not in body:
            breaks.append({"severity": "block", "kind": "core-contract", "phrase": pin})
    for pin in _contracts.PACKAGE_CONTRACTS.get(rel, ()):
        if pin not in package:
            breaks.append({"severity": "block", "kind": "package-contract", "phrase": pin})
    return breaks


def _preview(text: str, width: int = 100) -> str:
    return text if len(text) <= width else text[: width - 3] + "..."


def reference_home_gaps(
    repo_root: Path, rel: str, *, removed: list[str] | None = None
) -> list[dict[str, Any]]:
    """Removed prose lines whose content does not survive in the body or a reference.

    Each gap is a REVIEW item: confirm it is a justified no-op deletion (the §5
    no-op test) or re-home its content. Exact-substring survival is used, so a
    moved-and-reworded line may surface as a gap — the reviewer confirms.
    """
    skill_md = repo_root / rel
    if not skill_md.is_file():
        return []
    body = skill_md.read_text(encoding="utf-8")
    refs = _package_reference_text(repo_root, rel)
    gaps: list[dict[str, Any]] = []
    seen: set[str] = set()
    lines = _prose_pin.removed_lines(repo_root, rel) if removed is None else removed
    for line in lines:
        if line in seen:
            continue
        if len(line) < MIN_PROSE_LENGTH or " " not in line.strip():
            continue
        if line in body or line in refs:
            continue
        seen.add(line)
        gaps.append({"severity": "review", "kind": "reference-home-gap", "phrase": _preview(line)})
    return gaps


def test_pin_breaks(
    repo_root: Path,
    rel: str,
    test_roots: list[Path],
    *,
    removed: list[str] | None = None,
) -> list[dict[str, Any]]:
    """``tests/`` literal pins on lines this cut removed, that no longer survive.

    Reuses the `check_prose_pin` removed-line + test-literal scan, then suppresses a
    finding whose literal still appears elsewhere in the post-edit SKILL.md body: an
    ``assert "X" in skill_text`` pin only breaks when X is *gone* from the body, so a
    phrase moved off one line but still present elsewhere (e.g. the same command in
    another bullet) is not a real break. This keeps the heuristic's coverage while
    removing the diff-only over-report.
    """
    skill_md = repo_root / rel
    body = skill_md.read_text(encoding="utf-8") if skill_md.is_file() else ""
    removed_blob = "\n".join(
        _prose_pin.removed_lines(repo_root, rel) if removed is None else removed
    )
    if not removed_blob:
        return []
    breaks: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for literal, test_path, lineno in _prose_pin.test_string_literals(test_roots):
        if not _prose_pin._prose_candidate(literal):
            continue
        if literal not in removed_blob or literal in body:
            continue
        key = (literal, test_path.as_posix())
        if key in seen:
            continue
        seen.add(key)
        breaks.append(
            {
                "severity": "block",
                "kind": "test-pin",
                "phrase": _preview(literal),
                "test": test_path.relative_to(repo_root).as_posix(),
                "line": lineno,
            }
        )
    return breaks


def deletion_findings(
    repo_root: Path,
    rel: str,
    test_roots: list[Path],
    *,
    removed: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Findings for a deleted skill surface: any surviving test-pin break (a real
    deterministic block, unaffected by the file being gone) plus an unconditional
    REVIEW -- a maximal cut must never fall through to zero findings."""
    findings = test_pin_breaks(repo_root, rel, test_roots, removed=removed)
    findings.append({"severity": "review", "kind": "deleted-surface", "phrase": rel})
    return findings


def build_report(
    repo_root: Path,
    paths: list[str] | None,
    test_roots: list[Path],
    *,
    staged: bool = False,
    removed_by_path: dict[str, list[str]] | None = None,
    deleted_paths: list[str] | None = None,
) -> dict[str, Any]:
    targets = paths if paths is not None else changed_skill_md(repo_root, staged=staged)
    targets = sorted({Path(p).as_posix() for p in targets})
    removed_map = removed_by_path or {}
    skills: list[dict[str, Any]] = []
    for rel in targets:
        if not _is_skill_md(rel):
            continue
        removed = removed_map.get(rel)
        findings = (
            contract_pin_breaks(repo_root, rel)
            + test_pin_breaks(repo_root, rel, test_roots, removed=removed)
            + reference_home_gaps(repo_root, rel, removed=removed)
        )
        blocks = [f for f in findings if f["severity"] == "block"]
        reviews = [f for f in findings if f["severity"] == "review"]
        skills.append(
            {
                "path": rel,
                "status": "blocked" if blocks else ("review" if reviews else "clean"),
                "blocks": blocks,
                "reviews": reviews,
            }
        )
    if deleted_paths is not None:
        deleted = deleted_paths
    elif paths is None:
        # #<north-star> structural-skip fix: a deletion is invisible to
        # `changed_skill_md` (it filters `code != "D"`), so it needs its own pass
        # over the same diff -- otherwise a maximal cut yields zero findings.
        deleted = deleted_skill_surfaces(repo_root, staged=staged)
    else:
        deleted = []
    for rel in deleted:
        findings = deletion_findings(
            repo_root, rel, test_roots, removed=removed_map.get(rel)
        )
        blocks = [f for f in findings if f["severity"] == "block"]
        reviews = [f for f in findings if f["severity"] == "review"]
        skills.append(
            {
                "path": rel,
                "status": "blocked" if blocks else "review",
                "blocks": blocks,
                "reviews": reviews,
            }
        )
    if paths and not skills:
        # A NAMED scope this gate cannot judge. `--path` is how a caller asks "is
        # this cut safe", and every named path being dropped by `_is_skill_md`
        # (a references/*.md contract home, a docs path, a typo) used to answer
        # `clean` over zero checks. A DISCOVERED empty set (no --path, nothing
        # changed) stays a cheap pass, per the empty-scope family rule.
        return {"status": "unscoped", "skills": [], "unscoped_paths": targets}
    any_block = any(s["blocks"] for s in skills)
    any_review = any(s["reviews"] for s in skills)
    status = "blocked" if any_block else ("review" if any_review else "clean")
    return {"status": status, "skills": skills}


# Folded in from the deleted human renderer. The finding rows carry `kind`,
# `severity` and `phrase`; what only the prose carried is what each severity
# OBLIGES -- a BLOCK means restore or move the pin, a deleted-surface REVIEW means
# a whole SKILL.md/reference vanished and a merged deletion is not reversible.
# Output is unconditionally YAML now, so those obligations ride on the payload.
_KIND_MEANING = {
    "deleted-surface": (
        "a whole SKILL.md or reference was removed: confirm the deletion is intentional "
        "or re-home its contract before this lands, since a merged deletion is not "
        "reversible"
    ),
    "test-pin": "a tests/ literal pins prose this cut removed",
}
_DEFAULT_REVIEW_MEANING = (
    "the line vanished without a reference home: confirm it is a justified no-op "
    "deletion (the section 5 no-op test) or re-home its content into a reference"
)
_BLOCKED_REMEDY = (
    "A removed phrase is pinned by a contract or test. Restore it (a CORE pin must stay "
    "in SKILL.md; a PACKAGE pin may move to a reference) or move the pinned test literal "
    "before cutting."
)
_UNSCOPED_REMEDY = (
    "This gate judges SKILL.md cuts only. Name the SKILL.md, or run without --path to "
    "check the changed set (which also reviews deleted references)."
)


def report_payload(report: dict[str, Any]) -> dict[str, Any]:
    payload = dict(report)
    if report["status"] == "unscoped":
        payload["summary"] = (
            "none of the named --path values is a public/support SKILL.md, so nothing "
            "was checked: " + ", ".join(report["unscoped_paths"])
        )
        payload["remedy"] = _UNSCOPED_REMEDY
        return payload
    if not report["skills"]:
        payload["summary"] = "no changed public/support SKILL.md surfaces to check."
        return payload
    kinds = {
        finding["kind"]
        for skill in report["skills"]
        for finding in (*skill["blocks"], *skill["reviews"])
    }
    if kinds:
        payload["kind_meaning"] = {
            kind: _KIND_MEANING.get(kind, _DEFAULT_REVIEW_MEANING) for kind in sorted(kinds)
        }
    if report["status"] == "blocked":
        payload["remedy"] = _BLOCKED_REMEDY
    elif report["status"] == "review":
        payload["remedy"] = (
            "No contract/test pin broke. Each REVIEW line above names what to confirm "
            "before this lands; see `kind_meaning`."
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--path",
        action="append",
        help="SKILL.md path to check (repeatable; defaults to changed SKILL.md vs HEAD).",
    )
    parser.add_argument(
        "--tests-root",
        action="append",
        default=None,
        help="Test root to scan for literal pins (repeatable; defaults to tests/).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Also exit non-zero on REVIEW (reference-home / deleted-surface) gaps, not only BLOCKs.",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Diff the staged index vs HEAD (--cached) instead of the working tree vs HEAD.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    test_root_names = args.tests_root if args.tests_root else ["tests"]
    test_roots = [repo_root / name for name in test_root_names]
    report = build_report(repo_root, args.path, test_roots, staged=args.staged)

    emit_yaml(report_payload(report))

    if report["status"] in {"blocked", "unscoped"}:
        return 1
    if args.strict and report["status"] == "review":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
