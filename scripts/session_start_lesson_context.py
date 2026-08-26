#!/usr/bin/env python3
"""Emit the session-start lesson block the SessionStart routing hook injects.

WHY THIS EXISTS. The lesson lifecycle's WRITE half was fully automated --
`persist_retro_artifact.py` refreshes `recent-lessons.md` and
`lesson-selection-index.json` on every retro -- while its READ/EVALUATE half had
ZERO production callers in this repo or any consuming one: `open_lesson_session`,
`declare_session`, and `render_lesson_selection_preview` appeared only under
`tests/`, and `record_lesson_score` recorded nothing. The continuity gate then
reported `not-evaluated/missing-start=3; violations=0` -- a GREEN verdict over a
capability that was never installed, the same "fails toward silence" class as
issue #622. This module is the missing presentation seam: the hook asks it for a
lesson block, and it either produces the exact bytes a declared session would
freeze, or says out loud that it could not.

WHAT IT COSTS, MEASURED (authoring repo, 566 files in `charness-artifacts/retro/`):

- gate miss (no ledger): one `is_file()`, no subprocess, no injected text at all;
- gate hit: one `render_lesson_selection_preview.py` subprocess, 0.85 / 0.82 /
  0.85 s wall over three runs, and 2396 bytes of injected preview at 9 items.

Cost is linear in RETRO-ARTIFACT COUNT, not ledger size: the preview rebuilds the
selection index ~4 times internally. Threading one prebuilt index through
`build_lesson_selection_preview` would remove three of those rebuilds, but it
edits the surface that produces the snapshot the ledger digests, so it is filed
in `docs/deferred-decisions.md` rather than done here.

HONEST CEILING. Injecting these bytes proves EMISSION, never PRESENTATION. A hook
cannot observe that a model read what it was handed, which is precisely why the
disposition grammar carries `not-evaluated / presentation-unproven` as a state
distinct from `emission-unproven`. Nothing here may ever be reported as "the
agent read this".

WHAT THIS MODULE MUST NOT DO. It never writes to the ledger. An automatic
session-start declaration would emit one receipt per session, and
`reconcile_records` raises `unclaimed-emission` for every receipt no in-cohort
retro disposition cites -- so every session that does not end in a retro would
become a permanent violation and the continuity gate would exit 1 forever. It is
also not idempotent (`_replay_sessions` rejects a repeated id, and the Claude
matcher is `startup|resume|clear`, so re-fires are normal), has no rollback
(`open_lesson_session.py` appends to the ledger BEFORE writing bundle, stdout,
and receipt), and would append unattended into a tracked append-only file that is
diffed against `git show HEAD:<path>`. The hook prints the declare command; a
human-directed agent runs it.

Stdlib only, on purpose: this runs inside a host's SessionStart path in EVERY
session on the machine, including repos that never opted in. It must not be able
to fail because a repo module could not be imported.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# The opt-in declaration itself. `scripts/init_lesson_ledger.py` creates it and
# nothing else does; its ABSENCE is a real, recorded opt-out, which is the one
# state where this module is allowed to stay silent.
LEDGER_RELATIVE = Path("charness-artifacts/retro/lesson-ledger.json")

PREVIEW_SCRIPT_NAME = "render_lesson_selection_preview.py"
OPEN_SESSION_SCRIPT_NAME = "open_lesson_session.py"
SEED_SCRIPT_NAME = "seed_lesson_transitions.py"
RETRO_PLAN_SCRIPT_RELATIVE = (
    Path("skills") / "public" / "retro" / "scripts" / "plan_retro_run.py",
    Path("skills") / "retro" / "scripts" / "plan_retro_run.py",
)
REFRESH_SCRIPT_RELATIVE = (
    Path("skills") / "public" / "retro" / "scripts" / "refresh_recent_lessons.py",
    Path("skills") / "retro" / "scripts" / "refresh_recent_lessons.py",
)

# The measured preview is ~0.85 s here and grows linearly with retro-artifact
# count. Bounded all the same -- an unbounded rebuild inside a session-start hook
# is a hung host session.
LESSON_PREVIEW_TIMEOUT_SECONDS = 8
LESSON_ROUTING_TIMEOUT_SECONDS = 8

# The same three words `check_auto_trigger.py` and `check_boundary_escalation.py`
# already speak, spelled as literals for the same reason they are: this module
# must not import the retro/prove adapter stack to say three words. A fourth
# spelling (`available`, `wired`, `enabled: false`) is what makes two probes
# disagree about the same repo.
STATE_EVALUATED = "evaluated"
STATE_NOT_CONFIGURED = "not-configured"
STATE_NOT_ESTABLISHED = "not-established"

UNDETERMINED_EXIT = 3

# Copied from `lesson_evaluation_continuity_lib._SESSION_ID` rather than imported,
# because this module is stdlib-only by contract (see the docstring). The lexical
# grammar is the same, but the SessionStart producer owns one extra boundary: the
# ledger's `none` sentinel is legal only in a `missing-start` disposition and must
# never be suggested as a real session id.
RESERVED_SESSION_ID = "none"
_SESSION_ID = re.compile(r"(?!none\Z)[A-Za-z0-9][A-Za-z0-9._-]*")

# Owned here, and imported by `scripts/init_lesson_ledger.py`, so the sentence a
# fresh opt-in reads at `init` time and the sentence the hook prints when the
# preview is empty are ONE string. Two hand-written copies of this instruction is
# exactly how a repo ends up being told two different next steps for the same
# state. The dependency arrow points from the heavy bootstrap script to this
# stdlib-only module, never the other way.
#
# A FUNCTION, not a constant, because the command's spelling depends on the tree
# it is read in and a constant can only carry one spelling. It shipped as a
# constant naming `python3 scripts/seed_lesson_transitions.py`, which is the one
# path a consuming repo does not have -- the same "instructs an action the reader
# cannot perform" defect #624 fixed, reproduced inside the fix for #625, and in a
# module that already resolves two other commands this way (`_refresh_command`,
# `_declare_command`). The audience for this sentence is precisely a repo with an
# empty ledger, which in a consuming repo is every repo that just opted in.
def seed_lesson_next_step(repo_root: Path) -> str:
    return (
        "Next: a lesson enters the ledger only from a retro bullet tagged "
        "`recurrence-class: <slug>`; tag one, then append its seed transition with "
        f"`{_seed_command(repo_root)} --dry-run` to inspect and the "
        "same command without `--dry-run` to write. Until at least "
        "one lesson is seeded, `record_lesson_session.py` refuses with `preview selected no "
        "eligible lessons` and the only honest retro disposition stays `not-evaluated / "
        "missing-start`."
    )

_EMISSION_CEILING = (
    "This text being injected proves the lesson bytes were EMITTED, not that they were "
    "presented to or used by anyone. Score only lessons from a list actually presented "
    "before the affected work; otherwise the honest disposition is `not-evaluated / "
    "presentation-unproven`."
)


def _script_tree_root() -> Path:
    """The tree this copy belongs to: repo root here, `plugins/<pkg>` when installed."""
    return Path(__file__).resolve().parent.parent


def _sibling_script(name: str) -> Path:
    return Path(__file__).resolve().parent / name


def _refresh_command(repo_root: Path) -> str:
    """The runnable index-refresh command for THIS layout, not one repo's spelling.

    A consuming repo has no `skills/public/...` of its own; it gets
    `skills/retro/scripts/` inside the installed plugin. Naming a path the reader
    does not have is the same "instructs an impossible edit" defect #624 fixed, so
    resolve against the tree this script is actually running from.
    """
    tree = _script_tree_root()
    for relative in REFRESH_SCRIPT_RELATIVE:
        if (tree / relative).is_file():
            return f"python3 {tree / relative} --repo-root {repo_root}"
    # Unreachable when either shipped layout is intact. The bare token follows
    # `lesson_command_citation.PLUGIN_DIR_TOKEN`: a `<...>` placeholder inside a
    # pasted command becomes a shell redirection error, and `skills/public/` is a
    # spelling no consuming tree has (#632).
    return (
        "python3 CHARNESS_PLUGIN_DIR/skills/retro/scripts/refresh_recent_lessons.py "
        f"--repo-root {repo_root}"
    )


def _seed_command(repo_root: Path) -> str:
    """The runnable seeder command for THIS layout, not for one repo's spelling.

    Repo-local first, then the copy beside this module, mirroring
    `lesson_evaluation_records_lib.repo_or_installed_command`'s resolution order so
    a consuming author cites the same script its own broad gate would. That helper
    is not imported here because this module is stdlib-only by contract (see the
    module docstring): it runs inside a host SessionStart path in every session on
    the machine, and an import of the repo-module stack is what takes the routing
    directive down with it.
    """
    local = repo_root / "scripts" / SEED_SCRIPT_NAME
    if local.is_file():
        # `repo_root`, not `.`. The root is used to CHOOSE this branch and must not then
        # be discarded: `init_lesson_ledger.py --repo-root <other checkout>` would
        # otherwise print a next step whose `.` resolves to the operator's cwd -- a
        # different repo than the one just initialized. The script path stays relative
        # here, matching `repo_or_installed_command`'s in-repo spelling.
        return f"python3 scripts/{SEED_SCRIPT_NAME} --repo-root {repo_root}"
    return f"python3 {_sibling_script(SEED_SCRIPT_NAME)} --repo-root {repo_root}"


def _retro_plan_script() -> Path | None:
    """Find the canonical retro router in the source or installed tree."""
    tree = _script_tree_root()
    return next((tree / path for path in RETRO_PLAN_SCRIPT_RELATIVE if (tree / path).is_file()), None)


def _utc_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def derive_session_id(payload: dict[str, Any], *, repo_root: Path, today: str | None = None) -> str:
    """One string that is BOTH the suggested session id and the selection seed.

    Seed == session id on purpose: the preview the hook renders and the snapshot a
    later `open_lesson_session.py --session-id X --seed X` freezes are then derived
    from the same value, so the presented list is reproducible and citable from the
    retro that disposes it. Two values would let the presented list and the frozen
    one diverge, which is the defect, not the latency.

    Both hosts put a `session_id` in the SessionStart payload (Codex confirmed
    2026-05-29, charness-artifacts/gather/2026-05-22-codex-hooks-surface.md), and
    host UUIDs satisfy the ledger's id grammar. When they do not -- an unexpected
    host, a spelling with `/` or spaces -- fall back to a digest rather than
    suggesting an id `validate_session_id` will refuse at declare time.

    The fallback digest is over repo root and source only, so two host sessions in
    the same repo on the same day get the same SUGGESTED id. That is deliberate
    and safe: this module never writes, and a second `open_lesson_session.py` with
    a repeated id fails loudly on `duplicate session_id` rather than silently
    double-appending. Pick a different `--session-id` when that refusal fires.
    """
    date_text = today or _utc_date()
    raw = payload.get("session_id")
    if isinstance(raw, str) and raw.strip():
        host_id = raw.strip()
        if _SESSION_ID.fullmatch(host_id):
            candidate = f"{date_text}-{host_id}"
            if _SESSION_ID.fullmatch(candidate):
                return candidate
    material = f"{repo_root}\0{payload.get('source')}".encode("utf-8", "replace")
    return f"{date_text}-{hashlib.sha256(material).hexdigest()[:12]}"


def _run_child(script: Path, arguments: list[str], *, timeout: int) -> subprocess.CompletedProcess:
    """Run a sibling probe with one pinned module-resolution environment."""
    environment = {**os.environ, "CHARNESS_REPO_ROOT": str(_script_tree_root())}
    return subprocess.run(
        [sys.executable, str(script), *arguments],
        capture_output=True,
        timeout=timeout,
        check=False,
        env=environment,
    )


def _run_preview(repo_root: Path, seed: str) -> tuple[int, str, str]:
    script = _sibling_script(PREVIEW_SCRIPT_NAME)
    if not script.is_file():
        raise OSError(f"no `{PREVIEW_SCRIPT_NAME}` beside this script at `{script.parent}`")
    # Pin module resolution to the tree this script lives in. `runtime_bootstrap`
    # honors `CHARNESS_REPO_ROOT` when locating the `scripts.` package, and a
    # session that exported it for an unrelated repo would otherwise make the
    # preview import from a tree that has no `scripts/` package at all -- a
    # `not-established` caused by the caller's environment rather than by the
    # repo's state. The pinned value is what `repo_root_from_script` computes with
    # no override, so this is the documented default made explicit.
    completed = _run_child(
        script,
        ["--repo-root", str(repo_root), "--seed", seed],
        timeout=LESSON_PREVIEW_TIMEOUT_SECONDS,
    )
    return (
        completed.returncode,
        completed.stdout.decode("utf-8", "replace"),
        completed.stderr.decode("utf-8", "replace"),
    )


def _parse_preview(stdout: str) -> Any:
    """Read the one structured document `render_lesson_selection_preview.py` emits.

    That command emits YAML through `yaml_output`, which falls back to JSON syntax
    when PyYAML is not importable. The child runs under `sys.executable` -- THIS
    interpreter -- so parent and child always agree on whether PyYAML is available,
    and the JSON branch here is reachable exactly when the child took the JSON
    branch there. That equivalence is what keeps this module stdlib-only by
    contract (see the module docstring): it must never fail to produce a lesson
    block because a package is missing.
    """
    try:
        import yaml
    except ImportError:
        return json.loads(stdout)
    return yaml.safe_load(stdout)


def _run_unclaimed_sessions(repo_root: Path) -> dict[str, Any]:
    """Read canonical retro routing without changing lesson state.

    The retro planner delegates membership to the same shared helper that the
    continuity gate uses. Calling that owner through its CLI keeps this hook
    stdlib-only and prevents a second ledger/receipt/disposition rule from
    drifting away from the gate.
    """
    script = _retro_plan_script()
    if script is None:
        raise OSError("no `plan_retro_run.py` beside the SessionStart module")
    completed = _run_child(
        script,
        ["--repo-root", str(repo_root)],
        timeout=LESSON_ROUTING_TIMEOUT_SECONDS,
    )
    if completed.returncode != 0:
        raise OSError(
            f"`{script.name}` exited {completed.returncode}: "
            f"{_first_line(completed.stderr.decode('utf-8', 'replace'))}"
        )
    try:
        payload = _parse_preview(completed.stdout.decode("utf-8", "replace"))
        lesson_session = payload.get("lesson_session") if isinstance(payload, dict) else None
    except Exception as exc:  # noqa: BLE001 -- unreadable routing is not an empty answer
        raise ValueError(f"`{script.name}` emitted unreadable output ({type(exc).__name__}: {exc})") from exc
    if not isinstance(lesson_session, dict):
        raise ValueError(f"`{script.name}` emitted no `lesson_session` routing payload")
    if lesson_session.get("configuration_status") == "no-unclaimed-session":
        return {"state": "no-unclaimed-session", "sessions": []}
    rows = lesson_session.get("sessions")
    if lesson_session.get("state") != STATE_EVALUATED or not isinstance(rows, list):
        raise ValueError(
            "retro routing is not established "
            f"({lesson_session.get('configuration_status') or lesson_session.get('state')}): "
            f"{lesson_session.get('reason') or 'no reason reported'}"
        )
    if not all(
        isinstance(row, dict)
        and isinstance(row.get("session_id"), str)
        and isinstance(row.get("bundle_path"), str)
        for row in rows
    ):
        raise ValueError("retro routing emitted a session without id or frozen bundle path")
    sessions = [
        {"session_id": row["session_id"], "bundle_path": row["bundle_path"]} for row in rows
    ]
    if not sessions:
        raise ValueError("retro routing claimed evaluated state but emitted no sessions")
    return {"state": STATE_EVALUATED, "sessions": sessions}


def _first_line(text: str) -> str:
    """The most informative single line of the child's stderr.

    A Python child reports its cause on the LAST line; its FIRST line is the
    constant `Traceback (most recent call last):`, which names nothing. Since
    `render_lesson_selection_preview.py` fails by raising -- an invalid ledger, a
    stale selection index -- naively taking the first line publishes a
    `not-established` cause that is the same eight words for every distinct
    failure, which is a diagnostic no operator can act on.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "(no diagnostic output)"
    if lines[0].startswith("Traceback (most recent call last)"):
        return lines[-1]
    return lines[0]


