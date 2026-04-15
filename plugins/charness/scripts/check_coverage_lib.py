from __future__ import annotations

import io
import json
import os
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from contextlib import suppress
from pathlib import Path
from unittest import mock

PER_FILE_MIN_STATEMENTS = 30
PER_FILE_MIN_COVERAGE = 0.80
PER_FILE_WARN_BELOW = 0.95


class FakeUrlResponse:
    def __init__(self, payload: dict[str, object] | str) -> None:
        self.payload = payload

    def __enter__(self) -> "FakeUrlResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        if isinstance(self.payload, str):
            return self.payload.encode("utf-8")
        return json.dumps(self.payload).encode("utf-8")


def build_per_file_floor_report(
    files: list[dict[str, object]],
    *,
    floor: float = PER_FILE_MIN_COVERAGE,
) -> dict[str, object]:
    violations: list[dict[str, object]] = []
    warn_band: list[dict[str, object]] = []
    for item in files:
        total = int(item["total"])
        coverage = float(item["coverage"])
        if total < PER_FILE_MIN_STATEMENTS:
            continue
        candidate = {
            "path": item["path"],
            "covered": item["covered"],
            "total": total,
            "coverage": coverage,
        }
        if coverage < floor:
            violations.append(candidate)
        elif coverage < PER_FILE_WARN_BELOW:
            warn_band.append(candidate)
    return {
        "status": "enforced",
        "relationship": "per-file-floor",
        "min_statements_threshold": PER_FILE_MIN_STATEMENTS,
        "floor": floor,
        "warn_below": PER_FILE_WARN_BELOW,
        "violations": violations,
        "warn_band": warn_band,
    }


def _basic_manifest(tool_id: str = "demo") -> dict[str, object]:
    return {
        "tool_id": tool_id,
        "_manifest_path": f"integrations/tools/{tool_id}.json",
        "checks": {
            "detect": {"commands": ["demo --version"], "success_criteria": ["exit_code:0"]},
            "healthcheck": {"commands": ["demo --help"], "success_criteria": ["exit_code:0"]},
        },
        "version_expectation": {"policy": "minimum", "constraint": ">=1.0.0", "detected_by": "stdout"},
    }


def _tarball_with_single_root() -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        root = tarfile.TarInfo("archive-root")
        root.type = tarfile.DIRTYPE
        tar.addfile(root)
        payload = b"# demo\n"
        member = tarfile.TarInfo("archive-root/SKILL.md")
        member.size = len(payload)
        tar.addfile(member, io.BytesIO(payload))
    return buffer.getvalue()


def exercise_control_plane_scenarios() -> None:
    import jsonschema

    import scripts.control_plane_lib as control
    import scripts.control_plane_lifecycle_lib as lifecycle

    result = control.CommandResult("demo", 1, "out", "err")
    lifecycle.command_result_payload(result)
    control.evaluate_success_criteria(
        result,
        [
            "exit_code:0",
            "stdout_contains:missing",
            "stderr_contains:missing",
            "unsupported:value",
        ],
    )
    manifest = _basic_manifest()
    lifecycle.failed_healthcheck(manifest, reason="detect failed")
    lifecycle.attach_release_metadata({}, provenance={"status": "detected"}, release={"status": "ok"})
    selected = lifecycle.select_by_tool_id([manifest, _basic_manifest("other")], ["demo"])
    lifecycle.print_tool_statuses([{"tool_id": "demo", "status": "ok"}])
    lifecycle.has_any_status(selected, status_key="tool_id", statuses={"demo"})
    with mock.patch.object(lifecycle, "run_check", return_value={"ok": False}):
        lifecycle.detect_and_healthcheck(Path("."), manifest, failure_reason="detect failed")
    with mock.patch.object(lifecycle, "run_shell", return_value=result):
        lifecycle.run_command_payloads(["demo"], Path("."))
    control.evaluate_version(manifest, {"results": [{"stdout": "demo 1.2.0"}]})
    for version_manifest in (
        {**manifest, "version_expectation": {"policy": "exact", "constraint": "==1.0.0", "detected_by": "stdout"}},
        {**manifest, "version_expectation": {"policy": "range", "constraint": ">=1.0.0,<=2.0.0", "detected_by": "stdout"}},
        {**manifest, "version_expectation": {"policy": "unknown", "constraint": "latest", "detected_by": "stdout"}},
        {**manifest, "version_expectation": {"policy": "minimum", "constraint": ">=1.0.0", "detected_by": "manual"}},
    ):
        control.evaluate_version(version_manifest, {"results": [{"stdout": "demo not-a-version"}]})
    control.base_lock_payload(manifest)
    with tempfile.TemporaryDirectory(prefix="charness-control-plane-") as temp_dir:
        repo = Path(temp_dir)
        (repo / "integrations" / "locks").mkdir(parents=True)
        control.lock_paths(repo)
        with mock.patch.object(control, "manifest_by_tool_id", return_value={"demo": manifest}):
            control.selected_manifests(repo, [])
            control.selected_manifests(repo, ["demo", "missing"])
        with mock.patch.object(control, "load_lock_schema", return_value={"type": "object", "additionalProperties": False}):
            (repo / "integrations" / "locks" / "demo.json").write_text('{"unexpected": true}\n', encoding="utf-8")
            with mock.patch.object(control.sys.stderr, "write"):
                control.read_lock(repo, "demo")
        with suppress(jsonschema.ValidationError):
            control.validate_lock_data({"unexpected": True}, {"type": "object", "additionalProperties": False}, repo / "lock.json")


