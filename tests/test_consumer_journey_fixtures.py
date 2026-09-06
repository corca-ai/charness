"""Structural and baseline checks for the bounded consumer journey packets."""

from __future__ import annotations

import ast
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
JOURNEY_ROOT = ROOT / "evals" / "fixtures" / "consumer-journeys"
FIXTURES = {
    "spec-impl-alias": {
        "prompt_files": {"spec.md", "impl.md"},
        "seed_files": {
            "AGENTS.md",
            "README.md",
            "src/__init__.py",
            "src/catalog.py",
            "tests/test_catalog.py",
        },
    },
    "create-cli-refresh": {
        "prompt_files": {"create-cli.md", "impl.md"},
        "seed_files": {
            "AGENTS.md",
            "README.md",
            "scripts/refresh_cache.py",
            "scripts/check_cache.py",
            "tests/test_current_scripts.py",
        },
    },
}


def _relative_files(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def _assert_stdlib_only(seed: Path) -> None:
    stdlib = sys.stdlib_module_names
    local_roots = {path.name for path in seed.iterdir() if path.is_dir()}
    for path in sorted(seed.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".", 1)[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split(".", 1)[0]]
            else:
                continue
            unexpected = [name for name in names if name not in stdlib and name not in local_roots]
            assert not unexpected, (
                f"{path.relative_to(seed)} imports non-stdlib modules {unexpected}"
            )


def test_consumer_journey_packet_layout_is_bounded() -> None:
    assert set(path.name for path in JOURNEY_ROOT.iterdir()) == set(FIXTURES)
    for fixture_id, contract in FIXTURES.items():
        fixture = JOURNEY_ROOT / fixture_id
        assert {path.name for path in fixture.iterdir()} == {"README.md", "prompts", "seed"}
        assert _relative_files(fixture / "prompts") == contract["prompt_files"]
        assert _relative_files(fixture / "seed") == contract["seed_files"]
        readme = (fixture / "README.md").read_text(encoding="utf-8")
        assert "python3 -m unittest discover -s tests -v" in readme
        assert "task run --skip-prepare" in readme


@pytest.mark.boundary_contract(
    reason=(
        "execute each copied dependency-free consumer seed through its documented unittest boundary"
    )
)
@pytest.mark.parametrize("fixture_id", sorted(FIXTURES))
def test_each_seed_baseline_runs_in_a_clean_consumer_copy(tmp_path: Path, fixture_id: str) -> None:
    seed = JOURNEY_ROOT / fixture_id / "seed"
    _assert_stdlib_only(seed)
    assert not any(path.name in {"plugins", "skills"} for path in seed.rglob("*"))

    consumer = tmp_path / fixture_id
    shutil.copytree(seed, consumer)
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=consumer,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"{fixture_id} baseline failed\n{result.stdout}\n{result.stderr}"


def test_spec_alias_seed_has_only_canonical_lookup() -> None:
    seed = JOURNEY_ROOT / "spec-impl-alias" / "seed"
    source = (seed / "src/catalog.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    catalog = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Catalog"
    )
    initializer = next(
        node
        for node in catalog.body
        if isinstance(node, ast.FunctionDef) and node.name == "__init__"
    )
    assert [argument.arg for argument in initializer.args.args] == ["self", "mapping"]
    assert not (seed / "docs" / "alias-resolution.md").exists()


def test_create_cli_seed_has_no_repoctl_or_cache_state() -> None:
    seed = JOURNEY_ROOT / "create-cli-refresh" / "seed"
    assert not (seed / "repoctl").exists()
    assert not (seed / ".state").exists()
    assert (seed / "scripts" / "refresh_cache.py").is_file()
    assert (seed / "scripts" / "check_cache.py").is_file()
