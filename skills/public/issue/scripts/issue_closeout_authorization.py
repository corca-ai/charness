"""One way for every closeout carrier to reach `authorize_closeout()`.

Each ingress in this repo — commit-msg hook, `close-with-comment`, draft validation,
post-publication verify, the release paths — historically did its own target parsing.
This module exists so none of them does its own AUTHORIZING as well. Every caller
gets the same record from the same implementation, and none of them re-derives or
narrows it.

`enforce()` raises. That is deliberate: a refusal that a caller can accidentally
ignore by not reading a boolean is not a refusal, and these callers sit in front of
irreversible GitHub mutations.

ORDER is the other half of the contract and is NOT structurally enforced here. It is
not enough for a carrier to check authorization somewhere; the check has to happen
before the first side effect — before a temp file is written, before a comment is
posted, before a version is bumped. Each ingress places its own call, and what holds
that ordering in place is the test suite
(`tests/quality_gates/test_closeout_authorization_ingress.py`), which asserts that
zero backend calls, temp files, and bumps occurred on refusal. An earlier version of
this module claimed a wrapper made the ordering structural; nothing used it, so the
claim was false and it has been removed rather than left as reassurance.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Iterable

_CROSSWALK_CACHE: dict[str, Any] = {}

_QUALIFIED_DECLARATION_RE = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+#\d+$")

def _load_crosswalk_module():
    """Locate `scripts/evidence/evidence_boundary_crosswalk.py` from either layout.

    Root layout puts it at `<repo>/scripts/`; the exported plugin at
    `plugins/charness/scripts/`. Both sit beside a `runtime_bootstrap.py`, which the
    module imports by name, so that directory joins `sys.path` before the load.
    """
    if "module" in _CROSSWALK_CACHE:
        return _CROSSWALK_CACHE["module"]
    import importlib.util

    for ancestor in Path(__file__).resolve().parents:
        candidate = ancestor / "scripts" / "evidence" / "evidence_boundary_crosswalk.py"
        if not candidate.is_file():
            continue
        if str(ancestor) not in sys.path:
            sys.path.insert(0, str(ancestor))
        spec = importlib.util.spec_from_file_location("charness_evidence_boundary_crosswalk", candidate)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _CROSSWALK_CACHE["module"] = module
        return module
    _CROSSWALK_CACHE["module"] = None
    return None


def authorize(
    *,
    invoked_targets: Iterable[Any],
    carrier_targets: Iterable[Any],
    carrier_source: str,
    repo_root: Path,
) -> dict[str, Any]:
    """Return the authorization record, or a permissive one if the gate is absent.

    A missing crosswalk module means an installation without this surface. Refusing
    every close there would break unrelated issue work in every consumer repo, so the
    absence is REPORTED (`crosswalk_status`) rather than treated as a refusal. The
    protected-target teeth live in the crosswalk artifact, which this repo checks in.
    """
    module = _load_crosswalk_module()
    if module is None:
        return {
            "applies": False, "authorized": True, "refusal": None,
            "crosswalk_status": "authorization_module_unavailable",
            "carrier_source": carrier_source, "target": None,
        }
    return module.authorize_closeout(
        list(invoked_targets), list(carrier_targets), carrier_source, repo_root=Path(repo_root)
    )


def refusal_message(result: dict[str, Any]) -> str:
    protected = result.get("protected_issues") or []
    return "\n".join(
        [
            f"charness closeout authorization: REFUSED ({result['refusal']})",
            f"  carrier: {result.get('carrier_source')}",
            f"  detail: {result.get('detail')}",
            f"  protected issues: {protected}",
            "  This gate applies only to those issues; unrelated issue closes are unaffected.",
        ]
    )


def enforce(
    *,
    invoked_targets: Iterable[Any],
    carrier_targets: Iterable[Any],
    carrier_source: str,
    repo_root: Path,
) -> dict[str, Any]:
    result = authorize(
        invoked_targets=invoked_targets, carrier_targets=carrier_targets,
        carrier_source=carrier_source, repo_root=repo_root,
    )
    if not result["authorized"]:
        raise RuntimeError(refusal_message(result))
    return result


def parse_manual_declaration(declaration: str | None, invoked_repo: str, invoked_number: int) -> list[dict[str, Any]]:
    """Read the explicit `owner/repo#N` a manual close must declare.

    `close-with-comment` has no close keyword in its body, so without this the CLI's
    own `--number` would be the only authority for closing that number — the argument
    authorizing itself. Requiring a separately written, repository-qualified
    declaration turns the CLI target into something that can DISAGREE with an
    independent statement of intent, which is what makes the check able to fail.
    """
    if not declaration:
        raise RuntimeError(
            "charness closeout authorization: closing a protected issue through "
            "`close-with-comment` requires an explicit --manual-target-declaration in "
            f"`owner/repo#number` form (e.g. {invoked_repo}#{invoked_number}). The CLI "
            "--number cannot authorize itself."
        )
    # The qualified form is ENFORCED, not merely documented. `normalize_target` happily
    # accepts a bare `514` and resolves it against the CLI's own `--repo`, which makes
    # the "declaration" a restatement of the argument it is supposed to be independent
    # of — a check that cannot disagree cannot fail, which was the whole point.
    if not _QUALIFIED_DECLARATION_RE.match(declaration.strip()):
        raise RuntimeError(
            "charness closeout authorization: --manual-target-declaration must be "
            f"repository-qualified as `owner/repo#number` (got {declaration.strip()!r}). A bare "
            "number resolves against the CLI --repo and would restate the argument it exists to "
            "cross-check."
        )
    module = _load_crosswalk_module()
    if module is None:
        return []
    return [module.normalize_target(declaration.strip(), invoked_repo) | {"source": "manual-declaration"}]
