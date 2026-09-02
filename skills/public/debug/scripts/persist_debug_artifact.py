#!/usr/bin/env python3
"""Persist one debug artifact through the scaffold-selected path and validator."""
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
_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter.load_adapter
_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapters.adapter_version_verdict"
)
_persistence = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.debug_persistence_lib"
)
_scaffold = SKILL_RUNTIME.load_local_skill_module(__file__, "scaffold_debug_artifact")
emit_yaml = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output").emit_yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--artifact-path", required=True, help="Exact repo-relative path from scaffold `write_artifact_path`.")
    parser.add_argument("--title", default=None)
    parser.add_argument("--subject", default=None)
    parser.add_argument("--markdown-file", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.expanduser().resolve()
    adapter = load_adapter(repo_root)
    errors = adapter.get("errors")
    if _version_verdict.declarations_unhonored(errors):
        print(
            "debug adapter declarations are not honored; refusing to persist an artifact. "
            + _version_verdict.unhonored_remedy(errors, "debug-adapter.yaml"),
            file=sys.stderr,
        )
        return 1
    scaffold = _scaffold.payload_for(repo_root, title=args.title, subject=args.subject)
    output_dir = Path(str(adapter["data"]["output_dir"]))
    declared_path = Path(str(scaffold["write_artifact_path"]))
    pointer_path = Path(str(scaffold["artifact_path"]))
    raw_candidate = Path(args.artifact_path)
    if raw_candidate.is_absolute() or ".." in raw_candidate.parts:
        print("debug artifact path must be a repo-relative path", file=sys.stderr)
        return 1
    candidate = repo_root / raw_candidate
    try:
        candidate_relative = raw_candidate
        candidate.resolve().relative_to(repo_root)
        if candidate_relative not in {declared_path, pointer_path}:
            print(
                "debug artifact path is not the scaffold-selected write_artifact_path",
                file=sys.stderr,
            )
            return 1
    except ValueError:
        print("debug artifact path must stay inside --repo-root", file=sys.stderr)
        return 1
    # `candidate_relative` is already the lexical, repo-relative Path validated
    # above.  There is no operation here that can raise ValueError; keeping a
    # dead exception arm made the refusal surface look executable without giving
    # it a reachable contract.
    relative = candidate_relative
    prefix = output_dir.as_posix().rstrip("/") + "/"
    if not relative.as_posix().startswith(prefix):
        print(
            f"debug artifact path must stay under adapter output directory `{prefix}`",
            file=sys.stderr,
        )
        return 1
    markdown_text = args.markdown_file.expanduser().read_text(encoding="utf-8")
    validator_command = _scaffold.validator_command(repo_root, relative.as_posix())
    result = _persistence.persist_debug_artifact(
        repo_root=repo_root,
        artifact_path=relative,
        markdown_text=markdown_text,
        validator_command=validator_command,
    )
    emit_yaml(result)
    return 0 if result["validated"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
