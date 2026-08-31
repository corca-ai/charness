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
import yaml

from .repo_shapes import install_committed_repo

ROOT = Path(__file__).resolve().parents[2]

_DUP_RATCHET_FILES = {
    ".agents/quality-adapter.yaml": (
        "dup_ratchet:\n  enabled: true\n  scope_paths:\n    - scripts\n    - skills/public\n"
    ),
    "scripts/seed.py": "x = 1\n",
}


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


def _tree_snapshot(root: Path) -> tuple[tuple[str, bytes], ...]:
    return tuple(
        sorted(
            (path.relative_to(root).as_posix(), path.read_bytes())
            for path in root.rglob("*")
            if path.is_file()
        )
    )


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    return install_committed_repo(tmp_path / "repo", _DUP_RATCHET_FILES)


def test_cached_dup_ratchet_seed_is_never_mutated_by_a_test_clone(tmp_path: Path) -> None:
    first = install_committed_repo(tmp_path / "seed", _DUP_RATCHET_FILES)
    before_seed = _tree_snapshot(first)
    clone = install_committed_repo(tmp_path / "clone", _DUP_RATCHET_FILES)
    (clone / "scripts/seed.py").write_text("clone only\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=clone, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "clone-only"],
        cwd=clone,
        check=True,
        capture_output=True,
    )

    assert _tree_snapshot(first) == before_seed


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
    assert advisory.in_ratchet_scope("tests/helper.py", advisory.scope_paths(git_repo)) is False
    assert (
        advisory.advise_for_edited_file(git_repo, "tests/helper.py", added=80, head_sha="a" * 40)
        is None
    )


def test_unscanned_suffixes_stay_silent(git_repo: Path, advisory) -> None:
    """Docs and prose are not ratchet-relevant, inside a scanned root or not."""
    assert advisory.advise_for_edited_file(git_repo, "docs/x.md", added=80, head_sha="a" * 40) is None
    assert (
        advisory.advise_for_edited_file(git_repo, "scripts/notes.md", added=80, head_sha="a" * 40)
        is None
    )


def test_non_python_sources_the_ratchet_really_scans_are_covered(git_repo: Path, advisory) -> None:
    """The ratchet is not Python-only: this repo carries checked-in `.mjs` families.

    A `.py`-only advisory would be silent for exactly the files that already
    produced duplicate families here.
    """
    assert (
        advisory.advise_for_edited_file(git_repo, "scripts/tool.mjs", added=80, head_sha="a" * 40)
        is not None
    )


def test_a_repo_that_never_opted_into_the_ratchet_is_not_advised(git_repo: Path, advisory) -> None:
    """An ABSENT ratchet cannot hard-block either.

    This module ships to consumer repos on an opt-in hook. Falling back to the
    default scope for a missing `dup_ratchet` section would fire in a repo that
    never opted in, pointing at a command that may not exist there.
    """
    (git_repo / ".agents/quality-adapter.yaml").write_text("version: 1\n", encoding="utf-8")
    assert advisory.scope_paths(git_repo) == ()
    assert (
        advisory.advise_for_edited_file(git_repo, "scripts/seed.py", added=80, head_sha="a" * 40)
        is None
    )


def test_it_advises_once_per_file_per_head_not_on_every_later_edit(git_repo: Path, advisory) -> None:
    """"Warns at the FIRST substantial addition" has to be true.

    `added_lines_vs_head` measures CUMULATIVE additions, so without suppression a
    later one-word edit to the same file re-emits the whole advisory. Repeated
    identical advisories are the token-theater this module exists to avoid.
    """
    head = "a" * 40
    assert advisory.advise_for_edited_file(git_repo, "scripts/seed.py", added=80, head_sha=head) is not None
    assert (
        advisory.advise_for_edited_file(git_repo, "scripts/seed.py", added=80, head_sha=head) is None
    ), "must not re-fire"
    # A different file in the same slice is still its own first time.
    assert advisory.advise_for_edited_file(git_repo, "scripts/other.py", added=80, head_sha=head) is not None


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