def _not_established(repo_root: Path, ledger: Path, cause: str) -> dict[str, Any]:
    """Say it out loud. `not-established` MUST inject text.

    This is the state a stale `lesson-selection-index.json` produces --
    `check_lesson_selection_index` byte-compares the persisted index against what
    the RUNNING copy rebuilds, so a consumer whose index was written by an older
    plugin version fails here until it refreshes -- and it is the state a timeout
    or an unreadable ledger produces. Staying silent for it would recreate exactly
    the defect this whole slice exists to fix: a loop that looks wired because
    nothing complained.
    """
    return {
        "state": STATE_NOT_ESTABLISHED,
        "ledger_path": str(ledger),
        "session_id": None,
        "eligible_lessons_present": None,
        "cause": cause,
        "remediation": _refresh_command(repo_root),
        "text": (
            f"charness lesson loop (state: {STATE_NOT_ESTABLISHED}): this repo DECLARES a lesson "
            f"evaluator (`{LEDGER_RELATIVE.as_posix()}`) but its lesson selection could not be "
            "produced, so this session has no presented lesson list. Do not read that absence as "
            f"`no lessons owed`. Cause: {cause} Remediation: {_refresh_command(repo_root)}"
        ),
    }


def build_lesson_context(repo_root: Path | None, payload: dict[str, Any]) -> dict[str, Any]:
    """Classify this session's lesson-loop state and render the text to inject.

    Returns a payload whose FIRST key is `state`, matching `check_auto_trigger.py`.
    `text` is `None` only under `not-configured`; every other state injects.
    """
    if repo_root is None:
        # No discoverable repo root means no repo whose opt-in could be read. This
        # is the same fail-closed silence the handoff branch already takes for an
        # unresolvable cwd, and injecting a lesson complaint about a directory that
        # is not a repo would fire in every non-repo shell on the machine.
        return {
            "state": STATE_NOT_CONFIGURED,
            "ledger_path": None,
            "session_id": None,
            "eligible_lessons_present": None,
            "reason": "no repository root was discoverable from the session cwd",
            "text": None,
        }
    ledger = repo_root / LEDGER_RELATIVE
    if not ledger.is_file():
        # The whole opt-out path: ONE `is_file()`, no subprocess, no injected text.
        # Never run the preview to discover that a repo has no ledger.
        return {
            "state": STATE_NOT_CONFIGURED,
            "ledger_path": str(ledger),
            "session_id": None,
            "eligible_lessons_present": None,
            "reason": (
                "this repo declares no lesson evaluator; the disposition floor is inert and no "
                "lesson context is injected"
            ),
            "text": None,
        }
    seed = derive_session_id(payload, repo_root=repo_root)
    try:
        code, out, err = _run_preview(repo_root, seed)
    except subprocess.TimeoutExpired:
        return _not_established(
            repo_root,
            ledger,
            f"the lesson preview exceeded its {LESSON_PREVIEW_TIMEOUT_SECONDS}s bound.",
        )
    except (OSError, ValueError) as exc:
        return _not_established(repo_root, ledger, f"{type(exc).__name__}: {exc}.")
    if code != 0:
        return _not_established(
            repo_root, ledger, f"`{PREVIEW_SCRIPT_NAME}` exited {code}: {_first_line(err)}"
        )
    try:
        preview = _parse_preview(out)
    except Exception as exc:  # noqa: BLE001 -- an unreadable preview is `not-established`, never silence
        return _not_established(
            repo_root,
            ledger,
            f"`{PREVIEW_SCRIPT_NAME}` exited 0 but its output could not be parsed "
            f"({type(exc).__name__}: {exc}).",
        )
    if not isinstance(preview, dict) or not isinstance(preview.get("preview_text"), str):
        return _not_established(
            repo_root,
            ledger,
            f"`{PREVIEW_SCRIPT_NAME}` exited 0 but emitted no `preview_text`, so there are no "
            "lesson bytes to present.",
        )
    try:
        routing = _run_unclaimed_sessions(repo_root)
    except (OSError, ValueError, TypeError, subprocess.TimeoutExpired) as exc:
        routing = {"state": STATE_NOT_ESTABLISHED, "cause": f"{type(exc).__name__}: {exc}."}
    return _evaluated(repo_root, ledger, seed, preview, routing)


