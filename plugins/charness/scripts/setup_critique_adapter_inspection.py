"""Inspecting a repo's critique adapter: is a reviewer profile declared, and has it drifted?

Split out of `setup_agent_docs_lib.py` when that file crossed its length cap. The boundary is
cohesive rather than mechanical: everything here answers one question — what does THIS repo's
critique adapter declare about reviewer tiers, and does that declaration match the profile it
claims? — while the parent module inspects AGENTS.md prose surfaces (skill routing, subagent
policy, retro memory, commit discipline).

The reason this concern grew large enough to split is worth keeping next to it. Its
applicability predicate used to be `repo_root.name == "charness"` OR a prose token that no
writer in this repo emitted, so the drift finding could only be produced by a directory-name
coincidence — a permanent green for every consumer repo, and a tautology for this one, since
the only live subject was the AGENTS.md the tokens were copied from.
"""

from __future__ import annotations

from pathlib import Path

CODEX_DEFAULT_REVIEWER_TIER_FIELDS = {
    "model": "gpt-5.6-terra",
    "reasoning_effort": "medium",
    "fork_turns": "none",
}

# What declares the Codex multiagent reviewer policy in AGENTS.md prose. The token this
# replaced (`codex multiagent v2`) was emitted by NOTHING -- not a template, not a renderer,
# not this repo's own AGENTS.md -- so the prose disjunct could never fire and the whole
# predicate collapsed onto a directory-name check.
#
# Where it comes from, checked rather than assumed. The setup RENDERER is forbidden to write it
# -- a gate asserts the generated template does not bake a model id into the contract -- and
# this repo's own contract file keeps the per-host framing instead. But
# `skills/public/setup/references/default-surfaces.md` INSTRUCTS an agent to write exactly this
# profile into a repo's `## Subagent Delegation` contract, so it is a real writer-emitted
# declaration for a hand-authored or agent-authored AGENTS.md, not a dead token like the one it
# replaced. A first version of this comment claimed the opposite; opening the reference refuted
# it. That split -- a renderer forbidden to emit what a reference instructs -- is a live
# tension recorded in this module rather than smoothed over.
CODEX_POLICY_DECLARATION_TOKENS = ("gpt-5.6-terra",)


def _declares_codex_reviewer_profile(reviewer_tiers: object) -> bool:
    """True when the critique adapter names the Codex reviewer MODEL on any tier.

    Narrower than "declares any profile field", and the narrowing is load-bearing: a repo whose
    adapter pins `model: gpt-generic` has not adopted this profile, and telling it that its
    tiers drift from a Codex default would be a gate crying wolf at a repo that never opted in.
    Keyed on the model rather than on a tier NAME, so a repo that renames its tiers still
    evidences the policy.

    Adoption evidenced by the model, drift measured on the OTHER fields — effort and
    `fork_turns` — is not circular: the model is what says "this profile applies to me", and
    the check is about whether the rest of the profile matches. A repo that changes the model
    itself has left the profile rather than drifted within it. That case is NOT covered from
    here when it is the only evidence, and nothing else covers it either — said plainly,
    because a first draft of this docstring claimed the missing-adapter and per-host findings
    did, and neither can: the missing-adapter finding requires `found` to be false.
    """
    if not isinstance(reviewer_tiers, dict):
        return False
    expected_model = CODEX_DEFAULT_REVIEWER_TIER_FIELDS["model"]
    return any(
        isinstance(tier, dict) and str(tier.get("model", "")).strip() == expected_model
        for tier in reviewer_tiers.values()
    )



