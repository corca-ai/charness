#!/usr/bin/env python3
"""Shared corpus plumbing for the inventory-consumption measurement scripts.

Two scripts measure what a floor would cost this repo's checked-in quality artifacts:
`measure_inventory_consumption_floor.py` (the residual-character floor, sweep rows
S9/S10) and `measure_inventory_marker_rule.py` (the value-marker counterfactual,
[D47](../../charness-artifacts/spec/2026-09-04-deferred-decisions-archive.md)). They ask different questions of the same corpus,
so they share how the corpus is resolved, how an artifact is split into its
commands-run and body halves, and the class rule that an empty corpus is refused rather
than reported clean.

They deliberately do NOT share their scan bodies: what each counts is the whole point of
each script, and collapsing those would make one measurement's semantics depend on the
other's.
"""
from __future__ import annotations

import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.gates import validate_inventory_consumption as gate  # noqa: E402

DEFAULT_CORPUS = "charness-artifacts/quality"


def split_bodies(text: str) -> tuple[str, str]:
    """`(commands_run_section, everything_else)`.

    The split matters: a cited inventory is read from the commands-run section, while
    engagement is judged over the rest, so an artifact cannot satisfy a field floor by
    pasting the command line that names the field.
    """
    sections = gate._split_sections(text)
    commands = sections.get(gate.COMMANDS_RUN_HEADER, "")
    body = "\n".join(
        block for header, block in sections.items() if header != gate.COMMANDS_RUN_HEADER
    )
    return commands, body


def resolve_paths(args) -> tuple[Path, Path, Path]:
    """`(repo_root, corpus, consumer_fields_path)` from the shared CLI flags."""
    repo_root = args.repo_root.resolve()
    corpus = (args.corpus or (repo_root / DEFAULT_CORPUS)).resolve()
    fields_path = (
        args.consumer_fields_path or (repo_root / gate.DEFAULT_CONSUMER_FIELDS_PATH)
    ).resolve()
    return repo_root, corpus, fields_path


def corpus_paths(corpus: Path, *, recursive: bool = False) -> list[Path]:
    return sorted(corpus.rglob("*.md") if recursive else corpus.glob("*.md"))


def build_parser(description: str, *, recursive_flag: bool = False):
    """The measurement CLI both scripts expose: repo-root / corpus / fields."""
    import argparse

    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--corpus", type=Path, default=None, help=f"Default: {DEFAULT_CORPUS}")
    parser.add_argument("--consumer-fields-path", type=Path, default=None)
    if recursive_flag:
        parser.add_argument(
            "--recursive", action="store_true",
            help="Include nested directories such as charness-artifacts/quality/history/, "
                 "which the non-recursive default glob silently excludes.",
        )
    return parser


def cited_inventories(commands: str, inventories: dict):
    """Yield `(inventory_name, declared_fields)` for each declared inventory cited in the
    commands-run section. An inventory with no declared fields is skipped: it opted out."""
    for inventory in sorted(set(gate.INVENTORY_FILE_RE.findall(commands))):
        fields = (inventories.get(inventory) or {}).get("non_headline_fields") or []
        if fields:
            yield inventory, tuple(fields)


def exemption_state(repo_root: Path, path: Path, text: str) -> str:
    """How the gate's pre-contract exemption would read this artifact.

    `corroborated` means the gate exits 0 without running any floor, so a measurement
    that counts it reports a cost on an artifact the gate never judges. The artifact's
    own `Date:` line is not enough -- it is corroborated against git, the channel the
    artifact does not author (sweep row S9).
    """
    declared = gate.ARTIFACT_DATE_RE.search(text)
    declared_date = declared.group(1) if declared else None
    if not declared_date or declared_date >= gate.ENFORCED_FROM_DATE.isoformat():
        return "not-claimed"
    state, committed = gate.commit_state(repo_root, path)
    if committed is None or state == "unavailable":
        return "not-corroborated"
    return "corroborated" if committed < gate.ENFORCED_FROM_DATE else "REFUSED-uncorroborated"


def iter_citations(paths, inventories: dict, repo_root: Path):
    """Yield `(display_path, body, inventory_name, declared_fields, exemption_state)`.

    The traversal both measurements share; what each then COUNTS over `body` is the
    question each script exists to answer, and stays in the script.
    """
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        commands, body = split_bodies(text)
        display = gate._display_path(path, repo_root)
        exemption = exemption_state(repo_root, path, text)
        for inventory, fields in cited_inventories(commands, inventories):
            yield display, body, inventory, fields, exemption


def refuse_empty_corpus(corpus: Path, *, recursive: bool = False) -> bool:
    """True when the caller must exit 2.

    A clean result over an empty corpus is not a measurement -- the class rule this repo
    applies to every measurement script, after one of them reported `corpus_established:
    false` and still exited 0.
    """
    if corpus.is_dir() and corpus_paths(corpus, recursive=recursive):
        return False
    print(
        f"no artifacts found under {corpus}; a clean result over an empty corpus is "
        "not a measurement.",
        file=sys.stderr,
    )
    return True
