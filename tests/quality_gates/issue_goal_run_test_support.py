from __future__ import annotations

import hashlib
import json
import runpy
from pathlib import Path

REPO = "corca-ai/charness"
ROOT = Path(__file__).resolve().parents[2]
_BINDING = runpy.run_path(str(ROOT / "skills/public/achieve/scripts/goal_binding.py"))


def close_inputs(
    tmp_path: Path,
    *,
    attempt_id: str = "close-1",
    children: list[int] | None = None,
    index_payload: dict[str, object] | None = None,
    proof_overrides: dict[str, object] | None = None,
) -> Path:
    children = children or [725]
    comment = tmp_path / "close.md"
    comment.write_text("Closes the Goal Run.\n", encoding="utf-8")
    expected_children = tmp_path / "expected-children.json"
    expected_children.write_text(
        json.dumps(
            {
                "kind": "charness.expected-sub-issue-set/v1",
                "repo": REPO,
                "parent_number": 724,
                "children": children,
                "source": "test",
            }
        ),
        encoding="utf-8",
    )
    _write_binding_fixture(tmp_path)
    parent_obligation = tmp_path / "parent-obligation.md"
    parent_obligation.write_text(
        "Close only after the bound proof is green.\n", encoding="utf-8"
    )
    whole_system = tmp_path / "whole-system.json"
    whole_system.write_text('{"status":"pass"}\n', encoding="utf-8")
    index = tmp_path / "final-proof-index.json"
    index.write_text(
        json.dumps(
            index_payload
            or {
                "kind": "charness.goal-run-final-proof-index/v1",
                "repo": REPO,
                "parent_number": 724,
                "draft_sha256": _fixture_metadata(tmp_path)["draft_sha256"],
                "binding_sha256": _fixture_metadata(tmp_path)["binding_sha256"],
                "expected_children": {
                    "path": "expected-children.json",
                    "sha256": hashlib.sha256(expected_children.read_bytes()).hexdigest(),
                },
                "parent_obligation": {
                    "path": "parent-obligation.md",
                    "sha256": hashlib.sha256(parent_obligation.read_bytes()).hexdigest(),
                },
                "evidence": [
                    {
                        "role": "whole-system",
                        "path": "whole-system.json",
                        "sha256": hashlib.sha256(whole_system.read_bytes()).hexdigest(),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    proof_payload: dict[str, object] = {
        "kind": "charness.goal-run-close-proof/v1",
        "repo": REPO,
        "parent_number": 724,
        "attempt_id": attempt_id,
        "draft_sha256": _fixture_metadata(tmp_path)["draft_sha256"],
        "binding_sha256": _fixture_metadata(tmp_path)["binding_sha256"],
        "observation_dir": "observations",
        "comment_file": "close.md",
        "comment_sha256": hashlib.sha256(comment.read_bytes()).hexdigest(),
        "final_proof_index_file": "final-proof-index.json",
        "final_proof_index_sha256": hashlib.sha256(index.read_bytes()).hexdigest(),
        "children": [
            {
                "repo": REPO,
                "number": number,
                "evidence": {"kind": "issue-owned-closeout/v1", "identity": "comment"},
            }
            for number in children
        ],
    }
    proof_payload.update(proof_overrides or {})
    proof = tmp_path / "proof.json"
    proof.write_text(json.dumps(proof_payload), encoding="utf-8")
    return proof


def _write_binding_fixture(tmp_path: Path) -> None:
    draft = tmp_path / "goal.md"
    draft.write_text("# Goal Run fixture\n", encoding="utf-8")
    item = {
        "key": "child-725",
        "intent": "reuse",
        "issue": {
            "repo": REPO,
            "number": 725,
            "url": f"https://github.com/{REPO}/issues/725",
        },
        "dependencies": [],
        "rank": 1,
        "body_policy": "managed-addendum",
        "body_sha256": hashlib.sha256(b"new child body\n").hexdigest(),
        "observed": {
            "state": "OPEN",
            "title_sha256": hashlib.sha256(b"Child 725").hexdigest(),
            "body_sha256": hashlib.sha256(b"old child body\n").hexdigest(),
        },
    }
    payload = _BINDING["build_binding"](
        draft_path="goal.md",
        draft_sha256=_BINDING["sha256_file"](draft),
        briefing_sha256=hashlib.sha256(b"briefing").hexdigest(),
        approval_response="approved",
        approval_session_id="fixture-session",
        approval_observed_at="2026-08-30T00:00:00+09:00",
        parent={
            "repo": REPO,
            "number": 724,
            "url": f"https://github.com/{REPO}/issues/724",
        },
        approved_work_items=[item],
    )
    binding_path = tmp_path / "goal.binding.json"
    binding_path.write_bytes(_BINDING["canonical_json_bytes"](payload))
    metadata = {
        "binding_schema": "charness.goal-binding/v1",
        "binding_path": "goal.binding.json",
        "binding_sha256": hashlib.sha256(binding_path.read_bytes()).hexdigest(),
        "draft_path": "goal.md",
        "draft_sha256": payload["draft"]["sha256"],
        "initial_graph_sha256": payload["approved_work_items_sha256"],
        "current_membership_sha256": hashlib.sha256(b"membership").hexdigest(),
        "bootstrap_verification": "verified-target-roundtrip",
        "parent_identity": {
            "repo": REPO,
            "number": 724,
            "url": f"https://github.com/{REPO}/issues/724",
        },
        "progress": {
            "schema": "charness.goal-progress/v1",
            "revision": 1,
            "total": 1,
            "completed": 1,
            "open": 0,
            "membership_sha256": hashlib.sha256(b"membership").hexdigest(),
            "next": None,
        },
    }
    (tmp_path / ".goal-run-fixture.json").write_text(json.dumps(metadata), encoding="utf-8")


def _fixture_metadata(tmp_path: Path) -> dict[str, object]:
    return json.loads((tmp_path / ".goal-run-fixture.json").read_text(encoding="utf-8"))


def parent_body(tmp_path: Path, **metadata_overrides: object) -> str:
    if not (tmp_path / ".goal-run-fixture.json").is_file():
        _write_binding_fixture(tmp_path)
    metadata = _fixture_metadata(tmp_path)
    metadata.update(metadata_overrides)
    return "<!-- charness-goal-run:v1\n" + json.dumps(metadata, sort_keys=True, separators=(",", ":")) + "\n-->\n"
