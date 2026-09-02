#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.adapter_lib import (  # noqa: E402
    declared_fields_after_version_check,
    list_field_state,
    load_yaml_file_report,
    optional_string,
    parse_failure_error,
    uninterpreted_warnings,
)
from scripts.adapters.adapter_field_application import apply_optional_fields  # noqa: E402
from scripts.adapters.adapter_version_verdict import declarations_unhonored  # noqa: E402
from scripts.artifacts.artifact_naming_lib import RECORD_PATTERN  # noqa: E402

KIND_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
BUILTIN_KINDS = frozenset({"issues", "path"})

ADAPTER_CANDIDATES = (
    Path(".agents/announcement-adapter.yaml"),
)
STRING_FIELDS = (
    "repo",
    "language",
    "output_dir",
    "preset_id",
    "preset_version",
    "customized_from",
    "product_name",
    "delivery_kind",
    "delivery_target",
    "release_notes_path",
    "post_command_template",
    "delivery_capability",
    "format_rules_path",
    "post_delivery_readback_probe",
)
LIST_FIELDS = ("sections", "audience_tags", "omission_lenses")
INT_FIELDS = ("message_size_limit",)
PUBLIC_BODY_SHAPES = frozenset({"chat_update", "release_notes"})
ARTIFACT_FILENAME = "latest.md"
ARTIFACT_CLASS = "history"
RECORD_FILENAME = "announcements.jsonl"

VALID_DELIVERY_ROLES = {"single", "parent", "thread_reply"}

# Canonical delivery-kind vocabulary. Shared with record_announcement.py's
# --delivery-kind CLI choices so a self-attested record can only ever name a
# kind this adapter contract recognizes (case-normalized first).
DELIVERY_KINDS = ("none", "release-notes", "human-backend")


def normalize_delivery_kind(value: str) -> str:
    return (value or "").strip().lower()


def _validate_outputs(value: Any, errors: list[str]) -> list[dict[str, Any]] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        errors.append("outputs must be a list of output specs")
        return None
    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(value):
        if not isinstance(raw, dict):
            errors.append(f"outputs[{index}] must be a mapping")
            continue
        output_id = raw.get("id")
        if not isinstance(output_id, str) or not output_id:
            errors.append(f"outputs[{index}].id must be a non-empty string")
            continue
        if output_id in seen_ids:
            errors.append(f"outputs[{index}].id `{output_id}` is duplicated")
            continue
        seen_ids.add(output_id)
        audience_tags = raw.get("audience_tags", [])
        if not isinstance(audience_tags, list) or not all(isinstance(item, str) for item in audience_tags):
            errors.append(f"outputs[{index}].audience_tags must be a list of strings")
            continue
        delivery_role = raw.get("delivery_role", "single")
        if delivery_role not in VALID_DELIVERY_ROLES:
            errors.append(
                f"outputs[{index}].delivery_role must be one of: {', '.join(sorted(VALID_DELIVERY_ROLES))}"
            )
            continue
        normalized.append(
            {
                "id": output_id,
                "audience_tags": list(audience_tags),
                "delivery_role": delivery_role,
            }
        )
    return normalized


def _validate_in_progress_sources(value: Any, errors: list[str]) -> list[dict[str, Any]] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        errors.append("in_progress_sources must be a list of source specs")
        return None
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(value):
        if not isinstance(raw, dict):
            errors.append(f"in_progress_sources[{index}] must be a mapping")
            continue
        kind = raw.get("kind")
        if not isinstance(kind, str) or not KIND_PATTERN.match(kind):
            errors.append(
                f"in_progress_sources[{index}].kind must be a lowercase identifier matching {KIND_PATTERN.pattern}"
            )
            continue
        entry: dict[str, Any] = {"kind": kind}
        path_value = raw.get("path")
        if isinstance(path_value, str) and path_value:
            entry["path"] = path_value
        elif kind == "path":
            errors.append(f"in_progress_sources[{index}] of kind=path requires a non-empty `path`")
            continue
        summary = raw.get("summary")
        if isinstance(summary, str) and summary:
            entry["summary"] = summary
        query = raw.get("query")
        if isinstance(query, str) and query:
            entry["query"] = query
        if kind not in BUILTIN_KINDS and not (entry.get("path") or entry.get("summary") or entry.get("query")):
            errors.append(
                f"in_progress_sources[{index}] of host-defined kind `{kind}` requires at least one of: path, summary, query"
            )
            continue
        normalized.append(entry)
    return normalized


