"""Pure queue decisions and verify-profile contract for merge trains."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping, Sequence

PASS = "pass"
FAIL = "fail"

#: Terminal train decisions mapped to process exit codes. A flat 0/1 made a
#: refused train (bad profile, duplicate branches, worktree infrastructure
#: failure) indistinguishable from a red train (verification failed, first bad
#: branch named) and from a transient requeue (main moved under the run).
#: Drivers need all three apart: fix-the-input, drop-the-branch, retry-as-is.
TRAIN_EXIT_CODES = {
    "land": 0,
    "land-prefix": 1,
    "requeue": 3,
    "refused": 2,
}
_ID_RE = re.compile(r"^[a-z][a-z0-9_.-]*$")
_DEFAULT_PROFILE: dict[str, Any] = {
    "version": 1,
    "commands": [
        {
            "id": "standing-pytest",
            "argv": [
                "python3",
                "scripts/gates_support/run_standing_pytest.py",
                "--repo-root",
                ".",
            ],
            "report": "junit-xml",
        }
    ],
    "known_failures": [],
}


class TrainError(ValueError):
    """A train input or integration step cannot be completed safely."""


def _payload_from_decision(
    decision: dict[str, Any],
    *,
    queue: Sequence[str],
    base_sha: str,
    main_sha: str,
    candidate_sha: str,
    attempts: list[dict[str, Any]],
) -> dict[str, Any]:
    requeued, red = decision["action"] == "requeue", decision["action"] == "land-prefix"
    return {
        "status": PASS if not requeued and not red else FAIL,
        "decision": decision["action"],
        "reason": decision.get("reason"),
        "main_sha_at_start": base_sha,
        "main_sha": main_sha,
        "candidate_sha": candidate_sha,
        "landed_branches": decision["landed_branches"],
        "requeue_branches": decision["requeue_branches"],
        "first_bad_branch": decision["first_bad_branch"],
        "verification_attempts": attempts,
        "queue": list(queue),
    }


def landing_review_plan(
    python: str,
    prepare_script: Path,
    review_script: Path,
    repo_root: Path,
    execution_runtime_root: Path,
    base_sha: str,
    landed_sha: str,
    run_id: str,
) -> dict[str, Any]:
    """Derive packet, lifecycle, and receipt paths for one landed range."""
    attempt_id = f"train-landing-{run_id}"
    record_root = execution_runtime_root / "landing-review"
    record_path, log_path = record_root / "launch-record.json", record_root / "review.log"
    return {
        "attempt_id": attempt_id,
        "record_path": record_path,
        "log_path": log_path,
        "record": {
            "schema_version": "charness.train_landing_review_trigger.v1",
            "base_sha": base_sha,
            "landed_sha": landed_sha,
            "packet_identity": None,
            "launch_record_path": str(record_path),
            "log_path": str(log_path),
        },
        "prepare_command": [
            python, str(prepare_script), "--repo-root", str(repo_root), "--range",
            f"{base_sha}..{landed_sha}", "--slug", attempt_id,
        ],
        "review_command": [
            python, str(review_script), "--repo-root", str(repo_root),
            "--scope", "merge-train landing", "--lens", "fresh-eye",
            "--attempt-id", attempt_id, "--packet-file",
        ],
    }


def stack_order(queue: Sequence[str]) -> tuple[str, ...]:
    """Preserve queue order and reject ambiguous duplicate branch entries."""
    branches = tuple(queue)
    if not branches:
        raise TrainError("the train queue must contain at least one branch")
    if len(set(branches)) != len(branches):
        raise TrainError("the train queue contains a duplicate branch")
    return branches


def next_bisect_prefix(green_prefix: int, red_prefix: int) -> int | None:
    """Choose the midpoint prefix while a verified green/red bracket remains."""
    if green_prefix < 0 or red_prefix <= green_prefix:
        raise ValueError("bisect bounds must satisfy 0 <= green < red")
    if red_prefix - green_prefix == 1:
        return None
    return (green_prefix + red_prefix) // 2


def decide_next_action(
    queue: Sequence[str],
    outcomes: Mapping[int, bool],
    *,
    main_at_start: str,
    main_now: str,
) -> dict[str, Any]:
    """Pure next-action decision over explicit prefix results and main identity."""
    branches = stack_order(queue)
    if main_now != main_at_start:
        return {
            "action": "requeue",
            "reason": "main-moved",
            "land_count": 0,
            "first_bad_branch": None,
            "landed_branches": [],
            "requeue_branches": list(branches),
        }
    full = len(branches)
    observed = sorted((index, good) for index, good in outcomes.items() if 0 <= index <= full)
    for position, (_index, good) in enumerate(observed):
        if not good and any(later_good for _, later_good in observed[position + 1 :]):
            raise TrainError(
                "prefix outcomes are non-monotonic; the first bad branch "
                "cannot be bisected safely"
            )
    if outcomes.get(full) is True:
        return {
            "action": "land",
            "reason": None,
            "land_count": full,
            "first_bad_branch": None,
            "landed_branches": list(branches),
            "requeue_branches": [],
        }
    green = [index for index, good in outcomes.items() if good and 0 <= index < full]
    low = max(green, default=0)
    red = sorted(index for index, good in outcomes.items() if not good and low < index <= full)
    high = red[0] if red else full
    prefix = next_bisect_prefix(low, high)
    if prefix is not None:
        return {
            "action": "verify-prefix",
            "reason": None,
            "prefix_count": prefix,
            "land_count": low,
            "first_bad_branch": None,
            "landed_branches": list(branches[:low]),
            "requeue_branches": list(branches[low:]),
        }
    if high != low + 1 or outcomes.get(high) is not False:
        raise TrainError("the red train has no verified green/red bisect bracket")
    return {
        "action": "land-prefix",
        "reason": "verification-failed",
        "land_count": low,
        "first_bad_branch": branches[high - 1],
        "landed_branches": list(branches[:low]),
        "requeue_branches": list(branches[low:]),
    }


def derive_landing_review_routing(
    findings: Sequence[Mapping[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Route P1 findings to the next unit and P2/P3 findings to the batch."""
    if not isinstance(findings, Sequence) or isinstance(findings, (str, bytes)):
        raise TrainError("landing review findings must be a sequence")
    routes: dict[str, list[dict[str, Any]]] = {
        "next_unit": [],
        "batch": [],
        "unrouted": [],
    }
    for finding in findings:
        if not isinstance(finding, Mapping):
            raise TrainError("each landing review finding must be a mapping")
        severity = finding.get("severity")
        if not isinstance(severity, str):
            destination = "unrouted"
        else:
            destination = {
                "P1": "next_unit",
                "P2": "batch",
                "P3": "batch",
            }.get(severity.strip().upper(), "unrouted")
        routes[destination].append(dict(finding))
    return routes


