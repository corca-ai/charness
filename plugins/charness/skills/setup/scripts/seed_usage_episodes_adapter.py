#!/usr/bin/env python3

"""Seed `.agents/usage-episodes-adapter.yaml` for a product repo."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from seed_adapter_cli_lib import run_seed_adapter  # noqa: E402

DEFAULT_TARGET = Path(".agents/usage-episodes-adapter.yaml")
TEMPLATE = (
    Path(__file__).resolve().parent / "templates" / "usage_episodes_adapter.yaml"
).read_text(encoding="utf-8")


def main() -> int:
    options = {
        "description": __doc__,
        "repo_root_help": "Repo root whose usage-episodes adapter should be seeded",
        "target": DEFAULT_TARGET,
        "force_help": "Overwrite an existing .agents/usage-episodes-adapter.yaml.",
        "render": lambda _repo_root: TEMPLATE,
    }
    return run_seed_adapter(**options)


if __name__ == "__main__":
    sys.exit(main())
