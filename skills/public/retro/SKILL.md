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

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`. Every
invocation starts here.

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
python3 "$SKILL_DIR/scripts/prepare_packet.py" --repo-root . --prepared-for "<short label>" --json
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

1. Select the retro shape.
   - explicit user wording wins
   - `this session`, `this task`, `what just happened` => `session`
   - `this week`, `sprint`, `recent pattern` => `weekly`
   - if still ambiguous, default to `session`
2. Gather evidence in this order.
   - current thread, current task, changed files, recent commits
   - existing handoff or prior retro artifacts when they matter
   - for `weekly`, the most recent durable weekly retro under `output_dir` when one exists
   - adapter-defined `evidence_paths`
   - for host-log-derived efficiency signals, prefer `$SKILL_DIR/scripts/probe_host_logs.py`
     (`--repo-root .`) before claiming turns, tokens, or tool-call counts, and
     `$SKILL_DIR/scripts/audit_codex_session.py` for Codex session detail — as
     evidence producers, not waste conclusions. Pass `--session-id <id>` or
     `--session-file <path>` to read the full session JSONL directly; pass
     `probe_host_logs.py --goal-path <artifact>` (when the goal carries a
     `Host metric window:` line) for a scoped `goal_window_audit`; add
     `--format markdown` for the provider-safe measured-vs-proxy closeout block.
     The measured / proxy / unavailable signal distinctions live in
     `references/phase-aware-efficiency.md`.
   - adapter-defined `metrics_commands` only when they sharpen a weekly claim
   - if the adapter declares `packet_sections`, run
     `$SKILL_DIR/scripts/prepare_packet.py` once and read the markdown packet
     before writing lessons; see `references/prepare-packet.md`
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
   - for token, tool-call, broad exploration, or efficiency claims, apply
     `references/phase-aware-efficiency.md` before labeling work as waste
4. Make `Next Improvements` concrete.
   - `workflow`: change the sequence, gate, or review habit
   - `capability`: add or adjust a skill, tool, adapter, preset, or automation
   - `memory`: write the lesson into a durable artifact so it is not relearned
   - when a lesson names a *transferable* waste pattern (one that could recur in
     another skill, script, doc, or workflow), scan for siblings before
     declaring the lesson learned and record the result in a `## Sibling Search`
     section of the per-session artifact; narrowly local waste uses the
     `n/a — trivial fix; no plausible siblings` short-circuit. The four-axis
     scan, four-decision taxonomy, follow-up identifiers, and the section-gated
     validator are owned by `references/waste-sibling-scan.md`
   - when an improvement is headed for an issue, classify it on two axes — a
     generalized `Structural pattern:`+`Triggering instance(s):` and a
     `Destination:`, owned by `../../shared/references/retro-issue-destination-split.md`
5. Persist when there is a durable home.
   - if `output_dir` exists or the adapter defines one, persist the retro artifact with `$SKILL_DIR/scripts/persist_retro_artifact.py` instead of ad hoc file writes
   - if `weekly` and the adapter defines `snapshot_path`, write a compact machine-readable snapshot with the window, evidence sources, and any real metrics or deltas you used
   - if the adapter defines `summary_path`, `$SKILL_DIR/scripts/persist_retro_artifact.py` should refresh the compact recent-lessons digest automatically from the written durable artifact
   - on the first retro after a legacy hand-curated `recent-lessons.md` (file exists, `output_dir` has no prior `*.md` artifacts), the persistence helper preserves the existing summary instead of replacing it with an empty-stub digest. Pass `--force-empty-summary` only after confirming the legacy content is safe to drop.
   - otherwise still give the user a concise retro in chat
   - when the retro names an RCA-class event (a bug, repeated correction, or
     weak-proof finding) and the repo maintains the conversion ledger, append
     one RCA event (`--source retro`) per
     `../../shared/references/rca-ledger-append.md`; this is a silent no-op in
     repos without the ledger
   - never stop without stating `Persisted: yes: <path>` or `Persisted: no: <reason>`

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
- `Sibling Search` when a transferable waste pattern is named (opt-in;
  `n/a — trivial fix; no plausible siblings` short-circuit otherwise)
- `Persisted`
- `Packet Consumed` when a retro prepare packet was produced, or
  `n/a (no adapter sections)` when no sections are declared

## Auto-Retro Trigger

Trigger a short `session` retro automatically when a user correction exposes a
real miss in the workflow, not just a preference difference — for example a
fresh-eye reader misread an invariant that is present in the code, revealing it
still relies on convention rather than declaration. Also trigger after slice
closeout when
`python3 "$SKILL_DIR/scripts/check_auto_trigger.py" --repo-root .` reports
`triggered: true` (or the slice matches the adapter's
`auto_session_trigger_surfaces` / `auto_session_trigger_path_globs`). Keep it
bounded to the revealed miss rather than a postmortem; it may stay inline but
must still include `Persisted`. The full trigger/skip taxonomy and examples live
in `references/trigger-and-persistence.md`.

## Expert Counterfactual Rule

Every retro includes at least one counterfactual lens. Use named experts only
when the name sharpens a *different* changed action, constraint, or question
(never decoration); when sub-agents are available and the session warrants
depth, up to two distinct-lens expert sub-agents, otherwise write the
counterfactuals inline. The lens patterns, named-expert examples, and sub-agent
flow live in `references/expert-lens.md`.

## Guardrails

- Separate observed facts from proposed improvements.
- Do not fabricate metrics when the adapter does not provide a real source.
- Do not label broad exploration as waste solely because it was broad; identify
  phase intent and the triage lock first.
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
- `references/phase-aware-efficiency.md`
- `references/expert-lens.md`
- `references/trigger-and-persistence.md`
- `references/weekly-trends.md`
- `references/waste-sibling-scan.md`
- `references/prepare-packet.md`
- `../../shared/references/retro-issue-destination-split.md`
- `../debug/references/sibling-search.md`
- `../../shared/references/rca-ledger-append.md`
