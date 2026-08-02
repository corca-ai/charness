"""The dup-ratchet trap becomes a workflow affordance, not agent memory (#474).

`check_dup_ratchet.py` runs only in the closeout aggregate, where a new duplicate
family is a HARD BLOCK found after the slice is finished and the commit message
is written. Four consecutive runs wrote "run the dup ratchet early" into a plan
and hit it at the aggregate anyway -- a prose checklist fires exactly when nobody
is reading the prose.

The length-headroom advisory is the proven shape. These tests pin the sibling:
it fires at the edit, it stays quiet where it would be noise, and it never
changes an exit code.
"""

from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load_module(relpath: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def advisory():
    return _load_module("scripts/dup_ratchet_edit_advisory.py", "_dup_edit_advisory")


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".agents").mkdir()
    (repo / ".agents/quality-adapter.yaml").write_text(
        "dup_ratchet:\n  enabled: true\n  scope_paths:\n    - scripts\n    - skills/public\n",
        encoding="utf-8",
    )
    (repo / "scripts/seed.py").write_text("x = 1\n", encoding="utf-8")
    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "t@example.com"],
        ["git", "config", "user.name", "t"],
        ["git", "add", "-A"],
        ["git", "commit", "-q", "-m", "seed"],
    ):
        subprocess.run(cmd, cwd=repo, check=True, capture_output=True)
    return repo


def test_a_substantial_addition_to_a_scanned_file_fires(git_repo: Path, advisory) -> None:
    """The case that actually costs a run: a block of new code in a gated file."""
    target = git_repo / "scripts/seed.py"
    target.write_text("x = 1\n" + "\n".join(f"y{i} = {i}" for i in range(60)) + "\n", encoding="utf-8")
    state = advisory.advisory_state(git_repo, "scripts/seed.py")
    assert state["in_scope"] is True
    assert state["added_lines"] >= 60
    assert state["fires"] is True
    message = advisory.advise_for_edited_file(git_repo, "scripts/seed.py")
    assert message is not None
    assert "check_dup_ratchet.py" in message
    assert "HARD BLOCK at the closeout aggregate" in message
    assert "never blocks" in message


def test_a_brand_new_file_counts_as_fully_added(git_repo: Path, advisory) -> None:
    """`git diff HEAD` reports nothing for an untracked file, and a new module is
    the case MOST likely to introduce a family -- silence there would miss the
    biggest signal."""
    (git_repo / "scripts/brand_new.py").write_text("\n".join(f"a{i} = {i}" for i in range(40)) + "\n", encoding="utf-8")
    state = advisory.advisory_state(git_repo, "scripts/brand_new.py")
    assert state["added_lines"] == 40
    assert state["fires"] is True


def test_a_small_tweak_stays_silent(git_repo: Path, advisory) -> None:
    """An advisory that false-fires trains token-theater.

    A new fixable duplicate family is a repeated BLOCK, not a line, so a one-line
    change to a scanned file says nothing and must not speak.
    """
    (git_repo / "scripts/seed.py").write_text("x = 2\n", encoding="utf-8")
    assert advisory.advise_for_edited_file(git_repo, "scripts/seed.py") is None


def test_a_scanned_suffix_outside_the_declared_roots_stays_silent(git_repo: Path, advisory) -> None:
    """The ROOT check, exercised on its own.

    An earlier version of this test used only non-source files, so the suffix
    filter satisfied both assertions and the root check was never consulted --
    deleting the root check entirely left every test green. `tests/**` is a real
    Python tree outside the ratchet's declared scope, which is where a regression
    here would fire loudest.
    """
    (git_repo / "tests").mkdir()
    (git_repo / "tests/helper.py").write_text("\n".join(f"t{i} = {i}" for i in range(80)), encoding="utf-8")
    assert advisory.in_ratchet_scope("tests/helper.py", advisory.scope_paths(git_repo)) is False
    assert advisory.advise_for_edited_file(git_repo, "tests/helper.py") is None


def test_unscanned_suffixes_stay_silent(git_repo: Path, advisory) -> None:
    """Docs and prose are not ratchet-relevant, inside a scanned root or not."""
    (git_repo / "docs").mkdir()
    (git_repo / "docs/x.md").write_text("\n".join("line" for _ in range(80)), encoding="utf-8")
    assert advisory.advise_for_edited_file(git_repo, "docs/x.md") is None
    (git_repo / "scripts/notes.md").write_text("\n".join("line" for _ in range(80)), encoding="utf-8")
    assert advisory.advise_for_edited_file(git_repo, "scripts/notes.md") is None


