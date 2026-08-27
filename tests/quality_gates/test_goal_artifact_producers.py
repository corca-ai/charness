from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


goal_lib = _load(ROOT / "skills/public/achieve/scripts/goal_artifact_lib.py", "goal_artifact_lib")
backlog = _load(ROOT / "skills/public/achieve/scripts/goal_artifact_backlog.py", "goal_artifact_backlog")


def _assert_goal_shape(text: str) -> None:
    assert goal_lib.check_goal(text)["ok"] is True
    assert text.index("## Active Operating Frame") < text.index("## Goal")
    for section in goal_lib.REQUIRED_SECTIONS:
        assert f"## {section}" in text, section
    for section in goal_lib.PORTABILITY_SECTIONS:
        assert f"## {section}" in text, section
    assert "Activation: `/goal @" in text
    assert "## Operator Decision Queue" in text
    # Read the floor's own constants, NOT a literal. This assertion exists because the
    # backlog-recount floor is shipped into `achieve`'s template, so every
    # generated goal is refused by `--pursue-ready`
    # with no heading to fill — while this very test reported "producers share current
    # shape". A hardcoded string here would have been the same blind spot one layer up:
    # renaming the section or its fields would leave this passing against dead strings.
    assert f"## {backlog.SECTION}" in text
    for field in backlog.REQUIRED_FIELDS:
        assert f"- {field}: " in text, field
    # And the floor's own READER must find them. The round-1 symptom was
    # `--pursue-ready` refusing every pickup-generated goal, and string assertions alone
    # would stay green if the heading were demoted to `###`, moved below a fence, or its
    # fields rendered inside a code block — all of which reproduce that refusal.
    #
    # Asserted on the field reader, NOT on `backlog.check(text)`: these fixtures render a
    # pre-rule `Created:` date, so `check` short-circuits to the grandfather and would
    # pass vacuously no matter how broken the section was.
    body = backlog.joined_section_body(text, backlog.SECTION)
    assert body is not None, "the floor's own reader cannot find the section it scaffolds"
    assert backlog.missing_fields(body) == []


def test_goal_artifact_producers_share_current_shape(tmp_path: Path) -> None:
    goal_lib.upsert_goal(
        tmp_path,
        date="2026-06-01",
        slug="producer-contract",
        title="Producer Contract",
        goal_body="Exercise the canonical achieve scaffold.",
    )
    achieve_text = goal_lib.goal_path(tmp_path, "2026-06-01", "producer-contract").read_text(encoding="utf-8")
    _assert_goal_shape(achieve_text)
    # #315: the achieve scaffold (the activated/created artifact) seeds visible
    # closeout-evidence placeholders so an active run sees the obligation early.
    for placeholder in (
        "Retro: TODO",
        "Host log probe: TODO",
        "Retro dispositions: TODO",
        "Decision: operator-only decision or confirmation needed",
    ):
        assert placeholder in achieve_text, placeholder

    # The discussion summary is seeded in its correct location
    # (before `## Slice Log`) with a non-satisfying starter.
    assert "Discuss before activation: fill" in achieve_text
    # The summary must precede the real `## Slice Log` heading (not the Active
    # Operating Frame's inline backticked mention) — that placement is what the
    # discussion floor reads via its `\n## Slice Log` split.
    assert achieve_text.index("Discuss before activation:") < achieve_text.index("\n## Slice Log\n")
