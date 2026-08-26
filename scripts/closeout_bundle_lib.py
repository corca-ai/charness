"""Execute the bounded local phases of a Charness closeout bundle."""

from __future__ import annotations

import json
import re
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml

from runtime_bootstrap import import_repo_module

_preflight = import_repo_module(__file__, "scripts.final_bundle_preflight_lib")
_identity = import_repo_module(__file__, "scripts.reviewed_input_identity")
_lineage = import_repo_module(__file__, "scripts.goal_lineage")

KIND = "charness.closeout-bundle"
SCHEMA_VERSION = 1
BUNDLE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{2,79}$")
_SHELL_TOKENS = frozenset({";", "&&", "||", "|", ">", ">>", "<", "<<", "&"})


class BundleError(ValueError):
    """Raised when a bundle command cannot safely continue."""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _command_argv(command: str, *, repo_root: Path) -> list[str]:
    try:
        argv = shlex.split(command, posix=True)
    except ValueError as exc:
        raise BundleError(f"planned command is not shell-quotable: {exc}") from exc
    if not argv or any(token in _SHELL_TOKENS for token in argv):
        raise BundleError("planned command contains shell syntax; execute it through its owning gate")
    if argv[0] in {"python", "python3", "bash", "sh"}:
        if len(argv) < 2 or argv[1] in {"-c", "-m", "-e"}:
            raise BundleError("planned command must name a repo-owned script directly after its executable")
        script = Path(argv[1])
    elif argv[0].startswith("./"):
        script = Path(argv[0][2:])
    else:
        raise BundleError(f"planned command executable is not an approved repo runner: {argv[0]}")
    for token in argv:
        if token.startswith("/"):
            raise BundleError(f"planned command contains an absolute path: {token}")
    if script.is_absolute() or ".." in script.parts:
        raise BundleError(f"planned command script is not a repo-owned file: {script}")
    repo_root_resolved = repo_root.resolve()
    script_path = repo_root / script
    try:
        resolved_script = script_path.resolve(strict=True)
    except OSError as exc:
        raise BundleError(f"planned command script is not a repo-owned file: {script}") from exc
    try:
        resolved_script.relative_to(repo_root_resolved)
    except ValueError as exc:
        raise BundleError(f"planned command script is not a repo-owned file: {script}") from exc
    if not resolved_script.is_file():
        raise BundleError(f"planned command script is not a repo-owned file: {script}")
    return argv


