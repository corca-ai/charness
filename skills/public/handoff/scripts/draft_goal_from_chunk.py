#!/usr/bin/env python3
"""Write an auto-drafted goal artifact from a selected chunk candidate.

CLI surface:

    python3 draft_goal_from_chunk.py --chunk <path-to-chunk-json> --date YYYY-MM-DD
    python3 draft_goal_from_chunk.py --chunk - --date YYYY-MM-DD            # read stdin
    python3 draft_goal_from_chunk.py --chunk <path> --slug <override-slug>

The input is a single ChunkCandidate JSON (the shape from
``ChunkCandidate.to_dict()``). Writes to
``charness-artifacts/goals/<date>-<slug>.md`` at status ``draft`` and
then runs ``check_goal_artifact.check_goal`` against the result; an
artifact that fails the gate is removed and the failure is reported.

See ``docs/handoff-chunked-routing.md`` for the contract. Importantly,
this script must NOT modify any file under ``skills/public/achieve/``;
it only imports the achieve goal-artifact library to share the gate
contract.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
chunked_routing_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "chunked_routing_lib")


def _load_goal_artifact_lib():
    """Import the achieve goal-artifact library without modifying it.

    Walks up to find ``skills/public/achieve/scripts/goal_artifact_lib.py``.
    Importing is allowed by the slice-5 Standalone-Usefulness Invariant
    (the gate is on file mutation, not on read/import).
    """
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = (
            ancestor
            / "skills"
            / "public"
            / "achieve"
            / "scripts"
            / "goal_artifact_lib.py"
        )
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(
                "achieve_goal_artifact_lib", candidate
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError(
        "skills/public/achieve/scripts/goal_artifact_lib.py not found"
    )


GOAL_LIB = _load_goal_artifact_lib()


def _read_chunk_json(path_arg: str) -> dict:
    if path_arg == "-":
        return json.loads(sys.stdin.read())
    return json.loads(Path(path_arg).expanduser().resolve().read_text(encoding="utf-8"))


def _restore_chunk(payload: dict):
    def restore_entry(entry_dict):
        return chunked_routing_lib.HandoffEntry(
            index=int(entry_dict["index"]),
            title=entry_dict["title"],
            body=entry_dict["body"],
            referenced_paths=tuple(entry_dict.get("referenced_paths", [])),
            referenced_issues=tuple(entry_dict.get("referenced_issues", [])),
            referenced_skills=tuple(entry_dict.get("referenced_skills", [])),
            boundary_tokens=tuple(entry_dict.get("boundary_tokens", [])),
        )

    return chunked_routing_lib.ChunkCandidate(
        entries=tuple(restore_entry(entry) for entry in payload["entries"]),
        label=payload["label"],
        objective_summary=payload["objective_summary"],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--chunk",
        required=True,
        help="Path to a ChunkCandidate JSON, or `-` to read stdin.",
    )
    parser.add_argument(
        "--date",
        required=True,
        help="Goal date prefix YYYY-MM-DD used for the artifact filename.",
    )
    parser.add_argument(
        "--slug",
        help="Override the auto-derived goal slug. Optional.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repo root that owns charness-artifacts/goals/ (default: cwd).",
    )
    return parser.parse_args()


def main() -> int:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="handoff draft_goal_from_chunk")
    try:
        args = parse_args()
        repo_root = args.repo_root.expanduser().resolve()
        chunk_payload = _read_chunk_json(args.chunk)
        chunk = _restore_chunk(chunk_payload)
        slug = args.slug or chunked_routing_lib.auto_draft_slug(chunk)
        goal_path = GOAL_LIB.goal_path(repo_root, args.date, slug)
        goal_rel = GOAL_LIB.goal_rel(repo_root, goal_path)
        artifact_text = chunked_routing_lib.render_auto_draft_artifact(
            chunk, date=args.date, goal_rel=goal_rel
        )
        goal_path.parent.mkdir(parents=True, exist_ok=True)
        # Refuse to overwrite an existing artifact; the auto-draft writer
        # is for fresh drafts only.
        if goal_path.exists():
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": f"artifact already exists: {goal_rel}",
                    },
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
            return 1
        goal_path.write_text(artifact_text, encoding="utf-8")
        check = GOAL_LIB.check_goal(artifact_text)
        if not check["ok"]:
            # Roll back the bad artifact so a failure does not leave
            # half-written state on disk.
            goal_path.unlink(missing_ok=True)
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": "auto-drafted artifact failed check_goal_artifact",
                        "check_goal_issues": check["issues"],
                    },
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
            return 1
        payload = {
            "ok": True,
            "path": str(goal_path),
            "slug": slug,
            "status": check["status"],
            "activation": f"/goal @{goal_rel}",
        }
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
