#!/usr/bin/env python3
"""Inventory the script paths that shipped skill prose tells an agent to run.

A skill document that says ``python3 <repo-root>/scripts/x.py`` while ``x.py``
actually lives at ``skills/public/<skill>/scripts/x.py`` names a command that
cannot run -- not in a consuming repo, and not in this one either. Thirteen of
those accumulated unseen (measured 2026-08-02 over every ``.md`` under
``skills/``), because three separate silences overlap on exactly that spelling:

1. ``<repo-root>/`` is a documented *portable placeholder* in
   ``check_doc_links.py``, the escape hatch for commands that only resolve in a
   consuming repo -- so it is exempt from resolution by design.
2. ``iter_unresolved_command_targets`` skips any candidate containing ``<`` or
   ``>``, which every ``<repo-root>/`` token does.
3. Inside a portable skill package ``classify_backtick_token`` returns ``None``
   for every token, disabling the backticked-file-reference check entirely.

The escape hatch is therefore indistinguishable from a typo. This inventory
tells the two apart the only way that is decidable without a consuming repo: by
asking where the referenced file actually is.

PROMOTED TO A BLOCKING GATE (operator decision, 2026-08-02), after shipping one
run as an advisory. The Floor-Addition Restraint checklist asks for a recorded
RECURRENCE rather than one finding; what promoted it instead is the three-silence
MECHANISM above, which shows the class is invisible by construction rather than
by luck.

The promotion was first justified with "a false positive is structurally
impossible -- the file is on disk or it is not". That was WRONG, and the first
bounded review of the promotion proved it with two live refusals: the risk is
never disk existence, it is (a) resolving against the wrong root, and (b)
treating absence as a defect for a form where absence is correct. Both shipped
in the promoting slice and both are repaired here -- ``SkillPackage`` carries each
package's authoring root instead of counting ``../`` backwards, and
``<repo-root>/`` (the READER's tree) can only be refused when the file is sitting
in the skill's own package. What makes the gate safe is those two invariants and
the tests pinning them, not an appeal to determinism.

``--strict`` is the blocking mode and is what ``run-quality.sh`` runs; it refuses
on findings AND on unreadable docs. The default stays exit-0 so the same command
is still usable as a read-only inventory.

Output is unconditionally YAML, so every sentence a reader needs has to live in
the payload -- ``report()`` folds in the advisories, the per-finding hints, and
the two non-finding notes that used to exist only inside the human renderer.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import NamedTuple

from scripts.gates.check_doc_links import PORTABLE_SKILL_KINDS
from yaml_output import emit_yaml  # noqa: E402

# ANY extension, not just `.py`. A `.py`-only regex cannot report that it is
# `.py`-only -- it reports "0 remaining" with full confidence, which is exactly
# how `check-links-internal.sh` survived every enumeration pass of #478 until an
# adversarial reader found it by eye. The gate shipped in that same session was
# still `.py`-anchored, so it carried the class it was fixing.
_SCRIPT_NAME = r"[A-Za-z0-9_][A-Za-z0-9_./-]*\.[A-Za-z0-9]+"
# `<repo-root>/scripts/<name>` -- the CONSUMER's tree. Unverifiable here.
REPO_ROOT_SCRIPT_RE = re.compile(rf"<repo-root>/scripts/({_SCRIPT_NAME})")
# `<authoring-repo>/<path>` -- charness's OWN tree. Verifiable here, and the
# whole point of the split: a consumer reads it as "not mine", and this check
# resolves it instead of waving it through as an unverifiable placeholder.
# Keep the old public constant as an alias for callers that only need the
# historical scripts-shaped subset; the inventory itself scans the wider form.
AUTHORING_REPO_PATH_RE = re.compile(rf"<authoring-repo>/({_SCRIPT_NAME})")
AUTHORING_REPO_SCRIPT_RE = AUTHORING_REPO_PATH_RE
# `<plugin-dir>/scripts/<name>` -- the INSTALLED plugin package. Verifiable here
# against the generated `plugins/<pkg>/`, which is what makes it the honest
# spelling for a charness script the consumer actually receives. Adopted 2026-08-04
# (D50); until then this family was invisible to this inventory, so 41 references
# moved out of measurement the moment they were repaired into it.
PLUGIN_DIR_SCRIPT_RE = re.compile(rf"<plugin-dir>/scripts/({_SCRIPT_NAME})")
PLUGIN_PACKAGE_ROOT = "plugins/charness"
# `$SKILL_DIR/<path>` -- the in-package form the working references use.
SKILL_DIR_RE = re.compile(r"\$SKILL_DIR/([A-Za-z0-9_.][A-Za-z0-9_./-]*)")
# A `## References` list bullet naming a package-local script. Deliberately
# narrower than "any backticked `scripts/<name>.py`": in a bullet the form is
# unambiguously package-relative, while the same token in prose usually names a
# repo-level script ("point it at your repo's `scripts/ci_check.py`"). Scanning
# prose too would turn correct illustrative text into findings -- manufacturing
# a defect is the same failure as missing one.
#
# A trailing description is allowed (`- `scripts/issue_tool.py` - CLI entrypoint
# for ...`): anchoring to end-of-line would have skipped real bullets and made
# the check narrower than its own stated rationale. What matters is that the
# script path OPENS the bullet, which is what makes it a named affordance rather
# than an illustrative mention.
REFERENCES_BULLET_RE = re.compile(rf"^\s*-\s+`(scripts/{_SCRIPT_NAME})`")

# Classification tokens, most-actionable first.
BROKEN = "package_file_wrong_prefix"
UNRESOLVED = "unresolved"
AUTHORING_REPO = "authoring_repo_script"
# Resolved against this repo because the prose says so explicitly.
AUTHORING_MARKED = "authoring_repo_marked"
CONSUMER_PLACEHOLDER = "consumer_repo_placeholder"
IN_PACKAGE = "in_package"

ACTIONABLE = frozenset({BROKEN, UNRESOLVED})

# The two layouts a skill package is read in. They are not the same tree, and a
# reference can resolve in one and not the other -- `$SKILL_DIR/../../../scripts`
# reaches the repo root from `skills/public/<skill>` but overshoots the plugin
# root from `plugins/<pkg>/skills/<skill>`, where the exported scripts sit two
# levels up instead of three.
AUTHORING = "authoring"
SHIPPED = "shipped"


UNREADABLE_DOCS: list[str] = []


def _iter_doc_lines(path: Path):
    """Yield ``(lineno, line)``; record rather than raise on an unreadable doc.

    An unreadable doc must not turn a no-exit-code advisory into a traceback,
    but it must also not be indistinguishable from a scanned-and-clean one --
    that is the same "clean verdict over nothing" this tool exists to refuse.
    Callers surface the count via ``docs_unreadable``.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        UNREADABLE_DOCS.append(path.as_posix())
        return
    for lineno, line in enumerate(text.splitlines(), 1):
        yield lineno, line


