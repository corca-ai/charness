from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

from tests.script_main import load_script_module, run_loaded_script_main

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB_PATH = REPO_ROOT / "scripts/check_prescribed_skill_executed_lib.py"
CLI_PATH = REPO_ROOT / "scripts/check_prescribed_skill_executed.py"

_spec = importlib.util.spec_from_file_location("check_prescribed_skill_executed_lib", LIB_PATH)
lib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lib)
_CLI = load_script_module("check_prescribed_skill_executed_for_test", CLI_PATH)


def _run_cli(*args: str):
    return run_loaded_script_main(str(CLI_PATH), _CLI, *args)


def _touch(path: Path, body: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_satisfies_with_existing_evidence_files(tmp_path: Path) -> None:
    retro = tmp_path / "charness-artifacts/retro/2026-05-28-x.md"
    probe = tmp_path / "charness-artifacts/probe/2026-05-28-x.json"
    _touch(retro, "retro body")
    _touch(probe, "{}")
    result = lib.check(
        repo_root=tmp_path,
        required=["retro_artifact", "host_log_probe"],
        evidence={
            "retro_artifact": "charness-artifacts/retro/2026-05-28-x.md",
            "host_log_probe": "charness-artifacts/probe/2026-05-28-x.json",
        },
        skips={},
    )
    assert result["ok"] is True
    assert {entry["name"] for entry in result["satisfied"]} == {"retro_artifact", "host_log_probe"}
    assert result["missing"] == []
    assert result["missing_evidence_files"] == []


def test_missing_evidence_file_fails(tmp_path: Path) -> None:
    result = lib.check(
        repo_root=tmp_path,
        required=["retro_artifact"],
        evidence={"retro_artifact": "charness-artifacts/retro/missing.md"},
        skips={},
    )
    assert result["ok"] is False
    assert len(result["missing_evidence_files"]) == 1
    assert result["missing_evidence_files"][0]["name"] == "retro_artifact"


def test_empty_evidence_file_fails(tmp_path: Path) -> None:
    path = tmp_path / "charness-artifacts/retro/empty.md"
    _touch(path, "")
    result = lib.check(
        repo_root=tmp_path,
        required=["retro_artifact"],
        evidence={"retro_artifact": "charness-artifacts/retro/empty.md"},
        skips={},
    )
    assert result["ok"] is False
    assert result["missing_evidence_files"][0]["name"] == "retro_artifact"


def test_missing_name_with_neither_evidence_nor_skip_fails(tmp_path: Path) -> None:
    result = lib.check(
        repo_root=tmp_path,
        required=["resolution_critique"],
        evidence={},
        skips={},
    )
    assert result["ok"] is False
    assert result["missing"] == ["resolution_critique"]


def test_valid_skip_with_enum_prefix_passes(tmp_path: Path) -> None:
    skip = "host-log-not-exposed: claude session jsonl not under ~/.claude on this hostname"
    result = lib.check(
        repo_root=tmp_path,
        required=["host_log_probe"],
        evidence={},
        skips={"host_log_probe": skip},
    )
    assert result["ok"] is True
    assert result["skipped"][0]["reason"] == skip


def test_skip_without_enum_prefix_fails(tmp_path: Path) -> None:
    result = lib.check(
        repo_root=tmp_path,
        required=["resolution_critique"],
        evidence={},
        skips={"resolution_critique": "host limit prevented review"},
    )
    assert result["ok"] is False
    assert len(result["invalid_skips"]) == 1
    assert "must start with" in result["invalid_skips"][0]["detail"]


def test_skip_too_short_fails(tmp_path: Path) -> None:
    # Right enum prefix but no concrete detail; below the 40-char floor.
    result = lib.check(
        repo_root=tmp_path,
        required=["host_log_probe"],
        evidence={},
        skips={"host_log_probe": "host-log-not-exposed: nope"},
    )
    assert result["ok"] is False
    assert "too short" in result["invalid_skips"][0]["detail"]


def test_parse_evidence_arg_round_trips() -> None:
    assert lib.parse_evidence_arg("retro_artifact:foo/bar.md") == (
        "retro_artifact",
        "foo/bar.md",
    )
    with pytest.raises(ValueError):
        lib.parse_evidence_arg("no-colon")
    with pytest.raises(ValueError):
        lib.parse_evidence_arg("retro_artifact:")


def test_parse_skip_arg_round_trips() -> None:
    assert lib.parse_skip_arg("host_log_probe:host-log-not-exposed: claude code missing") == (
        "host_log_probe",
        "host-log-not-exposed: claude code missing",
    )
    with pytest.raises(ValueError):
        lib.parse_skip_arg("only-name")


def test_cli_smoke_fails_with_exit_one(tmp_path: Path) -> None:
    result = _run_cli(
        "--repo-root",
        str(tmp_path),
        "--require",
        "retro_artifact",
    )
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert payload["missing"] == ["retro_artifact"]


def test_cli_smoke_passes_with_real_file(tmp_path: Path) -> None:
    path = tmp_path / "charness-artifacts/retro/x.md"
    _touch(path, "retro body")
    result = _run_cli(
        "--repo-root",
        str(tmp_path),
        "--require",
        "retro_artifact",
        "--evidence",
        "retro_artifact:charness-artifacts/retro/x.md",
    )
    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True


def test_binding_passes_on_basename_token(tmp_path: Path) -> None:
    path = tmp_path / "charness-artifacts/retro/2026-05-28-230-229-closeout.md"
    _touch(path, "body that does not mention the goal")
    binds, reason = lib.evidence_binds_to_context(path, tokens=["230-229"])
    assert binds is True
    assert "basename" in reason


def test_binding_passes_on_content_token(tmp_path: Path) -> None:
    path = tmp_path / "charness-artifacts/retro/2026-05-28-unrelated.md"
    _touch(path, "this retro is about 230-229-self-substitution-pattern")
    binds, reason = lib.evidence_binds_to_context(
        path, tokens=["230-229-self-substitution-pattern"]
    )
    assert binds is True
    assert "content" in reason


def test_binding_fails_on_stale_unrelated_file(tmp_path: Path) -> None:
    # The #233 F1 attack: a present, non-empty, but unrelated pre-existing file.
    path = tmp_path / "charness-artifacts/retro/2026-04-10-some-old.md"
    _touch(path, "an old retro from a different goal entirely")
    binds, reason = lib.evidence_binds_to_context(
        path, tokens=["230-229-self-substitution-pattern", "230-229"]
    )
    assert binds is False
    assert "does not bind" in reason


def test_binding_opts_out_with_no_tokens(tmp_path: Path) -> None:
    path = tmp_path / "charness-artifacts/retro/anything.md"
    _touch(path, "body")
    binds, _ = lib.evidence_binds_to_context(path, tokens=[])
    assert binds is True


def test_binding_numeric_token_does_not_false_match_digit_run(tmp_path: Path) -> None:
    # F-C: `185` must not bind on `21850` / `0185abc` (unanchored substring).
    path = tmp_path / "charness-artifacts/retro/2026-05-28-unrelated.md"
    _touch(path, "this body mentions 21850 and 0185abc but not the issue")
    binds, _ = lib.evidence_binds_to_context(path, tokens=["185"])
    assert binds is False


def test_binding_numeric_token_matches_on_boundary(tmp_path: Path) -> None:
    path = tmp_path / "charness-artifacts/retro/2026-05-28-185-foo.md"
    _touch(path, "body")
    binds, reason = lib.evidence_binds_to_context(path, tokens=["185"])
    assert binds is True
    assert "185" in reason


def test_skip_detail_floor_is_not_paid_by_the_enum_head(tmp_path: Path) -> None:
    """B2 regression: the length floor must measure the skip DETAIL, not the
    whole reason.

    Callers such as `issue_resolution_critique` and `publish_release_preflight`
    manufacture the enum head themselves from an author shorthand, so the enum
    check validates a constant the caller supplied and only the length floor
    survives. `host-blocked-subagent: ` is 23 characters, so a 40-char total
    floor accepted a 17-character signal and closed a real GitHub issue with a
    fresh-eye critique that never ran."""
    head = "host-blocked-subagent: "
    assert len(head) == 23
    # The confirmed B2 cliff: 17 characters of author-written signal used to pass
    # because the 23-character head paid down the rest of the 40-char total.
    result = lib.check(
        repo_root=tmp_path,
        required=["resolution_critique"],
        evidence={},
        skips={"resolution_critique": head + "x" * 17},
    )
    assert result["ok"] is False
    assert "skip detail too short" in result["invalid_skips"][0]["detail"]
    # Control: exactly MIN_SKIP_DETAIL_LENGTH of author text passes, so the floor
    # is genuinely a detail floor and not a longer total floor in disguise.
    result = lib.check(
        repo_root=tmp_path,
        required=["resolution_critique"],
        evidence={},
        skips={"resolution_critique": head + "x" * lib.MIN_SKIP_DETAIL_LENGTH},
    )
    assert result["ok"] is True


def test_skip_detail_floor_does_not_re_baseline_honest_host_signals(tmp_path: Path) -> None:
    """Restraint control for the floor above: it must refuse terseness without
    sitting above observed honest usage.

    The repo's own genuine skip details run 24-39 characters, so a floor set at
    the 40-char *total* value would have rejected real recorded host signals and
    bought padding rather than signal. These are verbatim details from checked-in
    goal closeouts and fixtures; every one must still pass."""
    for detail in (
        "claude jsonl unavailable",
        "no codex rollout file in this env",
        "claude jsonl path missing on this host",
        "report writing is still possible",
        "no host token/time/session-log",
    ):
        result = lib.check(
            repo_root=tmp_path,
            required=["host_log_probe"],
            evidence={},
            skips={"host_log_probe": f"host-log-not-exposed: {detail}"},
        )
        assert result["ok"] is True, (detail, len(detail), result["invalid_skips"])


def test_repeated_enum_head_does_not_fund_the_skip_detail_floor(tmp_path: Path) -> None:
    """The manufactured-constant hole one level down: a caller prepending the
    enum head to an author shorthand that itself begins with an enum head must
    not let the duplicated head pay for the detail floor."""
    # Discriminating by construction: after stripping only the FIRST head the
    # detail is 41 chars and clears the floor, so this passes with the repeated-
    # head loop removed. Only stripping both heads leaves the 18-char detail that
    # the floor refuses.
    reason = "host-blocked-subagent: host-blocked-subagent: " + "x" * 18
    assert len(reason.partition(":")[2].strip()) > lib.MIN_SKIP_DETAIL_LENGTH
    result = lib.check(
        repo_root=tmp_path,
        required=["resolution_critique"],
        evidence={},
        skips={"resolution_critique": reason},
    )
    assert result["ok"] is False
    assert "skip detail too short" in result["invalid_skips"][0]["detail"]


def test_blocked_signal_floor_is_read_live_and_omitted_when_unreachable() -> None:
    """The author-facing shape describer reads the skip-detail floor from the
    owning library rather than restating it, so the number it prints cannot drift
    from the gate the way it did when the floor moved. When the shared helper is
    not resolvable — an installed copy, a partial vendor — it must return None so
    the describer omits the number; inventing one, or crashing the describer, are
    both worse than saying nothing."""
    critique_spec = importlib.util.spec_from_file_location(
        "issue_resolution_critique_floor",
        REPO_ROOT / "skills/public/issue/scripts/issue_resolution_critique.py",
    )
    critique = importlib.util.module_from_spec(critique_spec)
    critique_spec.loader.exec_module(critique)

    assert critique.min_blocked_signal_length() == lib.MIN_SKIP_DETAIL_LENGTH

    def _unreachable():
        raise ImportError("shared helper not resolvable from this copy")

    critique._load_shared_helper = _unreachable
    assert critique.min_blocked_signal_length() is None


def test_binding_bare_number_refuses_date_time_and_version_digit_runs(tmp_path: Path) -> None:
    """B4 regression: a bare issue number must not bind on any standalone digit
    run. A critique of a *different* issue bound a #27 closeout purely through
    its ``Date: 2026-07-27`` header, and ``v0.42.1`` / ``14:32:05`` bound
    #42 / #32 — a mandatory fresh-eye critique satisfied by an unrelated file at
    an irreversible boundary (issue close)."""
    path = tmp_path / "charness-artifacts/critique/unrelated-packet.md"
    _touch(
        path,
        "# Resolution Critique - #999\n\nIssue: #999\nDate: 2026-07-27\n"
        "Built v0.42.1 at 14:32:05; 63 files changed.\n",
    )
    for token in ("27", "2026", "42", "32", "63"):
        binds, reason = lib.evidence_binds_to_context(path, tokens=[token])
        assert binds is False, f"{token} falsely bound: {reason}"
    # Control: the issue this critique actually names still binds.
    binds, reason = lib.evidence_binds_to_context(path, tokens=["999"])
    assert binds is True
    assert "999" in reason


@pytest.mark.parametrize(
    "body",
    [
        "# Resolution Critique - #367\n\nIssue: #367\n",
        "Target: issue #184\n",
        "Angle 1 ... Closes #349 on push.\n",
        "Resolution diff for corca-ai/charness#429\n",
        "see https://github.com/corca-ai/charness/issues/430 for the thread\n",
        "issue 161 resolution critique\n",
        "gh-282 closeout critique\n",
    ],
)
def test_binding_bare_number_still_binds_the_forms_this_repo_writes(
    tmp_path: Path, body: str
) -> None:
    """False-refusal control for B4: every citation form found in the repo's real
    checked-in critique artifacts must still bind, otherwise the fix degenerates
    into a gate that always refuses."""
    number = body.split("#")[-1][:3] if "#" in body else "".join(c for c in body if c.isdigit())[:3]
    path = tmp_path / "charness-artifacts/critique/2026-05-14-packet.md"
    _touch(path, body)
    binds, reason = lib.evidence_binds_to_context(path, tokens=[number])
    assert binds is True, f"{number!r} refused for {body!r}: {reason}"


def test_binding_basename_date_run_does_not_bind_a_bare_number(tmp_path: Path) -> None:
    """The same B4 hole through the basename: a timestamped artifact name binds
    #2026 / #14 / #13911 for free."""
    path = tmp_path / "charness-artifacts/critique/2026-05-14-013911-packet.md"
    _touch(path, "an unrelated packet body")
    for token in ("2026", "14", "5"):
        binds, reason = lib.evidence_binds_to_context(path, tokens=[token])
        assert binds is False, f"{token} falsely bound: {reason}"
    # Control: a real identity segment in the basename still binds.
    named = tmp_path / "charness-artifacts/critique/2026-05-14-issue-161-packet.md"
    _touch(named, "body")
    binds, _ = lib.evidence_binds_to_context(named, tokens=["161"])
    assert binds is True


def test_issue_resolution_critique_refuses_a_date_bound_unrelated_critique(
    tmp_path: Path,
) -> None:
    """End-to-end at the gate that closes GitHub issues: the closeout must not be
    satisfiable by a critique of a different issue, and must still pass when the
    critique names the issue under close."""
    critique_spec = importlib.util.spec_from_file_location(
        "issue_resolution_critique_binding",
        REPO_ROOT / "skills/public/issue/scripts/issue_resolution_critique.py",
    )
    critique = importlib.util.module_from_spec(critique_spec)
    critique_spec.loader.exec_module(critique)

    unrelated = tmp_path / "charness-artifacts/critique/unrelated-packet.md"
    _touch(unrelated, "# Resolution Critique - #999\n\nIssue: #999\nDate: 2026-07-27\n")
    report = critique.check_resolution_critique(
        repo_root=tmp_path,
        body="Critique: charness-artifacts/critique/unrelated-packet.md",
        classification="bug",
        numbers=[27],
    )
    assert report["ok"] is False
    assert report["binding_failures"]
    assert report["missing_issue_bindings"] == [27]

    # Control: the critique that actually names #27 binds and the closeout passes.
    real = tmp_path / "charness-artifacts/critique/real-packet.md"
    _touch(real, "# Resolution Critique - #27\n\nIssue: #27\nDate: 2026-07-27\n")
    ok_report = critique.check_resolution_critique(
        repo_root=tmp_path,
        body="Critique: charness-artifacts/critique/real-packet.md",
        classification="bug",
        numbers=[27],
    )
    assert ok_report["ok"] is True, ok_report
    assert not ok_report["binding_failures"]


def test_a_timestamp_shaped_token_is_not_masked_away_by_the_date_mask(tmp_path: Path) -> None:
    """The basename date-mask exists so `2026-05-14-013911-packet.md` cannot bind
    #2026 or #14. A token that IS the timestamp-shaped run must survive it, or the
    mask would erase the very identity it was asked about.
    """
    assert lib._token_matches("013911", "2026-05-14-013911-packet.md", in_name=True) is True
    assert lib._token_matches("2026", "2026-05-14-013911-packet.md", in_name=True) is False


def test_check_binds_evidence_when_tokens_are_supplied(tmp_path: Path) -> None:
    """S4, parent-reproduced: `evidence_binds_to_context` was defined but `check()`
    never called it.

    Binding therefore held only where `achieve` and `issue` wired the predicate by
    hand, and nowhere else — the generic CLI and the release publish gate carried
    none at all. Reproduced before the fix: a real critique about an unrelated
    2026-07-27 topic satisfied an `issue-resolution` closeout for #466.
    """
    unrelated = tmp_path / "charness-artifacts/critique/2026-07-27-a3-staged-scope.md"
    _touch(unrelated, "# A3 staged scope\n\nNothing to do with the closeout at hand.\n")

    report = lib.check(
        repo_root=tmp_path,
        required=["resolution_critique"],
        evidence={
            "resolution_critique": "charness-artifacts/critique/2026-07-27-a3-staged-scope.md"
        },
        skips={},
        kind="issue-resolution",
        tokens=["466"],
    )
    assert report["ok"] is False, report
    assert [item["name"] for item in report["unbound_evidence"]] == ["resolution_critique"]
    assert report["binding_checked"] is True

    # Control: a critique that cites the issue satisfies the same call.
    bound = tmp_path / "charness-artifacts/critique/2026-07-31-closeout.md"
    _touch(bound, "# Closeout critique\n\nIssue: #466\n")
    ok_report = lib.check(
        repo_root=tmp_path,
        required=["resolution_critique"],
        evidence={"resolution_critique": "charness-artifacts/critique/2026-07-31-closeout.md"},
        skips={},
        kind="issue-resolution",
        tokens=["466"],
    )
    assert ok_report["ok"] is True, ok_report
    assert "content contains" in ok_report["satisfied"][0]["binding"]


def test_presence_only_runs_report_that_they_are_presence_only(tmp_path: Path) -> None:
    """No tokens is still allowed — some callers cannot derive an identity — but a
    consumer reading `ok: true` must be able to tell a bound pass from an unbound
    one. Before this the two were indistinguishable in the report."""
    path = tmp_path / "charness-artifacts/critique/anything.md"
    _touch(path, "# Anything\n")
    report = lib.check(
        repo_root=tmp_path,
        required=["standalone_critique"],
        evidence={"standalone_critique": "charness-artifacts/critique/anything.md"},
        skips={},
    )
    assert report["ok"] is True
    assert report["binding_checked"] is False
    assert report["binding_tokens"] == []
    assert report["satisfied"][0]["binding"] == "not-checked"


def test_a_stub_that_cites_its_context_is_refused(tmp_path: Path) -> None:
    """Sweep row S3's stub half, CLOSED -- this was a checked-in xfail.

    `printf '#466' > x.md` is four bytes and binds by CONTENT, because its content
    IS the token. Two floors were written for this and both withdrawn: a
    basename-only one left the cheaper content channel open, and a universal
    200-byte one was still defeated by filler while failing 34 existing tests.

    The rule that closed it is not a size number: evidence must say something
    BEYOND the identity it was checked against. Measured before it was written,
    by a checked-in script (`scripts/measure_evidence_residual.py`) rather than a
    comment: the stub's residual is 0, markdown artifacts floor at 337 over 2168
    files, and real JSON host-log probes at 530 over 83. The floor sits at 8,
    below every measured minimum rather than between two of them.

    It broke no existing ASSERTION, and it did break four degenerate FIXTURES
    (12-byte shapes like `{"goal":"g"}`), which were rewritten to be realistic.
    Recorded plainly, because the previous withdrawal of this floor rested on the
    mirror-image elision -- counting fixtures as if they were evidence.

    What it does not close: a few characters of filler still passes. This refuses
    a stub, not a lie.
    """
    stub = tmp_path / "charness-artifacts/critique/one-byte.md"
    _touch(stub, "#466")
    report = lib.check(
        repo_root=tmp_path,
        required=["standalone_critique"],
        evidence={"standalone_critique": str(stub)},
        skips={},
        tokens=["466"],
    )
    assert stub.stat().st_size == 4
    assert report["ok"] is False
    assert report["satisfied"] == []
    assert [item["name"] for item in report["stub_evidence"]] == ["standalone_critique"]
    assert report["stub_evidence"][0]["residual_chars"] == 0
    assert report["residual_checked"] is True


def test_a_real_artifact_that_binds_is_still_accepted(tmp_path: Path) -> None:
    """The discriminating control for the refusal above.

    Same token, same binding channel, same path -- only the artifact is real. If
    this ever goes red the floor has become bar-moving, which is what withdrew the
    two previous attempts.
    """
    artifact = tmp_path / "charness-artifacts/critique/2026-07-31-real.md"
    _touch(
        artifact,
        "# Critique: issue #466\n\n"
        "Angle one: the accept path took file presence for the executed skill.\n"
        "Angle two: the binding token and the artifact body were the same string.\n",
    )
    report = lib.check(
        repo_root=tmp_path,
        required=["standalone_critique"],
        evidence={"standalone_critique": str(artifact)},
        skips={},
        tokens=["466"],
    )
    assert report["ok"] is True
    assert report["stub_evidence"] == []
    assert report["satisfied"][0]["residual_chars"] >= lib.MIN_BOUND_RESIDUAL_CHARS


def test_the_residual_floor_does_not_run_without_any_identity(tmp_path: Path) -> None:
    """A caller that can derive NO identity sees no change in bar, and the report says so.

    Not "the floor runs only where binding runs" -- that was true of the first cut
    and is not true now: `residual_tokens=` runs the floor on the presence-only
    branch for the two wrappers that bind out-of-band. The surviving invariant is
    narrower: with no tokens of either kind there is nothing to remove, so the
    floor is inert and `residual_checked` says so.
    """
    stub = tmp_path / "charness-artifacts/critique/one-byte.md"
    _touch(stub, "#466")
    report = lib.check(
        repo_root=tmp_path,
        required=["standalone_critique"],
        evidence={"standalone_critique": str(stub)},
        skips={},
    )
    assert report["ok"] is True
    assert report["residual_checked"] is False
    assert report["satisfied"][0]["binding"] == "not-checked"


def test_residual_tokens_run_the_floor_on_the_presence_only_branch(tmp_path: Path) -> None:
    """The new path, pinned at the library rather than only through a wrapper.

    `residual_tokens` supplies identity for the stub floor without binding, which
    is what lets the issue and achieve gates keep their own binding rules.
    """
    stub = tmp_path / "charness-artifacts/critique/one-byte.md"
    _touch(stub, "#466")
    report = lib.check(
        repo_root=tmp_path,
        required=["standalone_critique"],
        evidence={"standalone_critique": str(stub)},
        skips={},
        residual_tokens=["466"],
    )
    assert report["ok"] is False
    assert report["binding_checked"] is False, "binding must stay untouched"
    assert report["residual_checked"] is True
    assert report["stub_evidence"][0]["residual_chars"] == 0


def test_an_overlapping_token_leaves_no_counting_fragment(tmp_path: Path) -> None:
    """Longest-token-first removal, so `466` inside `issue-466` cannot leave `issue-`
    behind as content when both are binding tokens."""
    stub = tmp_path / "charness-artifacts/critique/issue-466.md"
    _touch(stub, "issue-466")
    report = lib.check(
        repo_root=tmp_path,
        required=["standalone_critique"],
        evidence={"standalone_critique": str(stub)},
        skips={},
        tokens=["466", "issue-466"],
    )
    assert report["ok"] is False
    assert report["stub_evidence"][0]["residual_chars"] == 0


def test_a_dotted_version_token_is_boundary_matched(tmp_path: Path) -> None:
    """A release version is not a slug. `_token_matches` fell through to plain
    substring containment for anything that was not a hyphen/underscore numeric
    cluster, so `2.12.0` bound a critique that merely mentioned a dependency at
    `12.12.0` — and that critique then satisfied the mandatory release gate."""
    assert lib._token_matches("2.12.0", "bumped the dep to 12.12.0 today") is False
    assert lib._token_matches("2.12.0", "pinned 2.12.01 in the lockfile") is False
    assert lib._token_matches("1.0.0", "node 21.0.0 required") is False
    assert lib._token_matches("2.12.0", "publishing charness 2.12.0 now") is True
    # The hyphenated spelling keeps working: both are real in this repo.
    assert lib._token_matches("2-12-0", "v2-12-0-release-critique.md") is True


def test_a_v_prefix_is_admitted_for_versions_and_refused_for_bare_issue_numbers() -> None:
    """The `v` in `v2.12.0` has to be admitted or the release gate refuses this
    repo's own artifact naming. Admitting it for EVERY token — which the first
    version of this did — let a bare issue number bind the leading segment of a
    version-named artifact: token `2` matched the checked-in
    `v2-1-4-release-packet.md`, so closing issue #2 could be satisfied by an
    unrelated release packet.
    """
    assert lib._token_matches("2-12-0", "v2-12-0-release-critique.md") is True
    assert lib._token_matches("2.12.0", "2026-07-29-v2.12.0-release.md") is True
    assert lib._token_matches("2", "v2-1-4-release-packet.md", in_name=True) is False
    # The `v` still has to sit on a boundary of its own.
    assert lib._token_matches("2.12.0", "rev2.12.0x") is False


def test_the_residual_floor_reaches_the_issue_close_gate(tmp_path: Path) -> None:
    """The motivating case, at the gate it actually lives on.

    The floor was in the library and this gate never reached it: the
    resolution-critique wrapper binds per ISSUE NUMBER out-of-band and supplies no
    `tokens=`, so a four-byte `#466` file still closed issue #466 with the floor
    shipped. `residual_tokens=` wires the per-file question in without weakening
    the per-issue binding rule.
    """
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills/public/issue/scripts"))
    import issue_resolution_critique as irc

    stub = tmp_path / "charness-artifacts/critique/x.md"
    _touch(stub, "#466")
    body = "Close #466\n\nCritique: charness-artifacts/critique/x.md\n"
    report = irc.check_resolution_critique(
        repo_root=tmp_path, body=body, classification="bug", numbers=[466]
    )
    assert report["ok"] is False
    assert report["residual_checked"] is True
    assert [entry["name"] for entry in report["stub_evidence"]] == ["resolution_critique"]


def test_a_real_resolution_critique_still_closes_its_issue(tmp_path: Path) -> None:
    """Discriminating control for the refusal above: same gate, same token, real file."""
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills/public/issue/scripts"))
    import issue_resolution_critique as irc

    real = tmp_path / "charness-artifacts/critique/2026-08-01-real.md"
    _touch(
        real,
        "# Resolution critique for #466\n\n"
        "Angle one: the accept path took file presence for skill execution.\n"
        "Angle two: the binding token and the artifact body were the same string.\n",
    )
    body = "Close #466\n\nCritique: charness-artifacts/critique/2026-08-01-real.md\n"
    report = irc.check_resolution_critique(
        repo_root=tmp_path, body=body, classification="bug", numbers=[466]
    )
    assert report["ok"] is True
    assert report["stub_evidence"] == []


def test_an_unreadable_evidence_file_is_not_diagnosed_as_a_stub(tmp_path: Path) -> None:
    """Read failure and stub-ness are different facts.

    A file that bound by BASENAME but whose content cannot be read would score
    residual 0 and be reported as saying nothing — a wrong diagnosis at a refusal
    an operator has to act on.
    """
    artifact = tmp_path / "charness-artifacts/critique/2026-08-01-466-real.md"
    _touch(artifact, "# Critique\n\nA real body that the gate will not be able to read.\n")
    artifact.chmod(0o000)
    try:
        report = lib.check(
            repo_root=tmp_path,
            required=["standalone_critique"],
            evidence={"standalone_critique": str(artifact)},
            skips={},
            tokens=["466"],
        )
        if report["satisfied"]:  # root can read anything; skip the assertion there
            assert report["ok"] is True
            assert report["stub_evidence"] == []
            assert report["satisfied"][0]["residual_chars"] is None
    finally:
        artifact.chmod(0o644)
