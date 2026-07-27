from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from .release_script_loading import load_release_script

OBSERVER = load_release_script("release_observer")
ARTIFACT_SECTIONS = load_release_script("publish_release_artifact_sections")
HELPERS = load_release_script("publish_release_helpers")


def _result(returncode: int, stdout: str = "", stderr: str = "") -> SimpleNamespace:
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def _payload() -> dict:
    return {
        "target_version": "2.1.5",
        "tag_name": "v2.1.5",
        "commit_sha": "abc123",
        "release_url": "https://example.test/releases/tag/v2.1.5",
        "distinct_channel_verification": {
            "channel": "https-fetch",
            "status": "confirmed",
            "url": "https://example.test/releases/tag/v2.1.5",
        },
    }


def test_release_observer_persists_canonical_channel_and_installed_readback(tmp_path: Path) -> None:
    commands: list[str] = []

    def run_shell(command: str, **_kwargs):
        commands.append(command)
        if command == "charness version":
            return _result(0, "version: 2.1.5\n")
        return _result(0, "status: healthy\n")

    installed = OBSERVER.collect_installed_readback(
        tmp_path,
        install_refresh={"status": "refreshed", "command": "charness update"},
        version_command="charness version",
        doctor_command="charness doctor",
        run_shell=run_shell,
    )
    payload = _payload()
    out = OBSERVER.write_release_observer(
        tmp_path,
        payload=payload,
        installed_readback=installed,
        now=lambda: datetime(2026, 7, 19, 1, 2, tzinfo=timezone.utc),
    )

    assert out["path"] == "charness-artifacts/probe/2026-07-19-v2.1.5-release-observer.json"
    record = json.loads((tmp_path / out["path"]).read_text(encoding="utf-8"))
    assert record["distinct_channel_verification"] == payload["distinct_channel_verification"]
    assert record["installed_readback"]["status"] == "observed"
    assert record["installed_readback"]["version"]["value"] == "version: 2.1.5"
    assert commands == ["charness version", "charness doctor"]
    assert not any("verdict" in key for key in record if key != "distinct_channel_verification")


def test_release_observer_records_unavailable_readbacks_without_false_success(tmp_path: Path) -> None:
    installed = OBSERVER.collect_installed_readback(
        tmp_path,
        install_refresh={"status": "failed", "command": "charness update"},
        version_command="",
        doctor_command="charness doctor",
        run_shell=lambda *_a, **_k: _result(2, stderr="doctor unavailable"),
    )
    out = OBSERVER.write_release_observer(
        tmp_path,
        payload=_payload(),
        installed_readback=installed,
        now=lambda: datetime(2026, 7, 19, tzinfo=timezone.utc),
    )

    assert out["status"] == "unavailable"
    record = out["record"]
    assert record["installed_readback"]["version"]["status"] == "unavailable"
    assert record["installed_readback"]["version"]["reason"] == "adapter readback command is not configured"
    assert record["installed_readback"]["doctor"]["status"] == "unavailable"
    assert record["non_claims"]


def test_release_observer_converts_runner_exception_to_unavailable(tmp_path: Path) -> None:
    def fail(*_args, **_kwargs):
        raise OSError("binary disappeared")

    installed = OBSERVER.collect_installed_readback(
        tmp_path,
        install_refresh={"status": "refreshed"},
        version_command="charness version",
        doctor_command="charness doctor",
        run_shell=fail,
    )
    assert installed["status"] == "unavailable"
    assert installed["version"]["reason"] == "OSError: binary disappeared"
    assert installed["doctor"]["reason"] == "OSError: binary disappeared"


def test_release_observer_persistence_error_is_typed_and_nonblocking(tmp_path: Path) -> None:
    payload = _payload()
    payload["commit_sha"] = ""  # forces schema validation failure before any write
    out = OBSERVER.safe_write_release_observer(
        tmp_path,
        payload=payload,
        installed_readback={"status": "unavailable"},
    )
    assert out["status"] == "capture_error"
    assert out["path"] is None
    assert "target.commit" in out["reason"]
    assert out["non_claims"]


def test_release_observer_capture_error_renders_unavailable_record_disposition() -> None:
    lines = ARTIFACT_SECTIONS.release_observer_lines(
        {
            "status": "capture_error",
            "path": None,
            "reason": "ValueError: target commit is missing",
        }
    )

    assert "- Durable observer record: unavailable; see the capture disposition below." in lines
    assert "- Installed readback disposition: `capture_error`." in lines
    assert "- Capture disposition: ValueError: target commit is missing" in lines


