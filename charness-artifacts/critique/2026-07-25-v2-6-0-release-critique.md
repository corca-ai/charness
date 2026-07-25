# v2.6.0 Release Critique
Date: 2026-07-25

## Decision Under Review

Publishing v2.6.0 (minor, from 2.5.0): 18 commits covering #454's resolution (the
`## Result Delivery` contract clause and the typed `Delivery state` closeout
floor), the clearing of every changed-line mutation blocker in the unpushed
range, and earlier sessions' already-committed work.

## Failure Angles

- **Downstream compatibility / bump level** — is `minor` honest, or does a new
  required artifact field force a downstream migration?
- **Release readiness / ship-blockers** — what would make this release
  regret-worthy, and is anything not ready?

## Counterweight Pass

Both reviewers ran the counterweight inside their own lens rather than as a third
spawn, since each was asked to state plainly if its lens found nothing real.
The compatibility reviewer explicitly graded four candidate blockers down to
`nit` after checking the actual population affected — the delivery floor only
fires on artifacts that already carry a `## Reviewer Tier Evidence` section, so
the remediation is one added line inside a section the author already writes, not
a migration. The readiness reviewer explicitly checked and rejected the
"validator bricks a legitimate workflow" hypothesis: a heading with no parseable
fields returns falsy and skips the check entirely, so there is no repo-wide
closeout lockout.

The one finding both the fix and the counterweight agreed was real — the markup
normalization asymmetry — was reproduced before being fixed rather than taken on
the reviewer's word.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/critique_reviewer_evidence.py | action: fix | note: typed check stripped leading markup while the signal check tested the raw string, so a bolded no-delivery value skipped the name-the-channel rule; reproduced, then fixed by normalizing once, with six regression cases incl. a marked-up value with a real signal that must still pass
- F2 | bin: act-before-ship | evidence: strong | ref: docs/handoff.md | action: fix | note: handoff still described the pre-#454 session and posed an operator decision this push answers; rewritten, and the rewrite's own dropped References section was caught by the retro-memory contract test and restored
- F3 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/release/latest.md | action: document | note: release notes should list every behavior change, not only the delivery floor - the four sweep removals and the AI-provenance close-comment floor also alter accepted input
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/validate_critique_artifacts.py | action: document | note: the grandfather is a hardcoded date, not a version check, so a repo upgrading late and running --all sees pre-upgrade artifacts flagged; bounded because default validation is changed-paths-only, so it is a release-note line rather than a code change
- F5 | bin: over-worry | evidence: weak | ref: scripts/critique_reviewer_evidence.py | action: defer | note: a delivery signal wrapped onto a continuation line raises, since the field parser is single-line; fail-closed with an actionable message naming the required shape, not a brick
- F6 | bin: over-worry | evidence: weak | ref: scripts/boundary-bypass-exemptions.txt | action: defer | note: the new CLI-smoke exemption was checked against the file's own policy and the sibling entries and is honest - exactly one subprocess case, every behavior case in-process, with owner and revisit condition

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage (two release-critique angle reviewers).
- Requested spawn fields: none sent — per the repo's per-host subagent split, Claude Code hosts use the host's own typed-agent controls (`bounded-reviewer`) with session-model inheritance.
- Host exposure state: host-defaulted
- Application state: reviewers ran on the session-inherited model; no host tier-application signal exposed.
<!-- allowed Delivery state: findings-received | spawn-accepted-no-delivery | pending-parent-spawn. Boundary cleanliness is a separate claim and does not imply delivery. -->
- Delivery state: findings-received — both reviewers returned findings inline under the unnamed spawn shape.

## Fresh-Eye Satisfaction

`parent-delegated`. Two bounded reviewers spawned as `bounded-reviewer`; both
returned findings and both self-reported the read-only envelope bound. Rail-1
boundary verified `{"ok": true, "drift": []}` after the set.

Both reviewers named an evidence limit rather than guessing past it: having no
shell, neither could read commit diffs for four commits in the range, so the
compatibility reviewer reconstructed those from files and the sweep artifact and
said so. The parent closed that arm directly (`git log` over the range confirms
no `Closes #453` trailer, so the push does not auto-close #453).

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

<!-- allowed Verdict (substitute only these): single-surface | owned-correctly | moved-to-owner | escalated-to-issue-spec. Run the producer/consumer brief at skills/shared/references/boundary-ownership-brief.md. -->
- Producer: this repo's release surface (packaging manifest, plugin mirrors, marketplace files) and the new validator floor it ships.
- Consumer: downstream repos installing charness, whose critique authoring and closeout validation change behavior on upgrade.
- Owning surface: `packaging/charness.json` as the single version source, with `sync_root_plugin_manifests.py` deriving every mirror.
- Verdict: single-surface — the version lives in one manifest and every other surface is generated from it; no hand-edited generated files, and both reviewers independently verified all surfaces agree.
