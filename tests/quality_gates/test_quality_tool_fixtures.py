"""The fixture checker must REFUSE, not merely run.

Its predecessor was an inline one-liner that globbed non-recursively, short-circuited on a
missing `stdout_path`, and never looked at `stderr_sha256`. Under it the repo's single
checked-in fixture carried a 62-character stderr digest -- the empty-stream digest with two
characters dropped -- and no gate could see it. So every test here drives a refusal branch;
`test_the_checked_in_corpus_passes` is the only green-path case, and it is pinned against
the live tree deliberately, because a repaired digest that silently re-rots is the failure
this file exists to catch.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest
import quality_label_universe

from tests.script_loader import load_script_module

from .support import ROOT, run_script

SCRIPT = ROOT / "scripts" / "check_quality_tool_fixtures.py"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
RECORD = {
    "tool": "awiki",
    "version": "0.5.0",
    "command": "awiki lint -root docs -recursive",
    "exit_code": 1,
    "final_consumer": "test fixture",
    "non_claim": "fixture-only observation",
}


def _run(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return run_script(str(SCRIPT), "--repo-root", str(repo_root))


def _fixture_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "charness-artifacts" / "quality" / "fixtures"
    directory.mkdir(parents=True)
    return directory


def _write(directory: Path, name: str, payload: dict[str, object]) -> None:
    (directory / name).write_text(json.dumps({**RECORD, **payload}), encoding="utf-8")


def test_the_quality_runner_queues_this_gate_in_the_default_battery() -> None:
    """A refusal nobody runs is not a floor. The existing drift guard in
    `test_quality_runner.py` is one-directional -- it asserts every QUEUED gate has a
    harness stub, so deleting the queue line leaves it green and this gate simply stops
    running. `queue_selected` (not `queue_timed` behind an env opt-in) is the assertion:
    it is what puts the gate in the default battery rather than in a lane an operator
    must ask for."""
    rows = quality_label_universe.quality_gate_rows(ROOT)
    matches = [row for row in rows or [] if row["label"] == "quality-tool-fixtures"]
    assert [row["command"] for row in matches] == [
        [
            "python3",
            "scripts/check_quality_tool_fixtures.py",
            "--repo-root",
            "$REPO_ROOT",
        ]
    ], "quality-gates.yaml must declare check_quality_tool_fixtures.py"


def test_the_checked_in_corpus_passes() -> None:
    result = _run(ROOT)
    assert result.returncode == 0, result.stderr
    assert "Verified" in result.stdout


def test_a_missing_fixture_directory_is_refused() -> None:
    """The repo relies on captured fixtures, so their absence is not a clean corpus."""
    result = _run(Path(__file__).resolve().parent)
    assert result.returncode == 1
    assert "no fixtures" in result.stderr


def test_an_existing_but_empty_fixture_directory_is_refused(tmp_path: Path) -> None:
    """A directory without a fixture is the same unproven evidence contract."""
    _fixture_dir(tmp_path)
    result = _run(tmp_path)
    assert result.returncode == 1
    assert "no fixtures" in result.stderr


@pytest.mark.parametrize("stream", ["stdout", "stderr"])
def test_a_malformed_digest_is_refused(tmp_path: Path, stream: str) -> None:
    """The observed defect: 62 hex characters, which no comparison would ever reach.

    Parametrized over both streams on purpose. The defect that motivated this whole
    script was in `stderr_sha256`, and with stdout-only coverage narrowing `STREAMS` back
    to `("stdout",)` left the entire suite green -- caught by the round-2 review.
    """
    directory = _fixture_dir(tmp_path)
    (directory / "out.txt").write_text("captured\n", encoding="utf-8")
    _write(
        directory,
        "f.json",
        {
            f"{stream}_path": "charness-artifacts/quality/fixtures/out.txt",
            f"{stream}_sha256": EMPTY_SHA256[:62],
        },
    )
    result = _run(tmp_path)
    assert result.returncode == 1
    assert f"{stream}_sha256 is not 64 lowercase hex characters" in result.stderr


@pytest.mark.parametrize("stream", ["stdout", "stderr"])
def test_a_stream_path_without_a_digest_is_refused(tmp_path: Path, stream: str) -> None:
    """The mirror of the vacuous-skip hole: naming a file and pinning nothing.

    Same shape as this slice's root cause -- a rewrite that drops one key while every
    gate keeps reporting green.
    """
    directory = _fixture_dir(tmp_path)
    (directory / "out.txt").write_text("captured\n", encoding="utf-8")
    _write(directory, "f.json", {f"{stream}_path": "charness-artifacts/quality/fixtures/out.txt"})
    result = _run(tmp_path)
    assert result.returncode == 1
    assert f"{stream}_sha256 is absent" in result.stderr


@pytest.mark.parametrize(
    "escape",
    ["/etc/hostname", "../../../outside.txt", "charness-artifacts/quality/other.txt"],
)
def test_a_stream_path_outside_the_fixture_directory_is_refused(
    tmp_path: Path, escape: str
) -> None:
    """`repo_root / "/etc/hostname"` is `/etc/hostname`; `../` climbs out. Either would
    let a fixture verify against a file nobody reviewed."""
    directory = _fixture_dir(tmp_path)
    (tmp_path / "charness-artifacts" / "quality" / "other.txt").write_text("x\n", encoding="utf-8")
    _write(directory, "f.json", {"stdout_path": escape, "stdout_sha256": "a" * 64})
    result = _run(tmp_path)
    assert result.returncode == 1
    assert "escapes" in result.stderr


def test_a_digest_without_a_stream_path_is_refused(tmp_path: Path) -> None:
    """The short-circuit hole: `.get("stdout_path") and ...` passed this vacuously."""
    directory = _fixture_dir(tmp_path)
    _write(directory, "f.json", {"stdout_sha256": "a" * 64})
    result = _run(tmp_path)
    assert result.returncode == 1
    assert "nothing proves it" in result.stderr


def test_an_empty_stream_needs_no_path(tmp_path: Path) -> None:
    """A tool that wrote nothing to stderr records the empty digest and no file. Refusing
    that would be a refusal against malformed input that changes no verdict.

    It sits next to a file-backed fixture on purpose. Round 1 of this repair let this
    corpus satisfy the floor ALONE, which meant the floor's only test-guaranteed
    satisfier was the vacuous one -- see the corpus test below."""
    directory = _fixture_dir(tmp_path)
    (directory / "out.txt").write_text("captured\n", encoding="utf-8")
    _write(directory, "empty-stderr.json", {"stderr_sha256": EMPTY_SHA256})
    _write(
        directory,
        "real.json",
        {
            "stdout_path": "charness-artifacts/quality/fixtures/out.txt",
            "stdout_sha256": hashlib.sha256(b"captured\n").hexdigest(),
        },
    )
    assert _run(tmp_path).returncode == 0


@pytest.mark.parametrize("stream", ["stdout", "stderr"])
def test_digest_drift_is_refused(tmp_path: Path, stream: str) -> None:
    directory = _fixture_dir(tmp_path)
    (directory / "out.txt").write_text("captured\n", encoding="utf-8")
    _write(
        directory,
        "f.json",
        {
            f"{stream}_path": "charness-artifacts/quality/fixtures/out.txt",
            f"{stream}_sha256": "b" * 64,
        },
    )
    result = _run(tmp_path)
    assert result.returncode == 1
    assert f"{stream}_sha256 drift" in result.stderr


def test_a_nested_fixture_is_not_skipped(tmp_path: Path) -> None:
    """`source_paths` owns `fixtures/**`, so a non-recursive glob would let a nested
    fixture clear the unmatched-surface blocker while nothing ever read it."""
    directory = _fixture_dir(tmp_path)
    (directory / "out.txt").write_text("captured\n", encoding="utf-8")
    nested = directory / "awiki"
    nested.mkdir()
    _write(
        nested,
        "run.json",
        {
            "stdout_path": "charness-artifacts/quality/fixtures/out.txt",
            "stdout_sha256": "c" * 64,
        },
    )
    result = _run(tmp_path)
    assert result.returncode == 1
    assert "awiki/run.json" in result.stderr


def test_a_missing_stream_file_is_refused(tmp_path: Path) -> None:
    directory = _fixture_dir(tmp_path)
    _write(
        directory,
        "f.json",
        {
            "stdout_path": "charness-artifacts/quality/fixtures/gone.txt",
            "stdout_sha256": "d" * 64,
        },
    )
    result = _run(tmp_path)
    assert result.returncode == 1
    assert "does not exist" in result.stderr


@pytest.mark.parametrize(
    ("name", "body"),
    [("bad.json", "{not json"), ("list.json", "[]")],
)
def test_an_unreadable_fixture_is_refused(tmp_path: Path, name: str, body: str) -> None:
    directory = _fixture_dir(tmp_path)
    (directory / name).write_text(body, encoding="utf-8")
    assert _run(tmp_path).returncode == 1


def test_containment_is_exercised_in_process(tmp_path: Path) -> None:
    """Every other test drives the script through `subprocess`, which is the honest way to
    test a CLI but leaves the containment helper invisible to in-process coverage -- so
    the changed-line mutation gate reads it as untested. This calls it directly.
    """
    module = load_script_module(
        "check_quality_tool_fixtures_under_test",
        ROOT / "scripts" / "check_quality_tool_fixtures.py",
    )
    fixtures = tmp_path / "charness-artifacts" / "quality" / "fixtures"
    fixtures.mkdir(parents=True)
    inside = fixtures / "out.txt"
    inside.write_text("x\n", encoding="utf-8")
    (tmp_path / "charness-artifacts" / "quality" / "sibling.txt").write_text(
        "x\n", encoding="utf-8"
    )

    contained = module._contained(tmp_path, "charness-artifacts/quality/fixtures/out.txt")
    assert contained == inside.resolve()
    # nested is still inside
    assert module._contained(tmp_path, "charness-artifacts/quality/fixtures/a/b.txt") is not None
    # absolute path silently overrides the `/` join -- the escape the helper exists for
    assert module._contained(tmp_path, "/etc/hostname") is None
    # upward traversal
    assert module._contained(tmp_path, "../../../outside.txt") is None
    # a sibling directory inside the repo is still outside the FIXTURE dir
    assert module._contained(tmp_path, "charness-artifacts/quality/sibling.txt") is None
    # non-string and empty inputs
    assert module._contained(tmp_path, None) is None
    assert module._contained(tmp_path, "") is None
    assert module._contained(tmp_path, 7) is None


def test_a_fixture_with_no_digests_is_not_invented_into_a_failure(tmp_path: Path) -> None:
    """Not every recorded observation captures a stream. Refusing one PER FIXTURE would
    add teeth where nothing can escape -- so it stays allowed, next to a fixture that
    does pin something. The corpus-level floor below is what the escape actually needed.
    """
    directory = _fixture_dir(tmp_path)
    (directory / "out.txt").write_text("captured\n", encoding="utf-8")
    _write(
        directory,
        "pinned.json",
        {
            "stdout_path": "charness-artifacts/quality/fixtures/out.txt",
            "stdout_sha256": hashlib.sha256(b"captured\n").hexdigest(),
        },
    )
    _write(directory, "unpinned.json", {})
    result = _run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert "1 fixture(s) pinning no stream" in result.stdout


def test_a_corpus_that_pins_no_stream_at_all_is_refused(tmp_path: Path) -> None:
    """The round-2 hole in this script's OWN repair: the empty-corpus refusal keyed on
    how many fixture FILES exist, not on what was compared. A fixture carrying only the
    six required provenance fields printed `Verified 1 quality tool fixture(s) against
    their captured streams.` and exited 0 having compared zero streams -- reaching the
    unproven contract by ADDING a file instead of removing one.
    """
    directory = _fixture_dir(tmp_path)
    _write(directory, "f.json", {})
    result = _run(tmp_path)
    assert result.returncode == 1
    assert "none compared a digest against bytes checked in under" in result.stderr
    assert "Verified" not in result.stdout


def test_many_provenance_only_fixtures_do_not_add_up_to_a_comparison(tmp_path: Path) -> None:
    """Count is not evidence. Ten unpinned fixtures compare exactly as much as one."""
    directory = _fixture_dir(tmp_path)
    for index in range(10):
        _write(directory, f"f{index}.json", {})
    result = _run(tmp_path)
    assert result.returncode == 1
    assert "10 fixture(s) and 0 digest check(s)" in result.stderr


def test_the_success_line_reports_comparisons_not_only_files(tmp_path: Path) -> None:
    """The old line claimed fixtures were verified `against their captured streams`
    whether or not any stream existed. A reader triaging a green gate could not tell a
    corpus that compared six streams from one that compared none, so the claim is now
    the count itself."""
    directory = _fixture_dir(tmp_path)
    (directory / "out.txt").write_text("captured\n", encoding="utf-8")
    digest = hashlib.sha256(b"captured\n").hexdigest()
    _write(
        directory,
        "f.json",
        {
            "stdout_path": "charness-artifacts/quality/fixtures/out.txt",
            "stdout_sha256": digest,
            "stderr_sha256": EMPTY_SHA256,
        },
    )
    result = _run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert (
        "1 quality tool fixture(s): 2 stream digest(s) checked, 1 against checked-in capture file(s)."
        in result.stdout
    )
    assert "pinning no stream" not in result.stdout


def test_a_refused_comparison_is_never_counted_as_one(tmp_path: Path) -> None:
    """Drift, escape, and missing-file branches all `continue` past the counter. If any
    of them still incremented it, a corpus of nothing but broken comparisons would clear
    the corpus floor -- the floor would then be satisfied by the failures it exists to
    report."""
    module = load_script_module(
        "check_quality_tool_fixtures_compare_count",
        ROOT / "scripts" / "check_quality_tool_fixtures.py",
    )
    directory = _fixture_dir(tmp_path)
    (directory / "out.txt").write_text("captured\n", encoding="utf-8")
    for name, payload in (
        (
            "drift.json",
            {
                "stdout_path": "charness-artifacts/quality/fixtures/out.txt",
                "stdout_sha256": "b" * 64,
            },
        ),
        (
            "gone.json",
            {
                "stdout_path": "charness-artifacts/quality/fixtures/gone.txt",
                "stdout_sha256": "d" * 64,
            },
        ),
        ("escape.json", {"stdout_path": "/etc/hostname", "stdout_sha256": "a" * 64}),
        (
            "bad-digest.json",
            {
                "stdout_path": "charness-artifacts/quality/fixtures/out.txt",
                "stdout_sha256": EMPTY_SHA256[:62],
            },
        ),
        ("unproven.json", {"stdout_sha256": "a" * 64}),
    ):
        _write(directory, name, payload)
        found, checked, file_backed = module._problems(tmp_path, directory / name)
        assert found, name
        assert (checked, file_backed) == (0, 0), f"{name} counted a refused comparison"


def test_a_fixture_without_a_final_consumer_can_still_be_recorded_evidence(tmp_path: Path) -> None:
    directory = _fixture_dir(tmp_path)
    # Pins a FILE-backed stream so the corpus floor is satisfied; `final_consumer` is
    # the subject.
    (directory / "out.txt").write_text("captured\n", encoding="utf-8")
    _write(
        directory,
        "f.json",
        {
            "final_consumer": None,
            "stdout_path": "charness-artifacts/quality/fixtures/out.txt",
            "stdout_sha256": hashlib.sha256(b"captured\n").hexdigest(),
        },
    )
    assert _run(tmp_path).returncode == 0


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tool", ""),
        ("version", None),
        ("command", 7),
        ("exit_code", True),
        ("final_consumer", ""),
        ("non_claim", ""),
    ],
)
def test_a_fixture_without_required_observation_provenance_is_refused(
    tmp_path: Path, field: str, value: object
) -> None:
    directory = _fixture_dir(tmp_path)
    _write(directory, "f.json", {field: value})

    result = _run(tmp_path)

    assert result.returncode == 1
    assert f"required observation field {field!r}" in result.stderr


def test_a_corpus_of_empty_digests_alone_does_not_satisfy_the_floor(tmp_path: Path) -> None:
    """Round 1's own escape. It counted the empty-digest-without-path branch as a
    comparison, so ONE fixture carrying `sha256("")` for both streams reported
    `2 captured stream(s) compared` and exited 0 having opened no file at all -- a floor
    satisfiable by typing 64 known characters, requiring no tool run and pinning no
    captured evidence. That is the same "green over nothing checked" class the count was
    introduced to close, one layer down."""
    directory = _fixture_dir(tmp_path)
    _write(directory, "f.json", {"stdout_sha256": EMPTY_SHA256, "stderr_sha256": EMPTY_SHA256})
    result = _run(tmp_path)
    assert result.returncode == 1
    assert "1 fixture(s) and 2 digest check(s)" in result.stderr
    assert "none compared a digest against bytes checked in under" in result.stderr


def test_the_summary_separates_digest_checks_from_file_backed_ones(tmp_path: Path) -> None:
    """A reader of a green gate must be able to tell how much of it touched disk."""
    directory = _fixture_dir(tmp_path)
    (directory / "out.txt").write_text("captured\n", encoding="utf-8")
    _write(
        directory,
        "f.json",
        {
            "stdout_path": "charness-artifacts/quality/fixtures/out.txt",
            "stdout_sha256": hashlib.sha256(b"captured\n").hexdigest(),
            "stderr_sha256": EMPTY_SHA256,
        },
    )
    result = _run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert "2 stream digest(s) checked, 1 against checked-in capture file(s)" in result.stdout
