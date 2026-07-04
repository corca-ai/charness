"""WS-1 seeded proof: the rung-2 distinct-channel observer + rung-1 presence
floor on the release publish boundary (before `ensure_release_issues_closed`).

Network-free unit + integration proof: the rung-1 floor refuses a SILENT record,
a confirmation OR a typed non-`verified` disposition passes it EQUALLY (F2a), and
the observer never uses `gh release view` as the distinct channel.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills" / "public" / "release" / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_test", _SCRIPTS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_POST_CREATE = _load("publish_release_post_create")
_EXECUTE = _load("publish_release_execute")
_HELPERS = _load("publish_release_helpers")


def _shell_result(returncode: int, stdout: str = "", stderr: str = ""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


# --- rung-1 presence floor ------------------------------------------------


def test_rung1_floor_refuses_silent_record() -> None:
    assert _POST_CREATE.evaluate_release_distinct_channel({})["ok"] is False
    assert _POST_CREATE.evaluate_release_distinct_channel({"distinct_channel_verification": {}})["ok"] is False


def test_rung1_floor_passes_confirmation_and_typed_disposition_equally() -> None:
    # F2a: a confirmation and a typed non-`verified` disposition pass EQUALLY.
    confirmed = {"distinct_channel_verification": {"channel": "https-fetch", "status": "confirmed"}}
    disposed = {"distinct_channel_verification": {"channel": "none", "status": "skipped", "reason": "x"}}
    assert _POST_CREATE.evaluate_release_distinct_channel(confirmed)["ok"] is True
    assert _POST_CREATE.evaluate_release_distinct_channel(disposed)["ok"] is True


# --- rung-2 distinct-channel observer -------------------------------------


def test_observer_http_default_confirms_on_200() -> None:
    payload: dict = {}
    record = _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), payload, adapter_data={}, run_shell=None, tag_name="v1.2.3",
        expected_release_url="https://example/releases/tag/v1.2.3",
        http_probe=lambda url: {"channel": "https-fetch", "url": url, "status": "confirmed", "http_status": 200},
    )
    assert record["status"] == "confirmed"
    assert record["channel"] == "https-fetch"
    assert payload["distinct_channel_verification"] is record


def test_observer_http_default_records_typed_disposition_on_failure() -> None:
    payload: dict = {}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), payload, adapter_data={}, run_shell=None, tag_name="v1.2.3",
        expected_release_url="https://example/releases/tag/v1.2.3",
        http_probe=lambda url: {"channel": "https-fetch", "url": url, "status": "blocked-needs-capability", "reason": "offline"},
    )
    # A typed disposition is recorded, not a silent green.
    assert payload["distinct_channel_verification"]["status"] == "blocked-needs-capability"


def test_observer_adapter_probe_confirms_and_disposes() -> None:
    calls: list[str] = []

    def fake_run_shell(command, *, cwd, check):
        calls.append(command)
        return _shell_result(0 if "ok" in command else 1, stderr="probe could not confirm")

    ok_payload: dict = {}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), ok_payload, adapter_data={"post_publish_distinct_channel_probe": "probe ok {tag}"},
        run_shell=fake_run_shell, tag_name="v9", expected_release_url="https://x/v9",
    )
    assert ok_payload["distinct_channel_verification"]["status"] == "confirmed"
    assert calls == ["probe ok v9"]  # {tag} substituted, never `gh release view`

    fail_payload: dict = {}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), fail_payload, adapter_data={"post_publish_distinct_channel_probe": "probe bad {url}"},
        run_shell=fake_run_shell, tag_name="v9", expected_release_url="https://x/v9",
    )
    rec = fail_payload["distinct_channel_verification"]
    assert rec["status"] == "not-confirmed"
    assert rec["reason"] == "probe could not confirm"


def test_observer_never_uses_gh_release_view() -> None:
    # The observer's only subprocess hook is run_shell (the adapter probe); it has
    # no `run`/backend handle, so it structurally cannot re-read `gh release view`.
    def fake_run_shell(command, *, cwd, check):
        assert "gh release view" not in command
        return _shell_result(0)

    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), {}, adapter_data={"post_publish_distinct_channel_probe": "probe {tag}"},
        run_shell=fake_run_shell, tag_name="v1", expected_release_url=None,
    )


# --- north-star finding: same-proxy probe is mechanically flagged, not `confirmed` --


def test_observer_flags_probe_matching_release_view_shape_as_same_proxy() -> None:
    def run_shell_never_called(*_args, **_kwargs):
        raise AssertionError("a same-proxy-flagged probe must never be run")

    payload: dict = {}
    backend = {"id": "gh", "commands": None}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), payload, adapter_data={"post_publish_distinct_channel_probe": "gh release view {tag}"},
        run_shell=run_shell_never_called, tag_name="v1.2.3", expected_release_url="https://x/v1.2.3",
        backend=backend, backend_command=_HELPERS.backend_command,
    )
    record = payload["distinct_channel_verification"]
    assert record["status"] == "same-proxy-flagged"
    assert record["status"] != "confirmed"


def test_observer_confirms_genuinely_distinct_probe_with_backend_supplied() -> None:
    calls: list[str] = []

    def fake_run_shell(command, *, cwd, check):
        calls.append(command)
        return _shell_result(0)

    payload: dict = {}
    backend = {"id": "gh", "commands": None}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), payload, adapter_data={"post_publish_distinct_channel_probe": "distinct-channel-probe {tag}"},
        run_shell=fake_run_shell, tag_name="v1.2.3", expected_release_url="https://x/v1.2.3",
        backend=backend, backend_command=_HELPERS.backend_command,
    )
    assert payload["distinct_channel_verification"]["status"] == "confirmed"
    assert calls == ["distinct-channel-probe v1.2.3"]


def test_observer_flags_probe_matching_custom_backend_release_view_shape() -> None:
    # Data-driven: the check derives the forbidden shape from THIS backend's own
    # `release_view` template, not a hardcoded `gh release view` string.
    backend = {"id": "custom-release", "commands": {"release_view": ["custom-release", "release", "view", "{tag}"]}}

    def run_shell_never_called(*_args, **_kwargs):
        raise AssertionError("a same-proxy-flagged probe must never be run")

    payload: dict = {}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), payload, adapter_data={"post_publish_distinct_channel_probe": "custom-release release view {tag}"},
        run_shell=run_shell_never_called, tag_name="v9", expected_release_url="https://x/v9",
        backend=backend, backend_command=_HELPERS.backend_command,
    )
    assert payload["distinct_channel_verification"]["status"] == "same-proxy-flagged"


def test_observer_without_backend_kwargs_skips_the_same_proxy_check() -> None:
    # Back-compat: the mechanical check activates only when a caller supplies
    # `backend`/`backend_command` (every production call site now does). Callers
    # that omit them keep the pre-fix behavior instead of silently misbehaving.
    calls: list[str] = []

    def fake_run_shell(command, *, cwd, check):
        calls.append(command)
        return _shell_result(0)

    payload: dict = {}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), payload, adapter_data={"post_publish_distinct_channel_probe": "gh release view {tag}"},
        run_shell=fake_run_shell, tag_name="v1", expected_release_url="https://x/v1",
    )
    assert payload["distinct_channel_verification"]["status"] == "confirmed"
    assert calls == ["gh release view v1"]


# --- integration wiring: refuse on silence, proceed on presence -----------


def _fake_state() -> dict:
    return {
        "payload": {"tag_name": "v0.0.1"}, "branch": "main", "tag_name": "v0.0.1",
        "title": "v0.0.1", "backend": {"id": "gh"}, "issue_repo": "example/demo",
        "notes_file": None, "expected_release_url": "https://x/releases/tag/v0.0.1",
        "host_payload": {}, "fresh_checkout_payload": {}, "artifact_relpath": "rel.md",
    }


def _base_cli(observer, recorder: dict) -> SimpleNamespace:
    return SimpleNamespace(
        run=lambda *a, **k: _shell_result(0),
        run_shell=lambda *a, **k: _shell_result(0),
        backend_command=lambda *a, **k: ["gh"],
        create_release=lambda *a, **k: _shell_result(0, stdout="https://x/releases/tag/v0.0.1"),
        verify_release_visible=lambda *a, **k: _shell_result(0),
        finalize_release_payload=lambda *a, **k: None,
        confirm_release_via_distinct_channel=observer,
        evaluate_release_distinct_channel=_POST_CREATE.evaluate_release_distinct_channel,
        fail_release_distinct_channel_floor=_POST_CREATE.fail_release_distinct_channel_floor,
        fail_after_post_create_verification=_POST_CREATE.fail_after_post_create_verification,
        commit_final_release_artifact=lambda *a, **k: recorder.__setitem__("committed", k.get("has_issue_closeout")),
        ensure_release_issues_closed=lambda *a, **k: recorder.__setitem__("issues_closed", True),
        run_post_publish_install_refresh=lambda *a, **k: {"status": "not_configured"},
    )


def test_wiring_refuses_issue_close_on_silent_observer() -> None:
    recorder: dict = {}

    def silent_observer(repo_root, payload, **kwargs):
        return None  # records NOTHING — simulates a regression that skips the observer

    args = SimpleNamespace(remote="origin", close_issue=[], close_issue_behavior=[])
    cli = _base_cli(silent_observer, recorder)
    with pytest.raises(SystemExit, match="rung-1 floor refused issue closeout"):
        _EXECUTE._publish_and_finalize(args, Path("."), _fake_state(), {}, cli=cli)
    assert recorder.get("issues_closed") is None  # issue close NEVER reached
    assert recorder.get("committed") is False  # recovery artifact committed (no issue closeout)


def test_wiring_proceeds_to_issue_close_on_recorded_disposition() -> None:
    recorder: dict = {}

    def disposing_observer(repo_root, payload, **kwargs):
        payload["distinct_channel_verification"] = {"channel": "none", "status": "skipped", "reason": "x"}

    args = SimpleNamespace(remote="origin", close_issue=[44], close_issue_behavior=["Behavior #44: x"])
    cli = _base_cli(disposing_observer, recorder)
    _EXECUTE._publish_and_finalize(args, Path("."), _fake_state(), {}, cli=cli)
    # F2a: a typed disposition (not a confirmation) still advances the close.
    assert recorder.get("issues_closed") is True
