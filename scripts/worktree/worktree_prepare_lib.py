"""Prepare a worktree: the adapter's prepare commands around dependency reuse.

`worktree_doctor_lib` owns the manifest and the read-only doctor; this module
owns what `charness worktree prepare` DOES with them: the coverage-licensed
skip, the dependency-reuse step before the install command, the commands
themselves, the post-prepare doctor, and the verdict. The doctor module
re-exports `run_prepare` so existing callers keep one import.
"""

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

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process
TIMEOUT_EXIT_CODE = _subprocess_guard.TIMEOUT_EXIT_CODE

_state = import_repo_module(__file__, "scripts.worktree.worktree_doctor_state")
CommandResult = _state.CommandResult
DEFAULT_PREPARE_TIMEOUT_SECONDS = _state.DEFAULT_PREPARE_TIMEOUT_SECONDS
EXAMPLE_RELATIVE_PATH = _state.EXAMPLE_RELATIVE_PATH
FAIL = _state.FAIL
MANIFEST_RELATIVE_PATH = _state.MANIFEST_RELATIVE_PATH
ManifestState = _state.ManifestState
PASS = _state.PASS
now_iso = _state.now_iso
tail = _state.tail

_checks = import_repo_module(__file__, "scripts.worktree.worktree_doctor_checks")
_reuse = import_repo_module(__file__, "scripts.worktree.worktree_dependency_reuse")
_runtime_bootstrap = import_repo_module(__file__, "scripts.runtime_bootstrap")
ReuseSpec = _reuse.ReuseSpec
DEPENDENCY_CACHE_DIR_NAME = _reuse.CACHE_DIR_NAME


def _doctor():
    """The doctor module, looked up at call time so a caller's monkeypatch of
    `worktree_doctor_lib.run_doctor` reaches this module too."""
    return import_repo_module(__file__, "scripts.worktree.worktree_doctor_lib")


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
    declared_by_check = _covers_by_check(manifest)
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


def _covers_by_check(manifest: dict[str, Any]) -> dict[str, set[str]]:
    doctor_checks = (manifest.get("doctor") or {}).get("checks") or []
    declared: dict[str, set[str]] = {}
    for entry in doctor_checks:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            continue
        covers = entry.get("covers")
        if not isinstance(covers, list):
            continue
        declared[entry["id"]] = {
            command_id for command_id in covers if isinstance(command_id, str) and command_id
        }
    return declared


def parent_worktree(repo_root: Path) -> Path | None:
    """The main worktree this checkout belongs to, when it is a different tree."""
    facts = _checks.git_checkout_facts(repo_root, include_hooks_path=False)
    main = _checks.main_worktree(facts.common_dir)
    if main is None or main.resolve() == repo_root.resolve():
        return None
    return main


