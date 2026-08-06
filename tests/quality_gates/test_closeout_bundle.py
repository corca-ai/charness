from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from scripts import closeout_bundle as cli
from scripts import closeout_bundle_lib as lib

from .support import ROOT, run_script

MANIFEST = ROOT / "charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json"
CRITIQUE = "charness-artifacts/critique/2026-08-06-slice-3-final-bundle-contract.md"


def _args() -> dict[str, object]:
    return {
        "manifest_path": MANIFEST,
        "critique_paths": [CRITIQUE],
        "behavior_channels": ["behavior=python3 -m pytest -q tests/quality_gates/test_closeout_bundle.py"],
        "bundle_id": "closeout-bundle-test",
    }


def test_dry_run_is_ready_and_has_ordered_phases() -> None:
    payload = lib.build_plan(ROOT, **_args())
    assert payload["status"] == "ready"
    assert payload["mode"] == "dry-run"
    assert [phase["name"] for phase in payload["phases"]] == [
        "surface_inventory", "pointer_freshness", "authoring_preflight",
        "reviewer_packet", "evidence_identity", "verification_lock",
    ]
    assert payload["non_claims"]


def test_authoring_preflight_leaves_generated_packet_docs_to_artifact_owner(tmp_path: Path) -> None:
    packet = tmp_path / "charness-artifacts/critique/generated-packet.md"
    authored = tmp_path / "docs/owned.md"
    packet.parent.mkdir(parents=True)
    authored.parent.mkdir(parents=True)
    packet.write_text("# generated\n", encoding="utf-8")
    authored.write_text("# authored\n", encoding="utf-8")
    commands = lib._authoring_argv(tmp_path, [
        "charness-artifacts/critique/generated-packet.md",
        "docs/owned.md",
    ])
    doc_commands = [command for command in commands if "scripts/check_doc_authoring_preflight.py" in command]
    artifact_commands = [command for command in commands if "scripts/check_artifact_surface_preflight.py" in command]
    assert len(doc_commands) == 1
    assert "docs/owned.md" in doc_commands[0]
    assert "generated-packet.md" not in doc_commands[0]
    assert len(artifact_commands) == 1
    assert "charness-artifacts/critique/generated-packet.md" in artifact_commands[0]


