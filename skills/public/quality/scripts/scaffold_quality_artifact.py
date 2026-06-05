#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
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

# Mirrors REQUIRED_SECTIONS in scripts/validate_quality_artifact.py. The scaffold
# emits a skeleton that passes that validator out of the box so an author fills
# slots instead of rediscovering the contract by trial-and-error.
SECTIONS = (
    "## Scope",
    "## Current Gates",
    "## Runtime Signals",
    "## Healthy",
    "## Weak",
    "## Missing",
    "## Deferred",
    "## Advisory",
    "## Delegated Review",
    "## Commands Run",
    "## Recommended Next Gates",
    "## History",
)


def default_title(title: str | None) -> str:
    return title if title else "Quality Review"


def render_template(*, title: str, date_text: str) -> str:
    # Validator note: the first line must be exactly "# Quality Review"; the
    # Runtime Signals/Advisory/Delegated Review/Recommended/History blocks below
    # carry the literal tokens validate_quality_artifact.py asserts on.
    lines = [f"# {title}", f"Date: {date_text}", ""]
    for heading in SECTIONS:
        if heading == "## Runtime Signals":
            lines.extend(
                [
                    heading,
                    "",
                    "- runtime source: structured metrics from `.charness/quality/runtime-signals.json`"
                    " rendered by `render_runtime_summary.py`; TODO profile (or state timing capture is missing).",
                    "- runtime hot spots: TODO top gate timings (latest / median vs budget).",
                    "- coverage gate: TODO run-quality pass/fail.",
                    "- evaluator depth: TODO live Cautilus run or deterministic-gates-only, and why.",
                    "",
                ]
            )
            continue
        if heading == "## Advisory":
            lines.extend(
                [
                    heading,
                    "",
                    "- TODO advisory bullet — cite `inventory`/command:/artifact: evidence"
                    " (or write `none found by inventory` with a `command:`).",
                    "",
                ]
            )
            continue
        if heading == "## Delegated Review":
            lines.extend(
                [
                    heading,
                    "",
                    "- Delegated Review: not_applicable — TODO record executed with the reviewer verdict,"
                    " or blocked with a concrete `host signal:`/`tool signal:`.",
                    "- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):"
                    " TODO whether re-delegated (required when status is executed and slow-gate scope).",
                    "",
                ]
            )
            continue
        if heading == "## Recommended Next Gates":
            lines.extend(
                [
                    heading,
                    "",
                    "- active TODO — name the exact gate/seam/command family to implement now.",
                    "- passive TODO — describe the watch item, because TODO it is not yet actionable.",
                    "",
                ]
            )
            continue
        if heading == "## History":
            lines.extend(
                [
                    heading,
                    "",
                    "- [TODO prior review](history/TODO-quality-review.md)",
                    "",
                ]
            )
            continue
        lines.extend([heading, "", "TODO", ""])
    return "\n".join(lines).rstrip() + "\n"


def validator_command(repo_root: Path) -> str:
    for ancestor in Path(__file__).resolve().parents:
        for script_name in ("validate_quality_artifact.py", "validate-quality-artifact.py"):
            candidate = ancestor / "scripts" / script_name
            if candidate.is_file():
                return f"python3 {candidate} --repo-root ."
    for script_name in ("validate_quality_artifact.py", "validate-quality-artifact.py"):
        repo_local = repo_root / "scripts" / script_name
        if repo_local.is_file():
            return f"python3 scripts/{script_name} --repo-root ."
    raise FileNotFoundError("validate_quality_artifact.py not found in installed Charness layout")


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:
        return str(path)


def _current_pointer_write_path(repo_root: Path, artifact_path: Path) -> tuple[str, str, str | None]:
    absolute_artifact_path = repo_root / artifact_path
    if not absolute_artifact_path.is_symlink():
        return str(artifact_path), "current_pointer", None
    raw_target = os.readlink(absolute_artifact_path)
    target_path = Path(raw_target)
    if not target_path.is_absolute():
        target_path = absolute_artifact_path.parent / target_path
    return _portable_path(repo_root, target_path), "current_pointer_target", raw_target


def payload_for(repo_root: Path, *, title: str | None) -> dict[str, object]:
    adapter = load_adapter(repo_root)
    output_dir = Path(adapter["data"]["output_dir"])
    date_text = dt.date.today().isoformat()
    resolved_title = default_title(title)
    artifact_path = output_dir / "latest.md"
    write_path, write_role, symlink_target = _current_pointer_write_path(repo_root, artifact_path)
    return {
        "artifact_path": str(artifact_path),
        "artifact_role": "current_pointer",
        "write_artifact_path": write_path,
        "write_artifact_role": write_role,
        "current_pointer_symlink_target": symlink_target,
        "date": date_text,
        "title": resolved_title,
        "template": render_template(title=resolved_title, date_text=date_text),
        "validator_command": validator_command(repo_root),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root to scaffold the quality artifact into")
    parser.add_argument("--title", help="Title for the scaffolded quality artifact")
    parser.add_argument("--json", action="store_true", help="Emit the payload as JSON instead of the rendered template")
    args = parser.parse_args()

    payload = payload_for(args.repo_root.resolve(), title=args.title)
    if args.json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(payload["template"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
