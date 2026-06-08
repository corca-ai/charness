from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, Callable

CRITIQUE_ARTIFACT_PREFIX = "charness-artifacts/critique/"
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


def _load_shared_closeout_helper() -> Any:
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "scripts" / "check_prescribed_skill_executed_lib.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(
                "check_prescribed_skill_executed_lib", candidate
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scripts/check_prescribed_skill_executed_lib.py not found")


def validate_critique_artifact_arg(
    repo_root: Path,
    artifact: str | None,
    *,
    run_command: Callable,
) -> str | None:
    if artifact is None:
        return None
    relpath = Path(artifact)
    if relpath.is_absolute() or any(part in ("", ".", "..") for part in relpath.parts):
        raise SystemExit("--critique-artifact must be a normalized repo-relative path")
    normalized = relpath.as_posix()
    if not normalized.startswith(CRITIQUE_ARTIFACT_PREFIX) or relpath.suffix != ".md":
        raise SystemExit("--critique-artifact must point at a critique markdown artifact")
    resolved = (repo_root / relpath).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise SystemExit("--critique-artifact must stay inside the repo root") from exc
    if not resolved.is_file():
        raise SystemExit(f"--critique-artifact does not exist: {normalized}")
    tracked = run_command(["git", "ls-files", "--error-unmatch", normalized], cwd=repo_root, check=False)
    if tracked.returncode != 0:
        raise SystemExit(f"--critique-artifact must be tracked before release: {normalized}")
    return normalized


def update_instructions_version_blocker(
    update_instructions: Any, *, target_version: str, previous_version: str | None
) -> str | None:
    """Return a blocker when adapter `update_instructions` still describe the
    previous release version but not the target — i.e. they went stale.

    The adapter-focused preflight only triggers when the adapter FILE changed in the
    release delta, so a release that should refresh `update_instructions` but does not
    touch the file is never flagged. This check is unconditional. It uses plain
    substring containment of the concrete previous/target version strings rather than
    a general semver scan, so it does not false-positive on dotted dates or
    version-agnostic prose, and `v`-prefixed forms (`v0.20.0`) match transparently.
    """
    if isinstance(update_instructions, (list, tuple)):
        text = "\n".join(str(item) for item in update_instructions)
    else:
        text = str(update_instructions or "")
    if not previous_version or previous_version == target_version:
        return None
    if target_version in text or previous_version not in text:
        return None
    return (
        f"release adapter update_instructions still describe the previous version `{previous_version}` "
        f"but not the target version `{target_version}`; refresh update_instructions before publishing so "
        "the generated release record does not ship stale operator steps"
    )


def build_update_instructions_prep_payload(
    *,
    package_id: str,
    current_version: str,
    target_version: str,
    previous_version: str | None,
    update_instructions: Any,
) -> dict[str, Any]:
    """Pre-publish affordance: surface a target-version `update_instructions` stub
    BEFORE the release critique so the maintainer can refresh the adapter early and
    the staleness guard (`update_instructions_version_blocker`) does not HOLD the
    publish at the critique gate.

    Reports staleness as *data* and never raises — the whole point is to run before
    the clean-worktree / critique gate so the maintainer acts on it first. The stub
    embeds the target version verbatim, so pasting it into the adapter is exactly
    what makes the staleness guard pass.
    """
    if isinstance(update_instructions, (list, tuple)):
        current_list = [str(item) for item in update_instructions]
    elif update_instructions:
        current_list = [str(update_instructions)]
    else:
        current_list = []
    blocker = update_instructions_version_blocker(
        update_instructions, target_version=target_version, previous_version=previous_version
    )
    stub = (
        f"After updating {package_id} to v{target_version}, "
        f"<describe the operator-facing refresh step for {target_version}>."
    )
    return {
        "mode": "prep-update-instructions",
        "package_id": package_id,
        "current_version": current_version,
        "target_version": target_version,
        "previous_version": previous_version,
        "current_update_instructions": current_list,
        "update_instructions_stale": blocker is not None,
        "staleness_blocker": blocker,
        "stub_update_instructions_entry": stub,
        "next_step": (
            "Refresh the release adapter `update_instructions` so they describe the "
            f"target version `{target_version}` (paste/fill the stub above), then run "
            "the release critique and publish. Doing this now pre-empts the "
            "update_instructions staleness HOLD at the critique gate."
        ),
    }


def enforce_release_critique_gate(
    repo_root: Path,
    *,
    critique_artifact: str | None,
    critique_blocked: str | None,
) -> dict[str, Any]:
    """Refuse the publish unless the standalone critique either ran (artifact
    exists) or was honestly skipped with a blocked host signal.

    Closes the release-closeout self-substitution gap. The release skill's prose already required a
    critique; this gate makes the requirement non-optional at the publish
    boundary. Returns the shared helper's report so callers can include it
    in their structured payload.
    """
    helper = _load_shared_closeout_helper()
    if critique_artifact and critique_blocked:
        raise SystemExit(
            "release publish gate: pass exactly one of "
            "`--critique-artifact <path>` or `--critique-blocked <host-signal>`"
        )
    if critique_artifact:
        result = helper.check(
            repo_root=repo_root,
            required=["standalone_critique"],
            evidence={"standalone_critique": critique_artifact},
            skips={},
            kind="release",
        )
    elif critique_blocked:
        signal = critique_blocked.strip()
        result = helper.check(
            repo_root=repo_root,
            required=["standalone_critique"],
            evidence={},
            skips={"standalone_critique": f"host-blocked-subagent: {signal}"},
            kind="release",
        )
    else:
        result = helper.check(
            repo_root=repo_root,
            required=["standalone_critique"],
            evidence={},
            skips={},
            kind="release",
        )
    if not result["ok"]:
        raise SystemExit(
            "release publish gate refused: standalone critique not satisfied\n"
            + json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        )
    return result


def safe_real_host_payload(repo_root: Path, repo_paths: list[str], *, build_payload: Callable) -> dict:
    try:
        payload = build_payload(repo_root, repo_paths)
    except Exception as exc:  # pragma: no cover - defensive fail-closed path
        raise SystemExit(
            "release real-host proof probe failed\n"
            f"{type(exc).__name__}: {exc}"
        ) from exc
    if payload.get("configuration_status") == "broken" or payload.get("error"):
        raise SystemExit(
            "release real-host proof probe failed\n"
            + json.dumps(payload, ensure_ascii=False, indent=2)
        )
    return payload


def _git_stdout(repo_root: Path, args: list[str]) -> tuple[int, str]:
    import subprocess

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
    import re

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
