# Critique Review
Date: 2026-07-25

## Decision Under Review

Publish `charness` `2.5.0` (minor bump from `2.4.3`, tag `v2.5.0`). Release
content is three commits since the `v2.4.3` tag: `2116904c` (irreversible-boundary
terminal-trust fixes), `106f6d2f` (stale-proof and duplicated-prose deletions),
`aea6faea` (handoff baton), plus the pre-publish corrections this critique forced.

## Failure Angles

- Michael Jackson (problem framing): is `minor` the honest level when the shipped
  workflow template *removes* behavior a consumer may depend on?
- Atul Gawande (checklist/operational): what does an upgrading consumer actually
  receive, and what must they do?
- Barbara Minto (structure/communication): what would raw generated release notes
  omit that an operator must not miss?
- Jef Raskin (humane interface): is the delivery path a consumer is told to use
  the one that actually works?

## Counterweight Pass

- **Act Before Ship (both blockers, both fixed before publish):**
  1. The shipped reference told consumers to re-run
     `propose_mutation_testing.py --execute` to re-render the workflow. That is
     false and self-contradicted 20 lines later. Verified against
     `propose_mutation_testing.py:154-155` (refuses to overwrite an existing
     `workflow_path`) and `:183` (`--execute` acts only when status is `missing`).
     **There is no re-render path at all.** Shipping a release whose entire
     consumer value is a template change, behind a documented-but-nonexistent
     delivery path, is exactly the "wrong answer escapes to an operator" case.
     Fixed in the reference, its plugin mirror, and the misleading code comment.
  2. "Runtime-unproven until the next scheduled cycle" was materially optimistic.
     With no open marked issue, the recovery step iterates an empty set and emits
     nothing; the open path needs a failure. Corrected everywhere to "until a
     failure files a marked issue AND a later scheduled green runs."
  3. The boundary critique's own non-claim asserted `--execute` rewrites
     `workflow_path`. Falsified by this review and corrected in place.
- **Bundle Anyway:** a curated `--notes-file` rather than `--generate-notes`,
  since three commit titles convey none of the migration reality, the removal, the
  fixed label name, the `marker_token` orphaning, or the bump rationale.
- **Over-Worry:** "the template removal makes this a major." Rejected against
  `version-policy.md:26-31`: no major criterion is met. The install *surface*
  (propose script, adapter block, `workflow_path`) is unchanged, and because an
  installed workflow is never re-rendered, the removal reaches **zero existing
  consumers** — only fresh installs, who never had the old behavior. Also rejected:
  inflating the bump to signal significance; that is a communication problem, and
  solving it with a semver lie is worse.
- **Valid but Defer:** the plugin-copy fresh-install rendering path is untested
  (`test_a7` asserts mirror existence, not that the plugin copy resolves its
  template); the `v2.4.3` baton reconcile obligation standing open in the release
  record; `charness-artifacts/quality/latest.md` describing a pre-2.5.0 tree.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/references/mutation-testing.md:145-150 | action: fix | note: shipped reference instructed consumers to re-run `--execute` to re-render the workflow; the script refuses to overwrite an existing file and only acts when the block is `missing`, so the instruction silently no-ops — corrected in source, plugin mirror, and the code comment at propose_mutation_testing.py:157-160
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-07-25-irreversible-boundary-terminal-trust-critique.md:118 | action: fix | note: that critique's non-claim asserted `--execute` rewrites `workflow_path`; falsified against the script and corrected in place rather than left as a durable false record
- F3 | bin: act-before-ship | evidence: strong | ref: docs/handoff.md:18-24 | action: fix | note: "unproven until the next scheduled cycle" implied the next cycle resolves the gap; with zero open marked issues the recovery step observes nothing, so the honest condition is a failure followed by a later green
- F4 | bin: bundle-anyway | evidence: strong | ref: skills/public/release/references/version-policy.md:33-36 | action: fix | note: the policy requires stating why when a bump level is debatable; this one is, so the notes must carry "minor not major because no existing install is re-rendered; minor not patch because a new label surface and advisory ship"
- F5 | bin: bundle-anyway | evidence: strong | ref: scripts/quality_policy_defaults.py:226-231 | action: document | note: the comma-in-label refusal lands in `errors`, so a consumer whose adapter carries a comma'd label sees quality adapter validation newly fail — the release's only hard forced migration, must be named in the notes
- F6 | bin: bundle-anyway | evidence: strong | ref: skills/public/issue/scripts/issue_verify_closeout_body.py:321-344 | action: document | note: anchoring plus the close-with-comment composition means closeout bodies that passed on 2.4.3 can be refused on 2.5.0 — intended, but upgrade-visible and note-worthy
- F7 | bin: valid-but-defer | evidence: strong | ref: skills/public/quality/scripts/propose_mutation_testing.py:35 | action: defer | note: the plugin export hardcodes a source-repo-relative template path and `test_a7` only asserts the mirror files exist; since fresh install is now the ONLY delivery path for this release's headline change, that path deserves a real exercise in a throwaway repo
- F8 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/release/latest.md:179-182 | action: defer | note: the v2.4.3 `RECONCILE REQUIRED` obligation is still open and was neither discharged nor failed loudly; make sure the 2.5.0 baton reconcile lands an explicit version claim rather than inheriting the pattern
- F9 | bin: over-worry | evidence: contested | ref: skills/public/release/references/version-policy.md:26-31 | action: defer | note: "template behavior removal forces a major" — no major criterion is met and the removal reaches no existing install; `minor` errs safe, and `patch` was the only serious competitor
- F10 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/quality/latest.md:2 | action: defer | note: the canonical quality pointer is dated 2026-07-22 and describes a pre-2.5.0 tree; not a publish blocker since the release helper runs its own quality, but stale as a pickup pointer

