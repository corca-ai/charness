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
_adapter_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapter_version_verdict"
)
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


#: Where charness keeps its own governing design standard. Named as a repo-relative
#: path because that is what it is IN THE REPO THAT HAS IT; the scaffold below only
#: writes it when this repo is the one being scaffolded.
NORTH_STAR_DOC = "docs/design-north-star.md"


def _north_star_prompt(repo_root: Path | None) -> str:
    """The North Star TODO line, resolved against the repo being scaffolded.

    This is a READ field -- prose a human reads in their own retro artifact -- and it
    used to carry the literal `<authoring-repo>/docs/design-north-star.md`. That
    spelling is charness's INTERNAL authoring vocabulary for "resolves in my tree, not
    yours"; a consuming author reads it as a path, looks for a directory named
    `<authoring-repo>`, and finds nothing. A placeholder in a read field is legitimate
    only when its reader knows the convention, and this reader does not.

    So: name the real file when the repo scaffolded actually has one, and otherwise say
    what to go find, with no placeholder at all.
    """
    if repo_root is not None and (repo_root / NORTH_STAR_DOC).is_file():
        return f"TODO read this repo's governing design standard — `{NORTH_STAR_DOC}` —"
    return (
        "TODO read this repo's governing design standard — whatever it names as its own "
        "(design principles, invariants, an architecture decision record) —"
    )


def render_template(
    *,
    title: str,
    date_text: str,
    artifact_sections: list[str] | None = None,
    repo_root: Path | None = None,
) -> str:
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
            _north_star_prompt(repo_root),
            "and record what it says about THIS work: which facets held, which were",
            "mis-applied, and any named failure signature the run walked into. Reviewing",
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


def _declared_session_id(repo_root: Path) -> str | None:
    """The declared lesson session THIS retro is being written for, from the router.

    The same routing helper the planner uses, so the scaffold cannot disagree with the plan
    the author is following about which session is open. Degrades to `None` — unknown, not a
    refusal — whenever the router cannot establish one, which is every repo with no lesson
    evaluator configured.
    """
    try:
        records = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.lesson_evaluation_records_lib")
        sessions = records.lesson_session_routing(repo_root).get("sessions") or []
    except Exception:
        return None
    session_id = sessions[0].get("session_id") if sessions and isinstance(sessions[0], dict) else None
    return session_id if isinstance(session_id, str) else None


def _session_suffix(session_id: str | None) -> str:
    """A filename-safe distinguisher from the session id, with its leading date dropped.

    The record is already dated, so `2026-08-15-session-retro-2026-08-15-s2.md` would carry
    that date twice; the session's own tail is what distinguishes it from the sibling retro.
    """
    if session_id is None:
        return "second"
    return _slug(re.sub(r"^\d{4}-\d{2}-\d{2}-?", "", session_id)) or "second"


def payload_for(repo_root: Path, *, title: str | None, subject: str | None = None) -> dict[str, object]:
    # GUARDED AT THE READ SITE. Every scaffold in this family reads its write TARGET out
    # of the adapter, so an unhonored declaration does not degrade the answer -- it
    # relocates the artifact. Measured on the real CLI at `0bcb6b227`: a repo declaring
    # `output_dir: docs/mine-retro` under `version: 9` got back `artifact_path: charness-artifacts/retro/<date>-probe.md`, exit 0, and the scaffold
    # would have written there.
    #
    # `payload_for` rather than `main()`, and here the importer claim is MEASURED rather
    # than assumed: `plan_retro_run` calls this function directly, so a refusal at the
    # entrypoint would have covered the CLI and left that caller on charness defaults.
    # (The same sentence was refuted for quality, critique and handoff, whose only
    # importers are tests -- see those files.)
    refusal = _adapter_version_verdict.unspeakable_version_message(
        load_adapter, repo_root, adapter_name="retro-adapter.yaml"
    )
    if refusal is not None:
        raise SystemExit(refusal)
    adapter = load_adapter(repo_root)
    output_dir = str(adapter["data"]["output_dir"])
    date_text = dt.date.today().isoformat()
    resolved_title = default_title(title)
    slug = _slug(subject or resolved_title)
    # The lesson session NAMES the sibling record; it no longer decides whether to write over
    # one. It cannot: a repo with no evaluator reads `None` on both sides, and the scaffold's
    # own seeded disposition says `"session_id":"none"`, so a session-keyed comparison called
    # two different sessions' retros the same subject in exactly the state this repo ships.
    # The decision is the records-only rule — never write a template over an existing record —
    # and the session is what makes the second record's filename say which one it is.
    suffix = _session_suffix(_declared_session_id(repo_root))
    return _scaffold_lib.subject_scoped_record_payload(
        repo_root,
        output_dir=output_dir,
        date_text=date_text,
        title=resolved_title,
        record_slug=slug,
        template=render_template(
            title=resolved_title,
            date_text=date_text,
            artifact_sections=list(adapter["data"].get("artifact_sections", [])),
            repo_root=repo_root,
        ),
        validator_command_for=lambda path: validator_command(repo_root, path),
        remedy="Rerun scaffold_retro_artifact.py with --title <specific retro title>.",
        distinguishers=[suffix, f"{suffix}-2", f"{suffix}-3"],
    )


def main() -> int:
    return _scaffold_lib.emit_payload_main(payload_for, artifact_label="retro")


if __name__ == "__main__":
    raise SystemExit(main())
