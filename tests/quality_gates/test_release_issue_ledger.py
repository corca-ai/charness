"""Focused refusal tests for the activation-time release issue ledger."""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path

import yaml

from scripts.gates import check_release_issue_ledger as gate
from scripts import release_issue_ledger_contract as contract
from scripts import release_issue_ledger_evidence as evidence


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


def test_post_lock_exception_carries_its_own_repair_contract(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    source = _source(tmp_path, number=2)
    evidence = payload["issues"][0]["premise"]["evidence_path"]
    row = {
        "exception_id": "e1",
        "issue_number": 2,
        "issue_url": "https://github.com/corca-ai/charness/issues/2",
        "observed_at": "2026-08-20T18:01:00+09:00",
        "observed_head_sha": "b" * 40,
        "lock_head_sha": "a" * 40,
        "classification": "release-blocker",
        "release_impact": "release-blocker: new issue",
        "acceptance_owner": "owner",
        "acceptance_assertions": ["assertion"],
        "allowed_paths": [source],
        "proof_commands": ["python3 prove.py"],
        "release_content_evidence_path": source,
        "source_read_path": source,
        "premise": {
            "verdict": "post-lock-release-blocker-reproduced",
            "exact_command": "python3 reproduce-post-lock.py",
            "exit": 1,
            "evidence_path": evidence,
        },
    }
    payload["post_lock_exceptions"] = [row]
    assert gate.validate_ledger(payload, tmp_path) == []
    row["release_content_evidence_path"] = "missing-release-evidence.txt"
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("release_content_evidence_path: file does not exist" in error for error in errors)
    row.pop("acceptance_owner")
    errors = gate.validate_ledger(payload, tmp_path)
    assert any("acceptance_owner" in error for error in errors)


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


def test_cli_success_and_read_failures_are_executable(tmp_path: Path, capsys) -> None:
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text(json.dumps(_payload(tmp_path)), encoding="utf-8")
    assert gate.main(["--repo-root", str(tmp_path), "--ledger", "ledger.json"]) == 0
    assert gate.main(["--repo-root", str(tmp_path), "--ledger", "missing.json"]) == 1
    (tmp_path / "invalid.json").write_text("{", encoding="utf-8")
    assert gate.main(["--repo-root", str(tmp_path), "--ledger", "invalid.json"]) == 1
    (tmp_path / "rejected.json").write_text("{}", encoding="utf-8")
    assert gate.main(["--repo-root", str(tmp_path), "--ledger", "rejected.json"]) == 1
    assert capsys.readouterr().out


def test_contract_edge_refusals_execute_each_append_only_floor(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    issue = copy.deepcopy(payload["issues"][0])
    errors: list[str] = []
    contract.require_string_list("not-a-list", "field", errors)
    contract.require_string_list([], "field", errors, nonempty=True)
    assert any("list required" in error for error in errors)
    assert any("non-empty list required" in error for error in errors)

    issue["amendments"] = "not-a-list"
    errors = []
    contract.validate_amendments(issue, "issue", tmp_path, "a" * 40, datetime.fromisoformat("2026-08-20T18:00:00+09:00"), errors)
    assert any("append-only list" in error for error in errors)

    issue["amendments"] = []
    issue["locked_classification"] = "not-a-class"
    issue["locked_head_sha"] = "b" * 40
    errors = []
    contract.validate_amendments(issue, "issue", tmp_path, "a" * 40, datetime.fromisoformat("2026-08-20T18:00:00+09:00"), errors)
    assert any("required locked enum" in error for error in errors)
    assert any("must equal ledger head_sha" in error for error in errors)

    amendment = {
        "amendment_id": "same",
        "recorded_at": "2026-08-20T18:00:00+09:00",
        "from_classification": "not-a-class",
        "to_classification": "already-satisfied",
        "reason": "edge coverage",
        "owner": "owner",
        "evidence_path": "missing-evidence.txt",
    }
    issue["locked_classification"] = "qualified-repair"
    issue["locked_head_sha"] = "a" * 40
    issue["amendments"] = [amendment, copy.deepcopy(amendment)]
    issue["classification"] = "qualified-repair"
    errors = []
    contract.validate_amendments(issue, "issue", tmp_path, "a" * 40, datetime.fromisoformat("2026-08-20T18:00:00+09:00"), errors)
    assert any("unique non-empty id" in error for error in errors)
    assert any("must be after ledger capture" in error for error in errors)
    assert any("timestamps must increase" in error for error in errors)
    assert any("invalid classification transition" in error for error in errors)
    assert any("evidence_path: file does not exist" in error for error in errors)
    assert any("final transition does not reach" in error for error in errors)


def test_contract_issue_and_ledger_edges_execute_each_structural_floor(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    base_issue = copy.deepcopy(payload["issues"][0])
    captured = datetime.fromisoformat("2026-08-20T18:00:00+09:00")

    def issue_errors(mutator) -> list[str]:
        issue = copy.deepcopy(base_issue)
        mutator(issue)
        errors: list[str] = []
        contract.validate_issue(tmp_path, issue, 0, "a" * 40, captured, errors)
        return errors

    assert any("positive integer" in error for error in issue_errors(lambda row: row.update(number=0)))
    assert any("lowercase SHA-256" in error for error in issue_errors(lambda row: row.update(body_sha256="bad")))
    assert any("invalid disposition" in error for error in issue_errors(lambda row: row.update(close_disposition="later")))
    assert any("premise.exit: required integer" in error for error in issue_errors(lambda row: row["premise"].update(exit=True)))
    assert any("premise.evidence_path: file does not exist" in error for error in issue_errors(lambda row: row["premise"].update(evidence_path="missing.txt")))
    assert any("admitted row requires current reproducer" in error for error in issue_errors(lambda row: row["premise"].update(verdict="not-current")))
    assert any("release_content_evidence_path: file does not exist" in error for error in issue_errors(lambda row: row.update(release_content_evidence_path="missing.txt")))
    assert any("post_publication_closeout_path: must be null" in error for error in issue_errors(lambda row: row.update(post_publication_closeout_path="closeout.txt")))

    def refuted(row: dict) -> None:
        row["classification"] = "premise-refuted"
        row.pop("refutation_scope", None)
        row["post_lock_exception"] = "embedded"

    refuted_errors = issue_errors(refuted)
    assert any("refutation_scope" in error for error in refuted_errors)
    assert any("exceptions must be top-level" in error for error in refuted_errors)
    assert any("body_sha256: does not match" in error for error in issue_errors(lambda row: row.update(body_sha256="0" * 64, comments_sha256="0" * 64)))
    assert any("comments_sha256: does not match" in error for error in issue_errors(lambda row: row.update(body_sha256="0" * 64, comments_sha256="0" * 64)))

    def ledger_errors(mutator) -> list[str]:
        candidate = copy.deepcopy(payload)
        mutator(candidate)
        return gate.validate_ledger(candidate, tmp_path)

    missing = ledger_errors(lambda row: row.pop("repo"))
    assert any("ledger.repo: required" in error for error in missing)
    assert any("ledger.schema_version" in error for error in ledger_errors(lambda row: row.update(schema_version="wrong")))
    assert any("ledger.repo: expected" in error for error in ledger_errors(lambda row: row.update(repo="wrong/repo")))
    assert any("commit SHA required" in error for error in ledger_errors(lambda row: row.update(head_sha="bad")))
    assert any("issue_count: integer required" in error for error in ledger_errors(lambda row: row.update(issue_count=True)))
    assert any("does not equal issues length" in error for error in ledger_errors(lambda row: row.update(issue_count=2)))

    def duplicate_snapshot(row: dict) -> None:
        raw = '[{"number": 1}, {"number": 1}]\n'
        snapshot = row["activation_issue_snapshot"]
        (tmp_path / snapshot["path"]).write_text(raw, encoding="utf-8")
        snapshot.update(numbers=[1, 1], count=2, raw_sha256=hashlib.sha256(raw.encode()).hexdigest(), numbers_sha256=hashlib.sha256(b"[1,1]").hexdigest())

    assert any("duplicate issue number" in error for error in ledger_errors(duplicate_snapshot))
    assert any("duplicate activation issue" in error for error in ledger_errors(lambda row: row.update(issues=[copy.deepcopy(row["issues"][0]), copy.deepcopy(row["issues"][0])], issue_count=2)))
    assert any("parent_only_paths: non-empty" in error for error in ledger_errors(lambda row: row.update(parent_only_paths="bad")))
    assert any("allowed_paths[0]: required repo-relative path" in error for error in ledger_errors(lambda row: row["issues"][0].update(allowed_paths=[123, "src/repair.py"])))
    assert any("parent-only path admitted" in error for error in ledger_errors(lambda row: row.update(parent_only_paths=["src"] , issues=[dict(row["issues"][0], allowed_paths=["src/repair.py"])])))
    assert any("overlaps issue" in error for error in ledger_errors(lambda row: row["issues"][0].update(allowed_paths=["src/repair.py", "src/repair.py"])))
    assert any("package_id: unique" in error for error in ledger_errors(lambda row: row["work_packages"].append(copy.deepcopy(row["work_packages"][0]))))
    assert any("non-boolean activation" in error for error in ledger_errors(lambda row: row["work_packages"][0].update(issue_numbers=[True])))
    assert any("qualified disposition has no work package" in error for error in ledger_errors(lambda row: row.update(work_packages=[])))
    result = contract.summary(payload)
    assert result["status"] == "pass"


def test_evidence_edge_refusals_execute_helper_and_receipt_floors(tmp_path: Path, monkeypatch) -> None:
    errors: list[str] = []
    assert evidence.repo_path(tmp_path, "", field="path", errors=errors) is None
    assert evidence.repo_path(tmp_path, "../escape", field="path", errors=errors) is None
    assert evidence.require_mapping("not-an-object", "object", errors) == {}
    assert evidence.parse_timestamp("", "time", errors) is None
    assert evidence.parse_timestamp("not-a-time", "time", errors) is None
    assert evidence.parse_timestamp("2026-08-20T18:00:00", "time", errors) is None
    assert any("required repo-relative path" in error for error in errors)
    assert any("path must stay repo-relative" in error for error in errors)
    assert any("expected object" in error for error in errors)
    assert any("ISO-8601 timestamp required" in error for error in errors)
    assert any("invalid ISO-8601 timestamp" in error for error in errors)
    assert any("timezone required" in error for error in errors)

    source_path = tmp_path / "issues" / "reads" / "missing.raw.yaml"
    source_errors: list[str] = []
    assert evidence.source_record(tmp_path, source_path, source_errors, "source") == (None, None, None)
    bad_source = tmp_path / "issues" / "reads" / "bad.raw.yaml"
    bad_source.parent.mkdir(parents=True, exist_ok=True)
    bad_source.write_text("not: [valid", encoding="utf-8")
    assert evidence.source_record(tmp_path, bad_source, source_errors, "source") == (None, None, None)
    monkeypatch.setattr(evidence, "yaml", None)
    assert evidence.source_record(tmp_path, bad_source, source_errors, "source") == (None, None, None)
    evidence._receipt_metadata(bad_source, {}, "receipt", source_errors)
    monkeypatch.setattr(evidence, "yaml", yaml)
    assert any("PyYAML is required" in error for error in source_errors)

    payload = _payload(tmp_path)
    receipt = copy.deepcopy(payload["release_planner_receipt"])
    receipt_errors: list[str] = []
    evidence.validate_receipt(tmp_path, receipt, "receipt", "b" * 40, receipt_errors)
    receipt["exit_code"] = "0"
    evidence.validate_receipt(tmp_path, receipt, "receipt", "a" * 40, receipt_errors)
    receipt["raw_output_path"] = "missing.raw"
    receipt["meta_path"] = "missing.meta"
    evidence.validate_receipt(tmp_path, receipt, "receipt", "a" * 40, receipt_errors)
    receipt = copy.deepcopy(payload["release_planner_receipt"])
    receipt["raw_sha256"] = "bad"
    evidence.validate_receipt(tmp_path, receipt, "receipt", "a" * 40, receipt_errors)
    assert any("head_sha: differs" in error for error in receipt_errors)
    assert any("exit_code: required integer" in error for error in receipt_errors)
    assert any("file does not exist" in error for error in receipt_errors)
    assert any("lowercase SHA-256 required" in error for error in receipt_errors)

    meta_path = tmp_path / payload["release_planner_receipt"]["meta_path"]
    meta_path.write_text("[", encoding="utf-8")
    evidence.validate_receipt(tmp_path, copy.deepcopy(payload["release_planner_receipt"]), "receipt", "a" * 40, receipt_errors)
    meta_path.write_text("- item\n", encoding="utf-8")
    evidence.validate_receipt(tmp_path, copy.deepcopy(payload["release_planner_receipt"]), "receipt", "a" * 40, receipt_errors)
    meta_path.write_text("command: other\nhead_sha: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\ncaptured_at: 2026-08-20T19:00:00+09:00\nexit_code: 0\n", encoding="utf-8")
    evidence.validate_receipt(tmp_path, copy.deepcopy(payload["release_planner_receipt"]), "receipt", "a" * 40, receipt_errors)
    assert any("cannot parse metadata receipt" in error for error in receipt_errors)
    assert any("metadata must be an object" in error for error in receipt_errors)
    assert any("does not match metadata receipt" in error for error in receipt_errors)


def test_evidence_snapshot_refusals_execute_raw_binding_floors(tmp_path: Path) -> None:
    snapshot_errors: list[str] = []
    missing_snapshot = {"path": "missing.json", "numbers": [1], "count": 1, "list_truncated": False}
    evidence.validate_snapshot(tmp_path, missing_snapshot, snapshot_errors)
    invalid_json = _write(tmp_path, "issues/invalid.json", "{")
    evidence.validate_snapshot(tmp_path, {"path": invalid_json, "numbers": [1], "count": 1, "list_truncated": False}, snapshot_errors)
    non_list = _write(tmp_path, "issues/object.json", "{}")
    evidence.validate_snapshot(tmp_path, {"path": non_list, "numbers": [1], "count": 1, "list_truncated": False}, snapshot_errors)
    duplicate = _write(tmp_path, "issues/duplicate.json", '[{"number": true}, {"number": 1}, {"number": 1}]')
    evidence.validate_snapshot(tmp_path, {"path": duplicate, "numbers": [1, 1], "count": 3, "list_truncated": False}, snapshot_errors)
    assert any("path: file does not exist" in error for error in snapshot_errors)
    assert any("cannot read raw snapshot" in error for error in snapshot_errors)
    assert any("raw snapshot must be an issue list" in error for error in snapshot_errors)
    assert any("every issue needs" in error for error in snapshot_errors)
    assert any("duplicate issue number" in error for error in snapshot_errors)


def test_evidence_exception_refusals_execute_post_lock_floors(tmp_path: Path) -> None:
    exception_errors: list[str] = []
    captured = datetime.fromisoformat("2026-08-20T18:00:00+09:00")
    evidence.validate_post_lock_exceptions(tmp_path, "bad", {1}, "a" * 40, captured, exception_errors)
    source = _source(tmp_path, number=2)
    exception = {
        "exception_id": "same",
        "issue_number": 1,
        "issue_url": "https://github.com/corca-ai/charness/issues/1",
        "observed_at": "2026-08-20T17:00:00+09:00",
        "observed_head_sha": "bad",
        "lock_head_sha": "b" * 40,
        "classification": "qualified-repair",
        "release_impact": "release-blocker: edge",
        "source_read_path": source,
        "premise": {"verdict": "post-lock-release-blocker-reproduced", "exact_command": "python reproduce.py", "exit": 1, "evidence_path": "missing.txt"},
    }
    evidence.validate_post_lock_exceptions(tmp_path, [exception, copy.deepcopy(exception)], {1}, "a" * 40, captured, exception_errors)
    typed_number = copy.deepcopy(exception)
    typed_number["issue_number"] = "1"
    evidence.validate_post_lock_exceptions(tmp_path, [typed_number], {1}, "a" * 40, captured, exception_errors)
    assert any("required list" in error for error in exception_errors)
    assert any("unique non-empty id" in error for error in exception_errors)
    assert any("issue_number: integer required" in error for error in exception_errors)
    assert any("outside activation snapshot" in error for error in exception_errors)
    assert any("must be after ledger capture" in error for error in exception_errors)
    assert any("lock_head_sha: must equal" in error for error in exception_errors)
    assert any("observed_head_sha: commit SHA required" in error for error in exception_errors)
    assert any("classification: must be release-blocker" in error for error in exception_errors)
    assert any("premise.evidence_path: file does not exist" in error for error in exception_errors)
    assert any("issue number does not match" in error for error in exception_errors)
