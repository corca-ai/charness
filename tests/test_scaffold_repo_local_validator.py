from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.core.repo_layout import find_repo_script
from tests.quality_gates.support import run_script

ROOT = Path(__file__).resolve().parents[1]
# The materialized plugin export is the canonical installed-like tree: it ships
# scaffolds under skills/<skill>/scripts/ AND a sibling scripts/ dir carrying the
# bundled validators, exactly the ancestor an installed/cached plugin exposes.
PLUGIN_ROOT = ROOT / "plugins" / "charness"

# (skill_id, plugin skill dir, scaffold filename, repo-local validator filename)
SCAFFOLD_CASES = [
    ("debug", "debug", "scaffold_debug_artifact.py", "validate_debug_artifact.py"),
    ("critique", "critique", "scaffold_critique_artifact.py", "validate_critique_artifacts.py"),
    ("retro", "retro", "scaffold_retro_artifact.py", "validate_retro_artifact.py"),
    ("quality", "quality", "scaffold_quality_artifact.py", "validate_quality_artifact.py"),
    ("ideation", "ideation", "scaffold_ideation_artifact.py", "validate_ideation_artifact.py"),
]


@pytest.mark.parametrize(
    "skill_id, skill_dir, scaffold_name, validator_name",
    SCAFFOLD_CASES,
    ids=[case[0] for case in SCAFFOLD_CASES],
)
def test_installed_like_scaffold_prefers_repo_local_validator_when_repo_owns_one(
    tmp_path: Path,
    skill_id: str,
    skill_dir: str,
    scaffold_name: str,
    validator_name: str,
) -> None:
    """Version-skew regression: a scaffold invoked from the installed/mirrored
    plugin must cite the REPO-LOCAL `scripts/` validator when the working repo
    owns one, so the cited check == the broad gate instead of the possibly-looser
    installed copy that the old ancestor-first lookup would have cited. Pure
    presence/path resolution: the repo owning the validator file wins citation."""
    scaffold = PLUGIN_ROOT / "skills" / skill_dir / "scripts" / scaffold_name
    assert scaffold.is_file(), scaffold
    # Precondition: the installed-like tree ships a validator that the old
    # ancestor-first lookup would have cited (this is the shadow to beat).
    # Bundled validators live in concept packages under scripts/ (#770).
    assert find_repo_script(PLUGIN_ROOT, validator_name) is not None, validator_name

    repo = tmp_path / "repo-with-own-validator"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / f"{skill_id}-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                f"repo: {skill_id}-consumer",
                "language: en",
                f"output_dir: charness-artifacts/{skill_id}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    # The working repo owns its own (canonical, strict) validator.
    (repo / "scripts").mkdir()
    (repo / "scripts" / validator_name).write_text(
        "# repo-local validator stub (presence is enough to win citation)\n",
        encoding="utf-8",
    )

    result = run_script(str(scaffold), "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    command = payload["validator_command"]

    # Cites the repo-local validator (repo-relative), not the installed plugin copy.
    assert command.startswith(f"python3 scripts/{validator_name} "), command
    assert str(PLUGIN_ROOT) not in command, command
