"""Direct unit tests for the #873 `tool_next_steps` feature module.

The next-step builders only run inside tool flows the suite exercises through
seed-checkout copies, so in-process coverage never reaches them without
direct calls.
"""

from __future__ import annotations

import json

import scripts.cli.tool_next_steps as next_steps


def test_healthcheck_attention_suffix_shapes() -> None:
    assert next_steps._healthcheck_attention_suffix({}) == ""
    assert (
        next_steps._healthcheck_attention_suffix({"healthcheck": {"status": "ok"}})
        == " healthcheck=ok"
    )
    assert (
        next_steps._healthcheck_attention_suffix({"healthcheck": {"skipped": True}})
        == " healthcheck=skipped"
    )
    assert next_steps._healthcheck_attention_suffix({"healthcheck": {}}) == ""


def test_tool_release_suffix_shapes() -> None:
    assert next_steps._tool_release_suffix(None, None, None) == ""
    release = {"release": {"status": "ok", "latest_tag": "v9.0.0"}}
    assert "v9.0.0" in next_steps._tool_release_suffix(release, None, None)
    assert "v9.0.0" in next_steps._tool_release_suffix(None, release, None)
    full = {"release": {"status": "ok", "latest_tag": "v9.0.0", "html_url": "https://e.test/r"}}
    suffix = next_steps._tool_release_suffix(None, None, full)
    assert "v9.0.0" in suffix and "https://e.test/r" in suffix
    assert next_steps._tool_release_suffix({"release": {"status": "error"}}, None, None) == ""
    assert next_steps._with_release_suffix("msg", "") == "msg"
    assert next_steps._with_release_suffix("msg", "extra") == "msg extra"


def test_install_route_suffix_shapes() -> None:
    assert next_steps._install_route_suffix(None) == ""
    assert next_steps._install_route_suffix({}) == ""
    route = {
        "install_route": {
            "notes": ["first note", 42],
            "repo_followup": {"rendered_command": "make setup", "summary": "then run"},
            "install_url": "https://e.test/install",
            "docs_url": "https://e.test/docs",
        }
    }
    suffix = next_steps._install_route_suffix(route)
    assert "first note" in suffix
    assert "make setup" in suffix
    assert "https://e.test/install" in suffix
    assert "https://e.test/docs" in suffix
    bare_followup = {"install_route": {"repo_followup": {"rendered_command": "make x"}}}
    assert "make x" in next_steps._install_route_suffix(bare_followup)
    same_urls = {"install_route": {"install_url": "u", "docs_url": "u"}}
    assert "Docs:" not in next_steps._install_route_suffix(same_urls)


def test_support_discovery_suffix_shapes() -> None:
    assert next_steps._support_discovery_suffix(None) == ""
    assert next_steps._support_discovery_suffix({}) == ""
    assert (
        next_steps._support_discovery_suffix({"support_discovery": {"guidance": "read this"}})
        == "read this"
    )
    assert "skill" in next_steps._support_discovery_suffix(
        {"support_discovery": {"support_skill_path": "skills/x/SKILL.md"}}
    )
    assert next_steps._support_discovery_suffix({"support_discovery": {}}) == ""


def test_manual_tool_next_step_shapes() -> None:
    detected = {
        "notes": ["upstream note"],
        "provenance": {"status": "detected", "install_method": "npm"},
        "repo_followup": {"rendered_command": "make setup", "summary": "then run"},
        "install_url": "https://e.test/install",
        "docs_url": "https://e.test/docs",
    }
    message = next_steps._manual_tool_next_step("my-tool", detected, None)
    assert "already installed via `npm`" in message
    assert "make setup" in message
    assert "https://e.test/install" in message
    plain = next_steps._manual_tool_next_step("my-tool", {}, None)
    assert "upstream install flow" in plain
    bare_followup = {"repo_followup": {"rendered_command": "make x"}}
    assert "make x" in next_steps._manual_tool_next_step("my-tool", bare_followup, None)
    discovered = next_steps._manual_tool_next_step(
        "my-tool", {}, {"support_discovery": {"guidance": "read this"}}
    )
    assert discovered.endswith("read this")


