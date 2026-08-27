---
name: critique
description: "Use when a non-trivial design decision, code change, release, rename, deletion, spec, or workflow change needs a before-the-fact critique, or when reported review findings need approval-oriented evidence disposition. Probe distinct failure angles, then run a counterweight pass that separates real blockers from over-worry before the change locks in."
---

# Critique

Use this when the next risk is not implementation detail alone, but locking the
wrong change or carrying the wrong fear into the next slice.

`critique` is the structured before-the-fact counterpart to `retro`. Critique
is selected for consequential decisions, not routine micro-slices. Once
selected, the default substrate is two bounded fresh-eye reviewers run in
parallel, with materially different perspectives or scopes, followed by a
parent-owned counterweight pass. The orchestrator chooses the perspectives,
judges both delivered results, and integrates the findings; selection and
reviewer count are not encoded by filenames, diff size, labels, keywords, or
other mechanical heuristics. A single reviewer is an explicit, explained
exception only when the second perspective cannot add independent evidence.
Decision pre-mortem (Klein lineage) is one of those targets; code/PR critique,
release critique, rename critique, and spec critique reuse the same substrate.
When a caller brings an already-observed failure or a review report, the
optional evidence-led path verifies that report before debating the repair; it
is not a replacement for fresh-eye judgment or for `debug`'s causal record.

Critique is selected by risk, not by the fact that a task completed. When it is selected, scale the pass, not the obligation: use the risk boundary or meaningful slice as the review unit, not every commit. See `references/cadence.md`.

Compatibility contract: When this standalone `critique` skill runs, its default fresh-eye execution is a Charness-owned
file-backed worker. There is no same-context local standalone `critique` variant.
The rule is: apply the stop-instead-of-local-substitute rule when neither the configured
worker nor the optional typed-subagent path can provide a separate fresh-eye context.
Adapter, typed-carrier, and refusal details live in
`references/adapter-contract.md` and `../../shared/references/fresh-eye-subagent-review.md`.

Use `$SKILL_DIR/scripts/run_review.py` for the semantic review path; its packet, lineage, and lifecycle-carrier contract is in `references/prepare-packet.md`.

Delegated reviewer fast path: read
`../../shared/references/disposition-reviewer-brief.md` before treating the
canonical path as blocked.

Caller contract: pass a pending artifact or tight source summary, state success,
out-of-scope lines, and the scaffold's `Verification Scope Decision` (claim,
consumer closure, minimum proof, omitted checks, verifier contract, and failure
classification). Question the verifier itself, consume the four-bin triage
(`Act Before Ship`, `Bundle Anyway`, `Over-Worry`, `Valid but Defer`), and write
change-affecting results back into the durable contract. Record typed `Fresh-Eye
Satisfaction`; see `references/cadence.md` for the bounded follow-up rule,
negative controls, retry identity, and stop rule.

Autonomous trigger: if no pending artifact or source summary is supplied, do
not ask first by default; follow `references/autonomous-trigger.md`, infer a
bounded target with low inference risk when repo evidence converges, and ask
only when ambiguity changes the target reference, stakes, or effects.

## Target Selection

Pick the reference that matches the change. The target reference owns the
angle distribution, the counterweight-bin specifics, and the output shape;
the substrate (angles + counterweight + four bins) is shared.

| Trigger phrase                                  | Reference                          |
|-------------------------------------------------|------------------------------------|
| `decision premortem`, design lock-in            | `references/premortem-decision.md` |
| `code critique`, PR/commit/snippet/repo review  | `references/code-critique.md`      |
| `release critique`, release lock-in             | `references/release-critique.md`   |
| `rename critique`, deletion, slug churn         | `references/rename-critique.md`    |
| `spec critique`, pre-impl spec lock-in          | `references/spec-critique.md`      |

If the call is ambiguous, ask which target reference applies before selecting
the review focus. Do not silently pick a target that changes the output.

## Evidence-Led Mode

Activate this path for a reported failure, false-green finding, repeated symptom, or explicit reality check. Read `references/adversarial-evidence-review.md`;
preserve each claim's expected behavior and stimulus, then type it
`reproduced`, `disconfirmed`, `unproven`, or `not-applicable`. Run the scaffold
with `--evidence-led` so its template and emitted validator carry the typed
sections. The final consumer must observe the result through a receipt bound to
the claim before approval; hand reproduced/repeated interface-shape findings to
`debug`, keeping `unproven` as a non-claim.

