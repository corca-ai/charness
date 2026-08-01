"""Who read the resolution critique, at the issue-close boundary.

The floor checked that a `Critique #N: <path>` line exists and binds. It never
opened the cited file, so an artifact recording that NO distinct observer read
the resolution passed exactly as well as one recording a delegated review — at a
public, irreversible boundary.

These tests pin the three fixtures the acceptance names (delegated /
self-authored / blocked), the two portability arms (contract repo vs not), and
the refusal message the close carrier prints.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

from tests.quality_gates.issue_closeout_support import bug_closeout_body, seed_commit
from tests.quality_gates.support import ROOT, run_script, write_argv_logging_fake

SCRIPT = "skills/public/issue/scripts/issue_tool.py"
CRITIQUE_REL = "charness-artifacts/critique/res-42.md"

# Both markers `repo_requires_delegated_observer` looks for, so a fixture repo can
# opt INTO the delegation contract the way a real consuming repo does.
CONTRACT_AGENTS_MD = (
    "# Agents\n\n## Subagent Delegation\n\n"
    "Repo-mandated bounded fresh-eye subagent reviews are already delegated by this contract.\n"
)


def _load_observer():
    path = ROOT / "skills" / "public" / "issue" / "scripts" / "issue_critique_observer.py"
    spec = importlib.util.spec_from_file_location("issue_critique_observer", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_markdown_lib():
    path = ROOT / "skills" / "public" / "issue" / "scripts" / "issue_markdown_lib.py"
    spec = importlib.util.spec_from_file_location("issue_markdown_lib_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: The PRODUCTION fence stripper, not a copy. A local re-implementation would
#: prove the injected callable works and say nothing about the one actually wired
#: in — and the two have already diverged once (`~~~` was unhandled here).
_strip_code_fences = _load_markdown_lib().strip_code_fences


def _seed(repo: Path, *, satisfaction: str | None, contract: bool) -> None:
    """A closeout whose `Critique:` line cites a real artifact recording `satisfaction`."""
    critique = repo / CRITIQUE_REL
    critique.parent.mkdir(parents=True, exist_ok=True)
    body = "Critique of the #42 resolution.\n"
    if satisfaction is not None:
        body += f"\nFresh-eye satisfaction: {satisfaction}\n"
    critique.write_text(body, encoding="utf-8")
    if contract:
        (repo / "AGENTS.md").write_text(CONTRACT_AGENTS_MD, encoding="utf-8")
    seed_commit(repo, bug_closeout_body(critique_line=f"Critique: {CRITIQUE_REL}"))


def _verify(repo: Path):
    return run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(repo),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "bug", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )


# --------------------------------------------------------------------------- #
# The three acceptance fixtures.
# --------------------------------------------------------------------------- #
def test_a_delegated_critique_passes_and_the_distinction_is_recorded(tmp_path: Path) -> None:
    _seed(tmp_path, satisfaction="parent-delegated", contract=True)

    result = _verify(tmp_path)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    observer = payload["resolution_critique_check"]["fresh_eye_observer"]
    assert observer["disposition"] == "delegated"
    assert observer["value"] == "parent-delegated"
    assert payload["review_advisory"] == []


def test_a_self_authored_critique_is_refused_at_the_close_boundary(tmp_path: Path) -> None:
    """The #386 same-observer rubber stamp, in the artifact's own words.

    `self-authored` is not one of the typed values the authoring-side validator
    accepts, so an artifact carrying it is a positive record that nobody else
    read the resolution. Refusing costs the author nothing they cannot honestly
    pay: run the review, or record `blocked <host-signal>`.
    """
    _seed(tmp_path, satisfaction="self-authored — I reviewed my own work", contract=True)

    result = _verify(tmp_path)

    payload = json.loads(result.stdout)
    assert payload["ok"] is False, "a self-authored critique must not satisfy the floor"
    check = payload["resolution_critique_check"]
    assert check["fresh_eye_observer"]["disposition"] == "undelegated"
    assert len(check["observer_refusals"]) == 1
    reason = check["observer_refusals"][0]["reason"]
    assert "neither a completed delegation" in reason
    assert "parent-delegated" in reason and "blocked <host-signal>" in reason


def test_a_blocked_critique_still_closes_but_says_so(tmp_path: Path) -> None:
    """The degradation valve, and the reason refusal is safe.

    A host that cannot spawn a reviewer is not stranded — it records the host
    signal and the close proceeds. What it does NOT get is silence.
    """
    _seed(tmp_path, satisfaction="blocked host-refused-subagent-spawn", contract=True)

    result = _verify(tmp_path)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True, "a blocked host must still be able to close"
    check = payload["resolution_critique_check"]
    assert check["fresh_eye_observer"]["disposition"] == "blocked"
    assert check["observer_refusals"] == []
    assert any("no distinct observer read this resolution" in line for line in payload["review_advisory"])


# --------------------------------------------------------------------------- #
# Portability: the two arms that decide whether this is a refusal at all.
# --------------------------------------------------------------------------- #
def test_a_repo_without_the_delegation_contract_is_not_refused(tmp_path: Path) -> None:
    """The discriminating control for the refusal above.

    Same artifact, same value, no `AGENTS.md` delegation contract. If this also
    refused, the floor would be holding every consuming repo to a convention it
    never adopted — and the refusal test above would prove only that a string was
    matched, not that the contract gate does anything.
    """
    _seed(tmp_path, satisfaction="self-authored — I reviewed my own work", contract=False)

    result = _verify(tmp_path)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    check = payload["resolution_critique_check"]
    # Recorded either way. The disposition is a fact about the artifact; only the
    # REFUSAL is a fact about the repo's contract.
    assert check["fresh_eye_observer"]["disposition"] == "undelegated"
    assert check["observer_refusals"] == []


def test_an_absent_field_is_refused_under_the_contract_and_silent_without_it(tmp_path: Path) -> None:
    """Omission must not be the cheapest bypass of all.

    The first version of this floor let absence pass everywhere, reasoning that
    `validate_critique_artifacts.py` already refuses an artifact with no
    `Fresh-eye satisfaction:` line. That validator runs at the COMMIT boundary and
    `close-with-comment` performs no commit — nothing orders it before the GitHub
    mutation — so the rationale was a floor on the wrong side of the boundary,
    which is the defect class this lane exists to close. Under the contract,
    absence refuses. Outside it, the field is a convention the repo never adopted
    and the floor stays silent AND passing.
    """
    contract_repo = tmp_path / "contract"
    plain_repo = tmp_path / "plain"
    contract_repo.mkdir()
    plain_repo.mkdir()
    _seed(contract_repo, satisfaction=None, contract=True)
    _seed(plain_repo, satisfaction=None, contract=False)

    under_contract = json.loads(_verify(contract_repo).stdout)
    without = json.loads(_verify(plain_repo).stdout)

    assert under_contract["ok"] is False, "omitting the line must not be a free pass"
    check = under_contract["resolution_critique_check"]
    assert check["fresh_eye_observer"]["disposition"] == "absent"
    assert "who read this resolution is unrecorded" in check["observer_refusals"][0]["reason"]

    assert without["ok"] is True, "a repo that never adopted the contract must still close"
    assert without["resolution_critique_check"]["observer_refusals"] == []
    assert without["review_advisory"] == [], (
        "an advisory that fires on every close in every non-adopting repo trains the "
        "reader to skip the word REVIEW before the blocked case that matters"
    )


def test_the_delegation_contract_is_live_in_this_repo(tmp_path: Path) -> None:
    """The test that would have caught the refusal being inert.

    The contract marker is matched against this repo's REAL `AGENTS.md`, which
    writes the sentence as `**already delegated**`. A plain substring test against
    the unbolded literal returned False, so every refusal above was dead here and
    every fixture passed anyway — because each fixture wrote its own synthetic
    `AGENTS.md` in a form the real file does not use.
    """
    observer = _load_observer()

    assert observer.repo_requires_delegated_observer(ROOT) is True
    assert observer.repo_requires_delegated_observer(tmp_path) is False


def test_the_historical_delegated_form_is_not_refused() -> None:
    """Ten checked-in artifacts record delegation as `satisfied — parent-delegated
    ...`, which no prefix test matches. Refusing them would land every ounce of
    this floor's cost on honest authors and none on the failure mode."""
    observer = _load_observer()

    result = observer.observer_disposition(
        "Fresh-eye satisfaction: satisfied — parent-delegated bounded review returned findings\n",
        strip_code_fences=_strip_code_fences,
    )

    assert result["disposition"] == "delegated"


