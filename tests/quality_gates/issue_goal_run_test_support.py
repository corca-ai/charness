from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = "corca-ai/charness"


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
                "draft_sha256": "a" * 64,
                "binding_sha256": "b" * 64,
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
        "draft_sha256": "a" * 64,
        "binding_sha256": "b" * 64,
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
