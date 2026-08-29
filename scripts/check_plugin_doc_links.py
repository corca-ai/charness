#!/usr/bin/env python3

"""Refuse relative markdown links in the shipped plugin mirror that a consumer cannot follow.

`check_doc_links.py` validates links from the AUTHORING tree's position: its
`DOC_GLOBS` covers `docs/`, `skills/`, `presets/`, `profiles/`, `README`, and
`AGENTS`, and deliberately not `plugins/**`. That is why a link like
`../../../scripts/runtime_bootstrap.py` in `skills/shared/references/` is green
-- from `skills/shared/references/` it really does resolve to the repo's own
`scripts/`. Once `export_plugin.py` copies that file to
`plugins/charness/shared/references/`, the same three levels land on
`plugins/scripts/`, which exists in no tree. The link is correct where it is
checked and broken where it is read.

This gate measures from the READER's position instead: a consumer installs
`plugins/<pkg>/` and has nothing above it. So a relative link in the mirror is
followable only when it resolves to a real file INSIDE its own plugin root.
Two distinct defects fall out of that one rule:

- **escape** -- the target climbs above `plugins/<pkg>/` (the #477 depth class in
  link form; 11 live instances at 2026-08-04).
- **missing** -- the target stays inside the plugin root but names nothing,
  which is how an exporter LAYOUT transform shows up. `../../public/hitl/...`
  is right in the authoring tree and wrong in the mirror, because the exporter
  flattens `skills/<kind>/<skill>/` to `skills/<skill>/`. An escape-only ruler
  cannot see this one.

Non-claim: this proves a path does not RESOLVE for a consumer. It does not prove
the named target would fail at runtime if reached some other way, and a clean
run is evidence about this ruler, not about the whole unreachable-file class.

The repair for an escape is normally a backticked `<authoring-repo>/...`
placeholder, not a different number of `../` -- the target genuinely is not in
the consumer's tree, and saying so is the honest form.

# floor-addition-restraint: BLOCKING on first sight, deliberately. The checklist
# asks for a recorded recurrence rather than one finding, and there is one: #477
# and #478 each enumerated and repaired this class, both closed, and a bounded
# review found 12 further live instances the moment the ruler widened. Three
# passes reported an honest "0 remaining" while these shipped, so an advisory
# would be read as the fourth. The verdict is decidable without judgment -- a
# relative path either resolves inside the installed package or it does not --
# which is why THIS axis is a gate while the judgment-bearing axes from the same
# sweep (bare `scripts/...`, which may legitimately mean the consumer's own tree)
# stay in #479's disposition table. It does not raise closeout-contract weight:
# no new artifact, no new ledger field, ~0.17s on the same `.md` trigger as the
# sibling gate it sits beside.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_generated_mirror_files = _scripts_repo_file_listing_module.iter_generated_mirror_files
GeneratedMirrorAbsentError = _scripts_repo_file_listing_module.GeneratedMirrorAbsentError

_markdown_doc_scan = import_repo_module(__file__, "scripts.markdown_doc_scan")
classify_link_shape = _markdown_doc_scan.classify_link_shape
iter_doc_lines = _markdown_doc_scan.iter_doc_lines
iter_link_targets = _markdown_doc_scan.iter_link_targets
resolve_relative_link = _markdown_doc_scan.resolve_relative_link
RELATIVE_LINK = _markdown_doc_scan.RELATIVE_LINK

PLUGIN_DOC_GLOBS = ("plugins/**/*.md",)


class ValidationError(Exception):
    pass


def plugin_root_for(root: Path, doc: Path) -> Path | None:
    """The `plugins/<pkg>` directory a consumer would install, or None.

    A markdown file sitting directly at `plugins/<pkg>.md` has no package root and
    is not part of any installed tree, so it is out of scope rather than a defect.
    """
    try:
        rel = doc.relative_to(root)
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) < 3 or parts[0] != "plugins":
        return None
    return root / parts[0] / parts[1]


def classify_link(doc: Path, plugin_root: Path, raw_target: str) -> str | None:
    """Return "escape", "missing", or None when the link is followable by a consumer.

    Anchors, external URLs, and mail links carry no filesystem claim. Absolute and
    bare targets are left to `check_doc_links.py`, which owns those rules for the
    authoring source these files are generated from -- duplicating them here would
    report the same defect twice under two names.
    """
    if classify_link_shape(raw_target) != RELATIVE_LINK:
        return None

    candidate = resolve_relative_link(doc, raw_target)
    try:
        candidate.relative_to(plugin_root.resolve())
    except ValueError:
        return "escape"
    return None if candidate.exists() else "missing"


def iter_unfollowable_links(
    root: Path, *, skipped: Counter | None = None, docs: list[Path] | None = None
) -> list[tuple[Path, str, str]]:
    """Scan live prose only -- fenced and commented lines blanked, not dropped.

    A link inside a fenced block or an HTML comment is an EXAMPLE, not an
    assertion that the reader can reach something. This gate's own docstring
    teaches the broken shape, so a doc demonstrating it in a fence is a likely
    future file, and refusing that would be a false positive in a blocking gate.

    But the live lines are re-joined into TEXT before matching rather than
    scanned one at a time, because `LINK_RE`'s character classes match newlines
    and a prose-wrapped link is one link:

        See the [agent assessment
        invariant](../../../scripts/runtime_bootstrap.py) for the rule.

    Per-line scanning finds nothing there, which would be a false negative in
    exactly the class this gate exists to close -- and it would also make this
    gate disagree with `check_doc_links.py`, which scans whole text, about what
    counts as a link at all. Blanking rather than deleting the skipped lines
    keeps a fence from splicing two unrelated lines into a spurious match.

    Whatever is skipped is COUNTED into ``skipped`` and reported, because a gate
    that skips silently and then prints "Validated" reads as full coverage -- and
    a clean count under an unstated ruler is the exact failure this gate was
    built to close (#479).
    """
    skipped = Counter() if skipped is None else skipped
    findings: list[tuple[Path, str, str]] = []
    # NOT `iter_matching_repo_files`: it filters through `git ls-files
    # --exclude-standard`, and `/plugins/` is gitignored, so this loop ran zero
    # times over a complete 229-doc mirror and still reported "Validated".
    # `docs` lets `main` establish the scope ONCE and still report its size --
    # recounting it separately would let the reported count drift from the
    # examined set, which is the same class of lie this repair exists to end.
    if docs is None:
        docs = iter_generated_mirror_files(root, PLUGIN_DOC_GLOBS)
    for doc in docs:
        plugin_root = plugin_root_for(root, doc)
        if plugin_root is None:
            skipped["no-plugin-root"] += 1
            continue
        live = {lineno: line for lineno, line, in_fence in iter_doc_lines(doc) if not in_fence}
        if not live:
            skipped["no-live-prose"] += 1
            continue
        text = "\n".join(live.get(lineno, "") for lineno in range(1, max(live) + 1))
        skipped["fenced-or-commented-link"] += len(iter_link_targets(doc.read_text(encoding="utf-8"))) - len(
            iter_link_targets(text)
        )
        for target in iter_link_targets(text):
            reason = classify_link(doc, plugin_root, target)
            if reason is not None:
                findings.append((doc.relative_to(root), target, reason))
    return findings


REASON_HELP = {
    "escape": (
        "climbs above its plugin root, so it lands outside anything a consumer installed; "
        "use a backticked `<authoring-repo>/...` placeholder when the target really is "
        "authoring-repo-internal"
    ),
    "missing": (
        "stays inside the plugin root but names no file there; the exporter's layout "
        "transform (kind-flattening `skills/<kind>/<skill>/` to `skills/<skill>/`) is the "
        "usual cause, so fix the link in the AUTHORING source and re-export"
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    skipped: Counter = Counter()
    try:
        docs = iter_generated_mirror_files(root, PLUGIN_DOC_GLOBS)
    except GeneratedMirrorAbsentError as exc:
        print(f"status: unestablished\n{exc}", file=sys.stderr)
        return 1
    findings = iter_unfollowable_links(root, skipped=skipped, docs=docs)
    skipped_note = (
        " skipped: " + ", ".join(f"{count} {reason}" for reason, count in sorted(skipped.items()) if count)
        if any(skipped.values())
        else " skipped: none"
    )
    if findings:
        lines = [
            f"{doc}: relative link `{target}` is unfollowable for a consumer ({reason}): "
            f"{REASON_HELP[reason]}"
            for doc, target, reason in findings
        ]
        raise ValidationError("\n".join(lines) + f"\n({len(findings)} unfollowable link(s);{skipped_note})")
    # The EXAMINED count leads, because "skipped: none" over an empty scope reads
    # exactly like "skipped: none" over a complete one -- which is how this gate
    # spent a session reporting success while scanning nothing.
    print(f"Validated relative links in {len(docs)} plugin-mirror doc(s).{skipped_note}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
