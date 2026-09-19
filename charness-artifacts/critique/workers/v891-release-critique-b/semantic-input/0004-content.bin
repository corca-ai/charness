"""Goal Binding freeze CLI: hash one Goal Draft and atomically freeze its binding.

The lifecycle surface stays in ``goal_binding.py`` (construction, freeze, and
readback). This front-end owns only the operator ergonomics the binding API
cannot: reading the draft hash from the file once, accepting planner-ordered
manifests, and deriving the deterministic binding sibling. Imported lazily by
``goal_binding.py`` so the library keeps no CLI cost.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from goal_binding import (  # noqa: E402
    BindingError,
    binding_path_for_draft,
    build_binding,
    sha256_file,
    write_immutable_binding,
)


def load_manifest_file(path: Path) -> list[dict[str, Any]]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BindingError("input-missing", f"manifest file not found: {path}: {exc}") from exc
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BindingError("input-invalid", f"manifest file is not valid JSON: {exc}") from exc
    if isinstance(value, dict) and isinstance(value.get("approved_work_items"), list):
        return value["approved_work_items"]
    if isinstance(value, list):
        return value
    raise BindingError(
        "schema-invalid",
        "manifest file must be a JSON list or an object with approved_work_items",
    )


def parent_identity(repo: str, number: int) -> dict[str, Any]:
    return {
        "repo": repo,
        "number": number,
        "url": f"https://github.com/{repo}/issues/{number}",
    }


def emit_yaml(payload: dict[str, Any]) -> None:
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        helper = ancestor / "scripts" / "yaml_output.py"
        if helper.is_file():
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "charness_goal_binding_freeze_yaml_output", helper
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.emit_yaml(payload)
            return
    raise RuntimeError("scripts/yaml_output.py not found above goal_binding_freeze.py")


def build_freeze_parser() -> Any:
    import argparse

    parser = argparse.ArgumentParser(
        description="Freeze a Goal Draft and create its immutable Goal Binding."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    freeze = subparsers.add_parser(
        "freeze",
        help="Hash the draft, canonicalize the manifest, and atomically freeze the binding.",
    )
    freeze.add_argument("--repo-root", type=Path, default=Path.cwd())
    freeze.add_argument(
        "--draft",
        required=True,
        help="Repository-relative Goal Draft path ending in .md",
    )
    freeze.add_argument("--parent-repo", required=True, help="Parent owner/repository slug")
    freeze.add_argument("--parent-number", required=True, type=int, help="Parent issue number")
    freeze.add_argument("--briefing-sha256", required=True)
    freeze.add_argument("--approval-response", required=True)
    freeze.add_argument("--approval-session-id", required=True)
    freeze.add_argument("--approval-observed-at", required=True)
    freeze.add_argument(
        "--manifest",
        required=True,
        type=Path,
        help="JSON list of work items, or an object with approved_work_items",
    )
    freeze.add_argument(
        "--binding-path",
        type=Path,
        default=None,
        help="Binding path (default: the draft's deterministic .binding.json sibling)",
    )
    return parser


def run_freeze(args: Any) -> dict[str, Any]:
    repo_root = args.repo_root.expanduser().resolve()
    draft_arg = args.draft
    try:
        draft_sha = sha256_file(repo_root / draft_arg)
    except BindingError as exc:
        raise BindingError("draft-missing", str(exc)) from exc
    items = load_manifest_file(args.manifest.expanduser())
    parent = parent_identity(args.parent_repo, args.parent_number)
    payload = build_binding(
        draft_path=draft_arg,
        draft_sha256=draft_sha,
        briefing_sha256=args.briefing_sha256,
        approval_response=args.approval_response,
        approval_session_id=args.approval_session_id,
        approval_observed_at=args.approval_observed_at,
        parent=parent,
        approved_work_items=items,
    )
    target = args.binding_path or binding_path_for_draft(payload["draft"]["path"])
    digest = write_immutable_binding(
        Path(target),
        payload,
        repo_root=repo_root,
        expected_parent=parent,
        expected_draft_path=payload["draft"]["path"],
        expected_draft_sha256=draft_sha,
    )
    return {
        "ok": True,
        "kind": "charness.goal-binding-freeze/v1",
        "binding_path": binding_path_for_draft(payload["draft"]["path"]).as_posix(),
        "binding_sha256": digest,
        "draft_path": payload["draft"]["path"],
        "draft_sha256": draft_sha,
        "approved_work_item_count": len(payload["approved_work_items"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_freeze_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "freeze":
            emit_yaml(run_freeze(args))
            return 0
    except BindingError as exc:
        emit_yaml(
            {
                "ok": False,
                "kind": "charness.goal-binding-freeze/v1",
                "status": exc.code,
                "error_code": exc.code,
                "error": str(exc),
            }
        )
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
