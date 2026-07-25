from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from scripts import record_quality_runtime

# In-process on purpose: this recorder is import-safe and its `main()` is the whole
# CLI, so the 21 subprocess starts these cases used to pay bought no extra coverage.
# The boundary-bypass ratchet flags exactly this shape.


def _record(monkeypatch, repo: Path, *args: str) -> int:
    monkeypatch.setattr(
        sys,
        "argv",
        ["record_quality_runtime.py", "--repo-root", str(repo), *args],
    )
    return record_quality_runtime.main()


def test_record_quality_runtime_writes_summary_and_archive(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    for elapsed, status, timestamp in (
        ("1234", "pass", "2026-04-10T09:00:00Z"),
        ("2345", "fail", "2026-04-11T09:00:00Z"),
    ):
        assert (
            _record(
                monkeypatch,
                repo,
                "--label",
                "pytest",
                "--elapsed-ms",
                elapsed,
                "--status",
                status,
                "--timestamp",
                timestamp,
                "--runtime-profile",
                "default",
            )
            == 0
        )
    capsys.readouterr()

    summary_path = repo / ".charness" / "quality" / "runtime-signals.json"
    smoothing_path = repo / ".charness" / "quality" / "runtime-smoothing.json"
    archive_path = repo / ".charness" / "quality" / "history" / "runtime-signals-2026-04.jsonl"
    assert summary_path.exists()
    assert smoothing_path.exists()
    assert archive_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    pytest_entry = summary["commands"]["pytest"]
    assert pytest_entry["samples"] == 2
    assert pytest_entry["passes"] == 1
    assert pytest_entry["failures"] == 1
    assert pytest_entry["latest"]["elapsed_ms"] == 2345
    assert pytest_entry["median_recent_elapsed_ms"] == 1789

    smoothing = json.loads(smoothing_path.read_text(encoding="utf-8"))
    policy = smoothing["policy"]
    assert policy == {
        "kind": "ewma",
        "advisory": True,
        "alpha_base": 0.35,
        "warmup_n": 5,
    }
    smoothed_pytest = smoothing["commands"]["pytest"]
    assert smoothed_pytest["samples"] == 2
    assert smoothed_pytest["alpha_last"] == 0.14
    assert smoothed_pytest["ewma_elapsed_ms"] == 1389.54
    assert smoothed_pytest["advisory"] is True

    archive_lines = archive_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(archive_lines) == 2
    assert json.loads(archive_lines[-1])["runtime_profile"] == "default"


def test_record_quality_runtime_batch_matches_one_call_per_record(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """`--batch` exists only to stop paying one interpreter start per gate, so it must
    be a pure speedup: the state it leaves has to be byte-identical to replaying the
    same records one `--label` call at a time, in order."""
    records = [
        {"label": "pytest", "elapsed_ms": 1234, "status": "pass", "timestamp": "2026-04-10T09:00:00Z"},
        {"label": "ruff", "elapsed_ms": 28, "status": "pass", "timestamp": "2026-04-10T09:00:01Z"},
        {"label": "pytest", "elapsed_ms": 2345, "status": "fail", "timestamp": "2026-04-11T09:00:00Z"},
    ]

    sequential = tmp_path / "sequential"
    sequential.mkdir()
    for record in records:
        assert (
            _record(
                monkeypatch,
                sequential,
                "--label",
                record["label"],
                "--elapsed-ms",
                str(record["elapsed_ms"]),
                "--status",
                record["status"],
                "--timestamp",
                record["timestamp"],
                "--runtime-profile",
                "default",
            )
            == 0
        )

    batched = tmp_path / "batched"
    batched.mkdir()
    batch_path = tmp_path / "batch.jsonl"
    batch_path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )
    assert _record(monkeypatch, batched, "--batch", str(batch_path), "--runtime-profile", "default") == 0
    capsys.readouterr()

    for relative in (
        Path(".charness") / "quality" / "runtime-signals.json",
        Path(".charness") / "quality" / "runtime-smoothing.json",
        Path(".charness") / "quality" / "history" / "runtime-signals-2026-04.jsonl",
    ):
        assert (batched / relative).read_text(encoding="utf-8") == (
            sequential / relative
        ).read_text(encoding="utf-8"), f"batch mode diverged from sequential mode for {relative}"


def test_record_quality_runtime_batch_reports_a_malformed_record_without_losing_the_phase(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """A batch is written by the runner, not a human, so a malformed line means the
    runner broke and must be reported loudly. It must NOT cost the surrounding gates
    their samples: one killed gate subshell writing a truncated line would otherwise
    drop the whole phase and leave `check-runtime-budget` grading a stale store."""
    repo = tmp_path / "repo"
    repo.mkdir()
    batch_path = tmp_path / "batch.jsonl"
    batch_path.write_text(
        json.dumps({"label": "pytest", "elapsed_ms": 1, "status": "pass", "timestamp": "2026-04-10T09:00:00Z"})
        + '\n{"label":"ruff","elapsed_ms":,"status":"pass","timestamp":"2026-04-10T09:00:01Z"}\n'
        + json.dumps({"label": "ruff", "elapsed_ms": 28, "status": "pass", "timestamp": "2026-04-10T09:00:02Z"})
        + "\n",
        encoding="utf-8",
    )

    assert _record(monkeypatch, repo, "--batch", str(batch_path)) == 1
    captured = capsys.readouterr()
    assert "line 2" in captured.err

    summary = json.loads((repo / ".charness" / "quality" / "runtime-signals.json").read_text(encoding="utf-8"))
    commands = summary["profiles"][next(iter(summary["profiles"]))]["commands"]
    assert commands["pytest"]["latest"]["elapsed_ms"] == 1
    assert commands["ruff"]["latest"]["elapsed_ms"] == 28


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ('["pytest", 1, "pass"]', "not a JSON object"),
        ('{"label": "pytest"}', "missing elapsed_ms, status"),
        ('{"label": "pytest", "elapsed_ms": 1, "status": "skipped"}', "expected 'pass' or 'fail'"),
    ],
    ids=["not-an-object", "missing-keys", "bad-status"],
)
def test_record_quality_runtime_batch_names_why_a_record_is_malformed(
    tmp_path: Path, monkeypatch, capsys, line: str, expected: str
) -> None:
    """Each rejection reason is reported by name. A batch line is machine-written, so
    "malformed" alone does not tell the maintainer which part of the runner broke."""
    repo = tmp_path / "repo"
    repo.mkdir()
    batch_path = tmp_path / "batch.jsonl"
    batch_path.write_text(line + "\n", encoding="utf-8")

    assert _record(monkeypatch, repo, "--batch", str(batch_path)) == 1
    captured = capsys.readouterr()
    assert "line 1" in captured.err
    assert expected in captured.err


