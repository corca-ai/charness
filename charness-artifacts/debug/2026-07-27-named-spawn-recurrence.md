# Named Spawn Recurrence Debug
Date: 2026-07-27
Issue: corca-ai/charness#458

## Problem

The `name`-parameter spawn defect fixed in #454 recurred first-hand in this
session. A bounded reviewer spawned with `name` set stranded its findings; ~8
minutes of parent wall-clock and one complete review packet were lost, and the
review had to be re-run from scratch. #458 was filed from a consuming repo hitting
the same thing; this record is the charness-side observation.

## Correct Behavior

Given a parent that spawns any subagent, when the agent finishes, then its final
message is in the parent's own context — or the parent has a concrete, reportable
signal that delivery failed. An idle notification is not that signal: it reads
like success.

## Observed Facts

- The spawn carried `name: "plan-critique"` AND `run_in_background: false`. The
  tool result reported success and said the agent "will receive instructions via
  mailbox", so `name` selected the mailbox channel despite the foreground request.
- ~8 minutes later the only thing that arrived was
  `{"type":"idle_notification","idleReason":"available"}`. No findings.
- No DELIVERY channel was readable: `ToolSearch` for `select:SendMessage` returned
  no match; a keyword search over message/teammate/mailbox terms returned only the
  `Task*` family; and `TaskOutput` rejected BOTH the bare name (`plan-critique`)
  and the full `plan-critique@session-e7bc637b` id with "No task found".
- **The repo's own transcript DIAGNOSTIC did recover the findings**, and the parent
  initially failed to run it — reporting the review as unrecoverable when the
  contract already ships the tool for exactly this case.
  `reviewer_result.py list` showed the stranded agent as the only named one of
  seven (`aplan-critique-e5ce62fa470c0976`, `name: "plan-critique"`, every
  delivering sibling `name: null`), and `get --agent plan-critique` returned its
  complete final message with `status: found`. So the loss was the parent's, not
  the host's: delivery failed, recovery was available and unused.
- The same review packet re-spawned **unnamed**, `run_in_background: false`,
  returned complete findings inline in the tool result.
- Four further reviews in the same session used the unnamed foreground shape and
  all delivered.
- The recovered findings had independently identified two of the same blockers the
  parent later re-derived at full cost (sibling-scan Tier 1 already fixed; the
  one-pass validator machinery already shipped) AND one the parent never found: the
  audit artifact at `charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md`
  still listed Tier 1 A/B/C as work to do, which is what generated the phantom
  slice. That artifact is corrected in this resolution.

## Reproduction

- Spawn any `bounded-reviewer` with `name` set on this host: the spawn succeeds,
  completion emits an idle notification, and the findings are unreachable. Drop
  `name`, change nothing else, and the findings return inline. Identical to #454's
  A/B, so `n=2` for that arm across two sessions.

## Candidate Causes

- **The `name` parameter selects the delivery channel and `run_in_background: false`
  does not override it.** ✅ confirmed — the spawn result itself named the mailbox.
- The parent failed to wait long enough. ❌ refuted: the idle notification is the
  terminal event, and `TaskOutput` had no task to return afterward.
- The rule was absent from the repo. ❌ refuted: it was present and correct in
  [fresh-eye-subagent-review.md](../../skills/shared/references/fresh-eye-subagent-review.md), and unread.

## Hypothesis

- falsifiable claim: the rule did not bind because it lived only on a
  review-scoped surface, so a parent spawning for a non-review reason never opens
  it | disconfirmer: check whether the rule appears on any always-loaded surface —
  if it did, location is not the cause and operator attention is.

## Verification

- result: confirmed — `grep` for the rule's phrasing across always-loaded surfaces
  (`AGENTS.md`, `CLAUDE.md` symlink, [operating-contract.md](../../docs/conventions/operating-contract.md))
  matched nothing before this fix; the rule existed only in the review reference
  and its `plugins/` mirror, exactly as #458 reported.

## Root Cause

