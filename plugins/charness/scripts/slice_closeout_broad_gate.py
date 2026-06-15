from __future__ import annotations

import hashlib
import json
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BROAD_PYTEST_LOCK_MESSAGE = (
    "broad pytest closeout requires an explicit verification lock; rerun with "
    "--verification-lock after recording that the mutation set is locked, or use "
    "--skip-broad-pytest for a pre-lock rehearsal"
)
BROAD_PYTEST_PHASE_CONFLICT_MESSAGE = (
    "--skip-broad-pytest and --verification-lock are mutually exclusive; choose "
    "pre-lock focused-proof rehearsal or final locked broad proof"
)
PRE_LOCK_RECOMMENDATION = (
    "Use focused current-diff proof for the pre-lock slice, then rerun broad pytest "
    "with --verification-lock after recording that the mutation set is locked."
)
PRE_LOCK_COST_WARNING = (
    "Pre-lock broad pytest can become stale after reviewer-driven changes; skipping it "
    "keeps the expensive proof for the final locked closeout."
)
LOCK_REQUIRED_RECOMMENDATION = (
    "Choose --skip-broad-pytest for a pre-lock rehearsal, or record the mutation set "
    "as locked and rerun with --verification-lock."
)
LOCK_REQUIRED_COST_WARNING = (
    "Running broad pytest without an explicit phase makes the cost/evidence boundary "
    "ambiguous."
)
VERIFICATION_LOCK_RECOMMENDATION = (
    "Broad pytest remains in the plan because this run declares the final verification lock."
)
BROAD_PYTEST_CACHE_RELATIVE = Path(".charness/closeout/broad-pytest-proof.json")
STANDING_PYTEST_RUNNER_HELPER_FLAGS = {
    "--print-targets",
    "--print-expanded-targets",
    "--print-temp-root",
    "--print-command",
}


def is_broad_pytest_command(command: str) -> bool:
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    if not tokens:
        return False
    if any(Path(token).name == "run_standing_pytest.py" for token in tokens):
        token_set = set(tokens)
        return not STANDING_PYTEST_RUNNER_HELPER_FLAGS & token_set
    has_pytest = "pytest" in tokens or (
        len(tokens) >= 3 and tokens[0].endswith("python3") and tokens[1:3] == ["-m", "pytest"]
    )
    if not has_pytest:
        return False
    token_set = set(tokens)
    return "tests/quality_gates" in token_set and "tests/control_plane" in token_set