def test_record_quality_runtime_batch_skips_blank_lines(tmp_path: Path, monkeypatch, capsys) -> None:
    """A trailing newline or a blank separator is not a runner bug and must not be
    reported as a malformed record."""
    repo = tmp_path / "repo"
    repo.mkdir()
    batch_path = tmp_path / "batch.jsonl"
    batch_path.write_text(
        "\n   \n"
        + json.dumps({"label": "pytest", "elapsed_ms": 7, "status": "pass", "timestamp": "2026-04-10T09:00:00Z"})
        + "\n\n",
        encoding="utf-8",
    )

    assert _record(monkeypatch, repo, "--batch", str(batch_path)) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["recorded_count"] == 1
    assert payload["malformed_lines"] == []


def test_record_quality_runtime_batch_reports_an_unreadable_file(tmp_path: Path) -> None:
    """An unreadable batch is the runner failing to hand over its samples; silently
    recording nothing would leave `check-runtime-budget` grading a stale store."""
    missing = tmp_path / "absent.jsonl"

    with pytest.raises(SystemExit) as excinfo:
        record_quality_runtime.load_batch_records(missing)

    assert "is unreadable" in str(excinfo.value)
    assert str(missing) in str(excinfo.value)


def test_record_quality_runtime_empty_batch_leaves_no_store_behind(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """Zero records must not create an empty store: `check-runtime-budget` would then
    read a document that looks initialized but holds no samples."""
    repo = tmp_path / "repo"
    repo.mkdir()
    batch_path = tmp_path / "batch.jsonl"
    batch_path.write_text("\n", encoding="utf-8")

    assert _record(monkeypatch, repo, "--batch", str(batch_path)) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["recorded_count"] == 0
    assert not (repo / ".charness" / "quality" / "runtime-signals.json").exists()
    assert not (repo / ".charness" / "quality" / "runtime-smoothing.json").exists()


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        ((), "--label, --elapsed-ms, --status"),
        (("--label", "pytest"), "--elapsed-ms, --status"),
        (("--label", "pytest", "--elapsed-ms", "5"), "--status"),
    ],
    ids=["none", "label-only", "label-and-elapsed"],
)
def test_record_quality_runtime_names_every_missing_single_record_flag(
    tmp_path: Path, monkeypatch, capsys, args: tuple[str, ...], expected: str
) -> None:
    """Without `--batch` the three sample fields are required. argparse cannot mark
    them `required` (a batch run supplies none of them), so the check is hand-rolled
    and has to name what is actually missing."""
    repo = tmp_path / "repo"
    repo.mkdir()

    with pytest.raises(SystemExit):
        _record(monkeypatch, repo, *args)

    assert expected in capsys.readouterr().err


