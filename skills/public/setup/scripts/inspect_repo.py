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
_setup_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "setup_adapter")
_render_skill_routing_module = SKILL_RUNTIME.load_local_skill_module(__file__, "render_skill_routing")
_inspect_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.setup_inspect_lib")
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")


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
    yaml_output.emit_yaml(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
