from __future__ import annotations

import subprocess
from pathlib import Path

from .support import init_git_repo, run_script


def _bootstrap_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    spec_dir = repo / "charness-artifacts" / "spec"
    spec_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("artifacts/\n", encoding="utf-8")
    init_git_repo(repo, ".gitignore")
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)
    (repo / "artifacts").mkdir()
    (repo / "artifacts" / "eval-summary.json").write_text("{}\n", encoding="utf-8")
    return repo


def test_flags_gitignored_backtick_citation(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(
        "# Demo Spec\n\nProof: see `artifacts/eval-summary.json` for the field.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "gitignored target" in result.stderr
    assert "artifacts/eval-summary.json" in result.stderr


def test_flags_gitignored_markdown_link_citation(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(
        "# Demo Spec\n\nSee [eval](../../artifacts/eval-summary.json) for proof.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "gitignored target" in result.stderr


def test_passes_when_reproduction_marker_present(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(
        "# Demo Spec\n\nRun `make eval` to refresh `artifacts/eval-summary.json` <!-- reproduction-source -->.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_passes_when_path_is_checked_in(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    proof = repo / "charness-artifacts" / "spec" / "demo-proof.md"
    proof.write_text("# Demo Proof\n\nClaim: ok.\n", encoding="utf-8")
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(
        "# Demo Spec\n\nSee [proof](./demo-proof.md) for the claim.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_skips_paths_inside_fenced_code_blocks(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(
        "# Demo Spec\n\n```\ncat artifacts/eval-summary.json\n```\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_real_repo_passes(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo_root))
    assert result.returncode == 0, result.stderr


def test_marker_matching_is_case_insensitive(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(
        "# Demo Spec\n\nRefresh `artifacts/eval-summary.json` <!-- Reproduction-Source -->.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_marker_on_unrelated_line_does_not_exempt(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(
        "# Demo Spec\n\n<!-- reproduction-source -->\n\nProof: see `artifacts/eval-summary.json`.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "gitignored target" in result.stderr


def test_inline_command_with_space_is_not_flagged(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(
        "# Demo Spec\n\nRun `cat artifacts/eval-summary.json` to inspect.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_skips_when_repo_has_no_git_directory(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    spec_dir = repo / "charness-artifacts" / "spec"
    spec_dir.mkdir(parents=True)
    (spec_dir / "demo.md").write_text(
        "# Demo Spec\n\nProof: `artifacts/eval-summary.json`.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert "no git work tree" in result.stdout


def test_scope_covers_quality_release_dogfood_subdirs(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    for subdir in ("quality", "release", "dogfood", "debug", "premortem"):
        target = repo / "charness-artifacts" / subdir
        target.mkdir(parents=True, exist_ok=True)
        (target / "demo.md").write_text(
            "# Demo\n\nProof: `artifacts/eval-summary.json`.\n",
            encoding="utf-8",
        )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 1
    for subdir in ("quality", "release", "dogfood", "debug", "premortem"):
        assert f"charness-artifacts/{subdir}/demo.md" in result.stderr
