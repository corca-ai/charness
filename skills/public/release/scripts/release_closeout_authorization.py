"""Release-side closeout authorization.

Its own module, not a spill companion: this is the single place the release lane asks
whether a target may be closed at all, and every release entrypoint that can reach a
temp message, a bump, a publish, a tag, or an issue close consults it.

The authorization LOGIC lives in the issue skill and is loaded, never reimplemented.
A release-local copy is exactly how the two lanes drift until the release path permits
what the issue path refuses — and the release path is the one with the bigger blast
radius, since it can close several issues while publishing.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def load_closeout_authorization():
    """Load the issue skill's authorization helper, or None if it is not installed.

    The package-root walk is reused from `release_issue_closeout`, which already owns
    it for the sibling body-check import; duplicating that walk here is how the two
    would eventually disagree about where the issue skill lives.

    None means `release` is vendored without `issue`. That is a legitimate install, so
    it degrades to permissive rather than refusing every release close — the teeth live
    in the consuming repo's crosswalk artifact, and a repo with no crosswalk has
    nothing to protect.
    """
    # The single owner of "where is the issue skill" moved to `release_closeout_floors`
    # when the closeout module crossed its length gate. Following it keeps the one-owner
    # property this docstring depends on; pointing at the old home would have left two
    # answers again, which is exactly what it warns about.
    sibling = Path(__file__).resolve().with_name("release_closeout_floors.py")
    spec = importlib.util.spec_from_file_location("release_closeout_package_root", sibling)
    if spec is None or spec.loader is None:
        return None
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    package_root, installed_first = owner._package_root(Path(__file__).resolve())
    rels = (
        "skills/issue/scripts/issue_closeout_authorization.py",
        "skills/public/issue/scripts/issue_closeout_authorization.py",
    )
    if not installed_first:
        rels = tuple(reversed(rels))
    for rel in rels:
        candidate = package_root / rel
        if not candidate.is_file():
            continue
        module_spec = importlib.util.spec_from_file_location("release_issue_closeout_authorization", candidate)
        if module_spec is None or module_spec.loader is None:
            continue
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return module
    return None


def refuse_unauthorized_release_close(
    repo_root: Path, *, repo: str | None, issue_numbers: list[int], carrier_source: str
) -> dict[str, Any]:
    """Refuse a release-carried close of a protected target BEFORE any mutation.

    Called from every release entrypoint that can reach an irreversible act, including
    the resume/recovery paths. Guarding only the primary publish path would leave
    recovery as an unwatched route to the same act — and recovery is exactly where a
    blocked operator goes next.

    Which targets are protected is the consuming repo's crosswalk decision, not this
    module's. Unrelated release closes are untouched.
    """
    module = load_closeout_authorization()
    if module is None or not issue_numbers:
        return {"authorized": True, "applies": False, "carrier_source": carrier_source}
    targets = [
        {"repository": repo, "issue_number": number, "source": f"release-cli:{carrier_source}"}
        for number in issue_numbers
    ]
    result = module.authorize(
        invoked_targets=targets, carrier_targets=[], carrier_source=carrier_source, repo_root=repo_root
    )
    if not result["authorized"]:
        raise SystemExit(module.refusal_message(result))
    return result
