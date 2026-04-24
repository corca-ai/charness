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


def machine_runtime_profile() -> str:
    system = platform.system().lower() or "unknown-os"
    machine = platform.machine().lower() or "unknown-arch"
    cpu_count = os.cpu_count() or 1
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
        return {}, [f"runtime profile `{runtime_profile}` is not configured in runtime_budget_profiles"]
    if adapter_data.get("runtime_budgets"):
        budgets = adapter_data.get("runtime_budgets", {}) or {}
        return budgets if isinstance(budgets, dict) else {}, []
    return {}, []
