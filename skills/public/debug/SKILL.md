---
name: debug
description: "Use when investigating a bug, error, reported review finding, or unexpected behavior that needs root cause, Five Whys, or recurrence analysis. Follow a disciplined root-cause workflow, adversarially verify the report, preserve a durable debug artifact so future sessions inherit what was learned, and do not jump to fixes before a falsifiable hypothesis exists."
---

# Debug

Use this when the goal is to understand and resolve incorrect behavior without guessing.

`debug` is diagnosis before repair; without a durable record an investigation
only solves the current incident. When the input contains a prior critique or
review report, `debug` first verifies each claim with a disconfirming stimulus
and then climbs from the concrete failure to its structural siblings. `debug`
is callable directly when no GitHub issue exists; bug-class `issue resolve`
invokes the same RCA substrate through `../issue/references/causal-review.md`,
whose lenses map onto the debug steps below.
Do not run critique before the facts needed for diagnosis exist. Once a debug
slice closes repo work, hands off a fix, or authorizes repair, record the
required critique before closeout so the next move does not inherit an
untested repair story.

## Bootstrap

Resolve the adapter and run the planner before broad search, artifact edits, or
repair.

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/plan_debug_run.py" --repo-root .
python3 "$SKILL_DIR/scripts/scaffold_debug_artifact.py" --repo-root .
```

By default, `debug` writes durable artifacts to
`<repo-root>/charness-artifacts/debug/`; repos can override the directory with
`<repo-root>/.agents/debug-adapter.yaml`. The planner names the current artifact
status, related prior incidents, seam-risk interrupt posture, required reads,
on-demand reads, gate packets, and next action.

Follow the planner's `next_action`; its scaffold JSON is canonical for write target,
pointer role, section order, word budget, and validator. Write the emitted
`write_artifact_path` within `size_budget.max_words`. For continuation pass
`--subject <slug>`; without it the run is NEW. Interpret `write_artifact_subject_match`,
`write_artifact_effect`, `write_artifact_role`, and `intent` together: the effect
distinguishes `overwrite_existing_content` from `create_new_file`; `unknown`,
`not exhaustive`, and `refused_write_artifact_path` remain non-claims.

Before stopping, run the emitted `validator_command` (never a guessed path); it validates the current pointer's designated artifact strictly, names the failing path, and leaves other dated records as legacy memory.

```bash
# Required Tools: rg
# Missing-binary protocol: ../../shared/references/binary-preflight.md
# After the planner's required reads, gather only the clues the diagnosis needs.
rg -n "error|incident|debug|root cause|repro|stack trace|failure" .
git status --short
```

Read planner-listed prior incidents before diagnosing and record those that
shape the current hypothesis.

## Reported-Finding Mode

For review findings or suspected false-green approvals, read `../critique/references/adversarial-evidence-review.md`, preserve IDs, and type
each report `reproduced`, `disconfirmed`, `unproven`, or `not-applicable` before
changing code; no consumer observation means `unproven`. Run the planner/scaffold
with `--evidence-led` so the template and emitted validator are bound to the
typed sections; reproduced records need a receipt, `debug` handoff, and next move.

## Pattern Ladder

For every reproduced or recurring finding, use `references/pattern-ladder.md`: record observed failure → local pattern → interface sibling → pattern of patterns → structural prevention; each level needs location, proof, and disconfirmation.

## Workflow

1. Define the problem.
   - write a one-line problem statement
   - name the user or operator capability that failed when it matters
   - capture the exact symptom, error text, or failing behavior verbatim
2. Define correct behavior.
   - write what should happen in given/when/then form
   - state the capability restored by that correct behavior
   - separate observed facts from assumptions or prior knowledge
   - use web search by default for exact error text and likely causes
   - for async, scheduled, or user-visible workflows, separate pre-worker
     acknowledgement, worker execution, and post-worker side effects; identify
     the earliest component that can produce observable status before reasoning
     only about worker behavior
   - before absence, attribution, liveness, or frequency claims, run the
     cheapest falsifier first (`references/disconfirmer-first.md`); for named
     targets, verify runtime state (`references/named-target-verification.md`)
3. Adversarially verify active reports: run each claim's smallest stimulus
   through the final consumer and record disposition, output, and proof.
4. Build the smallest honest reproduction.
   - isolate the smallest input, path, or environment that still fails
   - if local reproduction fails, gather stronger observation instead of
     pretending the problem disappeared
5. Enumerate diverse causes.
   - list at least three plausible causes before verifying any one of them
   - include environment, dependency, state, control-flow, and — when the
     symptom is a verdict — the verifier (`references/detection-gap.md`)
   - walk from symptom to structural cause per
     `references/five-whys-causal-chain.md`
   - complete the Pattern Ladder before naming a root cause; nearby keywords are
     not siblings
6. Test a falsifiable hypothesis.
   - state what should change if the hypothesis is true
   - make the smallest change or observation that can verify or falsify it
7. Resolve and preserve the learning.
   - record root cause and the confirming evidence
   - for workflow-boundary bugs, propagated diagnostics, or readiness decisions,
     name the producer-to-final-consumer invariant per
     `references/invariant-first-review.md`; producer-only proof is not
     end-to-end workflow proof
   - walk the existing detection surface per `references/detection-gap.md` and
     record which gate did not fire and the smallest change that would have
     fired it
   - walk the four-axis sibling scan per `references/sibling-search.md`,
     name the wrong mental model, classify each sibling decision, and record
     proof level separately from the decision
   - persist `valid follow-up outside the slice` siblings with a `follow-up:`
     identifier per `references/sibling-search.md`; missing it blocks closeout
   - trivial single-file fixes may record `n/a — trivial fix` in detection-gap
     and sibling-search sections; this is reviewer-visible, not a default escape
   - classify seam risk explicitly when host behavior or repeated symptom fixes
     showed that local reasoning was not enough
   - external-seam, host-disproves-local, or repeated-symptom incidents set the
     next step to `spec` with a named handoff artifact, not ordinary `impl`
   - record prevention or follow-up; the prevention move should map to the
     detection-gap and sibling-search outputs, not restate the root cause
   - when the investigation is concluded (bug fixed or handed off), set
     `- Resolution: resolved` in the `Interrupt Decision` section so the next
     debug run treats this closed `latest.md` pointer as prior memory, not an
     open continuation; leave it `open` only while the bug is genuinely still
     in progress (a stale `open` pointer is what hijacks a fresh bug)
   - before closing task-completing debug work or handing off a repair, record
     the required critique as short scoped diagnosis/repair risk or full
     standalone review when the fix affects design, workflow, compatibility,
     host-proof, prompt-surface, public-skill, validator, or export behavior
   - at closeout, if the fix surfaced an RCA-class event and the repo maintains
     the conversion ledger, append one RCA event per `../../shared/references/rca-ledger-append.md` (`--source debug`); silent no-op otherwise
   - if the fix belongs to normal implementation work, hand off cleanly to
     `impl` with the debug artifact still intact

## Output Shape

The durable debug artifact should usually include:

- `Problem`
- `Capability Failure`
- `Correct Behavior`
- `Observed Facts`
- `Reported Findings` / `Adversarial Verification` (when active)
- `Reproduction`
- `Candidate Causes`
- `Hypothesis`
- `Pattern Ladder` (for reproduced or recurring findings)
- `Verification`
- `Root Cause`
- `Invariant Proof`
- `Detection Gap`
- `Sibling Search`
- `Seam Risk`
- `Interrupt Decision`
- `Prevention`
- `Related Prior Incidents` (optional)

The canonical heading pattern is `# ... Debug ...`, and the canonical section
order is the validator order above for `latest.md`. Historical dated records
may keep older extra sections, but they still need the core debug memory
sections. Prefer the scaffold helper over hand-typing the skeleton from memory.

## Guardrails

- Apply disciplined-RCA hygiene: no fix before a falsifiable hypothesis, the exact
  error preserved, multiple candidate causes, a minimal reproduction,
  web-search-first, and the artifact kept past the fix. If one of these slips, stop
  and repair the process before changing more code.
- Counterweight is not adversarial verification; every report needs a typed
  disposition, and one symptom needs a sibling, seam observation, or `unproven`.
- Do not leave external-seam or host-disproves-local risk as free-form prose;
  carry it forward in the structured handoff fields so the next slice cannot
  quietly reset into ordinary implementation posture.

## References

- `references/adapter-contract.md`
- `references/five-steps.md`
- `references/five-whys-causal-chain.md`
- `../critique/references/adversarial-evidence-review.md`
- `references/pattern-ladder.md`
- `references/invariant-first-review.md`
- `references/detection-gap.md`
- `references/sibling-search.md`
- `references/debug-memory.md`
- `references/document-seams.md`
- `references/disconfirmer-first.md`
- `references/named-target-verification.md`
- `../../shared/references/rca-ledger-append.md`
- `scripts/plan_debug_run.py`
