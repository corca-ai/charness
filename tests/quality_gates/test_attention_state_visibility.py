from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate_attention_state_visibility.py"


def _run(repo: Path, declaration: Path, scan_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--repo-root",
            str(repo),
            "--declaration-path",
            str(declaration),
            "--scan-root",
            str(scan_root),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _write_declaration(path: Path, files: dict[str, object]) -> None:
    path.write_text(json.dumps({"files": files}, indent=2), encoding="utf-8")


def test_fails_when_attention_state_file_is_undeclared(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scan_root = repo / "scripts"
    scan_root.mkdir(parents=True)
    (scan_root / "helper.py").write_text("print('no_adapter')\n", encoding="utf-8")
    declaration = repo / "attention.json"
    _write_declaration(declaration, {})

    result = _run(repo, declaration, scan_root)

    assert result.returncode == 1
    assert "scripts/helper.py" in result.stderr
    assert "not declared" in result.stderr


def test_fails_when_declared_states_drift(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scan_root = repo / "scripts"
    scan_root.mkdir(parents=True)
    (scan_root / "helper.py").write_text("print('disabled')\n", encoding="utf-8")
    declaration = repo / "attention.json"
    _write_declaration(
        declaration,
        {
            "scripts/helper.py": {
                "states": ["skipped"],
                "visibility": ["stdout_attention"],
                "evidence_terms": ["disabled"],
                "rationale": "demo",
            }
        },
    )

    result = _run(repo, declaration, scan_root)

    assert result.returncode == 1
    assert "do not match detected states" in result.stderr


def test_fails_when_evidence_terms_are_missing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scan_root = repo / "scripts"
    scan_root.mkdir(parents=True)
    (scan_root / "helper.py").write_text("print('skipped')\n", encoding="utf-8")
    declaration = repo / "attention.json"
    _write_declaration(
        declaration,
        {
            "scripts/helper.py": {
                "states": ["skipped"],
                "visibility": ["stdout_attention"],
                "evidence_terms": ["WARNING:"],
                "rationale": "demo",
            }
        },
    )

    result = _run(repo, declaration, scan_root)

    assert result.returncode == 1
    assert "evidence_terms missing" in result.stderr


def test_passes_with_declared_visibility(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scan_root = repo / "scripts"
    scan_root.mkdir(parents=True)
    (scan_root / "helper.py").write_text("print('WARNING: skipped')\n", encoding="utf-8")
    declaration = repo / "attention.json"
    _write_declaration(
        declaration,
        {
            "scripts/helper.py": {
                "states": ["skipped"],
                "visibility": ["stdout_attention"],
                "evidence_terms": ["WARNING:"],
                "rationale": "demo",
            }
        },
    )

    result = _run(repo, declaration, scan_root)

    assert result.returncode == 0, result.stderr
    assert "Validated attention-state visibility declarations" in result.stdout


def test_default_paths_support_exported_plugin_layout(tmp_path: Path) -> None:
    repo = tmp_path / "plugin"
    script_dir = repo / "scripts"
    quality_dir = repo / "skills" / "quality" / "scripts"
    support_dir = repo / "support" / "markdown-preview" / "scripts"
    declaration_dir = repo / "skills" / "quality" / "references"
    script_dir.mkdir(parents=True)
    quality_dir.mkdir(parents=True)
    support_dir.mkdir(parents=True)
    declaration_dir.mkdir(parents=True)
    (script_dir / "root_helper.py").write_text("print('WARNING: no_adapter')\n", encoding="utf-8")
    (quality_dir / "skill_helper.py").write_text("print('ADVISORY: prose_review_status')\n", encoding="utf-8")
    (support_dir / "support_helper.py").write_text("print('disabled by config')\n", encoding="utf-8")
    _write_declaration(
        declaration_dir / "attention-state-visibility.json",
        {
            "scripts/root_helper.py": {
                "states": ["no_adapter"],
                "visibility": ["stdout_attention"],
                "evidence_terms": ["WARNING:"],
                "rationale": "demo",
            },
            "skills/public/quality/scripts/skill_helper.py": {
                "states": ["prose_review_status"],
                "visibility": ["stdout_attention"],
                "evidence_terms": ["ADVISORY:"],
                "rationale": "demo",
            },
            "skills/support/markdown-preview/scripts/support_helper.py": {
                "states": ["disabled"],
                "visibility": ["terminal_payload"],
                "evidence_terms": ["disabled"],
                "rationale": "demo",
            },
        },
    )

    result = subprocess.run(
        ["python3", str(SCRIPT), "--repo-root", str(repo)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Validated attention-state visibility declarations for 3 file(s)." in result.stdout