def exit_code_for_decision(decision: Mapping[str, Any]) -> int:
    """Map a terminal train decision to a process exit code.

    `land` is success. `land-prefix` is verification failure with a named first
    bad branch. `refused` is a loader/input/infrastructure error -- the caller
    must fix something before retrying, mirroring the worktree commands' 2 for
    non-pass, non-warning outcomes. `requeue` is transient (main moved): the
    same queue is worth retrying, which a shared code with `land-prefix` would
    hide from a driver. Unknown actions fail closed: inventing a code here
    would let a new decision read as a settled one.
    """
    action = decision.get("action") if isinstance(decision, Mapping) else None
    if action not in TRAIN_EXIT_CODES:
        raise TrainError(f"unknown train decision {action!r}; cannot map to an exit code")
    return TRAIN_EXIT_CODES[action]


def default_verify_profile() -> dict[str, Any]:
    """Return a fresh copy of the built-in repo standing profile."""
    return {
        "version": 1,
        "commands": [
            dict(command, argv=list(command["argv"]))
            for command in _DEFAULT_PROFILE["commands"]
        ],
        "known_failures": [],
    }


def _validate_profile_commands(
    commands: object, errors: list[str]
) -> tuple[set[str], dict[str, object]]:
    if not isinstance(commands, list) or not commands:
        errors.append("profile.commands must be a non-empty list")
        commands = []
    ids: set[str] = set()
    reports: dict[str, object] = {}
    for index, entry in enumerate(commands):
        label = f"profile.commands[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be a mapping")
            continue
        if set(entry) - {"id", "argv", "report"}:
            errors.append(f"{label} has unknown keys")
        command_id = entry.get("id")
        if not isinstance(command_id, str) or not _ID_RE.fullmatch(command_id):
            errors.append(f"{label}.id must match {_ID_RE.pattern}")
            continue
        if command_id in ids:
            errors.append(f"{label}.id {command_id!r} is duplicated")
        ids.add(command_id)
        argv = entry.get("argv")
        if not isinstance(argv, list) or not argv or any(
            not isinstance(arg, str) or not arg for arg in argv
        ):
            errors.append(f"{label}.argv must be a non-empty list of non-empty strings")
        report = entry.get("report", "exit-code")
        if not isinstance(report, str) or report not in {"exit-code", "junit-xml"}:
            errors.append(f"{label}.report must be 'exit-code' or 'junit-xml'")
        reports[command_id] = report
    return ids, reports


def _validate_known_failures(
    baseline: object,
    ids: set[str],
    reports: Mapping[str, object],
    errors: list[str],
) -> None:
    if not isinstance(baseline, list):
        errors.append("profile.known_failures must be a list")
        baseline = []
    seen: set[tuple[str, str]] = set()
    for index, entry in enumerate(baseline):
        label = f"profile.known_failures[{index}]"
        if not isinstance(entry, dict) or set(entry) != {"command_id", "testcase"}:
            errors.append(f"{label} must contain command_id and testcase")
            continue
        command_id, testcase = entry.get("command_id"), entry.get("testcase")
        valid_command = (
            not isinstance(command_id, str)
            or command_id not in ids
            or reports.get(command_id) != "junit-xml"
        )
        if valid_command:
            errors.append(f"{label}.command_id must name a junit-xml command")
        if not isinstance(testcase, str) or not testcase.strip():
            errors.append(f"{label}.testcase must be a non-empty string")
            continue
        if isinstance(command_id, str):
            key = (command_id, testcase)
            if key in seen:
                errors.append(f"{label} duplicates a known failure")
            seen.add(key)


def validate_verify_profile(profile: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(profile, dict):
        return ["profile root must be a mapping"]
    if type(profile.get("version")) is not int or profile.get("version") != 1:
        errors.append("profile.version must be integer 1")
    unknown = set(profile) - {"version", "commands", "known_failures"}
    if unknown:
        errors.append(f"profile has unknown keys: {', '.join(sorted(map(str, unknown)))}")
    ids, reports = _validate_profile_commands(profile.get("commands"), errors)
    baseline = profile.get("known_failures", [])
    _validate_known_failures(baseline, ids, reports, errors)
    return errors
