from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import pytest
import yaml

import scripts.doctor as doctor_module
import scripts.install_tools as install_tools_module
import tools.validate_integrations as validate_integrations_module
from scripts.adapters.control_plane_lib import load_capabilities
from scripts.doctor import inspect_manifest
from scripts.sync_support import sync_one
from tests.dsl import Repo
from tests.repo_copy import clone_seeded_charness_repo
from tests.script_main import run_loaded_script_main
from tools.validate_integrations import (
    ValidationError,
    validate_access_mode_order,
    validate_capability_requirements,
    validate_config_layers,
    validate_support_install_entrypoint,
)

from .support import ROOT, run_script, seed_control_plane_repo

MANIFEST_SCHEMA = (ROOT / "integrations" / "tools" / "manifest.schema.json").read_text(
    encoding="utf-8"
)
DEPENDENCIES_SCHEMA = (ROOT / "integrations" / "tools" / "dependencies.schema.json").read_text(
    encoding="utf-8"
)


def write_manifest_schema(repo: Path) -> Path:
    tools_dir = repo / "integrations" / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    (tools_dir / "manifest.schema.json").write_text(
        MANIFEST_SCHEMA,
        encoding="utf-8",
    )
    return tools_dir


def read_manifest(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_lock(
    repo: Path,
    *,
    tool_id: str = "demo-tool",
    manifest_path: str = "integrations/tools/demo-tool.json",
) -> Path:
    lock_path = repo / "integrations" / "locks" / f"{tool_id}.json"
    lock_path.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": tool_id,
                "manifest_path": manifest_path,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return lock_path


def test_validate_integrations_refuses_lock_with_missing_manifest(tmp_path: Path) -> None:
    repo = seed_control_plane_repo(tmp_path)
    lock_path = write_lock(
        repo,
        tool_id="stale-tool",
        manifest_path="integrations/tools/deleted-tool.json",
    )

    result = run_loaded_script_main(
        "validate_integrations.py",
        validate_integrations_module,
        "--repo-root",
        str(repo),
    )

    assert result.returncode != 0
    assert lock_path.name in result.stderr
    assert "integrations/tools/deleted-tool.json" in result.stderr
    assert "remove the stale lock or restore the manifest" in result.stderr


def test_validate_integrations_accepts_lock_with_existing_manifest(tmp_path: Path) -> None:
    repo = seed_control_plane_repo(tmp_path)
    write_lock(repo)

    result = run_loaded_script_main(
        "validate_integrations.py",
        validate_integrations_module,
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 0, result.stderr
    assert "1 lock files" in result.stdout


def test_validate_integrations_rejects_invalid_local_wrapper(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file(
            "integrations/tools/manifest.schema.json",
            lambda: MANIFEST_SCHEMA,
        )
        .file(
            "integrations/tools/bad.json",
            json.dumps(
                {
                    "schema_version": "1",
                    "tool_id": "bad",
                    "kind": "external_skill",
                    "display_name": "bad",
                    "upstream_repo": "example/bad",
                    "homepage": "https://example.com/bad",
                    "lifecycle": {
                        "install": {
                            "mode": "manual",
                            "install_url": "https://example.com/bad/install",
                        },
                        "update": {"mode": "manual"},
                    },
                    "checks": {
                        "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                        "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    },
                    "access_modes": ["binary"],
                    "version_expectation": {"policy": "advisory", "constraint": "latest"},
                    "support_skill_source": {
                        "source_type": "local_wrapper",
                        "path": "docs/bad.md",
                        "ref": "main",
                    },
                }
            ),
        )
        .build(tmp_path)
    )
    result = run_loaded_script_main(
        "validate_integrations.py",
        validate_integrations_module,
        "--repo-root",
        str(repo),
    )
    assert result.returncode == 1
    assert "local_wrapper requires wrapper_skill_id" in result.stderr


def test_validate_integrations_requires_install_entrypoint_for_support_backed_tools(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    tools_dir = write_manifest_schema(repo)
    (tools_dir / "missing-install-url.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "missing-install-url",
                "kind": "external_binary_with_skill",
                "display_name": "missing-install-url",
                "upstream_repo": "example/missing-install-url",
                "homepage": "https://example.com/missing-install-url",
                "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["binary"],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
                "support_skill_source": {
                    "source_type": "upstream_repo",
                    "path": "skills/missing-install-url",
                    "ref": "main",
                },
            }
        ),
        encoding="utf-8",
    )
    manifest_path = tools_dir / "missing-install-url.json"
    with pytest.raises(ValidationError, match="must declare lifecycle.install.install_url"):
        validate_support_install_entrypoint(read_manifest(manifest_path), manifest_path)


def test_validate_integrations_rejects_unsorted_access_modes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tools_dir = write_manifest_schema(repo)
    (tools_dir / "bad-order.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "bad-order",
                "kind": "external_binary",
                "display_name": "bad-order",
                "upstream_repo": "example/bad-order",
                "homepage": "https://example.com/bad-order",
                "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["env", "binary", "degraded"],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
            }
        ),
        encoding="utf-8",
    )
    manifest_path = tools_dir / "bad-order.json"
    with pytest.raises(ValidationError, match="access_modes must stay in preferred runtime order"):
        validate_access_mode_order(read_manifest(manifest_path), manifest_path)


