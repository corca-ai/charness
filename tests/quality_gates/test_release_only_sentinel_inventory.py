from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
import yaml

from tests.script_main import run_loaded_script_main

from .seeding_support import load_module

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_release_only_sentinels.py"


def _load_inventory():
    return load_module("inventory_release_only_sentinels", SCRIPT)


def _run_cli(*args: str):
    return run_loaded_script_main("inventory_release_only_sentinels.py", _load_inventory(), *args)


def _assert_help_pairs(output: str, expected_pairs: dict[str, str]) -> None:
    """Assert each option's wrapped argparse block contains its own help text."""
    for option, fragment in expected_pairs.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"


def test_release_only_sentinel_help_describes_repo_root_and_yaml_modes(
    capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    inventory = _load_inventory()
    monkeypatch.setattr(sys, "argv", ["inventory_release_only_sentinels.py", "--help"])

    with pytest.raises(SystemExit) as excinfo:
        inventory.main()

    assert excinfo.value.code == 0
    _assert_help_pairs(
        capsys.readouterr().out,
        {
            "--repo-root": "Repository root containing the pytest files to inspect.",
            "--summary": "Emit compact YAML counts and samples instead of full per-test attribution.",
            "--detail": "Emit full per-test attribution as YAML.",
        },
    )


def test_release_only_sentinel_inventory_reports_counts_and_sentinel_names(
    tmp_path: Path,
) -> None:
    inventory = _load_inventory()
    test_file = tmp_path / "tests" / "test_release_flow.py"
    test_file.parent.mkdir()
    test_file.write_text(
        "\n".join(
            [
                "import pytest",
                "",
                "@pytest.mark.release_only",
                "def test_release_boundary_pushes_tag():",
                "    pass",
                "",
                "def test_release_dry_run_fails_closed_when_tag_fetch_fails():",
                "    pass",
                "",
                "def test_release_requested_review_gate_blocks_missing_review():",
                "    pass",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = inventory.inventory(tmp_path, [test_file])

    assert payload["release_only_test_count"] == 1
    assert payload["standing_test_count"] == 2
    item = payload["files"][0]
    assert item["standing_sentinel_names"] == [
        "test_release_dry_run_fails_closed_when_tag_fetch_fails",
        "test_release_requested_review_gate_blocks_missing_review",
    ]
    assert item["findings"] == []


def test_release_only_sentinel_inventory_warns_when_no_standing_sentinel(
    tmp_path: Path,
) -> None:
    inventory = _load_inventory()
    test_file = tmp_path / "tests" / "test_release_flow.py"
    test_file.parent.mkdir()
    test_file.write_text(
        "\n".join(
            [
                "import pytest",
                "",
                "@pytest.mark.release_only",
                "def test_release_boundary_pushes_tag():",
                "    pass",
                "",
                "def test_release_metadata_shape():",
                "    pass",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = inventory.inventory(tmp_path, [test_file])

    assert payload["findings"] == [
        {
            "path": "tests/test_release_flow.py",
            "severity": "advisory",
            "type": "missing_standing_sentinel",
            "message": "release_only tests exist but no obvious standing sentinel name was found",
        }
    ]


def test_release_only_sentinel_inventory_cli_accepts_selected_files(tmp_path: Path) -> None:
    test_file = tmp_path / "tests" / "test_release_flow.py"
    test_file.parent.mkdir()
    test_file.write_text(
        "\n".join(
            [
                "import pytest",
                "",
                "pytestmark = pytest.mark.release_only",
                "",
                "def test_release_boundary_pushes_tag():",
                "    pass",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = _run_cli(
        "--repo-root", str(tmp_path), "--path", "tests/test_release_flow.py", "--detail"
    )

    payload = yaml.safe_load(result.stdout)
    assert payload["release_only_test_count"] == 1
    assert payload["standing_test_count"] == 0
    assert "files" in payload


def test_release_only_sentinel_inventory_summary_omits_full_test_names(tmp_path: Path) -> None:
    test_file = tmp_path / "tests" / "test_release_flow.py"
    test_file.parent.mkdir()
    test_file.write_text(
        "\n".join(
            [
                "import pytest",
                "",
                "@pytest.mark.release_only",
                "def test_release_boundary_pushes_tag():",
                "    pass",
                "",
                "def test_release_metadata_shape():",
                "    pass",
                "",
            ]
        ),
        encoding="utf-8",
    )

    full = _run_cli(
        "--repo-root", str(tmp_path), "--path", "tests/test_release_flow.py", "--detail"
    )
    summary = _run_cli(
        "--repo-root", str(tmp_path), "--path", "tests/test_release_flow.py", "--summary"
    )

    payload = yaml.safe_load(summary.stdout)
    assert payload["release_only_test_count"] == 1
    assert payload["missing_standing_sentinel_file_count"] == 1
    assert payload["missing_standing_sentinel_files_sample"] == ["tests/test_release_flow.py"]
    assert "files" not in payload
    assert "release_only_test_names" not in summary.stdout
    assert len(summary.stdout.encode("utf-8")) < len(full.stdout.encode("utf-8"))


def test_release_only_sentinel_inventory_uses_structural_marker_detection(
    tmp_path: Path,
) -> None:
    inventory = _load_inventory()
    test_file = tmp_path / "tests" / "test_release_flow.py"
    test_file.parent.mkdir()
    test_file.write_text(
        "\n".join(
            [
                "import pytest",
                "",
                "@pytest.mark.skip(reason='mentions release_only but is not the marker')",
                "def test_release_name_mentions_marker_text_only():",
                "    pass",
                "",
                "class TestReleaseFlow:",
                "    pytestmark = [pytest.mark.release_only]",
                "",
                "    async def test_async_release_boundary(self):",
                "        pass",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = inventory.inventory(tmp_path, [test_file])

    assert payload["release_only_test_count"] == 1
    assert payload["standing_test_count"] == 1
    assert payload["files"][0]["release_only_test_names"] == [
        "TestReleaseFlow.test_async_release_boundary"
    ]