def _declare_command(repo_root: Path, session_id: str) -> str:
    return (
        f"python3 {_sibling_script(OPEN_SESSION_SCRIPT_NAME)} --repo-root {repo_root} "
        f"--session-id {session_id} --seed {session_id}"
    )


def _routing_details(repo_root: Path, routing: dict[str, Any]) -> tuple[str, list[dict[str, str]] | None]:
    if routing["state"] == STATE_EVALUATED:
        rows = "\n".join(
            f"  session_id: `{row['session_id']}`\n  frozen_bundle: `{row['bundle_path']}`"
            for row in routing["sessions"]
        )
        return (
            "\n\nOutstanding declared lesson session(s) still need an owner before the next push "
            "gate. Inspect the frozen bundle and carry the session into the retro workflow; "
            "SessionStart routing does not claim, score, or disposition it:\n"
            f"{rows}\nUse the canonical router beside this hook."
        ), routing["sessions"]
    if routing["state"] != "not-established":
        return "", []
    return (
        "\n\nSession-start could not establish whether a previously declared lesson session is "
        "unclaimed. Do not read this as no outstanding work or write an automatic disposition. "
        f"Cause: {routing['cause']}",
        None,
    )


def _evaluated(
    repo_root: Path,
    ledger: Path,
    seed: str,
    preview: dict[str, Any],
    routing: dict[str, Any],
) -> dict[str, Any]:
    """The preview ran. Either it selected lessons, or the ledger is still empty.

    ONE subprocess answers both questions. The preview command carries its rendered
    bytes as `preview_text` inside the same document that carries `items`, so item
    presence is read off the structured list while the injected bytes stay the
    renderer's own -- no second run, and no second hand-written copy of the item
    format here.
    """
    preview_text: str = preview["preview_text"]
    items = preview.get("items")
    has_items = isinstance(items, list) and bool(items)
    notice, unclaimed_sessions = _routing_details(repo_root, routing)
    result: dict[str, Any] = {"state": STATE_EVALUATED, "ledger_path": str(ledger), "session_id": seed}
    if not has_items:
        result.update(
            eligible_lessons_present=False,
            text=(
                f"charness lesson loop (state: {STATE_EVALUATED}): this repo declares a lesson "
                "evaluator, but the selection preview chose 0 eligible lessons, so no list can be "
                f"presented and no session can be declared yet. {seed_lesson_next_step(repo_root)}"
            ),
        )
    else:
        declare = _declare_command(repo_root, seed)
        # The preview bytes go in VERBATIM and UNTRUNCATED: they are the exact bytes
        # `open_lesson_session.py` freezes into the bundle and digests into the receipt.
        result.update(
            eligible_lessons_present=True,
            declare_command=declare,
            preview_byte_count=len(preview_text.encode("utf-8")),
            text=(
                f"charness lesson loop (state: {STATE_EVALUATED}): this repo declares a lesson "
                "evaluator. The list below is exactly what a declared session would freeze — read it "
                f"before the work.\n\n{preview_text.rstrip()}\n\n"
                f"Declare this session before the work if it will end in a retro:\n{declare}"
            ),
        )
    result["text"] += notice + (f"\n\n{_EMISSION_CEILING}" if has_items else "")
    result["unclaimed_sessions"] = unclaimed_sessions
    if unclaimed_sessions is None:
        result["unclaimed_sessions_cause"] = routing["cause"]
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--session-id",
        help="Host session id to derive the suggested session id and seed from (defaults to a digest).",
    )
    args = parser.parse_args(argv)
    payload: dict[str, Any] = {"source": "cli"}
    if args.session_id:
        payload["session_id"] = args.session_id
    context = build_lesson_context(args.repo_root.resolve(), payload)
    # Imported HERE, not at module scope. The SessionStart hook imports this module
    # and calls `build_lesson_context` in process; only the CLI reaches `main`. A
    # top-level import would put a non-stdlib-shaped dependency on the hook's import
    # path, which the module docstring forbids for exactly that reason.
    from yaml_output import emit_yaml

    # `text` is a payload key, so the block a hook would inject is still in the
    # output verbatim; the `not-configured` states that carry `text: null` also carry
    # the `reason` the prose fallback used to print in its place.
    emit_yaml(context)
    # Same byte contract as `check_auto_trigger.py` and `check_boundary_escalation.py`:
    # ANY nonzero exit means "not a no". `not-configured` is a real recorded answer
    # (this repo opted out) and exits 0; `not-established` could not tell and exits 3.
    return UNDETERMINED_EXIT if context["state"] == STATE_NOT_ESTABLISHED else 0


if __name__ == "__main__":
    raise SystemExit(main())
