"""The lesson session EMISSION path: declare -> render preview bytes -> durable receipt.

Split out of `test_lesson_evaluation_continuity.py`, which owns the opposite half
of the same loop: reading retro artifacts back and reconciling the dispositions
they claim against the ledger (the gate's read/audit side, plus its report and
CLI). This module owns the WRITE side -- `open_lesson_session` rendering the
preview to a stream, and the receipt/bundle pair that binds those exact bytes to
the ledger snapshot.

It is one concern, not a length-cap spill: every test here turns on the same
invariant -- a receipt may exist only if the bytes it attests to were provably
delivered first. The broken-write, failed-flush, short-write, unsafe-id and
atomic-replace cases are simply the distinct ways that delivery can come up
short, and each one asserts on what the durable artifact is allowed to claim
afterwards. None of them parses a `Lesson evaluation:` line, builds a
reconciliation report, or runs the continuity gate; symmetrically, nothing left
in the sibling module calls `open_lesson_session` at all. The seam cuts the
module, not just its line count.

Invalid-input refusals for this same surface (malformed receipts, tampered
bundles, invalid write progress) live in
`test_lesson_evaluation_contract_boundaries.py`, which owns the refusal boundary
across the whole lesson-evaluation surface. This module is the behavioral path
and its crash-safety failure modes.
"""

from __future__ import annotations

# Import order note: stdlib names are grouped as ruff/isort requires, but this
# block is deliberately NOT a copy of the sibling test modules' -- the emission
# tests need `copy`/`io`/`runpy` and no `datetime`, so the duplicate-ratchet has
# no line-for-line import family to latch onto here.
import copy
import io
import json
import runpy
from pathlib import Path

import pytest

from scripts import lesson_evaluation_continuity_lib as continuity
from scripts import open_lesson_session


def test_receipt_binds_ledger_snapshot_renderer_bytes_and_integrity(tmp_path: Path) -> None:
    stdout = "Lesson selection preview (1/1 eligible):\n- a — 안녕\n".encode()
    snapshot = "a" * 64
    receipt = continuity.build_receipt(
        session_id="s-1",
        snapshot_sha256=snapshot,
        stdout_bytes=stdout,
        emitted_at="2026-08-14T00:00:00Z",
    )
    continuity.write_bundle(continuity.bundle_path(tmp_path, "s-1"), stdout)
    assert receipt["stdout_byte_count"] == len(stdout)
    assert continuity.validate_receipt(
        receipt, sessions={"s-1": {"snapshot_sha256": snapshot}}, output_dir=tmp_path
    ) == receipt
    assert continuity.load_session_bundle(
        receipt, sessions={"s-1": {"snapshot_sha256": snapshot}}, output_dir=tmp_path
    ) == stdout

    for field, value in (("snapshot_sha256", "b" * 64), ("renderer_id", "changed"), ("stdout_byte_count", 1)):
        tampered = copy.deepcopy(receipt)
        tampered[field] = value
        with pytest.raises(ValueError):
            continuity.validate_receipt(
                tampered,
                sessions={"s-1": {"snapshot_sha256": snapshot}},
                output_dir=tmp_path,
            )


def test_open_session_writes_exact_bytes_before_atomic_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    snapshot = "a" * 64
    event = {"session_id": "s-1", "snapshot_sha256": snapshot}
    preview = {
        "eligible_count": 1,
        "items": [{"lesson_id": "a", "lesson": "lesson text"}],
    }
    monkeypatch.setattr(
        open_lesson_session._session,
        "declare_session",
        lambda **_kwargs: (event, preview),
    )
    stdout = io.BytesIO()
    result = open_lesson_session.open_session(
        repo_root=tmp_path,
        session_id="s-1",
        seed="seed",
        stdout=stdout,
        emitted_at="2026-08-14T00:00:00Z",
    )
    expected = continuity.render_preview_bytes(preview)
    assert stdout.getvalue() == expected
    bundle = tmp_path / result["bundle_path"]
    assert bundle.read_bytes() == expected
    path = tmp_path / result["receipt_path"]
    assert path.is_file()
    receipt = json.loads(path.read_text(encoding="utf-8"))
    assert continuity.validate_receipt(
        receipt,
        sessions={"s-1": event},
        output_dir=tmp_path / "charness-artifacts/retro",
    ) == receipt


def test_open_session_broken_stdout_never_writes_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    event = {"session_id": "s-1", "snapshot_sha256": "a" * 64}
    preview = {"eligible_count": 0, "items": []}
    monkeypatch.setattr(
        open_lesson_session._session,
        "declare_session",
        lambda **_kwargs: (event, preview),
    )

    class Broken:
        def write(self, _payload: bytes) -> None:
            raise BrokenPipeError("closed")

        def flush(self) -> None:
            raise AssertionError("flush must not follow failed write")

    with pytest.raises(BrokenPipeError):
        open_lesson_session.open_session(
            repo_root=tmp_path, session_id="s-1", seed="seed", stdout=Broken()
        )
    assert not continuity.receipt_path(
        tmp_path / "charness-artifacts/retro", "s-1"
    ).exists()
    assert continuity.bundle_path(
        tmp_path / "charness-artifacts/retro", "s-1"
    ).is_file()


