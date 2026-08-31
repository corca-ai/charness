from __future__ import annotations

from pathlib import Path

import yaml

from tests.quality_gates.issue_closeout_support import (
    SCRIPT,
    bug_closeout_body,
    load_verify_module,
    seed_commit,
)
from tests.quality_gates.support import run_script


def test_rung1_floors_on_the_carrier() -> None:
    module = load_verify_module()
    silent = bug_closeout_body(behavior_line=None)
    assert module.evaluate_behavioral_verdict(silent, "bug", [42])["missing"] == [42]

    typed_behavior = bug_closeout_body(
        behavior_line=(
            "Behavior #42: local-only-by-contract — surface is local "
            "by the resolution contract"
        ),
    )
    assert module.evaluate_behavioral_verdict(typed_behavior, "bug", [42])["ok"] is True

    undisposed = bug_closeout_body(
        hotl_line="HOTL #42: still checking the connector roundtrip"
    )
    hotl = module.evaluate_hotl_dispositions(undisposed, "bug", [42])
    assert hotl["undispositioned"][0]["target"] == "#42"
    assert module.evaluate_behavioral_verdict(undisposed, "bug", [42])["ok"] is True

    typed_hotl = bug_closeout_body(
        hotl_line="HOTL #42: blocked-needs-operator — awaiting prod approval; queued in the ODQ"
    )
    disposed = module.evaluate_hotl_dispositions(typed_hotl, "bug", [42])
    assert disposed["applies"] is True
    assert disposed["ok"] is True

    inert = module.evaluate_hotl_dispositions(bug_closeout_body(), "bug", [42])
    assert inert["applies"] is False
    assert inert["ok"] is True

    assert module.evaluate_ai_provenance(
        bug_closeout_body(provenance_line=None), "bug"
    )["ok"] is False

    question = "\n\n".join(
        [
            "Close #42.",
            "JTBD: answer a clarification question.",
            "Answer: documented the resolved decision in the issue thread.",
            "AI-provenance: authored by an agent session.",
        ]
    )
    assert module.evaluate_behavioral_verdict(question, "question", [42])["applies"] is False
    assert module.evaluate_ai_provenance(question, "question")["ok"] is True

    question_silent = "\n\n".join(
        [
            "Close #42.",
            "JTBD: answer a clarification question.",
            "Answer: documented the resolved decision in the issue thread.",
        ]
    )
    provenance = module.evaluate_ai_provenance(question_silent, "question")
    assert provenance["applies"] is True
    assert provenance["ok"] is False


def test_evaluate_hotl_dispositions_unit() -> None:
    """Direct unit coverage of the WS-2 floor: presence-gating, typed vocabulary,
    and multi-entry refusal.

    NO classification exemption: this floor used to go inert for
    question/decision-needed on the behavioral-verdict tuple's reason, which does not
    transfer -- whether a human loop was dispositioned is not a fact about behavior
    change. A presented entry is judged whatever the classification claims to be.
    """
    fn = load_verify_module().evaluate_hotl_dispositions
    # a presented entry is judged on EVERY classification, light ones included
    for classification in ("question", "decision-needed", "consolidated", "bug"):
        verdict = fn("HOTL #1: nonsense", classification, [1])
        assert verdict["applies"] is True, classification
        assert verdict["ok"] is False, classification
    # no entry -> inert
    assert fn("Close #1.\nBehavior: verified via X", "bug", [1])["applies"] is False
    # local-only-by-contract disposes; every typed status disposes
    for status in (
        "local-only-by-contract — no live surface", "verified: roundtrip <ts>",
        "blocked-needs-capability: no repo command", "deferred-by-operator: next window",
        "accepted-risk: owner ok", "out-of-scope: not this loop", "issue #77 tracks it",
    ):
        verdict = fn(f"HOTL: {status}", "feature", [1])
        assert verdict["applies"] is True and verdict["ok"] is True, status
    # multi-entry: one typed, one untyped -> refuse only the untyped
    multi = fn("HOTL #1: verified: roundtrip\nHOTL #2: probably fine", "bug", [1, 2])
    assert multi["ok"] is False
    assert [u["target"] for u in multi["undispositioned"]] == ["#2"]
    # placeholder value is undispositioned
    assert fn("HOTL #1: TODO", "bug", [1])["ok"] is False


