---
name: debug
description: "Use when investigating a bug, error, or unexpected behavior. Follow a disciplined root-cause workflow, preserve a durable debug artifact so future sessions inherit what was learned, and do not jump to fixes before a falsifiable hypothesis exists."
---

# Debug

Use this when the goal is to understand and resolve incorrect behavior without
guessing.

Use George Pólya-style problem-solving discipline here: understand the exact
problem first, reduce it to the smallest honest failing case, enumerate
multiple plausible causes, and only then test the next hypothesis.

`debug` is part of the execution cluster, but its job is diagnosis before
repair. A bug investigation without a durable record only solves the current
incident and wastes the next one.

## Bootstrap

Resolve the adapter first, then read the current debugging context.

Resolve `SKILL_DIR` to the directory that contains this `SKILL.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/scaffold_debug_artifact.py" --repo-root . --json
```

By default, `debug` writes durable artifacts to `charness-artifacts/debug/`. Each
investigation gets its own file: `debug-{date}-{slug}.md`. Repos can override
the directory with `.agents/debug-adapter.yaml`.

Treat the scaffold helper as the canonical artifact contract shortcut:

- it prints the default artifact path
- it prints the required heading / section order
- it points at the standing validator command

Before stopping, run:

```bash
python3 "$SKILL_DIR/../../../scripts/validate-debug-artifact.py" --repo-root .
```

Before writing a new artifact, read existing `debug-*.md` files in the output
directory. If the current incident relates to a prior one, fill in the
`## Related Prior Incidents` section with a filename reference and one-line
summary.

```bash
# Required Tools: rg
# Missing-binary protocol: create-skill/references/binary-preflight.md
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
3. Build the smallest honest reproduction.
   - isolate the smallest input, path, or environment that still fails
   - if local reproduction fails, gather stronger observation instead of
     pretending the problem disappeared
4. Enumerate diverse causes.
   - list at least three plausible causes before verifying any one of them
   - include environment, dependency, state, and control-flow causes alongside
     obvious logic bugs
5. Test a falsifiable hypothesis.
   - state what should change if the hypothesis is true
   - make the smallest change or observation that can verify or falsify it
6. Resolve and preserve the learning.
   - record root cause
   - record the confirming evidence
   - classify seam risk explicitly when host behavior or repeated symptom fixes
     showed that local reasoning was not enough
   - if the incident hits an external seam, host-disproves-local behavior, or a
     repeated symptom on the same seam, set the next step to `spec` and name a
     spec handoff artifact instead of handing directly to ordinary `impl`
   - record prevention or follow-up
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
- `Seam Risk`
- `Interrupt Decision`
- `Prevention`
- `Related Prior Incidents` (optional — include when the incident connects to a
  prior debug artifact)

The canonical heading pattern is `# ... Debug ...`, and the canonical section
order is the validator order above. Prefer the scaffold helper over hand-typing
the skeleton from memory.

## Guardrails

- Do not edit the real fix before you can state the correct behavior and a
  falsifiable hypothesis.
- Do not paraphrase the exact error text away.
- Do not stop at the first plausible cause; enumerate multiple candidates first.
- Do not treat "cannot reproduce locally" as resolution. Record what was tried
  and what observation is still missing.
- Do not leave external-seam or host-disproves-local risk as free-form prose;
  carry it forward in the structured handoff fields so the next slice cannot
  quietly reset into ordinary implementation posture.
- Do not leave the learning only in chat when the repo has a durable debug
  artifact path or document style.
- Web search is the default tool for any "gather more information" step.

## References

- `references/adapter-contract.md`
- `references/five-steps.md`
- `references/debug-memory.md`
- `references/anti-patterns.md`
- `references/document-seams.md`
