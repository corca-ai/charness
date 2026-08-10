"""Whether `inspect_repo` recognizes a charness-seeded repo AS charness-managed.

Split out of `test_setup_inspect_policy.py`, which was four lines from its length limit.
These cases share one subject: `charness_managed` gates two AGENTS.md policy findings, so
a recognizer that cannot say yes to the block `setup` itself writes turns those findings
into permanent greens. Every case here is built from the renderer's REAL output; the
fixtures that spelled the contract by hand are what let the drift hide.
"""

from __future__ import annotations

from pathlib import Path

from runtime_bootstrap import import_repo_module

from .support import ROOT, inspect_setup_repo
from .support import seed_normalize_repo as _seed_normalize_repo

_render_skill_routing = import_repo_module(
    ROOT / "skills/public/setup/scripts/render_skill_routing.py",
    "skills.public.setup.scripts.render_skill_routing",
)


def _run_inspect(repo: Path) -> dict[str, object]:
    return inspect_setup_repo(repo)


def _routing_block_naming_the_hook_without_declaring_its_standing() -> str:
    """A routing block that names the hook but never says the block stands without it.

    The gather line deliberately uses "fallback" the way this repo's own `gather` prose
    uses it — about a browser-mediated acquisition path, not about the hook. Before the
    polarity token was required in the SAME SENTENCE as the hook, this block was
    recognized as charness-managed on the strength of that unrelated word.
    """
    return "\n".join(
        [
            "# Agents",
            "",
            "## Skill Routing",
            "",
            "At session start, a pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment to start the matching workflow directly.",
            "Use the read-only `charness catalog list --repo-root .` inventory when hidden availability is unclear.",
            "If the command returns nonzero, report the command failure.",
            "External URLs and source links route through `gather`, escalating to the browser-mediated fallback when official paths fail.",
            "Validation closeout and operator reading tests route through `quality`.",
            "The SessionStart hook injects this context at session open.",
            "",
        ]
    )


def test_setup_inspect_refuses_a_routing_block_that_never_declares_the_hooks_standing(
    tmp_path: Path,
) -> None:
    """The refusal proven through the COMPOSED verdict, not only the module that computes it.

    This repo names asserting a floor's refusal only through its computing module as its
    house failure mode. `charness_managed` is computed in
    `setup_skill_routing_lib.py` but ACTED ON by `inspect_setup_repo`, so the refusal is
    pinned here where an operator would see it.
    """
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, _routing_block_naming_the_hook_without_declaring_its_standing())

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    assert normalization["charness_subagent_policy"]["charness_managed"] is False
    finding_types = {finding["type"] for finding in normalization["findings"]}
    assert "agents_missing_charness_dynamic_workflow_policy" not in finding_types
    assert "agents_missing_subagent_model_policy" not in finding_types


def test_setup_inspect_accepts_the_shipped_routing_block_an_operator_extended(tmp_path: Path) -> None:
    """#552 at the SECOND caller of the repaired predicate, mutated independently.

    `_detect_charness_subagent_policy` is one caller; this is the other. Here the same
    permanently-False recognizer meant that a repo carrying the block `setup` wrote —
    once an operator inserted a single repo-specific line into it, so the block is no
    longer a byte-identical substring and `matches_compact_block` stops rescuing it — was
    reported as `skill_routing_block_custom_or_drifted` and told to review the block
    charness itself had just written.

    Built from the renderer's REAL output rather than a fixture. The pre-existing sibling
    case, `test_setup_inspect_accepts_expanded_semantically_complete_skill_routing` in
    `test_setup_inspect_policy.py`, covers this path with hand-written prose spelling
    `context-only` — exactly the tautology that kept this caller's defect invisible.
    """
    markdown, _ = _render_skill_routing._render_skill_routing()
    hook_sentence = "The SessionStart hook"
    assert hook_sentence in markdown, "renderer no longer names the hook; rewrite this edit"
    extended = markdown.replace(
        hook_sentence,
        "This repo also keeps generated exports in sync before validators.\n\n" + hook_sentence,
    )
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\n" + extended)

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    skill_routing = normalization["skill_routing"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    assert skill_routing["matches_compact_block"] is False, "test no longer exercises the semantic path"
    assert skill_routing["semantically_complete"] is True
    assert skill_routing["recommended_action"] == "leave_as_is"
    assert skill_routing["decision_needed"] is None
    assert "skill_routing_block_custom_or_drifted" not in finding_types

