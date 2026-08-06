from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable

import pytest

from scripts import publish_state_ledger as ledger

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_REL = "charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json"
GOAL_REL = "charness-artifacts/goals/2026-08-06-post-push-operational-proof-runtime-evidence.md"
HANDOFF_REL = "docs/handoff.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _replace_claim(path: Path, manifest_rel: str, manifest_sha: str, mutate: Callable[[dict[str, Any]], None] | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    match = ledger.CLAIM_RE.search(text)
    assert match is not None
    claim = json.loads(match.group(1))
    claim["manifest_path"] = manifest_rel
    claim["manifest_sha256"] = manifest_sha
    if mutate is not None:
        mutate(claim)
    rendered = json.dumps(claim, ensure_ascii=False, separators=(",", ":"))
    path.write_text(text[: match.start(1)] + rendered + text[match.end(1) :], encoding="utf-8")


@pytest.fixture
def fixture_root(tmp_path: Path):
    path = tmp_path / "repo"
    path.mkdir()
    (path / ".git").symlink_to(ROOT / ".git", target_is_directory=True)
    manifest = json.loads((ROOT / MANIFEST_REL).read_text(encoding="utf-8"))
    required = {MANIFEST_REL, GOAL_REL, HANDOFF_REL, manifest["goal_path"]}
    critique = manifest["critique"]
    required.update(critique[key] for key in ("artifact_path", "packet_path"))
    required.update(root["owner"].split("#", 1)[0] for root in manifest["reader_roots"])
    for relative in required:
        destination = path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)
    yield path


def _write_fixture(
    fixture_root: Path,
    *,
    manifest_mutate: Callable[[dict[str, Any]], None] | None = None,
    goal_mutate: Callable[[dict[str, Any]], None] | None = None,
    handoff_mutate: Callable[[dict[str, Any]], None] | None = None,
    ledger_mutate: Callable[[dict[str, Any]], None] | None = None,
) -> Path:
    manifest = json.loads((ROOT / MANIFEST_REL).read_text(encoding="utf-8"))
    if manifest_mutate is not None:
        manifest_mutate(manifest)
    manifest_path = fixture_root / "fixture-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_rel = manifest_path.relative_to(fixture_root).as_posix()
    manifest_sha = _sha256(manifest_path)

    sources: dict[str, tuple[str, Callable[[dict[str, Any]], None] | None]] = {
        "goal": (GOAL_REL, goal_mutate),
        "handoff": (HANDOFF_REL, handoff_mutate),
    }
    source_entries: dict[str, dict[str, str]] = {}
    for owner, (source_rel, mutate) in sources.items():
        source_path = fixture_root / f"{owner}.md"
        shutil.copy2(ROOT / source_rel, source_path)
        _replace_claim(source_path, manifest_rel, manifest_sha, mutate)
        source_text = source_path.read_text(encoding="utf-8")
        source_match = ledger.CLAIM_RE.search(source_text)
        assert source_match is not None
        source_claim = json.loads(source_match.group(1))
        source_entries[owner] = {
            "path": source_path.relative_to(fixture_root).as_posix(),
            "block_id": ledger.CLAIM_ID,
            "sha256": ledger.canonical_claim_sha256(source_claim),
        }

    payload: dict[str, Any] = {
        "kind": ledger.LEDGER_KIND,
        "schema_version": 1,
        "manifest": {"path": manifest_rel, "sha256": manifest_sha},
        "sources": source_entries,
    }
    if ledger_mutate is not None:
        ledger_mutate(payload)
    ledger_path = fixture_root / "ledger.json"
    ledger_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ledger_path


def test_valid_ledger_reconciles_captured_snapshot() -> None:
    result = ledger.reconcile(ROOT)
    assert result["status"] == "reconciled"
    assert result["verdict"] == "reconciled_captured_snapshot"
    assert result["published_sha"] == "e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5"
    assert result["captured_open_issue_count"] == 0


