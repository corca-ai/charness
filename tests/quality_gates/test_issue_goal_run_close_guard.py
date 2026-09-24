from __future__ import annotations

import hashlib
import json
import runpy
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.quality_gates.issue_goal_run_test_support import (
    _fixture_metadata,
)
from tests.quality_gates.issue_goal_run_test_support import (
    close_inputs as _close_inputs,
)
from tests.quality_gates.issue_goal_run_test_support import (
    parent_body as _parent_body,
)

ROOT = Path(__file__).resolve().parents[2]
GUARD = runpy.run_path(
    str(ROOT / "skills/public/issue/scripts/issue_goal_run_guard.py")
)
CLOSE_PATH = ROOT / "skills/public/issue/scripts/issue_goal_run_close.py"
REPO = "corca-ai/charness"
CHILD_BODY = "old child body\n"

MENTION = "the body file must already contain the `<!-- charness-goal-run:v1 ... -->` block"


def _real_block() -> str:
    return (
        "<!-- charness-goal-run:v1\n"
        + json.dumps({"binding_schema": "charness.goal-binding/v1"})
        + "\n-->"
    )


def test_inline_code_marker_mention_does_not_block_close() -> None:
    GUARD["refuse_generic_close"](
        f"## Situation\n\n{MENTION}, which eight fields it needs.\n",
        context="target issue body",
    )


def test_fenced_marker_mention_does_not_block_close() -> None:
    body = f"## Evidence\n\n```text\n{MENTION}\n```\n\nPlain prose after the fence.\n"
    GUARD["refuse_generic_close"](body, context="target issue body")


def test_real_block_still_requires_goal_run_close() -> None:
    with pytest.raises(RuntimeError, match="goal-run-close-required"):
        GUARD["refuse_generic_close"](
            f"Human prose.\n\n{_real_block()}\n", context="target issue body"
        )


def test_real_block_is_found_beside_a_code_mention() -> None:
    with pytest.raises(RuntimeError, match="goal-run-close-required"):
        GUARD["refuse_generic_close"](
            f"{MENTION}\n\n{_real_block()}\n", context="target issue body"
        )


def test_bare_malformed_marker_still_refuses() -> None:
    with pytest.raises(RuntimeError, match="duplicate or malformed"):
        GUARD["refuse_generic_close"](
            "Human prose with a bare <!-- charness-goal-run:v1 fragment.\n",
            context="target issue body",
        )


def test_non_string_body_is_not_a_goal_run() -> None:
    GUARD["refuse_generic_close"](None, context="target issue body")


def test_tilde_fenced_marker_mention_does_not_block_close() -> None:
    body = f"## Evidence\n\n~~~\n{MENTION}\n~~~\n\nPlain prose after the fence.\n"
    GUARD["refuse_generic_close"](body, context="target issue body")


def test_unclosed_fence_cannot_hide_a_later_real_block() -> None:
    with pytest.raises(RuntimeError, match="goal-run-close-required"):
        GUARD["refuse_generic_close"](
            f"```text\nsome quoted code\n\n{_real_block()}\n",
            context="target issue body",
        )


def test_unclosed_fence_with_only_a_mention_still_refuses() -> None:
    with pytest.raises(RuntimeError, match="duplicate or malformed"):
        GUARD["refuse_generic_close"](
            "```text\nA bare <!-- charness-goal-run:v1 fragment after an unclosed fence.\n",
            context="target issue body",
        )


