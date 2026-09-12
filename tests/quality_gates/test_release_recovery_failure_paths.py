"""Meaningful failure and retry coverage for release-resume recovery."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from .release_resume_edge_support import (
    ClaimsResumeCli,
    ClaimsResumeCommon,
    ClassifierCli,
    ResumeCli,
)
from .release_script_loading import load_release_script

RESUME = load_release_script("publish_release_resume", suffix="failure_paths")
RESUME_CLOSEOUT = load_release_script(
    "publish_release_resume_closeout", suffix="failure_paths"
)
RESUME_PUBLISH = load_release_script(
    "publish_release_resume_publish", suffix="failure_paths"
)
RESUME_STATE = load_release_script(
    "publish_release_resume_state", suffix="failure_paths"
)

ADAPTER = {"output_dir": "charness-artifacts/release"}
RECORD_PATH = "charness-artifacts/release/latest.md"


def _plan() -> dict:
    return {
        "payload": {
            "commit_message": "Release demo 1.2.3",
            "previous_version": "1.2.2",
            "target_version": "1.2.3",
        },
        "tag_name": "v1.2.3",
        "branch": "main",
        "backend": "github",
        "issue_repo": "example/demo",
        "title": "v1.2.3",
    }


def _args(*, execute: bool, close_issue=None, **extra):
    values = {
        "execute": execute,
        "remote": "origin",
        "notes_file": None,
        "close_issue": [] if close_issue is None else close_issue,
        "close_issue_classification": None,
        "close_issue_carrier_file": None,
        "close_issue_behavior": [],
        "close_issue_probe_record": [],
        "claims_review_artifact": "charness-artifacts/release-review/review.json",
    }
    values.update(extra)
    return SimpleNamespace(**values)


def _claims_state() -> dict:
    return {
        "phase": "prepared-claims-review",
        "tag_local": True,
        "tag_remote": True,
        "tag_sha": "prepared-sha",
        "remote_tag_sha": "prepared-sha",
        "remote_branch_sha": "claims-evidence-sha",
        "claims_evidence_commit": "claims-evidence-sha",
        "head_sha": "claims-evidence-sha",
        "prepared": {"commit": "prepared-sha"},
        "release_exists": True,
        "record_path": RECORD_PATH,
        "claims_review": {
            "path": "charness-artifacts/release-review/review.json",
            "verdict": "pass",
            "observer_distinctness": {"signal": "separate reviewer"},
        },
    }


def _legacy_state() -> dict:
    return {
        "phase": "release-content",
        "release_exists": True,
        "record_path": RECORD_PATH,
        "head_sha": "release-sha",
        "tag_remote": True,
        "tag_local": True,
        "remote_branch_sha": "release-sha",
    }


def _run_publish_with_validator(tmp_path: Path, validator) -> ClaimsResumeCli:
    commands: list[list[str]] = []
    cli = ClaimsResumeCli(commands)
    with pytest.raises(SystemExit):
        RESUME_PUBLISH.resume_publish(
            tmp_path,
            args=_args(execute=True),
            plan=_plan(),
            adapter_data=ADAPTER,
            cli=cli,
            state=_claims_state(),
            resumable_state=lambda *_args, **_kwargs: _claims_state(),
            assert_resumable=lambda *_args, **_kwargs: None,
            common=ClaimsResumeCommon(),
            resume_closeout=SimpleNamespace(),
            commit_artifact_before_push=lambda *_args, **_kwargs: None,
            release_record_path=lambda _adapter: RECORD_PATH,
            claims_review_validator=validator,
        )
    return cli


def _raise_explicit_refusal(_repo_root, _state):
    raise SystemExit("explicit validator refusal")


def _raise_os_error(_repo_root, _state):
    raise OSError("claims evidence disappeared")


@pytest.mark.parametrize(
    ("validator", "message"),
    [
        (None, "no claims-review validator"),
        (_raise_explicit_refusal, "explicit validator refusal"),
        (_raise_os_error, "revalidation failed at the publication boundary"),
        (lambda _repo, _state: {"verdict": "reject"}, "not a validated pass or unproven"),
    ],
)
def test_claims_boundary_refuses_or_propagates_before_any_publish_command(
    tmp_path: Path, validator, message: str
) -> None:
    """A reconstructed claims state cannot publish without boundary revalidation."""
    cli = _run_publish_with_validator(tmp_path, validator)

    assert cli.commands == [], "claims refusal must happen before auth, push, or release creation"


def test_resume_entrypoint_binds_its_boundary_validator_into_the_publish_consumer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    """The public resume entrypoint supplies the exact prepared/evidence binding."""
    calls: list[dict] = []

    def validate(_repo_root: Path, **kwargs):
        calls.append(kwargs)
        return {
            "path": kwargs["artifact_path"],
            "verdict": "pass",
            "observer_distinctness": {"signal": "revalidated"},
        }

    monkeypatch.setitem(RESUME._claims_review, "validate_claims_review", validate)
    monkeypatch.setattr(RESUME, "_common", ClaimsResumeCommon())
    monkeypatch.setattr(
        RESUME, "_commit_artifact_before_push", lambda *_args, **_kwargs: None
    )
    commands: list[list[str]] = []
    cli = ClaimsResumeCli(commands)
    args = _args(execute=True)

    RESUME.resume_publish(
        tmp_path,
        args=args,
        plan=_plan(),
        adapter_data=ADAPTER,
        cli=cli,
        state=_claims_state(),
    )

    assert len(calls) == 1
    assert calls[0]["prepared"] == {"commit": "prepared-sha"}
    assert calls[0]["evidence_commit"] == "claims-evidence-sha"
    assert calls[0]["artifact_path"] == args.claims_review_artifact
    assert calls[0]["target_version"] == "1.2.3"
    assert calls[0]["tag_name"] == "v1.2.3"
    assert calls[0]["previous_version"] == "1.2.2"
    assert cli.finalized_payloads[0]["claims_review"]["verdict"] == "pass"
    assert not any(command[:2] == ["git", "push"] for command in commands)
    assert yaml.safe_load(capsys.readouterr().out)["expected_release_url"] == (
        "https://example.test/v1.2.3"
    )


def test_resume_publish_dry_run_skips_claims_revalidation_for_legacy_content(
    capsys, tmp_path: Path
) -> None:
    """The legacy lane remains a non-claims dry run and cannot mutate refs."""
    commands: list[list[str]] = []
    cli = ClaimsResumeCli(commands)

    RESUME_PUBLISH.resume_publish(
        tmp_path,
        args=_args(execute=False),
        plan=_plan(),
        adapter_data=ADAPTER,
        cli=cli,
        state=_legacy_state(),
        resumable_state=lambda *_args, **_kwargs: _legacy_state(),
        assert_resumable=lambda *_args, **_kwargs: None,
        common=ClaimsResumeCommon(),
        resume_closeout=SimpleNamespace(),
        commit_artifact_before_push=lambda *_args, **_kwargs: None,
        release_record_path=lambda _adapter: RECORD_PATH,
    )

    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["resume"] == (
        "dry-run: would re-validate gates, create missing refs, then publish the existing release commit"
    )
    assert commands == []


class _PendingCli(ResumeCli):
    def run(self, command, *, cwd, check=True):
        if command == ["git", "rev-parse", "HEAD"]:
            self.commands.append(command)
            return SimpleNamespace(returncode=0, stdout="tag-sha\n")
        return super().run(command, cwd=cwd, check=check)


def _pending_case(*, execute: bool, close_issue=None):
    cli = _PendingCli(changed=[], files={})
    preflight_calls: list[dict] = []
    tail_calls: list[dict] = []
    common = SimpleNamespace(
        preflight_close_issue_carrier=lambda *_args, **kwargs: preflight_calls.append(kwargs),
        run_release_closeout_tail=lambda *_args, **kwargs: tail_calls.append(kwargs),
    )
    args = _args(execute=execute, close_issue=close_issue)
    state = {
        "phase": "post-publication-pending",
        "record_path": RECORD_PATH,
        "tag_sha": "tag-sha",
        "head_sha": "tag-sha",
        "remote_branch_sha": "tag-sha",
    }
    plan = _plan()
    return cli, common, args, state, plan, preflight_calls, tail_calls


def test_pending_closeout_requires_original_issue_inputs_before_preflight() -> None:
    cli, common, args, state, plan, preflight_calls, _tail_calls = _pending_case(
        execute=True, close_issue=[44]
    )

    with pytest.raises(SystemExit, match="--close-issue-classification"):
        RESUME_CLOSEOUT.resume_post_publication_closeout(
            Path("."),
            args=args,
            plan=plan,
            adapter_data=ADAPTER,
            state=state,
            common=common,
            cli=cli,
        )

    assert preflight_calls == []
    assert cli.commands == []


def test_pending_closeout_dry_run_reports_a_retryable_published_boundary(capsys) -> None:
    cli, common, args, state, plan, preflight_calls, _tail_calls = _pending_case(
        execute=False
    )

    RESUME_CLOSEOUT.resume_post_publication_closeout(
        Path("."),
        args=args,
        plan=plan,
        adapter_data=ADAPTER,
        state=state,
        common=common,
        cli=cli,
    )

    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["resume"] == "dry-run: would continue pending post-publication closeout"
    assert payload["resume_state"]["phase"] == "post-publication-pending"
    assert preflight_calls == []
    assert cli.commands == []


def test_pending_closeout_retries_visibility_and_tail_from_the_published_tag(capsys) -> None:
    cli, common, args, state, plan, preflight_calls, tail_calls = _pending_case(
        execute=True, close_issue=[44]
    )
    args.close_issue_classification = "bug"
    args.close_issue_carrier_file = Path("carrier.md")
    args.close_issue_behavior = ["Behavior #44: confirmed"]
    args.close_issue_probe_record = ["Probe record #44: local-only"]
    cli.expected_github_release_url = lambda *_args: "https://example.test/v1.2.3"
    cli.run_fresh_checkout_probes = lambda *_args: {"status": "passed"}
    cli.verify_release_visible = lambda *_args, **_kwargs: SimpleNamespace(returncode=0)
    cli.backend_command = lambda *_args: ["gh"]
    finalize_calls: list[dict] = []
    cli.finalize_release_payload = (
        lambda _root, _payload, **kwargs: finalize_calls.append(kwargs)
    )

    RESUME_CLOSEOUT.resume_post_publication_closeout(
        Path("."),
        args=args,
        plan=plan,
        adapter_data=ADAPTER,
        state=state,
        common=common,
        cli=cli,
    )

    assert preflight_calls[0]["carrier_source"] == "release-resume-closeout"
    assert finalize_calls[0]["artifact_relpath"] == RECORD_PATH
    assert finalize_calls[0]["commit_sha"] == "tag-sha"
    assert finalize_calls[0]["release_verified"] is True
    assert tail_calls[0]["carrier_source"] == "release-resume-closeout"
    assert tail_calls[0]["state"]["artifact_relpath"] == RECORD_PATH
    assert cli.commands == [["git", "rev-parse", "HEAD"]]
    assert yaml.safe_load(capsys.readouterr().out)["resume"] == (
        "pending post-publication closeout completed"
    )


def test_published_tag_only_state_classifies_as_pending_closeout() -> None:
    state = RESUME_STATE.resumable_state(
        Path("."),
        tag_name="v1.2.3",
        commit_message="Release demo 1.2.3",
        remote="origin",
        branch="main",
        backend={},
        record_path=RECORD_PATH,
        cli=ClassifierCli(
            revs={"HEAD": "tag-sha", "tag": "tag-sha"},
            subject="Release demo 1.2.3",
            messages={"HEAD": "Release demo 1.2.3"},
        ),
    )

    assert state["phase"] == "post-publication-pending"
    assert state["head_sha"] == state["tag_sha"] == "tag-sha"
    assert state["tag_local"] is True
    assert state["tag_remote"] is True
    assert state["release_exists"] is True


class _InvalidReceiptOwner:
    def __init__(self, root: Path, *, fail_retention: bool):
        self.path = root / "scratch"
        self.fail_retention = fail_retention
        self.promoted: list[Path] = []
        self.retention_attempts: list[dict] = []
        self.closed: list[str] = []

    def open(self) -> Path:
        self.path.mkdir()
        (self.path / "receipt.json").write_text("{not-json\n", encoding="utf-8")
        return self.path

    def promote_file(self, source: Path, destination: Path) -> Path:
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(Path(source).read_bytes())
        self.promoted.append(destination)
        return destination

    def retain_failed_promotion(self, **kwargs) -> None:
        self.retention_attempts.append(kwargs)
        if self.fail_retention:
            raise RuntimeError("owner retention unavailable")

    def close(self, *, state: str) -> None:
        self.closed.append(state)


class _QualityFailureCommon(ClaimsResumeCommon):
    @staticmethod
    def run_pre_push_quality_gates(*_args, **_kwargs):
        raise RuntimeError("quality gate stopped before publication")


@pytest.mark.parametrize("fail_retention", [False, True])
def test_late_receipt_promotion_failure_retains_fallback_before_owner_close(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fail_retention: bool
) -> None:
    """A late failure keeps the promoted bytes inspectable even if retention itself fails."""
    owner = _InvalidReceiptOwner(tmp_path, fail_retention=fail_retention)
    monkeypatch.setattr(RESUME_PUBLISH, "owned_scratch", lambda *_args, **_kwargs: owner)
    cli = ClaimsResumeCli([])

    with pytest.raises(SystemExit, match="promoted quality receipt owner record is unreadable"):
        RESUME_PUBLISH.resume_publish(
            tmp_path,
            args=_args(execute=True),
            plan=_plan(),
            adapter_data=ADAPTER,
            cli=cli,
            state=_legacy_state(),
            resumable_state=lambda *_args, **_kwargs: _legacy_state(),
            assert_resumable=lambda *_args, **_kwargs: None,
            common=_QualityFailureCommon(),
            resume_closeout=SimpleNamespace(),
            commit_artifact_before_push=lambda *_args, **_kwargs: None,
            release_record_path=lambda _adapter: RECORD_PATH,
        )

    assert len(owner.promoted) == 1
    assert owner.promoted[0].read_text(encoding="utf-8") == "{not-json\n"
    assert len(owner.retention_attempts) == 1
    assert owner.retention_attempts[0]["recovery_reason"] == (
        "quality receipt promotion/read-back failed"
    )
    assert owner.closed == ["failed"]