def exercise_install_provenance_scenarios() -> None:
    import scripts.install_provenance_lib as provenance

    provenance.detect_binary_name({"checks": {"detect": {"commands": []}}})
    provenance.detect_binary_name({"checks": {"detect": {"commands": [42]}}})
    provenance.detect_binary_name({"checks": {"detect": {"commands": [""]}}})
    manifest = {
        "checks": {"detect": {"commands": ["demo --version"]}},
        "package_managers": {
            "brew": {"package_name": "demo-brew"},
            "npm": {"package_name": "demo-npm"},
            "cargo": {"package_name": "demo-cargo"},
            "go": {"package_name": "example.com/demo/cmd/demo"},
        },
    }
    with tempfile.TemporaryDirectory(prefix="charness-provenance-") as temp_dir:
        root = Path(temp_dir)
        prefixes = {manager: root / manager for manager in ("brew", "npm", "cargo", "go")}
        for prefix in prefixes.values():
            (prefix / "bin").mkdir(parents=True)
        commands = {
            ("brew", "--prefix"): str(prefixes["brew"]),
            ("npm", "prefix", "-g"): str(prefixes["npm"]),
            ("go", "env", "GOPATH"): str(prefixes["go"]),
        }

        def fake_run_command(command: list[str]) -> str | None:
            return commands.get(tuple(command))

        with mock.patch.object(provenance, "_run_command", side_effect=fake_run_command):
            with mock.patch.dict(os.environ, {"CARGO_HOME": str(prefixes["cargo"]), "GOPATH": ""}, clear=False):
                provenance.detect_package_manager_prefixes()
        with mock.patch.object(provenance.shutil, "which", return_value=None):
            with mock.patch.object(provenance, "detect_package_manager_prefixes", return_value={"brew": str(prefixes["brew"])}):
                provenance.detect_install_provenance(manifest)
        for manager, prefix in prefixes.items():
            binary = prefix / "bin" / "demo"
            binary.write_text("#!/bin/sh\n", encoding="utf-8")
            with mock.patch.object(provenance.shutil, "which", return_value=str(binary)):
                with mock.patch.object(provenance, "detect_package_manager_prefixes", return_value={manager: str(prefix)}):
                    detected = provenance.detect_install_provenance(manifest)
                    provenance.package_manager_update_action(manifest, detected)
        other_binary = root / "other" / "demo"
        other_binary.parent.mkdir()
        other_binary.write_text("#!/bin/sh\n", encoding="utf-8")
        with mock.patch.object(provenance.shutil, "which", return_value=str(other_binary)):
            with mock.patch.object(provenance, "detect_package_manager_prefixes", return_value={"brew": str(prefixes["brew"])}):
                provenance.detect_install_provenance(manifest)
        for bad_provenance in (
            {"status": "missing"},
            {"status": "detected", "install_method": 5},
            {"status": "detected", "install_method": "unknown"},
        ):
            provenance.package_manager_update_action(manifest, bad_provenance)
        provenance.package_manager_update_action({"package_managers": []}, {"status": "detected", "install_method": "brew"})
        provenance.package_manager_update_action(
            {"package_managers": {"brew": {"package_name": ""}}},
            {"status": "detected", "install_method": "brew"},
        )


