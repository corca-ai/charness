"""Failure and retry invariants for the critique review promotion boundary."""

from __future__ import annotations

import builtins
import hashlib
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
import yaml

from tests.module_eviction import evict_module
from tests.script_main import load_script_module

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "skills/public/critique/scripts"

# Keep these imports explicit: the changed-line producer uses the test source to
# select consumer tests, while the scripts themselves intentionally use flat,
# by-path loading rather than an importable package.
RUN_REVIEW = load_script_module(
    "review_promotion_run_review_under_test", SCRIPT_ROOT / "run_review.py"
)
SUPPORT = RUN_REVIEW.SUPPORT
PACKET = load_script_module(
    "review_promotion_packet_under_test", SCRIPT_ROOT / "run_review_packet.py"
)
CARRIER = load_script_module(
    "review_promotion_carrier_under_test", SCRIPT_ROOT / "run_review_carrier.py"
)
IDENTITY = load_script_module(
    "review_promotion_identity_under_test", SCRIPT_ROOT / "run_review_identity.py"
)
PROMOTION = load_script_module(
    "review_promotion_under_test", SCRIPT_ROOT / "run_review_promotion.py"
)
PROMOTION_DIRECT = PROMOTION
STORAGE = PROMOTION.STORAGE
STORAGE_DIRECT = load_script_module(
    "review_promotion_storage_under_test", SCRIPT_ROOT / "run_review_promotion_storage.py"
)
HOLD_OUT = load_script_module(
    "review_promotion_hold_out_under_test", SCRIPT_ROOT / "run_review_hold_out.py"
)
# This is a consumer import, not a line-execution probe: the test below injects
# the monitored phase result and asserts the typed timeout/interruption contract.
EXECUTION = load_script_module(
    "review_promotion_execution_under_test", SCRIPT_ROOT / "run_review_execution.py"
)


def _block_first_import(monkeypatch: pytest.MonkeyPatch, prefix: str) -> None:
    real_import = builtins.__import__
    blocked = True

    def import_hook(name, globals=None, locals=None, fromlist=(), level=0):  # noqa: ANN001
        nonlocal blocked
        if blocked and name.startswith(prefix):
            blocked = False
            raise ModuleNotFoundError(f"blocked bootstrap import: {name}", name=name)
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_hook)


def test_support_bootstraps_repo_imports_when_direct_package_import_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_first_import(monkeypatch, "scripts.core.subprocess_guard")

    module = load_script_module(
        "review_support_bootstrap_fallback", SCRIPT_ROOT / "run_review_support.py"
    )

    assert module.run_process is not None
    assert module.owned_scratch is not None