def default_dependency_cache_root(repo_root: Path, source_root: Path | None) -> Path:
    """The shared cache for installed dependency trees, keyed by the owning repo.

    Lanes of one parent repo must land on one cache, so the key is the parent
    (source) root when the caller names it, else the main worktree the checkout
    belongs to, else the checkout itself.
    """
    owner = source_root or parent_worktree(repo_root) or repo_root
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

    `require_isolation` is threaded rather than defaulted away because
    `worktree create --prepare` replaces its own doctor payload with this
    function's. Without it, an isolation-required FAIL computed by the caller was
    recomputed here WITHOUT the requirement, and both the payload and the status
    were overwritten with a pass -- on `--prepare`, which is the exact path the
    operating contract prescribes as the mechanism. Round-2 finding: the rule was
    enforced somewhere, but not on the path a consumer actually hits.

    `source_root` names the tree this worktree was created from; a plain
    `worktree prepare` derives the main worktree instead. With a manifest
    `prepare.dependency_reuse` declaration its installed tree (or the runtime
    cache keyed by lockfile digest) is linked in before the install command,
    which is then skipped. `dependency_reuse=False` disables the whole path;
    `force` does not, because force re-runs prepare, and reuse IS prepare.
    """
    doctor = _doctor()
    repo_root = repo_root.resolve()
    manifest_state = doctor.load_manifest(repo_root)
    if not manifest_state.found or not manifest_state.valid:
        return _missing_manifest_payload(manifest_state)

    if pre_doctor is None:
        pre_doctor = doctor.run_doctor(repo_root, require_isolation=require_isolation)
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
    executed, failure_seen, install_ran = reuse.run_commands(commands, repo_root)

    post_doctor = doctor.run_doctor(repo_root, require_isolation=require_isolation)
    # The cache is published only from a tree the doctor accepted: an install
    # that exited zero but fails readiness must never become a later lane's
    # donor (release-8-3-0-code-2 F1).
    reuse.seed_after_doctor(repo_root, install_ran=install_ran, doctor_status=post_doctor["status"])
    status, next_step = _prepare_verdict(
        post_doctor, manifest_state.data, failure_seen=failure_seen, reuse=reuse
    )
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
    post_doctor: dict[str, Any],
    manifest: dict[str, Any],
    *,
    failure_seen: bool,
    reuse: _DependencyReuse,
) -> tuple[str, str | None]:
    if failure_seen:
        return FAIL, "A prepare command failed; fix it and re-run `charness worktree prepare`."
    if post_doctor["status"] != FAIL:
        return PASS, None
    if reuse.blamed_by(post_doctor, manifest):
        return FAIL, (
            f"Doctor check(s) covering {reuse.reused_command_id} reject the reused "
            f"{reuse.spec.directory} linked from {reuse.payload['source']}; remove it and "
            "re-run `charness worktree prepare --no-dependency-reuse`."
        )
    return FAIL, (
        post_doctor.get("next_step")
        or "Doctor still reports failures after prepare; inspect output."
    )


class _DependencyReuse:
    """The dependency-reuse step around the declared prepare commands.

    `attempt` links a matching installed tree before any command runs and names
    the command that is therefore skipped; `run_commands` executes the rest;
    `seed_after_doctor` publishes a fresh install to the cache only once the
    post-prepare doctor accepted it.
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
            payload = _reuse.disabled_result(spec, reason="disabled by --no-dependency-reuse")
            return cls(spec, payload, cache_root=None, enabled=False)
        source_root = source_root or parent_worktree(repo_root)
        cache_root = cache_root or default_dependency_cache_root(repo_root, source_root)
        payload = _reuse.attempt_reuse(
            repo_root, spec, source_root=source_root, cache_root=cache_root
        )
        return cls(spec, payload, cache_root=cache_root, enabled=True)

    def run_commands(
        self, commands: list[dict[str, Any]], repo_root: Path
    ) -> tuple[list[CommandResult], bool, bool]:
        executed: list[CommandResult] = []
        install_ran = False
        for entry in commands:
            if self.reused_command_id is not None and entry.get("id") == self.reused_command_id:
                continue
            result, failed = _execute_prepare_command(entry, repo_root)
            executed.append(result)
            if failed:
                return executed, True, install_ran
            if self.spec is not None and entry.get("id") == self.spec.command_id:
                install_ran = True
        return executed, False, install_ran

    def seed_after_doctor(self, repo_root: Path, *, install_ran: bool, doctor_status: str) -> None:
        if not (
            install_ran and self.enabled and self.payload is not None and self.spec is not None
        ):
            return
        if doctor_status != PASS:
            self.payload["cache_seed"] = {
                "seeded": False,
                "entry": None,
                "reason": "doctor rejected the fresh install; not published to the cache",
                "duration_ms": 0,
            }
            return
        self.payload["cache_seed"] = _reuse.seed_cache(
            repo_root, self.spec, cache_root=self.cache_root
        )

    def blamed_by(self, post_doctor: dict[str, Any], manifest: dict[str, Any]) -> bool:
        """True only when a FAILED doctor check declares it covers the reused command."""
        if self.reused_command_id is None or self.spec is None or self.payload is None:
            return False
        covers = _covers_by_check(manifest)
        return any(
            isinstance(check, dict)
            and check.get("status") == FAIL
            and self.reused_command_id in covers.get(str(check.get("id")), set())
            for check in post_doctor.get("checks") or []
        )
