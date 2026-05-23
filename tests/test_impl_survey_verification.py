from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "public" / "impl" / "scripts" / "survey_verification.py"


def _load_module():
    name = "impl_survey_verification"
    cached = sys.modules.get(name)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_detect_lint_gate_empty_repo_returns_not_detected(tmp_path: Path) -> None:
    module = _load_module()
    result = module.detect_lint_gate(tmp_path)
    assert result == {"detected": False, "command": None, "surface": None, "source": None}


def test_detect_lint_gate_prefers_lefthook_when_lint_keyword_present(tmp_path: Path) -> None:
    module = _load_module()
    (tmp_path / "lefthook.yml").write_text(
        "pre-commit:\n  commands:\n    lint:\n      run: ruff check\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text(
        json.dumps({"scripts": {"lint": "eslint ."}}),
        encoding="utf-8",
    )
    result = module.detect_lint_gate(tmp_path)
    assert result["detected"] is True
    assert result["surface"] == "lefthook"


def test_detect_lint_gate_falls_through_when_lefthook_has_no_lint(tmp_path: Path) -> None:
    module = _load_module()
    (tmp_path / "lefthook.yml").write_text(
        "pre-commit:\n  commands:\n    test:\n      run: pytest\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text(
        json.dumps({"scripts": {"lint": "eslint ."}}),
        encoding="utf-8",
    )
    result = module.detect_lint_gate(tmp_path)
    assert result["detected"] is True
    assert result["surface"] == "package_json"
    assert result["command"] == "npm run lint"


def test_detect_lint_gate_picks_pnpm_when_lockfile_present(tmp_path: Path) -> None:
    module = _load_module()
    (tmp_path / "package.json").write_text(
        json.dumps({"scripts": {"lint": "eslint ."}}),
        encoding="utf-8",
    )
    (tmp_path / "pnpm-lock.yaml").write_text("lockfileVersion: '6.0'\n", encoding="utf-8")
    result = module.detect_lint_gate(tmp_path)
    assert result["command"] == "pnpm run lint"


def test_detect_lint_gate_rejects_bare_tool_ruff_table(tmp_path: Path) -> None:
    """`[tool.ruff]` with no `lint` subtable is not a standing lint gate."""
    module = _load_module()
    (tmp_path / "pyproject.toml").write_text(
        "[tool.ruff]\nline-length = 100\n",
        encoding="utf-8",
    )
    result = module.detect_lint_gate(tmp_path)
    assert result == {"detected": False, "command": None, "surface": None, "source": None}


def test_detect_lint_gate_accepts_tool_ruff_lint_subtable(tmp_path: Path) -> None:
    module = _load_module()
    (tmp_path / "pyproject.toml").write_text(
        "[tool.ruff]\nline-length = 100\n\n[tool.ruff.lint]\nselect = [\"E\", \"F\"]\n",
        encoding="utf-8",
    )
    result = module.detect_lint_gate(tmp_path)
    assert result["detected"] is True
    assert result["command"] == "ruff check ."
    assert result["surface"] == "ruff_config"


def test_detect_lint_gate_accepts_cargo(tmp_path: Path) -> None:
    module = _load_module()
    (tmp_path / "Cargo.toml").write_text("[package]\nname = \"demo\"\n", encoding="utf-8")
    result = module.detect_lint_gate(tmp_path)
    assert result["command"] == "cargo clippy --all-targets"


def test_detect_lint_gate_accepts_go(tmp_path: Path) -> None:
    module = _load_module()
    (tmp_path / "go.mod").write_text("module demo\n", encoding="utf-8")
    result = module.detect_lint_gate(tmp_path)
    assert result["command"] == "go vet ./..."


def test_detect_lint_gate_accepts_githooks_pre_commit(tmp_path: Path) -> None:
    module = _load_module()
    (tmp_path / ".githooks").mkdir()
    (tmp_path / ".githooks" / "pre-commit").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    result = module.detect_lint_gate(tmp_path)
    assert result["detected"] is True
    assert result["surface"] == "git_hook"
    assert result["stage"] == "pre-commit"


def test_survey_emits_lint_gate_block_in_json(tmp_path: Path) -> None:
    """End-to-end: the CLI surface includes the lint_gate block + summary key."""
    (tmp_path / "pyproject.toml").write_text(
        "[tool.ruff.lint]\nselect = [\"E\"]\n", encoding="utf-8"
    )
    result = subprocess.run(
        ["python3", str(SCRIPT), "--repo-root", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["lint_gate"]["detected"] is True
    assert payload["lint_gate"]["command"] == "ruff check ."
    assert payload["summary"]["lint_gate_detected"] is True
    assert any("Lint gate detected" in warning for warning in payload["warnings"])


def test_survey_emits_not_detected_warning_when_no_gate(tmp_path: Path) -> None:
    result = subprocess.run(
        ["python3", str(SCRIPT), "--repo-root", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["lint_gate"]["detected"] is False
    assert payload["summary"]["lint_gate_detected"] is False
    assert any("No standing lint gate detected" in warning for warning in payload["warnings"])
