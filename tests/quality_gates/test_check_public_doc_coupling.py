from __future__ import annotations

import importlib
import json
from pathlib import Path

from .support import run_script

coupling_gate = importlib.import_module("scripts.check_public_doc_coupling")

SCRIPT = "scripts/check_public_doc_coupling.py"


def _seed_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "skills" / "shared" / "references").mkdir(parents=True)
    (repo / "skills" / "public" / "demo" / "references").mkdir(parents=True)
    (repo / "docs" / "generated").mkdir(parents=True)
    (repo / "skills" / "shared" / "references" / "clean.md").write_text(
        "Portable guidance with no coupling.\n", encoding="utf-8"
    )
    return repo


def test_clean_tree_reports_clean_and_exits_zero(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path)
    result = run_script(SCRIPT, "--repo-root", str(repo))
    assert result.returncode == 0
    assert "exported reusable guidance is clean" in result.stdout


def test_issue_anchor_in_shared_reference_is_advisory_flagged(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path)
    (repo / "skills" / "shared" / "references" / "coupled.md").write_text(
        "This rule exists because of (#999) and stays portable.\n", encoding="utf-8"
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "coupled"
    assert [(f["kind"], f["path"]) for f in payload["findings"]] == [
        ("issue_anchor", "skills/shared/references/coupled.md")
    ]


def test_self_version_pin_flagged_but_external_versions_pass(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path)
    (repo / "skills" / "public" / "demo" / "references" / "pins.md").write_text(
        "Since v0.41.0 the helper exists.\n"
        "Use runner v2.327.1 or newer.\n"
        "cautilus 0.15.4 renamed the topic.\n"
        "Dated 2026.06.05 in a table.\n"
        "Charness 0.42.0 shipped the change.\n"
        "An external 0.x tool pin like v0.4.0 also matches by design.\n",
        encoding="utf-8",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0
    findings = json.loads(result.stdout)["findings"]
    assert [(f["kind"], f["line"]) for f in findings] == [
        ("self_version_pin", 1),
        ("self_version_pin", 5),
        ("self_version_pin", 6),
    ]


def test_allowed_anchor_context_is_not_flagged(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path)
    (repo / "skills" / "shared" / "references" / "allowed.md").write_text(
        "Use the placeholder https://github.com/<owner>/<repo>/.../issues/5 form.\n",
        encoding="utf-8",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "clean"


def test_human_output_names_the_policy_owner(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path)
    (repo / "docs" / "generated" / "ref.md").write_text(
        "See issues/123 for history.\n", encoding="utf-8"
    )
    result = run_script(SCRIPT, "--repo-root", str(repo))
    assert result.returncode == 0
    assert result.stdout.startswith("ADVISORY: public-doc-coupling")
    assert "provenance-placement.md" in result.stdout


def test_real_repo_baseline_is_clean() -> None:
    """Intentional zero-baseline ratchet.

    The CLI gate stays advisory (exit 0), but this repo chooses to hold its
    own exported guidance at zero findings; a deliberate new exception should
    update this test (or the gate scope) with the reasoning, not slip past.
    """
    findings = coupling_gate.find_coupling(Path(__file__).resolve().parents[2])
    assert findings == []