def _artifact_path(output_dir: str) -> str:
    return str(Path(output_dir) / ARTIFACT_FILENAME)


def _record_path() -> str:
    return str(Path(".charness") / "announcement" / RECORD_FILENAME)


def _record_artifact_pattern(output_dir: str) -> str:
    return str(Path(output_dir) / RECORD_PATTERN)


def _bootstrap_expectations(data: dict[str, Any]) -> dict[str, str]:
    delivery_note = (
        "Delivery stays draft-only until the adapter declares a backend and the user confirms posting."
        if data["delivery_kind"] == "none"
        else "Delivery still requires explicit user confirmation even when the adapter declares a backend."
    )
    return {
        "artifact_path": _artifact_path(data["output_dir"]),
        "record_path": _record_path(),
        "what_you_get_after_one_run": "A human-facing draft that explains recent repo value in a stable shape.",
        "artifact_meaning": "The markdown artifact is the visible announcement draft; the hidden JSONL record tracks finalized heads across runs.",
        "what_this_does_not_do": delivery_note,
    }


def _field_state_map(raw_data: dict[str, Any]) -> dict[str, str]:
    return {
        "audience_tags": list_field_state(raw_data, "audience_tags"),
        "omission_lenses": list_field_state(raw_data, "omission_lenses"),
        "outputs": list_field_state(raw_data, "outputs"),
        "in_progress_sources": list_field_state(raw_data, "in_progress_sources"),
    }


def infer_announcement_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "product_name": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/announcement",
        "artifact_class": ARTIFACT_CLASS,
        "sections": ["Highlights", "Changes", "Fixes"],
        "audience_tags": [],
        "omission_lenses": [],
        "in_progress_sources": [],
        "delivery_kind": "none",
        "delivery_target": "",
        "release_notes_path": "",
        "post_command_template": "",
        "delivery_capability": "",
        "format_rules_path": "",
        "post_delivery_readback_probe": "",
        "message_size_limit": 0,
        "public_body_shape": "chat_update",
        "outputs": [],
    }


def _apply_simple_fields(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str]
) -> dict[str, Any]:
    """Returns the declared fields the REST of this validator may honor.

    The return value is the containment: on a refused version it is empty, and the
    structured/delivery passes that run after this one must read it rather than the
    caller's original `data`, or they would honor a delivery seam declared under a
    schema no reader here speaks.
    """
    data = declared_fields_after_version_check(data, validated, errors)
    apply_optional_fields(data, validated, errors, string_fields=STRING_FIELDS, list_fields=LIST_FIELDS)
    # INT_FIELDS keeps its own loop: its refusal carries field-specific operator
    # guidance ("0 disables splitting") that the shared vocabulary's generic message
    # would drop.
    for field in INT_FIELDS:
        raw_value = data.get(field)
        if raw_value is None:
            continue
        if isinstance(raw_value, bool) or not isinstance(raw_value, int) or raw_value < 0:
            errors.append(f"{field} must be a non-negative integer (0 disables splitting)")
            continue
        validated[field] = raw_value
    return data


def _apply_structured_fields(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str]
) -> None:
    outputs = _validate_outputs(data.get("outputs"), errors)
    if outputs is not None:
        validated["outputs"] = outputs
    in_progress_sources = _validate_in_progress_sources(data.get("in_progress_sources"), errors)
    if in_progress_sources is not None:
        validated["in_progress_sources"] = in_progress_sources


def _delivery_warnings(
    data: dict[str, Any], validated: dict[str, Any], warnings: list[str], errors: list[str]
) -> None:
    if validated["delivery_kind"] not in DELIVERY_KINDS:
        errors.append(f"delivery_kind must be one of: {', '.join(DELIVERY_KINDS)}")
    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")
    if not validated["audience_tags"]:
        warnings.append("No audience_tags configured; drafts will omit audience prefixes.")
    if validated["delivery_kind"] == "release-notes" and not validated["release_notes_path"]:
        warnings.append("release-notes delivery_kind is set but release_notes_path is empty.")
    if validated["delivery_kind"] == "human-backend" and not validated["post_command_template"]:
        warnings.append("human-backend delivery_kind is set but post_command_template is empty.")
    if validated["delivery_kind"] == "human-backend" and not validated["delivery_capability"]:
        warnings.append("human-backend delivery_kind is set but delivery_capability is empty.")
    _validate_chaining_contract(validated, warnings)


