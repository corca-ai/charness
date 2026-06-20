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
optional_bool = _adapter_lib.optional_bool
optional_string = _adapter_lib.optional_string
optional_string_list = _adapter_lib.optional_string_list

_scaffold = None


def _load_scaffold():
    global _scaffold
    if _scaffold is not None:
        return _scaffold
    spec = importlib.util.spec_from_file_location(
        "goal_artifact_scaffold",
        Path(__file__).resolve().parent / "goal_artifact_scaffold.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("goal_artifact_scaffold.py not found beside achieve_adapter_policy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _scaffold = module
    return module


def _defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "artifact_dir": "charness-artifacts/goals",
        # Consumer-axis deploy/irreversible-side-effect detection vocabulary for the
        # pre-activation discussion gate. Empty -> the portable English default
        # (`goal_artifact_discussion._DEFAULT_DEPLOY_VOCAB`); a consumer declares its
        # own deploy verbs so charness does not hardcode one consumer's boundary words.
        "discussion_deploy_vocab": [],
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
        "scaffold": {
            "draft_active_frame_lines": list(_load_scaffold().DEFAULT_DRAFT_ACTIVE_FRAME_LINES),
        },
    }


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
    mode = optional_string(closeout.get("default_mode"), "closeout_publication.default_mode", errors)
    if mode is not None:
        if mode not in PUBLICATION_MODES:
            errors.append(
                "closeout_publication.default_mode must be one of: "
                + ", ".join(sorted(PUBLICATION_MODES))
            )
        else:
            policy["default_mode"] = mode
    carrier = optional_string(closeout.get("issue_closeout_carrier"), "closeout_publication.issue_closeout_carrier", errors)
    if carrier is not None:
        if carrier not in ISSUE_CLOSEOUT_CARRIERS:
            errors.append(
                "closeout_publication.issue_closeout_carrier must be one of: "
                + ", ".join(sorted(ISSUE_CLOSEOUT_CARRIERS))
            )
        else:
            policy["issue_closeout_carrier"] = carrier
    for field in ("require_draft_validation", "require_post_publication_verify", "publish_requires_user_confirmation"):
        value = optional_bool(closeout.get(field), f"closeout_publication.{field}", errors)
        if value is not None:
            policy[field] = value
    template = optional_string(
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
    floor = optional_string(auto.get("disposition_floor"), "auto_retro.disposition_floor", errors)
    if floor is not None:
        if floor not in DISPOSITION_FLOORS:
            errors.append("auto_retro.disposition_floor must be one of: " + ", ".join(sorted(DISPOSITION_FLOORS)))
        else:
            policy["disposition_floor"] = floor
    for field in ("allow_host_blocked_disposition_review_skip", "allow_none_optout"):
        value = optional_bool(auto.get(field), f"auto_retro.{field}", errors)
        if value is not None:
            policy[field] = value
    dispositions = optional_string_list(auto.get("valid_dispositions"), "auto_retro.valid_dispositions", errors)
    if dispositions is not None:
        unknown = sorted(set(dispositions) - VALID_DISPOSITIONS)
        if unknown:
            errors.append("auto_retro.valid_dispositions contains unknown item(s): " + ", ".join(unknown))
        elif not dispositions:
            errors.append("auto_retro.valid_dispositions must not be empty")
        else:
            policy["valid_dispositions"] = dispositions
    return policy


def _validate_scaffold(data: dict[str, Any], defaults: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    policy = dict(defaults["scaffold"])
    scaffold = _mapping(data.get("scaffold"), "scaffold", errors)
    lines = optional_string_list(scaffold.get("draft_active_frame_lines"), "scaffold.draft_active_frame_lines", errors)
    if lines is not None:
        if not lines:
            errors.append("scaffold.draft_active_frame_lines must not be empty")
        elif any(line.startswith("## ") for line in lines):
            errors.append("scaffold.draft_active_frame_lines must not contain markdown headings")
        else:
            policy["draft_active_frame_lines"] = lines
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
        value = optional_string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value
    deploy_vocab = optional_string_list(data.get("discussion_deploy_vocab"), "discussion_deploy_vocab", errors)
    if deploy_vocab is not None:
        validated["discussion_deploy_vocab"] = deploy_vocab
    validated["closeout_publication"] = _validate_closeout_publication(data, validated, errors)
    validated["auto_retro"] = _validate_auto_retro(data, validated, errors)
    validated["scaffold"] = _validate_scaffold(data, validated, errors)
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
    raw = _adapter_lib.load_yaml_file(adapter_path)
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


def resolve_discussion_deploy_vocab(repo_root: Path) -> list[str]:
    """The consumer-axis deploy vocabulary for the pre-activation discussion gate,
    or ``[]`` for the portable English default. Graceful: a missing or invalid
    achieve adapter resolves to ``[]`` so the discussion gate never fails on adapter
    state (the default preserves behavior)."""
    vocab = (load_adapter(repo_root).get("data") or {}).get("discussion_deploy_vocab")
    return list(vocab) if isinstance(vocab, list) else []


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
