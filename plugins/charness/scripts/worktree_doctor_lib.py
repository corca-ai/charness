from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module

_adapter_lib_module = import_repo_module(__file__, "scripts.adapter_lib")
load_yaml_file = _adapter_lib_module.load_yaml_file

_state = import_repo_module(__file__, "scripts.worktree_doctor_state")
CANONICAL_CHECK_IDS = _state.CANONICAL_CHECK_IDS
CheckResult = _state.CheckResult
CommandResult = _state.CommandResult
DEFAULT_PREPARE_TIMEOUT_SECONDS = _state.DEFAULT_PREPARE_TIMEOUT_SECONDS
EXAMPLE_RELATIVE_PATH = _state.EXAMPLE_RELATIVE_PATH
FAIL = _state.FAIL
MANIFEST_RELATIVE_PATH = _state.MANIFEST_RELATIVE_PATH
ManifestState = _state.ManifestState
PASS = _state.PASS
SKIPPED = _state.SKIPPED
aggregate_status = _state.aggregate_status
now_iso = _state.now_iso
tail = _state.tail

_checks = import_repo_module(__file__, "scripts.worktree_doctor_checks")
run_canonical_checks = _checks.run_canonical_checks
run_manifest_doctor_checks = _checks.run_manifest_doctor_checks


def load_manifest(repo_root: Path) -> ManifestState:
    manifest_path = repo_root / MANIFEST_RELATIVE_PATH
    if not manifest_path.is_file():
        return ManifestState(found=False, path=None, valid=True, errors=[], data={})
    try:
        data = load_yaml_file(manifest_path)
    except Exception as exc:
        return ManifestState(
            found=True,
            path=str(MANIFEST_RELATIVE_PATH),
            valid=False,
            errors=[f"failed to parse manifest: {exc}"],
            data={},
        )
    errors = validate_manifest(data)
    return ManifestState(
        found=True,
        path=str(MANIFEST_RELATIVE_PATH),
        valid=not errors,
        errors=errors,
        data=data if not errors else {},
    )