def test_non_python_sources_the_ratchet_really_scans_are_covered(git_repo: Path, advisory) -> None:
    """The ratchet is not Python-only: this repo carries checked-in `.mjs` families.

    A `.py`-only advisory would be silent for exactly the files that already
    produced duplicate families here.
    """
    (git_repo / "scripts/tool.mjs").write_text("\n".join(f"const a{i} = {i};" for i in range(80)), encoding="utf-8")
    assert advisory.advise_for_edited_file(git_repo, "scripts/tool.mjs") is not None


def test_a_repo_that_never_opted_into_the_ratchet_is_not_advised(git_repo: Path, advisory) -> None:
    """An ABSENT ratchet cannot hard-block either.

    This module ships to consumer repos on an opt-in hook. Falling back to the
    default scope for a missing `dup_ratchet` section would fire in a repo that
    never opted in, pointing at a command that may not exist there.
    """
    (git_repo / ".agents/quality-adapter.yaml").write_text("version: 1\n", encoding="utf-8")
    assert advisory.scope_paths(git_repo) == ()
    (git_repo / "scripts/seed.py").write_text("\n".join(f"n{i} = {i}" for i in range(80)), encoding="utf-8")
    assert advisory.advise_for_edited_file(git_repo, "scripts/seed.py") is None


def test_it_advises_once_per_file_per_head_not_on_every_later_edit(git_repo: Path, advisory) -> None:
    """"Warns at the FIRST substantial addition" has to be true.

    `added_lines_vs_head` measures CUMULATIVE additions, so without suppression a
    later one-word edit to the same file re-emits the whole advisory. Repeated
    identical advisories are the token-theater this module exists to avoid.
    """
    target = git_repo / "scripts/seed.py"
    target.write_text("\n".join(f"r{i} = {i}" for i in range(80)), encoding="utf-8")
    assert advisory.advise_for_edited_file(git_repo, "scripts/seed.py") is not None
    target.write_text("\n".join(f"r{i} = {i}" for i in range(80)) + "\n# typo fix\n", encoding="utf-8")
    assert advisory.advise_for_edited_file(git_repo, "scripts/seed.py") is None, "must not re-fire"
    # A different file in the same slice is still its own first time.
    (git_repo / "scripts/other.py").write_text("\n".join(f"o{i} = {i}" for i in range(80)), encoding="utf-8")
    assert advisory.advise_for_edited_file(git_repo, "scripts/other.py") is not None


def test_the_signal_returns_after_a_commit_moves_head(git_repo: Path, advisory) -> None:
    """Suppression is keyed by HEAD, so the next slice gets the signal again."""
    target = git_repo / "scripts/seed.py"
    target.write_text("\n".join(f"c{i} = {i}" for i in range(80)), encoding="utf-8")
    assert advisory.advise_for_edited_file(git_repo, "scripts/seed.py") is not None
    assert advisory.advise_for_edited_file(git_repo, "scripts/seed.py") is None
    for cmd in (["git", "add", "-A"], ["git", "commit", "-q", "-m", "slice"]):
        subprocess.run(cmd, cwd=git_repo, check=True, capture_output=True)
    target.write_text("\n".join(f"c{i} = {i}" for i in range(80)) + "\n" + "\n".join(f"d{i} = {i}" for i in range(60)), encoding="utf-8")
    assert advisory.advise_for_edited_file(git_repo, "scripts/seed.py") is not None


def test_generated_mirrors_are_never_advised_about(git_repo: Path, advisory) -> None:
    """Warning about a mirror sends the author to fix a file that is regenerated
    from the one they should be editing."""
    (git_repo / "plugins/charness/scripts").mkdir(parents=True)
    (git_repo / "plugins/charness/scripts/seed.py").write_text(
        "\n".join(f"z{i} = {i}" for i in range(80)), encoding="utf-8"
    )
    assert advisory.advise_for_edited_file(git_repo, "plugins/charness/scripts/seed.py") is None


