---
name: retro
description: "Use after a meaningful work unit or when the user asks for a retrospective. Reviews what happened, what created waste, which decisions mattered, what named experts in this domain would have done differently, and which workflow/capability/memory improvements should make the next session better. Auto-selects `session` or `weekly` mode from context; ambiguous cases default to `session`."
---

# Retro

Use this after a meaningful unit of work completes or when the user asks for a
retrospective.

## Bootstrap

Every invocation starts here.

```bash
# 1. basic repo and workflow context
sed -n '1,220p' docs/handoff.md
git status --short
git log --oneline -10

# 2. adapter resolution
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .

# 3. first-run scaffold when needed
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

Adapter policy:

- If the adapter is missing and the request is session-like, continue with
  inferred defaults.
- If the adapter is missing and the request is weekly-like, metrics-heavy, or
  explicitly asks for durable artifacts, create `.agents/retro-adapter.yaml`
  first, then continue.
- If the adapter is invalid, repair it using `references/adapter-contract.md`
  before relying on adapter-defined paths or metrics.
- Never block a `session` retro solely because the adapter is missing.

## Workflow

1. Select the mode.
   - explicit user wording wins
   - `this session`, `this task`, `what just happened` => `session`
   - `this week`, `sprint`, `recent pattern` => `weekly`
   - if still ambiguous, default to `session`
2. Gather evidence in this order.
   - current thread, current task, changed files, recent commits
   - existing handoff or prior retro artifacts when they matter
   - adapter-defined `evidence_paths`
   - adapter-defined `metrics_commands` only when they sharpen a weekly claim
3. Write the core retro.
   - `Context`: what unit of work is being reviewed and what matters next
   - `Waste`: where time, clarity, or trust was lost
   - `Critical Decisions`: which decisions changed outcome or constrained later work
   - `Expert Counterfactuals`: what 1-2 named experts in this domain would likely
     have done differently
   - `Next Improvements`: concrete changes for the next session
4. Make `Next Improvements` concrete.
   - `workflow`: change the sequence, gate, or review habit
   - `capability`: add or adjust a skill, tool, adapter, preset, or automation
   - `memory`: write the lesson into a durable artifact so it is not relearned
5. Persist when there is a durable home.
   - if `output_dir` exists or the adapter defines one, update the retro artifact
   - otherwise still give the user a concise retro in chat

## Expert Counterfactual Rule

- Every retro must include at least one expert counterfactual.
- Prefer two named experts with distinct lenses when the session had meaningful
  tradeoffs.
- If sub-agents are available and the session warrants depth, use two named
  expert sub-agents.
- If sub-agents are unavailable or too expensive for the session weight, write
  the two named counterfactuals inline.
- Do not use expert names as decoration. Each expert must produce a different
  changed action, constraint, or question.

## Guardrails

- Separate observed facts from proposed improvements.
- Do not fabricate metrics when the adapter does not provide a real source.
- Weekly retros may stay narrative without metrics, but must say so explicitly.
- Capability suggestions exist to reduce future waste, not to show tool awareness.
- Do not let the retro turn into a generic postmortem when the user asked for a
  short session review.
- If no improvement is proposed, explain why the current workflow should remain
  unchanged.

## References

- `references/adapter-contract.md`
- `references/mode-guide.md`
- `references/section-guide.md`
- `references/expert-lens.md`