def test_the_bold_bullet_form_is_read_rather_than_reported_as_missing() -> None:
    """Nine checked-in artifacts write `- **Fresh-Eye Satisfaction**: ...`.

    Reading it as absent would do two things: assert something false about an
    artifact just read, and hand any author a two-asterisk bypass of the refusal.
    """
    observer = _load_observer()

    assert observer.observer_disposition(
        "- **Fresh-Eye Satisfaction**: parent-delegated (repo contract)\n",
        strip_code_fences=_strip_code_fences,
    )["disposition"] == "delegated"
    assert observer.observer_disposition(
        "- **Fresh-Eye Satisfaction**: self-authored\n", strip_code_fences=_strip_code_fences
    )["disposition"] == "undelegated", "bolding the key must not defeat the refusal"


def test_a_bare_blocked_claims_the_valve_without_naming_anything() -> None:
    """The one-word escape. The refusal message tells authors to name the host
    signal; the cheapest way to comply must not be the word alone, or the
    blocking arm cannot stop the dishonest case while still stopping honest ones."""
    observer = _load_observer()

    assert observer.observer_disposition(
        "Fresh-eye satisfaction: blocked\n", strip_code_fences=_strip_code_fences
    )["disposition"] == "blocked-unsubstantiated"
    assert observer.observer_disposition(
        "Fresh-eye satisfaction: blocked host-refused-subagent-spawn-api-rejection\n",
        strip_code_fences=_strip_code_fences,
    )["disposition"] == "blocked"