@pytest.mark.parametrize(
    ("record_mode", "expected_detail"),
    [("missing", "second-observer record"), ("same-file", "distinct files")],
)
def test_goal_run_close_requires_independent_evidence_for_parent_adjudication(
    tmp_path: Path, record_mode: str, expected_detail: str
) -> None:
    module = runpy.run_path(str(CLOSE_PATH))
    proof = _close_inputs(tmp_path, attempt_id="close-adjudication-missing")
    claim = "WI-10b non-authority clause: behaviorally present."
    obligation = tmp_path / "parent-obligation.md"
    obligation.write_text(
        "Close only after the bound proof is green.\n\n"
        "## Adjudications\n\n"
        f"- {claim}\n",
        encoding="utf-8",
    )
    index_path = tmp_path / "final-proof-index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["parent_obligation"]["sha256"] = hashlib.sha256(
        obligation.read_bytes()
    ).hexdigest()
    if record_mode == "same-file":
        report = tmp_path / "whole-system.json"
        report.write_text(
            "Critique for corca-ai/charness#725.\n"
            f"Parent adjudication: {claim}\n"
            "Second observer verdict: corroborated\n"
            "Independent evidence: whole-system.json\n\n"
            "Fresh-eye satisfaction: parent-delegated\n\n"
            "## Reviewer Tier Evidence\n"
            "- Requested tier: high-leverage\n"
            "- Requested spawn fields: typed bounded reviewer\n"
            "- Host exposure state: host-defaulted\n"
            "- Application state: n/a\n"
            "- Delivery state: findings-received\n"
            "- Execution mode: typed-subagent\n",
            encoding="utf-8",
        )
        digest = hashlib.sha256(report.read_bytes()).hexdigest()
        index["evidence"][0]["sha256"] = digest
        index["evidence"].append(
            {"role": "observer", "path": "whole-system.json", "sha256": digest}
        )
        index["parent_adjudications"] = [
            {
                "claim": claim,
                "child_number": 725,
                "observer_role": "observer",
                "independent_roles": ["whole-system"],
            }
        ]
    index_path.write_text(json.dumps(index), encoding="utf-8")
    proof_payload = json.loads(proof.read_text(encoding="utf-8"))
    proof_payload["final_proof_index_sha256"] = hashlib.sha256(
        index_path.read_bytes()
    ).hexdigest()
    proof.write_text(json.dumps(proof_payload), encoding="utf-8")
    emitted: list[dict[str, object]] = []

    rc = module["command_close"](
        Namespace(repo=REPO, number=724, proof_file=proof, repo_root=tmp_path),
        resolve_backend=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("uncorroborated adjudication must refuse before provider selection")
        ),
        emit=emitted.append,
    )

    assert rc == 2
    assert emitted[0]["status"] == "adjudication-uncorroborated"
    assert emitted[0]["mutation_invoked"] is False
    assert expected_detail in emitted[0]["error"]
    assert not (tmp_path / "observations").exists()


