#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import re
import runpy
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
_scaffold_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.scaffold_artifact_lib")

VALIDATOR_SCRIPT_NAMES = ("validate_retro_artifact.py", "validate-retro-artifact.py")

# The scaffold emits every current structural field in a validating state. The
# author replaces the honest missing-start lesson disposition only when a
# declared session actually existed.


def default_title(title: str | None) -> str:
    return title if title else "Session Retro"


def _slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "retro"


def _sections_without_owned_headings(artifact_sections: list[str], owned: frozenset[str]) -> list[str]:
    """Drop every adapter-declared block whose H2 the scaffold already emits.

    ``artifact_sections`` used to be appended verbatim, so an adapter declaring a
    heading the scaffold also owns produced that section TWICE. This repo's own
    ``.agents/retro-adapter.yaml`` declared ``## Lesson Evaluation`` -- the exact
    heading the lesson-evaluation floor requires to appear EXACTLY once -- so the
    scaffold emitted an artifact its own validator refused twice over (`expected
    exactly one ... found 2`, then the duplicated `Lesson evaluation:` line).
    That is the same "the prescribed path does not produce a valid artifact"
    defect the seeded disposition block was added to fix -- shipped by that very
    repair, because it appended without looking at what the adapter declared.

    Scaffold-owned headings win because they are the ones the floors read and the
    scaffold's block is the one seeded in a validating state; an adapter that
    wants a different section names a different heading. Dropping is per BLOCK,
    not per line, so the colliding section's body goes with its heading rather
    than stranding orphan prose under the scaffold's own heading.
    """
    kept: list[str] = []
    dropping = False
    for line in artifact_sections:
        stripped = line.strip()
        if stripped.startswith("## "):
            dropping = stripped in owned
        if not dropping:
            kept.append(line)
    return kept


def render_template(*, title: str, date_text: str, artifact_sections: list[str] | None = None) -> str:
    lines = [f"# {title}", f"Date: {date_text}", ""]
    lines.extend(["## Context", "", "TODO what happened and why this retro.", ""])
    lines.extend(["## Evidence Summary", "", "- TODO concrete evidence (paths, line counts, command output).", ""])
    lines.extend(["## Waste", "", "TODO what created rework or wasted effort.", ""])
    lines.extend(["## Critical Decisions", "", "- TODO the decision that shaped the next move.", ""])
    # Seeded, not left to memory: the validator requires this section, and two
    # consecutive retros shipped without it while the skill prose already asked
    # for it. An author meets the obligation where they write, not at the gate.
    lines.extend(
        [
            "## North Star Alignment",
            "",
            "TODO read this repo's governing design standard —"
            " `<authoring-repo>/docs/design-north-star.md`",
            "in the authoring repo, or whatever this repo names as its own (design principles,",
            "invariants) — and record what it says about THIS work: which facets held, which",
            "were mis-applied, and any named failure signature the run walked into. Reviewing",
            "the work only against itself has no frame.",
            "",
        ]
    )
    lines.extend(
        [
            "## Expert Counterfactuals",
            "",
            "- TODO a named-expert or direct counterfactual lens that would have changed the next move.",
            "",
        ]
    )
    lines.extend(
        [
            "## Sibling Search",
            "",
            "- TODO axis: TODO location | decision: valid follow-up outside the slice"
            " | proof: TODO | follow-up: deferred TODO-handoff-anchor",
            "",
        ]
    )
    # Built before the adapter sections are placed, because the collision check
    # must see the headings the scaffold emits AFTER them too.
    trailer = [
        "## Lesson Evaluation",
        "",
        'Lesson evaluation: {"reason":"missing-start","score_event_count":0,"session_id":"none","status":"not-evaluated"}',
        "",
        "## Next Improvements",
        "",
        "- workflow: TODO",
        "- capability: TODO",
        "- memory: TODO",
        "",
        "## Persisted",
        "",
        "Persisted: yes: TODO path",
        "",
    ]
    owned = frozenset(
        line.strip() for line in (*lines, *trailer) if line.strip().startswith("## ")
    )
    if artifact_sections:
        kept = _sections_without_owned_headings(list(artifact_sections), owned)
        if kept:
            lines.extend([*kept, ""])
    lines.extend(trailer)
    return "\n".join(lines).rstrip() + "\n"


def validator_command(repo_root: Path, write_artifact_path: str) -> str:
    return _scaffold_lib.validator_command(
        repo_root=repo_root,
        script_file=__file__,
        script_names=VALIDATOR_SCRIPT_NAMES,
        artifact_path=write_artifact_path,
    )


def payload_for(repo_root: Path, *, title: str | None) -> dict[str, object]:
    adapter = load_adapter(repo_root)
    output_dir = str(adapter["data"]["output_dir"])
    date_text = dt.date.today().isoformat()
    resolved_title = default_title(title)
    write_artifact_path = f"{output_dir}/{date_text}-{_slug(resolved_title)}.md"
    return _scaffold_lib.dated_record_payload(
        repo_root,
        write_artifact_path=write_artifact_path,
        date_text=date_text,
        title=resolved_title,
        template=render_template(
            title=resolved_title,
            date_text=date_text,
            artifact_sections=list(adapter["data"].get("artifact_sections", [])),
        ),
        validator_command=validator_command(repo_root, write_artifact_path),
    )


def main() -> int:
    return _scaffold_lib.emit_payload_main(payload_for, artifact_label="retro")


if __name__ == "__main__":
    raise SystemExit(main())
