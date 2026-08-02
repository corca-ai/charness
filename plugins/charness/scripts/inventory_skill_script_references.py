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

Advisory by design (operator decision, 2026-08-02): one finding is not a recorded
recurrence, and this repo's recorded reflex is adding floors on first sight. This
command has deliberately no ``--strict`` flag and no code path that returns
non-zero, and ``run-quality.sh`` surfaces its ``WARN:`` output non-blocking.

Stated precisely, because "advisory" is easy to overclaim: the COMMAND cannot
fail a run. ``tests/test_skill_script_references.py`` is a different surface, and
it *is* a gate -- it fails when an authoring-layout reference stops resolving.
That regression test is the teeth this repair was asked to carry; the exit code
of this script is not.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_doc_links import PORTABLE_SKILL_KINDS  # noqa: E402

# `<repo-root>/scripts/<name>.py` -- the placeholder form.
REPO_ROOT_SCRIPT_RE = re.compile(r"<repo-root>/scripts/([A-Za-z0-9_][A-Za-z0-9_./-]*\.py)")
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
REFERENCES_BULLET_RE = re.compile(r"^\s*-\s+`(scripts/[A-Za-z0-9_][A-Za-z0-9_./-]*\.py)`")

# Classification tokens, most-actionable first.
BROKEN = "package_file_wrong_prefix"
UNRESOLVED = "unresolved"
AUTHORING_REPO = "authoring_repo_script"
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


def iter_skill_packages(repo_root: Path) -> list[tuple[Path, str, bool]]:
    """Every skill package root, in both the authoring and the shipped layout.

    Returns ``(package_root, layout, resolves_skill_dir)``. Authoring resolution
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
    packages: list[tuple[Path, str, bool]] = []

    skills_root = repo_root / "skills"
    if skills_root.is_dir():
        for kind in sorted(PORTABLE_SKILL_KINDS):
            for package in sorted((skills_root / kind).glob("*")):
                if package.is_dir():
                    packages.append((package, AUTHORING, True))
        if (skills_root / "shared").is_dir():
            packages.append((skills_root / "shared", AUTHORING, False))

    for package_dir in sorted(repo_root.glob("plugins/*/skills/*")) + sorted(
        repo_root.glob("plugins/*/support/*")
    ):
        if package_dir.is_dir():
            packages.append((package_dir, SHIPPED, True))
    for shared_dir in sorted(repo_root.glob("plugins/*/shared")):
        if shared_dir.is_dir():
            packages.append((shared_dir, SHIPPED, False))

    return packages


def _classify_repo_root_form(
    repo_root: Path, package_root: Path | None, layout: str, name: str
) -> tuple[str, str | None]:
    """Where `<repo-root>/scripts/<name>` actually points, per layout."""
    in_package = package_root is not None and (package_root / "scripts" / name).is_file()
    found_at = (
        _repo_relative(repo_root, package_root / "scripts" / name) if in_package else None
    )
    if layout == SHIPPED:
        # `<repo-root>` names the CONSUMING repo's root once the plugin is
        # installed. Nothing in this tree can decide whether that file is there,
        # so the only decidable half is the file being in the package instead.
        return (BROKEN if in_package else CONSUMER_PLACEHOLDER), found_at

    if (repo_root / "scripts" / name).is_file():
        return AUTHORING_REPO, found_at or f"scripts/{name}"
    if in_package:
        return BROKEN, found_at
    return UNRESOLVED, None


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

    docs = [
        (doc, package_root, layout, resolves_skill_dir)
        for package_root, layout, resolves_skill_dir in iter_skill_packages(repo_root)
        for doc in sorted(package_root.rglob("*.md"))
    ]

    for doc, package_root, layout, resolves_skill_dir in docs:
        rel_doc = _repo_relative(repo_root, doc)

        for lineno, line in _iter_doc_lines(doc):
            for match in REPO_ROOT_SCRIPT_RE.finditer(line):
                name = match.group(1)
                status, found_at = _classify_repo_root_form(repo_root, package_root, layout, name)
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

            if package_root is None:
                continue

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
    }


def build_parser() -> argparse.ArgumentParser:
    """The whole option surface, exposed so a test can assert what is NOT here.

    Deliberately carries no escalation flag; `test_skill_script_references.py`
    reads this parser rather than grepping the source for `--strict`.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    payload = inventory(args.repo_root)
    if args.json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        return 0

    findings = payload["findings"]
    denominator = payload["denominator"]
    scanned = denominator["references_scanned"]
    split = "/".join(f"{count} {layout}" for layout, count in denominator["by_layout"].items())

    if not scanned:
        # A clean verdict over nothing is the one failure an advisory can hide
        # behind. Gate on REFERENCES, not packages: a repo can carry skill
        # packages whose prose this scanner matches none of, and "all 0
        # references resolve" would be the same false all-clear one level down.
        packages = denominator["skill_packages_scanned"]
        detail = (
            f"no skill packages found under {payload['repo_root']}"
            if not packages
            else f"{packages} skill package(s) under {payload['repo_root']} name no script paths"
        )
        print(
            f"ADVISORY: {detail}; nothing was checked. Point --repo-root at a "
            "repo that carries `skills/` or `plugins/*/skills/`."
        )
        return 0

    if denominator["docs_unreadable"]:
        # An unreadable doc hides its references; without this it is
        # indistinguishable from a scanned-and-clean one.
        print(
            f"ADVISORY: {len(denominator['docs_unreadable'])} doc(s) could not be read "
            "and were not scanned: " + ", ".join(denominator["docs_unreadable"][:5])
        )

    if findings:
        # WARN: is the prefix run-quality.sh surfaces non-blocking. This helper
        # has no strict mode on purpose -- see the module docstring.
        print(f"WARN: {len(findings)} of {scanned} ({split}) skill script references do not resolve:")
        for row in findings:
            hint = (
                f" (file is at {row['found_at']})"
                if row["status"] == BROKEN
                else " (resolves in no layout)"
            )
            print(f"  - [{row['layout']}] {row['doc']}:{row['line']}: `{row['reference']}`{hint}")
    else:
        print(f"all {scanned} ({split}) skill script references resolve")

    placeholders = payload["counts"].get(SHIPPED, {}).get(CONSUMER_PLACEHOLDER, 0)
    if placeholders:
        # Not a finding, and deliberately not silent: `<repo-root>/scripts/X.py`
        # resolves against the CONSUMING repo, which this tree cannot inspect.
        # Without this line, "0 findings" reads as "every reference is fine".
        print(
            f"note: {placeholders} shipped reference(s) resolve only against a consuming "
            "repo's own `scripts/` and are unverifiable from here."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