def test_a_blocked_value_that_names_the_delegation_it_could_not_do_is_still_blocked() -> None:
    """Introduced by the repair for the historical-form over-block, caught by the
    second round.

    Matching delegated tokens by CONTAINMENT before testing `blocked` turned the
    valve's most natural phrasing — naming the spawn that failed — into a
    completed delegation. That silently dropped the advisory AND made the signal
    floor bypassable in 24 characters, cheaper than the bare `blocked` the floor
    had just been repaired to catch.
    """
    observer = _load_observer()

    assert observer.observer_disposition(
        "Fresh-eye satisfaction: blocked — the host rejected the parent-delegated spawn\n",
        strip_code_fences=_strip_code_fences,
    )["disposition"] == "blocked"
    assert observer.observer_disposition(
        "Fresh-eye satisfaction: blocked parent-delegated\n", strip_code_fences=_strip_code_fences
    )["disposition"] == "blocked-unsubstantiated", "the short-circuit must not skip the signal floor"


def test_a_value_that_denies_the_delegation_it_names_is_not_a_delegation() -> None:
    """Containment cannot tell "parent-delegated review returned findings" from
    "no parent-delegated review ran", and the second is what an honest author
    writes when none did."""
    observer = _load_observer()

    for denial in ("not parent-delegated", "no parent-delegated review ran"):
        assert observer.observer_disposition(
            f"Fresh-eye satisfaction: {denial}\n", strip_code_fences=_strip_code_fences
        )["disposition"] == "undelegated", denial

    # The other half of the same rule, and the reason it is a WINDOW rather than a
    # value-wide scan. Real records are prose that routinely says "no blockers"
    # and "not shipped" while recording a genuine delegation; scanning the whole
    # value for those words demoted eleven honest post-cutoff artifacts.
    assert observer.observer_disposition(
        "Fresh-eye satisfaction: parent-delegated. Round 2 returned no blockers and was not shipped.\n",
        strip_code_fences=_strip_code_fences,
    )["disposition"] == "delegated"


def test_a_section_whose_body_opens_with_prose_is_read_to_the_end() -> None:
    """Six checked-in artifacts open `## Fresh-Eye Satisfaction` with a prose
    verdict and put the typed value further down. Reading only the first line
    refused every one of them — the same over-block on honest authors that the
    inline form was already repaired once to avoid."""
    observer = _load_observer()
    text = (
        "## Fresh-Eye Satisfaction\n\n"
        "All three chunk reviewers ran in separate agent contexts and returned ship.\n"
        "parent-delegated\n\n"
        "## Next Section\n"
    )

    assert observer.observer_disposition(text, strip_code_fences=_strip_code_fences)[
        "disposition"
    ] == "delegated"


def test_a_deeper_heading_is_the_same_record() -> None:
    observer = _load_observer()

    assert observer.observer_disposition(
        "### Fresh-Eye Satisfaction\n\nparent-delegated\n", strip_code_fences=_strip_code_fences
    )["disposition"] == "delegated"


