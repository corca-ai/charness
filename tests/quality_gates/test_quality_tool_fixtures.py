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
import sys
from pathlib import Path

import pytest

from tests.script_loader import load_script_module

from .support import ROOT

SCRIPT = ROOT / "scripts" / "check_quality_tool_fixtures.py"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


def _run(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo_root)],
        capture_output=True, text=True, check=False,
    )


def _fixture_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "charness-artifacts" / "quality" / "fixtures"
    directory.mkdir(parents=True)
    return directory


def _write(directory: Path, name: str, payload: dict[str, object]) -> None:
    (directory / name).write_text(json.dumps(payload), encoding="utf-8")


def test_the_checked_in_corpus_passes() -> None:
    result = _run(ROOT)
    assert result.returncode == 0, result.stderr
    assert "Verified" in result.stdout


def test_a_missing_fixture_directory_is_not_a_silent_pass() -> None:
    """Exit 0 is right here -- there is nothing to verify -- but it must SAY so, or a
    mis-rooted invocation reads exactly like a clean corpus."""
    result = _run(Path(__file__).resolve().parent)
    assert result.returncode == 0
    assert "nothing to verify" in result.stdout


def test_an_existing_but_empty_fixture_directory_is_not_a_silent_pass(tmp_path: Path) -> None:
    """Distinct from the missing-directory case, which shares a branch today only by
    accident: any future existence check on the fixture dir would split them, and a single
    test would silently keep covering one side."""
    _fixture_dir(tmp_path)
    result = _run(tmp_path)
    assert result.returncode == 0
    assert "nothing to verify" in result.stdout


@pytest.mark.parametrize("stream", ["stdout", "stderr"])
def test_a_malformed_digest_is_refused(tmp_path: Path, stream: str) -> None:
    """The observed defect: 62 hex characters, which no comparison would ever reach.

    Parametrized over both streams on purpose. The defect that motivated this whole
    script was in `stderr_sha256`, and with stdout-only coverage narrowing `STREAMS` back
    to `("stdout",)` left the entire suite green -- caught by the round-2 review.
    """
    directory = _fixture_dir(tmp_path)
    (directory / "out.txt").write_text("captured\n", encoding="utf-8")
    _write(directory, "f.json", {
        f"{stream}_path": "charness-artifacts/quality/fixtures/out.txt",
        f"{stream}_sha256": EMPTY_SHA256[:62],
    })
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
def test_a_stream_path_outside_the_fixture_directory_is_refused(tmp_path: Path, escape: str) -> None:
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
    that would be a refusal against malformed input that changes no verdict."""
    directory = _fixture_dir(tmp_path)
    _write(directory, "f.json", {"stderr_sha256": EMPTY_SHA256})
    assert _run(tmp_path).returncode == 0


@pytest.mark.parametrize("stream", ["stdout", "stderr"])
def test_digest_drift_is_refused(tmp_path: Path, stream: str) -> None:
    directory = _fixture_dir(tmp_path)
    (directory / "out.txt").write_text("captured\n", encoding="utf-8")
    _write(directory, "f.json", {
        f"{stream}_path": "charness-artifacts/quality/fixtures/out.txt",
        f"{stream}_sha256": "b" * 64,
    })
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
    _write(nested, "run.json", {
        "stdout_path": "charness-artifacts/quality/fixtures/out.txt",
        "stdout_sha256": "c" * 64,
    })
    result = _run(tmp_path)
    assert result.returncode == 1
    assert "awiki/run.json" in result.stderr


def test_a_missing_stream_file_is_refused(tmp_path: Path) -> None:
    directory = _fixture_dir(tmp_path)
    _write(directory, "f.json", {
        "stdout_path": "charness-artifacts/quality/fixtures/gone.txt",
        "stdout_sha256": "d" * 64,
    })
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
    (tmp_path / "charness-artifacts" / "quality" / "sibling.txt").write_text("x\n", encoding="utf-8")

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
    """Not every recorded observation captures a stream. Refusing one would add teeth
    where nothing can escape."""
    directory = _fixture_dir(tmp_path)
    _write(directory, "f.json", {"tool": "awiki", "exit_code": 1})
    assert _run(tmp_path).returncode == 0
