"""External tool next-step builders."""

from __future__ import annotations

import json


def _healthcheck_attention_suffix(payload: dict[str, object]) -> str:
    healthcheck = payload.get("healthcheck")
    if not isinstance(healthcheck, dict):
        return ""
    status = healthcheck.get("status")
    if isinstance(status, str) and status:
        return f" healthcheck={status}"
    if healthcheck.get("skipped") is True:
        return " healthcheck=skipped"
    return ""


def _tool_release_suffix(
    action_result: dict[str, object] | None,
    doctor_result: dict[str, object] | None,
    support_result: dict[str, object] | None,
) -> str:
    for candidate in (action_result, doctor_result, support_result):
        if not isinstance(candidate, dict):
            continue
        release = candidate.get("release")
        if not isinstance(release, dict) or release.get("status") != "ok":
            continue
        parts: list[str] = []
        tag = release.get("latest_tag")
        url = release.get("html_url")
        if isinstance(tag, str) and tag:
            parts.append(f"Latest upstream release: `{tag}`.")
        if isinstance(url, str) and url:
            parts.append(url)
        return " ".join(parts).strip()
    return ""


def _with_release_suffix(message: str, release_suffix: str) -> str:
    return f"{message} {release_suffix}".strip() if release_suffix else message


def _install_route_suffix(result: dict[str, object] | None) -> str:
    if not isinstance(result, dict):
        return ""
    route = result.get("install_route")
    if not isinstance(route, dict):
        return ""
    install_url = route.get("install_url")
    docs_url = route.get("docs_url")
    notes = route.get("notes")
    details: list[str] = []
    if isinstance(notes, list) and notes:
        first_note = notes[0]
        if isinstance(first_note, str) and first_note:
            details.append(first_note)
    repo_followup = route.get("repo_followup")
    if isinstance(repo_followup, dict):
        rendered_command = repo_followup.get("rendered_command")
        summary = repo_followup.get("summary")
        if isinstance(rendered_command, str) and rendered_command:
            if isinstance(summary, str) and summary:
                details.append(f"{summary} Follow-up command: `{rendered_command}`")
            else:
                details.append(f"Follow-up command: `{rendered_command}`")
    if isinstance(install_url, str) and install_url:
        details.append(f"Install docs: {install_url}")
    if isinstance(docs_url, str) and docs_url and docs_url != install_url:
        details.append(f"Docs: {docs_url}")
    return " ".join(details)


def _support_discovery_suffix(result: dict[str, object] | None) -> str:
    if not isinstance(result, dict):
        return ""
    discovery = result.get("support_discovery")
    if not isinstance(discovery, dict):
        return ""
    guidance = discovery.get("guidance")
    if isinstance(guidance, str) and guidance:
        return guidance
    path = discovery.get("support_skill_path")
    if isinstance(path, str) and path:
        return f"Support skill is available at `{path}`."
    return ""


def _manual_tool_next_step(
    tool_id: str,
    action_result: dict[str, object],
    doctor_result: dict[str, object] | None,
) -> str:
    install_url = action_result.get("install_url")
    docs_url = action_result.get("docs_url")
    notes = action_result.get("notes")
    repo_followup = action_result.get("repo_followup")
    first_note = (
        notes[0] if isinstance(notes, list) and notes and isinstance(notes[0], str) else None
    )
    guidance = first_note or f"Follow the upstream install flow for `{tool_id}`."
    provenance = action_result.get("provenance")
    if isinstance(provenance, dict) and provenance.get("status") == "detected":
        manager = provenance.get("install_method")
        if isinstance(manager, str) and manager in {"npm", "cargo", "go"}:
            guidance = f"`{tool_id}` is already installed via `{manager}`."
    if isinstance(repo_followup, dict):
        rendered_command = repo_followup.get("rendered_command")
        summary = repo_followup.get("summary")
        if isinstance(rendered_command, str) and rendered_command:
            if isinstance(summary, str) and summary:
                guidance = f"{guidance} {summary} Follow-up command: `{rendered_command}`"
            else:
                guidance = f"{guidance} Follow-up command: `{rendered_command}`"
    if isinstance(install_url, str) and install_url:
        guidance = f"{guidance} Install docs: {install_url}"
    if isinstance(docs_url, str) and docs_url and docs_url != install_url:
        guidance = f"{guidance} Docs: {docs_url}"
    discovery_suffix = _support_discovery_suffix(doctor_result)
    return f"{guidance} {discovery_suffix}".strip() if discovery_suffix else guidance


