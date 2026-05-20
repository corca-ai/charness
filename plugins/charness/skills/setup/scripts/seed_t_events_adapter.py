#!/usr/bin/env python3

"""Seed `.agents/t-events-adapter.yaml` for a charness consumer repo.

The t-events adapter declares whether charness skills should emit T-loop
lifecycle events (skill_invoked, lesson_cited, anchor_invoked) into this
repo. Captured events are the artifact-level analog of hermes-agent runtime
telemetry; the Skill-T mechanism inventory consumes them as Tier C evidence.

Defaults match Leg 6 of the issue 135 umbrella spec:
- enabled: true
- storage_path: .charness/t-events
- events: all v1 event types

Consumers that prefer not to capture events should set `enabled: false`
after seeding (the manifest still parses cleanly when disabled).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_TARGET = Path(".agents/t-events-adapter.yaml")
TEMPLATE = """\
# charness t-events adapter: capture T-loop lifecycle events emitted by
# charness skills running inside this repo. The Skill-T mechanism inventory
# reads these records as Tier C evidence.
#
# Schema:    integrations/t-events/manifest.schema.json
# Records:   integrations/t-events/event.schema.json
# Spec:      charness-artifacts/spec/issue-135-t-first-self-evolving-unit.md
# Storage:   .charness/t-events/<event_type>.jsonl (gitignore the directory)
version: 1
enabled: true
storage_path: .charness/t-events
events:
  - skill_invoked
  - lesson_cited
  - anchor_invoked
rotation:
  max_files: 5
  max_size_mb: 5
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing .agents/t-events-adapter.yaml.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the would-be manifest to stdout instead of writing.",
    )
    args = parser.parse_args()
    if args.dry_run:
        sys.stdout.write(TEMPLATE)
        return 0
    repo_root = args.repo_root.resolve()
    target = (repo_root / DEFAULT_TARGET).resolve()
    if target.is_file() and not args.force:
        print(f"{target} already exists; pass --force to overwrite.", file=sys.stderr)
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(TEMPLATE, encoding="utf-8")
    print(f"wrote {target.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
