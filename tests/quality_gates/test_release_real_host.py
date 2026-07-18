from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from tests.script_main import load_script_module, run_loaded_script_main

from .release_publish_fixtures import _seed_publish_release_repo
from .support import ROOT

_PLANNER = load_script_module(
    "plan_release_run_for_release_real_host_test",
    ROOT / "skills" / "public" / "release" / "scripts" / "plan_release_run.py",
)

_REAL_HOST = load_script_module(
    "check_real_host_proof_for_test",
    ROOT / "skills" / "public" / "release" / "scripts" / "check_real_host_proof.py",
)

_RELEASE_DELTA = load_script_module(
    "release_delta_for_release_real_host_test",
    ROOT / "skills" / "public" / "release" / "scripts" / "release_delta.py",
)


def _run_real_host_proof(*args: str):
    return run_loaded_script_main("check_real_host_proof.py", _REAL_HOST, "--detail", *args)


def test_release_real_host_proof_triggers_for_support_tool_surfaces() -> None:
    result = _run_real_host_proof(
        "--repo-root",
        str(ROOT),
        "--paths",
        "integrations/tools/tokei.json",
        "scripts/doctor.py",
        "plugins/charness/scripts/install_tools.py",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["required"] is True
    assert payload["surface_hits"] == ["external-tool-control-plane"]
    assert any("tool doctor" in item for item in payload["checklist"])
    assert any("tool install" in item for item in payload["checklist"])
    assert any("manifest-supported path" in item for item in payload["checklist"])


def test_release_real_host_proof_stays_off_for_unrelated_derived_plugin_scripts() -> None:
    result = _run_real_host_proof(
        "--repo-root",
        str(ROOT),
        "--paths",
        "plugins/charness/scripts/run-quality.sh",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["required"] is False
    assert payload["surface_hits"] == []
    assert payload["path_hits"] == []


def test_release_real_host_proof_stays_off_for_unrelated_paths() -> None:
    result = _run_real_host_proof(
        "--repo-root",
        str(ROOT),
        "--paths",
        "docs/retro-self-improvement-spec.md",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["required"] is False
    assert payload["checklist"] == []


def test_release_real_host_proof_clean_changeset_does_not_trigger() -> None:
    result = _run_real_host_proof(
        "--repo-root",
        str(ROOT),
        "--paths",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["required"] is False
    assert payload["changed_paths"] == []
    assert payload["surface_hits"] == []
    assert payload["path_hits"] == []
    assert payload["checklist"] == []


def test_release_real_host_proof_supports_hidden_json_and_summary_output() -> None:
    json_result = run_loaded_script_main(
        "check_real_host_proof.py",
        _REAL_HOST,
        "--repo-root",
        str(ROOT),
        "--json",
        "--paths",
        "docs/retro-self-improvement-spec.md",
    )
    summary_result = run_loaded_script_main(
        "check_real_host_proof.py",
        _REAL_HOST,
        "--repo-root",
        str(ROOT),
        "--paths",
        "docs/retro-self-improvement-spec.md",
    )

    assert json_result.returncode == summary_result.returncode == 0
    assert json.loads(json_result.stdout)["required"] is False
    assert summary_result.stdout.startswith("real_host=not-required: ")
    assert summary_result.stderr == ""


def test_release_real_host_proof_renders_surface_errors_as_yaml(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_surface_error(_repo_root: Path, _changed_paths: list[str]) -> dict[str, object]:
        raise _REAL_HOST.SurfaceError("invalid test surfaces manifest")

    monkeypatch.setattr(_REAL_HOST, "build_payload", raise_surface_error)

    result = run_loaded_script_main(
        "check_real_host_proof.py",
        _REAL_HOST,
        "--repo-root",
        str(ROOT),
        "--paths",
        "README.md",
    )

    assert result.returncode == 1
    assert result.stdout == ""
    payload = yaml.safe_load(result.stderr)
    assert payload["error"] == "invalid test surfaces manifest"
    assert payload["checklist"] == []


@pytest.mark.parametrize(
    "text, stderr",
    [(True, "text failure" + chr(10)), (False, bytes([255]) + b"binary failure" + bytes([10]))],
)
def test_release_delta_includes_text_and_binary_git_failure_diagnostics(
    monkeypatch: pytest.MonkeyPatch, text: bool, stderr: str | bytes
) -> None:
    monkeypatch.setattr(
        _RELEASE_DELTA.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=7, stderr=stderr, stdout=""),
    )

    with pytest.raises(ValueError) as exc_info:
        _RELEASE_DELTA._git(Path("/repo"), "rev-parse", "missing", text=text)

    expected_stderr = stderr if isinstance(stderr, str) else os.fsdecode(stderr)
    assert str(exc_info.value) == "\n".join(
        ["git rev-parse missing failed", "exit_code: 7", expected_stderr.strip()]
    )


def test_release_delta_rejects_full_looking_but_noncanonical_range(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    base_sha = "a" * 40
    head_sha = "b" * 40
    monkeypatch.setattr(_RELEASE_DELTA, "resolve_full_commit", lambda _repo, _ref: "c" * 40)

    with pytest.raises(ValueError, match="immutable full lowercase object IDs"):
        _RELEASE_DELTA.collect_immutable_range(Path("/repo"), f"{base_sha}..{head_sha}")


def test_release_real_host_immutable_range_matches_explicit_paths(tmp_path: Path) -> None:
    repo, _remote, _bin = _seed_publish_release_repo(tmp_path)
    adapter = repo / ".agents" / "release-adapter.yaml"
    adapter.write_text(
        adapter.read_text(encoding="utf-8")
        + "\nreal_host_required_path_globs:\n- README.md\nreal_host_checklist:\n- Verify on a clean host.\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Configure proof"], cwd=repo, check=True)
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()
    (repo / "README.md").write_text("# Changed\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Change readme"], cwd=repo, check=True)
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()

    ranged = _run_real_host_proof(
        "--repo-root", str(repo), "--changed-range", f"{base_sha}..{head_sha}"
    )
    explicit = _run_real_host_proof("--repo-root", str(repo), "--paths", "README.md")

    assert ranged.returncode == explicit.returncode == 0
    ranged_payload = yaml.safe_load(ranged.stdout)
    explicit_payload = yaml.safe_load(explicit.stdout)
    for key in ("required", "surface_hits", "path_hits", "checklist", "reason"):
        assert ranged_payload[key] == explicit_payload[key]
    assert "changed_paths" not in ranged_payload
    assert ranged_payload["evidence_provenance"]["path_count"] == 1
    assert ranged_payload["evidence_provenance"]["base_sha"] == base_sha
    assert ranged_payload["evidence_provenance"]["head_sha"] == head_sha


def test_release_real_host_range_requires_full_immutable_shas() -> None:
    result = _run_real_host_proof("--repo-root", str(ROOT), "--changed-range", "HEAD^..HEAD")

    assert result.returncode != 0
    assert "immutable full lowercase object IDs" in result.stderr


def test_release_real_host_range_supports_sha256_repositories(tmp_path: Path) -> None:
    repo = tmp_path / "sha256-repo"
    init = subprocess.run(
        ["git", "init", "--object-format=sha256", "-b", "main", str(repo)],
        check=False,
        capture_output=True,
        text=True,
    )
    if init.returncode != 0:
        pytest.skip("installed Git does not support SHA-256 repositories")
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Base"], cwd=repo, check=True)
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()
    unusual_path = "line\nbreak.txt"
    (repo / unusual_path).write_text("changed\n", encoding="utf-8")
    subprocess.run(["git", "add", unusual_path], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Change"], cwd=repo, check=True)
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()

    paths, provenance = _REAL_HOST.collect_range_paths(repo, f"{base_sha}..{head_sha}")

    assert len(base_sha) == len(head_sha) == 64
    assert paths == [unusual_path]
    assert provenance == {
        "base_sha": base_sha,
        "head_sha": head_sha,
        "path_count": 1,
        "paths_sha256": hashlib.sha256(os.fsencode(unusual_path) + b"\0").hexdigest(),
    }


def test_release_real_host_proof_fails_loud_on_unresolved_surface_id(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: consumer",
                "output_dir: charness-artifacts/release",
                "package_id: consumer",
                "packaging_manifest_path: packaging/consumer.json",
                "checked_in_plugin_root: plugins/consumer",
                "sync_command: true",
                "quality_command: true",
                "real_host_required_surfaces:",
                "  - release-packagng",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "release-packaging",
                        "description": "release packaging surface",
                        "source_paths": ["scripts/release/**"],
                        "derived_paths": ["dist/**"],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = _run_real_host_proof(
        "--repo-root",
        str(repo),
        "--paths",
        "scripts/release/verify-public-release.mjs",
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    payload = yaml.safe_load(result.stderr)
    assert payload["required"] is False
    assert payload["configuration_status"] == "broken"
    assert payload["unresolved_trigger_surfaces"] == ["release-packagng"]
    assert payload["checklist"] == []
    assert "real_host_required_surfaces" in payload["reason"]
    assert "Fix the typo" in payload["remediation"]


def test_release_skill_enforces_phase_barriers_for_mutating_commands(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Guard against CI's detached HEAD. This test asserts the planner's static
    # phase-barrier / gate structure, not branch resolution, but `build_plan`
    # calls the real `current_branch(ROOT)`, which raises "detached HEAD is not
    # supported" on a detached checkout (GitHub Actions) while passing locally on
    # a named branch. Pin it to a named branch, mirroring test_release_run_planner.
    monkeypatch.setattr(_PLANNER, "current_branch", lambda _repo: "main")
    payload = _PLANNER.build_plan(
        SimpleNamespace(
            repo_root=ROOT,
            remote="origin",
            critique_artifact=None,
            critique_blocked=None,
            publish_current=False,
            part=None,
            set_version=None,
        )
    )

    assert "references/publication-boundary.md" in {item["path"] for item in payload["required_reads"]}
    assert any("publish-dry-run" in item and "publish-execute" in item for item in payload["phase_barriers"])
    assert any("parallelize" in item and "git" in item for item in payload["phase_barriers"])
    assert all({"id", "cost_tier", "trust_model", "run_when"} <= set(packet) for packet in payload["gate_packets"])
