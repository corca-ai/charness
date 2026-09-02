#!/usr/bin/env python3
"""Gate the closeout classification vocabulary on PARITY across every copy of it.

[#586](https://github.com/corca-ai/charness/issues/586) reports a shape the suite
cannot see: a check exists, its own tests pass, and it never fires on the wired
path. Its first and sixth recorded instances are one narrower thing -- a value
added to ONE enumeration and not its siblings. `consolidated` reached
`audit_brief.KNOWN_CLASSIFICATIONS` and a ledger table while
`issue_verify_closeout.CLASSIFICATIONS`, an argparse `choices` tuple, and the
commit-message regex all still refused it, and the commit hook's fallthrough then
demanded exactly the repair claims that disposition exists to forbid.

This gate compares the canonical tuple with the six real consumers listed in
`SITES` below. It does not duplicate every closeout floor across every carrier.

Three deliberate properties, because this is a proof surface:

1. **No site is judged by parsing a source literal.** Five of six are probed
   through the surface an operator reaches -- argparse by parsing an argv, a regex
   by matching the production line, a planner by building a plan, the ledger by
   calling its accessor. That is the #586 lesson applied to the gate written for
   #586: a test that reads a tuple passes while the wired surface refuses the
   value. **Stated exactly, because an earlier draft of this docstring overclaimed
   it:** `audit_brief.KNOWN_CLASSIFICATIONS` is read as a module ATTRIBUTE, not
   exercised through `audit_brief`'s own transcript check, so that one site is a
   membership read.
2. **A site that cannot be probed reports NOT-RUN, never a pass** -- and never
   takes the rest of the report down with it. Any exception from a probe resolves
   that one site to not-run, `SystemExit` included: a probed module growing an
   import-time `sys.exit` would otherwise end the process at exit 0 with no payload
   at all, which is the strongest fail-open available. `KeyboardInterrupt` is
   deliberately NOT caught.
3. **A missing classification fails unless the site DECLARED that absence.** A
   `subset` site names the values its recorded decision lets it omit; anything else
   missing is a failure. "Subset" without that list meant any subset, so deleting a
   real row read as designed.

What this gate does NOT check: whether the canonical vocabulary is the RIGHT one,
and whether a site that accepts a classification then does anything correct with
it. Parity is agreement, not correctness -- six sites can agree on a wrong value.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import sys
from pathlib import Path
from typing import Any, Callable

from runtime_bootstrap import load_path_module, repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

# The runner's shared "analyzed nothing, so this is not a pass" byte.
UNESTABLISHED_EXIT = 3

# The one tuple every other site is measured against. Loaded live rather than
# copied, because a gate carrying its own seventh copy of the vocabulary is the
# defect it exists to refuse.
CANONICAL_REL = "skills/public/issue/scripts/issue_verify_closeout.py"
CANONICAL_ATTR = "CLASSIFICATIONS"

# The negative probes. A site that accepts ANY of these is not enumerating a
# vocabulary at all, which a positives-only check reads as perfect parity.
#
# There is more than one because a single sentinel is defeated by a plausible
# loosening: a regex simplified to `[a-z][a-z-]*` accepts every canonical value
# AND refuses an underscore-wrapped sentinel, so the gate would certify parity for
# a hook that had stopped enumerating anything. The set therefore spans shapes --
# underscore-wrapped, plain lowercase, and a near-miss of a real value. A site
# must refuse EVERY one. Found by a bounded round-1 reviewer.
NON_CLASSIFICATIONS = ("__not-a-classification__", "banana", "bugg")
NON_CLASSIFICATION = NON_CLASSIFICATIONS[0]

# Sites already held elsewhere, named so a reader does not mistake this gate's
# scope for the whole vocabulary surface.
DELEGATED_SITES = {
    "plugins/charness/** (exported mirror copies)": (
        "derivative, not independent: the mirror is regenerated from its source by "
        "sync_root_plugin_manifests.py on charness init/update and at the release "
        "version bump, and it is untracked, so no commit carries it. Not re-probed here"
    ),
}

# Tuples keyed on the SAME vocabulary that this gate does NOT hold, because they
# are policy subsets rather than copies of it -- there is no canonical answer to
# compare them against. A typo in one silently disarms that classification's rule,
# so they are named here rather than left to look covered. Found by a bounded
# round-1 reviewer.
UNPROBED_RELATED = {
    "skills/public/issue/scripts/audit_brief.py:REQUIRE_BRIEF_CLASSIFICATIONS": "policy subset",
    "skills/public/issue/scripts/issue_closeout_rung1_floors.py:BEHAVIORAL_VERDICT_CLASSIFICATIONS": "policy subset",
    "skills/public/issue/scripts/issue_closeout_rung1_floors.py:FLOOR_EXEMPT_CLASSIFICATIONS": "policy subset",
    "skills/public/issue/scripts/issue_resolution_critique.py:CRITIQUE_REQUIRED_CLASSIFICATIONS": "policy subset",
    "skills/public/issue/SKILL.md and closeout reference prose": "prose, not behaviorally probeable",
}


# A site's arity decides whether a missing classification FAILS. Left as free
# text, a one-character typo (`"Exact"`, `"exact "`) silently demotes an exact site
# to permissive with every test green -- #586's own shape, inside the gate for
# #586. An unrecognized arity is a not-run, never a pass.
ARITIES = frozenset({"exact", "subset"})


class ProbeError(RuntimeError):
    """A site could not be observed. Resolves to NOT-RUN, never to a pass."""


def _load(repo_root: Path, rel: str) -> Any:
    path = repo_root / rel
    if not path.is_file():
        raise ProbeError(f"{rel} is absent")
    try:
        return load_path_module(f"parity_probe_{path.stem}", path)
    except (Exception, SystemExit) as exc:  # noqa: BLE001 - any import failure is an unobserved site
        raise ProbeError(f"{rel} did not import: {type(exc).__name__}: {exc}") from exc


def _attr(module: Any, name: str, rel: str) -> Any:
    if not hasattr(module, name):
        raise ProbeError(f"{rel} no longer defines {name}")
    return getattr(module, name)


def _membership_probe(rel: str, attr: str) -> Callable[..., Callable[[str], bool]]:
    def build(repo_root: Path, _canonical: tuple[str, ...]) -> Callable[[str], bool]:
        values = _attr(_load(repo_root, rel), attr, rel)
        if not isinstance(values, (tuple, list, set, frozenset)):
            raise ProbeError(f"{rel}:{attr} is {type(values).__name__}, not an enumeration")
        frozen = frozenset(values)
        return lambda value: value in frozen

    return build


def _regex_probe(rel: str, attr: str) -> Callable[..., Callable[[str], bool]]:
    """Probe a classification regex by the LINE it reads in production."""

    def build(repo_root: Path, canonical: tuple[str, ...]) -> Callable[[str], bool]:
        pattern = _attr(_load(repo_root, rel), attr, rel)
        if not hasattr(pattern, "search"):
            raise ProbeError(f"{rel}:{attr} is not a compiled pattern")

        def accepts(value: str) -> bool:
            match = pattern.search(f"Classification: {value}")
            return bool(match) and match.group("classification") == value

        # Liveness is "does this probe observe ANYTHING", never "does it accept the
        # first canonical value". Keying on `canonical[0]` made a site that had
        # merely DROPPED `bug` indistinguishable from a broken probe: it raised
        # ProbeError, resolved to not-run, and -- once the label became
        # unestablished-capable -- exited the whole quality run 0 on a real parity
        # break. Found by a bounded round-2 reviewer.
        if not any(accepts(value) for value in canonical) and not any(
            accepts(value) for value in NON_CLASSIFICATIONS
        ):
            raise ProbeError(
                f"{rel}:{attr} matched no probe line at all, so its vocabulary was not observed"
            )
        return accepts

    return build


def _release_cli_choices_probe(repo_root: Path, canonical: tuple[str, ...]) -> Callable[[str], bool]:
    """Probe argparse by PARSING an argv, not by reading the `choices` tuple."""
    rel = "skills/public/release/scripts/publish_release_cli.py"
    module = _load(repo_root, rel)
    parse_args = _attr(module, "parse_args", rel)

    def accepts(value: str) -> bool:
        saved = sys.argv
        sys.argv = [
            "publish_release_cli",
            "--repo-root", str(repo_root),
            "--publish-current",
            "--close-issue-classification", value,
        ]
        try:
            with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                namespace = parse_args()
        except SystemExit:
            return False
        finally:
            sys.argv = saved
        return getattr(namespace, "close_issue_classification", None) == value

    if not any(accepts(value) for value in canonical):
        # ANY canonical value, not the first: a site that dropped exactly `bug` is a
        # parity FAILURE, not an unobserved site. See the sibling note in _regex_probe.
        raise ProbeError(
            f"{rel} refused a canonical classification through an otherwise-valid argv, so the "
            "probe's argv no longer reaches --close-issue-classification and nothing here was observed"
        )
    return accepts


def _issue_plan_actions_probe(repo_root: Path, _canonical: tuple[str, ...]) -> Callable[[str], bool]:
    """Probe the resolve planner by BUILDING a plan and reading its dispatch keys."""
    rel = "skills/public/issue/scripts/issue_plan.py"
    module = _load(repo_root, rel)
    build_resolve_plan = _attr(module, "build_resolve_plan", rel)
    try:
        plan = build_resolve_plan(repo_root, {}, {})
    except Exception as exc:  # noqa: BLE001 - an unbuildable plan is an unobserved site
        raise ProbeError(f"{rel}:build_resolve_plan raised {type(exc).__name__}: {exc}") from exc
    actions = plan.get("classification_actions")
    if not isinstance(actions, dict) or not actions:
        raise ProbeError(f"{rel} emitted no classification_actions, so its dispatch was not observed")
    return lambda value: value in actions


def _ledger_fields_probe(repo_root: Path, _canonical: tuple[str, ...]) -> Callable[[str], bool]:
    """Probe the ledger through `has_classification_row`, its production accessor.

    Reading `CLASSIFICATION_FIELDS` directly would be the attribute read this gate
    exists to refuse. An earlier form asked whether `classification_requirements`
    returned something other than `DEFAULT_FIELDS`, which is a proxy that breaks the
    moment a classification is given an explicit row equal to the default -- the
    gate would then report it missing, and the remedy it prints ("add it to that
    site's surface") would be unsatisfiable because the row already exists. Found by
    a bounded round-2 reviewer.
    """
    rel = "skills/public/issue/scripts/issue_closeout_classification_ledger.py"
    has_row = _attr(_load(repo_root, rel), "has_classification_row", rel)
    return lambda value: bool(has_row(value))


# `exact` sites must accept EVERY canonical classification and refuse anything
# else. `subset` sites may omit classifications by a recorded design decision, so
# they are held only to the other direction: no key outside the vocabulary.
SITES: tuple[dict[str, Any], ...] = (
    {
        "id": "audit-brief-known-classifications",
        "arity": "exact",
        "surface": "skills/public/issue/scripts/audit_brief.py:KNOWN_CLASSIFICATIONS",
        "why": "the transcript auditor's own vocabulary; instance 1 of #586 added `consolidated` here first",
        "build": _membership_probe("skills/public/issue/scripts/audit_brief.py", "KNOWN_CLASSIFICATIONS"),
    },
    {
        "id": "commit-msg-hook-regex",
        "arity": "exact",
        "surface": "scripts/gates/check_issue_closeout_commit_msg.py:_CLASSIFICATION_RE",
        "why": (
            "a classification missing here does not fail loudly -- it falls through to "
            "`_infer_classification`, which defaults to `bug`"
        ),
        "build": _regex_probe("scripts/gates/check_issue_closeout_commit_msg.py", "_CLASSIFICATION_RE"),
    },
    {
        "id": "release-closeout-message-regex",
        "arity": "exact",
        "surface": "skills/public/release/scripts/release_issue_closeout_message.py:_CLASSIFICATION_LINE_RE",
        "why": "the release carrier's second copy of the same alternation; it falls through silently too",
        "build": _regex_probe(
            "skills/public/release/scripts/release_issue_closeout_message.py",
            "_CLASSIFICATION_LINE_RE",
        ),
    },
    {
        "id": "release-cli-close-issue-choices",
        "arity": "exact",
        "surface": "skills/public/release/scripts/publish_release_cli.py:--close-issue-classification",
        "why": "argparse refuses a missing value before any code runs, i.e. the disposition is unreachable",
        "build": _release_cli_choices_probe,
    },
    {
        "id": "issue-plan-classification-actions",
        "arity": "exact",
        "surface": "skills/public/issue/scripts/issue_plan.py:build_resolve_plan().classification_actions",
        "why": "a classification with no dispatch entry reaches the resolver with no action and no refusal",
        "build": _issue_plan_actions_probe,
    },
    {
        "id": "closeout-classification-fields",
        "arity": "subset",
        # The recorded decision covers exactly these two, which fall through to
        # DEFAULT_FIELDS. Without naming them, "subset" meant ANY subset -- deleting
        # the `bug` row silently dropped root-cause/prevention from every bug
        # closeout and this gate printed `absent_by_design: [bug]` and passed.
        "absent_by_design": ("question", "decision-needed"),
        "surface": "skills/public/issue/scripts/issue_closeout_classification_ledger.py:CLASSIFICATION_FIELDS",
        "why": (
            "`question`/`decision-needed` fall through to DEFAULT_FIELDS by a recorded decision, so "
            "absence is legal here and only an unknown KEY is a drift"
        ),
        "build": _ledger_fields_probe,
    },
)


def _judge_site(site: dict[str, Any], repo_root: Path, canonical: tuple[str, ...], assume: tuple[str, ...]) -> dict[str, Any]:
    """Render ONE site's verdict. Lifted out of `evaluate` so each refusal branch --
    stale declaration, stale exemption, unrecognized arity, unobservable probe,
    undeclared absence, over-permissive surface -- reads on its own."""
    row = {"id": site["id"], "arity": site["arity"], "surface": site["surface"]}
    declared_absences = tuple(site.get("absent_by_design", ()))

    stale = [value for value in declared_absences if value not in canonical]
    if stale:
        return {**row, "status": "not-run",
                "reason": f"declared absences {stale} are not classifications; this site's declaration is stale"}
    if site["arity"] not in ARITIES:
        return {**row, "status": "not-run",
                "reason": f"unrecognized arity {site['arity']!r}; expected one of {sorted(ARITIES)}"}
    try:
        accepts = site["build"](repo_root, canonical)
        missing = [value for value in canonical if not accepts(value)]
        accepted_non = [value for value in NON_CLASSIFICATIONS if accepts(value)]
    except ProbeError as exc:
        return {**row, "status": "not-run", "reason": str(exc)}
    except (Exception, SystemExit) as exc:  # noqa: BLE001 - ANY unobserved site is not-run
        # The probes call foreign code (a regex group name, an argparse surface, a
        # planner). Escaping here used to take the whole report down, so one broken
        # probe suppressed every other site's verdict -- real failures included.
        return {**row, "status": "not-run", "reason": f"probe raised {type(exc).__name__}: {exc}"}

    stale_exemptions = [value for value in declared_absences if value in canonical and value not in missing]
    if stale_exemptions:
        return {**row, "status": "not-run",
                "reason": (f"declared absences {stale_exemptions} are no longer absent; the declaration has "
                           "become a standing exemption that would let a real deletion pass")}
    if accepted_non:
        return {**row, "status": "fail", "accepts_non_classification": accepted_non,
                "reason": "this site is not enumerating the vocabulary; it accepts values outside it"}
    # An ASSUMED value is exempt from the subset rule: a `subset` site legally omits
    # values, so a hypothetical addition cannot be judged there at all.
    undeclared = [v for v in missing if v not in declared_absences and v not in assume]
    if site["arity"] == "subset" and undeclared:
        return {**row, "status": "fail", "missing": undeclared,
                "reason": ("this site may omit only the classifications its recorded decision names; "
                           f"declared absences are {list(declared_absences)}")}
    if site["arity"] == "exact" and missing:
        return {**row, "status": "fail", "missing": missing, "reason": site["why"]}
    return {**row, "status": "pass", **({"absent_by_design": missing} if missing else {})}


def evaluate(repo_root: Path, *, assume: tuple[str, ...] = ()) -> dict[str, Any]:
    """Judge every site against the canonical vocabulary, plus any ASSUMED additions.

    `assume` exists so the gate's own catch is MEASURABLE without editing the tree.
    A green parity gate proves nothing by itself -- every site agreeing today is
    also what a gate that probes nothing looks like. Passing a classification the
    tree does not have renders the verdict this gate would give the moment someone
    adds a seventh disposition to one site and not its siblings, which is the
    recorded #586 instance. It is a measurement instrument, not a policy knob: the
    values are never written anywhere and no site is exempted by it.
    """
    try:
        canonical = _attr(_load(repo_root, CANONICAL_REL), CANONICAL_ATTR, CANONICAL_REL)
    except ProbeError as exc:
        return {
            "status": "not-run",
            "reason": f"the canonical vocabulary was not observed: {exc}",
            "sites": [],
        }
    canonical = tuple(canonical)
    if not canonical:
        return {"status": "not-run", "reason": f"{CANONICAL_REL}:{CANONICAL_ATTR} is empty", "sites": []}
    already = [value for value in assume if value in canonical]
    if already:
        # Otherwise `--assume-classification bug` yields an exit-0 run wearing the
        # `hypothetical` badge: a measurement-shaped green that measured nothing.
        return {
            "status": "not-run",
            "reason": (
                f"assumed classifications {already} are already canonical, so this run would measure "
                "nothing while looking like a measurement. Assume a value the tree does NOT have."
            ),
            "sites": [],
        }
    # No emptiness re-check here. The guard above already returned for an empty
    # `canonical`, and concatenating cannot empty a non-empty tuple -- so the duplicate
    # was a branch no input could reach, which is a line the changed-line coverage gate
    # can never see covered and a reader can only mistake for a real case.
    canonical = canonical + tuple(assume)

    sites = [_judge_site(site, repo_root, canonical, assume) for site in SITES]

    if any(site["status"] == "fail" for site in sites):
        status = "fail"
    elif any(site["status"] == "not-run" for site in sites):
        status = "not-run"
    else:
        status = "pass"
    return {"status": status, "canonical": list(canonical), "sites": sites}


def report(result: dict[str, Any], repo_root: Path, assume: tuple[str, ...] = ()) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "check": "closeout-classification-parity",
        "issue": "https://github.com/corca-ai/charness/issues/586",
        "status": result["status"],
        "canonical_source": f"{CANONICAL_REL}:{CANONICAL_ATTR}",
        "canonical": result.get("canonical", []),
        "sites": result["sites"],
        # Named on EVERY run, passing included, so a green here is never read as a
        # verdict over the whole vocabulary surface.
        "not_judged": {
            "delegated": DELEGATED_SITES,
            "unprobed_related_tuples": UNPROBED_RELATED,
            "scope": (
                "parity only. This gate does not judge whether the canonical vocabulary is right, "
                "nor whether a site that accepts a classification handles it correctly."
            ),
        },
    }
    if assume:
        payload["hypothetical"] = {
            "assumed_classifications": list(assume),
            "reading": (
                "This run measures the verdict a seventh disposition WOULD produce; it is not a "
                "verdict about the tree. `subset` sites cannot be judged for an assumed value at "
                "all -- an absence there is legal by design, so they report it as absent_by_design "
                "whether or not a real addition would need them updated."
            ),
        }
    if result["status"] == "not-run" and "reason" in result:
        payload["reason"] = result["reason"]
    if result["status"] == "fail":
        over_permissive = [site for site in result["sites"] if site.get("accepts_non_classification")]
        missing_somewhere = [site for site in result["sites"] if site.get("missing")]
        remedies = []
        if missing_somewhere:
            remedies.append(
                f"A site below refuses a value {CANONICAL_REL}:{CANONICAL_ATTR} carries. Add it to that "
                "site's own surface -- not to this gate. A value the canonical tuple does not carry is "
                "not a seventh classification, it is a bug."
            )
        if over_permissive:
            # Distinct because "add the missing classification" is unsatisfiable here:
            # nothing is missing, the site accepts values outside the vocabulary.
            remedies.append(
                "A site below accepts values OUTSIDE the vocabulary, so it has stopped enumerating "
                "anything and its green said nothing. Narrow that surface back to the canonical set."
            )
        payload["remedy"] = " ".join(remedies)
    if result["status"] == "not-run":
        payload["remedy"] = (
            "A site could not be observed, which is not a pass. Repair the probe or the surface it "
            f"reads before trusting this lane. Sites live in {Path(__file__).name}:SITES."
        )
    payload["repo_root"] = str(repo_root)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--assume-classification",
        action="append",
        default=[],
        metavar="NAME",
        help=(
            "Measure the verdict a classification the tree does NOT have would produce, without "
            "editing anything. This is how the gate's catch is re-measured: a run under an assumed "
            "seventh disposition should turn every `exact` site red. Repeat for multiple. The "
            "result is a hypothetical, and says so in its payload."
        ),
    )
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    assume = tuple(args.assume_classification)
    result = evaluate(repo_root, assume=assume)
    emit_yaml(report(result, repo_root, assume))
    if result["status"] == "not-run":
        return UNESTABLISHED_EXIT
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
