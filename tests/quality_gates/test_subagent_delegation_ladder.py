"""The delegation ladder (#475): a mandated review must have a reachable grant.

`skills/shared/references/fresh-eye-subagent-review.md` named exactly ONE source
of the standing delegation request, so in every repo that had never run `setup`
the skills that MANDATE bounded fresh-eye review could not authorize it. The
refusal emitted no failure, no log line, and no ticket -- the same
rule-cannot-fire-where-it-was-written class as #471.

These tests pin the mechanism half only. The behavioural half -- an agent in a
block-less repo actually spawning after rung 3 -- is not obtainable here: the
decision is made by an agent reading its own repo root, and every agent this
suite can reach is rooted in charness, which carries the block.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "skills/shared/references/fresh-eye-subagent-review.md"
RECORD_RELPATH = ".agents/subagent-delegation.json"
SUBAGENT_DELEGATION_TEMPLATE = (
    ROOT / "scripts/templates/agents_subagent_delegation.txt"
).read_text(encoding="utf-8")


def _load_module(relpath: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _write_record(repo: Path, payload) -> None:
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    body = payload if isinstance(payload, str) else json.dumps(payload)
    (repo / RECORD_RELPATH).write_text(body, encoding="utf-8")


@pytest.fixture(scope="module")
def resolver():
    return _load_module("skills/shared/scripts/resolve_subagent_delegation.py", "_resolve_delegation")


@pytest.fixture(scope="module")
def validator():
    return _load_module("scripts/validate_critique_artifacts.py", "_vca_ladder")


@pytest.fixture(scope="module")
def observer():
    return _load_module("skills/public/issue/scripts/issue_critique_observer.py", "_ico_ladder")


# --------------------------------------------------------------------------
# Rung 1: existing repos are unchanged
# --------------------------------------------------------------------------


def test_block_carrying_repo_is_unchanged_and_stops_at_rung_1(resolver) -> None:
    """The no-regression pin, read against the REAL repo, not a fixture.

    A synthetic AGENTS.md spells the marker the way the code does, which is
    exactly how #471 hid for months. This repo carries the block, so it must
    resolve `granted` at rung 1 -- consuming repos that already ran `setup` see
    no behaviour change from the ladder.
    """
    result = resolver.resolve(ROOT)
    assert result["delegation"] == resolver.GRANTED
    assert result["rung"] == 1
    assert result["source"] == "AGENTS.md"
    assert not (ROOT / RECORD_RELPATH).exists()


def test_rung_1_does_not_claim_a_scope_list_it_never_read(resolver) -> None:
    """`scopes` at rung 1 is the shipped template's canonical set, not a repo fact.

    A repo whose block delegates a narrower set would otherwise get a payload
    asserting all five -- a constant standing in for a per-repo fact.
    """
    result = resolver.resolve(ROOT)
    assert result["scopes"] == list(resolver.CANONICAL_SCOPES)
    assert "does not read a per-repo scope list" in result["scopes_source"]


# --------------------------------------------------------------------------
# Rung 3: the reported symptom
# --------------------------------------------------------------------------


def test_repo_without_the_block_asks_rather_than_blocking(tmp_path: Path, resolver) -> None:
    """#475's reported symptom: no AGENTS.md is not a refusal, it is an unasked question."""
    result = resolver.resolve(tmp_path)
    assert result["delegation"] == resolver.ASK
    assert result["rung"] == 3
    assert result["source"] is None
    assert set(result["scopes"]) == set(resolver.CANONICAL_SCOPES)
    assert "ask the user once" in str(result["next_action"])


# --------------------------------------------------------------------------
# Rung 2
# --------------------------------------------------------------------------


