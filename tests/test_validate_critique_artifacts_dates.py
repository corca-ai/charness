"""In-process coverage for the critique-artifact date fallbacks
(`scripts/review/validate_critique_artifacts.py`). ``tests/test_critique_artifact_validation.py``
and the ``quality_gates`` critique suites drive this module through the CLI helper,
so this file attributes the date-parsing lines directly
inside its date-parsing helpers. Both ``_date_from_filename`` and
``_date_from_body`` match a well-formed-looking date string with a regex and
then hand it to ``date.fromisoformat``, which can still reject an
out-of-range calendar date (e.g. month 13 or day 30 of February) -- the
``except ValueError: return None`` guard exists for exactly that gap between
"looked like a date" and "is a real date".
"""
from __future__ import annotations

from pathlib import Path

from tests.script_main import load_script_module

ROOT = Path(__file__).resolve().parents[1]
vca = load_script_module(
    "validate_critique_artifacts_dates_under_test",
    ROOT / "scripts" / "review" / "validate_critique_artifacts.py",
)


def test_date_from_filename_returns_none_on_regex_match_but_invalid_calendar_date() -> None:
    # "2026-13-40" matches \d{4}-\d{2}-\d{2} but month 13 / day 40 do not exist.
    path = Path("2026-13-40-demo-critique.md")
    assert vca._date_from_filename(path) is None


def test_date_from_filename_reads_valid_leading_date() -> None:
    path = Path("2026-06-12-demo-critique.md")
    assert vca._date_from_filename(path) == vca.date(2026, 6, 12)


def test_date_from_body_returns_none_on_regex_match_but_invalid_calendar_date() -> None:
    # "Date: 2026-02-30" matches the line pattern but February has no 30th.
    text = "# Critique Review\nDate: 2026-02-30\n"
    assert vca._date_from_body(text) is None


def test_date_from_body_reads_valid_date_line() -> None:
    text = "# Critique Review\nDate: 2026-06-12\n"
    assert vca._date_from_body(text) == vca.date(2026, 6, 12)


def test_check_finding_followup_refuses_a_malformed_value_whatever_the_action() -> None:
    """The `file-issue` arm has its own message; this is the OTHER arm.

    A finding that is not `file-issue` may omit `follow-up:` entirely — but a value
    that is PRESENT and unparseable (bare `deferred` with no anchor) is worse than
    absence: it reads to a human as a recorded deferral while pointing at nothing,
    so the item leaves the triage without an owner. Absence stays legal; malformed
    does not.
    """
    for action in ("act-before-ship", "bundle-anyway", "valid-but-defer", "over-worry"):
        finding = {"action": action, "follow-up": "deferred"}

        try:
            vca._check_finding_followup(finding, "F1", Path("demo.md"))
        except vca.ValidationError as exc:
            assert "malformed `follow-up:` value" in str(exc), action
        else:
            raise AssertionError(f"bare `deferred` accepted for action {action}")


def test_check_finding_followup_leaves_an_absent_or_parseable_value_alone() -> None:
    """The discriminating control: the refusal is about malformedness, not presence."""
    for followup in ({}, {"follow-up": ""}, {"follow-up": "deferred docs/index.md#next-session"}):
        vca._check_finding_followup({"action": "valid-but-defer", **followup}, "F2", Path("demo.md"))


