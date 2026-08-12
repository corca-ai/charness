from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

MARKER = "charness-release-state:prepared-awaiting-claims-review"
SCHEMA_VERSION = "charness.release.claims-review.v1"
RELEASE_RECORD_PATH = "charness-artifacts/release/latest.md"


def blob_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def prepared_record(repo_root: Path, *, commit: str, run) -> dict[str, str] | None:
    result = run(["git", "show", f"{commit}:{RELEASE_RECORD_PATH}"], cwd=repo_root, check=False)
    if result.returncode != 0 or MARKER not in result.stdout:
        return None
    # The marker is intentionally inherited by descendants.  A prepared record
    # is the commit that *introduced* it, not any later commit that happens to
    # retain the same file; otherwise an unreviewed P -> X -> R sequence can
    # reclassify X as the prepared record and shift the review boundary.
    parent = run(["git", "show", f"{commit}^:{RELEASE_RECORD_PATH}"], cwd=repo_root, check=False)
    if parent.returncode == 0 and MARKER in parent.stdout:
        return None
    return {"commit": commit, "path": RELEASE_RECORD_PATH, "sha256": blob_sha256(result.stdout)}


def validate_claims_review(repo_root: Path, *, prepared: dict[str, str], evidence_commit: str,
                           artifact_path: str | None, target_version: str, tag_name: str, run) -> dict[str, Any]:
    if not artifact_path:
        raise SystemExit("--resume: prepared claims-review state requires --claims-review-artifact")
    path = Path(artifact_path)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise SystemExit("--claims-review-artifact must be a normalized repo-relative path")
    normalized = path.as_posix()
    if not normalized.startswith("charness-artifacts/release-review/") or not normalized.endswith(".json"):
        raise SystemExit("--claims-review-artifact must be a JSON record under charness-artifacts/release-review/")
    parents = run(["git", "show", "-s", "--format=%P", evidence_commit], cwd=repo_root, check=False)
    if parents.returncode != 0 or parents.stdout.split() != [prepared["commit"]]:
        raise SystemExit("--resume: claims-review evidence must be the direct child of the prepared release record")
    changed = [line for line in run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", prepared["commit"], evidence_commit], cwd=repo_root).stdout.splitlines() if line]
    if changed != [normalized]:
        raise SystemExit(f"--resume: claims-review evidence commit must change only the supplied artifact; observed {changed!r}")
    record = run(["git", "show", f"{evidence_commit}:{normalized}"], cwd=repo_root, check=False)
    if record.returncode != 0:
        raise SystemExit(f"--resume: claims-review artifact is not committed at HEAD: {normalized}")
    try:
        data = json.loads(record.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"--resume: claims-review artifact is not valid JSON: {normalized}") from exc
    expected = {"schema_version": SCHEMA_VERSION, "prepared_commit": prepared["commit"],
                "release_record_path": prepared["path"], "release_record_sha256": prepared["sha256"],
                "target_version": target_version, "tag_name": tag_name, "verdict": "pass"}
    if not isinstance(data, dict) or any(data.get(key) != value for key, value in expected.items()):
        raise SystemExit("--resume: claims-review artifact does not bind the exact prepared release record")
    preparer, reviewer = data.get("preparer_context"), data.get("reviewer_context")
    if not isinstance(preparer, str) or not preparer.strip() or not isinstance(reviewer, str) or not reviewer.strip() or preparer == reviewer:
        raise SystemExit("--resume: claims-review artifact requires distinct nonempty preparer_context and reviewer_context")
    return {"path": normalized, "sha256": blob_sha256(record.stdout), "prepared": prepared, "reviewer_context": reviewer}
