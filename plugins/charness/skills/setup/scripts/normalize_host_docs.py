#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_render_skill_routing = SKILL_RUNTIME.load_local_skill_module(__file__, "render_skill_routing")
_host_docs = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.setup_host_docs_lib")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize only AGENTS.md and CLAUDE.md according to setup host-doc policy."
    )
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root to normalize")
    parser.add_argument("--execute", action="store_true", help="Write AGENTS.md and/or CLAUDE.md symlink")
    args = parser.parse_args()
    payload = _host_docs.normalize_host_docs(
        args.repo_root.resolve(),
        skill_routing_payload=_render_skill_routing.build_payload,
        execute=args.execute,
    )
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return 1 if payload["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
