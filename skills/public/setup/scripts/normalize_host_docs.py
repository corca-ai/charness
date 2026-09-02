#!/usr/bin/env python3
from __future__ import annotations

import argparse
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_host_docs = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.setup.setup_host_docs_lib")
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize only AGENTS.md and CLAUDE.md according to setup host-doc policy."
    )
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root to normalize")
    parser.add_argument("--execute", action="store_true", help="Write the planned AGENTS.md and/or CLAUDE.md change")
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Replace an existing AGENTS.md with setup's minimal template; without this flag it is preserved",
    )
    args = parser.parse_args()
    payload = _host_docs.normalize_host_docs(
        args.repo_root.resolve(),
        execute=args.execute,
        compact=args.compact,
    )
    yaml_output.emit_yaml(payload)
    return 1 if payload["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
