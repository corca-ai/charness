# Critique Review
Date: 2026-07-23

## Decision Under Review

Publish `charness` `2.4.3` (patch bump from `2.4.2`, tag `v2.4.3`). Release
content is exactly three commits since the `v2.4.2` tag (`5fb4b7a4`):
`cce52540` (#451 mutation-score test-coverage fix, test-only), `531ec685`
(#452 create-cli "Named Option Semantics" doc addition), and `cfce9e3e`
(#449 resolution brief recording a declined CI-side release-observer
feature, no implementation).

## Failure Angles

- Atul Gawande (checklist/operational): is any release-time step missing —
  mirror sync, generated-doc staleness, fresh-checkout probes, changelog?
- Barbara Minto (structure/communication): will an operator reading only
  the release notes understand what shipped, without being misled about
  #449?
- Jef Raskin (humane interface): is the only operator-facing surface change
  (#452's doc) internally consistent and non-prescriptive?

## Counterweight Pass

- Act Before Ship: none.
- Bundle Anyway: (1) supply a curated `--notes-file` instead of GitHub's
  default `--generate-notes` raw commit-title compilation, since three
  reviewers independently found the raw-title path insufficient — it would
  not carry the "#449 not implemented, can revisit" caveat, nor the
  patch-vs-minor rationale for #452 that the version-policy Guardrail
  requires stating when debatable; (2) refresh `docs/handoff.md`'s stale
  "Next Session" line still framing #449 as an "open item to pursue."
- Over-Worry: "too thin a release to cut" (no documented minimum-content
  threshold, and this repo's own v2.4.0->v2.4.1->v2.4.2 history already
  ships small, unrelated-commit patch releases in rapid succession);
  "bundling a no-op record commit with two real fixes dilutes the release"
  (CLAUDE.md already treats `charness-artifacts/` changes as normal repo
  state to commit with supporting work, and v2.4.1 already bundled two
  unrelated fixes under one tag without incident); #451's patch
  classification (textbook "validation or packaging repair," not actually
  debatable).
- Valid but Defer: none identified beyond what's bundled above.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: skills/public/release/references/version-policy.md | action: fix | note: #452's patch-vs-minor classification is genuinely debatable per the policy's own Guardrail ("if the bump level is debatable, say why"); state the rationale in the curated release notes
- F2 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/issue/2026-07-23-issue-449-brief.md | action: fix | note: echo the brief's "not a technical blocker, revisit if judgment changes" caveat in the public release notes, not only the internal artifact, so the declined-feature record does not read as more final than intended
- F3 | bin: bundle-anyway | evidence: strong | ref: docs/handoff.md:43-45 | action: fix | note: "Next Session" step 3 still frames #449 as "the open release-proof design item" to pursue, stale against the now-declined decision; refresh as part of this release's post-publish baton reconcile
- F4 | bin: over-worry | evidence: weak | ref: n/a | action: defer | note: "release is too thin / should batch more before cutting" — no documented minimum-content threshold, and existing rapid small-patch precedent (v2.4.0-v2.4.2) contradicts the concern
- F5 | bin: over-worry | evidence: weak | ref: n/a | action: defer | note: "bundling a no-op #449 record commit with real fixes dilutes the release" — repo precedent (v2.4.1 bundled two unrelated fixes) and CLAUDE.md's own artifact-inclusion norm both contradict this
- F6 | bin: over-worry | evidence: weak | ref: skills/public/create-cli/SKILL.md:50,129 vs skills/public/create-cli/references/command-conventions.md:23-51 | action: document | note: SKILL.md says "flag-ordering independence" while the reference doc it points to says "named option"; self-resolves via `quality-gates.md`'s correctly-worded pointer and is not release-blocking, but noted for a future create-cli slice

## Reviewer Tier Evidence

- Requested tier: high-leverage (angles) / high-leverage (counterweight).
- Requested spawn fields: session-model inheritance (Claude Code host; the
  repo's Codex-only override fields do not apply on this host).
- Host exposure state: host-defaulted
- Application state: host-confirmed: bounded-reviewer subagent spawned via
  the Agent tool with Read/Grep/Glob-only envelope for all four reviewers.
  Two reviewers (Gawande, Minto) explicitly reported their envelope had no
  Bash and could not execute `git show`/probe commands directly; they
  substituted worktree file reads and named the gap for the parent. The
  parent (this session) independently ran the three declared fresh-checkout
  probes after those reports: `./charness --help` (exit 0), `./charness
  goal check --help` (exit 0), and `python3 scripts/doctor.py --repo-root .
  --json --skip-release-probe` (exit 0, `doctor_status: ok`).

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

n/a (no adapter `packet_sections` declared; reviewers were pointed at the
live git history/worktree directly).

## Release Scope

- Version: `2.4.2` -> `2.4.3` (patch)
- Tag: `v2.4.3`
- One line for consumers: a mutation-score CI test-coverage repair, a
  `create-cli` skill documentation clarification, and a recorded decision
  not to build a CI-side release observer — no functional or install-surface
  change.

## Surface-Lock Inventory

- Generated artifacts: none regenerated by this range (no CLI/parser code
  changed; `docs/generated/cli-reference.md` confirmed not stale).
- Consumer-visible behavior: none (test-only fix; doc-only skill guidance
  addition; a non-implementation record).
- Documentation surfaces: `skills/public/create-cli/references/command-conventions.md`,
  `quality-gates.md`, and `SKILL.md` (plus their checked-in plugin mirror);
  `docs/handoff.md` (post-publish baton reconcile, F3).
- Adapter/integration manifests: none touched.

## Operator Action Required

- F1/F2/F3 above: bundle a curated release-notes file and refresh
  `docs/handoff.md` before/at publish; no other Act Before Ship item exists.

## Upgrade Path

No consumer-visible behavior changed; `charness update` picks up the new
skill-doc content with no migration step.

## Boundary Ownership

- Producer: the three merged commits (#451, #452, #449 brief).
- Consumer: the release publish helper and its generated release notes /
  handoff baton, and any operator reading them.
- Owning surface: the release process itself (notes curation, baton
  reconcile), not the underlying commits (already critiqued individually).
- Verdict: owned-correctly

## Deliberately Not Doing

- Not reclassifying #452 as `minor` — patch remains the honest call (a
  doc clarification, not a new capability); the rationale is stated in the
  release notes (F1) instead.
- Not rewording `SKILL.md`'s "flag-ordering" back to "named-option" (F6) —
  that would retrip the `mode_option_pressure_terms` skill-ergonomics gate;
  left as a documented, non-blocking terminology note for a future slice.
