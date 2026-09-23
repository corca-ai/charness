"""Lane child env secret scrub (#832).

The lane child inherits ambient env, and an executor may re-emit its
environment where any local process can read it (observed: muse
`--env-json` argv). Secret-pattern names are dropped from the lane env
except per-executor auth keeps and the operator override; the receipt
records names, never values.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from scripts.task_run import task_run_runtime

from .test_task_run_fixtures import _codex, _repo, _run


def _env(*names: str) -> dict[str, str]:
    return {name: "value" for name in names}


def test_scrub_drops_secret_names_and_keeps_operational_ones() -> None:
    payload: dict[str, object] = {}

    kept = task_run_runtime.scrubbed_lane_env(
        payload,
        _env(
            "TAVILY_API_KEY",
            "SLACK_BOT_TOKEN",
            "HF_TOKEN",
            "DB_PASSWORD",
            "PATH",
            "SSH_AUTH_SOCK",
        ),
        "muse",
    )

    assert sorted(kept) == ["PATH", "SSH_AUTH_SOCK"]
    assert payload["lane_env"] == {
        "executor": "muse",
        "scrubbed": [
            "DB_PASSWORD",
            "HF_TOKEN",
            "SLACK_BOT_TOKEN",
            "TAVILY_API_KEY",
        ],
        "kept_secret_names": [],
    }


def test_codex_keeps_its_auth_key_while_muse_keeps_none() -> None:
    codex_payload: dict[str, object] = {}
    muse_payload: dict[str, object] = {}
    env = _env("OPENAI_API_KEY", "GEMINI_API_KEY")

    codex_kept = task_run_runtime.scrubbed_lane_env(
        codex_payload, env, "codex"
    )
    muse_kept = task_run_runtime.scrubbed_lane_env(muse_payload, env, "muse")

    assert sorted(codex_kept) == ["OPENAI_API_KEY"]
    assert codex_payload["lane_env"] == {
        "executor": "codex",
        "scrubbed": ["GEMINI_API_KEY"],
        "kept_secret_names": ["OPENAI_API_KEY"],
    }
    assert muse_kept == {}
    assert muse_payload["lane_env"] == {
        "executor": "muse",
        "scrubbed": ["GEMINI_API_KEY", "OPENAI_API_KEY"],
        "kept_secret_names": [],
    }


def test_operator_override_keeps_listed_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        task_run_runtime.LANE_KEEP_SECRET_ENV, " MY_PROVIDER_TOKEN ,, "
    )
    payload: dict[str, object] = {}

    kept = task_run_runtime.scrubbed_lane_env(
        payload, _env("MY_PROVIDER_TOKEN", "OTHER_SECRET"), "muse"
    )

    assert kept == {"MY_PROVIDER_TOKEN": "value"}
    assert payload["lane_env"] == {
        "executor": "muse",
        "scrubbed": ["OTHER_SECRET"],
        "kept_secret_names": ["MY_PROVIDER_TOKEN"],
    }


def test_unknown_executor_keeps_no_secret_names() -> None:
    payload: dict[str, object] = {}

    kept = task_run_runtime.scrubbed_lane_env(
        payload, _env("OPENAI_API_KEY", "PATH"), "future-exec"
    )

    assert kept == {"PATH": "value"}
    assert payload["lane_env"] == {
        "executor": "future-exec",
        "scrubbed": ["OPENAI_API_KEY"],
        "kept_secret_names": [],
    }


def test_lane_run_records_scrubbed_names_not_values(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CHARNESS_TEST_FAKE_TOKEN_832", "super-secret-value")
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py")

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "completed", payload
    assert (
        "CHARNESS_TEST_FAKE_TOKEN_832" in payload["lane_env"]["scrubbed"]
    )
    assert "super-secret-value" not in str(payload["lane_env"])
    assert os.environ["CHARNESS_TEST_FAKE_TOKEN_832"] == "super-secret-value"
