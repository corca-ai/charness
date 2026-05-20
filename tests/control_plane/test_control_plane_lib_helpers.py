from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.control_plane_lib as control
import scripts.repo_layout as repo_layout


def _write_manifest_schema(repo: Path) -> None:
    tools_dir = repo / "integrations" / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    (tools_dir / "manifest.schema.json").write_text(
        (Path(__file__).resolve().parents[2] / "integrations" / "tools" / "manifest.schema.json").read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )


def _write_support_schema(repo: Path) -> None:
    support_root = repo / "skills" / "support"
    support_root.mkdir(parents=True, exist_ok=True)
    (support_root / "capability.schema.json").write_text(
        (Path(__file__).resolve().parents[2] / "skills" / "support" / "capability.schema.json").read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )
    support_dir = support_root / "demo"
    support_dir.mkdir(parents=True, exist_ok=True)
    (support_dir / "SKILL.md").write_text("# demo\n", encoding="utf-8")
    (support_dir / "capability.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "capability_id": "demo-support",
                "kind": "support_runtime",
                "display_name": "Demo support",
                "summary": "Support runtime.",
                "support_skill_path": "skills/support/demo/SKILL.md",
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["grant", "env", "degraded"],
                "version_expectation": {"policy": "advisory", "constraint": "local"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_manifest_and_lock_paths_skip_schema_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_manifest_schema(repo)
    locks_dir = repo / "integrations" / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    (repo / "integrations" / "tools" / "a.json").write_text("{}", encoding="utf-8")
    (repo / "integrations" / "tools" / "z.json").write_text("{}", encoding="utf-8")
    (locks_dir / "lock.schema.json").write_text("{}", encoding="utf-8")
    (locks_dir / "a.json").write_text("{}", encoding="utf-8")

    assert [path.name for path in control.manifest_paths(repo)] == ["a.json", "z.json"]
    assert [path.name for path in control.lock_paths(repo)] == ["a.json"]


def test_validate_manifest_and_support_capability_guard_invalid_shapes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_manifest_schema(repo)
    _write_support_schema(repo)
    manifest_base = {
        "schema_version": "1",
        "tool_id": "demo-tool",
        "kind": "external_binary_with_skill",
        "display_name": "Demo tool",
        "upstream_repo": "example/demo-tool",
        "homepage": "https://github.com/example/demo-tool",
        "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
        "checks": {
            "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
            "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
        },
        "access_modes": ["binary"],
        "version_expectation": {"policy": "advisory", "constraint": "latest"},
    }

    with pytest.raises(ValueError, match="local_wrapper requires wrapper_skill_id"):
        control.validate_manifest_data(
            {
                **manifest_base,
                "support_skill_source": {
                    "source_type": "local_wrapper",
                    "path": "docs/demo.md",
                }
            },
            control.load_manifest_schema(),
            repo / "integrations" / "tools" / "bad.json",
        )

    with pytest.raises(ValueError, match="must point at a skill root directory"):
        control.validate_manifest_data(
            {
                **manifest_base,
                "support_skill_source": {
                    "source_type": "upstream_repo",
                    "path": "skills/demo/SKILL.md",
                }
            },
            control.load_manifest_schema(),
            repo / "integrations" / "tools" / "bad.json",
        )

    with pytest.raises(ValueError, match="must match colocated support skill"):
        control.validate_support_capability_data(
            {
                "schema_version": "1",
                "capability_id": "demo-support",
                "kind": "support_runtime",
                "display_name": "Demo support",
                "summary": "Support runtime.",
                "support_skill_path": "skills/support/wrong/SKILL.md",
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["grant", "env", "degraded"],
                "version_expectation": {"policy": "advisory", "constraint": "local"},
            },
            control.load_support_capability_schema(repo),
            repo / "skills" / "support" / "demo" / "capability.json",
            repo,
        )


def test_validate_manifest_accepts_valid_support_source_variants(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_manifest_schema(repo)
    manifest_base = {
        "schema_version": "1",
        "tool_id": "demo-tool",
        "kind": "external_binary_with_skill",
        "display_name": "Demo tool",
        "upstream_repo": "example/demo-tool",
        "homepage": "https://github.com/example/demo-tool",
        "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
        "checks": {
            "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
            "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
        },
        "access_modes": ["binary"],
        "version_expectation": {"policy": "advisory", "constraint": "latest"},
    }
    schema = control.load_manifest_schema()
    path = repo / "integrations" / "tools" / "demo.json"

    control.validate_manifest_data(
        {
            **manifest_base,
            "support_skill_source": {
                "source_type": "local_wrapper",
                "path": "skills/support/demo",
                "wrapper_skill_id": "demo",
            },
        },
        schema,
        path,
    )
    control.validate_manifest_data(
        {
            **manifest_base,
            "support_skill_source": {
                "source_type": "upstream_repo",
                "path": "skills/demo",
            },
        },
        schema,
        path,
    )


def test_loaders_reject_duplicate_ids_and_normalize_defaults(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tools_dir = repo / "integrations" / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    _write_manifest_schema(repo)
    _write_support_schema(repo)

    manifest_payload = {
        "schema_version": "1",
        "tool_id": "dup",
        "kind": "external_binary",
        "display_name": "dup",
        "upstream_repo": "example/dup",
        "homepage": "https://github.com/example/dup",
        "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
        "checks": {
            "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
            "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
        },
        "access_modes": ["binary"],
        "version_expectation": {"policy": "advisory", "constraint": "latest"},
    }
    (tools_dir / "a.json").write_text(json.dumps(manifest_payload), encoding="utf-8")
    (tools_dir / "b.json").write_text(json.dumps(manifest_payload), encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate manifest tool_id `dup`"):
        control.load_manifests(repo)

    (tools_dir / "b.json").write_text(json.dumps({**manifest_payload, "tool_id": "demo-support"}), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate capability id `demo-support`"):
        control.load_capabilities(repo)

    normalized = control.normalize_support_capability(
        {
            "capability_id": "demo-support",
            "kind": "support_runtime",
            "display_name": "Demo support",
            "summary": "Support runtime.",
            "checks": {
                "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
            },
            "access_modes": ["grant", "env", "degraded"],
            "version_expectation": {"policy": "advisory", "constraint": "local"},
            "support_skill_path": "skills/support/demo/SKILL.md",
        },
        repo / "skills" / "support" / "demo" / "capability.json",
        repo,
    )
    assert normalized["capability_requirements"] == {}
    assert normalized["readiness_checks"] == []
    assert normalized["config_layers"] == []
    assert normalized["supports_public_skills"] == []
    assert normalized["intent_triggers"] == []


def test_discovery_loader_merges_plugin_fallback_manifests(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", raising=False)
    repo = tmp_path / "repo"
    repo.mkdir()

    manifests = control.load_manifests_for_discovery(repo)

    assert manifests
    assert {item["_manifest_origin"] for item in manifests} == {"plugin-fallback"}


def test_discovery_loader_prefers_user_manifest_over_duplicate_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", raising=False)
    repo = tmp_path / "repo"
    tools_dir = repo / "integrations" / "tools"
    tools_dir.mkdir(parents=True)
    fallback = control.plugin_fallback_manifest_paths()[0]
    fallback_data = json.loads(fallback.read_text(encoding="utf-8"))
    (tools_dir / fallback.name).write_text(
        json.dumps({"tool_id": fallback_data["tool_id"]}),
        encoding="utf-8",
    )

    matches = [
        item
        for item in control.load_manifests_for_discovery(repo)
        if item["tool_id"] == fallback_data["tool_id"]
    ]

    assert matches == [
        {
            "tool_id": fallback_data["tool_id"],
            "_manifest_path": f"integrations/tools/{fallback.name}",
            "_manifest_origin": "user-repo",
        }
    ]


def test_evaluate_success_criteria_and_run_check_collect_failures(tmp_path: Path) -> None:
    result = control.CommandResult(command="demo", exit_code=1, stdout="hello", stderr="boom")
    ok, failures = control.evaluate_success_criteria(
        result,
        [
            "exit_code:0",
            "stdout_contains:world",
            "stderr_contains:oops",
            "custom:unsupported",
        ],
    )
    assert ok is False
    assert failures == [
        "expected exit_code 0, got 1",
        "stdout missing `world`",
        "stderr missing `oops`",
        "unsupported success criterion `custom:unsupported`",
    ]

    check = {
        "commands": ["printf 'hello\\n'", "printf 'boom\\n' >&2"],
        "success_criteria": ["exit_code:0", "stdout_contains:hello"],
        "failure_hint": "inspect command output",
    }
    payload = control.run_check(check, tmp_path)
    assert payload["ok"] is False
    assert payload["failure_hint"] == "inspect command output"
    assert payload["failure_details"] == ["stdout missing `hello`"]


def test_support_dir_honors_charness_support_dir_env_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sibling_support = tmp_path / "external" / "charness-support" / "support"
    sibling_support.mkdir(parents=True)
    monkeypatch.setenv("CHARNESS_SUPPORT_DIR", str(sibling_support))
    public_root = tmp_path / "external" / "charness-public"
    public_root.mkdir(parents=True)
    assert repo_layout.support_dir(public_root) == sibling_support.resolve()


def test_load_support_capability_schema_accepts_explicit_repo_root(tmp_path: Path) -> None:
    support = tmp_path / "skills" / "support"
    support.mkdir(parents=True)
    (support / "capability.schema.json").write_text(
        json.dumps({"type": "object"}) + "\n", encoding="utf-8"
    )
    assert control.load_support_capability_schema(tmp_path) == {"type": "object"}


def test_evaluate_version_handles_unknown_and_matched_states() -> None:
    detect_result = {"results": [{"stdout": "demo-tool 1.2.3"}]}

    assert control.evaluate_version(
        {"version_expectation": {"policy": "advisory", "constraint": "latest"}},
        detect_result,
    ) == {
        "status": "advisory",
        "constraint": "latest",
        "observed_version": None,
    }

    assert control.evaluate_version(
        {"version_expectation": {"policy": "minimum", "constraint": ">=1.0.0", "detected_by": "manual"}},
        detect_result,
    )["status"] == "unknown"
    assert control.evaluate_version(
        {"version_expectation": {"policy": "weird", "constraint": ">=1.0.0", "detected_by": "stdout"}},
        detect_result,
    )["status"] == "unknown"
    assert control.evaluate_version(
        {"version_expectation": {"policy": "range", "constraint": "not-a-spec", "detected_by": "stdout"}},
        detect_result,
    )["status"] == "unknown"
    assert control.evaluate_version(
        {"version_expectation": {"policy": "minimum", "constraint": ">=2.0.0", "detected_by": "stdout"}},
        detect_result,
    )["status"] == "mismatched"
    assert control.evaluate_version(
        {"version_expectation": {"policy": "minimum", "constraint": ">=1.0.0", "detected_by": "stdout"}},
        detect_result,
    )["status"] == "matched"


def test_evaluate_version_covers_advisory_exact_and_range_edges() -> None:
    detect_result = {"results": [{"stdout": "demo-tool 1.2.3"}]}

    assert control.evaluate_version(
        {
            "version_expectation": {
                "policy": "advisory",
                "constraint": "latest",
                "detected_by": "stdout",
            }
        },
        detect_result,
    ) == {
        "status": "advisory",
        "constraint": "latest",
        "observed_version": "1.2.3",
    }
    assert control.evaluate_version(
        {
            "version_expectation": {
                "policy": "exact",
                "constraint": "==1.2.3",
                "detected_by": "stdout",
            }
        },
        detect_result,
    )["status"] == "matched"
    assert control.evaluate_version(
        {
            "version_expectation": {
                "policy": "range",
                "constraint": ">=1.0,<1.2",
                "detected_by": "stdout",
            }
        },
        detect_result,
    )["status"] == "mismatched"
    assert control.evaluate_version(
        {
            "version_expectation": {
                "policy": "minimum",
                "constraint": ">=1.0",
                "detected_by": "stdout",
            }
        },
        {"results": [{"stdout": "no semantic version here"}]},
    ) == {
        "status": "unknown",
        "constraint": ">=1.0",
        "observed_version": None,
    }


def test_now_iso_returns_utc_z_timestamp() -> None:
    value = control.now_iso()

    assert value.endswith("Z")
    assert "+" not in value


def test_run_shell_uses_bash_and_captures_output(tmp_path: Path) -> None:
    result = control.run_shell("echo ok", tmp_path)

    assert result.command == "echo ok"
    assert result.exit_code == 0
    assert result.stdout.strip() == "ok"


def test_dependency_helpers_create_sorted_staged_ids(tmp_path: Path) -> None:
    assert control.staged_tool_ids(tmp_path) is None
    assert control.add_dependency(tmp_path, "z-tool") is True
    assert control.add_dependency(tmp_path, "a-tool") is True
    assert control.add_dependency(tmp_path, "z-tool") is False

    assert control.staged_tool_ids(tmp_path) == {"a-tool", "z-tool"}
    data = json.loads((tmp_path / "integrations" / "tools" / "dependencies.json").read_text(encoding="utf-8"))
    assert data["tool_dependencies"] == ["a-tool", "z-tool"]


def test_upsert_lock_preserves_all_optional_sections(tmp_path: Path) -> None:
    manifest = {
        "tool_id": "demo-tool",
        "_manifest_path": "integrations/tools/demo-tool.json",
    }
    check_result = {"ok": True, "results": [], "failure_details": []}
    readiness = {"ok": True, "checks": [], "failed_checks": []}
    install = {
        "installed_at": "2026-05-16T00:00:00Z",
        "install_status": "installed",
        "mode": "manual",
        "commands": [],
        "detect": check_result,
        "healthcheck": check_result,
    }
    update = {
        "updated_at": "2026-05-16T00:00:00Z",
        "update_status": "updated",
        "mode": "manual",
        "commands": [],
        "detect": check_result,
        "healthcheck": check_result,
    }
    support = {
        "synced_at": "2026-05-16T00:00:00Z",
        "support_state": "integration-only",
        "source_type": "upstream_repo",
        "source_path": "example/demo",
        "cache_path": ".cache/demo",
        "content_digest": "abc123",
        "materialized_paths": [],
    }
    doctor = {
        "checked_at": "2026-05-16T00:00:00Z",
        "kind": "external_binary",
        "access_modes": ["binary"],
        "capability_requirements": {},
        "support_state": "integration-only",
        "detect": check_result,
        "healthcheck": check_result,
        "readiness": readiness,
        "version": {
            "status": "advisory",
            "constraint": "latest",
            "observed_version": None,
        },
        "support_sync": {
            "status": "not-tracked",
            "expected_paths": [],
            "missing_paths": [],
        },
        "doctor_status": "ok",
        "doctor_disposition": "ready",
    }
    release = {
        "provider": "github",
        "repo": "example/demo",
        "status": "ok",
        "api_url": "https://api.github.com/repos/example/demo/releases/latest",
        "html_url": "https://github.com/example/demo/releases/tag/v1.2.3",
        "latest_tag": "v1.2.3",
        "latest_version": "1.2.3",
        "published_at": "2026-05-16T00:00:00Z",
        "asset_names": [],
        "error": None,
    }
    provenance = {
        "checked_at": "2026-05-16T00:00:00Z",
        "binary_name": "demo",
        "status": "detected",
        "install_method": "path",
        "binary_path": "demo",
        "resolved_path": "/usr/bin/demo",
        "package_name": None,
        "package_manager_prefix": None,
        "available_package_managers": [],
        "update_supported": False,
    }
    path = control.upsert_lock(
        tmp_path,
        manifest,
        support=support,
        doctor=doctor,
        release=release,
        provenance=provenance,
        install=install,
        update=update,
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload == {
        "schema_version": "1",
        "tool_id": "demo-tool",
        "manifest_path": "integrations/tools/demo-tool.json",
        "support": support,
        "doctor": doctor,
        "release": release,
        "provenance": provenance,
        "install": install,
        "update": update,
    }