def test_package_manager_tool_next_step_shapes() -> None:
    assert next_steps._package_manager_tool_next_step("t", {}) is None
    assert next_steps._package_manager_tool_next_step("t", {"mode": "package_manager"}) is None
    base = {"mode": "package_manager", "package_manager": "npm", "package_name": "pkg"}
    updated = dict(base, status="updated", version_transition={"from": "1.0", "to": "2.0"})
    assert "1.0 -> 2.0" in next_steps._package_manager_tool_next_step("t", updated)
    assert "was updated" in next_steps._package_manager_tool_next_step(
        "t", dict(base, status="updated")
    )
    refreshed = dict(base, status="refreshed", version_transition={"from": "1.0", "to": "1.0"})
    assert "(1.0)" in next_steps._package_manager_tool_next_step("t", refreshed)
    moved = dict(
        base, status="refreshed-not-ready", version_transition={"from": "1.0", "to": "2.0"}
    )
    assert "1.0 -> 2.0" in next_steps._package_manager_tool_next_step("t", moved)
    assert "was refreshed" in next_steps._package_manager_tool_next_step(
        "t", dict(base, status="refreshed")
    )
    assert "can be refreshed" in next_steps._package_manager_tool_next_step("t", base)


def test_doctor_ok_next_step_shapes() -> None:
    assert next_steps._doctor_ok_next_step("t", {}) is None
    ready = {"doctor_status": "ok"}
    assert next_steps._doctor_ok_next_step("t", ready) == "`t` is ready."
    npm = {
        "doctor_status": "ok",
        "provenance": {"install_method": "cargo", "package_name": "pkg"},
        "support_discovery": {"guidance": "read this"},
    }
    assert next_steps._doctor_ok_next_step("t", npm).endswith("read this")


def test_doctor_missing_next_step_shapes() -> None:
    assert next_steps._doctor_missing_next_step("t", {}, None) is None
    doctor = {
        "doctor_status": "missing",
        "detect": {"failure_hint": "install it"},
        "install_route": {"install_url": "https://e.test/install"},
        "support_discovery": {"guidance": "read this"},
    }
    support = {"status": "synced", "materialized_paths": ["p/a", "p/b"]}
    message = next_steps._doctor_missing_next_step("t", doctor, support)
    assert message is not None and "p/a, p/b" in message and "install it" in message
    hint_only = next_steps._doctor_missing_next_step(
        "t", {"doctor_status": "missing", "detect": {"failure_hint": "hint"}}, None
    )
    assert hint_only == "hint"
    hint_install = next_steps._doctor_missing_next_step(
        "t",
        {
            "doctor_status": "missing",
            "detect": {"failure_hint": "hint"},
            "install_route": {"install_url": "https://e.test/install"},
            "support_discovery": {"guidance": "read this"},
        },
        None,
    )
    assert hint_install == "hint Install docs: https://e.test/install read this"
    assert next_steps._doctor_missing_next_step("t", {"doctor_status": "missing"}, None) is None


def test_doctor_support_next_step_shapes() -> None:
    assert next_steps._doctor_support_next_step("t", {}, None) is None
    assert (
        next_steps._doctor_support_next_step("t", {"doctor_status": "support-missing"}, None)
        is None
    )
    assert (
        next_steps._doctor_support_next_step(
            "t",
            {"doctor_status": "support-missing"},
            {"status": "synced", "materialized_paths": []},
        )
        is None
    )
    message = next_steps._doctor_support_next_step(
        "t",
        {"doctor_status": "support-missing"},
        {"status": "synced", "materialized_paths": ["p"]},
    )
    assert message is not None and "`t`" in message and "p" in message


