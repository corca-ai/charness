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


def portable_path(repo_root: Path, value: str) -> str:
    path = Path(value)
    if not path.is_absolute():
        return value
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return f"external-path:{path.name}"


def target_provenance(repo_root: Path, value: str) -> dict[str, str]:
    path = Path(value)
    if not path.is_absolute():
        return {"kind": "logical-or-repo-relative"}
    try:
        path.resolve().relative_to(repo_root)
    except ValueError:
        return {"kind": "external-path", "basename": path.name}
    return {"kind": "repo-root-relative"}


def bootstrap_review(repo_root: Path, session_id: str, target: str, base_ref: str, scope: str) -> dict[str, str]:
    output_dir = repo_root / ".charness" / "hitl" / "runtime" / session_id
    output_dir.mkdir(parents=True, exist_ok=True)
    portable_target = portable_path(repo_root, target)
    provenance = target_provenance(repo_root, target)

    (output_dir / "hitl-scratchpad.md").write_text(
        "\n".join(
            [
                f"# HITL Scratchpad: {session_id}",
                "",
                f"- Updated: {utc_now()}",
                f"- Target: {portable_target}",
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
                ("target", portable_target),
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
        json.dumps(
            {"session_id": session_id, "target": portable_target, "target_provenance": provenance, "items": []},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "events.log").write_text(f"{utc_now()} bootstrap {portable_target}\n", encoding="utf-8")
    return {
        "session_dir": output_dir.relative_to(repo_root).as_posix(),
        "scratchpad": (output_dir / "hitl-scratchpad.md").relative_to(repo_root).as_posix(),
        "state_file": (output_dir / "state.yaml").relative_to(repo_root).as_posix(),
        "queue_file": (output_dir / "queue.json").relative_to(repo_root).as_posix(),
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
