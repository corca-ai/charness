from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
# The checked-in plugin mirror is the canonical installed-like tree: it ships
# scaffolds under skills/<skill>/scripts/ AND a sibling scripts/ dir carrying the
# bundled validators, exactly the ancestor an installed/cached plugin exposes.
PLUGIN_ROOT = ROOT / "plugins" / "charness"


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


# (skill_id, plugin skill dir, scaffold filename, repo-local validator filename)
SCAFFOLD_CASES = [
    ("debug", "debug", "scaffold_debug_artifact.py", "validate_debug_artifact.py"),
    ("critique", "critique", "scaffold_critique_artifact.py", "validate_critique_artifacts.py"),
    ("retro", "retro", "scaffold_retro_artifact.py", "validate_retro_artifact.py"),
    ("quality", "quality", "scaffold_quality_artifact.py", "validate_quality_artifact.py"),
    ("handoff", "handoff", "scaffold_handoff_artifact.py", "validate_handoff_artifact.py"),
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
    assert (PLUGIN_ROOT / "scripts" / validator_name).is_file(), validator_name

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

    result = run_script(str(scaffold), "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    command = payload["validator_command"]

    # Cites the repo-local validator (repo-relative), not the installed plugin copy.
    assert command.startswith(f"python3 scripts/{validator_name} "), command
    assert str(PLUGIN_ROOT) not in command, command
