"""Achieve adapter policy for closeout publication and Auto-Retro disposition.

The adapter is optional. Missing adapters use conservative audit-only defaults;
found-but-invalid adapters fail closeout so a repo cannot silently ignore a bad
publication policy.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

ADAPTER_CANDIDATES = (
    Path(".agents/achieve-adapter.yaml"),
    Path(".codex/achieve-adapter.yaml"),
    Path(".claude/achieve-adapter.yaml"),
    Path("docs/achieve-adapter.yaml"),
    Path("achieve-adapter.yaml"),
)

PUBLICATION_MODES = frozenset({"audit-only", "handoff-only", "direct-commit", "pull-request", "release", "manual"})
ISSUE_CLOSEOUT_CARRIERS = frozenset({"none", "direct-commit", "pull-request", "release", "manual"})
DISPOSITION_FLOORS = frozenset({"review-required", "deterministic-only"})
VALID_DISPOSITIONS = frozenset({"applied", "issue"})


def _load_adapter_lib():
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "scripts" / "adapter_lib.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("adapter_lib", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scripts/adapter_lib.py not found")


def _defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "artifact_dir": "charness-artifacts/goals",
        "closeout_publication": {
            "default_mode": "audit-only",
            "issue_closeout_carrier": "none",
            "require_draft_validation": True,
            "draft_validation_command_template": "",
            "require_post_publication_verify": True,
            "publish_requires_user_confirmation": True,
        },
        "auto_retro": {
            "disposition_floor": "review-required",
            "allow_host_blocked_disposition_review_skip": True,
            "valid_dispositions": ["applied", "issue"],
            "allow_none_optout": True,
        },
    }


def _string(value: Any, field: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        errors.append(f"{field} must be a string")
        return None
    return value


def _bool(value: Any, field: str, errors: list[str]) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        errors.append(f"{field} must be a boolean")
        return None
    return value


def _string_list(value: Any, field: str, errors: list[str]) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{field} must be a list of strings")
        return None
    return list(value)


def _mapping(value: Any, field: str, errors: list[str]) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        errors.append(f"{field} must be a mapping")
        return {}
    return value


def _validate_closeout_publication(data: dict[str, Any], defaults: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    policy = dict(defaults["closeout_publication"])
    closeout = _mapping(data.get("closeout_publication"), "closeout_publication", errors)
    mode = _string(closeout.get("default_mode"), "closeout_publication.default_mode", errors)
    if mode is not None:
        if mode not in PUBLICATION_MODES:
            errors.append(
                "closeout_publication.default_mode must be one of: "
                + ", ".join(sorted(PUBLICATION_MODES))
            )
        else:
            policy["default_mode"] = mode
    carrier = _string(closeout.get("issue_closeout_carrier"), "closeout_publication.issue_closeout_carrier", errors)
    if carrier is not None:
        if carrier not in ISSUE_CLOSEOUT_CARRIERS:
            errors.append(
                "closeout_publication.issue_closeout_carrier must be one of: "
                + ", ".join(sorted(ISSUE_CLOSEOUT_CARRIERS))
            )
        else:
            policy["issue_closeout_carrier"] = carrier
    for field in ("require_draft_validation", "require_post_publication_verify", "publish_requires_user_confirmation"):
        value = _bool(closeout.get(field), f"closeout_publication.{field}", errors)
        if value is not None:
            policy[field] = value
    template = _string(
        closeout.get("draft_validation_command_template"),
        "closeout_publication.draft_validation_command_template",
        errors,
    )
    if template is not None:
        policy["draft_validation_command_template"] = template
    if policy["issue_closeout_carrier"] == "direct-commit" and policy["require_draft_validation"]:
        required = ("validate-closeout-draft", "--carrier direct-commit", "--commit-message-file")
        missing = [needle for needle in required if needle not in policy["draft_validation_command_template"]]
        if missing:
            errors.append(
                "closeout_publication.draft_validation_command_template for direct-commit "
                "must include " + ", ".join(missing)
            )
    return policy


def _validate_auto_retro(data: dict[str, Any], defaults: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    policy = dict(defaults["auto_retro"])
    auto = _mapping(data.get("auto_retro"), "auto_retro", errors)
    floor = _string(auto.get("disposition_floor"), "auto_retro.disposition_floor", errors)
    if floor is not None:
        if floor not in DISPOSITION_FLOORS:
            errors.append("auto_retro.disposition_floor must be one of: " + ", ".join(sorted(DISPOSITION_FLOORS)))
        else:
            policy["disposition_floor"] = floor
    for field in ("allow_host_blocked_disposition_review_skip", "allow_none_optout"):
        value = _bool(auto.get(field), f"auto_retro.{field}", errors)
        if value is not None:
            policy[field] = value
    dispositions = _string_list(auto.get("valid_dispositions"), "auto_retro.valid_dispositions", errors)
    if dispositions is not None:
        unknown = sorted(set(dispositions) - VALID_DISPOSITIONS)
        if unknown:
            errors.append("auto_retro.valid_dispositions contains unknown item(s): " + ", ".join(unknown))
        elif not dispositions:
            errors.append("auto_retro.valid_dispositions must not be empty")
        else:
            policy["valid_dispositions"] = dispositions
    return policy


def validate_adapter_data(data: dict[str, Any], repo_root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = _defaults(repo_root)
    version = data.get("version")
    if version is not None:
        if isinstance(version, int):
            validated["version"] = version
        else:
            errors.append("version must be an integer")
    for field in ("repo", "language", "artifact_dir"):
        value = _string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value
    validated["closeout_publication"] = _validate_closeout_publication(data, validated, errors)
    validated["auto_retro"] = _validate_auto_retro(data, validated, errors)
    if validated["closeout_publication"]["default_mode"] in {"audit-only", "handoff-only"}:
        warnings.append(
            "Achieve closeout publication default is "
            f"{validated['closeout_publication']['default_mode']}; publication claims must remain explicit."
        )
    return validated, errors, warnings


def find_adapter(repo_root: Path) -> Path | None:
    for candidate in ADAPTER_CANDIDATES:
        path = repo_root / candidate
        if path.is_file():
            return path
    return None


def load_adapter(repo_root: Path) -> dict[str, Any]:
    searched_paths = [str((repo_root / candidate).resolve()) for candidate in ADAPTER_CANDIDATES]
    adapter_path = find_adapter(repo_root)
    if adapter_path is None:
        return {
            "found": False,
            "valid": True,
            "path": None,
            "data": _defaults(repo_root),
            "errors": [],
            "warnings": [
                "No achieve adapter found. Using audit-only closeout publication defaults.",
                "Create .agents/achieve-adapter.yaml to declare publication and Auto-Retro policy.",
            ],
            "searched_paths": searched_paths,
        }
    adapter_lib = _load_adapter_lib()
    raw = adapter_lib.load_yaml_file(adapter_path)
    raw_data = raw if isinstance(raw, dict) else {}
    warnings: list[str] = []
    canonical = repo_root / ".agents" / "achieve-adapter.yaml"
    if not isinstance(raw, dict):
        warnings.append("Adapter file did not contain a mapping. Using inferred defaults.")
    if adapter_path.resolve() != canonical.resolve():
        warnings.append(f"Adapter path is a compatibility fallback. Prefer {canonical}.")
    data, errors, extra_warnings = validate_adapter_data(raw_data, repo_root)
    warnings.extend(extra_warnings)
    return {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }


def closeout_policy_report(repo_root: Path) -> dict[str, Any]:
    adapter = load_adapter(repo_root)
    data = adapter["data"]
    publication = data["closeout_publication"]
    auto_retro = data["auto_retro"]
    return {
        "found": adapter["found"],
        "valid": adapter["valid"],
        "path": adapter["path"],
        "publication_default": publication["default_mode"],
        "issue_closeout_carrier": publication["issue_closeout_carrier"],
        "draft_validation_required": publication["require_draft_validation"],
        "post_publication_verify_required": publication["require_post_publication_verify"],
        "publish_requires_user_confirmation": publication["publish_requires_user_confirmation"],
        "auto_retro_disposition_floor": auto_retro["disposition_floor"],
        "auto_retro_valid_dispositions": auto_retro["valid_dispositions"],
        "auto_retro_allow_none_optout": auto_retro["allow_none_optout"],
        "errors": adapter["errors"],
        "warnings": adapter["warnings"],
    }
