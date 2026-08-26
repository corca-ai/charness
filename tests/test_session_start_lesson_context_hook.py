from __future__ import annotations

import importlib.util
import io
import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest
import session_start_lesson_context as lesson_context
import session_start_routing as hook
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_SCRIPT = REPO_ROOT / "scripts" / "session_start_routing.py"
LESSON_CONTEXT_SCRIPT = REPO_ROOT / "scripts" / "session_start_lesson_context.py"


def _configured_handoff_repo(tmp_path: Path) -> Path:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "handoff-adapter.yaml").write_text(
        "version: 1\nrepo: fixture\nlanguage: en\noutput_dir: state\n",
        encoding="utf-8",
    )
    return tmp_path

def test_lesson_ledger_gate_constant_matches_the_context_module() -> None:
    """The fallback gate copy exists only for a broken install; it must not drift.

    `session_start_routing` re-spells the ledger path so that, if this hook ever
    ships without its sibling module, an opted-OUT repo still hears nothing while
    an opted-IN repo hears that its loop is broken. Two spellings of the gate would
    make one of those two branches wrong.
    """
    assert hook.LESSON_LEDGER_RELATIVE == lesson_context.LEDGER_RELATIVE


def test_directive_is_unchanged_for_a_repo_that_declared_no_lesson_evaluator(
    tmp_path: Path,
) -> None:
    repo = _configured_handoff_repo(tmp_path)
    (repo / "state").mkdir()
    (repo / "state" / "handoff.md").write_text("# Handoff\n", encoding="utf-8")

    directive = hook.build_additional_context(str(repo), {"session_id": "host-1"})

    assert "lesson loop" not in directive
    assert directive.endswith("report the command failure.")