def test_evaluate_hotl_dispositions_binds_targeted_lines_to_closed_issues() -> None:
    fn = load_verify_module().evaluate_hotl_dispositions
    quoted_other = "- HOTL #77: not verified, see prior discussion"
    assert fn(quoted_other, "question", [800])["applies"] is False
    assert fn(quoted_other, "question", [77])["ok"] is False
    assert fn("HOTL: not verified", "question", [800])["ok"] is False
    assert fn("HOTL: not verified", "question", [800, 801])["applies"] is False
    combined = fn("HOTL #800, #801: not verified", "question", [800, 801])
    assert combined["ok"] is False
    assert combined["undispositioned"][0]["target"] == "#800, #801"


def test_issue_verify_closeout_bundle_binds_hotl_entries_to_its_numbers(tmp_path: Path) -> None:
    """The carrier, not only the parser helper, supplies bundle target identity."""
    seed_commit(
        tmp_path,
        "Closes #800, #801\n"
        "Jtbd: answer both tracker questions\n"
        "Answer: recorded in the linked discussion\n"
        "HOTL #77: not verified, quoted prior discussion\n"
        "HOTL: not verified, ambiguous shorthand\n"
        "AI-provenance: authored by an agent session\n",
    )
    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "800", "--number", "801",
        "--classification", "question", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )
    assert result.returncode == 0, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["hotl_dispositions"]["applies"] is False


def test_evaluate_hotl_dispositions_refuses_a_status_negation() -> None:
    """Seeded escape: an unanchored search over the typed vocabulary accepts a
    status's own NEGATION and incidental English prose, so the floor accepted
    exactly the undispositioned entries it exists to refuse. The recognizer is
    anchored to the value's leading token (the repo's existing disposition
    grammar), so a mention is no longer a disposition."""
    fn = load_verify_module().evaluate_hotl_dispositions
    for undispositioned in (
        "not verified",
        "could not be verified; no readback available",
        "not yet verified, will follow up",
        "this is a known issue with the provider",
        "see issue tracker",
        "unverified so far",
    ):
        verdict = fn(f"HOTL #1: {undispositioned}", "bug", [1])
        assert verdict["applies"] is True, undispositioned
        assert verdict["ok"] is False, undispositioned
    # A leading typed status still disposes, including through markdown emphasis
    # and the bare tracker-ref form of `issue`.
    for dispositioned in (
        "verified — readback captured 2026-07-25",
        "**verified**: roundtrip observed",
        # The contract renders the vocabulary AS code, so an author copying the
        # reference's own rendering writes a backticked status. Anchoring must not
        # refuse the form the docs themselves teach.
        "`verified` — readback captured 2026-07-25",
        "`blocked-needs-capability`: no repo-owned command",
        "blocked-needs-operator — awaiting prod approval",
        "#77 tracks the residual defect",
    ):
        assert fn(f"HOTL #1: {dispositioned}", "bug", [1])["ok"] is True, dispositioned


def test_issue_verify_closeout_requires_per_issue_behavioral_verdict_in_bundle(tmp_path: Path) -> None:
    """No aggregate pass: a bundle where one issue is silent fails for that issue
    even when the other carries a verdict."""
    seed_commit(
        tmp_path,
        bug_closeout_body(
            close_line="Close #1.\nClose #2.",
            critique_line="Critique #1 #2: charness-artifacts/critique/x.md",
            behavior_line="Behavior #1: behavior test exercises the fix (distinct channel)",
        ),
    )

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "1", "--number", "2",
        "--classification", "bug", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["behavioral_verdict"]["missing"] == [2]


def test_validate_closeout_draft_blocks_silent_carrier_before_mutation(tmp_path: Path) -> None:
    """The block-the-silent teeth land at the pre-publish draft boundary: a silent
    bug draft fails validate-closeout-draft before any GitHub mutation."""
    body = tmp_path / "draft.md"
    body.write_text(bug_closeout_body(close_line="Resolves #42.", behavior_line=None), encoding="utf-8")

    result = run_script(
        SCRIPT, "validate-closeout-draft", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "bug", "--carrier", "pr-body", "--body-file", str(body),
    )

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["behavioral_verdict"]["ok"] is False


