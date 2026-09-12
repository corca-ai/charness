"""Select an identity-bound follow-up path set from a prior packet."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def _content_index(identity: dict[str, Any]) -> dict[str, tuple[object, object]]:
    entries = identity.get("reviewed_content")
    if not isinstance(entries, list):
        return {}
    return {
        item["path"]: (item.get("content_sha256"), item.get("disposition"))
        for item in entries
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }


def select_paths(
    *,
    repo_root: Path,
    identity: dict[str, Any],
    prior_paths: list[str],
    explicit_paths: list[str] | None,
    prior_mode: str | None,
    current_mode: str,
    changed_ref: str | None,
    build_identity: Callable[..., dict[str, Any]],
    prior_binding: dict[str, Any],
    error: Callable[..., Exception],
) -> tuple[list[str], str, dict[str, Any] | None, dict[str, Any]]:
    """Return paths, selection label, comparison, and a selection receipt."""
    comparison: dict[str, Any] | None = None
    receipt: dict[str, Any] = {
        "prior_binding": prior_binding,
        "explicit_paths": bool(explicit_paths),
    }
    if explicit_paths:
        paths = sorted(set(explicit_paths))
        selection = "explicit-with-selection-receipt"
        comparable = prior_mode == current_mode and prior_paths and isinstance(
            identity.get("reviewed_content"), list
        )
        if comparable:
            prior_ref = identity.get("changed_ref") or identity.get("resolved_changed_ref")
            if current_mode == "committed-ref" and changed_ref != prior_ref:
                receipt["rationale"] = (
                    "Explicit paths were supplied because the committed review ref differs "
                    "from the prior ref; selection is not approval."
                )
                comparison = {
                    "prior_paths": len(prior_paths),
                    "changed_prior_paths": [],
                    "selected_changed_prior_paths": [],
                    "new_paths": sorted(set(paths) - set(prior_paths)),
                    "unchanged_selected_paths": [],
                    "omitted_changed_prior_paths": [],
                    "comparison_ref": {"prior": prior_ref, "current": changed_ref},
                }
            else:
                try:
                    current = build_identity(
                        repo_root=repo_root,
                        reviewed_paths=prior_paths,
                        changed_ref=changed_ref,
                        substrate_mode=current_mode,
                    )
                except (KeyError, TypeError, ValueError) as exc:
                    raise error("follow-up-delta-unavailable", str(exc)) from exc
                if current.get("status") != "captured":
                    raise error(
                        "follow-up-delta-unavailable",
                        "current review identity could not be captured for explicit selection",
                        details={"identity": current},
                    )
                before = _content_index(identity)
                after = _content_index(current)
                changed_prior = sorted(
                    path for path in prior_paths if before.get(path) != after.get(path)
                )
                selected = set(paths)
                prior = set(prior_paths)
                new_paths = sorted(selected - prior)
                unchanged = sorted(path for path in selected & prior if path not in changed_prior)
                omitted = sorted(set(changed_prior) - selected)
                comparison = {
                    "prior_paths": len(prior_paths),
                    "changed_prior_paths": changed_prior,
                    "selected_changed_prior_paths": sorted(set(changed_prior) & selected),
                    "new_paths": new_paths,
                    "unchanged_selected_paths": unchanged,
                    "omitted_changed_prior_paths": omitted,
                    "comparison_identity_sha256": current.get("identity_sha256"),
                    "comparison_identity_paths": sorted(prior),
                }
                receipt.update(
                    {
                        "prior_identity_sha256": identity.get("identity_sha256"),
                        "comparison_identity_sha256": current.get("identity_sha256"),
                        "comparison_identity_paths": sorted(prior),
                        "selected_changed_prior_paths": sorted(set(changed_prior) & selected),
                        "new_paths": new_paths,
                        "unchanged_selected_paths": unchanged,
                        "omitted_changed_prior_paths": omitted,
                        "rationale": (
                            "Explicit paths were supplied to include newly introduced consumers "
                            "or intentionally widen the stimulus; selection is not approval."
                        ),
                    }
                )
        elif prior_mode not in {None, current_mode}:
            raise error(
                "follow-up-substrate-mismatch",
                "explicit follow-up paths cannot silently compare different review substrates",
                details={"prior_substrate_mode": prior_mode, "current_substrate_mode": current_mode},
            )
        else:
            receipt["rationale"] = (
                "Explicit paths were supplied because the prior packet does not expose a "
                "comparable working-tree path identity; selection is not approval."
            )
        return paths, selection, comparison, receipt

    if prior_mode != current_mode:
        raise error(
            "follow-up-paths-required",
            "a follow-up cannot derive a delta from a different review substrate; provide --reviewed-path",
            details={
                "prior_substrate_mode": prior_mode,
                "current_substrate_mode": current_mode,
                "prior_paths": prior_paths,
            },
        )
    if not prior_paths or not isinstance(identity.get("reviewed_content"), list):
        raise error(
            "follow-up-paths-required",
            "prior review has no reconstructable reviewed paths; provide --reviewed-path",
        )
    if current_mode == "committed-ref":
        prior_ref = identity.get("changed_ref") or identity.get("resolved_changed_ref")
        if changed_ref != prior_ref:
            raise error(
                "follow-up-ref-mismatch",
                "implicit committed-ref follow-up requires the same pinned ref",
                details={"prior_ref": prior_ref, "current_ref": changed_ref},
            )
    try:
        current = build_identity(
            repo_root=repo_root,
            reviewed_paths=prior_paths,
            changed_ref=changed_ref,
            substrate_mode=current_mode,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise error("follow-up-delta-unavailable", str(exc)) from exc
    if current.get("status") != "captured":
        raise error(
            "follow-up-delta-unavailable",
            "current working-tree identity could not be captured; provide explicit paths",
            details={"identity": current},
        )
    before = _content_index(identity)
    after = _content_index(current)
    paths = sorted(path for path in prior_paths if before.get(path) != after.get(path))
    comparison = {
        "prior_paths": len(prior_paths),
        "changed_paths": len(paths),
        "comparison_identity_sha256": current.get("identity_sha256"),
        "comparison_identity_paths": sorted(prior_paths),
    }
    receipt.update(
        {
            "prior_identity_sha256": identity.get("identity_sha256"),
            "comparison_identity_sha256": current.get("identity_sha256"),
            "comparison_identity_paths": sorted(prior_paths),
            "selected_changed_prior_paths": paths,
            "new_paths": [],
            "unchanged_selected_paths": [],
            "omitted_changed_prior_paths": [],
        }
    )
    if not paths:
        raise error(
            "follow-up-no-delta",
            "no previously reviewed input changed; provide --reviewed-path for a new stimulus",
            details=comparison,
        )
    return paths, "changed-prior-inputs", comparison, receipt
