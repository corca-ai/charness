# Bounded Reviewer Result Delivery Debug
Date: 2026-07-25
Issue: corca-ai/charness#454

## Problem

Every bounded fresh-eye reviewer spawned for a repo-mandated review returned
without delivering findings to the parent (4/4 in session `af651c7f`). The
`Agent` spawn succeeded, `run_in_background: false` returned immediately anyway,
an `idle_notification` arrived later, and no findings text ever reached the
caller. `SendMessage` was not exposed, `TaskList` was empty, and `TaskOutput`
documents itself as unsuitable for local-agent tasks. Capability at risk: every
task-completing `setup`, `quality`, `critique`, `release`, and `issue` closeout,
all of which `AGENTS.md ## Subagent Delegation` requires a fresh-eye review for
and none of which accepts a same-agent substitute.

## Correct Behavior

Given a parent that spawns a bounded reviewer under the repo delegation
contract, when the reviewer finishes its lens, then the findings text is in the
parent's own context and the review can be recorded as obtained.

## Observed Facts

- The reviewer was never the problem. Probe A's on-disk transcript
  (`~/.claude/projects/-home-hwidong-codes-charness/820c4568-*/subagents/agent-adelivery-probe-1-*.jsonl`)
  holds a complete, correct final assistant message that the parent never saw.
- Probe A's `.meta.json`: `"taskKind": "in_process_teammate"`,
  `"teamName": "session-820c4568"`, `"name": "delivery-probe-1"`,
  `"customAgentType": "bounded-reviewer"`. The spawn result said the agent
  "will receive instructions via mailbox".
- `SendMessage` is absent from the session tool list and unresolvable via
  `ToolSearch` (both keyword search and `select:SendMessage`), so the mailbox
  channel has no reader.
- `reviewer_boundary_fingerprint.py verify` returned `{"ok": true, "drift": []}`
  across every affected round — rail 1 was green the whole time it was
  delivering nothing.
- Prior recurrence: `charness-artifacts/retro/2026-06-20-north-star-phase4-boundary-non-terminality.md:36-41,89-91`
  recorded this exact differential five weeks earlier. Two later retros then
  moved away from it without running the cheap unnamed-respawn falsifier:
  `2026-07-16-scout-driven-improvement-retro.md:44-48` concluded "Host-runtime
  behavior, not repo fixable" (and worked around it by polling subagent
  transcripts with fixed sleeps, ~10 idle minutes across four reviews), while
  `2026-07-17-prove-dogfood-via-444-polish-goal-session-retro.md:74-76` recorded
  the opposite observation — spawns "returned results inline this session" —
  and downgraded the lesson to "host-version-dependent rather than permanent".
  Neither connected the difference to the spawn's `name` parameter.

## Reproduction

Controlled differential, identical prompt / `subagent_type: bounded-reviewer` /
`run_in_background: false`, varying only the `name` parameter:

| arm | `name` passed | result |
| --- | --- | --- |
| A | yes | spawn metadata only; findings stranded in mailbox |
| B | no | findings returned synchronously in the tool result (`duration_ms: 6691`) |

## Candidate Causes

- **Spawn call shape selects the delivery channel; a named spawn routes to a
  mailbox the parent cannot read.** ✅ confirmed by the A/B differential plus
  `taskKind: in_process_teammate`. `n=1` per arm, one host and one version.
- Reviewers mis-shaping their final message. ❌ refuted twice: issue #454's 4th
  attempt instructed the message shape explicitly with an identical outcome, and
  Probe A's transcript shows a correctly shaped message.
- Reviewer boundary violation or envelope failure. ❌ rail-1 verify clean
  throughout; the causal reviewer self-reported `Bash/Edit/Write/Agent absent as
  designed`.
- Pure host/runtime behavior charness can only detect and report. ❌ a
  caller-controlled parameter flips the outcome.

## Root Cause

Structural, not host-only: **no charness surface owned reviewer result
delivery.** `skills/shared/references/fresh-eye-subagent-review.md` owned tier,
delegation, git hygiene, and boundary enforcement, but said nothing about spawn
call shape or findings retrieval, and `.claude/agents/bounded-reviewer.md`
stated the producer side reviewer-side only. The correct spawn shape was known
on 2026-06-20 but lived only as a retro "Next Improvement" with no promotion
path into a contract, so it aged out of the rolling digest and the next two
sessions re-derived a wrong attribution instead.

## Fix

`## Result Delivery` in the shared fresh-eye reference, which now owns: the
unnamed one-shot spawn shape, "a spawned reviewer is not a received review",
typed closeout states (`findings-received` / `spawn-accepted-no-delivery`) kept
separable from boundary state, the transcript read as diagnostic-only, and an
availability probe that passes only when findings text arrives. Pinned by
`tests/quality_gates/test_reviewer_result_delivery.py`. Because the recurrence
cause was lesson decay, the rule is in the contract rather than in
`recent-lessons.md`.

## Non-Claims

- Codex / `explorer` delivery is **not inspected**; the Claude envelope rail is
  already `unsupported` there.
- Proven on one Claude Code host at one version, `n=1` per arm. Background
  spawns and multi-reviewer concurrency are not inspected.
- Envelope binding on the unnamed path is proven live for this host only (the
  causal reviewer had no Bash/Edit/Write/Agent); tier application on that path is
  `metadata-hidden`, not `applied`.
- **The `.claude/agents/bounded-reviewer.md` paragraph is not proven live and is
  release-gated.** Reviewers spawned during this session ran the installed
  plugin cache copy (`~/.claude/plugins/cache/corca-charness/charness/2.5.0/agents/bounded-reviewer.md`),
  which predates this change; agent definitions load at parent session start, so
  every reviewer on this machine runs the old envelope text until a release and
  reinstall. The delivery rule therefore rides the parent-side spawn packet,
  which parents control immediately — the envelope paragraph is reinforcement,
  not the carrier. `test_envelope_points_reviewers_at_the_delivery_owner` pins
  the repo copy only and passes green regardless of the installed lag.
