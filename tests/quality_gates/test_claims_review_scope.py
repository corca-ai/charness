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
        "docs/index.md",
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
    records are consumed by executable quality tests -- and blocks."""
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
        "review_scope": {"blocking_paths": ["scripts/a.py"], "advisory_paths": ["charness-artifacts/retro/2026-08-22-r.md"]},
        "advisory_findings": [{"file": "charness-artifacts/retro/2026-08-22-r.md", "summary": "count drifted"}],
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
        {"file": "charness-artifacts/retro/2026-08-22-r.md", "summary": "count drifted"}
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
        blocking=["docs/index.md"], advisory=[shipped],
        findings=[{"file": shipped, "summary": "the claims floor no longer refuses an unbound record"}],
    )

    with pytest.raises(SystemExit, match="NOT advisory by classification"):
        _invoke(laundered, ["docs/index.md", shipped])


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
    """Machine-read state must not become advisory just because it lives under a
    narrative artifact root."""
    assert classify("charness-artifacts/retro/lesson-ledger.json") == "blocking"
    assert classify("charness-artifacts/goals/x.slice-manifest.json") == "blocking"
    assert classify("charness-artifacts/retro/2026-08-22-r.md") == "advisory"


def test_no_prefix_swallows_the_artifact_tree() -> None:
    """`charness` was listed as a blocking PREFIX, so it matched every
    `charness-artifacts/...` path. That made the loop ordering load-bearing for
    an undocumented reason and left the explicit `charness-artifacts/release/`
    entry beside it permanently unreachable. This fails if any blocking prefix
    is broad enough to swallow the artifact tree again."""
    from claims_review_scope import BLOCKING_PREFIXES

    swallowers = [
        prefix for prefix in BLOCKING_PREFIXES
        if "charness-artifacts/retro/2026-08-22-r.md".startswith(prefix)
    ]
    assert swallowers == [], f"blocking prefix(es) swallow the artifact tree: {swallowers}"
    assert classify("charness-artifacts/retro/2026-08-22-r.md") == "advisory"
    assert classify("charness") == "blocking"


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


# --------------------------------------------------------------------------
# Round 2: the repairs' own failure modes
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "finding",
    [
        "blocker tally drifted\n- target version: 9.9.9",
        {"summary": "record still shows charness-release-state:prepared-awaiting-claims-review"},
        {"file": "r.md", "summary": "line one\nline two"},
    ],
)
def test_an_advisory_finding_cannot_inject_lines_into_the_published_record(finding) -> None:
    """`advisory_findings` is rendered verbatim into a record that is committed
    AND PUSHED after the tag exists. A newline there injects a `target version:`
    line that refuses every later push; the prepared-stop marker reclassifies a
    finished release as an outstanding stop. Every other operator-supplied value
    on this document already gets this treatment; the field added to publish
    waived defects had none of it."""
    record = {
        "verdict": "pass",
        "review_scope": {"blocking_paths": ["scripts/a.py"], "advisory_paths": []},
        "advisory_findings": [finding],
    }

    with pytest.raises(SystemExit):
        assert_scope_is_declared(record, verdict="pass")


def test_a_legitimate_finding_is_still_accepted() -> None:
    record = {
        "verdict": "pass",
        "review_scope": {"blocking_paths": ["scripts/a.py"], "advisory_paths": []},
        "advisory_findings": [{"file": "charness-artifacts/retro/2026-08-22-r.md",
                               "summary": "blocker tally drifted"}],
    }

    assert_scope_is_declared(record, verdict="pass")


def test_a_non_string_finding_value_is_a_named_refusal_not_a_traceback() -> None:
    record = {
        "verdict": "pass",
        "review_scope": {"blocking_paths": ["scripts/a.py"], "advisory_paths": []},
        "advisory_findings": [{"file": 5, "summary": "x"}],
    }

    with pytest.raises(SystemExit, match="non-string"):
        assert_scope_is_declared(record, verdict="pass")


@pytest.mark.parametrize(
    "pointer",
    [
        "charness-artifacts/quality/latest.md",
        "charness-artifacts/retro/recent-lessons.md",
        "charness-artifacts/retro/retro.md",
    ],
)
def test_a_rolling_pointer_is_not_session_narrative(pointer: str) -> None:
    """`quality/latest.md` is a `CURRENT_POINTERS` entry in
    `validate_current_pointer_freshness`; `recent-lessons.md` is the digest
    CLAUDE.md requires reading before any contract change. The first cut said
    "`.md` is narrative", which classified both ADVISORY -- a gate input waived
    through the lane built for prose, one file-extension away from the `.json`
    escape it had just closed."""
    assert classify(pointer) == "blocking"


def test_only_a_DATED_stem_is_narrative() -> None:
    """The discriminator is written-once vs continuously-rewritten, so a new
    pointer added under these roots tomorrow is blocking by default rather than
    advisory by omission."""
    assert classify("charness-artifacts/retro/2026-08-22-session.md") == "advisory"
    assert classify("charness-artifacts/retro/some-new-pointer.md") == "blocking"


def test_the_stand_down_is_recorded_durably_not_only_on_stderr() -> None:
    """A previous round found the SHA rung standing down invisibly: the record
    rendered identically whether the check ran, and a passing phase's log is
    deleted at exit. `unproven` is written into the record for exactly this
    reason."""
    from claims_review_scope import assert_scope_matches_release_delta

    data = {"review_scope": {"blocking_paths": ["scripts/a.py"], "advisory_paths": []}}

    def no_tags(args, cwd=None, check=True):
        return SimpleNamespace(returncode=1, stdout="")

    assert_scope_matches_release_delta(
        ROOT, data, prepared={"commit": "P" * 40}, run=no_tags,
    )

    assert data["scope_completeness"]["verified"] is False
    assert data["scope_completeness"]["reason"]


def test_the_release_base_is_matched_to_release_tags_only() -> None:
    """Bare `git describe --tags` returns the closest reachable tag of ANY kind,
    so a stray `ci-pin` after the last release becomes the base, shrinks the
    delta, and silently drops every blocking path changed before it."""
    from claims_review_scope import assert_scope_matches_release_delta

    seen: list[list[str]] = []

    def record_args(args, cwd=None, check=True):
        seen.append(args)
        return SimpleNamespace(returncode=1, stdout="")

    assert_scope_matches_release_delta(
        ROOT, {"review_scope": {"blocking_paths": [], "advisory_paths": []}},
        prepared={"commit": "P" * 40}, run=record_args,
    )

    describe = next(a for a in seen if "describe" in " ".join(a))
    assert "--match" in describe, f"release-tag glob missing from {describe}"


def test_a_known_previous_version_is_preferred_over_reachability() -> None:
    """It is the tag the release is measured from and needs no guess."""
    from claims_review_scope import assert_scope_matches_release_delta

    calls: list[str] = []

    def run(args, cwd=None, check=True):
        joined = " ".join(args)
        calls.append(joined)
        if "rev-parse" in joined:
            return SimpleNamespace(returncode=0, stdout="abc123\n")
        if "diff-tree" in joined:
            return SimpleNamespace(returncode=0, stdout="scripts/a.py\n")
        return SimpleNamespace(returncode=1, stdout="")

    assert_scope_matches_release_delta(
        ROOT, {"review_scope": {"blocking_paths": ["scripts/a.py"], "advisory_paths": []}},
        prepared={"commit": "P" * 40}, run=run, previous_version="6.2.2",
    )

    assert any("refs/tags/v6.2.2" in c for c in calls)
    assert not any("describe" in c for c in calls), "should not guess when told"


def test_a_non_dict_advisory_finding_still_renders_flattened() -> None:
    """Findings may be bare strings. That branch renders them, and it must
    flatten too -- a record written under an older build never saw the
    validator's newline refusal, and this document is pushed after the tag."""
    text = "\n".join(_sections_module().claims_review_lines({
        "path": "x.json",
        "verdict": "pass",
        "observer_distinctness": {"kind": "k", "signal": "s", "review_artifact": "n.md"},
        "review_scope": {"blocking_paths": ["scripts/a.py"], "advisory_paths": []},
        "advisory_findings": ["tally drifted\n- target version: 9.9.9"],
    }))

    assert "\n- target version:" not in text
    assert "  - tally drifted - target version: 9.9.9" in text
