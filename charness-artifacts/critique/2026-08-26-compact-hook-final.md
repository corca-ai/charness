# Codex compact recovery hook final closeout
Date: 2026-08-26

## Decision Under Review

Make Codex SessionStart recovery distinguish a post-compaction start from a new
session, while keeping Claude routing independent and removing the user-declared
bare handoff pickup/resolver text.

## Verification Scope Decision

- Claim under test: Codex emits compact recovery context only for
  `source=compact`, preserves the host-selected rollout identity, and fails
  closed with usable hook output when recovery inputs or helper behavior are
  malformed.
- Changed surfaces: root and checked-in plugin SessionStart/recovery scripts,
  host matcher reconciliation, and routing/recovery regression tests.
- Minimum sufficient proof: compare the `../codex` lifecycle source, run the
  focused root/plugin test matrix, exercise hostile helper and entrypoint
  payloads, verify source/plugin parity, and run the packet and changed-surface
  validators.
- Deliberately omitted checks: no live Codex compaction, transcript selection,
  installed-cache readback, or model-following claim is made in this artifact.
- Verifier contract: packet verifier
  `skills/public/critique/scripts/verify_packet.py`,
  sha256:ca6dd6cb50f7573ec05475ba920c9ac59639effe59e81005f1401e3b21215e8d.
- Failure classification: subject-defect
- Negative control: command: `python3 -m pytest -q tests/test_session_start_routing.py tests/test_session_start_lesson_context_hook.py` | expected refusal: root/plugin `startup`, `resume`, `clear`, Claude, malformed, and unknown-source entrypoints emit no ready compact recovery | observed result: 65 passed and refusal assertions held | receipt: focused pytest output from the closeout run.
- Subject identity: sha256:1c6da7476ae4569c8b228f1fea270cdf07a5c73a81725efed19ebf9e44309525
- Verifier identity: sha256:6d3fd06993ae2050d316d750db0da1b8330fd305f587ec0d34c54c2a5a8e0e7a
- Input identity: sha256:1c6da7476ae4569c8b228f1fea270cdf07a5c73a81725efed19ebf9e44309525
- Failure identity: stable:compact-hook-r11-silent-fallback-and-identity-spoof
- Evidence identity: sha256:de8def69d7f2a6e3ed199df102e2532946e7505904da0bab1664a17af9212265
- Retry disposition: non-claim
- Retry key: sha256:29a554f36450c7c3ca4cc9cb7122c37d9c195513c279dafd74084aaf1cc55747

## Failure Angles

- Lifecycle polarity: `../codex` must distinguish queued
  `SessionStartSource::Compact` from ordinary startup/resume/clear; PostCompact
  does not supply model additional context.
- Recovery trust boundary: helper prose, substituted identity, hostile string
  subclasses, accessor exceptions, malformed source, and malformed `cwd` must
  not produce ready recovery or silent success.
- Consumer/export parity: root and checked-in plugin scripts and host matcher
  migration must remain synchronized.
- Operator cost: the ordinary session-start directive must not retain the
  user-rejected bare handoff pickup/resolver detour.

## Counterweight Pass

The r11 counterweight classified the unusable-`cwd` silent success and
equality-spoofed helper identity as Act Before Ship because both were executable
on both entrypoints. It classified bare handoff removal as Over-Worry only when
raised as a regression because the user explicitly approved that removal. Live
host/model behavior remains Valid but Defer and is recorded as a non-claim.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `scripts/session_start_routing.py:329-336` | action: fix | note: r11 reproduced `cwd=U+0000` yielding rc=0 with empty stdout; the parent replaced the silent outer fallback with prebuilt valid Claude/Codex output and added root/plugin entrypoint regressions.
- F2 | bin: act-before-ship | evidence: strong | ref: `scripts/session_start_routing.py:232-267` | action: fix | note: r11 reproduced hostile `str` subclasses causing helper-selected attacker identity to render; the router now requires exact built-in strings and renders validated payload identity.
- F3 | bin: over-worry | evidence: strong | ref: `scripts/session_start_routing.py:92-98` | action: defer | note: treating explicit removal of bare handoff pickup/resolver wording as a defect would contradict the user's stated direction.

## Reviewer Tier Evidence

- Requested tier: high-leverage (second bounded review of a verdict-rendering
  recovery surface).
- Requested spawn fields: file-backed `codex_exec` worker, read-only,
  ephemeral, timeout 900 seconds; provider model controls were not claimed.
- Host exposure state: host-defaulted
- Application state: host ran the file-backed worker; no independent provider
  tier-application signal was exposed.
- Delivery state: findings-received
- Worker report: `.charness/reviewer-round-compact-hook-r11/recovery-adversarial-report.yaml` <!-- reproduction-source -->
- Worker report identity: 7f1d4f8be7cc6a8c5c04075893d9f5079d9f5e5f85cc199050bcac70a6b068dc
- Worker report approval: approval_eligible: false
- Worker report delivery: findings-received
- Worker report packet identity: 7fa979dfcd0ea4940ea4be08759d6821ce19f0a20d24e2b6fe671f85a3405c03
- Worker report input identity: cf326d3c3a2db07cf954e29f59324036530173396bb44ed3ca39a94652f03790
- Worker report parent receipt identity: compact-hook-parent-r11-20260826
- Worker report findings identity: de8def69d7f2a6e3ed199df102e2532946e7505904da0bab1664a17af9212265

## Fresh-Eye Satisfaction

accepted-unreviewed-under-round-cap compact-hook-r11-second-round-repair-cap —
r11 was the second bounded review of the verdict surface and returned two
reproduced blockers. The repairs made after that round are recorded as an
explicit non-approval under the operating cap; no third fresh-eye approval is
claimed.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/compact-hook-final-packet.json`
- Packet path: `charness-artifacts/critique/compact-hook-final-packet.json`
- Packet SHA256: 4c5e80f0cddebb50462cd510b11eba9d3f84e95f5a0c3fceab02869d434b87b5
- Identity SHA256: 1c6da7476ae4569c8b228f1fea270cdf07a5c73a81725efed19ebf9e44309525

## Boundary Ownership

- Producer: Codex's SessionStart source/identity payload and Charness's
  host-specific router/recovery helper.
- Consumer: the Codex/Claude hook dispatcher and the model-visible
  `additionalContext` field.
- Owning surface: host routing matcher plus Codex-only recovery block; Claude
  keeps its ordinary matcher and context path.
- Verdict: owned-correctly — lifecycle distinction belongs to Codex's
  host-selected `source`, recovery prose belongs to the router, and the
  helper supplies only structured state and identity.

## Deliberately Not Doing

- No live compaction/transcript/model-compliance claim.
- No third bounded reviewer after the explicit two-round verdict-surface cap.
- No GitHub issue mutation in this implementation closeout; issue regroup follows
  after commit and installation readback.

## Next Move

Run the remaining standing/doc/critique validators, commit the verified source
slice, update the installed Charness hook, perform local config and entrypoint
readback, then regroup open issues with #722 and #723 at the top.