def test_doctor_not_ready_next_step_shapes() -> None:
    assert next_steps._doctor_not_ready_next_step("t", {}) is None
    doctor = {
        "doctor_status": "not-ready",
        "readiness": {
            "failed_checks": ["disk", 42],
            "checks": [{"ok": True}, {"ok": False, "failure_hint": "free space"}],
        },
    }
    message = next_steps._doctor_not_ready_next_step("t", doctor)
    assert message is not None and "disk" in message and "free space" in message
    bare = next_steps._doctor_not_ready_next_step("t", {"doctor_status": "not-ready"})
    assert bare is not None and "not ready" in bare


def test_healthcheck_runtime_next_step_shapes() -> None:
    assert next_steps._healthcheck_runtime_next_step({}) == (None, None)
    assert next_steps._healthcheck_runtime_next_step({"healthcheck": {}}) == (None, None)
    results = {
        "healthcheck": {
            "results": [
                "junk",
                {"stdout": "plain text"},
                {"stdout": "not json {"},
                {
                    "stdout": json.dumps(
                        {"next_step": "do the thing", "next_step_kind": "cleanup_command"}
                    )
                },
            ]
        }
    }
    assert next_steps._healthcheck_runtime_next_step(results) == (
        "do the thing",
        "cleanup_command",
    )
    garbage = {"healthcheck": {"results": [{"stdout": "{oops"}]}}
    assert next_steps._healthcheck_runtime_next_step(garbage) == (None, None)


def test_doctor_unhealthy_next_step_shapes() -> None:
    assert next_steps._doctor_unhealthy_next_step("t", {}) is None
    doctor = {
        "doctor_status": "unhealthy",
        "healthcheck": {
            "results": [
                {"stdout": json.dumps({"next_step": "restart it"})},
            ]
        },
    }
    message = next_steps._doctor_unhealthy_next_step("t", doctor)
    assert message is not None and "restart it" in message
    cleanup = {
        "doctor_status": "unhealthy",
        "healthcheck": {
            "results": [
                {
                    "stdout": json.dumps(
                        {
                            "next_step": "clean up",
                            "next_step_kind": "cleanup_command",
                        }
                    )
                }
            ]
        },
    }
    assert "tool repair" in next_steps._doctor_unhealthy_next_step("agent-browser", cleanup)
    hinted = {
        "doctor_status": "unhealthy",
        "healthcheck": {"failure_hint": "see logs"},
    }
    assert "see logs" in next_steps._doctor_unhealthy_next_step("t", hinted)
    bare = next_steps._doctor_unhealthy_next_step("t", {"doctor_status": "unhealthy"})
    assert "Inspect the structured doctor result" in bare


def test_support_only_next_step_shapes() -> None:
    assert next_steps._support_only_next_step("t", None, None) is None
    assert next_steps._support_only_next_step("t", {"status": "stale"}, None) is None
    assert (
        next_steps._support_only_next_step(
            "t", {"status": "synced", "materialized_paths": []}, None
        )
        is None
    )
    message = next_steps._support_only_next_step(
        "t", {"status": "synced", "materialized_paths": ["p"]}, None
    )
    assert message is not None and "p" in message


def test_tool_next_step_dispatch_shapes() -> None:
    unhealthy = {"doctor_status": "unhealthy"}
    assert "healthcheck failed" in next_steps.tool_next_step("t", None, unhealthy, None)
    manual = {"status": "manual"}
    assert "upstream install flow" in next_steps.tool_next_step("t", manual, None, None)
    package_manager = {"mode": "package_manager", "package_manager": "npm", "package_name": "p"}
    assert "can be refreshed" in next_steps.tool_next_step("t", package_manager, None, None)
    assert "`t` is ready." in next_steps.tool_next_step("t", None, {"doctor_status": "ok"}, None)
    support = {"status": "synced", "materialized_paths": ["p"]}
    assert "materialization" in next_steps.tool_next_step("t", None, None, support)
    assert "manifest guidance" in next_steps.tool_next_step("t", None, None, None)
    release = {"release": {"status": "ok", "latest_tag": "v9.0.0"}}
    assert "v9.0.0" in next_steps.tool_next_step("t", None, {"doctor_status": "ok"}, release)
