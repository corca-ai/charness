#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path


class ValidationError(Exception):
    pass


# Each tuple below pins the exact substrings a SKILL.md must contain so that
# load-bearing authoring contracts cannot be silently rewritten. When a pinned
# snippet is removed, the gate fails with a generic "missing snippet" error,
# so new pins should be grouped under their own dict entry with a short
# comment explaining the contract they protect — not added to an unrelated
# skill's tuple. When a pinned snippet is edited, the gate will fail and the
# fix is to update both the skill body and this list in the same commit.
REPRESENTATIVE_CONTRACTS: dict[str, tuple[str, ...]] = {
    "skills/public/handoff/SKILL.md": (
        "mention-only pickup",
        "Run a misunderstanding premortem",
        "Assume a competent next operator can follow one good link",
        "one reference to the owning artifact for metrics, history, or proof detail",
        "always-loaded host instruction surfaces out of `References` by",
        "The handoff should usually contain:",
        "- `Workflow Trigger`",
        "- `Current State`",
        "- `Next Session`",
        "- `Discuss`",
        "- `References`",
    ),
    "skills/public/gather/SKILL.md": (
        "Prefer primary sources.",
        "Refresh in place when the source identity matches.",
        "local files before external summaries",
        "browser-mediated fallback through `agent-browser`",
        "official API/export docs before browser automation",
        "- `Requested Facts`",
        "- `Open Gaps`",
    ),
    "skills/public/create-skill/SKILL.md": (
        "public skill: one user-facing concept",
        "support skill: teaches tool usage without becoming product philosophy",
        "if an upstream support skill already exists, prefer reference, sync, or a",
        "keep manifest",
        "metadata rich enough to reveal capability kind and supported access modes",
        "express them as manifest readiness checks",
        "If a skill needs the same bootstrap, adapter resolution, artifact upsert, or",
        "Treat public-skill frontmatter and generated AGENTS hints as classifier input",
        'python3 "$SKILL_DIR/../quality/scripts/suggest_public_skill_dogfood.py" --repo-root . --skill-id <skill-id>',
        # Binary Preflight Philosophy — pins the lazy-preflight contract so
        # that future edits cannot silently drop the "declare, detect, ask"
        # loop or the CHARNESS_BASELINE / CHARNESS_BINARY_PREFLIGHT names.
        "## Binary Preflight Philosophy",
        "Public skills must not silently assume non-baseline binaries",
        "CHARNESS_BASELINE",
        "Preflight is lazy, not eager",
        "CHARNESS_BINARY_PREFLIGHT=degraded",
        "Auto-install is forbidden",
        "Silent skip is forbidden",
    ),
    "skills/public/spec/SKILL.md": (
        "## Contract Shaping",
        "Choose the lightest honest contract shape.",
        "keep the contract",
        "probe-friendly and visible instead of inventing a user-facing mode choice.",
        "public executable contract",
        "maintenance lint / implementation guard",
        "- `Fixed Decisions`",
        "- `Probe Questions`",
        "- `Deferred Decisions`",
        "- `Acceptance Checks`",
        "- `First Implementation Slice`",
    ),
    "skills/public/impl/SKILL.md": (
        "impl adapter resolution and verification survey",
        "best self-verification path before you code and again before you stop",
        "re-read `Fixed Decisions` and named acceptance checks",
        "reflected in the delivered slice or explicitly",
        "$SKILL_DIR/../retro/scripts/check_auto_trigger.py",
    ),
    "skills/public/quality/SKILL.md": (
        "When the next quality move is repo-local, deterministic, and low-risk",
        "implementing that gate in the same turn",
        "when the automatable move is already clear and repo-owned, implement it in",
        "If you stop short of an obvious repo-owned deterministic gate",
        "$SKILL_DIR/scripts/inventory_public_spec_quality.py",
        "duplicated at the wrong layer",
        'scaffold one consumer-side dogfood case with `python3 "$SKILL_DIR/scripts/suggest_public_skill_dogfood.py" --repo-root . --skill-id <skill-id>`',
        "Do not stop at producer-side validators alone when the risk is public-skill routing or durable artifact behavior",
    ),
    "skills/public/narrative/SKILL.md": (
        "map the current source-of-truth surface",
        "rewrite the durable docs so the current story is honest in one place",
        "If the idea is still under-shaped, use `ideation` first.",
        "keep it audience-neutral by default",
        "when the repo adapter declares `brief_template`, use that ordered skeleton",
        "Hand off to `announcement` only when the user explicitly wants human-facing",
    ),
    "skills/public/release/SKILL.md": (
        "maintainer-facing workflow",
        "Choose the lightest honest bump",
        "patch for bug fixes, copy fixes, and behavior repairs",
        "Do not hand-edit generated plugin manifests",
        "Do not push, tag, or announce a release without explicit user confirmation",
    ),
    "skills/public/retro/SKILL.md": (
        "If the user correctly points out a missed issue",
        "`Persisted`: whether the retro was written to a durable artifact",
        "never stop without stating `Persisted: yes <path>` or `Persisted: no <reason>`",
        "Trigger a short `session` retro automatically when a user correction exposes a",
        "`Trends vs Last Retro`: for `weekly`, compare against the last durable weekly retro when one exists",
        "Only write a weekly snapshot when the adapter gives an explicit `snapshot_path`",
    ),
}


def validate_contract(path: Path, snippets: tuple[str, ...]) -> None:
    if not path.exists():
        raise ValidationError(f"missing representative contract file `{path}`")
    contents = path.read_text(encoding="utf-8")
    missing = [snippet for snippet in snippets if snippet not in contents]
    if missing:
        formatted = ", ".join(f"`{snippet}`" for snippet in missing)
        raise ValidationError(f"{path}: missing required contract snippet(s): {formatted}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    for rel_path, snippets in REPRESENTATIVE_CONTRACTS.items():
        validate_contract(root / rel_path, snippets)

    print(f"Validated {len(REPRESENTATIVE_CONTRACTS)} representative skill contracts.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
