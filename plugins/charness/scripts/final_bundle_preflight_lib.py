"""Build an offline, non-executing plan for a locked Charness closeout."""

from __future__ import annotations

import hashlib
import json
import shlex
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

from runtime_bootstrap import import_repo_module

_manifest = import_repo_module(__file__, "scripts.slice_manifest_lib")
_surfaces = import_repo_module(__file__, "scripts.surfaces_lib")
_selector = import_repo_module(__file__, "scripts.select_verifiers")
_evidence = import_repo_module(__file__, "scripts.final_bundle_preflight_evidence")
_packaging = import_repo_module(__file__, "scripts.packaging_lib")

KIND = "charness.final-bundle-preflight"
SCHEMA_VERSION = 1
class BundleError(ValueError):
    """Raised for a caller input that cannot produce a bundle plan."""


def _block(code: str, subject: str, message: str, remediation: str) -> dict[str, str]:
    return {
        "code": code,
        "subject": subject,
        "message": message,
        "remediation": remediation,
    }


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise BundleError(f"path is outside repository: {path}") from exc


def _git(repo_root: Path, *args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=repo_root, check=False, capture_output=True, text=text
    )


def _git_text(repo_root: Path, *args: str) -> str:
    result = _git(repo_root, *args)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "git command failed").strip()
        raise BundleError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def _git_bytes(repo_root: Path, *args: str) -> bytes:
    result = _git(repo_root, *args, text=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or b"git command failed").decode(
            "utf-8", errors="replace"
        ).strip()
        raise BundleError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def _safe_relative(value: str) -> str:
    if not value or "\\" in value:
        raise BundleError(f"unsafe repository-relative path: {value!r}")
    parsed = PurePosixPath(value)
    if parsed.is_absolute() or "." in parsed.parts or ".." in parsed.parts:
        raise BundleError(f"unsafe repository-relative path: {value!r}")
    return value


def _manifest_rel(repo_root: Path, manifest_path: Path) -> str:
    return _safe_relative(_relative(repo_root, manifest_path))


def _current_manifest_blockers(repo_root: Path, manifest_path: Path) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    rel = _manifest_rel(repo_root, manifest_path)
    tracked = _git(repo_root, "ls-files", "--error-unmatch", "--", rel)
    if tracked.returncode != 0:
        blockers.append(
            _block(
                "manifest_not_tracked",
                rel,
                "the baseline manifest is not a tracked file",
                "use the checked-in Slice 1 manifest, not a temporary replacement",
            )
        )
    if not manifest_path.is_file() or manifest_path.is_symlink():
        blockers.append(
            _block(
                "manifest_not_regular",
                rel,
                "the baseline manifest must be a regular file",
                "restore the checked-in manifest and rerun the preflight",
            )
        )
        return blockers
    for args, code in (
        (("diff", "--quiet", "HEAD", "--", rel), "manifest_worktree_drift"),
        (("diff", "--cached", "--quiet", "--", rel), "manifest_index_drift"),
    ):
        result = _git(repo_root, *args)
        if result.returncode != 0:
            blockers.append(
                _block(
                    code,
                    rel,
                    "the frozen baseline manifest differs from its checked-in HEAD/index content",
                    "restore the baseline manifest before planning a final bundle",
                )
            )
    return blockers


