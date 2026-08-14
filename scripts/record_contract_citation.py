#!/usr/bin/env python3
"""Append one declared contract-unit citation without editing projections."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script, require_repo_local_helper
from yaml_output import emit_yaml

ROOT = repo_root_from_script(__file__)
_register = import_repo_module(__file__, "scripts.contract_register_lib")
_writer = import_repo_module(__file__, "scripts.lesson_ledger_writer_lib")


def append_citation(
    *, repo_root: Path, event_id: str, source_retro: str, unit_id: str, anchor: str
) -> dict[str, Any]:
    require_repo_local_helper(__file__, repo_root)
    event = {
        "event_id": event_id.strip(),
        "source_retro": source_retro.strip(),
        "unit_id": unit_id.strip(),
        "anchor": anchor.strip(),
    }
    if not all(event.values()):
        raise ValueError("record contract citation: every field must be non-empty")
    output_dir = repo_root / "charness-artifacts/retro"
    path = _register.contract_register_path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(f"missing contract register `{path.relative_to(repo_root)}`")
    with _writer.ledger_lock(path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        _register.replay_validated_contract_register_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=output_dir / "recent-lessons.md",
            path=path,
            payload=payload,
        )
        candidate = copy.deepcopy(payload)
        candidate["citation_events"].append(event)
        _register.replay_validated_contract_register_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=output_dir / "recent-lessons.md",
            path=path,
            payload=candidate,
        )
        _writer.replace_payload(path, candidate)
    return event


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--event-id", required=True)
    parser.add_argument("--source-retro", required=True)
    parser.add_argument("--unit-id", required=True)
    parser.add_argument("--anchor", required=True)
    args = parser.parse_args(argv)
    # Receipt only. The appended event itself is persisted as JSON inside the
    # contract register by `append_citation` above; this is the stdout echo.
    emit_yaml(
        append_citation(
            repo_root=args.repo_root.resolve(),
            event_id=args.event_id,
            source_retro=args.source_retro,
            unit_id=args.unit_id,
            anchor=args.anchor,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
