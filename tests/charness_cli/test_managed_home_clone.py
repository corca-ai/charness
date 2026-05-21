from __future__ import annotations

import json
from pathlib import Path

import pytest

from .support import clone_seeded_managed_home

pytestmark = pytest.mark.release_only


def test_clone_seeded_managed_home_can_share_source_checkout(tmp_path: Path) -> None:
    seeded_home = tmp_path / "seeded-home"
    source = seeded_home / ".agents" / "src" / "charness"
    source.mkdir(parents=True)
    (source / "README.md").write_text("# seeded\n", encoding="utf-8")
    state_dir = seeded_home / ".local" / "state" / "charness"
    state_dir.mkdir(parents=True)
    (state_dir / "install-state.json").write_text(
        json.dumps({"repo_root": str(source)}) + "\n",
        encoding="utf-8",
    )

    home_root, _env = clone_seeded_managed_home(
        tmp_path / "case", seeded_home, share_source_checkout=True
    )
    cloned_source = home_root / ".agents" / "src" / "charness"
    install_state = json.loads((home_root / ".local" / "state" / "charness" / "install-state.json").read_text(encoding="utf-8"))

    assert cloned_source.is_symlink()
    assert cloned_source.resolve() == source.resolve()
    assert install_state["repo_root"] == str(home_root / ".agents" / "src" / "charness")