def test_structured_grant_answers_at_rung_2_without_agents_md(tmp_path: Path, resolver) -> None:
    """Rung 2 is the rung that removes the prose-matching fragility #471 proved."""
    resolver.record(
        tmp_path, decision=resolver.GRANTED, scopes=["critique"], recorded_on="2026-08-03", note="asked at slice A"
    )
    result = resolver.resolve(tmp_path)
    assert result["delegation"] == resolver.GRANTED
    assert result["rung"] == 2
    assert result["source"] == RECORD_RELPATH
    assert result["scopes"] == ["critique"]
    assert result["scopes_source"] == "record"
    assert result["provenance"]["note"] == "asked at slice A"


def test_a_decline_is_honoured_and_not_re_asked(tmp_path: Path, resolver) -> None:
    """A refusal to grant is an answer. It must stop the review, not loop."""
    resolver.record(tmp_path, decision=resolver.DECLINED, scopes=[], recorded_on="2026-08-03", note=None)
    result = resolver.resolve(tmp_path)
    assert result["delegation"] == resolver.DECLINED
    assert result["rung"] == 2
    assert "do not re-ask" in str(result["next_action"])
    # It must NOT be prescribed as a host incapacity.
    assert "delegation signal" in str(result["next_action"])
    assert "NOT a host incapacity" in str(result["next_action"])


def test_setup_writing_rung_1_cannot_silently_erase_a_decline(tmp_path: Path, resolver) -> None:
    """The sequence this harness itself manufactures.

    `setup` WRITES the rung-1 block. Decline at rung 3, then run `setup`, and a
    rung-1-first resolver would return `granted` forever after -- the user's only
    "no" erased with nothing said. The conflict must surface as `ask`.
    """
    resolver.record(tmp_path, decision=resolver.DECLINED, scopes=[], recorded_on="2026-08-03", note=None)
    (tmp_path / "AGENTS.md").write_text(
        "# Repo\n\n## Subagent Delegation\n\n"
        "- Repo-mandated bounded fresh-eye subagent reviews are already delegated.\n",
        encoding="utf-8",
    )
    result = resolver.resolve(tmp_path)
    assert result["delegation"] == resolver.ASK
    assert result["delegation"] != resolver.GRANTED
    assert "conflict" in str(result["source"])
    assert "declined" in str(result["reason"])


# --------------------------------------------------------------------------
# Fail-closed direction: toward ask, never toward granted
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        "not json at all {",
        ["granted"],
        {"version": 1},
        {"bounded_review_delegation": "GRANTED_MAYBE"},
        {"bounded_review_delegation": True},
        # A `scopes` key the author tried to NARROW must never widen to all five.
        {"bounded_review_delegation": "granted", "scopes": []},
        {"bounded_review_delegation": "granted", "scopes": "critique"},
        {"bounded_review_delegation": "granted", "scopes": [{"name": "critique"}]},
    ],
)
def test_unreadable_record_resolves_to_ask_never_to_granted(tmp_path: Path, resolver, payload) -> None:
    """Fail-closed here means ASK, the opposite of most gates in this repo.

    A malformed record must never be read as a grant: a silent self-grant would
    let the plugin authorize its own spawns in every repo that installs it. A
    redundant question costs one turn; that costs the grant itself.
    """
    _write_record(tmp_path, payload)
    result = resolver.resolve(tmp_path)
    assert result["delegation"] == resolver.ASK
    assert result["rung"] == 3


def test_unreadable_record_file_is_not_adopted(tmp_path: Path, resolver) -> None:
    """`is_file()` can pass on a file this process cannot read; unreadable is not a grant."""
    _write_record(tmp_path, {"bounded_review_delegation": "granted"})
    record = tmp_path / RECORD_RELPATH
    record.chmod(0o000)
    try:
        if os.access(record, os.R_OK):  # running as root: the mode is not enforced
            pytest.skip("cannot make a file unreadable for this user")
        assert resolver.resolve(tmp_path)["delegation"] == resolver.ASK
    finally:
        record.chmod(0o644)


