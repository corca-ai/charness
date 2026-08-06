#!/usr/bin/env python3
"""Reconcile one captured publish SHA without contacting external providers."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

from runtime_bootstrap import import_repo_module

_manifest = import_repo_module(__file__, "scripts.slice_manifest_lib")
ManifestError = _manifest.ManifestError
validate_manifest = _manifest.validate_manifest

LEDGER_PATH = Path("charness-artifacts/goals/2026-08-06-post-push-publish-state-ledger.json")
LEDGER_KIND = "charness.publish-state-ledger"
CLAIM_KIND = "charness.publish-state-claim"
CLAIM_ID = "post-push-operational-proof"
CLAIM_MARKER = f"<!-- charness-publish-state-claim:{CLAIM_ID} -->"
CLAIM_FIELDS = frozenset(
    {
        "kind", "schema_version", "block_id", "manifest_path", "manifest_sha256",
        "published_sha", "claim_state", "issue_scope", "pending_publish", "captured_at",
    }
)
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CLAIM_RE = re.compile(re.escape(CLAIM_MARKER) + r"\s*\n```json\s*\n(.*?)\n```", re.DOTALL)


class LedgerError(ValueError):
    """A stable, field-addressed reconciliation refusal."""

    def __init__(self, code: str, field: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.field = field

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "field": self.field, "message": str(self)}


def _fail(code: str, field: str, message: str) -> None:
    raise LedgerError(code, field, message)


def _read_json(path: Path, field: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        if field == "ledger":
            _fail("invalid_ledger", field, str(exc))
        if field == "manifest":
            _fail("manifest_missing", "manifest.path", str(exc))
        _fail("manifest_invalid", field, str(exc))
    if not isinstance(value, dict):
        _fail("invalid_ledger" if field == "ledger" else "manifest_invalid", field, "expected a JSON object")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_claim_sha256(claim: dict[str, Any]) -> str:
    payload = json.dumps(claim, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _repo_path(repo_root: Path, value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        _fail("invalid_ledger", field, "expected a repo-relative POSIX path")
    parsed = PurePosixPath(value)
    if parsed.is_absolute() or "." in parsed.parts or ".." in parsed.parts:
        _fail("invalid_ledger", field, "path must stay inside the repository")
    path = (repo_root / Path(*parsed.parts)).resolve()
    try:
        path.relative_to(repo_root.resolve())
    except ValueError:
        _fail("invalid_ledger", field, "path escapes the repository")
    if not path.is_file():
        if field == "manifest.path":
            _fail("manifest_missing", field, "file does not exist")
        source_field = field.removesuffix(".path") if field.startswith("sources.") else field
        _fail("source_claim_invalid", source_field, "file does not exist")
    return path


def _ledger_file(repo_root: Path, ledger_path: Path) -> Path:
    candidate = ledger_path if ledger_path.is_absolute() else repo_root / ledger_path
    try:
        candidate = candidate.resolve()
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        _fail("invalid_ledger", "ledger", "ledger must stay inside the repository")
    if not candidate.is_file():
        _fail("invalid_ledger", "ledger", "ledger file does not exist")
    return candidate


def _require_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("invalid_ledger", field, "expected an object")
    return value


def _require_sha(value: Any, field: str, expression: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or expression.fullmatch(value) is None:
        _fail("invalid_ledger", field, f"expected {label}")
    return value


def _validate_ledger_shape(repo_root: Path, ledger: dict[str, Any]) -> tuple[Path, dict[str, dict[str, Any]]]:
    if set(ledger) != {"kind", "schema_version", "manifest", "sources"}:
        _fail("invalid_ledger", "ledger", "unexpected or missing top-level fields")
    if ledger.get("kind") != LEDGER_KIND or ledger.get("schema_version") != 1:
        _fail("invalid_ledger", "ledger.kind/schema_version", "unsupported ledger kind or schema")
    manifest = _require_object(ledger.get("manifest"), "manifest")
    if set(manifest) != {"path", "sha256"}:
        _fail("invalid_ledger", "manifest", "manifest requires only path and sha256")
    manifest_path = _repo_path(repo_root, manifest.get("path"), "manifest.path")
    _require_sha(manifest.get("sha256"), "manifest.sha256", SHA256_RE, "64 lowercase hexadecimal characters")
    sources = _require_object(ledger.get("sources"), "sources")
    if set(sources) != {"goal", "handoff"}:
        _fail("invalid_ledger", "sources", "goal and handoff source locators are required")
    locators: dict[str, dict[str, Any]] = {}
    for owner in ("goal", "handoff"):
        locator = _require_object(sources.get(owner), f"sources.{owner}")
        if set(locator) != {"path", "block_id", "sha256"}:
            _fail("invalid_ledger", f"sources.{owner}", "source requires path, block_id, and sha256")
        if locator.get("block_id") != CLAIM_ID:
            _fail("invalid_ledger", f"sources.{owner}.block_id", f"expected `{CLAIM_ID}`")
        _repo_path(repo_root, locator.get("path"), f"sources.{owner}.path")
        _require_sha(locator.get("sha256"), f"sources.{owner}.sha256", SHA256_RE, "64 lowercase hexadecimal characters")
        locators[owner] = locator
    return manifest_path, locators


def _claim_error(owner: str, suffix: str, code: str, message: str) -> None:
    field = f"sources.{owner}.claim"
    if code == "source_claim_invalid":
        field = f"sources.{owner}"
    elif code in {"source_claim_pending", "source_claim_state"}:
        field += suffix
    _fail(code, field, message)


def _read_claim(repo_root: Path, owner: str, locator: dict[str, Any], manifest_path: Path, manifest_sha: str) -> dict[str, Any]:
    path = _repo_path(repo_root, locator["path"], f"sources.{owner}.path")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        _claim_error(owner, "", "source_claim_invalid", str(exc))
    if text.count(CLAIM_MARKER) != 1:
        _claim_error(owner, "", "source_claim_invalid", "expected exactly one publish-state marker")
    match = CLAIM_RE.search(text)
    if match is None:
        _claim_error(owner, "", "source_claim_invalid", "marker must be followed by one fenced JSON object")
    try:
        claim = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        _claim_error(owner, "", "source_claim_invalid", f"malformed claim JSON: {exc}")
    if not isinstance(claim, dict) or set(claim) != CLAIM_FIELDS:
        _claim_error(owner, "", "source_claim_invalid", "claim fields do not match the fixed schema")
    if claim.get("kind") != CLAIM_KIND or claim.get("schema_version") != 1 or claim.get("block_id") != CLAIM_ID:
        _claim_error(owner, ".block_id", "source_claim_invalid", "claim kind, schema, or block id is invalid")
    if canonical_claim_sha256(claim) != locator["sha256"]:
        _claim_error(owner, "", "source_claim_mismatch", "source claim digest differs from the ledger")
    if claim.get("manifest_path") != str(Path(manifest_path).relative_to(repo_root)):
        _claim_error(owner, ".manifest_path", "source_claim_mismatch", "claim manifest path differs from the ledger")
    if claim.get("manifest_sha256") != manifest_sha:
        _claim_error(owner, ".manifest_sha256", "source_claim_mismatch", "claim manifest digest differs from the ledger")
    if not isinstance(claim.get("published_sha"), str) or SHA_RE.fullmatch(claim["published_sha"]) is None:
        _claim_error(owner, ".published_sha", "source_claim_mismatch", "claim requires a full lowercase published SHA")
    if claim.get("claim_state") != "reconciled_captured_snapshot":
        _claim_error(owner, ".claim_state", "source_claim_state", "claim is not reconciled to a captured snapshot")
    if claim.get("issue_scope") != "repository_open_issues_empty":
        _claim_error(owner, ".issue_scope", "source_claim_mismatch", "unsupported issue scope")
    if claim.get("pending_publish") is True:
        _claim_error(owner, ".pending_publish", "source_claim_pending", "publish is still pending")
    if claim.get("pending_publish") is not False or not isinstance(claim.get("captured_at"), str) or not claim["captured_at"]:
        _claim_error(owner, ".pending_publish/captured_at", "source_claim_invalid", "claim requires false pending_publish and captured_at")
    return claim


def reconcile(repo_root: Path, ledger_path: Path = LEDGER_PATH) -> dict[str, Any]:
    ledger_path = _ledger_file(repo_root, ledger_path)
    ledger = _read_json(ledger_path, "ledger")
    manifest_path, locators = _validate_ledger_shape(repo_root, ledger)
    manifest_sha = ledger["manifest"]["sha256"]
    try:
        actual_manifest_sha = _sha256(manifest_path)
    except OSError as exc:
        _fail("manifest_missing", "manifest.path", str(exc))
    if actual_manifest_sha != manifest_sha:
        _fail("manifest_digest_mismatch", "manifest.sha256", "manifest content differs from the ledger")
    try:
        manifest_result = validate_manifest(repo_root, manifest_path)
    except ManifestError as exc:
        if exc.code in {"unsuccessful_ci_readback", "uncaptured_evidence"} and "ci_readback" in exc.path:
            _fail("ci_not_success", "manifest.ci_readback", str(exc))
        if exc.code in {"incomplete_ci_readback", "identity_mismatch"} and "ci_readback.jobs" in exc.path:
            _fail("ci_job_mismatch", "manifest.ci_readback.jobs", str(exc))
        _fail("manifest_invalid", "manifest", str(exc))
    claims = {owner: _read_claim(repo_root, owner, locator, manifest_path, manifest_sha) for owner, locator in locators.items()}
    target_sha = manifest_result["target_sha"]
    for owner, claim in claims.items():
        if claim["published_sha"] != target_sha:
            _claim_error(owner, ".published_sha", "source_claim_mismatch", "claim SHA differs from manifest target")
    raw_manifest = _read_json(manifest_path, "manifest")
    open_count = raw_manifest["remote_readback"]["open_issues"]["open_count"]
    if open_count != 0:
        _fail("issues_not_empty", "manifest.remote_readback.open_issues.open_count", f"captured open issue count is {open_count}")
    return {
        "status": "reconciled",
        "verdict": "reconciled_captured_snapshot",
        "published_sha": target_sha,
        "manifest_path": str(manifest_path.relative_to(repo_root)),
        "manifest_sha256": manifest_sha,
        "source_claims": {owner: {"path": locator["path"], "block_id": locator["block_id"]} for owner, locator in locators.items()},
        "captured_open_issue_count": open_count,
        "ci_run_id": manifest_result["ci_run_id"],
    }


def _render_human(result: dict[str, Any]) -> str:
    if result["status"] == "reconciled":
        return (
            f"RECONCILED verdict={result['verdict']} published_sha={result['published_sha']} "
            f"manifest={result['manifest_path']}"
        )
    return f"REFUSED {result['code']} field={result['field']}: {result['message']}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--ledger", type=Path, default=LEDGER_PATH)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = reconcile(args.repo_root.resolve(), args.ledger)
    except LedgerError as exc:
        result = {"status": "refused", **exc.as_dict()}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(_render_human(result))
    return 0 if result["status"] == "reconciled" else 1


if __name__ == "__main__":
    raise SystemExit(main())