def _repo_relative(repo_root: Path, path: Path) -> str:
    """`path` as a repo-relative posix string, or absolute when it escapes.

    `$SKILL_DIR/../../..` and friends can resolve outside the repo, and a bare
    `relative_to` would raise there -- turning a no-exit-code advisory into a
    traceback.
    """
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _is_generic_placeholder(target: str) -> bool:
    """True for prose that teaches the FORM rather than naming a real file.

    ``skills/shared/references/bootstrap-resolution.md`` documents
    ``$SKILL_DIR/scripts/`` itself; there is no concrete file to resolve, and
    ``$SKILL_DIR`` is undefined for shared prose anyway because it depends on
    whichever skill included it.
    """
    return "<" in target or ">" in target or not Path(target).suffix


class SkillPackage(NamedTuple):
    """One skill package root plus how paths resolve relative to it.

    ``authoring_root`` is what ``<authoring-repo>/`` resolves against, and it is
    CARRIED rather than derived from a fixed ``../`` count off ``root``. The
    shipped shapes are not the same depth -- ``plugins/<pkg>/skills/<skill>`` and
    ``plugins/<pkg>/support/<skill>`` are three deep, ``plugins/<pkg>/shared`` is
    two -- so a single ``.parent.parent`` is right for two of them and silently
    wrong for the third. That is the same "no single ``../``-count fixes that"
    trap the shim's docstring names, reproduced inside the checker meant to catch
    it: it made every `<authoring-repo>/` reference in `skills/shared` an
    unfixable refusal, i.e. following this tool's own printed advice broke it.
    """

    root: Path
    layout: str
    resolves_skill_dir: bool
    authoring_root: Path
    authoring_source_root: Path


