#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import importlib.util
import re
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
VALIDATOR_SCRIPT_NAMES = ("validate_ideation_artifact.py", "validate-ideation-artifact.py")


def _load_scaffold_artifact_lib():
    for ancestor in Path(__file__).resolve().parents:
        candidate = ancestor / "scripts" / "scaffold_artifact_lib.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("scaffold_artifact_lib", candidate)
            if spec is None or spec.loader is None:
                raise ImportError(f"Unable to load scaffold_artifact_lib from {candidate}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scaffold_artifact_lib.py not found")


_scaffold_lib = _load_scaffold_artifact_lib()


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
    return _scaffold_lib.validator_command(
        repo_root=repo_root,
        script_file=__file__,
        script_names=VALIDATOR_SCRIPT_NAMES,
        artifact_path=write_artifact_path,
    )


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
    return _scaffold_lib.emit_payload_main(payload_for, artifact_label="ideation")


if __name__ == "__main__":
    raise SystemExit(main())
