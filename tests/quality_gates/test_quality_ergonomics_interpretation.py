from __future__ import annotations

import json
from pathlib import Path

from .skill_ergonomics_support import run_inventory_skill_ergonomics as _run
from .support import ROOT


def test_inventory_skill_ergonomics_emits_interpretation_self_declaration(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\ndescription: \"Demo.\"\n---\n\n# Demo\n",
        encoding="utf-8",
    )

    result = _run("--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    interpretation = payload["interpretation"]
    assert set(interpretation) == {"measures", "proxy_for", "blind_spots", "interpretation_question"}
    assert all(interpretation[field].strip() for field in interpretation)

    plain = _run("--repo-root", str(repo))
    assert plain.returncode == 0, plain.stderr
    assert "INTERPRETATION" in plain.stdout
    assert "Consumer must answer first" in plain.stdout
    assert "intentional" in plain.stdout  # the load-bearing blind spot

    reference = (
        ROOT / "skills" / "public" / "quality" / "references" / "automation-promotion.md"
    ).read_text(encoding="utf-8")
    assert "Per-surface interpretation questions" in reference
    assert "inventory_skill_ergonomics.py" in reference