def test_opted_in_repo_appends_the_lesson_block_to_the_routing_directive(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _configured_handoff_repo(tmp_path)
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    (repo / "charness-artifacts" / "retro" / "lesson-ledger.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        hook._lesson_context,
        "build_lesson_context",
        lambda root, payload: {"state": "evaluated", "text": f"LESSON BLOCK for {payload['session_id']}"},
    )

    directive = hook.build_additional_context(str(repo), {"session_id": "host-1"})

    assert "charness catalog list" in directive
    assert directive.endswith("\n\nLESSON BLOCK for host-1")


def test_a_crashing_lesson_context_still_speaks_and_never_breaks_the_session(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _configured_handoff_repo(tmp_path)
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    (repo / "charness-artifacts" / "retro" / "lesson-ledger.json").write_text("{}", encoding="utf-8")

    def explode(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(hook._lesson_context, "build_lesson_context", explode)

    directive = hook.build_additional_context(str(repo), {"session_id": "host-1"})

    assert "state: not-established" in directive
    assert "RuntimeError" in directive


def test_a_missing_context_module_is_loud_for_opted_in_and_silent_for_opted_out(
    tmp_path: Path, monkeypatch
) -> None:
    """A packaging failure must not be paid for by repos that never opted in.

    A hard import would instead crash this hook in EVERY session on the machine,
    which is a far larger blast radius than the loop it protects.
    """
    monkeypatch.setattr(hook, "_lesson_context", None)

    (tmp_path / "out").mkdir()
    (tmp_path / "in").mkdir()
    opted_out = _configured_handoff_repo(tmp_path / "out")
    assert "lesson loop" not in hook.build_additional_context(str(opted_out), {})

    opted_in = _configured_handoff_repo(tmp_path / "in")
    (opted_in / "charness-artifacts" / "retro").mkdir(parents=True)
    (opted_in / "charness-artifacts" / "retro" / "lesson-ledger.json").write_text(
        "{}", encoding="utf-8"
    )
    directive = hook.build_additional_context(str(opted_in), {})
    assert "state: not-established" in directive
    assert "session_start_lesson_context.py" in directive


def test_a_corrupt_sibling_module_never_costs_the_routing_directive(tmp_path: Path) -> None:
    """A TRUNCATED sibling file is the realistic packaging failure, and it is not
    an `ImportError`.

    A half-written `session_start_lesson_context.py` raises `SyntaxError` at
    module import, which is outside `except ImportError` AND outside `main()`'s
    own `except Exception` (module import runs first). Narrowly guarding the
    import therefore loses the whole hook -- empty stdout, no routing directive --
    in EVERY session on the machine, opted in or not, which is precisely the
    "a missing optional host hook must not block session startup" line.

    Run as a real subprocess against a real broken file: monkeypatching
    `hook._lesson_context = None` cannot reach an import-time failure, which is
    why the previous guard's mutation survived the suite.
    """
    install = tmp_path / "install" / "scripts"
    install.mkdir(parents=True)
    (install / "session_start_routing.py").write_text(
        HOOK_SCRIPT.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (install / "session_start_lesson_context.py").write_text(
        "def build_lesson_context(  # truncated mid-signature\n", encoding="utf-8"
    )
    (tmp_path / "repo").mkdir()
    opted_in = _configured_handoff_repo(tmp_path / "repo")
    (opted_in / "charness-artifacts" / "retro").mkdir(parents=True)
    (opted_in / "charness-artifacts" / "retro" / "lesson-ledger.json").write_text(
        "{}", encoding="utf-8"
    )

    completed = subprocess.run(
        ["python3", str(install / "session_start_routing.py"), "--host", "claude"],
        input=json.dumps({"cwd": str(opted_in), "source": "startup"}),
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    context = json.loads(completed.stdout)["hookSpecificOutput"]["additionalContext"]
    # The routing half survives untouched...
    assert "charness session-start routing" in context
    # ...and the lesson half degrades to the same loud `not-established` a missing
    # module produces, rather than to silence or to a dead hook.
    assert "state: not-established" in context
    assert "session_start_lesson_context.py" in context


def test_a_corrupt_sibling_module_stays_silent_for_a_repo_that_never_opted_in(
    tmp_path: Path,
) -> None:
    """The blast radius of a broken install must stop at repos that opted in."""
    install = tmp_path / "install" / "scripts"
    install.mkdir(parents=True)
    (install / "session_start_routing.py").write_text(
        HOOK_SCRIPT.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (install / "session_start_lesson_context.py").write_text("(", encoding="utf-8")
    (tmp_path / "repo").mkdir()
    opted_out = _configured_handoff_repo(tmp_path / "repo")

    completed = subprocess.run(
        ["python3", str(install / "session_start_routing.py"), "--host", "claude"],
        input=json.dumps({"cwd": str(opted_out), "source": "startup"}),
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    context = json.loads(completed.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "charness session-start routing" in context
    assert "lesson" not in context.lower()


def test_importing_the_hook_over_a_broken_sibling_degrades_instead_of_raising(
    tmp_path: Path, monkeypatch
) -> None:
    """The `except Exception` around the sibling import, executed on THIS file.

    The two subprocess cases above prove the end-to-end behavior against a copied
    install, but they exercise a copy at another path -- nothing observes the guard
    in the module this repo ships. So load the real hook file with a truncated
    sibling shadowing the good one on `sys.path`: the import raises `SyntaxError`
    at module level, which is outside `except ImportError` and outside `main()`'s
    own handler, and narrowing or removing this clause means `exec_module` below
    raises instead of returning a usable module -- in every session on the machine.
    """
    broken_install = tmp_path / "broken-install"
    broken_install.mkdir()
    (broken_install / "session_start_lesson_context.py").write_text(
        "def build_lesson_context(  # truncated mid-signature\n", encoding="utf-8"
    )
    monkeypatch.syspath_prepend(str(broken_install))
    # The good sibling is already imported by this module; drop it so the import
    # inside the hook really re-resolves and finds the truncated file.
    monkeypatch.delitem(sys.modules, "session_start_lesson_context", raising=False)
    importlib.invalidate_caches()

    spec = importlib.util.spec_from_file_location("session_start_routing_broken_sibling", HOOK_SCRIPT)
    degraded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(degraded)

    assert degraded._lesson_context is None
    # The routing half is untouched -- that is the thing an import-time crash costs.
    assert "charness session-start routing" in degraded.build_additional_context()

    (tmp_path / "opted-in").mkdir()
    opted_in = _configured_handoff_repo(tmp_path / "opted-in")
    (opted_in / "charness-artifacts" / "retro").mkdir(parents=True)
    (opted_in / "charness-artifacts" / "retro" / "lesson-ledger.json").write_text(
        "{}", encoding="utf-8"
    )
    block = degraded._lesson_block(str(opted_in), {})
    # Loud for a repo that opted in: silence here would read as `no lessons owed`.
    assert "state: not-established" in block
    assert "session_start_lesson_context.py" in block
    assert "reinstall or update charness" in block

    # ...and mute for a repo that never opted in, so a broken install costs nothing
    # in the sessions that never asked for a lesson loop.
    (tmp_path / "opted-out").mkdir()
    opted_out = _configured_handoff_repo(tmp_path / "opted-out")
    assert degraded._lesson_block(str(opted_out), {}) == ""


# --- the sibling module's own CLI ------------------------------------------
#
# Pinned here rather than beside `build_lesson_context`'s unit tests because this
# is the surface the hook above degrades around: the exit byte and the prose line
# are what an operator sees when they run the module by hand after reading the
# `not-established` block, and both are stdlib-only by contract.


def test_the_lesson_context_cli_carries_both_the_state_and_the_injectable_text(
    tmp_path: Path, capsys
) -> None:
    """Two payload shapes, because `text` has two sides.

    `text` is `None` only under `not-configured`; the prose fallback that used to
    print a `state: ... — <reason>` line in its place is gone, so `reason` has to
    carry that sentence or an operator who just ran the command learns nothing.
    Every other state carries injectable text, and that text -- not a terse state
    summary -- is what names the cause and the remediation.
    """
    opted_out = tmp_path / "opted-out"
    opted_out.mkdir()

    assert lesson_context.main(["--repo-root", str(opted_out)]) == 0

    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["state"] == "not-configured"
    assert payload["text"] is None
    assert "declares no lesson evaluator" in payload["reason"]

    opted_in = tmp_path / "opted-in"
    (opted_in / "charness-artifacts" / "retro").mkdir(parents=True)
    (opted_in / "charness-artifacts" / "retro" / "lesson-ledger.json").write_text(
        "{ not a ledger", encoding="utf-8"
    )

    assert lesson_context.main(["--repo-root", str(opted_in)]) == 3

    payload = yaml.safe_load(capsys.readouterr().out)
    # The injectable text itself, not just the state: it names the state, the
    # cause, and what to run next.
    assert payload["state"] == "not-established"
    assert "not-established" in payload["text"]
    assert "lesson-ledger.json" in payload["text"]


def test_the_lesson_context_entrypoint_exits_with_the_undetermined_byte(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """`raise SystemExit(main())`, and the byte it must not flatten.

    The hook block reads `nonzero means not a no`: `not-configured` is a recorded
    answer and exits 0, while `not-established` could not tell and exits 3. An
    entrypoint that exited 0 unconditionally would turn every undetermined session
    into a recorded opt-out, which is the exact reading the module forbids.
    """
    repo = tmp_path / "opted-in"
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    (repo / "charness-artifacts" / "retro" / "lesson-ledger.json").write_text(
        "{ not a ledger", encoding="utf-8"
    )
    monkeypatch.setattr(
        sys, "argv", ["session_start_lesson_context.py", "--repo-root", str(repo)]
    )

    with pytest.raises(SystemExit) as caught:
        runpy.run_path(str(LESSON_CONTEXT_SCRIPT), run_name="__main__")

    assert caught.value.code == lesson_context.UNDETERMINED_EXIT == 3
    assert yaml.safe_load(capsys.readouterr().out)["state"] == "not-established"


def test_main_threads_the_host_payload_into_the_lesson_block(
    tmp_path: Path, monkeypatch
) -> None:
    """`main()` must hand the WHOLE payload down, not just its `cwd`.

    The host `session_id` is what makes the suggested session id (and therefore
    the selection seed) reproducible across the hook block, the declare command an
    operator retypes, and the retro that cites it. Dropping it silently downgrades
    every session to the repo+source digest fallback, and nothing else in the hook
    would notice.
    """
    repo = _configured_handoff_repo(tmp_path)
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    (repo / "charness-artifacts" / "retro" / "lesson-ledger.json").write_text(
        "{}", encoding="utf-8"
    )
    seen: list[dict[str, object]] = []

    def record(root, payload):
        seen.append(payload)
        return {"state": "evaluated", "text": "LESSON BLOCK"}

    monkeypatch.setattr(hook._lesson_context, "build_lesson_context", record)
    monkeypatch.setattr(
        "sys.stdin", io.StringIO(json.dumps({"cwd": str(repo), "session_id": "host-42"}))
    )

    assert hook.main(["--host", "claude"]) == 0

    assert seen and seen[0].get("session_id") == "host-42"


def test_repo_root_discovery_fails_closed_at_each_boundary(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    assert hook._discover_repo_root(str(missing)) is None

    git_only = tmp_path / "git-only"
    (git_only / ".git").mkdir(parents=True)
    nested = git_only / "nested"
    nested.mkdir()
    assert hook._discover_repo_root(str(nested)) == git_only

    configured = tmp_path / "configured"
    configured.mkdir()
    repo = _configured_handoff_repo(configured)
    assert hook._discover_repo_root(str(repo)) == repo
