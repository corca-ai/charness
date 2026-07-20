from __future__ import annotations

import builtins
import getpass
import importlib.util
import json
import os
from pathlib import Path
from types import ModuleType

import yaml

from tests.script_main import load_script_module, run_loaded_script_main

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
    return load_script_module("inventory_standing_test_economics_for_test", SCRIPT)


def _run_inventory_cli(*args: str, env: dict[str, str] | None = None):
    return run_loaded_script_main(
        "inventory_standing_test_economics.py",
        _load_inventory_cli(),
        *args,
        env=env,
    )


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

    result = _run_inventory_cli("--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
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

    # Isolate the pytest-temp footprint probe to this fixture's own (session-free)
    # temp root. Without this the probe scans the machine's real pytest temp root,
    # where retained failed-session dirs surface an extra `pytest_temp_footprint`
    # finding and break the exact-set assertion below (environmental, not a repo
    # signal). The sibling footprint tests isolate the same way.
    result = _run_inventory_cli(
        "--repo-root",
        str(repo),
        "--summary",
        "--json",
        env={**os.environ, "PYTEST_DEBUG_TEMPROOT": str(tmp_path)},
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert payload["nested_cli_file_count"] == 12
    assert payload["nested_cli_all_release_only_file_count"] == 0
    assert payload["nested_cli_mixed_release_only_file_count"] == 0
    assert payload["nested_cli_standing_file_count"] == 12
    assert payload["nested_cli_release_only_file_count"] == 0
    assert payload["nested_cli_standing_or_mixed_file_count"] == 12
    assert len(payload["nested_cli_files_sample"]) == 10
    assert len(payload["nested_cli_standing_files_sample"]) == 10
    assert len(payload["nested_cli_standing_or_mixed_files_sample"]) == 10
    assert "nested_cli_files" not in payload
    assert "nested_cli_standing_or_mixed_files" not in payload
    assert "--detail" in payload["summary_note"]
    assert {finding["type"] for finding in payload["findings"]} == {"nested_cli_fanout"}
    assert payload["findings"][0]["severity"] == "advisory"
    assert payload["proof_path_review"] == {
        "status": "review_recommended",
        "detail_ref": "references/proof-path-efficiency.md",
        "observed_finding_types": ["nested_cli_fanout"],
    }
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

    json_result = _run_inventory_cli("--repo-root", str(repo), "--summary", "--json")
    yaml_result = _run_inventory_cli("--repo-root", str(repo), "--summary")
    assert json_result.returncode == 0, json_result.stderr
    assert yaml_result.returncode == 0, yaml_result.stderr
    payload = yaml.safe_load(yaml_result.stdout)

    assert payload["nested_cli_file_count"] == 12
    assert payload["nested_cli_standing_file_count"] == 12
    assert payload["nested_cli_standing_or_mixed_file_count"] == 12
    assert "nested_cli_files" not in payload
    assert len(yaml_result.stdout.encode("utf-8")) < len(json_result.stdout.encode("utf-8"))


def test_standing_test_economics_summary_yaml_falls_back_without_pyyaml(monkeypatch) -> None:
    cli = _load_inventory_cli()
    original_import = builtins.__import__

    def missing_yaml_import(name, *args, **kwargs):
        if name == "yaml":
            raise ImportError("missing yaml")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", missing_yaml_import)

    assert json.loads(cli.dump_yaml({"ok": True})) == {"ok": True}


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

    result = _run_inventory_cli("--repo-root", str(repo), "--summary", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert payload["nested_cli_file_count"] == 3
    assert payload["nested_cli_all_release_only_file_count"] == 1
    assert payload["nested_cli_all_release_only_files_sample"] == ["tests/test_module_release_only.py"]
    assert payload["nested_cli_mixed_release_only_file_count"] == 1
    assert payload["nested_cli_mixed_release_only_files_sample"] == ["tests/test_mixed_release_only.py"]
    assert payload["nested_cli_standing_file_count"] == 1
    assert payload["nested_cli_standing_files_sample"] == ["tests/test_standing.py"]
    assert payload["nested_cli_release_only_file_count"] == 1
    assert payload["nested_cli_release_only_files_sample"] == ["tests/test_module_release_only.py"]
    assert payload["nested_cli_standing_or_mixed_file_count"] == 2
    assert payload["nested_cli_standing_or_mixed_files_sample"] == [
        "tests/test_mixed_release_only.py",
        "tests/test_standing.py",
    ]
    assert "nested_cli_release_only_files" not in payload


def test_standing_test_economics_routes_empty_nested_cli_test_modules_to_standing_or_mixed(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_module_body_only.py").write_text(
        "import subprocess\nsubprocess.run(['true'], check=True)\n",
        encoding="utf-8",
    )
    (tests / "test_standing.py").write_text(
        "import subprocess\n\n"
        "def test_case():\n"
        "    subprocess.run(['true'], check=True)\n",
        encoding="utf-8",
    )

    result = _run_inventory_cli("--repo-root", str(repo), "--summary", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert payload["nested_cli_file_count"] == 2
    assert payload["nested_cli_standing_file_count"] == 1
    assert payload["nested_cli_standing_or_mixed_file_count"] == 2
    assert "tests/test_module_body_only.py" in payload["nested_cli_standing_or_mixed_files_sample"]


def test_surface_marker_lib_skips_unreadable_files(tmp_path: Path, monkeypatch) -> None:
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    repo.mkdir()
    nested_path = repo / "test_nested.py"
    release_path = repo / "test_release.py"
    broken_path = repo / "test_broken.py"
    nested_path.write_text("import subprocess\nsubprocess.run(['true'])\n", encoding="utf-8")
    release_path.write_text("pytestmark = pytest.mark.release_only\n", encoding="utf-8")
    broken_path.write_text("def broken(:\n", encoding="utf-8")

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
    assert lib.pytest_file_test_counts(repo, [nested_path.name]) == []
    assert lib.pytest_file_test_counts(repo, [broken_path.name]) == []
    assert lib.module_release_only_files(repo, [broken_path.name]) == []

    # An unreadable file ordered BEFORE a matching readable file must not
    # short-circuit the scan: the unreadable entry should only be skipped
    # (`continue`), not abort the loop (`break`), so the later match is still
    # found.
    matching_nested = repo / "test_nested_match.py"
    matching_nested.write_text("import subprocess\nsubprocess.run(['true'])\n", encoding="utf-8")
    assert lib.nested_cli_files(repo, [nested_path, matching_nested]) == [
        matching_nested.relative_to(repo).as_posix()
    ]

    matching_release = repo / "test_release_match.py"
    matching_release.write_text("pytestmark = pytest.mark.release_only\n", encoding="utf-8")
    assert lib.module_release_only_files(repo, [release_path.name, matching_release.name]) == [
        matching_release.name
    ]


def test_surface_marker_lib_handles_call_and_class_release_only_variants(tmp_path: Path) -> None:
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    repo.mkdir()
    tests = repo / "tests"
    tests.mkdir()
    module_call = tests / "test_module_call.py"
    module_tuple = tests / "test_module_tuple.py"
    class_marked = tests / "test_class_marked.py"
    class_decorated = tests / "test_class_decorated.py"
    class_direct = tests / "test_class_direct.py"
    class_standing = tests / "test_class_standing.py"
    module_call.write_text(
        "\n".join(
            [
                "import pytest",
                "import subprocess",
                "",
                "pytestmark = pytest.mark.release_only()",
                "",
                "def test_case():",
                "    subprocess.run(['true'], check=True)",
            ]
        ),
        encoding="utf-8",
    )
    module_tuple.write_text(
        "\n".join(
            [
                "import pytest",
                "import subprocess",
                "",
                "pytestmark = (pytest.mark.release_only(),)",
                "",
                "def test_case():",
                "    subprocess.run(['true'], check=True)",
            ]
        ),
        encoding="utf-8",
    )
    class_marked.write_text(
        "\n".join(
            [
                "import pytest",
                "import subprocess",
                "",
                "class TestMarked:",
                "    pytestmark = [pytest.mark.release_only()]",
                "",
                "    def test_release_case(self):",
                "        subprocess.run(['true'], check=True)",
                "",
                "    def test_second_release_case(self):",
                "        subprocess.run(['true'], check=True)",
            ]
        ),
        encoding="utf-8",
    )
    class_decorated.write_text(
        "\n".join(
            [
                "import pytest",
                "import subprocess",
                "",
                "@pytest.mark.release_only",
                "class TestDecorated:",
                "    def test_release_case(self):",
                "        subprocess.run(['true'], check=True)",
            ]
        ),
        encoding="utf-8",
    )
    class_direct.write_text(
        "\n".join(
            [
                "import pytest",
                "import subprocess",
                "",
                "class TestDirect:",
                "    def helper(self):",
                "        return None",
                "    pytestmark = pytest.mark.release_only",
                "",
                "    def test_release_case(self):",
                "        subprocess.run(['true'], check=True)",
            ]
        ),
        encoding="utf-8",
    )
    class_standing.write_text(
        "\n".join(
            [
                "import subprocess",
                "",
                "unused = 1",
                "",
                "class TestStanding:",
                "    def helper(self):",
                "        return None",
                "",
                "    def test_case(self):",
                "        subprocess.run(['true'], check=True)",
            ]
        ),
        encoding="utf-8",
    )

    assert lib.module_release_only_files(
        repo,
        [
            module_call.relative_to(repo).as_posix(),
            module_tuple.relative_to(repo).as_posix(),
            class_marked.relative_to(repo).as_posix(),
            class_decorated.relative_to(repo).as_posix(),
            class_direct.relative_to(repo).as_posix(),
            class_standing.relative_to(repo).as_posix(),
        ],
    ) == [
        module_call.relative_to(repo).as_posix(),
        module_tuple.relative_to(repo).as_posix(),
    ]

    payload = lib.pytest_file_test_counts(
        repo,
        [
            module_call.relative_to(repo).as_posix(),
            module_tuple.relative_to(repo).as_posix(),
            class_marked.relative_to(repo).as_posix(),
            class_decorated.relative_to(repo).as_posix(),
            class_direct.relative_to(repo).as_posix(),
            class_standing.relative_to(repo).as_posix(),
        ],
    )

    assert payload == [
        {
            "path": "tests/test_module_call.py",
            "test_count": 1,
            "release_only_count": 1,
            "standing_count": 0,
        },
        {
            "path": "tests/test_module_tuple.py",
            "test_count": 1,
            "release_only_count": 1,
            "standing_count": 0,
        },
        {
            "path": "tests/test_class_marked.py",
            "test_count": 2,
            "release_only_count": 2,
            "standing_count": 0,
        },
        {
            "path": "tests/test_class_decorated.py",
            "test_count": 1,
            "release_only_count": 1,
            "standing_count": 0,
        },
        {
            "path": "tests/test_class_direct.py",
            "test_count": 1,
            "release_only_count": 1,
            "standing_count": 0,
        },
        {
            "path": "tests/test_class_standing.py",
            "test_count": 1,
            "release_only_count": 0,
            "standing_count": 1,
        },
    ]


def test_surface_marker_lib_counts_function_level_release_only_tests(tmp_path: Path) -> None:
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    repo.mkdir()
    release_only = repo / "tests" / "test_release_only.py"
    mixed = repo / "tests" / "test_mixed.py"
    standing = repo / "tests" / "test_standing.py"
    release_only.parent.mkdir()
    release_only.write_text(
        "\n".join(
            [
                "import pytest",
                "import subprocess",
                "",
                "@pytest.mark.release_only",
                "def test_release_case():",
                "    subprocess.run(['true'], check=True)",
            ]
        ),
        encoding="utf-8",
    )
    mixed.write_text(
        "\n".join(
            [
                "import pytest",
                "import subprocess",
                "",
                "@pytest.mark.release_only",
                "def test_release_case():",
                "    subprocess.run(['true'], check=True)",
                "",
                "def test_standing_case():",
                "    subprocess.run(['true'], check=True)",
            ]
        ),
        encoding="utf-8",
    )
    standing.write_text(
        "\n".join(
            [
                "import subprocess",
                "",
                "def test_case():",
                "    subprocess.run(['true'], check=True)",
            ]
        ),
        encoding="utf-8",
    )

    payload = lib.pytest_file_test_counts(
        repo,
        [
            release_only.relative_to(repo).as_posix(),
            mixed.relative_to(repo).as_posix(),
            standing.relative_to(repo).as_posix(),
        ],
    )

    assert payload == [
        {
            "path": "tests/test_release_only.py",
            "test_count": 1,
            "release_only_count": 1,
            "standing_count": 0,
        },
        {
            "path": "tests/test_mixed.py",
            "test_count": 2,
            "release_only_count": 1,
            "standing_count": 1,
        },
        {
            "path": "tests/test_standing.py",
            "test_count": 1,
            "release_only_count": 0,
            "standing_count": 1,
        },
    ]


def test_surface_marker_lib_recognizes_pytest_alias_release_only_marks(tmp_path: Path) -> None:
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    repo.mkdir()
    tests = repo / "tests"
    tests.mkdir()
    module_alias = tests / "test_module_alias.py"
    function_alias = tests / "test_function_alias.py"
    standing = tests / "test_standing.py"
    module_alias.write_text(
        "\n".join(
            [
                "import pytest as pt",
                "import subprocess",
                "",
                "pytestmark = pt.mark.release_only",
                "",
                "def test_release_case():",
                "    subprocess.run(['true'], check=True)",
            ]
        ),
        encoding="utf-8",
    )
    function_alias.write_text(
        "\n".join(
            [
                "from pytest import mark as pytest_mark",
                "import subprocess",
                "",
                "@pytest_mark.release_only",
                "def test_release_case():",
                "    subprocess.run(['true'], check=True)",
                "",
                "def test_standing_case():",
                "    subprocess.run(['true'], check=True)",
            ]
        ),
        encoding="utf-8",
    )
    standing.write_text(
        "\n".join(
            [
                "import subprocess",
                "",
                "def test_case():",
                "    subprocess.run(['true'], check=True)",
            ]
        ),
        encoding="utf-8",
    )

    assert lib.module_release_only_files(
        repo,
        [
            module_alias.relative_to(repo).as_posix(),
            function_alias.relative_to(repo).as_posix(),
            standing.relative_to(repo).as_posix(),
        ],
    ) == [module_alias.relative_to(repo).as_posix()]

    payload = lib.pytest_file_test_counts(
        repo,
        [
            module_alias.relative_to(repo).as_posix(),
            function_alias.relative_to(repo).as_posix(),
            standing.relative_to(repo).as_posix(),
        ],
    )

    assert payload == [
        {
            "path": "tests/test_module_alias.py",
            "test_count": 1,
            "release_only_count": 1,
            "standing_count": 0,
        },
        {
            "path": "tests/test_function_alias.py",
            "test_count": 2,
            "release_only_count": 1,
            "standing_count": 1,
        },
        {
            "path": "tests/test_standing.py",
            "test_count": 1,
            "release_only_count": 0,
            "standing_count": 1,
        },
    ]


def test_standing_test_economics_ignores_generated_mutant_tree(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_real.py").write_text("def test_real():\n    assert True\n", encoding="utf-8")
    mutant_tests = repo / "mutants" / "tests"
    mutant_tests.mkdir(parents=True)
    (mutant_tests / "test_generated.py").write_text("def test_generated():\n    assert True\n", encoding="utf-8")

    result = _run_inventory_cli("--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
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
    result = _run_inventory_cli("--repo-root", str(repo), "--json", env=env)
    assert result.returncode == 0, result.stderr
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


def test_standing_test_economics_counts_charness_run_session_dirs(tmp_path: Path) -> None:
    # The standing runner's explicit basetemp is named `charness-run-<time_ns>` (not
    # `pytest-*`, so pytest's cleanup cannot delete it mid-run). The drill-down
    # footprint must still recognize it as a session, or it silently under-reports the
    # standing suite's own popen-gw*/seed footprint while whole-root du still counts it.
    repo = tmp_path / "repo"
    repo.mkdir()
    pytest_root = tmp_path / f"pytest-of-{getpass.getuser()}" / "charness-run-123" / "popen-gw0"
    seed = pytest_root / "charness-repo-seed0"
    seed.mkdir(parents=True)
    (seed / "payload.bin").write_bytes(b"x" * 11)

    env = {**os.environ, "PYTEST_DEBUG_TEMPROOT": str(tmp_path)}
    result = _run_inventory_cli("--repo-root", str(repo), "--json", env=env)
    assert result.returncode == 0, result.stderr
    footprint = json.loads(result.stdout)["pytest_temp_footprint"]

    assert footprint["session_count"] == 1
    assert footprint["worker_dir_count"] == 1
    assert footprint["seed_totals"]["charness-repo-seed"]["count"] == 1


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
    result = _run_inventory_cli("--repo-root", str(repo), "--json", env=env)
    assert result.returncode == 0, result.stderr
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

    result = _run_inventory_cli("--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    interpretation = json.loads(result.stdout)["interpretation"]
    assert set(interpretation) == {"measures", "proxy_for", "blind_spots", "interpretation_question"}
    assert all(interpretation[field].strip() for field in interpretation)

    plain = _run_inventory_cli("--repo-root", str(repo))
    assert plain.returncode == 0, plain.stderr
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

