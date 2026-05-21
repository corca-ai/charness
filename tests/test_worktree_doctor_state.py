from __future__ import annotations

from scripts.worktree_doctor_state import (
    DEFAULT_DOCTOR_TIMEOUT_SECONDS,
    DEFAULT_PREPARE_TIMEOUT_SECONDS,
    FAIL,
    PASS,
    SKIPPED,
    CheckResult,
    CommandResult,
    ManifestState,
    aggregate_status,
    tail,
)


def test_tail_keeps_short_text_and_truncates_from_end() -> None:
    assert tail("abc", max_chars=5) == "abc"
    assert tail("abc", max_chars=3) == "abc"
    assert tail("abcdef", max_chars=2) == "ef"
    assert tail("abcdef", max_chars=3) == "def"


def test_tail_default_keeps_last_2000_characters() -> None:
    text = ("a" * 17) + ("b" * 2000)

    result = tail(text)

    assert result == "b" * 2000
    assert len(result) == 2000


def test_tail_accepts_text_as_keyword_argument() -> None:
    assert tail(text="abcdef", max_chars=2) == "ef"


def test_aggregate_status_fails_if_any_check_fails() -> None:
    dynamic_fail = "".join(["fa", "il"])

    result = aggregate_status(
        [
            CheckResult(id="first", status=PASS, detail="ok"),
            CheckResult(id="second", status=SKIPPED, detail="not applicable"),
            CheckResult(id="third", status=dynamic_fail, detail="broken"),
        ]
    )

    assert result == FAIL


def test_aggregate_status_passes_for_empty_or_non_failing_checks() -> None:
    assert aggregate_status([]) == PASS
    assert aggregate_status([CheckResult(id="skip", status=SKIPPED, detail="not applicable")]) == PASS
    assert aggregate_status([CheckResult(id="unknown", status="error", detail="unknown")]) == PASS


def test_command_result_default_timeout_and_dict_shape() -> None:
    result = CommandResult(
        id="doctor",
        argv=["echo", "ok"],
        exit_code=0,
        duration_ms=12,
        stdout_tail="ok",
        stderr_tail="",
    )

    assert result.timed_out is False
    assert result.to_dict() == {
        "id": "doctor",
        "argv": ["echo", "ok"],
        "exit_code": 0,
        "duration_ms": 12,
        "stdout_tail": "ok",
        "stderr_tail": "",
        "timed_out": False,
    }


def test_manifest_state_defaults_and_public_dict_shape() -> None:
    result = ManifestState(found=False, path=None, valid=False)

    assert result.errors == []
    assert result.data == {}
    assert result.to_dict() == {
        "found": False,
        "path": None,
        "valid": False,
        "errors": [],
    }


def test_worktree_doctor_timeout_defaults() -> None:
    assert DEFAULT_DOCTOR_TIMEOUT_SECONDS == 10
    assert DEFAULT_PREPARE_TIMEOUT_SECONDS == 600