## Reviewer Tier Evidence

- Requested tier: high-leverage (release decision review).
- Requested spawn fields: session-model inheritance (Claude Code host; the repo's
  Codex-only model/effort override does not apply on this host).
- Host exposure state: host-defaulted
- Application state: host-confirmed — a `bounded-reviewer` subagent spawned via the
  Agent tool with a Read/Grep/Glob-only envelope. It reported the envelope bound and
  named two evidence gaps it could not close without Bash; the parent ran the first
  (`git show v2.4.3:skills/public/quality/scripts/templates/mutation-tests.yml`,
  confirming the auto-close was in the *released* template at `:258`/`:284`, so the
  removal is real for consumers) and recorded the second (a live plugin-copy fresh
  install) as F7 rather than claiming it.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

n/a (no adapter `packet_sections` declared; the reviewer was pointed at the live
worktree, the two slice critiques, and the `v2.4.3` tag).

## Release Scope

- Version: `2.4.3` -> `2.5.0` (minor)
- Tag: `v2.5.0`
- One line for consumers: the mutation-testing workflow template stops closing
  GitHub issues from its own green and records a recovery candidate instead; the
  issue-closeout disposition floor stops accepting a status's own negation; runtime
  budgets report when they have gone slack.

## Surface-Lock Inventory

- Generated artifacts: plugin mirrors synced for every touched skill surface
  (`sync_root_plugin_manifests.py`), verified by `check_staged_mirror_drift` at
  both commits.
- Consumer-visible behavior: mutation workflow template (fresh installs only),
  `auto_issue.label` comma refusal (all consumers), anchored HOTL floor plus
  `close-with-comment` composition (all consumers), budget slack advisory.
- Documentation surfaces: `mutation-testing.md`, `automation-promotion.md`,
  `create-skill/SKILL.md` + `portable-authoring.md`, two `docs/conventions/` files.
- Adapter/integration manifests: `.agents/quality-adapter.yaml` runtime budgets
  (repo-internal, not shipped).

## Boundary Ownership

- Producer: `release` owns the publish decision; `quality` owns the mutation
  template and its reference; `issue` owns the closeout floors.
- Consumer: repos installing or upgrading the charness plugin.
- Verdict: owned-correctly

## Operator Action Required

- Publish with a curated notes file carrying F1's migration reality, the removal
  stated as a removal, the fixed `mutation-recovered-candidate` label name, the
  `marker_token` orphaning warning, F5's comma-label break, F6's closeout-floor
  tightening, F4's bump rationale, and the corrected runtime non-claim.

## Non-Claims

- Release visibility is not behavior verification. An HTTPS 200 on the release tag
  proves publication only; it says nothing about whether any of this release's
  behavior works.
- The unauthenticated HTTPS observer is **credential-distinct, not
  machine-distinct** — same host and process as the publisher.
- No `actions/github-script` line in this release has ever executed.
- No consumer-repo install was exercised; the fresh-install rendering path from the
  plugin copy is untested (F7).
- The word-for-word deletion diff of `create-skill/SKILL.md` carries only a partial
  distinct-observer signature; that reviewer could not read the base blob.