def validate_manifest(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest root must be a mapping"]
    if data.get("version") != 1:
        errors.append("manifest.version must be 1")
    _validate_prepare_section(data.get("prepare"), errors)
    _validate_doctor_section(data.get("doctor"), errors)
    return errors


def _validate_prepare_section(prepare: Any, errors: list[str]) -> None:
    if not isinstance(prepare, dict):
        errors.append("manifest.prepare must be a mapping with `commands`")
        return
    commands = prepare.get("commands")
    if not isinstance(commands, list) or not commands:
        errors.append("manifest.prepare.commands must be a non-empty list")
    else:
        for index, entry in enumerate(commands):
            _validate_command_entry(entry, f"manifest.prepare.commands[{index}]", errors)
    skip = prepare.get("skip_if_doctor_passes", True)
    if not isinstance(skip, bool):
        errors.append("manifest.prepare.skip_if_doctor_passes must be a boolean")


def _validate_doctor_section(doctor: Any, errors: list[str]) -> None:
    if doctor is None:
        return
    if not isinstance(doctor, dict):
        errors.append("manifest.doctor must be a mapping")
        return
    checks = doctor.get("checks")
    if checks is not None:
        if not isinstance(checks, list):
            errors.append("manifest.doctor.checks must be a list")
        else:
            seen_ids: set[str] = set()
            for index, entry in enumerate(checks):
                _validate_doctor_check_entry(entry, f"manifest.doctor.checks[{index}]", errors, seen_ids)
    disabled = doctor.get("disable_canonical_checks")
    if disabled is not None:
        _validate_disabled_checks(disabled, errors)


def _validate_disabled_checks(disabled: Any, errors: list[str]) -> None:
    if not isinstance(disabled, list):
        errors.append("manifest.doctor.disable_canonical_checks must be a list")
        return
    for entry in disabled:
        if entry not in CANONICAL_CHECK_IDS:
            errors.append(
                f"manifest.doctor.disable_canonical_checks: unknown check id {entry!r}; allowed: {list(CANONICAL_CHECK_IDS)}"
            )


def _validate_command_entry(entry: Any, label: str, errors: list[str]) -> None:
    if not isinstance(entry, dict):
        errors.append(f"{label} must be a mapping")
        return
    _validate_argv(entry.get("argv"), f"{label}.argv", errors)
    timeout = entry.get("timeout_seconds")
    if timeout is not None and not (isinstance(timeout, int) and 1 <= timeout <= 1800):
        errors.append(f"{label}.timeout_seconds must be an integer between 1 and 1800")


def _validate_argv(argv: Any, label: str, errors: list[str]) -> None:
    if isinstance(argv, str) and argv.lstrip().startswith("["):
        errors.append(
            f"{label} appears to use inline YAML array syntax (`[a, b]`); "
            "the repo-local YAML loader does not parse inline arrays — use block style "
            "(`- a` on its own line) instead."
        )
        return
    if not isinstance(argv, list) or not argv:
        errors.append(f"{label} must be a non-empty list of strings")
        return
    for token in argv:
        if not isinstance(token, str):
            errors.append(f"{label} must contain only strings")
            return


def _validate_doctor_check_entry(entry: Any, label: str, errors: list[str], seen_ids: set[str]) -> None:
    if not isinstance(entry, dict):
        errors.append(f"{label} must be a mapping")
        return
    check_id = entry.get("id")
    if not isinstance(check_id, str) or not check_id:
        errors.append(f"{label}.id must be a non-empty string")
    elif check_id in seen_ids:
        errors.append(f"{label}.id {check_id!r} is duplicated within manifest.doctor.checks")
    else:
        seen_ids.add(check_id)
    _validate_argv(entry.get("argv"), f"{label}.argv", errors)
    expect = entry.get("expect_exit_code", 0)
    if not isinstance(expect, int):
        errors.append(f"{label}.expect_exit_code must be an integer")
    timeout = entry.get("timeout_seconds")
    if timeout is not None and not (isinstance(timeout, int) and 1 <= timeout <= 120):
        errors.append(f"{label}.timeout_seconds must be an integer between 1 and 120")


def run_doctor(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    manifest_state = load_manifest(repo_root)
    if manifest_state.found and not manifest_state.valid:
        return {
            "checked_at": now_iso(),
            "manifest": manifest_state.to_dict(),
            "checks": [],
            "status": FAIL,
            "next_action": f"Fix manifest at {MANIFEST_RELATIVE_PATH}: {'; '.join(manifest_state.errors)}",
        }
    disabled_raw = (
        manifest_state.data.get("doctor", {}).get("disable_canonical_checks", []) if manifest_state.data else []
    )
    disabled = {entry for entry in disabled_raw if isinstance(entry, str)}
    canonical = run_canonical_checks(repo_root, disabled=disabled)
    manifest_checks = (
        run_manifest_doctor_checks(repo_root, manifest_state.data)
        if manifest_state.found and manifest_state.valid
        else []
    )
    all_checks = canonical + manifest_checks
    status = aggregate_status(all_checks)
    next_action = _first_next_action(all_checks) if status == FAIL else None
    return {
        "checked_at": now_iso(),
        "manifest": manifest_state.to_dict(),
        "checks": [result.to_dict() for result in all_checks],
        "status": status,
        "next_action": next_action,
    }


def _first_next_action(results: list[CheckResult]) -> str:
    for result in results:
        if result.status == FAIL and result.next_action:
            return result.next_action
    return "Run `charness worktree prepare` to install dependencies and hooks for this worktree."


def _missing_manifest_payload(manifest_state: ManifestState) -> dict[str, Any]:
    return {
        "checked_at": now_iso(),
        "manifest": manifest_state.to_dict(),
        "executed": [],
        "doctor": {
            "checked_at": now_iso(),
            "manifest": manifest_state.to_dict(),
            "checks": [],
            "status": FAIL,
            "next_action": f"Fix manifest at {MANIFEST_RELATIVE_PATH}.",
        },
        "status": FAIL,
        "next_action": (
            f"Add a worktree adapter at {MANIFEST_RELATIVE_PATH}; see {EXAMPLE_RELATIVE_PATH} for a starter template."
            if not manifest_state.found
            else f"Fix manifest at {MANIFEST_RELATIVE_PATH}: {'; '.join(manifest_state.errors)}"
        ),
    }


def _execute_prepare_command(entry: dict[str, Any], repo_root: Path) -> tuple[CommandResult, bool]:
    command_id = entry.get("id") or "step"
    argv = list(entry.get("argv") or [])
    timeout = int(entry.get("timeout_seconds") or DEFAULT_PREPARE_TIMEOUT_SECONDS)
    start = time.monotonic()
    try:
        result = subprocess.run(
            argv,
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        return (
            CommandResult(
                id=command_id,
                argv=argv,
                exit_code=None,
                duration_ms=duration_ms,
                stdout_tail="",
                stderr_tail=f"command not found: {exc.filename or (argv[0] if argv else '')}",
            ),
            True,
        )
    except subprocess.TimeoutExpired as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        stderr_tail = tail(exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or ""))
        stdout_tail = tail(exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or ""))
        return (
            CommandResult(
                id=command_id,
                argv=argv,
                exit_code=None,
                duration_ms=duration_ms,
                stdout_tail=stdout_tail,
                stderr_tail=stderr_tail,
                timed_out=True,
            ),
            True,
        )
    duration_ms = int((time.monotonic() - start) * 1000)
    return (
        CommandResult(
            id=command_id,
            argv=argv,
            exit_code=result.returncode,
            duration_ms=duration_ms,
            stdout_tail=tail(result.stdout or ""),
            stderr_tail=tail(result.stderr or ""),
        ),
        result.returncode != 0,
    )


def run_prepare(repo_root: Path, *, force: bool = False) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    manifest_state = load_manifest(repo_root)
    if not manifest_state.found or not manifest_state.valid:
        return _missing_manifest_payload(manifest_state)

    pre_doctor = run_doctor(repo_root)
    skip_when_clean = bool(manifest_state.data.get("prepare", {}).get("skip_if_doctor_passes", True))
    if pre_doctor["status"] == PASS and skip_when_clean and not force:
        return {
            "checked_at": now_iso(),
            "manifest": manifest_state.to_dict(),
            "executed": [],
            "doctor": pre_doctor,
            "status": PASS,
            "next_action": None,
            "skipped": "doctor already reports pass; pass --force to run prepare anyway.",
        }

    commands = manifest_state.data.get("prepare", {}).get("commands") or []
    executed: list[CommandResult] = []
    failure_seen = False
    for entry in commands:
        result, failed = _execute_prepare_command(entry, repo_root)
        executed.append(result)
        if failed:
            failure_seen = True
            break

    post_doctor = run_doctor(repo_root)
    if failure_seen:
        status = FAIL
        next_action = "A prepare command failed; fix it and re-run `charness worktree prepare`."
    elif post_doctor["status"] == FAIL:
        status = FAIL
        next_action = post_doctor.get("next_action") or "Doctor still reports failures after prepare; inspect output."
    else:
        status = PASS
        next_action = None

    return {
        "checked_at": now_iso(),
        "manifest": manifest_state.to_dict(),
        "executed": [item.to_dict() for item in executed],
        "doctor": post_doctor,
        "status": status,
        "next_action": next_action,
    }


def render_doctor_text(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    manifest = payload.get("manifest") or {}
    if manifest.get("found"):
        lines.append(f"manifest: {manifest.get('path')} ({'valid' if manifest.get('valid') else 'invalid'})")
    else:
        lines.append("manifest: none (canonical checks only)")
    for check in payload.get("checks") or []:
        line = f"{check['id']}: {check['status']}"
        if check.get("detail"):
            line += f" — {check['detail']}"
        lines.append(line)
    lines.append(f"status: {payload.get('status')}")
    next_action = payload.get("next_action")
    if next_action:
        lines.append(f"next: {next_action}")
    return "\n".join(lines)


def render_prepare_text(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    manifest = payload.get("manifest") or {}
    if manifest.get("found"):
        lines.append(f"manifest: {manifest.get('path')} ({'valid' if manifest.get('valid') else 'invalid'})")
    else:
        lines.append("manifest: none — nothing to run")
    skipped = payload.get("skipped")
    if skipped:
        lines.append(f"skipped: {skipped}")
    for command in payload.get("executed") or []:
        line = f"{command['id']}: exit={command.get('exit_code')} duration={command.get('duration_ms')}ms"
        if command.get("timed_out"):
            line += " (timed out)"
        lines.append(line)
    doctor = payload.get("doctor") or {}
    lines.append(f"post-doctor: {doctor.get('status')}")
    lines.append(f"status: {payload.get('status')}")
    next_action = payload.get("next_action")
    if next_action:
        lines.append(f"next: {next_action}")
    return "\n".join(lines)


def emit_payload(payload: dict[str, Any], *, json_mode: bool, renderer) -> None:
    if json_mode:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(renderer(payload))
