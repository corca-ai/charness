from __future__ import annotations

import shlex

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


def is_broad_pytest_command(command: str) -> bool:
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    if not tokens:
        return False
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


def should_block_broad_pytest_policy(broad_policy: dict[str, object], *, plan_only: bool) -> bool:
    return bool(broad_policy.get("phase_conflict") or (broad_policy["block_error"] and not plan_only))
