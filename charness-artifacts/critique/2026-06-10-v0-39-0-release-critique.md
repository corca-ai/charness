# v0.39.0 release critique
Date: 2026-06-10

## Decision Under Review

Cutting charness v0.39.0 (minor) from the pushed main 837cc640 via the
repo-owned publish helper: two additive capabilities (the corrected-root-cause
Claude-host per-goal metric scoping; the new portable `hotl` public skill),
artifact-only records, and an inert next-queue draft goal.

## Failure Angles

- The bump level could hide a compatibility break (helper renames,
  profile-schema change, dogfood-registry re-shape).
- The update_instructions entry could overclaim shipped behavior or omit an
  operator-visible change.
- A release surface could be stale pre-bump (version drift, uncommitted
  mirror, missing probes, lost install-refresh lesson).

## Counterweight Pass

- No blockers. The reviewer verified the bump-level call against the actual
  v0.38.0..837cc640 delta (renames were module-private with zero surviving
  references; schema/profile/registry changes additive; degrade paths honest),
  spot-checked every update_instructions claim against the shipped code and
  tests, confirmed all release surfaces agree pre-bump with validators green,
  and confirmed the install-refresh lesson is still adapter-declared.
- Folded nits: the byte-identical claim re-scoped to Codex hosts WITH a
  session audit (the no-audit unavailable wording changed and now names both
  hosts); the internal codex-audit helper renames + new last_event_at field
  noted in the entry per the prior release's precedent.
- Not folded (handled at invocation): the publish lane path is
  skills/public/release/scripts/publish_release.py with --repo-root.
- Over-worry (reviewer-dismissed): renames as a major trigger; schema/registry
  churn as breaking; stale latest.md (committed, helper rewrite is designed);
  the corrected-#346 framing (accuracy, not spin).

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: .agents/release-adapter.yaml | action: fix | note: byte-identical rendering claim over-scoped (the no-audit unavailable block wording changed for all hosts); entry re-scoped to Codex hosts with a session audit before publish.
- F2 | bin: act-before-ship | evidence: moderate | ref: .agents/release-adapter.yaml | action: fix | note: entry omitted the five in-repo codex-audit helper renames + the new last_event_at payload field; one-clause internal-rename note added per the prior release entry's precedent.
- F3 | bin: over-worry | evidence: strong | ref: scripts/codex_session_jsonl_audit.py | action: defer | note: private-to-public renames as a compat break — old names were module-private, zero references survive, all consumers in-repo.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: fresh-eye bounded subagent reviewer (repo-contract pre-approved scope), read-only in the shared parent worktree with read-only gh.
- Requested spawn fields: subagent_type=general-purpose, name=release-critique, prompt carrying the release packet (current/target versions, bump justification, lane, the drafted entry) and four verify-against-the-repo checks.
- Host exposure state: applied
- Application state: host-confirmed: Agent tool returned a structured SHIP-WITH-NITS verdict (37 tool uses, 295s) with per-check verified facts, including independent gh reads of the CLOSED issues and the green quality-core run on 837cc640.

## Fresh-Eye Satisfaction

Reviewer verdict: SHIP-WITH-NITS — bump level honest (minor), entry accurate
on every spot-checked claim, surfaces ready, install-refresh lesson encoded.
Both foldable nits folded into the entry before the publish helper ran; no
precondition outstanding.