def test_ledger_floors_refuse_a_bare_na_placeholder(tmp_path: Path) -> None:
    """B1 regression: `N/A` passed every rung-1 ledger floor.

    `_normalize_field_name` maps every non-`[a-z0-9]` run to a space *before* the
    placeholder-set test, so the set's own declared `"n/a"` entry could never be
    produced by it and sat as unreachable dead code. `_has_substantive_value` is
    the single predicate behind every ledger field, behavioral verdict, AI
    provenance, HOTL disposition, and source-preservation floor on all carriers,
    so one unreachable entry made an all-`N/A` closeout indistinguishable from a
    filled one. Pinned against the `TBD` control that always worked."""
    module = load_verify_module()
    na_body = (
        "Close #42.\n"
        "JTBD: N/A\nRoot cause: N/A\nDebug artifact: N/A\nSiblings: N/A\nPrevention: N/A\n"
    )
    na_missing = module._missing_ledger_fields(na_body, "bug")
    tbd_missing = module._missing_ledger_fields(na_body.replace("N/A", "TBD"), "bug")
    assert {"jtbd", "root_cause", "debug_artifact", "siblings", "prevention"} <= set(na_missing)
    # The control the defect was isolated against: `N/A` now behaves as `TBD` did.
    assert set(na_missing) == set(tbd_missing)
    # Falsifiable pair: a real ledger still passes, and a dismissal that carries a
    # REASON is substantive — only the bare placeholder is refused.
    assert module._missing_ledger_fields(bug_closeout_body(), "bug") == []
    assert module._has_substantive_value("n/a - the issue was context only") is True


def test_placeholder_field_does_not_absorb_the_next_ledger_section(tmp_path: Path) -> None:
    """B5 regression: `_body_fields` appended EVERY non-field line to the
    preceding field, and `Behavior #42:` / `HOTL #42:` match no field pattern
    (`_FIELD_RE`'s name class excludes `#` and digits). So a placeholder field
    that happened to be followed by the behavioral-verdict section absorbed that
    heading and normalized to a substantive value — the bare-placeholder refusal
    (B1) held only for a field with nothing after it.

    Measured before the fix: the same all-`N/A` ledger reported 5 missing fields
    with nothing following it and only 3 with a `Behavior` line following it."""
    module = load_verify_module()
    na_ledger = (
        "Close #42.\n"
        "JTBD: N/A\nRoot cause: N/A\nDebug artifact: N/A\nSiblings: N/A\nPrevention: N/A\n"
    )
    alone = module._missing_ledger_fields(na_ledger, "bug")
    followed = module._missing_ledger_fields(
        na_ledger
        + "Behavior #42: verified via focused pytest\nHOTL #42: verified\n"
        + "AI-provenance: agent-drafted.\n",
        "bug",
    )
    # The refusal must not depend on what follows the placeholder.
    assert set(followed) == set(alone)
    assert "prevention" in followed
    # The absorbed section is its own field, not part of `Prevention`.
    fields = module._BODY._body_fields(na_ledger + "Behavior #42: verified via focused pytest\n")
    assert fields["prevention"] == "N/A"
    assert fields["behavior 42"] == "verified via focused pytest"


