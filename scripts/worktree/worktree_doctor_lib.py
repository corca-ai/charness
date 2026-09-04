from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_adapter_lib_module = import_repo_module(__file__, "scripts.adapter_lib")
_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process
TIMEOUT_EXIT_CODE = _subprocess_guard.TIMEOUT_EXIT_CODE
load_yaml_file = _adapter_lib_module.load_yaml_file
validate_adapter_version = _adapter_lib_module.validate_adapter_version

_state = import_repo_module(__file__, "scripts.worktree.worktree_doctor_state")
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

_checks = import_repo_module(__file__, "scripts.worktree.worktree_doctor_checks")
run_canonical_checks = _checks.run_canonical_checks
run_canonical_checks_with_facts = _checks.run_canonical_checks_with_facts
run_manifest_doctor_checks = _checks.run_manifest_doctor_checks

_reuse = import_repo_module(__file__, "scripts.worktree.worktree_dependency_reuse")

_DOCTOR_CHECK_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_.-]*$")
_ROOT_KEYS = frozenset({"version", "repo", "language", "prepare", "doctor"})
_PREPARE_KEYS = frozenset({"commands", "skip_if_doctor_passes", "dependency_reuse"})
_PREPARE_COMMAND_KEYS = frozenset({"id", "argv", "description", "timeout_seconds"})
_DOCTOR_KEYS = frozenset({"checks", "disable_canonical_checks"})
_DOCTOR_CHECK_KEYS = frozenset(
    {
        "id",
        "argv",
        "description",
        "expect_exit_code",
        "next_action_hint",
        "covers",
        "timeout_seconds",
    }
)


def _is_strict_int(value: object) -> bool:
    return type(value) is int


def _reject_unknown_keys(
    mapping: dict[str, Any], allowed: frozenset[str], label: str, errors: list[str]
) -> None:
    for key in mapping:
        if key not in allowed:
            errors.append(f"{label} has unknown key {key!r}")


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
    # Hand-rolled `!= 1` accepted `version: true`, because `True == 1` in Python -- and
    # this manifest selects the argv this tool runs. The shared reconciler owns the
    # boolean case; the prefix keeps the wording every fixture here already expects.
    version_errors: list[str] = []
    validate_adapter_version(data, {}, version_errors, required=True)
    errors.extend(f"manifest.{error}" for error in version_errors)
    _reject_unknown_keys(data, _ROOT_KEYS, "manifest", errors)
    _validate_prepare_section(data.get("prepare"), errors)
    _validate_doctor_section(data.get("doctor"), errors)
    return errors


def _validate_prepare_section(prepare: Any, errors: list[str]) -> None:
    if not isinstance(prepare, dict):
        errors.append("manifest.prepare must be a mapping with `commands`")
        return
    _reject_unknown_keys(prepare, _PREPARE_KEYS, "manifest.prepare", errors)
    commands = prepare.get("commands")
    if not isinstance(commands, list) or not commands:
        errors.append("manifest.prepare.commands must be a non-empty list")
    else:
        seen_ids: list[str] = []
        for index, entry in enumerate(commands):
            command_id = _validate_command_entry(
                entry, f"manifest.prepare.commands[{index}]", errors
            )
            if command_id is not None:
                if command_id in seen_ids:
                    errors.append(
                        f"manifest.prepare.commands[{index}].id {command_id!r} is "
                        "duplicated within manifest.prepare.commands"
                    )
                else:
                    seen_ids.append(command_id)
    skip = prepare.get("skip_if_doctor_passes", False)
    if not isinstance(skip, bool):
        errors.append("manifest.prepare.skip_if_doctor_passes must be a boolean")
    _reuse.validate_dependency_reuse(prepare, errors)


def _validate_doctor_section(doctor: Any, errors: list[str]) -> None:
    if doctor is None:
        return
    if not isinstance(doctor, dict):
        errors.append("manifest.doctor must be a mapping")
        return
    _reject_unknown_keys(doctor, _DOCTOR_KEYS, "manifest.doctor", errors)
    checks = doctor.get("checks")
    if checks is not None:
        if not isinstance(checks, list):
            errors.append("manifest.doctor.checks must be a list")
        else:
            seen_ids: set[str] = set()
            for index, entry in enumerate(checks):
                _validate_doctor_check_entry(
                    entry, f"manifest.doctor.checks[{index}]", errors, seen_ids
                )
    disabled = doctor.get("disable_canonical_checks")
    if disabled is not None:
        _validate_disabled_checks(disabled, errors)


def _validate_disabled_checks(disabled: Any, errors: list[str]) -> None:
    if not isinstance(disabled, list):
        errors.append("manifest.doctor.disable_canonical_checks must be a list")
        return
    if len(disabled) != len(set(disabled)):
        errors.append("manifest.doctor.disable_canonical_checks must not contain duplicates")
    for entry in disabled:
        if entry not in CANONICAL_CHECK_IDS:
            errors.append(
                f"manifest.doctor.disable_canonical_checks: unknown check id {entry!r}; allowed: {list(CANONICAL_CHECK_IDS)}"
            )


