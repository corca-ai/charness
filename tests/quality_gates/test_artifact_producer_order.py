from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


PRODUCER_VALIDATOR_PAIRS = (
    (
        "achieve",
        "upsert_goal.py",
        "check_goal_artifact.py",
    ),
    (
        "debug",
        "scaffold_debug_artifact.py",
        "validate_debug_artifact.py",
    ),
    (
        "quality",
        "scaffold_quality_artifact.py",
        "validate_quality_artifact.py",
    ),
    (
        "ideation",
        "scaffold_ideation_artifact.py",
        "validate_ideation_artifact.py",
    ),
    (
        "critique",
        "scaffold_critique_artifact.py",
        "validate_critique_artifacts.py",
    ),
    (
        "handoff",
        "scaffold_handoff_artifact.py",
        "validate_handoff_artifact.py",
    ),
    (
        "retro",
        "scaffold_retro_artifact.py",
        "validate_retro_artifact.py",
    ),
    # Same helper, different mode: sync produces the durable artifact, --check
    # validates freshness after the artifact exists.
    (
        "hitl",
        'closeout sync: `python3 "$SKILL_DIR/scripts/sync_review_artifact.py" --repo-root . --session-id <session-id>`',
        'durable artifact freshness check: `python3 "$SKILL_DIR/scripts/sync_review_artifact.py" --repo-root . --session-id <session-id> --check`',
    ),
)


def _bootstrap_section(text: str) -> str:
    start = text.index("## Bootstrap")
    end = text.find("\n## ", start + len("## Bootstrap"))
    if end == -1:
        return text[start:]
    return text[start:end]


def test_artifact_bootstrap_examples_produce_before_they_validate() -> None:
    for skill, producer, validator in PRODUCER_VALIDATOR_PAIRS:
        skill_path = ROOT / "skills" / "public" / skill / "SKILL.md"
        bootstrap = _bootstrap_section(skill_path.read_text(encoding="utf-8"))
        producer_index = bootstrap.find(producer)
        validator_index = bootstrap.find(validator)

        if validator_index == -1:
            continue

        assert producer_index != -1, f"{skill} bootstrap validates with {validator} but does not name {producer}"
        assert producer_index < validator_index, (
            f"{skill} bootstrap names {validator} before {producer}; "
            "artifact validators must be post-scaffold gates"
        )
