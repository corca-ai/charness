# v2.11.2 release critique
Date: 2026-07-27

## Decision Under Review

Publishing `charness` 2.11.1 -> 2.11.2 (tag `v2.11.2`) through the repo-owned
publish helper. The delta is one commit, `cf43b62b`: the chunked-routing
auto-draft now marks stale citations (`MISSING` / `CLOSED` / `UNRESOLVED`) and
keeps `missing_paths` entries out of the Boundaries `In scope:` line, plus the
owning contract doc, the vendored reference, and tests. Lock-in event is the tag
push and GitHub release record.

**Release scope and bump rationale (version-policy.md:33-36).** The bump is
debatable, so it is argued rather than defaulted. Against `minor`: the change
adds a bullet and three inline markers that did not exist in a generated
operator-facing artifact. Against that reading: `version-policy.md:22` scopes
`minor` to behavior users can *adopt*, and nothing here is adoptable — no new
command, flag, skill, or invocation. The facts rendered were already computed,
already carried in the ranker packet, already documented. `draft_goal_from_chunk.py`
is byte-identical in args, JSON keys, exit codes, and gate. The change corrects
a *false* assertion — `In scope:` listed a path the checker had positively found
gone — which is `version-policy.md:13` "runtime corrections that preserve the
same public shape". **Patch.** The only shape change is additive bullets and
suffixes in newly drafted artifacts; no existing artifact or interface is
affected.

## Failure Angles

- **Gawande (checklist/operational).** Bump honesty, release-order gaps against
  the adapter, whether the changed surfaces actually ship via `charness update`,
  and whether an operator's in-flight goal artifact could change under them.
- **Minto (structure/communication).** Whether the release record and notes are
  legible to an operator who did not follow the thread, and whether the hardest
  thing here — a *negative* capability, that unmarked does not mean verified —
  survives into the channel operators actually read when upgrading.

## Counterweight Pass

The counterweight rejected four of ten concerns and overturned one angle's
factual base. The Minto angle argued the docs uniformly over-disclaim because
"the path check runs on every invocation"; the counterweight found
`_repo_root_for_live_filters` (`parse_handoff_entries.py:66-75`) returns `None`
for an explicit handoff path outside `cwd/docs/handoff.md`, so the path check
genuinely does not always run and "clean OR not-checked" is literally true for
paths too. I verified that function directly. The existing doc wording stands,
and re-opening it would have re-litigated a counterweight ruling the F9 critique
already settled.

