#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
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
# The same budget module `validate_handoff_artifact.py` loads, so
# `size_budget.max_words` cannot disagree with the ceiling the gate enforces.
_budget = SKILL_RUNTIME.load_local_skill_module(__file__, "handoff_content_budget")

# Mirrors REQUIRED_SECTIONS in scripts/validate_handoff_artifact.py. The handoff
# validator enforces an EXACT H2 set, a `# ... Handoff` title, a content-word
# ceiling (blank lines, the required headings, and `## References` are not
# counted), non-empty sections, and a markdown link under `## References` that
# carries a descriptor on the link's OWN line, so the scaffold emits a skeleton
# that passes that validator out of the box.
SECTIONS = (
    "## Workflow Trigger",
    "## Current State",
    "## Next Session",
    "## Discuss",
    "## References",
)
VALIDATOR_SCRIPT_NAMES = ("validate_handoff_artifact.py", "validate-handoff-artifact.py")

# The budget an author needs BEFORE writing, mirroring the quality scaffold's
# `size_budget`. The template already models the link shape; it cannot model the
# three rules an author only meets by failing the gate, which is what a session
# that hand-authored this artifact actually hit, four refusals in a row:
#
#   1. formatting is free, so trimming it buys nothing and STATE must go instead;
#   2. an owner counts only ON the entry -- a command in a fenced block below it
#      owns nothing, and that bullet belongs in the artifact it should link;
#   3. an entry that carries one owner while PARAPHRASING a second artifact
#      beside it passes the gate and still fills the budget.
#
# All three are in the skill body. Nothing bound them to the moment of authoring,
# which is the `rule-exists-but-does-not-bind` class this repo already records.
SIZE_GUIDANCE = (
    "Write the whole artifact within max_words. Blank lines, the required `##` headings, and "
    "the whole `## References` block are free, and the budget charges WORDS, so rewrapping or "
    "shortening links buys nothing — cut STATE instead, spilling detail to the artifact that "
    "owns it. `## Current "
    "State` and `## Next Session` read as a flat list of links: each entry is a link, an issue "
    "id, or an inline command WITH ARGUMENTS, on the entry itself. A command in a fenced block "
    "below a bullet owns nothing and is refused. The budget fills fastest when an entry names "
    "one owner and then restates what a second artifact already holds; link it instead."
)


def default_title(title: str | None) -> str:
    return title if title else "Session Handoff"


def _heading_title(title: str) -> str:
    # The validator requires "handoff" in the title line; guard a custom --title
    # so a subject like "Auth Migration" still yields a passing `# ... Handoff`.
    return title if "handoff" in title.lower() else f"{title} Handoff"


# One body per section, as DATA. The if-chain this replaces said the same four
# lines five times, which read as five decisions and was one.
#
# The three link-carrying sections MODEL the shape rather than describing it:
# link first, em dash, one line. An author fills in a template; if the template
# is a paragraph, the artifact becomes paragraphs, and the gate then refuses work
# that already looks finished. The stub also has to VALIDATE — the failure hint
# points authors at this scaffold, and a scaffold whose output fails the gate
# teaches that the gate is noise.
#
# `## References` carried a BARE link until this rule landed. It was the one
# section modelling a link with no descriptor, and it is the section consumers pool
# links into — `## References` lines are free against the content ceiling, so the
# budget pushes links here and the placeholder then taught them to arrive
# context-free. Two consumer repos measured `docs/handoff.md` as a leading
# contributor to their `link_only_lines` count, and could not fix it locally
# because the next handoff run rewrites the stub. The descriptor is modelled here
# AND required by the validator, because a placeholder alone does not bind: an
# author who deletes the TODO line is back to the shape this fixes.
#
# The line after the em dash says what the linked document HOLDS, never what to
# do about it. That is the wiki convention this artifact follows, and it is also
# the slower-rotting half: a description of contents goes stale when that
# document changes, and its owner fixes it; a description of the next action
# goes stale when the WORLD changes, which is every session. The measured
# handoff errors in this repo were action and status claims, not
# which-document-matters claims. The reading agent decides the action.
#
# Targets are `./handoff.md`: relative to the artifact's own directory, which is
# where a relative link resolves from. A bare `docs/handoff.md` here resolved to
# `docs/docs/handoff.md` and survived only because nothing runs a link gate over
# a freshly scaffolded stub.
SECTION_BODIES = {
    "## Workflow Trigger": "- TODO name the pickup workflow the next session invokes"
    " (e.g. `charness:handoff`) and the one-line condition that triggers it.",
    "## Current State": "- [TODO the artifact](./handoff.md)"
    " — TODO what this document holds, in one line.",
    "## Next Session": "- [TODO the artifact](./handoff.md)"
    " — TODO what this document holds, in one line.",
    "## Discuss": "- TODO open decisions for the next operator, or `none` when there are none.",
    "## References": "- [TODO pickup doc](./handoff.md)"
    " — TODO what this document holds, in one line.",
}