def test_an_unreadable_cited_artifact_is_typed_rather_than_treated_as_absent(tmp_path: Path) -> None:
    """A cited path that cannot be read is not a repo without the convention.

    Also pins that a non-UTF-8 artifact produces a disposition rather than a
    traceback: the binding library reads the same file with errors ignored, so a
    bad byte binds cleanly and only fails here.
    """
    _seed(tmp_path, satisfaction="parent-delegated", contract=True)
    (tmp_path / CRITIQUE_REL).write_bytes(b"Critique of the #42 resolution.\n\xff\xfe\nFresh-eye satisfaction: parent-delegated\n")

    result = _verify(tmp_path)

    payload = json.loads(result.stdout)
    assert payload["ok"] is True, "a decodable-with-replacement artifact must not crash the close"
    assert payload["resolution_critique_check"]["fresh_eye_observer"]["disposition"] == "delegated"


def test_a_tilde_fenced_example_is_not_read_as_the_claim() -> None:
    """`~~~` is a CommonMark fence the stripper did not know about, so a quoted
    example inside one was read as real content by every caller of it."""
    observer = _load_observer()
    text = (
        "Example:\n\n~~~\nFresh-eye satisfaction: parent-delegated\n~~~\n\n"
        "Fresh-eye satisfaction: self-authored\n"
    )

    assert observer.observer_disposition(text, strip_code_fences=_strip_code_fences)[
        "disposition"
    ] == "undelegated"


def test_the_corpus_this_refusal_would_actually_block_is_measured_with_its_denominator() -> None:
    """The measurement, stated with its denominator, that the refusal rests on.

    A blocking floor armed on an unmeasured population is how the previous
    arming in this repo went wrong. The number that matters is not "how many
    critique artifacts exist" — most are prepare packets and plan critiques that
    are never cited as issue-resolution evidence — but how many CITABLE
    resolution critiques this floor would refuse. Two earlier versions of this
    reader would have refused 11 and 6 of them respectively, both times for
    honest records; this pins that the answer is now zero, and fails loudly if a
    future edit re-opens either over-block.
    """
    observer = _load_observer()
    refused_dispositions = {"undelegated", "unreadable", "blocked-unsubstantiated", "absent"}
    citable = [
        path
        for path in sorted((ROOT / "charness-artifacts" / "critique").glob("*.md"))
        if not path.name.endswith("-packet.md")
        and ("resolution" in path.name or "issue" in path.name)
    ]
    would_refuse = []
    for path in citable:
        text = path.read_text(encoding="utf-8", errors="replace")
        disposition = observer.observer_disposition(text, strip_code_fences=_strip_code_fences)
        if disposition["disposition"] in refused_dispositions and not observer.predates_typed_contract(
            path, text
        ):
            would_refuse.append((path.name, disposition["disposition"], disposition["value"]))

    assert len(citable) > 100, f"denominator collapsed to {len(citable)}; the zero below would be vacuous"
    assert would_refuse == [], f"{len(would_refuse)} of {len(citable)} honest artifacts would be refused"


def test_a_pre_contract_artifact_is_reported_but_not_refused(tmp_path: Path) -> None:
    """Artifacts written before the typed contract existed record delegation in
    prose with no typed token anywhere. Refusing them applies a rule that did not
    exist when they were written — and the disposition is still REPORTED, so a
    grandfathered close is visibly grandfathered rather than silently clean."""
    _seed(tmp_path, satisfaction=None, contract=True)
    (tmp_path / CRITIQUE_REL).write_text(
        "# Res\n\nDate: 2026-06-05\n\n## Fresh-Eye Satisfaction\n\n"
        "All three chunk reviewers ran in separate agent contexts for #42.\n",
        encoding="utf-8",
    )

    payload = json.loads(_verify(tmp_path).stdout)

    check = payload["resolution_critique_check"]
    assert check["fresh_eye_observer"]["predates_typed_contract"] is True
    assert check["fresh_eye_observer"]["disposition"] == "undelegated", "still reported honestly"
    assert check["observer_refusals"] == [], "but not refused"
    assert payload["ok"] is True


def test_an_undatable_artifact_is_treated_as_current_not_grandfathered() -> None:
    """A NEW artifact carrying no date is itself the anomaly, so the safe default
    is enforcement — otherwise deleting the `Date:` line becomes the grandfather
    bypass."""
    observer = _load_observer()

    assert observer.predates_typed_contract(Path("res.md"), "no date anywhere\n") is False
    assert observer.predates_typed_contract(Path("2026-06-05-res.md"), "no date line\n") is True