def exercise_support_sync_scenarios() -> None:
    import scripts.support_sync_lib as support

    support.support_state_for_manifest({"kind": "support_runtime"})
    support.support_state_for_manifest({})
    support.support_state_for_manifest({"support_skill_source": {"source_type": "local_wrapper"}})
    support.inspect_support_sync(Path("."), None)
    support.support_link_name({"tool_id": "demo", "support_skill_source": {"source_type": "local_wrapper", "wrapper_skill_id": "wrapper"}})
    support.render_discovery_stub(
        manifest={
            "tool_id": "demo",
            "intent_triggers": ["open demo"],
            "lifecycle": {"install": {"docs_url": "https://example.com/docs"}},
        },
        support_skill_path="skills/support/demo/SKILL.md",
    )
    with tempfile.TemporaryDirectory(prefix="charness-support-sync-") as temp_dir:
        root = Path(temp_dir)
        repo = root / "repo"
        repo.mkdir()
        expected = repo / "skills" / "support" / "generated" / "demo"
        support.inspect_support_sync(repo, {"support": {"materialized_paths": [str(expected.relative_to(repo))]}})
        with suppress(ValueError):
            support.parse_upstream_checkout("bad")
        support.parse_upstream_checkout(f"example/demo={repo}")
        file_target = root / "target-file"
        file_target.write_text("x", encoding="utf-8")
        support.clear_materialized_target(file_target)
        dir_target = root / "target-dir"
        dir_target.mkdir()
        support.clear_materialized_target(dir_target)
        source = root / "source"
        source.mkdir()
        link = root / "link"
        link.symlink_to(source, target_is_directory=True)
        support.clear_materialized_target(link)
        fixture = root / "fixtures.json"
        upstream = root / "upstream"
        (upstream / "skills" / "demo").mkdir(parents=True)
        fixture.write_text(json.dumps({"example/demo@main": str(upstream)}), encoding="utf-8")
        with mock.patch.dict(os.environ, {support.SUPPORT_FIXTURES_ENV: str(fixture)}, clear=False):
            support._fixture_checkout_root("example/demo", "main")
        with mock.patch.object(support.urllib.request, "urlopen", side_effect=urllib.error.URLError("offline")):
            with suppress(ValueError):
                support._fetch_upstream_archive("example/demo", "main")
        support._safe_extract_tarball(_tarball_with_single_root(), root / "extract")
        source.joinpath("SKILL.md").write_text("# demo\n", encoding="utf-8")
        source.joinpath("linked").symlink_to(source / "SKILL.md")
        support._compute_tree_digest(source)
        manifest = {
            "tool_id": "demo",
            "support_skill_source": {
                "source_type": "local_wrapper",
                "path": "docs/demo.md",
                "wrapper_skill_id": "demo-wrapper",
            },
        }
        (repo / "docs").mkdir()
        (repo / "docs" / "demo.md").write_text("# upstream\n", encoding="utf-8")
        with mock.patch.object(support, "support_skill_cache_dir", return_value=root / "cache"):
            cache_root, _digest = support._write_local_wrapper_to_cache(repo, manifest, "# wrapper\n")
            support.materialize_repo_symlink(cache_root, repo / "skills" / "support" / "generated" / "demo-wrapper", repo)
        upstream_manifest = {
            "tool_id": "demo-upstream",
            "upstream_repo": "example/demo",
            "support_skill_source": {"source_type": "upstream_repo", "path": "skills/demo", "ref": "main"},
        }
        with mock.patch.object(support, "support_skill_cache_dir", return_value=root / "cache"):
            support.materialize_upstream_support(upstream_manifest, upstream_checkouts={"example/demo": upstream})


