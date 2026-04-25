---
name: retro
description: "Use after a meaningful work unit or when the user asks for a retrospective. Reviews what happened, what created waste, which decisions mattered, which named expert lens or direct counterfactual would have changed the next move, and which workflow/capability/memory improvements should make the next session better. Auto-selects `session` or `weekly` mode from context; ambiguous cases default to `session`."
---

# Retro

Use this after a meaningful unit of work completes or when the user asks for a
retrospective.

If the user correctly points out a missed issue, broken assumption, or missing
gate that the current workflow should likely have caught, run a short
`session` retro before continuing. Keep it bounded to the miss that was just
revealed; do not turn every correction into a long postmortem.

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
  explicitly asks for durable artifacts, create `<repo-root>/.agents/retro-adapter.yaml`
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
   - for `weekly`, the most recent durable weekly retro under `output_dir` when one exists
   - adapter-defined `evidence_paths`
   - for host-log-derived efficiency signals, prefer
     `$SKILL_DIR/scripts/probe_host_logs.py` before claiming turns, tokens, or tool-call
     counts; pass `--repo-root .` when probing the current repo
   - adapter-defined `metrics_commands` only when they sharpen a weekly claim
3. Write the core retro.
   - `Context`: what unit of work is being reviewed and what matters next
   - `Window`: for `weekly`, the time window being summarized
   - `Evidence Summary`: which durable artifacts, commands, or metrics actually informed the retro
   - `Waste`: where time, clarity, or trust was lost
   - `Critical Decisions`: which decisions changed outcome or constrained later work
   - `Trends vs Last Retro`: for `weekly`, compare against the last durable weekly retro when one exists
   - `Expert Counterfactuals`: what 1-2 counterfactual lenses, named experts
     when useful, would likely have done differently
   - `Next Improvements`: concrete changes for the next session
   - `Persisted`: whether the retro was written to a durable artifact, and if
     not, why not
4. Make `Next Improvements` concrete.
   - `workflow`: change the sequence, gate, or review habit
   - `capability`: add or adjust a skill, tool, adapter, preset, or automation
   - `memory`: write the lesson into a durable artifact so it is not relearned
5. Persist when there is a durable home.
   - if `output_dir` exists or the adapter defines one, persist the retro artifact with `$SKILL_DIR/scripts/persist_retro_artifact.py` instead of ad hoc file writes
   - if `weekly` and the adapter defines `snapshot_path`, write a compact machine-readable snapshot with the window, evidence sources, and any real metrics or deltas you used
   - if the adapter defines `summary_path`, `$SKILL_DIR/scripts/persist_retro_artifact.py` should refresh the compact recent-lessons digest automatically from the written durable artifact
   - otherwise still give the user a concise retro in chat
   - never stop without stating `Persisted: yes <path>` or `Persisted: no <reason>`

## Output Shape

The result should usually include:

- `Mode`
- `Context`
- `Window` for `weekly`
- `Evidence Summary` for `weekly`
- `Waste`
- `Critical Decisions`
- `Trends vs Last Retro` for `weekly` when prior evidence exists
- `Expert Counterfactuals`
- `Next Improvements`
- `Persisted`

## Auto-Retro Trigger

- Trigger a short `session` retro automatically when a user correction exposes a
  real miss in the workflow, not just a preference difference.
- Also trigger a short `session` retro after slice closeout when
  `$SKILL_DIR/scripts/check_auto_trigger.py` reports `triggered: true` for the current
  repo (for example via `python3 "$SKILL_DIR/scripts/check_auto_trigger.py" --repo-root .`).
  Keep this bounded to the configured repeat-trap seam rather than turning
  every slice into a postmortem.
- Treat valid examples such as:
  - missing local enforcement that the agent claimed existed
  - a wrong ownership or source-of-truth assumption
  - a broken or missing gate that should have been checked
  - a fresh-eye reader misread an invariant that is present in the code, revealing that the invariant still relies on convention rather than declaration
  - install/update/support/export/discovery slices that match the adapter's
    `auto_session_trigger_surfaces` or `auto_session_trigger_path_globs`
- Do not trigger the full retro flow for:
  - wording preferences
  - open product tradeoffs the agent already marked as unresolved
  - minor factual slips that do not reveal a workflow or guardrail gap
- The retro may stay inline and short, but it must still include `Persisted`.

## Expert Counterfactual Rule

- Every retro must include at least one counterfactual lens.
- Prefer named experts only when the name sharpens a different changed action,
  constraint, or question.
- When the core miss is decision quality under uncertainty, Gary Klein +
  Daniel Kahneman is a reasonable pair unless a more domain-specific lens fits
  better.
- If sub-agents are available and the session warrants depth, use up to two
  named-expert sub-agents with clearly different lenses.
- If sub-agents are unavailable, too expensive for the session weight, or
  names add little, write the counterfactuals inline without forcing personas.
- Do not use expert names as decoration. Each expert must produce a different
  changed action, constraint, or question.

## Guardrails

- Separate observed facts from proposed improvements.
- Do not fabricate metrics when the adapter does not provide a real source.
- Weekly retros may stay narrative without metrics, but must say so explicitly.
- If no prior weekly retro exists, say so explicitly instead of implying a trend line.
- Capability suggestions exist to reduce future waste, not to show tool awareness.
- Do not let the retro turn into a generic postmortem when the user asked for a
  short session review.
- Do not claim persistence implicitly; name the durable path or the reason it
  remained chat-only.
- Do not invent hidden machine formats. Only write a weekly snapshot when the adapter gives an explicit `snapshot_path`.
- If no improvement is proposed, explain why the current workflow should remain
  unchanged.

## References

- `references/adapter-contract.md`
- `references/mode-guide.md`
- `references/section-guide.md`
- `references/expert-lens.md`
- `references/trigger-and-persistence.md`
- `references/weekly-trends.md`
