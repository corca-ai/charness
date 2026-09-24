"""Post-publication closeout must stop when the release is no longer visible.

The pre-publication lane refuses an unverified release before issue closeout
(`fail_after_post_create_verification`). These cases pin the same floor on the
two recovery lanes, which recorded `release_verified: False` and continued
into the closeout tail: the verification record is committed first (mirroring
that lane) and the tail -- carrier commits, issue closes, final artifact --
never runs.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from .release_resume_edge_support import ResumeCli
from .release_script_loading import load_release_script

RESUME_CLOSEOUT = load_release_script("publish_release_resume_closeout")
RECORD_PATH = "charness-artifacts/release/latest.md"
OBSERVER = "charness-artifacts/probe/demo-v1.2.3-release-observer.json"
MESSAGE = "carrier message"


def _cli(*, verify_returncode: int, recorder: dict) -> ResumeCli:
    cli = ResumeCli(
        changed=[RECORD_PATH, OBSERVER],
        files={
            RECORD_PATH: f"{OBSERVER}\ncarrier-pending-state-verification",
            OBSERVER: json.dumps({"target": {"tag": "v1.2.3"}}),
        },
    )
    cli.expected_github_release_url = lambda *_args: "https://example.test/v1.2.3"
    cli.backend_command = lambda *_args: ["gh"]
    cli.run_fresh_checkout_probes = lambda *_args: {"status": "passed"}
    cli.verify_release_visible = lambda *_args, **_kwargs: SimpleNamespace(
        returncode=verify_returncode,
        args=["gh", "release", "view", "v1.2.3"],
        stdout="",
        stderr="" if verify_returncode == 0 else "release not found",
    )
    cli.finalize_release_payload = lambda _root, payload, **_kwargs: recorder.setdefault(
        "finalized", []
    ).append(dict(payload))
    cli.commit_final_release_artifact = lambda *_args, **kwargs: recorder.setdefault(
        "final_commits", []
    ).append(kwargs)

    def fail_unverified(_payload, *, verification_result):
        raise SystemExit(
            "release post-create verification failed after external mutation\n"
            f"exit_code: {verification_result.returncode}"
        )

    cli.fail_after_post_create_verification = fail_unverified
    return cli


def _common(recorder: dict) -> SimpleNamespace:
    calls = recorder["tail_calls"]
    return SimpleNamespace(
        preflight_close_issue_carrier=lambda *_args, **_kwargs: None,
        run_release_closeout_tail=lambda *_args, **kwargs: calls.append(kwargs),
    )


def _plan(payload: dict) -> dict:
    return {
        "payload": payload,
        "issue_repo": "example/demo",
        "tag_name": "v1.2.3",
        "branch": "main",
        "backend": {"id": "gh"},
    }


def _closeout_args(**overrides) -> SimpleNamespace:
    base = {
        "execute": True,
        "close_issue": [44],
        "close_issue_classification": "bug",
        "close_issue_carrier_file": Path("carrier.md"),
        "close_issue_behavior": ["Behavior #44: fixture"],
        "close_issue_probe_record": ["Probe record #44: local-only-by-contract"],
        "remote": "origin",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_carrier_closeout_stops_when_reverification_fails() -> None:
    recorder: dict = {"tail_calls": []}
    cli = _cli(verify_returncode=1, recorder=recorder)
    common = _common(recorder)
    payload = {"issue_closeout_draft_validation": {"commit_message": MESSAGE}}
    state = {
        "phase": "post-publication-carrier",
        "head_message": MESSAGE,
        "head_sha": "carrier-sha",
        "remote_branch_sha": "carrier-sha",
        "record_path": RECORD_PATH,
    }

    with pytest.raises(SystemExit, match="post-create verification failed"):
        RESUME_CLOSEOUT.resume_post_publication_closeout(
            Path("."),
            args=_closeout_args(),
            plan=_plan(payload),
            adapter_data={"output_dir": "charness-artifacts/release"},
            state=state,
            common=common,
            cli=cli,
        )

    assert recorder["tail_calls"] == [], "no carrier, issue close, or final commit may run"
    assert len(recorder["final_commits"]) == 1
    assert recorder["final_commits"][0]["has_issue_closeout"] is False
    assert recorder["finalized"], "the failed verification itself is still finalized"


def test_carrier_closeout_runs_the_tail_when_reverification_passes() -> None:
    recorder: dict = {"tail_calls": []}
    cli = _cli(verify_returncode=0, recorder=recorder)
    common = _common(recorder)
    payload = {"issue_closeout_draft_validation": {"commit_message": MESSAGE}}
    state = {
        "phase": "post-publication-carrier",
        "head_message": MESSAGE,
        "head_sha": "carrier-sha",
        "remote_branch_sha": "carrier-sha",
        "record_path": RECORD_PATH,
    }

    RESUME_CLOSEOUT.resume_post_publication_closeout(
        Path("."),
        args=_closeout_args(),
        plan=_plan(payload),
        adapter_data={"output_dir": "charness-artifacts/release"},
        state=state,
        common=common,
        cli=cli,
    )

    assert len(recorder["tail_calls"]) == 1
    assert recorder.get("final_commits", []) == []


def test_pending_closeout_stops_when_reverification_fails() -> None:
    recorder: dict = {"tail_calls": []}
    cli = _cli(verify_returncode=1, recorder=recorder)
    common = _common(recorder)
    payload: dict = {}
    state = {
        "phase": "post-publication-pending",
        "head_sha": "tag-sha",
        "tag_sha": "tag-sha",
        "tag_local": True,
        "tag_remote": True,
        "release_exists": True,
        "remote_branch_sha": "tag-sha",
        "record_path": RECORD_PATH,
    }

    with pytest.raises(SystemExit, match="post-create verification failed"):
        RESUME_CLOSEOUT.resume_post_publication_closeout(
            Path("."),
            args=_closeout_args(close_issue=[]),
            plan=_plan(payload),
            adapter_data={"output_dir": "charness-artifacts/release"},
            state=state,
            common=common,
            cli=cli,
        )

    assert recorder["tail_calls"] == [], "no closeout tail may run over an unverified release"
    assert len(recorder["final_commits"]) == 1


def test_closeout_refusal_loader_refuses_a_broken_spec(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        RESUME_CLOSEOUT.importlib.util, "spec_from_file_location", lambda *args, **kwargs: None
    )

    with pytest.raises(ImportError, match="Unable to load"):
        RESUME_CLOSEOUT._load_closeout_refusal()
