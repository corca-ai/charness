from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.control_plane_lib as control


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
    support_dir = repo / "skills" / "support" / "demo"
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
            control.load_support_capability_schema(),
            repo / "skills" / "support" / "demo" / "capability.json",
            repo,
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
