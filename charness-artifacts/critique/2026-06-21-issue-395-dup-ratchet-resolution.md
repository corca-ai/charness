# Resolution Critique — issue #395 (dup-ratchet family_id rotation)

- Target reference: `code-critique` (resolution critique, recurrence focus)
- Packet consumed: `charness-artifacts/critique/2026-06-20-184913-packet.md`
- Fresh-Eye Satisfaction: parent-delegated (3 angle subagents + 1 counterweight, high-leverage)
- Prior context: causal review (SOUND) in `charness-artifacts/debug/2026-06-21-dup-ratchet-family-id-rotation.md`

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=opus (Claude Code host resolution of high-leverage; the critique adapter records the Codex-host mapping model=gpt-5.5, reasoning_effort=medium, service_tier=priority)
- Host exposure state: requested_fields_sent
- Application state: model=opus sent to all 4 bounded subagents (3 angles + counterweight) via the Agent tool; the host does not echo resolved spawn fields, so application is unverified-by-carrier (not claimed host-confirmed)

## Diff Scope

Doc correction of the false "family_id stable across sibling churn" claim across
3 carriers (`dup_ratchet_lib.py`, `nose_baseline_lib.py`,
`references/dup-ratchet.md`) + a real-nose characterization test + lockstep
re-baseline of both id-set baselines. Deferred: the gate id-rotation affordance
(solution c).

## Angles

- **Jackson (problem framing):** is doc-only solving the named problem (the
  forced re-baseline) or the convenient adjacent one (the doc lie)?
- **Weinberg (diagnostic):** is the cause located, and does the characterization
  test prove what it claims (not pass for the wrong reason)?
- **Gawande (operational):** does the re-baseline workflow / nose-gated test add
  a silent failure mode?

## Findings → Counterweight four-bin triage

**Act Before Ship (all applied in this commit):**
- Track deferred (c) in `docs/deferred-decisions.md` (D30) — was prose-only
  (Jackson; counterweight: a one-line backlog handle, not redundant ceremony).
- Hedge "membership" as a by-construction (not demonstrated) rotation trigger in
  `nose_baseline_lib.py` — it was asserted with the same confidence as the
  measured offset claim (Weinberg).
- Port the deferred-(c) false-negative caveat (a new clone reusing the same
  member files fingerprint-matches a vanished family → wrongly downgraded) into
  `references/dup-ratchet.md` (Weinberg).
- Document that both id-set baselines re-baseline in lockstep (Gawande, rated
  Act-Before-Ship; the advisory would otherwise go silently stale).

**Over-Worry (no change):** `dup-ratchet.md` "expected churn, not a defect"
wording — already names the limitation and the deferred affordance one line down
(counterweight overrode Jackson's softening request).

**Valid but Defer:** a tool affordance enforcing verify-before-re-baseline *is*
the deferred (c) (D30); a CI signal for nose-gated test skips is a separate
observability slice, not #395-specific.

**Confirmed sound (no action):** the characterization test guards against
false-pass (`len==1` before+after, sibling byte-identical, body > min-size 24);
the "same failure nose's `key` has" doc claim is accurate (Test 2 proved it on a
25-member family); baseline lockstep was executed correctly (identical id sets).

## Deliberately Not Doing

- The gate id-rotation affordance (solution c) — deferred to D30; needs a
  baseline schema migration and must guard the false-negative above.
- A CI "nose-gated suites skipped" observability signal — separate slice.
- Softening "expected churn, not a defect" — counterweight ruled it Over-Worry.

## Next Move

Commit the doc fix + characterization test + lockstep re-baseline with the four
Act-Before-Ship one-liners folded in; close #395 via direct-commit keyword;
verify CLOSED + render the behavioral verdict (characterization test green +
the dogfooded case-2 recovery on this commit).
