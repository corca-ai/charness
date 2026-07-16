# v1.1.0 Baton-Reconcile + Provenance Release Critique

Goal: release charness v1.1.0 (minor bump from 1.0.11) and push the local
commit bundle `e1653d73..cbf37690` to origin/main.
Date: 2026-07-16
Verdict: SHIP

Fresh-Eye Satisfaction: parent-delegated bounded release critique in a
different agent context (bounded-reviewer, read-only Read/Grep/Glob);
worktree+index reviewer boundary fingerprint verified with zero drift around
the review.

## Reviewer Tier Evidence

- Requested tier: pre-publish release-boundary critique.
- Requested spawn fields: repo standing request is `model=gpt-5.6-terra`,
  `reasoning_effort=medium`; this Claude Code host does not expose those
  fields, so the session model was inherited (limitation stated in-session).
- Host exposure state: unsupported
- Application state: session-model inheritance; no provider-side per-subagent
  model/effort application metadata was available.

## Release Boundary Findings

- Bump honesty: MINOR endorsed. The `post_publish_baton_path` adapter field,
  the `## Baton Reconcile` artifact section, and the observation module are
  backward-compatible additive operator surface; the glow/tokei/vulture
  update flip is a contract-conformance repair of behavior
  `docs/control-plane.md` already forbids (updates never guess an installer
  from PATH), with the stable status enum and the behind-latest advisory
  intact — not a major-shaped break. `next_action` is a human summary, not a
  contracted parse API (automation is routed to `--detail`/lock state).
- Highest-value finding (act-before-ship, APPLIED): the baton observation ran
  unguarded in the closeout tail *after* the irreversible publish; an
  unreadable baton would have skipped the final artifact commit, issue
  closeout, and install refresh. Fixed pre-publish in `cbf37690` with
  `_capture_lifecycle`-style containment (typed `capture_error` record +
  rendered manual-reconcile instruction + regression test).
- Baton semantics at this release: publishing 1.1.0 while the baton claims
  1.0.11 records `stale` + `RECONCILE REQUIRED` — the intended dogfood
  forcing function, non-fatal by design; no v-prefix mismatch (target and
  observed versions are both bare).
- Notes/update-instructions staleness: `docs/generated/cli-reference.md`
  carries no version strings; the narrative audit gates on the release
  artifact + target tag, not README/notes versions; adapter
  `update_instructions` remain version-agnostic and correct.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_common.py | action: fix | note: unguarded baton read after the irreversible publish could skip final artifact persistence; contained in cbf37690 before publish (regression test pins the containment).
- F2 | bin: over-worry | evidence: strong | ref: charness | action: defer | note: next_action wording change breaking external parsers — not a contracted API; docs route automation to --detail/lock state.
- F3 | bin: over-worry | evidence: strong | ref: docs/handoff.md | action: document | note: the expected stale baton record at this publish is the intended forcing function, not a blocker; reconcile the handoff right after publish.

## Structural Destination

- Verdict: owned-correctly

The containment fix landed in the closeout tail that owns the call site,
mirroring the sibling `_capture_lifecycle` guard; no new gate is requested.

## Issue Lifecycle And Public Proof

- No issue close rides this release; #439/#440/#441 remain open by intent.
- Publish proof is owned by the helper: release quality gate, tag+push,
  post-create verification, distinct-channel confirmation, install refresh,
  and final artifact persistence — judged per publication-boundary.md, not by
  helper green alone.
- Non-claims: the reviewer ran no tests and no git commands (read-only
  envelope); implementation internals were covered by the prior S1/S2+S3
  slice reviews; live network `tool update` behavior remains unproven by this
  release.

## Boundary Ownership

- Verdict: owned-correctly

- Producer: the goal-run slices own the shipped changes and their tests.
- Verifier: the release helper's gate battery plus this pre-publish critique
  own the release boundary; the post-publish distinct-channel probe is the
  second observer on a different evidence channel.
- Operator: approved the push+release lane explicitly ("push release"); D18
  and the live Codex probe remain queued.