def split_broad_pytest_commands(
    command_plan: list[tuple[str, str]]
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    ordinary: list[tuple[str, str]] = []
    broad: list[tuple[str, str]] = []
    for phase, command in command_plan:
        if is_broad_pytest_command(command):
            broad.append((phase, command))
        else:
            ordinary.append((phase, command))
    return ordinary, broad


def plan_broad_pytest_policy(
    command_plan: list[tuple[str, str]], *, skip_broad_pytest: bool, verification_lock: bool
) -> dict[str, object]:
    ordinary, broad = split_broad_pytest_commands(command_plan)
    phase_conflict = bool(broad and skip_broad_pytest and verification_lock)
    planned = ordinary if broad and skip_broad_pytest else command_plan
    policy_mode = ""
    recommendation = ""
    cost_warning = ""
    if broad and skip_broad_pytest:
        policy_mode = "pre-lock-rehearsal"
        recommendation = PRE_LOCK_RECOMMENDATION
        cost_warning = PRE_LOCK_COST_WARNING
    elif broad and verification_lock:
        policy_mode = "verification-lock"
        recommendation = VERIFICATION_LOCK_RECOMMENDATION
    elif broad:
        policy_mode = "lock-required"
        recommendation = LOCK_REQUIRED_RECOMMENDATION
        cost_warning = LOCK_REQUIRED_COST_WARNING
    return {
        "command_plan": planned,
        "broad_pytest_commands": [{"phase": phase, "command": command} for phase, command in broad],
        "broad_pytest_policy_mode": policy_mode,
        "broad_pytest_recommendation": recommendation,
        "broad_pytest_cost_warning": cost_warning,
        "skipped_broad_pytest_commands": (
            [{"phase": phase, "command": command} for phase, command in broad]
            if broad and skip_broad_pytest
            else []
        ),
        "verification_lock_required": bool(broad and not skip_broad_pytest and not verification_lock),
        "phase_conflict": phase_conflict,
        "block_error": (
            BROAD_PYTEST_PHASE_CONFLICT_MESSAGE
            if phase_conflict
            else BROAD_PYTEST_LOCK_MESSAGE
            if broad and not skip_broad_pytest and not verification_lock
            else ""
        ),
    }


def format_broad_pytest_policy_lines(payload: dict[str, object]) -> list[str]:
    rows = [
        ("mode", payload.get("broad_pytest_policy_mode")),
        ("recommendation", payload.get("broad_pytest_recommendation")),
        ("cost warning", payload.get("broad_pytest_cost_warning")),
    ]
    lines = [f"- {label}: {value}" for label, value in rows if value]
    return ["Broad pytest policy:", *lines] if lines else []


def print_broad_pytest_policy(payload: dict[str, object]) -> None:
    for line in format_broad_pytest_policy_lines(payload):
        print(line)
    skipped = payload.get("skipped_broad_pytest_commands")
    if isinstance(skipped, list) and skipped:
        print("Skipped broad pytest commands:")
        for item in skipped:
            if isinstance(item, dict) and item.get("command"):
                print(f"- {item['command']}")
    if payload.get("verification_lock_required"):
        print("Verification lock required before broad pytest.")
    _print_cached_proofs("Reused broad pytest proof:", payload.get("reused_broad_pytest_proofs"))
    _print_cached_proofs(
        "Invalidated broad pytest proof:", payload.get("invalidated_broad_pytest_proofs")
    )


def _print_cached_proofs(label: str, value: object) -> None:
    if not isinstance(value, list) or not value:
        return
    print(label)
    for item in value:
        if isinstance(item, dict):
            print(f"- {item.get('command')} ({item.get('cache_path')})")


def should_block_broad_pytest_policy(broad_policy: dict[str, object], *, plan_only: bool) -> bool:
    return bool(broad_policy.get("phase_conflict") or (broad_policy["block_error"] and not plan_only))


def _git_bytes(repo_root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    return result.stdout + b"\n--stderr--\n" + result.stderr + f"\n--rc={result.returncode}--\n".encode()


def broad_pytest_fingerprint(repo_root: Path, changed_paths: list[str]) -> str:
    normalized = sorted(dict.fromkeys(path for path in changed_paths if path))
    digest = hashlib.sha256()
    digest.update(b"charness-broad-pytest-v1\n")
    digest.update(_git_bytes(repo_root, "rev-parse", "HEAD"))
    if normalized:
        digest.update(_git_bytes(repo_root, "diff", "--binary", "--", *normalized))
        digest.update(_git_bytes(repo_root, "diff", "--cached", "--binary", "--", *normalized))
    for relative in normalized:
        path = repo_root / relative
        digest.update(f"\n--path:{relative}--\n".encode())
        if not path.is_file():
            digest.update(b"<absent-or-non-file>")
            continue
        digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode())
    return digest.hexdigest()


def broad_pytest_cache_path(repo_root: Path) -> Path:
    return repo_root / BROAD_PYTEST_CACHE_RELATIVE


def _load_cache(repo_root: Path) -> dict[str, Any]:
    path = broad_pytest_cache_path(repo_root)
    if not path.is_file():
        return {"schema_version": 1, "records": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"schema_version": 1, "records": []}
    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        return {"schema_version": 1, "records": []}
    return payload


def broad_pytest_cache_report(repo_root: Path, *, command: str, fingerprint: str) -> dict[str, Any]:
    records = [
        record for record in _load_cache(repo_root)["records"]
        if isinstance(record, dict) and record.get("command") == command
    ]
    latest = records[-1] if records else None
    matching = next(
        (
            record for record in reversed(records)
            if record.get("fingerprint") == fingerprint and record.get("status") == "passed"
        ),
        None,
    )
    if matching:
        status = "reusable"
    elif latest:
        status = "invalidated"
    else:
        status = "missing"
    return {
        "cache_path": str(BROAD_PYTEST_CACHE_RELATIVE),
        "status": status,
        "fingerprint": fingerprint,
        "latest": latest,
        "match": matching,
    }


def record_broad_pytest_proof(
    repo_root: Path,
    *,
    command: str,
    fingerprint: str,
    elapsed_seconds: float,
    changed_paths: list[str],
) -> dict[str, Any]:
    path = broad_pytest_cache_path(repo_root)
    payload = _load_cache(repo_root)
    record = {
        "command": command,
        "fingerprint": fingerprint,
        "status": "passed",
        "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "elapsed_seconds": round(elapsed_seconds, 2),
        "changed_paths": sorted(dict.fromkeys(changed_paths)),
    }
    payload["schema_version"] = 1
    payload["records"] = (payload.get("records") or [])[-19:] + [record]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record
