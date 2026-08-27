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
)

PUBLICATION_MODES = frozenset({"audit-only", "direct-commit", "pull-request", "release", "manual"})
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
optional_int = _adapter_lib.optional_int
optional_string = _adapter_lib.optional_string
declared_fields_after_version_check = _adapter_lib.declared_fields_after_version_check
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
        "interview": {
            "max_questions": 15,
            "allow_provisional_local_fallback": False,
        },
        "closeout_publication": {
            "default_mode": "audit-only",
            "issue_closeout_carrier": "none",
            "require_draft_validation": True,
            "draft_validation_command_template": "",
            "require_post_publication_verify": True,
            "publish_requires_user_confirmation": True,
        },
        "auto_retro": {
            # Ordinary goals keep the deterministic Auto-Retro form checks. A
            # separate disposition reviewer is an explicit opt-in for a goal
            # whose own boundary warrants it, not a default completion ceremony.
            "disposition_floor": "deterministic-only",
            "allow_host_blocked_disposition_review_skip": True,
            "valid_dispositions": ["applied", "issue"],
            "allow_none_optout": True,
        },
        "scaffold": {
            "draft_active_frame_lines": list(_load_scaffold().DEFAULT_DRAFT_ACTIVE_FRAME_LINES),
            "execution_efficiency_context_path": None,
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


def _validate_interview(data: dict[str, Any], defaults: dict[str, Any], errors: list[str]) -> dict[str, Any]:
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


def _validate_scaffold(
    data: dict[str, Any], defaults: dict[str, Any], errors: list[str], repo_root: Path
) -> dict[str, Any]:
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
    context_path = optional_string(
        scaffold.get("execution_efficiency_context_path"),
        "scaffold.execution_efficiency_context_path",
        errors,
    )
    if context_path is not None:
        if not context_path.strip():
            errors.append("scaffold.execution_efficiency_context_path must not be empty")
        elif any(char in context_path for char in ("\x00", "\n", "\r")):
            errors.append(
                "scaffold.execution_efficiency_context_path must be a single-line repo-relative path"
            )
        else:
            relative_path = Path(context_path)
            if relative_path.is_absolute():
                errors.append("scaffold.execution_efficiency_context_path must be repo-relative")
            else:
                root = repo_root.resolve()
                candidate = repo_root / relative_path
                try:
                    resolved = candidate.resolve(strict=False)
                except (OSError, RuntimeError) as exc:
                    errors.append(
                        "scaffold.execution_efficiency_context_path could not be resolved: "
                        f"{exc}"
                    )
                else:
                    try:
                        resolved.relative_to(root)
                    except ValueError:
                        errors.append(
                            "scaffold.execution_efficiency_context_path must resolve within the repo"
                        )
                    else:
                        if not candidate.exists() or not candidate.is_file() or not resolved.is_file():
                            errors.append(
                                "scaffold.execution_efficiency_context_path must point to an existing regular file"
                            )
                        else:
                            policy["execution_efficiency_context_path"] = relative_path.as_posix()
    return policy


def validate_adapter_data(data: dict[str, Any], repo_root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = _defaults(repo_root)
    data = declared_fields_after_version_check(data, validated, errors)
    for field in ("repo", "language", "artifact_dir"):
        value = optional_string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value
    deploy_vocab = optional_string_list(data.get("discussion_deploy_vocab"), "discussion_deploy_vocab", errors)
    if deploy_vocab is not None:
        validated["discussion_deploy_vocab"] = deploy_vocab
    validated["interview"] = _validate_interview(data, validated, errors)
    validated["closeout_publication"] = _validate_closeout_publication(data, validated, errors)
    validated["auto_retro"] = _validate_auto_retro(data, validated, errors)
    validated["scaffold"] = _validate_scaffold(data, validated, errors, repo_root)
    if validated["closeout_publication"]["default_mode"] == "audit-only":
        warnings.append(
            "Achieve closeout publication default is "
            f"{validated['closeout_publication']['default_mode']}; publication claims must remain explicit."
        )
    return validated, errors, warnings


def load_adapter(repo_root: Path) -> dict[str, Any]:
    # `resolve_adapter_payload`, NOT a hand-written pair of branches around
    # `load_yaml_file`. The bare loader RAISES on a document the parser refuses and DISCARDS
    # the uninterpreted-line sink, so `parse_refused` and `declarations_dropped` were both
    # structurally dead for this skill's consumers.
    return _adapter_lib.resolve_adapter_payload(
        repo_root,
        candidates=ADAPTER_CANDIDATES,
        infer_defaults=_defaults,
        validate=validate_adapter_data,
        absent_warnings=lambda _data: [
            "No achieve adapter found. Using audit-only closeout publication defaults.",
            "Create .agents/achieve-adapter.yaml to declare publication and Auto-Retro policy.",
        ],
    )


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