def _validate_chaining_contract(validated: dict[str, Any], warnings: list[str]) -> None:
    contract = delivery_contract(validated)
    for issue in contract["blocking_issues"]:
        warnings.append(issue)


def delivery_contract(data: dict[str, Any]) -> dict[str, Any]:
    outputs = data.get("outputs") or []
    has_thread_reply = any(
        isinstance(output, dict) and output.get("delivery_role") == "thread_reply"
        for output in outputs
    )
    has_parent = any(
        isinstance(output, dict) and output.get("delivery_role") == "parent"
        for output in outputs
    )
    template = data.get("post_command_template") or ""
    has_handle_placeholder = "{parent_delivery_handle}" in template or "{parent_delivery_handle_q}" in template
    thread_replies_without_prior_parent = [
        output.get("id")
        for index, output in enumerate(outputs)
        if (
            isinstance(output, dict)
            and output.get("delivery_role") == "thread_reply"
            and not any(
                isinstance(prior, dict) and prior.get("delivery_role") == "parent"
                for prior in outputs[:index]
            )
        )
    ]
    blocking_issues: list[str] = []
    if data["delivery_kind"] == "none":
        blocking_issues.append("delivery_kind is `none`; announcement remains draft-only.")
    if data["delivery_kind"] == "release-notes" and not data.get("release_notes_path"):
        blocking_issues.append("release-notes delivery requires `release_notes_path` before publication.")
    if data["delivery_kind"] == "human-backend" and not data.get("post_command_template"):
        blocking_issues.append("human-backend delivery requires `post_command_template` before posting.")
    if data["delivery_kind"] == "human-backend" and not data.get("delivery_capability"):
        blocking_issues.append("human-backend delivery requires `delivery_capability` before posting.")
    if has_thread_reply and not has_parent:
        blocking_issues.append(
            "outputs declare `thread_reply` without a preceding `parent` output; "
            "delivery is draft-only until the parent output can emit a delivery handle."
        )
    elif thread_replies_without_prior_parent:
        blocking_issues.append(
            "outputs declare `thread_reply` before any preceding `parent` output: "
            + ", ".join(str(item) for item in thread_replies_without_prior_parent)
            + "; delivery is draft-only until output order provides a parent handle first."
        )
    if has_thread_reply and not has_handle_placeholder:
        blocking_issues.append(
            "outputs declare `thread_reply` but `post_command_template` does not reference "
            "`{parent_delivery_handle}` or `{parent_delivery_handle_q}`; follow-up replies will "
            "not be wired to the parent post."
        )
    return {
        "status": "draft-only" if blocking_issues else "executable",
        "blocking_issues": blocking_issues,
        "chaining_required": has_thread_reply,
        "chaining_satisfied": has_thread_reply
        and has_parent
        and has_handle_placeholder
        and not thread_replies_without_prior_parent,
        "has_parent_output": has_parent,
        "has_parent_handle_placeholder": has_handle_placeholder,
    }


def _apply_public_body_shape(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str]
) -> None:
    raw_value = data.get("public_body_shape")
    if raw_value is None:
        validated["public_body_shape"] = (
            "release_notes" if validated["delivery_kind"] == "release-notes" else "chat_update"
        )
        return
    value = optional_string(raw_value, "public_body_shape", errors)
    if value is None:
        return
    if value not in PUBLIC_BODY_SHAPES:
        allowed = ", ".join(sorted(PUBLIC_BODY_SHAPES))
        errors.append(f"public_body_shape must be one of: {allowed}")
        return
    validated["public_body_shape"] = value


