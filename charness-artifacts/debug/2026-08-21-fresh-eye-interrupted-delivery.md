# Fresh-Eye Interrupted Delivery Debug Review
Date: 2026-08-21

## Problem

The bounded fresh-eye contract requires a received reviewer report before a
proof boundary can close. In the consumer-validator round-2 review, the first
reviewer and one unnamed retry produced no received final report; the parent
correctly left the boundary unproven.

## Correct Behavior

Given a bounded reviewer spawn, the parent must distinguish invocation,
execution, findings delivery, and non-delivery. When findings arrive in the
parent context, the review may be evaluated. When the child times out, is
interrupted, or is routed to an unread channel, the result must be a typed
non-delivery and must never become PASS, BLOCK approval, or same-agent review.

## Observed Facts

- `charness-artifacts/critique/rounds/2026-08-21-consumer-validator-round-2-retry.md`
  records two missing final reports, a clean retry boundary, and no fresh-eye
  PASS/BLOCK claim.
- The first attempt ran for more than ten minutes. The retry used an unnamed
  spawn, ran for about five minutes, and was interrupted without a report.
  The episode records do not contain a host event trace proving the exact
  `Interrupted` status.
- The existing Charness contract identifies named-spawn mailbox routing as a
  separate delivery defect and requires an unnamed one-shot shape.
- Adjacent Codex source at commit
  `53cec04646576d3a55d431b6d6820455a26ffd69` maps an interrupted turn to
  `AgentStatus::Interrupted`, excludes it from `is_final`, waits on that
  predicate in the completion watcher and v1 `wait_agent`, and formats no
  completion payload for it.
- Three read-only audits independently reached the same source-level boundary
  and all distinguished it from named-channel routing. They were audits, not
  the required fresh-eye approval.
- A first spec-critique attempt reported a prepared-packet SHA different from
  the parent-supplied SHA; a subsequent new angle spawn was refused with the
  host signal `agent thread limit reached`. Neither event is fresh-eye
  approval.
- R1 also passed `--path` to the issue source-preservation checker, which the
  CLI rejected; the declared `--body-file` form passed. A zsh wrapper used the
  read-only variable `status` after a producer succeeded; the corrected wrapper
  uses `rc`. Wrong call shape and shell-state errors are recorded as sibling
  boundary smells, not hidden behind the successful rerun.

## Reproduction

The live incident is preserved by the round record but is not replayable as an
episode-level host trace here. The source-level path is
reproducible with:

`git -C ../codex rev-parse HEAD` →
`53cec04646576d3a55d431b6d6820455a26ffd69`

and inspection of `codex-rs/core/src/agent/status.rs`,
`agent/control.rs`, `tools/handlers/multi_agents/wait.rs`, and
`session_prefix.rs`. The live disconfirmer is a host fixture or event
trace showing that an interrupted child does produce a parent-deliverable
terminal result.

## Candidate Causes

- Channel cause: a named spawn routes completion to a mailbox the parent does
  not read; the unnamed request shape prevents this class.
- Terminal-state cause: the host's `Interrupted` status is not final and has no
  completion payload, so interruption can end without a parent result.
- Invocation-boundary cause: the available collaboration API and the host's
  direct-tool delivery path may not share the same channel; this has not been
  proven causal for this episode.
- Workload cause: an oversized review or missing bounded completion prompt may
  make timeout/interruption more likely, without explaining a missing terminal
  record by itself.

## Hypothesis

There are two independent delivery classes: unnamed one-shot calls remove the
known named-channel risk, while an interrupted child can still lose
the canonical final result at the host terminal-state boundary.
`disconfirmer: obtain a runtime event trace or deterministic fake-host result in which AgentStatus::Interrupted reaches the parent as a typed terminal non-delivery; if that path is already delivered, this host-source hypothesis is false for the observed episode.`

## Verification

- Source-level host hypothesis: supported by the pinned Codex predicates and
  formatter paths.
