from __future__ import annotations

import importlib.util
import json
import re
import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

CRITIQUE_ARTIFACT_PREFIX = "charness-artifacts/critique/"
SEMVER_PIN_RE = re.compile(
    r"(?<![\w.])v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?![\w]|\.\d)"
)


def _load_adapter_preflight_helper() -> Any:
    helper_path = Path(__file__).resolve().with_name("publish_release_adapter_preflight.py")
    spec = importlib.util.spec_from_file_location("publish_release_adapter_preflight", helper_path)
    if spec is None or spec.loader is None:
        raise ImportError("publish_release_adapter_preflight.py not found")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_adapter_preflight = _load_adapter_preflight_helper()


def _version_pins(text: str) -> list[str]:
    pins: list[str] = []
    seen: set[str] = set()
    for match in SEMVER_PIN_RE.finditer(text):
        major = int(match.group("major"))
        minor = int(match.group("minor"))
        patch = int(match.group("patch"))
        if 1900 <= major <= 2199 and 1 <= minor <= 12 and 1 <= patch <= 31:
            continue
        version = f"{major}.{minor}.{patch}"
        if version not in seen:
            seen.add(version)
            pins.append(version)
    return pins


def _load_shared_closeout_helper() -> Any:
    bootstrap = next(
        (
            ancestor / "skill_runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "skill_runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:  # pragma: no cover - defensive broken-install layout
        raise ImportError("skill_runtime_bootstrap.py not found")
    runtime = SimpleNamespace(**runpy.run_path(str(bootstrap)))
    return runtime.load_repo_module_from_skill_script(
        __file__,
        "scripts.check_prescribed_skill_executed_lib",
    )


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
    """Return a blocker when adapter `update_instructions` carry release-pinned
    narrative instead of an evergreen refresh path.

    The adapter-focused preflight only triggers when the adapter FILE changed in the
    release delta, so a release that should repair `update_instructions` but does not
    touch the file is never flagged. This check is unconditional. It uses plain
    a release-version pin detector that ignores common dotted dates while still
    catching older non-previous release notes left in the adapter field.
    """
    if isinstance(update_instructions, (list, tuple)):
        text = "\n".join(str(item) for item in update_instructions)
    else:
        text = str(update_instructions or "")
    pins = _version_pins(text)
    if not pins:
        return None
    pins_text = ", ".join(f"`{pin}`" for pin in pins)
    return (
        "release adapter update_instructions contain version-pinned release narrative "
        f"({pins_text}); keep adapter update_instructions "
        "version-agnostic and put release-specific behavior, migration, and rollback notes "
        "in the release notes or release artifact"
    )


def build_update_instructions_prep_payload(
    *,
    package_id: str,
    current_version: str,
    target_version: str,
    previous_version: str | None,
    update_instructions: Any,
) -> dict[str, Any]:
    """Pre-publish affordance: surface evergreen `update_instructions` guidance
    BEFORE the release critique so the maintainer can refresh the adapter early and
    the staleness guard (`update_instructions_version_blocker`) does not HOLD the
    publish at the critique gate.

    Reports staleness as *data* and never raises — the whole point is to run before
    the clean-worktree / critique gate so the maintainer acts on it first. The
    suggested adapter text deliberately avoids the target version; per-release
    narrative belongs in release notes, not in the adapter contract.
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
    suggestion = [
        f"Run the repo-owned update command for {package_id} to install the latest published release.",
        "Read the release notes for release-specific behavior changes, migrations, or rollback notes.",
    ]
    return {
        "mode": "prep-update-instructions",
        "package_id": package_id,
        "current_version": current_version,
        "target_version": target_version,
        "previous_version": previous_version,
        "current_update_instructions": current_list,
        "update_instructions_stale": blocker is not None,
        "staleness_blocker": blocker,
        "suggested_update_instructions": suggestion,
        "stub_update_instructions_entry": suggestion[0],
        "next_step": (
            "Refresh the release adapter `update_instructions` to a version-agnostic "
            "operator refresh path, and put release-specific behavior, migration, or "
            "rollback notes in the release notes/artifact. Then run the release critique "
            "and publish; doing this now pre-empts the update_instructions HOLD at the "
            "critique gate."
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


def release_adapter_preflight_payload(
    repo_root: Path,
    *,
    release_content_paths: list[str],
    previous_version: str | None,
) -> dict[str, Any]:
    return _adapter_preflight.release_adapter_preflight_payload(
        repo_root,
        release_content_paths=release_content_paths,
        previous_version=previous_version,
    )


def run_release_adapter_preflight(
    repo_root: Path,
    payload: dict[str, Any],
    *,
    run_command: Callable,
) -> None:
    _adapter_preflight.run_release_adapter_preflight(
        repo_root,
        payload,
        run_command=run_command,
    )
