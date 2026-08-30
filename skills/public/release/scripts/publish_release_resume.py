"""Resume a partially-completed `publish_release` run.

When the pre-push gate flakes after the local `Release ...` commit is made but
before the push lands, the original run leaves a partial state: a local commit,
an optional local tag, nothing on the remote, and no GitHub release. Re-running the normal flow is
not idempotent (`git commit` hits "nothing to commit", `git tag` hits "tag
exists"). `--resume` detects that exact partial state, RE-VALIDATES the pre-push
gates (it must not blindly push a stale local commit), then continues with
push -> create-release -> verify -> finalize, skipping the commit/tag it already
has and skipping a release that already exists.

The resume flow reuses the CLI module's already-bound helpers (passed in as
``cli``) so there is no second copy of the publish tail to drift.
"""

from __future__ import annotations

import importlib.util
import runpy
import sys
from pathlib import Path
from typing import Any


def _load_release_common():
    module_path = Path(__file__).resolve().with_name("publish_release_common.py")
    spec = importlib.util.spec_from_file_location("publish_release_common_for_resume", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_common = _load_release_common()


def _load_resume_closeout():
    module_path = Path(__file__).resolve().with_name("publish_release_resume_closeout.py")
    spec = importlib.util.spec_from_file_location("publish_release_resume_closeout", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_resume_closeout = _load_resume_closeout()
_claims_review = runpy.run_path(
    str(Path(__file__).resolve().with_name("publish_release_claims_review.py"))
)
_resume_publish = runpy.run_path(
    str(Path(__file__).resolve().with_name("publish_release_resume_publish.py"))
)
_resume_state = runpy.run_path(
    str(Path(__file__).resolve().with_name("publish_release_resume_state.py"))
)
_helpers = runpy.run_path(str(Path(__file__).resolve().with_name("publish_release_helpers.py")))

# Re-exported: `resumable_state` is the resume surface's public entry point and several
# callers and tests reach it through this module. The classification lives next door;
# this name stays here so the split did not become a caller migration.
resumable_state = _resume_state["resumable_state"]


def _artifact_commit_candidates(record_path: str) -> list[str]:
    """Compatibility entry point for the shared adapter-derived path contract."""
    return _resume_state["artifact_commit_candidates"](record_path)


def _commit_artifact_before_push(
    repo_root: Path, *, cli: Any, tag_name: str, record_path: str
) -> None:
    # B1: the resume refresh of the release record (and any retro-trigger artifact) must be
    # committed BEFORE the push, mirroring the normal flow's release commit. Otherwise the
    # artifact tree is dirty at push time and a pre-push hook's `git diff --quiet` blocks
    # with a false "mutated during a read-only quality run" attribution. Guarded on a real
    # change so an unchanged refresh stays idempotent ("nothing to commit").
    #
    # Each candidate is statused SEPARATELY and only the ones that matched are added.
    # `git status` tolerates a pathspec matching nothing; `git add` does NOT -- it exits 128
    # with `fatal: pathspec ... did not match any files` (verified) and `cli.run` is
    # check=True, so passing both a present and an absent pathspec kills the resume mid-lane
    # in exactly the consumer this threading exists for: one with no `charness-artifacts`.
    dirty = [
        candidate
        for candidate in _artifact_commit_candidates(record_path)
        if cli.run(["git", "status", "--porcelain", "--", candidate], cwd=repo_root).stdout.strip()
    ]
    if not dirty:
        return
    cli.run(["git", "add", "--", *dirty], cwd=repo_root)
    cli.run(
        ["git", "commit", "-m", f"chore(release): commit {tag_name} artifact before resume push"],
        cwd=repo_root,
    )


def _assert_post_publication_resumable(state: dict[str, Any], *, tag_name: str) -> bool:
    post_publication_phases = {
        "post-publication-carrier",
        "post-publication-final",
        "post-publication-claims-carrier",
        "post-publication-claims-final",
    }
    if state["phase"] not in post_publication_phases:
        return False
    if not (state["tag_local"] and state["tag_remote"] and state["release_exists"]):
        raise SystemExit(
            f"--resume: `{tag_name}` carrier HEAD lacks confirmed tag/release publication state."
        )
    claims_evidence = state.get("claims_evidence_commit", "")
    expected_parent = (
        claims_evidence
        if state["phase"] == "post-publication-claims-carrier"
        else state["tag_sha"]
        if state["phase"] == "post-publication-carrier"
        else state["parent_sha"]
    )
    if state["phase"] == "post-publication-carrier":
        valid, message = (
            state["head_parent_is_tag"],
            "carrier HEAD is not directly based on its release tag.",
        )
    elif state["phase"] == "post-publication-final":
        valid, message = (
            state["head_grandparent_is_tag"],
            "final closeout HEAD is not based on its carrier and release tag.",
        )
    elif state["phase"] == "post-publication-claims-carrier":
        valid, message = (
            state["parent_sha"] == claims_evidence,
            "claims carrier is not directly based on its claims evidence.",
        )
    else:
        valid, message = (
            state["grandparent_sha"] == claims_evidence,
            "claims final HEAD is not based on its carrier and evidence.",
        )
    if not valid:
        raise SystemExit(f"--resume: `{tag_name}` {message}")
    if state["remote_branch_sha"] not in {expected_parent, state["head_sha"]}:
        raise SystemExit(
            "--resume: remote branch is neither the release-content nor local carrier commit; "
            "refusing ambiguous closeout recovery."
        )
    return True


def assert_resumable(state: dict[str, Any], *, tag_name: str) -> None:
    if state["tag_local"] and state["tag_remote"] and state["remote_tag_sha"] != state["tag_sha"]:
        raise SystemExit(
            f"--resume: remote tag `{tag_name}` does not resolve to the local release commit; "
            "refusing ambiguous recovery."
        )
    if _assert_post_publication_resumable(state, tag_name=tag_name):
        return
    if state["phase"] == "prepared-claims-review":
        prepared = state.get("prepared")
        if not isinstance(prepared, dict):
            raise SystemExit("--resume: marked prepared state lacks its release-record binding")
        if state["tag_local"] and state["tag_sha"] != prepared["commit"]:
            raise SystemExit(
                f"--resume: local tag `{tag_name}` does not point at the prepared release record"
            )
        if state["tag_remote"] and state["remote_tag_sha"] != prepared["commit"]:
            raise SystemExit(
                f"--resume: remote tag `{tag_name}` does not point at the prepared release record"
            )
        allowed_remote_heads = {
            state.get("prepared_parent_sha", ""),
            prepared["commit"],
            state.get("claims_evidence_commit", "") or state["head_sha"],
        }
        if (
            state["remote_branch_sha"]
            and state["remote_branch_sha"] not in allowed_remote_heads
            and not state.get("remote_is_prepared_base", False)
        ):
            raise SystemExit(
                "--resume: remote branch is not the prepared record, claims evidence, or their known base; "
                "refusing unrelated advancement before publication."
            )
        return
    if state.get("marker_at_head"):
        # The legacy marker-free lane never validates a claims review, so reaching it with
        # the prepared marker present publishes with none at all. The prepared branches
        # above all require `prepared_record`, which declines when the marker is INHERITED
        # rather than introduced -- a second prepare while one is outstanding, which is the
        # likeliest action at a stop. Refuse instead of falling through.
        published = state.get("tag_remote") and state.get("release_exists")
        recovery = (
            # Already published: the tag is on the remote and the release exists, so the
            # "reset to one prepared record" advice would rewrite history behind a
            # published tag and discard the committed claims record.
            "The tag is already pushed and its release exists, so this is a publication "
            "whose closeout did not finish -- do NOT reset past the claims record. Drop only "
            "the post-push artifact commit (`git reset --hard <claims-evidence-commit>`) and "
            "resume."
            if published
            else "This is the state a second prepare over an outstanding marker produces; "
            "reset to one prepared record before resuming rather than publishing through the "
            "marker-free lane."
        )
        raise SystemExit(
            "--resume: HEAD's release record carries "
            "`charness-release-state:prepared-awaiting-claims-review`, but no single-parent "
            "prepared boundary could be identified, so the claims-review floor cannot run. "
            + recovery
        )
    if not state["head_is_release_commit"]:
        raise SystemExit(
            f"--resume: HEAD is not the `{tag_name}` release commit; nothing to resume. "
            "Resume only continues a publish whose local release commit already exists."
        )
    if not state["tag_local"]:
        if state["tag_remote"] or state["release_exists"]:
            raise SystemExit(
                f"--resume: local tag `{tag_name}` is missing while remote publication state exists; "
                "refusing to reconstruct an ambiguous tag."
            )
    elif not state["tag_points_at_head"]:
        raise SystemExit(
            f"--resume: tag `{tag_name}` does not point at HEAD; refusing to resume an inconsistent state."
        )
    if state["tag_remote"] and state["release_exists"]:
        raise SystemExit(
            f"--resume: tag `{tag_name}` is already on the remote and its GitHub release exists; "
            "the publish is already complete (nothing to resume)."
        )


def preflight_resume_state(
    repo_root: Path,
    *,
    args: Any,
    adapter_data: dict[str, Any],
    cli: Any,
) -> dict[str, Any]:
    record_path = _claims_review["release_record_path"](adapter_data)
    current_version = cli.build_release_payload(repo_root)["surface_versions"]["packaging_manifest"]
    if not isinstance(current_version, str):
        raise SystemExit("current_release did not report a packaging manifest version")
    # Before `resumable_state`, which spends a `git ls-remote` and a `gh release view` on the
    # way to classifying a state this refusal invalidates anyway, and before `assert_resumable`,
    # because the states this catches otherwise reach it looking ORDINARY: an unreadable path
    # yields no marker, so the phase resolves to `release-content` and a HEAD that really is
    # the release commit passes -- publication proceeds with the claims floor never invoked.
    _claims_review["assert_record_readable"](
        repo_root, record_path=record_path, commit="HEAD", run=cli.run
    )
    # The publication tail owns the irreversible-boundary check: after claims review and
    # before push/create it re-reads the target surface and binds the disposition into the
    # release artifact. Keep this classifier preflight focused on record readability so a
    # missing record cannot be mistaken for an ordinary release-content state; the tail's
    # check is the one that catches a surface changed between prepare and resume.
    tag_name = f"v{current_version}"
    state = resumable_state(
        repo_root,
        tag_name=tag_name,
        commit_message=f"Release {adapter_data['package_id']} {current_version}",
        remote=args.remote,
        branch=_resume_state["git_out"](cli, repo_root, ["rev-parse", "--abbrev-ref", "HEAD"]),
        backend=adapter_data["release_backend"],
        record_path=record_path,
        cli=cli,
    )
    assert_resumable(state, tag_name=tag_name)
    _claims_review["assert_claims_artifact_is_read"](state["phase"], args.claims_review_artifact)
    if state["phase"] in _claims_review["CLAIMS_PHASES"]:
        state["claims_review"] = _claims_review["validate_claims_review"](
            repo_root,
            prepared=state["prepared"],
            evidence_commit=state.get("claims_evidence_commit") or state["head_sha"],
            artifact_path=args.claims_review_artifact,
            target_version=current_version,
            tag_name=tag_name,
            run=cli.run,
            # Resolved through the CANONICAL owner rather than re-derived: it
            # filters to the release-tag glob and consults the remote, which a
            # local `git describe` cannot. The scope-completeness check falls
            # back to a `--match`ed describe when this returns None.
            previous_version=_helpers["latest_previous_release_version"](
                repo_root,
                target_version=current_version,
                remote=args.remote,
            ),
        )
        _claims_review["unproven_claims_warning"](state["claims_review"], write=sys.stderr.write)
    return state


def resume_publish(
    repo_root: Path,
    *,
    args: Any,
    plan: dict[str, Any],
    adapter_data: dict[str, Any],
    cli: Any,
    state: dict[str, Any] | None = None,
) -> None:
    _resume_publish["resume_publish"](
        repo_root,
        args=args,
        plan=plan,
        adapter_data=adapter_data,
        cli=cli,
        state=state,
        resumable_state=resumable_state,
        assert_resumable=assert_resumable,
        common=_common,
        resume_closeout=_resume_closeout,
        commit_artifact_before_push=_commit_artifact_before_push,
        release_record_path=_claims_review["release_record_path"],
    )