def _package_manager_tool_next_step(tool_id: str, action_result: dict[str, object]) -> str | None:
    if action_result.get("mode") != "package_manager":
        return None
    package_manager = action_result.get("package_manager")
    package_name = action_result.get("package_name")
    if not isinstance(package_manager, str) or not isinstance(package_name, str):
        return None
    if action_result.get("status") in {"updated", "updated-not-ready"}:
        version_transition = action_result.get("version_transition")
        if isinstance(version_transition, dict):
            from_version = version_transition.get("from")
            to_version = version_transition.get("to")
            if (
                isinstance(from_version, str)
                and from_version
                and isinstance(to_version, str)
                and to_version
                and from_version != to_version
            ):
                return (
                    f"`{tool_id}` was updated via `{package_manager}` package `{package_name}` "
                    f"({from_version} -> {to_version})."
                )
        return f"`{tool_id}` was updated via `{package_manager}` package `{package_name}`."
    if action_result.get("status") in {"refreshed", "refreshed-not-ready"}:
        version_transition = action_result.get("version_transition")
        if isinstance(version_transition, dict):
            from_version = version_transition.get("from")
            to_version = version_transition.get("to")
            if (
                isinstance(from_version, str)
                and from_version
                and isinstance(to_version, str)
                and to_version
            ):
                if from_version != to_version:
                    return (
                        f"`{tool_id}` was refreshed via `{package_manager}` package `{package_name}` "
                        f"({from_version} -> {to_version})."
                    )
                return f"`{tool_id}` was refreshed via `{package_manager}` package `{package_name}` ({to_version})."
        return f"`{tool_id}` was refreshed via `{package_manager}` package `{package_name}`."
    return f"`{tool_id}` can be refreshed via `{package_manager}` package `{package_name}`."


def _doctor_ok_next_step(tool_id: str, doctor_result: dict[str, object]) -> str | None:
    if doctor_result.get("doctor_status") != "ok":
        return None
    provenance = doctor_result.get("provenance")
    if isinstance(provenance, dict):
        manager = provenance.get("install_method")
        package_name = provenance.get("package_name")
        if (
            isinstance(manager, str)
            and manager in {"npm", "cargo", "go"}
            and isinstance(package_name, str)
        ):
            message = f"`{tool_id}` is ready via `{manager}` package `{package_name}`."
            discovery_suffix = _support_discovery_suffix(doctor_result)
            return f"{message} {discovery_suffix}".strip() if discovery_suffix else message
    message = f"`{tool_id}` is ready."
    discovery_suffix = _support_discovery_suffix(doctor_result)
    return f"{message} {discovery_suffix}".strip() if discovery_suffix else message


def _doctor_missing_next_step(
    tool_id: str,
    doctor_result: dict[str, object],
    support_result: dict[str, object] | None,
) -> str | None:
    if doctor_result.get("doctor_status") != "missing":
        return None
    detect = doctor_result.get("detect")
    hint = detect.get("failure_hint") if isinstance(detect, dict) else None
    install_suffix = _install_route_suffix(doctor_result)
    discovery_suffix = _support_discovery_suffix(doctor_result)
    if isinstance(support_result, dict) and support_result.get("status") == "synced":
        paths = support_result.get("materialized_paths")
        if isinstance(paths, list) and paths:
            message = (
                f"Support skill materialization for `{tool_id}` was refreshed under {', '.join(paths)}, "
                "but the standalone binary is still missing."
            )
            if isinstance(hint, str) and hint:
                message = f"{message} {hint}"
            if install_suffix:
                message = f"{message} {install_suffix}"
            if discovery_suffix:
                message = f"{message} {discovery_suffix}"
            return message
    if isinstance(hint, str) and hint:
        if install_suffix:
            hint = f"{hint} {install_suffix}"
        if discovery_suffix:
            hint = f"{hint} {discovery_suffix}"
        return hint
    return None


def _doctor_support_next_step(
    tool_id: str,
    doctor_result: dict[str, object],
    support_result: dict[str, object] | None,
) -> str | None:
    if doctor_result.get("doctor_status") != "support-missing" or not isinstance(
        support_result, dict
    ):
        return None
    paths = support_result.get("materialized_paths")
    if not isinstance(paths, list) or not paths:
        return None
    message = f"Regenerated support artifacts for `{tool_id}` under {', '.join(paths)}."
    discovery_suffix = _support_discovery_suffix(doctor_result)
    return f"{message} {discovery_suffix}".strip() if discovery_suffix else message