def test_a_narrowed_grant_does_not_read_as_granted_to_an_uncovered_scope(tmp_path: Path, resolver) -> None:
    """"Yes, but only for critique" must not answer a `release` caller."""
    resolver.record(tmp_path, decision=resolver.GRANTED, scopes=["critique"], recorded_on=None, note="only critique")
    covered = resolver.resolve(tmp_path, scope="critique")
    assert covered["delegation"] == resolver.GRANTED
    assert covered["scope_covered"] is True
    uncovered = resolver.resolve(tmp_path, scope="release")
    assert uncovered["delegation"] == resolver.ASK
    assert uncovered["scope_covered"] is False


# --------------------------------------------------------------------------
# `record` hazards
# --------------------------------------------------------------------------


def test_record_refuses_a_grant_with_no_provenance(tmp_path: Path, resolver) -> None:
    """`recorded_by: user` is a literal the writer chose; a note is the only real provenance."""
    with pytest.raises(resolver.DelegationError):
        resolver.record(tmp_path, decision=resolver.GRANTED, scopes=[], recorded_on=None, note=None)
    with pytest.raises(resolver.DelegationError):
        resolver.record(tmp_path, decision=resolver.GRANTED, scopes=[], recorded_on=None, note="   ")
    assert not (tmp_path / RECORD_RELPATH).exists()


def test_record_refuses_a_repo_root_that_is_not_a_directory(tmp_path: Path, resolver) -> None:
    """A typo'd or cwd-relative root would otherwise CREATE the path and report success,
    landing the answer where no later resolve looks -- so the user is asked again."""
    with pytest.raises(resolver.DelegationError):
        resolver.record(tmp_path / "nope", decision=resolver.DECLINED, scopes=[], recorded_on=None, note=None)
    assert not (tmp_path / "nope").exists()


def test_record_names_the_decision_it_replaced(tmp_path: Path, resolver) -> None:
    """Silent clobber of the opposite answer is the class this ladder exists to stop."""
    resolver.record(tmp_path, decision=resolver.DECLINED, scopes=[], recorded_on=None, note=None)
    result = resolver.record(tmp_path, decision=resolver.GRANTED, scopes=[], recorded_on=None, note="user changed mind")
    assert result["replaced_decision"] == resolver.DECLINED
    assert Path(str(result["path"])).is_absolute()


def test_a_grant_with_no_note_is_flagged_at_the_point_of_use(tmp_path: Path, resolver) -> None:
    """A hand-written record bypasses `record`'s note floor; `resolve` must still say so."""
    _write_record(tmp_path, {"bounded_review_delegation": "granted"})
    result = resolver.resolve(tmp_path)
    assert result["delegation"] == resolver.GRANTED
    assert "not proof" in result["provenance_warning"]


# --------------------------------------------------------------------------
# Three readers, one contract: behavioural parity, not marker-text parity
# --------------------------------------------------------------------------

_ADOPTED_BLOCK = (
    "# Repo\n\n## Subagent Delegation\n\n"
    "- Repo-mandated bounded fresh-eye subagent reviews are **already delegated** by contract.\n"
)
# The marker is 58 characters and fits one line only at the template's current
# wrap width. A reflow must not drop an adopting repo out of the contract.
_ADOPTED_REFLOWED = (
    "# Repo\n\n## Subagent Delegation\n\n"
    "- Repo-mandated bounded fresh-eye subagent reviews are already\n  delegated by contract.\n"
)
# A fence is documentation, not the repo's own assertion. `setup`'s policy
# reference ships this template inside one for operators to copy.
_QUOTED_ONLY = (
    "# Repo\n\n## Review Policy\n\nWe have not adopted the charness contract. The template reads:\n\n"
    "```markdown\n## Subagent Delegation\n\n"
    "- Repo-mandated bounded fresh-eye subagent reviews are already delegated.\n```\n"
)