@pytest.mark.parametrize("adjudication_mode", ["clean", "override", "corroborated"])
def test_goal_run_close_carries_parent_adjudication_review(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, adjudication_mode: str
) -> None:
    module = runpy.run_path(str(CLOSE_PATH))
    proof = _close_inputs(tmp_path, attempt_id="close-2")
    adjudication_claim = "WI-10b non-authority clause: behaviorally present."
    if adjudication_mode != "clean":
        obligation = tmp_path / "parent-obligation.md"
        obligation.write_text(
            "Close only after the bound proof is green.\n\n"
            "## Adjudications\n\n"
            f"- {adjudication_claim}\n",
            encoding="utf-8",
        )
        index_path = tmp_path / "final-proof-index.json"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        index["parent_obligation"]["sha256"] = hashlib.sha256(
            obligation.read_bytes()
        ).hexdigest()
        if adjudication_mode == "override":
            index["parent_adjudications"] = [
                {
                    "claim": adjudication_claim,
                    "child_number": 725,
                    "override_reason": "The distinct report is unavailable; operator accepts this residual risk.",
                }
            ]
        else:
            report = tmp_path / "independent-adjudication-review.md"
            report.write_text(
                "Critique for corca-ai/charness#725.\n"
                f"Parent adjudication: {adjudication_claim}\n"
                "Second observer verdict: corroborated\n"
                "Independent evidence: whole-system.json\n\n"
                "Fresh-eye satisfaction: parent-delegated\n\n"
                "## Reviewer Tier Evidence\n\n"
                "- Requested tier: high-leverage\n"
                "- Requested spawn fields: typed bounded reviewer\n"
                "- Host exposure state: host-defaulted\n"
                "- Application state: n/a\n"
                "- Delivery state: findings-received\n"
                "- Execution mode: typed-subagent\n",
                encoding="utf-8",
            )
            index["evidence"].append(
                {
                    "role": "independent-adjudication-review",
                    "path": "independent-adjudication-review.md",
                    "sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
                }
            )
            index["parent_adjudications"] = [
                {
                    "claim": adjudication_claim,
                    "child_number": 725,
                    "observer_role": "independent-adjudication-review",
                    "independent_roles": ["whole-system"],
                }
            ]
        index_path.write_text(json.dumps(index), encoding="utf-8")
        proof_payload = json.loads(proof.read_text(encoding="utf-8"))
        proof_payload["final_proof_index_sha256"] = hashlib.sha256(
            index_path.read_bytes()
        ).hexdigest()
        proof.write_text(json.dumps(proof_payload), encoding="utf-8")
    parent = {
        "number": 724,
        "state": "OPEN",
        "body": _parent_body(tmp_path),
        "comments": [],
    }
    child = {"number": 725, "state": "CLOSED", "body": CHILD_BODY, "comments": [{"url": "comment"}]}
    reads: list[int] = []
    updated_parent = dict(parent)

    def read_issue(_repo: str, number: int, **_kwargs: object) -> dict[str, object]:
        reads.append(number)
        return {
            "issue": updated_parent
            if number == 724 and len(reads) > 2
            else parent
            if number == 724
            else child
        }

    module["command_close"].__globals__["READ"] = SimpleNamespace(
        read_issue_with_comments=read_issue
    )
    module["command_close"].__globals__["TRACKER"] = SimpleNamespace(
        list_sub_issues=lambda *_args, **_kwargs: {
            "children": [{"number": 725, "state": "CLOSED"}]
        },
        update_issue_body=lambda _repo, _number, body_file, **_kwargs: (
            updated_parent.update(state="CLOSED", body=body_file.read_text(encoding="utf-8"))
            or {
                "ok": True,
                "status": "verified-write",
                "outcome": "verified-write",
                "mutation_invoked": True,
                "body_verified": True,
            }
        ),
    )
    captured: dict[str, object] = {}
    closes: list[int] = []

    def close_with_comment(*_args: object, **kwargs: object) -> dict[str, object]:
        closes.append(1)
        captured.update(kwargs)
        return {"carrier": "test", "preflight_state": kwargs["preflight_state"]}

    module["command_close"].__globals__["CLOSE"] = SimpleNamespace(
        close_with_comment=close_with_comment
    )
    if adjudication_mode == "clean":
        contract = module["command_close"].__globals__["CONTRACT"].CLOSE_CONTRACT
        monkeypatch.setattr(
            contract.REVIEW._FRESH_EYE,
            "_observer_disposition",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(
                AssertionError("clean closeout must not invoke the second observer")
            ),
        )
    emitted: list[dict[str, object]] = []

    rc = module["command_close"](
        Namespace(repo=REPO, number=724, proof_file=proof, repo_root=tmp_path),
        resolve_backend=lambda _root, **_kwargs: {"adapter_ok": True, "backend": {"id": "gh"}},
        emit=emitted.append,
    )

    assert rc == 0
    assert reads == [724, 725, 724]
    assert captured["preflight_state"] == parent
    assert emitted[0]["status"] == "verified-write"
    assert emitted[0]["terminal_metadata"]["readback"]["state"] == "CLOSED"
    metadata = json.loads(updated_parent["body"].split("\n", 2)[1])
    fixture = _fixture_metadata(tmp_path)
    assert metadata["draft_sha256"] == fixture["draft_sha256"]
    assert metadata["binding_sha256"] == fixture["binding_sha256"]
    assert metadata["initial_graph_sha256"] == fixture["initial_graph_sha256"]
    assert metadata["parent_identity"] == {
        "number": 724,
        "repo": REPO,
        "url": f"https://github.com/{REPO}/issues/724",
    }
    assert metadata["progress"]["revision"] == 1
    assert metadata["terminal_observation_path"].endswith("close-2.terminal.json")
    assert metadata["terminal_observation_sha256"] == emitted[0]["observation"]["terminal_sha256"]
    assert closes == [1]
    terminal = json.loads(
        (tmp_path / emitted[0]["observation"]["terminal_path"]).read_text(encoding="utf-8")
    )
    if adjudication_mode == "clean":
        assert "parent_adjudication_review" not in emitted[0]
        assert "parent_adjudication_review" not in terminal["result"]
    elif adjudication_mode == "override":
        review = emitted[0]["parent_adjudication_review"]
        assert review == [
            {
                "claim": adjudication_claim,
                "child_number": 725,
                "status": "overridden",
                "override_reason": "The distinct report is unavailable; operator accepts this residual risk.",
            }
        ]
        assert terminal["result"]["parent_adjudication_review"] == review
    else:
        review = emitted[0]["parent_adjudication_review"]
        assert terminal["result"]["parent_adjudication_review"] == review
        assert review[0]["status"] == "corroborated"
        assert review[0]["fresh_eye_observer"]["disposition"] == "delegated"


