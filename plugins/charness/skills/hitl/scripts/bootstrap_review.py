from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
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

_scripts_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
render_yaml_mapping = _scripts_adapter_lib_module.render_yaml_mapping
_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter


def apply_mode(require_explicit_apply: bool) -> str:
    return "explicit-after-all-chunks" if require_explicit_apply else "accepted-chunk-or-final-apply-boundary"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def portable_path(repo_root: Path, value: str) -> str:
    path = Path(value)
    if not path.is_absolute():
        return value
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return f"external-path:{path.name}"


def target_provenance(repo_root: Path, value: str) -> dict[str, str]:
    path = Path(value)
    if not path.is_absolute():
        return {"kind": "logical-or-repo-relative"}
    try:
        path.resolve().relative_to(repo_root)
    except ValueError:
        return {"kind": "external-path", "basename": path.name}
    return {"kind": "repo-root-relative"}


def full_target_review_item(portable_target: str, scope: str) -> dict[str, object]:
    return {
        "id": "full_target_review",
        "type": "full_target_review",
        "status": "pending_after_chunks",
        "target": portable_target,
        "scope": scope,
        "requires_whole_target_judgment": True,
        "activation_condition": "all_chunks_reviewed_and_target_edit_applied_or_staged",
        "decision_needed": "Review the full updated target before accepting the target as complete.",
    }


def applied_rewrite_review_policy() -> dict[str, object]:
    return {
        "id": "applied_rewrite_review",
        "type": "applied_rewrite_review_policy",
        "status": "inactive_until_reviewer_requested_rewrite_is_applied",
        "requires_applied_excerpt_before_cursor_advance": True,
        "anchor_preference": "line-or-hunk-anchor",
        "verification_role": "secondary",
        "decision_needed": "Decide whether the rewritten chunk is accepted or needs another revision.",
    }


def scratchpad_text(session_id: str, portable_target: str, base_ref: str, scope: str, mode: str) -> str:
    return f"""# HITL Scratchpad: {session_id}

- Updated: {utc_now()}
- Target: {portable_target}
- Base Ref: {base_ref}
- Scope: {scope}
- Apply Mode: {mode}

## Agreements

## Open Questions

## Pre-Edit Constraints
- Accepted Rules: []
- Active Rules Applied:
- Target/Cursor Checked: false; Target/Cursor Check Result:

## Applied Rewrite Review

- Status: inactive until a reviewer-requested rewrite is applied
- Decision Needed: Decide whether the rewritten chunk is accepted or needs another revision.
- Required Surface: applied chunk excerpt with line or hunk anchor when possible, surrounding context, and secondary verification results if available.
- Pending Chunk ID:
- Source Anchor:
- Applied Excerpt:
- Verification:
- Review Result:

## Full Target Review

- Status: pending after all chunks and apply/stage boundary
- Decision Needed: Review the full updated target before accepting the target as complete.
"""


def bootstrap_review(repo_root: Path, session_id: str, target: str, base_ref: str, scope: str) -> dict[str, object]:
    output_dir = repo_root / ".charness" / "hitl" / "runtime" / session_id
    output_dir.mkdir(parents=True, exist_ok=True)
    adapter = load_adapter(repo_root)
    require_explicit_apply = bool(adapter["data"].get("require_explicit_apply", True))
    mode = apply_mode(require_explicit_apply)
    portable_target = portable_path(repo_root, target)
    provenance = target_provenance(repo_root, target)
    full_target_review = full_target_review_item(portable_target, scope)
    applied_rewrite_review = applied_rewrite_review_policy()

    (output_dir / "hitl-scratchpad.md").write_text(
        scratchpad_text(session_id, portable_target, base_ref, scope, mode),
        encoding="utf-8",
    )
    (output_dir / "state.yaml").write_text(
        render_yaml_mapping(
            [
                ("session_id", session_id),
                ("status", "in_progress"),
                ("target", portable_target),
                ("base_ref", base_ref),
                ("scope", scope),
                ("require_explicit_apply", require_explicit_apply),
                ("apply_mode", mode),
                ("queue_epoch", 1),
                ("queue_status", "ready"),
                ("accepted_rules", []),
                ("active_rules_applied", []),
                ("target_cursor_checked", False),
                ("target_cursor_check_result", ""),
                ("intent_resync_required", False),
                ("last_presented_chunk_id", ""),
                ("last_intent_resync_at", ""),
                ("applied_rewrite_review_status", "inactive"),
                ("pending_rewrite_chunk_id", ""),
                ("pending_rewrite_source_anchor", ""),
                ("last_rewritten_chunk_id", ""),
                ("last_rewrite_review_result", ""),
                ("full_target_review_item_id", "full_target_review"),
                ("full_target_review_status", "pending_after_chunks"),
                ("full_target_review_result", ""),
            ]
        ),
        encoding="utf-8",
    )
    (output_dir / "rules.yaml").write_text("rules: []\n", encoding="utf-8")
    (output_dir / "fix-queue.yaml").write_text("items: []\n", encoding="utf-8")
    (output_dir / "queue.json").write_text(
        json.dumps(
            {
                "session_id": session_id,
                "target": portable_target,
                "target_provenance": provenance,
                "require_explicit_apply": require_explicit_apply,
                "apply_mode": mode,
                "priority_policy_version": 1,
                "queue_epoch": 1,
                "status": "ready",
                "current_queue_order": [],
                "reviewed_item_ids": [],
                "superseded_unreviewed_item_ids": [],
                "queue_recommendation": None,
                "applied_rewrite_review": applied_rewrite_review,
                "completion_item_ids": ["full_target_review"],
                "full_target_review": full_target_review,
                "items": [full_target_review],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "events.log").write_text(f"{utc_now()} bootstrap {portable_target}\n", encoding="utf-8")
    return {
        "session_dir": output_dir.relative_to(repo_root).as_posix(),
        "scratchpad": (output_dir / "hitl-scratchpad.md").relative_to(repo_root).as_posix(),
        "state_file": (output_dir / "state.yaml").relative_to(repo_root).as_posix(),
        "queue_file": (output_dir / "queue.json").relative_to(repo_root).as_posix(),
        "require_explicit_apply": require_explicit_apply,
        "apply_mode": mode,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root whose HITL review should be bootstrapped")
    parser.add_argument("--session-id", default=f"hitl-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}", help="HITL session identifier")
    parser.add_argument("--target", default="git-diff", help="Path to review, or 'git-diff' to diff against --base-ref")
    parser.add_argument("--base-ref", default="main", help="Base git ref to diff against")
    parser.add_argument("--scope", default="all", help="Review scope (all, code, or docs)")
    args = parser.parse_args()
    payload = bootstrap_review(args.repo_root.resolve(), args.session_id, args.target, args.base_ref, args.scope)
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