def test_scope_membership_uses_the_canonical_normalized_prefixes(git_repo: Path, advisory) -> None:
    """The edit advisory and ratchet gate must agree on equivalent scope spellings."""
    adapter = git_repo / ".agents/quality-adapter.yaml"
    adapter.write_text(
        "dup_ratchet:\n  enabled: true\n  scope_paths:\n    - .\n", encoding="utf-8"
    )
    assert advisory.in_ratchet_scope("scripts/seed.py", advisory.scope_paths(git_repo)) is True

    adapter.write_text(
        "dup_ratchet:\n  enabled: true\n  scope_paths:\n    - ./src/\n", encoding="utf-8"
    )
    assert advisory.in_ratchet_scope("src/tool.py", advisory.scope_paths(git_repo)) is True
    assert advisory.in_ratchet_scope("scripts/seed.py", advisory.scope_paths(git_repo)) is False


def test_unresolvable_scope_does_not_widen_the_advisory(git_repo: Path, advisory) -> None:
    """A glob cannot be proven by a literal prefix matcher, so it stays quiet."""
    roots = ("src/**/*.py",)
    assert advisory.in_ratchet_scope("src/tool.py", roots) is False
    # A known literal sibling remains actionable without turning the unknown entry
    # into a whole-tree scope.
    assert advisory.in_ratchet_scope("scripts/seed.py", ("scripts/", "src/**/*.py")) is True
    assert advisory.in_ratchet_scope("tests/helper.py", ("scripts/", "src/**/*.py")) is False


def test_missing_scope_resolver_stays_conservative(tmp_path: Path, advisory, monkeypatch) -> None:
    helper = tmp_path / "skills/public/quality/scripts/dup_ratchet_scope.py"
    helper.parent.mkdir(parents=True)
    helper.write_text("# resolver unavailable\n", encoding="utf-8")
    module_path = tmp_path / "scripts/dup_ratchet_edit_advisory.py"
    module_path.parent.mkdir()
    monkeypatch.setattr(advisory, "__file__", str(module_path))
    monkeypatch.setattr(advisory.importlib.util, "spec_from_file_location", lambda *_a, **_k: None)
    assert advisory._resolve_scope_prefixes(tmp_path, ("scripts",)) == ([], ["scripts"])


def test_scope_resolver_import_failure_stays_conservative(tmp_path: Path, advisory, monkeypatch) -> None:
    helper = tmp_path / "skills/public/quality/scripts/dup_ratchet_scope.py"
    helper.parent.mkdir(parents=True)
    helper.write_text("def resolve_scope_prefixes(_roots): return (None, [])\n", encoding="utf-8")
    module_path = tmp_path / "scripts/dup_ratchet_edit_advisory.py"
    module_path.parent.mkdir()
    monkeypatch.setattr(advisory, "__file__", str(module_path))

    def fail_import(_spec):
        raise ImportError("resolver unavailable")

    monkeypatch.setattr(advisory.importlib.util, "module_from_spec", fail_import)
    assert advisory._resolve_scope_prefixes(tmp_path, ("scripts",)) == ([], ["scripts"])


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


# --------------------------------------------------------------------------
# Degenerate and failure paths
#
# Every branch below exists because this advisory rides an EDIT-TIME hook: it
# must reach a decision or stay silent for any input, and never raise. They were
# added when the pre-push mutation gate reported them as changed-and-uncovered
# -- an error path nothing exercises is an error path nobody knows the shape of.
# --------------------------------------------------------------------------