def test_support_load_module_restores_sys_modules_after_a_failed_import(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    broken = tmp_path / "broken_helper.py"
    broken.write_text("raise RuntimeError('broken helper')\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="broken helper"):
        SUPPORT.load_module(broken, "review_broken_helper")
    assert "review_broken_helper" not in sys.modules

    previous = ModuleType("review_broken_helper")
    monkeypatch.setitem(sys.modules, "review_broken_helper", previous)
    with pytest.raises(RuntimeError, match="broken helper"):
        SUPPORT.load_module(broken, "review_broken_helper")
    assert sys.modules["review_broken_helper"] is previous


def test_run_review_support_rejects_unreadable_yaml_and_non_mapping_carriers() -> None:
    with pytest.raises(SUPPORT.RunReviewError) as invalid_yaml:
        SUPPORT.yaml_payload("key: [", label="runner")
    assert invalid_yaml.value.code == "carrier-invalid"

    with pytest.raises(SUPPORT.RunReviewError, match="YAML mapping"):
        SUPPORT.yaml_payload("a scalar\n", label="runner")


def _packet_payload(*, paths: list[str] | None = None, content: str = "semantic input") -> dict:
    reviewed_paths = paths if paths is not None else ["reviewed.txt"]
    return {
        "kind": "charness.critique_prepare_packet",
        "ok": True,
        "section_count": 1,
        "sections": [{"id": "input", "content": content}],
        "reviewed_input_identity": {
            "identity_sha256": "a" * 64,
            "reviewed_paths": reviewed_paths,
            "reviewed_content": [
                {
                    "path": path,
                    "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
                }
                for path in reviewed_paths
            ],
        },
    }


def test_packet_reader_refuses_empty_sections_content_and_unbound_identity(
    tmp_path: Path,
) -> None:
    cases = (
        ("invalid.json", b"{") ,
        ("wrong-kind.json", json.dumps({"kind": "other"}).encode()),
        (
            "empty-sections.json",
            json.dumps({**_packet_payload(), "section_count": 0, "sections": []}).encode(),
        ),
        (
            "empty-content.json",
            json.dumps({**_packet_payload(), "sections": [{"content": "  "}]}).encode(),
        ),
        (
            "empty-input.json",
            json.dumps({**_packet_payload(paths=[])}).encode(),
        ),
        (
            "bad-identity.json",
            json.dumps({**_packet_payload(), "reviewed_input_identity": {"identity_sha256": "bad", "reviewed_paths": ["reviewed.txt"]}}).encode(),
        ),
    )
    expected = (
        "packet-invalid",
        "packet-invalid",
        "adapter-no-sections",
        "producer-empty",
        "empty-reviewed-paths",
        "packet-invalid",
    )
    for (name, raw), code in zip(cases, expected):
        path = tmp_path / name
        path.write_bytes(raw)
        with pytest.raises(SUPPORT.RunReviewError) as caught:
            PACKET.read_packet(SUPPORT, tmp_path, name, tmp_path / "unused-verifier.py")
        assert caught.value.code == code


def test_packet_reader_reports_stale_verifier_and_manifest_paths_are_canonical(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(_packet_payload()) + "\n", encoding="utf-8")
    monkeypatch.setattr(
        SUPPORT,
        "run_command",
        lambda _command, root: (0, "status: stale\nreason: changed\n", "verifier stderr"),
    )
    with pytest.raises(SUPPORT.RunReviewError) as caught:
        PACKET.read_packet(SUPPORT, tmp_path, "packet.json", tmp_path / "verify.py")
    assert caught.value.code == "packet-stale"
    assert caught.value.details["verification"]["status"] == "stale"

    manifest = tmp_path / "paths.txt"
    manifest.write_text("# ignored\nother.txt\nreviewed.txt\n", encoding="utf-8")
    assert PACKET.manifest_paths(SUPPORT, tmp_path, "paths.txt", ["reviewed.txt"]) == [
        "other.txt",
        "reviewed.txt",
    ]
    manifest.write_bytes(b"\xff\n")
    with pytest.raises(SUPPORT.RunReviewError, match="unreadable"):
        PACKET.manifest_paths(SUPPORT, tmp_path, "paths.txt", None)


def test_packet_preparation_preserves_followup_range_and_reports_producer_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    args = SimpleNamespace(
        prepared_for="repair",
        prepared_target=["target-1"],
        follow_up_from="prior.json",
        commit=None,
        changed_range="base..head",
    )
    seen: list[str] = []

    def prepare_command(command, *, root):  # noqa: ANN001
        seen.extend(command)
        return 0, "ok: true\njson_path: packet.json\nreviewed_input_binding:\n  usable: true\n", ""

    monkeypatch.setattr(SUPPORT, "run_command", prepare_command)
    packet = PACKET.prepare_packet(
        SUPPORT,
        tmp_path,
        args,
        "attempt",
        ["reviewed.txt"],
        {"data": {}},
        tmp_path / "prepare_packet.py",
    )
    assert packet == tmp_path / "packet.json"
    assert "--follow-up-from" in seen
    assert "prior.json" in seen
    assert "--range" in seen
    assert "base..head" in seen
    assert "--prepared-target" in seen

    monkeypatch.setattr(
        SUPPORT,
        "run_command",
        lambda _command, root: (1, "ok: false\n", "producer failed"),
    )
    with pytest.raises(SUPPORT.RunReviewError) as caught:
        PACKET.prepare_packet(
            SUPPORT,
            tmp_path,
            SimpleNamespace(
                prepared_for="repair",
                prepared_target=None,
                follow_up_from=None,
                commit=None,
                changed_range=None,
            ),
            "other-attempt",
            [],
            {"data": {}},
            tmp_path / "prepare_packet.py",
        )
    assert caught.value.code == "packet-invalid"
    assert caught.value.details["stderr"] == "producer failed"


def test_packet_loader_failures_and_prompt_carrier_mismatch_are_typed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(PACKET.importlib.util, "spec_from_file_location", lambda *_a, **_k: None)
    with pytest.raises(RuntimeError, match="semantic review input"):
        PACKET._load_semantic_input()
    with pytest.raises(RuntimeError, match="follow-up scope"):
        PACKET._load_followup_scope()

    packet = _packet_payload()
    with pytest.raises(ValueError, match="carriers do not exactly match"):
        PACKET.write_prompt(
            tmp_path / "prompt.md",
            packet,
            scope="scope",
            lens="lens",
            packet_sha="p" * 64,
            input_sha="i" * 64,
            semantic_input={"entries": []},
        )


def test_run_review_helper_boundaries_preserve_typed_semantic_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert RUN_REVIEW._adapter_name(tmp_path, {"path": "../outside.yaml"}) == "../outside.yaml"
    semantic_error = RUN_REVIEW.PACKET.SemanticInputError(
        "preimage-unavailable", "pre-image unavailable", details={"path": "deleted.txt"}
    )

    def fail_materialize(*_args, **_kwargs):  # noqa: ANN002, ANN003
        raise semantic_error

    monkeypatch.setattr(RUN_REVIEW.PACKET, "materialize_semantic_input", fail_materialize)
    with pytest.raises(SUPPORT.RunReviewError) as caught:
        RUN_REVIEW._materialize_semantic_input(tmp_path, {}, tmp_path / "run")
    assert caught.value.code == "preimage-unavailable"
    assert caught.value.details == {"path": "deleted.txt"}


def test_adapter_backend_selection_is_authoritative_and_has_explicit_fallbacks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configured = {
        "data": {
            "reviewer_runner": {
                "mode": "file-backed-worker",
                "backend": "codex_exec",
                "timeout_seconds": 7,
            }
        }
    }
    assert SUPPORT.select_backend(configured, None, dry_run=False) == ("codex_exec", 7)
    with pytest.raises(SUPPORT.RunReviewError, match="authoritative"):
        SUPPORT.select_backend(configured, "claude_p", dry_run=False)

    typed = {"data": {"reviewer_runner": {"mode": "typed-subagent"}}}
    with pytest.raises(SUPPORT.RunReviewError) as selected:
        SUPPORT.select_backend(typed, None, dry_run=True)
    assert selected.value.code == "typed-subagent-selected"

    host_defaulted = {"data": {"reviewer_runner": {"backend": "host-defaulted"}}}
    assert SUPPORT.select_backend(host_defaulted, "claude_p", dry_run=False)[0] == "claude_p"
    assert SUPPORT.select_backend(host_defaulted, None, dry_run=True)[0] is None
    monkeypatch.setattr(SUPPORT.shutil, "which", lambda _name: None)
    with pytest.raises(SUPPORT.RunReviewError) as unavailable:
        SUPPORT.select_backend(host_defaulted, None, dry_run=False)
    assert unavailable.value.code == "backend-unavailable"

    invalid_timeout = {"data": {"reviewer_runner": {"timeout_seconds": 0}}}
    with pytest.raises(SUPPORT.RunReviewError, match="positive integer"):
        SUPPORT.select_backend(invalid_timeout, None, dry_run=True)


def test_runner_injection_preserves_timeout_interruption_and_spawn_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stdout = tmp_path / "runner.stdout"
    stderr = tmp_path / "runner.stderr"

    monkeypatch.setattr(
        SUPPORT,
        "run_monitored_phase",
        lambda *args, **kwargs: SimpleNamespace(
            stdout="partial", stderr="diagnostic", timed_out=True, returncode=None
        ),
    )
    timeout = SUPPORT.run_runner(["worker"], root=tmp_path, stdout_path=stdout, stderr_path=stderr, timeout=4)
    assert timeout[0:3] == (124, "runner-timeout", True)
    assert "partial" == stdout.read_text(encoding="utf-8")
    assert "diagnostic" == stderr.read_text(encoding="utf-8")

    monkeypatch.setattr(SUPPORT, "run_monitored_phase", lambda *args, **kwargs: (_ for _ in ()).throw(KeyboardInterrupt))
    interrupted = SUPPORT.run_runner(
        ["worker"], root=tmp_path, stdout_path=stdout, stderr_path=stderr, timeout=4
    )
    assert interrupted == (
        130,
        "runner-interrupted",
        True,
        "canonical runner interrupted; worker group terminated",
    )

    monkeypatch.setattr(SUPPORT, "run_monitored_phase", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("spawn denied")))
    failed = SUPPORT.run_runner(
        ["worker"], root=tmp_path, stdout_path=stdout, stderr_path=stderr, timeout=4
    )
    assert failed == (None, "runner-invalid", False, "spawn denied")


def test_runner_output_classification_overrides_a_runner_invalid_carrier(tmp_path: Path) -> None:
    path = tmp_path / "runner.stdout"
    SUPPORT.write_yaml(path, {"status": "runner-invalid", "error": "worker refused"})

    assert SUPPORT.classify_runner_output(
        path, returncode=1, status="runner-completed", started=True, error=None
    ) == (1, "runner-invalid", False, "worker refused")
    assert SUPPORT.classify_runner_output(
        tmp_path / "missing", returncode=3, status="runner-completed", started=True, error="x"
    ) == (3, "runner-completed", True, "x")


def test_hold_out_bootstrap_fallback_and_owner_boundary_refusal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _block_first_import(monkeypatch, "scripts.runtime_scratch")
    module = load_script_module(
        "review_hold_out_bootstrap_fallback", SCRIPT_ROOT / "run_review_hold_out.py"
    )
    target = tmp_path / "in-progress.md"
    target.write_text("in progress\n", encoding="utf-8")

    with module.hold_out(
        tmp_path,
        ["in-progress.md"],
        resolve_path=SUPPORT.repo_path,
        error_cls=SUPPORT.RunReviewError,
    ):
        assert not target.exists()
    assert target.read_text(encoding="utf-8") == "in progress\n"

    outside = tmp_path.parent / "outside-hold-out.md"
    outside.write_text("outside\n", encoding="utf-8")

    def escaped(_root: Path, _value: str, **_kwargs: object) -> Path:
        return outside

    with pytest.raises(SUPPORT.RunReviewError) as escaped_error:
        with module.hold_out(
            tmp_path, ["outside-hold-out.md"], resolve_path=escaped, error_cls=SUPPORT.RunReviewError
        ):
            pass
    assert escaped_error.value.code == "hold-out-invalid"


def test_identity_binding_requires_the_attempt_and_expected_run_plan() -> None:
    expected = {
        "attempt_id": "attempt-1",
        "packet_sha256": "p" * 64,
        "reviewed_input_identity_sha256": "i" * 64,
        "parent_receipt_identity": "parent-1",
    }
    report = {
        "attempt_id": "wrong",
        "packet_identity": expected["packet_sha256"],
        "reviewed_input_identity": expected["reviewed_input_identity_sha256"],
        "parent_receipt_identity": expected["parent_receipt_identity"],
        "provenance": {"packet_identity": expected["packet_sha256"]},
    }
    binding = IDENTITY.identity_binding(report, expected)
    assert binding["status"] == "mismatch"
    assert binding["checks"]["attempt_id"]["matches"] is False

    unbound = IDENTITY.identity_binding(report, None)
    assert unbound["status"] == "unbound"
    assert unbound["matches"] is False
    approval, details = IDENTITY.approval_for(report, expected_identities=expected)
    assert approval is False
    assert details["approval"]["reason"] == "final lifecycle carrier was not supplied"


def test_carrier_manifest_integrity_rejects_bad_shapes_and_binds_hashes(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.json"
    file_path = tmp_path / "result.json"
    file_path.write_text("result\n", encoding="utf-8")
    SUPPORT.write_json(manifest, {"files": {"result": "result.json"}})

    integrity = CARRIER.refresh_manifest_integrity(SUPPORT, STORAGE, tmp_path, "manifest.json")
    assert integrity["result"]["bytes"] == len("result\n")
    assert integrity["result"]["sha256"] == hashlib.sha256(b"result\n").hexdigest()

    for payload, message in ((["not a mapping"], "not a mapping"), ({}, "no file map")):
        bad = tmp_path / f"bad-{len(list(tmp_path.glob('bad-*')))}.json"
        SUPPORT.write_json(bad, payload)
        with pytest.raises(SUPPORT.RunReviewError, match=message):
            CARRIER.refresh_manifest_integrity(SUPPORT, STORAGE, tmp_path, bad.name)

    bad = tmp_path / "bad-non-string-key.yaml"
    bad.write_text("files:\n  1: result.json\n", encoding="utf-8")
    with pytest.raises(SUPPORT.RunReviewError, match="malformed file"):
        CARRIER.refresh_manifest_integrity(SUPPORT, STORAGE, tmp_path, bad.name)


def test_carrier_manifest_integrity_refuses_a_corrupt_readback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = tmp_path / "manifest.json"
    file_path = tmp_path / "result.json"
    file_path.write_text("result\n", encoding="utf-8")
    SUPPORT.write_json(manifest, {"files": {"result": "result.json"}})
    write_json = STORAGE.write_json_atomically

    def corrupt_readback(path: Path, payload: object) -> None:
        corrupted = dict(payload)
        corrupted["file_integrity"] = {}
        write_json(path, corrupted)

    monkeypatch.setattr(STORAGE, "write_json_atomically", corrupt_readback)
    with pytest.raises(SUPPORT.RunReviewError, match="did not read back"):
        CARRIER.refresh_manifest_integrity(SUPPORT, STORAGE, tmp_path, "manifest.json")


def test_carrier_write_and_stream_helpers_fail_closed_on_symlink_escape_and_mismatch(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "lifecycle.yaml"
    CARRIER.write_promoted_yaml(SUPPORT, STORAGE, tmp_path, "lifecycle.yaml", {"state": "failed"})
    assert yaml.safe_load(destination.read_text(encoding="utf-8")) == {"state": "failed"}

    outside = tmp_path.parent / "outside-lifecycle.yaml"
    outside.write_text("outside\n", encoding="utf-8")
    escaped = tmp_path / "escaped.yaml"
    escaped.symlink_to(outside)
    with pytest.raises(SUPPORT.RunReviewError, match="lifecycle symlink"):
        CARRIER.write_promoted_yaml(SUPPORT, STORAGE, tmp_path, "escaped.yaml", {})
    with pytest.raises(SUPPORT.RunReviewError, match="escaped repository root"):
        CARRIER.write_promoted_yaml(SUPPORT, STORAGE, tmp_path, "../outside-lifecycle.yaml", {})

    stream = tmp_path / "runner.stdout"
    report = tmp_path / "report.yaml"
    SUPPORT.write_yaml(stream, {"state": "stream"})
    SUPPORT.write_yaml(report, {"state": "report"})
    mismatch = CARRIER.compare_report_stream(SUPPORT, stream, report)
    assert mismatch["consistent"] is False
    assert "differs" in mismatch["reason"]
    missing = CARRIER.compare_report_stream(SUPPORT, tmp_path / "missing", report)
    assert missing["consistent"] is False
    assert "missing" in missing["reason"]


def test_failure_carrier_without_lifecycle_is_explicitly_preflight_blocked() -> None:
    carrier = CARRIER.failure_carrier(
        PACKET,
        None,
        scope="promotion",
        lens="failure semantics",
        error="adapter missing",
        code="adapter-invalid",
        details={"remedy": "repair adapter"},
    )
    assert carrier["execution_state"] == "preflight-blocked"
    assert carrier["reviewer_started"] is False
    assert carrier["approval_eligible"] is False
    assert carrier["paths"] == {}


def test_failure_carrier_projects_details_when_lifecycle_exists() -> None:
    lifecycle = SimpleNamespace(
        build_lifecycle=lambda **kwargs: {"schema_version": "lifecycle", **kwargs}
    )
    carrier = CARRIER.failure_carrier(
        PACKET,
        lifecycle,
        scope="promotion",
        lens="failure semantics",
        error="bad packet",
        code="packet-invalid",
        details={"remedy": "repair packet", "warning": "no reviewer"},
    )
    assert carrier["status"] == "runner-invalid"
    assert carrier["reason_code"] == "packet-invalid"
    assert carrier["remedy"] == "repair packet"
    assert carrier["warning"] == "no reviewer"


def test_promoted_paths_remove_scratch_aliases_and_rebind_partial_artifacts() -> None:
    context = {
        "paths": {
            "report": ".charness/scratch/critique-review/report.yaml",
            "ledger": ".charness/scratch/critique-review/delivery.json",
            "stable": "charness-artifacts/critique/stable.json",
        }
    }
    promoted = {
        "worker-report.yaml": "charness-artifacts/critique/workers/a/report.yaml",
        "delivery.json": "charness-artifacts/critique/workers/a/delivery.json",
        "runner.stderr": "charness-artifacts/critique/workers/a/runner.stderr",
    }
    bound = CARRIER.bind_promoted_paths(context, promoted, PROMOTION)
    assert bound["report"] == promoted["worker-report.yaml"]
    assert "runtime_report" not in bound
    assert bound["ledger"] == promoted["delivery.json"]

    carrier = {
        "partial_outputs": [None, {"path": ".charness/scratch/critique-review/runner.stderr"}],
        "output": {"artifacts": [{"path": ".charness/scratch/critique-review/runner.stderr"}]},
    }
    CARRIER.rebind_partial_artifacts(
        carrier,
        {"runner_stderr": ".charness/scratch/critique-review/runner.stderr"},
        {"runner_stderr": promoted["runner.stderr"]},
        PROMOTION,
    )
    assert carrier["partial_outputs"][1]["path"] == promoted["runner.stderr"]
    assert carrier["output"]["artifacts"][0]["path"] == promoted["runner.stderr"]


@pytest.mark.parametrize(
    ("status", "delivery", "expected"),
    [
        ("runner-timeout", "none", "timed-out"),
        ("runner-completed", "timed-out", "timed-out"),
        ("runner-interrupted", "none", "cancelled"),
        ("runner-completed", "interrupted", "cancelled"),
        ("runner-completed", "findings-received", "succeeded"),
        ("runner-completed", "none", "failed"),
    ],
)
def test_owner_terminal_state_keeps_timeout_cancel_and_failure_distinct(
    status: str, delivery: str, expected: str
) -> None:
    assert CARRIER.owner_terminal_state(
        status, {"execution_state": "terminal", "delivery_state": delivery}
    ) == expected


def test_storage_write_once_and_log_retention_refuse_replacement(tmp_path: Path) -> None:
    destination = tmp_path / "carrier.json"
    STORAGE.write_or_verify(destination, b"stable")
    STORAGE.write_or_verify(destination, b"stable")
    with pytest.raises(ValueError, match="overwrite durable reviewer metadata") as caught:
        STORAGE.write_or_verify(destination, b"changed")
    assert caught.value.code == "stale-artifact-refused"

    source = tmp_path / "runner.log"
    source.write_bytes(b"x" * (STORAGE.MAX_DURABLE_LOG_BYTES + 100))
    log = tmp_path / "retained.log"
    descriptor = STORAGE.promote_log(tmp_path, source, log)
    assert descriptor["truncated"] is True
    assert descriptor["bytes"] > descriptor["retained_bytes"]
    assert b"durable log truncated" in log.read_bytes()
    source.write_bytes(b"y" * (STORAGE.MAX_DURABLE_LOG_BYTES + 100))
    with pytest.raises(ValueError, match="overwrite durable reviewer log") as caught:
        STORAGE.promote_log(tmp_path, source, log)
    assert caught.value.code == "stale-artifact-refused"

    symlink = tmp_path / "metadata-link"
    symlink.symlink_to(destination)
    with pytest.raises(ValueError, match="durable reviewer metadata"):
        STORAGE.write_or_verify(symlink, b"stable")


def test_storage_semantic_promotion_rewrites_manifest_carrier_paths(tmp_path: Path) -> None:
    run_dir = tmp_path / ".charness" / "scratch" / "review"
    source_dir = run_dir / "semantic-input"
    source_dir.mkdir(parents=True)
    content = source_dir / "0000-content.bin"
    content.write_bytes(b"reviewed bytes\n")
    manifest = source_dir / "manifest.json"
    SUPPORT.write_json(
        manifest,
        {
            "entries": [
                {"path": "reviewed.txt", "carrier_path": SUPPORT.relative(tmp_path, content)}
            ]
        },
    )
    destination = tmp_path / "charness-artifacts" / "critique" / "workers" / "attempt"

    promoted = STORAGE_DIRECT.promote_semantic_inputs(
        tmp_path, {"run_dir": run_dir}, destination
    )
    assert promoted["semantic-input/0000-content.bin"].endswith("0000-content.bin")
    durable_manifest = destination / "semantic-input" / "manifest.json"
    payload = json.loads(durable_manifest.read_text(encoding="utf-8"))
    assert payload["entries"][0]["carrier_path"] == promoted["semantic-input/0000-content.bin"]


def test_storage_path_replacements_and_symlinked_inputs_are_safe(tmp_path: Path) -> None:
    run_dir = tmp_path / ".charness" / "scratch" / "review"
    source_dir = run_dir / "semantic-input"
    source_dir.mkdir(parents=True)
    content = source_dir / "0000-content.bin"
    content.write_bytes(b"reviewed\n")
    link = source_dir / "linked-content.bin"
    link.symlink_to(content)
    destination = tmp_path / "durable" / "0000-content.bin"
    paths = {"prompt": run_dir / "review-prompt.md", "runner_stdout": run_dir / "runner.stdout"}
    promoted = {
        "review-prompt.md": "durable/review-prompt.md",
        "runner.stdout": "durable/runner.stdout",
        "semantic-input/0000-content.bin": "durable/0000-content.bin",
    }
    replacements = STORAGE_DIRECT.report_path_replacements(paths, promoted)
    assert replacements[str(paths["prompt"])] == "durable/review-prompt.md"
    assert STORAGE_DIRECT.semantic_path_replacements(
        tmp_path, {"run_dir": run_dir}, promoted
    ) == {SUPPORT.relative(tmp_path, content): "durable/0000-content.bin"}

    destination.parent.mkdir(parents=True)
    STORAGE_DIRECT.copy_or_verify(content, destination)
    assert destination.read_bytes() == content.read_bytes()

    log_link = tmp_path / "log-link"
    log_link.symlink_to(destination)
    with pytest.raises(ValueError, match="durable reviewer log"):
        STORAGE_DIRECT.promote_log(tmp_path, content, log_link)


def test_storage_worker_report_destination_guards_refuse_symlinks_and_escape(
    tmp_path: Path,
) -> None:
    runtime = tmp_path / "runtime-report.yaml"
    runtime.write_text("status: runner-invalid\n", encoding="utf-8")
    workers = tmp_path / STORAGE_DIRECT.DURABLE_WORKER_REPORTS
    workers.mkdir(parents=True)
    outside = tmp_path.parent / "worker-destination"
    outside.mkdir()
    (workers / "linked").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="worker directory symlink"):
        STORAGE_DIRECT.promote_worker_report(tmp_path, "linked", runtime)
    with pytest.raises(ValueError, match="escaped repository root"):
        STORAGE_DIRECT.promote_worker_report(tmp_path, "../../../../worker-escape", runtime)


def test_partial_scanner_finds_nested_result_and_rejects_wrong_identity(
    tmp_path: Path,
) -> None:
    packet = "p" * 64
    reviewed = "a" * 64
    source = tmp_path / "backend.stdout"
    candidate = {
        "kind": "charness.bounded_review.v1",
        "packet_sha256": packet,
        "reviewed_input_identity_sha256": reviewed,
        "verdict": "defer",
        "findings": [],
        "counterweight_triage": [],
        "next_move": "retry",
        "non_claims": ["not approval"],
    }
    source.write_text(json.dumps({"envelope": [candidate]}) + "\n", encoding="utf-8")
    found = STORAGE_DIRECT.extract_partial_review(
        {"backend_stdout": source},
        None,
        expected_identities={"packet_sha256": packet, "reviewed_input_identity_sha256": reviewed},
    )
    assert found is not None and found[0]["verdict"] == "defer"

    source.write_text(
        json.dumps({"envelope": [{**candidate, "packet_sha256": "wrong"}]}) + "\n",
        encoding="utf-8",
    )
    assert STORAGE_DIRECT.extract_partial_review(
        {"backend_stdout": source},
        None,
        expected_identities={"packet_sha256": packet, "reviewed_input_identity_sha256": reviewed},
    ) is None


def test_partial_review_extraction_requires_both_identities_and_reports_sources(tmp_path: Path) -> None:
    packet = "p" * 64
    reviewed = "i" * 64
    stderr = tmp_path / "runner.stderr"
    stderr.write_text(
        "ordinary diagnostic\n"
        + json.dumps(
            {
                "kind": "charness.bounded_review.v1",
                "packet_sha256": packet,
                "reviewed_input_identity_sha256": reviewed,
                "verdict": "defer",
                "findings": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    diagnostics: dict[str, object] = {}
    found = STORAGE_DIRECT.extract_partial_review(
        {"runner_stderr": stderr},
        None,
        diagnostics,
        expected_identities={"packet_sha256": packet, "reviewed_input_identity_sha256": reviewed},
    )
    assert found is not None
    assert found[0]["verdict"] == "defer"
    assert diagnostics["status"] == "preserved"
    assert diagnostics["sources"][0]["key"] == "runner.stderr"

    no_identity: dict[str, object] = {}
    assert STORAGE_DIRECT.extract_partial_review({"runner_stderr": stderr}, None, no_identity) is None
    assert "identities" in str(no_identity["reason"])


def test_storage_and_promotion_support_loaders_refuse_unavailable_helpers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evict_module(monkeypatch, "charness_run_review_support")
    evict_module(monkeypatch, "run_review_support")
    monkeypatch.setattr(STORAGE_DIRECT.importlib.util, "spec_from_file_location", lambda *_a, **_k: None)
    with pytest.raises(RuntimeError, match="cannot load run_review_support"):
        STORAGE_DIRECT._support()

    evict_module(monkeypatch, "charness_run_review_support")
    evict_module(monkeypatch, "run_review_support")
    monkeypatch.setattr(PROMOTION_DIRECT.importlib.util, "spec_from_file_location", lambda *_a, **_k: None)
    with pytest.raises(RuntimeError, match="cannot load run_review_support"):
        PROMOTION_DIRECT._support()


def test_storage_and_promotion_reload_support_after_cache_eviction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evict_module(monkeypatch, "charness_run_review_support")
    evict_module(monkeypatch, "run_review_support")
    assert STORAGE_DIRECT._support().RunReviewError is not None
    evict_module(monkeypatch, "charness_run_review_support")
    evict_module(monkeypatch, "run_review_support")
    assert PROMOTION_DIRECT._support().RunReviewError is not None


def test_run_review_loader_and_main_preflight_refusals_are_typed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class FailingLoader:
        def create_module(self, _spec):
            return ModuleType("charness_run_review_support")

        def exec_module(self, _module):
            raise RuntimeError("support load failed")

    spec = RUN_REVIEW.importlib.util.spec_from_loader(
        "charness_run_review_support", FailingLoader()
    )
    monkeypatch.setattr(RUN_REVIEW.importlib.util, "spec_from_file_location", lambda *_a, **_k: spec)
    evict_module(monkeypatch, "charness_run_review_support")
    with pytest.raises(RuntimeError, match="support load failed"):
        RUN_REVIEW._load_support()
    assert "charness_run_review_support" not in sys.modules
    monkeypatch.setattr(RUN_REVIEW.importlib.util, "spec_from_file_location", lambda *_a, **_k: None)
    with pytest.raises(RuntimeError, match="semantic review support"):
        RUN_REVIEW._load_support()

    with pytest.raises(SystemExit):
        RUN_REVIEW.main(["--repo-root", str(tmp_path), "--scope", "x"])
    with pytest.raises(SystemExit):
        RUN_REVIEW.main(
            [
                "--repo-root",
                str(tmp_path),
                "--scope",
                "x",
                "--lens",
                "y",
                "--commit",
                "HEAD",
                "--range",
                "HEAD^..HEAD",
            ]
        )
    with pytest.raises(SystemExit):
        RUN_REVIEW.main(
            [
                "--repo-root",
                str(tmp_path),
                "--resume-retained-attempt",
                "retained",
                "--packet-file",
                "packet.json",
            ]
        )
