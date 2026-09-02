from __future__ import annotations

import time
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
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
    skip = prepare.get("skip_if_doctor_passes", False)
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


def _validate_doctor_check_entry(
    entry: Any, label: str, errors: list[str], seen_ids: set[str]
) -> None:
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
    covers = entry.get("covers")
    if covers is not None:
        if not isinstance(covers, list):
            errors.append(f"{label}.covers must be a list of prepare command ids")
        elif any(not isinstance(command_id, str) or not command_id for command_id in covers):
            errors.append(f"{label}.covers must contain only non-empty strings")
    expect = entry.get("expect_exit_code", 0)
    if not isinstance(expect, int):
        errors.append(f"{label}.expect_exit_code must be an integer")
    timeout = entry.get("timeout_seconds")
    if timeout is not None and not (isinstance(timeout, int) and 1 <= timeout <= 120):
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
            "next_step": f"Fix manifest at {MANIFEST_RELATIVE_PATH}.",
        },
        "status": FAIL,
        "next_step": (
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
        result = run_process(argv, cwd=repo_root, timeout_seconds=timeout)
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
    if result.returncode == TIMEOUT_EXIT_CODE:
        duration_ms = int((time.monotonic() - start) * 1000)
        stderr_tail = tail(result.stderr or "")
        stdout_tail = tail(result.stdout or "")
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


def _prepare_coverage(manifest: dict[str, Any], doctor: dict[str, Any]) -> dict[str, Any]:
    """Derive the skip licence from the manifest's explicit coverage relation.

    The relation is ``doctor.checks[].covers`` -> ``prepare.commands[].id``.
    Neither command argv nor check names are interpreted. A relation is
    established only when every prepare command has a unique id and each id is
    covered by a doctor check that actually passed in this doctor run.
    """
    commands = (manifest.get("prepare") or {}).get("commands") or []
    prepare_ids: list[str | None] = [
        entry.get("id") if isinstance(entry, dict) and isinstance(entry.get("id"), str) else None
        for entry in commands
    ]
    doctor_checks = (manifest.get("doctor") or {}).get("checks") or []
    declared_by_check: dict[str, set[str]] = {}
    for entry in doctor_checks:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            continue
        covers = entry.get("covers")
        if not isinstance(covers, list):
            continue
        declared_by_check[entry["id"]] = {
            command_id for command_id in covers if isinstance(command_id, str) and command_id
        }

    passing_ids = {
        check.get("id")
        for check in doctor.get("checks") or []
        if isinstance(check, dict)
        and check.get("status") == PASS
        and isinstance(check.get("id"), str)
    }
    passing_coverage = {
        check_id: declared_by_check[check_id]
        for check_id in sorted(passing_ids)
        if check_id in declared_by_check
    }
    declared_intersection = {
        command_id for covered_ids in passing_coverage.values() for command_id in covered_ids
    }
    intersection = sorted(
        command_id
        for command_id in set(prepare_ids) - {None}
        if command_id in declared_intersection
    )
    uncovered = [
        command_id
        for command_id in prepare_ids
        if command_id is None or command_id not in declared_intersection
    ]
    unique_prepare_ids = len(prepare_ids) == len(set(prepare_ids)) and None not in prepare_ids
    established = bool(prepare_ids) and unique_prepare_ids and not uncovered
    covering_check_ids = sorted(
        check_id
        for check_id, covered_ids in passing_coverage.items()
        if covered_ids.intersection(set(intersection))
    )
    return {
        "established": established,
        "prepare_command_ids": prepare_ids,
        "doctor_check_ids": covering_check_ids,
        "intersection": intersection,
        "uncovered_prepare_command_ids": uncovered,
    }


def run_prepare(
    repo_root: Path,
    *,
    force: bool = False,
    require_isolation: bool = False,
    pre_doctor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prepare a worktree, carrying the caller's isolation requirement THROUGH.

    `require_isolation` is threaded rather than defaulted away because
    `worktree create --prepare` replaces its own doctor payload with this
    function's. Without it, an isolation-required FAIL computed by the caller was
    recomputed here WITHOUT the requirement, and both the payload and the status
    were overwritten with a pass -- on `--prepare`, which is the exact path the
    operating contract prescribes as the mechanism. Round-2 finding: the rule was
    enforced somewhere, but not on the path a consumer actually hits.
    """
    repo_root = repo_root.resolve()
    manifest_state = load_manifest(repo_root)
    if not manifest_state.found or not manifest_state.valid:
        return _missing_manifest_payload(manifest_state)

    if pre_doctor is None:
        pre_doctor = run_doctor(repo_root, require_isolation=require_isolation)
    coverage = _prepare_coverage(manifest_state.data, pre_doctor)
    skip_when_clean = bool(
        manifest_state.data.get("prepare", {}).get("skip_if_doctor_passes", False)
    )
    if pre_doctor["status"] == PASS and skip_when_clean and coverage["established"] and not force:
        prepare_ids = ", ".join(coverage["prepare_command_ids"])
        doctor_ids = ", ".join(coverage["doctor_check_ids"])
        return {
            "checked_at": now_iso(),
            "manifest": manifest_state.to_dict(),
            "executed": [],
            "doctor": pre_doctor,
            "coverage": coverage,
            "status": PASS,
            "next_step": None,
            # Exit-ZERO attention state: prepare ran NOTHING. YAML renders this key
            # verbatim as `skipped: <reason>`, which is the visible marker that a
            # passing prepare here did no work -- and the evidence term declared in
            # skills/public/quality/references/attention-state-visibility.json.
            "skipped": (
                "doctor passed and declared coverage justifies skipping prepare command(s) "
                f"[{prepare_ids}] via doctor check(s) [{doctor_ids}]; pass --force to run prepare anyway."
            ),
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

    post_doctor = run_doctor(repo_root, require_isolation=require_isolation)
    if failure_seen:
        status = FAIL
        next_step = "A prepare command failed; fix it and re-run `charness worktree prepare`."
    elif post_doctor["status"] == FAIL:
        status = FAIL
        next_step = (
            post_doctor.get("next_step")
            or "Doctor still reports failures after prepare; inspect output."
        )
    else:
        status = PASS
        next_step = None

    return {
        "checked_at": now_iso(),
        "manifest": manifest_state.to_dict(),
        "executed": [item.to_dict() for item in executed],
        "doctor": post_doctor,
        "coverage": coverage,
        "status": status,
        "next_step": next_step,
    }
