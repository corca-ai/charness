from __future__ import annotations

import pytest

from .release_script_loading import load_release_script

RESUME = load_release_script("publish_release_resume", suffix="state_validation")


def _published_state(phase: str) -> dict[str, object]:
    return {
        "phase": phase,
        "tag_local": True,
        "tag_remote": True,
        "release_exists": True,
        "tag_sha": "release-sha",
        "head_parent_is_tag": True,
        "parent_sha": "carrier-sha",
        "head_grandparent_is_tag": True,
        "remote_branch_sha": "release-sha" if phase == "post-publication-carrier" else "carrier-sha",
        "head_sha": "local-sha",
    }


@pytest.mark.parametrize(
    ("phase", "override", "message"),
    [
        (
            "post-publication-carrier",
            {"tag_remote": False},
            "lacks confirmed tag/release publication state",
        ),
        (
            "post-publication-carrier",
            {"head_parent_is_tag": False},
            "carrier HEAD is not directly based on its release tag",
        ),
        (
            "post-publication-final",
            {"head_grandparent_is_tag": False},
            "final closeout HEAD is not based on its carrier and release tag",
        ),
        (
            "post-publication-carrier",
            {"remote_branch_sha": "unrelated-sha"},
            "refusing ambiguous closeout recovery",
        ),
    ],
)
def test_assert_resumable_rejects_ambiguous_published_state(
    phase: str, override: dict[str, object], message: str
) -> None:
    state = {**_published_state(phase), **override}

    with pytest.raises(SystemExit, match=message):
        RESUME.assert_resumable(state, tag_name="v1.2.3")