def test_record_quality_runtime_batch_refuses_a_single_record_timestamp(
    tmp_path: Path, monkeypatch
) -> None:
    """Each batch record carries its own timestamp; a stray `--timestamp` alongside
    `--batch` would be silently ignored, which is how a runner bug hides."""
    repo = tmp_path / "repo"
    repo.mkdir()
    batch_path = tmp_path / "batch.jsonl"
    batch_path.write_text("", encoding="utf-8")

    with pytest.raises(SystemExit):
        _record(monkeypatch, repo, "--batch", str(batch_path), "--timestamp", "2026-04-10T09:00:00Z")


def test_record_quality_runtime_batch_refuses_mixed_single_record_flags(
    tmp_path: Path, monkeypatch
) -> None:
    """Silently ignoring one of the two input modes would drop samples on a runner bug."""
    repo = tmp_path / "repo"
    repo.mkdir()
    batch_path = tmp_path / "batch.jsonl"
    batch_path.write_text("", encoding="utf-8")

    with pytest.raises(SystemExit):
        _record(monkeypatch, repo, "--batch", str(batch_path), "--label", "pytest")


def test_record_quality_runtime_keeps_named_profiles_separate(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    for profile, elapsed in (("local-fast", "1200"), ("ci-slow", "9000")):
        assert (
            _record(
                monkeypatch,
                repo,
                "--label",
                "pytest",
                "--elapsed-ms",
                elapsed,
                "--status",
                "pass",
                "--timestamp",
                "2026-04-10T09:00:00Z",
                "--runtime-profile",
                profile,
            )
            == 0
        )
    capsys.readouterr()

    summary = json.loads((repo / ".charness" / "quality" / "runtime-signals.json").read_text(encoding="utf-8"))
    assert summary.get("commands", {}) == {}
    assert summary["profiles"]["local-fast"]["commands"]["pytest"]["latest"]["elapsed_ms"] == 1200
    assert summary["profiles"]["ci-slow"]["commands"]["pytest"]["latest"]["elapsed_ms"] == 9000


def test_record_quality_runtime_rotates_old_monthly_archives(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    history_dir = repo / ".charness" / "quality" / "history"
    history_dir.mkdir(parents=True)

    for month in range(1, 14):
        assert (
            _record(
                monkeypatch,
                repo,
                "--label",
                "pytest",
                "--elapsed-ms",
                str(1000 + month),
                "--status",
                "pass",
                "--timestamp",
                f"2025-{month:02d}-01T00:00:00Z" if month <= 12 else "2026-01-01T00:00:00Z",
            )
            == 0
        )
    capsys.readouterr()

    archives = sorted(path.name for path in history_dir.glob("runtime-signals-*.jsonl"))
    assert len(archives) == 12
    assert "runtime-signals-2025-01.jsonl" not in archives
    assert "runtime-signals-2026-01.jsonl" in archives


def test_rotate_archives_tolerates_concurrently_deleted_oldest(tmp_path: Path, monkeypatch) -> None:
    # Two concurrent recorders can both glob the same archive list and both
    # target the same oldest file; the loser's unlink must not raise
    # FileNotFoundError and fail the recorder run.
    history_dir = tmp_path / "history"
    history_dir.mkdir()
    for month in range(1, record_quality_runtime.MAX_ARCHIVE_FILES + 3):
        name = f"{record_quality_runtime.ARCHIVE_PREFIX}2025-{month:02d}.jsonl"
        (history_dir / name).write_text("", encoding="utf-8")

    original_glob = Path.glob

    def racing_glob(self, pattern):
        results = sorted(original_glob(self, pattern))
        # Simulate the competing recorder evicting the same oldest archive
        # between this recorder's enumeration and its unlink.
        if results:
            results[0].unlink()
        return results

    monkeypatch.setattr(Path, "glob", racing_glob)
    record_quality_runtime.rotate_archives(history_dir)  # must not raise
    monkeypatch.undo()

    remaining = [
        path
        for path in history_dir.iterdir()
        if path.name.startswith(record_quality_runtime.ARCHIVE_PREFIX)
    ]
    assert len(remaining) <= record_quality_runtime.MAX_ARCHIVE_FILES