def _doctor_not_ready_next_step(tool_id: str, doctor_result: dict[str, object]) -> str | None:
    if doctor_result.get("doctor_status") != "not-ready":
        return None
    readiness = doctor_result.get("readiness")
    failed_checks = []
    hint = None
    if isinstance(readiness, dict):
        raw_failed = readiness.get("failed_checks")
        if isinstance(raw_failed, list):
            failed_checks = [str(check) for check in raw_failed if isinstance(check, str)]
        checks = readiness.get("checks")
        if isinstance(checks, list):
            for check in checks:
                if not isinstance(check, dict) or check.get("ok") is not False:
                    continue
                failure_hint = check.get("failure_hint")
                if isinstance(failure_hint, str) and failure_hint:
                    hint = failure_hint
                    break
    check_text = f" Failed readiness check(s): {', '.join(failed_checks)}." if failed_checks else ""
    hint_text = f" {hint}" if hint else ""
    return f"`{tool_id}` is installed but not ready for its consuming workflow.{check_text}{hint_text}".strip()


def _healthcheck_runtime_next_step(
    doctor_result: dict[str, object],
) -> tuple[str | None, str | None]:
    healthcheck = doctor_result.get("healthcheck")
    if not isinstance(healthcheck, dict):
        return None, None
    results = healthcheck.get("results")
    if not isinstance(results, list):
        return None, None
    for item in results:
        if not isinstance(item, dict):
            continue
        stdout = item.get("stdout")
        if not isinstance(stdout, str) or not stdout.strip().startswith("{"):
            continue
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            continue
        next_step = payload.get("next_step")
        next_step_kind = payload.get("next_step_kind")
        if isinstance(next_step, str) and next_step:
            return next_step, next_step_kind if isinstance(next_step_kind, str) else None
    return None, None


def _doctor_unhealthy_next_step(tool_id: str, doctor_result: dict[str, object]) -> str | None:
    if doctor_result.get("doctor_status") != "unhealthy":
        return None
    runtime_next_step, runtime_next_step_kind = _healthcheck_runtime_next_step(doctor_result)
    if tool_id == "agent-browser" and runtime_next_step_kind == "cleanup_command":
        return (
            "`agent-browser` is installed but its runtime healthcheck found owned orphan "
            "daemon trees. Run `charness tool repair --execute agent-browser` to run "
            "the cleanup and post-doctor verification."
        )
    if isinstance(runtime_next_step, str) and runtime_next_step:
        return f"`{tool_id}` is installed but its healthcheck failed. {runtime_next_step}"
    healthcheck = doctor_result.get("healthcheck")
    hint = healthcheck.get("failure_hint") if isinstance(healthcheck, dict) else None
    if isinstance(hint, str) and hint:
        return f"`{tool_id}` is installed but its healthcheck failed. {hint}"
    return f"`{tool_id}` is installed but its healthcheck failed. Inspect the structured doctor result."


def _support_only_next_step(
    tool_id: str,
    support_result: dict[str, object] | None,
    doctor_result: dict[str, object] | None,
) -> str | None:
    if not isinstance(support_result, dict) or support_result.get("status") != "synced":
        return None
    paths = support_result.get("materialized_paths")
    if not isinstance(paths, list) or not paths:
        return None
    message = (
        f"Support skill materialization for `{tool_id}` was refreshed under {', '.join(paths)}."
    )
    discovery_suffix = _support_discovery_suffix(doctor_result)
    return f"{message} {discovery_suffix}".strip() if discovery_suffix else message


def tool_next_step(
    tool_id: str,
    action_result: dict[str, object] | None,
    doctor_result: dict[str, object] | None,
    support_result: dict[str, object] | None,
) -> str:
    release_suffix = _tool_release_suffix(action_result, doctor_result, support_result)
    if isinstance(doctor_result, dict):
        for message in (
            _doctor_unhealthy_next_step(tool_id, doctor_result),
            _doctor_not_ready_next_step(tool_id, doctor_result),
        ):
            if message is not None:
                return _with_release_suffix(message, release_suffix)
    if isinstance(action_result, dict) and action_result.get("status") == "manual":
        return _with_release_suffix(
            _manual_tool_next_step(tool_id, action_result, doctor_result), release_suffix
        )
    if isinstance(action_result, dict):
        package_manager_message = _package_manager_tool_next_step(tool_id, action_result)
        if package_manager_message is not None:
            return _with_release_suffix(package_manager_message, release_suffix)
    if isinstance(doctor_result, dict):
        for message in (
            _doctor_ok_next_step(tool_id, doctor_result),
            _doctor_missing_next_step(tool_id, doctor_result, support_result),
            _doctor_support_next_step(tool_id, doctor_result, support_result),
        ):
            if message is not None:
                return _with_release_suffix(message, release_suffix)
    support_only_message = _support_only_next_step(tool_id, support_result, doctor_result)
    if support_only_message is not None:
        return _with_release_suffix(support_only_message, release_suffix)
    return _with_release_suffix(
        f"Review the structured result for `{tool_id}` and follow the manifest guidance.",
        release_suffix,
    )