def test_validate_integrations_requires_capability_requirements_for_grant_and_env(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    tools_dir = write_manifest_schema(repo)
    (tools_dir / "grant-env.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "grant-env",
                "kind": "external_binary",
                "display_name": "grant-env",
                "upstream_repo": "example/grant-env",
                "homepage": "https://example.com/grant-env",
                "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["grant", "env", "degraded"],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
            }
        ),
        encoding="utf-8",
    )
    manifest_path = tools_dir / "grant-env.json"
    with pytest.raises(
        ValidationError, match="grant access requires capability_requirements.grant_ids"
    ):
        validate_capability_requirements(read_manifest(manifest_path), manifest_path)


def test_validate_integrations_rejects_unsorted_config_layers(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tools_dir = write_manifest_schema(repo)
    (tools_dir / "bad-layers.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "bad-layers",
                "kind": "external_binary",
                "display_name": "bad-layers",
                "upstream_repo": "example/bad-layers",
                "homepage": "https://example.com/bad-layers",
                "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["grant", "env", "degraded"],
                "capability_requirements": {
                    "grant_ids": ["demo.grant"],
                    "env_vars": ["DEMO_TOKEN"],
                },
                "config_layers": [
                    {
                        "layer_id": "env-fallback",
                        "layer_type": "env",
                        "summary": "Use env fallback.",
                    },
                    {
                        "layer_id": "grant-first",
                        "layer_type": "grant",
                        "summary": "Use runtime grant first.",
                    },
                ],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
            }
        ),
        encoding="utf-8",
    )
    manifest_path = tools_dir / "bad-layers.json"
    with pytest.raises(ValidationError, match="config_layers must stay in preferred order"):
        validate_config_layers(read_manifest(manifest_path), manifest_path)


def test_doctor_detects_missing_materialized_support_from_previous_sync(
    tmp_path: Path, monkeypatch
) -> None:
    repo = seed_control_plane_repo(tmp_path)
    plugin_root = tmp_path / "plugin"
    monkeypatch.setenv("CHARNESS_CACHE_HOME", str(tmp_path / "cache-home"))
    monkeypatch.setenv("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", "1")
    manifest = load_capabilities(repo)[0]
    sync_one(repo, manifest, execute=True, upstream_checkouts={}, plugin_root=plugin_root)
    generated_skill_root = plugin_root / "support" / "demo-tool-wrapper"
    shutil.rmtree(generated_skill_root)

    doctor_payload = inspect_manifest(repo, manifest, write=True, skip_release_probe=False)
    assert doctor_payload["doctor_status"] == "support-missing"
    assert doctor_payload["support_sync"]["status"] == "missing"
    assert doctor_payload["support_sync"]["missing_paths"] == ["support/demo-tool-wrapper"]
    assert doctor_payload["support_sync"]["action_required"] is True
    assert (
        doctor_payload["support_sync"]["suggested_command"]
        == "charness tool sync-support demo-tool"
    )
    assert (
        "Previously materialized support skill paths are missing."
        in doctor_payload["next_steps"][0]
    )


