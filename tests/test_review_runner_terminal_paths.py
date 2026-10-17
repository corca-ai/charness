"""Runner errors must preserve resumable bytes; recovery must read back before cleanup."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from tests.charness_cli.worktree_fixtures import copy_worktree_seed
from tests.quality_gates.seeding_support import git as fixture_git
from tests.test_review_recovery_failures import (
    EXECUTION,
    PACKET,
    PROMOTION,
    RECOVERY,
    SCRIPT_ROOT,
    SUPPORT,
    _RecoveryOwner,
)


class Owner(_RecoveryOwner):
    def __init__(self, path):
        super().__init__(path)
        self.retained = []

    def update(self, **kwargs):
        self.identity = kwargs

    def retain_with(self, **kwargs):
        self.retained.append(kwargs)


@pytest.mark.boundary_contract(
    reason="A real linked checkout is required to route final review bytes to its primary worktree."
)
def test_primary_collision_preserves_original_and_retains_reviewer_scratch(tmp_path):
    primary = copy_worktree_seed(tmp_path, "primary")
    (primary / ".gitignore").write_text("charness-artifacts/critique/\n", encoding="utf-8")
    fixture_git(primary, "add", ".gitignore")
    fixture_git(primary, "commit", "-m", "ignore critique runtime")
    linked = tmp_path / "linked"
    fixture_git(primary, "worktree", "add", "-b", "review-collision", str(linked))

    run = tmp_path / "runtime"
    run.mkdir()
    owner = Owner(run)
    canonical = tmp_path / "schema.json"
    canonical.write_text("{}")
    packet_relative = Path("charness-artifacts/critique/collision-packet.json")
    packet_path = linked / packet_relative
    packet_path.parent.mkdir(parents=True)
    packet_path.write_bytes(b'{"packet":"bound"}\n')
    primary_packet = primary / packet_relative
    primary_packet.parent.mkdir(parents=True)
    primary_packet.write_bytes(packet_path.read_bytes())
    primary_attempt = primary / PROMOTION.DURABLE_WORKER_REPORTS / "a"
    primary_attempt.mkdir(parents=True)
    original = b"original primary proof\n"
    (primary_attempt / "result.json").write_bytes(original)
    (primary_attempt / "attempt-manifest.json").write_bytes(b"{}\n")
    for name in ("receipt.json", "delivery.json", "result.json", "worker-report.yaml", "lifecycle.yaml"):
        (run / name).write_text("{}")

    emitted = []

    def finalize(_support, _promotion, root, attempt_id, paths, *_args):
        linked_attempt = root / PROMOTION.DURABLE_WORKER_REPORTS / attempt_id
        linked_attempt.mkdir(parents=True, exist_ok=True)
        (linked_attempt / "result.json").write_bytes(b"new linked proof\n")
        (linked_attempt / "attempt-manifest.json").write_bytes(b"{}\n")
        PROMOTION.PRIMARY_PROMOTION.promote_finalized_closure(
            SUPPORT,
            PROMOTION.STORAGE,
            PROMOTION.DURABLE_WORKER_REPORTS,
            root,
            attempt_id,
            paths,
        )

    support = _support(
        emit=emitted.append,
        load_goal_lineage=lambda *args, **kwargs: None,
        package_paths=lambda _path: {
            "schema": canonical,
            "partial_output": canonical,
            "resolve_adapter": canonical,
        },
        load_runtime=lambda _package: (
            NS(build_lifecycle=lambda **kwargs: {**kwargs, "approval_eligible": True}),
            NS(validate_capability_envelope=lambda *args, **kwargs: NS(envelope_sha256="cap")),
        ),
        load_module=lambda *args: NS(collect_run_logs=lambda *args, **kwargs: []),
        resolve_adapter=lambda *args: {"data": {"packet_sections": [{}]}},
        select_backend=lambda *args, **kwargs: ("codex_exec", 1),
        new_run_owner=lambda *args: owner,
        run_runner_held_out=lambda *args, **kwargs: (0, "runner-completed", True, None),
        classify_runner_output=lambda *args, **kwargs: (0, "runner-completed", True, None),
    )
    packet = NS(
        manifest_paths=lambda *args: [],
        select_packet=lambda *args: (packet_path, {}, "packet", "input", {}),
        run_paths=PACKET.run_paths,
        default_capability=lambda _root: {},
        write_prompt=lambda path, *args, **kwargs: Path(path).write_text("prompt\n"),
    )
    carrier = NS(
        failure_carrier=lambda *args, **kwargs: {
            "approval_eligible": False,
            "reason_code": kwargs["code"],
        },
        finalize_carrier=finalize,
        compare_report_stream=lambda *args: {"consistent": True, "reason": None},
        owner_terminal_state=lambda *args: "failed",
    )

    result = EXECUTION.run_live(
        NS(
            attempt_id="a",
            artifact_key="a",
            scope="test",
            lens="collision",
            goal_lineage_file=None,
            backend=None,
            dry_run=False,
            reviewed_paths_file=None,
            reviewed_path=[],
            hold_out=[],
        ),
        linked,
        support=support,
        packet=packet,
        invocation=NS(runner_command=lambda *args, **kwargs: []),
        promotion=NS(
            DURABLE_WORKER_REPORTS=PROMOTION.DURABLE_WORKER_REPORTS,
            load_and_promote_report=lambda *args: {"delivery_state": "findings-received"},
            identity_binding=lambda *args: {"matches": False},
        ),
        carrier_module=carrier,
        script_dir=SCRIPT_ROOT,
        read_only_boundary_mode="read-only",
        lifecycle_semantic_input=lambda value: value,
        materialize_semantic_input=lambda *args, **kwargs: {},
        semantic_review_paths=lambda _packet: ([], []),
        adapter_name=lambda *args: "adapter.yaml",
    )

    assert result == 2
    assert (primary_attempt / "result.json").read_bytes() == original
    assert owner.closed == [{"state": "failed"}]
    assert len(owner.retained) == 1
    assert emitted[-1]["durable_promotion"]["status"] == "failed"


def _support(**overrides):
    base = {k: getattr(SUPPORT, k) for k in (
        "RunReviewError", "relative", "sha256", "write_json", "write_yaml", "load_mapping", "repo_path",
    )}
    return NS(**{**base, **overrides})


@pytest.mark.parametrize("fault,fail_promotion", [
    ("schema", False), ("backend", False), ("typed", False), ("typed", True),
    ("unexpected", False), ("unexpected", True), ("identity", False), ("early", False),
])
def test_live_runner_disposes_terminal_failure_without_losing_retry_inputs(tmp_path, fault, fail_promotion):
    run = tmp_path / "run"
    run.mkdir()
    owner = Owner(run)
    canonical = tmp_path / "schema.json"
    canonical.write_text("{}")
    packet_path = tmp_path / "packet.json"
    packet_path.write_text("{}")
    for name in ("receipt.json", "delivery.json", "result.json", "worker-report.yaml", "lifecycle.yaml"):
        (run / name).write_text("{}")
    emitted, finalized = [], []
    def finalize(*args):
        finalized.append(args[6])
        if fail_promotion:
            raise OSError("durable destination unavailable")
    def invoke(*args, **kwargs):
        if fault == "typed":
            raise SUPPORT.RunReviewError("runner-refused", "refused before spawn")
        if fault == "unexpected":
            raise RuntimeError("transport crashed")
        return []
    def lineage(*args, **kwargs):
        if fault == "early":
            raise RuntimeError("lineage unavailable")
        return None
    def sha(path):
        if fault == "schema" and path == canonical:
            return "wrong"
        return SUPPORT.sha256(path)
    lifecycle = NS(build_lifecycle=lambda **kwargs: {**kwargs, "approval_eligible": True})
    support = _support(
        emit=emitted.append, load_goal_lineage=lineage,
        package_paths=lambda path: {"schema": canonical, "partial_output": canonical, "resolve_adapter": canonical},
        load_runtime=lambda package: (lifecycle, NS(validate_capability_envelope=lambda *a, **k: NS(envelope_sha256="cap"))),
        load_module=lambda *args: NS(collect_run_logs=lambda *args, **kwargs: []),
        resolve_adapter=lambda *args: {"data": {"packet_sections": [{}]}},
        select_backend=lambda *a, **k: (None if fault == "backend" else "codex_exec", 1),
        new_run_owner=lambda *args: owner, sha256=sha,
        run_runner_held_out=lambda *a, **k: (0, "runner-completed", True, None),
        classify_runner_output=lambda *a, **k: (0, "runner-completed", True, None),
    )
    def _write_prompt(path, *args, **kwargs):
        Path(path).write_text("terminal prompt\n", encoding="utf-8")

    packet = NS(
        manifest_paths=lambda *args: [],
        select_packet=lambda *args: (packet_path, {}, "packet", "input", {}),
        run_paths=PACKET.run_paths, default_capability=lambda root: {},
        write_prompt=_write_prompt,
    )
    carrier = NS(
        failure_carrier=lambda *a, **k: {"approval_eligible": False, "reason_code": k["code"]},
        finalize_carrier=finalize,
        compare_report_stream=lambda *args: {"consistent": True, "reason": None},
        owner_terminal_state=lambda *args: "failed",
    )
    result = EXECUTION.run_live(
        NS(attempt_id="a", artifact_key="a", scope="test", lens="terminal", goal_lineage_file=None,
           backend=None, dry_run=False, reviewed_paths_file=None, reviewed_path=[], hold_out=[]),
        tmp_path, support=support, packet=packet, invocation=NS(runner_command=invoke),
        promotion=NS(DURABLE_WORKER_REPORTS="durable", load_and_promote_report=lambda *a: {"delivery_state": "findings-received"},
                     identity_binding=lambda *a: {"matches": False}),
        carrier_module=carrier, script_dir=SCRIPT_ROOT, read_only_boundary_mode="read-only",
        lifecycle_semantic_input=lambda x: x,
        materialize_semantic_input=lambda *args, **kwargs: {},
        semantic_review_paths=lambda _packet: ([], []),
        adapter_name=lambda *args: "adapter.yaml",
    )
    assert result == (1 if fault == "identity" else 2)
    assert emitted[-1]["approval_eligible"] is False
    if fault == "early":
        assert owner.closed == [] and finalized == []
    else:
        assert owner.closed == [{"state": "failed"}]
        assert bool(owner.retained) is fail_promotion
        if fail_promotion:
            assert emitted[-1]["durable_promotion"]["status"] == "failed"
            receipt = owner.retained[0]
            assert "--resume-retained-attempt a" in receipt["recovery_command"]
            assert receipt["delivery_sha256"] == SUPPORT.sha256(run / "delivery.json")
            assert receipt["result_sha256"] == SUPPORT.sha256(run / "result.json")


@pytest.mark.parametrize("fault", ["plan", "packet", "report", "validator", "identity", "stream", "chain", "promotion", "pass", "partial"])
def test_recovery_only_removes_retained_inputs_after_promoted_readback(tmp_path, fault, monkeypatch):
    run = tmp_path / "run"
    run.mkdir()
    owner = Owner(run)
    packet_path = tmp_path / "packet.json"
    packet_path.write_text("{}")
    plan = {"packet_path": "packet.json", "packet_sha256": "p", "reviewed_input_identity_sha256": "i", "parent_receipt_identity": "parent"}
    SUPPORT.write_json(run / "run-plan.json", [] if fault == "plan" else {} if fault == "packet" else plan)
    if fault != "report":
        SUPPORT.write_json(run / "worker-report.yaml", {"delivery_state": "findings-received"})
    emitted, events = [], []
    manifest = tmp_path / "attempt-manifest.json"
    SUPPORT.write_json(manifest, {"approval_eligible": False, "identity_binding": {"matches": True}})
    def validate(**kwargs):
        if fault == "validator":
            raise ValueError("unbound worker receipt")
    def finalize(*args):
        events.append("promote")
        if fault == "promotion":
            raise OSError("promotion unavailable")
        promoted_chain = chain(*args)
        saved = SUPPORT.load_mapping(manifest)
        if promoted_chain["ok"]:
            saved.update(
                approval_eligible=fault == "pass",
                use_class="approval" if fault == "pass" else "diagnostic-retryable",
                identity_binding={"matches": True},
            )
            SUPPORT.write_json(manifest, saved)
        real_read_text = Path.read_text

        def fail_postcommit_manifest_read(path, *read_args, **read_kwargs):
            if path == manifest:
                raise OSError("manifest acknowledgement read unavailable")
            return real_read_text(path, *read_args, **read_kwargs)

        monkeypatch.setattr(Path, "read_text", fail_postcommit_manifest_read)
        return {"promoted_chain": promoted_chain, "manifest": saved}
    def chain(*args, **kwargs):
        events.append("readback")
        assert SUPPORT.load_mapping(manifest)["approval_eligible"] is False
        return {"ok": fault != "chain", "reason": "bad durable chain", "attempt_manifest": manifest.name}
    modules = {
        "carrier": NS(validate_delivered_worker_report=validate),
        "identity": NS(),
        "lifecycle": NS(build_lifecycle=lambda **kwargs: {"approval_eligible": False}),
        "run_review_recovery_inputs.py": NS(validate_retained_inputs=lambda *a, **k: {"ok": True}),
        "run_review_carrier.py": NS(compare_report_stream=lambda *a: {"consistent": fault != "stream"}, finalize_carrier=finalize),
    }
    support = _support(
        owned_scratch=lambda *a, **k: owner, emit=emitted.append,
        package_paths=lambda path: {"carrier_validation": Path("carrier"), "identity_verification": Path("identity"), "lifecycle": Path("lifecycle")},
        load_module=lambda path, name: modules[path.name],
    )
    kwargs = dict(support=support, packet=PACKET, script_dir=SCRIPT_ROOT,
                  promotion=NS(identity_binding=lambda *a: {"matches": fault != "identity"},
                               approval_for=lambda *a, **k: (fault == "pass", {"matches": fault != "identity"})))
    if fault in {"plan", "packet", "promotion"}:
        with pytest.raises((SUPPORT.RunReviewError, OSError)):
            RECOVERY.resume_retained_attempt(tmp_path, "a", **kwargs)
        assert owner.closed == [{"state": "failed"}]
    else:
        rc = RECOVERY.resume_retained_attempt(tmp_path, "a", **kwargs)
        assert rc == (0 if fault == "pass" else 1)
        recovered = fault in {"pass", "partial"}
        assert emitted[-1]["status"] == ("recovered" if recovered else "refused")
        assert emitted[-1]["approval_eligible"] is (fault == "pass")
        if recovered:
            assert emitted[-1]["identity_binding"] == {"matches": True}
        assert owner.closed == ([{"state": "succeeded", "remove_retained": True}] if recovered else [{"state": "failed"}])
        assert events == (["promote", "readback"] if recovered or fault == "chain" else [])
