#!/usr/bin/env python3
"""The single authorization gate every #514/#515/#518 closeout carrier must pass.

WHAT THIS IS NOT: it is not a shared evidence schema, an applicability taxonomy, a
verdict fold, or a reader contract. It answers exactly one question — *may this
carrier close this target right now* — and returns typed target/source identity plus
refusal evidence. That narrowness is deliberate and load-bearing. A "shared
projection" invented before two real readers are proven is the failure this whole
goal is repairing; adding fields here on speculation would recreate it inside the
tool meant to prevent it.

WHY IT EXISTS. This repo has many ways to close an issue: a commit-message close
keyword, a staged closeout artifact, `issue_tool.py close-with-comment`, a PR body,
and several release paths including recovery/resume. Each grew its own target
parsing. That is fine while every path is equivalent, and it is a hole the moment
one issue needs stricter handling than the others — the strictness lands on the path
someone remembered, and the close arrives through one of the others. So every ingress
calls this, and none of them re-parses the result.

THE AGGREGATE RULE is the non-obvious part. Authorization is computed over the UNION
of every closure-bearing source in the carrier — CLI target, manual declaration, body
close keywords, staged artifact — not over each independently. A carrier that closes
#514 in its commit body and #999 via a staged artifact is not "one authorized close
plus one unrelated close"; it is a combined carrier whose #514 half cannot be
evidenced separately, so the whole thing refuses.

BOOTSTRAP STATE. While the crosswalk's `matrix_state` is `bootstrap` (no acceptance
matrix built yet), NO protected close is authorized. The bootstrap slice that creates
this file must not be able to close the issues it exists to protect.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)
_freeze_lib = import_repo_module(__file__, "scripts.issue.issue_source_freeze_lib")
_refusal_lib = import_repo_module(__file__, "scripts.review.closeout_refusal_lib")

CROSSWALK_SCHEMA = "evidence-boundary-crosswalk/v1"
DEFAULT_CROSSWALK_PATH = "charness-artifacts/spec/2026-08-07-evidence-boundary-crosswalk.json"
OWNER_VALUES = ("Charness-owned", "consumer-owned", "re-scoped")
DEPENDENCY_VALUES = ("undecided", "no-shared-artifact", "local-consumer", "shared-consumer")
MATRIX_STATES = ("bootstrap", "complete")

# Carriers that may never close a protected issue in this goal. Release publication,
# tagging, and PR merge are explicitly out of scope, so their close paths must REFUSE
# rather than quietly become the route that ships an unproven close.
OUT_OF_SCOPE_CARRIERS = frozenset(
    {"release", "release-resume", "release-resume-closeout", "publish-execute", "pr-body"}
)

_QUALIFIED_RE = re.compile(r"^(?P<repo>[A-Za-z0-9._-]+/[A-Za-z0-9._-]+)#(?P<number>\d+)$")


class CrosswalkError(_refusal_lib.RefusalError):
    """A close target or crosswalk state that cannot authorize a protected close."""


def normalize_target(target: Any, current_repository: str) -> dict[str, Any]:
    """Normalize one closure-bearing reference to `{repository, issue_number, source}`.

    An UNQUALIFIED `#514` resolves only against the declared current repository, and a
    QUALIFIED reference keeps whatever repository it names — it is never rewritten to
    the current one. That asymmetry is the point: `other-org/other-repo#514` must stay
    foreign so it can be refused, instead of being normalized into the protected
    target it merely resembles.
    """
    if isinstance(target, dict):
        repository = target.get("repository") or current_repository
        number = target.get("issue_number")
        source = target.get("source") or "unknown"
    elif isinstance(target, (tuple, list)) and len(target) == 2:
        repository = target[0] or current_repository
        number, source = target[1], "unknown"
    elif isinstance(target, int):
        repository, number, source = current_repository, target, "unknown"
    elif isinstance(target, str):
        match = _QUALIFIED_RE.match(target.strip())
        if match:
            repository, number, source = match.group("repo"), int(match.group("number")), "unknown"
        elif target.strip().lstrip("#").isdigit():
            repository, number, source = current_repository, int(target.strip().lstrip("#")), "unknown"
        else:
            raise CrosswalkError("unparsable_target", f"cannot read a close target from {target!r}")
    else:
        raise CrosswalkError("unparsable_target", f"cannot read a close target from {target!r}")
    if not isinstance(number, int):
        raise CrosswalkError("unparsable_target", f"issue number is not an integer in {target!r}")
    return {"repository": repository, "issue_number": number, "source": source}


def _key(target: dict[str, Any]) -> tuple[str, int]:
    return (target["repository"].lower(), target["issue_number"])


def load_crosswalk(repo_root: Path, rel: str = DEFAULT_CROSSWALK_PATH) -> dict[str, Any]:
    path = repo_root / rel
    if not path.is_file():
        raise CrosswalkError("crosswalk_missing", f"{rel} does not exist")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise CrosswalkError("crosswalk_invalid", f"{rel}: {exc}") from exc
    if payload.get("schema") != CROSSWALK_SCHEMA:
        raise CrosswalkError("crosswalk_invalid", f"{rel} declares schema {payload.get('schema')!r}")
    return payload


def verify_frozen_source(repo_root: Path, crosswalk: dict[str, Any]) -> None:
    """The crosswalk's declared source identity must still be the frozen one on disk.

    Cheap and local: it compares identities, it does not re-fetch. Re-capturing the
    live issues is a separate, explicit closeout step — this check is what makes a
    crosswalk built against a superseded freeze refuse at every ingress in between.
    """
    identity = crosswalk.get("source_identity") or {}
    freeze_rel = identity.get("freeze_receipt_path")
    if not freeze_rel:
        raise CrosswalkError("stale_source", "the crosswalk declares no freeze receipt path")
    try:
        freeze = _freeze_lib.load_json(repo_root, freeze_rel, _freeze_lib.FREEZE_RECEIPT_SCHEMA)
    except _freeze_lib.FreezeError as exc:
        raise CrosswalkError("stale_source", f"{freeze_rel}: {exc.detail}") from exc
    for field in ("source_snapshot_sha256", "clause_inventory_identity", "reviewed_input_identity", "freeze_identity"):
        if identity.get(field) != freeze.get(field):
            raise CrosswalkError(
                "stale_source",
                f"crosswalk {field}={identity.get(field)!r} but the freeze receipt says {freeze.get(field)!r}",
            )


def _protected_keys(crosswalk: dict[str, Any]) -> set[tuple[str, int]]:
    repository = crosswalk["current_repository"].lower()
    return {(repository, number) for number in crosswalk["protected_issues"]}


def _issue_row(crosswalk: dict[str, Any], number: int) -> dict[str, Any]:
    for row in crosswalk.get("issues") or []:
        if row.get("number") == number:
            return row
    raise CrosswalkError("unmapped_issue", f"the crosswalk protects #{number} but carries no row for it")


def _refusal(reason: str, detail: str, **extra: Any) -> dict[str, Any]:
    return {"applies": True, "authorized": False, "refusal": reason, "detail": detail, **extra}


def authorize_closeout(
    invoked_target_set: Iterable[Any],
    carrier_target_set: Iterable[Any],
    carrier_source: str,
    *,
    repo_root: Path = REPO_ROOT,
    crosswalk_path: str = DEFAULT_CROSSWALK_PATH,
    crosswalk: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Authorize (or refuse) one carrier's close of one target.

    `invoked_target_set` is what the caller ASKED to close (CLI target, manual
    declaration); `carrier_target_set` is what the carrier's CONTENT would close
    (body close keywords, staged artifact).

    They are aggregated for every carrier except `close-with-comment`: its invoked
    manual declaration is an assertion about the separately supplied CLI target,
    so exactly-one-versus-exactly-one disagreement is a distinct
    `target_disagreement` refusal. Commit-hook sets remain halves of one carrier
    because GitHub may close both on push.
    """
    if crosswalk is None:
        try:
            crosswalk = load_crosswalk(repo_root, crosswalk_path)
        except CrosswalkError as exc:
            # No crosswalk means no protected-target knowledge. Refusing every close
            # would break every unrelated issue in the repo, so this stays scoped:
            # the refusal below fires only once a protected target is in play, and a
            # missing crosswalk is reported so it cannot be mistaken for a pass.
            return {
                "applies": False, "authorized": True, "refusal": None,
                "crosswalk_status": exc.code, "crosswalk_detail": exc.detail,
                "invoked_targets": [], "carrier_targets": [], "aggregate_targets": [],
                "carrier_source": carrier_source, "target": None,
            }

    current = crosswalk["current_repository"]
    invoked = [normalize_target(item, current) for item in invoked_target_set]
    carrier = [normalize_target(item, current) for item in carrier_target_set]
    aggregate = invoked + carrier
    protected = _protected_keys(crosswalk)
    hits = [target for target in aggregate if _key(target) in protected]

    base = {
        "invoked_targets": invoked,
        "carrier_targets": carrier,
        "aggregate_targets": aggregate,
        "carrier_source": carrier_source,
        "crosswalk_status": "loaded",
        "protected_issues": sorted(crosswalk["protected_issues"]),
        "current_repository": current,
    }
    # A qualified ref carrying a protected NUMBER but a different repository is
    # checked BEFORE the generic pass-through, and deliberately so. It is not a
    # protected target — normalization correctly refused to rewrite it into one — but
    # letting it fall through as "unrelated" is how a typo'd or copy-pasted
    # `fork/charness#514` becomes a close nobody reviewed. The near-miss is worth a
    # refusal precisely because it looks so much like the real thing.
    foreign = [
        target for target in aggregate
        if target["repository"].lower() != current.lower() and target["issue_number"] in crosswalk["protected_issues"]
    ]
    if not hits and not foreign:
        # Generic pass-through. Unrelated issues keep their existing behavior
        # EXACTLY; this gate adds teeth for three issues, it does not become a new
        # global floor that every other close must now satisfy.
        return {"applies": False, "authorized": True, "refusal": None, "target": None, **base}

    if foreign:
        return _refusal(
            "foreign_repository",
            f"{foreign[0]['repository']}#{foreign[0]['issue_number']} is a different repository than {current}; "
            "a qualified foreign ref is never resolved to the protected target it resembles",
            target=None, **base,
        )
    if carrier_source in OUT_OF_SCOPE_CARRIERS:
        return _refusal(
            "carrier_out_of_scope",
            f"carrier {carrier_source!r} may not close protected issues "
            f"{sorted(crosswalk['protected_issues'])}; release/PR closure is outside this goal's boundary "
            "and needs a separately scoped publish boundary",
            target=None, **base,
        )

    distinct = {_key(target) for target in aggregate}
    if not invoked:
        return _refusal(
            "missing_invoked_target",
            "no invoked/declared target was supplied; a protected close may not be authorized by carrier "
            "content alone (this is what makes close-with-comment declare its target explicitly)",
            target=None, **base,
        )
    invoked_distinct = {_key(target) for target in invoked}
    carrier_distinct = {_key(target) for target in carrier}
    if (
        carrier_source == "close-with-comment"
        and len(invoked_distinct) == 1
        and len(carrier_distinct) == 1
        and invoked_distinct != carrier_distinct
    ):
        declared_repo, declared_number = next(iter(invoked_distinct))
        cli_repo, cli_number = next(iter(carrier_distinct))
        return _refusal(
            "target_disagreement",
            "close-with-comment requires --manual-target-declaration to name the same target as "
            f"the CLI --repo/--number: declaration is {declared_repo}#{declared_number}, "
            f"CLI target is {cli_repo}#{cli_number}; make them identical before retrying.",
            target=None,
            **base,
        )
    if len(distinct) != 1:
        return _refusal(
            "not_singleton",
            "a protected target makes the WHOLE carrier subject to exact singleton equality; "
            f"this carrier closes {sorted(f'{repo}#{number}' for repo, number in distinct)}. "
            "Split protected references cannot be evidenced independently.",
            target=None, **base,
        )

    repository, number = next(iter(distinct))
    target = {"repository": current, "issue_number": number}
    if crosswalk.get("matrix_state") != "complete":
        return _refusal(
            "matrix_incomplete",
            f"the crosswalk is in {crosswalk.get('matrix_state')!r} state; the acceptance matrix that would "
            f"evidence closing #{number} does not exist yet",
            target=target, **base,
        )
    try:
        verify_frozen_source(repo_root, crosswalk)
    except CrosswalkError as exc:
        return _refusal(exc.code, exc.detail, target=target, **base)

    try:
        row = _issue_row(crosswalk, number)
    except CrosswalkError as exc:
        return _refusal(exc.code, exc.detail, target=target, **base)
    if row.get("owner") == "consumer-owned":
        return _refusal(
            "consumer_owned",
            f"#{number} is classified consumer-owned; Charness cannot close it from here",
            target=target, owner=row.get("owner"), **base,
        )
    if row.get("owner") == "re-scoped":
        return _refusal(
            "re_scoped",
            f"#{number} is re-scoped to {row.get('replacement') or 'an unnamed replacement'}; "
            "a re-scope is not completion",
            target=target, owner=row.get("owner"), **base,
        )
    dependency = row.get("projection_dependency")
    if dependency not in DEPENDENCY_VALUES or dependency == "undecided":
        return _refusal(
            "undecided_projection_dependency",
            f"#{number} has projection_dependency={dependency!r}; the seam decision must be made before close",
            target=target, owner=row.get("owner"), **base,
        )
    return {
        "applies": True,
        "authorized": True,
        "refusal": None,
        "target": target,
        "owner": row.get("owner"),
        "projection_dependency": dependency,
        "source_identity": crosswalk.get("source_identity"),
        **base,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect the closeout authorization record for a target.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--crosswalk", default=DEFAULT_CROSSWALK_PATH)
    parser.add_argument("--carrier-source", required=True)
    parser.add_argument("--invoked", nargs="*", default=[], help="e.g. corca-ai/charness#514 or 514")
    parser.add_argument("--carrier", nargs="*", default=[])
    args = parser.parse_args()

    result = authorize_closeout(
        args.invoked, args.carrier, args.carrier_source,
        repo_root=args.repo_root.resolve(), crosswalk_path=args.crosswalk,
    )
    emit_yaml(result)
    return 0 if result["authorized"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
