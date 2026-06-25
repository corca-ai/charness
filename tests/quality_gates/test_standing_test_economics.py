from __future__ import annotations

import builtins
import getpass
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import yaml

from .support import ROOT

SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_standing_test_economics.py"
LIB = ROOT / "skills" / "public" / "quality" / "scripts" / "standing_test_economics_lib.py"
SURFACE_LIB = ROOT / "skills" / "public" / "quality" / "scripts" / "surface_marker_lib.py"


def _load_inventory_lib() -> ModuleType:
    spec = importlib.util.spec_from_file_location("standing_test_economics_lib_for_test", LIB)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_surface_marker_lib() -> ModuleType:
    spec = importlib.util.spec_from_file_location("surface_marker_lib_for_test", SURFACE_LIB)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_inventory_cli() -> ModuleType:
    spec = importlib.util.spec_from_file_location("inventory_standing_test_economics_for_test", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_standing_test_economics_surfaces_runner_startup_shape(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "package.json").write_text(
        json.dumps({"scripts": {"test:unit": "node --test --import tsx tests/**/*.test.ts"}}),
        encoding="utf-8",
    )
    tests = repo / "tests"
    tests.mkdir()
    for index in range(52):
        (tests / f"case{index}.test.ts").write_text("import { spawnSync } from 'node:child_process';\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["test_file_count"] == 52
    finding_types = {finding["type"] for finding in payload["findings"]}
    assert {
        "many_test_files",
        "node_test_isolation_unknown",
        "transpiler_startup_surface",
        "nested_cli_fanout",
    }.issubset(finding_types)


def test_standing_test_economics_summary_omits_full_nested_cli_list(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    tests = repo / "tests"
    tests.mkdir()
    for index in range(12):
        (tests / f"test_case_{index}.py").write_text(
            "import subprocess\n\n"
            "def test_case():\n"
            "    subprocess.run(['true'], check=True)\n",
            encoding="utf-8",
        )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--summary"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["nested_cli_file_count"] == 12
    assert payload["nested_cli_release_only_file_count"] == 0
    assert payload["nested_cli_standing_or_mixed_file_count"] == 12
    assert len(payload["nested_cli_files_sample"]) == 10
    assert len(payload["nested_cli_standing_or_mixed_files_sample"]) == 10
    assert "nested_cli_files" not in payload
    assert "nested_cli_standing_or_mixed_files" not in payload
    assert "--json" in payload["summary_note"]
    assert {finding["type"] for finding in payload["findings"]} == {"nested_cli_fanout"}
    assert payload["findings"][0]["severity"] == "advisory"
    assert "interpretation" in payload


def test_standing_test_economics_summary_yaml_is_compact_and_parseable(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    tests = repo / "tests"
    tests.mkdir()
    for index in range(12):
        (tests / f"test_case_{index}.py").write_text(
            "import subprocess\n\n"
            "def test_case():\n"
            "    subprocess.run(['true'], check=True)\n",
            encoding="utf-8",
        )

    json_result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--summary"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    yaml_result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--summary-yaml"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = yaml.safe_load(yaml_result.stdout)

    assert payload["nested_cli_file_count"] == 12
    assert payload["nested_cli_standing_or_mixed_file_count"] == 12
    assert "nested_cli_files" not in payload
    assert len(yaml_result.stdout.encode("utf-8")) < len(json_result.stdout.encode("utf-8"))


def test_standing_test_economics_summary_yaml_reports_missing_pyyaml(monkeypatch) -> None:
    cli = _load_inventory_cli()
    original_import = builtins.__import__

    def missing_yaml_import(name, *args, **kwargs):
        if name == "yaml":
            raise ImportError("missing yaml")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", missing_yaml_import)

    try:
        cli._dump_yaml({"ok": True})
    except SystemExit as exc:
        assert "PyYAML is required for --summary-yaml" in str(exc)
    else:
        raise AssertionError("expected missing PyYAML to raise SystemExit")


def test_standing_test_economics_splits_module_release_only_nested_cli_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_module_release_only.py").write_text(
        "import pytest\nimport subprocess\n\n"
        "pytestmark = pytest.mark.release_only\n\n"
        "def test_case():\n"
        "    subprocess.run(['true'], check=True)\n",
        encoding="utf-8",
    )
    (tests / "test_mixed_release_only.py").write_text(
        "import pytest\nimport subprocess\n\n"
        "@pytest.mark.release_only\n"
        "def test_release_case():\n"
        "    subprocess.run(['true'], check=True)\n\n"
        "def test_standing_case():\n"
        "    assert True\n",
        encoding="utf-8",
    )
    (tests / "test_standing.py").write_text(
        "import subprocess\n\n"
        "def test_case():\n"
        "    subprocess.run(['true'], check=True)\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--summary"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["nested_cli_file_count"] == 3
    assert payload["nested_cli_release_only_file_count"] == 1
    assert payload["nested_cli_release_only_files_sample"] == ["tests/test_module_release_only.py"]
    assert payload["nested_cli_standing_or_mixed_file_count"] == 2
    assert payload["nested_cli_standing_or_mixed_files_sample"] == [
        "tests/test_mixed_release_only.py",
        "tests/test_standing.py",
    ]
    assert "nested_cli_release_only_files" not in payload


def test_surface_marker_lib_skips_unreadable_files(tmp_path: Path, monkeypatch) -> None:
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    repo.mkdir()
    nested_path = repo / "test_nested.py"
    release_path = repo / "test_release.py"
    nested_path.write_text("import subprocess\nsubprocess.run(['true'])\n", encoding="utf-8")
    release_path.write_text("pytestmark = pytest.mark.release_only\n", encoding="utf-8")

    original_read_text = Path.read_text

    def flaky_read_text(path: Path, *args, **kwargs):
        if path == nested_path:
            raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "bad byte")
        if path == release_path:
            raise OSError("gone")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", flaky_read_text)

    assert lib.nested_cli_files(repo, [nested_path]) == []
    assert lib.module_release_only_files(repo, [release_path.name]) == []


def test_standing_test_economics_ignores_generated_mutant_tree(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_real.py").write_text("def test_real():\n    assert True\n", encoding="utf-8")
    mutant_tests = repo / "mutants" / "tests"
    mutant_tests.mkdir(parents=True)
    (mutant_tests / "test_generated.py").write_text("def test_generated():\n    assert True\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["test_file_count"] == 1


def test_standing_test_economics_reports_pytest_temp_footprint(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    pytest_root = tmp_path / f"pytest-of-{getpass.getuser()}" / "pytest-0" / "popen-gw0"
    seed = pytest_root / "charness-repo-seed0"
    top_test = pytest_root / "test_expensive0"
    seed.mkdir(parents=True)
    top_test.mkdir()
    (seed / "payload.bin").write_bytes(b"x" * 11)
    (top_test / "payload.bin").write_bytes(b"x" * 13)

    env = {**os.environ, "PYTEST_DEBUG_TEMPROOT": str(tmp_path)}
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    payload = json.loads(result.stdout)
    footprint = payload["pytest_temp_footprint"]

    assert footprint["status"] == "available"
    assert footprint["session_count"] == 1
    assert footprint["worker_dir_count"] == 1
    assert footprint["total_disk_bytes"] >= 24
    assert footprint["seed_totals"]["charness-repo-seed"]["count"] == 1
    assert footprint["seed_totals"]["charness-repo-seed"]["bytes"] >= 11
    assert footprint["seed_totals"]["charness-repo-seed"]["disk_bytes"] >= 11
    assert footprint["top_test_dirs"][0]["bytes"] >= 13
    assert footprint["top_test_dirs"][0]["disk_bytes"] >= 13


def test_pytest_tmp_retention_keeps_only_failed_session_dirs() -> None:
    config = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert 'tmp_path_retention_count = 1' in config
    assert 'tmp_path_retention_policy = "failed"' in config


def test_standing_test_economics_does_not_double_count_nested_seed_dirs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    pytest_root = tmp_path / f"pytest-of-{getpass.getuser()}" / "pytest-0" / "popen-gw0"
    outer = pytest_root / "charness-repo-seed0"
    nested = outer / "charness-repo-seed-nested"
    nested.mkdir(parents=True)
    (outer / "outer.bin").write_bytes(b"x" * 11)
    (nested / "nested.bin").write_bytes(b"x" * 13)

    env = {**os.environ, "PYTEST_DEBUG_TEMPROOT": str(tmp_path)}
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    footprint = json.loads(result.stdout)["pytest_temp_footprint"]

    assert footprint["seed_totals"]["charness-repo-seed"]["count"] == 1
    assert footprint["seed_totals"]["charness-repo-seed"]["bytes"] >= 24
    assert footprint["seed_totals"]["charness-repo-seed"]["disk_bytes"] >= 24


def test_standing_test_economics_emits_interpretation_self_declaration(tmp_path: Path) -> None:
    # Advisory-interpretation contract rollout (#322): the test-economics trend is
    # an inference-layer proxy; assert both halves — the 4-field self-declaration
    # in the inventory output and the paired consumer-must-answer requirement in
    # the consuming `quality` reference.
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "tests").mkdir()
    (repo / "tests" / "test_real.py").write_text("def test_real():\n    assert True\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    interpretation = json.loads(result.stdout)["interpretation"]
    assert set(interpretation) == {"measures", "proxy_for", "blind_spots", "interpretation_question"}
    assert all(interpretation[field].strip() for field in interpretation)

    plain = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "INTERPRETATION" in plain.stdout
    assert "Consumer must answer first" in plain.stdout
    assert "intentional" in plain.stdout  # the load-bearing blind spot

    reference = (
        ROOT / "skills" / "public" / "quality" / "references" / "automation-promotion.md"
    ).read_text(encoding="utf-8")
    assert "inventory_standing_test_economics.py" in reference


def test_pytest_temp_footprint_tolerates_disappearing_temp_dirs(tmp_path: Path, monkeypatch) -> None:
    lib = _load_inventory_lib()
    root = tmp_path / f"pytest-of-{getpass.getuser()}"
    session = root / "pytest-0"
    worker = session / "popen-gw0"
    stale = root / "garbage-stale"
    worker.mkdir(parents=True)
    stale.mkdir(parents=True)

    original_iterdir = Path.iterdir

    def racy_iterdir(path: Path):
        if path == root:
            yield session
            raise FileNotFoundError(stale)
        yield from original_iterdir(path)

    monkeypatch.setenv("PYTEST_DEBUG_TEMPROOT", str(tmp_path))
    monkeypatch.setattr(lib, "_du_bytes", lambda *args: None)
    monkeypatch.setattr(Path, "iterdir", racy_iterdir)

    footprint = lib._pytest_temp_footprint()

    assert footprint["status"] == "available"
    assert footprint["session_count"] == 1
    assert footprint["worker_dir_count"] == 1


def test_pytest_temp_iter_helpers_skip_missing_and_stale_children(
    tmp_path: Path,
    monkeypatch,
) -> None:
    lib = _load_inventory_lib()
    root = tmp_path / "root"
    root.mkdir()
    file_path = root / "payload.bin"
    stale_path = root / "stale.bin"
    file_path.write_bytes(b"x")
    stale_path.write_bytes(b"y")

    missing = tmp_path / "missing"
    original_iterdir = Path.iterdir
    original_stat = Path.stat

    def flaky_iterdir(path: Path):
        if path == missing:
            raise FileNotFoundError(path)
        return original_iterdir(path)

    def flaky_stat(path: Path, *args, **kwargs):
        if path == stale_path:
            raise FileNotFoundError(path)
        return original_stat(path, *args, **kwargs)

    monkeypatch.setattr(Path, "iterdir", flaky_iterdir)
    monkeypatch.setattr(Path, "stat", flaky_stat)

    assert list(lib._iter_child_stats(missing)) == []
    assert [item.st_size for item in lib._iter_file_stats(root)] == [1]
