from __future__ import annotations

import json
import subprocess
from pathlib import Path

_SEED_NAME = "reviewed-input-identity-repo-seed-v2"


def _build_seed(seed_root: Path) -> None:
    repo = seed_root / "repo"
    repo.mkdir()
    (repo / "reviewed.txt").write_text("base\n", encoding="utf-8")
    (repo / "unrelated.txt").write_text("base\n", encoding="utf-8")
    for cmd in (
        ["init"],
        ["add", "."],
        ["commit", "-m", "initial"],
    ):
        subprocess.run(
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", *cmd],
            cwd=repo,
            check=True,
            capture_output=True,
        )

    # Git's read commands may take optional index locks, so consumers must never
    # run identity capture against the shared repository. Capture once while the
    # seed builder owns it; later workers read immutable bytes or copy the repo.
    from scripts.reviewed_input_identity import build_reviewed_input_identity

    identity = build_reviewed_input_identity(
        repo_root=repo,
        reviewed_paths=["reviewed.txt"],
    )
    (seed_root / "reviewed-input-identity.json").write_text(
        json.dumps(identity, separators=(",", ":"), sort_keys=True),
        encoding="utf-8",
    )


def _seed_bundle(*, cache_get_or_build=None) -> Path:
    if cache_get_or_build is None:
        from tests.seed_cache import get_or_build

        cache_get_or_build = get_or_build
    return cache_get_or_build(_SEED_NAME, _build_seed)


def repo_seed(*, cache_get_or_build=None) -> Path:
    return _seed_bundle(cache_get_or_build=cache_get_or_build) / "repo"


def reviewed_identity_seed(*, cache_get_or_build=None) -> dict:
    bundle = _seed_bundle(cache_get_or_build=cache_get_or_build)
    return json.loads(
        (bundle / "reviewed-input-identity.json").read_text(encoding="utf-8")
    )


def tree_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
