"""Regression checks for repo-owned mutation sampling."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.sample_mutation_files import rewrite_cosmic_ray_targets  # noqa: E402


def test_sample_rewrites_cosmic_ray_module_path(tmp_path: Path) -> None:
    config = tmp_path / "cosmic-ray.toml"
    config.write_text(
        dedent(
            """\
            [cosmic-ray]
            module-path = ["scripts/control_plane_lib.py"]
            timeout = 30.0
            test-command = "python3 -m pytest -q tests"
            """
        ),
        encoding="utf-8",
    )

    rewrite_cosmic_ray_targets(config, ["scripts/a.py", "scripts/b.py"])

    text = config.read_text(encoding="utf-8")
    assert '    "scripts/a.py",' in text
    assert '    "scripts/b.py",' in text
    assert 'test-command = "python3 -m pytest -q tests"' in text


def test_sample_script_rewrites_config_and_manifest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    for name in ("a.py", "b.py", "c.py"):
        (scripts_dir / name).write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "cosmic-ray.toml").write_text(
        dedent(
            """\
            [cosmic-ray]
            module-path = ["scripts/control_plane_lib.py"]
            timeout = 30.0
            test-command = "python3 -m pytest -q tests"
            """
        ),
        encoding="utf-8",
    )
    env = {
        **os.environ,
        "MUTATION_SAMPLE_MAX_FILES": "2",
        "MUTATION_SAMPLE_CHANGED_QUOTA": "0",
        "MUTATION_SAMPLE_SEED": "fixed-seed",
    }

    result = subprocess.run(
        ["python3", "scripts/sample_mutation_files.py", "--repo-root", str(repo)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    manifest = json.loads((repo / "reports" / "mutation" / "sample.json").read_text(encoding="utf-8"))
    assert len(manifest["sample"]) == 2
    text = (repo / "cosmic-ray.toml").read_text(encoding="utf-8")
    assert 'module-path = [\n' in text
    for path in manifest["sample"]:
        assert f'    "{path}",' in text
    assert "scripts/control_plane_lib.py" not in manifest["sample"]
