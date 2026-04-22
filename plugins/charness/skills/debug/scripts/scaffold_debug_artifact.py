#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
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
            sys.modules.setdefault(spec.name, module)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter.load_adapter

SECTIONS = (
    "## Problem",
    "## Correct Behavior",
    "## Observed Facts",
    "## Reproduction",
    "## Candidate Causes",
    "## Hypothesis",
    "## Verification",
    "## Root Cause",
    "## Seam Risk",
    "## Interrupt Decision",
    "## Prevention",
)


def default_title(title: str | None) -> str:
    return title if title else "Debug Review"


def render_template(*, title: str, date_text: str) -> str:
    lines = [f"# {title}", f"Date: {date_text}", ""]
    for heading in SECTIONS:
        if heading == "## Candidate Causes":
            lines.extend([heading, "", "- TODO", "- TODO", "- TODO", ""])
            continue
        if heading == "## Seam Risk":
            lines.extend(
                [
                    heading,
                    "",
                    "- Interrupt ID: TODO",
                    "- Risk Class: none",
                    "- Seam: none",
                    "- Disproving Observation: none",
                    "- What Local Reasoning Cannot Prove: none",
                    "- Generalization Pressure: none",
                    "",
                ]
            )
            continue
        if heading == "## Interrupt Decision":
            lines.extend(
                [
                    heading,
                    "",
                    "- Premortem Required: no",
                    "- Next Step: impl",
                    "- Handoff Artifact: none",
                    "",
                ]
            )
            continue
        lines.extend([heading, "", "TODO", ""])
    return "\n".join(lines).rstrip() + "\n"


def payload_for(repo_root: Path, *, title: str | None) -> dict[str, object]:
    adapter = load_adapter(repo_root)
    output_dir = Path(adapter["data"]["output_dir"])
    date_text = dt.date.today().isoformat()
    resolved_title = default_title(title)
    return {
        "artifact_path": str(output_dir / "latest.md"),
        "date": date_text,
        "title": resolved_title,
        "template": render_template(title=resolved_title, date_text=date_text),
        "validator_command": "python3 scripts/validate-debug-artifact.py --repo-root .",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--title")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = payload_for(args.repo_root.resolve(), title=args.title)
    if args.json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(payload["template"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
