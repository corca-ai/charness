# Achieve Goal: Reviewer tier closeout and issue 275

Status: active
Created: 2026-06-01
Activation: `/goal @charness-artifacts/goals/2026-06-01-reviewer-tier-closeout-and-issue-275.md`

This file is the living goal scratchpad for the active local closeout run.

## Active Operating Frame

- Current slice: post-commit subagent critique findings are being applied
  locally; remote issue closure pending explicit push request.
- Next action: verify and commit the critique fixup carrier, then wait for the
  operator's push decision before claiming GitHub issue closure.
- Discuss before activation: #275 and #276 are bundled in one local carrier;
  the carrier includes close keywords but must not be pushed or claimed closed
  until the operator explicitly asks for push, after which GitHub issue state
  must be verified.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files, expected invariants, tests/proof, non-claims, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Deliver the four reviewer-tier waste-prevention improvements and resolve GitHub
issues #275 and #276 locally without losing the existing unreleased
reviewer-tier commits.

## Non-Goals

- Do not publish or release the accumulated commits unless the user separately
  asks for release/push.
- Do not close #275 until the fix is present in a pushed carrier and GitHub
  verifies the issue state.
- Do not close #276 until the fix is present in a pushed carrier and GitHub
  verifies the issue state.
- Do not make broad verification run before fresh-eye Act Before Ship findings
  are dispositioned.
- Do not turn adapter scaffold parity into exact field equality; intentional
  evidence-only defaults must remain expressible.

## Boundaries

- Existing local commits `45e4d51`, `9362288`, and `1180991` are in scope and
  must be preserved.
- Issue #275 is the tracked bug source of truth:
  <https://github.com/corca-ai/charness/issues/275>.
- Issue #276 was added by the operator during closeout and is also in scope:
  <https://github.com/corca-ai/charness/issues/276>.
- The four improvement requests are:
  1. add a fresh-eye blocker disposition checklist before broad verification,
  2. strengthen reviewer-tier direct-spawn scanning,
  3. add adapter scaffold/example/resolver parity for policy-bearing fields,
  4. make live-state handoff tests avoid exact backlog cardinality.
- #275 must cover installed plugin layout paths where public skills live under
  `skills/<id>/`, not only source-tree `skills/public/<id>/`.

## User Acceptance

- Run the final named verification commands from `## Final Verification`.
- Inspect #275 and see a closeout carrier with explicit `Close #275` semantics
  after push/release is requested.
- In an installed plugin layout, `parse_handoff_entries.py --with-issues` can
  find the configured issue backend and `draft_goal_from_chunk.py --help` no
  longer fails from a source-tree-only sibling import.
- A consequential achieve Before-phase goal cannot pass
  `check_goal_artifact.py --pursue-ready` unless a non-empty
  `Discuss before activation:` summary is visible.
- See that broad verification is gated by fresh-eye blocker disposition rather
  than by convention.

## Agent Verification Plan

### Low-Cost Checks

- Targeted unit tests for #275 import resolution and diagnostics.
- Targeted tests for fresh-eye blocker disposition checklist behavior.
- Targeted tests for reviewer-tier direct-spawn scanner.
- Targeted tests for adapter scaffold policy-bearing parity.
- `ruff check` and `py_compile` on changed Python files.

### High-Confidence Checks

- `python3 scripts/check_changed_surfaces.py --repo-root .` and all listed
  planned sync/verify commands for changed surfaces.
- `pytest -q` on affected targeted test modules after each slice.
- Final broad pytest after all fresh-eye Act Before Ship findings have a
  disposition and targeted regression.

### External Or Live Proof

- `gh issue view 275 --repo corca-ai/charness` before and after closeout.
- If a release/push is requested, verify GitHub issue #275 reaches `CLOSED`.
- If a release/push is requested, verify GitHub issue #276 reaches `CLOSED`.
- Installed-layout reproduction should be fixture-backed locally; a real
  consumer-repo proof is preferred only if the activation run has enough time
  and does not mutate that repo unexpectedly.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Fresh-eye blocker checklist | Prevent the just-observed broad-gate waste before more verification-heavy work | helper/gate tests and integration into closeout flow | done in prior local commits |
