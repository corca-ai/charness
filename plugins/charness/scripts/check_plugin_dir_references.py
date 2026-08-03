#!/usr/bin/env python3

"""Resolve every `<plugin-dir>/...` reference against the shipped plugin package.

`<plugin-dir>/` was a recognised placeholder with **zero usage** for as long as it
existed (D50). The recorded reason not to adopt it was sharp: `$SKILL_DIR` is a
resolution PROCEDURE an agent can follow, while `<plugin-dir>/` was a doc
placeholder with nothing behind it -- "the ambiguity of a placeholder without the
resolution of a variable".

This closes that half. A `<plugin-dir>/X` reference is checked against
`plugins/<pkg>/X` in this repo, and a dangling one is refused. That is the
property `<repo-root>/` can never have: `<repo-root>/` means the READER's tree, so
it is unverifiable from here by construction, and that unverifiability is exactly
what let a whole class of unreachable references accumulate. `<plugin-dir>/` names
a tree this repo actually builds, so it can be resolved.

Why the placeholder is needed at all, measured 2026-08-04. `$SKILL_DIR/../..`
resolves in BOTH trees -- but only for `shared/` and `support/`, which are the
only two entries present at that position in each:

    authoring  skills/            -> public/ shared/ support/
    installed  plugins/<pkg>/     -> skills/ shared/ support/ scripts/ agents/ ...

So `$SKILL_DIR/../../shared/scripts/x.py` is correct in both trees by the same
exporter cancellation that makes `parents[3]` correct in both -- the flattened
kind level and the added package level cancel. Anything else under that root
(`scripts/`, `skills/<other>/`) exists only in the installed tree, and for those
there IS no both-trees relative spelling. `<plugin-dir>/` is how a doc says "this
resolves in the plugin you installed" instead of guessing a `../` count.

Non-claim: resolving here proves the target exists in the plugin package THIS repo
generates. It does not prove any host substitutes `<plugin-dir>/` textually -- the
placeholder is agent-resolved, per the procedure in the shared bootstrap
reference -- and it does not prove a consumer's installed copy is current.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_markdown_doc_scan = import_repo_module(__file__, "scripts.markdown_doc_scan")
iter_doc_lines = _markdown_doc_scan.iter_doc_lines
_repo_file_listing = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _repo_file_listing.iter_matching_repo_files

DOC_GLOBS = ("README.md", "AGENTS.md", "docs/**/*.md", "presets/**/*.md", "profiles/**/*.md", "skills/**/*.md")
PORTABLE_DOC_GLOBS = ("skills/**/*.md",)
PLUGINS_DIR = Path("plugins")
# `([^\s`)]+)` on purpose, not a character class of "safe" characters: the point is
# to capture what the author WROTE, including a templated `<skill>` segment or a
# `..`, so those can be judged instead of silently truncated into a shorter target
# that happens to resolve.
PLUGIN_DIR_RE = re.compile(r"<plugin-dir>/([^\s`)]+)")
AUTHORING_RE = re.compile(r"<authoring-repo>/([^\s`)]+)")
TEMPLATED = "templated"
ESCAPES = "escapes-package-root"


class ValidationError(Exception):
    pass


def plugin_roots(root: Path) -> list[Path]:
    """Every `plugins/<pkg>/` package this tree exports.

    Discovered, never hardcoded. The package name comes from the packaging
    manifest, so a rename or a second package would make a hardcoded
    `plugins/charness` absent -- and the no-package branch below exits 0. That
    would turn every reference in the repo unchecked while the run stayed green,
    which is the silent-zero shape this gate exists to close.
    """
    plugins = root / PLUGINS_DIR
    return sorted(path for path in plugins.iterdir() if path.is_dir()) if plugins.is_dir() else []


def iter_references(doc: Path) -> list[tuple[int, str]]:
    """`(lineno, target)` for every live-prose `<plugin-dir>/…` reference.

    Fenced and commented lines are skipped: a doc TEACHING the placeholder must be
    able to show a shape that does not resolve. The trailing-punctuation strip
    handles an un-backticked reference that ends a sentence.
    """
    return [
        (lineno, match.group(1).rstrip(".,;:)"))
        for lineno, line, in_fence in iter_doc_lines(doc)
        if not in_fence
        for match in PLUGIN_DIR_RE.finditer(line)
    ]


def shipped_but_marked_authoring_only(root: Path, roots: list[Path]) -> list[tuple[str, int, str, str]]:
    """`<authoring-repo>/P` in a SHIPPED skill doc where P is in the package.

    The mirror image of the unreachable-file class, and it was created while
    closing it: `<authoring-repo>/` asserts "this resolves in charness, not
    yours", so writing it for a file the consumer DOES have -- at
    `<plugin-dir>/P` -- tells the reader to go somewhere they cannot instead of
    somewhere they can. 39 such sites existed the moment the repair rule
    "anything not consumer-shaped gets `<authoring-repo>/`" was applied.

    Scoped to PORTABLE SKILL PACKAGES on purpose. In `docs/**` the reader is a
    charness maintainer and `<authoring-repo>/` is simply true; inside a doc that
    ships to consumers the reader is the consumer, and there the claim is false
    whenever the exporter carries the file along. The installed layout drops the
    `<kind>` segment, so a `skills/public/X` cite is checked as `skills/X` too.
    """
    findings: list[tuple[str, int, str, str]] = []
    for doc in iter_matching_repo_files(root, PORTABLE_DOC_GLOBS):
        for lineno, line, in_fence in iter_doc_lines(doc):
            if in_fence:
                continue
            for match in AUTHORING_RE.finditer(line):
                target = match.group(1).rstrip(".,;:)")
                for candidate in _installed_spellings(target):
                    shipped = next((r for r in roots if (r / candidate).exists()), None)
                    if shipped is not None:
                        findings.append(
                            (doc.relative_to(root).as_posix(), lineno, target, candidate)
                        )
                        break
    return findings


def _installed_spellings(target: str) -> list[str]:
    spellings = [target]
    for kind in ("skills/public/", "skills/support/"):
        if target.startswith(kind):
            spellings.append("skills/" + target[len(kind):])
    return spellings


def classify(target: str, roots: list[Path]) -> str | None:
    """`None` when the target resolves in some package; otherwise why it does not.

    A templated segment is SKIPPED rather than resolved. Truncating
    `<plugin-dir>/skills/<skill>/scripts/x.py` at the first `<` left the target
    `skills/`, which exists as a directory, so the canonical teaching lines in the
    bootstrap reference were being reported as validated on a prefix.
    """
    if "<" in target or ">" in target or "\u2026" in target:
        return TEMPLATED
    if target.startswith("/") or ".." in Path(target).parts:
        # `plugin_root / "/etc/hostname"` is `/etc/hostname` under pathlib, and a
        # `..` that climbs out and back in still resolves. Both name paths outside
        # the installed package, so neither is a reference this gate can bless.
        return ESCAPES
    return None if any((plugin_root / target).exists() for plugin_root in roots) else "missing"


def unresolved_references(
    root: Path, roots: list[Path], *, require_git: bool = False, skipped: Counter | None = None
) -> list[tuple[str, int, str, str]]:
    skipped = Counter() if skipped is None else skipped
    findings: list[tuple[str, int, str, str]] = []
    for doc in iter_matching_repo_files(root, DOC_GLOBS, require_git=require_git):
        for lineno, target in iter_references(doc):
            reason = classify(target, roots)
            if reason == TEMPLATED:
                skipped[TEMPLATED] += 1
                continue
            if reason is not None:
                findings.append((doc.relative_to(root).as_posix(), lineno, target, reason))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--require-git-file-listing", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    roots = plugin_roots(root)
    if not roots:
        # A consumer or temp repo has no generated plugin package to resolve
        # against. Saying so beats a green run that checked nothing.
        print(f"No `{PLUGINS_DIR}/<pkg>` package in this tree; nothing was resolved.")
        return 0

    skipped: Counter = Counter()
    findings = unresolved_references(root, roots, require_git=args.require_git_file_listing, skipped=skipped)
    packages = ", ".join(path.name for path in roots)
    note = (
        " skipped: " + ", ".join(f"{count} {reason}" for reason, count in sorted(skipped.items()))
        if any(skipped.values())
        else " skipped: none"
    )
    shipped = shipped_but_marked_authoring_only(root, roots)
    if shipped:
        raise ValidationError(
            "\n".join(
                f"{doc}:{lineno}: `<authoring-repo>/{target}` says this file is NOT in the reader's "
                f"tree, but it SHIPS at `<plugin-dir>/{candidate}`; a consumer reading this skill doc "
                "has the file and is being sent to a tree they do not have"
                for doc, lineno, target, candidate in shipped
            )
            + f"\n({len(shipped)} mis-prefixed; the mirror image of the unreachable-file class)"
        )
    if findings:
        raise ValidationError(
            "\n".join(
                f"{doc}:{lineno}: `<plugin-dir>/{target}` {reason} ({packages}); `<plugin-dir>/` names "
                "the installed plugin package root, so the target must be a path this repo exports there"
                for doc, lineno, target, reason in findings
            )
            + f"\n({len(findings)} unresolved;{note})"
        )
    print(f"Validated `<plugin-dir>/` references against package(s): {packages}.{note}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