def iter_skill_packages(repo_root: Path) -> list[SkillPackage]:
    """Every skill package root, in both the authoring and the shipped layout.

    Authoring resolution
    defers to ``check_doc_links``'s own ``PORTABLE_SKILL_KINDS`` rather than
    re-deriving the layout: a second spelling of the same rule is how this class
    hides in the first place. The shipped layout has no equivalent helper because
    the exporter flattens `skills/<kind>/<skill>` to `skills/<skill>`, so it is
    derived here from the exported tree itself.

    ``skills/shared`` is scanned but ``resolves_skill_dir`` is False for it:
    shared prose is included BY a skill, so `$SKILL_DIR` is whichever skill
    included it, not the shared directory. Resolving those against the shared
    root would manufacture failures out of correct references -- which is exactly
    the wrong-denominator mistake this goal exists to stop repeating.
    """
    repo_root = repo_root.resolve()
    packages: list[SkillPackage] = []

    skills_root = repo_root / "skills"
    if skills_root.is_dir():
        for kind in sorted(PORTABLE_SKILL_KINDS):
            for package in sorted((skills_root / kind).glob("*")):
                if package.is_dir():
                    packages.append(SkillPackage(package, AUTHORING, True, repo_root, repo_root))
        if (skills_root / "shared").is_dir():
            packages.append(
                SkillPackage(skills_root / "shared", AUTHORING, False, repo_root, repo_root)
            )

    # Each shipped package carries its OWN plugin root, taken from the
    # `plugins/<pkg>` path that produced it rather than counted backwards.
    for plugin_root in sorted(repo_root.glob("plugins/*")):
        if not plugin_root.is_dir():
            continue
        for kind, resolves in (("skills", True), ("support", True)):
            for package_dir in sorted((plugin_root / kind).glob("*")):
                if package_dir.is_dir():
                    packages.append(
                        SkillPackage(package_dir, SHIPPED, resolves, plugin_root, repo_root)
                    )
        shared_dir = plugin_root / "shared"
        if shared_dir.is_dir():
            packages.append(SkillPackage(shared_dir, SHIPPED, False, plugin_root, repo_root))

    return packages


def _package_script_index(packages: list["SkillPackage"]) -> dict[str, set[str]]:
    """``layout -> {script basename found in ANY scanned package}``.

    The counted defect is "the file is in a skill package, so the consumer-tree
    prefix is wrong". Checking only the REFERRING package misses it whenever the
    doc and the file live in different packages -- `skills/shared` prose naming a
    `skills/public/<x>/scripts/` helper is the common shape, and it has no owning
    package at all. Round 1 removed a false positive here and re-opened that
    false negative; the index closes both.
    """
    index: dict[str, set[str]] = {}
    for package in packages:
        bucket = index.setdefault(package.layout, set())
        scripts_dir = package.root / "scripts"
        if scripts_dir.is_dir():
            bucket.update(
                entry.relative_to(scripts_dir).as_posix()
                for entry in scripts_dir.rglob("*")
                if entry.is_file()
            )
    return index


