from __future__ import annotations

import importlib
import json
import os
import runpy
import tarfile
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


def _run_module_top_level(*relative_paths: str) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    for relative_path in relative_paths:
        runpy.run_path(str(repo_root / relative_path), run_name="coverage_probe")


def _seed_control_plane_repo(repo: Path) -> tuple[Path, Path]:
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
    return tools_dir, capability_path


def _exercise_control_plane_loader_paths(control: object, repo: Path, tools_dir: Path, capability_path: Path) -> None:
    control.manifest_paths(repo)
    control.load_manifests(repo)
    control.load_support_capabilities(repo)
    control.load_capabilities(repo)
    with suppress(ValueError):
        (tools_dir / "duplicate.json").write_text(json.dumps(_manifest_base()), encoding="utf-8")
        control.load_manifests(repo)
    duplicate_capability_dir = repo / "skills" / "support" / "duplicate"
    duplicate_capability_dir.mkdir(parents=True)
    (duplicate_capability_dir / "SKILL.md").write_text("# duplicate\n", encoding="utf-8")
    (duplicate_capability_dir / "capability.json").write_text(capability_path.read_text(encoding="utf-8"), encoding="utf-8")
    with suppress(ValueError):
        control.load_support_capabilities(repo)
    (tools_dir / "duplicate.json").write_text(json.dumps({**_manifest_base(), "tool_id": "demo-support"}), encoding="utf-8")
    with suppress(ValueError):
        control.load_capabilities(repo)


def _exercise_control_plane_validation_paths(control: object, repo: Path, tools_dir: Path, capability_path: Path) -> None:
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


def _exercise_control_plane_runtime_paths(control: object, repo: Path) -> None:
    control.run_check(
        {
            "commands": ["printf 'hello\\n'", "printf 'boom\\n' >&2"],
            "success_criteria": ["exit_code:0", "stdout_contains:hello"],
        },
        repo,
    )
    control.evaluate_version(
        {"version_expectation": {"policy": "weird", "constraint": ">=1.0.0", "detected_by": "stdout"}},
        {"results": [{"stdout": "demo 1.2.3"}]},
    )
    control.evaluate_version(
        {"version_expectation": {"policy": "minimum", "constraint": "not-a-spec", "detected_by": "stdout"}},
        {"results": [{"stdout": "demo 1.2.3"}]},
    )


def exercise_control_plane_helper_scenarios() -> None:
    import scripts.control_plane_lib as control

    importlib.reload(control)
    _run_module_top_level("scripts/control_plane_lib.py")
    with tempfile.TemporaryDirectory(prefix="charness-control-plane-extra-") as temp_dir:
        repo = Path(temp_dir)
        tools_dir, capability_path = _seed_control_plane_repo(repo)
        _exercise_control_plane_loader_paths(control, repo, tools_dir, capability_path)
        _exercise_control_plane_validation_paths(control, repo, tools_dir, capability_path)
        _exercise_control_plane_runtime_paths(control, repo)


def exercise_install_tool_helper_scenarios() -> None:
    import scripts.install_tools as install_tools

    importlib.reload(install_tools)
    _run_module_top_level("scripts/install_tools.py")
    with tempfile.TemporaryDirectory(prefix="charness-install-tools-extra-") as temp_dir:
        repo = Path(temp_dir)
        manifest = {**_manifest_base(), "_manifest_path": "integrations/tools/demo-tool.json"}
        install_action = {"docs_url": "https://example.com/install", "notes": ["demo"]}
        detect_result = {"ok": True, "results": [], "failure_details": [], "failure_hint": None}
        healthcheck_result = {"ok": True, "results": [], "failure_details": [], "failure_hint": None}
        with mock.patch.object(install_tools, "detect_install_provenance", return_value={"install_method": "npm"}):
            install_tools.capture_provenance(manifest)
        for install_method in ("npm", "path"):
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
            detect=detect_result,
            healthcheck=healthcheck_result,
        )


def exercise_support_sync_helper_scenarios() -> None:
    import scripts.support_sync_lib as support

    importlib.reload(support)
    _run_module_top_level("scripts/support_sync_lib.py", "scripts/sync_support.py")
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
        fixture_path.write_text(json.dumps({"other/repo": str(root / "repo")}) + "\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {support.SUPPORT_FIXTURES_ENV: str(fixture_path)}, clear=False):
            support._fixture_checkout_root("example/demo", "main")
        with suppress(ValueError):
            support.parse_upstream_checkout(f"example/demo={root / 'missing-checkout'}")
        support.write_discovery_stub(
            repo,
            {"tool_id": "demo", "intent_triggers": [], "lifecycle": {"install": {}}},
            support_skill_path="skills/support/generated/demo/SKILL.md",
        )
        bad_extract = root / "bad-extract"
        bad_extract.mkdir()
        with suppress(ValueError, tarfile.ReadError):
            support._safe_extract_tarball(b"", bad_extract)
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
        with mock.patch.object(support, "_fetch_upstream_archive", return_value=b"not-a-tarball"):
            with suppress(ValueError, OSError, EOFError, Exception):
                support._resolve_upstream_source_path(manifest, upstream_checkouts={})
        generated = repo / "skills" / "support" / "generated"
        generated.mkdir(parents=True)
        support.materialize_repo_symlink(checkout, generated / "demo", repo)


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


def exercise_install_provenance_helper_scenarios() -> None:
    import scripts.install_provenance_lib as provenance

    importlib.reload(provenance)
    with mock.patch.object(provenance.subprocess, "run", side_effect=OSError()):
        provenance._run_command(["missing"])
    failed = type("Completed", (), {"returncode": 1, "stdout": "nope\n"})()
    with mock.patch.object(provenance.subprocess, "run", return_value=failed):
        provenance._run_command(["demo"])

    with tempfile.TemporaryDirectory(prefix="charness-install-provenance-extra-") as temp_dir:
        home = Path(temp_dir) / "home"
        (home / ".cargo").mkdir(parents=True)
        (home / "go").mkdir(parents=True)
        with mock.patch.object(provenance.Path, "home", return_value=home):
            with mock.patch.dict(os.environ, {"CARGO_HOME": "", "GOPATH": ""}, clear=False):
                with mock.patch.object(provenance, "_run_command", return_value=None):
                    provenance.detect_package_manager_prefixes()
    provenance.detect_install_provenance({"checks": {"detect": {"commands": []}}})
    provenance.package_manager_update_action(
        {"package_managers": {"pip": {"package_name": "demo"}}},
        {"status": "detected", "install_method": "pip"},
    )
    provenance._path_matches_manager(home / "bin" / "demo", home / "bin" / "demo", "pip", home)
