from __future__ import annotations

import json
from pathlib import Path

from .support import ROOT, run_script


def test_check_changed_surfaces_reports_expected_obligations_for_readme() -> None:
    result = run_script(
        "scripts/check-changed-surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "README.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    surface_ids = {surface["surface_id"] for surface in payload["matched_surfaces"]}
    assert "checked-in-plugin-export" in surface_ids
    assert "repo-markdown" in surface_ids
    assert "python3 scripts/sync_root_plugin_manifests.py --repo-root ." in payload["sync_commands"]
    assert "python3 scripts/validate-packaging.py --repo-root ." in payload["verify_commands"]
    assert "python3 scripts/check-doc-links.py --repo-root ." in payload["verify_commands"]
    assert "./scripts/check-markdown.sh" in payload["verify_commands"]


def test_check_changed_surfaces_reports_unmatched_paths() -> None:
    result = run_script(
        "scripts/check-changed-surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "notes/private-plan.txt",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["matched_surfaces"] == []
    assert payload["unmatched_paths"] == ["notes/private-plan.txt"]


def test_validate_surfaces_rejects_duplicate_ids(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "dup",
                        "description": "first",
                        "source_paths": ["README.md"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    },
                    {
                        "surface_id": "dup",
                        "description": "second",
                        "source_paths": ["docs/**"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script("scripts/validate-surfaces.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "duplicate surface id `dup`" in result.stderr


def test_run_slice_closeout_executes_sync_then_verify(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "demo-surface",
                        "description": "demo",
                        "source_paths": ["README.md"],
                        "derived_paths": ["plugins/demo/README.md"],
                        "sync_commands": ["python3 scripts/sync.py"],
                        "verify_commands": ["python3 scripts/verify.py"],
                        "notes": ["demo note"],
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "sync.py").write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                "root = Path.cwd()",
                "(root / 'plugins' / 'demo').mkdir(parents=True, exist_ok=True)",
                "(root / 'plugins' / 'demo' / 'README.md').write_text('# Generated\\n', encoding='utf-8')",
                "(root / 'sync.log').write_text('sync\\n', encoding='utf-8')",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "scripts" / "verify.py").write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                "root = Path.cwd()",
                "assert (root / 'plugins' / 'demo' / 'README.md').is_file()",
                "(root / 'verify.log').write_text('verify\\n', encoding='utf-8')",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/run-slice-closeout.py",
        "--repo-root",
        str(repo),
        "--paths",
        "README.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
    assert [step["phase"] for step in payload["executed_commands"]] == ["sync", "verify"]
    assert (repo / "sync.log").read_text(encoding="utf-8").strip() == "sync"
    assert (repo / "verify.log").read_text(encoding="utf-8").strip() == "verify"


def test_run_slice_closeout_blocks_unmatched_paths_by_default(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "demo-surface",
                        "description": "demo",
                        "source_paths": ["README.md"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "scripts/run-slice-closeout.py",
        "--repo-root",
        str(repo),
        "--paths",
        "notes/todo.txt",
    )
    assert result.returncode == 1
    assert "not covered by the surfaces manifest" in result.stderr