Same structural shape as #454, one level up: #454 promoted the rule "into a
contract" but into the **reviewer** contract. The mechanic it governs is scoped to
every `Agent` spawn, while its location and routing were scoped to fresh-eye
review. A parent spawning for any other reason — or, as here, invoking a skill
that merely lists the reference — never reaches it. The two skills that do cite it
cite it as a remedy "before reporting the reviewer path as blocked", but the
defect's signature is that the spawn SUCCEEDS, so a parent never believes it is
blocked and never follows the pointer.

## Invariant Proof

- Invariant: a spawned agent is not a received result; delivery is proven by
  findings text in the parent's context or recorded as failed.
- Producer Proof: the unnamed re-spawn of the identical packet returned complete
  findings, so the reviewer side was never at fault.
- Final-Consumer Proof: the named spawn's findings were unreachable through every
  retrieval path this host exposes (`SendMessage` absent, `TaskOutput` "No task
  found" for both id forms).
- Interface-Shape Sibling Scan: the rule's location was scoped to one caller class
  (review) while the mechanic is scoped to all callers (any spawn) — the same
  scope-mismatch shape as #454's sent-vs-delivered gap, one level up.
- Non-Claims: one session, one host, one version. Explicit
  `run_in_background: true` was not tested here (this spawn requested `false`), and
  every observation is a single reviewer, so concurrency is untested. "Unreadable"
  scopes to delivery channels only — the transcript diagnostic recovered the text,
  so nothing here claims the findings were destroyed.

## Detection Gap

- No gate observes a general spawn; the existing delivery floors
  (`reviewer_result.py`, the `Delivery state` field) are reviewer-closeout
  surfaces, so a non-review spawn has nothing watching it. Smallest change that
  would have fired: the rule on an always-loaded surface, which is what this
  resolution does — a gate cannot see a spawn parameter the host owns.
- The parent had the reference listed in the invoked skill's `## References` and
  did not open it, so attention is part of the causal chain; the fix removes the
  dependence on attention rather than asking for more of it.
- Second attention gap, same root: the contract ships `reviewer_result.py get` as
  the diagnostic for exactly this failure, and the parent reported the findings
  unrecoverable without running it. The recovery path is named in the same
  reference the parent did not open, so it decayed for the same reason. Recorded
  here rather than fixed with more prose.

## Sibling Search

- Mental model: "a rule that exists in the repo is a rule that binds."
- abstraction up: rule PLACEMENT versus rule SCOPE generally — a contract line is
  only as reachable as the surface it sits on | decision: same bug, fix now |
  proof: the rule was correct and unread; moving it to `AGENTS.md` is the fix.
- cross-file: [handoff SKILL.md](../../skills/public/handoff/SKILL.md) and [setup SKILL.md](../../skills/public/setup/SKILL.md)
  both phrase the pointer as a post-failure remedy | decision: same bug, fix now |
  proof: both reworded to a precondition of spawning in this resolution.

## Seam Risk

- Interrupt ID: named-spawn-recurrence-2026-07-27
- Risk Class: external-seam, repeated-symptom
- Seam: parent-to-subagent result delivery, owned by the host runtime and selected
  by a caller-supplied parameter; no repo code owns it.
- Disproving Observation: the spawn succeeded and the agent ran correctly while
  delivering nothing, so every local success signal was green during total loss.
- What Local Reasoning Cannot Prove: that any host delivers. Charness can influence
  the channel (spawn shape) and record the outcome, not guarantee it.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-07-25-reviewer-delivery-seam.md

## Prevention

The spawn-shape rule now sits in `AGENTS.md` `## Subagent Delegation` (loaded on
every session via the `CLAUDE.md` symlink), scoped to EVERY spawn and not only
fresh-eye review, with the reference retained for lineage and non-claims. The
`handoff` and `setup` pointers read as a precondition of spawning rather than a
remedy after a blocked report.

The placement fix is shipped, but this is the SECOND recurrence of one external
seam, so the forward work stays with the existing seam spec
(`charness-artifacts/spec/2026-07-25-reviewer-delivery-seam.md`) rather than
another point fix: host-plural delivery proof, and the open question of whether
anything can observe a general spawn's delivery at all. Upstream `anthropics/claude-code#71723` stays the
lineage for the workaround framing: if it closes, re-probe rather than assume, and
the invariant "a spawned agent is not a received result" does not relax either way.