_PARITY_CASES = {
    "no agents.md": (None, None, False),
    "agents.md without the block": ("# Repo\n\nNothing here.\n", None, False),
    "heading only, no contract sentence": ("# Repo\n\n## **Subagent** _Delegation_\n\nad hoc.\n", None, False),
    "adopted, bolded": (_ADOPTED_BLOCK, None, True),
    "adopted, reflowed across a line break": (_ADOPTED_REFLOWED, None, True),
    "quoted inside a fence only": (_QUOTED_ONLY, None, False),
    "rung 2 granted, no agents.md": (None, {"bounded_review_delegation": "granted"}, True),
    "rung 2 declined, no agents.md": (None, {"bounded_review_delegation": "declined"}, False),
    "rung 2 malformed, no agents.md": (None, "{ broken", False),
    "rung 2 granted, agents.md without the block": ("# Repo\n\nNothing.\n", {"bounded_review_delegation": "granted"}, True),
    # The states the ladder INVENTED. An earlier fixture set omitted exactly
    # these, so "behavioural parity" held only over inputs chosen to avoid the
    # divergences -- the same blind spot as the marker-text test it replaced,
    # one level down.
    "conflict: block plus a recorded decline": (
        _ADOPTED_BLOCK,
        {"bounded_review_delegation": "declined"},
        False,
    ),
    "rung 2 granted but scopes exclude this scope": (
        None,
        {"bounded_review_delegation": "granted", "scopes": ["release"]},
        False,
    ),
    "rung 2 granted with an unreadable scopes key": (
        None,
        {"bounded_review_delegation": "granted", "scopes": []},
        False,
    ),
    "unclosed fence above the block does not swallow it": (
        "# Repo\n\n```bash\necho oops\n\n## Subagent Delegation\n\n"
        "- Repo-mandated bounded fresh-eye subagent reviews are already delegated.\n",
        None,
        True,
    ),
}
# The scope every reader is asked about, so the narrowed-grant row means something.
_PARITY_SCOPE = "critique"


@pytest.mark.parametrize("case", sorted(_PARITY_CASES))
def test_all_three_readers_of_the_one_contract_agree_behaviourally(
    tmp_path: Path, resolver, validator, observer, case: str
) -> None:
    """One contract, three readers, deliberately duplicated -- pin BEHAVIOUR, not text.

    The two prior readers restate the markers rather than importing them, and for
    one window only one carried the markup-flattening repair, so they disagreed
    about whether this repo had adopted its own contract. The parity test that
    existed then compared marker TEXT and could not have seen it. The ladder adds
    a third reader and two new rungs, so parity is now checked over a shared
    fixture set: text equality cannot see one reader knowing two rungs while the
    others know one.

    The shared question is "is bounded review AUTHORIZED here for this scope".
    All three must answer it the same way, including for the conflict and
    narrowed-scope states -- those are where a reader that models fewer states
    than the contract would refuse a repo the ladder just told not to spawn.
    """
    agents_text, record_payload, expected_authorized = _PARITY_CASES[case]
    repo = tmp_path / "repo"
    repo.mkdir()
    if agents_text is not None:
        (repo / "AGENTS.md").write_text(agents_text, encoding="utf-8")
    if record_payload is not None:
        _write_record(repo, record_payload)

    ladder_grants = resolver.resolve(repo, scope=_PARITY_SCOPE)["delegation"] == resolver.GRANTED
    assert validator.has_repo_delegation_contract(repo, scope=_PARITY_SCOPE) is expected_authorized, case
    assert observer.repo_requires_delegated_observer(repo, scope=_PARITY_SCOPE) is expected_authorized, case
    assert ladder_grants is expected_authorized, case


def test_marker_text_still_matches_across_the_three_readers(resolver, validator, observer) -> None:
    """Behavioural parity is the real guard; marker equality is the cheap corroboration."""
    assert resolver.DELEGATION_CONTRACT_MARKERS == validator.DELEGATION_CONTRACT_MARKERS
    assert resolver.DELEGATION_CONTRACT_MARKERS == observer.DELEGATION_CONTRACT_MARKERS


# --------------------------------------------------------------------------
# The decline must survive the floors it is prescribed to
# --------------------------------------------------------------------------


def _prescribed_decline_status(resolver) -> str:
    """The exact text the resolver tells a caller to write, read from the source.

    Taken from the module constant rather than retyped, so this test cannot drift
    from the prescription it is checking.
    """
    return resolver._DECLINE_ACTION


