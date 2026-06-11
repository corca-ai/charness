from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Callable

RELEASE_ADAPTER_CANDIDATES = (
    ".agents/release-adapter.yaml",
    ".codex/release-adapter.yaml",
    ".claude/release-adapter.yaml",
    "docs/release-adapter.yaml",
    "release-adapter.yaml",
)
REAL_HOST_FIELDS = {
    "real_host_required_surfaces",
    "real_host_required_path_globs",
    "real_host_checklist",
}
FRESH_CHECKOUT_FIELDS = {"fresh_checkout_probes"}
BACKEND_FIELDS = {"release_backend"}
UPDATE_TEXT_FIELDS = {"update_instructions"}


def _git_stdout(repo_root: Path, args: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout


def _tag_ref(repo_root: Path, previous_version: str | None) -> str | None:
    if not previous_version:
        return None
    ref = f"refs/tags/v{previous_version}"
    code, _stdout = _git_stdout(repo_root, ["rev-parse", "--verify", "--quiet", ref])
    return ref if code == 0 else None


def _changed_adapter_fields(repo_root: Path, previous_ref: str, adapter_path: str) -> set[str]:
    code, stdout = _git_stdout(
        repo_root,
        ["diff", "--unified=3", previous_ref, "--", adapter_path],
    )
    if code != 0:
        return set()
    fields: set[str] = set()
    current_field: str | None = None
    for raw in stdout.splitlines():
        if raw.startswith("@@"):
            header_match = re.search(r"@@\s+([A-Za-z_][A-Za-z0-9_]*):", raw)
            if header_match:
                current_field = header_match.group(1)
            continue
        if raw.startswith(("+++", "---", "diff ", "index ")) or not raw:
            continue
        marker = raw[0]
        if marker not in {"+", "-", " "}:
            continue
        match = re.match(r"^[ +\-]([A-Za-z_][A-Za-z0-9_]*):", raw)
        if match:
            current_field = match.group(1)
            if marker in {"+", "-"}:
                fields.add(current_field)
        elif marker in {"+", "-"} and current_field is not None:
            fields.add(current_field)
    return fields


def release_adapter_preflight_payload(
    repo_root: Path,
    *,
    release_content_paths: list[str],
    previous_version: str | None,
) -> dict[str, Any]:
    changed_adapter_paths = sorted(set(release_content_paths) & set(RELEASE_ADAPTER_CANDIDATES))
    if not changed_adapter_paths:
        return {
            "status": "not_required",
            "reason": "release adapter did not change in the release delta",
            "commands": [],
        }
    previous_ref = _tag_ref(repo_root, previous_version)
    if previous_ref is None:
        return {
            "status": "not_evaluable",
            "reason": "release adapter changed, but no previous release tag is available for field diff",
            "commands": [],
        }
    changed_fields: set[str] = set()
    for adapter_path in changed_adapter_paths:
        changed_fields.update(_changed_adapter_fields(repo_root, previous_ref, adapter_path))
    commands = []
    if (repo_root / "skills/public/release/scripts/resolve_adapter.py").is_file():
        commands.append(["python3", "skills/public/release/scripts/resolve_adapter.py", "--repo-root", "."])
    field_set = set(changed_fields)
    if field_set & REAL_HOST_FIELDS and (repo_root / "tests/quality_gates/test_release_real_host.py").is_file():
        commands.append(["pytest", "tests/quality_gates/test_release_real_host.py", "-q"])
    if field_set & FRESH_CHECKOUT_FIELDS and (repo_root / "tests/quality_gates/test_release_backend.py").is_file():
        commands.append(
            [
                "pytest",
                "tests/quality_gates/test_release_backend.py::test_release_adapter_preserves_fresh_checkout_probes",
                "tests/quality_gates/test_release_backend.py::test_release_adapter_rejects_invalid_fresh_checkout_probes",
                "-q",
            ]
        )
    if field_set & BACKEND_FIELDS and (repo_root / "tests/quality_gates/test_release_backend.py").is_file():
        commands.append(["pytest", "tests/quality_gates/test_release_backend.py", "-q"])
    if field_set & UPDATE_TEXT_FIELDS and (repo_root / "tests/quality_gates/test_release_narrative_audit.py").is_file():
        commands.append(["pytest", "tests/quality_gates/test_release_narrative_audit.py", "-q"])
    if not commands:
        return {
            "status": "not_configured",
            "reason": "release adapter changed, but this repo has no focused release adapter preflight commands",
            "previous_ref": previous_ref,
            "adapter_paths": changed_adapter_paths,
            "changed_fields": sorted(changed_fields),
            "commands": [],
        }
    if (
        len(commands) == 1
        and (repo_root / "tests/quality_gates/test_release_real_host.py").is_file()
        and (repo_root / "tests/quality_gates/test_release_backend.py").is_file()
    ):
        commands.append(
            [
                "pytest",
                "tests/quality_gates/test_release_real_host.py",
                "tests/quality_gates/test_release_backend.py",
                "-q",
            ]
        )
    return {
        "status": "required",
        "reason": "release adapter changed in the release delta; focused adapter preflight is required before release mutation",
        "previous_ref": previous_ref,
        "adapter_paths": changed_adapter_paths,
        "changed_fields": sorted(changed_fields),
        "commands": commands,
    }


def run_release_adapter_preflight(
    repo_root: Path,
    payload: dict[str, Any],
    *,
    run_command: Callable,
) -> None:
    if payload.get("status") != "required":
        return
    for command in payload.get("commands", []):
        result = run_command(command, cwd=repo_root, check=False)
        if result.returncode != 0:
            raise SystemExit(
                "release adapter focused preflight blocked publish before mutation\n"
                f"command: {' '.join(command)}\n"
                f"exit_code: {result.returncode}\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )
