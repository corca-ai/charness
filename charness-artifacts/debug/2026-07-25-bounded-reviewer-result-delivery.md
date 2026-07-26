# Bounded Reviewer Result Delivery Debug
Date: 2026-07-25
Issue: corca-ai/charness#454

## Problem

Every bounded fresh-eye reviewer spawned for a repo-mandated review returned
without delivering findings to the parent (4/4 in session `af651c7f`). The spawn
succeeded, `run_in_background: false` returned immediately anyway, an idle
notification arrived later, and no findings text ever reached the caller;
`SendMessage` was unexposed and `TaskList` empty. Capability at risk: every
task-completing `setup`, `quality`, `critique`, `release`, and `issue` closeout,
all of which require a fresh-eye review that accepts no same-agent substitute.

## Correct Behavior

Given a parent that spawns a bounded reviewer under the repo delegation
contract, when the reviewer finishes its lens, then the findings text is in the
parent's own context and the review can be recorded as obtained.

## Observed Facts

- The reviewer was never the problem. Probe A's on-disk transcript
  (`~/.claude/projects/-home-hwidong-codes-charness/820c4568-*/subagents/`)
  holds a complete, correct final message the parent never saw.
- Probe A's `.meta.json`: `"taskKind": "in_process_teammate"`,
  `"teamName": "session-820c4568"`, `"customAgentType": "bounded-reviewer"`. The
  spawn result said the agent "will receive instructions via mailbox".
- `SendMessage` is absent from the tool list and unresolvable via `ToolSearch`,
  so that mailbox has no reader; `TaskList` stayed empty.
- `reviewer_boundary_fingerprint.py verify` returned `{"ok": true, "drift": []}`
  every affected round — rail 1 was green the whole time it delivered nothing.

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
  `taskKind: in_process_teammate`.
- Reviewers mis-shaping their final message. ❌ refuted twice: #454's 4th attempt
  instructed the shape explicitly with an identical outcome, and Probe A's
  transcript holds a correctly shaped message.
- Reviewer boundary or envelope failure. ❌ rail-1 verify clean throughout.
- Pure host behavior charness can only report. ❌ a caller parameter flips it.

## Hypothesis

If the spawn call shape selects the delivery channel, re-running the same packet
with `name` removed — nothing else changed — returns the findings inline.
disconfirmer: re-spawned the identical reviewer packet with `name` removed and
nothing else changed, run BEFORE any fix — had it also stranded its result, the
call shape would have been ruled out and charness could only detect and report.

## Verification

Ran exactly that differential (see Reproduction): the unnamed arm returned
findings synchronously, the named arm did not, and its complete final message was
recoverable only from the transcript. The hypothesis held; its falsifier did not
fire.

Fix verification: four bounded reviewers spawned unnamed during this resolution
all delivered. The `Delivery state` floor was proven to reject all four violation
shapes plus the markup-smuggling case a release reviewer found, while accepting
real records and grandfathering pre-cutoff artifacts. Suite: 5144 passing.

## Root Cause

Structural, not host-only: **no charness surface owned reviewer result
delivery.** `fresh-eye-subagent-review.md` owned tier, delegation, git hygiene,
and boundary enforcement but said nothing about spawn call shape or findings
retrieval, and the reviewer envelope stated the producer side only. The correct
spawn shape was known on 2026-06-20 but lived as a retro lesson with no promotion
path into a contract, so it aged out and the next two sessions re-derived a wrong
attribution instead.

## Invariant Proof