def test_human_and_json_cli_modes_share_verdict() -> None:
    human = subprocess.run(
        ["python3", "scripts/publish_state_ledger.py", "--repo-root", "."],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    machine = subprocess.run(
        ["python3", "scripts/publish_state_ledger.py", "--repo-root", ".", "--json"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    payload = json.loads(machine.stdout)
    assert human.returncode == machine.returncode == 0
    assert payload["status"] == "reconciled"
    assert payload["verdict"] in human.stdout
    assert payload["published_sha"] in human.stdout


def test_human_and_json_cli_modes_share_refusal(fixture_root: Path) -> None:
    path = _write_fixture(fixture_root, goal_mutate=lambda claim: claim.update(pending_publish=True))
    human = subprocess.run(
        ["python3", "scripts/publish_state_ledger.py", "--repo-root", str(fixture_root), "--ledger", str(path)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    machine = subprocess.run(
        ["python3", "scripts/publish_state_ledger.py", "--repo-root", str(fixture_root), "--ledger", str(path), "--json"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    payload = json.loads(machine.stdout)
    assert human.returncode == machine.returncode == 1
    assert payload["status"] == "refused"
    assert payload["code"] == "source_claim_pending"
    assert payload["field"] == "sources.goal.claim.pending_publish"
    assert payload["code"] in human.stdout
    assert f"field={payload['field']}" in human.stdout


def test_invalid_ledger_shape_refuses(fixture_root: Path) -> None:
    path = _write_fixture(fixture_root, ledger_mutate=lambda value: value.update(extra=True))
    with pytest.raises(ledger.LedgerError) as caught:
        ledger.reconcile(fixture_root, path)
    assert caught.value.code == "invalid_ledger"
    assert caught.value.field == "ledger"


def test_external_ledger_path_refuses() -> None:
    with pytest.raises(ledger.LedgerError) as caught:
        ledger.reconcile(ROOT, Path("/tmp/publish-state-ledger.json"))
    assert caught.value.code == "invalid_ledger"
    assert caught.value.field == "ledger"


def test_missing_manifest_refuses(fixture_root: Path) -> None:
    path = _write_fixture(fixture_root, ledger_mutate=lambda value: value["manifest"].update(path="missing.json"))
    with pytest.raises(ledger.LedgerError) as caught:
        ledger.reconcile(fixture_root, path)
    assert caught.value.code == "manifest_missing"
    assert caught.value.field == "manifest.path"


def test_invalid_manifest_refuses(fixture_root: Path) -> None:
    path = _write_fixture(fixture_root, manifest_mutate=lambda value: value.update(kind="wrong"))
    with pytest.raises(ledger.LedgerError) as caught:
        ledger.reconcile(fixture_root, path)
    assert caught.value.code == "manifest_invalid"
    assert caught.value.field == "manifest"


def test_unreadable_manifest_refuses(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = _write_fixture(fixture_root)
    manifest_path = fixture_root / "fixture-manifest.json"
    original_sha256 = ledger._sha256

    def fail_manifest(candidate: Path) -> str:
        if candidate == manifest_path:
            raise OSError("permission denied")
        return original_sha256(candidate)

    monkeypatch.setattr(ledger, "_sha256", fail_manifest)
    with pytest.raises(ledger.LedgerError) as caught:
        ledger.reconcile(fixture_root, path)
    assert caught.value.code == "manifest_missing"
    assert caught.value.field == "manifest.path"


@pytest.mark.parametrize(
    ("name", "kwargs", "code", "field"),
    [
        ("source-sha", {"goal_mutate": lambda claim: claim.update(published_sha="0" * 40)}, "source_claim_mismatch", "sources.goal.claim"),
        ("source-manifest-path", {"goal_mutate": lambda claim: claim.update(manifest_path="wrong.json")}, "source_claim_mismatch", "sources.goal.claim"),
        ("source-manifest-sha", {"goal_mutate": lambda claim: claim.update(manifest_sha256="0" * 64)}, "source_claim_mismatch", "sources.goal.claim"),
        ("pending", {"handoff_mutate": lambda claim: claim.update(pending_publish=True)}, "source_claim_pending", "sources.handoff.claim.pending_publish"),
        ("claim-state", {"goal_mutate": lambda claim: claim.update(claim_state="OPEN")}, "source_claim_state", "sources.goal.claim.claim_state"),
        ("ci-failure", {"manifest_mutate": lambda manifest: manifest["ci_readback"].update(conclusion="failure")}, "ci_not_success", "manifest.ci_readback"),
        ("ci-job", {"manifest_mutate": lambda manifest: manifest["ci_readback"]["jobs"][0].update(head_sha="0" * 40)}, "ci_job_mismatch", "manifest.ci_readback.jobs"),
        ("ci-incomplete", {"manifest_mutate": lambda manifest: manifest["ci_readback"]["jobs"][0].update(status="queued")}, "ci_job_mismatch", "manifest.ci_readback.jobs"),
        ("open-issue", {"manifest_mutate": lambda manifest: manifest["remote_readback"]["open_issues"].update(open_count=1)}, "issues_not_empty", "manifest.remote_readback.open_issues.open_count"),
    ],
)
def test_refusal_matrix_rejects_one_factor_drift(
    fixture_root: Path, name: str, kwargs: dict[str, Any], code: str, field: str,
) -> None:
    path = _write_fixture(fixture_root, **kwargs)
    with pytest.raises(ledger.LedgerError) as caught:
        ledger.reconcile(fixture_root, path)
    assert caught.value.code == code, name
    assert caught.value.field == field, name


@pytest.mark.parametrize(
    ("name", "mutate"),
    [
        ("extra-field", lambda claim: claim.update(extra=True)),
        ("missing-field", lambda claim: claim.pop("captured_at")),
        ("wrong-block", lambda claim: claim.update(block_id="wrong")),
    ],
)
def test_source_claim_shape_refuses(fixture_root: Path, name: str, mutate: Callable[[dict[str, Any]], None]) -> None:
    path = _write_fixture(fixture_root, goal_mutate=mutate)
    with pytest.raises(ledger.LedgerError) as caught:
        ledger.reconcile(fixture_root, path)
    assert caught.value.code == "source_claim_invalid", name
    assert caught.value.field == "sources.goal"


def test_manifest_digest_drift_refuses_before_readback(fixture_root: Path) -> None:
    path = _write_fixture(fixture_root, ledger_mutate=lambda value: value["manifest"].update(sha256="0" * 64))
    with pytest.raises(ledger.LedgerError) as caught:
        ledger.reconcile(fixture_root, path)
    assert caught.value.code == "manifest_digest_mismatch"
    assert caught.value.field == "manifest.sha256"


def test_source_digest_drift_refuses_before_claim_read(fixture_root: Path) -> None:
    path = _write_fixture(fixture_root, ledger_mutate=lambda value: value["sources"]["goal"].update(sha256="0" * 64))
    with pytest.raises(ledger.LedgerError) as caught:
        ledger.reconcile(fixture_root, path)
    assert caught.value.code == "source_claim_mismatch"
    assert caught.value.field == "sources.goal.claim"


def test_surrounding_source_prose_does_not_change_claim_binding(fixture_root: Path) -> None:
    path = _write_fixture(fixture_root)
    goal = fixture_root / "goal.md"
    goal.write_text(goal.read_text(encoding="utf-8") + "\nUnrelated continuation prose.\n", encoding="utf-8")
    result = ledger.reconcile(fixture_root, path)
    assert result["verdict"] == "reconciled_captured_snapshot"


def test_missing_source_marker_refuses(fixture_root: Path) -> None:
    def remove_marker(claim: dict[str, Any]) -> None:
        claim.clear()

    path = _write_fixture(fixture_root, goal_mutate=remove_marker)
    goal = fixture_root / "goal.md"
    text = goal.read_text(encoding="utf-8")
    goal.write_text(re.sub(re.escape(ledger.CLAIM_MARKER), "", text), encoding="utf-8")
    payload = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ledger.LedgerError) as caught:
        ledger.reconcile(fixture_root, path)
    assert caught.value.code == "source_claim_invalid"
    assert caught.value.field == "sources.goal"


def test_malformed_source_claim_refuses(fixture_root: Path) -> None:
    path = _write_fixture(fixture_root)
    goal = fixture_root / "goal.md"
    text = goal.read_text(encoding="utf-8")
    match = ledger.CLAIM_RE.search(text)
    assert match is not None
    goal.write_text(text[:match.start(1)] + "{not-json" + text[match.end(1):], encoding="utf-8")
    with pytest.raises(ledger.LedgerError) as caught:
        ledger.reconcile(fixture_root, path)
    assert caught.value.code == "source_claim_invalid"
    assert caught.value.field == "sources.goal"


def test_duplicate_source_marker_refuses(fixture_root: Path) -> None:
    path = _write_fixture(fixture_root)
    goal = fixture_root / "goal.md"
    text = goal.read_text(encoding="utf-8")
    match = ledger.CLAIM_RE.search(text)
    assert match is not None
    goal.write_text(text + text[match.start():match.end()] + "\n", encoding="utf-8")
    with pytest.raises(ledger.LedgerError) as caught:
        ledger.reconcile(fixture_root, path)
    assert caught.value.code == "source_claim_invalid"
    assert caught.value.field == "sources.goal"