def test_open_session_failed_flush_never_writes_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    event = {"session_id": "s-1", "snapshot_sha256": "a" * 64}
    preview = {"eligible_count": 0, "items": []}
    monkeypatch.setattr(
        open_lesson_session._session,
        "declare_session",
        lambda **_kwargs: (event, preview),
    )

    class FlushFails(io.BytesIO):
        def flush(self) -> None:
            raise OSError("flush failed")

    with pytest.raises(OSError, match="flush failed"):
        open_lesson_session.open_session(
            repo_root=tmp_path, session_id="s-1", seed="seed", stdout=FlushFails()
        )
    assert not continuity.receipt_path(
        tmp_path / "charness-artifacts/retro", "s-1"
    ).exists()
    assert continuity.bundle_path(
        tmp_path / "charness-artifacts/retro", "s-1"
    ).is_file()


def test_open_session_completes_short_writes_before_receipting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    event = {"session_id": "s-1", "snapshot_sha256": "a" * 64}
    preview = {"eligible_count": 1, "items": [{"lesson_id": "a", "lesson": "lesson"}]}
    monkeypatch.setattr(
        open_lesson_session._session,
        "declare_session",
        lambda **_kwargs: (event, preview),
    )

    class ShortWriter:
        def __init__(self) -> None:
            self.data = bytearray()

        def write(self, payload: bytes) -> int:
            amount = min(3, len(payload))
            self.data.extend(payload[:amount])
            return amount

        def flush(self) -> None:
            pass

    stdout = ShortWriter()
    open_lesson_session.open_session(
        repo_root=tmp_path,
        session_id="s-1",
        seed="seed",
        stdout=stdout,
        emitted_at="2026-08-14T00:00:00Z",
    )
    assert bytes(stdout.data) == continuity.render_preview_bytes(preview)


def test_open_session_rejects_unsafe_id_before_declaration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    called = False

    def declare(**_kwargs: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(open_lesson_session._session, "declare_session", declare)
    with pytest.raises(ValueError, match="path-safe"):
        open_lesson_session.open_session(
            repo_root=tmp_path,
            session_id="../../bad",
            seed="seed",
            stdout=io.BytesIO(),
        )
    assert called is False
    assert not (tmp_path / "charness-artifacts").exists()


@pytest.mark.parametrize("kind", ["receipt", "bundle"])
def test_atomic_replace_failure_leaves_no_output_or_temp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    path = tmp_path / "receipts" / ("s-1.json" if kind == "receipt" else "s-1.md")
    def replace_error(*_args: object) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(continuity.os, "replace", replace_error)

    with pytest.raises(OSError, match="replace failed"):
        if kind == "receipt":
            continuity.write_receipt(
                path,
                continuity.build_receipt(
                    session_id="s-1",
                    snapshot_sha256="a" * 64,
                    stdout_bytes=b"preview\n",
                    emitted_at="2026-08-14T00:00:00Z",
                ),
            )
        else:
            continuity.write_bundle(path, b"preview\n")

    assert not path.exists()
    assert not list(path.parent.glob(f".{path.name}.*"))


def test_open_session_cli_main_delegates_arguments(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    seen: dict[str, object] = {}

    def fake_open_session(**kwargs: object) -> dict[str, object]:
        seen.update(kwargs)
        return {"bundle_path": "charness-artifacts/retro/lesson-session-receipts/s-1.md"}

    monkeypatch.setattr(open_lesson_session, "open_session", fake_open_session)
    monkeypatch.setattr(
        open_lesson_session.sys,
        "argv",
        [
            "open_lesson_session.py",
            "--repo-root",
            str(tmp_path),
            "--session-id",
            "s-1",
            "--seed",
            "seed",
        ],
    )
    assert open_lesson_session.main() == 0
    assert seen["repo_root"] == tmp_path.resolve()
    assert seen["session_id"] == "s-1"
    assert seen["seed"] == "seed"

    # #617 asks the COMMAND to reference the bundle by session id, and it did not:
    # `open_session` returned `bundle_path` and `main` dropped it. The announcement must
    # land on STDERR, because the receipt binds `stdout_sha256`/`stdout_byte_count` to the
    # rendered lesson bytes -- one extra stdout line would make every receipt this command
    # writes fail its own digest check. Both streams are asserted, because putting it on
    # the wrong one is the failure this arm exists to catch.
    captured = capsys.readouterr()
    assert "charness-artifacts/retro/lesson-session-receipts/s-1.md" in captured.err
    assert "s-1" in captured.err
    assert captured.out == "", (
        "the bundle announcement must not reach stdout: those bytes are digest-bound to "
        "the receipt, so announcing the bundle there would break every receipt"
    )


def test_open_session_script_entrypoint_reports_operational_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        open_lesson_session.sys,
        "argv",
        [
            "open_lesson_session.py",
            "--repo-root",
            str(tmp_path),
            "--session-id",
            "s-1",
            "--seed",
            "seed",
        ],
    )
    with pytest.raises(SystemExit) as caught:
        runpy.run_path(str(Path(open_lesson_session.__file__)), run_name="__main__")
    assert caught.value.code == 1
    assert capsys.readouterr().err