def test_cli_help_and_dry_run_do_not_write_receipt() -> None:
    help_result = run_script("scripts/closeout_bundle.py", "--help")
    assert help_result.returncode == 0
    assert "--execute" in help_result.stdout
    assert "ready = plan readiness" in help_result.stdout
    assert "Behavior channels are recorded, not run" in help_result.stdout
    result = run_script(
        "scripts/closeout_bundle.py", "--repo-root", str(ROOT), "--manifest", str(MANIFEST),
        "--bundle-id", "closeout-bundle-cli-test", "--critique-path", CRITIQUE,
        "--behavior-channel", "behavior=echo behavior",
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ready"
    assert not (ROOT / "charness-artifacts/goals/closeout-bundle-cli-test.json").exists()


def test_rejects_unsafe_planned_shell_command(tmp_path: Path) -> None:
    with pytest.raises(lib.BundleError, match="shell syntax"):
        lib._command_argv("python3 scripts/check.py && touch escaped", repo_root=tmp_path)


@pytest.mark.parametrize(
    "command",
    [
        "sh -c 'echo unsafe' scripts/run_slice_closeout.py",
        "python3 -c 'print(1)' scripts/run_slice_closeout.py",
        "python3 -m pytest tests/quality_gates/test_closeout_bundle.py",
    ],
)
def test_rejects_interpreter_code_execution_modes(tmp_path: Path, command: str) -> None:
    with pytest.raises(lib.BundleError, match="directly"):
        lib._command_argv(command, repo_root=tmp_path)


def test_rejects_repo_symlink_to_external_script(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("print('outside')\n", encoding="utf-8")
    os.symlink(outside, repo_root / "linked.py")
    with pytest.raises(lib.BundleError, match="repo-owned"):
        lib._command_argv("python3 linked.py", repo_root=repo_root)


def test_receipt_requires_completed_payload(tmp_path: Path) -> None:
    with pytest.raises(lib.BundleError, match="completed bundle"):
        lib.write_receipt(tmp_path, {"status": "failed"}, output_path=Path("receipt.json"))


def test_packet_identity_binding_mismatch_refuses(tmp_path: Path) -> None:
    (tmp_path / "packet.json").write_text(
        json.dumps({"reviewed_input_identity": {"identity_sha256": "b" * 64}}),
        encoding="utf-8",
    )
    result = {
        "returncode": 0,
        "stdout": json.dumps({
            "ok": True,
            "reviewed_input_binding": {
                "packet_path": "packet.json",
                "identity_sha256": "a" * 64,
            },
        }),
        "stderr": "",
    }
    with pytest.raises(lib.BundleError, match="identity binding"):
        lib._packet_payload(tmp_path, result)


def test_unsafe_planned_command_is_rejected_before_any_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(lib, "build_plan", lambda *_args, **_kwargs: {
        "status": "ready",
        "preflight": {
            "planned_commands": [
                {"phase": "sync", "command": "python3 scripts/sync_root_plugin_manifests.py --repo-root ."},
                {"phase": "sync", "command": "python3 -m pytest tests/quality_gates/test_closeout_bundle.py"},
            ],
        },
    })
    calls: list[list[str]] = []

    def fake_runner(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, "", "")

    with pytest.raises(lib.BundleError, match="directly"):
        lib.execute(ROOT, **_args(), runner=fake_runner)
    assert calls == []


def test_identity_drift_refuses_before_lock(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(lib, "build_plan", lambda *_args, **_kwargs: {
        "status": "ready", "mode": "dry-run", "preflight": {"planned_commands": []},
        "changed_paths": ["scripts/example.py"], "phases": [], "non_claims": [],
    })
    monkeypatch.setattr(lib._preflight, "build_plan", lambda *_args, **_kwargs: {
        "status": "ready", "planned_commands": [{"phase": "closeout", "command": "python3 scripts/run_slice_closeout.py --verification-lock"}],
    })
    calls: list[str] = []

    def fake_runner(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv[1])
        if argv[1].endswith("prepare_packet.py"):
            (tmp_path / "packet.json").write_text(
                json.dumps({"reviewed_input_identity": {"identity_sha256": "a" * 64}}),
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(argv, 0, json.dumps({
                "ok": True,
                "reviewed_input_binding": {"packet_path": "packet.json", "identity_sha256": "a" * 64, "reviewed_paths": ["scripts/example.py"]},
            }), "")
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(lib, "_authoring_argv", lambda *_args: [])
    monkeypatch.setattr(lib._identity, "verify_reviewed_input_identity", lambda *_args: (False, "changed bytes"))
    result = lib.execute(tmp_path, **_args(), runner=fake_runner)
    assert result["status"] == "failed"
    assert "stale before verification lock" in result["error"]
    assert not any(command.endswith("run_slice_closeout.py") for command in calls)


def test_post_sync_scope_drives_authoring_and_packet(monkeypatch: pytest.MonkeyPatch) -> None:
    plans = iter([
        {
            "status": "ready",
            "changed_paths": ["scripts/initial.py"],
            "planned_commands": [
                {"phase": "sync", "command": "python3 scripts/sync_root_plugin_manifests.py --repo-root ."},
            ],
        },
        {"status": "ready", "changed_paths": ["scripts/refreshed.py"], "planned_commands": []},
        {
            "status": "ready",
            "changed_paths": ["scripts/refreshed.py"],
            "planned_commands": [
                {"phase": "closeout", "command": "python3 scripts/run_slice_closeout.py --verification-lock"},
            ],
        },
    ])
    monkeypatch.setattr(lib._preflight, "build_plan", lambda *_args, **_kwargs: next(plans))
    authoring_invocations: list[list[str]] = []

    def fake_authoring(_repo_root: Path, paths: list[str]) -> list[list[str]]:
        authoring_invocations.append(list(paths))
        return [["python3", "scripts/check_doc_authoring_preflight.py", "--path", *paths]]

    monkeypatch.setattr(lib, "_authoring_argv", fake_authoring)
    packet_path = ROOT / "charness-artifacts/critique/2026-07-18-185648-packet.json"
    packet_json = json.loads(packet_path.read_text(encoding="utf-8"))
    calls: list[list[str]] = []

    def fake_runner(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        if argv[1].endswith("prepare_packet.py"):
            binding = {
                "packet_path": "charness-artifacts/critique/2026-07-18-185648-packet.json",
                "identity_sha256": packet_json["reviewed_input_identity"]["identity_sha256"],
                "reviewed_paths": packet_json["reviewed_input_identity"]["reviewed_paths"],
            }
            return subprocess.CompletedProcess(argv, 0, json.dumps({
                "ok": True,
                "reviewed_input_binding": binding,
            }), "")
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(lib._identity, "verify_reviewed_input_identity", lambda *_args: (True, ""))
    result = lib.execute(ROOT, **_args(), runner=fake_runner)
    assert result["status"] == "completed"
    assert authoring_invocations == [["scripts/initial.py"], ["scripts/refreshed.py"]]
    packet_calls = [call for call in calls if call[1].endswith("prepare_packet.py")]
    assert len(packet_calls) == 1
    assert "scripts/refreshed.py" in packet_calls[0]
    assert "scripts/initial.py" not in packet_calls[0]


def test_command_validation_covers_runner_and_path_refusals() -> None:
    with pytest.raises(lib.BundleError, match="shell-quotable"):
        lib._command_argv("python3 'unterminated", repo_root=ROOT)
    assert lib._command_argv("./scripts/check-shell.sh", repo_root=ROOT)[0] == "./scripts/check-shell.sh"
    with pytest.raises(lib.BundleError, match="approved repo runner"):
        lib._command_argv("perl scripts/check-shell.sh", repo_root=ROOT)
    with pytest.raises(lib.BundleError, match="absolute path"):
        lib._command_argv("python3 scripts/check-shell.sh /tmp/out", repo_root=ROOT)
    with pytest.raises(lib.BundleError, match="repo-owned"):
        lib._command_argv("python3 ../scripts/check-shell.sh", repo_root=ROOT)
    with pytest.raises(lib.BundleError, match="repo-owned"):
        lib._command_argv("python3 missing-closeout-script.py", repo_root=ROOT)
    with pytest.raises(lib.BundleError, match="repo-owned"):
        lib._command_argv("python3 scripts", repo_root=ROOT)


def test_packet_payload_rejects_each_unusable_shape(tmp_path: Path) -> None:
    cases = [
        ({"returncode": 1, "stdout": "out", "stderr": "err"}, "generation failed"),
        ({"returncode": 0, "stdout": "not json", "stderr": ""}, "did not return JSON"),
        ({"returncode": 0, "stdout": json.dumps({"ok": False}), "stderr": ""}, "not ready"),
        ({"returncode": 0, "stdout": json.dumps({"ok": True, "reviewed_input_binding": []}), "stderr": ""}, "input binding"),
        ({"returncode": 0, "stdout": json.dumps({"ok": True, "reviewed_input_binding": {"usable": False}}), "stderr": ""}, "not usable"),
        ({"returncode": 0, "stdout": json.dumps({"ok": True, "reviewed_input_binding": {"packet_path": 4}}), "stderr": ""}, "durable packet path"),
        ({"returncode": 0, "stdout": json.dumps({"ok": True, "reviewed_input_binding": {"packet_path": "missing.json"}}), "stderr": ""}, "path is missing"),
    ]
    for result, message in cases:
        with pytest.raises(lib.BundleError, match=message):
            lib._packet_payload(tmp_path, result)
    (tmp_path / "invalid.json").write_text("{}", encoding="utf-8")
    invalid_packet = {
        "returncode": 0,
        "stdout": json.dumps({
            "ok": True,
            "reviewed_input_binding": {"packet_path": "invalid.json", "identity_sha256": "a" * 64},
        }),
        "stderr": "",
    }
    with pytest.raises(lib.BundleError, match="durable input identity"):
        lib._packet_payload(tmp_path, invalid_packet)


def test_failed_payload_and_invalid_bundle_id_are_explicit() -> None:
    payload = {"status": "ready"}
    phases: list[dict[str, object]] = []
    result = lib._failed(payload, phases, "boom", detail="recorded")
    assert result == {"status": "failed", "phases": phases, "error": "boom", "detail": "recorded"}
    with pytest.raises(lib.BundleError, match="bundle-id"):
        lib.build_plan(ROOT, **{**_args(), "bundle_id": "BAD"})


def test_execute_returns_blocked_plan_without_running_commands(monkeypatch: pytest.MonkeyPatch) -> None:
    blocked = {
        "status": "blocked",
        "preflight": {"planned_commands": [{"phase": "sync", "command": "python3 scripts/check-shell.sh"}]},
    }
    monkeypatch.setattr(lib, "build_plan", lambda *_args, **_kwargs: blocked)
    result = lib.execute(
        ROOT,
        **_args(),
        runner=lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("runner must not execute")),
    )
    assert result["status"] == "blocked"
    assert result["mode"] == "execute"


def test_execute_refuses_after_sync_or_preflight_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    def build_initial(*_args: object, **_kwargs: object) -> dict[str, object]:
        return {
            "status": "ready",
            "preflight": {"planned_commands": [{"phase": "sync", "command": "python3 scripts/check-shell.sh"}]},
            "changed_paths": [],
        }

    monkeypatch.setattr(lib, "build_plan", build_initial)
    monkeypatch.setattr(lib._preflight, "build_plan", lambda *_args, **_kwargs: {"status": "blocked"})
    failed_sync = lib.execute(
        ROOT,
        **_args(),
        runner=lambda argv, **_kwargs: subprocess.CompletedProcess(argv, 1, "", "sync failed"),
    )
    assert failed_sync["status"] == "failed"
    assert "surface sync failed" in failed_sync["error"]

    monkeypatch.setattr(lib, "build_plan", lambda *_args, **_kwargs: {
        "status": "ready",
        "preflight": {"planned_commands": [
            {"phase": "sync", "command": "python3 scripts/check-shell.sh"},
            {"phase": "closeout", "command": "python3 scripts/run_slice_closeout.py --verification-lock"},
        ]},
        "changed_paths": [],
    })
    blocked_after_sync = lib.execute(
        ROOT,
        **_args(),
        runner=lambda argv, **_kwargs: subprocess.CompletedProcess(argv, 0, "", ""),
    )
    assert blocked_after_sync["status"] == "failed"
    assert "post-sync" in blocked_after_sync["error"]


def test_execute_refuses_pointer_and_authoring_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(lib, "build_plan", lambda *_args, **_kwargs: {
        "status": "ready", "preflight": {"planned_commands": []}, "changed_paths": [],
    })
    monkeypatch.setattr(lib._preflight, "build_plan", lambda *_args, **_kwargs: {"status": "ready", "planned_commands": []})
    monkeypatch.setattr(lib, "_authoring_argv", lambda *_args: [["python3", "scripts/check-shell.sh"]])
    calls: list[list[str]] = []

    def fail_pointer(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 1, "", "pointer failed")

    pointer = lib.execute(ROOT, **_args(), runner=fail_pointer)
    assert pointer["status"] == "failed"
    assert "pointer freshness" in pointer["error"]

    def fail_authoring(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        if "validate_current_pointer_freshness.py" in argv[1]:
            return subprocess.CompletedProcess(argv, 0, "", "")
        return subprocess.CompletedProcess(argv, 1, "", "authoring failed")

    monkeypatch.setattr(lib, "_authoring_argv", lambda *_args: [["python3", "scripts/check-shell.sh"]])
    authoring = lib.execute(ROOT, **_args(), runner=fail_authoring)
    assert authoring["status"] == "failed"
    assert "authoring preflight" in authoring["error"]


def test_execute_refuses_when_packet_has_no_verification_lock(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(lib, "build_plan", lambda *_args, **_kwargs: {
        "status": "ready", "preflight": {"planned_commands": []}, "changed_paths": [],
    })
    plans = iter([
        {"status": "ready", "planned_commands": []},
        {"status": "ready", "planned_commands": []},
    ])
    monkeypatch.setattr(lib._preflight, "build_plan", lambda *_args, **_kwargs: next(plans))
    monkeypatch.setattr(lib, "_authoring_argv", lambda *_args: [])
    monkeypatch.setattr(lib, "_packet_payload", lambda *_args: {
        "packet_sha256": "b" * 64,
        "durable_identity_sha256": "a" * 64,
        "reviewed_input_binding": {"packet_path": "packet.json", "reviewed_paths": []},
    })
    monkeypatch.setattr(lib._identity, "verify_reviewed_input_identity", lambda *_args: (True, ""))
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps({"reviewed_input_identity": {"identity_sha256": "a" * 64}}), encoding="utf-8")
    result = lib.execute(
        tmp_path,
        **_args(),
        runner=lambda argv, **_kwargs: subprocess.CompletedProcess(argv, 0, "", ""),
    )
    assert result["status"] == "failed"
    assert "verification lock" in result["error"]


def test_write_receipt_writes_completed_payload_and_rejects_escape(tmp_path: Path) -> None:
    target = lib.write_receipt(tmp_path, {"status": "completed", "value": 1}, output_path=Path("nested/receipt.json"))
    assert target == tmp_path / "nested/receipt.json"
    assert json.loads(target.read_text(encoding="utf-8"))["value"] == 1
    with pytest.raises(lib.BundleError, match="outside repository"):
        lib.write_receipt(tmp_path, {"status": "completed"}, output_path=tmp_path.parent / "outside.json")


def test_cli_main_covers_execute_receipt_and_exception(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(cli._lib, "execute", lambda *_args, **_kwargs: {"status": "completed"})
    monkeypatch.setattr(cli._lib, "write_receipt", lambda repo_root, payload, *, output_path: repo_root / "receipt.json")
    argv = [
        "--repo-root", str(ROOT), "--manifest", str(MANIFEST), "--bundle-id", "closeout-cli-main",
        "--critique-path", CRITIQUE, "--behavior-channel", "behavior=echo test", "--execute",
    ]
    assert cli.main(argv) == 0
    assert "receipt_path" in capsys.readouterr().out
    monkeypatch.setattr(cli._lib, "build_plan", lambda *_args, **_kwargs: (_ for _ in ()).throw(cli._lib.BundleError("blocked")))
    assert cli.main(argv[:-1]) == 1
    assert '"status": "blocked"' in capsys.readouterr().out