def _classify_repo_root_form(
    package: "SkillPackage", name: str, packaged_names: set[str]
) -> tuple[str, str | None]:
    """Where `<repo-root>/scripts/<name>` actually points.

    `<repo-root>` names the tree the READER is operating on, which is
    unverifiable from here BY DESIGN (`authoring-preflight.md` calls it exempt).
    So absence is NOT a defect for this form -- a skill legitimately writes
    "point your gate at `<repo-root>/scripts/run_pre_push.py`" about a file only
    the consumer has, and refusing that armed the gate against its own escape
    hatch.

    The one decidable defect is the opposite: the named script is sitting in a
    skill package of THIS tree, which makes the consumer-tree prefix wrong no
    matter whose tree it is.

    The `at_root` escape matters: when the basename ALSO exists at the authoring
    root, the reference is genuinely ambiguous -- `plan_risk_interrupt.py` is
    both `scripts/gates_support/plan_risk_interrupt.py` and the `skills/shared/scripts/` shim,
    so a true sentence about the repo-level planner would otherwise be refused
    with advice pointing at the shim. Ambiguous is not blockable.
    """
    in_own_package = (package.root / "scripts" / name).is_file()
    at_root = (package.authoring_root / "scripts" / name).is_file()

    if not at_root and (in_own_package or name in packaged_names):
        found = (
            _repo_relative(package.authoring_root, package.root / "scripts" / name)
            if in_own_package
            else f"a skill package's scripts/{name}"
        )
        return BROKEN, found
    if at_root and package.layout == AUTHORING:
        return AUTHORING_REPO, f"scripts/{name}"
    return CONSUMER_PLACEHOLDER, None


def _classify_package_relative_form(
    repo_root: Path, package_root: Path, layout: str, target: str
) -> tuple[str, str | None]:
    """Where a bare `scripts/<name>.py` points.

    Genuinely ambiguous: in a `## References` bullet it is package-relative, in
    prose it usually names a repo-level script. Resolved the way
    `check_doc_links` does -- package, then repo root -- instead of picking one
    meaning and manufacturing findings out of correct references.
    """
    packaged = (package_root / target).resolve()
    if packaged.is_file():
        return IN_PACKAGE, _repo_relative(repo_root, packaged)
    if layout == SHIPPED:
        return CONSUMER_PLACEHOLDER, None
    if (repo_root / target).is_file():
        return AUTHORING_REPO, target
    return UNRESOLVED, None