def render_template(*, title: str, date_text: str) -> str:
    lines = [f"# {_heading_title(title)}", f"Date: {date_text}", ""]
    for heading in SECTIONS:
        lines.extend([heading, "", SECTION_BODIES.get(heading, "- TODO"), ""])
    return "\n".join(lines).rstrip() + "\n"


def validator_command(repo_root: Path) -> str:
    return _scaffold_lib.validator_command(repo_root=repo_root, script_file=__file__, script_names=VALIDATOR_SCRIPT_NAMES)


def max_content_words(adapter: dict | None = None) -> int:
    """The validator's own ceiling, read rather than transcribed.

    A second copy of the number here would go stale silently the next time an
    operator re-bases the budget -- the class this repo's `regenerable-facts`
    gate exists for. It went stale in the UNIT too: this function was
    `max_content_lines` until 2026-08-19.

    An adapter that declares `max_content_words` overrides it, resolved with the same
    rule the gate applies: a forecast that disagreed with the gate would send the
    author to write-to-fit against a number that then refuses them. `adapter` stays
    optional so the no-adapter callers keep the default.
    """
    default = int(_budget.DEFAULT_MAX_CONTENT_WORDS)
    declared = (adapter or {}).get("data", {}).get(_resolve_adapter.WORD_BUDGET_FIELD)
    if isinstance(declared, bool) or not isinstance(declared, int) or declared < 1:
        return default
    return declared


def invocation_subject_key(artifact_path: str) -> str:
    """`handoff`'s subject key: the rolling artifact itself.

    Not the title, and not a slug. There is exactly ONE handoff per repo and every invocation
    is for that same one — rewriting it in place IS the contract — so the key that makes this
    family honest is the one that always agrees with its target. A title-derived key here
    would refuse the repo's own handoff, whose H1 (`Charness Handoff`) has never matched the
    default title; the subject-identity rule must not manufacture a mismatch where the family
    has a single subject by construction.
    """
    return f"rolling:{artifact_path}"


def payload_for(repo_root: Path, *, title: str | None, subject: str | None = None) -> dict[str, object]:
    # GUARDED AT THE READ SITE. Every scaffold in this family reads its write TARGET out
    # of the adapter, so an unhonored declaration does not degrade the answer -- it
    # relocates the artifact. Measured on the real CLI at `0bcb6b227`: a repo declaring
    # `output_dir: docs/mine` under `version: 9` got back
    # `artifact_path: docs/handoff.md`, exit 0, and the scaffold would have written there.
    #
    # `output_dir`, not `artifact_path`: this adapter derives the path from a directory
    # plus a fixed `handoff.md`. The first cut of this probe declared `artifact_path`,
    # which this resolver ignores -- so the speakable-version CONTROL returned the default
    # too and could not tell "honored" from "fell back". Re-measured on the field the
    # contract actually reads, and the control now returns `docs/mine/handoff.md`.
    #
    # `payload_for` rather than `main()`: the target is resolved HERE, so the refusal is a
    # property of this function rather than of whatever calls it. A round-1 bounded review
    # over rows 6-13 REFUTED the sentence this comment used to carry ("this module's
    # `payload_for` is imported elsewhere; a refusal at the entrypoint would cover one
    # caller") -- verified false for quality, critique and handoff, whose only importers
    # are tests. It is true only for retro (`plan_retro_run`) and debug (`plan_debug_run`).
    # This slice had ALREADY struck the same unmeasured harm claim once, for rows 1-5.
    refusal = _adapter_version_verdict.unspeakable_version_message(
        load_adapter, repo_root, adapter_name="handoff-adapter.yaml"
    )
    if refusal is not None:
        raise SystemExit(refusal)
    adapter = load_adapter(repo_root)
    artifact_path = str(adapter["artifact_path"])
    date_text = dt.date.today().isoformat()
    resolved_title = default_title(title)
    subject_key = invocation_subject_key(artifact_path)
    payload = _scaffold_lib.with_write_target_facts(repo_root, {
        "artifact_path": artifact_path,
        "artifact_role": "rolling",
        "write_artifact_path": artifact_path,
        "date": date_text,
        "title": resolved_title,
        "template": render_template(title=resolved_title, date_text=date_text),
        "validator_command": validator_command(repo_root),
        "size_budget": {"max_words": max_content_words(adapter), "guidance": SIZE_GUIDANCE},
    })
    return _scaffold_lib.with_subject_identity_facts(
        payload,
        invocation_subject_key=subject_key,
        # Both keys are the rolling artifact, so this family reports `match` by construction
        # and cannot construct a mismatch — stated here rather than left to be inferred from a
        # tautology. A `--subject` passed to `handoff` is deliberately not part of the key:
        # there is one handoff per repo, and rewriting it in place IS the contract.
        target_subject_key=subject_key,
    )


def main() -> int:
    return _scaffold_lib.emit_payload_main(payload_for, artifact_label="handoff")


if __name__ == "__main__":
    raise SystemExit(main())