def test_doctor_missing_manual_tool_is_advisory_exit_zero_for_script_and_cli(
    tmp_path: Path,
) -> None:
    repo = seed_control_plane_repo(tmp_path)
    (repo / "bin" / "demo-tool").unlink()

    doctor = run_loaded_script_main(
        "doctor.py",
        doctor_module,
        "--repo-root",
        str(repo),
        "--skip-release-probe",
    )
    assert doctor.returncode == 0, doctor.stderr
    doctor_payload = yaml.safe_load(doctor.stdout)
    assert doctor_payload[0]["doctor_status"] == "missing"
    assert doctor_payload[0]["doctor_disposition"] == "advisory-install-needed"


def test_doctor_missing_advisory_script_tool_is_exit_zero(tmp_path: Path) -> None:
    repo = seed_control_plane_repo(tmp_path)
    manifest_path = repo / "integrations" / "tools" / "demo-tool.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["lifecycle"]["install"]["mode"] = "script"
    manifest["lifecycle"]["install"]["commands"] = ["./install-demo-tool"]
    manifest["doctor_policy"] = "advisory"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (repo / "bin" / "demo-tool").unlink()

    doctor = run_loaded_script_main(
        "doctor.py",
        doctor_module,
        "--repo-root",
        str(repo),
        "--skip-release-probe",
    )
    assert doctor.returncode == 0, doctor.stderr
    doctor_payload = yaml.safe_load(doctor.stdout)
    assert doctor_payload[0]["doctor_status"] == "missing"
    assert doctor_payload[0]["doctor_disposition"] == "advisory-install-needed"


