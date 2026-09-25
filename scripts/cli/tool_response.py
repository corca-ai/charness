"""External tool response projection."""

from __future__ import annotations

import argparse


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli.bootstrap import (  # noqa: E402
    _MUTATING_TOOL_EVENTS,
    BLOCKING_DOCTOR_DISPOSITIONS,
    TOOL_DOCTOR_FAILURE_STATUSES,
    TOOL_SUPPORT_FAILURE_STATUSES,
    TOOL_UPDATE_FAILURE_STATUSES,
)
from scripts.cli.tool_next_steps import (  # noqa: E402
    _healthcheck_attention_suffix,
)


def _tool_doctor_result_is_blocking(result: dict[str, object]) -> bool:
    status = result.get("doctor_status")
    disposition = result.get("doctor_disposition")
    return status in TOOL_DOCTOR_FAILURE_STATUSES or disposition in BLOCKING_DOCTOR_DISPOSITIONS


def _tool_result_failure_phases(result: dict[str, object]) -> list[str]:
    phases: list[str] = []
    update = result.get("update")
    if isinstance(update, dict) and update.get("status") in TOOL_UPDATE_FAILURE_STATUSES:
        phases.append("update")
    support = result.get("support")
    if isinstance(support, dict) and support.get("status") in TOOL_SUPPORT_FAILURE_STATUSES:
        phases.append("support")
    doctor = result.get("doctor")
    if isinstance(doctor, dict) and _tool_doctor_result_is_blocking(doctor):
        phases.append("doctor")
    return phases


def tool_ids_from_args(args: argparse.Namespace) -> list[str]:
    return list(getattr(args, "tool_ids", []) or [])


def tool_result_map(results: object) -> dict[str, dict[str, object]]:
    if not isinstance(results, list):
        return {}
    mapped: dict[str, dict[str, object]] = {}
    for item in results:
        if not isinstance(item, dict):
            continue
        tool_id = item.get("tool_id")
        if isinstance(tool_id, str):
            mapped[tool_id] = item
    return mapped


def _tool_release_result(*candidates: object) -> dict[str, object] | None:
    for candidate in candidates:
        if isinstance(candidate, dict) and isinstance(candidate.get("release"), dict):
            return candidate["release"]
    return None


def _print_tool_result_block(tool_id: str, result: dict[str, object]) -> None:
    print(f"{tool_id}:")
    repair_result = result.get("repair")
    if isinstance(repair_result, dict):
        print(
            f"  REPAIR: {repair_result.get('status')} "
            f"({'execute' if repair_result.get('execute') else 'preview'})"
        )
    install_result = result.get("install")
    if isinstance(install_result, dict):
        print(f"  INSTALL: {install_result.get('status')} ({install_result.get('mode')})")
        provenance = install_result.get("provenance")
        if isinstance(provenance, dict):
            print(
                "  INSTALL_PROVENANCE: "
                f"{provenance.get('install_method')} "
                f"{provenance.get('package_name') or provenance.get('binary_path') or ''}".rstrip()
            )
    update_result = result.get("update")
    if isinstance(update_result, dict):
        print(
            f"  UPDATE: {update_result.get('status')} "
            f"({update_result.get('mode')}){_healthcheck_attention_suffix(update_result)}"
        )
        package_manager = update_result.get("package_manager")
        package_name = update_result.get("package_name")
        if isinstance(package_manager, str) and package_manager:
            print(f"  UPDATE_ROUTE: {package_manager} {package_name or ''}".rstrip())
    support_result = result.get("support")
    if isinstance(support_result, dict):
        print(f"  SUPPORT: {support_result.get('status')}")
    doctor_result = result.get("doctor")
    if isinstance(doctor_result, dict):
        print(
            f"  DOCTOR: {doctor_result.get('doctor_status')} "
            f"({doctor_result.get('support_state')}){_healthcheck_attention_suffix(doctor_result)}"
        )
        provenance = doctor_result.get("provenance")
        if isinstance(provenance, dict):
            print(
                "  PROVENANCE: "
                f"{provenance.get('install_method')} "
                f"{provenance.get('package_name') or provenance.get('binary_path') or ''}".rstrip()
            )
    release_result = _tool_release_result(
        install_result, update_result, doctor_result, support_result
    )
    if isinstance(release_result, dict):
        print(
            f"  RELEASE: {release_result.get('status')} "
            f"{release_result.get('latest_tag') or release_result.get('html_url') or ''}".rstrip()
        )
    next_step = result.get("next_step")
    if isinstance(next_step, str):
        print(f"  NEXT: {next_step}")


def _compact_mapping(payload: object, keys: tuple[str, ...]) -> dict[str, object] | None:
    if not isinstance(payload, dict):
        return None
    compact = {key: payload[key] for key in keys if key in payload}
    return compact or None


def _compact_healthcheck(payload: dict[str, object]) -> dict[str, object] | None:
    return _compact_mapping(payload.get("healthcheck"), ("status",))


