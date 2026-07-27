# Distinct channel D4 D6 D8
Date: 2026-07-28

## Decision Under Review

Fixing D4, D6, D8 and D2's `--generate-notes` residual — the distinct-channel and
readback family. These are north-star P4 itself: at an irreversible boundary,
confirm through a different evidence channel and a different observer, never by
re-reading the same proxy. D4: the HTTP probe confirmed on any 200 with one body
byte. D6: the installed readback recorded `observed` on exit code alone. D8: the
artifact asserted "a channel distinct from `gh release view`" on records that
were nothing of the kind. D2 residual: the notes audit never ran on the default
publish path.

## Failure Angles

- **A fix that adds a check the caller never reaches is worse than no fix**, because
  it reads as closed. Bit exactly: the published-body audit was wired to a shell
  runner that silently discards list arguments, so it would have recorded
  `unavailable` on every publish forever.
- **A new call after the point of no return can strand the thing it audits.** Bit:
  `SystemExit` from an undeclared backend op escaped an `except Exception` and
  would have killed the run after the release existed, for every non-`gh` adapter.
- **Branching on the wrong field reproduces the defect.** Bit: distinctness is a
  property of the same-proxy guard, not of the status, so the D8 fix still
  asserted distinctness over a literal `gh release view` probe.
- **A comparison that "works" on the happy example.** Bit: substring matching made
  `2.11.3` match `2.11.30` and match the trailer in `2.11.1 (latest 2.11.3)` —
  reporting agreement while the wrong version was installed.
- **Confirming the wrong proposition.** The deepest one: the probe can be made to
  check content and still not establish what the artifact claims.

## Counterweight Pass

- Four blockers from the bounded reviewer, all reproduced by execution before
  repair, all fixed: the runner mismatch, the escaping `SystemExit`, the empty
  body recorded `clean`, and the guard-vs-status branch.
- Folded in beyond the blockers: the substring comparison, `version_match`
  emitted unconditionally, the advisory rendered into the artifact instead of
  living only in stdout JSON, and socket hygiene in the new HTTP tests.
- **Accepted and recorded rather than hidden:** the HTTP probe cannot distinguish
  a released tag from a pushed one. Measured, not assumed — `releases/tag/v0.1.1`
  (no release) returns 200 with the tag 23 times, and both pages title themselves
  `Release <tag>`. The unauthenticated API that would distinguish is rate-limited.
  So D4 is PARTIAL and the record names what the channel does and does not
  establish. Claiming D4 FIXED here would have been the exact failure this hunt
  is about, committed by the fix for it.
- Over-worry: that the new `version-mismatch` status would block or strand an
  already-published release. Traced every consumer — nothing gates on the status
  enum, and `safe_write_release_observer` catches exceptions.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_common.py:107 | action: fix | note: the published-body audit was wired `run=cli.run_shell`, and `shell=True` with a list drops every argument after the first — measured, `run_shell(["git","status","--short"])` runs bare `git`; the audit would have recorded `unavailable` on every publish while reading as closed
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_post_create.py:103 | action: fix | note: `backend_command` raises SystemExit for an undeclared op and SystemExit is not an Exception, so a non-`gh` backend would die after the release existed and outside the rollback wrapper — stranding the publish before the rung-1 floor, issue closeout, and the final artifact commit
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_artifact_sections.py:177 | action: fix | note: the D8 fix branched on status, but distinctness is a property of the same-proxy guard; confirmed rendering "a channel distinct from `gh release view`" over a probe of literally `gh release view v1` when the guard never ran
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_post_create.py:114 | action: fix | note: an empty published body recorded `clean` — a PASS over a scope never established, class (a) reintroduced by the fix for class (d)
- F5 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/release_observer.py:96 | action: fix | note: substring comparison matched `2.11.3` inside `2.11.30` and inside the trailer of `charness 2.11.1 (latest 2.11.3 available)`, reporting a match while the wrong version was installed — the dangerous direction for a readback whose whole job is catching that
- F6 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_artifact.py:105 | action: fix | note: `published_notes_audit` was written to the payload and read nowhere, surviving only in the publish run's stdout JSON; an advisory nobody reads is the silent path the D8 fix is about, one surface over
- F7 | bin: bundle-anyway | evidence: strong | ref: skills/public/release/scripts/publish_release_post_create.py:79 | action: document | note: measured that the release page returns 200 for a tag with no release, so the probe establishes tag-page reachability, not release existence; recorded as `establishes`/`does_not_establish` and rendered, with D4 left PARTIAL rather than claimed fixed
- F8 | bin: valid-but-defer | evidence: moderate | ref: skills/public/release/scripts/publish_release_post_create.py:73 | action: defer | note: body truncation at `_PROBE_BODY_BYTES` is not recorded, so a missing marker past the limit would be reported as "the body does not mention the tag" — a false statement about the response; low probability since the tag appears in the page title
- F9 | bin: over-worry | evidence: contested | ref: skills/public/release/scripts/release_observer.py:120 | action: defer | note: concern that `version-mismatch` would block or strand an already-published release; traced every consumer and nothing gates on the status enum

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (typed read-only agent), one spawn over the whole family since the four fixes share a call path.
- Requested spawn fields: subagent_type=bounded-reviewer, scope prompt naming both directions per angle and inviting the reviewer to name commands it could not run; no host addressing name; session-model inheritance.
- Host exposure state: applied
- Application state: host-confirmed: Claude Code accepted the `bounded-reviewer` spawn and returned findings inline; `reviewer_boundary_fingerprint.py verify` reported `ok: true` with `drift: []` across window `w-20260727T222605Z`.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated` — a bounded read-only reviewer ran in a separate agent
context. It listed eight commands it could not run itself; the parent ran all of
them, including the live-network discriminator check that turned D4 from a
claimed fix into a recorded PARTIAL. Every blocker was reproduced before repair.

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

- Producer: the distinct-channel probe, the installed-version readback, and the published-body audit — three post-publish observers.
- Consumer: the release artifact and the human rung-2 disposition review that reads it as the record of what was actually confirmed.
- Owning surface: the artifact renderer, because every defect here ended as a sentence the artifact asserted over evidence that did not support it; fixing the probes without fixing what the artifact claims would have left the overclaim intact.
- Verdict: owned-correctly
