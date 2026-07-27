from __future__ import annotations

import json
from pathlib import Path

from tests.quality_gates.issue_closeout_support import (
    SCRIPT,
    bug_closeout_body,
    load_verify_module,
    seed_commit,
)
from tests.quality_gates.support import run_script


def test_issue_verify_closeout_rejects_silent_behavioral_verdict(tmp_path: Path) -> None:
    """Seeded escape: a bug carrier silent on the per-issue behavioral verdict
    must FAIL before the CLOSED-state green can stand alone."""
    seed_commit(tmp_path, bug_closeout_body(close_line="Close #42.", behavior_line=None))

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "bug", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["behavioral_verdict"]["ok"] is False
    assert payload["behavioral_verdict"]["missing"] == [42]


def test_issue_verify_closeout_accepts_typed_nonverified_disposition(tmp_path: Path) -> None:
    """Render-not-declare: a typed non-`verified` disposition satisfies the floor
    exactly as a confirmation does — the obligation is to render, not to confirm."""
    seed_commit(
        tmp_path,
        bug_closeout_body(
            close_line="Close #42.",
            behavior_line="Behavior #42: local-only-by-contract — surface is local by the resolution contract",
        ),
    )

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "bug", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["behavioral_verdict"]["ok"] is True
    assert payload["status"] == "carrier_verified"


def test_issue_verify_closeout_rejects_undispositioned_hotl_entry(tmp_path: Path) -> None:
    """WS-2 seeded escape (Direction-3): a bug carrier that PRESENTS a HOTL entry
    without a typed disposition must FAIL before the CLOSED-state green stands."""
    seed_commit(
        tmp_path,
        bug_closeout_body(
            close_line="Close #42.",
            hotl_line="HOTL #42: still checking the connector roundtrip",
        ),
    )

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "bug", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["hotl_dispositions"]["ok"] is False
    assert payload["hotl_dispositions"]["undispositioned"][0]["target"] == "#42"
    # the OTHER floors pass — the close fails ONLY on the undispositioned HOTL entry
    assert payload["behavioral_verdict"]["ok"] is True


def test_issue_verify_closeout_accepts_typed_hotl_disposition(tmp_path: Path) -> None:
    """A typed HOTL status (here `blocked-needs-operator`) disposes the entry —
    render-not-declare: the floor passes; honesty is the resolution critique."""
    seed_commit(
        tmp_path,
        bug_closeout_body(
            close_line="Close #42.",
            hotl_line="HOTL #42: blocked-needs-operator — awaiting prod approval; queued in the ODQ",
        ),
    )

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "bug", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["hotl_dispositions"]["applies"] is True
    assert payload["hotl_dispositions"]["ok"] is True


def test_issue_verify_closeout_inert_without_hotl_entry(tmp_path: Path) -> None:
    """Presence-gated: a carrier with NO HOTL entry is inert (no live loop to
    dispose) — the floor does not over-fire on internal/no-live closes."""
    seed_commit(tmp_path, bug_closeout_body(close_line="Close #42."))

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "bug", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["hotl_dispositions"]["applies"] is False
    assert payload["hotl_dispositions"]["ok"] is True


def test_evaluate_hotl_dispositions_unit() -> None:
    """Direct unit coverage of the WS-2 floor: presence-gating, typed vocabulary,
    classification exemption, and multi-entry refusal."""
    fn = load_verify_module().evaluate_hotl_dispositions
    # question/decision-needed have no live behavior -> inert
    assert fn("HOTL #1: nonsense", "question")["applies"] is False
    # no entry -> inert
    assert fn("Close #1.\nBehavior: verified via X", "bug")["applies"] is False
    # local-only-by-contract disposes; every typed status disposes
    for status in (
        "local-only-by-contract — no live surface", "verified: roundtrip <ts>",
        "blocked-needs-capability: no repo command", "deferred-by-operator: next window",
        "accepted-risk: owner ok", "out-of-scope: not this loop", "issue #77 tracks it",
    ):
        verdict = fn(f"HOTL: {status}", "feature")
        assert verdict["applies"] is True and verdict["ok"] is True, status
    # multi-entry: one typed, one untyped -> refuse only the untyped
    multi = fn("HOTL #1: verified: roundtrip\nHOTL #2: probably fine", "bug")
    assert multi["ok"] is False
    assert [u["target"] for u in multi["undispositioned"]] == ["#2"]
    # placeholder value is undispositioned
    assert fn("HOTL #1: TODO", "bug")["ok"] is False


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
        verdict = fn(f"HOTL #1: {undispositioned}", "bug")
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
        assert fn(f"HOTL #1: {dispositioned}", "bug")["ok"] is True, dispositioned


def test_issue_verify_closeout_rejects_missing_ai_provenance_marker(tmp_path: Path) -> None:
    """Seeded escape: an agent-authored bug carrier without an AI-provenance marker
    is not legible to the distinct observer and must FAIL its presence check."""
    seed_commit(tmp_path, bug_closeout_body(close_line="Close #42.", provenance_line=None))

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "bug", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["ai_provenance"]["ok"] is False


def test_issue_verify_closeout_question_class_exempt_from_rung1_floors(tmp_path: Path) -> None:
    """A `question` carrier has no behavior to confirm: both rung-1 floors are
    inert (mirroring the resolution-critique classification gate)."""
    seed_commit(
        tmp_path,
        "\n\n".join(
            [
                "Close #42.",
                "JTBD: answer a clarification question.",
                "Answer: documented the resolved decision in the issue thread.",
            ]
        ),
    )

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "question", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["behavioral_verdict"]["applies"] is False
    assert payload["ai_provenance"]["applies"] is False


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
    payload = json.loads(result.stdout)
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
    payload = json.loads(result.stdout)
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