def test_a_disabled_ratchet_says_nothing(git_repo: Path, advisory) -> None:
    """A ratchet that cannot hard-block has no trap to warn about.

    Without this the advisory would be a rule firing where it was NOT written to
    -- the mirror image of the class this goal is about.
    """
    (git_repo / ".agents/quality-adapter.yaml").write_text(
        "dup_ratchet:\n  enabled: false\n  scope_paths:\n    - scripts\n", encoding="utf-8"
    )
    (git_repo / "scripts/seed.py").write_text("\n".join(f"q{i} = {i}" for i in range(80)), encoding="utf-8")
    assert advisory.scope_paths(git_repo) == ()
    assert advisory.advise_for_edited_file(git_repo, "scripts/seed.py") is None


def test_scope_falls_back_to_the_shipped_default_when_the_adapter_is_unreadable(
    git_repo: Path, advisory
) -> None:
    """An unreadable adapter must not silently disable the advisory."""
    (git_repo / ".agents/quality-adapter.yaml").write_text("{{ not yaml", encoding="utf-8")
    assert advisory.scope_paths(git_repo) == advisory.DEFAULT_SCOPE_PATHS


def test_the_shipped_default_scope_matches_the_real_adapter() -> None:
    """The pinned fallback is only honest if it matches what this repo declares."""
    import yaml

    module = _load_module("scripts/dup_ratchet_edit_advisory.py", "_dup_edit_advisory_real")
    declared = yaml.safe_load((ROOT / ".agents/quality-adapter.yaml").read_text(encoding="utf-8"))
    assert tuple(declared["dup_ratchet"]["scope_paths"]) == module.DEFAULT_SCOPE_PATHS


# --------------------------------------------------------------------------
# The hook carrying it
# --------------------------------------------------------------------------


def test_the_hook_emits_the_advisory_without_changing_its_exit_code(
    git_repo: Path, capsys
) -> None:
    """Strictly advisory: a dup-ratchet signal must never block an edit that the
    anchor scan would have allowed."""
    guard = _load_module("scripts/post_edit_skill_anchor_guard.py", "_anchor_guard_dup")
    target = git_repo / "scripts/seed.py"
    target.write_text("\n".join(f"w{i} = {i}" for i in range(80)), encoding="utf-8")
    payload = json.dumps({"tool_input": {"file_path": str(target)}})

    exit_code = guard.main(["--repo-root", str(git_repo)], stdin=io.StringIO(payload))

    assert exit_code == 0, "a dup-ratchet advisory must not change the guard's verdict"
    captured = capsys.readouterr()
    # STDOUT, as `hookSpecificOutput.additionalContext`. The host branches on
    # exit 0 (silent) vs 2 (surface findings) for this guard, so a message on
    # stderr at exit 0 would be computed correctly and then thrown away -- an
    # advisory that cannot fire where it was written, which is the class this
    # slice was built during.
    payload_out = json.loads(captured.out)
    context = payload_out["hookSpecificOutput"]["additionalContext"]
    assert payload_out["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert "ADVISORY (dup ratchet)" in context
    assert "scripts/seed.py" in context


def test_the_hook_stays_silent_and_clean_for_an_unremarkable_edit(git_repo: Path, capsys) -> None:
    guard = _load_module("scripts/post_edit_skill_anchor_guard.py", "_anchor_guard_quiet")
    target = git_repo / "scripts/seed.py"
    target.write_text("x = 3\n", encoding="utf-8")
    payload = json.dumps({"tool_input": {"file_path": str(target)}})

    assert guard.main(["--repo-root", str(git_repo)], stdin=io.StringIO(payload)) == 0
    captured = capsys.readouterr()
    assert "ADVISORY (dup ratchet)" not in captured.out
    assert "ADVISORY (dup ratchet)" not in captured.err


def test_an_advisory_failure_never_breaks_an_edit(git_repo: Path, monkeypatch, capsys) -> None:
    """This rides on an edit-time hook. If the advisory can raise, an author's
    ordinary edit breaks over a signal that is explicitly non-blocking."""
    guard = _load_module("scripts/post_edit_skill_anchor_guard.py", "_anchor_guard_boom")

    def boom(*_args, **_kwargs):
        raise RuntimeError("advisory exploded")

    monkeypatch.setattr(guard, "repo_relpath", boom)
    target = git_repo / "scripts/seed.py"
    target.write_text("\n".join(f"v{i} = {i}" for i in range(80)), encoding="utf-8")
    payload = json.dumps({"tool_input": {"file_path": str(target)}})

    assert guard.main(["--repo-root", str(git_repo)], stdin=io.StringIO(payload)) == 0
