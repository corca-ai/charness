"""The claims-review scope split, and the laundering guard on it.

Four claims rounds on one release all returned `unproven` and produced ~14
blockers, NONE in shipped code. Every blocker was prose about the review, in
artifacts that ship inside the bundle being reviewed -- so repairing one changed
the bundle and generated the next round's findings. The predecessor release hit
the same wall three rounds deep and stopped, recording "publishing on a fourth
round would be reviewing until it passes".

The split lets the loop converge. The risk it introduces is obvious and is
tested at least as hard: a scope split is a way to launder findings out of a
release unless a `pass` is required to carry what it waived.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from types import SimpleNamespace

import pytest

from .support import ROOT

_RELEASE = ROOT / "skills" / "public" / "release" / "scripts"
sys.path.insert(0, str(_RELEASE))

from claims_review_scope import (  # noqa: E402
    assert_scope_is_declared,
    classify,
    partition,
    render_packet_scope,
    scope_summary,
)


def _claims_module():
    spec = importlib.util.spec_from_file_location(
        "pcr", _RELEASE / "publish_release_claims_review.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    [
        "scripts/mutate_and_restore.py",
        "skills/public/release/SKILL.md",
        "plugins/charness/scripts/x.py",
        "tests/quality_gates/test_x.py",
        "packaging/charness.json",
        ".claude-plugin/marketplace.json",
        "charness",
        "docs/handoff.md",
    ],
)
def test_shipped_surfaces_block(path: str) -> None:
    """A tag is a claim about what ships. These are it."""
    assert classify(path) == "blocking"


@pytest.mark.parametrize(
    "path",
    [
        "charness-artifacts/goals/2026-08-22-x.md",
        "charness-artifacts/retro/2026-08-22-x.md",
        "charness-artifacts/critique/2026-08-22-x.md",
        "charness-artifacts/probe/2026-08-22-x.md",
    ],
)
def test_session_narrative_is_advisory(path: str) -> None:
    """An account of how the work went, written by the run under review and
    rewritten by every repair the review provokes. Real defects, not tag gates.

    Only `.md`. A `.json` under the same roots is machine-read state -- probe
    records are consumed by `tests/probe_drift_support.py` -- and blocks."""
    assert classify(path) == "advisory"
    assert classify(path.replace(".md", ".json")) == "blocking"


def test_the_release_record_blocks_but_the_review_narrative_does_not() -> None:
    """THE ordering case. `charness-artifacts/release/` and
    `charness-artifacts/release-review/` share a prefix, and getting this
    backwards either makes the record unreviewable or lets the review's own
    narrative gate the publish it is reviewing -- which is exactly what round 4
    found had happened."""
    assert classify("charness-artifacts/release/latest.md") == "blocking"
    assert classify("charness-artifacts/release-review/2026-08-22-x.md") == "advisory"


def test_an_unrecognised_surface_is_blocking() -> None:
    """Fail closed. A new top-level directory must not become advisory by being
    unlisted; that is how a scope split turns into a laundering channel."""
    assert classify("brand-new-surface/thing.py") == "blocking"
    assert classify("Makefile") == "blocking"


def test_partition_dedupes_and_sorts() -> None:
    split = partition([
        "scripts/b.py", "scripts/a.py", "scripts/a.py",
        "charness-artifacts/retro/z.md",
    ])

    assert split == {
        "blocking": ["scripts/a.py", "scripts/b.py"],
        "advisory": ["charness-artifacts/retro/z.md"],
    }


def test_scope_summary_counts_match_the_lists() -> None:
    summary = scope_summary(["scripts/a.py", "charness-artifacts/goals/g.md"])

    assert summary["blocking_count"] == len(summary["blocking_paths"]) == 1
    assert summary["advisory_count"] == len(summary["advisory_paths"]) == 1


def test_the_packet_names_both_scopes_and_says_advisory_is_not_unimportant() -> None:
    packet = render_packet_scope(["scripts/a.py", "charness-artifacts/retro/r.md"])

    assert "`scripts/a.py`" in packet
    assert "`charness-artifacts/retro/r.md`" in packet
    assert "does NOT make the verdict `unproven`" in packet
    assert "not-a-tag-gate" in packet


# --------------------------------------------------------------------------
# The laundering guard
# --------------------------------------------------------------------------


def _pass_record(**overrides):
    record = {
        "verdict": "pass",
        "review_scope": {"blocking_paths": ["scripts/a.py"], "advisory_paths": []},
        "advisory_findings": [],
    }
    record.update(overrides)
    return record


def test_a_pass_without_a_declared_scope_is_refused() -> None:
    """A verdict with no declared scope cannot be audited later for what it did
    not look at."""
    with pytest.raises(SystemExit, match="review_scope"):
        assert_scope_is_declared({"verdict": "pass"}, verdict="pass")


def test_a_pass_over_an_empty_blocking_scope_is_refused() -> None:
    """A `pass` over no blocking surface is a verdict about nothing -- the
    render-identically-either-way shape, at the release boundary."""
    record = _pass_record(review_scope={"blocking_paths": [], "advisory_paths": ["x"]})

    with pytest.raises(SystemExit, match="verdict about nothing"):
        assert_scope_is_declared(record, verdict="pass")


def test_a_pass_must_carry_advisory_findings_even_when_empty() -> None:
    """An absent field and an empty list read identically to a later auditor, so
    `nothing found` must be distinguishable from `nobody looked`."""
    record = _pass_record()
    del record["advisory_findings"]

    with pytest.raises(SystemExit, match="advisory_findings"):
        assert_scope_is_declared(record, verdict="pass")


def test_a_well_formed_pass_is_accepted() -> None:
    assert_scope_is_declared(_pass_record(), verdict="pass")


def test_an_unproven_verdict_is_exempt_from_scope_bookkeeping() -> None:
    """It is already blocking. Demanding bookkeeping from a refusal would make
    refusing costlier than passing -- the wrong gradient on a proof surface."""
    assert_scope_is_declared({"verdict": "unproven"}, verdict="unproven")


def test_advisory_findings_survive_into_the_validator_result() -> None:
    """The point of requiring them is that they REACH the record an operator
    reads. A field validated and then dropped would be theatre.

    This RUNS `validate_claims_review` against a stubbed git rather than
    grepping the source: a reviewer caught two source-text assertions in this
    session already, and an assertion on a string literal passes whether or not
    the value is ever returned.
    """
    module = _claims_module()
    prepared = {"commit": "P" * 40, "path": "charness-artifacts/release/latest.md", "sha256": "s" * 64}
    narrative = "charness-artifacts/release-review/2026-08-22-v9.9.9-prepared-claims-review.md"
    review_json = "charness-artifacts/release-review/2026-08-22-v9.9.9-prepared-claims-review.json"
    record = {
        "schema_version": module.SCHEMA_VERSION,
        "prepared_commit": prepared["commit"],
        "release_record_path": prepared["path"],
        "release_record_sha256": prepared["sha256"],
        "target_version": "9.9.9",
        "tag_name": "v9.9.9",
        "verdict": "pass",
        "preparer_context": "parent",
        "reviewer_context": "bounded-reviewer",
        "review_artifact": narrative,
        "observer_distinctness": {
            "kind": "separate-agent-context",
            "signal": "bounded-reviewer spawn, read-only envelope",
            "review_artifact": narrative,
        },
        "review_scope": {"blocking_paths": ["scripts/a.py"], "advisory_paths": ["charness-artifacts/retro/r.md"]},
        "advisory_findings": [{"file": "charness-artifacts/retro/r.md", "summary": "count drifted"}],
    }

    def fake_run(args, cwd=None, check=True):
        joined = " ".join(args)
        if "--format=%P" in joined:
            return SimpleNamespace(returncode=0, stdout=prepared["commit"])
        if "diff-tree" in joined and "--name-status" in joined:
            return SimpleNamespace(returncode=0, stdout=f"A\t{narrative}\n")
        if "diff-tree" in joined:
            return SimpleNamespace(returncode=0, stdout=f"{review_json}\n{narrative}\n")
        if joined.endswith(review_json):
            return SimpleNamespace(returncode=0, stdout=json.dumps(record))
        if joined.endswith(narrative):
            return SimpleNamespace(returncode=0, stdout=f"{prepared['commit'][:12]} 9.9.9 " + "x" * 900)
        return SimpleNamespace(returncode=0, stdout="")

    result = module.validate_claims_review(
        ROOT, prepared=prepared, evidence_commit="R" * 40,
        artifact_path=review_json, target_version="9.9.9", tag_name="v9.9.9", run=fake_run,
    )

    assert result["verdict"] == "pass"
    assert result["review_scope"]["blocking_paths"] == ["scripts/a.py"]
    assert result["advisory_findings"] == [
        {"file": "charness-artifacts/retro/r.md", "summary": "count drifted"}
    ]


# --------------------------------------------------------------------------
# Round 1: the guard's WIRING, and the laundering shape it missed
# --------------------------------------------------------------------------


def _fake_git(prepared, review_json, narrative, record, *, delta=None, base="v9.9.8"):
    """A git stub covering every call `validate_claims_review` makes."""
    def run(args, cwd=None, check=True):
        joined = " ".join(args)
        if "describe" in joined:
            return SimpleNamespace(returncode=0, stdout=base + "\n")
        if "diff-tree" in joined and "--name-status" in joined:
            return SimpleNamespace(returncode=0, stdout=f"A\t{narrative}\n")
        if "diff-tree" in joined and base and base in joined:
            return SimpleNamespace(returncode=0, stdout="\n".join(delta or []) + "\n")
        if "--format=%P" in joined:
            return SimpleNamespace(returncode=0, stdout=prepared["commit"])
        if "diff-tree" in joined:
            return SimpleNamespace(returncode=0, stdout=f"{review_json}\n{narrative}\n")
        if joined.endswith(review_json):
            return SimpleNamespace(returncode=0, stdout=json.dumps(record))
        if joined.endswith(narrative):
            return SimpleNamespace(
                returncode=0, stdout=f"{prepared['commit'][:12]} 9.9.9 " + "x" * 900
            )
        return SimpleNamespace(returncode=0, stdout="")
    return run


def _scoped_record(prepared, narrative, *, blocking, advisory, findings=None):
    return {
        "schema_version": "charness.release.claims-review.v3",
        "prepared_commit": prepared["commit"],
        "release_record_path": prepared["path"],
        "release_record_sha256": prepared["sha256"],
        "target_version": "9.9.9",
        "tag_name": "v9.9.9",
        "verdict": "pass",
        "preparer_context": "parent",
        "reviewer_context": "bounded-reviewer",
        "review_artifact": narrative,
        "observer_distinctness": {
            "kind": "separate-agent-context",
            "signal": "bounded-reviewer spawn, read-only envelope",
            "review_artifact": narrative,
        },
        "review_scope": {"blocking_paths": blocking, "advisory_paths": advisory},
        "advisory_findings": findings if findings is not None else [],
    }


def _invoke(record, delta):
    module = _claims_module()
    prepared = {"commit": "P" * 40, "path": "charness-artifacts/release/latest.md", "sha256": "s" * 64}
    narrative = "charness-artifacts/release-review/2026-08-22-v9.9.9-prepared-claims-review.md"
    review_json = narrative.replace(".md", ".json")
    return module.validate_claims_review(
        ROOT, prepared=prepared, evidence_commit="R" * 40, artifact_path=review_json,
        target_version="9.9.9", tag_name="v9.9.9",
        run=_fake_git(prepared, review_json, narrative, record, delta=delta),
    )


def test_the_guard_is_WIRED_not_merely_defined() -> None:
    """THE regression round 1 found: every guard test called the assertion
    directly, so deleting its call from `validate_claims_review` broke nothing.
    This drives the validator end to end with a record missing the fields."""
    prepared = {"commit": "P" * 40, "path": "charness-artifacts/release/latest.md", "sha256": "s" * 64}
    narrative = "charness-artifacts/release-review/2026-08-22-v9.9.9-prepared-claims-review.md"
    unscoped = _scoped_record(prepared, narrative, blocking=["scripts/a.py"], advisory=[])
    del unscoped["review_scope"]

    with pytest.raises(SystemExit, match="review_scope"):
        _invoke(unscoped, ["scripts/a.py"])


def test_a_shipped_file_cannot_be_waived_by_calling_it_advisory() -> None:
    """The laundering record a fresh-eye round demonstrated was ACCEPTED: a real
    defect in the release gate itself, declared advisory, filed as an advisory
    finding, published. `classify()` had no production caller."""
    prepared = {"commit": "P" * 40, "path": "charness-artifacts/release/latest.md", "sha256": "s" * 64}
    narrative = "charness-artifacts/release-review/2026-08-22-v9.9.9-prepared-claims-review.md"
    shipped = "skills/public/release/scripts/publish_release_claims_review.py"
    laundered = _scoped_record(
        prepared, narrative,
        blocking=["docs/handoff.md"], advisory=[shipped],
        findings=[{"file": shipped, "summary": "the claims floor no longer refuses an unbound record"}],
    )

    with pytest.raises(SystemExit, match="NOT advisory by classification"):
        _invoke(laundered, ["docs/handoff.md", shipped])


def test_a_scope_that_omits_a_changed_path_is_refused() -> None:
    """Classification-consistency alone still lets a reviewer drop an
    inconvenient path from both lists."""
    prepared = {"commit": "P" * 40, "path": "charness-artifacts/release/latest.md", "sha256": "s" * 64}
    narrative = "charness-artifacts/release-review/2026-08-22-v9.9.9-prepared-claims-review.md"
    record = _scoped_record(prepared, narrative, blocking=["scripts/a.py"], advisory=[])

    with pytest.raises(SystemExit, match="omits 1 BLOCKING changed"):
        _invoke(record, ["scripts/a.py", "scripts/quietly_broken.py"])


def test_a_scope_padded_with_untouched_paths_is_refused() -> None:
    prepared = {"commit": "P" * 40, "path": "charness-artifacts/release/latest.md", "sha256": "s" * 64}
    narrative = "charness-artifacts/release-review/2026-08-22-v9.9.9-prepared-claims-review.md"
    record = _scoped_record(prepared, narrative, blocking=["scripts/a.py", "scripts/never_touched.py"], advisory=[])

    with pytest.raises(SystemExit, match="not in the release delta"):
        _invoke(record, ["scripts/a.py"])


def test_a_faithful_scope_passes_end_to_end() -> None:
    prepared = {"commit": "P" * 40, "path": "charness-artifacts/release/latest.md", "sha256": "s" * 64}
    narrative = "charness-artifacts/release-review/2026-08-22-v9.9.9-prepared-claims-review.md"
    retro = "charness-artifacts/retro/2026-08-22-r.md"
    record = _scoped_record(
        prepared, narrative, blocking=["scripts/a.py"], advisory=[retro],
        findings=[{"file": retro, "summary": "blocker tally drifted"}],
    )

    result = _invoke(record, ["scripts/a.py", retro])

    assert result["verdict"] == "pass"
    assert result["advisory_findings"] == [{"file": retro, "summary": "blocker tally drifted"}]


def test_machine_read_state_under_an_advisory_root_still_blocks() -> None:
    """`charness-artifacts/quality/dup-ratchet-baseline.json` is an INPUT to the
    duplicate ratchet. A directory-only rule let a rebaselined ceiling ship as an
    advisory finding -- a real behaviour change escaping through the prose lane."""
    assert classify("charness-artifacts/quality/dup-ratchet-baseline.json") == "blocking"
    assert classify("charness-artifacts/retro/lesson-ledger.json") == "blocking"
    assert classify("charness-artifacts/goals/x.slice-manifest.json") == "blocking"
    assert classify("charness-artifacts/retro/2026-08-22-r.md") == "advisory"


def test_the_cli_entrypoint_matches_exactly_not_as_a_prefix() -> None:
    """Bare `charness` as a PREFIX matched every `charness-artifacts/...` path,
    which made the loop ordering load-bearing for an undocumented reason and left
    the explicit `charness-artifacts/release/` entry beside it unreachable."""
    assert classify("charness") == "blocking"
    assert classify("charness-artifacts/retro/2026-08-22-r.md") == "advisory"


def _sections_module():
    spec = importlib.util.spec_from_file_location(
        "prs", _RELEASE / "publish_release_artifact_sections.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rendered(**overrides) -> str:
    claims = {
        "path": "charness-artifacts/release-review/x.json",
        "verdict": "pass",
        "observer_distinctness": {
            "kind": "separate-agent-context", "signal": "sig", "review_artifact": "n.md",
        },
        "review_scope": {"blocking_paths": ["scripts/a.py"], "advisory_paths": ["r.md"]},
        "advisory_findings": [],
    }
    claims.update(overrides)
    return "\n".join(_sections_module().claims_review_lines(claims))


def test_the_published_record_names_what_shipped_known_inaccurate() -> None:
    """`published as known-inaccurate` was the design intent and was untrue at
    the one surface outside readers get: the fields were validated and then
    dropped before the renderer. A record saying only `verdict: pass` hides
    exactly what the scope split waived."""
    text = _rendered(advisory_findings=[{"file": "r.md", "summary": "blocker tally drifted"}])

    assert "SHIPPED KNOWN-INACCURATE" in text
    assert "`r.md`: blocker tally drifted" in text


def test_an_empty_advisory_scope_says_so_rather_than_omitting_the_line() -> None:
    """An absent line and "none found" read identically. The split is only
    honest if "nobody looked" is distinguishable."""
    assert "Advisory findings: none recorded by this review." in _rendered()


def test_the_record_reports_both_scope_sizes() -> None:
    text = _rendered()

    assert "1 blocking path(s) gated this tag" in text
    assert "1 advisory path(s)" in text
