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

See ``references/chunked-routing.md`` for the contract (in the charness source
repo the full implementation contract is ``docs/handoff-chunked-routing.md``,
which is not vendored with the skill). Importantly,
this script must NOT modify any file under ``skills/public/achieve/``;
it only imports the achieve goal-artifact library to share the gate
contract.
"""
import argparse
import importlib.util
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
chunked_routing_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "chunked_routing_lib")
chunked_routing_cli = SKILL_RUNTIME.load_local_skill_module(__file__, "chunked_routing_cli")


def _load_goal_artifact_lib():
    """Import the achieve goal-artifact library without modifying it.

    Supports both source-tree ``skills/public/achieve`` and installed plugin
    ``skills/achieve`` layouts. Importing is allowed by the slice-5
    Standalone-Usefulness Invariant (the gate is on mutation, not read/import).
    """
    here = Path(__file__).resolve()
    package_root, installed_first = _package_root(here)
    rels = (
        Path("skills/achieve/scripts/goal_artifact_lib.py"),
        Path("skills/public/achieve/scripts/goal_artifact_lib.py"),
    )
    if not installed_first:
        rels = tuple(reversed(rels))
    for rel in rels:
        candidate = package_root / rel
        if not candidate.is_file():
            continue
        spec = importlib.util.spec_from_file_location(
            "achieve_goal_artifact_lib", candidate
        )
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise ImportError(
        "achieve goal_artifact_lib.py not found in source-tree "
        "skills/public/achieve/scripts or installed skills/achieve/scripts layout"
    )


def _package_root(script_path: Path) -> tuple[Path, bool]:
    parts = script_path.parts
    for index in range(len(parts) - 3):
        if parts[index:index + 4] == ("skills", "public", "handoff", "scripts"):
            return Path(*parts[:index]), False
    for index in range(len(parts) - 2):
        if parts[index:index + 3] == ("skills", "handoff", "scripts"):
            return Path(*parts[:index]), True
    raise ImportError(f"cannot resolve handoff package root for {script_path}")


GOAL_LIB = _load_goal_artifact_lib()


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
    chunked_routing_cli.add_input_argument(
        parser,
        legacy=("--chunk",),
        help_text="A single ChunkCandidate JSON. `--chunk` is a kept alias.",
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
        chunk_payload = chunked_routing_cli.read_pipeline_json(
            args.input,
            stage="draft_goal_from_chunk",
            expects="a single ChunkCandidate JSON (ChunkCandidate.to_dict())",
        )
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
            # `activation` is the goal artifact's own activation line, NOT the
            # operator's immediate next move. The auto-draft is still UNSHAPED
            # (User Acceptance / Agent Verification Plan / Slice Plan are
            # placeholders), so surfacing `/goal` as the next action would tell
            # the operator to start the During run on an unshaped goal. The real
            # next move is to SHAPE the draft through the achieve Before-phase
            # first; `/goal` activates the run only afterward (#246).
            "activation": f"/goal @{goal_rel}",
            "shape_command": f"/achieve @{goal_rel}",
            "next_step": (
                f"Shape first: run `/achieve @{goal_rel}` so the achieve "
                f"Before-phase fills User Acceptance / Agent Verification Plan "
                f"/ Slice Plan. The draft stays inert until you then run "
                f"`/goal @{goal_rel}` to activate the run."
            ),
        }
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
