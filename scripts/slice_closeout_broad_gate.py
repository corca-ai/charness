from __future__ import annotations

import shlex

BROAD_PYTEST_LOCK_MESSAGE = (
    "broad pytest closeout requires an explicit verification lock; rerun with "
    "--verification-lock after recording that the mutation set is locked, or use "
    "--skip-broad-pytest for a pre-lock rehearsal"
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
    planned = ordinary if broad and skip_broad_pytest else command_plan
    return {
        "command_plan": planned,
        "broad_pytest_commands": [{"phase": phase, "command": command} for phase, command in broad],
        "skipped_broad_pytest_commands": (
            [{"phase": phase, "command": command} for phase, command in broad]
            if broad and skip_broad_pytest
            else []
        ),
        "verification_lock_required": bool(broad and not skip_broad_pytest and not verification_lock),
        "block_error": (
            BROAD_PYTEST_LOCK_MESSAGE if broad and not skip_broad_pytest and not verification_lock else ""
        ),
    }