def test_a_malformed_or_absent_adapter_falls_back_rather_than_raising(tmp_path: Path, advisory) -> None:
    repo = tmp_path / "r"
    (repo / ".agents").mkdir(parents=True)
    # No adapter file at all -> the pinned default, so the advisory still works
    # in a checkout where the adapter has not been written yet.
    assert advisory.scope_paths(repo) == advisory.DEFAULT_SCOPE_PATHS
    # Adapter that parses to a non-mapping.
    (repo / ".agents/quality-adapter.yaml").write_text("- just\n- a\n- list\n", encoding="utf-8")
    assert advisory.scope_paths(repo) == advisory.DEFAULT_SCOPE_PATHS
    # Enabled section whose `scope_paths` is unusable: fall back rather than
    # silently scoping to nothing, which would look identical to "not gated".
    (repo / ".agents/quality-adapter.yaml").write_text(
        "dup_ratchet:\n  enabled: true\n  scope_paths: not-a-list\n", encoding="utf-8"
    )
    assert advisory.scope_paths(repo) == advisory.DEFAULT_SCOPE_PATHS
    (repo / ".agents/quality-adapter.yaml").write_text(
        "dup_ratchet:\n  enabled: true\n  scope_paths: []\n", encoding="utf-8"
    )
    assert advisory.scope_paths(repo) == advisory.DEFAULT_SCOPE_PATHS
    # Non-string entries are dropped, not stringified into nonsense roots.
    (repo / ".agents/quality-adapter.yaml").write_text(
        "dup_ratchet:\n  enabled: true\n  scope_paths:\n    - scripts\n    - 7\n", encoding="utf-8"
    )
    assert advisory.scope_paths(repo) == ("scripts",)


def test_git_failures_resolve_to_no_answer_rather_than_a_wrong_one(tmp_path: Path, advisory) -> None:
    """A directory that is not a git repo, and a git binary that cannot run."""
    not_a_repo = tmp_path / "plain"
    (not_a_repo / "scripts").mkdir(parents=True)
    (not_a_repo / "scripts/x.py").write_text("\n".join(f"a{i} = {i}" for i in range(80)), encoding="utf-8")
    assert advisory.added_lines_vs_head(not_a_repo, "scripts/x.py") is None
    assert advisory.advise_for_edited_file(not_a_repo, "scripts/x.py") is None


def test_git_binary_missing_is_not_an_exception(git_repo: Path, advisory, monkeypatch) -> None:
    def boom(*_a, **_k):
        raise OSError("git not found")

    monkeypatch.setattr(advisory.subprocess, "run", boom)
    assert advisory._git(git_repo, "status") is None
    assert advisory.added_lines_vs_head(git_repo, "scripts/seed.py") is None


def test_an_untracked_unreadable_file_reports_no_answer(git_repo: Path, advisory) -> None:
    """The byte-count fallback is only reached for an untracked file; if that read
    fails there is no honest number to report."""
    target = git_repo / "scripts/binaryish.py"
    target.write_bytes(b"\xff\xfe\x00" * 4000)
    assert advisory.added_lines_vs_head(git_repo, "scripts/binaryish.py") is None


def test_a_deleted_file_is_not_advised_about(git_repo: Path, advisory) -> None:
    """The hook fires on Write/Edit tools, but a path can be gone by the time the
    advisory runs (a rename or delete right after)."""
    assert advisory.added_lines_vs_head(git_repo, "scripts/never_existed.py") is None
    assert advisory.advise_for_edited_file(git_repo, "scripts/never_existed.py") is None


def test_a_corrupt_suppression_state_file_re_advises(git_repo: Path, advisory) -> None:
    """Unreadable state means re-advise, never go silent: a repeated advisory is
    noise, a missed one is the trap this exists to catch."""
    state = git_repo / advisory._SEEN_RELPATH
    state.parent.mkdir(parents=True, exist_ok=True)
    for corrupt in ("{ not json", "[]", '{"head": "abc", "paths": "nope"}'):
        state.write_text(corrupt, encoding="utf-8")
        (git_repo / "scripts/seed.py").write_text(
            "\n".join(f"s{i} = {i}" for i in range(80)), encoding="utf-8"
        )
        assert advisory.advise_for_edited_file(git_repo, "scripts/seed.py") is not None
        state.write_text(corrupt, encoding="utf-8")


def test_an_unknown_head_never_suppresses(git_repo: Path, advisory) -> None:
    assert advisory._already_advised(git_repo, "scripts/seed.py", None) is False


