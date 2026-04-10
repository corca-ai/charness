#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path


class ValidationError(Exception):
    pass


REPRESENTATIVE_CONTRACTS: dict[str, tuple[str, ...]] = {
    "skills/public/handoff/SKILL.md": (
        "mention-only pickup",
        "Run a misunderstanding premortem",
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
    ),
    "skills/public/spec/SKILL.md": (
        "## Contract Shaping",
        "Choose the lightest honest contract shape.",
        "keep the contract",
        "probe-friendly and visible instead of inventing a user-facing mode choice.",
        "- `Fixed Decisions`",
        "- `Probe Questions`",
        "- `Deferred Decisions`",
        "- `Acceptance Checks`",
        "- `First Implementation Slice`",
    ),
    "skills/public/impl/SKILL.md": (
        "impl adapter resolution and verification survey",
        "best self-verification path before you code and again before you stop",
        "inspect the real output in a browser or equivalent",
        "real invocation over mock-only proof",
        "propose the install or setup during onboarding",
    ),
    "skills/public/quality/SKILL.md": (
        "When the next quality move is repo-local, deterministic, and low-risk",
        "implementing that gate in the same turn",
        "when the automatable move is already clear and repo-owned, implement it in",
        "If you stop short of an obvious repo-owned deterministic gate",
    ),
    "skills/public/retro/SKILL.md": (
        "If the user correctly points out a missed issue",
        "`Persisted`: whether the retro was written to a durable artifact",
        "never stop without stating `Persisted: yes <path>` or `Persisted: no <reason>`",
        "Trigger a short `session` retro automatically when a user correction exposes a",
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