def _decline_status_line(resolver) -> str:
    """The one-line record an agent copying the prescription actually writes."""
    return f"Fresh-eye satisfaction: {_prescribed_decline_status(resolver).split('`')[1]}\n"


def test_the_prescribed_decline_survives_the_quality_artifact_floor(resolver) -> None:
    """The critique validator is not the only floor the prescription must survive.

    `validate_quality_artifact` carries its own copy of the blocked-signal rule,
    and `quality` is one of the canonical bounded-review scopes -- so a decline
    recorded there hit a floor that still demanded a `host signal:` line, and
    the only way to comply was to write one that would have been a lie.
    """
    quality = _load_module("scripts/validate_quality_artifact.py", "_vqa_ladder")
    body = _prescribed_decline_status(resolver).split("`")[1]
    section = ["## Delegated Review", f"- status: blocked — {body}", "## Commands Run"]
    quality.validate_delegated_review_section(section)  # must not raise
    # And the floor is still a floor: a bare `blocked` with no signal is refused.
    with pytest.raises(Exception):
        quality.validate_delegated_review_section(["## Delegated Review", "- status: blocked", "## Commands Run"])


def test_a_grant_narrowed_away_from_a_scope_does_not_wedge_that_scope(
    tmp_path: Path, resolver, validator, observer
) -> None:
    """A repo must never be refused for not spawning a reviewer it may not spawn.

    The ladder returns `ask` for an uncovered scope. If the floors still read the
    repo as fully authorized, every close is refused unless the artifact records
    a delegated observer the ladder just forbade -- refused if it does not spawn,
    unauthorized if it does.
    """
    resolver.record(tmp_path, decision=resolver.GRANTED, scopes=["critique"], recorded_on=None, note="critique only")
    assert resolver.resolve(tmp_path, scope="issue")["delegation"] == resolver.ASK
    assert observer.repo_requires_delegated_observer(tmp_path, scope="issue") is False
    assert validator.has_repo_delegation_contract(tmp_path, scope="issue") is False
    # The scope it DOES cover stays authorized.
    assert validator.has_repo_delegation_contract(tmp_path, scope="critique") is True


def test_a_recorded_decline_is_not_overridden_at_the_floors(
    tmp_path: Path, resolver, validator, observer
) -> None:
    """The conflict state, seen from the floors rather than from the resolver.

    `setup` writes the `AGENTS.md` block. If the floors treat rung 1 as final,
    they refuse artifacts in a repo whose user explicitly said no -- a refusal
    the harness manufactures on top of the answer it was supposed to honour.
    """
    resolver.record(tmp_path, decision=resolver.DECLINED, scopes=[], recorded_on=None, note=None)
    (tmp_path / "AGENTS.md").write_text(_ADOPTED_BLOCK, encoding="utf-8")
    assert resolver.resolve(tmp_path)["delegation"] == resolver.ASK
    assert validator.has_repo_delegation_contract(tmp_path) is False
    assert observer.repo_requires_delegated_observer(tmp_path) is False


def test_a_genuine_host_signal_is_not_reclassified_as_a_user_decline(observer) -> None:
    """The damaging direction: a machine incapacity typed as a deliberate "no".

    "the spawn API returned 403, delegation declined by the workspace policy" is
    how a real host refusal reads. Reclassifying it would suppress the very
    prompt asking the operator to confirm the host truly could not spawn.
    """
    strip = _load_module("skills/public/issue/scripts/issue_markdown_lib.py", "_iml_host").strip_code_fences
    result = observer.observer_disposition(
        "Fresh-eye satisfaction: blocked host signal: the spawn API returned 403, "
        "delegation declined by the workspace policy\n",
        strip_code_fences=strip,
    )
    assert result["disposition"] == "blocked"
    assert result["blocked_kind"] == "host"


