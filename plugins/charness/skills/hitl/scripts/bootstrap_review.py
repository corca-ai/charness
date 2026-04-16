#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
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
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)







_scripts_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
render_yaml_mapping = _scripts_adapter_lib_module.render_yaml_mapping


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def bootstrap_review(repo_root: Path, session_id: str, target: str, base_ref: str, scope: str) -> dict[str, str]:
    output_dir = repo_root / ".charness" / "hitl" / "runtime" / session_id
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "hitl-scratchpad.md").write_text(
        "\n".join(
            [
                f"# HITL Scratchpad: {session_id}",
                "",
                f"- Updated: {utc_now()}",
                f"- Target: {target}",
                f"- Base Ref: {base_ref}",
                f"- Scope: {scope}",
                "",
                "## Agreements",
                "",
                "## Open Questions",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "state.yaml").write_text(
        render_yaml_mapping(
            [
                ("session_id", session_id),
                ("status", "in_progress"),
                ("target", target),
                ("base_ref", base_ref),
                ("scope", scope),
                ("intent_resync_required", False),
                ("last_presented_chunk_id", ""),
                ("last_intent_resync_at", ""),
            ]
        ),
        encoding="utf-8",
    )
    (output_dir / "rules.yaml").write_text("rules: []\n", encoding="utf-8")
    (output_dir / "fix-queue.yaml").write_text("items: []\n", encoding="utf-8")
    (output_dir / "queue.json").write_text(
        json.dumps({"session_id": session_id, "target": target, "items": []}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "events.log").write_text(f"{utc_now()} bootstrap {target}\n", encoding="utf-8")
    return {
        "session_dir": str(output_dir),
        "scratchpad": str(output_dir / "hitl-scratchpad.md"),
        "state_file": str(output_dir / "state.yaml"),
        "queue_file": str(output_dir / "queue.json"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--session-id", default=f"hitl-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}")
    parser.add_argument("--target", default="git-diff")
    parser.add_argument("--base-ref", default="main")
    parser.add_argument("--scope", default="all")
    args = parser.parse_args()
    sys.stdout.write(
        json.dumps(
            bootstrap_review(args.repo_root.resolve(), args.session_id, args.target, args.base_ref, args.scope),
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
