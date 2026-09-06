"""Readiness failures of the issue-owned launch happen before any reviewer."""

import os
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from tests.quality_gates.support import ROOT, run_script
from tests.quality_gates.test_semantic_review_command import _fake_codex, _repo
from tests.script_loader import load_script_module


def _module():
    return load_script_module(
        "issue_resolution_readiness_test",
        ROOT / "skills/public/issue/scripts/issue_review_resolution.py",
    )


def _args(root: Path, **changes) -> Namespace:
    values = dict(
        repo="corca-ai/charness",
        number=[42],
        reviewed_path=["subject.md"],
        lens="recurrence",
        repo_root=root,
        attempt_id=None,
        goal_lineage_file=None,
        dry_run=False,
    )
    return Namespace(**(values | changes))


@pytest.mark.parametrize(
    "changes",
    [
        {"repo": ""},
        {"repo": "not-qualified"},
        {"repo": "a/b#42"},
        {"number": []},
        {"number": [0]},
        {"number": [True]},
        {"number": [42, 42]},
        {"reviewed_path": []},
        {"reviewed_path": [""]},
        {"reviewed_path": ["a", "a"]},
        {"reviewed_path": ["../outside"]},
        {"reviewed_path": ["/outside"]},
        {"lens": " "},
    ],
)
def test_invalid_inputs_refuse_without_loading_a_runner(
    tmp_path: Path, monkeypatch, changes
) -> None:
    module = _module()
    monkeypatch.setattr(module, "_load_package_script", lambda *_args: pytest.fail("must not load"))
    emitted = []
    assert module.command_review_resolution(_args(tmp_path, **changes), emit=emitted.append) == 2
    assert emitted[0]["reason_code"] == "input-invalid"
    assert emitted[0]["reviewer_started"] is False
    assert emitted[0]["approval_eligible"] is False


def test_symlink_outside_review_root_refuses(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    (root / "subject.md").symlink_to(outside)
    emitted = []
    assert _module().command_review_resolution(_args(root), emit=emitted.append) == 2
    assert "resolves outside" in emitted[0]["error"]


@pytest.mark.parametrize("number", ["0", "-1", "not-a-number"])
def test_parser_rejects_nonpositive_or_noninteger_numbers(number: str) -> None:
    module = load_script_module(
        "issue_resolution_parser_test", ROOT / "skills/public/issue/scripts/issue_tool.py"
    )
    with pytest.raises(SystemExit) as refusal:
        module.build_parser().parse_args(
            [
                "review-resolution",
                "--repo",
                "corca-ai/charness",
                "--number",
                number,
                "--reviewed-path",
                "subject.md",
                "--lens",
                "recurrence",
            ]
        )
    assert refusal.value.code == 2


def test_missing_package_parts_refuse(tmp_path: Path, monkeypatch) -> None:
    module = _module()
    with pytest.raises(RuntimeError, match="package-owned script is unavailable"):
        module._load_package_script("critique", "missing-review-script.py")
    monkeypatch.setattr(module, "__file__", str(tmp_path / "issue_review_resolution.py"))
    with pytest.raises(RuntimeError, match="skill_runtime_bootstrap.py not found"):
        module._load_package_script("critique", "run_review.py")


def test_citation_scanner_error_is_a_structured_preflight_refusal(
    tmp_path: Path, monkeypatch
) -> None:
    module = _module()

    class ScanFailure(Exception):
        pass

    def failed_scan(*_args):
        raise ScanFailure("git check-ignore failed")

    monkeypatch.setattr(
        module,
        "_load_package_script",
        lambda *_args: SimpleNamespace(
            selected_doc_violations=failed_scan,
            ValidationError=ScanFailure,
        ),
    )
    emitted = []
    assert module.command_review_resolution(_args(tmp_path), emit=emitted.append) == 2
    assert emitted[0]["reason_code"] == "evidence-durability"
    assert emitted[0]["error"] == "git check-ignore failed"
    assert emitted[0]["reviewer_started"] is False


@pytest.mark.parametrize(
    "script",
    [
        "skills/public/issue/scripts/issue_tool.py",
        "plugins/charness/skills/issue/scripts/issue_tool.py",
    ],
)
@pytest.mark.boundary_contract(
    reason="observe source and installed packet preparation, including Git, while refusing any reviewer launch"
)
def test_source_and_installed_dry_run_never_start_a_worker(
    tmp_path: Path, monkeypatch, script: str
) -> None:
    _repo(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")
    monkeypatch.setenv("PATH", str(bin_dir), prepend=os.pathsep)
    result = run_script(
        script,
        "review-resolution",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--reviewed-path",
        "reviewed.txt",
        "--lens",
        "recurrence",
        "--dry-run",
        "--attempt-id",
        "dry-ready",
    )
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 0, result.stdout + result.stderr
    assert payload["reviewer_started"] is False
    assert payload["approval_eligible"] is False
    assert not (bin_dir / "review-called").exists()
