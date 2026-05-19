from __future__ import annotations

import json
from pathlib import Path

from .support import run_script

RESOLVE = "skills/public/create-skill/scripts/resolve_adapter.py"
INIT = "skills/public/create-skill/scripts/init_adapter.py"


def test_create_skill_adapter_resolver_reports_visible_missing_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(RESOLVE, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["found"] is False
    assert payload["valid"] is True
    assert payload["data"]["output_dir"] == "charness-artifacts/create-skill"
    assert payload["field_state"]["implementation_identity_terms"] == "unset"
    assert "Using generic topology vocabulary" in "\n".join(payload["warnings"])


def test_create_skill_adapter_resolver_accepts_repo_topology_terms(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    adapter_dir = repo / ".agents"
    adapter_dir.mkdir(parents=True)
    (adapter_dir / "create-skill-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/create-skill",
                "implementation_identity_terms:",
                "  - canonical implementation",
                "placement_terms:",
                "  - host-facing registration",
                "intentional_fork_signals:",
                "  - data isolation",
                "topology_verification_hints:",
                "  - Report shared implementation versus intentional fork.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(RESOLVE, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["found"] is True
    assert payload["valid"] is True
    assert payload["data"]["placement_terms"] == ["host-facing registration"]
    assert payload["field_state"]["topology_verification_hints"] == "configured"


def test_create_skill_adapter_resolver_rejects_invalid_list_field(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    adapter_dir = repo / ".agents"
    adapter_dir.mkdir(parents=True)
    (adapter_dir / "create-skill-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "implementation_identity_terms: canonical implementation",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(RESOLVE, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["found"] is True
    assert payload["valid"] is False
    assert "implementation_identity_terms must be a list of strings" in payload["errors"]


def test_create_skill_adapter_resolver_rejects_unsupported_version(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    adapter_dir = repo / ".agents"
    adapter_dir.mkdir(parents=True)
    (adapter_dir / "create-skill-adapter.yaml").write_text(
        "version: 2\nimplementation_identity_terms:\n  - shared implementation\n",
        encoding="utf-8",
    )

    result = run_script(RESOLVE, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["found"] is True
    assert payload["valid"] is False
    assert "version must be 1" in payload["errors"]


def test_create_skill_adapter_resolver_rejects_top_level_list(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    adapter_dir = repo / ".agents"
    adapter_dir.mkdir(parents=True)
    (adapter_dir / "create-skill-adapter.yaml").write_text("- just a list\n", encoding="utf-8")

    result = run_script(RESOLVE, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["found"] is True
    assert payload["valid"] is False
    assert "top-level mapping" in "\n".join(payload["errors"])


def test_create_skill_adapter_resolver_rejects_unparseable_mapping(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    adapter_dir = repo / ".agents"
    adapter_dir.mkdir(parents=True)
    (adapter_dir / "create-skill-adapter.yaml").write_text("not yaml\n", encoding="utf-8")

    result = run_script(RESOLVE, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["found"] is True
    assert payload["valid"] is False
    assert "supported create-skill adapter mapping entries" in "\n".join(payload["errors"])


def test_create_skill_adapter_resolver_reports_explicit_empty_lists(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    adapter_dir = repo / ".agents"
    adapter_dir.mkdir(parents=True)
    (adapter_dir / "create-skill-adapter.yaml").write_text(
        "version: 1\nimplementation_identity_terms: []\n",
        encoding="utf-8",
    )

    result = run_script(RESOLVE, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["found"] is True
    assert payload["valid"] is True
    assert payload["field_state"]["implementation_identity_terms"] == "explicit-empty"


def test_create_skill_adapter_resolver_warns_on_compatibility_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "create-skill-adapter.yaml").write_text(
        "version: 1\nimplementation_identity_terms:\n  - shared implementation\n",
        encoding="utf-8",
    )

    result = run_script(RESOLVE, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["found"] is True
    assert payload["valid"] is True
    assert "compatibility fallback" in "\n".join(payload["warnings"])


def test_create_skill_init_adapter_writes_canonical_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(INIT, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    adapter = repo / ".agents" / "create-skill-adapter.yaml"
    assert adapter.is_file()
    text = adapter.read_text(encoding="utf-8")
    assert "implementation_identity_terms:" in text
    assert "host-facing registration" in text