def _compact_tool_action(action: str, payload: object) -> dict[str, object] | None:
    if not isinstance(payload, dict):
        return None
    if action == "doctor":
        compact = _compact_mapping(
            payload, ("doctor_status", "doctor_disposition", "observed_version")
        )
        version = payload.get("version")
        if isinstance(version, dict):
            observed = version.get("observed_version")
            if isinstance(observed, str) and observed:
                compact = dict(compact or {})
                compact.setdefault("observed_version", observed)
    elif action == "repair":
        compact = _compact_mapping(payload, ("status", "execute"))
    else:
        compact = _compact_mapping(
            payload,
            ("status", "mode", "package_manager", "package_name", "version_transition"),
        )
    if compact is None:
        compact = {}
    healthcheck = _compact_healthcheck(payload)
    if healthcheck is not None:
        compact["healthcheck"] = healthcheck
    return compact or None


def _tool_result_status(result: dict[str, object]) -> str | None:
    for action in ("install", "update", "repair", "support"):
        payload = result.get(action)
        if isinstance(payload, dict) and isinstance(payload.get("status"), str):
            return payload["status"]
    doctor = result.get("doctor")
    if isinstance(doctor, dict) and isinstance(doctor.get("doctor_status"), str):
        return doctor["doctor_status"]
    return None


def _tool_attention_groups(result: dict[str, object]) -> set[str]:
    """Classify the bounded set of tool ids worth surfacing in an aggregate."""
    groups: set[str] = set()
    for action in ("install", "update", "repair", "support"):
        payload = result.get(action)
        if not isinstance(payload, dict):
            continue
        status = payload.get("status")
        if status in {"failed", "updated-not-ready", "refreshed-not-ready", "installed-not-ready"}:
            groups.add("failed")
        elif status == "manual":
            groups.add("manual")
    doctor = result.get("doctor")
    if isinstance(doctor, dict):
        disposition = doctor.get("doctor_disposition")
        status = doctor.get("doctor_status")
        if disposition in BLOCKING_DOCTOR_DISPOSITIONS or status in {
            "failed",
            "missing",
            "unhealthy",
        }:
            groups.add("not_ready")
    return groups


def _project_single_tool_result(
    raw_result: dict[str, object],
) -> tuple[dict[str, object], str | None]:
    result: dict[str, object] = {}
    for action in ("install", "update", "repair", "support", "doctor"):
        compact_action = _compact_tool_action(action, raw_result.get(action))
        if compact_action is not None:
            result[action] = compact_action
    next_step = raw_result.get("next_step")
    if isinstance(next_step, str) and next_step:
        result["next_step"] = next_step
    status = _tool_result_status(raw_result)
    if status is not None:
        result["status"] = status
    return result, status


def _project_tool_results(
    raw_results: object,
) -> tuple[dict[str, dict[str, object]], dict[str, int]]:
    projected_results: dict[str, dict[str, object]] = {}
    status_counts: dict[str, int] = {}
    if not isinstance(raw_results, dict):
        return projected_results, status_counts
    for tool_id in sorted(raw_results):
        raw_result = raw_results.get(tool_id)
        if not isinstance(raw_result, dict):
            continue
        result, status = _project_single_tool_result(raw_result)
        if status is not None:
            status_counts[status] = status_counts.get(status, 0) + 1
        projected_results[tool_id] = result
    return projected_results, status_counts


def project_tool_response(payload: dict[str, object], *, event: str) -> dict[str, object]:
    """Return the stable, compact public view of a tool-operation payload.

    The underlying helper payload is intentionally richer than the root CLI
    response: it contains commands, releases, routes, and probe evidence for
    lock files and diagnosis.  The default root response keeps only the
    operator-facing status, transition, and next action for each tool.
    """
    raw_results = payload.get("results")
    projected_results, status_counts = _project_tool_results(raw_results)
    response: dict[str, object] = {
        "event": event,
        "response_level": "summary",
        "detail_available": True,
    }
    for key in ("repo_root", "managed_checkout", "tool_ids", "tool_selection", "execute"):
        if key in payload:
            response[key] = payload[key]
    response["summary"] = {
        "tool_count": len(projected_results),
        "status_counts": dict(sorted(status_counts.items())),
    }
    for key in ("status", "failure_scope", "failed_tool_ids", "failure_phases"):
        if key in payload:
            response[key] = payload[key]
    if len(projected_results) <= 1:
        response["results"] = projected_results
        return response

    attention: dict[str, list[str]] = {}
    if isinstance(raw_results, dict):
        for tool_id, raw_result in raw_results.items():
            if not isinstance(tool_id, str) or not isinstance(raw_result, dict):
                continue
            for group in _tool_attention_groups(raw_result):
                attention.setdefault(f"{group}_tool_ids", []).append(tool_id)
    if attention:
        response["attention"] = {
            key: sorted(tool_ids) for key, tool_ids in sorted(attention.items())
        }
        response["next_step"] = _tool_attention_next_step(event, payload)
    return response


def _tool_attention_next_step(event: str, payload: dict[str, object]) -> str:
    if event in _MUTATING_TOOL_EVENTS and payload.get("execute") is not False:
        return (
            "Inspect integrations/locks/<tool_id>.json for the executed records, or run "
            "`charness tool doctor <tool_id> --detail` for current state; re-running this "
            "command with --detail may execute the operation again."
        )
    return "Use --detail to inspect the listed tool records."
