#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import runpy
import shlex
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
_adapter_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapters.adapter_version_verdict"
)
_artifact_naming = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.artifact_naming_lib")
_refresh_current_pointer = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.refresh_current_pointer")
_scaffold_artifact_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.core.scaffold_artifact_lib")
dated_artifact_filename = _artifact_naming.dated_artifact_filename
slugify = _artifact_naming.slugify
_summary_output = SKILL_RUNTIME.load_local_skill_module(__file__, "summary_output_lib")


def payload_for(repo_root: Path, *, slug: str, intent: str, artifact_date: dt.date) -> dict[str, object]:
    # GUARDED AT THE READ SITE. Every ARTIFACT path this function returns is derived from
    # `output_dir` (the `refresh_current_pointer_argv` entry is not, and a bounded review
    # was right that the universal was overstated), so an unhonored declaration relocates the quality artifact rather than
    # degrading the answer. Measured at `00c50ed3f`: a repo declaring
    # `output_dir: docs/mine-q` under `version: 9` returned
    # `artifact_path: charness-artifacts/quality/latest.md`, exit 0.
    refusal = _adapter_version_verdict.unspeakable_version_message(
        load_adapter, repo_root, adapter_name="quality-adapter.yaml"
    )
    if refusal is not None:
        raise SystemExit(refusal)
    adapter = load_adapter(repo_root)
    output_dir = Path(adapter["data"]["output_dir"])
    current_path = output_dir / "latest.md"
    record_path = output_dir / dated_artifact_filename(slugify(slug), artifact_date=artifact_date)
    pointer_state = _scaffold_artifact_lib.published_pointer_state(repo_root, repo_root / current_path)
    if intent == "record":
        write_path = str(record_path)
        write_role = "durable_record"
        update_current = True
        refresh_argv = [
            "python3",
            str(Path(_refresh_current_pointer.__file__).resolve()),
            "--repo-root",
            ".",
            "--skill-id",
            "quality",
            "--record-artifact-path",
            str(record_path),
            "--execute",
        ]
        refresh_command = shlex.join(refresh_argv)
    else:
        write_path, write_role, _ = _scaffold_artifact_lib.current_pointer_write_path(repo_root, current_path)
        update_current = False
        refresh_argv = None
        refresh_command = None
    payload = {
        "skill_id": "quality",
        "intent": intent,
        "slug": slugify(slug),
        "date": artifact_date.isoformat(),
        "artifact_path": str(current_path),
        "record_artifact_path": str(record_path),
        "record_artifact_supported": True,
        "current_artifact_path": str(current_path),
        "write_artifact_path": write_path,
        "write_artifact_role": write_role,
        **_scaffold_artifact_lib.write_target_facts(repo_root, write_path),
        "update_current_pointer_after_write": update_current,
        "refresh_current_pointer_argv": refresh_argv,
        "refresh_current_pointer_command": refresh_command,
    }
    payload.update(pointer_state)
    return payload


def main() -> int:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="quality resolve_quality_artifact")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root whose quality artifact paths should be resolved")
    parser.add_argument("--slug", default="quality-review", help="Slug used in the dated quality artifact filename")
    parser.add_argument("--intent", choices=("current", "record"), default="current", help="Whether to resolve the current pointer or a new dated record")
    parser.add_argument("--date", help="ISO date stamp for the record artifact (defaults to today)")
    try:
        args = parser.parse_args()
        artifact_date = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
        payload = payload_for(
            args.repo_root.resolve(),
            slug=args.slug,
            intent=args.intent,
            artifact_date=artifact_date,
        )
        _summary_output.emit_yaml(payload)
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