REVIEW_MOD = runpy.run_path(
    str(ROOT / "skills/public/issue/scripts/issue_review_resolution.py")
)
CLOSE_FN_MOD = runpy.run_path(str(CLOSE_PATH))
_INPUT_MOD = runpy.run_path(
    str(ROOT / "skills/public/issue/scripts/issue_goal_run_input.py")
)
INPUT = SimpleNamespace(
    error=_INPUT_MOD["error"],
    positive=_INPUT_MOD["positive"],
    fields=_INPUT_MOD["fields"],
)

_OBLIGATION = "## Adjudications\n\n- first claim text\n"


def _review_kwargs(tmp_path: Path, *, records, claims=("first claim text",), evidence=None):
    obligation = tmp_path / "obligation.md"
    obligation.write_text(_OBLIGATION, encoding="utf-8")
    return {
        "repo_root": tmp_path,
        "value": {"repo": REPO, "parent_adjudications": records},
        "input_contract": INPUT,
        "parent_adjudication_claims": list(claims),
        "parent_obligation_path": obligation,
        "evidence": evidence if evidence is not None else [],
        "expected_children": [{"number": 725}],
    }


def _record(**overrides):
    base = {"claim": "first claim text", "child_number": 725}
    base.update(overrides)
    return base


def test_review_refuses_non_list_adjudications(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="must be a list"):
        REVIEW_MOD["validate_parent_adjudications"](**_review_kwargs(tmp_path, records="x"))


def test_review_refuses_records_absent_from_obligation(tmp_path: Path) -> None:
    kwargs = _review_kwargs(tmp_path, records=[_record()], claims=[])
    with pytest.raises(RuntimeError, match="absent from the parent obligation"):
        REVIEW_MOD["validate_parent_adjudications"](**kwargs)


def test_review_refuses_non_object_record(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="must be an object"):
        REVIEW_MOD["validate_parent_adjudications"](
            **_review_kwargs(tmp_path, records=["x"])
        )


def test_review_refuses_claim_mismatch(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="does not match obligation"):
        REVIEW_MOD["validate_parent_adjudications"](
            **_review_kwargs(tmp_path, records=[_record(claim="other claim")])
        )


