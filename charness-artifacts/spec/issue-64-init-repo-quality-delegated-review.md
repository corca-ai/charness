# Issue 64 Spec: Delegated Review for Init-Repo and Quality

## Problem

Issue [#64](https://github.com/corca-ai/charness/issues/64) shows that
`init-repo` and `quality` can miss operating-surface and quality-posture issues
when a single agent follows deterministic gates too literally.

The original failure was not only a missing premortem phrase. The deeper problem
is that contextual operating guidance is currently delivered as prose or narrow
text detectors instead of as a reviewable recommendation queue, and the
review posture for high-judgment surfaces is not explicit enough. A later
Cautilus session confirmed that several bounded reviewers found different
classes of issues that the original same-context pass missed.

## Current Slice

Define the implementation contract for making `init-repo` and `quality`
explicit delegated-review workflows:

- `AGENTS.md` should authorize bounded subagent spawning for repo-mandated
  `init-repo` and `quality` review work, similar to the existing premortem
  host-restriction rule.
- `init-repo` should emit structured recommendation queues instead of hiding
  contextual policy recommendations behind generic normalization findings.
- `quality` should review adapter and gate design as a first-class posture:
  structural facts, contextual recommendations, acknowledgement/migration
  state, and brittle gate risks.
- deterministic scripts should produce evidence and candidate findings for
  reviewers, not try to own the whole judgment.
- final reports must carry advisory findings and delegated-review status, not
  only green gate summaries.

This spec was itself checked by a bounded fresh-eye reviewer before closeout.
The reviewer confirmed the direction and called out three must-not-lose details:
keep inspect/help routes cheap, preserve existing adapter compatibility with
optional migration fields, and require concrete evidence when a delegated
review is `blocked` or when no advisory findings are reported.

## Fixed Decisions

- Task-completing `init-repo` and `quality` runs require bounded subagent
  review. Route-only, help-only, and raw inspection commands do not.
- If the host cannot spawn subagents, the run is blocked for the canonical
  review path. Same-agent fallback must not be reported as equivalent.
- The final artifact must record whether delegated review was actually spawned,
  blocked by host/tooling, or not applicable. A blocked state needs a concrete
  host signal, not a generic assertion.
- Hard gates remain reserved for structural facts with low false-positive risk:
  missing required files, broken symlink policy, invalid adapters, generated
  export drift, malformed schemas, broken links, failing tests, and similar
  directly verifiable facts.
- Contextual operating guidance becomes a reviewable recommendation queue with
  target, id, priority, confidence, evidence, suggested action, and
  acknowledgement/migration status.
- Repo-specific policy sources must come from adapters or repo-local config,
  not hardcoded Charness defaults.
- Multi-review findings feed the same recommendation queue, where duplicate or
  low-confidence findings can be triaged instead of becoming noisy gates.

## Probe Questions

- Should the minimum delegated review set be two reviewers or three reviewers
  for `init-repo`? The Cautilus evidence suggests three useful lenses:
  host-policy, operating surfaces/adapters, and operator takeover flow.
- Should `quality` always run the same number of reviewers, or should the
  adapter define review lenses by repo type?
- Should the recommendation queue live only in each skill adapter, or should
  `quality` own a cross-adapter queue index?
- Should `init-repo` eventually migrate existing adapters to `version: 2`, or
  keep the first implementation as `version: 1` plus optional fields? The first
  slice should preserve `version: 1` compatibility.
- Should Cautilus instruction-surface proof be required for every prompt-facing
  contract change here, or only for changed public skill/AGENTS surfaces?

## Deferred Decisions

- exact UI or CLI for accepting/acknowledging recommendations
- auto-opening GitHub issues from recommendation queues
- a universal Charness recommendation schema shared by every skill
- making delegated review a standing local gate
- scoring or ranking reviewers by historical yield

## Non-Goals

- replacing deterministic validators with subagents
- turning every advisory heuristic into a hard gate
- hardcoding Cautilus-specific policy files such as
  `docs/internal/working-patterns.md`
- expanding `init-repo` into a full `quality` audit
- treating a same-agent checklist as delegated review

## Surfaces to Modify

### Repo Operating Contract

- `AGENTS.md`
  - add an explicit rule that repo-mandated `init-repo` and `quality`
    bounded reviews are already authorized to spawn subagents
  - keep the existing host-block behavior: if spawning is unavailable, stop and
    report the host restriction rather than substituting same-agent review
  - keep wording short enough that AGENTS remains a startup contract rather
    than a long skill catalog

### `init-repo`

- `skills/public/init-repo/SKILL.md`
  - add a delegated review gate for task-completing normalization
  - state that deterministic inspection provides evidence for reviewers
  - state that the output must include delegated-review status and queued
    recommendations
- `skills/public/init-repo/references/agent-docs-policy.md`
  - distinguish hard facts from contextual recommendations
  - document the AGENTS delegated-review authorization snippet
- `skills/public/init-repo/references/normalization-flow.md`
  - define the bounded review sequence and priority ordering
- `skills/public/init-repo/adapter.example.yaml`
  - add optional `policy_sources`, `recommendation_sets.enabled`,
    `acknowledged`, and `defaults_version` examples without breaking current
    `version: 1` adapters
- `skills/public/init-repo/scripts/init_repo_adapter.py`
  - parse and validate policy sources, recommendation sets, defaults version,
    and acknowledgements
  - resolve missing optional fields to safe empty defaults
- `scripts/init_repo_inspect_lib.py`
  - replace the AGENTS-only fresh-eye marker check with adapter-declared
    policy-source evidence
  - emit `recommendations[]` alongside existing `normalization.findings`
  - prioritize host-policy recommendations above skill-routing drift
- tests
  - add a synthetic repo where adapter-declared policy sources imply an
    `AGENTS.md` delegated-review recommendation even though `AGENTS.md` lacks
    the trigger marker
  - cover acknowledgement suppressing repeated custom Skill Routing warnings
  - cover priority sorting so review-required host policy outranks generated
    block drift

### `quality`

- `skills/public/quality/SKILL.md`
  - upgrade the current single fresh-eye step into an explicit bounded
    multi-lens review posture for task-completing quality reviews
  - require the final summary to include `Advisory` and `Delegated Review`
    sections even when hard gates pass
  - add adapter/gate design review to the detection workflow
- `skills/public/quality/references/adapter-contract.md`
  - add fields for recommendation defaults version, adapter review sources,
    acknowledged recommendations, and gate-design review globs
- new `skills/public/quality/references/adapter-gate-review.md`
  - define structural fact, contextual recommendation, acknowledgement,
    migration, and brittle hard-gate smell
- new `skills/public/quality/scripts/inventory_adapter_gate_design.py`
  - inventory Charness adapters, local gates, recommendation-like scripts, and
    high-noise heuristics
  - emit structured findings with enforcement tier, confidence, evidence, and
    suggested structural action
- `scripts/quality_adapter_lib.py`
  - validate new adapter fields without breaking existing adapters
- `scripts/validate_quality_artifact.py`
  - require `Advisory` and `Delegated Review` sections in current quality
    artifacts
  - reject final reports that only summarize green gates when advisory findings
    exist in the artifact
  - require a reasoned `none found by inventory` style statement when no
    advisory findings are present
  - require a concrete host/tool signal when delegated review is blocked
- tests
  - cover adapter-gate inventory output
  - cover quality artifact validation for advisory/delegated-review sections
  - cover existing adapters resolving with default empty review fields

### Current Reports and Artifacts

- `charness-artifacts/quality/latest.md`
  - add `Advisory` and `Delegated Review` sections as the current report shape
  - keep the file under the existing concision limit
- `charness-artifacts/spec/issue-64-init-repo-quality-delegated-review.md`
  - this file is the implementation contract until the first slice lands
- `docs/public-skill-dogfood.json`
  - refresh reviewed dogfood notes for `init-repo` and `quality` after the
    public contracts change
- `charness-artifacts/cautilus/latest.md`
  - refresh if prompt-affecting skill, adapter, or AGENTS surfaces change

## Delegated Review Lenses

### `init-repo`

- `host-instruction-policy`
  - checks `AGENTS.md`, `CLAUDE.md`, delegated review authorization, skill
    routing, repo-owned skill proof policy, and host-block behavior
- `operating-surface-adapter`
  - checks README, roadmap, operator acceptance, handoff/retro memory, adapter
    declared surfaces, missing files, and false confidence from defaults
- `operator-takeover-flow`
  - checks read-first paths, command tiers, bootstrap/probe surface,
    maintainer takeover checklist, and whether a new operator can act without
    rediscovering state

### `quality`

- `gate-design`
  - separates structural fact gates from contextual recommendations and flags
    brittle phrase-matching gates
- `adapter-policy`
  - checks adapter defaults versions, policy sources, acknowledgements,
    migrations, and repo-specific configuration boundaries
- `operator-signal`
  - checks whether the final report carries hard-gate proof, advisory findings,
    delegated-review status, runtime hot spots, coverage posture, and evaluator
    depth without implying false cleanliness

## Recommendation Record Shape

```json
{
  "id": "agents.delegated_review_policy",
  "target": "AGENTS.md",
  "kind": "policy_sync",
  "priority": "review_required",
  "confidence": "medium",
  "enforcement_tier": "NON_AUTOMATABLE",
  "evidence": [
    "adapter-declared policy source mentions premortem or bounded fresh-eye review",
    "AGENTS.md lacks delegated-review host restriction wording"
  ],
  "suggested_action": "Review whether AGENTS.md should carry the delegated review rule.",
  "acknowledgement": {
    "status": "unacknowledged",
    "adapter_path": ".agents/init-repo-adapter.yaml"
  }
}
```

## Constraints

- Keep public skill cores concise; move schema and examples to references.
- Do not hardcode repo-specific policy paths in public skills or default
  scripts.
- Do not make subagents responsible for facts scripts can verify.
- Do not make deterministic scripts responsible for final judgment on
  contextual operating guidance.
- Keep generated plugin exports synchronized after source skill/script changes.
- Prompt-affecting changes must follow the Cautilus proof planner.

## Success Criteria

- `init-repo` task-completing runs have an explicit delegated-review gate and
  report `executed`, `blocked`, or `not_applicable` with a reason.
- `quality` task-completing reviews have an explicit bounded multi-lens review
  gate and report `executed`, `blocked`, or `not_applicable` with a reason.
- `AGENTS.md` explicitly authorizes repo-mandated `init-repo` and `quality`
  bounded review subagent spawning.
- `init-repo` emits reviewable recommendations from adapter-declared policy
  sources, not only AGENTS-local marker checks.
- `quality` can inventory adapter/gate design and classify findings as
  structural facts, contextual recommendations, or acknowledgement/migration
  gaps.
- quality reports cannot pass validation while omitting advisory findings or
  delegated-review status. Empty advisory sections need inventory-backed
  evidence, and blocked delegated-review sections need concrete host/tool
  evidence.
- existing adapters continue to resolve with safe defaults.
- tests prove acknowledgement suppresses intentional customizations without
  suppressing unrelated required recommendations.

## Acceptance Checks

- implementation proof expectations:
  - `init-repo inspect` emits `normalization.findings` and `recommendations[]`
    separately. A synthetic repo with adapter-declared fresh-eye/premortem
    policy sources produces `agents.delegated_review_policy` even when
    `AGENTS.md` lacks the old marker text.
  - recommendation priority sorts host-policy `review_required` above generated
    Skill Routing drift.
  - acknowledgement suppresses only the acknowledged recommendation and does
    not hide unrelated required recommendations.
  - `quality` adapter resolve/bootstrap keeps existing `version: 1` adapters
    passing and returns safe empty defaults for new review fields.
  - adapter/gate inventory classifies findings as `structural_fact`,
    `contextual_recommendation`, `acknowledgement_gap`, `migration_gap`, or
    `brittle_hard_gate_smell`, and assigns `AUTO_EXISTING`, `AUTO_CANDIDATE`,
    or `NON_AUTOMATABLE` enforcement tier.
  - quality artifact validation fails when `Advisory` or `Delegated Review` is
    absent, when an empty advisory lacks inventory-backed evidence, or when a
    blocked delegated review lacks a concrete host/tool signal.
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/validate_adapters.py --repo-root .`
- `python3 scripts/validate_quality_artifact.py --repo-root .`
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`
- `python3 scripts/validate_cautilus_proof.py --repo-root .`
- `python3 scripts/check_changed_surfaces.py --repo-root .`
- targeted pytest:
  - `pytest -q tests/quality_gates/test_init_repo_inspect_policy.py`
  - `pytest -q tests/quality_gates/test_quality_bootstrap.py`
  - `pytest -q tests/quality_gates/test_quality_artifact.py`
  - `pytest -q tests/quality_gates/test_docs_and_misc.py`
- full closeout:
  - `python3 scripts/run_slice_closeout.py --repo-root .`
  - `./scripts/run-quality.sh`

## Premortem

- Likely wrong next move: implement a stronger premortem phrase detector and
  call #64 fixed. That would preserve the brittle-gate problem and miss the
  adapter-policy source issue.
- Likely wrong next move: make delegated review unconditional for every helper
  command, making `init-repo --json` style inspection expensive and noisy.
- Likely wrong next move: let subagent review produce prose-only findings that
  never enter the recommendation queue, recreating the original salience
  problem.
- Likely wrong next move: update `quality` but leave `init-repo` without a
  mandatory delegated review gate, even though the evidence came from
  init-repo normalization.

## First Implementation Slice

1. Add AGENTS wording for repo-mandated `init-repo` and `quality` delegated
   review authorization and host-block behavior.
2. Add `init-repo` adapter policy-source and recommendation queue support,
   keeping old adapters compatible.
3. Add `init-repo` delegated-review gate language and synthetic tests for
   policy-source-driven AGENTS recommendations.
4. Add `quality` adapter/gate review inventory and adapter fields.
5. Tighten `validate_quality_artifact.py` so quality reports include advisory
   and delegated-review status.
6. Refresh public skill dogfood and Cautilus proof for prompt-affecting
   surfaces.

## Canonical Artifact

`charness-artifacts/spec/issue-64-init-repo-quality-delegated-review.md`
