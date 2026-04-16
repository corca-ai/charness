from __future__ import annotations

import json
import os
import tempfile
from contextlib import suppress
from pathlib import Path
from unittest import mock


def _manifest_base() -> dict[str, object]:
    return {
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


def exercise_control_plane_helper_scenarios() -> None:
    import scripts.control_plane_lib as control

    with tempfile.TemporaryDirectory(prefix="charness-control-plane-extra-") as temp_dir:
        repo = Path(temp_dir)
        tools_dir = repo / "integrations" / "tools"
        tools_dir.mkdir(parents=True)
        (tools_dir / "manifest.schema.json").write_text(
            (Path(__file__).resolve().parent.parent / "integrations" / "tools" / "manifest.schema.json").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        support_dir = repo / "skills" / "support" / "demo"
        support_dir.mkdir(parents=True)
        (support_dir / "SKILL.md").write_text("# demo\n", encoding="utf-8")
        capability_path = support_dir / "capability.json"
        capability_path.write_text(
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
        (tools_dir / "demo-tool.json").write_text(json.dumps(_manifest_base()), encoding="utf-8")
        control.manifest_paths(repo)
        control.load_manifests(repo)
        control.load_support_capabilities(repo)
        control.load_capabilities(repo)
        with suppress(ValueError):
            control.validate_manifest_data(
                {**_manifest_base(), "support_skill_source": {"source_type": "local_wrapper", "path": "docs/demo.md"}},
                control.load_manifest_schema(),
                tools_dir / "bad-local-wrapper.json",
            )
        with suppress(ValueError):
            control.validate_manifest_data(
                {
                    **_manifest_base(),
                    "support_skill_source": {"source_type": "upstream_repo", "path": "skills/demo/SKILL.md"},
                },
                control.load_manifest_schema(),
                tools_dir / "bad-upstream.json",
            )
        with suppress(ValueError):
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
            capability_path,
            repo,
        )
        control.normalize_support_capability(
            {
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
            capability_path,
            repo,
        )


def exercise_install_tool_helper_scenarios() -> None:
    import scripts.install_tools as install_tools

    with tempfile.TemporaryDirectory(prefix="charness-install-tools-extra-") as temp_dir:
        repo = Path(temp_dir)
        manifest = {**_manifest_base(), "_manifest_path": "integrations/tools/demo-tool.json"}
        install_action = {"docs_url": "https://example.com/install", "notes": ["demo"]}
        detect_result = {"ok": True, "results": [], "failure_details": [], "failure_hint": None}
        healthcheck_result = {"ok": True, "results": [], "failure_details": [], "failure_hint": None}
        with mock.patch.object(install_tools, "detect_install_provenance", return_value={"install_method": "brew"}):
            install_tools.capture_provenance(manifest)
        for install_method in ("brew", "path"):
            provenance = {"install_method": install_method, "package_name": "demo"}
            with mock.patch.object(install_tools, "upsert_lock"):
                install_tools.persist_install_lock(
                    repo,
                    manifest,
                    install_action,
                    status="installed",
                    mode="script",
                    commands=[{"command": "demo install", "exit_code": 0}],
                    detect=detect_result,
                    healthcheck=healthcheck_result,
                    release={"status": "ok"},
                    provenance=provenance,
                )
        install_tools.base_result(
            repo,
            manifest,
            install_action,
            status="installed",
            mode="script",
            commands=[{"command": "demo install", "exit_code": 0}],
        )


def exercise_support_sync_helper_scenarios() -> None:
    import scripts.support_sync_lib as support

    with tempfile.TemporaryDirectory(prefix="charness-support-sync-extra-") as temp_dir:
        root = Path(temp_dir)
        repo = root / "repo"
        repo.mkdir()
        fixture_path = root / "fixtures.json"
        fixture_path.write_text('["bad"]\n', encoding="utf-8")
        with mock.patch.dict(os.environ, {support.SUPPORT_FIXTURES_ENV: str(fixture_path)}, clear=False):
            with suppress(ValueError):
                support._fixture_checkout_root("example/demo", "main")
        fixture_path.write_text(json.dumps({"example/demo": str(root / "missing")}) + "\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {support.SUPPORT_FIXTURES_ENV: str(fixture_path)}, clear=False):
            with suppress(ValueError):
                support._fixture_checkout_root("example/demo", None)
        support.write_discovery_stub(
            repo,
            {"tool_id": "demo", "intent_triggers": [], "lifecycle": {"install": {}}},
            support_skill_path="skills/support/generated/demo/SKILL.md",
        )
        manifest = {
            "tool_id": "demo",
            "upstream_repo": "example/demo",
            "support_skill_source": {"source_type": "upstream_repo", "path": "skills/demo"},
        }
        with suppress(ValueError):
            support._resolve_upstream_source_path(manifest, upstream_checkouts={})
        checkout = root / "checkout"
        skill_root = checkout / "skills" / "demo"
        skill_root.mkdir(parents=True)
        (skill_root / "SKILL.md").write_text("# demo\n", encoding="utf-8")
        manifest["support_skill_source"]["ref"] = "main"
        support._resolve_upstream_source_path(manifest, upstream_checkouts={"example/demo": checkout})
        bad_checkout = root / "bad-checkout"
        bad_checkout.mkdir()
        with suppress(ValueError):
            support._resolve_upstream_source_path(manifest, upstream_checkouts={"example/demo": bad_checkout})


def exercise_upstream_release_helper_scenarios() -> None:
    import scripts.upstream_release_lib as upstream

    upstream.extract_version(None)
    upstream.extract_version("release 2026.04")
    upstream.normalize_release_payload(
        "example/tool",
        {
            "status": "error",
            "reason": "fixture-error",
            "error": "broken",
            "tag_name": "release v3.4.5",
            "assets": [{"name": "tool.tar.gz"}, {"name": 7}, "bad"],
        },
    )
    upstream.probe_release({"tool_id": "demo"})
    upstream.probe_release({"upstream_repo": "example/demo", "homepage": "https://example.com/demo"})
    with mock.patch.dict(os.environ, {"CHARNESS_RELEASE_PROBE_NO_GH": "1"}, clear=False):
        upstream._probe_github_release_with_gh("example/tool")
    with mock.patch.dict(os.environ, {"CHARNESS_RELEASE_PROBE_NO_GH": ""}, clear=False):
        with mock.patch.object(upstream.shutil, "which", return_value="/usr/bin/gh"):
            completed = type("Completed", (), {"returncode": 0, "stdout": "{not-json", "stderr": ""})()
            with mock.patch.object(upstream.subprocess, "run", return_value=completed):
                upstream._probe_github_release_with_gh("example/tool")