def test_review_refuses_unexpected_child(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="is not an expected child"):
        REVIEW_MOD["validate_parent_adjudications"](
            **_review_kwargs(tmp_path, records=[_record(child_number=999)])
        )


def test_review_refuses_blank_override_reason(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="override_reason must be non-empty"):
        REVIEW_MOD["validate_parent_adjudications"](
            **_review_kwargs(tmp_path, records=[_record(override_reason="   ")])
        )


def test_review_needs_distinct_observer_roles(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="needs distinct observer and evidence roles"):
        REVIEW_MOD["validate_parent_adjudications"](
            **_review_kwargs(tmp_path, records=[_record()])
        )


def test_review_refuses_roles_not_bound_by_proof(tmp_path: Path) -> None:
    record = _record(observer_role="observer", independent_roles=["evidence"])
    with pytest.raises(RuntimeError, match="cites roles not bound"):
        REVIEW_MOD["validate_parent_adjudications"](
            **_review_kwargs(tmp_path, records=[record])
        )


def test_review_refuses_parent_summary_as_evidence(tmp_path: Path) -> None:
    other = tmp_path / "ev.md"
    other.write_text("independent\n", encoding="utf-8")
    record = _record(observer_role="observer", independent_roles=["evidence"])
    with pytest.raises(RuntimeError, match="cannot use the parent summary"):
        REVIEW_MOD["validate_parent_adjudications"](
            **_review_kwargs(
                tmp_path,
                records=[record],
                evidence=[
                    {"role": "observer", "path": str(tmp_path / "obligation.md")},
                    {"role": "evidence", "path": str(other)},
                ],
            )
        )


def test_review_requires_distinct_evidence_files(tmp_path: Path) -> None:
    shared = tmp_path / "shared.md"
    shared.write_text("report\n", encoding="utf-8")
    record = _record(observer_role="observer", independent_roles=["evidence"])
    with pytest.raises(RuntimeError, match="must be distinct files"):
        REVIEW_MOD["validate_parent_adjudications"](
            **_review_kwargs(
                tmp_path,
                records=[record],
                evidence=[
                    {"role": "observer", "path": str(shared)},
                    {"role": "evidence", "path": str(shared)},
                ],
            )
        )


def test_review_refuses_unreadable_observer_report(tmp_path: Path) -> None:
    other = tmp_path / "ev.md"
    other.write_text("independent\n", encoding="utf-8")
    record = _record(observer_role="observer", independent_roles=["evidence"])
    with pytest.raises(RuntimeError, match="observer report is unreadable"):
        REVIEW_MOD["validate_parent_adjudications"](
            **_review_kwargs(
                tmp_path,
                records=[record],
                evidence=[
                    {"role": "observer", "path": str(tmp_path / "missing.md")},
                    {"role": "evidence", "path": str(other)},
                ],
            )
        )