def classify_references(repo_root: Path) -> list[dict[str, object]]:
    """Every script reference in shipped skill prose, with where its file is."""
    repo_root = repo_root.resolve()
    rows: list[dict[str, object]] = []
    UNREADABLE_DOCS.clear()

    packages = iter_skill_packages(repo_root)
    script_index = _package_script_index(packages)
    docs = [(doc, package) for package in packages for doc in sorted(package.root.rglob("*.md"))]

    for doc, package in docs:
        package_root, layout, resolves_skill_dir = (
            package.root,
            package.layout,
            package.resolves_skill_dir,
        )
        rel_doc = _repo_relative(repo_root, doc)

        for lineno, line in _iter_doc_lines(doc):
            for match in REPO_ROOT_SCRIPT_RE.finditer(line):
                name = match.group(1)
                status, found_at = _classify_repo_root_form(
                    package, name, script_index.get(layout, set())
                )
                rows.append(
                    {
                        "doc": rel_doc,
                        "line": lineno,
                        "layout": layout,
                        "reference": f"<repo-root>/scripts/{name}",
                        "form": "repo-root",
                        "status": status,
                        "found_at": found_at,
                    }
                )

            # Both placeholders make a CHECKABLE claim; they differ only in which
            # tree they claim. `<authoring-repo>/` resolves against the charness
            # tree carried per package (never counted backwards, see SkillPackage);
            # `<plugin-dir>/` resolves against the generated package, because that
            # is the claim it makes -- that the consumer received the file.
            for pattern, placeholder, form, target_root, target_prefix, reference_prefix in (
                (
                    AUTHORING_REPO_PATH_RE,
                    "<authoring-repo>",
                    "authoring-repo",
                    package.authoring_source_root,
                    "",
                    "",
                ),
                (
                    PLUGIN_DIR_SCRIPT_RE,
                    "<plugin-dir>",
                    "plugin-dir",
                    repo_root / PLUGIN_PACKAGE_ROOT,
                    "scripts",
                    "scripts/",
                ),
            ):
                for match in pattern.finditer(line):
                    name = match.group(1)
                    target_path = target_root / target_prefix / name
                    resolved = target_path.is_file()
                    rows.append(
                        {
                            "doc": rel_doc,
                            "line": lineno,
                            "layout": layout,
                            "reference": f"{placeholder}/{reference_prefix}{name}",
                            "form": form,
                            "status": AUTHORING_MARKED if resolved else UNRESOLVED,
                            "found_at": _repo_relative(repo_root, target_path)
                            if resolved
                            else None,
                        }
                    )

            bullet = REFERENCES_BULLET_RE.match(line)
            if bullet is not None:
                target = bullet.group(1)
                status, found_at = _classify_package_relative_form(
                    repo_root, package_root, layout, target
                )
                rows.append(
                    {
                        "doc": rel_doc,
                        "line": lineno,
                        "layout": layout,
                        "reference": target,
                        "form": "references-bullet",
                        "status": status,
                        "found_at": found_at,
                    }
                )

            if not resolves_skill_dir:
                continue

            for match in SKILL_DIR_RE.finditer(line):
                target = match.group(1).rstrip("/")
                if _is_generic_placeholder(target):
                    continue
                resolved = (package_root / target).resolve()
                rows.append(
                    {
                        "doc": rel_doc,
                        "line": lineno,
                        "layout": layout,
                        "reference": f"$SKILL_DIR/{target}",
                        "form": "skill-dir",
                        "status": IN_PACKAGE if resolved.is_file() else UNRESOLVED,
                        "found_at": (
                            _repo_relative(repo_root, resolved) if resolved.is_file() else None
                        ),
                    }
                )

    return rows


def inventory(repo_root: Path) -> dict[str, object]:
    rows = classify_references(repo_root)
    counts: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket = counts.setdefault(str(row["layout"]), {})
        bucket[str(row["status"])] = bucket.get(str(row["status"]), 0) + 1
    by_layout = {
        layout: sum(1 for row in rows if row["layout"] == layout) for layout in (AUTHORING, SHIPPED)
    }
    return {
        "repo_root": repo_root.resolve().as_posix(),
        "portable_skill_kinds": sorted(PORTABLE_SKILL_KINDS),
        "denominator": {
            # Each authored reference is counted once per layout it appears in,
            # so this total is roughly double the number of authored sites. The
            # per-layout split is the honest figure to quote.
            "references_scanned": len(rows),
            "distinct_reference_strings": len({row["reference"] for row in rows}),
            "skill_packages_scanned": len(iter_skill_packages(repo_root)),
            "docs_unreadable": list(UNREADABLE_DOCS),
            "by_layout": by_layout,
        },
        "counts": counts,
        "findings": [row for row in rows if row["status"] in ACTIONABLE],
        "authoring_marker_candidates": [
            row
            for row in rows
            if row["layout"] == AUTHORING
            and row["form"] == "repo-root"
            and row["status"] == AUTHORING_REPO
        ],
    }


_AUTHORING_MARKER_NOTE = (
    "reference(s) use `<repo-root>/scripts/` for a file that is also a charness "
    "authoring-repo script. NOT a finding, and not settled either: some are correct "
    "as-is -- `rca-ledger-append.md` uses the path as an existence predicate the "
    "READER evaluates, which is exactly what `<repo-root>/` should mean. A human "
    "decides each; `<authoring-repo>/scripts/` is the spelling when the subject is "
    "charness's own tree (#478). The full set is in `authoring_marker_candidates`."
)
_CONSUMER_PLACEHOLDER_NOTE = (
    "shipped reference(s) resolve only against a consuming repo's own `scripts/` and "
    "are unverifiable from here. Not a finding, and deliberately not silent: without "
    "this line, `0 findings` reads as `every reference is fine`."
)


