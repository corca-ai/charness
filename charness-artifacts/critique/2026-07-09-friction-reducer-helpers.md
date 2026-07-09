# Friction Reducer Helpers Critique
Date: 2026-07-09
Fresh-eye satisfaction: parent-delegated

## Decision Under Review

Add read-only helper surfaces that reduce late prompt-mutation and closeout
friction without adding new blocking floors: scenario clean-proof preflight,
post-capture blinding scan, goal closeout normalizer, duplicate-ratchet triage
draft, shared bundle JSONL reader, plugin sync change summary, and a blind
workspace preparation helper for capture runs that need a git checkout.

## Failure Angles

- Advisory drift into gate semantics: helpers could be misread as new hard
  closeout requirements, increasing the same closeout-contract weight they are
  meant to reduce.
- False clean blinding: scanners could miss common git invocation forms and let
  a tainted capture be claimed as clean.
- Duplicate-helper churn: new convenience scripts could introduce fresh
  duplicate-ratchet pressure.
- Generated-surface drift: root script and skill helper changes must sync to
  the checked-in plugin mirror.
- Ambient git environment poisoning: a blind-workspace helper that runs git
  under inherited `GIT_DIR`, `GIT_WORK_TREE`, or `GIT_INDEX_FILE` can mutate or
  inspect the wrong repo and silently invalidate the blinding claim.

## Counterweight Pass

- Floor-Addition Restraint: keep as advisory/read-only, not a blocking floor.
  The new `check_prompt_mutation_blinding.py` name matches helper convention but
  does not raise closeout-contract weight: it exits 0 and reports taint JSON for
  the operator to interpret. The concern is better absorbed by prompt-mutation
  policy plus pre/post-capture helper commands than by a new deterministic gate.
- The policy doc names both blinding helpers as advisory/read-only and says a
  taint finding means no clean blinding proof is claimed, not that a repo gate
  blocks.
- Public-skill dogfood decision: `suggest_public_skill_dogfood.py` for
  `achieve` and `quality` returned HITL-recommended consumer prompts, but this
  slice adds helper scripts only. It does not change either skill's trigger
  description, required artifact, or user-facing consumer contract, so
  `docs/public-skill-dogfood.json` is intentionally unchanged for this slice.
- A fresh-eye reviewer found an option-prefixed git invocation blind spot; tests
  and patterns now cover `git -C . log`, `git --no-pager show`, and
  `git -c color.ui=never diff`.
- The bundle JSONL reader is shared between the survival scorer and blinding
  scanner, removing an extractable duplicate family instead of classifying it.
- Plugin mirrors were regenerated with `sync_root_plugin_manifests.py`; the
  sync output now reports a digest-based change summary.
- Blind workspace preparation remains advisory. It exports only the snapshot
  tree into a standalone one-commit repo, refuses metadata inside the
  run-visible workspace, and does not run captures or block commits.
- Fresh-eye review found the ambient-git poisoning path before commit. Git
  plumbing now scrubs ambient `GIT_*` routing/config variables centrally while
  preserving explicit identity and `GIT_INDEX_FILE` for the mutation builder's
  temporary index.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `scripts/check_prompt_mutation_blinding.py` | action: fix | note: Fresh-eye review found global-option git probes were missed; scanners now share a `GIT_PREFIX` and regression tests cover the examples.
- F2 | bin: bundle-anyway | evidence: strong | ref: `scripts/prompt_mutation_bundle_lib.py` | action: fix | note: Shared bundle JSONL/tool-input extraction avoids duplicating scorer logic in the blinding scanner.
- F3 | bin: bundle-anyway | evidence: strong | ref: `docs/prompt-mutation-policy.md` | action: document | note: New blinding helpers are documented as advisory/read-only, preserving floor-addition restraint.
- F4 | bin: act-before-ship | evidence: strong | ref: `plugins/charness/scripts/check_prompt_mutation_blinding.py` | action: fix | note: Plugin mirror was regenerated after root script and skill helper changes.
- F5 | bin: act-before-ship | evidence: strong | ref: `scripts/prepare_prompt_mutation_blind_workspace.py` | action: fix | note: Fresh-eye review found ambient `GIT_DIR`/`GIT_WORK_TREE` poisoning could redirect workspace git operations; `scrub_git_env` now protects helper and shared prompt-mutant git plumbing.
- F6 | bin: bundle-anyway | evidence: strong | ref: `tests/test_prompt_mutation_blind_workspace.py` | action: fix | note: Regression test poisons `GIT_DIR`/`GIT_WORK_TREE` with a different repo and proves source, poison, and blind workspace histories stay separated.

## Reviewer Tier Evidence

- Requested tier: bounded friction-helper slice review.
- Requested spawn fields: agent_type=explorer, model=inherited,
  reasoning_effort=medium; service_tier inherited.
- Host exposure state: requested_fields_sent
- Application state: follow-up re-review returned `PASS` after deterministic
  regression tests and direct reproducer probes covered the reported blind spot.
- Second reviewer pass: read-only reviewer `Linnaeus` initially returned
  `FAIL` for ambient git environment poisoning, then returned `PASS` after the
  git scrubber moved into shared prompt-mutant plumbing and the cross-repo
  poisoning regression test passed.

## Fresh-Eye Satisfaction

parent-delegated — bounded read-only reviewer completed through
`multi_agent_v1.spawn_agent`; its initial `FAIL` finding was fixed before
commit and the same reviewer returned `PASS` on the narrow fix.

## Boundary Ownership

- Producer: helper CLIs produce advisory JSON and normalization/draft output.
- Consumer: operators and future prompt-mutation goals consume the helper
  output before capture, after capture, or before closeout artifact validation.
- Owning surface: prompt-mutation policy, repo scripts, achieve/quality skill
  helper scripts, and plugin mirror exports.
- Verdict: owned-correctly