def test_the_decline_reaches_the_operator_facing_advisory() -> None:
    """A guard whose value nothing consumes is the class, one level out.

    `blocked_kind` was computed and discarded while the advisory an operator
    reads at the irreversible boundary still told them to confirm a host failure
    that never happened.
    """
    critique = _load_module("skills/public/issue/scripts/issue_resolution_critique.py", "_irc_ladder")
    declined = critique._observer_advisories(
        [
            {
                "numbers": [475],
                "fresh_eye_observer": {
                    "disposition": "blocked",
                    "blocked_kind": "delegation-declined",
                    "value": "blocked delegation-declined",
                },
            }
        ]
    )
    assert len(declined) == 1
    assert "DECLINED" in declined[0]
    assert "host genuinely could not spawn" not in declined[0]
    host = critique._observer_advisories(
        [
            {
                "numbers": [1],
                "fresh_eye_observer": {
                    "disposition": "blocked",
                    "blocked_kind": "host",
                    "value": "blocked host signal: no Agent tool",
                },
            }
        ]
    )
    assert "host genuinely could not spawn" in host[0]


def test_prescribed_decline_record_passes_the_authoring_blocked_signal_floor(resolver, validator) -> None:
    """A prescribed record that its own floor refuses is a rule that cannot fire.

    The floor matched a signal heading only at the START of a line, while the
    typed record is written as ONE line -- `Fresh-eye satisfaction: blocked
    <value> — <heading>: <signal>`. So the widening that added `delegation
    signal` could not fire on any record the contract actually prescribes: the
    repair reproduced the class it was repairing. The status below is built from
    the resolver's own prescription rather than retyped, because the first
    version of this test hand-built a TWO-line form that appears nowhere in the
    contract and passed while the prescribed form was still refused.
    """
    assert "delegation signal" in validator.SIGNAL_HEADINGS
    status = _decline_status_line(resolver)
    assert "delegation signal:" in status
    assert not status.lstrip().lower().startswith("delegation signal:"), (
        "the prescribed record is an inline form; a test using a line-initial heading "
        "would pass without exercising the repair"
    )
    assert validator.has_blocked_signal_detail(status) is True


def test_a_decline_is_not_reported_as_a_host_incapacity(observer) -> None:
    """The `blocked` valve means "the host could not spawn". A user's "no" is not that.

    Reporting a deliberate refusal as a machine limitation at an irreversible
    public boundary is a proof-semantics change; the ladder moves authorization
    only.
    """

    _strip = _load_module("skills/public/issue/scripts/issue_markdown_lib.py", "_iml_ladder").strip_code_fences

    declined = observer.observer_disposition(
        "Fresh-eye satisfaction: blocked delegation-declined — delegation signal: the user "
        f"declined the standing request, recorded in {RECORD_RELPATH}\n",
        strip_code_fences=_strip,
    )
    assert declined["disposition"] == "blocked"
    assert declined["blocked_kind"] == "delegation-declined"

    host = observer.observer_disposition(
        "Fresh-eye satisfaction: blocked host signal: the Agent tool is not exposed in this session\n",
        strip_code_fences=_strip,
    )
    assert host["disposition"] == "blocked"
    assert host["blocked_kind"] == "host"


# --------------------------------------------------------------------------
# The contract surface itself
# --------------------------------------------------------------------------


def test_reference_names_all_three_rungs_and_their_legitimacy() -> None:
    """The contract text is the surface an agent actually reads; a mechanism the
    reference does not name cannot fire either -- that is this defect's own shape."""
    text = REFERENCE.read_text(encoding="utf-8")
    assert "## Where The Delegation Request Comes From" in text
    assert RECORD_RELPATH in text
    assert "resolve_subagent_delegation.py" in text
    assert "ask the user once" in text.lower()
    # No silent self-grant: the rejected alternative must stay named as rejected.
    assert "A skill invocation is not a rung." in text
    # Rung 2 read even when rung 1 answers, or `setup` erases the user's "no".
    assert "Rung 2 is read even when rung 1 answers" in text