| 2 | Reviewer-tier direct-spawn scanner | Make new direct fresh-eye reviewer surfaces fail closed when they omit `high-leverage` tier application | scanner plus tests covering current direct surfaces | done in prior local commits |
| 3 | Adapter scaffold parity | Catch policy-bearing drift between examples, init output, and resolver-consumed fields | parity helper/tests with explicit intentional-difference allowances | done in prior local commits |
| 4 | Issue #275 installed-layout fix | Restore handoff issue source and goal draft imports in installed plugin layout | fixture proving `skills/<id>/` layout works and fallback diagnostics surface | done locally |
| 5 | Issue #276 activation discussion gate | Prevent structurally shaped achieve artifacts from hiding consequential activation decisions | pursue-readiness helper, docs, and regression tests | done locally |
| 6 | Verification, critique, retro, closeout | Prove the bundle without premature broad gates | final validators, broad pytest, critique artifact, retro, issue closeout draft | done locally; remote closure pending push |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns.
- Routing: `find-skills` recommended `issue` and `critique` for the #275/#276
  closeout boundary; `achieve` coordinated the goal artifact.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- Gather: n/a — GitHub issue source was read directly through `gh issue view`;
  no durable external gather asset was needed beyond the issue closeout artifact.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- Release: n/a — no version bump, release publication, or install manifest edit
  was part of this carrier.

## Slice Log

- Before-phase shaped on 2026-06-01. User asked to achieve all four proposed
  improvements and resolve #275. Execution is intentionally inert until the
  activation command is run.
- Activated by the continuing goal context. Preserved existing local reviewer
  tier commits `45e4d51`, `9362288`, and `1180991`.
- #275 implementation: handoff issue-source cross-skill lookup now supports
  source `skills/public/issue` and installed `skills/issue` layouts from the
  package/script root, prefers installed sibling layout when handoff itself is
  installed-layout, does not fall back to consumer repo `skills/issue`, and
  exposes issue-source diagnostics for pre-provider/provider failures.
- #275 implementation: `draft_goal_from_chunk.py --help` now resolves achieve
  goal artifact imports in installed `skills/achieve` layout as well as source
  `skills/public/achieve`.
- #276 implementation: `goal_artifact_discussion.py` detects consequential
  activation decisions in goal sections and `pursue_readiness` blocks activation
  until a non-empty `Discuss before activation:` summary is visible.
- Fresh-eye causal reviews ran for #275 and #276. Code critique found and the
  implementation fixed #275 consumer shadowing, installed/source preference,
  malformed provider payload diagnostics, #276 empty summary capture, broad
  combined-scope triggers, and proof non-claim over-breadth.
- Final broad verification passed: `1973 passed, 4 skipped in 270.06s`.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- `charness-artifacts/retro/2026-06-01-reviewer-tier-sibling-scan-waste.md`
- `charness-artifacts/debug/2026-06-01-reviewer-tier-sibling-scan.md`
- `charness-artifacts/critique/2026-06-01-reviewer-tier-sibling-scan-critique.md`
- GitHub issue #275: <https://github.com/corca-ai/charness/issues/275>
- GitHub issue #276: <https://github.com/corca-ai/charness/issues/276>
- Existing local commits: `45e4d51`, `9362288`, `1180991`

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Mode: user asked "어치브 해주세요"; chosen value is shaped goal artifact now,
  activation-required execution next. Rejected auto-execution because `achieve`
  explicitly keeps Before-phase artifacts inert until `/goal`.
- Scope: bundle all four proposed improvements plus #275. Rejected splitting
  #275 into a separate goal because the issue and the improvements both touch
  handoff/skill closeout reliability and share final verification cost.
- Release/push: out of scope until explicitly requested. Rejected implicit
  publish because current branch is already ahead of `origin/main` and release
  guardrails require explicit confirmation.
- Issue classification: #275 is bug-class. Rejected feature/deferred-work
  classification because observed installed-layout behavior diverges from the
  expected handoff issue-source contract.
- Issue classification: #276 is bug-class. Rejected treating it as a docs-only
  feature because `check_goal_artifact.py --pursue-ready` could report an
  activation artifact ready while operator-facing consequential decisions were
  unsurfaced.
- Scope update: user asked to include issue #276. Chosen value is a single local
  carrier for #275 and #276 because both affect pickup/activation trust and
  share final verification. Rejected pushing/closing because the goal boundary
  still requires an explicit push request before remote closure.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Not yet run. First active slice should run a bounded plan critique before
  implementation if the changed-surface map grows beyond the planned scripts and
  tests.
- Known risk folded in: broad verification must wait until fresh-eye blockers
  are dispositioned.
- Known risk folded in: #275 has an installed-layout path dimension, so tests
  must include `skills/<id>/`, not only source-tree `skills/public/<id>/`.
- Fresh-eye #275 Act Before Ship findings folded in: no consumer repo fallback,
  installed-layout preference over stale source layout, malformed provider
  payload diagnostics, stronger argv proof, and provider failure diagnostics.
