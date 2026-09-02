"""#342: validate-adapters runs the owning integration's manifest schema.

An `.agents/<name>-adapter.yaml` edit must fail at the commit boundary when
`integrations/<name>/manifest.schema.json` rejects it, instead of landing as a
clean commit and failing slices later at the runtime emitter.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

from scripts.gates.validate_adapters import (
    ValidationError,
    integration_schema_path,
    validate_adapter_integration_schema,
)
from tests.quality_gates.support import run_script as run_repo_script

jsonschema = pytest.importorskip("jsonschema")

REPO_ROOT = Path(__file__).resolve().parent.parent
SIBLING_INTEGRATIONS = ("worktree",)


def _seed_pair(tmp_path: Path, name: str, adapter_text: str, *, with_schema: bool = True) -> Path:
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    adapter_path = agents_dir / f"{name}-adapter.yaml"
    adapter_path.write_text(adapter_text, encoding="utf-8")
    if with_schema:
        schema_dir = tmp_path / "integrations" / name
        schema_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(
            REPO_ROOT / "integrations" / name / "manifest.schema.json",
            schema_dir / "manifest.schema.json",
        )
    return adapter_path


@pytest.mark.parametrize("name", SIBLING_INTEGRATIONS)
def test_schema_forbidden_key_rejected_per_sibling(tmp_path: Path, name: str) -> None:
    example = (REPO_ROOT / "integrations" / name / "adapter.example.yaml").read_text(encoding="utf-8")
    adapter_path = _seed_pair(tmp_path, name, example + "\nnot_in_schema_342: true\n")
    with pytest.raises(ValidationError, match="rejected by integration schema"):
        validate_adapter_integration_schema(adapter_path)


@pytest.mark.parametrize("name", SIBLING_INTEGRATIONS)
def test_example_adapter_passes_per_sibling(tmp_path: Path, name: str) -> None:
    example = (REPO_ROOT / "integrations" / name / "adapter.example.yaml").read_text(encoding="utf-8")
    adapter_path = _seed_pair(tmp_path, name, example)
    validate_adapter_integration_schema(adapter_path)


@pytest.mark.parametrize("name", SIBLING_INTEGRATIONS)
def test_live_repo_adapter_passes_per_sibling(name: str) -> None:
    validate_adapter_integration_schema(REPO_ROOT / ".agents" / f"{name}-adapter.yaml")


def test_repo_without_schema_inherits_nothing(tmp_path: Path) -> None:
    adapter_path = _seed_pair(tmp_path, "worktree", "bogus: true\n", with_schema=False)
    assert integration_schema_path(adapter_path) is None
    validate_adapter_integration_schema(adapter_path)


def test_tools_integration_is_not_a_sibling() -> None:
    assert (REPO_ROOT / "integrations" / "tools" / "manifest.schema.json").is_file()
    assert not (REPO_ROOT / ".agents" / "tools-adapter.yaml").exists()


def test_broken_schema_json_is_a_hard_error(tmp_path: Path) -> None:
    adapter_path = _seed_pair(tmp_path, "worktree", "version: 1\nenabled: false\n")
    (tmp_path / "integrations" / "worktree" / "manifest.schema.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(ValidationError, match="integration manifest schema is unreadable"):
        validate_adapter_integration_schema(adapter_path)


def test_non_mapping_adapter_rejected_with_schema_present(tmp_path: Path) -> None:
    adapter_path = _seed_pair(tmp_path, "worktree", "- just\n- a\n- list\n")
    with pytest.raises(ValidationError, match="must parse to a mapping"):
        validate_adapter_integration_schema(adapter_path)


def test_unparseable_adapter_yaml_rejected_with_schema_present(tmp_path: Path) -> None:
    adapter_path = _seed_pair(tmp_path, "worktree", "key: [unclosed\n")
    with pytest.raises(ValidationError, match="failed to parse"):
        validate_adapter_integration_schema(adapter_path)


@pytest.mark.parametrize(
    "missing_dep",
    [
        "jsonschema",
        # `yaml` was strict-xfail here while the YAML output migration had hoisted
        # `import yaml` to module scope in scripts/gates/validate_adapters.py, which turned
        # this gate from degrades-to-no-gate into dies-at-IMPORT on a PyYAML-less
        # interpreter. The import is back under the same `except ImportError: return`
        # guard as jsonschema, so both dependencies are asserted the same way again.
        "yaml",
    ],
)
def test_missing_runtime_dependency_degrades_to_no_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, missing_dep: str
) -> None:
    adapter_path = _seed_pair(tmp_path, "worktree", "bogus: true\n")
    monkeypatch.setitem(sys.modules, missing_dep, None)
    validate_adapter_integration_schema(adapter_path)


def test_cli_main_rejects_schema_violating_adapter(tmp_path: Path) -> None:
    # Pins the main() wiring: without the validate_adapter_integration_schema
    # call, this tmp repo passes the generic shape checks and exits 0.
    _seed_pair(tmp_path, "worktree", "version: 1\nrepo: tmp\nenabled: false\nnot_in_schema_342: true\n")
    completed = run_repo_script(
        "scripts/gates/validate_adapters.py",
        "--repo-root",
        str(tmp_path),
    )
    assert completed.returncode == 1
    assert "not_in_schema_342" in completed.stderr


def test_cli_main_rejects_invalid_retro_packet_sections(tmp_path: Path) -> None:
    agents = tmp_path / ".agents"
    agents.mkdir(parents=True)
    (agents / "retro-adapter.yaml").write_text(
        """\
version: 1
repo: demo
packet_sections:
  - id: bad
    title: Bad
    content_kind: script
    content: wrong field
""",
        encoding="utf-8",
    )

    completed = run_repo_script(
        "scripts/gates/validate_adapters.py",
        "--repo-root",
        str(tmp_path),
    )

    assert completed.returncode == 1
    assert "content_kind=script requires `command`" in completed.stderr


def test_cli_main_preserves_generic_floor_for_retro_adapter(tmp_path: Path) -> None:
    agents = tmp_path / ".agents"
    agents.mkdir(parents=True)
    (agents / "retro-adapter.yaml").write_text("packet_sections: []\n", encoding="utf-8")

    completed = run_repo_script(
        "scripts/gates/validate_adapters.py",
        "--repo-root",
        str(tmp_path),
    )

    assert completed.returncode == 1
    # The floor this test names -- the gate still refuses a retro adapter with no
    # `version` -- is unchanged. The MESSAGE changed, deliberately: the old wording
    # ("must be a positive integer") described the old predicate, which accepted
    # `version: 9` and `version: true` while every runtime resolver refused them. Keeping
    # it would have left the gate telling operators a rule it no longer enforces.
    assert "version is required" in completed.stderr


def test_schema_violation_names_offending_key(tmp_path: Path) -> None:
    adapter_path = _seed_pair(tmp_path, "worktree", "version: 1\nenabled: false\nnot_in_schema_342: true\n")
    with pytest.raises(ValidationError, match="not_in_schema_342"):
        validate_adapter_integration_schema(adapter_path)


def test_each_sibling_schema_is_strict_about_unknown_keys() -> None:
    for name in SIBLING_INTEGRATIONS:
        schema = json.loads(
            (REPO_ROOT / "integrations" / name / "manifest.schema.json").read_text(encoding="utf-8")
        )
        assert schema.get("additionalProperties") is False