def _validate_command_entry(entry: Any, label: str, errors: list[str]) -> str | None:
    if not isinstance(entry, dict):
        errors.append(f"{label} must be a mapping")
        return None
    _reject_unknown_keys(entry, _PREPARE_COMMAND_KEYS, label, errors)
    command_id = entry.get("id")
    if command_id is not None and (not isinstance(command_id, str) or not command_id):
        errors.append(f"{label}.id must be a non-empty string")
        command_id = None
    _validate_argv(entry.get("argv"), f"{label}.argv", errors)
    timeout = entry.get("timeout_seconds")
    if timeout is not None and not (_is_strict_int(timeout) and 1 <= timeout <= 1800):
        errors.append(f"{label}.timeout_seconds must be an integer between 1 and 1800")
    return command_id if isinstance(command_id, str) else None


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


def _validate_doctor_check_entry(
    entry: Any, label: str, errors: list[str], seen_ids: set[str]
) -> None:
    if not isinstance(entry, dict):
        errors.append(f"{label} must be a mapping")
        return
    _reject_unknown_keys(entry, _DOCTOR_CHECK_KEYS, label, errors)
    check_id = entry.get("id")
    if not isinstance(check_id, str) or not check_id:
        errors.append(f"{label}.id must be a non-empty string")
    elif not _DOCTOR_CHECK_ID_PATTERN.fullmatch(check_id):
        errors.append(
            f"{label}.id {check_id!r} must match {_DOCTOR_CHECK_ID_PATTERN.pattern}"
        )
    elif check_id in seen_ids:
        errors.append(f"{label}.id {check_id!r} is duplicated within manifest.doctor.checks")
    else:
        seen_ids.add(check_id)
    _validate_argv(entry.get("argv"), f"{label}.argv", errors)
    covers = entry.get("covers")
    if covers is not None:
        if not isinstance(covers, list):
            errors.append(f"{label}.covers must be a list of prepare command ids")
        elif any(not isinstance(command_id, str) or not command_id for command_id in covers):
            errors.append(f"{label}.covers must contain only non-empty strings")
        elif len(covers) != len(set(covers)):
            errors.append(f"{label}.covers must not contain duplicates")
    expect = entry.get("expect_exit_code", 0)
    if not _is_strict_int(expect):
        errors.append(f"{label}.expect_exit_code must be an integer")
    timeout = entry.get("timeout_seconds")
    if timeout is not None and not (_is_strict_int(timeout) and 1 <= timeout <= 120):
        errors.append(f"{label}.timeout_seconds must be an integer between 1 and 120")


def run_doctor(repo_root: Path, *, require_isolation: bool = False) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    manifest_state = load_manifest(repo_root)
    if manifest_state.found and not manifest_state.valid:
        return {
            "checked_at": now_iso(),
            "manifest": manifest_state.to_dict(),
            "checks": [],
            "status": FAIL,
            "next_step": f"Fix manifest at {MANIFEST_RELATIVE_PATH}: {'; '.join(manifest_state.errors)}",
        }
    disabled_raw = (
        manifest_state.data.get("doctor", {}).get("disable_canonical_checks", [])
        if manifest_state.data
        else []
    )
    disabled = {entry for entry in disabled_raw if isinstance(entry, str)}
    canonical, facts = run_canonical_checks_with_facts(
        repo_root, disabled=disabled, require_isolation=require_isolation
    )
    manifest_checks = (
        run_manifest_doctor_checks(repo_root, manifest_state.data)
        if manifest_state.found and manifest_state.valid
        else []
    )
    all_checks = canonical + manifest_checks
    status = aggregate_status(all_checks)
    next_step = _first_next_step(all_checks) if status == FAIL else None
    return {
        "checked_at": now_iso(),
        "manifest": manifest_state.to_dict(),
        "checks": [result.to_dict() for result in all_checks],
        "status": status,
        "next_step": next_step,
        # Internal handoff for a just-created linked worktree. The canonical
        # checks already proved this checkout's own git dir; consumers must
        # revalidate the path before using it and must fail closed if absent.
        "_checkout": {
            "own_dir": str(facts.own_dir) if facts.own_dir is not None else None,
        },
    }


def _first_next_step(results: list[CheckResult]) -> str:
    for result in results:
        if result.status == FAIL and result.next_step:
            return result.next_step
    return "Run `charness worktree prepare` to install dependencies and hooks for this worktree."


# Prepare lives in its own module; these names stay importable from here so the
# CLI, `worktree create`, and existing tests keep one import.
_prepare = import_repo_module(__file__, "scripts.worktree.worktree_prepare_lib")
run_prepare = _prepare.run_prepare
_prepare_coverage = _prepare._prepare_coverage
default_dependency_cache_root = _prepare.default_dependency_cache_root
DEPENDENCY_CACHE_DIR_NAME = _prepare.DEPENDENCY_CACHE_DIR_NAME