def validate_announcement_adapter_data(
    data: dict[str, Any], repo_root: Path
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_announcement_defaults(repo_root)
    data = _apply_simple_fields(data, validated, errors)
    _apply_structured_fields(data, validated, errors)
    _delivery_warnings(data, validated, warnings, errors)
    _apply_public_body_shape(data, validated, errors)
    return validated, errors, warnings


def load_announcement_adapter(repo_root: Path) -> dict[str, Any]:
    searched_paths = [str((repo_root / candidate).resolve()) for candidate in ADAPTER_CANDIDATES]
    adapter_path = next((repo_root / candidate for candidate in ADAPTER_CANDIDATES if (repo_root / candidate).is_file()), None)
    if adapter_path is None:
        data = infer_announcement_defaults(repo_root)
        contract = delivery_contract(data)
        return {
            "found": False,
            "valid": True,
            "path": None,
            "data": data,
            "delivery_contract": contract,
            "field_state": _field_state_map({}),
            "artifact_filename": ARTIFACT_FILENAME,
            "artifact_class": data["artifact_class"],
            "artifact_path": _artifact_path(data["output_dir"]),
            "record_artifact_pattern": _record_artifact_pattern(data["output_dir"]),
            "record_path": _record_path(),
            "bootstrap_expectations": _bootstrap_expectations(data),
            "errors": [],
            "warnings": [
                "No announcement adapter found. Using draft-first defaults.",
                f"First run leaves `{_artifact_path(data['output_dir'])}` as the visible draft artifact.",
                f"`{_record_path()}` only advances after explicit draft finalization or delivery.",
                "delivery_kind defaults to `none`, so bootstrap is intentionally draft-only until a repo chooses a backend seam.",
                "Create .agents/announcement-adapter.yaml to record section order, audience tags, and human-facing delivery seams.",
            ],
            "searched_paths": searched_paths,
        }

    # `load_yaml_file_report`, NOT `load_yaml_file`. The bare loader DISCARDS the
    # uninterpreted-line sink, and a bounded review measured what that costs on the
    # surface that matters most: `preflight_sources` is a PUBLISH GATE, and an
    # over-indented `in_progress_sources:` block left `errors: []`, `valid: true`, no
    # warning, and `delivery_blocked: false / ok: true` at exit 0 -- clear to announce over
    # a repo that declared a source it must not claim finished. Two of
    # `adapter_version_verdict`'s three refusal doors were structurally dead for this
    # adapter, so its consumers' guards could only ever see a refused `version`.
    #
    # This is one of the six resolvers #673 names. It is repaired HERE, ahead of that
    # issue, because the bypass it leaves open is a publish boundary rather than a message
    # shape.
    def _payload(
        *,
        data: dict[str, Any],
        errors: list[str],
        warnings: list[str],
        raw_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Every return below this line, built ONCE.

        A round-2 bounded review found the parse-failure arm hand-built as a nine-key
        dict while the other two arms carried fifteen -- omitting `artifact_path`, which
        `preflight_sources` indexes directly. Unreachable today only because the version
        guard refuses first on exactly the input that produces that arm; any reordering
        or any unguarded caller turns the refusal into a `KeyError`. The sibling this
        repair was modelled on, `simple_skill_adapter_lib`, avoids that structurally with
        one builder, and this copied the idea without the mechanism.
        """
        return {
            "found": True,
            "valid": not errors,
            "path": str(adapter_path),
            "data": data,
            "delivery_contract": delivery_contract(data),
            # CONTAINED ON THE UNHONORED CONDITION, not on `errors` -- the difference is
            # load-bearing and was measured. `simple_skill_adapter_lib` uses
            # `declarations_unhonored` here for the reason its own comment gives: under a
            # refused version the payload honors nothing, so reporting `configured` beside
            # a defaulted value makes the payload and the state map disagree about one
            # adapter. Keying on `if errors` instead ALSO zeroes the map for an ORDINARY
            # field error -- and `preflight_sources` reads this map precisely to catch a
            # declaration lost to one. The first cut did that and left the bypass open.
            "field_state": _field_state_map({} if declarations_unhonored(errors) else raw_data),
            "artifact_filename": ARTIFACT_FILENAME,
            "artifact_class": data["artifact_class"],
            "artifact_path": _artifact_path(data["output_dir"]),
            "record_artifact_pattern": _record_artifact_pattern(data["output_dir"]),
            "record_path": _record_path(),
            "bootstrap_expectations": _bootstrap_expectations(data),
            "errors": errors,
            "warnings": warnings,
            "searched_paths": searched_paths,
        }

    try:
        raw, uninterpreted = load_yaml_file_report(adapter_path)
    except ValueError as exc:
        return _payload(
            data=infer_announcement_defaults(repo_root),
            errors=[parse_failure_error(exc)],
            warnings=[],
            raw_data={},
        )
    raw_data = raw if isinstance(raw, dict) else {}
    warnings: list[str] = uninterpreted_warnings(uninterpreted)
    if not isinstance(raw, dict):
        warnings.append("Adapter file did not contain a mapping. Using inferred defaults.")
    data, errors, extra_warnings = validate_announcement_adapter_data(raw_data, repo_root)
    warnings.extend(extra_warnings)
    return _payload(data=data, errors=errors, warnings=warnings, raw_data=raw_data)
