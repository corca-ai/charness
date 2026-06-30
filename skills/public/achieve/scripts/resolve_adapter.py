#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
adapter_policy = SKILL_RUNTIME.load_local_skill_module(__file__, "achieve_adapter_policy")


def main() -> None:
    SKILL_RUNTIME.run_adapter_cli(
        adapter_policy.load_adapter,
        label="achieve resolve_adapter",
        repo_root_help="Repo root to load the achieve adapter from",
        description="Resolve the optional achieve adapter policy.",
    )


if __name__ == "__main__":
    main()
