from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from tests.script_loader import load_script_module

from .support import ROOT, run_loaded_script_main

SEED_RETRO_MEMORY = load_script_module(
    "tests.quality_gates.setup_seed_retro_memory",
    ROOT / "skills/public/setup/scripts/seed_retro_memory.py",
)
# In-process on purpose: the exit-code half of the trigger probe's contract is proven in
# tests/quality_gates/test_retro_auto_trigger.py, so joining the two seams here needs the
# payload only — and a fresh subprocess call site would add a new boundary-bypass
# candidate for a fact an import already establishes.
CHECK_AUTO_TRIGGER = load_script_module(
    "tests.quality_gates.retro_check_auto_trigger",
    ROOT / "skills/public/retro/scripts/check_auto_trigger.py",
)


def test_setup_seed_retro_memory_writes_adapter_and_digest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_loaded_script_main("seed_retro_memory.py", SEED_RETRO_MEMORY, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["created"] == {"adapter": True, "summary": True, "gitignore": True}

    adapter_text = (repo / ".agents" / "retro-adapter.yaml").read_text(encoding="utf-8")
    summary_text = (repo / "charness-artifacts" / "retro" / "recent-lessons.md").read_text(encoding="utf-8")
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
    seed = run_loaded_script_main("seed_retro_memory.py", SEED_RETRO_MEMORY, "--repo-root", str(repo))
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

    result = run_loaded_script_main("seed_retro_memory.py", SEED_RETRO_MEMORY, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)

    assert payload["created"]["gitignore"] is False
    assert (repo / ".gitignore").read_text(encoding="utf-8") == "node_modules/\n.charness/retro/\n"


def test_the_opt_in_command_is_named_by_the_validator_that_owns_it(tmp_path: Path) -> None:
    """The runnable line is resolved, not composed here.

    `validate_retro_artifact` already decides between a repo-local `scripts/` copy and
    the installed plugin copy, and a second derivation in the seam bootstrap is how
    setup starts telling a consuming repo to run a path it does not have. Paired with
    the degradation test below: this is the arm where the command resolves, so nothing
    reports it as unavailable.
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    report = SEED_RETRO_MEMORY.lesson_loop_report(repo)

    assert "init_lesson_ledger.py" in report["opt_in_command"]
    assert "opt_in_command_unavailable_reason" not in report


def test_an_unloadable_validator_costs_the_command_not_the_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Setup runs in repos and hosts whose layout need not expose the repo-root modules.

    Losing the opt-in command there must cost exactly that one line. Two things it must
    NOT do: take the whole seam bootstrap down (setup still has an adapter, a summary
    and a gitignore to seed), and turn a host-layout accident into a verdict about the
    repo -- an un-opted-in repo is a real opt-out, and a probe that could not run has
    established nothing about it either way. The reason is carried so a reader can tell
    "no command to give you" from "no command exists".
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    def unloadable(_path: str) -> dict:
        raise ModuleNotFoundError("No module named 'scripts.validate_retro_artifact'")

    monkeypatch.setattr(SEED_RETRO_MEMORY, "runpy", SimpleNamespace(run_path=unloadable))

    report = SEED_RETRO_MEMORY.lesson_loop_report(repo)

    assert report["opt_in_command"] is None
    assert report["opt_in_command_unavailable_reason"] == (
        "ModuleNotFoundError: No module named 'scripts.validate_retro_artifact'"
    )
    # The state is still read off the repo, from the same ledger probe as always.
    assert report["state"] == "not-configured"
    assert report["created"] is False


def test_setup_skill_mentions_retro_memory_scaffold() -> None:
    skill_text = (ROOT / "skills" / "public" / "setup" / "SKILL.md").read_text(encoding="utf-8")
    bootstrap_seams_text = (
        ROOT / "skills" / "public" / "setup" / "references" / "bootstrap-seams.md"
    ).read_text(encoding="utf-8")
    default_surfaces_text = (
        ROOT / "skills" / "public" / "setup" / "references" / "default-surfaces.md"
    ).read_text(encoding="utf-8")
    reference_text = (
        ROOT / "skills" / "public" / "setup" / "references" / "retro-memory-seam.md"
    ).read_text(encoding="utf-8")

    assert "retro-memory-seam.md" in skill_text
    assert "bootstrap-seams.md" in skill_text
    assert "seed_retro_memory.py" in bootstrap_seams_text
    assert "recent-lessons.md" in bootstrap_seams_text
    assert "recent-lessons.md" in default_surfaces_text
    assert ".agents/retro-adapter.yaml" in reference_text
    assert "recent-lessons.md" in reference_text
