from __future__ import annotations

import re

ARM_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
CONFIG_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def _coerce_positive_int(value: object, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(field)
    if isinstance(value, int):
        if value < 1:
            raise ValueError(field)
        return value
    if isinstance(value, float):
        if not value.is_integer():
            raise ValueError(field)
        value = int(value)
        if value < 1:
            raise ValueError(field)
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError(field)
        try:
            parsed = int(text, 10)
        except ValueError as exc:
            raise ValueError(field) from exc
        if parsed < 1:
            raise ValueError(field)
        return parsed
    raise ValueError(field)


def validate_results_name(name: object) -> str:
    if not isinstance(name, str) or not name:
        raise ValueError("`name` must be a non-empty string")
    if not CONFIG_NAME_RE.fullmatch(name):
        raise ValueError(f"invalid config name: {name!r}")
    return name


def validate_run_config(config: object, *, require_results_name: bool = False) -> tuple[int, list[dict], object]:
    if not isinstance(config, dict):
        raise ValueError("config must be an object")
    if require_results_name:
        validate_results_name(config.get("name"))
    runs = _coerce_positive_int(config.get("runs", 4), "`runs` must be a positive integer")
    arms = config.get("arms")
    if not isinstance(arms, list) or not arms:
        raise ValueError("`arms` must be a non-empty list")
    default_spec = config.get("spec_path")
    seen: set[str] = set()
    validated_arms: list[dict] = []
    for arm in arms:
        if not isinstance(arm, dict):
            raise ValueError("each arm must be an object")
        name = arm.get("name", "")
        if not isinstance(name, str) or not ARM_NAME_RE.fullmatch(name):
            raise ValueError(f"invalid arm name: {name!r}")
        if name in seen:
            raise ValueError(f"duplicate arm name: {name!r}")
        seen.add(name)
        ref = arm.get("ref")
        if not isinstance(ref, str) or not ref.strip():
            raise ValueError(f"arm {name!r} must have a non-empty `ref`")
        spec_path = arm.get("spec_path") or default_spec
        if not isinstance(spec_path, str) or not spec_path.strip():
            raise ValueError(f"arm {name!r} must have a non-empty `spec_path`")
        invocation = arm.get("invocation")
        if invocation is not None and not isinstance(invocation, str):
            raise ValueError(f"arm {name!r} `invocation` must be a string")
        validated_arms.append(arm)
    return runs, validated_arms, default_spec
