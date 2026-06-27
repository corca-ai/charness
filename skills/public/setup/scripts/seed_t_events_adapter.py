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

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from seed_adapter_cli_lib import run_seed_adapter  # noqa: E402

DEFAULT_TARGET = Path(".agents/t-events-adapter.yaml")
TEMPLATE = (
    Path(__file__).resolve().parent / "templates" / "t_events_adapter.yaml"
).read_text(encoding="utf-8")


def main() -> int:
    return run_seed_adapter(
        description=__doc__,
        repo_root_help="Repo root whose t-events adapter should be seeded",
        target=DEFAULT_TARGET,
        force_help="Overwrite an existing .agents/t-events-adapter.yaml.",
        render=lambda _repo_root: TEMPLATE,
    )


if __name__ == "__main__":
    sys.exit(main())