def exercise_lifecycle_scenarios() -> None:
    import scripts.install_tools as install_tools
    import scripts.sync_support as sync_support
    import scripts.update_tools as update_tools
    from scripts.control_plane_lib import CommandResult

    manifest = _basic_manifest()
    manifest["lifecycle"] = {
        "install": {"mode": "script", "commands": ["demo install"], "docs_url": "https://example.com/install"},
        "update": {"mode": "script", "commands": ["demo update"], "docs_url": "https://example.com/update"},
    }
    manual_manifest = {**manifest, "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}}}
    none_manifest = {**manifest, "lifecycle": {"install": {"mode": "none"}, "update": {"mode": "none"}}}
    detect_ok = {"ok": True, "results": [], "failure_details": [], "failure_hint": None}
    health_ok = {"ok": True, "results": [], "failure_details": [], "failure_hint": None}
    provenance = {"status": "detected", "install_method": "path", "package_name": None}
    with tempfile.TemporaryDirectory(prefix="charness-lifecycle-") as temp_dir:
        repo = Path(temp_dir)
        release = {"status": "ok", "latest_version": "1.0.0"}
        with mock.patch.object(install_tools, "probe_release", return_value=release):
            with mock.patch.object(install_tools, "capture_provenance", return_value=dict(provenance)):
                with mock.patch.object(install_tools, "detect_and_healthcheck", return_value=(detect_ok, health_ok)):
                    with mock.patch.object(install_tools, "persist_install_lock"):
                        install_tools.install_one(repo, none_manifest, execute=True)
                        install_tools.install_one(repo, manual_manifest, execute=True)
                        install_tools.install_one(repo, manifest, execute=False)
                        with mock.patch.object(
                            install_tools,
                            "run_command_payloads",
                            return_value=[{"command": "demo install", "exit_code": 0, "stdout": "", "stderr": ""}],
                        ):
                            install_tools.install_one(repo, manifest, execute=True)
        with mock.patch.object(update_tools, "probe_release", return_value=release):
            with mock.patch.object(update_tools, "detect_install_provenance", return_value=dict(provenance)):
                with mock.patch.object(update_tools, "package_manager_update_action", return_value=None):
                    with mock.patch.object(update_tools, "detect_and_healthcheck", return_value=(detect_ok, health_ok)):
                        with mock.patch.object(update_tools, "upsert_lock"):
                            update_tools.update_one(repo, none_manifest, execute=True)
                            update_tools.update_one(repo, manual_manifest, execute=True)
                            update_tools.update_one(repo, manifest, execute=False)
                            with mock.patch.object(update_tools, "run_shell", return_value=CommandResult("demo update", 0, "ok\n", "")):
                                update_tools.update_one(repo, manifest, execute=True)
        no_support = {"tool_id": "no-support"}
        sync_support.sync_one(repo, no_support, execute=False, upstream_checkouts={})
        with mock.patch.object(sync_support, "parse_upstream_checkout", return_value=("example/demo", repo)):
            with mock.patch.object(sync_support, "load_manifests", return_value=[no_support]):
                with mock.patch.object(sys, "argv", ["sync_support.py", "--repo-root", str(repo)]):
                    sync_support.main()


def exercise_upstream_release_scenarios() -> None:
    import scripts.upstream_release_lib as upstream

    def ok_urlopen(_request: urllib.request.Request, *, timeout: int) -> FakeUrlResponse:
        if timeout != 10:
            raise AssertionError("unexpected release probe timeout")
        return FakeUrlResponse({"tag_name": "v9.9.9", "assets": []})

    class FailedGh:
        returncode = 1
        stdout = ""
        stderr = "not authenticated"

    release_env = {
        "CHARNESS_RELEASE_PROBE_FIXTURES": "",
        "CHARNESS_RELEASE_PROBE_NO_GH": "",
        "GH_TOKEN": "",
        "GITHUB_TOKEN": "",
    }
    with mock.patch.dict(os.environ, release_env, clear=False):
        with mock.patch.object(upstream.shutil, "which", return_value=None):
            with mock.patch.object(upstream.urllib.request, "urlopen", ok_urlopen):
                upstream.probe_github_release("example/no-gh")
        with mock.patch.object(upstream.shutil, "which", return_value="/usr/bin/gh"):
            with mock.patch.object(upstream.subprocess, "run", return_value=FailedGh()):
                with mock.patch.object(upstream.urllib.request, "urlopen", ok_urlopen):
                    upstream.probe_github_release("example/failed-gh")
        with mock.patch.object(upstream.shutil, "which", return_value=None):
            for code in (403, 500):

                def http_error_urlopen(request: urllib.request.Request, *, timeout: int, code: int = code) -> FakeUrlResponse:
                    raise urllib.error.HTTPError(request.full_url, code, "error", hdrs=None, fp=None)

                with mock.patch.object(upstream.urllib.request, "urlopen", http_error_urlopen):
                    upstream.probe_github_release(f"example/http-{code}")

            def invalid_json_urlopen(_request: urllib.request.Request, *, timeout: int) -> FakeUrlResponse:
                return FakeUrlResponse("{not-json")

            with mock.patch.object(upstream.urllib.request, "urlopen", invalid_json_urlopen):
                upstream.probe_github_release("example/invalid-json")

            def malformed_urlopen(_request: urllib.request.Request, *, timeout: int) -> FakeUrlResponse:
                return FakeUrlResponse("[]")

            with mock.patch.object(upstream.urllib.request, "urlopen", malformed_urlopen):
                upstream.probe_github_release("example/malformed")
