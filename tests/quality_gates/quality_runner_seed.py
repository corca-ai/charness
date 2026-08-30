"""Cross-worker cache boundary for the synthetic quality-runner repository."""

from __future__ import annotations

from pathlib import Path

import pytest


def quality_runner_seed(*, cache_get_or_build=None) -> Path:
    """Return one source-bound, cross-worker quality-runner seed."""
    from tests.quality_gates.support import make_quality_runner_repo

    if cache_get_or_build is None:
        from tests.seed_cache import get_or_build

        cache_get_or_build = get_or_build

    def build(staging: Path) -> None:
        make_quality_runner_repo(staging)

    return cache_get_or_build("quality-runner-repo-seed", build) / "repo"


@pytest.fixture(scope="session")
def seeded_quality_runner_repo() -> Path:
    return quality_runner_seed()
