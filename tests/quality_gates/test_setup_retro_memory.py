from __future__ import annotations

from pathlib import Path

import yaml

from tests.script_loader import load_script_module

from .support import ROOT, run_loaded_script_main

SEED_RETRO_MEMORY = load_script_module(
    "tests.quality_gates.setup_seed_retro_memory",
    ROOT / "skills/public/setup/scripts/seed_retro_memory.py",
)
# In-process on purpose: the exit-code half of the trigger probe's contract is proven in
# tests/quality_gates/test_retro_auto_trigger.py, so joining the two seams here needs the
# payload only — an import already establishes this fact without a process boundary.
CHECK_AUTO_TRIGGER = load_script_module(
    "tests.quality_gates.retro_check_auto_trigger",
    ROOT / "skills/public/retro/scripts/check_auto_trigger.py",
)


def test_setup_seed_retro_memory_writes_adapter_and_digest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_loaded_script_main(
        "seed_retro_memory.py", SEED_RETRO_MEMORY, "--repo-root", str(repo)
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["created"] == {"adapter": True, "summary": True, "gitignore": True}
    assert "lesson_loop" not in payload

    adapter_text = (repo / ".agents" / "retro-adapter.yaml").read_text(encoding="utf-8")
    summary_text = (repo / "charness-artifacts" / "retro" / "recent-lessons.md").read_text(
        encoding="utf-8"
    )
    gitignore_text = (repo / ".gitignore").read_text(encoding="utf-8")
    assert "summary_path: charness-artifacts/retro/recent-lessons.md" in adapter_text
    assert "repo: repo" in adapter_text
    # The two auto-retro trigger keys must be seeded COMMENTED, never as bare `[]`.
    # `[]` reads as `explicit-empty` -> `intentional-empty` -> an opt-out the repo never
    # chose, and `check_auto_trigger.py` then suppresses its own remediation for it. This
    # asserts the seam both ways: the guidance is present, and no uncommented form of
    # either key is.
    assert "# auto_session_trigger_surfaces: []" in adapter_text
    assert "# auto_session_trigger_path_globs: []" in adapter_text
    for line in adapter_text.splitlines():
        assert not line.startswith("auto_session_trigger_"), line
    assert "No durable retro summary yet." in summary_text
    assert ".charness/retro/" in gitignore_text


def test_seeded_adapter_leaves_the_trigger_question_open_end_to_end(tmp_path: Path) -> None:
    """The two mechanisms, joined. Asserting the seeded TEXT is not enough: the defect was
    that setup's `[]` and the probe's reading of `[]` agreed on an opt-out nobody chose,
    so the seam only holds if the seeded file actually drives the probe to
    `not-established` instead of a `triggered: false` that reads as a judged answer."""
    repo = tmp_path / "repo"
    repo.mkdir()
    seed = run_loaded_script_main(
        "seed_retro_memory.py", SEED_RETRO_MEMORY, "--repo-root", str(repo)
    )
    assert seed.returncode == 0, seed.stderr

    payload = CHECK_AUTO_TRIGGER.build_payload(repo, paths=["README.md"])

    assert payload["state"] == "not-established"
    assert "triggered" not in payload
    assert payload["configuration_status"] == "unset"
    assert payload["field_state"]["auto_session_trigger_surfaces"] == "unset"
    assert payload["field_state"]["auto_session_trigger_path_globs"] == "unset"
    assert "intentional opt-out" in payload["remediation"]


def test_setup_seed_retro_memory_preserves_existing_gitignore(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".gitignore").write_text("node_modules/\n.charness/retro/\n", encoding="utf-8")

    result = run_loaded_script_main(
        "seed_retro_memory.py", SEED_RETRO_MEMORY, "--repo-root", str(repo)
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)

    assert payload["created"]["gitignore"] is False
    assert (repo / ".gitignore").read_text(encoding="utf-8") == "node_modules/\n.charness/retro/\n"


def test_setup_skill_mentions_retro_memory_scaffold() -> None:
    skill_text = (ROOT / "skills" / "public" / "setup" / "SKILL.md").read_text(encoding="utf-8")
    bootstrap_seams_text = (
        ROOT / "skills" / "public" / "setup" / "references" / "bootstrap-seams.md"
    ).read_text(encoding="utf-8")
    reference_text = (
        ROOT / "skills" / "public" / "setup" / "references" / "retro-memory-seam.md"
    ).read_text(encoding="utf-8")

    assert "retro-memory-seam.md" in skill_text
    assert "bootstrap-seams.md" in skill_text
    assert "seed_retro_memory.py" in bootstrap_seams_text
    assert ".agents/retro-adapter.yaml" in reference_text
    assert "recent-lessons.md" in reference_text