def test_review_refuses_report_without_verdict(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    report.write_text("first claim text\nnames ev.md here\n", encoding="utf-8")
    other = tmp_path / "ev.md"
    other.write_text("independent\n", encoding="utf-8")
    record = _record(observer_role="observer", independent_roles=["evidence"])
    with pytest.raises(RuntimeError, match="does not support the claim"):
        REVIEW_MOD["validate_parent_adjudications"](
            **_review_kwargs(
                tmp_path,
                records=[record],
                evidence=[
                    {"role": "observer", "path": str(report)},
                    {"role": "evidence", "path": str(other)},
                ],
            )
        )


def _already_closed(review) -> dict:
    return {
        "already_closed": {
            "terminal_metadata": {
                "receipt": {"payload": {"result": {"parent_adjudication_review": review}}}
            }
        }
    }


def test_existing_close_rejects_unbound_review() -> None:
    with pytest.raises(RuntimeError, match="does not bind"):
        CLOSE_FN_MOD["existing_close_result"](_already_closed(["old"]), ["new"])


def test_existing_close_returns_bound_receipt() -> None:
    result = CLOSE_FN_MOD["existing_close_result"](_already_closed(["a"]), ["a"])

    assert result["parent_adjudication_review"] == ["a"]


def test_existing_close_rejects_unbound_recovery() -> None:
    prepared = {
        "recovery": True,
        "result": {"prior_terminal": {"payload": {"result": {"parent_adjudication_review": []}}}},
    }
    with pytest.raises(RuntimeError, match="does not bind"):
        CLOSE_FN_MOD["existing_close_result"](prepared, ["x"])


def test_existing_close_binds_recovery_review() -> None:
    prepared = {
        "recovery": True,
        "result": {"prior_terminal": {"payload": {"result": {"parent_adjudication_review": ["a"]}}}},
    }

    assert CLOSE_FN_MOD["existing_close_result"](prepared, ["a"]) is None
    assert prepared["result"]["parent_adjudication_review"] == ["a"]


def _close_args(tmp_path: Path) -> SimpleNamespace:
    return SimpleNamespace(repo_root=tmp_path, repo=REPO, number=1)


def test_close_backend_refuses_provider_failure(tmp_path: Path) -> None:
    def boom(_root, **_kwargs):
        raise RuntimeError("nope")

    emitted: list = []
    result = CLOSE_FN_MOD["_resolve_close_backend"](_close_args(tmp_path), boom, emitted.append)

    assert result is None
    assert "provider-selection-invalid" in json.dumps(emitted[0])


def test_close_backend_refuses_invalid_adapter(tmp_path: Path) -> None:
    emitted: list = []
    result = CLOSE_FN_MOD["_resolve_close_backend"](
        _close_args(tmp_path), lambda _root, **_kwargs: {"adapter_ok": False}, emitted.append
    )

    assert result is None
    assert "adapter-invalid" in json.dumps(emitted[0])


def test_review_refuses_unverified_observer(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    report.write_text(
        "Second observer verdict: corroborated\nfirst claim text\nnames ev.md here\n",
        encoding="utf-8",
    )
    other = tmp_path / "ev.md"
    other.write_text("independent\n", encoding="utf-8")
    record = _record(observer_role="observer", independent_roles=["evidence"])
    kwargs = _review_kwargs(
        tmp_path,
        records=[record],
        evidence=[
            {"role": "observer", "path": str(report)},
            {"role": "evidence", "path": str(other)},
        ],
    )
    original = REVIEW_MOD["_FRESH_EYE"]
    REVIEW_MOD["_FRESH_EYE"] = SimpleNamespace(
        _observer_disposition=lambda * _args, **_kwargs: None
    )
    try:
        with pytest.raises(RuntimeError, match="has no verified distinct observer"):
            REVIEW_MOD["validate_parent_adjudications"](**kwargs)
    finally:
        REVIEW_MOD["_FRESH_EYE"] = original


def test_close_emits_refusal_on_unbound_existing_review(tmp_path: Path) -> None:
    prepared = _already_closed(["old"])
    proof = {"final_proof_index": {"adjudication_review": ["new"]}}
    # command_close resolves names in its own globals (the lane idiom), not the
    # runpy carrier dict.
    namespace = CLOSE_FN_MOD["command_close"].__globals__
    patched = ("_prepare_close", "_load_proof", "_resolve_close_backend")
    saved = {key: namespace[key] for key in patched}
    namespace["_prepare_close"] = lambda **_kwargs: prepared
    namespace["_load_proof"] = lambda _args, _emit: proof
    namespace["_resolve_close_backend"] = lambda _args, _rb, _emit: object()
    try:
        emitted: list = []
        args = SimpleNamespace(repo_root=tmp_path, repo=REPO, number=1)
        result = CLOSE_FN_MOD["command_close"](
            args, resolve_backend=None, emit=emitted.append
        )
    finally:
        namespace.update(saved)

    assert result == 2
    assert "close-refused" in json.dumps(emitted[0])