def test_the_cli_emits_the_structured_decision_carrying_the_advisory(
    git_repo: Path, advisory, capsys
) -> None:
    """One payload now carries both halves the two output modes used to split.

    The decision (`fires`/`in_scope`) and the advisory prose were separate modes;
    the prose is the only part a reader cannot reconstruct from the state, so it
    rides in the payload as `advisory` rather than being deleted with the mode.
    """
    (git_repo / "scripts/seed.py").write_text("\n".join(f"c{i} = {i}" for i in range(80)), encoding="utf-8")
    assert advisory.main(["--repo-root", str(git_repo), "--path", "scripts/seed.py"]) == 0
    state = yaml.safe_load(capsys.readouterr().out)
    assert state["fires"] is True and state["in_scope"] is True
    assert "ADVISORY (dup ratchet)" in state["advisory"]

    # Silent path still exits 0 and advises nothing: the CLI is never a gate.
    assert advisory.main(["--repo-root", str(git_repo), "--path", "docs/x.md"]) == 0
    silent = yaml.safe_load(capsys.readouterr().out)
    assert silent["fires"] is False
    assert silent["advisory"] is None


def test_the_threshold_is_a_knob_not_a_constant(git_repo: Path, advisory) -> None:
    (git_repo / "scripts/seed.py").write_text("x = 1\ny = 2\nz = 3\n", encoding="utf-8")
    assert advisory.advise_for_edited_file(git_repo, "scripts/seed.py", threshold=1) is not None


def test_a_tracked_unchanged_file_reports_zero_not_no_answer(git_repo: Path, advisory) -> None:
    """`git diff --numstat` prints nothing for an unchanged tracked file, which is
    indistinguishable from "no answer" unless the tracked check runs. Reporting
    None there would make the advisory silent for a reason it never established."""
    assert advisory.added_lines_vs_head(git_repo, "scripts/seed.py") == 0
    assert advisory.advise_for_edited_file(git_repo, "scripts/seed.py") is None


def test_a_suppression_state_file_that_cannot_be_written_re_advises(
    git_repo: Path, advisory, monkeypatch
) -> None:
    """A read-only or full disk must not silently disable the signal.

    A repeated advisory is noise; a missed one is the trap this exists to catch,
    so the unwritable path deliberately errs toward advising again rather than
    recording a suppression it never persisted.
    """
    (git_repo / "scripts/seed.py").write_text(
        "\n".join(f"u{i} = {i}" for i in range(80)), encoding="utf-8"
    )
    real_write = Path.write_text

    def only_the_state_file_fails(self, *args, **kwargs):
        if self.name == "advised.json":
            raise OSError("read-only file system")
        return real_write(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", only_the_state_file_fails)
    assert advisory.advise_for_edited_file(git_repo, "scripts/seed.py") is not None
    assert advisory.advise_for_edited_file(git_repo, "scripts/seed.py") is not None, (
        "an unwritable state file must re-advise, never go silent"
    )


def test_unreadable_tracked_membership_reports_no_answer(
    git_repo: Path, advisory, monkeypatch
) -> None:
    """`git diff` can succeed with no numstat row while tracked membership fails.

    That pair is the only way to reach the tracked-check's own failure path, and
    it must report "no answer" rather than fall through to the byte count, which
    would report a whole file as added for a file that is merely unchanged.
    """
    monkeypatch.setattr(
        "scripts.checkout_view.path_is_tracked",
        lambda *_args, **_kwargs: None,
    )
    assert advisory.added_lines_vs_head(git_repo, "scripts/seed.py") is None


def test_a_state_file_for_this_head_with_an_unusable_paths_key_still_suppresses_correctly(
    git_repo: Path, advisory
) -> None:
    """The corrupt-`paths` branch is only reachable when `head` MATCHES.

    A head mismatch resets the whole record before `paths` is ever read, so a
    fixture with a stale head exercises the reset, not this branch.
    """
    head = advisory._git(git_repo, "rev-parse", "HEAD").stdout.strip()
    state = git_repo / advisory._SEEN_RELPATH
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({"head": head, "paths": "not-a-list"}), encoding="utf-8")

    assert advisory._already_advised(git_repo, "scripts/seed.py", head) is False
    # The unusable value was replaced by a real list, so the second call suppresses.
    assert advisory._already_advised(git_repo, "scripts/seed.py", head) is True
