from __future__ import annotations

import os
import platform
import re
from typing import Any

DEFAULT_RUNTIME_PROFILE = "default"
RUNTIME_PROFILE_ID_RE = re.compile(r"[^A-Za-z0-9_.-]+")


def normalize_runtime_profile(value: str | None) -> str:
    profile = (value or DEFAULT_RUNTIME_PROFILE).strip()
    return profile or DEFAULT_RUNTIME_PROFILE


def usable_cpu_count() -> int:
    """CPUs this process may actually run on, not the CPUs the box has.

    `os.cpu_count()` ignores affinity, so a run under `taskset`, a cpuset, or a
    container CPU limit reported the host's full count and filed its samples into
    the unrestricted profile. That is silent cross-contamination in the direction
    that matters: throttled runs are SLOW, so they inflate a fast profile's window
    and drag its median toward the bar, manufacturing a blocking false red on a
    machine where nothing regressed. Affinity is what the timings actually reflect,
    so it is what the profile keys on.

    `OSError` is caught alongside the missing-attribute case because affinity is the
    one input here that can be REFUSED, not merely absent: `os.cpu_count()` returns
    `None` at worst, while `sched_getaffinity` raises under a seccomp/LSM policy that
    blocks the syscall. Letting that escape would crash every gate that derives a
    profile over a detection detail -- strictly worse than what it replaced.
    """
    try:
        return len(os.sched_getaffinity(0)) or 1
    except (AttributeError, OSError):  # not Linux, or the kernel refused the query
        return os.cpu_count() or 1


def machine_runtime_profile() -> str:
    system = platform.system().lower() or "unknown-os"
    machine = platform.machine().lower() or "unknown-arch"
    cpu_count = usable_cpu_count()
    raw = f"local-{system}-{machine}-{cpu_count}cpu"
    return RUNTIME_PROFILE_ID_RE.sub("-", raw).strip("-") or f"local-{cpu_count}cpu"


def selected_runtime_profile(adapter_data: dict[str, Any], requested_profile: str | None) -> str:
    explicit = requested_profile or os.environ.get("CHARNESS_RUNTIME_PROFILE")
    if explicit:
        return normalize_runtime_profile(explicit)
    adapter_default = adapter_data.get("runtime_profile_default")
    if isinstance(adapter_default, str) and adapter_default.strip() and adapter_default.strip() != DEFAULT_RUNTIME_PROFILE:
        return adapter_default.strip()
    return machine_runtime_profile()


def profile_commands(payload: dict[str, Any], runtime_profile: str) -> dict[str, Any]:
    if runtime_profile == DEFAULT_RUNTIME_PROFILE:
        commands = payload.get("commands")
        if isinstance(commands, dict):
            return commands
    profiles = payload.get("profiles")
    if isinstance(profiles, dict):
        profile_entry = profiles.get(runtime_profile)
        if isinstance(profile_entry, dict):
            commands = profile_entry.get("commands")
            if isinstance(commands, dict):
                return commands
    return {}


def profile_budgets(adapter_data: dict[str, Any], runtime_profile: str) -> tuple[dict[str, int], list[str]]:
    profiles = adapter_data.get("runtime_budget_profiles")
    if isinstance(profiles, dict) and runtime_profile in profiles:
        profile_entry = profiles.get(runtime_profile)
        if isinstance(profile_entry, dict):
            budgets = profile_entry.get("budgets", {})
            if isinstance(budgets, dict):
                return budgets, []
        return {}, [f"runtime_budget_profiles.{runtime_profile}.budgets must be configured"]
    if runtime_profile == DEFAULT_RUNTIME_PROFILE:
        budgets = adapter_data.get("runtime_budgets", {}) or {}
        return budgets if isinstance(budgets, dict) else {}, []
    if isinstance(profiles, dict) and profiles:
        # The message carries the way out: this error blocks the pre-push path, and
        # the fix is a budgets block the gate can derive from the samples already
        # recorded for this profile. `--runtime-profile` is interpolated, not left to
        # the operator: without it the suggest path re-derives the profile from the
        # MACHINE, so pasting the command verbatim while investigating another
        # profile's failure yields a block sized from the wrong hardware and filed
        # under the right heading -- the false-red class this message exists to end.
        return {}, [
            f"runtime profile `{runtime_profile}` is not configured in runtime_budget_profiles"
            " (derive a starting block with `check_runtime_budget.py"
            f" --runtime-profile {runtime_profile} --suggest-budgets`)"
        ]
    if adapter_data.get("runtime_budgets"):
        budgets = adapter_data.get("runtime_budgets", {}) or {}
        return budgets if isinstance(budgets, dict) else {}, []
    return {}, []