def test_doctor_reuses_package_manager_prefix_probe_for_batch(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = seed_control_plane_repo(tmp_path)
    monkeypatch.setenv("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", "1")
    manifest_path = repo / "integrations" / "tools" / "demo-tool.json"
    second_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    second_manifest["tool_id"] = "demo-tool-two"
    (repo / "integrations" / "tools" / "demo-tool-two.json").write_text(
        json.dumps(second_manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    calls = 0

    def fake_prefixes() -> dict[str, str]:
        nonlocal calls
        calls += 1
        return {}

    monkeypatch.setattr(doctor_module, "detect_package_manager_prefixes", fake_prefixes)
    monkeypatch.setattr(
        sys,
        "argv",
        ["doctor.py", "--repo-root", str(repo), "--skip-release-probe"],
    )

    assert doctor_module.main() == 0
    payload = yaml.safe_load(capsys.readouterr().out)
    assert {item["tool_id"] for item in payload} == {"demo-tool", "demo-tool-two"}
    assert calls == 1


def test_defuddle_manifest_missing_binary_is_advisory() -> None:
    manifest = json.loads(
        (ROOT / "integrations" / "tools" / "defuddle.json").read_text(encoding="utf-8")
    )

    assert manifest["doctor_policy"] == "advisory"
    assert "degraded" in manifest["access_modes"]


def test_advisory_doctor_policy_requires_a_declared_degraded_mode() -> None:
    """`integrations/tools/README.md` allows `doctor_policy: advisory` ONLY when the
    consuming workflow has an explicit degraded path. That rule lived as prose, and a
    v6.0.0 release-checklist item asserted the opposite for `nose` -- which declares no
    degraded mode -- so nothing was red while the checklist demanded an unreachable
    disposition. Executable here so the pairing cannot drift again.

    Blind class: this reads DECLARED manifest fields. It cannot see whether a tool's
    real consumer actually degrades, only whether the manifest claims a degraded mode.
    """
    for path in sorted((ROOT / "integrations" / "tools").glob("*.json")):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if manifest.get("doctor_policy") != "advisory":
            continue
        assert "degraded" in manifest.get("access_modes", []), (
            f"{path.name} declares doctor_policy: advisory without a `degraded` access mode. "
            "integrations/tools/README.md conditions advisory on the CONSUMING WORKFLOW having a "
            "degraded path; a declared `degraded` access mode is this check's proxy for that, not "
            "the README rule itself. If this tool's consumer really degrades, say so in access_modes"
        )


def test_nose_stays_blocking_because_it_has_no_degraded_path() -> None:
    """Pins the three nose manifest values that decide its disposition. This test does
    NOT observe the verdict -- that is
    `test_script_install_required_policy_tool_missing_is_blocking_exit_one` below, and
    the two only together cover what this one's name suggests alone.

    The release adapter previously carried a prose expectation for this case;
    that expectation was unreachable at the tag and is now covered by the executable
    doctor assertions below.
    """
    manifest = json.loads(
        (ROOT / "integrations" / "tools" / "nose.json").read_text(encoding="utf-8")
    )

    assert manifest["doctor_policy"] == "required"
    assert "degraded" not in manifest["access_modes"]

    assert manifest["lifecycle"]["install"]["mode"] == "script"


def test_script_install_required_policy_tool_missing_is_blocking_exit_one(
    tmp_path: Path, monkeypatch
) -> None:
    """The verdict half of the test above: drive the real doctor over a seeded tool
    carrying nose's two decisive values (`mode: script`, `doctor_policy: required`) and
    observe `blocking-install-needed` with exit 1.

    Mirror of `test_doctor_missing_advisory_script_tool_is_exit_zero`, which pins the
    advisory arm of the same ladder. Widening the ladder so a required/script tool goes
    advisory turns this red; a manifest-only assertion could not.

    The fallback-manifest env var is REQUIRED for the exit-code half to mean anything:
    without it `_load_manifests_merged` folds this repo's real manifests into the tmp
    repo, and `doctor.py` returns 1 if ANY result blocks -- so on a host missing `nose`
    or `agent-browser` the assertion would pass on an unrelated tool.

    Fidelity limit: the seeded demo-tool declares a `support_skill_source` and a
    `degraded` access mode, neither of which nose has. It escapes the support-missing
    branch only because the seeded repo has no prior lock, where nose escapes it by
    declaring no support source at all. The ladder arm reached is the same; the route to
    it is not.
    """
    monkeypatch.setenv("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", "1")
    repo = seed_control_plane_repo(tmp_path)
    manifest_path = repo / "integrations" / "tools" / "demo-tool.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["lifecycle"]["install"]["mode"] = "script"
    manifest["lifecycle"]["install"]["commands"] = ["./install-demo-tool"]
    manifest["doctor_policy"] = "required"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (repo / "bin" / "demo-tool").unlink()

    doctor = run_loaded_script_main(
        "doctor.py",
        doctor_module,
        "--repo-root",
        str(repo),
        "--skip-release-probe",
    )
    assert doctor.returncode == 1, doctor.stdout
    doctor_payload = yaml.safe_load(doctor.stdout)
    assert doctor_payload[0]["doctor_status"] == "missing"
    assert doctor_payload[0]["doctor_disposition"] == "blocking-install-needed"


def test_doctor_accepts_manifest_without_healthcheck(tmp_path: Path, monkeypatch) -> None:
    repo = seed_control_plane_repo(tmp_path)
    monkeypatch.setenv("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", "1")
    write_lock(repo)
    manifest_path = repo / "integrations" / "tools" / "demo-tool.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["checks"].pop("healthcheck")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    validate = run_loaded_script_main(
        "validate_integrations.py",
        validate_integrations_module,
        "--repo-root",
        str(repo),
    )
    assert validate.returncode == 0, validate.stderr

    payload = inspect_manifest(
        repo, load_capabilities(repo)[0], write=False, skip_release_probe=True
    )
    assert payload["doctor_status"] == "ok"
    assert payload["healthcheck"]["ok"] is True
    assert payload["healthcheck"]["status"] == "not-configured"
    assert payload["healthcheck"]["skipped"] is True

    env = os.environ.copy()
    env["PATH"] = f"{repo / 'bin'}:{env.get('PATH', '')}"
    cli_doctor = run_loaded_script_main(
        "doctor.py",
        doctor_module,
        "--repo-root",
        str(repo),
        "--skip-release-probe",
        env=env,
    )
    assert cli_doctor.returncode == 0, cli_doctor.stderr
    # The retired per-tool line ("demo-tool: ok ... healthcheck=not-configured")
    # was a strict projection of these payload keys; assert them at the source.
    cli_payload = yaml.safe_load(cli_doctor.stdout)
    assert cli_payload[0]["tool_id"] == "demo-tool"
    assert cli_payload[0]["doctor_status"] == "ok"
    assert cli_payload[0]["healthcheck"]["status"] == "not-configured"


def test_doctor_reports_not_ready_when_readiness_check_fails(tmp_path: Path, monkeypatch) -> None:
    repo = seed_control_plane_repo(tmp_path)
    monkeypatch.setenv("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", "1")
    (repo / ".demo-ready").unlink()

    doctor_payload = inspect_manifest(
        repo, load_capabilities(repo)[0], write=True, skip_release_probe=False
    )
    assert doctor_payload["doctor_status"] == "not-ready"
    payload = doctor_payload["readiness"]
    assert payload["ok"] is False
    assert payload["failed_checks"] == ["demo-ready-file"]


# Deliberately NOT `release_only`. This is the only observer of a public CLI
# surface contract (`charness tool doctor` exit code + payload shape), and it sat
# in the lane no standing gate runs -- so a flag rename broke it and nothing said
# so until an operator hit the same break by hand. `release_only` means "excluded
# from standing pre-push", which is the wrong home for an assertion about a
# command a consumer runs on day one.
#
# That decision is RECORDED, not just argued here: this test is listed in
# `scripts/check_test_repo_copy_invariants.STANDING_COPY_HEAVY_TESTS`, which holds
# the measured cost and the rejected alternative. The decision previously lived
# only in this comment while the guard forbade it, so the guard failed for a week
# behind a skipped broad gate. Change one and the other refuses.
def test_tool_doctor_cli_returns_nonzero_for_blocking_disposition(
    tmp_path: Path, seeded_charness_repo: Path
) -> None:
    repo = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)
    tools_dir = repo / "integrations" / "tools"
    for manifest_path in tools_dir.glob("*.json"):
        if manifest_path.name not in {"manifest.schema.json", "demo-tool.json"}:
            manifest_path.unlink()
    seeded = seed_control_plane_repo(tmp_path / "seeded")
    shutil.copy2(seeded / "integrations" / "tools" / "demo-tool.json", tools_dir / "demo-tool.json")
    (repo / ".demo-ready").write_text("ready\n", encoding="utf-8")
    (repo / "bin").mkdir(exist_ok=True)
    shutil.copy2(seeded / "bin" / "demo-tool", repo / "bin" / "demo-tool")
    (repo / "bin" / "demo-tool").chmod(0o755)
    (repo / ".demo-ready").unlink()

    # `--detail`, not `--json`: this call was half-migrated -- the flag still named
    # the removed hidden JSON mode while the assertion below already parsed YAML.
    # argparse rejects it with exit 2, so the returncode assertion failed FIRST and
    # reported the wrong cause, and the whole test is `release_only`, so the
    # standing battery never ran it.
    cli_doctor = run_script(
        "charness",
        "tool",
        "doctor",
        "--repo-root",
        str(repo),
        "--detail",
        "--no-write-locks",
        "demo-tool",
    )

    assert cli_doctor.returncode == 1, cli_doctor.stderr
    cli_payload = yaml.safe_load(cli_doctor.stdout)
    demo_doctor = cli_payload["results"]["demo-tool"]["doctor"]
    assert demo_doctor["doctor_status"] == "not-ready"
    assert demo_doctor["doctor_disposition"] == "blocking-failure"


def test_doctor_skip_release_probe_preserves_local_readiness_without_release_lookup(
    tmp_path: Path, monkeypatch
) -> None:
    repo = seed_control_plane_repo(tmp_path)
    monkeypatch.setenv("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", "1")
    manifest_path = repo / "integrations" / "tools" / "demo-tool.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["homepage"] = "https://github.com/example/demo-tool"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    monkeypatch.setenv(
        "CHARNESS_RELEASE_PROBE_FIXTURES", str(tmp_path / "missing-release-fixtures.json")
    )

    doctor_payload = inspect_manifest(
        repo, load_capabilities(repo)[0], write=True, skip_release_probe=True
    )
    assert doctor_payload["doctor_status"] == "ok"
    assert doctor_payload["readiness"]["ok"] is True
    assert "release" not in doctor_payload
    lock_payload = json.loads(
        (repo / "integrations" / "locks" / "demo-tool.json").read_text(encoding="utf-8")
    )
    assert lock_payload["doctor"]["doctor_status"] == "ok"
    assert "release" not in lock_payload


