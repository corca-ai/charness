from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

from runtime_bootstrap import import_repo_module
from scripts.setup_agent_docs_lib import _detect_charness_subagent_policy
from scripts.setup_skill_routing_lib import (
    skill_routing_declares_charness_management,
    skill_routing_semantically_complete,
)

from .support import ROOT

_render_skill_routing = import_repo_module(
    ROOT / "skills/public/setup/scripts/render_skill_routing.py",
    "skills.public.setup.scripts.render_skill_routing",
)


def run_render_skill_routing(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["render_skill_routing.py", *args])
    returncode = _render_skill_routing.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def test_setup_render_skill_routing_defaults_to_compact_mode(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    result = run_render_skill_routing(monkeypatch, capsys, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["recommended_action"] == "create_agents_with_skill_routing"
    assert payload["skill_routing_mode"] == "compact"
    assert payload["skill_routing_mode_source"] == "default"
    assert payload["listed_skill_ids"] == []
    # 2026-07-04 revision: session start routes directly instead of always
    # The hook/context path no longer invokes a public semantic router.
    # discovery or a missing/stale/unclear route.
    assert "At session start, a pickup follows docs/handoff.md" in payload["markdown"]
    assert "charness catalog list --repo-root <repo>" in payload["markdown"]
    assert "installed skill metadata and model judgment" in payload["markdown"]
    assert "choose the durable workflow directly" in payload["markdown"]
    assert "if the command returns nonzero" in payload["markdown"]
    assert "SessionStart hook" in payload["markdown"]
    assert "release-note style summary or chat-ready human update" not in payload["markdown"]


def test_setup_render_skill_routing_suggests_add_block_for_mature_agents(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n\nExisting policy.\n", encoding="utf-8")

    result = run_render_skill_routing(monkeypatch, capsys, "--repo-root", str(repo), "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["agents_has_skill_routing"] is False
    assert payload["recommended_action"] == "add_skill_routing_block"


def test_setup_render_skill_routing_reviews_drifted_existing_block(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "# Agents\n\n## Skill Routing\n\nFor task-oriented sessions, use local judgment.\n",
        encoding="utf-8",
    )

    result = run_render_skill_routing(monkeypatch, capsys, "--repo-root", str(repo), "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["agents_has_skill_routing"] is True
    assert payload["skill_routing_matches_compact_block"] is False
    assert payload["recommended_action"] == "review_existing_skill_routing"
    assert any("charness catalog list --repo-root <repo>" in item for item in payload["missing_expected_snippets"])


def test_setup_render_skill_routing_leaves_semantically_complete_block(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "\n".join(
            [
                "# Agents",
                "",
                "## Skill Routing",
                "",
                "A pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment to start the matching workflow directly.",
                "Use the read-only `charness catalog list --repo-root .` inventory when hidden availability is unclear.",
                "If the command returns nonzero, report the command failure rather than concluding skills are unavailable.",
                "External URLs and source links route through `gather` before deciding.",
                "Validation closeout and operator reading tests route through `quality`.",
                "The SessionStart hook may inject this context; it remains context-only.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = _render_skill_routing.build_payload(repo)

    assert payload["skill_routing_matches_compact_block"] is False
    assert payload["skill_routing_semantically_complete"] is True
    assert payload["recommended_action"] == "leave_as_is"
    assert payload["missing_expected_snippets"] == []


def test_setup_render_skill_routing_reviews_block_without_direct_or_failure_actions(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "\n".join(
            [
                "# Agents",
                "",
                "## Skill Routing",
                "",
                "A pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment.",
                "Use the read-only `charness catalog list --repo-root .` inventory when hidden availability is unclear.",
                "External URLs and source links route through `gather` before deciding.",
                "Validation closeout and operator reading tests route through `quality`.",
                "The SessionStart hook may inject this context; it remains context-only.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = _render_skill_routing.build_payload(repo)

    assert payload["skill_routing_semantically_complete"] is False
    assert payload["recommended_action"] == "review_existing_skill_routing"


def _shipped_routing_section_body() -> str:
    """The REAL block `setup` tells an operator to write, split at its own heading.

    Deliberately not a fixture. Every pre-#552 fixture for this predicate — the five
    above and the routing preamble inside
    `test_subagent_delegation_ladder.py::test_the_shipped_setup_template_satisfies_BOTH_readers_of_the_contract`
    — hand-wrote `context-only`, so all of them passed while the surface `setup`
    actually writes failed. A fixture spells the contract the way whichever matcher the
    author had in mind wants; that is how this hid for the life of the check.
    """
    markdown, _ = _render_skill_routing._render_skill_routing()
    heading, _, body = markdown.partition("## Skill Routing")
    assert heading == "", "renderer no longer leads with its own heading"
    return body


def test_the_shipped_renderer_output_satisfies_BOTH_readers_of_the_routing_contract(
    tmp_path: Path,
) -> None:
    """#552: the routing block `setup` writes must be recognized by everything reading it.

    `skill_routing_declares_charness_management` required the literal `context-only`;
    the renderer emits "may inject this context when installed; this block is the
    fallback when it is absent". Five of its six signals matched the renderer's real
    text — only that one word did not — and because the signals are combined with
    `all(...)`, a repo seeded by `charness setup` read as NOT charness-managed.
    """
    body = _shipped_routing_section_body()

    assert skill_routing_declares_charness_management(body) is True, (
        "a repo seeded by `charness setup` would read as not charness-managed"
    )
    assert skill_routing_semantically_complete(body) is True, (
        "the block `setup` writes would read as an incomplete routing contract"
    )

    # THIRD call site of the predicate family, distinct from the two in
    # `setup_agent_docs_lib.py`: the renderer reads its own output back through
    # `agents_skill_routing_semantically_complete` to decide `leave_as_is`. Exercised with
    # renderer-derived text rather than a fixture, for the same reason as the pin above.
    # Written with the heading, because this call site reads the section back out of a
    # whole AGENTS.md via `extract_section` rather than taking a section body.
    markdown, _ = _render_skill_routing._render_skill_routing()
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n\n" + markdown, encoding="utf-8")

    payload = _render_skill_routing.build_payload(repo)

    assert payload["skill_routing_semantically_complete"] is True
    assert payload["recommended_action"] == "leave_as_is"


def test_a_setup_seeded_repo_can_produce_both_gated_agents_policy_findings() -> None:
    """#552, second half: two AGENTS.md policy checks could never fire where they were written for.

    `agents_missing_charness_dynamic_workflow_policy` and
    `agents_missing_subagent_model_policy` are both guarded by `if charness_managed`, so
    a permanently-False recognizer made both unreachable for every setup-seeded repo.
    Their only live subject was this repo's own AGENTS.md, from which their match tokens
    were copied — a tautology the setup path's silent exclusion hid.

    Constructs the seeded surface rather than inferring the refusal from a green suite:
    the routing block alone (no `## Dynamic Workflows`, no `## Subagent Delegation`) must
    produce BOTH findings, and the real shipped delegation template must clear both.
    """
    seeded_agents = "# Agents\n\n" + _render_skill_routing._render_skill_routing()[0]

    policy, findings = _detect_charness_subagent_policy(seeded_agents)

    assert policy["charness_managed"] is True
    assert {finding["type"] for finding in findings} == {
        "agents_missing_charness_dynamic_workflow_policy",
        "agents_missing_subagent_model_policy",
    }, "both gated policy checks must be able to fire for a setup-seeded repo"

    template = (ROOT / "scripts/templates/agents_subagent_delegation.txt").read_text(encoding="utf-8")
    satisfied_policy, satisfied_findings = _detect_charness_subagent_policy(
        seeded_agents + "\n" + template
    )

    assert satisfied_policy["charness_managed"] is True
    assert satisfied_findings == [], (
        "a repo seeded from the shipped template would be flagged for policies it carries"
    )


_ROUTING_PREFIX = (
    "A pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment to start the matching workflow directly.",
    "Use the read-only `charness catalog list --repo-root .` inventory when hidden availability is unclear.",
    "If the command returns nonzero, report the command failure.",
    "External URLs and source links route through `gather` before deciding.",
    "Validation closeout and operator reading tests route through `quality`.",
)
# The word "fallback" spent on an UNRELATED subject, the way this repo's own `gather` prose
# spends it ("a browser-mediated fallback"). Signal 4 already requires `gather` in the
# section, so this is the realistic shape of the false positive, not a contrived one.
_GATHER_LINE_USING_FALLBACK_FOR_ACQUISITION = "External URLs and source links route through `gather`, escalating to the browser-mediated fallback when official paths fail."
_HOOK_NAMED_WITHOUT_ITS_STANDING = "The SessionStart hook injects this context at session open."
_HOOK_STANDING_DECLARED = "The SessionStart hook may inject this context; it remains context-only."


def _routing_block(*lines: str) -> str:
    return "\n".join(["", *lines, ""])


def test_naming_the_session_start_hook_alone_does_not_declare_charness_management() -> None:
    """A block that names the hook while asserting nothing about its standing fails.

    Accepting both `context-only` and `fallback` accepts two spellings of one claim — the
    hook is not the authority and the block stands without it. Naming the hook is not that
    claim.

    Paired with its own positive control below rather than left standing alone: this
    fixture must fail signal 6 specifically, not incidentally because some OTHER signal's
    token drifted. Adding only the standing sentence to the same text must flip it.
    """
    refused = _routing_block(
        *_ROUTING_PREFIX[:3],
        _GATHER_LINE_USING_FALLBACK_FOR_ACQUISITION,
        _ROUTING_PREFIX[4],
        _HOOK_NAMED_WITHOUT_ITS_STANDING,
    )

    assert skill_routing_declares_charness_management(refused) is False

    # Positive control: same text, standing sentence added, nothing else changed.
    accepted = _routing_block(
        *_ROUTING_PREFIX[:3],
        _GATHER_LINE_USING_FALLBACK_FOR_ACQUISITION,
        _ROUTING_PREFIX[4],
        _HOOK_NAMED_WITHOUT_ITS_STANDING,
        "This block is the fallback when the hook is absent.",
    )

    assert skill_routing_declares_charness_management(accepted) is True, (
        "the refusal above did not come from signal 6; another signal is failing"
    )


def test_a_polarity_word_about_session_start_but_no_hook_declares_nothing() -> None:
    """The claim must be about a HOOK, not merely co-located with a session-start phrase.

    Added because a mutation check found the `hook` requirement unproven: dropping it
    killed no test. A block saying "at session start this block is the fallback" says
    nothing about a hook injecting context, which is the claim the signal recognizes.
    """
    body = _routing_block(
        *_ROUTING_PREFIX,
        "At session start, treat this block as the fallback routing contract.",
    )

    assert skill_routing_declares_charness_management(body) is False


def test_the_hooks_standing_is_recognized_in_hand_written_spellings_too() -> None:
    """The signal must recognize the CLAIM, not two blessed spellings of it.

    The detector reads hand-written AGENTS.md as well as generated blocks. Each variant
    declares what the two shipped spellings declare — the hook only injects context and the
    block stands without it — in wording neither writer uses.
    """
    variants = (
        "A session-start routing hook may inject this context; this block is the fallback.",
        "A hook may inject this context at session start; this block remains context-only.",
        "The SessionStart hook is one input; this block is the fallback when it is absent.",
    )

    for variant in variants:
        assert skill_routing_declares_charness_management(
            _routing_block(*_ROUTING_PREFIX, variant)
        ) is True, variant


def test_the_claim_survives_being_spelled_as_two_sentences() -> None:
    """A correct block must not be refused for where its periods land.

    Requiring one sentence to carry the whole claim looked tighter and was not: it made the
    verdict depend on punctuation rather than meaning, so this block — which says exactly
    what the renderer says — was refused. A bounded review caught it. That is the #552 class
    reintroduced by its own repair, which is why the polarity claim now names its subject
    instead of relying on sentence adjacency.
    """
    body = _routing_block(
        *_ROUTING_PREFIX,
        "The SessionStart hook may inject this context when installed.",
        "This block is the fallback when the hook is absent.",
    )

    assert skill_routing_declares_charness_management(body) is True


def test_a_bulleted_block_is_segmented_even_though_bullets_carry_no_periods() -> None:
    """Markdown bullets have no terminal punctuation, and both directions must still hold.

    A sentence-only splitter collapsed a bulleted section into ONE segment, which silently
    restored the whole-section search it was meant to replace: a block declaring the hook
    AUTHORITATIVE passed on the strength of the gather line's unrelated "fallback". Both
    cases below are bulleted; only the meaning differs.
    """
    bullets = (
        "- At session start, a pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment to start the matching workflow directly",
        "- Run the read-only `charness catalog list --repo-root .` inventory; if the command returns nonzero, report the command failure",
        "- Validation closeout and operator reading tests go through `quality`",
    )

    hook_is_authoritative = _routing_block(
        *bullets,
        "- External URLs or source links route through `gather`, escalating to the browser-mediated fallback",
        "- The SessionStart hook is authoritative when installed",
    )
    standing_across_two_bullets = _routing_block(
        *bullets,
        "- External URLs or source links route through `gather` before deciding",
        "- The SessionStart hook may inject this context when installed",
        "- This block is the fallback when the hook is absent",
    )

    assert skill_routing_declares_charness_management(hook_is_authoritative) is False
    assert skill_routing_declares_charness_management(standing_across_two_bullets) is True


def test_every_standing_spelling_the_setup_REFERENCES_offer_is_accepted() -> None:
    """The docs that tell an operator what to write are writers too, and were drifting.

    `render_skill_routing.py` is not the only writer of this block: two `setup` references
    describe it in prose for the hand-written path, on load paths `SKILL.md` routes to
    separately. Both described a block the reader REFUSED — one omitted the standing claim
    entirely, and the other described only part of the signal set. Same reader/writer split
    as #552, one layer out, where no test was looking.

    Bound PER FILE, not across the union. An earlier version asserted each standing spelling
    appeared in *some* reference; since both files carried both spellings, either file could
    have had its standing sentence deleted with this test still green — which is the whole
    failure it exists to prevent, one indirection out.

    `default-surfaces.md` owns the full description, so its own routing bullet is fed to the
    readers directly: the guidance that tells an operator what to write must itself be
    recognizable. `bootstrap-seams.md` defers the block's content to the renderer, so it owes
    only the standing requirement.
    """
    references_dir = ROOT / "skills/public/setup/references"
    standings = (
        "it remains context-only",
        "this block is the fallback when the hook is absent",
    )

    described = " ".join((references_dir / "default-surfaces.md").read_text(encoding="utf-8").split())
    # Two prose anchors, asserted before use. This test pins reference prose ON PURPOSE —
    # that is the whole mechanism — but a reworded anchor should say so rather than raise a
    # bare `ValueError` from `str.index` and send the next reader hunting.
    opening = "a short `Skill Routing` fallback paragraph"
    following = "- when the repo keeps repo-owned skills"
    for anchor in (opening, following):
        assert anchor in described, (
            f"default-surfaces.md no longer contains the anchor {anchor!r} this test slices "
            "its routing bullet with; re-anchor the slice rather than deleting the check"
        )
    routing_bullet = described[described.index(opening) : described.index(following)]
    for standing in standings:
        assert standing in routing_bullet, (
            f"default-surfaces.md no longer offers this standing spelling: {standing!r}"
        )
    # The description is fed to the readers as written. Any signal the guidance stops naming
    # fails here, which is what the first version of this test could not see: it supplied the
    # `gather` and `quality` clauses itself while the reference named neither.
    assert skill_routing_declares_charness_management(routing_bullet) is True, (
        "a repo written as default-surfaces.md describes would read as NOT charness-managed"
    )
    assert skill_routing_semantically_complete(routing_bullet) is True, (
        "a repo written as default-surfaces.md describes would read as an incomplete contract"
    )

    seams = " ".join((references_dir / "bootstrap-seams.md").read_text(encoding="utf-8").split())
    for standing in standings:
        assert standing in seams, (
            f"bootstrap-seams.md no longer offers this standing spelling: {standing!r}"
        )

    # And a block an operator writes from that guidance, in the third person the references
    # use rather than the renderer's imperative, satisfies both readers.
    for standing in standings:
        body = _routing_block(
            "Pickup follows the handoff at docs/handoff.md `## Workflow Trigger`; ordinary routing starts the matching workflow directly from installed skill metadata and model judgment.",
            "Unclear hidden support/integration availability runs the read-only `charness catalog list --repo-root <repo>` inventory; a nonzero result reports a command failure.",
            "An external URL or source link goes through `gather` before deciding from it.",
            "Validation closeout and operator reading tests go through `quality` validation.",
            f"A SessionStart hook may inject the same context, and {standing}.",
        )
        assert skill_routing_declares_charness_management(body) is True, standing
        assert skill_routing_semantically_complete(body) is True, standing


def test_setup_render_skill_routing_accepts_equivalent_action_order(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "\n".join(
            [
                "# Agents",
                "",
                "## Skill Routing",
                "",
                "A pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment.",
                "Directly invoke the appropriate workflow for ordinary requests.",
                "Use the read-only `charness catalog list --repo-root .` inventory when hidden availability is unclear.",
                "Report the command failure whenever it returns a nonzero status.",
                "External URLs and source links route through `gather` before deciding.",
                "Validation closeout and operator reading tests route through `quality`.",
                "The SessionStart hook may inject this context; it remains context-only.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = _render_skill_routing.build_payload(repo)

    assert payload["skill_routing_semantically_complete"] is True
    assert payload["recommended_action"] == "leave_as_is"
