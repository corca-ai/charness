"""Unit pins for the lane's worker argv: declaration flags, order, omission."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from skills.public.critique.scripts import run_review_invocation as invocation

_KEYS = (
    "prompt",
    "capability",
    "scope",
    "ledger",
    "output",
    "receipt",
    "report",
    "stdout",
    "stderr",
    "schema",
    "packet",
    "reviewed",
    "backend_stdout",
    "backend_stderr",
)


def _command(tmp_path: Path, **overrides: object) -> list[str]:
    package = {"skill_dir": tmp_path, "shared_dir": tmp_path, "runner": tmp_path / "worker.py"}
    paths = {key: tmp_path / f"{key}.json" for key in _KEYS}
    support = SimpleNamespace(relative=lambda _root, path: Path(path).name)
    kwargs: dict[str, object] = {
        "root": tmp_path,
        "backend": "codex_exec",
        "scope": "scope-1",
        "attempt": "attempt-1",
        "packet_sha": "p" * 64,
        "input_sha": "i" * 64,
        "parent_receipt": "parent-1",
        "boundary_mode": "unscoped",
        "boundary_sha": None,
        "expected_targets": None,
        "owner_run_id": "owner-attempt-1",
        "owner_receipt": tmp_path / ".charness-owner.json",
    }
    kwargs.update(overrides)
    return invocation.runner_command(support, package, paths, **kwargs)  # type: ignore[arg-type]


def test_expected_targets_become_worker_flags_in_order(tmp_path: Path) -> None:
    argv = _command(tmp_path, expected_targets=["item-a", "item-b"])

    pairs = [argv[index : index + 2] for index, token in enumerate(argv) if token == "--expected-target"]
    assert pairs == [["--expected-target", "item-a"], ["--expected-target", "item-b"]]


def test_no_declaration_means_no_worker_flags(tmp_path: Path) -> None:
    assert "--expected-target" not in _command(tmp_path)
    assert "--expected-target" not in _command(tmp_path, expected_targets=[])


def test_boundary_fingerprint_stays_optional(tmp_path: Path) -> None:
    assert "--boundary-fingerprint" not in _command(tmp_path)
    assert "--boundary-fingerprint" in _command(tmp_path, boundary_sha="boundary-1")


def test_selected_reviewer_tier_reaches_canonical_runner(tmp_path: Path) -> None:
    argv = _command(tmp_path, reviewer_tier="medium")
    index = argv.index("--reviewer-tier")
    assert argv[index + 1] == "medium"


def test_invocation_binds_the_exact_owned_runtime_reference(tmp_path: Path) -> None:
    argv = _command(tmp_path)
    assert argv[argv.index("--owner-run-id") + 1] == "owner-attempt-1"
    assert argv[argv.index("--owner-receipt-file") + 1] == str(
        (tmp_path / ".charness-owner.json")
    )
