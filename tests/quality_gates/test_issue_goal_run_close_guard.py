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


def test_goal_run_close_refuses_parent_adjudication_without_second_observer(
    tmp_path: Path,
) -> None:
    module = runpy.run_path(str(CLOSE_PATH))
    proof = _close_inputs(tmp_path, attempt_id="close-adjudication-missing")
    obligation = tmp_path / "parent-obligation.md"
    obligation.write_text(
        "Close only after the bound proof is green.\n\n"
        "## Adjudications\n\n"
        "- WI-10b non-authority clause: behaviorally present.\n",
        encoding="utf-8",
    )
    index_path = tmp_path / "final-proof-index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["parent_obligation"]["sha256"] = hashlib.sha256(
        obligation.read_bytes()
    ).hexdigest()
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
    assert "second-observer record" in emitted[0]["error"]
    assert not (tmp_path / "observations").exists()


@pytest.mark.parametrize("adjudication_mode", ["clean", "override", "corroborated"])
def test_goal_run_close_reuses_parent_read_for_carrier_preflight(
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
    review = emitted[0]["parent_adjudication_review"]
    terminal = json.loads(
        (tmp_path / emitted[0]["observation"]["terminal_path"]).read_text(encoding="utf-8")
    )
    assert terminal["result"]["parent_adjudication_review"] == review
    if adjudication_mode == "clean":
        assert review == []
    elif adjudication_mode == "override":
        assert review == [
            {
                "claim": adjudication_claim,
                "child_number": 725,
                "status": "overridden",
                "override_reason": "The distinct report is unavailable; operator accepts this residual risk.",
            }
        ]
    else:
        assert review[0]["status"] == "corroborated"
        assert review[0]["fresh_eye_observer"]["disposition"] == "delegated"
