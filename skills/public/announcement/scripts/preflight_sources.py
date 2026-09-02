#!/usr/bin/env python3
from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


arm_cli_timeout = _load_skill_runtime_bootstrap().arm_cli_timeout


def _repo_root() -> Path:
    return next(parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "gates_support" / "announcement_preflight_lib.py").is_file())


def main() -> None:
    cancel_timeout = arm_cli_timeout(label="announcement preflight_sources")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root that owns the announcement adapter and draft artifact")
    parser.add_argument("--draft-path", type=Path, default=None, help="Override path to the announcement draft to preflight (defaults to the adapter artifact path)")
    try:
        args = parser.parse_args()
        repo_root = args.repo_root.resolve()
        sys.path.insert(0, str(_repo_root()))
        from scripts.adapter_version_verdict import unspeakable_version_message
        from scripts.announcement_adapter_lib import load_announcement_adapter
        from scripts.gates_support.announcement_preflight_lib import preflight_sources
        from scripts.yaml_output import emit_yaml

        # GUARDED AT THE READ SITE, and this is a PUBLISH-BOUNDARY gate: its whole job is
        # to block a delivery that would claim an in-progress source is finished.
        #
        # WHAT IT COSTS TO BE UNGUARDED, measured at `254fa5c44`: a repo declaring one
        # `in_progress_sources` entry got `delivery_blocked: false`, `ok: true`,
        # `surfaces: []`, exit 0 -- clear to announce. The same repo at a speakable version
        # gets `delivery_blocked: true`, `ok: false`, exit 2. The gate did not degrade; it
        # INVERTED, because `announcement_preflight_lib.preflight_sources` short-circuits
        # to ok/unblocked the moment `in_progress_sources` is empty, and an unhonored
        # declaration is indistinguishable there from a repo that declared none.
        refusal = unspeakable_version_message(
            load_announcement_adapter, repo_root, adapter_name="announcement-adapter.yaml"
        )
        if refusal is not None:
            raise SystemExit(refusal)
        adapter = load_announcement_adapter(repo_root)
        adapter_data = adapter["data"]
        # DECLARED-BUT-NOT-HONORED, which the version verdict cannot see. A bounded review
        # measured this: `_validate_in_progress_sources` uses `continue` on every rejected
        # entry, so ONE bad entry -- `kind: Path` with a capital P, or a `kind: path` with
        # no `path:` -- empties the list, and an empty list takes the short-circuit to
        # `ok: True, delivery_blocked: False` at exit 0. The gate that exists to stop a
        # premature announcement was cleared by one capital letter.
        #
        # `field_state` already carries the distinction between "unset" and "configured",
        # so this asks the payload rather than re-deriving: the repo WROTE the key and
        # nothing survived validation.
        # KEYED ON WHETHER A DECLARATION WAS LOST, not on whether the list ended up empty.
        # The first cut asked `not adapter_data["in_progress_sources"]`, and a round-2
        # bounded review found that closes the bypass only when EVERY entry dies: with two
        # entries, one `kind: Path` and one valid, the list is non-empty, the guard never
        # fires, and the preflight clears the delivery over a source the repo declared and
        # this reader dropped. Measured, exit 0.
        #
        # Every message `_validate_in_progress_sources` emits starts with
        # `in_progress_sources`, so the prefix is a complete witness for "an entry the repo
        # wrote did not survive". The emptiness test stays as the second arm because a
        # declaration can also be lost without an error -- a non-list value takes a
        # different path.
        source_errors = [
            str(error)
            for error in (adapter.get("errors") or [])
            if str(error).startswith("in_progress_sources")
        ]
        if source_errors or (
            adapter.get("field_state", {}).get("in_progress_sources") == "configured"
            and not adapter_data.get("in_progress_sources")
        ):
            raise SystemExit(
                "`.agents/announcement-adapter.yaml` declares `in_progress_sources` that "
                "this reader did not honor, so this preflight would judge the delivery "
                "against a source list the repo did not write. Refusing instead. Adapter "
                "errors: "
                + "; ".join(str(error) for error in (adapter.get("errors") or []))
            )
        if args.draft_path is not None:
            draft_path = args.draft_path.resolve()
        else:
            artifact_path = Path(adapter["artifact_path"])
            draft_path = artifact_path if artifact_path.is_absolute() else (repo_root / artifact_path)
        payload = preflight_sources(adapter_data, draft_path)
        emit_yaml(dict(sorted(payload.items())))
        sys.exit(0 if payload["ok"] else 2)
    finally:
        cancel_timeout()


if __name__ == "__main__":
    main()
