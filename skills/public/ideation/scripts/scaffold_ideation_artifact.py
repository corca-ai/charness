#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

# `ideation` is a conversation-first skill with no adapter or scripts package, so
# this scaffold is self-contained: it writes per-concept dated records under a
# fixed default directory. The validator is opt-in and only enforces the
# `## Structured Questions` schema, so the emitted skeleton carries a valid
# structured block (the part most easily hand-typed wrong) and exercises
# scripts/validate_ideation_artifact.py via `--paths` out of the box.
DEFAULT_OUTPUT_DIR = "charness-artifacts/ideation"

# Mirrors the enums in scripts/validate_ideation_artifact.py so the emitted
# `## Structured Questions` block validates unedited.
STRUCTURED_QUESTIONS = (
    "- Q1 | urgency: must-resolve | depends-on: null | action: spec"
    " | note: TODO the decision that blocks the build contract",
    "- Q2 | urgency: probe-in-impl | depends-on: Q1 | action: impl"
    " | note: TODO the item safe to defer into implementation as a probe",
)


def default_title(title: str | None) -> str:
    return title if title else "Concept Ideation"


def _slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "concept"


def render_template(*, title: str, date_text: str) -> str:
    lines = [f"# {title}", f"Date: {date_text}", ""]
    lines.extend(["## World Model", "", "TODO who the user is, the job, and the status quo.", ""])
    lines.extend(["## Verified Facts", "", "- TODO fact with its source.", ""])
    lines.extend(["## Assumptions", "", "- TODO assumption to test, and how.", ""])
    lines.extend(["## Structured Questions", "", *STRUCTURED_QUESTIONS, ""])
    lines.extend(["## Open Questions", "", "- TODO prose open question for the conversation.", ""])
    lines.extend(["## Next Step", "", "TODO route to spec, impl, or hold, and why.", ""])
    return "\n".join(lines).rstrip() + "\n"


def validator_command(repo_root: Path, write_artifact_path: str) -> str:
    # Prefer the repo-local validator when the working repo owns one so the cited
    # check == the broad gate; fall back to the installed-plugin copy only for a
    # consumer repo that ships no validator of its own. Repo-local-first kills the
    # installed-vs-repo version-skew class (an installed validator looser than the
    # repo's must not shadow it).
    for script_name in ("validate_ideation_artifact.py", "validate-ideation-artifact.py"):
        repo_local = repo_root / "scripts" / script_name
        if repo_local.is_file():
            return f"python3 scripts/{script_name} --repo-root . --paths {write_artifact_path}"
    for ancestor in Path(__file__).resolve().parents:
        for script_name in ("validate_ideation_artifact.py", "validate-ideation-artifact.py"):
            candidate = ancestor / "scripts" / script_name
            if candidate.is_file():
                return f"python3 {candidate} --repo-root . --paths {write_artifact_path}"
    raise FileNotFoundError("validate_ideation_artifact.py not found in installed Charness layout")


def payload_for(repo_root: Path, *, title: str | None) -> dict[str, object]:
    date_text = dt.date.today().isoformat()
    resolved_title = default_title(title)
    write_artifact_path = f"{DEFAULT_OUTPUT_DIR}/{date_text}-{_slug(resolved_title)}.md"
    return {
        "artifact_path": write_artifact_path,
        "artifact_role": "record",
        "write_artifact_path": write_artifact_path,
        "date": date_text,
        "title": resolved_title,
        "template": render_template(title=resolved_title, date_text=date_text),
        "validator_command": validator_command(repo_root, write_artifact_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root to scaffold the ideation artifact into")
    parser.add_argument("--title", help="Title for the scaffolded ideation artifact")
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
