#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_setup_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "setup_adapter")
_render_skill_routing_module = SKILL_RUNTIME.load_local_skill_module(__file__, "render_skill_routing")
_inspect_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.setup_inspect_lib")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root to inspect")
    args = parser.parse_args()
    payload = _inspect_lib.build_setup_inspection_payload(
        args.repo_root.resolve(),
        load_setup_adapter=_setup_adapter_module.load_setup_adapter,
        prose_wrap_state=_setup_adapter_module.prose_wrap_state,
        recommendation_policy=_setup_adapter_module.recommendation_policy,
        surface_overrides=_setup_adapter_module.surface_overrides,
        skill_routing_payload=_render_skill_routing_module.build_payload,
    )
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