def _run_argv(
    repo_root: Path,
    argv: list[str],
    *,
    phase: str,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    result = runner(
        argv,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "phase": phase,
        "command": shlex.join(argv),
        "returncode": result.returncode,
        "status": "passed" if result.returncode == 0 else "failed",
        "stdout": result.stdout[-12000:],
        "stderr": result.stderr[-12000:],
    }


def _safe_changed_paths(paths: list[str]) -> list[str]:
    return sorted({path for path in paths if path and not path.startswith(".charness/")})


def _authoring_argv(repo_root: Path, paths: list[str]) -> list[list[str]]:
    markdown = [
        path
        for path in paths
        if path.endswith(".md")
        and not (path.startswith("charness-artifacts/") and path.endswith("-packet.md"))
        and (repo_root / path).is_file()
    ]
    commands: list[list[str]] = []
    for path in markdown:
        commands.append(
            [
                "python3",
                "scripts/check_doc_authoring_preflight.py",
                "--repo-root",
                ".",
                "--path",
                path,
            ]
        )
    artifact_paths = [path for path in paths if path.startswith("charness-artifacts/")]
    if artifact_paths:
        commands.append(
            [
                "python3",
                "scripts/check_artifact_surface_preflight.py",
                "--repo-root",
                ".",
                "--changed-artifacts",
                *artifact_paths,
            ]
        )
    return commands


def _packet_argv(bundle_id: str, paths: list[str]) -> list[str]:
    return [
        "python3",
        "skills/public/critique/scripts/prepare_packet.py",
        "--repo-root",
        ".",
        "--prepared-for",
        f"closeout bundle {bundle_id}",
        "--slug",
        bundle_id,
        *sum((["--reviewed-path", path] for path in paths), []),
    ]


def _packet_payload(repo_root: Path, result: dict[str, Any]) -> dict[str, Any]:
    if result["returncode"] != 0:
        raise BundleError(f"reviewer packet generation failed: {result['stderr'] or result['stdout']}")
    try:
        payload = yaml.safe_load(result["stdout"])
    except yaml.YAMLError as exc:
        raise BundleError("reviewer packet generator did not return JSON-compatible YAML") from exc
    if not isinstance(payload, dict):
        # `yaml.safe_load` returns a plain scalar for unparsed prose where
        # `json.loads` raised, so the mapping check is what keeps a non-payload
        # stdout a refusal instead of an AttributeError further down.
        raise BundleError("reviewer packet generator did not return JSON-compatible YAML")
    if not payload.get("ok"):
        raise BundleError("reviewer packet is not ready")
    binding = payload.get("reviewed_input_binding")
    if not isinstance(binding, dict):
        raise BundleError("reviewer packet omitted its input binding")
    if binding.get("usable") is False:
        raise BundleError("reviewer packet input binding is not usable")
    if not isinstance(binding.get("packet_path"), str):
        raise BundleError("reviewer packet did not return a durable packet path")
    packet_path = repo_root / binding["packet_path"]
    if not packet_path.is_file():
        raise BundleError(f"reviewer packet path is missing: {binding['packet_path']}")
    try:
        packet_json = json.loads(packet_path.read_text(encoding="utf-8"))
        packet_identity = packet_json["reviewed_input_identity"]["identity_sha256"]
    except (KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        raise BundleError("reviewer packet omitted its durable input identity") from exc
    if not isinstance(binding.get("identity_sha256"), str) or binding["identity_sha256"] != packet_identity:
        raise BundleError("reviewer packet identity binding does not match its durable packet")
    payload["packet_sha256"] = _identity.packet_file_sha256(packet_path)
    payload["durable_identity_sha256"] = packet_identity
    return payload


def _phase(name: str, status: str, **details: Any) -> dict[str, Any]:
    return {"name": name, "status": status, **details}


def _failed(payload: dict[str, Any], phases: list[dict[str, Any]], error: str, **details: Any) -> dict[str, Any]:
    payload["status"] = "failed"
    payload["phases"] = phases
    payload["error"] = error
    payload.update(details)
    return payload


def build_plan(
    repo_root: Path,
    *,
    manifest_path: Path,
    critique_paths: list[str],
    behavior_channels: list[str],
    bundle_id: str,
    goal_lineage_path: Path | None = None,
) -> dict[str, Any]:
    if not BUNDLE_ID_RE.fullmatch(bundle_id):
        raise BundleError("bundle-id must match [a-z0-9][a-z0-9._-]{2,79}")
    try:
        goal_lineage = (
            _lineage.load_goal_lineage_file(repo_root, goal_lineage_path, require_work_item=True)
            if goal_lineage_path is not None
            else _lineage.not_goal_bound_lineage("closeout bundle was planned without a Goal Run Work Item identity")
        )
    except _lineage.LineageError as exc:
        raise BundleError(str(exc)) from exc
    plan = _preflight.build_plan(
        repo_root,
        manifest_path=manifest_path,
        critique_paths=critique_paths,
        behavior_channels=behavior_channels,
        goal_lineage_path=goal_lineage_path,
    )
    paths = _safe_changed_paths(list(plan.get("changed_paths", [])))
    authoring = [shlex.join(argv) for argv in _authoring_argv(repo_root, paths)]
    packet = shlex.join(_packet_argv(bundle_id, paths))
    phases = [
        _phase("surface_inventory", "ready" if plan["status"] == "ready" else "blocked"),
        _phase("pointer_freshness", "planned", command="python3 scripts/validate_current_pointer_freshness.py --repo-root ."),
        _phase("authoring_preflight", "planned", commands=authoring),
        _phase("reviewer_packet", "planned", command=packet),
        _phase("evidence_identity", "planned", source="reviewed_input_identity in packet"),
        _phase("verification_lock", "planned", command=next(
            (item["command"] for item in plan["planned_commands"] if item["phase"] == "closeout"),
            None,
        )),
    ]
    return {
        "kind": KIND,
        "schema_version": SCHEMA_VERSION,
        "status": "ready" if plan["status"] == "ready" else "blocked",
        "mode": "dry-run",
        "bundle_id": bundle_id,
        "created_at": _now(),
        "preflight": plan,
        "changed_paths": paths,
        "phases": phases,
        "goal_lineage": goal_lineage,
        "non_claims": [
            "dry-run only; no pointer, packet, quality, or worktree state was written",
            "behavior commands, provider state, installed-consumer behavior, remote CI, and release state are not claimed",
        ],
    }


def execute(
    repo_root: Path,
    *,
    manifest_path: Path,
    critique_paths: list[str],
    behavior_channels: list[str],
    bundle_id: str,
    goal_lineage_path: Path | None = None,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    payload = build_plan(
        repo_root,
        manifest_path=manifest_path,
        critique_paths=critique_paths,
        behavior_channels=behavior_channels,
        bundle_id=bundle_id,
        goal_lineage_path=goal_lineage_path,
    )
    payload["mode"] = "execute"
    if payload["status"] != "ready":
        return payload
    phases: list[dict[str, Any]] = []
    preflight = payload["preflight"]
    sync_argvs: list[list[str]] = []
    for item in preflight["planned_commands"]:
        if item["phase"] == "sync":
            sync_argvs.append(_command_argv(item["command"], repo_root=repo_root))
        elif item["phase"] == "closeout":
            _command_argv(item["command"], repo_root=repo_root)
    for argv in sync_argvs:
        result = _run_argv(repo_root, argv, phase="surface_sync", runner=runner)
        phases.append(result)
        if result["returncode"] != 0:
            return _failed(payload, phases, "surface sync failed before authoring preflight")

    refreshed_plan = _preflight.build_plan(
        repo_root,
        manifest_path=manifest_path,
        critique_paths=critique_paths,
        behavior_channels=behavior_channels,
        goal_lineage_path=goal_lineage_path,
    )
    if refreshed_plan["status"] != "ready":
        return _failed(
            payload,
            phases,
            "post-sync final-bundle preflight refused before authoring preflight",
            preflight=refreshed_plan,
        )
    payload["preflight"] = refreshed_plan
    payload["changed_paths"] = _safe_changed_paths(list(refreshed_plan.get("changed_paths", [])))

    pointer_check = _run_argv(
        repo_root,
        ["python3", "scripts/validate_current_pointer_freshness.py", "--repo-root", "."],
        phase="pointer_freshness",
        runner=runner,
    )
    phases.append(pointer_check)
    if pointer_check["returncode"] != 0:
        return _failed(payload, phases, "current-pointer freshness failed before reviewer packet generation")

    for argv in _authoring_argv(repo_root, payload["changed_paths"]):
        result = _run_argv(repo_root, argv, phase="authoring_preflight", runner=runner)
        phases.append(result)
        if result["returncode"] != 0:
            return _failed(payload, phases, "authoring preflight failed before reviewer packet generation")

    packet_result = _run_argv(
        repo_root,
        _packet_argv(bundle_id, payload["changed_paths"]),
        phase="reviewer_packet",
        runner=runner,
    )
    phases.append(packet_result)
    try:
        packet = _packet_payload(repo_root, packet_result)
        identity = packet["durable_identity_sha256"]
        packet_path = packet["reviewed_input_binding"]["packet_path"]
        packet_json = json.loads((repo_root / packet_path).read_text(encoding="utf-8"))
        current, reason = _identity.verify_reviewed_input_identity(
            repo_root, packet_json["reviewed_input_identity"]
        )
        if not current:
            raise BundleError(f"reviewed input identity is stale before verification lock: {reason}")
        payload["packet"] = {
            "path": packet_path,
            "sha256": packet["packet_sha256"],
            "identity_sha256": identity,
            "reviewed_paths": packet["reviewed_input_binding"].get("reviewed_paths", []),
        }
    except (BundleError, KeyError, OSError, json.JSONDecodeError) as exc:
        payload["status"] = "failed"
        payload["phases"] = phases
        payload["error"] = str(exc)
        return payload

    latest_plan = _preflight.build_plan(
        repo_root,
        manifest_path=manifest_path,
        critique_paths=critique_paths,
        behavior_channels=behavior_channels,
        goal_lineage_path=goal_lineage_path,
    )
    closeout = next(
        (item["command"] for item in latest_plan["planned_commands"] if item["phase"] == "closeout"),
        None,
    )
    if latest_plan["status"] != "ready" or not closeout:
        return _failed(
            payload,
            phases,
            "post-packet final-bundle preflight did not produce a verification lock",
            post_packet_preflight=latest_plan,
        )
    lock_result = _run_argv(repo_root, _command_argv(closeout, repo_root=repo_root), phase="verification_lock", runner=runner)
    phases.append(lock_result)
    payload["status"] = "completed" if lock_result["returncode"] == 0 else "failed"
    payload["phases"] = phases
    payload["verification_lock"] = {"command": closeout, "returncode": lock_result["returncode"]}
    payload["non_claims"] = [
        "behavior commands were recorded but not executed by the bundle orchestrator",
        "local verification is not provider, installed-consumer, remote-CI, or release proof",
        "push, tag, release publication, and release readback remain separate final-boundary phases",
    ]
    return payload


def write_receipt(repo_root: Path, payload: dict[str, Any], *, output_path: Path) -> Path:
    if payload.get("status") != "completed":
        raise BundleError("only a completed bundle can write a terminal receipt")
    target = output_path if output_path.is_absolute() else repo_root / output_path
    target = target.resolve()
    try:
        _preflight._relative(repo_root, target)
    except ValueError as exc:
        raise BundleError(f"path is outside repository: {target}") from exc
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target
