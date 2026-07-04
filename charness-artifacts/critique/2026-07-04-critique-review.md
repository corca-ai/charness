# Critique Review
Date: 2026-07-04

## Decision Under Review

Cut and push **charness 0.61.0** (minor bump from 0.60.0). Scope: 11 committed-but-unpushed
commits — session-start hook front-loads 3-branch routing (pickup→handoff / discovery→find-skills
/ else→matching skill) so `find-skills` is no longer invoked every session; achieve phase-brief
demote (52KB always-load lifecycle → phase-keyed dispatch); quality inventory-dispatch demote to
on-demand; reference-compaction of docs/refs; tests + cautilus spec edits. Only remaining mutation:
version bump + manifest sync + tag + push, plus authoring the 0.61.0 release note. Target reference:
`release-critique.md`. Minor (not patch) justified by the new *adoptable* session-start behavior.

## Failure Angles

Three bounded fresh-eye angle reviewers (opus, high-leverage) + one counterweight, parent-delegated:

- **Gawande (operational/checklist):** mirror parity (source `skills/public/` vs generated
  `plugins/charness/skills/`), front-load activation mechanic, fresh-checkout probes, new-script
  wiring, release-artifact freshness.
- **Minto (structure/communication):** whether an operator who did not follow the dev thread can
  read the release scope; overclaim risk on the "efficiency" framing.
- **Raskin (humane interface):** the release changes the first thing every session does for every
  installed operator (find-skills no longer every session); reversibility and stale-map risk.

## Counterweight Pass

No release-hold blocker on the committed code. All Gawande operational items verified clean
(13 mirror pairs byte-identical, probes exit 0, new helper wired end-to-end and tested). The two
`act-before-ship` items are constraints on the release **note** (itself a remaining pre-push
deliverable), not holds on the 11 commits. M2 (no overclaim) is the one non-negotiable integrity
line. R1 ("genuinely" wording) triaged to over-worry. R2/R4 are real but disclosed/pre-existing and
deferred.

Surface-Lock Inventory (surfaces this release locks): generated plugin mirror
`plugins/charness/skills/**` + `plugins/charness/scripts/**`; consumer-visible behavior = session-start
hook directive (`scripts/session_start_find_skills.py`, `host_hook_find_skills.py`); skill-execution
logic (achieve `goal_artifact_phase_brief.py`/`check_goal_artifact.py`, quality `plan_quality_run.py`/
`catalog.yaml`); docs (`docs/handoff.md`, `docs/conventions/operating-contract.md`); release artifact
`charness-artifacts/release/latest.md`; cautilus eval specs. No operator-typed command, flag, doctor
exit code, or install prerequisite changed; no migration required.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/efficiency/achieve-phase-brief-ab/finding.md | action: fix | note: release note must claim ONLY the honest behavioral win (silent non-compliance 0/3 -> phase-scoped compliance 3/3 at judged outcome parity), NOT a token/context-reduction win (A/B ~null at n=3)
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/session_start_find_skills.py | action: fix | note: release note must LEAD with the operator-facing session-start behavior change in plain terms, not internal slice vocabulary
- F3 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/release/v0.61.0-notes.md | action: fix | note: carry a one-line why-minor-not-patch (new adoptable session-start behavior)
- F4 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/release/v0.61.0-notes.md | action: fix | note: carry no-migration + restart-sessions-after-update to activate new routing
- F5 | bin: bundle-anyway | evidence: strong | ref: scripts/host_hook_find_skills.py:141 | action: fix | note: note one line that the change is reversible/opt-in (adapter-gated hook, uninstall paths)
- F6 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/release/latest.md | action: defer | note: post-publish verify latest.md flips to v0.61.0 record (helper overwrites; do not pre-edit)
- F7 | bin: valid-but-defer | evidence: moderate | ref: skills/public/find-skills/references/session-start-routing.md:76 | action: defer | note: capability-map (latest.*) no longer auto-refreshed by every-session find-skills; disclosed + recurrence-gated (extend validate_current_pointer_freshness.py)
- F8 | bin: over-worry | evidence: weak | ref: scripts/session_start_find_skills.py:48 | action: document | note: injected directive keeps protective fallback and does not nudge under-routing; "genuinely" wording is aesthetic
- F9 | bin: valid-but-defer | evidence: weak | ref: scripts/session_start_find_skills.py:52 | action: defer | note: no-handoff+no-task fall-through dead-end for fresh/non-charness installs is pre-existing, not introduced by this release

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage (release-closeout review class).
- Requested spawn fields: adapter declares `model=gpt-5.5, reasoning_effort=medium, service_tier=priority` (Codex-host mapping); this Claude Code host resolves high-leverage to its strongest reviewer, so `model=opus` was sent via the Agent tool `model` param for all four reviewers.
- Host exposure state: requested_fields_sent
- Application state: not host-confirmed — the Agent tool accepted `model=opus`; no provider-side echo confirms application, and reasoning_effort/service_tier have no Claude-host mapping.

## Fresh-Eye Satisfaction

parent-delegated. Four bounded fresh-eye subagents spawned via the Agent tool under the repo
`Subagent Delegation` contract (3 angle: Gawande/Minto/Raskin + 1 counterweight), each completing its
assigned lens directly with no nested spawn. All ran read-only in the shared parent worktree; index
left clean. Packet consumed: `charness-artifacts/critique/2026-07-04-034014-packet.md`.
