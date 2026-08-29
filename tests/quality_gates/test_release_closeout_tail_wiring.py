"""The release closeout TAIL's wiring: what runs, in what order, and what refuses.

Split from `test_release_distinct_channel.py` when that file crossed its length
cap. The boundary is the subject, not the line count: the sibling owns the rung-1
floor and the rung-2 observer as VERDICT functions -- pure evaluations over a
payload -- while everything here drives `run_release_closeout_tail` and asserts
the ORDER its side effects happen in, and that a silent observer or a failed
carrier stops the irreversible issue close.

These cases used to reach the tail through
`publish_release_execute._publish_and_finalize`, whose own docstring said it was
"UNREACHABLE in production ... its only live callers are tests". They now drive
the owner `resume_publish` actually calls.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from .release_script_loading import load_release_script

_COMMON = load_release_script("publish_release_common")
_POST_CREATE = load_release_script("publish_release_post_create")


def _shell_result(returncode: int, stdout: str = "", stderr: str = ""):
    """Local, not imported from the sibling: a cross-module private import makes a
    TEST FILE the owner of a shared helper, which is the coupling that broke
    `test_markdown_lint_resolution.py` when its helper was promoted this session."""

    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def _fake_state() -> dict:
    return {
        "payload": {"tag_name": "v0.0.1"}, "branch": "main", "tag_name": "v0.0.1",
        "title": "v0.0.1", "backend": {"id": "gh"}, "issue_repo": "example/demo",
        "notes_file": None, "expected_release_url": "https://x/releases/tag/v0.0.1",
        "fresh_checkout_payload": {}, "artifact_relpath": "rel.md",
    }


def _run_closeout_tail(args, cli, state: dict | None = None) -> None:
    """Drive the LIVE tail: the one `resume_publish` actually calls.

    These cases used to reach it through `publish_release_execute._publish_and_finalize`,
    whose own docstring says it is "UNREACHABLE in production ... its only live callers
    are tests" -- `execute_publish_plan` stops at the prepared record and publication
    happens in `resume_publish`. So the only execution coverage of the
    carrier -> issue-state-readback -> final-artifact ordering and the rung-1 floor
    reached them through a driver no release ever runs.

    `run_release_closeout_tail` is the owner both production callers invoke
    identically (`publish_release_resume_publish.py:218`, and the deleted wrapper),
    so driving it directly covers the live path rather than a dead copy of it.
    `carrier_source` is spelled as the live resume caller spells it.
    """

    state = state if state is not None else _fake_state()
    _COMMON.run_release_closeout_tail(
        Path("."),
        args=args,
        adapter_data={},
        state=state,
        issue_repo=state["issue_repo"],
        payload=state["payload"],
        cli=cli,
        carrier_source="release-resume",
    )


def _base_cli(observer, recorder: dict) -> SimpleNamespace:
    events = recorder.setdefault("events", [])

    def record_final(*_args, **kwargs):
        events.append(("final-artifact", kwargs.get("has_issue_closeout")))
        recorder["committed"] = kwargs.get("has_issue_closeout")

    return SimpleNamespace(
        run=lambda *a, **k: _shell_result(0),
        run_shell=lambda *a, **k: _shell_result(0),
        backend_command=lambda *a, **k: ["gh"],
        create_release=lambda *a, **k: _shell_result(0, stdout="https://x/releases/tag/v0.0.1"),
        verify_release_visible=lambda *a, **k: _shell_result(0),
        finalize_release_payload=lambda *a, **k: None,
        confirm_release_via_distinct_channel=observer,
        # The `--generate-notes` path publishes a body nothing inspected
        # pre-publish, so the wiring reads it back and audits it post-create.
        audit_published_release_body=_POST_CREATE.audit_published_release_body,
        audit_notes_text=lambda text, **k: [],
        evaluate_release_distinct_channel=_POST_CREATE.evaluate_release_distinct_channel,
        reconcile_public_release_verification=_POST_CREATE.reconcile_public_release_verification,
        fail_release_distinct_channel_floor=_POST_CREATE.fail_release_distinct_channel_floor,
        fail_after_post_create_verification=_POST_CREATE.fail_after_post_create_verification,
        commit_final_release_artifact=record_final,
        commit_issue_closeout_carrier_artifact=lambda *a, **k: events.append(("carrier-artifact", True)),
        ensure_release_issues_closed=lambda *a, **k: (
            events.append(("issue-state-readback", True)),
            recorder.__setitem__("issues_closed", True),
        ),
        run_post_publish_install_refresh=lambda *a, **k: {"status": "not_configured"},
        collect_installed_readback=lambda *a, **k: {"status": "not_configured"},
        safe_write_release_observer=lambda *a, **k: {
            "status": "not_configured",
            "path": "charness-artifacts/probe/test.json",
        },
    )


def test_wiring_refuses_issue_close_on_silent_observer() -> None:
    recorder: dict = {}

    def silent_observer(repo_root, payload, **kwargs):
        return None  # records NOTHING — simulates a regression that skips the observer

    args = SimpleNamespace(remote="origin", close_issue=[], close_issue_behavior=[], close_issue_probe_record=[])
    cli = _base_cli(silent_observer, recorder)
    with pytest.raises(SystemExit, match="rung-1 floor refused issue closeout"):
        _run_closeout_tail(args, cli)
    assert recorder.get("issues_closed") is None  # issue close NEVER reached
    assert recorder.get("committed") is False  # recovery artifact committed (no issue closeout)


def test_wiring_proceeds_to_issue_close_on_recorded_disposition() -> None:
    recorder: dict = {}

    def disposing_observer(repo_root, payload, **kwargs):
        payload["distinct_channel_verification"] = {"channel": "none", "status": "skipped", "reason": "x"}

    args = SimpleNamespace(remote="origin", close_issue=[44], close_issue_behavior=["Behavior #44: x"],
        close_issue_probe_record=["Probe record #44: local-only-by-contract"])
    cli = _base_cli(disposing_observer, recorder)
    _run_closeout_tail(args, cli)
    # F2a: a typed disposition (not a confirmation) still advances the close.
    assert recorder.get("issues_closed") is True
    assert recorder["events"] == [
        ("carrier-artifact", True),
        ("issue-state-readback", True),
        ("final-artifact", True),
    ]


def test_carrier_commit_failure_prevents_issue_state_mutation() -> None:
    recorder: dict = {}

    def confirmed_observer(_repo_root, payload, **_kwargs):
        payload["distinct_channel_verification"] = {
            "channel": "https-fetch",
            "status": "confirmed",
        }

    cli = _base_cli(confirmed_observer, recorder)

    def fail_carrier(*_args, **_kwargs):
        recorder["events"].append(("carrier-artifact", "failed"))
        raise RuntimeError("carrier push failed")

    cli.commit_issue_closeout_carrier_artifact = fail_carrier
    args = SimpleNamespace(remote="origin", close_issue=[44], close_issue_behavior=["Behavior #44: x"],
        close_issue_probe_record=["Probe record #44: local-only-by-contract"])

    with pytest.raises(RuntimeError, match="carrier push failed"):
        _run_closeout_tail(args, cli)

    assert recorder.get("issues_closed") is None
    assert recorder.get("committed") is None
    assert recorder["events"] == [("carrier-artifact", "failed")]
