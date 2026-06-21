---
name: debug
description: "Use when investigating a bug, error, or unexpected behavior. Follow a disciplined root-cause workflow, preserve a durable debug artifact so future sessions inherit what was learned, and do not jump to fixes before a falsifiable hypothesis exists."
---

# Debug

Use this when the goal is to understand and resolve incorrect behavior without guessing.

`debug` is part of the execution cluster, but its job is diagnosis before
repair. A bug investigation without a durable record only solves the current
incident and wastes the next one. `debug` is callable directly when no
GitHub issue exists; bug-class `issue resolve` invokes the same RCA substrate
through `../issue/references/causal-review.md`, whose lenses map onto the debug
steps below (so each step states its substrate once, not per lens).
Do not run critique before the facts needed for diagnosis exist. Once a debug
slice closes repo work, hands off a fix, or authorizes repair, record the
required critique before closeout so the next move does not inherit an
untested repair story.

## Bootstrap

Resolve the adapter first, then read the current debugging context.

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/scaffold_debug_artifact.py" --repo-root . --json
```

By default, `debug` writes durable artifacts to `<repo-root>/charness-artifacts/debug/`. Each
investigation gets its own file: `debug-{date}-{slug}.md`. Repos can override
the directory with `<repo-root>/.agents/debug-adapter.yaml`.
The scaffold helper emits the current pointer artifact, usually `latest.md`.
When the investigation becomes durable history, preserve it as a dated record
using the same core debug sections.
Edit the scaffold payload's `write_artifact_path`, not `latest.md` by habit; it
resolves a symlinked current pointer to its actual target.

The helper's JSON is the canonical artifact contract — it carries the safe write
target, current-pointer role, required heading/section order, and the validator
command for the installed Charness layout (consumer repos do not copy Charness
validator scripts into their own `scripts/`). Use it instead of hand-typing the
skeleton.

Before stopping, run the `validator_command` emitted by the scaffold helper.
Do not replace it with a guessed repo-local scripts path unless the emitted
command already points there. The validator treats `latest.md` as the strict
current schema and historical debug records as legacy debug memory; when a
record fails, the error names the artifact path.

Before writing a new artifact, read existing `debug-*.md` files in the output
directory. If the current incident relates to a prior one, fill in the
`## Related Prior Incidents` section with a filename reference and one-line
summary.

```bash
# Required Tools: rg
# Missing-binary protocol: ../../shared/references/binary-preflight.md
# 1. recent context and adjacent contracts
rg --files docs skills
sed -n '1,220p' <resolved-debug-artifact> 2>/dev/null || true
rg -n "Current Slice|Success Criteria|Acceptance Checks|Fixed Decisions|Probe Questions|Deferred Decisions" .

# 2. existing debug notes, incident docs, or failure reports
rg -n "error|incident|debug|root cause|repro|stack trace|failure" .

# 3. current runtime clues
git status --short
```

If a similar past debug artifact exists, read it first. Treat prior debug notes
as codebase memory rather than as stale trivia.

## Workflow

1. Define the problem.
   - write a one-line problem statement
   - capture the exact symptom, error text, or failing behavior verbatim
2. Define correct behavior.
   - write what should happen in given/when/then form
   - separate observed facts from assumptions or prior knowledge
   - use web search by default for exact error text and likely causes
   - for async, scheduled, or user-visible workflows, separate pre-worker
     acknowledgement, worker execution, and post-worker side effects; identify
     the earliest component that can produce observable status before reasoning
     only about worker behavior
   - before absence, attribution, liveness, or frequency claims, run the
     cheapest falsifier first (`references/disconfirmer-first.md`); for named
     targets, verify runtime state (`references/named-target-verification.md`)
3. Build the smallest honest reproduction.
   - isolate the smallest input, path, or environment that still fails
   - if local reproduction fails, gather stronger observation instead of
     pretending the problem disappeared
4. Enumerate diverse causes.
   - list at least three plausible causes before verifying any one of them
   - include environment, dependency, state, and control-flow causes alongside
     obvious logic bugs
   - walk from symptom to structural cause per
     `references/five-whys-causal-chain.md`
5. Test a falsifiable hypothesis.
   - state what should change if the hypothesis is true
   - make the smallest change or observation that can verify or falsify it
6. Resolve and preserve the learning.
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
   - trivial single-file fixes may record `n/a — trivial fix` in the detection
     gap and sibling-search sections; reviewer-visible, not a default escape
   - classify seam risk explicitly when host behavior or repeated symptom fixes
     showed that local reasoning was not enough
   - if the incident hits an external seam, host-disproves-local behavior, or a
     repeated symptom on the same seam, set the next step to `spec` with a named
     handoff artifact instead of handing directly to ordinary `impl`
   - record prevention or follow-up; the prevention move should map to the
     detection-gap and sibling-search outputs, not restate the root cause
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
- `Correct Behavior`
- `Observed Facts`
- `Reproduction`
- `Candidate Causes`
- `Hypothesis`
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
  web-search-first, and the artifact kept past the fix. The full anti-pattern list
  lives in `references/anti-patterns.md`.
- Do not leave external-seam or host-disproves-local risk as free-form prose;
  carry it forward in the structured handoff fields so the next slice cannot
  quietly reset into ordinary implementation posture.

## References

- `references/adapter-contract.md`
- `references/five-steps.md`
- `references/five-whys-causal-chain.md`
- `references/invariant-first-review.md`
- `references/detection-gap.md`
- `references/sibling-search.md`
- `references/debug-memory.md`
- `references/anti-patterns.md`
- `references/document-seams.md`
- `references/disconfirmer-first.md`
- `references/named-target-verification.md`
- `../../shared/references/rca-ledger-append.md`
