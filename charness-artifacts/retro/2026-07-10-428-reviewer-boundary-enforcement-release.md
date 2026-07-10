# Session Retro — 428 Reviewer Boundary Enforcement Release

Date: 2026-07-10
Goal: `charness-artifacts/goals/2026-07-10-428-reviewer-boundary-enforcement-release.md`

## Mode

session

## Context

Autonomous improvement run over the handoff backlog: fixed the
credentials-less CI baseline failure blocking the #421 mutation gate,
resolved #428 (reviewer read-only boundary enforcement: rail-1
worktree+index fingerprint + rail-2 read-only reviewer envelope), and shipped
v0.65.0 (pushed, tagged, published, install-refreshed, #428 closed with a
verified carrier).

## Evidence Summary

- Goal artifact and slice logs: `2026-07-10-428-reviewer-boundary-enforcement-release.md`.
- Commits `3c25073c`, `5d894aa1`, `8145629a`, `7531144a`, `8bfa3147`,
  `0528718e` (closeout carrier), `b8930138` (tagged release), `4b7ba6ca`.
- Critique artifacts: `2026-07-10-428-resolution-critique.md`,
  `2026-07-10-v0-65-0-release-critique.md`.
- Live proof: rail-1 snapshot/verify clean around every bounded reviewer;
  full CI-baseline suite (4431 passed) in a credentials-less env;
  release URL readback HTTP 200; `verify-closeout` verified CLOSED.

## Waste

- The publish helper's own release commit embeds `Close #N` without the
  ledger the repo's commit-msg gate demands, so `--execute` failed twice
  (~160s of duplicate quality runs) before the carrier was committed
  manually and the helper resumed without `--close-issue`. Helper and gate
  disagree about one contract.
- The `bounded-reviewer` typed envelope accepted the spawn but did not bind
  its tool restriction mid-session; detecting that cost one probe round.
  Worse, the spawn-name was echoed back as `agentType`, so a
  host-signal-shaped confirmation would have been wrong — only the
  transcript tool-use audit was trustworthy.
- Background subagent completion produced no notification and `TaskOutput`
  could not find named agents, so waiting was polling `sleep` loops against
  worktree state and transcript files (~20 idle minutes across three
  reviewers).
- Repo-local git identity was left as `hotl proof <hotl-proof@example.invalid>`
  by a prior proof session; 62 commits (mostly already pushed) carry the
  placeholder. Caught only by the release critique NIT at the last boundary.

## Critical Decisions

- Reading the latest #421 machine comment during goal shaping surfaced the
  red CI baseline; sequencing that fix as slice 1 prevented releasing on a
  red gate.
- Closing #428 with per-acceptance-line non-claims (rail-2 binding deferred,
  spawn-denial unregressed, git-state-scoped regression) instead of a blanket
  "acceptance met" — the resolution critique's CLOSE-WITH-EDITS made the
  close honest without blocking the release.
- Not rewriting the 4 local placeholder-identity commits: artifact SHA
  references inside committed goal/critique files outweighed cosmetic
  authorship; config fixed forward, structural fix filed (#432).

## Expert Counterfactuals

- Engelbart (system-improving-itself): the enforcement was dogfooded on its
  own review loop in the same run (snapshot → reviewer → verify), which is
  the right T-loop shape; the miss is that the tool restriction (the H-side
  guarantee) was assumed from the spawn accepting the agent type. The
  counterfactual: land the capability with a same-session *negative probe*
  designed before implementation (spawn, attempt a write, expect denial), so
  host-binding facts are measured at the moment the contract is authored,
  not discovered post-hoc (#430 now owns that probe).
- Charity Majors (production evidence): the CI baseline break was found by
  reading the machine's latest comment, not by local gates — the local suite
  passed because maintainer credentials masked the failure mode.
  Counterfactual: any test that consumes ambient machine state
  (`$HOME`, credentials, git identity) should pin that state explicitly;
  the same class produced both the CI red and the identity leak. Sibling
  sweep below.

## Sibling Search

Transferable pattern: tests and tools consuming ambient machine state
(credentials, `$HOME`, git identity) instead of pinning it. Scanned
`tests/test_skill_efficiency_ab.py` (now pins `CLAUDE_CONFIG_DIR`) and the
capture script (guarded). The git-identity sibling is real and recurred (62
commits) — filed as issue #432 (pre-commit/pre-release `.invalid`-identity
check named in its non-binding direction). Remaining ambient consumers are
owned by #429's gate-scope follow-up; no further unfiled siblings found in
this run's changed surfaces.

## Next Improvements

- workflow: before any release that closes issues, rehearse the *helper's
  generated commit message* against the commit-msg gate (not only the
  hand-drafted carrier) — mismatch filed as the publish-helper/gate seam in
  the goal's Auto-Retro (issue below).
- capability: fresh-session envelope binding probe + spawn-denial regression
  (#430); rail-1 spawn-step wiring in consuming skills (#431).
- memory: reviewer self-report is never evidence — transcript tool-use audit
  plus rail-1 verify is the provable channel; recorded in the goal artifact
  and the fresh-eye reference's Enforcement section.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-10-428-reviewer-boundary-enforcement-release.md
