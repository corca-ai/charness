"""Retained-attempt validation and recovery refusal tests for critique reviews."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from tests.script_main import load_script_module

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "skills/public/critique/scripts"
RUN_REVIEW = load_script_module(
    "review_recovery_run_review_under_test", SCRIPT_ROOT / "run_review.py"
)
SUPPORT = RUN_REVIEW.SUPPORT
PACKET = RUN_REVIEW.PACKET
PROMOTION = RUN_REVIEW.PROMOTION
RECOVERY = load_script_module(
    "review_recovery_under_test", SCRIPT_ROOT / "run_review_recovery.py"
)
# These three modules had no standing static mapping. Keep the real consumers
# explicit and exercise their returned validation/refusal data below.
RECOVERY_INPUTS = load_script_module(
    "review_recovery_inputs_under_test", SCRIPT_ROOT / "run_review_recovery_inputs.py"
)
EXECUTION = load_script_module(
    "review_recovery_execution_under_test", SCRIPT_ROOT / "run_review_execution.py"
)


class _IdentityVerification:
    @staticmethod
    def verify_semantic_carrier_entry(_identity, _entry, _content):
        return True, None


class _PacketReader:
    @staticmethod
    def read_packet(*_args):
        return None


def _retained_fixture(tmp_path: Path) -> dict[str, object]:
    attempt = "retained-1"
    run_dir = tmp_path / ".charness" / "scratch" / "critique-review" / attempt
    semantic_dir = run_dir / "semantic-input"
    semantic_dir.mkdir(parents=True)
    content = b"immutable review input\n"
    content_path = semantic_dir / "0000-content.bin"
    content_path.write_bytes(content)
    content_sha = hashlib.sha256(content).hexdigest()

    packet_payload = {
        "kind": "charness.critique_prepare_packet",
        "sections": [{"id": "input", "content": "review input"}],
        "reviewed_input_identity": {
            "identity_sha256": "i" * 64,
            "reviewed_paths": ["reviewed.txt"],
            "reviewed_content": [
                {"path": "reviewed.txt", "content_sha256": content_sha}
            ],
        },
    }
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet_payload, sort_keys=True) + "\n", encoding="utf-8")
    packet_sha = hashlib.sha256(packet_path.read_bytes()).hexdigest()

    plan = {
        "kind": "charness.review_run_plan.v1",
        "attempt_id": attempt,
        "packet_path": "packet.json",
        "packet_sha256": packet_sha,
        "reviewed_input_identity_sha256": "i" * 64,
        "scope": "retained recovery",
        "lens": "identity",
    }
    plan["parent_receipt_identity"] = RECOVERY_INPUTS.parent_receipt_identity(plan)
    plan_path = run_dir / "run-plan.json"
    plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    paths = {
        "run_dir": run_dir,
        "plan": plan_path,
        "receipt": run_dir / "receipt.json",
        "ledger": run_dir / "delivery.json",
        "output": run_dir / "result.json",
        "report": run_dir / "worker-report.yaml",
        "summary": run_dir / "lifecycle.yaml",
        "runner_stdout": run_dir / "runner.stdout",
        "runner_stderr": run_dir / "runner.stderr",
    }
    receipt = {
        "attempt_id": attempt,
        "packet_identity": packet_sha,
        "reviewed_input_identity": "i" * 64,
        "parent_receipt_identity": plan["parent_receipt_identity"],
    }
    ledger = {
        "attempts": [
            {
                "attempt_id": attempt,
                "packet_identity": packet_sha,
                "reviewed_input_identity": "i" * 64,
                "parent_receipt_identity": plan["parent_receipt_identity"],
                "state": "timed-out",
            }
        ]
    }
    output = {"state": "partial", "approval_eligible": False}
    report = {
        "attempt_id": attempt,
        "packet_identity": packet_sha,
        "reviewed_input_identity": "i" * 64,
        "parent_receipt_identity": plan["parent_receipt_identity"],
        "delivery_state": "timed-out",
        "approval_eligible": False,
    }
    summary = {"status": "runner-timeout", "approval_eligible": False}
    SUPPORT.write_json(paths["receipt"], receipt)
    SUPPORT.write_json(paths["ledger"], ledger)
    SUPPORT.write_json(paths["output"], output)
    SUPPORT.write_yaml(paths["report"], report)
    SUPPORT.write_yaml(paths["summary"], summary)
    paths["runner_stdout"].write_text("", encoding="utf-8")
    paths["runner_stderr"].write_text("timeout\n", encoding="utf-8")
    semantic_manifest = {
        "entries": [
            {
                "path": "reviewed.txt",
                "carrier_path": SUPPORT.relative(tmp_path, content_path),
                "content_sha256": content_sha,
            }
        ]
    }
    SUPPORT.write_json(semantic_dir / "manifest.json", semantic_manifest)

    owner_payload = {
        "attempt_id": attempt,
        "packet_identity": packet_sha,
        "reviewed_input_identity": "i" * 64,
        "parent_receipt_identity": plan["parent_receipt_identity"],
        "plan_sha256": SUPPORT.sha256(plan_path),
        "receipt_sha256": SUPPORT.sha256(paths["receipt"]),
        "delivery_sha256": SUPPORT.sha256(paths["ledger"]),
        "result_sha256": SUPPORT.sha256(paths["output"]),
        "report_sha256": SUPPORT.sha256(paths["report"]),
        "summary_sha256": SUPPORT.sha256(paths["summary"]),
    }
    owner_receipt = run_dir / ".charness-owner.json"
    SUPPORT.write_json(owner_receipt, owner_payload)
    return {
        "attempt": attempt,
        "run_dir": run_dir,
        "plan": plan,
        "packet": packet_path,
        "paths": paths,
        "owner_receipt": owner_receipt,
        "package": {"verify_packet": tmp_path / "verify_packet.py"},
        "packet_module": _PacketReader,
        "identity_verification": _IdentityVerification,
        "content_path": content_path,
    }


def test_parent_receipt_identity_is_stable_and_non_approval_carrier_is_explicit() -> None:
    plan = {"attempt_id": "a", "packet_sha256": "p"}
    identity = RECOVERY_INPUTS.parent_receipt_identity(plan)
    plan["parent_receipt_identity"] = "untrusted"
    assert RECOVERY_INPUTS.parent_receipt_identity(plan) == identity
    carrier = RECOVERY_INPUTS.non_approval_carrier("retained report is incomplete")
    assert carrier == {
        "approval_eligible": False,
        "identity_check": {"matches": False, "reason": "retained report is incomplete"},
        "runner_stream": {"consistent": False, "reason": "retained report is incomplete"},
    }


def test_retained_input_validation_rebinds_all_identity_and_semantic_bytes(
    tmp_path: Path,
) -> None:
    fixture = _retained_fixture(tmp_path)
    result = RECOVERY_INPUTS.validate_retained_inputs(
        tmp_path,
        fixture["plan"],
        fixture["packet"],
        fixture["paths"],
        attempt=fixture["attempt"],
        owner_receipt=fixture["owner_receipt"],
        package=fixture["package"],
        support=SUPPORT,
        packet_module=fixture["packet_module"],
        identity_verification=fixture["identity_verification"],
    )
    assert result["status"] == "verified"
    assert result["ok"] is True
    assert result["checks"]["semantic_input"] == {"status": "verified", "entries": 1}


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("owner", "retained owner receipt does not bind the requested attempt"),
        ("plan", "retained run plan bytes do not match the owner receipt"),
        ("semantic", "retained semantic-input manifest paths do not match the packet"),
    ],
)
def test_retained_input_validation_refuses_tampering_before_recovery(
    tmp_path: Path, mutation: str, expected: str
) -> None:
    fixture = _retained_fixture(tmp_path)
    if mutation == "owner":
        owner = json.loads(fixture["owner_receipt"].read_text(encoding="utf-8"))
        owner["packet_identity"] = "tampered"
        SUPPORT.write_json(fixture["owner_receipt"], owner)
    elif mutation == "plan":
        fixture["paths"]["plan"].write_text(
            fixture["paths"]["plan"].read_text(encoding="utf-8") + "\n",
            encoding="utf-8",
        )
    else:
        manifest = fixture["run_dir"] / "semantic-input" / "manifest.json"
        SUPPORT.write_json(manifest, {"entries": []})

    result = RECOVERY_INPUTS.validate_retained_inputs(
        tmp_path,
        fixture["plan"],
        fixture["packet"],
        fixture["paths"],
        attempt=fixture["attempt"],
        owner_receipt=fixture["owner_receipt"],
        package=fixture["package"],
        support=SUPPORT,
        packet_module=fixture["packet_module"],
        identity_verification=fixture["identity_verification"],
    )
    assert result["ok"] is False
    assert result["reason"] == expected


def test_promoted_chain_reopens_durable_files_and_checks_integrity(tmp_path: Path) -> None:
    durable = tmp_path / "charness-artifacts" / "critique" / "workers" / "attempt"
    durable.mkdir(parents=True)
    names = {key: f"{key}.json" for key in ("report", "receipt", "ledger", "output", "summary")}
    files = {}
    for key, name in names.items():
        path = durable / name
        if key == "summary":
            path.write_text("state: terminal\napproval_eligible: false\n", encoding="utf-8")
        else:
            SUPPORT.write_json(path, {"kind": key})
        files[key] = SUPPORT.relative(tmp_path, path)
    final_carrier = {"state": "terminal", "approval_eligible": False}
    SUPPORT.write_yaml(durable / "summary.json", final_carrier)
    integrity = {
        key: {
            "path": relative,
            "bytes": (tmp_path / relative).stat().st_size,
            "sha256": SUPPORT.sha256(tmp_path / relative),
        }
        for key, relative in files.items()
    }
    SUPPORT.write_json(
        durable / "attempt-manifest.json",
        {"files": files, "file_integrity": integrity, "approval_eligible": False},
    )
    paths = dict(files)
    result = RECOVERY_INPUTS.validate_promoted_chain(
        tmp_path,
        paths,
        final_carrier,
        {"attempt_id": "attempt", "packet_sha256": "p", "reviewed_input_identity_sha256": "i", "parent_receipt_identity": "parent"},
        support=SUPPORT,
        carrier_validation=SimpleNamespace(validate_delivered_worker_report=lambda **_kwargs: None),
        promotion=SimpleNamespace(identity_binding=lambda _report, _expected: {"matches": True}),
    )
    assert result["ok"] is True
    assert result["file_integrity"] == {"status": "verified", "files": 5}

    integrity["output"]["sha256"] = "0" * 64
    SUPPORT.write_json(
        durable / "attempt-manifest.json",
        {"files": files, "file_integrity": integrity, "approval_eligible": False},
    )
    invalid = RECOVERY_INPUTS.validate_promoted_chain(
        tmp_path,
        paths,
        final_carrier,
        {"attempt_id": "attempt", "packet_sha256": "p", "reviewed_input_identity_sha256": "i", "parent_receipt_identity": "parent"},
        support=SUPPORT,
        carrier_validation=SimpleNamespace(validate_delivered_worker_report=lambda **_kwargs: None),
        promotion=SimpleNamespace(identity_binding=lambda _report, _expected: {"matches": True}),
    )
    assert invalid["ok"] is False
    assert "integrity check failed" in invalid["reason"]


class _RecoveryOwner:
    def __init__(self, path: Path):
        self.path = path
        self.receipt_path = path / ".charness-owner.json"
        self.closed: list[dict[str, object]] = []
        self.reopened = False

    def reopen_existing(self) -> None:
        self.reopened = True

    def close(self, **kwargs: object) -> None:
        self.closed.append(kwargs)


def test_recovery_emits_refusal_and_retains_scratch_when_inputs_do_not_bind(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run_dir = tmp_path / ".charness" / "scratch" / "critique-review" / "retained"
    run_dir.mkdir(parents=True)
    (tmp_path / "packet.json").write_text("{}\n", encoding="utf-8")
    SUPPORT.write_json(
        run_dir / "run-plan.json",
        {"attempt_id": "retained", "packet_path": "packet.json"},
    )
    SUPPORT.write_json(run_dir / ".charness-owner.json", {})
    owner = _RecoveryOwner(run_dir)
    monkeypatch.setattr(SUPPORT, "owned_scratch", lambda *args, **kwargs: owner)

    result = RECOVERY.resume_retained_attempt(
        tmp_path,
        "retained",
        support=SUPPORT,
        packet=PACKET,
        promotion=PROMOTION,
        script_dir=SCRIPT_ROOT,
    )
    payload = yaml.safe_load(capsys.readouterr().out)
    assert result == 1
    assert owner.reopened is True
    assert owner.closed == [{"state": "failed"}]
    assert payload["status"] == "refused"
    assert payload["approval_eligible"] is False
    assert payload["retained"] is True
    assert payload["recovery_validation"]["reason"] == (
        "retained owner receipt does not bind the requested attempt"
    )


def test_recovery_rejects_path_like_attempt_ids_before_opening_a_retained_run(
    tmp_path: Path,
) -> None:
    with pytest.raises(SUPPORT.RunReviewError) as caught:
        RECOVERY.resume_retained_attempt(
            tmp_path,
            "../retained",
            support=SUPPORT,
            packet=PACKET,
            promotion=PROMOTION,
            script_dir=SCRIPT_ROOT,
        )
    assert caught.value.code == "attempt-invalid"


def test_run_review_resume_dispatches_without_requiring_live_scope_or_lens(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    called: dict[str, object] = {}

    def resume(root, attempt, **kwargs):  # noqa: ANN001
        called.update(root=root, attempt=attempt, kwargs=kwargs)
        return 9

    monkeypatch.setattr(RUN_REVIEW.RECOVERY, "resume_retained_attempt", resume)
    result = RUN_REVIEW.main(
        ["--repo-root", str(tmp_path), "--resume-retained-attempt", "retained"]
    )
    assert result == 9
    assert called["root"] == tmp_path.resolve()
    assert called["attempt"] == "retained"


def test_execution_refuses_a_sectionless_adapter_before_starting_a_reviewer() -> None:
    emitted: list[dict[str, object]] = []
    args = SimpleNamespace(
        attempt_id="sectionless",
        artifact_key="sectionless",
        scope="recovery",
        lens="failure semantics",
        goal_lineage_file=None,
        dry_run=True,
    )
    package = {
        "partial_output": Path("partial-output.py"),
        "resolve_adapter": Path("resolve_adapter.py"),
    }
    support = SimpleNamespace(
        RunReviewError=SUPPORT.RunReviewError,
        load_goal_lineage=lambda *args, **kwargs: {},
        package_paths=lambda _script_dir: package,
        load_runtime=lambda _package: (SimpleNamespace(), SimpleNamespace()),
        load_module=lambda *_args: SimpleNamespace(),
        resolve_adapter=lambda _root, _resolver: {"data": {"packet_sections": []}},
        emit=lambda payload: emitted.append(payload),
    )
    packet = SimpleNamespace(REFUSAL_DETAIL_FIELDS=())
    carrier = SimpleNamespace(
        failure_carrier=lambda _packet, _lifecycle, **kwargs: {
            "status": "runner-invalid",
            "reviewer_started": False,
            "reason_code": kwargs["code"],
            "error": kwargs["error"],
        }
    )

    result = EXECUTION.run_live(
        args,
        Path("/tmp/recovery-fixture"),
        support=support,
        packet=packet,
        invocation=SimpleNamespace(),
        promotion=SimpleNamespace(),
        carrier_module=carrier,
        script_dir=SCRIPT_ROOT,
        read_only_boundary_mode="read-only-worker",
        lifecycle_semantic_input=lambda value: value,
        materialize_semantic_input=lambda *values: {},
        adapter_name=lambda *values: ".agents/critique-adapter.yaml",
    )
    assert result == 2
    assert emitted == [
        {
            "status": "runner-invalid",
            "reviewer_started": False,
            "reason_code": "adapter-no-sections",
            "error": "critique adapter `.agents/critique-adapter.yaml` declares no packet_sections; run_review cannot start without semantic review input",
        }
    ]
