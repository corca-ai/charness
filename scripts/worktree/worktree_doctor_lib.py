from __future__ import annotations

import time
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
_runtime_bootstrap = import_repo_module(__file__, "scripts.runtime_bootstrap")
ReuseSpec = _reuse.ReuseSpec
DEPENDENCY_CACHE_DIR_NAME = _reuse.CACHE_DIR_NAME


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
    _reuse.validate_dependency_reuse(prepare, errors)


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


def default_dependency_cache_root(repo_root: Path, source_root: Path | None) -> Path:
    """The shared cache for installed dependency trees, keyed by the owning repo.

    Lanes of one parent repo must land on one cache, so the key is the parent
    (source) root when the caller names it, else the main worktree the checkout
    belongs to, else the checkout itself.
    """
    owner = source_root
    if owner is None:
        facts = _checks.git_checkout_facts(repo_root, include_hooks_path=False)
        owner = _checks.main_worktree(facts.common_dir) or repo_root
    return _runtime_bootstrap.runtime_root(owner) / DEPENDENCY_CACHE_DIR_NAME


def run_prepare(
    repo_root: Path,
    *,
    force: bool = False,
    require_isolation: bool = False,
    pre_doctor: dict[str, Any] | None = None,
    source_root: Path | None = None,
    dependency_cache_root: Path | None = None,
    dependency_reuse: bool = True,
) -> dict[str, Any]:
    """Prepare a worktree, carrying the caller's isolation requirement THROUGH.

    `source_root` names the tree this worktree was created from; with a manifest
    `prepare.dependency_reuse` declaration its installed tree (or the runtime
    cache keyed by lockfile digest) is linked in before the install command,
    which is then skipped (#792). `dependency_reuse=False` disables the whole
    path; `force` does not, because force re-runs prepare, and reuse IS prepare.

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
    reuse = _DependencyReuse.attempt(
        manifest_state.data.get("prepare"),
        repo_root,
        source_root=source_root,
        cache_root=dependency_cache_root,
        enabled=dependency_reuse,
    )
    executed, failure_seen = reuse.run_commands(commands, repo_root)

    post_doctor = run_doctor(repo_root, require_isolation=require_isolation)
    status, next_step = _prepare_verdict(post_doctor, failure_seen=failure_seen, reuse=reuse)
    payload: dict[str, Any] = {
        "checked_at": now_iso(),
        "manifest": manifest_state.to_dict(),
        "executed": [item.to_dict() for item in executed],
        "doctor": post_doctor,
        "coverage": coverage,
        "status": status,
        "next_step": next_step,
    }
    if reuse.payload is not None:
        payload["dependency_reuse"] = reuse.payload
    return payload


def _prepare_verdict(
    post_doctor: dict[str, Any], *, failure_seen: bool, reuse: _DependencyReuse
) -> tuple[str, str | None]:
    if failure_seen:
        return FAIL, "A prepare command failed; fix it and re-run `charness worktree prepare`."
    if post_doctor["status"] != FAIL:
        return PASS, None
    if reuse.reused_command_id is not None and reuse.spec is not None and reuse.payload:
        return FAIL, (
            f"Doctor rejects the reused {reuse.spec.directory} linked from "
            f"{reuse.payload['source']}; remove it and re-run "
            "`charness worktree prepare --no-dependency-reuse`."
        )
    return FAIL, (
        post_doctor.get("next_step")
        or "Doctor still reports failures after prepare; inspect output."
    )


class _DependencyReuse:
    """The #792 reuse step around the declared prepare commands.

    `attempt` links a matching installed tree before any command runs and names
    the command that is therefore skipped; `run_commands` executes the rest and,
    when the install command had to run, seeds the cache for the next worktree.
    """

    def __init__(
        self,
        spec: ReuseSpec | None,
        payload: dict[str, Any] | None,
        *,
        cache_root: Path | None,
        enabled: bool,
    ) -> None:
        self.spec = spec
        self.payload = payload
        self.cache_root = cache_root
        self.enabled = enabled
        self.reused_command_id = (
            spec.command_id
            if spec is not None
            and payload is not None
            and payload["strategy"] != _reuse.STRATEGY_NONE
            else None
        )

    @classmethod
    def attempt(
        cls,
        prepare: dict[str, Any] | None,
        repo_root: Path,
        *,
        source_root: Path | None,
        cache_root: Path | None,
        enabled: bool,
    ) -> _DependencyReuse:
        spec = ReuseSpec.from_manifest(prepare)
        if spec is None:
            return cls(None, None, cache_root=None, enabled=enabled)
        if not enabled:
            payload = {
                "command_id": spec.command_id,
                "directory": spec.directory,
                "strategy": _reuse.STRATEGY_NONE,
                "origin": None,
                "source": None,
                "lockfile_digest": None,
                "reason": "disabled by --no-dependency-reuse",
                "duration_ms": 0,
                "attempts": [],
            }
            return cls(spec, payload, cache_root=None, enabled=False)
        cache_root = cache_root or default_dependency_cache_root(repo_root, source_root)
        payload = _reuse.attempt_reuse(
            repo_root, spec, source_root=source_root, cache_root=cache_root
        )
        return cls(spec, payload, cache_root=cache_root, enabled=True)

    def run_commands(
        self, commands: list[dict[str, Any]], repo_root: Path
    ) -> tuple[list[CommandResult], bool]:
        executed: list[CommandResult] = []
        install_ran = False
        for entry in commands:
            if self.reused_command_id is not None and entry.get("id") == self.reused_command_id:
                continue
            result, failed = _execute_prepare_command(entry, repo_root)
            executed.append(result)
            if failed:
                return executed, True
            if self.spec is not None and entry.get("id") == self.spec.command_id:
                install_ran = True
        if install_ran and self.enabled and self.payload is not None and self.spec is not None:
            self.payload["cache_seed"] = _reuse.seed_cache(
                repo_root, self.spec, cache_root=self.cache_root
            )
        return executed, False