- Invariant: a bounded reviewer's findings text reaches the parent's context, or the failure is recorded — spawn acceptance never stands in for delivery.
- Producer Proof: Probe A's on-disk transcript holds a complete, correct final assistant message the parent never received.
- Final-Consumer Proof: Probe B returned findings in the parent's tool result, and four real reviewers delivered the same way during this resolution.
- Interface-Shape Sibling Scan: reviewer-tier evidence modeled `requested_fields_sent` vs `applied` but had no spawned-vs-delivered sibling; `Delivery state` closes that asymmetry.
- Non-Claims: Codex/`explorer` delivery not inspected; envelope binding on the unnamed path proven for this host only; tier application there is `metadata-hidden`, not `applied`. Explicit `run_in_background: true` and multi-reviewer concurrency remain uninspected — **restated, not discharged**, with new corroboration under *Recurrence Corroboration* below (#458).

## Detection Gap

- `reviewer_boundary_fingerprint.py` proves git-state only and was green through
  every failed round, while closeout prose had begun citing it as reviewer
  validity — active false confidence. Smallest change: a closeout delivery field
  separate from boundary state, not a script change.
- The blocked-path probe treated spawn acceptance as availability proof; it now
  passes only when findings reach the caller.
- Nothing could observe "spawned but never delivered" — human detection only. A
  missing invariant, not missing scope.

## Sibling Search

Mental model that allowed the bug: "a reviewer that ran correctly and kept its
boundary clean has delivered its review."

- cross-file: `scripts/validate_critique_artifacts.py` reviewer-tier evidence —
  sent-vs-applied was modeled for tier but not spawned-vs-delivered for findings
  (abstraction up). `same bug, fix now`; local payload proof.
- Specialization down — the envelope requires binding be proven live per host;
  the parallel delivery claim had no such clause. `same bug, fix now`; runtime
  roundtrip proof (Probes A/B).
- Same layer — `2026-07-15-release-execute-noop-debug.md:68`, a nested call whose
  result never reached its caller. `same class, diagnostic-only`; static scan.
- Mental-model — `quality`/`release` SKILL.md say "verify after each reviewer
  returns" without defining *returns*. `valid follow-up outside the slice`.

## Seam Risk

- Interrupt ID: reviewer-result-delivery-2026-07-25
- Risk Class: external-seam, repeated-symptom
- Seam: parent-to-reviewer result delivery, owned by host runtime and selected by a caller-supplied spawn parameter; no repo code owns it.
- Disproving Observation: rail-1 boundary verify returned `{"ok": true, "drift": []}` through every round in which delivery failed, so a green local proof coexisted with total delivery loss.
- What Local Reasoning Cannot Prove: that any host actually delivers. Charness can influence the channel (spawn shape) and record the outcome (delivery state) but cannot guarantee it, and the channel mapping on unprobed hosts is unverified.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-07-25-reviewer-delivery-seam.md

Continued rather than interrupting: the differential was cheap, ran in-session,
and produced a working path immediately. Forward seam work — host-plural delivery
proof and the lesson-decay promotion gate — is handed to the spec above.

## Prevention

`## Result Delivery` in `skills/shared/references/fresh-eye-subagent-review.md`
now owns the unnamed one-shot spawn shape, "a spawned reviewer is not a received
review", typed closeout states (`findings-received` /
`spawn-accepted-no-delivery <signal>`) kept separable from boundary state, the
transcript read as diagnostic-only, and an availability probe that passes only
when findings arrive. Pinned by `tests/quality_gates/test_reviewer_result_delivery.py`
and enforced at closeout by the `Delivery state` floor in
`scripts/critique_reviewer_evidence.py`. Because the recurrence cause was lesson
decay, the rule sits in the contract, not in `recent-lessons.md`.

### Non-claims

- Codex / `explorer` delivery not inspected (the Claude envelope rail is already
  `unsupported` there). Envelope binding on the unnamed path is proven for this
  host only, and tier application there is `metadata-hidden`, not `applied`.
- #458: explicit `run_in_background: true` and concurrency stay uninspected; the named arm recurred 2026-07-27 (`n=2`) in `charness-artifacts/debug/2026-07-27-named-spawn-recurrence.md`.
- The `.claude/agents/bounded-reviewer.md` paragraph is **release-gated and not
  proven live**: reviewers this session ran the installed plugin cache copy, which
  predates the change. The rule therefore rides the parent-side spawn packet,
  which parents control immediately; the envelope text is reinforcement.

## Related Prior Incidents

Upstream: anthropics/claude-code#71723, *"Agent tool name parameter silently
switches to teammate protocol, losing background agent results"* — filed
2026-06-27, updated 2026-07-13, still OPEN. Its documented workarounds are the
two this repo reached independently: omit `name`, or run synchronously. So the
mechanism no longer rests on `n=1`-per-arm local evidence, and the charness rule
is a **workaround for a live upstream defect**, not a permanent fact. Revisit
when it closes: if named spawns deliver, the unnamed-shape rule can relax to a
preference, but the delivery invariant and floor stay regardless.

Repo-internal recurrence: `2026-06-20-north-star-phase4-boundary-non-terminality.md:36-41,89-91`
recorded this exact differential five weeks earlier and it decayed out of
`recent-lessons.md` before reaching a contract; `2026-07-16-scout-driven-improvement-retro.md:44-48`
then concluded "not repo fixable" and
`2026-07-17-prove-dogfood-via-444-polish-goal-session-retro.md:74-76` observed the
opposite and called it host-version-dependent. Neither connected the difference
to `name`. That decay is why the rule now lives in a contract and a validator
floor; the unaddressed class is booked as D38.
