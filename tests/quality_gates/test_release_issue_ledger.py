"""Focused refusal tests for the activation-time release issue ledger."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import yaml

from scripts import check_release_issue_ledger as gate


def _write(repo: Path, relative: str, content: str) -> str:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return relative


def _source(repo: Path, number: int = 1) -> str:
    payload = {
        "issue": {
            "number": number,
            "title": "Example issue",
            "state": "OPEN",
            "url": f"https://github.com/corca-ai/charness/issues/{number}",
            "updatedAt": "2026-08-20T00:00:00Z",
            "body": "## Body\n\nA claim.  \n",
            "comments": [
                {
                    "id": "comment-1",
                    "author": {"login": "reviewer"},
                    "createdAt": "2026-08-20T00:00:00Z",
                    "body": "## Comment\r\n\r\nA note.  \r\n",
                }
            ],
        }
    }
    return _write(repo, f"issues/reads/{number}.raw.yaml", yaml.safe_dump(payload, sort_keys=False))


def _hashes() -> tuple[str, str]:
    body = "## Body\n\nA claim.\n"
    comments = [{
        "id": "comment-1",
        "author": "reviewer",
        "created_at": "2026-08-20T00:00:00Z",
        "body": "## Comment\n\nA note.\n",
    }]
    canonical = json.dumps(comments, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode()).hexdigest(), hashlib.sha256(canonical.encode()).hexdigest()


def _payload(tmp_path: Path) -> dict:
    source = _source(tmp_path)
    evidence = _write(tmp_path, "issues/evidence.txt", "current reproducer\n")
    raw_content = "planner\n"
    raw = _write(tmp_path, "receipts/planner.raw.txt", raw_content)
    meta_content = "command: planner\nhead_sha: " + "a" * 40 + "\ncaptured_at: 2026-08-20T18:00:00+09:00\nexit_code: 0\n"
    meta = _write(tmp_path, "receipts/planner.meta.txt", meta_content)
    snapshot_content = '[{"number": 1, "title": "Example issue", "state": "OPEN", "url": "https://github.com/corca-ai/charness/issues/1", "updatedAt": "2026-08-20T00:00:00Z"}]\n'
    snapshot = _write(tmp_path, "issues/open.raw.json", snapshot_content)
    body_hash, comments_hash = _hashes()
    receipt = {
        "command": "planner",
        "raw_output_path": raw,
        "meta_path": meta,
        "head_sha": "a" * 40,
        "captured_at": "2026-08-20T18:00:00+09:00",
        "exit_code": 0,
        "raw_sha256": hashlib.sha256(raw_content.encode()).hexdigest(),
        "meta_sha256": hashlib.sha256(meta_content.encode()).hexdigest(),
    }
    return {
        "schema_version": gate.SCHEMA_VERSION,
        "repo": gate.REPOSITORY,
        "captured_at": "2026-08-20T18:00:00+09:00",
        "head_sha": "a" * 40,
        "issue_count": 1,
        "list_truncated": False,
        "activation_issue_snapshot": {
            "path": snapshot,
            "numbers": [1],
            "count": 1,
            "list_truncated": False,
            "raw_sha256": hashlib.sha256(snapshot_content.encode()).hexdigest(),
            "numbers_sha256": hashlib.sha256(b"[1]").hexdigest(),
        },
        "release_planner_receipt": copy.deepcopy(receipt),
        "quality_planner_receipt": copy.deepcopy(receipt),
        "issue_plan_receipt": copy.deepcopy(receipt),
        "post_lock_exceptions": [],
        "parent_only_paths": [".charness"],
        "freshness_note": "GitHub freshness is re-read before issue closeout and publication.",
        "issues": [{
            "number": 1,
            "url": "https://github.com/corca-ai/charness/issues/1",
            "title": "Example issue",
            "state": "open",
            "updated_at": "2026-08-20T00:00:00Z",
            "source_read_path": source,
            "body_sha256": body_hash,
            "comments_sha256": comments_hash,
            "premise": {
                "verdict": "current-reproducer",
                "exact_command": "python3 reproduce.py",
                "exit": 1,
                "evidence_path": evidence,
            },
            "classification": "qualified-repair",
            "locked_classification": "qualified-repair",
            "locked_head_sha": "a" * 40,
            "release_impact": "release-train-quality: release-path",
            "acceptance_owner": "owner",
            "acceptance_assertions": ["the supported path succeeds"],
            "lane_id": "lane-1",
            "allowed_paths": ["src/repair.py"],
            "dependencies": [],
            "proof_commands": ["python3 -m pytest tests/test_repair.py"],
            "release_content_evidence_path": evidence,
            "post_publication_closeout_path": None,
            "close_disposition": "leave-open",
            "amendments": [],
        }],
        "work_packages": [{
            "package_id": "p1",
            "issue_numbers": [1],
            "lane_id": "lane-1",
            "status": "admitted",
            "allowed_paths": ["src/repair.py"],
            "dependencies": [],
            "proof_commands": ["python3 -m pytest tests/test_repair.py"],
        }],
    }


def test_valid_ledger_binds_normalized_source_and_has_exact_once_coverage(tmp_path: Path) -> None:
    assert gate.validate_ledger(_payload(tmp_path), tmp_path) == []


def test_truncated_snapshot_is_refused(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    payload["list_truncated"] = True
    payload["activation_issue_snapshot"]["list_truncated"] = True
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("non-truncated" in error for error in errors)


def test_duplicate_or_missing_activation_issue_is_refused(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    payload["activation_issue_snapshot"]["numbers"] = [1, 2]
    payload["activation_issue_snapshot"]["count"] = 2
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("does not match raw snapshot order" in error for error in errors)


def test_unknown_classification_is_refused(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    payload["issues"][0]["classification"] = "maybe-fixed"
    assert any("invalid classification" in error for error in gate.validate_ledger(payload, tmp_path))


def test_qualified_repair_requires_acceptance_owner_assertions_proof_and_path_budget(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    issue = payload["issues"][0]
    issue["acceptance_owner"] = ""
    issue["acceptance_assertions"] = []
    issue["proof_commands"] = []
    issue["allowed_paths"] = []
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("acceptance_owner" in error for error in errors)
    assert any("acceptance_assertions" in error for error in errors)
    assert any("proof_commands" in error for error in errors)
    assert any("allowed_paths" in error for error in errors)


def test_release_blocker_requires_release_impact(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    payload["issues"][0]["classification"] = "release-blocker"
    payload["issues"][0]["release_impact"] = ""
    assert any("meaningful release impact" in error for error in gate.validate_ledger(payload, tmp_path))


def test_amendment_history_must_be_a_contiguous_append_only_chain(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    evidence = payload["issues"][0]["premise"]["evidence_path"]
    payload["issues"][0]["amendments"] = [
        {
            "amendment_id": "a1",
            "recorded_at": "2026-08-20T18:01:00+09:00",
            "from_classification": "deferred",
            "to_classification": "already-satisfied",
            "reason": "wrong direction",
            "owner": "owner",
            "evidence_path": evidence,
        },
        {
            "amendment_id": "a2",
            "recorded_at": "2026-08-20T18:02:00+09:00",
            "from_classification": "deferred",
            "to_classification": "qualified-repair",
            "reason": "overwrites a1",
            "owner": "owner",
            "evidence_path": evidence,
        },
    ]
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("overwrites prior history" in error for error in errors)


def test_post_lock_exception_requires_a_reproduced_post_lock_blocker(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    source = _source(tmp_path, number=2)
    payload["post_lock_exceptions"] = [{
        "exception_id": "e1",
        "issue_number": 2,
        "issue_url": "https://github.com/corca-ai/charness/issues/2",
        "observed_at": "2026-08-20T18:01:00+09:00",
        "observed_head_sha": "b" * 40,
        "lock_head_sha": "a" * 40,
        "classification": "release-blocker",
        "release_impact": "release-blocker",
        "source_read_path": source,
        "premise": {
            "verdict": "current-reproducer",
            "exact_command": "python3 reproduce-post-lock.py",
            "exit": 0,
            "evidence_path": payload["issues"][0]["premise"]["evidence_path"],
        },
    }]
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("reproduced post-lock blocker required" in error for error in errors)


def test_freshness_note_is_not_a_prose_bypass(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    payload["freshness_note"] = "The snapshot is fresh."
    assert any("GitHub freshness is re-read" in error for error in gate.validate_ledger(payload, tmp_path))


def test_shared_or_parent_only_paths_are_refused(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    payload["work_packages"].append({
        "package_id": "p2",
        "issue_numbers": [1],
        "lane_id": "lane-2",
        "status": "admitted",
        "allowed_paths": ["src/repair.py", ".charness/state.json"],
        "dependencies": [],
        "proof_commands": [],
    })
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("overlaps p1:src/repair.py" in error for error in errors)
    assert any("parent-only path admitted" in error for error in errors)


def test_raw_snapshot_and_digest_are_bound_to_the_ledger(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    snapshot = tmp_path / payload["activation_issue_snapshot"]["path"]
    snapshot.write_text('[{"number": 2}]\n', encoding="utf-8")
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("raw_sha256" in error for error in errors)
    assert any("does not match raw snapshot order" in error for error in errors)


def test_issue_source_receipt_identity_is_bound_beyond_body_and_comments(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    source = _source(tmp_path, number=2)
    payload["issues"][0]["source_read_path"] = source
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("issues[0].number: does not match source read receipt" in error for error in errors)


def test_deferred_and_decision_rows_have_typed_reason_fields(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    issue = payload["issues"][0]
    issue["classification"] = "deferred"
    issue["locked_classification"] = "deferred"
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("defer_reason" in error for error in errors)
    issue["defer_reason"] = "missing-current-reproducer"
    issue["classification"] = "decision-required"
    issue["locked_classification"] = "decision-required"
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("decision_owner" in error for error in errors)
    assert any("decision_question" in error for error in errors)


def test_package_paths_must_be_authorized_by_the_referenced_issue_row(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    payload["work_packages"][0]["allowed_paths"] = ["src/unrelated.py"]
    assert any("outside every referenced issue budget" in error for error in gate.validate_ledger(payload, tmp_path))


def test_planner_receipt_bytes_and_metadata_are_bound(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    meta = tmp_path / payload["release_planner_receipt"]["meta_path"]
    meta.write_text(meta.read_text(encoding="utf-8") + "tampered: true\n", encoding="utf-8")
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("meta_sha256: does not match receipt file" in error for error in errors)


def test_admitted_rows_reject_placeholder_strings(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    issue = payload["issues"][0]
    issue["release_impact"] = "x"
    issue["acceptance_assertions"] = [""]
    issue["proof_commands"] = [""]
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("meaningful release impact" in error for error in errors)
    assert any("acceptance_assertions[0]" in error for error in errors)
    assert any("proof_commands[0]" in error for error in errors)


def test_amendment_timestamp_must_be_iso8601_and_after_lock(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    issue = payload["issues"][0]
    issue["classification"] = "already-satisfied"
    issue["amendments"] = [{
        "amendment_id": "a1",
        "recorded_at": "not-a-timestamp",
        "from_classification": "qualified-repair",
        "to_classification": "already-satisfied",
        "reason": "new evidence",
        "owner": "owner",
        "evidence_path": issue["premise"]["evidence_path"],
    }]
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("recorded_at: invalid ISO-8601 timestamp" in error for error in errors)


def test_parent_only_paths_and_boolean_issue_numbers_are_refused(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    payload["parent_only_paths"] = ["/"]
    payload["activation_issue_snapshot"]["numbers"] = [True]
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("parent_only_paths[0]" in error and "repo-relative" in error for error in errors)
    assert any("numbers: integer list required" in error for error in errors)


def test_post_lock_exception_identity_and_time_are_bound(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    source = _source(tmp_path, number=2)
    payload["post_lock_exceptions"] = [{
        "exception_id": "e1",
        "issue_number": 2,
        "issue_url": "not-a-github-url",
        "observed_at": "yesterday",
        "observed_head_sha": "b" * 40,
        "lock_head_sha": "a" * 40,
        "classification": "release-blocker",
        "release_impact": "release-blocker: new issue",
        "source_read_path": source,
        "premise": {
            "verdict": "post-lock-release-blocker-reproduced",
            "exact_command": "python3 reproduce-post-lock.py",
            "exit": 1,
            "evidence_path": payload["issues"][0]["premise"]["evidence_path"],
        },
    }]
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("observed_at: invalid ISO-8601 timestamp" in error for error in errors)
    assert any("issue_url: must match issue number" in error for error in errors)
