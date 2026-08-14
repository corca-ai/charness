#!/usr/bin/env python3
"""Resolve who authorized a repo's bounded fresh-eye subagent reviews.

The contract lives in the sibling reference ``fresh-eye-subagent-review.md``
("Where The Delegation Request Comes From"). This script is its deterministic
half: a skill that MANDATES bounded review cannot also AUTHORIZE it, so the
grant is resolved as a ladder and the first rung that answers wins.

1. ``<repo-root>/AGENTS.md`` carries a ``Subagent Delegation`` contract.
2. Else ``<repo-root>/.agents/subagent-delegation.json`` records a decision.
3. Else ``ask`` -- put the question to the user once, then ``record`` the
   answer into rung 2 so it is asked at most once per repo.

Naming only rung 1 is what made the mandate inert in every repo that never ran
``setup``: the review was required, no source of authorization was reachable,
and the refusal emitted no failure, no log line, and no ticket.

Rung 2 is read even when rung 1 answers, because ``setup`` WRITES the rung-1
block: without that read, a user who declined at rung 3 would have their answer
silently erased by the next ``setup`` run. A recorded ``declined`` under a
present rung-1 block is a CONFLICT and resolves to ``ask``, never to ``granted``
and never to a silently-dropped "no".

Fail-closed direction matters and is the opposite of most gates here: anything
unreadable as a decision resolves to ``ask``, never to ``granted``. Asking a
redundant question costs one turn; a silent self-grant would let the plugin
authorize its own spawns in every repo that installs it.

The record is repo-owned testimony, not proof of human authorship -- no
file-based mechanism can prove that. What it does buy is an auditable, per-repo,
diffable record: ``resolve`` surfaces ``recorded_by`` / ``recorded_on`` /
``note`` at the point of use so a grant with no provenance is visible as one,
and ``record`` refuses to write a ``granted`` with no ``--note``.

Record storage lives in the sibling ``subagent_delegation_record.py``.

Subcommands ``resolve`` and ``record``. Exit codes: 0 resolved (any decision,
including ``ask`` and ``declined`` -- they are answers, not errors) or recorded,
2 usage error, 3 the record could not be written (the answer was NOT persisted,
so the caller must not treat the question as asked).
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import sys
from pathlib import Path


def _load_record_module():
    """Load the sibling record module by path, not by package import: this file
    runs from the repo AND from an installed plugin's `shared/scripts/`, where no
    package context exists and the cwd is the consuming repository."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "subagent_delegation_record.py")
    spec = importlib.util.spec_from_file_location("subagent_delegation_record", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"delegation record module not found beside this script: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_yaml_output():
    """Load the shared YAML renderer from the nearest tree root, by path.

    Same both-layouts problem `_load_record_module` solves for a sibling, one
    tier up: the helper is `<repo>/scripts/yaml_output.py` in the authoring tree
    and `<plugin-root>/scripts/yaml_output.py` once exported, which sit at
    different depths from here, so the root is walked to rather than counted.
    The walk is BOUNDED for the reason `authoring_script_shim.locate` records --
    an unbounded one climbs past the package into the CONSUMING repository and
    would execute whatever `scripts/yaml_output.py` it found there."""
    directory = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        directory = os.path.dirname(directory)
        candidate = os.path.join(directory, "scripts", "yaml_output.py")
        if os.path.isfile(candidate):
            spec = importlib.util.spec_from_file_location("charness_yaml_output", candidate)
            if spec is None or spec.loader is None:
                break
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scripts/yaml_output.py not found within 5 ancestors of this script")


_RECORD = _load_record_module()
_YAML = _load_yaml_output()
render_yaml = _YAML.render_yaml
emit_yaml = _YAML.emit_yaml
DelegationError = _RECORD.DelegationError
RecordWriteError = _RECORD.RecordWriteError
read_delegation_record = _RECORD.read_delegation_record
record = _RECORD.write_delegation_record
RECORD_RELPATH = _RECORD.RECORD_RELPATH
RECORD_VERSION = _RECORD.RECORD_VERSION
DECISION_FIELD = _RECORD.DECISION_FIELD
GRANTED = _RECORD.GRANTED
DECLINED = _RECORD.DECLINED
RECORDABLE_DECISIONS = _RECORD.RECORDABLE_DECISIONS
CANONICAL_SCOPES = _RECORD.CANONICAL_SCOPES

ASK = "ask"

# Deliberately restated rather than imported, matching the two sibling readers
# (`scripts/validate_critique_artifacts.has_repo_delegation_contract` and
# `skills/public/issue/scripts/issue_critique_observer.repo_requires_delegated_observer`):
# portable skill scripts must not reach into the authoring repo's `scripts/`.
# The duplication is guarded by a parity test that runs ALL THREE readers over a
# shared fixture set -- an earlier parity test compared only marker text and so
# could not see the readers disagreeing about behaviour.
DELEGATION_CONTRACT_MARKERS = (
    "subagent delegation",
    "repo-mandated bounded fresh-eye subagent reviews are already delegated",
)
_MARKUP_FLATTEN_RE = re.compile(r"[`*_]+")
_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_contract_text(text: str) -> str:
    """Flatten a markdown body to the form the delegation markers are matched against.

    Three normalizations, each closing a way the SAME sentence stopped matching:

    * inline markup is REMOVED, not tolerated -- this repo writes
      ``**already delegated**`` and the literal comparison returned False in the
      repo that authored the contract;
    * whitespace is collapsed, because the 58-character marker only fits on one
      line at the template's current wrap width. Reflowing that bullet -- a
      prettier run, a narrower column -- would otherwise drop an adopting repo
      off rung 1. Fixing this widens matching and refuses strictly less;
    * fenced blocks are DROPPED, because a fence is documentation, not the
      repo's own assertion. `setup`'s own policy reference ships the delegation
      template inside a fence for operators to copy, so a repo that pasted that
      reference in while explicitly NOT adopting the contract would otherwise
      read as having granted spawn rights.
    """

    kept: list[str] = []
    pending: list[str] = []
    opener: str | None = None
    for line in text.splitlines():
        match = _FENCE_RE.match(line)
        if match:
            marker = match.group(1)
            if opener is None:
                opener = marker
                pending = []
                continue
            if marker[0] == opener[0] and len(marker) >= len(opener):
                opener = None
                pending = []
                continue
        if opener is None:
            kept.append(line)
        else:
            pending.append(line)
    # An UNCLOSED fence must not swallow the rest of the file. Dropping everything
    # after a stray ``` would silently un-adopt a repo whose contract sits below
    # it -- no failure, no log line, no ticket, which is the class this ladder was
    # built to close. Markdown renderers auto-close at EOF, so the file looks fine
    # to every human. Treat the unterminated tail as content: the error direction
    # is toward matching, which refuses strictly less.
    kept.extend(pending)
    flattened = _MARKUP_FLATTEN_RE.sub("", "\n".join(kept).lower())
    return _WHITESPACE_RE.sub(" ", flattened)


def has_agents_md_delegation_contract(repo_root: Path) -> bool:
    """Rung 1: does `<repo-root>/AGENTS.md` carry the standing delegation block?"""

    text = _RECORD.read_text(Path(repo_root) / "AGENTS.md")
    if text is None:
        return False
    normalized = normalize_contract_text(text)
    return all(marker in normalized for marker in DELEGATION_CONTRACT_MARKERS)


_DECLINE_ACTION = (
    "record `blocked delegation-declined — delegation signal: the user declined the standing "
    f"bounded-review delegation request, recorded in {RECORD_RELPATH}` and do not re-ask. "
    "This is a user decision, NOT a host incapacity; do not report it as one, and do not "
    "substitute a same-agent pass."
)
_ASK_ACTION_TAIL = (
    "then persist the answer with `record --decision granted|declined --note \"<the question you asked>\"` "
    f"into {RECORD_RELPATH}"
)


def _rung_1_result() -> dict[str, object]:
    return {
        "delegation": GRANTED,
        "rung": 1,
        "source": "AGENTS.md",
        # Rung 1 never READ a scope list; the canonical set is what the shipped
        # template names, not a per-repo fact. `scopes_source` says so rather
        # than letting a constant pass as something the repo asserted.
        "scopes": list(CANONICAL_SCOPES),
        "scopes_source": "canonical default (rung 1 does not read a per-repo scope list)",
        # Rung 1's provenance is the `AGENTS.md` block itself. Echoing a rung-2
        # record's `recorded_by`/`note` here would attach provenance describing a
        # different rung to a payload whose source says `AGENTS.md`.
        "provenance": {"source": "AGENTS.md block (checked in by the repo owner)"},
        "reason": "AGENTS.md carries the standing `Subagent Delegation` contract",
        "next_action": "spawn the bounded reviewers this scope mandates",
    }


def _conflict_result(provenance: dict) -> dict[str, object]:
    # `setup` writes the rung-1 block, so this state is one the harness itself
    # manufactures: decline at rung 3, then run `setup`. Returning `granted`
    # here would erase the only "no" the user ever gave.
    return {
        "delegation": ASK,
        "rung": 3,
        "source": f"conflict: AGENTS.md vs {RECORD_RELPATH}",
        "scopes": list(CANONICAL_SCOPES),
        "scopes_source": "canonical default",
        "provenance": provenance,
        "reason": (
            f"AGENTS.md carries the standing contract but {RECORD_RELPATH} records `declined`; "
            "a recorded refusal is not overridden silently"
        ),
        "next_action": f"ask the user once which source is current, naming both, and {_ASK_ACTION_TAIL}",
    }


def _rung_2_result(record_data: dict) -> dict[str, object]:
    decision = record_data["decision"]
    scopes = record_data["scopes"]
    return {
        "delegation": decision,
        "rung": 2,
        "source": RECORD_RELPATH,
        "scopes": scopes or list(CANONICAL_SCOPES),
        "scopes_source": "record" if scopes else "canonical default (record names no scopes)",
        "provenance": record_data["provenance"],
        "reason": record_data["reason"],
        "next_action": (
            "spawn the bounded reviewers this scope mandates" if decision == GRANTED else _DECLINE_ACTION
        ),
    }


def _rung_3_result(record_data: dict) -> dict[str, object]:
    return {
        "delegation": ASK,
        "rung": 3,
        "source": None,
        "scopes": list(CANONICAL_SCOPES),
        "scopes_source": "canonical default",
        "provenance": {},
        "reason": f"no delegation grant found: AGENTS.md contract absent; {record_data['reason']}",
        "next_action": (
            "ask the user once, naming the bounded reviewer scopes above and their token cost, "
            f"{_ASK_ACTION_TAIL}"
        ),
    }


def _apply_scope(result: dict[str, object], scope: str) -> None:
    result["requested_scope"] = scope
    covered = scope.strip().lower() in [s.lower() for s in result["scopes"]]
    result["scope_covered"] = covered
    if result["rung"] == 1:
        # Honest limitation, stated rather than implied: rung 1 reads prose, not a
        # scope list, so `scopes` here is the shipped template's canonical set and
        # this check cannot narrow a repo that hand-narrowed its own block. Saying
        # so beats a `scope_covered: true` that reads like a per-repo answer.
        result["scope_check"] = (
            "not enforceable at rung 1: the `AGENTS.md` block is prose, so a repo that narrowed "
            "it by hand is not detected here; record a scoped grant at rung 2 to make it enforceable"
        )
    if result["delegation"] == GRANTED and not covered:
        # A grant narrowed to `critique` must not read as `granted` to a
        # `release` caller. The top-level verdict is what callers branch on.
        result["delegation"] = ASK
        result["reason"] = (
            f"the recorded grant covers {result['scopes']} and does not name `{scope}`; "
            "ask before spawning for this scope"
        )
        result["next_action"] = f"ask the user whether the grant extends to `{scope}`, {_ASK_ACTION_TAIL}"


def resolve(repo_root: Path, *, scope: str | None = None) -> dict[str, object]:
    """Walk the ladder. Rung 2 is always read, so a decline can never be erased."""

    repo_root = Path(repo_root)
    rung1 = has_agents_md_delegation_contract(repo_root)
    record_data = read_delegation_record(repo_root)
    decision = record_data["decision"]

    if rung1 and decision == DECLINED:
        result = _conflict_result(record_data["provenance"])
    elif rung1:
        result = _rung_1_result()
    elif decision is not None:
        result = _rung_2_result(record_data)
    else:
        result = _rung_3_result(record_data)

    result["repo_root"] = str(repo_root.resolve())
    if scope is not None:
        _apply_scope(result, scope)
    if result["delegation"] == GRANTED and result["rung"] == 2 and not result["provenance"].get("note"):
        result["provenance_warning"] = (
            f"{RECORD_RELPATH} grants with no `note`; the record is repo-owned testimony, not proof "
            "of who answered — confirm it with the repo owner if the grant is load-bearing"
        )
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    resolve_parser = sub.add_parser("resolve", help="Resolve the delegation ladder for a repo.")
    resolve_parser.add_argument("--repo-root", default=".", help="Repo root to resolve (default: cwd).")
    resolve_parser.add_argument(
        "--scope",
        default=None,
        help="Bounded reviewer scope being requested; a grant that does not cover it resolves to ask.",
    )

    record_parser = sub.add_parser("record", help="Persist a rung-3 answer into the structured record.")
    record_parser.add_argument("--repo-root", default=".", help="Repo root to write into (default: cwd).")
    record_parser.add_argument(
        "--decision",
        required=True,
        choices=list(RECORDABLE_DECISIONS),
        help="The user's answer. `declined` is recorded so it is honoured and not re-asked.",
    )
    record_parser.add_argument(
        "--scope",
        action="append",
        default=None,
        dest="scopes",
        help="Bounded reviewer scope this answer covers (repeatable; defaults to the canonical set).",
    )
    record_parser.add_argument("--recorded-on", default=None, help="ISO date the user answered.")
    record_parser.add_argument(
        "--note",
        default=None,
        help="Provenance for the answer; required for `granted` (record the question that was asked).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    repo_root = Path(args.repo_root)
    try:
        if args.command == "resolve":
            payload = resolve(repo_root, scope=args.scope)
        else:
            payload = record(
                repo_root,
                decision=args.decision,
                scopes=list(args.scopes or []),
                recorded_on=args.recorded_on,
                note=args.note,
            )
    except DelegationError as exc:
        print(render_yaml({"error": str(exc), "recorded": False}), end="", file=sys.stderr)
        return 2
    except RecordWriteError as exc:
        print(
            render_yaml(
                {
                    "error": str(exc),
                    "recorded": False,
                    "next_action": "the answer was NOT persisted; do not treat the question as asked",
                }
            ),
            end="",
            file=sys.stderr,
        )
        return 3
    emit_yaml(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