def test_distinct_channel_section_renders_observer_identity() -> None:
    # The rung-2 audit reads the markdown section, so the observer identity
    # recorded on the verification record must surface there, not only in the
    # persisted JSON probe artifact.
    observer = "unauthenticated-http (credential-free; same host/process as publisher)"
    lines = ARTIFACT_SECTIONS.distinct_channel_verification_lines(
        {
            "channel": "https-fetch",
            "observer": observer,
            "status": "confirmed",
            "url": "https://x/v9",
            "http_status": 200,
        }
    )
    assert f"- Observer identity: {observer}" in lines


def test_post_publish_artifact_commits_untracked_observer_after_git_tracking_check_fails(tmp_path: Path) -> None:
    calls: list[list[str]] = []
    writes: list[dict] = []

    def run_command(command: list[str], **_kwargs):
        calls.append(command)
        if command[:3] == ["git", "diff", "--quiet"]:
            return _result(0)
        if command[:3] == ["git", "ls-files", "--error-unmatch"]:
            return _result(1, stderr="path is untracked")
        if command == ["git", "rev-parse", "HEAD"]:
            return _result(0, "post-publish-sha\n")
        return _result(0)

    payload = {
        "tag_name": "v2.1.5",
        "release_observer": {"path": "charness-artifacts/probe/observer.json"},
    }
    HELPERS.commit_post_publish_artifact(
        tmp_path,
        write_artifact=lambda **kwargs: writes.append(kwargs),
        payload=payload,
        fresh_checkout_payload={"status": "passed"},
        artifact_relpath="charness-artifacts/release/latest.md",
        expected_release_url="https://example.test/releases/tag/v2.1.5",
        remote="origin",
        branch="main",
        run_command=run_command,
    )

    assert writes == [
        {
            "fresh_checkout_payload": {"status": "passed"},
            "release_url": "https://example.test/releases/tag/v2.1.5",
            "issue_closeout": None,
        }
    ]
    assert calls == [
        ["git", "diff", "--quiet", "--", "charness-artifacts/release/latest.md", "charness-artifacts/probe/observer.json"],
        ["git", "ls-files", "--error-unmatch", "charness-artifacts/probe/observer.json"],
        ["git", "add", "charness-artifacts/release/latest.md", "charness-artifacts/probe/observer.json"],
        ["git", "commit", "-m", "Record release verification for v2.1.5"],
        ["git", "push", "origin", "main"],
        ["git", "rev-parse", "HEAD"],
    ]
    assert payload["post_publish_artifact_commit_sha"] == "post-publish-sha"


@pytest.mark.parametrize(
    "mutate, match",
    [
        (lambda record: record["target"].__setitem__("commit", ""), "target.commit"),
        (lambda record: record.__setitem__("distinct_channel_verification", {}), "channel"),
        (lambda record: record.__setitem__("installed_readback", {}), "installed_readback.status"),
        (lambda record: record.__setitem__("non_claims", []), "non_claims"),
    ],
)
def test_release_observer_validator_rejects_incomplete_evidence(mutate, match: str) -> None:
    record = {
        "schema_version": "charness.release_observer.v1",
        "target": {
            "version": "2.1.5",
            "tag": "v2.1.5",
            "commit": "abc123",
            "release_url": "https://example.test/v2.1.5",
        },
        "distinct_channel_verification": {"channel": "https-fetch", "status": "confirmed"},
        "installed_readback": {"status": "observed"},
        "non_claims": ["not terminal proof"],
    }
    mutate(record)
    with pytest.raises(ValueError, match=match):
        OBSERVER.validate_release_observer_record(record)