def test_a_fence_is_closed_only_by_its_own_marker() -> None:
    """A `~~~` line inside a ``` block is content, not a close. Getting this wrong
    inverts the whole scan for any document that quotes one fence style in the
    other, which would flip content and commentary for every caller."""
    markdown = _load_markdown_lib()

    lines = markdown.strip_code_fences("a\n```\n~~~\nhidden\n```\nb\n")

    assert lines == ["a", "b"]


# --------------------------------------------------------------------------- #
# The close carrier's operator-facing message.
# --------------------------------------------------------------------------- #
def test_the_close_carrier_names_the_real_defect_not_the_generic_one(tmp_path: Path) -> None:
    """The `Critique:` line is PRESENT and valid on this path, so the pre-existing
    "add `Critique: <path>`" message would send the author to fix the one thing
    that is not wrong."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    write_argv_logging_fake(bin_dir, "gh", "GH_LOG", ["print('unreachable')"])
    critique = tmp_path / CRITIQUE_REL
    critique.parent.mkdir(parents=True, exist_ok=True)
    critique.write_text(
        "Critique of the #42 resolution.\n\nFresh-eye satisfaction: self-authored\n", encoding="utf-8"
    )
    (tmp_path / "AGENTS.md").write_text(CONTRACT_AGENTS_MD, encoding="utf-8")
    body = tmp_path / "body.md"
    body.write_text(bug_closeout_body(critique_line=f"Critique: {CRITIQUE_REL}"), encoding="utf-8")

    result = run_script(
        SCRIPT, "close-with-comment", "--repo", "corca-ai/charness", "--number", "42",
        "--body-file", str(body), "--classification", "bug", "--repo-root", str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_LOG": str(log)},
    )

    assert result.returncode != 0
    payload = json.loads(result.stdout)
    assert "is not a distinct observer" in payload["error"]
    assert "missing/invalid resolution-critique evidence" not in payload["error"]
    assert not log.exists(), "the refusal must land before any GitHub mutation"


# --------------------------------------------------------------------------- #
# Reading the field: the two traps the authoring-side reader already knows about.
# --------------------------------------------------------------------------- #
def test_the_canonical_section_wins_over_an_earlier_inline_mention() -> None:
    """An earlier sentence using the phrase must not shadow the real record below
    it — that is how the authoring-side consistency check was once disarmed while
    a human reader saw the contradiction plainly."""
    observer = _load_observer()
    text = (
        "## Decision Under Review\n\n"
        "Fresh-eye satisfaction: blocked something-that-is-not-the-record\n\n"
        "## Fresh-Eye Satisfaction\n\nparent-delegated\n"
    )

    assert observer.observer_disposition(text, strip_code_fences=_strip_code_fences) == {
        "value": "parent-delegated",
        "disposition": "delegated",
    }


def test_a_quoted_example_inside_a_fence_is_not_read_as_the_claim() -> None:
    observer = _load_observer()
    text = (
        "Example of what to write:\n\n```\nFresh-eye satisfaction: parent-delegated\n```\n\n"
        "Fresh-eye satisfaction: blocked host-refused-subagent-spawn\n"
    )

    result = observer.observer_disposition(text, strip_code_fences=_strip_code_fences)

    assert result["disposition"] == "blocked", "a fenced example is documentation, not a record"


def test_nested_delegation_counts_as_a_completed_delegation() -> None:
    """Keying only on the parent spelling would let the same false confidence
    through under the other typed value the scaffold offers as a co-equal choice."""
    observer = _load_observer()

    result = observer.observer_disposition(
        "Fresh-eye satisfaction: nested-delegated\n", strip_code_fences=_strip_code_fences
    )

    assert result["disposition"] == "delegated"


def test_leading_markup_does_not_defeat_the_typed_read() -> None:
    """`**self-authored**` is the unedited value wearing three characters of
    markup — how this class of surface has been defeated before."""
    observer = _load_observer()

    assert observer.observer_disposition(
        "Fresh-eye satisfaction: **self-authored**\n", strip_code_fences=_strip_code_fences
    )["disposition"] == "undelegated"
    assert observer.observer_disposition(
        "Fresh-eye satisfaction: `parent-delegated`\n", strip_code_fences=_strip_code_fences
    )["disposition"] == "delegated"