def test_c6_worktree_scope_arms_the_cross_surface_tooth(tmp_path: Path, monkeypatch) -> None:
    """Audit row C6, at the scope resolver rather than only at the path helper.

    Two guards, both pinned below: an empty committed range resolves to zero paths
    and must report `not-established` rather than `evaluated (no match)`, and the
    flag-OFF, nothing-supplied case must still report `not-established` — the #408
    guard against "configured but handed nothing" reading as a clean miss.
    """
    scope = load_script_module(
        "critique_enforcement_scope_dates_under_test", ROOT / "scripts" / "review" / "critique_enforcement_scope.py"
    )
    probe = load_script_module(
        "boundary_probe_lib_dates_under_test",
        ROOT / "scripts" / "evidence" / "boundary_probe_lib.py",
    )

    class _Adapter:
        @staticmethod
        def load_adapter(_repo_root):
            return {"data": {"boundary_cross_surface_globs": ["scripts/*_lib.py"]}}

    # `resolve_hit` reads its OWN module-level adapter rather than the `adapter_lib`
    # handed to the scope resolver, so both have to be stubbed. Noted rather than
    # worked around silently: two adapter reads on one decision can disagree.
    monkeypatch.setattr(probe, "_critique_adapter_lib", _Adapter)
    monkeypatch.setattr(probe._surfaces_lib, "collect_changed_paths_for_ref", lambda r, ref: [])
    monkeypatch.setattr(
        probe._surfaces_lib, "collect_changed_paths", lambda r: ["scripts/adapters/surfaces_lib.py"]
    )

    committed_only = scope.resolve_cross_surface_scope(
        tmp_path, "HEAD..HEAD", None, probe_lib=probe, adapter_lib=_Adapter
    )
    with_worktree = scope.resolve_cross_surface_scope(
        tmp_path, "HEAD..HEAD", None, probe_lib=probe, adapter_lib=_Adapter, include_worktree=True
    )
    # The committed range resolved to NO paths, so it is `not-established`, not
    # `evaluated (no match)`. The state is decided by the resolved path list rather
    # than by which flags were passed -- reporting an evaluation over zero paths is
    # the "no hit is indistinguishable from never ran" defect this vocabulary kills,
    # and the first cut of `--include-worktree` reintroduced it.
    assert (committed_only.state, committed_only.overrides) == ("not-established", False)
    assert (with_worktree.state, with_worktree.overrides) == ("evaluated", True)

    nothing_supplied = scope.resolve_cross_surface_scope(
        tmp_path, None, None, probe_lib=probe, adapter_lib=_Adapter
    )
    assert nothing_supplied.state == "not-established"
    assert nothing_supplied.overrides is False


def test_an_empty_resolved_scope_is_not_established_even_with_the_flag(
    tmp_path: Path, monkeypatch
) -> None:
    """`--include-worktree` must not make `not-established` unreachable.

    `run-quality.sh` passes the flag unconditionally, so on a host with no
    `origin/main` base AND a clean tree the run resolves zero paths. The first cut
    reported that as `evaluated (no match)` -- an assertion of evaluation over
    nothing, in the module whose job is telling those two apart.

    The ref passed here is `""`, which is falsy, so the union branch is not the
    path executed -- `resolve_changed_paths` takes its early return and the empty
    set comes from the worktree read. That is the shape `run-quality.sh` actually
    produces on a base-less host, which is why it is the one pinned.
    """
    scope = load_script_module(
        "critique_enforcement_scope_dates_under_test", ROOT / "scripts" / "review" / "critique_enforcement_scope.py"
    )
    probe = load_script_module(
        "boundary_probe_lib_dates_under_test",
        ROOT / "scripts" / "evidence" / "boundary_probe_lib.py",
    )

    class _Adapter:
        @staticmethod
        def load_adapter(_repo_root):
            return {"data": {"boundary_cross_surface_globs": ["scripts/*_lib.py"]}}

    monkeypatch.setattr(probe, "_critique_adapter_lib", _Adapter)
    monkeypatch.setattr(probe._surfaces_lib, "collect_changed_paths_for_ref", lambda r, ref: [])
    monkeypatch.setattr(probe._surfaces_lib, "collect_changed_paths", lambda r: [])

    empty = scope.resolve_cross_surface_scope(
        tmp_path, "", None, probe_lib=probe, adapter_lib=_Adapter, include_worktree=True
    )
    assert empty.state == "not-established"
    assert empty.overrides is False


def test_the_empty_worktree_scope_note_states_its_real_cause() -> None:
    """The rendered note, not just the state.

    `not-established` is reached two ways now, and the generic text ("no
    --changed-ref/--changed-path resolved") is FALSE for the new one: a ref and
    the worktree were both supplied, the probe ran, and the union was empty.
    """
    scope = load_script_module(
        "critique_enforcement_scope_note_dates_under_test", ROOT / "scripts" / "review" / "critique_enforcement_scope.py"
    )

    empty_with_worktree = scope.CrossSurfaceScope(
        scope.CROSS_SURFACE_NOT_ESTABLISHED, False, 0, True, None
    )
    note = scope._cross_surface_note(empty_with_worktree)
    assert "resolved 0 path(s)" in note
    assert "nothing to probe" in note

    never_handed_a_scope = scope.CrossSurfaceScope(
        scope.CROSS_SURFACE_NOT_ESTABLISHED, False, 0, False, None
    )
    assert "no changed scope resolved" in scope._cross_surface_note(never_handed_a_scope)
