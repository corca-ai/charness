"""Adapter policy for Goal Draft planning.

Only planning inputs live here: discussion vocabulary and the bounded
interview policy. Goal Draft lifecycle and closeout policy are intentionally
not adapter concerns.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

ADAPTER_CANDIDATES = (Path(".agents/achieve-adapter.yaml"),)
_KNOWN_FIELDS = frozenset(
    {"version", "repo", "language", "artifact_dir", "discussion_deploy_vocab", "interview"}
)

_ADAPTER_LIB = None


def _load_adapter_lib():
    global _ADAPTER_LIB
    if _ADAPTER_LIB is not None:
        return _ADAPTER_LIB
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "scripts" / "adapter_lib.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("adapter_lib", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            _ADAPTER_LIB = module
            return module
    raise ImportError("scripts/adapter_lib.py not found")


_adapter_lib = _load_adapter_lib()
normalize_adapter_result = _adapter_lib.normalize_adapter_result
optional_bool = _adapter_lib.optional_bool
optional_int = _adapter_lib.optional_int
optional_string = _adapter_lib.optional_string
optional_string_list = _adapter_lib.optional_string_list
declared_fields_after_version_check = _adapter_lib.declared_fields_after_version_check


def _defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "artifact_dir": "charness-artifacts/goals",
        "discussion_deploy_vocab": [],
        "interview": {
            "max_questions": 15,
            "allow_provisional_local_fallback": False,
        },
    }


def _mapping(value: Any, field: str, errors: list[str]) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        errors.append(f"{field} must be a mapping")
        return {}
    return value


def _validate_interview(
    data: dict[str, Any], defaults: dict[str, Any], errors: list[str]
) -> dict[str, Any]:
    policy = dict(defaults["interview"])
    interview = _mapping(data.get("interview"), "interview", errors)
    max_questions = optional_int(
        interview.get("max_questions"), "interview.max_questions", errors, minimum=1
    )
    if max_questions is not None:
        policy["max_questions"] = max_questions
    fallback = optional_bool(
        interview.get("allow_provisional_local_fallback"),
        "interview.allow_provisional_local_fallback",
        errors,
    )
    if fallback is not None:
        policy["allow_provisional_local_fallback"] = fallback
    return policy


def validate_adapter_data(
    data: dict[str, Any], repo_root: Path
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = _defaults(repo_root)
    data = declared_fields_after_version_check(data, validated, errors)
    unknown = sorted(set(data) - _KNOWN_FIELDS)
    if unknown:
        errors.append("unknown field(s): " + ", ".join(unknown))
    for field in ("repo", "language", "artifact_dir"):
        value = optional_string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value
    deploy_vocab = optional_string_list(
        data.get("discussion_deploy_vocab"), "discussion_deploy_vocab", errors
    )
    if deploy_vocab is not None:
        validated["discussion_deploy_vocab"] = deploy_vocab
    validated["interview"] = _validate_interview(data, validated, errors)
    return validated, errors, warnings


def load_adapter(repo_root: Path) -> dict[str, Any]:
    payload = _adapter_lib.resolve_adapter_payload(
        repo_root,
        candidates=ADAPTER_CANDIDATES,
        infer_defaults=_defaults,
        validate=validate_adapter_data,
        absent_warnings=lambda _data: [
            "No achieve adapter found. Using default planning and interview policy."
        ],
    )
    return normalize_adapter_result(payload, skill_id="achieve")


def resolve_discussion_deploy_vocab(repo_root: Path) -> list[str]:
    """Return adapter-provided deploy vocabulary, or the portable default input."""
    vocab = (load_adapter(repo_root).get("data") or {}).get("discussion_deploy_vocab")
    return list(vocab) if isinstance(vocab, list) else []


def interview_policy_report(repo_root: Path) -> dict[str, Any]:
    adapter = load_adapter(repo_root)
    interview = adapter["data"]["interview"]
    return {
        "found": adapter["found"],
        "valid": adapter["valid"],
        "path": adapter["path"],
        "max_questions": interview["max_questions"],
        "allow_provisional_local_fallback": interview[
            "allow_provisional_local_fallback"
        ],
        "errors": adapter["errors"],
        "warnings": adapter["warnings"],
    }
