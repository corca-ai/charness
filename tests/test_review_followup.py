from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from scripts.review.reviewed_input_identity import build_reviewed_input_identity
from tests.quality_gates.repo_shapes import install_committed_repo

HELPER_PATH = Path(__file__).resolve().parents[1] / "skills/public/critique/scripts/review_followup.py"
_spec = importlib.util.spec_from_file_location("test_review_followup_helper", HELPER_PATH)
assert _spec is not None and _spec.loader is not None
FOLLOWUP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FOLLOWUP)


def _prior_review(repo: Path) -> tuple[str, Path]:
    identity = build_reviewed_input_identity(
        repo_root=repo,
        reviewed_paths=["a.py", "b.py"],
        substrate_mode="working-tree",
    )
    packet = repo / "charness-artifacts/critique/prior-packet.json"
    packet.parent.mkdir(parents=True)
    packet.write_text(
        json.dumps(
            {
                "kind": "charness.critique_prepare_packet",
                "version": 1,
                "sections": [{"content": "prior"}],
                "section_count": 1,
                "ok": True,
                "reviewed_input_identity": identity,
            }
        ),
        encoding="utf-8",
    )
    packet_sha256 = hashlib.sha256(packet.read_bytes()).hexdigest()
    attempt = repo / "charness-artifacts/critique/workers/prior"
    attempt.mkdir(parents=True)
    semantic = attempt / "semantic-input"
    semantic.mkdir()
    semantic_entries = []
    for index, name in enumerate(("a.py", "b.py")):
        content = (repo / name).read_bytes()
        carrier = semantic / f"{index:04d}-content.bin"
        carrier.write_bytes(content)
        digest = hashlib.sha256(b"file\0-\0" + content).hexdigest()
        carrier_digest = hashlib.sha256(content).hexdigest()
        semantic_entries.append(
            {
                "path": name,
                "carrier_path": carrier.relative_to(repo).as_posix(),
                "content_sha256": digest,
                "carrier_sha256": carrier_digest,
            }
        )
    (semantic / "manifest.json").write_text(
        json.dumps(
            {
                "kind": "charness.semantic_input_carrier.v1",
                "entries": semantic_entries,
            }
        ),
        encoding="utf-8",
    )
    (attempt / "run-plan.json").write_text(
        json.dumps(
            {
                "attempt_id": "prior",
                "packet_path": "charness-artifacts/critique/prior-packet.json",
                "packet_sha256": packet_sha256,
                "reviewed_input_identity_sha256": identity["identity_sha256"],
                "parent_receipt_identity": "pending",
            }
        ),
        encoding="utf-8",
    )
    result = attempt / "partial-result.json"
    result_payload = {
        "kind": "charness.bounded_review.v1",
        "attempt_id": "prior",
        "packet_sha256": packet_sha256,
        "reviewed_input_identity_sha256": identity["identity_sha256"],
        "verdict": "block",
        "scope": "prior scope",
        "findings": [
            {
                "id": "F-1",
                "severity": "blocker",
                "summary": "The old behavior is unsafe.",
                "action": "Repair it and rerun the bounded check.",
                "evidence": ["a.py: old behavior"],
            }
        ],
        "next_move": "Repair the finding.",
    }
    result.write_text(json.dumps(result_payload), encoding="utf-8")
    result_path = result.parent / "result.json"
    result_path.write_text(json.dumps(result_payload), encoding="utf-8")
    backend = result.parent / "backend.stdout"
    backend.write_bytes(result.read_bytes())
    result_digest = hashlib.sha256(result_path.read_bytes()).hexdigest()
    plan_path = attempt / "run-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    unsigned_plan = dict(plan)
    unsigned_plan.pop("parent_receipt_identity", None)
    parent_identity = "parent-" + hashlib.sha256(
        (json.dumps(unsigned_plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    ).hexdigest()[:48]
    plan["parent_receipt_identity"] = parent_identity
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    result_descriptor = {
        "schema_version": "charness.reviewer_partial_output/v1",
        "kind": "bounded-review-result",
        "path": result.relative_to(repo).as_posix(),
        "source": backend.relative_to(repo).as_posix(),
        "bytes": result.stat().st_size,
        "sha256": hashlib.sha256(result.read_bytes()).hexdigest(),
        "approval_eligible": False,
    }
    (attempt / "receipt.json").write_text(
        json.dumps(
            {
                "attempt_id": "prior",
                "packet_identity": packet_sha256,
                "reviewed_input_identity": identity["identity_sha256"],
                "parent_receipt_identity": parent_identity,
                "output_file": result_path.relative_to(repo).as_posix(),
                "output_sha256": result_digest,
            }
        ),
        encoding="utf-8",
    )
    (attempt / "delivery.json").write_text(
        json.dumps(
            {
                "attempts": [
                    {
                        "attempt_id": "prior",
                        "packet_identity": packet_sha256,
                        "reviewed_input_identity": identity["identity_sha256"],
                        "parent_receipt_identity": parent_identity,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (attempt / "worker-report.yaml").write_text(
        json.dumps(
            {
                "attempt_id": "prior",
                "packet_identity": packet_sha256,
                "reviewed_input_identity": identity["identity_sha256"],
                "receipt_path": (attempt / "receipt.json").relative_to(repo).as_posix(),
                "ledger_path": (attempt / "delivery.json").relative_to(repo).as_posix(),
                "producer_binding": {"output_file": result_path.relative_to(repo).as_posix()},
                "receipt_output_sha256": result_digest,
            }
        ),
        encoding="utf-8",
    )
    (attempt / "attempt-manifest.json").write_text(
        json.dumps(
            {
                "attempt_id": "prior",
                "packet_identity": packet_sha256,
                "reviewed_input_identity": identity["identity_sha256"],
                "partial_result": result_descriptor,
                "files": {
                    "partial-result.json": result.relative_to(repo).as_posix(),
                    "backend.stdout": backend.relative_to(repo).as_posix(),
                },
                "logs": {
                    "backend.stdout": {
                        "path": backend.relative_to(repo).as_posix(),
                        "bytes": backend.stat().st_size,
                        "sha256": hashlib.sha256(backend.read_bytes()).hexdigest(),
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    return "charness-artifacts/critique/workers/prior/partial-result.json", result


def test_followup_defaults_to_changed_prior_inputs(tmp_path: Path) -> None:
    repo = install_committed_repo(
        tmp_path / "repo",
        {"a.py": "VALUE = 1\n", "b.py": "VALUE = 2\n"},
    )
    source_value, _ = _prior_review(repo)
    (repo / "a.py").write_text("VALUE = 3\n", encoding="utf-8")

    paths, context = FOLLOWUP.build_followup(
        repo_root=repo,
        source_value=source_value,
        explicit_paths=None,
        build_identity=build_reviewed_input_identity,
    )

    assert paths == ["a.py"]
    assert context["selection"] == "changed-prior-inputs"
    assert context["prior_findings"][0]["id"] == "F-1"
    assert context["prior_verdict"] == "block"
    assert context["prior_reviewed_paths"] == 2
    assert context["selection_receipt"]["prior_binding"]["status"] == "verified"
    assert context["selection_receipt"]["selected_changed_prior_paths"] == ["a.py"]


def test_followup_refuses_when_prior_inputs_have_no_delta(tmp_path: Path) -> None:
    repo = install_committed_repo(
        tmp_path / "repo", {"a.py": "VALUE = 1\n", "b.py": "VALUE = 2\n"}
    )
    source_value, _ = _prior_review(repo)

    with pytest.raises(FOLLOWUP.FollowupError, match="no previously reviewed input changed"):
        FOLLOWUP.build_followup(
            repo_root=repo,
            source_value=source_value,
            explicit_paths=None,
            build_identity=build_reviewed_input_identity,
        )


def test_followup_can_explicitly_add_a_new_path(tmp_path: Path) -> None:
    repo = install_committed_repo(
        tmp_path / "repo", {"a.py": "VALUE = 1\n", "b.py": "VALUE = 2\n"}
    )
    source_value, _ = _prior_review(repo)
    (repo / "new.py").write_text("VALUE = 4\n", encoding="utf-8")

    paths, context = FOLLOWUP.build_followup(
        repo_root=repo,
        source_value=source_value,
        explicit_paths=["new.py"],
        build_identity=build_reviewed_input_identity,
    )

    assert paths == ["new.py"]
    assert context["selection"] == "explicit-with-selection-receipt"
    assert context["selection_receipt"]["new_paths"] == ["new.py"]


def test_followup_refuses_a_tampered_prior_packet(tmp_path: Path) -> None:
    repo = install_committed_repo(
        tmp_path / "repo", {"a.py": "VALUE = 1\n", "b.py": "VALUE = 2\n"}
    )
    source_value, _ = _prior_review(repo)
    packet = repo / "charness-artifacts/critique/prior-packet.json"
    payload = json.loads(packet.read_text(encoding="utf-8"))
    payload["tampered"] = True
    packet.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(FOLLOWUP.FollowupError, match="packet bytes do not match") as error:
        FOLLOWUP.build_followup(
            repo_root=repo,
            source_value=source_value,
            explicit_paths=None,
            build_identity=build_reviewed_input_identity,
        )

    assert error.value.code == "prior-packet-tampered"


def test_followup_refuses_a_tampered_prior_semantic_carrier(tmp_path: Path) -> None:
    repo = install_committed_repo(
        tmp_path / "repo", {"a.py": "VALUE = 1\n", "b.py": "VALUE = 2\n"}
    )
    source_value, _ = _prior_review(repo)
    carrier = repo / "charness-artifacts/critique/workers/prior/semantic-input/0000-content.bin"
    carrier.write_bytes(b"tampered\n")

    with pytest.raises(FOLLOWUP.FollowupError, match="prior semantic carrier bytes") as error:
        FOLLOWUP.build_followup(
            repo_root=repo,
            source_value=source_value,
            explicit_paths=None,
            build_identity=build_reviewed_input_identity,
        )

    assert error.value.code == "prior-semantic-input-tampered"


def test_followup_refuses_partial_replacement_even_when_manifest_is_rewritten(
    tmp_path: Path,
) -> None:
    repo = install_committed_repo(
        tmp_path / "repo", {"a.py": "VALUE = 1\n", "b.py": "VALUE = 2\n"}
    )
    source_value, partial = _prior_review(repo)
    (repo / "a.py").write_text("VALUE = 3\n", encoding="utf-8")
    tampered = json.loads(partial.read_text(encoding="utf-8"))
    tampered["findings"] = []
    partial.write_text(json.dumps(tampered), encoding="utf-8")
    manifest_path = partial.parent / "attempt-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["partial_result"]["bytes"] = partial.stat().st_size
    manifest["partial_result"]["sha256"] = hashlib.sha256(partial.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(FOLLOWUP.FollowupError) as error:
        FOLLOWUP.build_followup(
            repo_root=repo,
            source_value=source_value,
            explicit_paths=None,
            build_identity=build_reviewed_input_identity,
        )

    assert error.value.code == "prior-result-tampered"


def test_followup_rejects_an_implicit_committed_ref_change() -> None:
    identity = {
        "status": "captured",
        "reviewed_paths": ["a.py"],
        "reviewed_content": [{"path": "a.py", "content_sha256": "x"}],
        "substrate_mode": "committed-ref",
        "mode": "committed-ref",
        "changed_ref": "HEAD",
    }

    def error(code: str, message: str, *, details: dict | None = None) -> Exception:
        return FOLLOWUP.FollowupError(code, message, details=details)

    with pytest.raises(FOLLOWUP.FollowupError) as raised:
        FOLLOWUP.SELECTION.select_paths(
            repo_root=Path("."),
            identity=identity,
            prior_paths=["a.py"],
            explicit_paths=None,
            prior_mode="committed-ref",
            current_mode="committed-ref",
            changed_ref="HEAD^",
            build_identity=lambda **_: {},
            prior_binding={"status": "verified"},
            error=error,
        )

    assert raised.value.code == "follow-up-ref-mismatch"


def test_followup_context_has_a_hard_byte_bound() -> None:
    context = {
        "kind": "charness.review_followup.v1",
        "source": "prior",
        "source_sha256": "a" * 64,
        "prior_attempt_id": "prior",
        "prior_verdict": "block",
        "prior_packet_path": "packet.json",
        "prior_packet_sha256": "b" * 64,
        "prior_reviewed_input_identity_sha256": "c" * 64,
        "selection": "explicit-with-selection-receipt",
        "selected_paths": [f"src/{index:05d}-very-long-file-name.py" for index in range(10000)],
        "selection_receipt": {
            "selected_changed_prior_paths": [f"src/{index:05d}-very-long-file-name.py" for index in range(10000)],
            "new_paths": [],
        },
        "prior_findings": [
            {
                "id": f"F-{index}",
                "severity": "blocker",
                "summary": "x" * 5000,
                "action": "y" * 5000,
                "evidence": ["z" * 5000] * 4,
            }
            for index in range(64)
        ],
        "approval_rule": "selection is not approval",
    }

    bounded = FOLLOWUP._bound_context(context)

    assert len(FOLLOWUP._context_bytes(bounded)) <= FOLLOWUP.MAX_CONTEXT_BYTES
    assert bounded["selected_paths"]["summarized"] is True


def test_final_followup_identity_binding_measures_its_size_field() -> None:
    identity = {"identity_sha256": "a" * 64, "reviewed_paths": []}
    candidate = None
    for padding_size in range(FOLLOWUP.MAX_CONTEXT_BYTES - 512, FOLLOWUP.MAX_CONTEXT_BYTES):
        base = {"kind": "charness.review_followup.v1", "padding": "x" * padding_size}
        measured = dict(base)
        measured["final_reviewed_input_identity_sha256"] = identity["identity_sha256"]
        measured["final_selected_path_count"] = 0
        before_size = len(FOLLOWUP._context_bytes(measured))
        measured["context_size_bytes"] = before_size
        if (
            before_size <= FOLLOWUP.MAX_CONTEXT_BYTES
            and len(FOLLOWUP._context_bytes(measured)) > FOLLOWUP.MAX_CONTEXT_BYTES
        ):
            candidate = base
            break

    assert candidate is not None

    with pytest.raises(FOLLOWUP.FollowupError, match="hard byte bound"):
        FOLLOWUP.bind_final_identity(candidate, identity)