It also split the R1/R8 pair decisively: a backticked version in the baton is
the sanctioned answer in both owning contracts, so recording "intentionally no
version claim" would pick the documented-worse branch and re-arm the same ask
every release.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_helpers.py:164 | action: fix | note: the helper defaults to `--generate-notes`; with a one-commit delta the operator-facing notes collapse to the commit subject — a bare positive-capability claim for a feature whose premise is asymmetric checking. Publishing with `--notes-file charness-artifacts/release/v2.11.2-notes.md`, which carries the complement sentence
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_preflight.py:71-95 | action: fix | note: the critique gate accepts any tracked critique markdown, so it cannot tell the F9 code critique from a release critique; that artifact self-disclaims post-fix coverage. This artifact is the one passed to `--critique-artifact`, and it is committed before publish so the tracked-file preflight passes
- F3 | bin: bundle-anyway | evidence: strong | ref: docs/handoff.md:22-25 | action: fix | note: the baton carried no version string, so the post-publish reconcile would emit `no_version_claim` — an ask, not a pass. Added a backticked `2.11.2`, which state-selection.md:41-45 blesses as an address rather than a regenerable claim
- F4 | bin: bundle-anyway | evidence: strong | ref: docs/handoff-chunked-routing.md:340-349 | action: fix | note: the third Boundaries branch (every cited path missing) was new in this commit and tested but documented nowhere; same class as the F9 critique's own F1. Documented in the owning contract; the vendored reference stays terser deliberately
- F5 | bin: bundle-anyway | evidence: moderate | ref: skills/public/release/references/version-policy.md:33-36 | action: document | note: the bump is debatable and the helper has no rationale field, so `--part patch` would be a silent default; the argument is recorded in Decision Under Review above. Rejected the proposed `--bump-rationale` flag — the policy says "say why", not "add a CLI surface"
- F6 | bin: valid-but-defer | evidence: moderate | ref: docs/public-skill-dogfood.json:311 | action: document | note: the analogous prior auto-draft shape change (#381) got a dogfood ledger entry and this one does not; the validator does not require per-change entries and the consumer contract is unchanged, so it is owed but does not hold the tag — see Deliberately Not Doing
- F7 | bin: over-worry | evidence: weak | ref: skills/public/handoff/scripts/parse_handoff_entries.py:66-75 | action: document | note: the "clean OR not-checked" disjunction is accurate, not an over-disclaim — the repo root can be `None`, so the path check does not always run
- F8 | bin: over-worry | evidence: weak | ref: skills/public/release/scripts/publish_release_artifact.py:74 | action: document | note: hand-appending a delta line to the generated `## Scope` edits a generated surface the next helper run reverts; the delta is one link away via Review Proof
- F9 | bin: over-worry | evidence: weak | ref: skills/public/release/scripts/publish_release_baton.py:75-76 | action: document | note: the "explicit no_version_claim disposition" alternative loses to F3; both owning docs name the quoted version as the sanctioned answer
- F10 | bin: over-worry | evidence: weak | ref: skills/public/handoff/scripts/draft_goal_from_chunk.py:145-156 | action: document | note: an operator holding a pre-2.11.2 draft is unaffected — the drafter renders at draft time and refuses to overwrite, so the release neither creates nor worsens a stale draft; a reassurance sentence would spend the notes' attention budget on a non-event

## Reviewer Tier Evidence

- Requested tier: `high-leverage` (adapter `reviewer_tiers.high-leverage`), realized as the host's typed `bounded-reviewer` agent with session-model inheritance.
- Requested spawn fields: `subagent_type: bounded-reviewer`, no host addressing/team `name` (#458), one angle per spawn. The adapter's Codex-host fields (`model: gpt-5.6-terra`, `reasoning_effort`, `fork_turns`, `service_tier`) do not apply on this Claude Code host per the CLAUDE.md per-host split.
- Host exposure state: host-defaulted
- Application state: host exposed typed read-only agents; all three reviewers self-reported Read/Grep/Glob only.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`. Three bounded reviewers in separate agent contexts — two
release angles (Gawande, Minto) plus one separate counterweight, never collapsed
into an angle. Rail-1 boundary fingerprint snapshotted before the spawns and
verified clean (`{"ok": true, "drift": []}`) after all three returned, before any
parent edit — the bracketing failure recorded in the F9 critique was not repeated.

## Reviewed Input Identity

<!-- No prepare-packet consumed for the release lens; the reviewers were briefed against the committed release delta (cf43b62b) and the live release surface, and the boundary fingerprint verified clean across the review window. -->

## Boundary Ownership

- Producer: the repo-owned publish helper (`publish_release_cli.py` and friends), which owns bump, sync, verify, tag, publish, and the durable ledger.
- Consumer: the operator upgrading via `charness update`, plus the maintainer reading `charness-artifacts/release/latest.md`.
- Owning surface: release notes own the operator-facing change story; the generated ledger owns publication mechanics. F1 moves the change story into the notes rather than hand-editing the generated ledger (F8).
- Verdict: single-surface

## Deliberately Not Doing

- **No `docs/public-skill-dogfood.json` entry (F6).** The analogous #381 auto-draft shape change got one. This change is smaller, the consumer contract (routing, bootstrap, maintained scenarios) is unchanged, and the validator does not require per-change entries. Owed at the next handoff-touching slice; recorded here so the omission is a decision rather than an oversight.
- **No `--bump-rationale` CLI flag.** A permanent surface plus a validator obligation to stop it being filled with "n/a", bought for a sentence prose already carries.
- **No hand-append to the generated `## Scope` line.** Editing a generated surface the next helper run reverts.
- **No reword of the "clean OR not-checked" disjunction.** Its premise was overturned; the wording is accurate.