def report(payload: dict[str, object], *, strict: bool) -> dict[str, object]:
    """Fold the verdict-explaining text into the payload this gate emits.

    Output is unconditionally YAML, so anything a reader needs has to live in the
    payload. The advisories, the per-finding hint, and the two NON-finding notes
    used to exist only inside a human renderer; emitting the bare inventory would
    have deleted them while leaving the exit code green, which is the fail-quiet
    shape the `--strict` promotion exists against.
    """
    out = dict(payload)
    denominator = payload["denominator"]
    assert isinstance(denominator, dict)
    findings = payload["findings"]
    assert isinstance(findings, list)
    unreadable = denominator["docs_unreadable"]
    assert isinstance(unreadable, list)
    blind = bool(unreadable)
    scanned = denominator["references_scanned"]
    assert isinstance(scanned, int)
    packages = denominator["skill_packages_scanned"]

    out["strict"] = strict
    # `--strict` refuses on findings AND on "I could not look": an unreadable doc
    # hides its references, so a green over it is the clean-verdict-over-nothing
    # this tool exists to refuse.
    out["refuse"] = bool(strict and (findings or blind))

    advisories: list[str] = []
    if blind:
        # An unreadable doc hides its references; without this it is
        # indistinguishable from a scanned-and-clean one. Listed BEFORE the
        # zero-reference advisory, or the one path that returns green would be the
        # only path that never mentions the blind spot.
        advisories.append(
            f"{len(unreadable)} doc(s) could not be read and were not scanned: "
            + ", ".join(str(doc) for doc in unreadable[:5])
        )
    if not scanned:
        # A clean verdict over nothing is the one failure an advisory can hide
        # behind. Gate on REFERENCES, not packages: a repo can carry skill packages
        # whose prose this scanner matches none of, and "all 0 references resolve"
        # would be the same false all-clear one level down.
        if blind:
            detail = f"{payload['repo_root']} had no readable doc naming a script path"
        elif not packages:
            detail = f"no skill packages found under {payload['repo_root']}"
        else:
            detail = (
                f"{packages} skill package(s) under {payload['repo_root']} name no script paths"
            )
        advisories.append(
            f"{detail}; nothing was checked. Point --repo-root at a repo that carries "
            "`skills/` or `plugins/*/skills/`."
        )
    out["advisories"] = advisories

    if not scanned:
        out["verdict"] = "not-run"
    elif findings:
        # FAIL under --strict (the gate mode); WARN otherwise, which run-quality.sh
        # surfaces non-blocking. Same finding set either way -- only the exit code
        # differs, so the read-only inventory and the gate cannot disagree.
        out["verdict"] = "fail" if strict else "warn"
    else:
        out["verdict"] = "ok"

    out["findings"] = [
        {
            **row,
            "hint": (
                f"file is at {row['found_at']}"
                if row["status"] == BROKEN
                else "resolves in no layout"
            ),
        }
        for row in findings
        if isinstance(row, dict)
    ]

    notes: list[str] = []
    candidates = payload["authoring_marker_candidates"]
    assert isinstance(candidates, list)
    if candidates:
        notes.append(f"{len(candidates)} {_AUTHORING_MARKER_NOTE}")
    counts = payload["counts"]
    assert isinstance(counts, dict)
    placeholders = counts.get(SHIPPED, {}).get(CONSUMER_PLACEHOLDER, 0)
    if placeholders:
        notes.append(f"{placeholders} {_CONSUMER_PLACEHOLDER_NOTE}")
    out["notes"] = notes
    return out


def build_parser() -> argparse.ArgumentParser:
    """The whole option surface, read by a test rather than grepped from source.

    `--strict` is the gate mode added when the operator promoted this check
    (2026-08-02). The default stays exit-0 so the same command remains a
    read-only inventory.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 when any reference cannot resolve (the blocking gate mode).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    payload = report(inventory(args.repo_root), strict=args.strict)
    emit_yaml(payload)
    return 1 if payload["refuse"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
