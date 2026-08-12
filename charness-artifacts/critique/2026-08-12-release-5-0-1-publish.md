# Release 5.0.1 publish critique

Date: 2026-08-12

## Decision Under Review

Whether the completed quality-planning and issue-closeout repairs should ship
as Charness `5.0.1`. This is a compatible patch: it repairs validator,
template, and authoring behavior without adding a public command or requiring
a migration. Existing direct and environment-prefixed Charness quality-runner
CI forms can newly receive a parity finding, which must be disclosed rather
than silently treated as unchanged behavior.

## Failure Angles

- Gawande: a local green result could conceal unsynchronised version surfaces,
  a stale install, or an unrun clean-checkout probe.
- Minto: generated notes could omit the newly-recognised runner forms or
  overstate local verification as hosted/provider/consumer behavior.
- Jackson: the operator needs the repaired outcome and update path, not only
  internal issue numbers.
- Counterweight: a patch should not be inflated into a minor solely because a
  previously missed CI spelling can now be diagnosed; the runner remains
  optional and the stricter refusal remains opt-in.

## Counterweight Pass

- Act Before Ship: commit a curated notes file and this packet-bound critique;
  run the post-notes claims review, the release helper's quality and
  clean-checkout checks, then independent remote/public/install readbacks.
- Bundle Anyway: state the adapter-template repair, closeout-authoring repairs,
  normal update path, and the runner-recognition change with its advisory
  default.
- Over-Worry: do not run the real-host `nose` checklist; the measured release
  range does not touch a configured real-host trigger surface.
- Valid but Defer: consumer CI outcomes, provider-backed adapter invocation,
  and GitHub issue closure remain separate external/post-publication work.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-08-12-v5.0.1-notes.md | action: document | note: disclose that direct/env-prefixed Charness runner forms can now yield parity findings, while no-runner repositories stay advisory absent explicit canonical-match refusal.
- F2 | bin: act-before-ship | evidence: strong | ref: .agents/release-adapter.yaml | action: fix | note: use the release helper to synchronize version surfaces, rerun release gates and fresh-checkout probes, then obtain remote, public, and installed readbacks through their distinct channels.
- F3 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/issue/2026-08-12-issue-604-canonical-gate-recognition.md | action: document | note: run a post-notes claims review before publication; do not promote local validation into hosted CI or consumer-runtime claims.
- F4 | bin: bundle-anyway | evidence: strong | ref: skills/public/issue/adapter.example.yaml | action: document | note: describe the repaired create-template grammar without claiming a live external provider invocation.
- F5 | bin: over-worry | evidence: strong | ref: /tmp/release-real-host.json | action: defer | note: no configured real-host release surface matched the frozen candidate range, so no real-host tool-install checklist is required for this patch.
- F6 | bin: valid-but-defer | evidence: strong | ref: skills/public/issue/references/closeout-discipline.md | action: defer | note: close #581, #593, #594, #603, and #604 only after their post-publication per-issue carrier and tracker readback; do not use the release tag as a closure claim.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: fork_turns=3; host model and effort controls inherited from this session.
- Host exposure state: host-defaulted
- Application state: host returned separate delegated reviewer contexts; no provider application metadata was exposed.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — Gawande, Minto, and counterweight reviewers read the
packet independently and returned their findings. The reviewer boundary window
`release-5-0-1-critique` verified clean before this artifact was authored.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-release-5-0-1-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-release-5-0-1-packet.json
- Packet SHA256: 504aa73f7743ae372a713bc5658df3090b551569797d9d2002195f1df955b403
- Identity SHA256: 131ad65228a7534f1332af0bd90146743930883c2560bd8da2d82f834066ae10

## Boundary Ownership

- Producer: the release helper, its synchronized version surfaces, curated release notes, and release evidence.
- Consumer: operators updating Charness and maintainers relying on the public release record.
- Owning surface: release contract and package/plugin publication surfaces.
- Verdict: owned-correctly