- Named-channel-only hypothesis: insufficient; the retry was unnamed and still
  delivered no report.
- Exact runtime attribution: unproven; no episode trace establishes that both
  attempts reached `TurnAborted(Interrupted)`.
- Charness prevention boundary: supported by the existing unnamed-spawn rule,
  round record, and the need to separate received findings from silence.
- Spec-critique delivery: unproven; the first findings consumed a stale packet
  identity and the replacement spawn was host-blocked.

## Root Cause

The confirmed Charness-level root cause is an incomplete delivery contract:
spawn acceptance and clean boundary fingerprints are not findings delivery,
and the parent has no uniform typed terminal record for every non-delivery.
The Codex `Interrupted` path is a strong, separate host-level candidate that
can explain the observed symptom, but it is not claimed as the runtime cause
of every failed episode until an event trace is available.

## Invariant Proof

- Invariant: only findings received in the parent context can satisfy a
  fresh-eye proof boundary; every other terminal observation is non-delivery.
- Producer Proof: the spawn contract and round record preserve unnamed shape,
  boundary fingerprint, attempt, and the absence of a report.
- Final-Consumer Proof: current closeout records leave round-2 unproven, but
  no executable shared delivery ledger yet consumes host interruption states.
- Interface-Shape Sibling Scan: named mailbox routing, custom fingerprint
  handoff, auto-retro commit-range identity, and installed-layout command
  resolution all show that a successful producer signal is not sufficient
  without a consumer-readable continuation.
- Non-Claims: no fresh-eye approval, episode-level Interrupted trace, upstream
  Codex fix, hosted release, managed install proof, or issue closure is claimed.

## Detection Gap

The current gate detects an absent report only after a human records the retry;
it does not consume a host event stream or emit a typed delivery state during
the attempt. The critique packet runner also allowed a packet identity to drift
between preparation and reviewer read, and host capacity refusal has no
structured retry disposition. Add a repository-owned delivery ledger/fake-host
contract that records `findings-received`, `interrupted`, `timed-out`,
`host-channel-unreadable`, packet-mismatch, and capacity-blocked states
separately, and make closeout refuse approval for every non-delivery.

## Sibling Search

- Mental model: a reviewer result is a typed producer-to-parent message, not a
  boolean implied by spawn success or idle state.
- Same-layer axis: `fresh-eye-subagent-review.md` and
  `reviewer_result.py` | retain the named/unnamed distinction and add typed
  delivery readback | source contract and round records support the gap.
- Boundary axis: `reviewer_boundary_fingerprint.py` | keep tree-integrity proof
  independent from findings delivery | current clean fingerprints do not prove
  a report arrived.
- cross-file: `../codex/codex-rs/core/src/agent/status.rs` plus Charness
  critique rounds and closeout consumers; host terminal state and Charness
  prevention must remain separate owners.

## Seam Risk

- Interrupt ID: fresh-eye-interrupted-delivery-2026-08-21
- Risk Class: external-seam, host-disproves-local, repeated-symptom
- Seam: subagent spawn/wait/interruption status -> parent findings delivery -> fresh-eye closeout verdict
- Disproving Observation: a captured interrupted episode yields a typed,
  parent-readable terminal non-delivery and the Charness closeout consumes it
  without treating it as findings.
- What Local Reasoning Cannot Prove: the actual host event for each failed
  episode, cross-host delivery semantics, and whether the current API wrapper
  altered the channel.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-21-fresh-eye-delivery-boundary.md

## Prevention

Keep the proven unnamed one-shot request rule. Add a Charness-owned delivery
state machine and deterministic interrupted fake-host test before changing the
review/closeout contract. Record the exact host signal when available, bound
recovery to one retry, and keep all non-delivery states visibly unproven.
Bind the packet SHA and reviewed-input identity at spawn time, fingerprint the
parent boundary before and after, and record host capacity refusals as typed
non-delivery. Track the Codex terminal-state behavior in issue #687 without
claiming that a request prompt alone fixes it.