def test_ladder_does_not_loosen_what_counts_as_proof() -> None:
    """The ladder moves AUTHORIZATION only. A genuine host block still blocks and
    a same-agent substitute stays forbidden -- pinned so a later edit cannot
    quietly widen an authorization change into a proof change."""
    flat = REFERENCE.read_text(encoding="utf-8").replace("\n", " ")
    assert "same-agent pass is still forbidden" in flat
    assert "Only a real tool refusal, missing spawn surface, exhausted host" in flat
    assert "Do not silently collapse into a same-agent review" in REFERENCE.read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# Rung-2 record shapes, exercised through BOTH shipped readers
#
# Added when the pre-push mutation gate reported these branches as
# changed-and-uncovered. Each one is a way a record can fail to be a decision,
# and every one of them must land on "not authorized" rather than on a grant.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param([1, 2, 3], id="not-an-object"),
        pytest.param({"bounded_review_delegation": 7}, id="decision-not-a-string"),
        pytest.param({"bounded_review_delegation": "maybe"}, id="unrecognized-decision"),
        pytest.param({"bounded_review_delegation": "granted", "scopes": []}, id="empty-scopes"),
        pytest.param({"bounded_review_delegation": "granted", "scopes": [1]}, id="non-string-scopes"),
        pytest.param({"bounded_review_delegation": "granted", "scopes": {"a": 1}}, id="scopes-not-a-list"),
    ],
)
def test_an_unusable_record_authorizes_nothing_in_either_shipped_reader(
    tmp_path: Path, validator, observer, payload
) -> None:
    _write_record(tmp_path, payload)
    assert validator.has_repo_delegation_contract(tmp_path, scope="critique") is False
    assert observer.repo_requires_delegated_observer(tmp_path, scope="issue") is False


def test_a_record_granting_no_scopes_key_covers_every_scope(tmp_path: Path, validator, observer) -> None:
    """An ABSENT `scopes` key is a grant with no narrowing -- distinct from a
    present-but-unusable one, which is refused above."""
    _write_record(tmp_path, {"bounded_review_delegation": "granted"})
    for scope in ("critique", "issue", "release"):
        assert validator.has_repo_delegation_contract(tmp_path, scope=scope) is True
        assert observer.repo_requires_delegated_observer(tmp_path, scope=scope) is True


def test_scope_matching_is_case_and_whitespace_insensitive(tmp_path: Path, validator, observer) -> None:
    """A capitalization must not decide whether a rule fires -- the whole reason
    rung 2 is structured rather than prose."""
    _write_record(tmp_path, {"bounded_review_delegation": "GRANTED ", "scopes": ["  Critique "]})
    assert validator.has_repo_delegation_contract(tmp_path, scope="critique") is True
    assert observer.repo_requires_delegated_observer(tmp_path, scope="CRITIQUE") is True
    assert validator.has_repo_delegation_contract(tmp_path, scope="release") is False


def test_an_unreadable_record_file_authorizes_nothing_in_either_reader(
    tmp_path: Path, validator, observer
) -> None:
    _write_record(tmp_path, {"bounded_review_delegation": "granted"})
    record = tmp_path / RECORD_RELPATH
    record.chmod(0o000)
    try:
        if os.access(record, os.R_OK):  # running as root: the mode is not enforced
            pytest.skip("cannot make a file unreadable for this user")
        assert validator.has_repo_delegation_contract(tmp_path) is False
        assert observer.repo_requires_delegated_observer(tmp_path) is False
    finally:
        record.chmod(0o644)


def test_a_non_utf8_agents_md_is_not_adopted_and_does_not_traceback(
    tmp_path: Path, resolver, validator, observer
) -> None:
    """A consuming repo can commit `AGENTS.md` in cp1252. Every reader must treat
    that as "not adopted" rather than letting a UnicodeDecodeError escape -- it is
    not an OSError, so a handler catching only OSError would surface a traceback
    instead of a verdict."""
    (tmp_path / "AGENTS.md").write_bytes(b"# Repo\n\n## Subagent Delegation\n\n- caf\xe9 \x93quoted\x94\n")
    assert resolver.has_agents_md_delegation_contract(tmp_path) is False
    assert validator.has_repo_delegation_contract(tmp_path) is False
    assert observer.repo_requires_delegated_observer(tmp_path) is False
    # And rung 2 still answers underneath it.
    _write_record(tmp_path, {"bounded_review_delegation": "granted"})
    assert validator.has_repo_delegation_contract(tmp_path) is True
    assert observer.repo_requires_delegated_observer(tmp_path) is True


