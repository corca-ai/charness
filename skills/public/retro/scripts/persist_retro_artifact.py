#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)







_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter
_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapters.adapter_version_verdict"
)

_scripts_retro_persistence_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.retro_debug.retro_persistence_lib")
persist_retro_artifact = _scripts_retro_persistence_lib_module.persist_retro_artifact

emit_yaml = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output").emit_yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root that owns the retro adapter and output directory")
    parser.add_argument(
        "--artifact-name",
        required=True,
        help="Subject key, or an explicitly named dated retro artifact filename",
    )
    parser.add_argument("--markdown-file", type=Path, required=True, help="Path to the rendered retro markdown body to persist")
    parser.add_argument(
        "--goal-path",
        type=Path,
        help=(
            "Opt into goal-aware persistence; the retro must contain exactly one "
            "matching `Goal:` field before any output is written"
        ),
    )
    parser.add_argument(
        "--goal-lineage-file",
        type=Path,
        help="Bind the retro to one repo-local Goal Run lineage JSON; cannot be combined with --goal-path.",
    )
    parser.add_argument(
        "--force-empty-summary",
        action="store_true",
        help=(
            "Allow the summary refresh to write an empty-stub digest even when "
            "lesson extraction returns 0 candidates and a non-stub summary "
            "already exists. Default behavior preserves the existing summary."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    SKILL_RUNTIME.require_repo_local_helper(__file__, repo_root)
    adapter = load_adapter(repo_root)
    # Both paths below are adapter-declared, and a version this reader cannot speak
    # leaves both at the charness defaults: the retro would be persisted outside the
    # directory the repo keeps retros in, and a SECOND lessons digest would appear at
    # the default `summary_path` while the repo's own stopped being refreshed -- on the
    # surface every session reads before work.
    #
    # Widened in round 2 of the slice-5 review: this asked `version_refused`, one of the
    # two doors into "nothing declared is honored". A parser refusal is the other, and
    # would have written a shadow retro AND a shadow lessons digest at the charness
    # defaults -- on the surface every session reads before work.
    errors = adapter.get("errors")
    if _version_verdict.declarations_unhonored(errors):
        print(
            f"retro adapter {_version_verdict.unhonored_cause(errors)} "
            f"({'; '.join(errors or [])}); nothing it declares is honored, "
            "so this retro would be written to the charness default directory rather "
            "than this repo's. "
            + _version_verdict.unhonored_remedy(errors, "retro-adapter.yaml"),
            file=sys.stderr,
        )
        return 1
    output_dir = repo_root / adapter["data"]["output_dir"]
    summary_rel = adapter["data"].get("summary_path")
    markdown_text = args.markdown_file.read_text(encoding="utf-8")
    try:
        result = persist_retro_artifact(
            repo_root=repo_root,
            output_dir=output_dir,
            artifact_name=args.artifact_name,
            markdown_text=markdown_text,
            summary_path=(repo_root / summary_rel) if isinstance(summary_rel, str) else None,
            force_empty_summary=args.force_empty_summary,
            goal_path=args.goal_path,
            goal_lineage_path=args.goal_lineage_file,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    emit_yaml(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