## Bootstrap

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`. Read only
the smallest change surface that makes the next move legible.
For no-argument slash-command use, run the autonomous trigger scan first.

If `<repo-root>/.agents/critique-adapter.yaml` declares ≥1 `packet_sections`, run the
prepare runner once before starting the reviewer (see `references/prepare-packet.md`).

```bash
# Required Tools: rg
# Missing-binary protocol: ../../shared/references/binary-preflight.md
rg --files docs skills
rg -n "spec|decision|follow-up|non-goal|out of scope|acceptance|risk|rename|delete|remove|migration" .
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/prepare_packet.py" --repo-root . --prepared-for "<short label>"
```

If a current spec, plan, PR proposal, issue, diff, or release artifact already
exists, use that as the change contract. Do not restate the whole project
history.

## Workflow

1. Restate the pending change.
   - what is being changed, removed, or locked
   - what capability or failure is at stake; what would count as success
   - what is explicitly out of scope for this pass
2. If evidence-led review is active, normalize each report, run its smallest
   deletion/omission/skip/mutation/stale-input/package stimulus, and record the
   typed disposition plus final-consumer output before counterweight triage.
3. Pick one bounded review boundary that matches the named risk, then assign
   two materially different reviewer perspectives or scopes within it. A
   single reviewer requires an explicit explanation of why the second
   perspective cannot add independent evidence.
   - use the target reference's `Anchor Angle Distribution`; see also
     `references/angle-selection.md`
4. Run the angle pass with the two reviewers in parallel.
   - Resolve the adapter's fresh-eye branch, consume its typed carrier, and bind
     packet identity; caller flags cannot cross that branch.
   - use two bounded fresh-eye reviewers with materially different perspectives
     or scopes, and consume both typed delivered results. Raw same-context
     substitutions are refused. A delivered `block` or `defer` is recorded as
     evidence but is not approval. For a shared, untyped reviewer, the shared
     fingerprint helper snapshots and verifies parent git state; typed
     read-only or isolated execution needs no extra fingerprint. Mismatched
     snapshots refuse.
5. Collapse the findings into one candidate concern list.
   - deduplicate overlap
   - keep evidence and cited source paths with each concern when available
   - prefer concerns that would change the next move, not generic worry
6. Perform the counterweight pass while integrating the findings: triage each
   concern with `references/counterweight-triage.md` and preserve all four bins.
   A separate counterweight worker is optional and only justified by its own
   independent evidence axis.
7. Persist any change-affecting concern in the spec, plan, diff, or rename
   contract; record rejected recurring concerns in `Deliberately Not Doing`.
8. End with the next move.
   - what must change before implementation, merge, or release
   - what can be bundled cheaply
   - what is over-worry and should be ignored
   - what is valid but explicitly deferred

## Output Shape

The result should usually include:

- `Execution`
- `Fresh-Eye Satisfaction`
- `Packet Consumed` — `<path>`, `n/a (no adapter sections)`, or
  `blocked <reason>` per `references/prepare-packet.md`
- `Reviewed Input Identity` — packet path, exact packet SHA-256, and input
  identity SHA-256 when a packet was consumed
- `Target` — which reference shaped this run
- `Change`
- `Capability at Stake`
- `Evidence Disposition` (when active; identity/count/coverage/digest)
- `Adversarial Verification` (stimulus, observed output, and proof level)
- `Angles`
- `Findings`
- `Counterweight Triage` (optional `Structured Findings` per `references/counterweight-triage.md`)
- `Deliberately Not Doing`
- `Next Move`

The target reference's `Output Shape` section names additional sections
required for that target (for example, release surface-lock inventory or
rename title/slug coherence review evidence).

If the configured worker path blocks before execution, report
`Execution: blocked <host-signal>` and the next move; record
`Fresh-Eye Satisfaction: worker-delivered` only after the typed worker report
is approval-eligible and the artifact records its report carrier, packet
identity, and result identity. Use `parent-delegated` or `nested-delegated` only
when the adapter explicitly selected a typed-subagent path and the findings text
reached the parent context. A same-agent short critique is never either claim.
When a repair materially changes the reviewed risk on a proof or verdict
surface, one follow-up fresh-eye review may read the repaired surface. Do not
repeat review when the repair does not materially change that risk.

## Guardrails

- Do not turn critique into broad ideation. Start from an actual pending
  change.
- Do not treat the counterweight pass as adversarial evidence. Counterweight
  triages concern cost; only a recorded stimulus and final-consumer observation
  can establish a reported failure.
- `unproven` is a typed non-claim, not a softened approval. If the report is a
  repeated seam symptom, hand it to `debug` even when the local reproduction is
  unavailable.
- Keep the counterweight pass owned, not a paranoia backlog: triage every concern into the four bins, never skip it or treat all concerns as equal, and don't add
  an angle without a genuinely independent evidence axis. Persist rejected-but-recurring concerns
  to `Deliberately Not Doing` (Workflow step 6), not chat. See
  `references/counterweight-triage.md`.

## References

- `references/premortem-decision.md`
- `references/code-critique.md`
- `references/release-critique.md`
- `references/rename-critique.md`
- `references/spec-critique.md`
- `references/cadence.md`
- `references/autonomous-trigger.md`
- `references/confirmed-input-over-anchoring.md`
- `references/angle-selection.md`
- `references/counterweight-triage.md`
- `references/adversarial-evidence-review.md`
- `references/prepare-packet.md`
- `references/adapter-contract.md`
- `../../shared/references/agent-assessment-invariant.md`
- `../../shared/references/fresh-eye-subagent-review.md`
