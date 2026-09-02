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
    __file__, "scripts.adapters.adapter_version_verdict"
)
_scaffold_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.core.scaffold_artifact_lib")
_persistence_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.retro_debug.retro_persistence_lib")
resolve_retro_artifact_path = _persistence_lib.resolve_retro_artifact_path

VALIDATOR_SCRIPT_NAMES = ("validate_retro_artifact.py", "validate-retro-artifact.py")

# The scaffold emits the generic structural fields in a validating state. The
# optional lesson ledger is selection memory, so scaffolding a retro does not
# create or require a session receipt or lesson disposition.


def default_title(title: str | None) -> str:
    return title if title else "Session Retro"


def _slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "retro"


def _sections_without_owned_headings(artifact_sections: list[str], owned: frozenset[str]) -> list[str]:
    """Drop every adapter-declared block whose H2 the scaffold already emits.

    ``artifact_sections`` used to be appended verbatim, so an adapter declaring a
    heading the scaffold also owns produced that section TWICE. Scaffold-owned
    headings win because they are the sections the generic floors read; an adapter
    that wants a different section names a different heading.

    Dropping is per BLOCK, not per line, so the colliding section's body goes with
    its heading rather than stranding orphan prose under the scaffold's own heading.
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


def _record_paths(
    output_dir: str, *, date_text: str, record_slug: str, distinguishers: tuple[str, ...] = ("2", "3", "4")
) -> tuple[Path, list[Path]]:
    artifact_date = dt.date.fromisoformat(date_text)
    base = resolve_retro_artifact_path(
        Path(output_dir), record_slug, artifact_date=artifact_date, subject_key=True
    )[0]
    alternatives = [
        resolve_retro_artifact_path(
            Path(output_dir), f"{record_slug}-{tail}", artifact_date=artifact_date, subject_key=True
        )[0]
        for tail in distinguishers
    ]
    return base, [base, *alternatives]


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
    write_path, candidates = _record_paths(output_dir, date_text=date_text, record_slug=slug)
    resolved_path = next((path for path in candidates if not (repo_root / path).exists()), None)
    if resolved_path is None:
        raise SystemExit(
            f"every dated record path this scaffold derives for `{slug}` today already exists "
            f"({', '.join(str(path) for path in candidates)}), and a scaffold writes a fresh "
            "template over whatever is there. Rerun scaffold_retro_artifact.py with "
            "--title <specific retro title>."
        )
    refusal = (
        {}
        if resolved_path == write_path
        else _scaffold_lib.subject_refusal_facts(
            refused_path=str(write_path),
            refused_subject_key=_scaffold_lib.record_subject_slug(str(write_path)),
            reason="record-occupied",
        )
    )
    return _scaffold_lib.dated_record_payload(
        repo_root,
        write_artifact_path=str(resolved_path),
        date_text=date_text,
        title=resolved_title,
        template=render_template(
            title=resolved_title,
            date_text=date_text,
            artifact_sections=list(adapter["data"].get("artifact_sections", [])),
            repo_root=repo_root,
        ),
        validator_command=validator_command(repo_root, str(resolved_path)),
        extra={
            **refusal,
            **_scaffold_lib.final_subject_facts(
                invocation_subject_key=slug,
                target_subject_key=_scaffold_lib.record_subject_slug(str(resolved_path)),
                chosen=resolved_path != write_path,
            ),
        },
    )


def main() -> int:
    return _scaffold_lib.emit_payload_main(payload_for, artifact_label="retro")


if __name__ == "__main__":
    raise SystemExit(main())