def test_doctor_reads_support_owned_capability_metadata(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setenv("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", "1")
    support_dir = repo / "skills" / "support" / "gather-slack"
    locks_dir = repo / "integrations" / "locks"
    support_dir.mkdir(parents=True)
    locks_dir.mkdir(parents=True)
    (repo / "skills" / "support" / "capability.schema.json").write_text(
        (ROOT / "skills" / "support" / "capability.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (support_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: gather-slack",
                'description: "Slack runtime."',
                "---",
                "",
                "# Gather Slack",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (support_dir / "capability.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "capability_id": "gather-slack",
                "kind": "support_runtime",
                "display_name": "Slack gather",
                "summary": "Support-owned Slack runtime.",
                "support_skill_path": "skills/support/gather-slack/SKILL.md",
                "supports_public_skills": ["gather"],
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["grant", "env", "degraded"],
                "capability_requirements": {
                    "grant_ids": ["slack.history"],
                    "env_vars": ["SLACK_BOT_TOKEN"],
                },
                "config_layers": [
                    {
                        "layer_id": "slack-grant",
                        "layer_type": "grant",
                        "summary": "Prefer runtime grant first.",
                    },
                    {"layer_id": "slack-env", "layer_type": "env", "summary": "Fallback to env."},
                ],
                "readiness_checks": [
                    {
                        "check_id": "slack-ready",
                        "summary": "Slack runtime is ready.",
                        "commands": ["true"],
                        "success_criteria": ["exit_code:0"],
                    }
                ],
                "version_expectation": {"policy": "advisory", "constraint": "local"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    payload = inspect_manifest(
        repo, load_capabilities(repo)[0], write=True, skip_release_probe=False
    )
    assert payload["tool_id"] == "gather-slack"
    assert payload["kind"] == "support_runtime"
    assert payload["support_state"] == "native-support"
    assert payload["support_discovery"]["status"] == "native"
    assert (
        payload["support_discovery"]["support_skill_path"] == "skills/support/gather-slack/SKILL.md"
    )
    assert payload["doctor_status"] == "ok"
    assert payload["access_modes"] == ["grant", "env", "degraded"]

    lock_payload = json.loads((locks_dir / "gather-slack.json").read_text(encoding="utf-8"))
    assert lock_payload["manifest_path"] == "skills/support/gather-slack/capability.json"
    assert lock_payload["doctor"]["kind"] == "support_runtime"


def test_validate_integrations_accepts_dependencies_referencing_known_tool(tmp_path: Path) -> None:
    repo = seed_control_plane_repo(tmp_path)
    write_lock(repo)
    deps = {"schema_version": 1, "tool_dependencies": ["demo-tool"]}
    (repo / "integrations" / "tools" / "dependencies.json").write_text(
        json.dumps(deps, indent=2) + "\n", encoding="utf-8"
    )
    (repo / "integrations" / "tools" / "dependencies.schema.json").write_text(
        DEPENDENCIES_SCHEMA,
        encoding="utf-8",
    )

    result = run_loaded_script_main(
        "validate_integrations.py",
        validate_integrations_module,
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 0, result.stderr
    assert "1 declared tool dependencies" in result.stdout


def test_validate_integrations_rejects_dependencies_with_unknown_tool(tmp_path: Path) -> None:
    repo = seed_control_plane_repo(tmp_path)
    write_lock(repo)
    deps = {"schema_version": 1, "tool_dependencies": ["demo-tool", "ghost-tool"]}
    (repo / "integrations" / "tools" / "dependencies.json").write_text(
        json.dumps(deps, indent=2) + "\n", encoding="utf-8"
    )
    (repo / "integrations" / "tools" / "dependencies.schema.json").write_text(
        DEPENDENCIES_SCHEMA,
        encoding="utf-8",
    )

    result = run_loaded_script_main(
        "validate_integrations.py",
        validate_integrations_module,
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 1
    assert "unknown tool_ids" in result.stderr
    assert "ghost-tool" in result.stderr


def test_install_tools_add_dependency_creates_and_extends_dependencies_file(tmp_path: Path) -> None:
    repo = seed_control_plane_repo(tmp_path)
    (repo / "integrations" / "tools" / "dependencies.schema.json").write_text(
        DEPENDENCIES_SCHEMA,
        encoding="utf-8",
    )

    bin_dir = repo / "bin"
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:/usr/bin:/bin"

    first = run_loaded_script_main(
        "install_tools.py",
        install_tools_module,
        "--repo-root",
        str(repo),
        "--tool-id",
        "demo-tool",
        "--execute",
        "--add-dependency",
        env=env,
    )
    assert first.returncode == 0, first.stderr
    payload = yaml.safe_load(first.stdout)
    assert payload[0]["status"] in {"installed", "already-installed"}
    assert payload[0]["dependency_added"] is True
    deps_path = repo / "integrations" / "tools" / "dependencies.json"
    deps = json.loads(deps_path.read_text(encoding="utf-8"))
    assert deps == {"schema_version": 1, "tool_dependencies": ["demo-tool"]}

    second = run_loaded_script_main(
        "install_tools.py",
        install_tools_module,
        "--repo-root",
        str(repo),
        "--tool-id",
        "demo-tool",
        "--execute",
        "--add-dependency",
        env=env,
    )
    assert second.returncode == 0, second.stderr
    payload2 = yaml.safe_load(second.stdout)
    assert payload2[0]["dependency_added"] is False
    deps_after = json.loads(deps_path.read_text(encoding="utf-8"))
    assert deps_after == deps


def test_validate_integrations_refuses_a_lock_pointing_at_a_non_owner_json_file(
    tmp_path: Path,
) -> None:
    """Existing + parseable is not the same question as "is this the lock's owner".

    The lock schema constrains `manifest_path` to any non-empty string, so a stale
    lock naming `integrations/tools/manifest.schema.json` -- a file this validator
    explicitly EXCLUDES from the owned manifest set -- existed, parsed, and counted
    toward the validated-lock total. The release review named this exact file.
    """
    repo = seed_control_plane_repo(tmp_path)
    schema_reference = "integrations/tools/manifest.schema.json"
    assert (repo / schema_reference).is_file(), "the counterexample needs the excluded file present"
    lock_path = write_lock(repo, tool_id="stale-tool", manifest_path=schema_reference)

    result = run_loaded_script_main(
        "validate_integrations.py", validate_integrations_module, "--repo-root", str(repo)
    )

    assert result.returncode != 0
    assert lock_path.name in result.stderr
    assert "not a discovered tool manifest or support capability" in result.stderr


def test_validate_integrations_refuses_a_lock_whose_tool_id_names_another_owner(
    tmp_path: Path,
) -> None:
    """A lock must not claim an identity its referenced manifest does not declare."""
    repo = seed_control_plane_repo(tmp_path)
    lock_path = write_lock(repo, tool_id="not-the-demo-tool")

    result = run_loaded_script_main(
        "validate_integrations.py", validate_integrations_module, "--repo-root", str(repo)
    )

    assert result.returncode != 0
    assert lock_path.name in result.stderr
    assert "does not match the identity" in result.stderr