def _detect_critique_adapter_normalization(
    repo_root: Path,
    *,
    agents_text: str,
    fresh_eye_review: dict[str, object],
) -> tuple[dict[str, object], list[dict[str, str]]]:
    from scripts.critique_adapter_lib import load_adapter

    adapter = load_adapter(repo_root)
    data = adapter.get("data", {}) if isinstance(adapter.get("data"), dict) else {}
    reviewer_tiers = data.get("reviewer_tiers", {}) if isinstance(data.get("reviewer_tiers"), dict) else {}
    high_leverage = (
        reviewer_tiers.get("high-leverage", {})
        if isinstance(reviewer_tiers.get("high-leverage"), dict)
        else {}
    )
    medium = reviewer_tiers.get("medium", {}) if isinstance(reviewer_tiers.get("medium"), dict) else {}
    model = str(high_leverage.get("model", ""))
    reasoning_effort = str(high_leverage.get("reasoning_effort", ""))
    stop_gate_detected = bool(fresh_eye_review.get("stop_gate_detected"))
    findings: list[dict[str, str]] = []
    if stop_gate_detected and not adapter.get("found"):
        findings.append(
            {
                "type": "critique_adapter_missing_for_fresh_eye_review",
                "message": (
                    "Fresh-eye or critique review policy is present, but no critique adapter pins reviewer tiers; "
                    "Codex subagents may inherit the parent turn's reasoning effort instead of the intended medium tier."
                ),
                "recommended_action": "run_critique_init_adapter_or_add_reviewer_tiers",
            }
        )
    # What makes the Codex reviewer-tier profile APPLICABLE to this repo. Two disjuncts used
    # to answer that and neither could be true for a consumer: `repo_root.name == "charness"`
    # is a directory-name coincidence (false for any consumer, and false for this repo cloned
    # under another name), and the prose token it fell back to is emitted by NO writer anywhere
    # in this repo -- a reader requiring a token nothing writes, which is the same permanent
    # green a sibling predicate was repaired for ten lines above.
    #
    # The adapter's own contents answer it instead, and that is self-evidencing rather than
    # incidental: a repo that declares a Codex-shaped reviewer tier HAS adopted the profile the
    # drift check is about, whatever its directory is called. The prose disjunct is kept but
    # keyed on a phrase a writer actually emits, so a hand-written AGENTS.md can still declare
    # it -- the reader must not become a comparison against one renderer's output.
    # ADOPTION is what makes the profile applicable, and it is evidenced in two ways that are
    # deliberately different in strength. Prose in AGENTS.md is a REPO-LEVEL statement ("we run
    # this profile"), so when it is present the adapter's own model is fair game to report as
    # drifted. The adapter naming the model on some tier is a WEAKER, per-tier signal: it says
    # this repo is on the profile, so the other tiers' fields can be measured against it — but
    # a repo whose every tier names some other model has not drifted within this profile, it is
    # not on it, and firing there would be a wolf-cry at a repo that never opted in.
    #
    # What this does NOT cover, stated rather than implied: a repo that adopted the profile
    # with NO prose declaration and has since moved every tier off the model is silent. That
    # case is genuinely ambiguous from here — it reads identically to a repo that chose another
    # model on purpose — and nothing else in this module covers it either.
    codex_policy_evidenced = _declares_codex_reviewer_profile(reviewer_tiers) or any(
        token in agents_text.lower() for token in CODEX_POLICY_DECLARATION_TOKENS
    )
    if adapter.get("found") and codex_policy_evidenced:
        # Only tiers the repo actually DECLARED. A first version measured against the literal
        # pair `high-leverage`/`medium`, each defaulting to `{}` when absent — so a consumer
        # declaring one correct tier drifted against an empty dict whose every field is
        # `None != expected`, producing a `review_required` finding naming a tier it does not
        # have. That is the wolf-cry this repair set out to avoid, newly reachable for
        # consumers precisely because the directory-name gate is gone.
        # Every DECLARED tier, read from the adapter itself — not the literal pair
        # `high-leverage`/`medium`. Two rounds moved this line in opposite directions and both
        # were wrong: measuring the fixed pair told a one-tier repo it drifted on a tier it does
        # not have, and then narrowing to that pair's truthiness left a repo with a RENAMED tier
        # evidencing adoption and measuring nothing at all — a permanent green for a repo the
        # adoption predicate deliberately supports, which is this check's original defect
        # reproduced inside its own repair. Adoption iterates every tier, so measurement must
        # too. (`critique_adapter_lib` only WARNS on an unknown tier name; it still loads it.)
        declared = {
            name: tier
            for name, tier in reviewer_tiers.items()
            if isinstance(tier, dict) and tier
        }
        # EVERY field, including `model`, once adoption is evidenced. A first version excluded
        # `model` unless prose declared the profile, on a circularity worry that does not
        # survive contact: a tier that names the model is by definition not drifted on it, so
        # including the field costs that tier nothing — while EXCLUDING it silently dropped the
        # mixed case, where `high-leverage` is on the profile and `medium` has left it. That is
        # the sharpest instance the check exists to catch, and it is exactly the shape a repo
        # reaches by upgrading one tier and forgetting the other.
        drifted_tiers = {
            name: {
                field: tier.get(field)
                for field, expected in CODEX_DEFAULT_REVIEWER_TIER_FIELDS.items()
                if tier.get(field) != expected
            }
            for name, tier in declared.items()
        }
        drifted_tiers = {name: fields for name, fields in drifted_tiers.items() if fields}
    else:
        drifted_tiers = {}
    if drifted_tiers:
        findings.append(
            {
                "type": "critique_adapter_codex_profile_drift",
                "message": (
                    "Critique adapter's Codex reviewer tiers drift from the default "
                    "`gpt-5.6-terra` / `medium` / `fork_turns: none` profile: "
                    + "; ".join(
                        f"{name} ({', '.join(f'{field}={value!r}' for field, value in sorted(fields.items()))})"
                        for name, fields in sorted(drifted_tiers.items())
                    )
                    + "."
                ),
                "recommended_action": "set_codex_reviewer_tiers_default_profile",
            }
        )
    return (
        {
            "found": bool(adapter.get("found")),
            "valid": bool(adapter.get("valid")),
            "path": (
                Path(str(adapter["path"])).resolve().relative_to(repo_root.resolve()).as_posix()
                if adapter.get("path")
                else None
            ),
            "high_leverage_model": model or None,
            "high_leverage_reasoning_effort": reasoning_effort or None,
            "medium_model": str(medium.get("model", "")) or None,
            "medium_reasoning_effort": str(medium.get("reasoning_effort", "")) or None,
        },
        findings,
    )