def test_the_shipped_setup_template_satisfies_BOTH_readers_of_the_contract() -> None:
    """#476: the block `setup` writes must be recognized by everything that reads it.

    Two spellings of one contract had grown apart. The marker readers require
    `... are already delegated`; the compact-contract inspector requires
    `standing delegation request` (plus canonical scopes, host block, reviewer
    tier, spawn shape). The shipped template carried only the second, so a repo
    that ran `setup` and accepted the block read as NEVER HAVING ADOPTED it in
    all three marker readers -- the same rule-cannot-fire class as #471 and #475,
    sitting in the path `setup` actually writes.

    Pinned against the REAL template, not a fixture: a fixture would spell it the
    way whichever matcher the author had in mind wants, which is how this hid.
    """
    resolver = _load_module("skills/shared/scripts/resolve_subagent_delegation.py", "_rsd_tmpl")
    inspector = _load_module("scripts/setup_agent_docs_fresh_eye_lib.py", "_fe_tmpl")
    template = SUBAGENT_DELEGATION_TEMPLATE

    normalized = resolver.normalize_contract_text(template)
    for marker in resolver.DELEGATION_CONTRACT_MARKERS:
        assert marker in normalized, f"marker readers would not adopt a repo set up from this template: {marker!r}"
    assert inspector._missing_snippets(template, inspector.FRESH_EYE_COMPACT_REQUIRED_SNIPPETS) == []
    assert inspector.fresh_eye_compact_contract_present(template) is True

    # THIRD reader, added after it split from the writer exactly as #476 predicts.
    # `_detect_charness_subagent_policy` reads AGENTS.md for the per-host subagent
    # model/effort policy. When the contract dropped the baked Codex model id, the reader
    # was moved and this template was not, so charness shipped a template its own
    # inspector flagged. Pinned against the REAL template for the same reason as above.
    #
    # #552: this reader is GATED on `charness_managed`, so the routing block above it
    # decides whether the assertion below can fail at all. It used to be hand-written
    # here, spelling the recognizer's required `context-only` — which the shipped
    # renderer never emits — so this pin passed while the real setup path was excluded
    # from the very check this test guards. Both halves now come from their writers.
    docs = _load_module("scripts/setup_agent_docs_lib.py", "_sad_tmpl")
    routing = _load_module("skills/public/setup/scripts/render_skill_routing.py", "_rsr_tmpl")
    seeded_routing, _ = routing._render_skill_routing()
    policy, _ = docs._detect_charness_subagent_policy("# Agents\n\n" + seeded_routing + "\n" + template)
    assert policy["charness_managed"] is True, (
        "the gate in front of the assertion below is shut, so it cannot fail"
    )
    assert policy["subagent_model_policy_complete"] is True, (
        "a repo set up from this template would be flagged for missing the per-host "
        "subagent model policy the template is supposed to write"
    )


def test_a_repo_set_up_from_the_shipped_template_reads_as_adopted(
    tmp_path: Path, resolver, validator, observer
) -> None:
    """The end-to-end shape of #476, through every reader that acts on adoption."""
    (tmp_path / "AGENTS.md").write_text(
        "# Consumer repo\n\n"
        + SUBAGENT_DELEGATION_TEMPLATE,
        encoding="utf-8",
    )
    assert resolver.resolve(tmp_path)["delegation"] == resolver.GRANTED
    assert resolver.resolve(tmp_path)["rung"] == 1
    assert validator.has_repo_delegation_contract(tmp_path) is True
    assert observer.repo_requires_delegated_observer(tmp_path) is True
