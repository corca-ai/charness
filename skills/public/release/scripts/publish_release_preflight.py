from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, Callable

CRITIQUE_ARTIFACT_PREFIX = "charness-artifacts/critique/"


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


def enforce_release_critique_gate(
    repo_root: Path,
    *,
    critique_artifact: str | None,
    critique_blocked: str | None,
) -> dict[str, Any]:
    """Refuse the publish unless the standalone critique either ran (artifact
    exists) or was honestly skipped with a blocked host signal.

    Closes #230 Waste 1c. The release skill's prose already required a
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