- Fresh-eye #276 Act Before Ship findings folded in: empty
  `Discuss before activation:` labels do not count as summaries, combined issue
  scope triggers discussion, and proof non-claim detection is scoped to proof or
  verification context.
- Counterweight over-worry: more installed/source layout permutations and broad
  regex expansion were rejected as overfitting after the reported failures and
  same-class critique findings were covered.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- Same-class support-skill topology risk from causal review: broader resolver
  unification may be useful later, but was deferred because #275's acceptance
  boundary is handoff-to-issue and handoff-to-achieve.

## Final Verification

- GitHub source-of-truth before closeout: #275 OPEN and #276 OPEN on
  2026-06-01.
- Sync: `python3 scripts/sync_root_plugin_manifests.py --repo-root .` passed
  after final source and metadata edits.
- Packaging: `python3 scripts/validate_packaging.py --repo-root .` passed.
- Packaging committed mirror:
  `python3 scripts/validate_packaging_committed.py --repo-root .` passed.
- Docs: `python3 scripts/check_doc_links.py --repo-root .`,
  `python3 scripts/check_command_docs.py --repo-root .`,
  `./scripts/check-markdown.sh`, and `./scripts/check-secrets.sh` passed.
- Prompt proof policy:
  `python3 scripts/validate_cautilus_proof.py --repo-root .` passed with
  deterministic validation owning prompt-affecting paths.
- Skill/package gates:
  `python3 scripts/validate_skills.py --repo-root .`,
  `python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py`,
  `python3 scripts/check_skill_ownership_overlap.py --repo-root .`,
  `python3 scripts/validate_public_skill_validation.py --repo-root .`,
  `python3 scripts/validate_public_skill_dogfood.py --repo-root .`, and
  `python3 scripts/validate_critique_artifacts.py --repo-root . --all` passed.
- Python gates: `ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts`,
  `python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing`,
  and `python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support`
  passed. Length gate reported advisory near-limit warnings only.
- Focused tests:
  `pytest -q tests/test_handoff_chunker_parse.py tests/test_handoff_chunker_issue_source.py tests/quality_gates/test_goal_artifact_lib.py tests/quality_gates/test_achieve_before_activation.py tests/quality_gates/test_goal_artifact_producers.py tests/quality_gates/test_goal_head_freshness.py tests/quality_gates/test_repo_copy_invariants.py`
  passed (`116 passed` on the focused rerun before final detector hardening;
  final focused achieve rerun passed `63 passed`).
- Broad tests:
  `pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py`
  passed before post-commit critique: `1973 passed, 4 skipped in 270.06s`;
  passed after post-commit critique fixes:
  `1980 passed, 4 skipped in 271.87s`.
- Critique: `charness-artifacts/critique/2026-06-01-reviewer-tier-275-276-resolution.md`.
- Retro: `charness-artifacts/retro/2026-06-01-reviewer-tier-275-276-closeout.md`.
- Issue closeout carrier:
  `charness-artifacts/issue/2026-06-01-reviewer-tier-275-276-closeout.md`.
- Non-claim: GitHub issue closure has not been verified because the carrier has
  not been pushed by explicit operator request.
- Post-commit subagent critique:
  `charness-artifacts/critique/2026-06-01-reviewer-tier-275-276-postcommit-subagent-critique.md`.
  Fresh-eye reviewers found four Act Before Ship concerns; the local fixup
  tightened #276 heading/Non-Goals/Slice Log readiness semantics, preserved
  #275 issue-source diagnostics through `propose_merges.py`, bounded installed
  issue lookup to the current package root, and aligned installed achieve lookup
  preference.
- Post-critique focused tests:
  `pytest -q tests/quality_gates/test_goal_artifact_lib.py tests/quality_gates/test_achieve_before_activation.py tests/test_handoff_chunker_issue_source.py tests/test_handoff_chunker_parse.py tests/test_handoff_chunker_merge_proposer.py`
  passed: `115 passed in 4.07s`.

## User Verification Instructions

- Inspect the local closeout carrier:
  `charness-artifacts/issue/2026-06-01-reviewer-tier-275-276-closeout.md`.
- When ready to publish, push the carrier commit and verify #275 and #276 reach
  `CLOSED` on GitHub.

## Auto-Retro

- Retro artifact:
  `charness-artifacts/retro/2026-06-01-reviewer-tier-275-276-closeout.md`.
- Disposition review: `charness-artifacts/critique/2026-06-01-reviewer-tier-275-276-resolution.md`.
- Retro dispositions:
  - applied: plugin export sync rerun after attention-state metadata edits,
    recorded as final verification evidence.
  - applied: #276 discussion-readiness helper, docs, and tests prevent the
    structural-readiness/operator-readiness miss from recurring in achieve.
