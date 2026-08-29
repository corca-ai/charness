"""A version this reader cannot speak must REFUSE, never quietly fall back to defaults.

The producer half of the contract -- a refused version honors no declared field -- is
pinned in `test_adapter_version_reconciliation.py`. That containment is what makes this
file necessary: once nothing declared is honored, every surface that resolves scope, a
ceiling, or a write path from an adapter is resolving it from a CHARNESS default, and
the surfaces here deliberately do not key on the payload's `valid` flag.

Both regressions below were measured on the real CLIs before the guard existed, not
imagined:

* `validate_retro_artifact.py --paths docs/retros/<x>.md` against an adapter declaring
  `version: 9` + `output_dir: docs/retros` printed `Validated 0 retro artifact(s).` and
  exited 0 -- over an artifact it had been handed by name.
* `validate_debug_artifact.py --all` against `version: 9` + `max_artifact_lines: 60`
  enforced the shipped 180 instead, so a 151-line artifact that the declared ceiling
  refused passed clean.

Blind class: these prove the five guarded surfaces refuse and say why. They prove nothing
about a surface that never calls the guard -- the scaffolds and run planners still
forecast a default ceiling under a refused version, which is a weaker wrong answer than
a gate's, but not no answer -- and nothing about any adapter error other than the
version.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ADAPTER_LIB, ROOT

VERDICT = load_script_module("adapter_version_verdict", ROOT / "scripts/adapter_version_verdict.py")


class _Raised:
    """A refusal a surface raises out of `main()` rather than printing.

    Two of the five surfaces do that by their own existing contract -- gather's writer
    routes every `WriteError` through its `__main__` handler, and this harness calls
    `main()` directly. Normalising here rather than special-casing the assertions keeps
    "refused, with this message, non-zero" one question across all five; the alternative
    was a subprocess boundary for two rows and an in-process call for four, which would
    have measured two different things and called them the same test.
    """

    def __init__(self, exc: BaseException) -> None:
        self.returncode = 1
        self.stdout = ""
        self.stderr = str(exc)


def run_main(rel_path: str, *args: str):
    module = load_script_module(Path(rel_path).stem, ROOT / rel_path)
    try:
        return run_loaded_script_main(rel_path, module, *args)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - see `_Raised`
        return _Raised(exc)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seeded_repo(tmp_path: Path, version: str) -> Path:
    """One repo declaring every adapter these surfaces read, at ``version``.

    Every adapter names a NON-default `output_dir`, because that is what makes the
    fallback observable: with the shipped default declared, "honored the repo's value"
    and "fell back to ours" render identically and the fixture would prove nothing.
    """
    repo = tmp_path / "repo"
    for name, output_dir in (
        ("debug", "docs/debugging"),
        ("retro", "docs/retros"),
        ("quality", "docs/quality"),
        ("gather", "docs/gathered"),
    ):
        _write(
            repo / ".agents" / f"{name}-adapter.yaml",
            f"version: {version}\nrepo: demo\noutput_dir: {output_dir}\n",
        )
    _write(repo / "docs/retros/2026-08-18-probe.md", "# Session Retro\n\nbody\n")
    _write(repo / "docs/debugging/latest.md", "# Debug Review\n\nbody\n")
    _write(repo / "docs/quality/latest.md", "# Quality Review\n\nbody\n")
    _write(repo / "body.md", "# Session Retro\n\nbody\n")
    return repo


# `(label, rel_path, args_fn)`. Driven through each surface's own `main()` with its own
# argv, because the guard's whole point is where it sits in that entrypoint's order --
# calling the helper directly would pass on a surface that never wired it in.
SURFACES = (
    ("debug_gate", "scripts/validate_debug_artifact.py", lambda repo: ("--repo-root", str(repo), "--all")),
    (
        "retro_gate",
        "scripts/validate_retro_artifact.py",
        lambda repo: ("--repo-root", str(repo), "--paths", "docs/retros/2026-08-18-probe.md"),
    ),
    ("quality_gate", "scripts/validate_quality_artifact.py", lambda repo: ("--repo-root", str(repo))),
    (
        "gather_writer",
        "skills/public/gather/scripts/write_record.py",
        lambda repo: ("--repo-root", str(repo), "--slug", "probe", "--content-file", str(repo / "body.md")),
    ),
    (
        "retro_writer",
        "skills/public/retro/scripts/persist_retro_artifact.py",
        lambda repo: (
            "--repo-root", str(repo), "--artifact-name", "2026-08-18-probe",
            "--markdown-file", str(repo / "body.md"),
        ),
    ),
    # Round-2 review found these two, and the first was measured before it was guarded:
    # `refresh_recent_lessons` wrote a SHADOW digest and selection index into
    # `charness-artifacts/retro/` while the repo's declared digest stayed untouched, and
    # reported the shadow path at exit 0. It is the explicit repair entrypoint,
    # so the operator is sent there precisely when the adapter is what is wrong.
    (
        "lessons_digest_writer",
        "skills/public/retro/scripts/refresh_recent_lessons.py",
        lambda repo: ("--repo-root", str(repo)),
    ),
    (
        "current_pointer_writer",
        "scripts/refresh_current_pointer.py",
        lambda repo: (
            "--repo-root", str(repo), "--skill-id", "retro",
            "--record-artifact-path", "docs/retros/2026-08-18-probe.md",
        ),
    ),
)


@pytest.mark.parametrize(("label", "rel_path", "args_fn"), SURFACES, ids=[row[0] for row in SURFACES])
def test_an_unspeakable_version_refuses_loudly(label, rel_path, args_fn, tmp_path) -> None:
    repo = _seeded_repo(tmp_path, "9")

    result = run_main(rel_path, *args_fn(repo))

    assert result.returncode != 0, f"{label} did not refuse: {result.stdout}"
    combined = result.stdout + result.stderr
    assert "version" in combined, f"{label} refused without naming the version: {combined}"
    # The refusal must be diagnosable. Naming the field alone would leave the operator
    # reading a message about a directory or a ceiling and editing the wrong line.
    assert "does not speak" in combined, f"{label} refusal does not name the cause: {combined}"
    # And it must not read as a pass. `Validated 0 <label>(s).` was the measured
    # fail-quiet, and it is a SUCCESS string -- a run that still prints it has not been
    # repaired, only made noisier.
    assert "Validated 0" not in combined, f"{label} still reports a vacuous pass: {combined}"


@pytest.mark.parametrize(("label", "rel_path", "args_fn"), SURFACES, ids=[row[0] for row in SURFACES])
def test_a_parser_refusal_refuses_just_as_loudly_at_every_surface(
    label, rel_path, args_fn, tmp_path
) -> None:
    """The second door, driven through every surface's own `main()` — which is what the
    first cut of this repair did NOT do.

    Round 1 of the slice-5 review found the consumer guards keyed on the wording of one
    check rather than on the condition. The repair widened the shared helper and added a
    predicate-level test, and round 2 found that test could not see the defect it was
    written for: three consumers ask the predicate DIRECTLY and were still on the narrow
    one. `version: !!int 9` beside a declared `output_dir: docs/gathered` wrote both the
    dated record and `latest.md` under `charness-artifacts/gather`, `status: updated`,
    exit 0 — a durable write to a directory the repo never named, while `version: 9` in
    the same repo refused.

    Parameterizing the EXISTING surface table is the fix that could not have been faked:
    it is the same eight entrypoints, the same `main()`, one token different in the
    fixture.
    """
    repo = _seeded_repo(tmp_path, "!!int 9")

    result = run_main(rel_path, *args_fn(repo))

    assert result.returncode != 0, f"{label} did not refuse: {result.stdout}"
    combined = result.stdout + result.stderr
    # Two shapes are acceptable and both are refusals. Seven surfaces route through a
    # resolver that CATCHES the parse failure and records it in `errors`, so they render
    # this module's `could not be parsed` refusal. `quality_gate` reaches a loader that
    # lets the `ValueError` out, so it refuses with the parser's own
    # `unsupported YAML construct` text. What matters is the same for both: non-zero, the
    # parse problem named, and no vacuous pass.
    assert (
        "could not be parsed" in combined or "unsupported YAML construct" in combined
    ), f"{label} refusal does not name the cause: {combined}"
    # The instruction must match the door. Sending an operator to edit `version:` in a
    # document the parser never read is the wrong repair, and is what every one of these
    # surfaces said before round 2.
    assert "does not speak" not in combined, f"{label} sends the operator to the wrong line: {combined}"
    assert "Validated 0" not in combined, f"{label} still reports a vacuous pass: {combined}"


@pytest.mark.parametrize(("label", "rel_path", "args_fn"), SURFACES, ids=[row[0] for row in SURFACES])
def test_a_speakable_version_is_not_refused_for_its_version(label, rel_path, args_fn, tmp_path) -> None:
    """The polarity control. Every assertion above is satisfied by a surface that refuses
    EVERYTHING, so each must be shown not to fire on the supported version. The surfaces
    may still fail here on artifact shape -- these fixtures are deliberately minimal
    stubs -- so the assertion is on the version refusal specifically, never on exit 0."""
    repo = _seeded_repo(tmp_path, "1")

    result = run_main(rel_path, *args_fn(repo))

    combined = result.stdout + result.stderr
    assert "does not speak" not in combined, f"{label} refused a supported version: {combined}"


@pytest.mark.parametrize(
    ("declared", "required", "refused"),
    [
        ({"version": 9}, False, True),
        ({"version": "1"}, False, True),
        ({"version": True}, False, True),
        ({}, True, True),
        ({"version": 1}, False, False),
        ({}, False, False),
    ],
    ids=["unsupported", "string", "bool", "required-absent", "supported", "absent"],
)
def test_the_predicate_tracks_the_shared_check_rather_than_a_copy_of_its_wording(
    declared, required, refused
) -> None:
    """`version_refused` reads ERROR STRINGS, so its correctness is a coupling to
    `validate_adapter_version`'s wording. Asserting the literals against themselves would
    prove nothing; driving the real check and asking the predicate about ITS output is
    what makes a reworded refusal fail here instead of silently turning every consumer
    guard into a no-op.

    The two negative rows are not decoration: without them a predicate hardcoded to
    `True` passes every positive row.
    """
    errors: list[str] = []
    ADAPTER_LIB.validate_adapter_version(declared, {}, errors, required=required)

    assert VERDICT.version_refused(errors) is refused, errors


def test_a_renamed_version_field_is_the_predicate_s_pinned_blind_spot() -> None:
    """The limit, asserted rather than described.

    `version_refused` reads error STRINGS, so a `field=` override renames the message out
    from under it: `schema_version must be 1` starts with neither refusal prefix. No call
    site passes `field=` today and the one real renamer (`worktree_doctor_lib`'s
    `manifest.` prefix) is an exempt census row -- but the day a caller does, every
    consumer guard becomes a silent no-op with nothing red.

    Asserted as the CURRENT behavior, so a future widening of the predicate fails here and
    the person doing it has to decide deliberately: this test flipping is the signal that
    the blind spot closed, not a breakage.
    """
    errors: list[str] = []
    ADAPTER_LIB.validate_adapter_version({"schema_version": 9}, {}, errors, field="schema_version")

    assert errors == ["schema_version must be 1"], errors
    assert VERDICT.version_refused(errors) is False, (
        "the renamed-field blind spot closed; update the comment in "
        "scripts/adapter_version_verdict.py and this test together"
    )


def test_an_unreadable_adapter_is_not_reported_as_a_version_refusal(tmp_path: Path) -> None:
    """A loader that raises answers None, not a refusal. Whatever is wrong with that
    adapter is not a version this reader refused, and the caller's own discovery already
    reports it -- rendering a version message there would send the operator to edit a
    line that is not the problem."""

    def boom(_repo_root: Path) -> dict:
        raise RuntimeError("resolver exploded")

    assert VERDICT.unspeakable_version_message(boom, tmp_path, adapter_name="x-adapter.yaml") is None


def test_a_non_list_errors_payload_does_not_read_as_refused() -> None:
    """A vendored resolver older than this reader can return a payload whose `errors` is
    absent or a bare string. Neither is a version refusal, and treating a string as one
    would refuse every run against that repo -- `"version must be 1" in payload` is the
    substring trap this shape avoids."""
    assert VERDICT.version_refused(None) is False
    assert VERDICT.version_refused("version must be 1") is False
    assert VERDICT.version_refused([None, 3]) is False


def test_a_parser_refusal_is_the_second_door_into_the_same_state(tmp_path: Path) -> None:
    """A round-1 bounded review found the guard keyed on the WORDING of one check rather
    than on the condition that check detects.

    `simple_skill_adapter_lib` answers a parser refusal with
    `data=infer_repo_defaults(...)` and `errors=[parse_failure_error(exc)]` — the same
    "nothing declared is honored" state a refused version leaves, reached by a different
    door. Before this, `version: !!int 9` (one token added to the very input the version
    guard refuses) walked past every consumer guard, and the pre-repair harm was
    reproduced at exit 0 on `check_requested_review_gate` and
    `bootstrap_review`.

    The messages must stay DISTINCT: the remediation for one is an adapter line and for
    the other is a YAML document that would not parse, and sending an operator to edit
    `version:` in a file the parser never read is the wrong instruction.
    """
    parse_errors = ["adapter could not be parsed: unsupported YAML construct in scalar: '!!int 9'"]
    assert VERDICT.parse_refused(parse_errors) is True
    assert VERDICT.version_refused(parse_errors) is False
    assert VERDICT.declarations_unhonored(parse_errors) is True

    message = VERDICT.unspeakable_version_message(
        lambda _repo_root: {"errors": parse_errors, "data": {}},
        tmp_path,
        adapter_name="release-adapter.yaml",
    )
    assert message is not None
    assert "could not be parsed" in message
    assert "Fix the YAML" in message
    assert "Set `version: 1`" not in message

    version_message = VERDICT.unspeakable_version_message(
        lambda _repo_root: {"errors": ["version must be 1"], "data": {}},
        tmp_path,
        adapter_name="release-adapter.yaml",
    )
    assert version_message is not None
    assert "does not speak" in version_message
    assert "Set `version: 1`" in version_message
    assert "could not be parsed" not in version_message


def test_an_ordinary_invalid_field_is_still_not_a_refusal() -> None:
    """The polarity control on the widened predicate. `valid: false` from one bad field
    beside fifteen honored ones is the case this module's docstring is explicit must NOT
    refuse — widening the condition to `not valid` would refuse it, which is why the
    condition is the two doors and not the flag."""
    ordinary = ["requested_review_policy must be 'warn-if-unconfigured' or 'advisory-only'"]
    assert VERDICT.declarations_unhonored(ordinary) is False
    assert VERDICT.parse_refused(ordinary) is False
    assert VERDICT.parse_refused(None) is False
    assert VERDICT.parse_refused("adapter could not be parsed: x") is False


def test_a_silently_dropped_line_is_the_third_door(tmp_path: Path) -> None:
    """The door this module's own docstring denied having, closed where the resolver
    reports it.

    `adapter_lib._parse_block` discards an over-indented line and records it in WARNINGS,
    not errors. A predicate over `errors` alone therefore answers False while `errors: []`,
    `valid: True`, and the repo's declaration is gone. Measured at `9fc1164db` with the
    slice-5 guard installed: `survey_verification` printed `adapter_valid: true` beside
    `tool_checks: []`, exit 0 — WORSE than the pre-guard base, which printed `false`.

    The message must be its OWN, not the version one: sending an operator to edit
    `version:` in a file whose `version:` is fine is the wrong instruction.
    """
    dropped = {
        "errors": [],
        "warnings": [
            "line 3 was not interpreted (over-indented line): 'verification_tools:'. "
            "Any field it meant to set is serving an inferred default instead."
        ],
        "data": {},
    }
    assert VERDICT.declarations_dropped(dropped) is True
    assert VERDICT.declarations_unhonored(dropped["errors"]) is False

    message = VERDICT.unspeakable_version_message(
        lambda _repo_root: dropped, tmp_path, adapter_name="impl-adapter.yaml"
    )
    assert message is not None
    assert "could not interpret" in message
    assert "Set `version: 1`" not in message
    assert "could not be parsed" not in message


def test_the_dropped_line_marker_matches_the_producer() -> None:
    """This module holds the marker as a LITERAL rather than importing it, because a hard
    dependency on `adapter_lib` would break the consumer guard in the skill-script layout
    that reaches `scripts.` through a runtime bootstrap. The literal must therefore be
    pinned against the producer, or the third door silently reopens on a reword."""
    assert VERDICT._UNINTERPRETED_WARNING_MARKER == ADAPTER_LIB.UNINTERPRETED_WARNING_MARKER


def test_an_ordinary_invalid_adapter_is_still_not_a_dropped_declaration() -> None:
    """The polarity that decides the shape of the fix. `adapter_lib.unreadable_reasons`
    returns errors AND uninterpreted warnings; keying on it would refuse an adapter that
    is merely invalid in an ordinary way, which this module's docstring forbids. Only the
    warning half counts."""
    ordinary = {"errors": ["preset_version must be a string"], "warnings": [], "data": {}}
    assert VERDICT.declarations_dropped(ordinary) is False
    assert VERDICT.declarations_dropped({"warnings": "not a list"}) is False
    assert VERDICT.declarations_dropped(None) is False
    no_adapter = {"errors": [], "warnings": ["No adapter found. Using defaults."], "data": {}}
    assert VERDICT.declarations_dropped(no_adapter) is False
