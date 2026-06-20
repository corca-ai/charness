# WS-3b Critique — Tier-2 verb-vocabulary deleak (taxonomy token + discussion seam + heading)

Date: 2026-06-20
Slice: WS-3b of `charness-artifacts/goals/2026-06-20-north-star-phase4-boundary-non-terminality.md`
Concept lock: `charness-artifacts/spec/2026-06-20-phase4-boundary-non-terminality-concept.md` §4b (F5 straight-rename, F6 Option A)
Scope: governing-surface edits (achieve `lifecycle.md`/`goal-artifact.md`/`adapter-contract.md`,
`docs/prescribed-skill-closeout-contract.md`) + an `achieve` behavior change (the
discussion-gate adapter seam) + the public-skill validation review for `achieve`.

## What changed

The deepest WS-3 slice — the consumer-VERB vocabulary deleak:

- **(b-i) Taxonomy token rename, straight (NO grandfathered alias):**
  `applied-restarted` → neutral **`instance-synced`** across the taxonomy
  (`lifecycle.md:809,813`), the closeout-delegation example/vocab
  (`goal-artifact.md:266,277`), the gate docstring + `CLOSEOUT_STATE_LEVELS`
  constant (`goal_artifact_closeout_delegation.py:21,40`), the governing contract
  doc (`docs/prescribed-skill-closeout-contract.md:227`), and the test fixture.
  F5-safe because the gate `_item_resolved` is **token-agnostic** (resolves on
  `verified`/`skipped:`/`issue #N`, never the literal) and the drift test asserts
  **membership** — an existing consumer artifact carrying `applied-restarted —
  verified:` still resolves on `verified`, so no alias is needed.
- **(b-ii) Discussion-gate deploy vocabulary made adapter-provided (Option A):**
  `goal_artifact_discussion.py` now builds its triggers via `build_triggers(deploy_vocab)`
  from charness-neutral concepts (`prod`/`live proof`/`irreversible`/...) + a
  deploy-verb vocabulary whose **default is the byte-preserving English set**
  (`apply/restart`, `restart`, `deploy`). A consumer's achieve adapter
  (`discussion_deploy_vocab`) **replaces** the English default; absent adapter →
  byte-identical behavior. Live end-to-end: `check_goal_artifact.py --pursue-ready`
  resolves `discussion_deploy_vocab` (graceful → `[]` → English default) and
  threads it through `pursue_readiness` → `discussion_readiness`.
- **(b-iii) Heading rename:** `Post-Apply Checkpoint Classification` →
  `Post-Checkpoint Commit Classification` (`lifecycle.md:278,540`; the pinned
  `test_workflow_safety_docs.py:14` + the test fn name updated).

## Bounded fresh-eye critique — PASS (folded)

A bounded fresh-eye reviewer (distinct agent context, read-only) verified every
angle **against the actual staged code, re-deriving every claim** (its own greps,
in-process regex byte-equality checks, and **live `check_goal_artifact.py
--pursue-ready` CLI runs in an isolated repo with adapter present / absent /
invalid**), not the slice author's summary. **Verdict: PASS, no blockers.**

CONFIRMED: (A1) the rename is complete (0 hits of `applied-restarted` /
`Post-Apply Checkpoint` across `skills/ scripts/ tests/ docs/ plugins/`), and the
F5 straight-rename is genuinely safe — the reviewer drove a legacy
`applied-restarted — verified:` artifact through `apply_closeout_delegation()` →
`ok: True` (resolves on `verified`, the token is never read); the drift test
passes (constant ↔ lifecycle.md in sync). (A2, critical) `build_triggers()` with
the default produces regexes **byte-identical** to the original hardcoded
patterns (`re.escape` is a no-op on the English verbs). (A3) the seam is live:
a custom `discussion_deploy_vocab` **replaces** the English default and the
neutral concepts always fire; resolution is graceful (missing/invalid adapter →
English default, no exception). (A4) the new adapter field is optional + validated
(non-list errors cleanly). (A5) 648 achieve/goal/adapter tests pass; no existing
test changed for a non-rename reason. (A6) the `plugins/` mirror is sha256-identical
to source; `instance-synced` is free of apply/restart/deploy and non-colliding.
(A7) the seeded tests are non-tautological (default-preserves / custom-replaces /
field-resolves).

Over-worries dismissed (NOT folded): the illustrative English-default verbs in
`_DEFAULT_DEPLOY_VOCAB`, the lifecycle prose ("live apply, restart, deployment
smoke"), and the `instance-synced` description ("applied / restarted / redeployed")
— Option A REQUIRES keeping the English default, and the descriptive verbs are
explicitly in-spec; only the taxonomy *token* had to be neutral, and it is. No
grandfathered alias — correctly omitted (F5; the gate is token-agnostic).

## Public-skill validation decision (cautilus `next_action: none`, ask-before-run)

Cautilus `run_mode: ask`, `next_action: none` — no live evaluator run; deterministic
validation + this recorded fresh-eye review own the closeout. `achieve` is the
changed public skill; its consumer contract is unchanged — the token rename is
gate-agnostic (no behavior change) and the discussion seam preserves behavior by
default (a repo without `discussion_deploy_vocab` is byte-identical). `achieve`
dogfood case refreshed. Closeout proceeds with `--ack-cautilus-skill-review`.

## Non-claims

- Portability deleak, not boundary-hardening (charness owns no prod-apply boundary).
- The b-ii seam is proven via unit + the live `--pursue-ready` CLI on a seeded
  `/tmp` adapter; no live goal was activated through `/goal` with a custom vocab
  this run (the deterministic CLI proof is the proof level).
