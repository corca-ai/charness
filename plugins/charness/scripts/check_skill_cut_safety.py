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
import json
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script

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


def changed_skill_md(repo_root: Path) -> list[str]:
    """Changed (non-deleted) public/support SKILL.md paths in the diff vs HEAD."""
    rows = _prose_pin.changed_status(repo_root)
    return sorted({new for code, _old, new in rows if code != "D" and _is_skill_md(new)})


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


def reference_home_gaps(repo_root: Path, rel: str) -> list[dict[str, Any]]:
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
    for removed in _prose_pin.removed_lines(repo_root, rel):
        if removed in seen:
            continue
        if len(removed) < MIN_PROSE_LENGTH or " " not in removed.strip():
            continue
        if removed in body or removed in refs:
            continue
        seen.add(removed)
        gaps.append({"severity": "review", "kind": "reference-home-gap", "phrase": _preview(removed)})
    return gaps


def test_pin_breaks(repo_root: Path, rel: str, test_roots: list[Path]) -> list[dict[str, Any]]:
    """``tests/`` literal pins on lines this cut removed (check_prose_pin heuristic)."""
    literals = _prose_pin.test_string_literals(test_roots)
    findings = _prose_pin.find_prose_pins(repo_root, [rel], literals)
    return [
        {
            "severity": "block",
            "kind": "test-pin",
            "phrase": finding["phrase"],
            "test": finding["test"],
            "line": finding["line"],
        }
        for finding in findings
    ]


def build_report(
    repo_root: Path,
    paths: list[str] | None,
    test_roots: list[Path],
) -> dict[str, Any]:
    targets = paths if paths is not None else changed_skill_md(repo_root)
    targets = sorted({Path(p).as_posix() for p in targets})
    skills: list[dict[str, Any]] = []
    for rel in targets:
        if not _is_skill_md(rel):
            continue
        findings = (
            contract_pin_breaks(repo_root, rel)
            + test_pin_breaks(repo_root, rel, test_roots)
            + reference_home_gaps(repo_root, rel)
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
    any_block = any(s["blocks"] for s in skills)
    any_review = any(s["reviews"] for s in skills)
    status = "blocked" if any_block else ("review" if any_review else "clean")
    return {"status": status, "skills": skills}


def format_human(report: dict[str, Any]) -> str:
    lines = [f"skill-cut-safety: {report['status']}"]
    if not report["skills"]:
        lines.append("- no changed public/support SKILL.md surfaces to check.")
        return "\n".join(lines)
    for skill in report["skills"]:
        lines.append(f"- {skill['path']}: {skill['status']}")
        for block in skill["blocks"]:
            if block["kind"] == "test-pin":
                lines.append(
                    f"  BLOCK test-pin {block['test']}:{block['line']} pins removed prose: "
                    f"\"{block['phrase']}\""
                )
            else:
                lines.append(f"  BLOCK {block['kind']} no longer satisfied: \"{block['phrase']}\"")
        for review in skill["reviews"]:
            lines.append(
                f"  REVIEW {review['kind']} (confirm no-op deletion or re-home): "
                f"\"{review['phrase']}\""
            )
    if report["status"] == "blocked":
        lines.append(
            "A removed phrase is pinned by a contract or test. Restore it (a CORE pin "
            "must stay in SKILL.md; a PACKAGE pin may move to a reference) or move the "
            "pinned test literal before cutting."
        )
    elif report["status"] == "review":
        lines.append(
            "No contract/test pin broke. Each REVIEW line vanished without a reference "
            "home: confirm it is a justified no-op deletion (the §5 no-op test) or "
            "re-home its content into a reference."
        )
    return "\n".join(lines)


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
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Also exit non-zero on REVIEW (reference-home) gaps, not only BLOCKs.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    test_root_names = args.tests_root if args.tests_root else ["tests"]
    test_roots = [repo_root / name for name in test_root_names]
    report = build_report(repo_root, args.path, test_roots)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_human(report))

    if report["status"] == "blocked":
        return 1
    if args.strict and report["status"] == "review":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