def test_wrapped_prose_continuation_still_belongs_to_its_field(tmp_path: Path) -> None:
    """Control for the B5 fix: continuation of genuinely wrapped prose is
    INTENDED and must keep working, and the sections that follow it must keep
    satisfying their own floors. Without this the B5 fix could degenerate into
    refusing every multi-line field."""
    module = load_verify_module()
    wrapped = (
        "Close #42.\n"
        "JTBD: keep the closeout ledger honest\n"
        "Root cause: the body parser appended every non-field line\n"
        "  to the preceding field, so a placeholder absorbed the next section.\n"
        "Debug artifact: charness-artifacts/debug/latest.md\n"
        "Siblings: swept the sibling parsers | decision: same bug, fix now | proof: static scan\n"
        "Prevention: focused tests pin both the refusal and this control\n"
        "Behavior #42: verified via focused pytest (distinct channel from CLOSED)\n"
        "HOTL #42: verified\n"
        "AI-provenance: agent-drafted; human-audited per the resolution critique\n"
    )
    assert module._missing_ledger_fields(wrapped, "bug") == []
    assert module._BODY._body_fields(wrapped)["root cause"] == (
        "the body parser appended every non-field line\n"
        "to the preceding field, so a placeholder absorbed the next section."
    )
    assert module.evaluate_behavioral_verdict(wrapped, "bug", [42])["ok"] is True
    assert module.evaluate_hotl_dispositions(wrapped, "bug", [42])["ok"] is True
    assert module.evaluate_ai_provenance(wrapped, "bug")["ok"] is True
    # The standard shipped carrier stays green too.
    assert module._missing_ledger_fields(bug_closeout_body(), "bug") == []


def test_ledger_floors_refuse_every_declared_placeholder() -> None:
    """Falsifiable sweep over the DECLARED set itself, not a hardcoded copy of
    it: every value `_PLACEHOLDER_VALUES` names must actually be reachable
    through the normalizer the comparison uses, so a future entry that the
    normalizer cannot produce (the B1 shape) fails here when it is added."""
    module = load_verify_module()
    body_module = module._BODY
    declared = body_module._PLACEHOLDER_VALUES
    assert "n/a" in declared, "the entry B1 was about must stay declared"
    for placeholder in declared:
        assert module._has_substantive_value(placeholder) is False, placeholder
        # Case is not part of the comparison space either.
        assert module._has_substantive_value(placeholder.upper()) is False, placeholder
    # Positive control so the all-negative sweep cannot pass on a broken predicate.
    assert module._has_substantive_value("a real root cause sentence") is True


def test_bare_na_source_origin_is_not_externally_sourced(tmp_path: Path) -> None:
    """Recorded consequence of the B1 fix, pinned rather than left silent.

    `evaluate_source_preservation` uses `_has_substantive_value` as a
    gate-OPENER, not as a floor: a substantive `Source origin:` is what makes a
    body externally sourced and therefore obliged to carry a preservation form.
    Making bare `N/A` a placeholder therefore flips `Source origin: N/A` from
    refused to exempt. That is the intended reading — a bare `N/A` origin asserts
    there is no external source, exactly as omitting the field does, and the old
    behavior demanded a preservation form for a source that does not exist — but
    it is a floor moving toward PASS inside a fix that otherwise only tightens,
    so it is pinned here. The falsifiable pair below is the case that must keep
    failing: a REAL origin with no preservation form."""
    module = load_verify_module()
    exempt = module.evaluate_source_preservation("Source origin: N/A\n")
    assert exempt["external_sourced"] is False
    assert exempt["ok"] is True
    real = module.evaluate_source_preservation("Source origin: slack thread in #eng\n")
    assert real["external_sourced"] is True
    assert real["missing"] is True
    assert real["ok"] is False


def test_a_placeholder_behavior_value_does_not_bind_its_issue() -> None:
    """`Behavior #N: TODO` is silence wearing a line's clothes.

    The floor refuses SILENCE, and a placeholder value is silence — so the line must
    not bind its issue. Without this the presence check could be satisfied by writing
    the field name and nothing else, which is the shape the placeholder vocabulary
    (`todo`/`tbd`/`n/a`/`missing`) exists to refuse everywhere else in the ledger.
    """
    fn = load_verify_module().evaluate_behavioral_verdict
    for placeholder in ("TODO", "tbd", "n/a", "missing"):
        verdict = fn(f"Behavior #42: {placeholder}", "bug", [42])
        assert verdict["applies"] is True, placeholder
        assert verdict["ok"] is False, placeholder
        assert verdict["missing"] == [42], placeholder
    # A substantive value on the same grammar binds, so the refusal above is the
    # placeholder's doing and not the line shape's.
    assert fn("Behavior #42: confirmed via the readback", "bug", [42])["ok"] is True