@pytest.mark.parametrize(
    "record, match",
    [
        (None, "record must be an object"),
        ({"schema_version": "wrong"}, "schema_version"),
        ({"schema_version": OBSERVER.SCHEMA_VERSION, "target": None}, "target.*must be an object"),
        (
            {"schema_version": OBSERVER.SCHEMA_VERSION, "target": {}},
            "target.version",
        ),
        (
            {
                "schema_version": OBSERVER.SCHEMA_VERSION,
                "target": {"version": "v", "tag": "t", "commit": "c", "release_url": "u"},
                "distinct_channel_verification": None,
            },
            "distinct_channel_verification.*must be an object",
        ),
        (
            {
                "schema_version": OBSERVER.SCHEMA_VERSION,
                "target": {"version": "v", "tag": "t", "commit": "c", "release_url": "u"},
                "distinct_channel_verification": {"channel": "channel", "status": "status"},
                "installed_readback": None,
            },
            "installed_readback.*must be an object",
        ),
        (
            {
                "schema_version": OBSERVER.SCHEMA_VERSION,
                "target": {"version": "v", "tag": "t", "commit": "c", "release_url": "u"},
                "distinct_channel_verification": {"channel": "channel", "status": "status"},
                "installed_readback": {"status": "observed"},
                "non_claims": [""],
            },
            "non_claims\\[0\\]",
        ),
    ],
)
def test_release_observer_validator_rejects_each_remaining_schema_branch(record, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        OBSERVER.validate_release_observer_record(record)


def test_release_observer_readback_failure_has_unavailable_status_and_fallback_reason(tmp_path: Path) -> None:
    installed = OBSERVER.collect_installed_readback(
        tmp_path,
        install_refresh={"status": "refreshed"},
        version_command="charness version",
        doctor_command="charness doctor",
        run_shell=lambda *_args, **_kwargs: _result(1),
    )

    assert installed["status"] == "unavailable"
    assert installed["version"] == {
        "status": "unavailable",
        "command": "charness version",
        "returncode": 1,
        "reason": "readback command failed",
    }
    assert installed["doctor"]["status"] == "unavailable"


def test_release_observer_unknown_refresh_stays_fail_closed(tmp_path: Path) -> None:
    installed = OBSERVER.collect_installed_readback(
        tmp_path,
        install_refresh={},
        version_command="charness version",
        doctor_command="charness doctor",
        run_shell=lambda *_args, **_kwargs: _result(0, "confirmed\n"),
    )

    assert installed["status"] == "unavailable"
    assert installed["version"]["status"] == "confirmed"
    assert installed["doctor"]["status"] == "confirmed"


def test_installed_readback_compares_the_version_it_read(tmp_path: Path) -> None:
    """D6 regression: the disposition keyed on exit code alone, so the version
    read back was stored in the durable JSON and never looked at.

    Confirmed: target `2.11.2`, readback `charness 2.11.1`, disposition
    `observed` — a readback that proves the command ran, not that the right
    thing is installed."""
    def run_shell(_command, **_kwargs):
        return SimpleNamespace(returncode=0, stdout="charness 2.11.1\n", stderr="")

    record = OBSERVER.collect_installed_readback(
        tmp_path, install_refresh={"status": "refreshed"},
        version_command="charness --version", doctor_command="charness doctor",
        run_shell=run_shell, expected_version="2.11.3",
    )

    assert record["status"] == "version-mismatch"
    assert record["version"]["version_match"] == "mismatch"
    assert record["version"]["expected_version"] == "2.11.3"
    assert record["version"]["reported_version"] == "2.11.1"
    assert "not the published version '2.11.3'" in record["version"]["reason"]


def test_installed_readback_reads_the_reported_version_not_any_version(tmp_path: Path) -> None:
    """The REPORTED version is the first version-shaped token, and it must EQUAL
    the expected one.

    A substring test matched `2.11.3` inside `2.11.30`; even an anchored search
    matched the trailer in `charness 2.11.1 (latest 2.11.3 available)` —
    reporting a match while the wrong version is installed, which is the
    dangerous direction for a readback whose entire job is catching that."""
    def readback(stdout: str):
        return OBSERVER.collect_installed_readback(
            tmp_path, install_refresh={"status": "refreshed"},
            version_command="v", doctor_command="d",
            run_shell=lambda *_a, **_k: SimpleNamespace(returncode=0, stdout=stdout, stderr=""),
            expected_version="2.11.3",
        )

    for stdout, expected in (
        ("charness 2.11.3\n", "observed"),
        ("version: 2.11.3\n", "observed"),
        ("charness 2.11.30\n", "version-mismatch"),
        ("charness 2.11.1 (latest 2.11.3 available)\n", "version-mismatch"),
        ("charness 2.11.3-rc1\n", "version-mismatch"),
    ):
        assert readback(stdout)["status"] == expected, stdout

    # No version-shaped token is an unestablished comparison, not a match.
    no_version = readback("charness (dev build)\n")
    assert no_version["version"]["version_match"] == "not-compared"


def test_installed_readback_observes_when_the_version_matches(tmp_path: Path) -> None:
    """Falsifiable counterpart: the same shape with a matching readback still
    reaches `observed`, and records that the comparison actually happened."""
    def run_shell(_command, **_kwargs):
        return SimpleNamespace(returncode=0, stdout="charness 2.11.3\n", stderr="")

    record = OBSERVER.collect_installed_readback(
        tmp_path, install_refresh={"status": "refreshed"},
        version_command="charness --version", doctor_command="charness doctor",
        run_shell=run_shell, expected_version="2.11.3",
    )

    assert record["status"] == "observed"
    assert record["version"]["version_match"] == "matched"


def test_installed_readback_marks_an_uncompared_version_as_such(tmp_path: Path) -> None:
    """When the readback could not run there is nothing to compare, and the
    record says `not-compared` rather than leaving the absence of a mismatch to
    read as agreement."""
    def run_shell(_command, **_kwargs):
        return SimpleNamespace(returncode=1, stdout="", stderr="command not found")

    record = OBSERVER.collect_installed_readback(
        tmp_path, install_refresh={"status": "refreshed"},
        version_command="charness --version", doctor_command="charness doctor",
        run_shell=run_shell, expected_version="2.11.3",
    )

    assert record["status"] == "unavailable"
    assert record["version"]["version_match"] == "not-compared"


def test_distinct_channel_section_does_not_assert_distinctness_it_lacks() -> None:
    """D8 regression: the artifact appended "(a channel distinct from
    `gh release view`)" unconditionally.

    It said that on `same-proxy-flagged` records — whose own observer field reads
    `same-proxy (backend release_view shape; not a distinct observer)` — and on
    `skipped` records where no channel ran at all. The published artifact is what
    the rung-2 human audit reads, so a sentence it cannot support is the whole
    failure mode this section exists to prevent."""
    flagged = ARTIFACT_SECTIONS.distinct_channel_verification_lines(
        {"status": "same-proxy-flagged", "channel": "adapter-probe"}
    )
    verdict = next(line for line in flagged if "verdict" in line)
    assert "NOT a distinct channel" in verdict
    assert "(a channel distinct from `gh release view`)" not in verdict

    skipped = ARTIFACT_SECTIONS.distinct_channel_verification_lines(
        {"status": "skipped", "channel": "none"}
    )
    assert "no distinct channel ran" in next(line for line in skipped if "verdict" in line)

    not_confirmed = ARTIFACT_SECTIONS.distinct_channel_verification_lines(
        {"status": "not-confirmed", "channel": "https-fetch"}
    )
    assert "did NOT confirm" in next(line for line in not_confirmed if "verdict" in line)

    # Falsifiable counterpart: the claim survives where it is earned.
    confirmed = ARTIFACT_SECTIONS.distinct_channel_verification_lines(
        {"status": "confirmed", "channel": "https-fetch", "expected_content": "v1.2.3"}
    )
    verdict = next(line for line in confirmed if "verdict" in line)
    assert "a channel distinct from `gh release view`" in verdict
    assert "NOT" not in verdict
    assert any("Response content checked for" in line for line in confirmed)


def test_distinct_channel_section_keys_distinctness_on_the_guard_not_the_status() -> None:
    """Distinctness is a property of the same-proxy GUARD, not of the status.

    Branching on status alone left two escapes: a probe of literally
    `gh release view v1` reaches `confirmed` when the caller omits
    `backend`/`backend_command` so the guard never runs, and an
    `inconclusive-degenerate-release-view-template` guard coexists with
    `confirmed`. In both, the guard did not establish distinctness and the
    artifact asserted it anyway — D8's exact failure mode surviving the D8 fix.
    The guard's own verdict is now rendered too, so the rung-2 reader can see it."""
    for guard in ("inconclusive-degenerate-release-view-template", "not-configured", None):
        lines = ARTIFACT_SECTIONS.distinct_channel_verification_lines(
            {"status": "confirmed", "channel": "adapter-probe",
             "command": "gh release view v1", **({"same_proxy_guard": guard} if guard else {})}
        )
        verdict = next(line for line in lines if "verdict" in line)
        assert "distinctness NOT established" in verdict, guard
        assert "(a channel distinct from `gh release view`)" not in verdict, guard

    evaluated = ARTIFACT_SECTIONS.distinct_channel_verification_lines(
        {"status": "confirmed", "channel": "adapter-probe", "same_proxy_guard": "evaluated"}
    )
    assert "a channel distinct from `gh release view`" in next(line for line in evaluated if "verdict" in line)
    assert any("Same-proxy guard: `evaluated`" in line for line in evaluated)

    # The default HTTP probe is distinct by construction (no guard applies).
    http = ARTIFACT_SECTIONS.distinct_channel_verification_lines(
        {"status": "confirmed", "channel": "https-fetch", "expected_content": "v1.2.3"}
    )
    assert "a channel distinct from `gh release view`" in next(line for line in http if "verdict" in line)


def test_published_notes_audit_reaches_the_artifact() -> None:
    """An advisory nobody reads is the same silent path the distinct-channel
    section exists to close. This record previously lived only in the publish
    run's stdout JSON, which nothing re-reads after a release."""
    advisory = ARTIFACT_SECTIONS.published_notes_audit_lines(
        {"status": "advisory", "advisories": ["public release notes point at ... MUTABLE ref `main`"]}
    )
    assert "## Published Notes Audit" in advisory
    assert any("MUTABLE ref" in line for line in advisory)
    assert any("gh release edit" in line for line in advisory)

    unestablished = ARTIFACT_SECTIONS.published_notes_audit_lines(
        {"status": "unestablished", "reason": "empty body"}
    )
    assert any("NOT audited" in line for line in unestablished)

    assert ARTIFACT_SECTIONS.published_notes_audit_lines(None) == []