def _candidate_snapshot(repo_root: Path, base_sha: str, changed_paths: list[str]) -> dict[str, str]:
    status = _git_bytes(repo_root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    path_state = _sha256_bytes(status)
    head_sha = _git_text(repo_root, "rev-parse", "HEAD").strip()
    return {
        "base_sha": base_sha,
        "head_sha": head_sha,
        "path_state_sha256": path_state,
        "changed_paths_sha256": _sha256_bytes(
            json.dumps(sorted(set(changed_paths)), separators=(",", ":")).encode()
        ),
    }


def _surface_inventory(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for surface in payload.get("matched_surfaces", []):
        rows.append(
            {
                "surface_id": surface["surface_id"],
                "description": surface["description"],
                "matched_source_paths": list(surface.get("matched_source_paths", [])),
                "matched_derived_paths": list(surface.get("matched_derived_paths", [])),
                "sync_commands": list(surface.get("sync_commands", [])),
                "verify_commands": list(surface.get("verify_commands", [])),
            }
        )
    return rows


def _tree_files(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and not path.is_symlink()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
        and ".pytest_cache" not in path.parts
        and ".ruff_cache" not in path.parts
    }


def packaging_mirror_inventory(repo_root: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    try:
        packaging_manifest = _packaging.load_manifest(repo_root, "charness")
        checked_in = repo_root / _packaging.checked_in_plugin_root(packaging_manifest)
        with tempfile.TemporaryDirectory(prefix="charness-final-bundle-plugin-") as temp_root:
            expected = Path(temp_root) / "plugins" / "charness"
            _packaging.export_plugin_tree(repo_root, expected, packaging_manifest)
            expected_files = _tree_files(expected)
            checked_in_files = _tree_files(checked_in)
            differences: list[str] = []
            for relative in sorted(expected_files | checked_in_files):
                expected_path = expected / relative
                checked_path = checked_in / relative
                if not expected_path.is_file() or not checked_path.is_file():
                    differences.append(relative)
                    continue
                if expected_path.read_bytes() != checked_path.read_bytes():
                    differences.append(relative)
    except Exception as exc:
        return (
            {
                "owner": "scripts/packaging_lib.py#export_plugin_tree",
                "status": "unavailable",
                "reason": str(exc),
            },
            [
                _block(
                    "packaging_owner_unavailable",
                    "plugins/charness",
                    f"the canonical packaging renderer could not produce a comparison tree: {exc}",
                    "repair the packaging manifest or renderer before final-bundle proof",
                )
            ],
        )
    status = "matched" if not differences else "needs_sync"
    inventory = {
        "owner": "scripts/packaging_lib.py#export_plugin_tree",
        "status": status,
        "checked_in_root": _relative(repo_root, checked_in),
        "expected_file_count": len(expected_files),
        "checked_in_file_count": len(checked_in_files),
        "differences": differences,
    }
    blockers = []
    if differences:
        blockers.append(
            _block(
                "needs_sync",
                _relative(repo_root, checked_in),
                "checked-in plugin output differs from the canonical packaging render",
                "run `python3 scripts/sync_root_plugin_manifests.py --repo-root .`, then rerun this preflight",
            )
        )
    return inventory, blockers


def _plan_command(phase: str, command: str, reason_surface_ids: list[str] | None = None) -> dict[str, Any]:
    return {
        "phase": phase,
        "command": command,
        "reason_surface_ids": list(reason_surface_ids or []),
    }


def build_plan(
    repo_root: Path,
    *,
    manifest_path: Path,
    critique_paths: list[str],
    behavior_channels: list[str],
    explicit_paths: list[str] | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    manifest_path = manifest_path.resolve()
    blockers: list[dict[str, str]] = []
    manifest_result: dict[str, Any] = {}
    captured_identity: dict[str, Any] = {"status": "unavailable"}
    base_sha = ""
    try:
        blockers.extend(_current_manifest_blockers(repo_root, manifest_path))
        manifest_result = _manifest.validate_manifest(repo_root, manifest_path, verify_current=False)
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        base_sha = data["premise"]["local_head_sha"]
        ancestor = _git(repo_root, "merge-base", "--is-ancestor", base_sha, "HEAD")
        if ancestor.returncode != 0:
            blockers.append(_block("candidate_base_not_ancestor", base_sha, "manifest local capture head is not an ancestor of current HEAD", "rebind the candidate to a descendant worktree before final-bundle proof"))
        captured_identity = {
            "target_sha": manifest_result["target_sha"],
            "carrier_sha": manifest_result["carrier_sha"],
            "ci_run_id": manifest_result["ci_run_id"],
            "captured_open_issue_count": manifest_result["captured_open_issue_count"],
            "manifest": _manifest_rel(repo_root, manifest_path),
        }
    except (_manifest.ManifestError, OSError, KeyError, TypeError, json.JSONDecodeError, BundleError) as exc:
        if isinstance(exc, _manifest.ManifestError):
            blockers.append(_block("invalid_manifest", exc.path, str(exc), "repair or replace the captured Slice 1 manifest and rerun validation"))
        else:
            blockers.append(_block("invalid_manifest", manifest_path.as_posix(), str(exc), "repair the captured Slice 1 manifest and rerun validation"))

    try:
        changed_paths = (
            [_safe_relative(path) for path in explicit_paths]
            if explicit_paths is not None
            else _surfaces.collect_changed_paths_since_resolved_base(repo_root, base_sha)
        )
        changed_paths = sorted(set(changed_paths))
    except (BundleError, _surfaces.SurfaceError) as exc:
        changed_paths = []
        blockers.append(_block("changed_path_collection_failed", "changed_paths", str(exc), "restore a valid git base and rerun the preflight"))

    diagnostic = explicit_paths is not None
    if diagnostic:
        blockers.append(_block("diagnostic_scope", "--paths", "explicit paths are diagnostic-only and cannot certify the complete bundle", "omit --paths for the production final-bundle plan"))

    candidate = {}
    if base_sha:
        try:
            candidate = _candidate_snapshot(repo_root, base_sha, changed_paths)
        except BundleError as exc:
            blockers.append(_block("candidate_snapshot_failed", "candidate_snapshot", str(exc), "rerun from a valid git worktree"))

    surface_payload: dict[str, Any] = {"matched_surfaces": [], "unmatched_paths": [], "sync_commands": [], "verify_commands": []}
    try:
        surface_manifest = _surfaces.load_surfaces(repo_root, surfaces_path=_surfaces.SURFACES_PATH)
        surface_payload = _surfaces.match_surfaces(surface_manifest, changed_paths)
    except Exception as exc:
        blockers.append(_block("surface_inventory_failed", ".agents/surfaces.json", str(exc), "repair the surfaces manifest before final-bundle proof"))
    if surface_payload.get("unmatched_paths"):
        blockers.append(_block("unmatched_surface_path", ",".join(surface_payload["unmatched_paths"]), "one or more changed paths have no owning surface", "add surface coverage or stop the bundle before broad proof"))
    if not surface_payload.get("verify_commands"):
        blockers.append(_block("missing_verify_command", "surface_inventory", "the selected surface set has no verification command", "add or select the owning repo verifier before closeout"))

    mirror_inventory, mirror_blockers = packaging_mirror_inventory(repo_root)
    blockers.extend(mirror_blockers)
    critique_rows, critique_blockers = _evidence.critique_inventory(repo_root, critique_paths, _safe_relative)
    blockers.extend(critique_blockers)
    behavior_rows, behavior_blockers = _evidence.behavior_inventory(
        behavior_channels, list(surface_payload.get("verify_commands", []))
    )
    blockers.extend(behavior_blockers)

    planned: list[dict[str, Any]] = []
    if base_sha:
        planned.append(
            _plan_command(
                "preflight",
                shlex.join(
                    [
                        "python3",
                        "scripts/validate_slice_manifest.py",
                        "--repo-root",
                        ".",
                        "--manifest",
                        _manifest_rel(repo_root, manifest_path),
                    ]
                ),
            )
        )
    planned.extend(_selector.command_reasons(surface_payload, "sync"))
    if critique_paths:
        planned.append(
            _plan_command(
                "verify",
                shlex.join(
                    [
                        "python3",
                        "scripts/validate_critique_artifacts.py",
                        "--repo-root",
                        ".",
                        "--paths",
                        *sorted(critique_paths),
                        "--include-worktree",
                    ]
                ),
            )
        )
    planned.extend(_plan_command("behavior", row["command"]) for row in behavior_rows)
    planned.extend(_selector.command_reasons(surface_payload, "verify"))
    if not blockers and not diagnostic and base_sha:
        planned.append(_plan_command("closeout", f"python3 scripts/run_slice_closeout.py --repo-root . --base {base_sha} --verification-lock"))

    status = "diagnostic" if diagnostic else ("ready" if not blockers else "blocked")
    return {
        "kind": KIND,
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "captured_baseline_identity": captured_identity,
        "candidate_snapshot": candidate,
        "changed_paths": changed_paths,
        "artifact_inventory": _evidence.artifact_inventory(repo_root, changed_paths),
        "surface_inventory": _surface_inventory(surface_payload),
        "surface_unmatched_paths": list(surface_payload.get("unmatched_paths", [])),
        "mirror_inventory": mirror_inventory,
        "critique_inventory": critique_rows,
        "behavior_channels": behavior_rows,
        "planned_commands": planned,
        "blockers": sorted(blockers, key=lambda item: (item["code"], item["subject"])),
        "non_claims": [
            "dry-run only; planned commands were not executed",
            "behavior semantics, provider freshness, installed-consumer behavior, and remote state are not claimed",
        ],
    }


def render_text(payload: dict[str, Any]) -> str:
    lines = [f"Final-bundle preflight: {payload['status']}", f"Changed paths: {len(payload['changed_paths'])}"]
    lines.append("Surfaces: " + ", ".join(row["surface_id"] for row in payload["surface_inventory"]) if payload["surface_inventory"] else "Surfaces: none")
    lines.append("Artifacts: " + str(len(payload["artifact_inventory"])))
    lines.append("Critique inputs: " + str(len(payload["critique_inventory"])))
    lines.append("Behavior channels: " + str(len(payload["behavior_channels"])))
    lines.append("Planned commands:")
    for item in payload["planned_commands"]:
        reasons = ",".join(item["reason_surface_ids"]) or "declared"
        lines.append(f"- [{item['phase']}] {item['command']} ({reasons})")
    if payload["blockers"]:
        lines.append("Blockers:")
        for item in payload["blockers"]:
            lines.append(f"- {item['code']}: {item['subject']} — {item['message']} Remediation: {item['remediation']}")
    else:
        lines.append("Blockers: none")
    return "\n".join(lines) + "\n"
